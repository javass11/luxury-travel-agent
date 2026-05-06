import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AmadeusFlightAPI:
    """
    Amadeus Flight Search API client.
    Provides flight search functionality with fallback to demo data.
    """

    def __init__(self):
        self.api_key = os.getenv('AMADEUS_API_KEY')
        self.api_secret = os.getenv('AMADEUS_API_SECRET')
        self.enabled = bool(self.api_key and self.api_secret)

        if self.enabled:
            try:
                # Lazy import to avoid dependency if not configured
                from amadeus import Client
                self.client = Client(
                    client_id=self.api_key,
                    client_secret=self.api_secret
                )
            except ImportError:
                logger.warning("Amadeus SDK not installed, using fallback mode")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Amadeus client: {e}")
                self.enabled = False

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: Optional[str] = None,
        adults: int = 1,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for flights.

        Args:
            origin: IATA code (e.g., 'ORD')
            destination: IATA code (e.g., 'MIA')
            departure_date: Date in YYYY-MM-DD format
            cabin_class: ECONOMY, BUSINESS, FIRST
            adults: Number of passengers
            max_results: Maximum results to return

        Returns:
            List of flight dictionaries with pricing
        """
        if not self.enabled:
            logger.info("Amadeus API disabled, returning demo data")
            return self._get_demo_flights(origin, destination, departure_date, cabin_class)

        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                travelClass=cabin_class or 'ECONOMY'
            )

            if not response.data:
                logger.info(f"No flights found for {origin}->{destination}")
                return []

            flights = [self._format_flight(f) for f in response.data[:max_results]]
            logger.info(f"Found {len(flights)} flights via Amadeus")
            return sorted(flights, key=lambda x: x['cpp'], reverse=True)

        except Exception as e:
            logger.error(f"Amadeus API error: {str(e)}")
            logger.info("Falling back to demo data")
            return self._get_demo_flights(origin, destination, departure_date, cabin_class)

    def _format_flight(self, flight: Dict) -> Dict:
        """Convert Amadeus API response to standard format"""
        try:
            first_segment = flight['itineraries'][0]['segments'][0]
            last_segment = flight['itineraries'][-1]['segments'][-1]

            cash_price = float(flight['price']['total'])
            miles_cost = self._estimate_miles(cash_price)

            return {
                'id': flight['id'],
                'airline': flight['validatingAirlineCodes'][0] if flight.get('validatingAirlineCodes') else 'Various',
                'origin': first_segment['departure']['iataCode'],
                'destination': last_segment['arrival']['iataCode'],
                'departure_date': first_segment['departure']['at'].split('T')[0],
                'cash_price': cash_price,
                'miles_cost': miles_cost,
                'cpp': cash_price / miles_cost if miles_cost > 0 else 0.0,
                'cabin_class': 'ECONOMY',
                'duration': flight['itineraries'][0].get('duration', 'N/A'),
                'stops': len(flight['itineraries'][0]['segments']) - 1,
                'source': 'amadeus'
            }
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing flight data: {e}")
            return None

    def _estimate_miles(self, cash_price: float) -> int:
        """Estimate miles cost based on cash price"""
        if cash_price < 200:
            return 10000
        elif cash_price < 500:
            return 25000
        elif cash_price < 1000:
            return 50000
        else:
            return 100000

    def _get_demo_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        cabin_class: Optional[str] = None
    ) -> List[Dict]:
        """Return demo flights matching search criteria"""
        demo_flights = [
            {
                'id': 'FL001',
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'airline': 'United',
                'cabin_class': cabin_class or 'ECONOMY',
                'cash_price': 450.0,
                'miles_cost': 85000,
                'cpp': 5.29,
                'duration': 'PT3H30M',
                'stops': 0,
                'source': 'demo'
            },
            {
                'id': 'FL002',
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'airline': 'American',
                'cabin_class': cabin_class or 'ECONOMY',
                'cash_price': 480.0,
                'miles_cost': 90000,
                'cpp': 5.33,
                'duration': 'PT4H00M',
                'stops': 1,
                'source': 'demo'
            },
            {
                'id': 'FL003',
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'airline': 'Delta',
                'cabin_class': cabin_class or 'ECONOMY',
                'cash_price': 420.0,
                'miles_cost': 80000,
                'cpp': 5.25,
                'duration': 'PT3H15M',
                'stops': 0,
                'source': 'demo'
            }
        ]
        return sorted(demo_flights, key=lambda x: x['cpp'], reverse=True)
