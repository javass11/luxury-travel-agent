# MVP Requirements - Minimal Viable Product

This document focuses on the **absolute minimum needed** to launch a functioning platform.

## Current State Assessment

### ✅ What Works
- REST API endpoints (6 endpoints)
- Database layer (SQLite with sample data)
- Flight search engine
- Hotel search engine
- CPP calculations
- LLM chat assistant
- Premium UI
- Comprehensive tests

### ❌ What's Missing for MVP

| Feature | Status | Impact | Effort |
|---------|--------|--------|--------|
| User Authentication | ❌ Missing | CRITICAL | 2-3 days |
| Persistent Database | ❌ Missing | CRITICAL | 2-3 days |
| Real Flight Data | ❌ Missing | CRITICAL | 2-3 days |
| Real Hotel Data | ❌ Missing | CRITICAL | 2-3 days |
| User Profiles | ❌ Missing | CRITICAL | 1-2 days |
| Error Handling | ⚠️ Partial | HIGH | 1 day |
| API Credentials | ⚠️ Partial | HIGH | 0.5 days |
| Email Verification | ❌ Missing | MEDIUM | 1 day |

## MVP Scope Definition

### Must Have (for MVP)
1. User registration & login
2. Real flight data from APIs
3. Real hotel data from APIs
4. User can save deals
5. Loyalty profile setup
6. Basic error handling
7. User dashboard

### Should Have (soon after)
1. Email notifications
2. Deal alerts
3. Advanced search filters
4. Mobile responsive design
5. Logging & monitoring

### Nice to Have (later)
1. Booking integration
2. Payment processing
3. Admin dashboard
4. Analytics
5. Mobile app

## Critical Path to Launch

### Week 1: Foundation
```
Day 1-2: User Authentication
  └─ Register/Login/Logout
  └─ JWT tokens
  └─ Password hashing

Day 3-4: Database Persistence
  └─ Switch to PostgreSQL
  └─ User model
  └─ Loyalty profile model
  └─ Saved deals storage

Day 5: API Credentials Setup
  └─ Environment variable configuration
  └─ Credential validation
  └─ Error handling when missing
```

### Week 2: Real Data Integration
```
Day 1-2: Flight API Integration
  └─ Amadeus setup
  └─ Replace sample data
  └─ Real pricing
  └─ Real availability

Day 3-4: Hotel API Integration
  └─ Hotel API setup
  └─ Real rates
  └─ Real availability
  └─ Elite benefits data

Day 5: Testing & Fixes
  └─ Integration tests
  └─ Error scenarios
  └─ API rate limiting
```

### Week 3: Features & Polish
```
Day 1-2: User Dashboard
  └─ View saved deals
  └─ Loyalty profile display
  └─ Search history

Day 3: Error Handling & Validation
  └─ Graceful API failures
  └─ User-friendly errors
  └─ Fallback strategies

Day 4-5: Testing & Deployment
  └─ Full test suite
  └─ Docker setup
  └─ CI/CD pipeline
  └─ Deploy to staging
```

## Detailed MVP Requirements

### 1. User Authentication (Critical)

**What to build:**
```python
# New endpoints needed:
POST   /api/auth/register      # Create account
POST   /api/auth/login         # Login with email/password
POST   /api/auth/logout        # Logout
POST   /api/auth/refresh       # Refresh JWT token
GET    /api/auth/me            # Get current user
POST   /api/auth/password-reset # Reset password
```

**Data Model:**
```python
class User:
    id: str
    email: str (unique)
    password: str (hashed)
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

**Implementation:**
- [ ] Flask-JWT-Extended for JWT management
- [ ] Bcrypt for password hashing
- [ ] Email validation
- [ ] Password reset flow

**Estimated Time:** 2-3 days

### 2. Persistent Database (Critical)

**Migration from SQLite to PostgreSQL:**

```bash
# Install
pip install flask-sqlalchemy alembic psycopg2-binary

# Setup PostgreSQL
docker run --name postgres \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=luxury_travel \
  -p 5432:5432 \
  -d postgres:15
```

**Models to create:**
```python
User
├─ id (PK)
├─ email (unique)
├─ password_hash
├─ profile (relationship to LoyaltyProfile)
├─ saved_deals (relationship to SavedDeal)
└─ chat_history (relationship to ChatMessage)

