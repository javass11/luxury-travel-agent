# STEP 2: User Authentication (2-3 Days)

Complete implementation guide for adding user registration, login, and JWT authentication to the luxury travel agent.

## What You'll Build

By the end of this step, you'll have:
- ✅ User registration (POST /api/auth/register)
- ✅ User login (POST /api/auth/login)
- ✅ JWT token generation
- ✅ Protected routes (require login)
- ✅ Token refresh (POST /api/auth/refresh)
- ✅ User profile retrieval (GET /api/auth/me)
- ✅ Full test coverage for auth

## Prerequisites

✅ PostgreSQL running (Step 1 complete)
✅ `.env` file configured
✅ Python dependencies installed

**Verify with:**
```bash
docker ps | grep postgres  # Should show running
cat .env | grep DATABASE_URL  # Should show your connection string
python -c "import psycopg2; print('✅ psycopg2 installed')"
```

---

## Implementation Plan

### Phase 1: Database Models (Day 1 Morning)
### Phase 2: Authentication Routes (Day 1 Afternoon)
### Phase 3: JWT Integration (Day 2 Morning)
### Phase 4: Tests & Validation (Day 2 Afternoon)
### Phase 5: Deploy & Test (Day 2/3)

---

## PHASE 1: Create User Models

### Step 1.1: Create Database Models File

Create new file: `src/models.py` (UPDATE the existing one)

```python
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    loyalty_profile = db.relationship('LoyaltyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    saved_deals = db.relationship('SavedDeal', backref='user', cascade='all, delete-orphan')
    chat_history = db.relationship('ChatMessage', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class LoyaltyProfile(db.Model):
    """User loyalty profile (miles, points, elite status)"""
    __tablename__ = 'loyalty_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Airline miles (stored as JSON)
    airline_miles = db.Column(db.JSON, nullable=False, default={})
    
    # Hotel points (stored as JSON)
    hotel_points = db.Column(db.JSON, nullable=False, default={})
    
    # Elite status (stored as JSON)
    elite_status = db.Column(db.JSON, nullable=False, default={})
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'airline_miles': self.airline_miles,
            'hotel_points': self.hotel_points,
            'elite_status': self.elite_status,
        }
    
    def __repr__(self):
        return f'<LoyaltyProfile user_id={self.user_id}>'


class SavedDeal(db.Model):
    """Saved flight/hotel deals"""
    __tablename__ = 'saved_deals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deal_type = db.Column(db.String(20), nullable=False)  # 'flight' or 'hotel'
    deal_data = db.Column(db.JSON, nullable=False)  # Store complete deal info
    notes = db.Column(db.Text)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deal_type': self.deal_type,
            'deal_data': self.deal_data,
            'notes': self.notes,
            'saved_at': self.saved_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<SavedDeal {self.deal_type} user_id={self.user_id}>'


class ChatMessage(db.Model):
    """Chat history with LLM assistant"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<ChatMessage user_id={self.user_id}>'
```

### Step 1.2: Update requirements.txt

Add these lines to `requirements.txt`:

```
flask-sqlalchemy==3.0.0
flask-jwt-extended==4.5.0
bcrypt==4.0.0
psycopg2-binary==2.9.0
alembic==1.11.0
```

Install them:
```bash
pip install -q flask-sqlalchemy flask-jwt-extended bcrypt psycopg2-binary alembic
```

### Step 1.3: Create Alembic Migration

