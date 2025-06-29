import json
import hashlib
from typing import Any, Optional, Union
from functools import wraps
import redis
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager for application data."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis server."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning("Failed to connect to Redis, caching disabled", error=str(e))
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args: Any) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error("Cache pattern invalidation failed", pattern=pattern, error=str(e))
        return 0


# Global cache instance
cache = CacheManager()


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, *args, *kwargs.values())
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit", function=func.__name__, key=cache_key)
                return cached_result
            
            # Execute function
            logger.debug("Cache miss", function=func.__name__, key=cache_key)
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, *args, *kwargs.values())
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit", function=func.__name__, key=cache_key)
                return cached_result
            
            # Execute function
            logger.debug("Cache miss", function=func.__name__, key=cache_key)
            result = func(*args, **kwargs)
            
            # Cache the result
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_competitor_research(ttl: int = 7200):
    """Cache decorator specifically for competitor research (2 hours TTL)."""
    return cached("competitor_research", ttl)


def cache_language_detection(ttl: int = 86400):
    """Cache decorator for language detection (24 hours TTL)."""
    return cached("language_detection", ttl)


def cache_image_search(ttl: int = 3600):
    """Cache decorator for image search results (1 hour TTL)."""
    return cached("image_search", ttl)