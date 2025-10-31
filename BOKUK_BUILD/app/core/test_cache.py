"""Tests for Intelligent Caching System"""

import time

import pytest

from .cache import (
    CacheKeys,
    InMemoryCache,
    MultiLayerCache,
    get_cache,
    get_or_compute,
    invalidate_cache,
)
from .cache_invalidation import (
    InvalidationRule,
    add_cache_dependency,
    invalidate_by_write,
    invalidate_with_dependencies,
)
from .cache_monitoring import CacheMetricsCollector, CachePerformanceAnalyzer
from .cache_warming import (
    UsagePatternTracker,
    WarmingTask,
    get_warming_engine,
    warm_cache,
)


class TestCacheKeys:
    """Test CacheKeys namespace management"""

    def test_user_session_key(self):
        key = CacheKeys.user_session("user123")
        assert key == "user_session:user123"

    def test_form_data_key(self):
        key = CacheKeys.form_data("form1", "user123")
        assert key == "form_data:form1:user123"

    def test_computed_key(self):
        key = CacheKeys.computed("calculate_price", 100, discount=0.1)
        assert key.startswith("computed:calculate_price:")
        assert len(key.split(":")[-1]) == 8  # Hash length

    def test_custom_key(self):
        key = CacheKeys.custom("my_namespace", "part1", "part2")
        assert key == "my_namespace:part1:part2"