LoyaltyProfile
├─ id (PK)
├─ user_id (FK)
├─ airline_miles (JSON)
├─ hotel_points (JSON)
├─ elite_status (JSON)

SavedDeal
├─ id (PK)
├─ user_id (FK)
├─ deal_type (flight/hotel)
├─ deal_data (JSON)
├─ saved_at

ChatMessage
├─ id (PK)
├─ user_id (FK)
├─ message
├─ response
├─ created_at
```

**Setup:**
```bash
# Alembic for migrations
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Estimated Time:** 2-3 days

### 3. Real Flight Data (Critical)

**Option A: Amadeus API (Recommended)**
```python
# Implementation needed:
class AmadeusFlightAPI:
    def search_flights(self, origin, destination, departure_date):
        # Call: GET /v2/shopping/flight-offers
        # Return: Real flight data with prices & miles cost
        pass
    
    def get_flight_details(self, flight_id):
        # Get seat maps, amenities
        pass
```

**Integration Points:**
```python
# Replace in src/app.py
@app.route('/api/flights/search')
def search_flights():
    # OLD: return db.get_flights(...)
    # NEW: return amadeus.search_flights(...)
```

**Estimated Time:** 2-3 days

### 4. Real Hotel Data (Critical)

**Option A: Marriott / Hilton APIs**
```python
class HotelAPI:
    def search_hotels(self, destination, checkin, checkout):
        # Get real availability
        # Get real pricing
        # Get elite benefits
        pass
```

**Estimated Time:** 2-3 days

### 5. User Profiles (Critical)

**New endpoints:**
```python
POST   /api/profile              # Create/update profile
GET    /api/profile              # Get user profile
POST   /api/profile/loyalty      # Add loyalty account
DELETE /api/profile/loyalty/{id} # Remove loyalty account
```

**UI needed:**
```html
<!-- Profile page -->
<form>
  <!-- Personal info -->
  <input name="first_name" />
  <input name="last_name" />
  
  <!-- Loyalty programs -->
  <select name="airline">
    <option>United Airlines</option>
    <option>American Airlines</option>
  </select>
  <input name="miles_balance" type="number" />
  <input name="elite_status" />
</form>
```

**Estimated Time:** 1-2 days

### 6. Error Handling (High Priority)

**What needs fixing:**
```python
# Current: Returns 500 if API unavailable
# Needed: Graceful degradation

@app.route('/api/flights/search')
def search_flights():
    try:
        flights = external_api.search()
    except APIUnavailableError:
        # Return cached data or empty result
        return {
            "flights": [],
            "error": "Live data unavailable. Showing cached results.",
            "cached": True,
            "cached_at": "2026-05-05T10:00:00Z"
        }
```

**Required:**
- [ ] API timeout handling (30 second timeout)
- [ ] Fallback to cache
- [ ] User-friendly error messages
- [ ] Logging of errors
- [ ] Rate limiting (prevent hammering APIs)

**Estimated Time:** 1 day

### 7. Configuration Management (High Priority)

**Current state:** Hardcoded or .env file
**Needed:** Secure credential management

```python
# .env file
AMADEUS_CLIENT_ID=xxxx
AMADEUS_CLIENT_SECRET=xxxx
DUFFEL_ACCESS_TOKEN=xxxx
SEATS_AERO_API_KEY=xxxx
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=secure_random_string
```

**In production:** Use environment secrets
```bash
# GitHub Actions
AWS Secrets Manager
Google Cloud Secret Manager
Vault
```

**Estimated Time:** 0.5 days

## Implementation Order (Critical Path)

### Phase 1: Foundation (5 days)
1. ✅ Database persistence (PostgreSQL + SQLAlchemy)
2. ✅ User authentication (Register/Login)
3. ✅ Configuration management
4. ✅ Update tests

### Phase 2: Real Data (5 days)
1. ✅ Flight API integration (Amadeus)
2. ✅ Hotel API integration
3. ✅ Error handling for API failures
4. ✅ Caching strategy

### Phase 3: Features (3 days)
1. ✅ User profile management
2. ✅ Saved deals persistence
3. ✅ User dashboard
4. ✅ Testing

