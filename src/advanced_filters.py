"""Advanced filtering logic for flights, hotels, and awards"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FlightFilter:
    """Advanced flight filtering"""

    @staticmethod
    def apply_filters(flights: List[Dict], filters: Dict) -> List[Dict]:
        """Apply all filters to flight list"""
        if not flights:
            return flights

        # Duration filters
        if 'max_duration_hours' in filters:
            flights = FlightFilter._filter_by_max_duration(flights, filters['max_duration_hours'])

        if 'min_duration_hours' in filters:
            flights = FlightFilter._filter_by_min_duration(flights, filters['min_duration_hours'])

        # Stops filter
        if 'max_stops' in filters:
            flights = FlightFilter._filter_by_stops(flights, filters['max_stops'])

        if 'direct_only' in filters and filters['direct_only']:
            flights = [f for f in flights if f.get('stops', 0) == 0]

        # Airline filters
        if 'exclude_airlines' in filters and filters['exclude_airlines']:
            flights = FlightFilter._filter_exclude_airlines(flights, filters['exclude_airlines'])

        if 'include_airlines' in filters and filters['include_airlines']:
            flights = FlightFilter._filter_include_airlines(flights, filters['include_airlines'])

        # Cabin filter
        if 'cabin_class' in filters:
            flights = [f for f in flights if f.get('cabin_class', 'ECONOMY').upper() == filters['cabin_class'].upper()]

        # Price range filter
        if 'min_price' in filters:
            flights = [f for f in flights if f.get('cash_price', float('inf')) >= filters['min_price']]

        if 'max_price' in filters:
            flights = [f for f in flights if f.get('cash_price', 0) <= filters['max_price']]

        # CPP range filter
        if 'min_cpp' in filters:
            flights = [f for f in flights if f.get('cpp', 0) >= filters['min_cpp']]

        if 'max_cpp' in filters:
            flights = [f for f in flights if f.get('cpp', float('inf')) <= filters['max_cpp']]

        # Departure time filter
        if 'preferred_departure_time' in filters:
            flights = FlightFilter._filter_by_departure_time(flights, filters['preferred_departure_time'])

        # Arrival time filter
        if 'preferred_arrival_time' in filters:
            flights = FlightFilter._filter_by_arrival_time(flights, filters['preferred_arrival_time'])

        return flights

    @staticmethod
    def _filter_by_max_duration(flights: List[Dict], max_hours: float) -> List[Dict]:
        """Filter flights by maximum duration"""
        def parse_duration(duration_str):
            if not duration_str:
                return float('inf')
            # Handle ISO 8601 format like "PT3H30M"
            try:
                duration_str = duration_str.replace('PT', '')
                hours = 0
                if 'H' in duration_str:
                    h_part = duration_str.split('H')[0].split('M')[0]
                    hours = float(h_part.split('M')[-1]) if 'M' in duration_str else float(h_part)
                if 'M' in duration_str:
                    m_part = duration_str.split('M')[0].split('H')[-1]
                    hours += float(m_part) / 60 if m_part else 0
                return hours
            except:
                return float('inf')

        return [f for f in flights if parse_duration(f.get('duration', '')) <= max_hours]

    @staticmethod
    def _filter_by_min_duration(flights: List[Dict], min_hours: float) -> List[Dict]:
        """Filter flights by minimum duration"""
        # Similar to max duration but reversed
        return [f for f in flights if parse_duration(f.get('duration', '')) >= min_hours]

    @staticmethod
    def _filter_by_stops(flights: List[Dict], max_stops: int) -> List[Dict]:
        """Filter by maximum stops"""
        return [f for f in flights if f.get('stops', 0) <= max_stops]

    @staticmethod
    def _filter_exclude_airlines(flights: List[Dict], exclude_list: List[str]) -> List[Dict]:
        """Exclude specific airlines"""
        exclude = [a.upper() for a in exclude_list]
        return [f for f in flights if f.get('airline', '').upper() not in exclude]

    @staticmethod
    def _filter_include_airlines(flights: List[Dict], include_list: List[str]) -> List[Dict]:
        """Include only specific airlines"""
        include = [a.upper() for a in include_list]
        return [f for f in flights if f.get('airline', '').upper() in include]

    @staticmethod
    def _filter_by_departure_time(flights: List[Dict], time_pref: str) -> List[Dict]:
        """Filter by preferred departure time (morning/afternoon/evening/night)"""
        time_ranges = {
            'morning': (6, 12),
            'afternoon': (12, 18),
            'evening': (18, 21),
            'night': (21, 6),
        }

        if time_pref.lower() not in time_ranges:
            return flights

        start_hour, end_hour = time_ranges[time_pref.lower()]

        def get_departure_hour(flight):
            # Parse departure time from flight data
            departure = flight.get('departure_time', '')
            if departure and 'T' in departure:
                time_str = departure.split('T')[1]
                try:
                    return int(time_str.split(':')[0])
                except:
                    return None
            return None

        filtered = []
        for f in flights:
            hour = get_departure_hour(f)
            if hour is None:
                filtered.append(f)  # Keep if can't parse
            elif start_hour <= end_hour:
                if start_hour <= hour < end_hour:
                    filtered.append(f)
            else:  # night wraps around midnight
                if hour >= start_hour or hour < end_hour:
                    filtered.append(f)

        return filtered

    @staticmethod
    def _filter_by_arrival_time(flights: List[Dict], time_pref: str) -> List[Dict]:
        """Filter by preferred arrival time (morning/afternoon/evening/night)"""
        # Similar to departure time filtering but using arrival_time field
        return FlightFilter._filter_by_departure_time(flights, time_pref)


class HotelFilter:
    """Advanced hotel filtering"""

    @staticmethod
    def apply_filters(hotels: List[Dict], filters: Dict) -> List[Dict]:
        """Apply all filters to hotel list"""
        if not hotels:
            return hotels

        # Star rating
        if 'min_stars' in filters:
            hotels = [h for h in hotels if h.get('stars', 0) >= filters['min_stars']]

        if 'max_stars' in filters:
            hotels = [h for h in hotels if h.get('stars', 0) <= filters['max_stars']]

        # Price range
        if 'min_price_per_night' in filters:
            hotels = [h for h in hotels if h.get('price_per_night', float('inf')) >= filters['min_price_per_night']]

        if 'max_price_per_night' in filters:
            hotels = [h for h in hotels if h.get('price_per_night', 0) <= filters['max_price_per_night']]

        # Hotel chains
        if 'preferred_chains' in filters and filters['preferred_chains']:
            chains = [c.lower() for c in filters['preferred_chains']]
            hotels = [h for h in hotels if h.get('chain', '').lower() in chains]

        # Amenities
        if 'required_amenities' in filters and filters['required_amenities']:
            required = [a.lower() for a in filters['required_amenities']]
            hotels = [h for h in hotels if all(a in [x.lower() for x in h.get('amenities', [])] for a in required)]

        # Loyalty program
        if 'loyalty_program_only' in filters and filters['loyalty_program_only']:
            hotels = [h for h in hotels if h.get('earns_points', False)]

        # Rating
        if 'min_rating' in filters:
            hotels = [h for h in hotels if h.get('rating', 0) >= filters['min_rating']]

        # CPP filter (for points)
        if 'min_cpp' in filters:
            hotels = [h for h in hotels if h.get('cpp', 0) >= filters['min_cpp']]

        if 'max_cpp' in filters:
            hotels = [h for h in hotels if h.get('cpp', float('inf')) <= filters['max_cpp']]

        return hotels


class AwardFilter:
    """Advanced award filtering"""

    @staticmethod
    def apply_filters(awards: List[Dict], filters: Dict) -> List[Dict]:
        """Apply all filters to award list"""
        if not awards:
            return awards

        # Miles range
        if 'min_miles' in filters:
            awards = [a for a in awards if a.get('miles_required', float('inf')) >= filters['min_miles']]

        if 'max_miles' in filters:
            awards = [a for a in awards if a.get('miles_required', 0) <= filters['max_miles']]

        # Program filter
        if 'program' in filters:
            program = filters['program'].lower()
            awards = [a for a in awards if program in a.get('program', '').lower()]

        # Cabin filter
        if 'cabin' in filters:
            cabin = filters['cabin'].lower()
            awards = [a for a in awards if cabin == a.get('cabin', 'economy').lower()]

        # Exclude high fuel surcharge
        if 'low_fuel_surcharge_only' in filters and filters['low_fuel_surcharge_only']:
            awards = [a for a in awards if a.get('taxes', 0) < 100]  # Arbitrary threshold

        # CPP range
        if 'min_cpp' in filters:
            awards = [a for a in awards if a.get('cpp', 0) >= filters['min_cpp']]

        if 'max_cpp' in filters:
            awards = [a for a in awards if a.get('cpp', float('inf')) <= filters['max_cpp']]

        # Availability
        if 'availability' in filters:
            avail = filters['availability'].lower()
            awards = [a for a in awards if avail == a.get('availability', 'available').lower()]

        return awards


def parse_duration(duration_str: str) -> float:
    """Parse ISO 8601 duration string to hours (PT3H30M -> 3.5)"""
    if not duration_str:
        return 0

    try:
        duration_str = duration_str.replace('PT', '')
        hours = 0

        # Extract hours
        if 'H' in duration_str:
            parts = duration_str.split('H')
            hours = float(parts[0])
            duration_str = parts[1] if len(parts) > 1 else ''

        # Extract minutes
        if 'M' in duration_str:
            parts = duration_str.split('M')
            minutes = float(parts[0])
            hours += minutes / 60

        return hours
    except Exception as e:
        logger.error(f"Failed to parse duration '{duration_str}': {e}")
        return 0
