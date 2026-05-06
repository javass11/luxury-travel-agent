import os
import json
import logging
from typing import Optional, Any, List, Dict

logger = logging.getLogger(__name__)


class CacheClient:
    """
    Simple caching client with Redis support.
    Falls back to in-memory cache if Redis is unavailable.
    """

    def __init__(self):
        self.redis_client = None
        self.in_memory_cache: Dict[str, Any] = {}
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        except ImportError:
            logger.warning("Redis not installed, using in-memory cache")
            self.redis_client = None
        except Exception as e:
            logger.warning(f"Redis connection failed ({str(e)}), using in-memory cache")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(value)
            else:
                if key in self.in_memory_cache:
                    logger.debug(f"Cache HIT (memory): {key}")
                    return self.in_memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get failed: {e}")

        logger.debug(f"Cache MISS: {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
                logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
                return True
            else:
                self.in_memory_cache[key] = value
                logger.debug(f"Cache SET (memory): {key}")
                return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            elif key in self.in_memory_cache:
                del self.in_memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False

    def flush_pattern(self, pattern: str = "*") -> bool:
        """Flush cache keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Flushed {len(keys)} cache keys matching {pattern}")
            else:
                # For in-memory cache, flush matching keys
                to_delete = [k for k in self.in_memory_cache.keys() if self._pattern_match(k, pattern)]
                for k in to_delete:
                    del self.in_memory_cache[k]
                logger.info(f"Flushed {len(to_delete)} cache keys matching {pattern}")
            return True
        except Exception as e:
            logger.error(f"Cache flush failed: {e}")
            return False

    def _pattern_match(self, text: str, pattern: str) -> bool:
        """Simple pattern matching (e.g., flights:* matches flights:ORD:MIA)"""
        if pattern == "*":
            return True
        pattern = pattern.replace("*", ".*")
        import re
        return bool(re.match(pattern, text))

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'backend': 'redis',
                    'used_memory_mb': info.get('used_memory', 0) / 1024 / 1024,
                    'keys': self.redis_client.dbsize(),
                    'status': 'connected'
                }
            else:
                return {
                    'backend': 'memory',
                    'keys': len(self.in_memory_cache),
                    'status': 'active'
                }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'status': 'error'}


# Global cache instance
cache = CacheClient()
