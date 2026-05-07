import logging
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from flask import jsonify
from .models import (
    db, User, UserPreferences, PriceHistory, LoyaltyAccount,
    Alert, AlertHistory
)
from .email_service import email_service

logger = logging.getLogger(__name__)


class PreferencesHandler:
    """User preferences management"""

    @staticmethod
    def get_user_preferences(user_id: str):
        """Get user preferences or create defaults"""
        prefs = UserPreferences.query.filter_by(user_id=user_id).first()

        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()

        return prefs.to_dict()

    @staticmethod
    def update_user_preferences(user_id: str, data: dict):
        """Update user preferences"""
        prefs = UserPreferences.query.filter_by(user_id=user_id).first()

        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)

        for key, value in data.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        prefs.updated_at = datetime.utcnow()
        db.session.commit()

        return prefs.to_dict()

    @staticmethod
    def filter_flights_by_preferences(flights: list, user_id: str) -> list:
        """Filter flights based on user preferences"""
        prefs = UserPreferences.query.filter_by(user_id=user_id).first()

        if not prefs:
            return flights

        filtered = flights

        # Filter by excluded airlines
        if prefs.excluded_airlines:
            filtered = [f for f in filtered if f.get('airline') not in prefs.excluded_airlines]

        # Filter by preferred airlines if specified
        if prefs.preferred_airlines:
            filtered = [f for f in filtered if f.get('airline') in prefs.preferred_airlines]

        # Filter by cabin
        if prefs.preferred_cabins:
            filtered = [f for f in filtered if f.get('cabin_class', 'ECONOMY') in prefs.preferred_cabins]

        # Filter by max stops
        if prefs.max_stops is not None:
            filtered = [f for f in filtered if f.get('stops', 0) <= prefs.max_stops]

        return filtered


class PriceHistoryHandler:
    """Price history tracking and analytics"""

    @staticmethod
    def record_price(origin: str, destination: str, cabin: str, price: dict, source: str = 'demo'):
        """Record a flight price for historical tracking"""
        try:
            route_key = f"{origin}{destination}"
            history = PriceHistory(
                route_key=route_key,
                origin=origin,
                destination=destination,
                cabin=cabin,
                search_date=datetime.now().date(),
                cash_price=price.get('cash_price'),
                miles_cost=price.get('miles_cost'),
                cpp=price.get('cpp'),
                source=source,
                currency=price.get('currency', 'USD'),
            )
            db.session.add(history)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record price: {e}")
            return False

    @staticmethod
    def get_price_history(origin: str, destination: str, cabin: str = None, days: int = 30):
        """Get historical prices for a route"""
        query = PriceHistory.query.filter(
            and_(
                PriceHistory.origin == origin,
                PriceHistory.destination == destination,
                PriceHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
            )
        )

        if cabin:
            query = query.filter_by(cabin=cabin)

        history = query.order_by(PriceHistory.recorded_at.asc()).all()
        return [h.to_dict() for h in history]

    @staticmethod
    def get_price_analytics(origin: str, destination: str, cabin: str = None, days: int = 30):
        """Get price analytics for a route"""
        history = PriceHistoryHandler.get_price_history(origin, destination, cabin, days)

        if not history:
            return None

        prices = [h['cash_price'] for h in history if h['cash_price']]
        miles = [h['miles_cost'] for h in history if h['miles_cost']]
        cpps = [h['cpp'] for h in history if h['cpp']]

        if not prices:
            return None

        return {
            'route': f"{origin}-{destination}",
            'cabin': cabin or 'all',
            'days': days,
            'price': {
                'current': prices[-1] if prices else None,
                'average': sum(prices) / len(prices),
                'min': min(prices),
                'max': max(prices),
                'trend': 'up' if prices[-1] > prices[0] else 'down' if prices[-1] < prices[0] else 'stable',
            },
            'miles': {
                'current': miles[-1] if miles else None,
                'average': sum(miles) / len(miles) if miles else None,
                'min': min(miles) if miles else None,
                'max': max(miles) if miles else None,
            },
            'cpp': {
                'current': cpps[-1] if cpps else None,
                'average': sum(cpps) / len(cpps) if cpps else None,
                'min': min(cpps) if cpps else None,
                'max': max(cpps) if cpps else None,
            },
            'samples': len(history),
            'data': history[-7:],  # Last 7 data points
        }


