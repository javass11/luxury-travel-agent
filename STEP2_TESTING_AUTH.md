# Step 2: Test Authentication Locally

Complete guide to test the authentication system locally before deploying to production.

## Prerequisites

- Project dependencies installed: `pip install -r requirements.txt`
- Flask development server ready
- curl or Postman for API testing
- PostgreSQL running (use SQLite for quick testing)

## Quick Start (2 minutes)

```bash
# Terminal 1: Start Flask server
python -m src.app

# Terminal 2: Run authentication tests
pytest tests/test_auth.py -v
```

Expected output:
```
test_register_success PASSED                 [ 10%]
test_register_duplicate_email PASSED         [ 20%]
test_register_weak_password PASSED           [ 30%]
test_login_success PASSED                    [ 40%]
test_login_invalid_password PASSED           [ 50%]
test_get_current_user PASSED                 [ 60%]
test_protected_route_without_token PASSED    [ 70%]
test_refresh_token PASSED                    [ 80%]
test_invalid_email_format PASSED             [ 90%]
test_loyalty_profile_created PASSED          [100%]
======================== 10 passed in 0.25s ========================
```

## Full Authentication Testing Workflow

### 1. Start the Flask Development Server

```bash
python -m src.app
```

Output:
```
 * Serving Flask app 'src.app'
 * Debug mode: on
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

Keep this running in a separate terminal.

### 2. Test User Registration

#### Using curl (Command Line)

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }'
```

Expected response (201 Created):
```json
{
  "message": "User registered successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "first_name": null,
    "last_name": null,
    "is_active": true,
    "created_at": "2026-05-06T12:00:00"
  }
}
```

**Save the access_token** - you'll use it for protected endpoints.

#### Using Postman

1. Open Postman
2. Create new request: `POST http://localhost:5000/api/auth/register`
3. Headers tab:
   ```
   Content-Type: application/json
   ```
4. Body tab (raw, JSON):
   ```json
   {
     "email": "alice@example.com",
     "password": "SecurePass123"
   }
   ```
5. Click "Send"

### 3. Test Password Validation

Weak passwords should be rejected:

```bash
# Try registering with weak password (too short)
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "short"
  }'
```

Expected response (400 Bad Request):
```json
{
  "error": "Password must be at least 8 characters long and contain uppercase letters and digits"
}
```

#### Valid password examples:
- ✅ `SecurePass123`
- ✅ `MyPassword456`
- ✅ `Travel2024Deal`

#### Invalid password examples:
- ❌ `short` (too short, no uppercase, no digit)
- ❌ `nouppercase123` (no uppercase)
- ❌ `NODIGITS` (no digit)
- ❌ `NoSpecialChars` (short enough but let's make it longer first)

### 4. Test Email Validation

```bash
# Try registering with invalid email
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "password": "ValidPass123"
  }'
```

Expected response (400 Bad Request):
```json
{
  "error": "Invalid email format"
}
```

### 5. Test Duplicate Email Prevention

```bash
# Try registering with same email again
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "DifferentPass456"
  }'
```

Expected response (400 Bad Request):
```json
{
  "error": "Email already registered"
}
```

### 6. Test User Login

```bash
# Login with correct credentials
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }'
```

Expected response (200 OK):
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "first_name": null,
    "last_name": null,
    "is_active": true
  }
}
```

### 7. Test Failed Login

```bash
# Try login with wrong password
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "WrongPassword999"
  }'
```

Expected response (401 Unauthorized):
```json
{
  "error": "Invalid email or password"
}
```

### 8. Test Protected Endpoints

#### Get Current User Info (requires token)

```bash
# Use the access_token from registration/login response
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Expected response (200 OK):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "first_name": null,
    "last_name": null,
    "is_active": true,
    "created_at": "2026-05-06T12:00:00"
  },
  "loyalty_profile": {
    "airline_miles": {},
    "hotel_points": {},
    "elite_status": {}
  }
}
```

#### Test Missing Token

```bash
# Try accessing protected endpoint without token
curl -X GET http://localhost:5000/api/auth/me
```

Expected response (401 Unauthorized):
```json
{
  "msg": "Missing Authorization Header"
}
```

#### Test Invalid Token

```bash
# Try with invalid token
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer invalid.token.here"
```

Expected response (422 Unprocessable Entity):
```json
{
  "msg": "Invalid token format"
}
```

### 9. Test Token Refresh

```bash
# Use the refresh_token from registration/login
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"
```

Expected response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 10. Test Logout

```bash
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Expected response (200 OK):
```json
{
  "message": "Logout successful"
}
```

## Complete Test Workflow Script

Save this as `test_auth_manual.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"
EMAIL="test_$(date +%s)@example.com"
PASSWORD="TestPass123"

echo "=== Testing Luxury Travel Agent Authentication ==="
echo ""

# 1. Register
echo "1️⃣  Registering user: $EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.refresh_token')
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user.id')

echo "✅ Registered successfully"
echo "   User ID: $USER_ID"
echo "   Access Token: ${ACCESS_TOKEN:0:20}..."
echo ""

# 2. Get Current User
echo "2️⃣  Getting current user info"
ME_RESPONSE=$(curl -s -X GET $BASE_URL/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $ME_RESPONSE | jq '.'
echo "✅ Retrieved current user"
echo ""

# 3. Save a Deal (protected endpoint)
echo "3️⃣  Saving a flight deal (protected endpoint)"
SAVE_RESPONSE=$(curl -s -X POST $BASE_URL/api/deals/save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "deal_type": "flight",
    "deal_id": "FL001",
    "notes": "Great deal!"
  }')

echo $SAVE_RESPONSE | jq '.'
echo "✅ Saved deal successfully"
echo ""

# 4. Test Protected Endpoint Without Token
echo "4️⃣  Testing protected endpoint without token (should fail)"
FAIL_RESPONSE=$(curl -s -X POST $BASE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}')

echo $FAIL_RESPONSE | jq '.'
echo "✅ Correctly rejected unauthorized request"
echo ""

# 5. Refresh Token
echo "5️⃣  Refreshing access token"
REFRESH_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN")

NEW_ACCESS_TOKEN=$(echo $REFRESH_RESPONSE | jq -r '.access_token')
echo "✅ Token refreshed successfully"
echo "   New Token: ${NEW_ACCESS_TOKEN:0:20}..."
echo ""

# 6. Logout
echo "6️⃣  Logging out"
LOGOUT_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $LOGOUT_RESPONSE | jq '.'
echo "✅ Logged out successfully"
echo ""

echo "=== ✅ All Authentication Tests Passed ==="
```

