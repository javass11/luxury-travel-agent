# 🚀 Deploy to Heroku - 5 Minutes

Your Luxury Travel Agent is ready to deploy. Here's how to get a **live, working website** in 5 minutes.

## Prerequisites

1. **Heroku Account** (free): https://www.heroku.com/
2. **Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

## Deploy in 3 Steps

### Step 1: Install Heroku CLI

**Mac:**
```bash
brew install heroku
```

**Windows:**
Download from: https://devcenter.heroku.com/articles/heroku-cli

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Run Deployment Script

```bash
bash deploy-heroku.sh
```

This script will:
1. Login to Heroku (opens browser)
2. Create your app
3. Add PostgreSQL database
4. Set security keys
5. Deploy your code
6. Run migrations

### Step 3: Visit Your Live Site

After deployment completes, you'll get a URL like:

```
https://luxury-travel-agent-1234567890.herokuapp.com
```

**Visit it in your browser!** 🎉

---

## Manual Deployment (if script doesn't work)

```bash
# 1. Login
heroku login

# 2. Create app
heroku create your-app-name-luxury-travel

# 3. Add database
heroku addons:create heroku-postgresql:hobby-dev

# 4. Set secrets
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# 5. Deploy
git push heroku main

# 6. Run migrations
heroku run alembic upgrade head

# 7. View
heroku open
```

---

## Your Live Site Includes

✅ User authentication (register, login)  
✅ Flight search with demo data  
✅ Hotel search with demo data  
✅ Redemption evaluation  
✅ All 15+ API endpoints  
✅ Complete documentation  

---

## Add Real APIs (Optional)

Once deployed, add API credentials:

```bash
# Amadeus Flight API
heroku config:set AMADEUS_API_KEY=your_key
heroku config:set AMADEUS_API_SECRET=your_secret

# Booking.com Hotel API  
heroku config:set BOOKING_API_KEY=your_key
```

Get credentials:
- Amadeus: https://developers.amadeus.com/
- Booking: https://affiliates.booking.com/

---

## Test Your Live Site

```bash
# Health check
curl https://your-app-name.herokuapp.com/api/health

# Register user
curl -X POST https://your-app-name.herokuapp.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'

# Search flights
curl "https://your-app-name.herokuapp.com/api/flights/search?origin=ORD&destination=MIA&departure_date=2024-06-15"
```

---

## Monitor Your App

```bash
# View logs
heroku logs --tail

# Check app info
heroku apps:info

# View database
heroku pg:info

# Open app
heroku open
```

---

## Troubleshooting

### "Heroku command not found"
- Heroku CLI not installed
- Follow installation link above

### "Permission denied on deploy-heroku.sh"
```bash
chmod +x deploy-heroku.sh
bash deploy-heroku.sh
```

### "PostgreSQL addon failed"
- May be billing issue
- Verify Heroku account
- Try creating app first, then addon

### "Deployment failed"
```bash
# Check logs
heroku logs --tail --app your-app-name
```

---

## You Now Have

✅ **Live Website** - Accessible at public URL  
✅ **Real Database** - PostgreSQL on Heroku  
✅ **All Features** - Working authentication, search, evaluation  
✅ **Scalable** - Can upgrade anytime  
✅ **Professional** - Production-ready deployment  

---

**That's it!** Your luxury travel platform is now live on the internet. 🚀

Share the URL with anyone!

---

**Generated:** May 6, 2026
