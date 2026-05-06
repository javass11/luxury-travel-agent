# Step 3: Implement Real API Integration

Transform the demo app with real flight and hotel data from production APIs.

## Overview

Replace hardcoded sample data (from `LuxuryTravelDB`) with live pricing and availability from real travel APIs.

## Architecture

```
┌─────────────────────────────────────────┐
│        Flask App (Protected Routes)     │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┬──────────────┐
    │                     │              │
┌───▼────────────┐  ┌────▼───────┐  ┌──▼──────────┐
│ Amadeus Flight │  │ Hotel APIs │  │ Caching     │
│   + Pricing    │  │   + Rates  │  │  Layer      │
└────────────────┘  └────────────┘  └─────────────┘
```

## APIs to Integrate

### 1. Amadeus Flight API (Recommended)

**Why:** Industry standard, comprehensive, extensive testing sandbox

**Setup:**
```bash
# Install Amadeus SDK
pip install amadeus
```

**Credentials:**
- API Key: https://developers.amadeus.com
- API Secret: (from same dashboard)
- Free tier: 2,000 calls/month

**Example Implementation:**
```python
from amadeus import Client, ResponseError

class AmadeusFlightAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.amadeus = Client(
            client_id=api_key,
            client_secret=api_secret,
            environment='production'  # 'test' for sandbox
        )
    
    def search_flights(self, origin: str, destination: str, 
                       departure_date: str, cabin_class: str = None) -> List[Dict]:
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=1,
                travelClass=cabin_class or 'ECONOMY'
            )
            return self._parse_flights(response.data)
        except ResponseError as error:
            print(f"API Error: {error.response.status_code} - {error}")
            return []
    
    def _parse_flights(self, flights: List) -> List[Dict]:
        results = []
        for flight in flights:
            results.append({
                'id': flight['id'],
                'airline': flight['validatingAirlineCodes'][0],
                'origin': flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                'destination': flight['itineraries'][-1]['segments'][-1]['arrival']['iataCode'],
                'departure_date': flight['itineraries'][0]['segments'][0]['departure']['at'].split('T')[0],
                'cabin_class': 'ECONOMY',  # from flight['class']
                'cash_price': float(flight['price']['total']),
                'miles_cost': self._estimate_miles(float(flight['price']['total'])),
                'cpp': self._calculate_cpp(float(flight['price']['total']))
            })
        return sorted(results, key=lambda x: x['cpp'], reverse=True)
    
    def _estimate_miles(self, cash_price: float) -> int:
        # Typical award chart: $500 = 50,000 miles, etc.
        return int((cash_price / 1000) * 5000)  # Rough estimate
    
    def _calculate_cpp(self, cash_price: float) -> float:
        miles = self._estimate_miles(cash_price)
        return cash_price / miles if miles > 0 else 0.0
```

### 2. Hotel Search API - Google Hotels API (Alternative)

**Why:** Free tier available, integrates with search results

**Setup:**
```bash
pip install google-hotels-api
```

**Alternative: Hotel Tonight API**
- Simple REST API
- Real-time availability
- Free tier: 1,000 calls/day

### 3. Booking.com API (Production)

**Why:** Largest hotel inventory, affiliates program

**Credentials:** https://affiliates.booking.com/
- Partner ID
- API Key

## Implementation Steps

### Step 1: Create API Wrapper Classes

Create `src/api_clients/amadeus.py`:

```python
import os
from typing import List, Dict, Optional
from amadeus import Client, ResponseError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AmadeusClient:
    def __init__(self):
        self.client = Client(
            client_id=os.getenv('AMADEUS_API_KEY'),
            client_secret=os.getenv('AMADEUS_API_SECRET'),
            environment='production'
        )
    
    def search_flights(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str,
        cabin_class: Optional[str] = None,
        adults: int = 1
    ) -> List[Dict]:
        """Search for flights using Amadeus API"""
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                travelClass=cabin_class or 'ECONOMY'
            )
            
            if not response.data:
                return []
            
            return [self._format_flight(f) for f in response.data]
        except ResponseError as e:
            logger.error(f"Amadeus API error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Flight search failed: {str(e)}")
            return []
    
    def _format_flight(self, flight: Dict) -> Dict:
        """Convert Amadeus response to standard format"""
        first_segment = flight['itineraries'][0]['segments'][0]
        last_segment = flight['itineraries'][-1]['segments'][-1]
        
        cash_price = float(flight['price']['total'])
        miles_cost = self._estimate_miles(cash_price)
        
        return {
            'id': flight['id'],
            'airline': flight['validatingAirlineCodes'][0],
            'origin': first_segment['departure']['iataCode'],
            'destination': last_segment['arrival']['iataCode'],
            'departure_date': first_segment['departure']['at'].split('T')[0],
            'cash_price': cash_price,
            'miles_cost': miles_cost,
            'cpp': cash_price / miles_cost if miles_cost > 0 else 0.0,
            'cabin_class': 'ECONOMY',
            'duration': flight['itineraries'][0].get('duration'),
            'stops': len(flight['itineraries'][0]['segments']) - 1
        }
    
    def _estimate_miles(self, cash_price: float) -> int:
        """Estimate miles based on cash price"""
        if cash_price < 200:
            return 10000
        elif cash_price < 500:
            return 25000
        elif cash_price < 1000:
            return 50000
        else:
            return 100000
```