Run it:
```bash
chmod +x test_auth_manual.sh
./test_auth_manual.sh
```

## Integration Tests

Run the full integration test suite:

```bash
pytest tests/test_integration.py -v
```

This runs 13 tests covering:
- ✅ User registration and login
- ✅ Protected endpoint access
- ✅ Deal saving (requires authentication)
- ✅ Chat endpoint (requires authentication)
- ✅ Token refresh
- ✅ 401/400 error handling

## Authentication Test Coverage

Run the authentication-specific test suite:

```bash
pytest tests/test_auth.py -v
```

Test cases (10 tests):
1. ✅ Register user successfully
2. ✅ Prevent duplicate email registration
3. ✅ Reject weak passwords
4. ✅ Login with correct credentials
5. ✅ Reject wrong passwords
6. ✅ Get current user info
7. ✅ Protect routes with @jwt_required()
8. ✅ Refresh access token
9. ✅ Validate email format
10. ✅ Create loyalty profile on registration

Check coverage:
```bash
pytest tests/test_auth.py --cov=src.auth --cov-report=term-missing -v
```

## Testing with Postman Collection

Import this collection into Postman for easier testing:

```json
{
  "info": {
    "name": "Luxury Travel Agent - Auth Testing",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register User",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/auth/register",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"user@example.com\", \"password\": \"SecurePass123\"}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/auth/login",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"user@example.com\", \"password\": \"SecurePass123\"}"
        }
      }
    },
    {
      "name": "Get Current User",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/auth/me",
        "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}]
      }
    },
    {
      "name": "Refresh Token",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/auth/refresh",
        "header": [{"key": "Authorization", "value": "Bearer {{refresh_token}}"}]
      }
    },
    {
      "name": "Logout",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/auth/logout",
        "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}]
      }
    },
    {
      "name": "Save Deal (Protected)",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/deals/save",
        "header": [
          {"key": "Content-Type", "value": "application/json"},
          {"key": "Authorization", "value": "Bearer {{access_token}}"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"deal_type\": \"flight\", \"deal_id\": \"FL001\", \"notes\": \"Great deal\"}"
        }
      }
    }
  ]
}
```

Set Postman variables:
- `base_url`: `http://localhost:5000`
- `access_token`: (from Register/Login response)
- `refresh_token`: (from Register/Login response)

## Troubleshooting

### "Missing Authorization Header" when accessing protected route

**Problem:** You forgot to include the Bearer token.

**Solution:**
```bash
# ❌ Wrong
curl -X GET http://localhost:5000/api/auth/me

# ✅ Correct
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### "Invalid token format"

**Problem:** Token is malformed or expired.

**Solution:**
- Copy the full token from registration/login response
- Ensure token is passed with `Bearer ` prefix
- Refresh token if expired (24-hour expiration)

### "Email already registered"

**Problem:** Using email that's already in the system.

**Solution:** Use a different email or delete the user from database:
```bash
python << 'EOF'
from src.app import db, app
from src.models import User

with app.app_context():
    user = User.query.filter_by(email='alice@example.com').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"Deleted user: {user.email}")
EOF
```

### Tests fail with "no such table: users"

**Problem:** Database tables not created.

**Solution:**
```bash
python << 'EOF'
from src.app import db, app
with app.app_context():
    db.create_all()
    print("✅ Tables created")
EOF
```

### "Connection refused" when accessing API

**Problem:** Flask server not running.

**Solution:** Start the server in another terminal:
```bash
python -m src.app
```

## Performance Testing

Measure authentication performance:

```bash
pytest tests/test_performance.py -v -k "auth"
```

Expected benchmarks:
- Password hashing: ~100ms (bcrypt)
- Token generation: <1ms
- Token verification: <1ms
- Database lookup: <10ms

## Next Steps

✅ **Step 1: PostgreSQL Setup** - Complete
✅ **Step 2: Test Authentication Locally** - You are here
🔄 **Step 3: Implement Real API Integration** - Next

Once authentication is working:
1. Deploy to Heroku with PostgreSQL
2. Implement Amadeus Flight API integration
3. Implement hotel search API integration
4. Add real pricing and availability data

## References

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Bcrypt Documentation](https://github.com/pyca/bcrypt)
- [curl Documentation](https://curl.se/docs/)
- [Postman Documentation](https://learning.postman.com/)

## Summary

| Task | Command | Expected Result |
|------|---------|-----------------|
| Start server | `python -m src.app` | Server runs on :5000 |
| Run auth tests | `pytest tests/test_auth.py -v` | 10 tests pass |
| Register user | `curl -X POST /api/auth/register` | 201 Created + tokens |
| Login | `curl -X POST /api/auth/login` | 200 OK + tokens |
| Get user | `curl -X GET /api/auth/me` | 200 OK + user data |
| Refresh token | `curl -X POST /api/auth/refresh` | 200 OK + new token |
| Logout | `curl -X POST /api/auth/logout` | 200 OK |
