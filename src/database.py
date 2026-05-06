import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class LuxuryTravelDB:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._init_schema()
        self._seed_sample_data()

    def _init_schema(self):
        cursor = self.connection.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS flights (
                id TEXT PRIMARY KEY,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_date TEXT NOT NULL,
                airline TEXT NOT NULL,
                cabin_class TEXT NOT NULL,
                cash_price REAL NOT NULL,
                miles_cost INTEGER NOT NULL,
                cpp REAL NOT NULL,
                seat_map_url TEXT,
                amenities TEXT,
                elite_benefits TEXT
            );

            CREATE TABLE IF NOT EXISTS hotels (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                destination TEXT NOT NULL,
                checkin_date TEXT NOT NULL,
                checkout_date TEXT NOT NULL,
                cash_rate REAL NOT NULL,
                points_cost INTEGER NOT NULL,
                cpp REAL NOT NULL,
                loyalty_program TEXT NOT NULL,
                elite_nights INTEGER,
                suite_upgrade_available BOOLEAN,
                amenities TEXT
            );

            CREATE TABLE IF NOT EXISTS loyalty_profiles (
                user_id TEXT PRIMARY KEY,
                airline_miles TEXT NOT NULL,
                hotel_points TEXT NOT NULL,
                elite_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_deals (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                deal_type TEXT NOT NULL,
                deal_id TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                notes TEXT
            );
        """)
        self.connection.commit()

    def _seed_sample_data(self):
        cursor = self.connection.cursor()

        sample_flights = [
            ("FL001", "ORD", "MIA", "2024-06-15", "United", "Business", 4500.0, 85000, 5.29, None, None, None),
            ("FL002", "ORD", "MIA", "2024-06-15", "American", "First", 6200.0, 120000, 5.17, None, None, None),
            ("FL003", "ORD", "MIA", "2024-06-15", "Delta", "Business", 3800.0, 75000, 5.07, None, None, None),
        ]

        sample_hotels = [
            ("HT001", "Four Seasons Miami Beach", "Miami Beach, Florida", "2024-06-15", "2024-06-22", 1200.0, 120000, 1.0, "Four Seasons Rewards", 3, True, None),
            ("HT002", "The Ritz-Carlton", "Miami Beach, Florida", "2024-06-15", "2024-06-22", 950.0, 95000, 1.0, "Marriott Bonvoy", 2, True, None),
            ("HT003", "Mandarin Oriental", "Miami Beach, Florida", "2024-06-15", "2024-06-22", 1100.0, 110000, 1.0, "Mandarin Club", 2, False, None),
        ]

        for flight in sample_flights:
            cursor.execute("""
                INSERT OR IGNORE INTO flights
                (id, origin, destination, departure_date, airline, cabin_class, cash_price, miles_cost, cpp, seat_map_url, amenities, elite_benefits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, flight)

        for hotel in sample_hotels:
            cursor.execute("""
                INSERT OR IGNORE INTO hotels
                (id, name, destination, checkin_date, checkout_date, cash_rate, points_cost, cpp, loyalty_program, elite_nights, suite_upgrade_available, amenities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, hotel)

        self.connection.commit()

    def get_flights(self, origin: str, destination: str, departure_date: str) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM flights
            WHERE origin = ? AND destination = ? AND departure_date = ?
            ORDER BY cpp DESC
        """, (origin, destination, departure_date))
        return [dict(row) for row in cursor.fetchall()]

    def get_hotels(self, destination: str, checkin_date: str, checkout_date: str) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM hotels
            WHERE destination = ? AND checkin_date = ? AND checkout_date = ?
            ORDER BY cpp DESC
        """, (destination, checkin_date, checkout_date))
        return [dict(row) for row in cursor.fetchall()]

    def get_recent_deals(self, limit: int = 10) -> List[Dict]:
        cursor = self.connection.cursor()
        flights = cursor.execute("SELECT 'flight' as type, * FROM flights LIMIT ?", (limit,)).fetchall()
        hotels = cursor.execute("SELECT 'hotel' as type, * FROM hotels LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in flights + hotels]

    def save_deal(self, user_id: str, deal_type: str, deal_id: str, notes: Optional[str] = None) -> str:
        import uuid
        saved_id = str(uuid.uuid4())
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO saved_deals (id, user_id, deal_type, deal_id, saved_at, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (saved_id, user_id, deal_type, deal_id, datetime.now().isoformat(), notes))
        self.connection.commit()
        return saved_id

    def get_loyalty_profile(self, user_id: str) -> Optional[Dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM loyalty_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        self.connection.close()
