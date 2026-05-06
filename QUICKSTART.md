# 🚀 Luxury Travel Agent - Complete Quickstart

**Everything is ready to go.** Just follow these simple steps.

## ⚡ 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create environment file
cp .env.example .env

# 3. Start the app
python -m src.app

# 4. Visit
http://localhost:5000
```

That's it! Your app is running.

---

## 📋 What You Get

✅ **User Authentication**
- Register, login, token refresh
- Secure JWT tokens
- Protected endpoints

✅ **Flight & Hotel Search**
- Works with or without API credentials
- Demo data included
- Smart caching

✅ **Redemption Evaluation**
- Compare flights/hotels by value
- CPP (cents per point) calculation
- Find best deals

✅ **All Tests Passing**
- 53 comprehensive tests
- 100% working features
- Production-ready code

✅ **Documentation**
- Beautiful GitHub Pages site
- Complete API reference
- Full deployment guide

---

## 🔧 Full Setup (5 Minutes)

### Step 1: Clone & Install
```bash
cd luxury-travel-agent
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings (optional - works with defaults)
nano .env
```

### Step 3: Start Server
```bash
python -m src.app
```

You'll see:
```
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

### Step 4: Test Everything
```bash
# In another terminal
pytest tests/ -o addopts="" -q
```

Expected: `53 passed` ✅

---

## 💻 Using the App

### 1. Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

**Response includes:** access_token, refresh_token

### 2. Search Flights
```bash
curl "http://localhost:5000/api/flights/search?origin=ORD&destination=MIA&departure_date=2024-06-15"
```

**Returns:** Flights sorted by best value (CPP)

### 3. Search Hotels
```bash
curl "http://localhost:5000/api/hotels/search?destination=Miami&checkin_date=2024-06-15&checkout_date=2024-06-22"
```

**Returns:** Hotels with ratings, amenities, pricing

### 4. Evaluate Redemptions
```bash
curl -X POST http://localhost:5000/api/redemptions/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "options": [
      {
        "name": "JFK to LHR",
        "redemption_type": "flight",
        "cash_price": 4200,
        "points_required": 80000,
        "taxes_and_fees": 350
      },
      {
        "name": "Park Hyatt Paris",
        "redemption_type": "hotel",
        "cash_price": 2400,
        "points_required": 90000
      }
    ]
  }'
```

**Returns:** Ranked by CPP value with best option highlighted

---

## 📚 API Endpoints Quick Reference

### Authentication
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/auth/register` | POST | ❌ | Register user |
| `/api/auth/login` | POST | ❌ | Login user |
| `/api/auth/refresh` | POST | ✅ | Refresh token |
| `/api/auth/me` | GET | ✅ | Get user info |
| `/api/auth/logout` | POST | ✅ | Logout |

### Search
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/flights/search` | GET | ❌ | Search flights |
| `/api/hotels/search` | GET | ❌ | Search hotels |
| `/api/deals/analyze` | POST | ❌ | Analyze flights + hotels |

### Redemptions
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/redemptions/evaluate` | POST | ❌ | Compare & rank redemptions |

### Deals
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/deals/save` | POST | ✅ | Save a deal |
| `/api/chat` | POST | ✅ | Chat with AI |

### Admin
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/cache/stats` | GET | ✅ | View cache stats |
| `/api/cache/flush` | POST | ✅ | Clear cache |
| `/api/health` | GET | ❌ | Health check |

---

## 🎯 Optional: Enable Real APIs

### Amadeus Flight API (Free Sandbox)
1. Go to: https://developers.amadeus.com/
2. Create account → Create app
3. Copy API Key & Secret
4. Add to `.env`:
   ```
   AMADEUS_API_KEY=your_key
   AMADEUS_API_SECRET=your_secret
   ```
5. Restart app → flights now use real data

### Booking.com Hotel API
1. Go to: https://affiliates.booking.com/
2. Request API access
3. Add to `.env`:
   ```
   BOOKING_API_KEY=your_key
   ```
4. Restart app → hotels now use real data

### Redis Caching (Optional)
```bash
# Install Redis
brew install redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis

# Add to .env
REDIS_URL=redis://localhost:6379/0
```

---

## 🚀 Deploy to Heroku (10 Minutes)

### Prerequisites
- Heroku account (free)
- Heroku CLI installed
- This repository

### Step 1: Login to Heroku
```bash
heroku login
```

### Step 2: Create App
```bash
heroku create your-app-name-luxury-travel
```

### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Step 4: Set Environment Variables
```bash
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Optional: API credentials
heroku config:set AMADEUS_API_KEY=your_key
heroku config:set AMADEUS_API_SECRET=your_secret
heroku config:set BOOKING_API_KEY=your_key
```

### Step 5: Deploy
```bash
git push heroku main
```

### Step 6: Run Migrations
```bash
heroku run alembic upgrade head
```

### Step 7: Verify
```bash
curl https://your-app-name-luxury-travel.herokuapp.com/api/health
```

Expected: `{"status": "healthy", ...}`

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `PRODUCTION_IMPLEMENTATION.md` | Complete roadmap & checklist |
| `API_INTEGRATION_QUICK_START.md` | API integration details |
| `STEP2_TESTING_AUTH.md` | Authentication testing guide |
| `STEP3_REAL_API_INTEGRATION.md` | Detailed API implementation |
| `SETUP_HEROKU_POSTGRES.md` | PostgreSQL setup guide |
| `GITHUB_PAGES_SETUP.md` | GitHub Pages setup |
| `TESTING.md` | Complete testing guide |

Visit GitHub Pages: **https://javass11.github.io/luxury-travel-agent**

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -o addopts="" -q
```

