import os
import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from .models import db, User
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
    """Search flights from Amadeus API with caching"""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    departure_date = request.args.get("departure_date")
    cabin_class = request.args.get("cabin_class", "ECONOMY")

    if not all([origin, destination, departure_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Check cache first
    cache_key = f"flights:{origin}:{destination}:{departure_date}:{cabin_class}"
    cached_flights = cache.get(cache_key)
    if cached_flights:
        return jsonify({
            "flights": cached_flights,
            "source": "cache",
            "message": "Results from cache (valid for 1 hour)"
        }), 200

    # Fetch from API
    flights = amadeus_api.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class
    )

    # Cache results for 1 hour
    if flights:
        cache.set(cache_key, flights, ttl=3600)
        source = next((f.get('source', 'unknown') for f in flights), 'unknown')
    else:
        source = 'no_results'

    return jsonify({
        "flights": flights,
        "source": source,
        "count": len(flights)
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
