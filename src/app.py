import json
from flask import Flask, jsonify, request, render_template_string
from .config import Config
from .database import LuxuryTravelDB
from .flights import FlightSearchEngine
from .hotels import HotelSearchEngine
from .agent import LuxuryTravelAssistant

app = Flask(__name__, static_url_path="/static", static_folder="../static")
app.config.from_object(Config)

db = LuxuryTravelDB()
flight_engine = FlightSearchEngine(db)
hotel_engine = HotelSearchEngine(db)
assistant = LuxuryTravelAssistant(db)


@app.route("/")
def index():
    with open("static/index.html", "r") as f:
        return f.read()


@app.route("/api/health", methods=["GET"])
def health():
    missing_credentials = Config.validate_api_credentials()
    return jsonify(
        {
            "status": "healthy",
            "missing_credentials": missing_credentials,
        }
    )


@app.route("/api/deals/analyze", methods=["POST"])
def analyze_deals():
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

    return jsonify(
        {
            "flights": flights[:10],
            "hotels": hotels[:10],
            "summary": {
                "flight_count": len(flights),
                "hotel_count": len(hotels),
                "best_flight_cpp": flights[0]["cpp"] if flights else None,
                "best_hotel_cpp": hotels[0]["cpp"] if hotels else None,
            },
        }
    )


@app.route("/api/flights/search", methods=["GET"])
def search_flights():
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
    destination = request.args.get("destination")
    checkin_date = request.args.get("checkin_date")
    checkout_date = request.args.get("checkout_date")
    loyalty_program = request.args.get("loyalty_program")

    if not all([destination, checkin_date, checkout_date]):
        return jsonify({"error": "Missing required parameters"}), 400

    hotels = hotel_engine.search_hotels(destination, checkin_date, checkout_date, loyalty_program)
    return jsonify({"hotels": hotels})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message")
    user_id = data.get("user_id")

    if not message:
        return jsonify({"error": "Message required"}), 400

    try:
        response = assistant.chat(message, user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/deals/save", methods=["POST"])
def save_deal():
    data = request.json
    user_id = data.get("user_id")
    deal_type = data.get("deal_type")
    deal_id = data.get("deal_id")
    notes = data.get("notes")

    if not all([user_id, deal_type, deal_id]):
        return jsonify({"error": "Missing required fields"}), 400

    saved_id = db.save_deal(user_id, deal_type, deal_id, notes)
    return jsonify({"saved_id": saved_id})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
