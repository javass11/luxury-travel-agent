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
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

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
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

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
        self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

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
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

        refresh_token = json.loads(register_response.data)['refresh_token']

        response = self.client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'},
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_invalid_email_format(self):
        """Test registration with invalid email"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'invalid-email',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('email', data['error'].lower())

    def test_loyalty_profile_created(self):
        """Test that loyalty profile is created with user"""
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPassword123',
            }),
            content_type='application/json',
        )

        token = json.loads(register_response.data)['access_token']

        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'},
        )

        data = json.loads(response.data)
        self.assertIsNotNone(data['loyalty_profile'])
        self.assertEqual(data['loyalty_profile']['airline_miles'], {})
        self.assertEqual(data['loyalty_profile']['hotel_points'], {})


if __name__ == '__main__':
    unittest.main()
