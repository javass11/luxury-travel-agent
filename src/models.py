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


class UserPreferences(db.Model):
    """User travel preferences for personalization"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)

    home_airport = db.Column(db.String(3))
    work_airport = db.Column(db.String(3))
    preferred_airlines = db.Column(db.JSON, default=list)
    excluded_airlines = db.Column(db.JSON, default=list)
    preferred_cabins = db.Column(db.JSON, default=lambda: ['economy', 'business'])
    max_stops = db.Column(db.Integer, default=2)
    preferred_alliances = db.Column(db.JSON, default=list)
    preferred_departure_time = db.Column(db.String(20))
    preferred_arrival_time = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'home_airport': self.home_airport,
            'work_airport': self.work_airport,
            'preferred_airlines': self.preferred_airlines,
            'excluded_airlines': self.excluded_airlines,
            'preferred_cabins': self.preferred_cabins,
            'max_stops': self.max_stops,
            'preferred_alliances': self.preferred_alliances,
            'preferred_departure_time': self.preferred_departure_time,
            'preferred_arrival_time': self.preferred_arrival_time,
        }


class PriceHistory(db.Model):
    """Historical price tracking for trend analysis"""
    __tablename__ = 'price_history'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_key = db.Column(db.String(10), nullable=False, index=True)
    origin = db.Column(db.String(3), nullable=False, index=True)
    destination = db.Column(db.String(3), nullable=False, index=True)
    cabin = db.Column(db.String(20), nullable=False)
    search_date = db.Column(db.Date, nullable=False, index=True)
    cash_price = db.Column(db.Float)
    miles_cost = db.Column(db.Integer)
    cpp = db.Column(db.Float)
    source = db.Column(db.String(50))
    currency = db.Column(db.String(3), default='USD')
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'route_key': self.route_key,
            'origin': self.origin,
            'destination': self.destination,
            'cabin': self.cabin,
            'search_date': self.search_date.isoformat(),
            'cash_price': self.cash_price,
            'miles_cost': self.miles_cost,
            'cpp': self.cpp,
            'source': self.source,
            'currency': self.currency,
            'recorded_at': self.recorded_at.isoformat(),
        }


class LoyaltyAccount(db.Model):
    """Linked frequent flyer accounts"""
    __tablename__ = 'loyalty_accounts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    program_name = db.Column(db.String(50), nullable=False)
    frequent_flyer_number = db.Column(db.String(50), nullable=False)
    miles_balance = db.Column(db.Integer, default=0)
    elite_status = db.Column(db.String(50))
    elite_expiration = db.Column(db.Date)
    program_tier = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, default=False)

    last_synced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'program_name': self.program_name,
            'frequent_flyer_number': self.frequent_flyer_number,
            'miles_balance': self.miles_balance,
            'elite_status': self.elite_status,
            'elite_expiration': self.elite_expiration.isoformat() if self.elite_expiration else None,
            'program_tier': self.program_tier,
            'is_verified': self.is_verified,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
        }


class Alert(db.Model):
    """Price and availability alerts"""
    __tablename__ = 'alerts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    origin = db.Column(db.String(3), nullable=False, index=True)
    destination = db.Column(db.String(3), nullable=False, index=True)
    cabin = db.Column(db.String(20))
    threshold_price = db.Column(db.Float)
    threshold_miles = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)

    last_triggered = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'origin': self.origin,
            'destination': self.destination,
            'cabin': self.cabin,
            'threshold_price': self.threshold_price,
            'threshold_miles': self.threshold_miles,
            'is_active': self.is_active,
            'email_enabled': self.email_enabled,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
        }


class AlertHistory(db.Model):
    """Alert trigger history for tracking"""
    __tablename__ = 'alert_history'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = db.Column(db.String(36), db.ForeignKey('alerts.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deal_price = db.Column(db.Float)
    deal_miles = db.Column(db.Integer)
    triggered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notification_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'deal_price': self.deal_price,
            'deal_miles': self.deal_miles,
            'triggered_at': self.triggered_at.isoformat(),
            'notification_sent': self.notification_sent,
        }


class DealAnalytics(db.Model):
    """Route-level analytics for trending & insights"""
    __tablename__ = 'deal_analytics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_key = db.Column(db.String(10), nullable=False, index=True)
    origin = db.Column(db.String(3), nullable=False, index=True)
    destination = db.Column(db.String(3), nullable=False, index=True)
    cabin = db.Column(db.String(20), default='economy')
    date = db.Column(db.Date, nullable=False, index=True)

    search_count = db.Column(db.Integer, default=0)
    booking_count = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float)
    avg_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    best_cpp = db.Column(db.Float)
    best_source = db.Column(db.String(50))
    trending = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'route': f"{self.origin}-{self.destination}",
            'cabin': self.cabin,
            'search_count': self.search_count,
            'booking_count': self.booking_count,
            'conversion_rate': self.conversion_rate,
            'avg_price': self.avg_price,
            'price_range': {'min': self.min_price, 'max': self.max_price},
            'best_cpp': self.best_cpp,
            'best_source': self.best_source,
            'trending': self.trending,
        }


class UserAnalytics(db.Model):
    """User behavior analytics"""
    __tablename__ = 'user_analytics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)

    total_searches = db.Column(db.Integer, default=0)
    total_saved_deals = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    favorite_routes = db.Column(db.JSON, default=list)
    favorite_airlines = db.Column(db.JSON, default=list)
    avg_booking_lead_days = db.Column(db.Integer)
    preferred_cabin_distribution = db.Column(db.JSON, default=dict)
    last_search_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'total_searches': self.total_searches,
            'total_saved_deals': self.total_saved_deals,
            'total_bookings': self.total_bookings,
            'favorite_routes': self.favorite_routes,
            'favorite_airlines': self.favorite_airlines,
            'avg_booking_lead_days': self.avg_booking_lead_days,
            'preferred_cabin_distribution': self.preferred_cabin_distribution,
            'last_search_date': self.last_search_date.isoformat() if self.last_search_date else None,
        }


class SearchLog(db.Model):
    """Search history for analytics"""
    __tablename__ = 'search_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    origin = db.Column(db.String(3), nullable=False, index=True)
    destination = db.Column(db.String(3), nullable=False, index=True)
    departure_date = db.Column(db.Date, nullable=False, index=True)
    cabin = db.Column(db.String(20))

    results_count = db.Column(db.Integer, default=0)
    filters_applied = db.Column(db.JSON, default=dict)
    clicked_result_id = db.Column(db.String(120))
    booked = db.Column(db.Boolean, default=False)
    duration_ms = db.Column(db.Integer)
    source = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'departure_date': self.departure_date.isoformat(),
            'cabin': self.cabin,
            'results_count': self.results_count,
            'filters_applied': self.filters_applied,
            'booked': self.booked,
            'duration_ms': self.duration_ms,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
        }
