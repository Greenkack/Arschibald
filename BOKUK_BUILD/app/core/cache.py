"""Intelligent Caching System with Multi-Layer Support"""

import hashlib
import json
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

import builtins

from .config import get_config


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime | None
    tags: set[str] = field(default_factory=set)
    hit_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """Update access metadata"""
        self.hit_count += 1
        self.last_accessed = datetime.now()


class CacheKeys:
    """Centralized cache key management with namespacing"""

    # Namespace prefixes
    USER_SESSION = "user_session"
    FORM_DATA = "form_data"
    JOB_RESULT = "job_result"
    COMPUTED_DATA = "computed"
    QUERY_RESULT = "query"
    WIDGET_STATE = "widget"
    NAVIGATION = "navigation"

    @staticmethod
    def user_session(user_id: str) -> str:
        """Generate user session cache key"""
        return f"{CacheKeys.USER_SESSION}:{user_id}"

    @staticmethod
    def form_data(form_id: str, user_id: str) -> str:
        """Generate form data cache key"""
        return f"{CacheKeys.FORM_DATA}:{form_id}:{user_id}"

    @staticmethod
    def job_result(job_id: str) -> str:
        """Generate job result cache key"""
        return f"{CacheKeys.JOB_RESULT}:{job_id}"

    @staticmethod
    def computed(function_name: str, *args, **kwargs) -> str:
        """Generate computed data cache key with hash"""
        # Create hash of arguments
        args_str = json.dumps(
            {"args": args, "kwargs": kwargs},
            sort_keys=True,
            default=str
        )
        args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
        return f"{CacheKeys.COMPUTED_DATA}:{function_name}:{args_hash}"

    @staticmethod
    def query_result(query: str, params: dict = None) -> str:
        """Generate query result cache key"""
        params_str = json.dumps(params or {}, sort_keys=True, default=str)
        query_hash = hashlib.md5(
            (query + params_str).encode()
        ).hexdigest()[:8]
        return f"{CacheKeys.QUERY_RESULT}:{query_hash}"

    @staticmethod
    def widget_state(widget_key: str, user_id: str) -> str:
        """Generate widget state cache key"""
        return f"{CacheKeys.WIDGET_STATE}:{widget_key}:{user_id}"

    @staticmethod
    def navigation(user_id: str) -> str:
        """Generate navigation cache key"""
        return f"{CacheKeys.NAVIGATION}:{user_id}"

    @staticmethod
    def custom(namespace: str, *parts: str) -> str:
        """Generate custom cache key"""
        return ":".join([namespace] + list(parts))


class InMemoryCache:
    """In-memory cache with LRU eviction and TTL support"""

    def __init__(self, max_entries: int = 1000, default_ttl: int = 3600):
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0
        }

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                logger.debug("Cache miss", key=key, layer="memory")
                return None

            if entry.is_expired():
                self._cache.pop(key)
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                logger.debug("Cache expired", key=key, layer="memory")
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats["hits"] += 1
            logger.debug("Cache hit", key=key, layer="memory")
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        tags: set[str] = None
    ) -> None:
        """Set value in cache"""
        with self._lock:
            # Calculate expiration
            ttl_seconds = ttl if ttl is not None else self.default_ttl
            expires_at = None
            if ttl_seconds > 0:
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

            # Estimate size
            try:
                size_bytes = len(json.dumps(value, default=str).encode())
            except Exception:
                size_bytes = 0

            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                tags=tags or set(),
                size_bytes=size_bytes
            )

            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)

            # Evict if over capacity
            while len(self._cache) > self.max_entries:
                evicted_key, _ = self._cache.popitem(last=False)
                self._stats["evictions"] += 1
                logger.debug("Cache eviction", key=evicted_key, layer="memory")

            logger.debug("Cache set", key=key, ttl=ttl_seconds, layer="memory")

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("Cache delete", key=key, layer="memory")
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared", layer="memory")

    def invalidate_by_tags(self, tags: builtins.set[str]) -> int:
        """Invalidate all entries with matching tags"""
        with self._lock:
            keys_to_delete = []
            for key, entry in self._cache.items():
                if entry.tags & tags:  # Intersection
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del self._cache[key]

            logger.info(
                "Cache invalidated by tags",
                tags=list(tags),
                count=len(keys_to_delete),
                layer="memory"
            )
            return len(keys_to_delete)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests
                if total_requests > 0
                else 0.0
            )

            total_size = sum(
                entry.size_bytes for entry in self._cache.values()
            )

            return {
                "layer": "memory",
                "entries": len(self._cache),
                "max_entries": self.max_entries,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": hit_rate,
                "evictions": self._stats["evictions"],
                "expirations": self._stats["expirations"],
                "total_size_bytes": total_size
            }

    def get_all_keys(self) -> list[str]:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())

    def get_entry(self, key: str) -> CacheEntry | None:
        """Get cache entry with metadata"""
        with self._lock:
            return self._cache.get(key)


