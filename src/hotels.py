from typing import List, Dict, Optional
from .models import HotelDeal
from .database import LuxuryTravelDB


class HotelSearchEngine:
    def __init__(self, db: LuxuryTravelDB):
        self.db = db

    def search_hotels(
        self, destination: str, checkin_date: str, checkout_date: str, loyalty_program: Optional[str] = None
    ) -> List[Dict]:
        hotels = self.db.get_hotels(destination, checkin_date, checkout_date)

        if loyalty_program:
            hotels = [h for h in hotels if loyalty_program.lower() in h["loyalty_program"].lower()]

        return sorted(hotels, key=lambda x: x["cpp"], reverse=True)

    def calculate_cpp(self, cash_rate: float, points_cost: int) -> float:
        if points_cost == 0:
            return 0.0
        return cash_rate / points_cost

    def get_hotel_details(self, hotel_id: str) -> Optional[Dict]:
        hotels = self.db.connection.cursor().execute(
            "SELECT * FROM hotels WHERE id = ?", (hotel_id,)
        ).fetchall()
        return dict(hotels[0]) if hotels else None

    def rank_by_cpp(self, hotels: List[Dict]) -> List[Dict]:
        return sorted(hotels, key=lambda x: x["cpp"], reverse=True)

    def filter_elite_benefits(self, hotels: List[Dict], min_elite_nights: int = 2) -> List[Dict]:
        return [h for h in hotels if h["elite_nights"] >= min_elite_nights]

    def filter_upgrade_availability(self, hotels: List[Dict], upgrade_only: bool = False) -> List[Dict]:
        if upgrade_only:
            return [h for h in hotels if h["suite_upgrade_available"]]
        return hotels
