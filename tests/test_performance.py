import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import LuxuryTravelDB
from src.flights import FlightSearchEngine
from src.hotels import HotelSearchEngine


class TestPerformance(unittest.TestCase):
    """Performance and benchmark tests"""

    def setUp(self):
        self.db = LuxuryTravelDB(":memory:")
        self.flight_engine = FlightSearchEngine(self.db)
        self.hotel_engine = HotelSearchEngine(self.db)

    def tearDown(self):
        self.db.close()

    def test_flight_search_performance(self):
        """Flight search should complete in < 100ms"""
        start = time.time()
        for _ in range(100):
            self.flight_engine.search_flights("ORD", "MIA", "2024-06-15")
        duration = (time.time() - start) * 1000
        self.assertLess(duration, 100, f"Flight search took {duration}ms (target: <100ms)")

    def test_hotel_search_performance(self):
        """Hotel search should complete in < 100ms"""
        start = time.time()
        for _ in range(100):
            self.hotel_engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        duration = (time.time() - start) * 1000
        self.assertLess(duration, 100, f"Hotel search took {duration}ms (target: <100ms)")

    def test_cpp_calculation_performance(self):
        """CPP calculation should be < 1ms for 1000 iterations"""
        start = time.time()
        for _ in range(1000):
            self.flight_engine.calculate_cpp(4500.0, 85000)
        duration = (time.time() - start) * 1000
        self.assertLess(duration, 10, f"CPP calculation took {duration}ms (target: <10ms)")

    def test_ranking_performance(self):
        """Ranking 100 flights should complete in < 50ms"""
        flights = self.flight_engine.search_flights("ORD", "MIA", "2024-06-15")
        large_list = flights * 100

        start = time.time()
        self.flight_engine.rank_by_cpp(large_list)
        duration = (time.time() - start) * 1000
        self.assertLess(duration, 50, f"Ranking took {duration}ms (target: <50ms)")

    def test_database_query_performance(self):
        """Database queries should be < 10ms"""
        start = time.time()
        for _ in range(50):
            self.db.get_flights("ORD", "MIA", "2024-06-15")
        duration = (time.time() - start) * 1000
        self.assertLess(duration, 50, f"Database queries took {duration}ms (target: <50ms)")


if __name__ == "__main__":
    unittest.main()
