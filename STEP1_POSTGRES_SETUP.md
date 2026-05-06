# STEP 1: PostgreSQL Setup - Complete Guide

Follow these exact steps to set up PostgreSQL for the luxury travel agent.

## Prerequisites Check (5 minutes)

### Check if Docker is installed:
```bash
docker --version
```

**Expected output:** `Docker version 20.x.x` or higher

If NOT installed:
- **macOS:** Download Docker Desktop from https://www.docker.com/products/docker-desktop
- **Windows:** Download Docker Desktop from https://www.docker.com/products/docker-desktop
- **Linux:** Run `sudo apt-get install docker.io` (Ubuntu/Debian)

After installing, restart your terminal and rerun `docker --version`.

---

## Step-by-Step Setup (55 minutes total)

### STEP 1A: Start PostgreSQL Container (5 minutes)

**Open your terminal/command prompt** and run this EXACT command:

```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=luxury_travel_password \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=luxury_travel \
  -p 5432:5432 \
  -d postgres:15
```

**What this does:**
- `--name postgres` - Names the container "postgres"
- `-e POSTGRES_PASSWORD=...` - Sets database password
- `-e POSTGRES_USER=postgres` - Sets username
- `-e POSTGRES_DB=luxury_travel` - Creates the database
- `-p 5432:5432` - Exposes port 5432
- `-d` - Runs in background
- `postgres:15` - Uses PostgreSQL version 15

**Expected output:**
```
[random-container-id]
```

### STEP 1B: Verify PostgreSQL is Running (2 minutes)

Wait 10 seconds, then run:

```bash
docker ps | grep postgres
```

**Expected output:**
```
[container-id]  postgres:15  ...  Up 5 seconds  0.0.0.0:5432->5432/tcp  postgres
```

If you see the above, PostgreSQL is running! ✅

If NOT, troubleshoot:
```bash
docker logs postgres
```

This shows any error messages.

### STEP 1C: Create Environment File (5 minutes)

In your project directory (`/home/user/luxury-travel-agent`), create a file named `.env`:

**Using your text editor, create `.env` with this content:**

```
# Flask Configuration
DEBUG=False
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://postgres:luxury_travel_password@localhost:5432/luxury_travel

# External APIs (you'll fill these in later)
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=
DUFFEL_ACCESS_TOKEN=
SEATS_AERO_API_KEY=

# Anthropic API for LLM Assistant
ANTHROPIC_API_KEY=
```

**Save this file in your project root directory.**

**Verify file location:**
```bash
ls -la /home/user/luxury-travel-agent/.env
```

Should output:
```
-rw-r--r--  1 root root  ... .env
```

### STEP 1D: Install Python Database Libraries (10 minutes)

In your terminal, run:

```bash
pip install -q flask-sqlalchemy psycopg2-binary alembic
```

Expected output: (None - it installs quietly with `-q`)

**Verify installation:**
```bash
python -c "import psycopg2; import sqlalchemy; print('✅ Libraries installed')"
```

Expected output:
```
✅ Libraries installed
```

### STEP 1E: Test Connection (15 minutes)

Create a test file to verify you can connect:

**Create file: `test_postgres_connection.py`**

```python
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Connecting to: {DATABASE_URL}")

try:
    # Parse connection string
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    
    print(f"✅ Connected to PostgreSQL!")
    print(f"✅ Version: {version[0]}")
    
    # List existing tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
    """)
    tables = cursor.fetchall()
    print(f"✅ Tables in database: {tables if tables else 'None (database is empty)'}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print(f"❌ DATABASE_URL: {DATABASE_URL}")
```

**Run the test:**

```bash
python test_postgres_connection.py
```

**Expected output:**
```
Connecting to: postgresql://postgres:luxury_travel_password@localhost:5432/luxury_travel
✅ Connected to PostgreSQL!
✅ Version: PostgreSQL 15.x on ...
✅ Tables in database: None (database is empty)
```

If you see the above, PostgreSQL is working! ✅

**If you get an error:**

Common errors and fixes:

| Error | Fix |
|-------|-----|
| `connection refused` | PostgreSQL container not running. Run: `docker ps` |
| `password authentication failed` | Check `.env` file password matches. Run: `cat .env` |
| `database "luxury_travel" does not exist` | Wait 5 more seconds and retry |
| `psycopg2 not found` | Run: `pip install psycopg2-binary` |

### STEP 1F: Set Up Alembic for Database Migrations (15 minutes)

Alembic lets you manage database schema changes. Initialize it:

