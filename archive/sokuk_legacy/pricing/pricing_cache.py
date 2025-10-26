"""Intelligent Pricing Calculation Caching System

This module provides a comprehensive caching system for pricing calculations
with intelligent cache invalidation, performance monitoring, and benchmarking.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for different types of data"""
    COMPONENT = "component"  # Individual component pricing
    SYSTEM = "system"       # Complete system pricing
    MODIFICATION = "modification"  # Pricing modifications
    FINAL = "final"         # Final pricing results


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"             # Time-to-live based
    LRU = "lru"             # Least recently used
    DEPENDENCY = "dependency"  # Dependency-based invalidation
    HYBRID = "hybrid"       # Combination of strategies


@dataclass
class CacheEntry:
    """Represents a single cache entry"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    ttl_seconds: int | None = None

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)

    def touch(self) -> None:
        """Update access time and count"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    memory_usage_bytes: int = 0
    avg_access_time_ms: float = 0.0
    hit_rate: float = 0.0

    def update_hit_rate(self) -> None:
        """Update hit rate calculation"""
        total_requests = self.hits + self.misses
        self.hit_rate = (
            self.hits /
            total_requests) if total_requests > 0 else 0.0


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics"""
    operation_name: str
    start_time: float
    end_time: float | None = None
    duration_ms: float | None = None
    cache_hit: bool = False
    cache_level: CacheLevel | None = None

    def finish(self) -> None:
        """Mark operation as finished and calculate duration"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


