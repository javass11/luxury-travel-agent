import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import LuxuryTravelDB
from src.hotels import HotelSearchEngine


class TestHotelSearchEngine(unittest.TestCase):
    def setUp(self):
        self.db = LuxuryTravelDB(":memory:")
        self.engine = HotelSearchEngine(self.db)

    def tearDown(self):
        self.db.close()

    def test_calculate_cpp(self):
        cpp = self.engine.calculate_cpp(1200.0, 120000)
        self.assertEqual(cpp, 0.01)

    def test_calculate_cpp_zero_points(self):
        cpp = self.engine.calculate_cpp(1200.0, 0)
        self.assertEqual(cpp, 0.0)

    def test_search_hotels(self):
        hotels = self.engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        self.assertIsInstance(hotels, list)
        self.assertGreater(len(hotels), 0)

    def test_search_hotels_with_loyalty_program(self):
        hotels = self.engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22", "Marriott")
        self.assertIsInstance(hotels, list)

    def test_rank_by_cpp(self):
        hotels = self.engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        ranked = self.engine.rank_by_cpp(hotels)
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(ranked[i]["cpp"], ranked[i + 1]["cpp"])

    def test_filter_elite_benefits(self):
        hotels = self.engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        filtered = self.engine.filter_elite_benefits(hotels, min_elite_nights=2)
        self.assertIsInstance(filtered, list)
        for hotel in filtered:
            self.assertGreaterEqual(hotel["elite_nights"], 2)

    def test_filter_upgrade_availability(self):
        hotels = self.engine.search_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        upgrades = self.engine.filter_upgrade_availability(hotels, upgrade_only=True)
        self.assertIsInstance(upgrades, list)
        for hotel in upgrades:
            self.assertTrue(hotel["suite_upgrade_available"])


if __name__ == "__main__":
    unittest.main()
