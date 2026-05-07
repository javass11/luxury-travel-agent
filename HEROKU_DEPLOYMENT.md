# Heroku Deployment Guide

**Status:** Ready for deployment  
**Last Updated:** May 7, 2026  
**Python Version:** 3.11.5  
**Database:** PostgreSQL

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Heroku CLI installed**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   
   # Windows
   # Download from https://cli-assets.heroku.com/heroku-x64.exe
   ```

2. **Heroku account** - Sign up at https://www.heroku.com

3. **Git repository** - Already set up ✅

4. **Production SECRET_KEY** - Generate a strong key (32+ characters)

---

## 🚀 Step-by-Step Deployment

### Step 1: Login to Heroku

```bash
heroku login
```

This will open a browser to authenticate. Return to terminal once authenticated.

---

### Step 2: Create Heroku App

```bash
# Create app with unique name
heroku create luxury-travel-agent  # Replace with your unique app name

# Verify it was created
heroku apps
```

**Output should show:**
```
luxury-travel-agent       https://luxury-travel-agent.herokuapp.com/
```

---

### Step 3: Add PostgreSQL Database

```bash
# Add PostgreSQL add-on (free tier available)
heroku addons:create heroku-postgresql:hobby-dev --app luxury-travel-agent

# Verify database was created
heroku pg:info --app luxury-travel-agent
```

**This will automatically set `DATABASE_URL` environment variable.**

---

### Step 4: Configure Environment Variables

```bash
# Generate a secure SECRET_KEY (example using OpenSSL)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: aB_cDefg-HijKL_MnOpQrStUvWxYz-AbCdE1FgH2Ij3

# Set environment variables
heroku config:set SECRET_KEY="your-generated-secret-key" --app luxury-travel-agent
heroku config:set DEBUG=false --app luxury-travel-agent
heroku config:set CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com" --app luxury-travel-agent

# Optional: Set API keys if you have them
heroku config:set AMADEUS_CLIENT_ID="your-key" --app luxury-travel-agent
heroku config:set AMADEUS_CLIENT_SECRET="your-secret" --app luxury-travel-agent
```

**Verify configuration:**
```bash
heroku config --app luxury-travel-agent
```

---

### Step 5: Deploy Code

```bash
# Push code to Heroku
git push heroku claude/hero-landing-page-pi6vV:main

# Or if you're on main branch
git push heroku main
```

**Wait for deployment to complete.** Output will show:
```
Collecting dependencies... done
Installing dependencies... done
Detecting process types... web
Launching... done, v123
https://luxury-travel-agent.herokuapp.com/ deployed to Heroku
```

---

### Step 6: Run Database Migrations

```bash
# Create all tables
heroku run python -c "from src.app import app; from src.models import db; \
  app.app_context().push(); db.create_all(); print('✓ Tables created')" \
  --app luxury-travel-agent
