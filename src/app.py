import os
import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from .models import db, User, SearchLog, Alert
from .auth import auth_bp
from .config import Config
from .database import LuxuryTravelDB
from .flights import FlightSearchEngine
from .hotels import HotelSearchEngine
from .agent import LuxuryTravelAssistant
from .api_clients.amadeus import AmadeusFlightAPI
from .api_clients.hotels import HotelSearchAPI
from .cache import cache
from .redemption import evaluate_redemption, redemption_to_dict
from .visualization import visualize_cpp_bar_chart, TravelRedemptionOption
from .api_clients.seats_aero import SeatsAeroAPI
from .travel_api_config import load_travel_api_config
from .phase1_handlers import PreferencesHandler, PriceHistoryHandler, LoyaltyHandler, AlertHandler
from .advanced_filters import FlightFilter, HotelFilter, AwardFilter
from .analytics_handlers import DealAnalyticsHandler, UserAnalyticsHandler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config.from_object(Config)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///luxury_travel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * 24

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)

# Load centralized API configuration
travel_api_config = load_travel_api_config()

# Initialize API clients
amadeus_api = AmadeusFlightAPI()
hotels_api = HotelSearchAPI()
seats_aero_api = SeatsAeroAPI()

# Initialize legacy database and engines for demo
try:
    legacy_db = LuxuryTravelDB()
    flight_engine = FlightSearchEngine(legacy_db)
    hotel_engine = HotelSearchEngine(legacy_db)
    assistant = LuxuryTravelAssistant(legacy_db)
except Exception as e:
    print(f"Warning: Could not initialize legacy database: {e}")
    legacy_db = None


@app.route("/")
def index():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return f.read()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    missing_credentials = Config.validate_api_credentials()
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'missing_credentials': missing_credentials,
    })


@app.route("/api/deals/analyze", methods=["POST"])
def analyze_deals():
    """Analyze flight and hotel deals using real APIs"""
    data = request.json

    origin = data.get("origin", "").upper()
    destination = data.get("destination", "").upper()
    departure_date = data.get("departure_date")
    cabin_class = data.get("cabin_class", "ECONOMY")

    hotel_destination = data.get("hotel_destination", destination)
    checkin = data.get("checkin", departure_date)
    checkout = data.get("checkout")

    if not all([origin, destination, departure_date, checkin, checkout]):
        return jsonify({"error": "Missing required fields"}), 400

    # Search flights
    flights = amadeus_api.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class
    )

    # Search hotels
    hotels = hotels_api.search_hotels(
        destination=hotel_destination,
        checkin_date=checkin,
        checkout_date=checkout
    )

    return jsonify({
        "flights": flights[:10],
        "hotels": hotels[:10],
        "summary": {
            "flight_count": len(flights),
            "hotel_count": len(hotels),
            "best_flight_cpp": flights[0]["cpp"] if flights else None,
            "best_hotel_cpp": hotels[0]["cpp"] if hotels else None,
            "flight_source": next((f.get('source', 'unknown') for f in flights), 'unknown'),
            "hotel_source": next((h.get('source', 'unknown') for h in hotels), 'unknown'),
        },
    }), 200