```bash
# Initialize Alembic in your project
alembic init migrations
```

**What you should see:**
```
Creating directory /home/user/luxury-travel-agent/migrations ...
Creating directory /home/user/luxury-travel-agent/migrations/versions ...
[... more output ...]
Generating initial revision...
```

**Edit the Alembic config file to use your database:**

Open: `migrations/env.py`

Find this line (around line 20):
```python
sqlalchemy.url = config.get_main_option("sqlalchemy.url")
```

Replace it with:
```python
import os
from dotenv import load_dotenv

load_dotenv()
sqlalchemy.url = os.getenv("DATABASE_URL")
```

**Now create the initial migration:**

```bash
alembic revision --autogenerate -m "Initial schema"
```

**Expected output:**
```
  Generating /home/user/luxury-travel-agent/migrations/versions/xxxx_initial_schema.py ...  done
```

### STEP 1G: Verify Everything Works Together (3 minutes)

**Create a quick test to verify Flask can access the database:**

Create: `test_flask_db.py`

```python
from dotenv import load_dotenv
load_dotenv()

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

with app.app_context():
    try:
        # Test connection
        result = db.session.execute(db.text("SELECT 1"))
        print("✅ Flask can connect to PostgreSQL!")
        print(f"✅ Database URL: {os.getenv('DATABASE_URL')}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

Run it:
```bash
python test_flask_db.py
```

Expected output:
```
✅ Flask can connect to PostgreSQL!
✅ Database URL: postgresql://postgres:...
```

---

## Verification Checklist ✅

- [ ] Docker installed (`docker --version` works)
- [ ] PostgreSQL running (`docker ps | grep postgres` shows it)
- [ ] `.env` file created in project root
- [ ] Python libraries installed (`pip list | grep sqlalchemy`)
- [ ] Can connect to database (`test_postgres_connection.py` succeeds)
- [ ] Alembic initialized (`migrations/` folder exists)
- [ ] Flask can use database (`test_flask_db.py` succeeds)

---

## Important Passwords & Credentials

**SAVE THESE SOMEWHERE SAFE:**

```
Database Host:     localhost
Database Port:     5432
Database Name:     luxury_travel
Database User:     postgres
Database Password: luxury_travel_password
```

**Connection String (in .env):**
```
postgresql://postgres:luxury_travel_password@localhost:5432/luxury_travel
```

---

## Useful Docker Commands

### Check if PostgreSQL is running:
```bash
docker ps | grep postgres
```

### Stop PostgreSQL:
```bash
docker stop postgres
```

### Start PostgreSQL (after stopping):
```bash
docker start postgres
```

### View PostgreSQL logs:
```bash
docker logs postgres
```

### Delete PostgreSQL container (WARNING: deletes data):
```bash
docker stop postgres
docker rm postgres
```

---

## Next Steps After Setup

Once you see all ✅ checks passing:

1. **You're done with Step 1!**
2. **Next: Build User Authentication (Step 2)**
   - User model (email, password)
   - Register/Login endpoints
   - JWT tokens

3. **Save your `.env` file** - you'll need the credentials

---

## Troubleshooting

### "Connection refused"
```bash
# Check if container is running
docker ps

# If not running, start it
docker start postgres

# Wait 5 seconds and try again
```

### "Password authentication failed"
```bash
# Check your .env file
cat .env | grep DATABASE_URL

# Should show:
# DATABASE_URL=postgresql://postgres:luxury_travel_password@localhost:5432/luxury_travel
```

### "psycopg2 module not found"
```bash
pip install psycopg2-binary
```

### "Could not translate host name"
Make sure `localhost` is correct (not `127.0.0.1` in some cases):
```bash
# Test connection directly
psql postgresql://postgres:luxury_travel_password@localhost:5432/luxury_travel
```

### PostgreSQL container keeps exiting
```bash
docker logs postgres
# Shows the actual error message
```

---

## How to Check Everything is Working

Run all three tests:

```bash
# Test 1: Can you connect via psycopg2?
python test_postgres_connection.py

# Test 2: Can Flask connect?
python test_flask_db.py

# Test 3: Existing tests still pass?
pytest tests/ -v
```

All three should show ✅ success messages.

---

## Time Breakdown

- **5 min** - Docker verification
- **5 min** - Start PostgreSQL
- **2 min** - Verify running
- **5 min** - Create .env file
- **10 min** - Install libraries
- **15 min** - Test connection
- **15 min** - Setup Alembic
- **3 min** - Flask verification

**Total: 60 minutes**

Once complete, you're ready for Step 2: User Authentication!