class PricingCache:
    """Intelligent caching system for pricing calculations"""

    def __init__(self,
                 max_size: int = 1000,
                 default_ttl: int = 300,  # 5 minutes
                 strategy: CacheStrategy = CacheStrategy.HYBRID,
                 enable_monitoring: bool = True):
        """Initialize pricing cache

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
            strategy: Cache invalidation strategy
            enable_monitoring: Enable performance monitoring
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self.enable_monitoring = enable_monitoring

        # Cache storage by level
        self._caches: dict[CacheLevel, OrderedDict[str, CacheEntry]] = {
            level: OrderedDict() for level in CacheLevel
        }

        # Dependency tracking
        self._dependencies: dict[str, list[str]] = defaultdict(list)
        self._reverse_dependencies: dict[str, list[str]] = defaultdict(list)

        # Performance monitoring
        self._stats: dict[CacheLevel, CacheStats] = {
            level: CacheStats() for level in CacheLevel
        }
        self._performance_metrics: list[PerformanceMetrics] = []
        self._lock = threading.RLock()

        # Cache configuration by level
        self._level_config = {
            # 10 minutes
            CacheLevel.COMPONENT: {"ttl": 600, "max_size": max_size // 2},
            # 5 minutes
            CacheLevel.SYSTEM: {"ttl": 300, "max_size": max_size // 5},
            # 3 minutes
            CacheLevel.MODIFICATION: {"ttl": 180, "max_size": max_size // 10},
            CacheLevel.FINAL: {
                "ttl": 120,
                "max_size": max_size //
                5}       # 2 minutes
        }

        logger.info(
            f"Initialized PricingCache with strategy={
                strategy.value}, max_size={max_size}")

    def get(
            self,
            key: str,
            level: CacheLevel = CacheLevel.FINAL) -> Any | None:
        """Get value from cache

        Args:
            key: Cache key
            level: Cache level

        Returns:
            Cached value if found and valid, None otherwise
        """
        with self._lock:
            metric = self._start_performance_metric(f"cache_get_{level.value}")

            try:
                cache = self._caches[level]
                stats = self._stats[level]

                if key not in cache:
                    stats.misses += 1
                    stats.update_hit_rate()
                    return None

                entry = cache[key]

                # Check if expired
                if entry.is_expired():
                    del cache[key]
                    stats.misses += 1
                    stats.evictions += 1
                    stats.total_entries = len(cache)
                    stats.update_hit_rate()
                    return None

                # Update access info
                entry.touch()

                # Move to end for LRU
                if self.strategy in [CacheStrategy.LRU, CacheStrategy.HYBRID]:
                    cache.move_to_end(key)

                stats.hits += 1
                stats.update_hit_rate()
                metric.cache_hit = True
                metric.cache_level = level

                logger.debug(f"Cache hit for key={key}, level={level.value}")
                return entry.value

            finally:
                metric.finish()
                if self.enable_monitoring:
                    self._performance_metrics.append(metric)

    def put(
            self,
            key: str,
            value: Any,
            level: CacheLevel = CacheLevel.FINAL,
            ttl: int | None = None,
            dependencies: list[str] | None = None) -> None:
        """Put value in cache

        Args:
            key: Cache key
            value: Value to cache
            level: Cache level
            ttl: Time-to-live in seconds (uses default if None)
            dependencies: List of dependency keys
        """
        with self._lock:
            metric = self._start_performance_metric(f"cache_put_{level.value}")

            try:
                cache = self._caches[level]
                stats = self._stats[level]
                config = self._level_config[level]

                # Use level-specific TTL if not provided
                if ttl is None:
                    ttl = config["ttl"]

                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    dependencies=dependencies or [],
                    ttl_seconds=ttl
                )

                # Add to cache
                cache[key] = entry

                # Update dependency tracking
                if dependencies:
                    self._dependencies[key] = dependencies
                    for dep in dependencies:
                        self._reverse_dependencies[dep].append(key)

                # Enforce size limits
                max_size = config["max_size"]
                while len(cache) > max_size:
                    self._evict_entry(cache, stats)

                stats.total_entries = len(cache)

                logger.debug(
                    f"Cached key={key}, level={
                        level.value}, ttl={ttl}s")

            finally:
                metric.finish()
                if self.enable_monitoring:
                    self._performance_metrics.append(metric)

    def invalidate(self, key: str, level: CacheLevel | None = None,
                   cascade: bool = True) -> int:
        """Invalidate cache entry(ies)

        Args:
            key: Cache key to invalidate
            level: Specific cache level (all levels if None)
            cascade: Whether to cascade invalidation to dependents

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            metric = self._start_performance_metric("cache_invalidate")
            invalidated_count = 0

            try:
                levels_to_check = [level] if level else list(CacheLevel)

                for cache_level in levels_to_check:
                    cache = self._caches[cache_level]
                    stats = self._stats[cache_level]

                    if key in cache:
                        del cache[key]
                        stats.evictions += 1
                        stats.total_entries = len(cache)
                        invalidated_count += 1

                        logger.debug(
                            f"Invalidated key={key}, level={
                                cache_level.value}")

                # Cascade invalidation to dependents
                if cascade and key in self._reverse_dependencies:
                    for dependent_key in self._reverse_dependencies[key]:
                        invalidated_count += self.invalidate(
                            dependent_key, cascade=True)

                # Clean up dependency tracking
                if key in self._dependencies:
                    for dep in self._dependencies[key]:
                        if key in self._reverse_dependencies[dep]:
                            self._reverse_dependencies[dep].remove(key)
                    del self._dependencies[key]

                if key in self._reverse_dependencies:
                    del self._reverse_dependencies[key]

                return invalidated_count

            finally:
                metric.finish()
                if self.enable_monitoring:
                    self._performance_metrics.append(metric)

    def invalidate_by_pattern(
            self,
            pattern: str,
            level: CacheLevel | None = None) -> int:
        """Invalidate cache entries matching pattern

        Args:
            pattern: Pattern to match (simple string contains)
            level: Specific cache level (all levels if None)

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            invalidated_count = 0
            levels_to_check = [level] if level else list(CacheLevel)

            for cache_level in levels_to_check:
                cache = self._caches[cache_level]
                keys_to_remove = [
                    key for key in cache.keys() if pattern in key]

                for key in keys_to_remove:
                    invalidated_count += self.invalidate(
                        key, cache_level, cascade=False)

            logger.info(
                f"Invalidated {invalidated_count} entries matching pattern: {pattern}")
            return invalidated_count

    def clear(self, level: CacheLevel | None = None) -> int:
        """Clear cache entries

        Args:
            level: Specific cache level (all levels if None)

        Returns:
            Number of entries cleared
        """
        with self._lock:
            cleared_count = 0
            levels_to_clear = [level] if level else list(CacheLevel)

            for cache_level in levels_to_clear:
                cache = self._caches[cache_level]
                stats = self._stats[cache_level]

                cleared_count += len(cache)
                cache.clear()
                stats.total_entries = 0

                logger.info(
                    f"Cleared {
                        len(cache)} entries from level: {
                        cache_level.value}")

            # Clear dependency tracking if clearing all levels
            if level is None:
                self._dependencies.clear()
                self._reverse_dependencies.clear()

            return cleared_count

    def get_stats(self, level: CacheLevel |
                  None = None) -> dict[str, CacheStats]:
        """Get cache statistics

        Args:
            level: Specific cache level (all levels if None)

        Returns:
            Dictionary of cache statistics by level
        """
        with self._lock:
            if level:
                return {level.value: self._stats[level]}
            return {level.value: stats for level, stats in self._stats.items()}

    def get_performance_metrics(self,
                                operation_filter: str | None = None,
                                limit: int = 100) -> list[PerformanceMetrics]:
        """Get performance metrics

        Args:
            operation_filter: Filter by operation name
            limit: Maximum number of metrics to return

        Returns:
            List of performance metrics
        """
        with self._lock:
            metrics = self._performance_metrics[-limit:]

            if operation_filter:
                metrics = [
                    m for m in metrics if operation_filter in m.operation_name]

            return metrics

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries

        Returns:
            Number of entries cleaned up
        """
        with self._lock:
            cleaned_count = 0

            for level in CacheLevel:
                cache = self._caches[level]
                stats = self._stats[level]

                expired_keys = [
                    key for key, entry in cache.items()
                    if entry.is_expired()
                ]

                for key in expired_keys:
                    del cache[key]
                    cleaned_count += 1

                stats.evictions += len(expired_keys)
                stats.total_entries = len(cache)

            logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            return cleaned_count

    def _evict_entry(self, cache: OrderedDict, stats: CacheStats) -> None:
        """Evict an entry based on strategy"""
        if self.strategy == CacheStrategy.LRU or self.strategy == CacheStrategy.HYBRID:
            # Remove least recently used (first item in OrderedDict)
            if cache:
                key, _ = cache.popitem(last=False)
                stats.evictions += 1
                logger.debug(f"Evicted LRU entry: {key}")
        elif self.strategy == CacheStrategy.TTL:
            # Remove oldest entry
            if cache:
                key, _ = cache.popitem(last=False)
                stats.evictions += 1
                logger.debug(f"Evicted oldest entry: {key}")

    def _start_performance_metric(
            self, operation_name: str) -> PerformanceMetrics:
        """Start performance metric tracking"""
        return PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time()
        )