Create `src/api_clients/hotels.py`:

```python
import os
from typing import List, Dict, Optional
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HotelsAPIClient:
    def __init__(self):
        self.base_url = "https://api.booking.com/v1"  # Example
        self.api_key = os.getenv('BOOKING_API_KEY')
    
    def search_hotels(
        self,
        destination: str,
        checkin_date: str,
        checkout_date: str,
        guests: int = 1
    ) -> List[Dict]:
        """Search hotels using Booking.com API"""
        try:
            response = requests.get(
                f"{self.base_url}/hotels/search",
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={
                    'destination': destination,
                    'checkin': checkin_date,
                    'checkout': checkout_date,
                    'guests': guests
                },
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Hotels API error: {response.status_code}")
                return []
            
            return [self._format_hotel(h) for h in response.json().get('hotels', [])]
        except requests.Timeout:
            logger.error("Hotels API timeout")
            return []
        except Exception as e:
            logger.error(f"Hotel search failed: {str(e)}")
            return []
    
    def _format_hotel(self, hotel: Dict) -> Dict:
        """Convert API response to standard format"""
        cash_rate = float(hotel.get('price', {}).get('amount', 0))
        points_cost = self._estimate_points(cash_rate)
        
        return {
            'id': hotel['id'],
            'name': hotel['name'],
            'destination': hotel.get('city', ''),
            'cash_rate': cash_rate,
            'points_cost': points_cost,
            'cpp': cash_rate / points_cost if points_cost > 0 else 0.0,
            'rating': hotel.get('rating'),
            'amenities': hotel.get('amenities', []),
            'image': hotel.get('image_url')
        }
    
    def _estimate_points(self, cash_rate: float) -> int:
        """Estimate points cost based on nightly rate"""
        if cash_rate < 100:
            return 5000
        elif cash_rate < 200:
            return 10000
        elif cash_rate < 300:
            return 15000
        else:
            return 20000
```

### Step 2: Add Caching Layer

Create `src/cache.py`:

```python
import redis
import json
from typing import Optional, Dict, Any
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheClient:
    def __init__(self, redis_url: str = None):
        try:
            self.redis_client = redis.from_url(
                redis_url or 'redis://localhost:6379/0',
                decode_responses=True
            )
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    def flush(self, pattern: str = "*") -> bool:
        """Flush cache keys matching pattern"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache flush failed: {e}")
            return False

# Initialize cache client
cache = CacheClient()
```

### Step 3: Update Flight Search Endpoint

Update `src/app.py`:

```python
from src.api_clients.amadeus import AmadeusClient
from src.cache import cache

amadeus = AmadeusClient()

@app.route("/api/flights/search", methods=["GET"])
def search_flights():
    """Search flights from real Amadeus API"""
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    departure_date = request.args.get("departure_date")
    cabin_class = request.args.get("cabin_class", "ECONOMY")
    
    if not all([origin, destination, departure_date]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Check cache first
    cache_key = f"flights:{origin}:{destination}:{departure_date}:{cabin_class}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"flights": cached, "source": "cache"}), 200
    
    # Fetch from API
    flights = amadeus.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class
    )
    
    if not flights:
        return jsonify({
            "flights": [],
            "source": "fallback",
            "message": "No flights found or API unavailable"
        }), 200
    
    # Cache results for 1 hour
    cache.set(cache_key, flights, ttl=3600)
    
    return jsonify({"flights": flights, "source": "live"}), 200
```

### Step 4: Update Hotel Search Endpoint

```python
from src.api_clients.hotels import HotelsAPIClient

hotels_client = HotelsAPIClient()

@app.route("/api/hotels/search", methods=["GET"])
def search_hotels():
    """Search hotels from real API"""
    destination = request.args.get("destination")
    checkin_date = request.args.get("checkin_date")
    checkout_date = request.args.get("checkout_date")
    
    if not all([destination, checkin_date, checkout_date]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Check cache
    cache_key = f"hotels:{destination}:{checkin_date}:{checkout_date}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"hotels": cached, "source": "cache"}), 200
    
    # Fetch from API
    hotels = hotels_client.search_hotels(
        destination=destination,
        checkin_date=checkin_date,
        checkout_date=checkout_date
    )
    
    if not hotels:
        return jsonify({
            "hotels": [],
            "source": "fallback",
            "message": "No hotels found or API unavailable"
        }), 200
    
    cache.set(cache_key, hotels, ttl=3600)
    
    return jsonify({"hotels": hotels, "source": "live"}), 200
```

## Environment Setup

Add to `.env`:

```bash
# Amadeus API
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
AMADEUS_ENVIRONMENT=production  # or 'test' for sandbox

# Booking.com API
BOOKING_API_KEY=your_booking_api_key

# Redis Cache (Optional - defaults to localhost)
REDIS_URL=redis://localhost:6379/0

# API Timeouts
API_TIMEOUT=10
CACHE_TTL=3600
```

