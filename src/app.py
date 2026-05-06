import os
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

load_dotenv()

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
    """Analyze flight and hotel deals (demo uses legacy database)"""
    if not legacy_db:
        return jsonify({"error": "Database not available"}), 503

    data = request.json

    origin = data.get("origin", "").upper()
    destination = data.get("destination", "").upper()
    departure_date = data.get("departure_date")

    cabin_class = data.get("cabin_class", "Economy")

    hotel_destination = data.get("hotel_destination", destination)
    checkin = data.get("checkin", departure_date)
    checkout = data.get("checkout")

    if not all([origin, destination, departure_date, checkin, checkout]):
        return jsonify({"error": "Missing required fields"}), 400

    flights = flight_engine.search_flights(origin, destination, departure_date, cabin_class)
    hotels = hotel_engine.search_hotels(hotel_destination, checkin, checkout)

    return jsonify({
        "flights": flights[:10],
        "hotels": hotels[:10],
        "summary": {
            "flight_count": len(flights),
            "hotel_count": len(hotels),
            "best_flight_cpp": flights[0]["cpp"] if flights else None,
            "best_hotel_cpp": hotels[0]["cpp"] if hotels else None,
        },
    })


@app.route("/api/flights/search", methods=["GET"])
def search_flights():
    """Search flights (demo uses legacy database)"""
    if not legacy_db:
        return jsonify({"error": "Database not available"}), 503

    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    departure_date = request.args.get("departure_date")
    cabin_class = request.args.get("cabin_class")

    if not all([origin, destination, departure_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    flights = flight_engine.search_flights(origin, destination, departure_date, cabin_class)
    return jsonify({"flights": flights})


@app.route("/api/hotels/search", methods=["GET"])
def search_hotels():
    """Search hotels (demo uses legacy database)"""
    if not legacy_db:
        return jsonify({"error": "Database not available"}), 503

    destination = request.args.get("destination")
    checkin_date = request.args.get("checkin_date")
    checkout_date = request.args.get("checkout_date")
    loyalty_program = request.args.get("loyalty_program")

    if not all([destination, checkin_date, checkout_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    hotels = hotel_engine.search_hotels(destination, checkin_date, checkout_date, loyalty_program)
    return jsonify({"hotels": hotels})


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
