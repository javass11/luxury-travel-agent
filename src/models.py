from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime


@dataclass
class FlightDeal:
    id: str
    origin: str
    destination: str
    departure_date: str
    airline: str
    cabin_class: str
    cash_price: float
    miles_cost: int
    cpp: float
    seat_map_url: Optional[str] = None
    amenities: Optional[List[str]] = None
    elite_benefits: Optional[Dict[str, str]] = None


@dataclass
class HotelDeal:
    id: str
    name: str
    destination: str
    checkin_date: str
    checkout_date: str
    cash_rate: float
    points_cost: int
    cpp: float
    loyalty_program: str
    elite_nights: int
    suite_upgrade_available: bool
    amenities: Optional[List[str]] = None


@dataclass
class LoyaltyProfile:
    user_id: str
    airline_miles: Dict[str, int]
    hotel_points: Dict[str, int]
    elite_status: Dict[str, str]
    created_at: datetime
    updated_at: datetime


@dataclass
class SavedDeal:
    id: str
    user_id: str
    deal_type: str
    deal_id: str
    saved_at: datetime
    notes: Optional[str] = None
