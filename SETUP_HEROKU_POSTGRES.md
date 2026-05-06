# Setup PostgreSQL on Heroku (Free Tier)

Complete guide to setup a free PostgreSQL database on Heroku.

## Prerequisites

- Heroku account (free): https://www.heroku.com/
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli
- Your luxury-travel-agent project

## Step 1: Create Heroku App (5 minutes)

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name-luxury-travel

# Example:
heroku create my-luxury-travel-app
```

You should see:
```
Creating ⬢ my-luxury-travel-app... done
https://my-luxury-travel-app.herokuapp.com/
git remote heroku added
```

## Step 2: Add PostgreSQL Database (2 minutes)

```bash
# Add the free Postgres addon
heroku addons:create heroku-postgresql:hobby-dev --app my-luxury-travel-app
```

You should see:
```
Creating heroku-postgresql:hobby-dev on ⬢ my-luxury-travel-app... free
```

## Step 3: Get Your Database URL (1 minute)

```bash
# View your database URL
heroku config --app my-luxury-travel-app
```

You should see:
```
DATABASE_URL: postgresql://user:pass@host:5432/dbname
```

**Copy this URL** - you'll need it next.

## Step 4: Update Your .env File (2 minutes)

In your project, update `.env`:

```bash
# Replace the DATABASE_URL with your Heroku PostgreSQL URL
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## Step 5: Test Connection (5 minutes)

Run this Python script to test the connection:

```bash
python << 'EOF'
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f"✅ Connected to PostgreSQL!")
    print(f"✅ Version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

Expected output:
```
✅ Connected to PostgreSQL!
✅ Version: PostgreSQL 13.x...
```

## Step 6: Run Migrations (2 minutes)

```bash
# Apply database migrations
alembic upgrade head
```

You should see:
```
INFO  [alembic.runtime.migration] Running upgrade ... Create user authentication tables
```

## Step 7: Verify Tables Created (1 minute)

```bash
python << 'EOF'
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public'
""")
tables = cursor.fetchall()
print("✅ Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
cursor.close()
conn.close()
EOF
```

Expected output:
```
✅ Tables in database:
  - users
  - loyalty_profiles
  - saved_deals
  - chat_messages
```

## All Done! ✅

Your PostgreSQL database is now ready to use. Your user data will persist even after the app restarts.

### Useful Commands

```bash
# View database info
heroku config --app my-luxury-travel-app

# View database stats
heroku pg:info --app my-luxury-travel-app

# Access the database directly
heroku pg:psql --app my-luxury-travel-app

# View all addons
heroku addons --app my-luxury-travel-app
```

### Important Notes

- **Free tier limit**: 10,000 rows
- **Automatic backup**: Yes
- **Connection limit**: 20 concurrent connections
- **Upgrade anytime**: Easy to upgrade to paid tier if needed

### Next Steps

1. Test authentication locally
2. Deploy to Heroku
3. Implement real API integration
