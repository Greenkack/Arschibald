"""Verification script for Cache Warming System"""

from core.cache_warming import (
    CacheWarmingEngine,
    UsagePatternTracker,
    WarmingTask,
    get_warming_performance,
    get_warming_stats,
    register_critical_task,
    warm_cache,
    warm_critical_data,
)
from core.cache import CacheKeys, get_cache
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def verify_warming_task():
    """Verify WarmingTask functionality"""
    print("\n1. Testing WarmingTask...")

    def compute_fn():
        return "test_value"

    task = WarmingTask(
        task_id="test_task",
        name="Test Task",
        cache_key="test_key",
        compute_fn=compute_fn,
        priority=50,
        tags={"test"}
    )

    assert task.task_id == "test_task"
    assert task.should_run()
    assert task.priority == 50

    task.update_schedule(60)
    assert task.next_run is not None

    print("   ✓ WarmingTask works correctly")


def verify_usage_tracker():
    """Verify UsagePatternTracker functionality"""
    print("\n2. Testing UsagePatternTracker...")

    tracker = UsagePatternTracker(history_size=100)

    # Record some accesses
    for i in range(10):
        tracker.record_access("key1")
        tracker.record_access("key2")
        if i % 2 == 0:
            tracker.record_access("key3")

    # Get hot keys
    hot_keys = tracker.get_hot_keys(top_n=3)
    assert len(hot_keys) == 3
    assert hot_keys[0][0] in ["key1", "key2"]  # Most accessed

    # Get frequency
    frequency = tracker.get_access_frequency("key1", window_minutes=60)
    assert frequency >= 0

    print("   ✓ UsagePatternTracker works correctly")


def verify_basic_warming():
    """Verify basic cache warming"""
    print("\n3. Testing basic cache warming...")

    call_count = 0

    def expensive_compute():
        nonlocal call_count
        call_count += 1
        time.sleep(0.01)
        return {"result": "computed", "count": call_count}

    # Warm the cache
    success = warm_cache(
        key="expensive_key",
        compute_fn=expensive_compute,
        ttl=60,
        tags={"expensive"}
    )

    assert success
    assert call_count == 1

    # Verify it's cached
    cache = get_cache()
    value = cache.get("expensive_key")
    assert value is not None
    assert value["result"] == "computed"

    print("   ✓ Basic cache warming works correctly")


def verify_task_registration():
    """Verify task registration"""
    print("\n4. Testing task registration...")

    engine = CacheWarmingEngine()

    def compute1():
        return "value1"

    def compute2():
        return "value2"

    task1 = WarmingTask(
        task_id="task1",
        name="Task 1",
        cache_key="key1",
        compute_fn=compute1,
        priority=50
    )

    task2 = WarmingTask(
        task_id="task2",
        name="Task 2",
        cache_key="key2",
        compute_fn=compute2,
        priority=100
    )

    # Register tasks
    engine.register_task(task1)
    engine.register_task(task2, is_critical=True)

    stats = engine.get_stats()
    assert stats["tasks"] == 2
    assert stats["critical_keys"] == 1
    assert "key2" in engine._critical_data_keys

    print("   ✓ Task registration works correctly")


def verify_critical_data_warming():
    """Verify critical data warming"""
    print("\n5. Testing critical data warming...")

    engine = CacheWarmingEngine()

    def compute_critical():
        return "critical_value"

    task = WarmingTask(
        task_id="critical_task",
        name="Critical Task",
        cache_key="critical_key",
        compute_fn=compute_critical,
        priority=100
    )

    engine.register_task(task, is_critical=True)

    # Warm critical data
    results = engine.warm_critical_data()

    assert results["total"] >= 1
    assert results["succeeded"] >= 1
    assert "total_duration_ms" in results

    print("   ✓ Critical data warming works correctly")


def verify_user_data_warming():
    """Verify user-specific data warming"""
    print("\n6. Testing user data warming...")

    engine = CacheWarmingEngine()
    user_id = "test_user_123"

    # First warming
    results1 = engine.warm_user_data(user_id, force=False, preload_forms=True)

    assert results1["user_id"] == user_id
    assert "succeeded" in results1
    assert "duration_ms" in results1

    # Second warming (should be skipped)
    results2 = engine.warm_user_data(user_id, force=False, preload_forms=True)

    assert results2.get("skipped")
    assert results2.get("reason") == "recently_warmed"

    # Force warming
    results3 = engine.warm_user_data(user_id, force=True, preload_forms=True)

    assert results3.get("skipped") != True
    assert results3["succeeded"] >= 0

    print("   ✓ User data warming works correctly")


def verify_performance_tracking():
    """Verify performance tracking"""
    print("\n7. Testing performance tracking...")

    engine = CacheWarmingEngine()

    def compute_fn():
        time.sleep(0.01)
        return "value"

    # Warm multiple times
    for i in range(5):
        engine.warm_key(f"key_{i}", compute_fn, ttl=60)

    perf = engine.get_performance_stats()

    assert perf["total_warmings"] == 5
    assert perf["avg_duration_ms"] > 0
    assert perf["fastest_ms"] > 0
    assert perf["slowest_ms"] >= perf["fastest_ms"]
    assert "efficiency_score" in perf

    print("   ✓ Performance tracking works correctly")


