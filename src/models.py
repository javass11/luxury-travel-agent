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

    airline_miles = db.Column(db.JSON, nullable=False, default={})
    hotel_points = db.Column(db.JSON, nullable=False, default={})
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
    deal_type = db.Column(db.String(20), nullable=False)
    deal_data = db.Column(db.JSON, nullable=False)
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
