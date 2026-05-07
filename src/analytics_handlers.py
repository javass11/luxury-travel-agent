"""Analytics and insights handlers for Phase 2"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from .models import db, DealAnalytics, UserAnalytics, SearchLog, PriceHistory

logger = logging.getLogger(__name__)


class DealAnalyticsHandler:
    """Handle deal analytics and trending"""

    @staticmethod
    def record_search(user_id: str, origin: str, destination: str, departure_date: str,
                     cabin: str, results_count: int, filters: dict, duration_ms: int, source: str = 'search'):
        """Record a search for analytics"""
        try:
            search_log = SearchLog(
                user_id=user_id,
                origin=origin.upper(),
                destination=destination.upper(),
                departure_date=datetime.fromisoformat(departure_date).date(),
                cabin=cabin,
                results_count=results_count,
                filters_applied=filters,
                duration_ms=duration_ms,
                source=source,
            )
            db.session.add(search_log)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record search: {e}")
            return False

    @staticmethod
    def update_deal_analytics(origin: str, destination: str, cabin: str = 'economy',
                             prices: list = None, best_cpp: float = None, best_source: str = None):
        """Update analytics for a route"""
        try:
            route_key = f"{origin}{destination}"
            today = datetime.now().date()

            analytics = DealAnalytics.query.filter(
                DealAnalytics.route_key == route_key,
                DealAnalytics.origin == origin,
                DealAnalytics.destination == destination,
                DealAnalytics.cabin == cabin,
                DealAnalytics.date == today
            ).first()

            if not analytics:
                analytics = DealAnalytics(
                    route_key=route_key,
                    origin=origin,
                    destination=destination,
                    cabin=cabin,
                    date=today,
                )
                db.session.add(analytics)

            # Update counts and prices
            analytics.search_count = (analytics.search_count or 0) + 1

            if prices:
                analytics.avg_price = sum(prices) / len(prices)
                analytics.min_price = min(prices)
                analytics.max_price = max(prices)

            if best_cpp:
                analytics.best_cpp = best_cpp

            if best_source:
                analytics.best_source = best_source

            # Detect trending (price dropping)
            yesterday = DealAnalytics.query.filter(
                DealAnalytics.route_key == route_key,
                DealAnalytics.date == today - timedelta(days=1)
            ).first()

            if yesterday and analytics.avg_price and yesterday.avg_price:
                analytics.trending = analytics.avg_price < yesterday.avg_price

            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update deal analytics: {e}")
            return False

    @staticmethod
    def get_trending_routes(days: int = 7, limit: int = 10):
        """Get trending routes based on search volume"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            # Get top routes by search count
            trending = db.session.query(
                SearchLog.origin,
                SearchLog.destination,
                func.count(SearchLog.id).label('search_count'),
                func.count(func.case([(SearchLog.booked == True, 1)])).label('booking_count'),
            ).filter(
                SearchLog.created_at >= start_date
            ).group_by(
                SearchLog.origin,
                SearchLog.destination
            ).order_by(
                func.count(SearchLog.id).desc()
            ).limit(limit).all()

            results = []
            for origin, destination, search_count, booking_count in trending:
                # Get latest analytics
                analytics = DealAnalytics.query.filter(
                    DealAnalytics.origin == origin,
                    DealAnalytics.destination == destination,
                ).order_by(DealAnalytics.date.desc()).first()

                conversion_rate = (booking_count / search_count) if search_count > 0 else 0

                results.append({
                    'origin': origin,
                    'destination': destination,
                    'popularity_score': min(10, search_count / 100),  # Normalize to 0-10
                    'searches': search_count,
                    'bookings': booking_count,
                    'conversion_rate': round(conversion_rate * 100, 2),
                    'avg_price': analytics.avg_price if analytics else None,
                    'best_cpp': analytics.best_cpp if analytics else None,
                    'trending': analytics.trending if analytics else False,
                })

            return results
        except Exception as e:
            logger.error(f"Failed to get trending routes: {e}")
            return []

    @staticmethod
    def get_pricing_patterns(origin: str, destination: str, days: int = 30):
        """Get pricing patterns for a route"""
        try:
            history = PriceHistory.query.filter(
                PriceHistory.origin == origin,
                PriceHistory.destination == destination,
                PriceHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
            ).order_by(PriceHistory.recorded_at.asc()).all()

            if not history:
                return None

            # Analyze patterns
            prices = [h.cash_price for h in history if h.cash_price]
            if not prices:
                return None

            # Best day of week to search (simplified)
            prices_by_day = {}
            for h in history:
                day = h.recorded_at.strftime('%A')
                if day not in prices_by_day:
                    prices_by_day[day] = []
                if h.cash_price:
                    prices_by_day[day].append(h.cash_price)

            best_day = min(prices_by_day.items(), key=lambda x: sum(x[1]) / len(x[1]))[0]

            # Trend analysis
            recent_avg = sum(prices[-7:]) / len(prices[-7:]) if len(prices) >= 7 else prices[-1]
            old_avg = sum(prices[:7]) / len(prices[:7]) if len(prices) >= 7 else prices[0]
            trend_direction = 'down' if recent_avg < old_avg else 'up' if recent_avg > old_avg else 'stable'

            return {
                'route': f"{origin}-{destination}",
                'days_analyzed': days,
                'best_day_to_search': best_day,
                'best_time_to_book': '5-6 weeks advance',  # Simplified
                'price_trend': trend_direction,
                'current_avg_price': round(recent_avg, 2),
                'historical_low': round(min(prices), 2),
                'historical_high': round(max(prices), 2),
                'volatility': round(max(prices) - min(prices), 2),
                'samples': len(prices),
            }
        except Exception as e:
            logger.error(f"Failed to get pricing patterns: {e}")
            return None

    @staticmethod
    def get_deal_insights(limit: int = 20):
        """Get actionable deal insights"""
        try:
            # Get best deals right now
            recent_analytics = DealAnalytics.query.filter(
                DealAnalytics.date == datetime.now().date()
            ).order_by(DealAnalytics.best_cpp.desc()).limit(limit).all()

            best_today = [a.to_dict() for a in recent_analytics if a.best_cpp]

            # Get trending down (prices falling)
            trending_down = [a.to_dict() for a in recent_analytics if a.trending and a.best_cpp]

            # Get high conversion (popular deals)
            high_conversion = DealAnalytics.query.filter(
                DealAnalytics.conversion_rate >= 0.05
            ).order_by(DealAnalytics.best_cpp.desc()).limit(limit).all()

            high_conversion = [a.to_dict() for a in high_conversion if a.best_cpp]

            return {
                'best_today': best_today[:10],
                'trending_down': trending_down[:10],
                'most_booked': high_conversion[:10],
            }
        except Exception as e:
            logger.error(f"Failed to get deal insights: {e}")
            return {'best_today': [], 'trending_down': [], 'most_booked': []}

    @staticmethod
    def get_popular_destinations(days: int = 30, limit: int = 10):
        """Get popular destination cities"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            # Get most searched destinations
            popular = db.session.query(
                SearchLog.destination,
                func.count(SearchLog.id).label('search_count'),
            ).filter(
                SearchLog.created_at >= start_date
            ).group_by(
                SearchLog.destination
            ).order_by(
                func.count(SearchLog.id).desc()
            ).limit(limit).all()

            results = []
            for dest_code, search_count in popular:
                # Get latest analytics for this destination
                analytics = DealAnalytics.query.filter(
                    DealAnalytics.destination == dest_code
                ).order_by(DealAnalytics.date.desc()).first()

                results.append({
                    'iata': dest_code,
                    'search_volume': search_count,
                    'avg_price': analytics.avg_price if analytics else None,
                    'best_cpp': analytics.best_cpp if analytics else None,
                    'trending': analytics.trending if analytics else False,
                })

            return results
        except Exception as e:
            logger.error(f"Failed to get popular destinations: {e}")
            return []


class UserAnalyticsHandler:
    """Handle user behavior analytics"""

    @staticmethod
    def update_user_analytics(user_id: str):
        """Update or create user analytics"""
        try:
            analytics = UserAnalytics.query.filter_by(user_id=user_id).first()

            if not analytics:
                analytics = UserAnalytics(user_id=user_id)
                db.session.add(analytics)

            # Get search stats
            search_logs = SearchLog.query.filter_by(user_id=user_id).all()
            analytics.total_searches = len(search_logs)

            # Get booking stats
            bookings = [s for s in search_logs if s.booked]
            analytics.total_bookings = len(bookings)

            # Get last search date
            if search_logs:
                analytics.last_search_date = max(s.created_at.date() for s in search_logs)

            # Calculate average booking lead time
            if bookings:
                lead_times = []
                for b in bookings:
                    if b.departure_date:
                        lead_days = (b.departure_date - b.created_at.date()).days
                        lead_times.append(lead_days)
                if lead_times:
                    analytics.avg_booking_lead_days = int(sum(lead_times) / len(lead_times))

            # Get favorite routes
            from sqlalchemy import and_
            from collections import Counter

            routes = [(s.origin, s.destination) for s in search_logs]
            if routes:
                route_counts = Counter(routes)
                analytics.favorite_routes = [f"{o}-{d}" for (o, d), _ in route_counts.most_common(5)]

            db.session.commit()
            return analytics.to_dict()
        except Exception as e:
            logger.error(f"Failed to update user analytics: {e}")
            return None

    @staticmethod
    def get_user_analytics(user_id: str):
        """Get user analytics"""
        analytics = UserAnalytics.query.filter_by(user_id=user_id).first()
        if not analytics:
            return UserAnalyticsHandler.update_user_analytics(user_id)
        return analytics.to_dict()
