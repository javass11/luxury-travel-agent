from typing import List, Dict, Optional
from .database import LuxuryTravelDB


class FlightSearchEngine:
    def __init__(self, db: LuxuryTravelDB):
        self.db = db

    def search_flights(
        self, origin: str, destination: str, departure_date: str, cabin_class: Optional[str] = None
    ) -> List[Dict]:
        flights = self.db.get_flights(origin, destination, departure_date)

        if cabin_class:
            flights = [f for f in flights if f["cabin_class"].lower() == cabin_class.lower()]

        return sorted(flights, key=lambda x: x["cpp"], reverse=True)

    def calculate_cpp(self, cash_price: float, miles_cost: int) -> float:
        if miles_cost == 0:
            return 0.0
        return cash_price / miles_cost

    def get_flight_details(self, flight_id: str) -> Optional[Dict]:
        flights = self.db.connection.cursor().execute(
            "SELECT * FROM flights WHERE id = ?", (flight_id,)
        ).fetchall()
        return dict(flights[0]) if flights else None

    def rank_by_cpp(self, flights: List[Dict]) -> List[Dict]:
        return sorted(flights, key=lambda x: x["cpp"], reverse=True)

    def highlight_sweet_spots(self, flights: List[Dict], threshold_cpp: float = 5.0) -> List[Dict]:
        return [f for f in flights if f["cpp"] >= threshold_cpp]