class StreamlitCacheWrapper:
    """Wrapper for Streamlit's caching with enhanced tagging"""

    def __init__(self):
        self._tag_registry: dict[str, set[str]] = {}
        self._lock = threading.RLock()

    def cache_data(
        self,
        func: Callable = None,
        ttl: int | None = None,
        tags: set[str] = None,
        **kwargs
    ):
        """Wrapper for st.cache_data with tagging"""
        if not STREAMLIT_AVAILABLE or not st:
            # Fallback to regular function call
            def decorator(f):
                return f
            return decorator if func is None else decorator(func)

        # Register tags
        if tags:
            func_name = func.__name__ if func else None
            if func_name:
                with self._lock:
                    if func_name not in self._tag_registry:
                        self._tag_registry[func_name] = set()
                    self._tag_registry[func_name].update(tags)

        # Apply Streamlit cache
        cache_kwargs = kwargs.copy()
        if ttl is not None:
            cache_kwargs["ttl"] = ttl

        return st.cache_data(**cache_kwargs)(func) if func else (
            st.cache_data(**cache_kwargs)
        )

    def cache_resource(
        self,
        func: Callable = None,
        tags: set[str] = None,
        **kwargs
    ):
        """Wrapper for st.cache_resource with tagging"""
        if not STREAMLIT_AVAILABLE or not st:
            def decorator(f):
                return f
            return decorator if func is None else decorator(func)

        # Register tags
        if tags:
            func_name = func.__name__ if func else None
            if func_name:
                with self._lock:
                    if func_name not in self._tag_registry:
                        self._tag_registry[func_name] = set()
                    self._tag_registry[func_name].update(tags)

        return st.cache_resource(**kwargs)(func) if func else (
            st.cache_resource(**kwargs)
        )

    def clear_by_tags(self, tags: set[str]) -> int:
        """Clear Streamlit cache by tags"""
        if not STREAMLIT_AVAILABLE or not st:
            return 0

        count = 0
        with self._lock:
            for func_name, func_tags in self._tag_registry.items():
                if func_tags & tags:
                    try:
                        st.cache_data.clear()
                        count += 1
                    except Exception as e:
                        logger.warning(
                            "Failed to clear Streamlit cache",
                            func=func_name,
                            error=str(e)
                        )

        logger.info(
            "Streamlit cache cleared by tags",
            tags=list(tags),
            count=count
        )
        return count


class DatabaseCache:
    """Database-level caching for expensive query results"""

    def __init__(self):
        self._enabled = True

    def get(self, key: str) -> Any | None:
        """Get value from database cache"""
        if not self._enabled:
            return None

        try:
            from .database import get_db_manager
            db = get_db_manager()

            query = """
                SELECT value, expires_at
                FROM cache_entries
                WHERE key = :key
                AND (expires_at IS NULL OR expires_at > :now)
            """

            result = db.execute_raw(
                query,
                {"key": key, "now": datetime.now()}
            ).fetchone()

            if result:
                value_json, _ = result
                value = json.loads(value_json)
                logger.debug("Cache hit", key=key, layer="database")
                return value

            logger.debug("Cache miss", key=key, layer="database")
            return None

        except Exception as e:
            logger.warning(
                "Database cache get failed",
                key=key,
                error=str(e)
            )
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        tags: set[str] = None
    ) -> None:
        """Set value in database cache"""
        if not self._enabled:
            return

        try:
            from .database import get_db_manager
            db = get_db_manager()

            expires_at = None
            if ttl and ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=ttl)

            value_json = json.dumps(value, default=str)
            tags_json = json.dumps(list(tags or []))

            query = """
                INSERT OR REPLACE INTO cache_entries
                (key, value, tags, created_at, expires_at)
                VALUES (:key, :value, :tags, :created_at, :expires_at)
            """

            db.execute_raw(query, {
                "key": key,
                "value": value_json,
                "tags": tags_json,
                "created_at": datetime.now(),
                "expires_at": expires_at
            })

            logger.debug("Cache set", key=key, layer="database")

        except Exception as e:
            logger.warning(
                "Database cache set failed",
                key=key,
                error=str(e)
            )

    def delete(self, key: str) -> bool:
        """Delete key from database cache"""
        if not self._enabled:
            return False

        try:
            from .database import get_db_manager
            db = get_db_manager()

            query = "DELETE FROM cache_entries WHERE key = :key"
            db.execute_raw(query, {"key": key})

            logger.debug("Cache delete", key=key, layer="database")
            return True

        except Exception as e:
            logger.warning(
                "Database cache delete failed",
                key=key,
                error=str(e)
            )
            return False

    def clear(self) -> None:
        """Clear all database cache entries"""
        if not self._enabled:
            return

        try:
            from .database import get_db_manager
            db = get_db_manager()

            query = "DELETE FROM cache_entries"
            db.execute_raw(query)

            logger.info("Cache cleared", layer="database")

        except Exception as e:
            logger.warning("Database cache clear failed", error=str(e))

    def invalidate_by_tags(self, tags: builtins.set[str]) -> int:
        """Invalidate database cache entries by tags"""
        if not self._enabled:
            return 0

        try:
            from .database import get_db_manager
            db = get_db_manager()

            # This is a simplified version - proper implementation would
            # need JSON query support
            query = "DELETE FROM cache_entries WHERE 1=0"
            for tag in tags:
                query += f" OR tags LIKE '%{tag}%'"

            result = db.execute_raw(query)
            count = result.rowcount if hasattr(result, 'rowcount') else 0

            logger.info(
                "Database cache invalidated by tags",
                tags=list(tags),
                count=count
            )
            return count

        except Exception as e:
            logger.warning(
                "Database cache invalidation failed",
                error=str(e)
            )
            return 0


