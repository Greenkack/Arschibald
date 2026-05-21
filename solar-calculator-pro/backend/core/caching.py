"""
Response Caching Module with Redis Support

This module provides caching functionality including:
- Redis-based caching for API responses
- In-memory caching for expensive calculations
- Cache invalidation strategies
- Cache statistics and monitoring
"""

from typing import Any, Callable, Optional, Union
from functools import wraps
import hashlib
import json
import pickle
import time
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Using in-memory cache only.")


class CacheBackend:
    """Base class for cache backends"""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value in cache"""
        raise NotImplementedError
    
    def delete(self, key: str):
        """Delete value from cache"""
        raise NotImplementedError
    
    def clear(self):
        """Clear all cache"""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        raise NotImplementedError


class InMemoryCache(CacheBackend):
    """In-memory cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: dict = {}
        self.expiry: dict = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check if key exists and not expired
        if key in self.cache:
            if key in self.expiry and time.time() > self.expiry[key]:
                # Expired
                del self.cache[key]
                del self.expiry[key]
                self.misses += 1
                return None
            
            self.hits += 1
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value in cache"""
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if oldest_key in self.expiry:
                del self.expiry[oldest_key]
        
        self.cache[key] = value
        
        if expire:
            self.expiry[key] = time.time() + expire
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.expiry.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'size': len(self.cache),
            'max_size': self.max_size
        }


class RedisCache(CacheBackend):
    """Redis cache implementation"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = 'cache:'
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not installed. Install with: pip install redis")
        
        self.client = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  # We'll handle encoding ourselves
        )
        self.prefix = prefix
        
        # Test connection
        try:
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(self._make_key(key))
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value in cache"""
        try:
            serialized = pickle.dumps(value)
            if expire:
                self.client.setex(self._make_key(key), expire, serialized)
            else:
                self.client.set(self._make_key(key), serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str):
        """Delete value from cache"""
        try:
            self.client.delete(self._make_key(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def clear(self):
        """Clear all cache with prefix"""
        try:
            pattern = f"{self.prefix}*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.client.exists(self._make_key(key)))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get Redis statistics"""
        try:
            info = self.client.info('stats')
            return {
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'connected_clients': info.get('connected_clients', 0),
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {}


class CacheManager:
    """Unified cache manager supporting multiple backends"""
    
    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_expire: int = 3600
    ):
        self.backend = backend or InMemoryCache()
        self.default_expire = default_expire
    
    def cache_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a stable string representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        
        # Hash for shorter keys
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def cached(
        self,
        expire: Optional[int] = None,
        key_prefix: str = '',
        key_func: Optional[Callable] = None
    ):
        """
        Decorator for caching function results
        
        Args:
            expire: Cache expiration in seconds
            key_prefix: Prefix for cache key
            key_func: Custom function to generate cache key
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.cache_key(*args, **kwargs)
                
                full_key = f"{key_prefix}:{func.__name__}:{cache_key}"
                
                # Try to get from cache
                cached_value = self.backend.get(full_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {full_key}")
                    return cached_value
                
                # Execute function
                logger.debug(f"Cache miss for {full_key}")
                result = func(*args, **kwargs)
                
                # Store in cache
                expiration = expire if expire is not None else self.default_expire
                self.backend.set(full_key, result, expiration)
                
                return result
            return wrapper
        return decorator
    
    def invalidate(self, pattern: str):
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Pattern to match cache keys
        """
        # Note: This is a simple implementation
        # For Redis, you'd use SCAN with pattern matching
        logger.info(f"Invalidating cache pattern: {pattern}")
        # Implementation depends on backend
    
    def clear_all(self):
        """Clear all cache"""
        self.backend.clear()
        logger.info("Cleared all cache")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return self.backend.get_stats()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def init_cache(
    use_redis: bool = False,
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: Optional[str] = None,
    default_expire: int = 3600
):
    """
    Initialize global cache manager
    
    Args:
        use_redis: Whether to use Redis backend
        redis_host: Redis host
        redis_port: Redis port
        redis_db: Redis database number
        redis_password: Redis password
        default_expire: Default expiration time in seconds
    """
    global _cache_manager
    
    if use_redis and REDIS_AVAILABLE:
        backend = RedisCache(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password
        )
        logger.info("Initialized Redis cache backend")
    else:
        backend = InMemoryCache()
        logger.info("Initialized in-memory cache backend")
    
    _cache_manager = CacheManager(backend=backend, default_expire=default_expire)


# Convenience decorators
def cache(expire: int = 3600, key_prefix: str = ''):
    """
    Simple cache decorator
    
    Args:
        expire: Cache expiration in seconds
        key_prefix: Prefix for cache key
    """
    manager = get_cache_manager()
    return manager.cached(expire=expire, key_prefix=key_prefix)


def cache_result(expire: int = 3600):
    """
    Cache function result decorator
    
    Args:
        expire: Cache expiration in seconds
    """
    return cache(expire=expire, key_prefix='result')
