import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TravelApiConfig:
    """Centralized configuration for all travel API integrations"""
    amadeus_client_id: Optional[str]
    amadeus_client_secret: Optional[str]
    amadeus_base_url: str
    seats_aero_api_key: Optional[str]
    seats_aero_base_url: str


def load_travel_api_config() -> TravelApiConfig:
    """
    Load travel API configuration from environment variables.

    All API credentials are optional - if not provided, APIs will use demo data.
    Base URLs have sensible defaults but can be overridden.
    """
    return TravelApiConfig(
        amadeus_client_id=os.getenv("AMADEUS_CLIENT_ID"),
        amadeus_client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
        amadeus_base_url=os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com"),
        seats_aero_api_key=os.getenv("SEATS_AERO_API_KEY"),
        seats_aero_base_url=os.getenv("SEATS_AERO_BASE_URL", "https://seats.aero/partnerapi"),
    )