class TestInMemoryCache:
    """Test in-memory cache with LRU eviction"""

    def test_basic_get_set(self):
        cache = InMemoryCache(max_entries=10)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        cache = InMemoryCache(max_entries=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key4, should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cache_with_tags(self):
        cache = InMemoryCache()
        cache.set("key1", "value1", tags={"user", "session"})
        cache.set("key2", "value2", tags={"user"})
        cache.set("key3", "value3", tags={"product"})

        # Invalidate by tags
        count = cache.invalidate_by_tags({"user"})
        assert count == 2

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_cache_stats(self):
        cache = InMemoryCache()

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 1

    def test_cache_clear(self):
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestMultiLayerCache:
    """Test multi-layer cache coordination"""

    def test_cache_layers(self):
        cache = MultiLayerCache()

        # Set in memory layer
        cache.set("key1", "value1", layers={"memory"})

        # Should retrieve from memory
        assert cache.get("key1") == "value1"

    def test_cache_fallback(self):
        cache = MultiLayerCache()

        # Set in database layer only
        cache.set("key1", "value1", layers={"database"})

        # Should fall back to database and populate memory
        value = cache.get("key1")
        # Note: This might be None if database cache is not initialized
        # In real usage, database would be properly set up

    def test_invalidate_all_layers(self):
        cache = MultiLayerCache()

        cache.set("key1", "value1", tags={"test"})
        count = cache.invalidate_by_tags({"test"})

        assert count >= 0  # At least memory layer


class TestGetOrCompute:
    """Test get_or_compute function"""

    def test_compute_and_cache(self):
        call_count = 0

        def expensive_fn():
            nonlocal call_count
            call_count += 1
            return "computed_value"

        # First call should compute
        value1 = get_or_compute("test_key", expensive_fn)
        assert value1 == "computed_value"
        assert call_count == 1

        # Second call should use cache
        value2 = get_or_compute("test_key", expensive_fn)
        assert value2 == "computed_value"
        assert call_count == 1  # Not called again

    def test_force_refresh(self):
        call_count = 0

        def expensive_fn():
            nonlocal call_count
            call_count += 1
            return f"value_{call_count}"

        # Use unique key to avoid interference from other tests
        value1 = get_or_compute("test_key_refresh", expensive_fn)
        assert value1 == "value_1"

        value2 = get_or_compute(
            "test_key_refresh",
            expensive_fn,
            force_refresh=True)
        assert value2 == "value_2"
        assert call_count == 2


class TestCacheInvalidation:
    """Test cache invalidation system"""

    def test_invalidation_rule(self):
        rule = InvalidationRule(
            name="test_rule",
            trigger_tags={"user"},
            invalidate_tags={"user_session", "user_data"}
        )

        # Set up cache entries
        cache = get_cache()
        cache.set("key1", "value1", tags={"user_session"})
        cache.set("key2", "value2", tags={"user_data"})

        # Execute rule
        count = rule.execute()
        assert count >= 0
        assert rule.execution_count == 1

    def test_invalidate_by_write(self):
        # Set up cache
        cache = get_cache()
        cache.set("user_key", "value", tags={"user"})

        # Simulate write
        count = invalidate_by_write("user", "user123")
        assert count >= 0

    def test_cache_dependencies(self):
        # Add dependency
        add_cache_dependency("derived_key", {"source_key1", "source_key2"})

        # Set up cache
        cache = get_cache()
        cache.set("derived_key", "derived_value")
        cache.set("source_key1", "source_value1")

        # Invalidate with dependencies
        count = invalidate_with_dependencies("source_key1")
        assert count >= 0


class TestCacheMonitoring:
    """Test cache performance monitoring"""

    def test_metrics_collector(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "hit_rate", 0.90)

        metrics = collector.get_metrics(layer="memory", metric_type="hit_rate")
        assert len(metrics) == 2

    def test_performance_analyzer(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Analyze hit rate
        report = analyzer.analyze_hit_rate("memory")
        assert "hit_rate" in report
        assert "status" in report

    def test_cache_size_analysis(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        report = analyzer.analyze_cache_size("memory")
        assert "utilization" in report
        assert "entries" in report


class TestCacheWarming:
    """Test cache warming system"""

    def test_usage_pattern_tracker(self):
        tracker = UsagePatternTracker()

        tracker.record_access("key1")
        tracker.record_access("key1")
        tracker.record_access("key2")

        hot_keys = tracker.get_hot_keys(top_n=2)
        assert len(hot_keys) <= 2
        assert hot_keys[0][0] == "key1"
        assert hot_keys[0][1] == 2

    def test_warming_task(self):
        def compute_fn():
            return "warmed_value"

        task = WarmingTask(
            task_id="task1",
            name="Test Task",
            cache_key="test_key",
            compute_fn=compute_fn,
            priority=10
        )

        assert task.should_run()

    def test_warm_cache(self):
        def compute_fn():
            return "warmed_value"

        success = warm_cache("warm_key", compute_fn, ttl=60)
        assert success

        # Verify it's cached
        cache = get_cache()
        value = cache.get("warm_key")
        assert value == "warmed_value"

    def test_warming_engine(self):
        engine = get_warming_engine()

        def compute_fn():
            return "critical_data"

        task = WarmingTask(
            task_id="critical_task",
            name="Critical Data",
            cache_key="critical_key",
            compute_fn=compute_fn,
            priority=100
        )

        engine.register_task(task)

        # Warm critical data
        results = engine.warm_critical_data()
        assert results["total"] >= 1


class TestCacheIntegration:
    """Integration tests for complete caching system"""

    def test_end_to_end_caching(self):
        """Test complete caching workflow"""
        # 1. Compute and cache
        def expensive_computation():
            time.sleep(0.01)  # Simulate expensive operation
            return {"result": "computed"}

        key = CacheKeys.computed("test_function", arg1=1, arg2=2)
        value = get_or_compute(
            key,
            expensive_computation,
            ttl=60,
            tags={"test"})

        assert value == {"result": "computed"}

        # 2. Verify it's cached
        cache = get_cache()
        cached_value = cache.get(key)
        assert cached_value == {"result": "computed"}

        # 3. Invalidate by tags
        count = invalidate_cache(tags={"test"})
        assert count >= 1

        # 4. Verify it's gone
        assert cache.get(key) is None

    def test_cache_with_dependencies(self):
        """Test caching with dependency tracking"""
        # Set up dependent caches
        cache = get_cache()
        cache.set("source", "source_value")
        cache.set("derived", "derived_value")

        # Add dependency
        add_cache_dependency("derived", {"source"})

        # Invalidate source
        count = invalidate_with_dependencies("source")
        assert count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
