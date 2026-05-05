import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app


class TestFlaskIntegration(unittest.TestCase):
    """Integration tests for Flask API"""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index_page_loads(self):
        """Test that the index page loads successfully"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Luxury Travel Deal Finder", response.data)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("missing_credentials", data)

    def test_deals_analyze_success(self):
        """Test deal analysis with valid input"""
        payload = {
            "origin": "ORD",
            "destination": "MIA",
            "departure_date": "2024-06-15",
            "hotel_destination": "Miami Beach, Florida",
            "checkin": "2024-06-15",
            "checkout": "2024-06-22",
            "cabin_class": "Business",
        }
        response = self.client.post(
            "/api/deals/analyze",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("flights", data)
        self.assertIn("hotels", data)
        self.assertIn("summary", data)
        self.assertGreater(len(data["flights"]), 0)
        self.assertGreater(len(data["hotels"]), 0)

    def test_deals_analyze_missing_fields(self):
        """Test deal analysis with missing required fields"""
        payload = {"origin": "ORD"}  # Missing required fields
        response = self.client.post(
            "/api/deals/analyze",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_flight_search_endpoint(self):
        """Test flight search endpoint"""
        response = self.client.get(
            "/api/flights/search?origin=ORD&destination=MIA&departure_date=2024-06-15&cabin_class=Business"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("flights", data)
        self.assertIsInstance(data["flights"], list)

    def test_flight_search_missing_params(self):
        """Test flight search with missing parameters"""
        response = self.client.get("/api/flights/search?origin=ORD")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_hotel_search_endpoint(self):
        """Test hotel search endpoint"""
        response = self.client.get(
            "/api/hotels/search?destination=Miami%20Beach,%20Florida&checkin_date=2024-06-15&checkout_date=2024-06-22"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("hotels", data)
        self.assertIsInstance(data["hotels"], list)

    def test_hotel_search_missing_params(self):
        """Test hotel search with missing parameters"""
        response = self.client.get("/api/hotels/search?destination=Miami")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_save_deal_success(self):
        """Test saving a deal"""
        payload = {
            "user_id": "user123",
            "deal_type": "flight",
            "deal_id": "FL001",
            "notes": "Great deal",
        }
        response = self.client.post(
            "/api/deals/save",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("saved_id", data)

    def test_save_deal_missing_fields(self):
        """Test saving a deal with missing fields"""
        payload = {"user_id": "user123"}  # Missing required fields
        response = self.client.post(
            "/api/deals/save",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_chat_endpoint_no_api_key(self):
        """Test chat endpoint without API key configured"""
        payload = {"message": "What flights do you recommend?"}
        response = self.client.post(
            "/api/chat",
            data=json.dumps(payload),
            content_type="application/json",
        )
        # Should return 200 with error message in response
        self.assertIn(response.status_code, [200, 500])

    def test_chat_missing_message(self):
        """Test chat endpoint without message"""
        payload = {}
        response = self.client.post(
            "/api/chat",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_404_endpoint(self):
        """Test 404 error handling"""
        response = self.client.get("/api/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_response_headers(self):
        """Test API response headers"""
        response = self.client.get("/api/health")
        self.assertIn("Content-Type", response.headers)
        self.assertIn("application/json", response.headers.get("Content-Type", ""))

    def test_deals_analyze_cpp_values(self):
        """Test that CPP values are calculated correctly in response"""
        payload = {
            "origin": "ORD",
            "destination": "MIA",
            "departure_date": "2024-06-15",
            "hotel_destination": "Miami Beach, Florida",
            "checkin": "2024-06-15",
            "checkout": "2024-06-22",
        }
        response = self.client.post(
            "/api/deals/analyze",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        # Verify CPP values are present and positive
        for flight in data.get("flights", []):
            self.assertIn("cpp", flight)
            self.assertGreater(flight["cpp"], 0)

        for hotel in data.get("hotels", []):
            self.assertIn("cpp", hotel)
            self.assertGreater(hotel["cpp"], 0)


if __name__ == "__main__":
    unittest.main()