class MultiLayerCache:
    """Multi-layer cache coordinator (memory + Streamlit + database)"""

    def __init__(self):
        config = get_config()
        self.memory_cache = InMemoryCache(
            max_entries=config.cache.max_entries,
            default_ttl=config.cache.default_ttl
        )
        self.streamlit_cache = StreamlitCacheWrapper()
        self.database_cache = DatabaseCache()
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """Get value from cache (checks all layers)"""
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            return value

        # Try database cache
        value = self.database_cache.get(key)
        if value is not None:
            # Populate memory cache
            self.memory_cache.set(key, value)
            return value

        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        tags: set[str] = None,
        layers: set[str] = None
    ) -> None:
        """Set value in cache (all layers by default)"""
        layers = layers or {"memory", "database"}

        if "memory" in layers:
            self.memory_cache.set(key, value, ttl, tags)

        if "database" in layers:
            self.database_cache.set(key, value, ttl, tags)

    def delete(self, key: str) -> bool:
        """Delete key from all cache layers"""
        memory_deleted = self.memory_cache.delete(key)
        db_deleted = self.database_cache.delete(key)
        return memory_deleted or db_deleted

    def clear(self) -> None:
        """Clear all cache layers"""
        self.memory_cache.clear()
        self.database_cache.clear()
        if STREAMLIT_AVAILABLE and st:
            try:
                st.cache_data.clear()
                st.cache_resource.clear()
            except Exception as e:
                logger.warning("Failed to clear Streamlit cache", error=str(e))

    def invalidate_by_tags(self, tags: builtins.set[str]) -> int:
        """Invalidate cache entries by tags across all layers"""
        count = 0
        count += self.memory_cache.invalidate_by_tags(tags)
        count += self.streamlit_cache.clear_by_tags(tags)
        count += self.database_cache.invalidate_by_tags(tags)
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get statistics from all cache layers"""
        return {
            "memory": self.memory_cache.get_stats(),
            "streamlit": {
                "layer": "streamlit",
                "available": STREAMLIT_AVAILABLE
            },
            "database": {
                "layer": "database",
                "enabled": self.database_cache._enabled
            }
        }


# Global cache instance
_cache: MultiLayerCache | None = None
_cache_lock = threading.Lock()


def get_cache() -> MultiLayerCache:
    """Get global cache instance"""
    global _cache
    with _cache_lock:
        if _cache is None:
            _cache = MultiLayerCache()
    return _cache


def get_or_compute(
    key: str,
    fn: Callable[[], Any],
    ttl: int | None = None,
    tags: set[str] = None,
    force_refresh: bool = False
) -> Any:
    """
    Get value from cache or compute and cache it

    Args:
        key: Cache key
        fn: Function to compute value if not cached
        ttl: Time to live in seconds (None = use default)
        tags: Tags for cache invalidation
        force_refresh: If True, bypass cache and recompute

    Returns:
        Cached or computed value
    """
    cache = get_cache()

    # Check cache unless force refresh
    if not force_refresh:
        value = cache.get(key)
        if value is not None:
            return value

    # Compute value
    start_time = time.time()
    value = fn()
    compute_time = time.time() - start_time

    # Cache the result
    cache.set(key, value, ttl, tags)

    logger.debug(
        "Value computed and cached",
        key=key,
        compute_time_ms=int(compute_time * 1000)
    )

    return value


def invalidate_cache(tags: set[str] = None, keys: list[str] = None) -> int:
    """
    Invalidate cache entries

    Args:
        tags: Tags to invalidate
        keys: Specific keys to invalidate

    Returns:
        Number of entries invalidated
    """
    cache = get_cache()
    count = 0

    if tags:
        count += cache.invalidate_by_tags(tags)

    if keys:
        for key in keys:
            if cache.delete(key):
                count += 1

    logger.info("Cache invalidated", tags=list(tags or []), count=count)
    return count


def clear_cache() -> None:
    """Clear all cache layers"""
    cache = get_cache()
    cache.clear()
    logger.info("All caches cleared")


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics"""
    cache = get_cache()
    return cache.get_stats()
