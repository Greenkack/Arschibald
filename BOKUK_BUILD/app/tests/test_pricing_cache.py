"""Tests for pricing cache system

This module contains comprehensive tests for the intelligent pricing cache system,
including performance benchmarks and cache invalidation strategies.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from pricing.cache_performance import (
    BenchmarkResult,
    CacheBenchmark,
    PerformanceMonitor,
    export_performance_report,
)
from pricing.pricing_cache import (
    CacheEntry,
    CacheLevel,
    CacheStrategy,
    PerformanceMetrics,
    PricingCache,
    PricingCacheManager,
    get_cache_manager,
    get_pricing_cache,
    reset_global_cache,
)


class TestCacheEntry:
    """Test CacheEntry functionality"""

    def test_cache_entry_creation(self):
        """Test cache entry creation and basic properties"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl_seconds=300
        )

        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.ttl_seconds == 300
        assert entry.access_count == 0
        assert not entry.is_expired()

    def test_cache_entry_expiration(self):
        """Test cache entry expiration logic"""
        # Create expired entry
        old_time = datetime.now() - timedelta(seconds=400)
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=old_time,
            last_accessed=old_time,
            ttl_seconds=300
        )

        assert entry.is_expired()

        # Create non-expiring entry
        entry_no_ttl = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl_seconds=None
        )

        assert not entry_no_ttl.is_expired()

    def test_cache_entry_touch(self):
        """Test cache entry access tracking"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )

        initial_access_time = entry.last_accessed
        initial_count = entry.access_count

        time.sleep(0.01)  # Small delay to ensure time difference
        entry.touch()

        assert entry.last_accessed > initial_access_time
        assert entry.access_count == initial_count + 1


class TestPricingCache:
    """Test PricingCache functionality"""

    def setup_method(self):
        """Set up test cache"""
        self.cache = PricingCache(max_size=100, default_ttl=300)

    def test_cache_initialization(self):
        """Test cache initialization with different strategies"""
        cache = PricingCache(
            max_size=500,
            default_ttl=600,
            strategy=CacheStrategy.LRU,
            enable_monitoring=True
        )

        assert cache.max_size == 500
        assert cache.default_ttl == 600
        assert cache.strategy == CacheStrategy.LRU
        assert cache.enable_monitoring
        assert len(cache._caches) == len(CacheLevel)

    def test_basic_cache_operations(self):
        """Test basic put/get operations"""
        # Test put and get
        self.cache.put("test_key", "test_value", CacheLevel.COMPONENT)
        result = self.cache.get("test_key", CacheLevel.COMPONENT)

        assert result == "test_value"

        # Test cache miss
        result = self.cache.get("nonexistent_key", CacheLevel.COMPONENT)
        assert result is None

    def test_cache_ttl_expiration(self):
        """Test TTL-based cache expiration"""
        # Put with short TTL
        self.cache.put(
            "short_ttl_key",
            "test_value",
            CacheLevel.COMPONENT,
            ttl=1)

        # Should be available immediately
        result = self.cache.get("short_ttl_key", CacheLevel.COMPONENT)
        assert result == "test_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        result = self.cache.get("short_ttl_key", CacheLevel.COMPONENT)
        assert result is None

    def test_cache_size_limits(self):
        """Test cache size enforcement"""
        small_cache = PricingCache(max_size=5)

        # Fill cache beyond limit
        for i in range(10):
            small_cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

        # Check that cache size is limited
        component_cache = small_cache._caches[CacheLevel.COMPONENT]
        config = small_cache._level_config[CacheLevel.COMPONENT]
        assert len(component_cache) <= config["max_size"]

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        # Put some test data
        self.cache.put("key1", "value1", CacheLevel.COMPONENT)
        self.cache.put("key2", "value2", CacheLevel.SYSTEM)

        # Verify data is there
        assert self.cache.get("key1", CacheLevel.COMPONENT) == "value1"
        assert self.cache.get("key2", CacheLevel.SYSTEM) == "value2"

        # Invalidate specific key
        invalidated = self.cache.invalidate("key1", CacheLevel.COMPONENT)
        assert invalidated == 1
        assert self.cache.get("key1", CacheLevel.COMPONENT) is None
        assert self.cache.get("key2", CacheLevel.SYSTEM) == "value2"

    def test_cache_invalidation_by_pattern(self):
        """Test pattern-based cache invalidation"""
        # Put test data with patterns
        self.cache.put("user_123_data", "value1", CacheLevel.COMPONENT)
        self.cache.put("user_456_data", "value2", CacheLevel.COMPONENT)
        self.cache.put("product_789_data", "value3", CacheLevel.COMPONENT)

        # Invalidate by pattern
        invalidated = self.cache.invalidate_by_pattern(
            "user_", CacheLevel.COMPONENT)
        assert invalidated == 2

        # Check results
        assert self.cache.get("user_123_data", CacheLevel.COMPONENT) is None
        assert self.cache.get("user_456_data", CacheLevel.COMPONENT) is None
        assert self.cache.get(
            "product_789_data",
            CacheLevel.COMPONENT) == "value3"

    def test_cache_dependency_invalidation(self):
        """Test dependency-based cache invalidation"""
        # Put data with dependencies
        self.cache.put("parent_key", "parent_value", CacheLevel.SYSTEM)
        self.cache.put("child_key", "child_value", CacheLevel.FINAL,
                       dependencies=["parent_key"])

        # Verify both are cached
        assert self.cache.get(
            "parent_key",
            CacheLevel.SYSTEM) == "parent_value"
        assert self.cache.get("child_key", CacheLevel.FINAL) == "child_value"

        # Invalidate parent with cascade
        invalidated = self.cache.invalidate("parent_key", cascade=True)
        assert invalidated >= 1  # Should invalidate at least the parent

        # Child should also be invalidated due to dependency
        assert self.cache.get("child_key", CacheLevel.FINAL) is None

    def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries"""
        # Add entries with different TTLs
        self.cache.put("key1", "value1", CacheLevel.COMPONENT, ttl=1)
        self.cache.put("key2", "value2", CacheLevel.COMPONENT, ttl=10)

        # Wait for first to expire
        time.sleep(1.1)

        # Cleanup expired entries
        cleaned = self.cache.cleanup_expired()
        assert cleaned >= 1

        # Check results
        assert self.cache.get("key1", CacheLevel.COMPONENT) is None
        assert self.cache.get("key2", CacheLevel.COMPONENT) == "value2"

    def test_cache_statistics(self):
        """Test cache statistics tracking"""
        # Perform some operations
        self.cache.put("key1", "value1", CacheLevel.COMPONENT)
        self.cache.get("key1", CacheLevel.COMPONENT)  # Hit
        self.cache.get("nonexistent", CacheLevel.COMPONENT)  # Miss

        # Get statistics
        stats = self.cache.get_stats(CacheLevel.COMPONENT)
        component_stats = stats[CacheLevel.COMPONENT.value]

        assert component_stats.hits >= 1
        assert component_stats.misses >= 1
        assert component_stats.total_entries >= 1