@app.route("/api/flights/search", methods=["GET"])
def search_flights():
    """Search flights with advanced filtering, preferences, and analytics"""
    import time
    start_time = time.time()

    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    departure_date = request.args.get("departure_date")
    cabin_class = request.args.get("cabin_class", "ECONOMY")

    if not all([origin, destination, departure_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass

    # Build advanced filters from query params
    filters = {
        'cabin_class': cabin_class,
        'max_stops': request.args.get("max_stops", type=int),
        'max_price': request.args.get("max_price", type=float),
        'min_price': request.args.get("min_price", type=float),
        'direct_only': request.args.get("direct_only", type=bool),
        'exclude_airlines': request.args.getlist("exclude_airlines"),
        'include_airlines': request.args.getlist("include_airlines"),
        'preferred_departure_time': request.args.get("preferred_departure_time"),
    }

    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    # Check cache
    cache_key = f"flights:{origin}:{destination}:{departure_date}:{cabin_class}"
    cached_flights = cache.get(cache_key)
    if cached_flights:
        flights = cached_flights
        source = "cache"
    else:
        # Fetch from API
        flights = amadeus_api.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            cabin_class=cabin_class
        )

        # Cache results
        if flights:
            cache.set(cache_key, flights, ttl=3600)
            source = next((f.get('source', 'unknown') for f in flights), 'unknown')
        else:
            source = 'no_results'

    # Record prices to history
    prices = []
    for flight in flights:
        price = flight.get('cash_price')
        if price:
            prices.append(price)
        PriceHistoryHandler.record_price(
            origin, destination, cabin_class,
            {'cash_price': flight.get('cash_price'), 'miles_cost': flight.get('miles_cost'), 'cpp': flight.get('cpp')},
            source
        )

    # Apply user preferences
    if user_id:
        flights = PreferencesHandler.filter_flights_by_preferences(flights, user_id)

    # Apply advanced filters
    flights = FlightFilter.apply_filters(flights, filters)

    # Update deal analytics
    best_cpp = max([f.get('cpp', 0) for f in flights]) if flights else None
    DealAnalyticsHandler.update_deal_analytics(origin, destination, cabin_class, prices, best_cpp, source)

    # Record search for analytics
    duration_ms = int((time.time() - start_time) * 1000)
    if user_id:
        DealAnalyticsHandler.record_search(user_id, origin, destination, departure_date, cabin_class, len(flights), filters, duration_ms, source)

    # Check alerts
    search_results = {'origin': origin, 'destination': destination, 'flights': flights}
    AlertHandler.check_all_alerts(search_results)

    return jsonify({
        "flights": flights,
        "source": source,
        "count": len(flights),
        "preferences_applied": bool(user_id),
        "filters_applied": len([k for k in filters.keys() if filters[k] is not None]) > 0,
        "duration_ms": duration_ms,
    }), 200


@app.route("/api/hotels/search", methods=["GET"])
def search_hotels():
    """Search hotels from Hotel API with caching"""
    destination = request.args.get("destination")
    checkin_date = request.args.get("checkin_date")
    checkout_date = request.args.get("checkout_date")
    loyalty_program = request.args.get("loyalty_program")

    if not all([destination, checkin_date, checkout_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Check cache first
    cache_key = f"hotels:{destination}:{checkin_date}:{checkout_date}"
    cached_hotels = cache.get(cache_key)
    if cached_hotels:
        hotels = cached_hotels
        source = "cache"
    else:
        # Fetch from API
        hotels = hotels_api.search_hotels(
            destination=destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )
        source = next((h.get('source', 'unknown') for h in hotels), 'unknown')

        # Cache results for 1 hour
        if hotels:
            cache.set(cache_key, hotels, ttl=3600)

    # Filter by loyalty program if provided
    if loyalty_program and hotels:
        hotels = [h for h in hotels if loyalty_program.lower() in h.get("loyalty_program", "").lower()]

    return jsonify({
        "hotels": hotels,
        "source": source,
        "count": len(hotels)
    }), 200


@app.route("/api/chat", methods=["POST"])
@jwt_required()
def chat():
    """Chat with LLM assistant (protected route)"""
    if not legacy_db:
        return jsonify({"error": "Database not available"}), 503

    current_user_id = get_jwt_identity()
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"error": "Message required"}), 400

    try:
        response = assistant.chat(message, current_user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/deals/save", methods=["POST"])
@jwt_required()
def save_deal():
    """Save a deal (protected route)"""
    current_user_id = get_jwt_identity()
    data = request.json
    deal_type = data.get("deal_type")
    deal_id = data.get("deal_id")
    notes = data.get("notes")

    if not all([deal_type, deal_id]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        from .models import SavedDeal
        saved_deal = SavedDeal(
            user_id=current_user_id,
            deal_type=deal_type,
            deal_data={"deal_id": deal_id},
            notes=notes,
        )
        db.session.add(saved_deal)
        db.session.commit()
        return jsonify({"saved_id": saved_deal.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/redemptions/evaluate", methods=["POST"])
def evaluate_redemptions_endpoint():
    """Evaluate redemption options by CPP value (cents per point)"""
    data = request.json
    options_data = data.get("options", [])

    if not options_data:
        return jsonify({"error": "No redemption options provided"}), 400

    try:
        # Evaluate each redemption
        evaluated = []
        best = None
        best_cpp = -1

        for opt in options_data:
            redemption = evaluate_redemption(
                redemption_type=opt.get("redemption_type"),
                cash_price=float(opt.get("cash_price", 0)),
                points_required=int(opt.get("points_required", 0)),
                taxes_and_fees=float(opt.get("taxes_and_fees", 0)),
            )
            evaluated.append(redemption_to_dict(redemption))

            # Track best
            if redemption.cpp > best_cpp:
                best_cpp = redemption.cpp
                best = redemption_to_dict(redemption)

        # Sort by CPP (descending)
        evaluated.sort(key=lambda x: x["cpp"], reverse=True)

        return jsonify({
            "redemptions": evaluated,
            "best_redemption": best,
            "count": len(evaluated)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500


@app.route("/api/cache/stats", methods=["GET"])
@jwt_required()
def cache_stats():
    """Get cache statistics (protected)"""
    stats = cache.get_stats()
    return jsonify({
        "cache": stats,
        "amadeus_api": {
            "enabled": amadeus_api.enabled,
            "status": "configured" if amadeus_api.enabled else "demo_mode"
        },
        "hotels_api": {
            "enabled": hotels_api.enabled,
            "status": "configured" if hotels_api.enabled else "demo_mode"
        }
    }), 200


@app.route("/api/cache/flush", methods=["POST"])
@jwt_required()
def flush_cache():
    """Flush cache (protected)"""
    pattern = request.json.get("pattern", "*") if request.json else "*"
    success = cache.flush_pattern(pattern)
    return jsonify({
        "status": "flushed" if success else "error",
        "pattern": pattern
    }), 200 if success else 500


@app.route("/api/redemptions/visualize", methods=["POST"])
def visualize_redemptions():
    """Generate CPP comparison chart for redemption options"""
    data = request.json
    options_data = data.get("options", [])

    if not options_data:
        return jsonify({"error": "No redemption options provided"}), 400

    try:
        options = []
        for opt in options_data:
            option = TravelRedemptionOption(
                program_or_airline=opt.get("program_or_airline", opt.get("redemption_type", "Unknown")),
                flight_number=opt.get("flight_number", ""),
                origin=opt.get("origin", ""),
                destination=opt.get("destination", ""),
                cabin=opt.get("cabin", "Economy"),
                cash_price_usd=float(opt.get("cash_price", 0)) if opt.get("cash_price") else None,
                miles_required=int(opt.get("miles_required", opt.get("points_required", 0))) if opt.get("miles_required") or opt.get("points_required") else None,
                taxes_usd=float(opt.get("taxes_usd", opt.get("taxes_and_fees", 0))) if opt.get("taxes_usd") or opt.get("taxes_and_fees") else None,
                cpp=float(opt.get("cpp")) if opt.get("cpp") else None,
            )
            options.append(option)

        chart_image = visualize_cpp_bar_chart(
            options,
            title=data.get("title", "Cents Per Point Redemption Value"),
            return_base64=True
        )

        if not chart_image:
            return jsonify({"error": "No cpp values to visualize"}), 400

        return jsonify({
            "chart": chart_image,
            "chart_type": "png_base64",
            "count": len(options),
            "message": "Chart generated successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Visualization failed: {str(e)}"}), 500


@app.route("/api/awards/search", methods=["GET"])
def search_awards():
    """Search award flight availability via Seats.aero"""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    cabin = request.args.get("cabin", "business").lower()
    program = request.args.get("program")
    max_results = int(request.args.get("max_results", 25))

    if not all([origin, destination, start_date]):
        return jsonify({"error": "Missing required parameters: origin, destination, start_date"}), 400

    try:
        awards = seats_aero_api.search_awards(
            origin=origin,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            cabin=cabin,
            program=program,
            max_results=max_results,
        )

        return jsonify({
            "awards": awards,
            "source": "seats_aero",
            "count": len(awards),
            "origin": origin,
            "destination": destination,
            "cabin": cabin,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Award search failed: {str(e)}"}), 500


# ============================================================================
# PHASE 1: User Preferences, Price History, Loyalty, Alerts
# ============================================================================

@app.route("/api/user/preferences", methods=["GET"])
@jwt_required()
def get_preferences():
    """Get user's travel preferences"""
    user_id = get_jwt_identity()
    try:
        prefs = PreferencesHandler.get_user_preferences(user_id)
        return jsonify(prefs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/preferences", methods=["POST"])
@jwt_required()
def update_preferences():
    """Update user's travel preferences"""
    user_id = get_jwt_identity()
    data = request.json

    try:
        prefs = PreferencesHandler.update_user_preferences(user_id, data)
        return jsonify(prefs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/analytics/price-history", methods=["GET"])
def get_price_history():
    """Get historical prices for a route"""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    cabin = request.args.get("cabin")
    days = int(request.args.get("days", 30))

    if not all([origin, destination]):
        return jsonify({"error": "Missing origin or destination"}), 400

    try:
        history = PriceHistoryHandler.get_price_history(origin, destination, cabin, days)
        return jsonify({
            "history": history,
            "count": len(history),
            "origin": origin,
            "destination": destination,
            "days": days
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/price-trends", methods=["GET"])
def get_price_trends():
    """Get price trends and analytics for a route"""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    cabin = request.args.get("cabin")
    days = int(request.args.get("days", 30))

    if not all([origin, destination]):
        return jsonify({"error": "Missing origin or destination"}), 400

    try:
        analytics = PriceHistoryHandler.get_price_analytics(origin, destination, cabin, days)

        if not analytics:
            return jsonify({"error": "No price history available"}), 404

        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/loyalty/accounts", methods=["GET"])
@jwt_required()
def get_loyalty_accounts():
    """Get user's linked loyalty accounts"""
    user_id = get_jwt_identity()

    try:
        accounts = LoyaltyHandler.get_user_loyalty_accounts(user_id)
        return jsonify({
            "accounts": accounts,
            "count": len(accounts)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/loyalty/link", methods=["POST"])
@jwt_required()
def link_loyalty_account():
    """Link a frequent flyer account"""
    user_id = get_jwt_identity()
    data = request.json

    program = data.get("program")
    ff_number = data.get("frequent_flyer_number")

    if not all([program, ff_number]):
        return jsonify({"error": "Missing program or frequent flyer number"}), 400

    try:
        account = LoyaltyHandler.link_loyalty_account(user_id, program, ff_number)
        return jsonify(account), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/loyalty/accounts/<account_id>", methods=["DELETE"])
@jwt_required()
def unlink_loyalty_account(account_id):
    """Unlink a loyalty account"""
    user_id = get_jwt_identity()

    try:
        LoyaltyHandler.delete_loyalty_account(user_id, account_id)
        return jsonify({"message": "Account unlinked"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    """Get user's alerts"""
    user_id = get_jwt_identity()

    try:
        alerts = AlertHandler.get_user_alerts(user_id)
        return jsonify({
            "alerts": alerts,
            "count": len(alerts)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts", methods=["POST"])
@jwt_required()
def create_alert():
    """Create a price or award alert"""
    user_id = get_jwt_identity()
    data = request.json

    alert_type = data.get("alert_type")
    origin = data.get("origin", "").upper()
    destination = data.get("destination", "").upper()
    threshold_price = data.get("threshold_price")
    threshold_miles = data.get("threshold_miles")
    cabin = data.get("cabin")

    if not all([alert_type, origin, destination]):
        return jsonify({"error": "Missing alert_type, origin, or destination"}), 400

    try:
        alert = AlertHandler.create_alert(
            user_id, alert_type, origin, destination,
            threshold_price, threshold_miles, cabin
        )
        return jsonify(alert), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/alerts/<alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id):
    """Delete an alert"""
    user_id = get_jwt_identity()

    try:
        AlertHandler.delete_alert(user_id, alert_id)
        return jsonify({"message": "Alert deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts/<alert_id>/deactivate", methods=["POST"])
@jwt_required()
def deactivate_alert(alert_id):
    """Deactivate an alert"""
    user_id = get_jwt_identity()

    try:
        AlertHandler.deactivate_alert(user_id, alert_id)
        return jsonify({"message": "Alert deactivated"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PHASE 2: Advanced Filtering, Analytics, Error Handling, Tax Breakdown
# ============================================================================

@app.route("/api/analytics/trending-routes", methods=["GET"])
def get_trending_routes():
    """Get trending routes based on search volume and conversion"""
    days = int(request.args.get("days", 7))
    limit = int(request.args.get("limit", 10))

    try:
        routes = DealAnalyticsHandler.get_trending_routes(days, limit)
        return jsonify({
            "routes": routes,
            "count": len(routes),
            "period_days": days
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/pricing-patterns", methods=["GET"])
def get_pricing_patterns():
    """Get pricing patterns and trends for a route"""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    days = int(request.args.get("days", 30))

    if not all([origin, destination]):
        return jsonify({"error": "Missing origin or destination"}), 400

    try:
        patterns = DealAnalyticsHandler.get_pricing_patterns(origin, destination, days)

        if not patterns:
            return jsonify({"error": "Insufficient data for analysis"}), 404

        return jsonify(patterns), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/deal-insights", methods=["GET"])
def get_deal_insights():
    """Get actionable deal insights"""
    limit = int(request.args.get("limit", 20))

    try:
        insights = DealAnalyticsHandler.get_deal_insights(limit)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/popular-destinations", methods=["GET"])
def get_popular_destinations():
    """Get popular destination cities"""
    days = int(request.args.get("days", 30))
    limit = int(request.args.get("limit", 10))

    try:
        destinations = DealAnalyticsHandler.get_popular_destinations(days, limit)
        return jsonify({
            "destinations": destinations,
            "count": len(destinations)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/analytics", methods=["GET"])
@jwt_required()
def get_user_analytics():
    """Get user behavior analytics"""
    user_id = get_jwt_identity()

    try:
        analytics = UserAnalyticsHandler.get_user_analytics(user_id)
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/analytics/summary", methods=["GET"])
@jwt_required()
def get_analytics_summary():
    """Get summary analytics (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Simple admin check (in production, use proper role-based access)
    if not user or user.email not in ['admin@example.com', 'admin@luxurytravelagent.com']:
        return jsonify({"error": "Admin access required"}), 403

    try:
        from sqlalchemy import func

        total_searches = db.session.query(func.count(SearchLog.id)).scalar() or 0
        total_users = db.session.query(func.count(User.id)).scalar() or 0
        total_alerts = db.session.query(func.count(Alert.id)).scalar() or 0

        return jsonify({
            "total_searches": total_searches,
            "total_users": total_users,
            "total_alerts": total_alerts,
            "trending_routes": DealAnalyticsHandler.get_trending_routes(7, 5),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized - valid token required"}), 401


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=Config.DEBUG, port=5000)
