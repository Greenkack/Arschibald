"""Example usage of the Cache Warming System"""

import time

from core.cache import CacheKeys
from core.cache_warming import (
    WarmingTask,
    get_warming_performance,
    get_warming_stats,
    optimize_warming_schedules,
    register_critical_task,
    register_warming_task,
    start_cache_warming,
    stop_cache_warming,
    warm_cache,
    warm_critical_data,
    warm_user_data_optimized,
)


def example_basic_warming():
    """Example: Basic cache warming"""
    print("\n=== Basic Cache Warming ===")

    # Define a compute function
    def load_expensive_data():
        time.sleep(0.1)  # Simulate expensive operation
        return {"data": "expensive_result", "timestamp": time.time()}

    # Warm a specific cache key
    success = warm_cache(
        key="expensive_data",
        compute_fn=load_expensive_data,
        ttl=3600,
        tags={"expensive", "critical"}
    )

    print(f"Cache warming success: {success}")


def example_register_tasks():
    """Example: Register warming tasks"""
    print("\n=== Register Warming Tasks ===")

    # Define compute functions
    def load_user_preferences():
        return {"theme": "dark", "language": "en"}

    def load_product_catalog():
        return {"products": ["A", "B", "C"]}

    def load_analytics_data():
        return {"views": 1000, "clicks": 50}

    # Register regular task
    task1 = WarmingTask(
        task_id="user_prefs",
        name="User Preferences",
        cache_key=CacheKeys.custom("prefs", "default"),
        compute_fn=load_user_preferences,
        ttl=3600,
        priority=50,
        tags={"user", "preferences"}
    )
    register_warming_task(task1)

    # Register critical task (high priority)
    task2 = WarmingTask(
        task_id="product_catalog",
        name="Product Catalog",
        cache_key=CacheKeys.custom("catalog", "products"),
        compute_fn=load_product_catalog,
        ttl=7200,
        priority=100,
        tags={"catalog", "critical"}
    )
    register_critical_task(task2)

    # Register analytics task
    task3 = WarmingTask(
        task_id="analytics",
        name="Analytics Dashboard",
        cache_key=CacheKeys.custom("analytics", "dashboard"),
        compute_fn=load_analytics_data,
        ttl=1800,
        priority=30,
        tags={"analytics"}
    )
    register_warming_task(task3)

    print("Registered 3 warming tasks (1 critical)")


def example_warm_critical_data():
    """Example: Warm critical data"""
    print("\n=== Warm Critical Data ===")

    # Warm all critical data
    results = warm_critical_data()

    print(f"Total tasks: {results['total']}")
    print(f"Succeeded: {results['succeeded']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Duration: {results.get('total_duration_ms', 0)}ms")

    for task_result in results['tasks']:
        print(
            f"  - {
                task_result['name']}: {
                task_result['success']} ({
                task_result['duration_ms']}ms)")


def example_warm_user_data():
    """Example: Warm user-specific data"""
    print("\n=== Warm User Data ===")

    user_id = "user_123"

    # Warm user data with form preloading
    results = warm_user_data_optimized(
        user_id=user_id,
        force=False,  # Skip if recently warmed
        preload_forms=True  # Also preload recent forms
    )

    if results.get("skipped"):
        print(f"User data warming skipped: {results.get('reason')}")
    else:
        print(f"User: {results['user_id']}")
        print(f"Succeeded: {results['succeeded']}")
        print(f"Failed: {results['failed']}")
        print(f"Duration: {results['duration_ms']}ms")
        print(f"Keys warmed: {len(results['keys_warmed'])}")

        for key_info in results['keys_warmed']:
            print(f"  - {key_info['type']}: {key_info['key']}")


def example_background_warming():
    """Example: Background cache warming"""
    print("\n=== Background Cache Warming ===")

    # Start background warming
    start_cache_warming(
        interval_minutes=60,  # Warm every hour
        enable_pattern_warming=True,  # Enable usage pattern-based warming
        enable_critical_warming=True  # Enable critical data warming
    )

    print("Background warming started (60 minute interval)")

    # Let it run for a bit
    time.sleep(2)

    # Get statistics
    stats = get_warming_stats()
    print("\nWarming Statistics:")
    print(f"  Tasks: {stats['tasks']}")
    print(f"  Critical keys: {stats['critical_keys']}")
    print(f"  Running: {stats['running']}")
    print(f"  Users preloaded: {stats['users_preloaded']}")

    # Get performance stats
    perf = get_warming_performance()
    print("\nPerformance:")
    print(f"  Total warmings: {perf['total_warmings']}")
    print(f"  Avg duration: {perf['avg_duration_ms']:.2f}ms")
    print(f"  Fastest: {perf['fastest_ms']:.2f}ms")
    print(f"  Slowest: {perf['slowest_ms']:.2f}ms")
    print(f"  Efficiency score: {perf['efficiency_score']:.1f}%")

    # Stop background warming
    stop_cache_warming()
    print("\nBackground warming stopped")


def example_optimize_schedules():
    """Example: Optimize warming schedules"""
    print("\n=== Optimize Warming Schedules ===")

    # Optimize schedules based on usage patterns
    results = optimize_warming_schedules()

    print(f"Tasks optimized: {results['tasks_optimized']}")

    for adjustment in results['schedules_adjusted']:
        print(f"  - {adjustment['task_id']}:")
        print(f"    Frequency: {adjustment['frequency']} accesses/min")
        print(f"    New interval: {adjustment['interval_minutes']} minutes")


def example_complete_workflow():
    """Example: Complete warming workflow"""
    print("\n=== Complete Warming Workflow ===")

    # 1. Register tasks
    print("\n1. Registering warming tasks...")
    example_register_tasks()

    # 2. Warm critical data immediately
    print("\n2. Warming critical data...")
    example_warm_critical_data()

    # 3. Warm user-specific data
    print("\n3. Warming user data...")
    example_warm_user_data()

    # 4. Start background warming
    print("\n4. Starting background warming...")
    start_cache_warming(
        interval_minutes=60,
        enable_pattern_warming=True,
        enable_critical_warming=True
    )

    # 5. Monitor performance
    print("\n5. Monitoring performance...")
    time.sleep(1)

    stats = get_warming_stats()
    perf = get_warming_performance()

    print("\nSystem Status:")
    print(f"  Active tasks: {stats['tasks']}")
    print(f"  Critical keys: {stats['critical_keys']}")
    print(
        f"  Background warming: {
            'Active' if stats['running'] else 'Inactive'}")
    print(f"  Total warmings: {perf['total_warmings']}")
    print(f"  Average duration: {perf['avg_duration_ms']:.2f}ms")
    print(f"  Efficiency: {perf['efficiency_score']:.1f}%")

    # 6. Optimize schedules
    print("\n6. Optimizing schedules...")
    optimize_results = optimize_warming_schedules()
    print(f"  Optimized {optimize_results['tasks_optimized']} task schedules")

    # 7. Cleanup
    print("\n7. Stopping background warming...")
    stop_cache_warming()

    print("\n✓ Complete workflow finished")


if __name__ == "__main__":
    print("Cache Warming System - Example Usage")
    print("=" * 50)

    # Run examples
    example_basic_warming()
    example_register_tasks()
    example_warm_critical_data()
    example_warm_user_data()
    example_background_warming()
    example_optimize_schedules()

    # Run complete workflow
    example_complete_workflow()

    print("\n" + "=" * 50)
    print("All examples completed!")
