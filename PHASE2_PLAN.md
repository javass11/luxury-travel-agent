# Phase 2 Implementation Plan

**Phase 2 Focus:** Advanced filtering, deal analytics, error handling, tax details

## 1. Advanced Filtering System

### New Filter Parameters

**Flight Search Filters:**
- `max_duration_hours` - Max flight duration (e.g., "PT12H")
- `min_duration_hours` - Min flight duration
- `preferred_departure_time` - morning/afternoon/evening/night
- `preferred_arrival_time` - morning/afternoon/evening/night
- `departure_time_window` - specific hours (e.g., "06:00-12:00")
- `arrival_time_window` - specific hours (e.g., "18:00-23:00")
- `exclude_airlines` - Airlines to skip
- `include_airlines` - Only these airlines
- `alliance_filter` - Star Alliance, SkyTeam, oneworld
- `stops_filter` - exact number of stops
- `aircraft_filter` - Preferred aircraft (e.g., "A350", "B787")
- `include_direct_only` - boolean

**Hotel Search Filters:**
- `min_stars` - Minimum star rating
- `max_stars` - Maximum star rating
- `preferred_chains` - Hotel chains (Marriott, Hilton, etc)
- `loyalty_program_exclusive` - only properties earning points
- `amenities` - wifi, pool, gym, breakfast, etc
- `distance_from_airport` - Max km from airport
- `distance_from_city_center` - Max km from city
- `room_type` - Suite, Standard, Deluxe, etc
- `cancellation_policy` - Free, Non-refundable, etc

**Award Search Filters:**
- `min_miles` - Minimum miles required
- `max_miles` - Maximum miles required
- `program_filter` - Specific loyalty program
- `include_cash_plus` - Include points+cash options
- `no_fuel_surcharge` - Exclude high fuel surcharge options

### Implementation
```python
# Update search endpoints to parse and apply filters
# Add filtering logic to handler classes
# Update API documentation
```

---

## 2. Deal Analytics System

### Analytics Endpoints

**Trending Routes:**
```
GET /api/analytics/trending-routes?days=7&limit=10
Response:
{
  "routes": [
    {
      "origin": "JFK",
      "destination": "LAX",
      "popularity_score": 8.5,
      "searches": 1243,
      "bookings": 156,
      "avg_price": 425,
      "best_cpp": 5.2,
      "trend": "up"
    }
  ]
}
```

**Pricing Patterns:**
```
GET /api/analytics/pricing-patterns?origin=JFK&destination=LAX
Response:
{
  "route": "JFK-LAX",
  "best_day_to_search": "Tuesday",
  "best_time_to_book": "5-6 weeks advance",
  "seasonal_patterns": {...},
  "average_lead_time_days": 42,
  "price_volatility": "medium"
}
```

**Deal Insights:**
```
GET /api/analytics/deal-insights?limit=20
Response:
{
  "best_today": [...],      # Best deals right now
  "trending_down": [...],   # Prices falling
  "about_to_expire": [...], # Limited availability
  "underrated": [...]       # Good value, not popular
}
```

**Popular Destinations:**
```
GET /api/analytics/popular-destinations?season=summer
Response:
{
  "destinations": [
    {
      "city": "Paris",
      "iata": "CDG",
      "search_volume": 5432,
      "avg_cpp": 4.8,
      "best_airline": "Air France",
      "best_price": 380
    }
  ]
}
```

### Database Models
- `DealAnalytics` - Route-level analytics
- `UserAnalytics` - Aggregate user behavior
- `SearchLog` - Search history for analysis

---

## 3. Structured Logging & Error Handling

### Logging System

**Current:** Basic Python logging  
**New:** Structured JSON logging with levels

```python
# New logging structure
logger.info({
    'event': 'flight_search',
    'user_id': user_id,
    'origin': 'JFK',
    'destination': 'LHR',
    'results': 42,
    'duration_ms': 234,
    'source': 'amadeus'
})

logger.error({
    'event': 'api_failure',
    'service': 'amadeus',
    'error': 'Connection timeout',
    'retry_count': 3,
    'user_id': user_id
})
```

### Error Handling

