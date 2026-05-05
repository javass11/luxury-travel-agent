import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import LuxuryTravelDB


class TestLuxuryTravelDB(unittest.TestCase):
    def setUp(self):
        self.db = LuxuryTravelDB(":memory:")

    def tearDown(self):
        self.db.close()

    def test_get_flights(self):
        flights = self.db.get_flights("ORD", "MIA", "2024-06-15")
        self.assertIsInstance(flights, list)
        self.assertGreater(len(flights), 0)
        self.assertEqual(flights[0]["origin"], "ORD")
        self.assertEqual(flights[0]["destination"], "MIA")

    def test_get_hotels(self):
        hotels = self.db.get_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
        self.assertIsInstance(hotels, list)
        self.assertGreater(len(hotels), 0)
        self.assertEqual(hotels[0]["destination"], "Miami Beach, Florida")

    def test_get_recent_deals(self):
        deals = self.db.get_recent_deals(limit=5)
        self.assertIsInstance(deals, list)
        self.assertGreaterEqual(len(deals), 1)

    def test_save_deal(self):
        saved_id = self.db.save_deal("user123", "flight", "FL001", "Great deal")
        self.assertIsNotNone(saved_id)
        self.assertIsInstance(saved_id, str)

    def test_get_loyalty_profile(self):
        profile = self.db.get_loyalty_profile("nonexistent_user")
        self.assertIsNone(profile)


if __name__ == "__main__":
    unittest.main()
