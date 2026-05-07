from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
from .models import db, User, LoyaltyProfile
import re
import logging
import secrets
import os
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting for login attempts
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def check_login_rate_limit(email: str) -> tuple:
    """Check if email has exceeded login attempt limit. Returns (allowed, remaining_seconds)"""
    now = datetime.utcnow()
    lockout_until = now - timedelta(minutes=LOCKOUT_DURATION_MINUTES)

    # Clean old attempts
    login_attempts[email] = [timestamp for timestamp in login_attempts[email] if timestamp > lockout_until]

    if len(login_attempts[email]) >= MAX_LOGIN_ATTEMPTS:
        oldest_attempt = login_attempts[email][0]
        reset_time = oldest_attempt + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        remaining_seconds = int((reset_time - now).total_seconds())
        return False, remaining_seconds

    return True, 0


def record_login_attempt(email: str):
    """Record a failed login attempt"""
    login_attempts[email].append(datetime.utcnow())

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple:
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

    if not data:
        return jsonify({'error': 'Request body required'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()

    if not email:
        return jsonify({'error': 'Email required'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    if not password:
        return jsonify({'error': 'Password required'}), 400

    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400

    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)

        loyalty_profile = LoyaltyProfile(user=user)

        db.session.add(user)
        db.session.add(loyalty_profile)
        db.session.commit()

        logger.info(f"New user registered: {email}")
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
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

    # Check rate limiting
    allowed, remaining_seconds = check_login_rate_limit(email)
    if not allowed:
        logger.warning(f"Login rate limit exceeded for email: {email}")
        return jsonify({
            'error': f'Too many login attempts. Try again in {remaining_seconds} seconds.'
        }), 429

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        record_login_attempt(email)
        logger.warning(f"Failed login attempt for email: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        logger.warning(f"Inactive account login attempt: {email}")
        return jsonify({'error': 'Account is inactive'}), 403

    # Clear rate limiting on successful login
    login_attempts[email] = []

    logger.info(f"Successful login: {email}")
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
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
    access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(minutes=15))

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


@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request a password reset token"""
    data = request.get_json()
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Email required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        return jsonify({'message': 'If email exists, reset link will be sent'}), 200

    from .models import PasswordReset
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    existing = PasswordReset.query.filter_by(user_id=user.id).first()
    if existing:
        db.session.delete(existing)

    reset = PasswordReset(user_id=user.id, token=reset_token, expires_at=expires_at)
    db.session.add(reset)
    db.session.commit()

    logger.info(f"Password reset requested for: {email}")
    reset_link = f"https://app.example.com/reset-password?token={reset_token}"

    try:
        from .email_service import email_service
        email_service.send_email(
            email,
            "Password Reset - Luxury Travel Agent",
            f"<p>Click <a href='{reset_link}'>here</a> to reset your password. Link expires in 1 hour.</p>"
        )
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")

    return jsonify({'message': 'If email exists, reset link will be sent'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({'error': 'Token and password required'}), 400

    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({'error': message}), 400

    from .models import PasswordReset
    reset = PasswordReset.query.filter_by(token=token).first()

    if not reset or reset.expires_at < datetime.utcnow():
        logger.warning(f"Invalid or expired password reset token")
        return jsonify({'error': 'Invalid or expired reset token'}), 400

    user = User.query.get(reset.user_id)
    user.set_password(new_password)
    db.session.delete(reset)
    db.session.commit()

    logger.info(f"Password reset successful for user: {user.email}")
    return jsonify({'message': 'Password reset successful'}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    current_user_id = get_jwt_identity()
    logger.info(f"User logout: {current_user_id}")
    return jsonify({
        'message': 'Logged out successfully',
    }), 200
