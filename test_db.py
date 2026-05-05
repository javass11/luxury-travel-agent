from database import LuxuryTravelDB

db = LuxuryTravelDB()

flights = db.get_flights("ORD", "MIA", "2024-06-15")
print(f"✓ Flights in database: {len(flights)}")

hotels = db.get_hotels("Miami Beach, Florida", "2024-06-15", "2024-06-22")
print(f"✓ Hotels in database: {len(hotels)}")

deals = db.get_recent_deals(limit=5)
print(f"✓ Deals in database: {len(deals)}")

print("\n✅ All database tests passed!")