Expected: `53 passed` ✅

### Test Specific Feature
```bash
# Auth tests
pytest tests/test_auth.py -o addopts="" -v

# Integration tests
pytest tests/test_integration.py -o addopts="" -v

# Flight tests
pytest tests/test_flights.py -o addopts="" -v
```

### Run with Coverage
```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## 🔐 Security Best Practices

### Before Production
1. **Change SECRET_KEY & JWT_SECRET_KEY**
   ```bash
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

2. **Use Strong Passwords**
   - Min 8 characters
   - Include uppercase, lowercase, numbers

3. **Enable HTTPS**
   - Heroku does this automatically
   - Use SSL certificates for custom domains

4. **Protect API Credentials**
   - Never commit `.env` files
   - Use environment variables
   - Rotate credentials regularly

5. **Enable Rate Limiting**
   - Prevent brute force attacks
   - Already configured in code

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
```bash
# Make sure you're in the correct directory
cd luxury-travel-agent
python -m src.app
```

### "Port 5000 is already in use"
```bash
# Kill the process
lsof -ti:5000 | xargs kill -9

# Or use a different port
python -m src.app --port 8000
```

### "Database connection error"
```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# For local SQLite (default)
DATABASE_URL=sqlite:///luxury_travel.db
```

### "API returns demo data instead of real data"
1. Check if API credentials are set: `heroku config`
2. Verify credentials are correct
3. Check API rate limits
4. Look at logs: `heroku logs --tail`

### "Tests failing"
```bash
# Install missing dependencies
pip install -r requirements.txt

# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +

# Run with verbose output
pytest -vv --tb=short
```

---

## 📊 Project Structure

```
luxury-travel-agent/
├── src/
│   ├── app.py                 # Flask app with all endpoints
│   ├── auth.py                # Authentication blueprint
│   ├── models.py              # SQLAlchemy models
│   ├── redemption.py          # Redemption evaluation
│   ├── cache.py               # Caching layer
│   ├── api_clients/           # Real API integrations
│   │   ├── amadeus.py         # Flight API
│   │   └── hotels.py          # Hotel API
│   └── ...
├── tests/                     # Test suite (53 tests)
├── docs/                      # GitHub Pages site
├── migrations/                # Database migrations
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # Project documentation
```

---

## ✅ Checklist

### Local Development
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy .env: `cp .env.example .env`
- [ ] Run app: `python -m src.app`
- [ ] Run tests: `pytest tests/ -o addopts="" -q`
- [ ] Test endpoints with curl

### Before Deploying
- [ ] All 53 tests passing
- [ ] Created strong SECRET_KEY
- [ ] Reviewed .env file
- [ ] (Optional) Configured API credentials
- [ ] (Optional) Set up Redis

### Heroku Deployment
- [ ] Created Heroku app
- [ ] Added PostgreSQL addon
- [ ] Set environment variables
- [ ] Pushed code: `git push heroku main`
- [ ] Ran migrations: `heroku run alembic upgrade head`
- [ ] Verified health endpoint

### GitHub Pages
- [ ] Made repository public
- [ ] Enabled GitHub Pages (Settings → Pages)
- [ ] Set source: `main` branch, `/docs` folder
- [ ] Verified site is live

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

---

## 📞 Support

### Common Commands

```bash
# Start app
python -m src.app

# Run tests
pytest tests/ -o addopts="" -q

# Run specific test
pytest tests/test_auth.py -o addopts="" -v

# Generate coverage report
pytest --cov=src --cov-report=html

# Check dependencies
pip list

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Get Help

1. Check the documentation files
2. Review test files for examples
3. Check logs: `python -m src.app 2>&1 | head -50`
4. Review error messages carefully
5. Check GitHub issues

---

## 🎉 You're All Set!

Your luxury travel platform is **ready to go**:

✅ **Running locally** → `python -m src.app`  
✅ **All tests passing** → `pytest tests/`  
✅ **Documentation live** → GitHub Pages  
✅ **APIs working** → Demo data + real API support  
✅ **Ready to deploy** → Push to Heroku  

**Next steps:**
1. Run the app locally
2. Test the endpoints
3. Deploy to Heroku
4. Celebrate! 🎊

---

**Need help?** Check the documentation files or review the test examples!

**Status:** Production-Ready ✅  
**Last Updated:** May 6, 2026  
**Version:** 1.0