```

**Expected output:**
```
Redis connection failed, using in-memory cache
✓ Tables created
```

---

### Step 7: Create Admin User

```bash
# Create an admin user in production
heroku run python << 'EOF' --app luxury-travel-agent
from src.app import app
from src.models import db, User, LoyaltyProfile

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(email='admin@luxurytravelagent.com').first()
    
    if not admin:
        admin = User(
            email='admin@luxurytravelagent.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('ChangeMe123!')  # Change this immediately after
        
        loyalty_profile = LoyaltyProfile(user=admin)
        
        db.session.add(admin)
        db.session.add(loyalty_profile)
        db.session.commit()
        
        print('✓ Admin user created')
        print('  Email: admin@luxurytravelagent.com')
        print('  Password: ChangeMe123!')
        print('  ⚠️  Change password immediately after first login!')
    else:
        print('ℹ️  Admin user already exists')
EOF
```

---

### Step 8: View Logs and Test

```bash
# View recent logs
heroku logs --tail --app luxury-travel-agent

# Test the API
curl https://luxury-travel-agent.herokuapp.com/api/health

# Expected response:
# {"status":"healthy","database":"healthy","missing_credentials":[...]}
```

---

### Step 9: Set Domain Name (Optional)

```bash
# Add custom domain
heroku domains:add app.yourdomain.com --app luxury-travel-agent

# Update CORS_ORIGINS with your domain
heroku config:set CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com" \
  --app luxury-travel-agent
```

---

## 🔐 Important Security Notes

### 1. Change Admin Password Immediately
```bash
heroku run python << 'EOF' --app luxury-travel-agent
from src.app import app
from src.models import db, User

with app.app_context():
    admin = User.query.filter_by(email='admin@luxurytravelagent.com').first()
    if admin:
        admin.set_password('YourNewSecurePassword123!')
        db.session.commit()
        print('✓ Admin password updated')
EOF
```

### 2. Never Commit .env Files
```bash
# Verify .env is in .gitignore
cat .gitignore | grep "^\.env"

# Should show: .env
```

### 3. Monitor Environment Variables
```bash
# Don't log or expose SECRET_KEY
heroku config --app luxury-travel-agent | grep -v SECRET_KEY
```

### 4. Enable HTTPS
Heroku automatically provides HTTPS. Verify your app redirects HTTP to HTTPS:
```bash
curl -I http://luxury-travel-agent.herokuapp.com/api/health
# Should show 301 redirect to https://
```

---

## 🧪 Post-Deployment Testing

### Test Health Endpoint
```bash
curl -X GET https://luxury-travel-agent.herokuapp.com/api/health
```

### Test User Registration
```bash
curl -X POST https://luxury-travel-agent.herokuapp.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Test Login
```bash
curl -X POST https://luxury-travel-agent.herokuapp.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Test Flight Search
```bash
curl -X GET "https://luxury-travel-agent.herokuapp.com/api/flights/search?origin=JFK&destination=LAX&departure_date=2026-07-15"
```

---

## 📊 Monitoring

### View Logs in Real-Time
```bash
heroku logs --tail --app luxury-travel-agent
```

### Check Dyno Status
```bash
heroku ps --app luxury-travel-agent
```

### Monitor Database
```bash
# Database info
heroku pg:info --app luxury-travel-agent

# Database size
heroku pg:psql --command="SELECT pg_size_pretty(pg_database_size(current_database()));" --app luxury-travel-agent
```

### View Metrics
```bash
# Open Heroku dashboard
heroku open --app luxury-travel-agent
# Then go to Metrics tab to see CPU, memory, response time
```

---

## 🔄 Updates and Redeployment

### Deploy New Code
```bash
# Make changes locally
git add .
git commit -m "Your changes"

# Push to Heroku
git push heroku main
```

### Rollback to Previous Version
```bash
# View releases
heroku releases --app luxury-travel-agent

# Rollback to previous
heroku releases:rollback v123 --app luxury-travel-agent
```

### Run Migrations After Updates
```bash
heroku run python -c "from src.app import app; from src.models import db; \
  app.app_context().push(); db.create_all()" --app luxury-travel-agent
```

---

## 🆘 Troubleshooting

### App Won't Start
```bash
# Check logs
heroku logs --tail --app luxury-travel-agent

# Common issues:
# - Missing SECRET_KEY
# - DATABASE_URL not set
# - Port not set to 0.0.0.0:$PORT
```

### Database Connection Failed
```bash
# Verify DATABASE_URL is set
heroku config:get DATABASE_URL --app luxury-travel-agent

# Reset database if needed (WARNING: deletes all data)
heroku pg:reset DATABASE --app luxury-travel-agent --confirm luxury-travel-agent
```

### 502 Bad Gateway
```bash
# Check if dyno is running
heroku ps --app luxury-travel-agent

# Restart dyno
heroku dyno:restart --app luxury-travel-agent

# Check logs for errors
heroku logs --tail --app luxury-travel-agent
```

### Email Not Sending
```bash
# Check SMTP configuration
heroku config:get SMTP_ENABLED --app luxury-travel-agent
heroku config:get SMTP_HOST --app luxury-travel-agent

# In production, email returns False if not configured
# This is intentional - configure SMTP or use email service provider
```

---

## 💰 Cost Estimate

**Free Tier (Recommended for testing):**
- Dyno (web): Free ($0/month)
- PostgreSQL: hobby-dev ($0/month)
- Total: $0/month

**Hobby Tier (Small production):**
- Dyno (web): $7/month
- PostgreSQL: hobby-basic $9/month (or higher)
- Total: $16/month

**Professional Tier (High traffic):**
- Dyno (web): $50+/month (Standard 2x)
- PostgreSQL: Standard $50+/month
- Total: $100+/month

---

## 📱 Frontend Deployment

After backend is deployed, deploy frontend to:
- **Vercel** (recommended for React) - Free tier available
- **Netlify** - Free tier available
- **Heroku** - Use different app instance
- **S3 + CloudFront** - AWS solution

**Frontend CORS_ORIGINS will be:**
```
https://app.yourdomain.com,https://www.yourdomain.com
```

---

## ✅ Deployment Checklist

- [ ] Heroku CLI installed and authenticated
- [ ] App created on Heroku
- [ ] PostgreSQL add-on added
- [ ] SECRET_KEY generated and set
- [ ] DEBUG set to false
- [ ] CORS_ORIGINS configured
- [ ] Code pushed to Heroku
- [ ] Database migrations run
- [ ] Admin user created
- [ ] Health endpoint tested (✓ healthy)
- [ ] User registration tested
- [ ] Login tested
- [ ] Flight search tested
- [ ] Admin password changed
- [ ] .env added to .gitignore
- [ ] Logs monitored
- [ ] DNS configured (if using custom domain)
- [ ] Frontend ready for deployment

---

## 🎯 Next Steps

1. **Deploy frontend** to Vercel/Netlify
2. **Configure frontend API endpoint** to use Heroku URL
3. **Test full application** end-to-end
4. **Set up monitoring** (Heroku Metrics, Sentry, etc.)
5. **Configure email service** (SendGrid, Gmail, etc.)
6. **Set up SSL certificate** (Heroku provides automatic)
7. **Configure custom domain**
8. **Monitor and scale** as needed

---

**Deployment Status:** Ready ✅  
**Estimated Time:** 15 minutes  
**Difficulty:** Easy (step-by-step automated)
