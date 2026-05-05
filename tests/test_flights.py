import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import LuxuryTravelDB
from src.flights import FlightSearchEngine


class TestFlightSearchEngine(unittest.TestCase):
    def setUp(self):
        self.db = LuxuryTravelDB(":memory:")
        self.engine = FlightSearchEngine(self.db)

    def tearDown(self):
        self.db.close()

    def test_calculate_cpp(self):
        cpp = self.engine.calculate_cpp(4500.0, 85000)
        self.assertAlmostEqual(cpp, 0.0529, places=4)

    def test_calculate_cpp_zero_miles(self):
        cpp = self.engine.calculate_cpp(4500.0, 0)
        self.assertEqual(cpp, 0.0)

    def test_search_flights(self):
        flights = self.engine.search_flights("ORD", "MIA", "2024-06-15")
        self.assertIsInstance(flights, list)
        self.assertGreater(len(flights), 0)

    def test_search_flights_with_cabin_class(self):
        flights = self.engine.search_flights("ORD", "MIA", "2024-06-15", "Business")
        self.assertIsInstance(flights, list)
        if flights:
            for flight in flights:
                self.assertEqual(flight["cabin_class"].lower(), "business")

    def test_rank_by_cpp(self):
        flights = self.engine.search_flights("ORD", "MIA", "2024-06-15")
        ranked = self.engine.rank_by_cpp(flights)
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(ranked[i]["cpp"], ranked[i + 1]["cpp"])

    def test_highlight_sweet_spots(self):
        flights = self.engine.search_flights("ORD", "MIA", "2024-06-15")
        sweet_spots = self.engine.highlight_sweet_spots(flights, threshold_cpp=5.0)
        self.assertIsInstance(sweet_spots, list)
        for flight in sweet_spots:
            self.assertGreaterEqual(flight["cpp"], 5.0)


if __name__ == "__main__":
    unittest.main()