Initialize Alembic (if you haven't already):

```bash
alembic init migrations
```

Create the initial migration:

```bash
alembic revision --autogenerate -m "Create user and related tables"
```

**Check the migration file** - it should be in `migrations/versions/xxxx_create_user_and_related_tables.py`

Run the migration:

```bash
alembic upgrade head
```

**Expected output:**
```
[2026-05-06 12:00:00,000] INFO [alembic.runtime.migration] Context impl PostgresqlImpl.
[2026-05-06 12:00:00,000] INFO [alembic.runtime.migration] Running upgrade  -> xxxx, create user and related tables
```

---

## PHASE 2: Authentication Routes

### Step 2.1: Create Authentication Routes File

Create new file: `src/auth.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
from .models import db, User, LoyaltyProfile
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    
    # Validate email
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate password
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    try:
        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        
        # Create loyalty profile
        loyalty_profile = LoyaltyProfile(user=user)
        
        # Save to database
        db.session.add(user)
        db.session.add(loyalty_profile)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Create tokens
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Logged in successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=24))
    
    return jsonify({
        'access_token': access_token,
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    loyalty_profile = LoyaltyProfile.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        'user': user.to_dict(),
        'loyalty_profile': loyalty_profile.to_dict() if loyalty_profile else None,
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    return jsonify({
        'message': 'Logged out successfully. Please discard your token.',
    }), 200
```

---

## PHASE 3: Integrate JWT with Flask App

### Step 3.1: Update src/app.py

Replace the entire file with this:

```python
import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from src.models import db, User
from src.auth import auth_bp
from src.config import Config

load_dotenv()

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config.from_object(Config)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///luxury_travel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * 24  # 24 hours

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    """Serve the main HTML page"""
    with open('static/index.html', 'r') as f:
        return f.read()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
    })


@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile (protected route example)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized - token required or invalid'}), 401


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=Config.DEBUG, port=5000)
```

---

## PHASE 4: Tests for Authentication

### Step 4.1: Create Auth Tests

Create file: `tests/test_auth.py`

```python
import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app, db
from src.models import User


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_success(self):
        """Test successful registration"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
                'first_name': 'John',
                'last_name': 'Doe',
            }),
            content_type='application/json',
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertEqual(data['user']['email'], 'test@example.com')
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )
        
        # Duplicate registration
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword456',
            }),
            content_type='application/json',
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('already registered', data['error'])
    
    def test_register_weak_password(self):
        """Test registration with weak password"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'weak',
            }),
            content_type='application/json',
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('password', data['error'].lower())
    
    def test_login_success(self):
        """Test successful login"""
        # Register first
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )
        
        # Login
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['email'], 'test@example.com')
    
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        # Register first
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )
        
        # Login with wrong password
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'WrongPassword123',
            }),
            content_type='application/json',
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        # Register and login
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
                'first_name': 'John',
            }),
            content_type='application/json',
        )
        
        token = json.loads(register_response.data)['access_token']
        
        # Get current user
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'},
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['user']['first_name'], 'John')
    
    def test_protected_route_without_token(self):
        """Test accessing protected route without token"""
        response = self.client.get('/api/auth/me')
        
        self.assertEqual(response.status_code, 401)
    
    def test_refresh_token(self):
        """Test token refresh"""
        # Register and login
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )
        
        refresh_token = json.loads(register_response.data)['refresh_token']
        
        # Refresh token
        response = self.client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'},
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)


if __name__ == '__main__':
    unittest.main()
```

---

## PHASE 5: Run and Test

### Step 5.1: Run Database Migrations

```bash
alembic upgrade head
```

### Step 5.2: Run Tests

```bash
pytest tests/test_auth.py -v
```

**Expected output:**
```
tests/test_auth.py::TestAuthentication::test_register_success PASSED
tests/test_auth.py::TestAuthentication::test_register_duplicate_email PASSED
tests/test_auth.py::TestAuthentication::test_register_weak_password PASSED
tests/test_auth.py::TestAuthentication::test_login_success PASSED
tests/test_auth.py::TestAuthentication::test_login_invalid_password PASSED
tests/test_auth.py::TestAuthentication::test_get_current_user PASSED
tests/test_auth.py::TestAuthentication::test_protected_route_without_token PASSED
tests/test_auth.py::TestAuthentication::test_refresh_token PASSED

====== 8 passed ======
```

### Step 5.3: Start the Server

```bash
python -m src.app
```

**Expected output:**
```
 * Serving Flask app 'src.app'
 * Running on http://127.0.0.1:5000
```

### Step 5.4: Test Manually

In a new terminal, test registration:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Smith"
  }'
```

**Expected response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "...",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "created_at": "2026-05-06T...",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Save the `access_token` and test login:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'
```

---

## Summary

You now have:
- ✅ User registration with validation
- ✅ User login with password verification
- ✅ JWT token generation & refresh
- ✅ Protected routes
- ✅ User profiles with loyalty tracking
- ✅ Complete test coverage

**Next step:** Update other routes to require authentication and integrate with real flight/hotel APIs.

---

## Troubleshooting

### Database Error
```bash
# Check connection
python -c "from src.models import db; from src.app import app; print('✅ Database connected')"
```

### JWT Error
```bash
# Verify JWT installed
python -c "from flask_jwt_extended import JWTManager; print('✅ JWT installed')"
```

### Migration Error
```bash
# Recreate migrations
rm -rf migrations/
alembic init migrations
alembic revision --autogenerate -m "Create tables"
alembic upgrade head
```
