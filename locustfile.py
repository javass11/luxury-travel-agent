from locust import HttpUser, task, between
import json


class LuxuryTravelUser(HttpUser):
    """Load test user for luxury travel agent API"""

    wait_time = between(1, 3)

    @task(3)
    def search_flights_and_hotels(self):
        """Most common task - search for flights and hotels"""
        payload = {
            "origin": "ORD",
            "destination": "MIA",
            "departure_date": "2024-06-15",
            "hotel_destination": "Miami Beach, Florida",
            "checkin": "2024-06-15",
            "checkout": "2024-06-22",
            "cabin_class": "Business",
        }
        self.client.post(
            "/api/deals/analyze",
            json=payload,
            name="/api/deals/analyze",
        )

    @task(2)
    def search_flights(self):
        """Search flights endpoint"""
        self.client.get(
            "/api/flights/search?origin=ORD&destination=MIA&departure_date=2024-06-15&cabin_class=Business",
            name="/api/flights/search",
        )

    @task(2)
    def search_hotels(self):
        """Search hotels endpoint"""
        self.client.get(
            "/api/hotels/search?destination=Miami%20Beach,%20Florida&checkin_date=2024-06-15&checkout_date=2024-06-22",
            name="/api/hotels/search",
        )

    @task(1)
    def save_deal(self):
        """Save a deal endpoint"""
        payload = {
            "user_id": "user123",
            "deal_type": "flight",
            "deal_id": "FL001",
            "notes": "Excellent value",
        }
        self.client.post(
            "/api/deals/save",
            json=payload,
            name="/api/deals/save",
        )

    @task(1)
    def health_check(self):
        """Check API health"""
        self.client.get("/api/health", name="/api/health")

    def on_start(self):
        """Called when a user starts"""
        pass

    def on_stop(self):
        """Called when a user stops"""
        pass