class PricingCacheManager:
    """Manager for pricing cache with intelligent key generation and invalidation"""

    def __init__(self, cache: PricingCache | None = None):
        """Initialize cache manager

        Args:
            cache: PricingCache instance (creates default if None)
        """
        self.cache = cache or PricingCache()
        self.logger = logging.getLogger(f"{__name__}.PricingCacheManager")

    def generate_component_key(self,
                               product_id: int,
                               quantity: int,
                               modifications: dict[str,
                                                   Any] | None = None) -> str:
        """Generate cache key for component pricing

        Args:
            product_id: Product ID
            quantity: Quantity
            modifications: Optional modifications

        Returns:
            Cache key string
        """
        key_data = {
            "type": "component",
            "product_id": product_id,
            "quantity": quantity,
            "modifications": modifications or {}
        }
        return self._hash_key_data(key_data)

    def generate_system_key(self, components: list[dict[str, Any]],
                            system_type: str = "pv") -> str:
        """Generate cache key for system pricing

        Args:
            components: List of component data
            system_type: Type of system

        Returns:
            Cache key string
        """
        # Sort components for consistent key generation
        sorted_components = sorted(
            components,
            key=lambda x: (x.get('product_id', 0), x.get('quantity', 0))
        )

        key_data = {
            "type": "system",
            "system_type": system_type,
            "components": sorted_components
        }
        return self._hash_key_data(key_data)

    def generate_final_key(self, calculation_data: dict[str, Any]) -> str:
        """Generate cache key for final pricing calculation

        Args:
            calculation_data: Complete calculation data

        Returns:
            Cache key string
        """
        # Create normalized data for consistent hashing
        normalized_data = {
            "type": "final",
            "components": sorted(
                calculation_data.get("components", []),
                key=lambda x: (x.get('product_id', 0), x.get('quantity', 0))
            ),
            "modifications": calculation_data.get("modifications", {}),
            "vat_rate": calculation_data.get("vat_rate", 19.0),
            "system_type": calculation_data.get("system_type", "pv")
        }
        return self._hash_key_data(normalized_data)

    def cache_component_pricing(self, key: str, pricing_data: Any,
                                dependencies: list[str] | None = None) -> None:
        """Cache component pricing data

        Args:
            key: Cache key
            pricing_data: Pricing data to cache
            dependencies: Optional dependencies
        """
        self.cache.put(
            key,
            pricing_data,
            CacheLevel.COMPONENT,
            dependencies=dependencies)

    def cache_system_pricing(self, key: str, pricing_data: Any,
                             component_keys: list[str] | None = None) -> None:
        """Cache system pricing data

        Args:
            key: Cache key
            pricing_data: Pricing data to cache
            component_keys: Component cache keys as dependencies
        """
        self.cache.put(
            key,
            pricing_data,
            CacheLevel.SYSTEM,
            dependencies=component_keys)

    def cache_final_pricing(self, key: str, pricing_data: Any,
                            system_key: str | None = None) -> None:
        """Cache final pricing data

        Args:
            key: Cache key
            pricing_data: Pricing data to cache
            system_key: System cache key as dependency
        """
        dependencies = [system_key] if system_key else None
        self.cache.put(
            key,
            pricing_data,
            CacheLevel.FINAL,
            dependencies=dependencies)

    def get_component_pricing(self, key: str) -> Any | None:
        """Get cached component pricing"""
        return self.cache.get(key, CacheLevel.COMPONENT)

    def get_system_pricing(self, key: str) -> Any | None:
        """Get cached system pricing"""
        return self.cache.get(key, CacheLevel.SYSTEM)

    def get_final_pricing(self, key: str) -> Any | None:
        """Get cached final pricing"""
        return self.cache.get(key, CacheLevel.FINAL)

    def invalidate_product_cache(self, product_id: int) -> int:
        """Invalidate all cache entries for a specific product

        Args:
            product_id: Product ID to invalidate

        Returns:
            Number of entries invalidated
        """
        pattern = f"product_id\":{product_id}"
        return self.cache.invalidate_by_pattern(pattern)

    def invalidate_system_cache(self, system_type: str) -> int:
        """Invalidate all cache entries for a system type

        Args:
            system_type: System type to invalidate

        Returns:
            Number of entries invalidated
        """
        pattern = f"system_type\":\"{system_type}\""
        return self.cache.invalidate_by_pattern(pattern)

    def _hash_key_data(self, key_data: dict[str, Any]) -> str:
        """Generate hash from key data

        Args:
            key_data: Data to hash

        Returns:
            Hash string
        """
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()


# Global cache instance
_global_cache: PricingCache | None = None
_global_cache_manager: PricingCacheManager | None = None


def get_pricing_cache() -> PricingCache:
    """Get global pricing cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = PricingCache()
    return _global_cache


def get_cache_manager() -> PricingCacheManager:
    """Get global cache manager instance"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = PricingCacheManager(get_pricing_cache())
    return _global_cache_manager


def reset_global_cache() -> None:
    """Reset global cache instances (mainly for testing)"""
    global _global_cache, _global_cache_manager
    _global_cache = None
    _global_cache_manager = None