### Phase 4: Deployment (2 days)
1. ✅ Docker setup
2. ✅ CI/CD pipeline
3. ✅ Staging environment
4. ✅ Production deployment

## Code Changes Summary

### New Files to Create
```
src/
├── models.py          → Database models
├── auth.py            → Authentication logic
├── external_apis/
│   ├── amadeus.py     → Amadeus API client
│   ├── hotel_api.py   → Hotel API client
│   └── cache.py       → Redis cache wrapper
└── config.py          → Updated with DB config

migrations/           → Alembic migrations
```

### Files to Modify
```
src/
├── app.py             → Add auth routes, update API routes
├── database.py        → Switch to SQLAlchemy
├── flights.py         → Use real API instead of DB
├── hotels.py          → Use real API instead of DB
└── requirements.txt   → Add new dependencies
```

### New Dependencies
```
flask-sqlalchemy==3.0.0
flask-jwt-extended==4.5.0
python-dotenv==1.0.0
psycopg2-binary==2.9.0
alembic==1.11.0
redis==5.0.0
requests==2.31.0
bcrypt==4.0.0
```

## Success Criteria for MVP

- [ ] Users can register and login
- [ ] Real flight data displays (from Amadeus)
- [ ] Real hotel data displays (from API)
- [ ] Users can save deals to their profile
- [ ] Users can view their loyalty profile
- [ ] Search works with real pricing
- [ ] CPP calculations use real data
- [ ] Errors handled gracefully
- [ ] All tests pass (>90% coverage)
- [ ] Can deploy with Docker
- [ ] CI/CD pipeline working

## Launch Checklist

**Week 1 Before Launch:**
- [ ] Security audit
- [ ] Load testing (100 concurrent users)
- [ ] Data backup strategy
- [ ] Disaster recovery plan
- [ ] Documentation complete
- [ ] User guide created
- [ ] FAQ page
- [ ] Support email setup

**Day Before Launch:**
- [ ] Final code review
- [ ] Deploy to staging
- [ ] Full regression testing
- [ ] Performance testing
- [ ] Backup database
- [ ] Monitor alerts setup

**Launch Day:**
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Check API integrations
- [ ] Verify email sending
- [ ] Monitor database performance
- [ ] Have team on standby

**Week After Launch:**
- [ ] Monitor user feedback
- [ ] Fix critical bugs
- [ ] Monitor costs (APIs, hosting)
- [ ] Optimize slow queries
- [ ] Plan Phase 2 features

## Budget Estimate

| Item | Cost | Notes |
|------|------|-------|
| **Development** | $15k-$25k | 2-3 devs, 3 weeks |
| **External APIs** | $500-$2k/month | Depends on usage |
| **Database (PostgreSQL)** | $15-$100/month | AWS RDS or DigitalOcean |
| **Hosting** | $50-$500/month | AWS/Heroku/DigitalOcean |
| **Email Service** | $10-$100/month | SendGrid or AWS SES |
| **Monitoring** | $50-$300/month | Sentry, DataDog |
| **Domain + SSL** | $12-$100/year | Auto with hosting |
| **Testing/QA** | Included | Automated tests + manual |

**Total First Month: ~$2.5k-$4k**
**Total Ongoing: ~$1k-$3k/month**

## Timeline Summary

```
Week 1: Database + Authentication (Days 1-5)
Week 2: API Integration (Days 1-5)
Week 3: Features + Testing (Days 1-5)
Deployment: Days 1-3
Launch: Day 4-5

Total: 3 weeks for MVP
```

## Next Steps

1. **Decide on approach:**
   - Build MVP (3 weeks)
   - Build Phase 2 (2 weeks)
   - Launch (1 week)

2. **Get team/resources:**
   - 2-3 developers
   - 1 product manager
   - 1 QA tester

3. **Setup infrastructure:**
   - PostgreSQL database
   - Redis cache
   - API credentials (Amadeus, hotels, etc.)
   - GitHub repo with CI/CD

4. **Start Phase 1:**
   - Database migration
   - Authentication system
   - Configuration management

---

**Recommendation:** Start with Phase 1 (Database + Auth). This is the foundation everything else depends on.