class LoyaltyHandler:
    """Loyalty account management"""

    @staticmethod
    def link_loyalty_account(user_id: str, program: str, ff_number: str):
        """Link a loyalty account"""
        try:
            account = LoyaltyAccount(
                user_id=user_id,
                program_name=program,
                frequent_flyer_number=ff_number,
                is_verified=False,
            )
            db.session.add(account)
            db.session.commit()
            return account.to_dict()
        except Exception as e:
            logger.error(f"Failed to link loyalty account: {e}")
            raise

    @staticmethod
    def get_user_loyalty_accounts(user_id: str):
        """Get all loyalty accounts for user"""
        accounts = LoyaltyAccount.query.filter_by(user_id=user_id).all()
        return [a.to_dict() for a in accounts]

    @staticmethod
    def update_loyalty_balance(account_id: str, miles: int, elite_status: str = None, elite_expiration: str = None):
        """Update loyalty account balance"""
        account = LoyaltyAccount.query.get(account_id)

        if not account:
            raise ValueError("Account not found")

        account.miles_balance = miles
        if elite_status:
            account.elite_status = elite_status
        if elite_expiration:
            account.elite_expiration = datetime.fromisoformat(elite_expiration).date()
        account.last_synced = datetime.utcnow()
        account.is_verified = True

        db.session.commit()
        return account.to_dict()

    @staticmethod
    def delete_loyalty_account(user_id: str, account_id: str):
        """Unlink a loyalty account"""
        account = LoyaltyAccount.query.filter(
            and_(
                LoyaltyAccount.id == account_id,
                LoyaltyAccount.user_id == user_id
            )
        ).first()

        if not account:
            raise ValueError("Account not found")

        db.session.delete(account)
        db.session.commit()
        return True


class AlertHandler:
    """Alert management"""

    @staticmethod
    def create_alert(user_id: str, alert_type: str, origin: str, destination: str,
                    threshold_price: float = None, threshold_miles: int = None,
                    cabin: str = None) -> dict:
        """Create a price or award alert"""
        alert = Alert(
            user_id=user_id,
            alert_type=alert_type,
            origin=origin,
            destination=destination,
            threshold_price=threshold_price,
            threshold_miles=threshold_miles,
            cabin=cabin,
            is_active=True,
        )
        db.session.add(alert)
        db.session.commit()

        user = User.query.get(user_id)
        if user and user.email:
            email_service.send_email(
                user.email,
                f"Alert Created: {origin} → {destination}",
                f"<p>Your {alert_type} alert has been created. We'll notify you when deals are found.</p>"
            )

        return alert.to_dict()

    @staticmethod
    def get_user_alerts(user_id: str) -> list:
        """Get all alerts for user"""
        alerts = Alert.query.filter_by(user_id=user_id).all()
        return [a.to_dict() for a in alerts]

    @staticmethod
    def deactivate_alert(user_id: str, alert_id: str) -> bool:
        """Deactivate an alert"""
        alert = Alert.query.filter(
            and_(
                Alert.id == alert_id,
                Alert.user_id == user_id
            )
        ).first()

        if not alert:
            raise ValueError("Alert not found")

        alert.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def delete_alert(user_id: str, alert_id: str) -> bool:
        """Delete an alert"""
        alert = Alert.query.filter(
            and_(
                Alert.id == alert_id,
                Alert.user_id == user_id
            )
        ).first()

        if not alert:
            raise ValueError("Alert not found")

        db.session.delete(alert)
        db.session.commit()
        return True

    @staticmethod
    def trigger_alert(alert_id: str, deal_price: float = None, deal_miles: int = None) -> bool:
        """Trigger alert and send notification"""
        alert = Alert.query.get(alert_id)

        if not alert or not alert.is_active:
            return False

        try:
            # Record trigger
            history = AlertHistory(
                alert_id=alert_id,
                user_id=alert.user_id,
                deal_price=deal_price,
                deal_miles=deal_miles,
            )
            db.session.add(history)

            # Update alert
            alert.last_triggered = datetime.utcnow()
            alert.trigger_count += 1
            db.session.commit()

            # Send email if enabled
            if alert.email_enabled:
                user = User.query.get(alert.user_id)
                if user and user.email:
                    route = {'origin': alert.origin, 'destination': alert.destination}
                    deal = {
                        'price': deal_price,
                        'miles': deal_miles,
                        'cabin': alert.cabin or 'Economy'
                    }

                    if alert.alert_type == 'price_drop':
                        email_service.send_price_alert(user.email, route, deal)
                    elif alert.alert_type == 'award_available':
                        email_service.send_award_alert(user.email, route, deal)

            return True

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            return False

    @staticmethod
    def check_all_alerts(search_results: dict):
        """Check if any alerts should be triggered based on search results"""
        origin = search_results.get('origin', '').upper()
        destination = search_results.get('destination', '').upper()

        alerts = Alert.query.filter(
            and_(
                Alert.origin == origin,
                Alert.destination == destination,
                Alert.is_active == True
            )
        ).all()

        for alert in alerts:
            if alert.alert_type == 'price_drop':
                flights = search_results.get('flights', [])
                for flight in flights:
                    if alert.threshold_price and flight.get('cash_price', float('inf')) <= alert.threshold_price:
                        AlertHandler.trigger_alert(
                            alert.id,
                            deal_price=flight.get('cash_price'),
                            deal_miles=flight.get('miles_cost')
                        )

            elif alert.alert_type == 'award_available':
                awards = search_results.get('awards', [])
                for award in awards:
                    if alert.threshold_miles and award.get('miles_required', float('inf')) <= alert.threshold_miles:
                        AlertHandler.trigger_alert(
                            alert.id,
                            deal_price=award.get('cash_price'),
                            deal_miles=award.get('miles_required')
                        )
