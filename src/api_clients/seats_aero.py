import os
import requests
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class SeatsAeroAPI:
    """Client for Seats.aero award availability search"""

    def __init__(self):
        self.enabled = bool(os.getenv("SEATS_AERO_API_KEY"))
        self.base_url = os.getenv("SEATS_AERO_BASE_URL", "https://seats.aero/partnerapi").rstrip("/")
        self.endpoint_path = os.getenv("SEATS_AERO_AVAILABILITY_PATH", "/search")
        self.api_key = os.getenv("SEATS_AERO_API_KEY")

        if self.enabled:
            logger.info("Seats.aero API configured and enabled")
        else:
            logger.warning("Seats.aero API not configured - award searches will use demo data")

    def search_awards(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: Optional[str] = None,
        cabin: str = "business",
        program: Optional[str] = None,
        max_results: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Search award availability using Seats.aero API with fallback to demo data.

        Args:
            origin: Departure airport code (e.g., "JFK")
            destination: Arrival airport code (e.g., "LHR")
            start_date: Search start date (YYYY-MM-DD)
            end_date: Search end date (optional)
            cabin: Cabin class (economy, business, first)
            program: Loyalty program filter (optional)
            max_results: Max results to return

        Returns:
            List of award options with availability and points cost
        """
        if not self.enabled:
            logger.info("Seats.aero not configured, using demo award data")
            return self._get_demo_awards(origin, destination, cabin)

        try:
            return self._search_api(
                origin=origin,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                cabin=cabin,
                program=program,
                max_results=max_results,
            )
        except Exception as e:
            logger.warning(f"Seats.aero API error: {str(e)}, falling back to demo data")
            return self._get_demo_awards(origin, destination, cabin)

    def _search_api(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: Optional[str] = None,
        cabin: str = "business",
        program: Optional[str] = None,
        max_results: int = 25,
    ) -> List[Dict[str, Any]]:
        """Make actual API call to Seats.aero"""
        params = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "start_date": start_date,
            "cabin": cabin.lower(),
            "limit": max_results,
        }

        if end_date:
            params["end_date"] = end_date

        if program:
            params["program"] = program

        response = requests.get(
            f"{self.base_url}{self.endpoint_path}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            params=params,
            timeout=30,
        )

        if response.status_code in {401, 403}:
            raise RuntimeError(
                "Seats.aero authentication failed. Check SEATS_AERO_API_KEY, "
                "account permissions, and the required authentication header format."
            )

        if response.status_code == 404:
            raise RuntimeError(
                "Seats.aero endpoint not found. Confirm SEATS_AERO_BASE_URL and "
                "SEATS_AERO_AVAILABILITY_PATH from your partner documentation."
            )

        if response.status_code == 429:
            raise RuntimeError("Seats.aero rate limit reached. Retry later or request a higher quota.")

        response.raise_for_status()
        data = response.json()

        # Parse response - handle different response formats
        results = data.get("data", data.get("results", []))
        return self._format_awards(results)

    def _format_awards(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Seats.aero API response to consistent structure"""
        formatted = []
        for item in results:
            formatted.append({
                "source": "seats_aero",
                "program": item.get("program") or item.get("source"),
                "airline": item.get("airline") or item.get("carrier"),
                "flight_number": item.get("flight_number") or item.get("flight"),
                "origin": item.get("origin"),
                "destination": item.get("destination"),
                "departure": item.get("departure") or item.get("departure_date"),
                "cabin": item.get("cabin"),
                "miles_required": item.get("miles") or item.get("points"),
                "taxes_usd": item.get("taxes") or item.get("fees"),
                "availability": item.get("availability", "available"),
                "last_seen": item.get("last_seen") or item.get("updated_at"),
                "cpp": self._estimate_cpp(
                    item.get("miles") or item.get("points", 0),
                    item.get("taxes") or item.get("fees", 0),
                ),
            })
        return formatted

    def _estimate_cpp(self, miles_required: int, taxes_usd: float) -> Optional[float]:
        """
        Estimate CPP by working backwards from typical cash prices.
        This is a rough estimate - for accurate CPP, use actual cash equivalent.
        """
        if not miles_required or miles_required <= 0:
            return None

        # This would ideally come from a companion cash price search
        # For now, return None and let the caller enrich with cash prices
        return None

    def _get_demo_awards(self, origin: str, destination: str, cabin: str) -> List[Dict[str, Any]]:
        """Return sample award availability for demo/testing"""
        demo_data = [
            {
                "source": "seats_aero",
                "program": "United MileagePlus",
                "airline": "United Airlines",
                "flight_number": "UA900",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure": "2026-07-15 08:30",
                "cabin": cabin,
                "miles_required": 155000,
                "taxes_usd": 75.00,
                "availability": "available",
                "last_seen": "2026-05-06T15:30:00Z",
                "cpp": None,
            },
            {
                "source": "seats_aero",
                "program": "American AAdvantage",
                "airline": "American Airlines",
                "flight_number": "AA280",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure": "2026-07-15 14:15",
                "cabin": cabin,
                "miles_required": 120000,
                "taxes_usd": 125.00,
                "availability": "available",
                "last_seen": "2026-05-06T14:45:00Z",
                "cpp": None,
            },
            {
                "source": "seats_aero",
                "program": "Delta SkyMiles",
                "airline": "Delta Air Lines",
                "flight_number": "DL214",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure": "2026-07-16 11:00",
                "cabin": cabin,
                "miles_required": 140000,
                "taxes_usd": 95.00,
                "availability": "available",
                "last_seen": "2026-05-06T13:20:00Z",
                "cpp": None,
            },
        ]
        return demo_data