## Testing Real APIs

### Get API Credentials

1. **Amadeus:**
   - Go to https://developers.amadeus.com/
   - Create free account
   - Create app → Get API Key + Secret
   - Use `test` environment first

2. **Booking.com:**
   - Go to https://affiliates.booking.com/
   - Sign up as affiliate
   - Request API access
   - Get API key

3. **Redis (optional, for caching):**
   ```bash
   # Local installation
   brew install redis  # macOS
   redis-server        # Start server
   
   # Or use Docker
   docker run -d -p 6379:6379 redis
   ```

### Test Flight Search

```bash
# Test with real API
python << 'EOF'
from src.api_clients.amadeus import AmadeusClient
from datetime import datetime, timedelta

amadeus = AmadeusClient()

# Search flights tomorrow
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

flights = amadeus.search_flights(
    origin='ORD',
    destination='MIA',
    departure_date=tomorrow,
    cabin_class='ECONOMY'
)

print(f"Found {len(flights)} flights:")
for f in flights[:3]:
    print(f"  - {f['airline']} ${f['cash_price']} ({f['miles_cost']} miles)")
EOF
```

### Test Hotel Search

```bash
python << 'EOF'
from src.api_clients.hotels import HotelsAPIClient
from datetime import datetime, timedelta

hotels_client = HotelsAPIClient()

tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
next_week = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')

hotels = hotels_client.search_hotels(
    destination='Miami Beach, Florida',
    checkin_date=tomorrow,
    checkout_date=next_week
)

print(f"Found {len(hotels)} hotels:")
for h in hotels[:3]:
    print(f"  - {h['name']} ${h['cash_rate']} ({h['points_cost']} points)")
EOF
```

## Error Handling

Implement graceful fallbacks when APIs are unavailable:

```python
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def api_fallback(fallback_data: List[Dict] = None):
    """Decorator to provide fallback when API fails"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API call failed: {str(e)}")
                return fallback_data or []
        return wrapper
    return decorator

@api_fallback(fallback_data=[])
def search_flights_with_fallback(origin, destination, date):
    return amadeus.search_flights(origin, destination, date)
```

## Rate Limiting

Implement rate limiting to avoid API quota exhaustion:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/flights/search", methods=["GET"])
@limiter.limit("10 per minute")  # 10 searches per minute
def search_flights():
    # ...
```

## Deployment

### Heroku Deployment with APIs

```bash
# Set API credentials in Heroku
heroku config:set AMADEUS_API_KEY=xxxx --app your-app-name
heroku config:set AMADEUS_API_SECRET=xxxx --app your-app-name
heroku config:set BOOKING_API_KEY=xxxx --app your-app-name
heroku config:set REDIS_URL=redis://.... --app your-app-name

# Add Redis addon (optional)
heroku addons:create heroku-redis:premium-0 --app your-app-name

# Deploy
git push heroku main
```

## Monitoring

Monitor API health and performance:

```python
from datetime import datetime
import time

class APIMetrics:
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.total_time = 0
    
    def record_request(self, success: bool, duration: float):
        self.requests += 1
        self.total_time += duration
        if not success:
            self.errors += 1
    
    def get_stats(self) -> Dict:
        return {
            'total_requests': self.requests,
            'error_rate': self.errors / self.requests if self.requests > 0 else 0,
            'avg_response_time': self.total_time / self.requests if self.requests > 0 else 0
        }

metrics = APIMetrics()

# Add to endpoints
@app.route("/api/flights/search")
def search_flights():
    start = time.time()
    try:
        # ... search logic
        metrics.record_request(True, time.time() - start)
    except Exception as e:
        metrics.record_request(False, time.time() - start)
        raise
```

View metrics:
```bash
@app.route("/api/metrics", methods=["GET"])
@jwt_required()
def get_metrics():
    return jsonify(metrics.get_stats()), 200
```

## Testing Integration

```bash
# Run integration tests with real APIs
pytest tests/test_api_integration.py -v

# Test caching
pytest tests/test_cache.py -v

# Test error handling
pytest tests/test_api_errors.py -v
```

## Summary

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Setup Amadeus API | 10m | 📋 TODO |
| 2 | Setup Booking API | 10m | 📋 TODO |
| 3 | Create API wrappers | 30m | 📋 TODO |
| 4 | Implement caching | 20m | 📋 TODO |
| 5 | Update endpoints | 20m | 📋 TODO |
| 6 | Error handling | 15m | 📋 TODO |
| 7 | Test locally | 15m | 📋 TODO |
| 8 | Deploy to Heroku | 10m | 📋 TODO |

## Next Steps

1. **Get API credentials** (Amadeus free sandbox)
2. **Implement Amadeus flight search** (highest ROI)
3. **Add caching layer** (Redis)
4. **Implement hotel search**
5. **Deploy to Heroku**
6. **Monitor API performance**

## Resources

- [Amadeus Docs](https://developers.amadeus.com/docs)
- [Amadeus Python SDK](https://github.com/amadeus4dev/amadeus-python)
- [Booking.com Affiliates API](https://affiliates.booking.com/en/api)
- [Redis Docs](https://redis.io/docs/)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