**Current:** Generic error responses  
**New:** Detailed error codes and recovery suggestions

```json
{
  "error": "Service temporarily unavailable",
  "error_code": "AMADEUS_API_TIMEOUT",
  "retry_after_seconds": 30,
  "fallback_available": true,
  "suggested_action": "use_demo_data",
  "timestamp": "2026-05-07T10:30:00Z",
  "request_id": "req_abc123"
}
```

---

## 4. Tax & Fee Breakdown

### New Response Format

**Current Flight Response:**
```json
{
  "cash_price": 450,
  "airlines": "United"
}
```

**New Flight Response:**
```json
{
  "base_fare": 350,
  "fuel_surcharge": 25,
  "taxes": {
    "federal": 32.50,
    "international": 5.00,
    "airport": 12.50
  },
  "fees": {
    "airline": 0,
    "booking": 0
  },
  "total_price": 450,
  "currency": "USD",
  "price_breakdown": "Base $350 + Fuel $25 + Taxes $50 = $450",
  "effective_per_mile": 0.15,
  "tax_percentage": 11.1
}
```

### Implementation
- Parse tax details from API responses
- Store in database
- Return in all search results
- Include in analytics

---

## Database Models to Add

### DealAnalytics
```sql
CREATE TABLE deal_analytics (
  id UUID PRIMARY KEY,
  route_key VARCHAR(10),
  origin VARCHAR(3),
  destination VARCHAR(3),
  cabin VARCHAR(20),
  date DATE,
  search_count INT,
  booking_count INT,
  conversion_rate FLOAT,
  avg_price FLOAT,
  min_price FLOAT,
  max_price FLOAT,
  best_cpp FLOAT,
  best_source VARCHAR(50),
  trending BOOLEAN,
  created_at TIMESTAMP
)
```

### UserAnalytics
```sql
CREATE TABLE user_analytics (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  total_searches INT,
  total_saved_deals INT,
  total_bookings INT,
  favorite_routes JSON,
  favorite_airlines JSON,
  avg_booking_lead_days INT,
  preferred_cabin_distribution JSON,
  last_search_date DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### SearchLog
```sql
CREATE TABLE search_logs (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  origin VARCHAR(3),
  destination VARCHAR(3),
  departure_date DATE,
  cabin VARCHAR(20),
  results_count INT,
  filters_applied JSON,
  clicked_result_id VARCHAR,
  booked BOOLEAN,
  duration_ms INT,
  source VARCHAR(50),
  created_at TIMESTAMP
)
```

---

## API Endpoints to Add

### Filtering & Search
- `GET /api/flights/search` - Enhanced with filters
- `GET /api/hotels/search` - Enhanced with filters
- `GET /api/awards/search` - Enhanced with filters

### Analytics (New)
- `GET /api/analytics/trending-routes`
- `GET /api/analytics/pricing-patterns`
- `GET /api/analytics/deal-insights`
- `GET /api/analytics/popular-destinations`
- `GET /api/analytics/search-stats`
- `GET /api/analytics/booking-stats`

### Error Tracking (New)
- `GET /api/admin/errors` - Recent errors (admin only)
- `GET /api/admin/api-health` - Service health status

---

## Implementation Order

1. **Day 1-2:** Add database models & update schema
2. **Day 2-3:** Implement advanced filtering logic
3. **Day 3-4:** Build analytics endpoints
4. **Day 4-5:** Add logging & error handling
5. **Day 5-6:** Tax/fee parsing & response updates
6. **Day 6:** Testing & bug fixes
7. **Day 7:** Documentation & deployment

---

## Success Criteria

- ✅ All filters working on flight/hotel/award searches
- ✅ Analytics endpoints returning meaningful data
- ✅ Structured logging to console/file
- ✅ Tax breakdown in all search responses
- ✅ Error codes for all failure scenarios
- ✅ Database queries optimized with indexes
- ✅ 100% test coverage for new code
- ✅ All existing tests still passing

---

## Estimated Work

- **New Lines of Code:** 1000+
- **New Database Models:** 3
- **New Endpoints:** 10+
- **Time Estimate:** 2-3 days of focused work

Ready to start?