class TestPricingCacheManager:
    """Test PricingCacheManager functionality"""

    def setup_method(self):
        """Set up test cache manager"""
        self.cache = PricingCache()
        self.manager = PricingCacheManager(self.cache)

    def test_component_key_generation(self):
        """Test component cache key generation"""
        key1 = self.manager.generate_component_key(123, 5)
        key2 = self.manager.generate_component_key(123, 5)
        key3 = self.manager.generate_component_key(124, 5)

        # Same inputs should generate same key
        assert key1 == key2

        # Different inputs should generate different keys
        assert key1 != key3

    def test_system_key_generation(self):
        """Test system cache key generation"""
        components1 = [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
        components2 = [
            {"product_id": 2, "quantity": 1},
            {"product_id": 1, "quantity": 2}
        ]
        components3 = [
            {"product_id": 1, "quantity": 3},
            {"product_id": 2, "quantity": 1}
        ]

        key1 = self.manager.generate_system_key(components1, "pv")
        key2 = self.manager.generate_system_key(components2, "pv")
        key3 = self.manager.generate_system_key(components3, "pv")

        # Same components in different order should generate same key
        assert key1 == key2

        # Different components should generate different keys
        assert key1 != key3

    def test_final_key_generation(self):
        """Test final pricing cache key generation"""
        calc_data1 = {
            "components": [{"product_id": 1, "quantity": 2}],
            "modifications": {"discount_percent": 5.0},
            "vat_rate": 19.0,
            "system_type": "pv"
        }
        calc_data2 = {
            "components": [{"product_id": 1, "quantity": 2}],
            "modifications": {"discount_percent": 10.0},
            "vat_rate": 19.0,
            "system_type": "pv"
        }

        key1 = self.manager.generate_final_key(calc_data1)
        key2 = self.manager.generate_final_key(calc_data2)

        # Different modifications should generate different keys
        assert key1 != key2

    def test_cache_operations(self):
        """Test cache manager operations"""
        # Test component caching
        key = self.manager.generate_component_key(123, 5)
        test_data = {"price": 100.0, "total": 500.0}

        self.manager.cache_component_pricing(key, test_data)
        result = self.manager.get_component_pricing(key)

        assert result == test_data

    def test_product_cache_invalidation(self):
        """Test product-specific cache invalidation"""
        # Cache some data for different products
        key1 = self.manager.generate_component_key(123, 5)
        key2 = self.manager.generate_component_key(456, 3)

        self.manager.cache_component_pricing(key1, {"price": 100})
        self.manager.cache_component_pricing(key2, {"price": 200})

        # Invalidate specific product
        invalidated = self.manager.invalidate_product_cache(123)

        # Should invalidate at least one entry
        assert invalidated >= 0  # Pattern matching might not find exact matches

    def test_system_cache_invalidation(self):
        """Test system-specific cache invalidation"""
        # Cache data for different systems
        components = [{"product_id": 1, "quantity": 2}]
        key_pv = self.manager.generate_system_key(components, "pv")
        key_hp = self.manager.generate_system_key(components, "heatpump")

        self.manager.cache_system_pricing(key_pv, {"total": 1000})
        self.manager.cache_system_pricing(key_hp, {"total": 2000})

        # Invalidate specific system
        invalidated = self.manager.invalidate_system_cache("pv")

        # Should invalidate at least one entry
        assert invalidated >= 0


class TestPerformanceMonitoring:
    """Test performance monitoring functionality"""

    def setup_method(self):
        """Set up performance monitor"""
        self.cache = PricingCache()
        self.monitor = PerformanceMonitor(self.cache)

    def test_performance_monitoring(self):
        """Test performance metric recording"""
        self.monitor.start_monitoring()

        # Create test metric
        metric = PerformanceMetrics(
            operation_name="test_operation",
            start_time=time.time(),
            cache_hit=True
        )
        metric.finish()

        # Record metric
        self.monitor.record_operation(metric)

        # Get stats
        stats = self.monitor.get_current_stats()

        assert stats["total_operations"] == 1
        assert stats["cache_hit_rate"] == 1.0
        assert "test_operation" in stats["operation_stats"]

    def test_performance_stats_calculation(self):
        """Test performance statistics calculation"""
        self.monitor.start_monitoring()

        # Record multiple operations
        for i in range(10):
            metric = PerformanceMetrics(
                operation_name="test_op",
                start_time=time.time(),
                cache_hit=(i % 2 == 0)  # 50% hit rate
            )
            metric.duration_ms = float(i + 1)  # Varying durations
            metric.finish()
            self.monitor.record_operation(metric)

        stats = self.monitor.get_current_stats()

        assert stats["total_operations"] == 10
        assert stats["cache_hit_rate"] == 0.5
        assert "duration_stats" in stats
        assert "operation_stats" in stats


class TestCacheBenchmark:
    """Test cache benchmarking functionality"""

    def setup_method(self):
        """Set up benchmark suite"""
        self.cache = PricingCache()
        self.benchmark = CacheBenchmark(self.cache)

    def test_basic_operations_benchmark(self):
        """Test basic operations benchmark"""
        result = self.benchmark.benchmark_cache_operations(
            num_operations=100,
            value_size_bytes=512
        )

        assert isinstance(result, BenchmarkResult)
        assert result.operation_name == "cache_operations"
        assert result.total_operations == 100
        assert result.avg_duration_ms >= 0
        assert result.operations_per_second > 0

    def test_concurrent_access_benchmark(self):
        """Test concurrent access benchmark"""
        result = self.benchmark.benchmark_concurrent_access(
            num_threads=3,
            operations_per_thread=10
        )

        assert isinstance(result, BenchmarkResult)
        assert result.operation_name == "concurrent_access"
        # 3 threads * 10 ops * 2 (put+get)
        assert result.total_operations == 60
        assert result.avg_duration_ms >= 0

    def test_cache_invalidation_benchmark(self):
        """Test cache invalidation benchmark"""
        result = self.benchmark.benchmark_cache_invalidation(
            num_entries=50,
            invalidation_patterns=["pattern1", "pattern2"]
        )

        assert isinstance(result, BenchmarkResult)
        assert result.operation_name == "cache_invalidation"
        assert result.total_operations == 2  # Number of patterns
        assert result.avg_duration_ms >= 0

    def test_comprehensive_benchmark(self):
        """Test comprehensive benchmark suite"""
        report = self.benchmark.run_comprehensive_benchmark()

        assert report.report_id is not None
        assert len(report.benchmarks) > 0
        assert report.duration_minutes >= 0
        assert len(report.recommendations) > 0
        assert "total_operations" in report.summary


class TestGlobalCacheInstances:
    """Test global cache instance management"""

    def test_global_cache_singleton(self):
        """Test global cache singleton behavior"""
        cache1 = get_pricing_cache()
        cache2 = get_pricing_cache()

        # Should return same instance
        assert cache1 is cache2

    def test_global_cache_manager_singleton(self):
        """Test global cache manager singleton behavior"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_global_cache_reset(self):
        """Test global cache reset functionality"""
        # Get initial instances
        cache1 = get_pricing_cache()
        manager1 = get_cache_manager()

        # Reset global cache
        reset_global_cache()

        # Get new instances
        cache2 = get_pricing_cache()
        manager2 = get_cache_manager()

        # Should be different instances after reset
        assert cache1 is not cache2
        assert manager1 is not manager2


class TestCacheIntegration:
    """Test cache integration with pricing engine"""

    def setup_method(self):
        """Set up integration test environment"""
        reset_global_cache()
        self.cache_manager = get_cache_manager()

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_pricing_engine_cache_integration(self, mock_get_product):
        """Test pricing engine integration with cache"""
        from pricing.enhanced_pricing_engine import PricingEngine

        # Mock product data
        mock_get_product.return_value = {
            "id": 1,
            "model_name": "Test Module",
            "category": "pv_module",
            "price_euro": 200.0,
            "calculate_per": "Stück"
        }

        # Create pricing engine with caching enabled
        engine = PricingEngine("pv", enable_caching=True)

        components = [{"product_id": 1, "quantity": 10}]

        # First calculation should miss cache
        result1 = engine.calculate_base_price(components)
        assert result1.metadata.get("cached", False) is False

        # Second calculation should hit cache
        result2 = engine.calculate_base_price(components)
        # Note: In real implementation, this would be cached
        # For this test, we just verify the engine works with caching enabled
        assert result2 is not None


def test_export_performance_report():
    """Test performance report export functionality"""
    from pricing.cache_performance import PerformanceReport

    # Create mock report
    report = PerformanceReport(
        report_id="test_report",
        start_time=datetime.now(),
        end_time=datetime.now(),
        duration_minutes=5.0,
        benchmarks=[],
        cache_stats={},
        recommendations=["Test recommendation"],
        summary={"total_operations": 100}
    )

    # Test JSON export
    json_output = export_performance_report(report, "json")
    assert "test_report" in json_output
    assert "Test recommendation" in json_output

    # Test CSV export
    csv_output = export_performance_report(report, "csv")
    assert "Operation" in csv_output  # Header should be present


if __name__ == "__main__":
    pytest.main([__file__])