def verify_pattern_based_warming():
    """Verify usage pattern-based warming"""
    print("\n8. Testing pattern-based warming...")

    engine = CacheWarmingEngine()

    # Register tasks
    def compute1():
        return "value1"

    task = WarmingTask(
        task_id="pattern_task",
        name="Pattern Task",
        cache_key="pattern_key",
        compute_fn=compute1,
        priority=50
    )

    engine.register_task(task)

    # Simulate usage
    for i in range(10):
        engine._usage_tracker.record_access("pattern_key")

    # Warm by patterns
    results = engine.warm_by_usage_patterns(top_n=5, min_access_frequency=0.0)

    assert "total" in results
    assert "succeeded" in results
    assert "duration_ms" in results

    print("   ✓ Pattern-based warming works correctly")


def verify_schedule_optimization():
    """Verify schedule optimization"""
    print("\n9. Testing schedule optimization...")

    engine = CacheWarmingEngine()

    def compute_fn():
        return "value"

    # Register task
    task = WarmingTask(
        task_id="opt_task",
        name="Optimization Task",
        cache_key="opt_key",
        compute_fn=compute_fn,
        priority=50
    )

    engine.register_task(task)

    # Simulate high frequency access
    for i in range(100):
        engine._usage_tracker.record_access("opt_key")

    # Optimize schedules
    results = engine.optimize_schedules()

    assert results["tasks_optimized"] >= 1
    assert len(results["schedules_adjusted"]) >= 1

    adjustment = results["schedules_adjusted"][0]
    assert "task_id" in adjustment
    assert "frequency" in adjustment
    assert "interval_minutes" in adjustment

    print("   ✓ Schedule optimization works correctly")


def verify_background_warming():
    """Verify background warming"""
    print("\n10. Testing background warming...")

    engine = CacheWarmingEngine()

    def compute_fn():
        return "background_value"

    task = WarmingTask(
        task_id="bg_task",
        name="Background Task",
        cache_key="bg_key",
        compute_fn=compute_fn,
        priority=100
    )

    engine.register_task(task, is_critical=True)

    # Start background warming
    engine.start_background_warming(
        interval_minutes=1,
        enable_pattern_warming=True,
        enable_critical_warming=True
    )

    stats = engine.get_stats()
    assert stats["running"]

    # Let it run briefly
    time.sleep(0.5)

    # Stop background warming
    engine.stop_background_warming()

    stats = engine.get_stats()
    assert stats["running"] == False

    print("   ✓ Background warming works correctly")


def verify_global_functions():
    """Verify global convenience functions"""
    print("\n11. Testing global functions...")

    # Register a task
    def compute_fn():
        return "global_value"

    task = WarmingTask(
        task_id="global_task",
        name="Global Task",
        cache_key="global_key",
        compute_fn=compute_fn,
        priority=75
    )

    register_critical_task(task)

    # Warm critical data
    results = warm_critical_data()
    assert "total" in results

    # Get stats
    stats = get_warming_stats()
    assert "tasks" in stats
    assert "performance" in stats

    # Get performance
    perf = get_warming_performance()
    assert "total_warmings" in perf

    print("   ✓ Global functions work correctly")


def verify_integration():
    """Verify integration with cache system"""
    print("\n12. Testing cache integration...")

    def expensive_operation():
        time.sleep(0.02)
        return {"data": "expensive", "timestamp": time.time()}

    key = CacheKeys.computed("expensive_op", arg1=1, arg2=2)

    # Warm the cache
    success = warm_cache(key, expensive_operation, ttl=60, tags={"expensive"})
    assert success

    # Verify it's in cache
    cache = get_cache()
    value = cache.get(key)
    assert value is not None
    assert value["data"] == "expensive"

    # Warm again (should use cache)
    start_time = time.time()
    success2 = warm_cache(key, expensive_operation, ttl=60, force=False)
    duration = time.time() - start_time

    # Should be fast (from cache)
    assert duration < 0.01

    print("   ✓ Cache integration works correctly")


def run_all_verifications():
    """Run all verification tests"""
    print("=" * 60)
    print("Cache Warming System - Verification")
    print("=" * 60)

    try:
        verify_warming_task()
        verify_usage_tracker()
        verify_basic_warming()
        verify_task_registration()
        verify_critical_data_warming()
        verify_user_data_warming()
        verify_performance_tracking()
        verify_pattern_based_warming()
        verify_schedule_optimization()
        verify_background_warming()
        verify_global_functions()
        verify_integration()

        print("\n" + "=" * 60)
        print("✓ All verifications passed!")
        print("=" * 60)

        return True

    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_verifications()
    exit(0 if success else 1)
