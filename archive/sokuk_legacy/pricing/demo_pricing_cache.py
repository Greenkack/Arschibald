"""Demo script for pricing cache system

This script demonstrates the intelligent pricing cache system with
performance monitoring and benchmarking capabilities.
"""

import time

from cache_performance import (
    CacheBenchmark,
    PerformanceMonitor,
    export_performance_report,
)
from pricing_cache import CacheLevel, PricingCache, get_cache_manager


def demo_basic_caching():
    """Demonstrate basic caching operations"""
    print("=== Basic Caching Demo ===")

    cache = PricingCache(max_size=1000, enable_monitoring=True)

    # Put some data
    print("Storing pricing data in cache...")
    cache.put("pv_module_123",
              {"price": 200.0,
               "quantity": 10,
               "total": 2000.0},
              CacheLevel.COMPONENT)
    cache.put("inverter_456",
              {"price": 800.0,
               "quantity": 1,
               "total": 800.0},
              CacheLevel.COMPONENT)
    cache.put("system_pv_001",
              {"base_price": 2800.0,
               "final_price": 2660.0},
              CacheLevel.SYSTEM)

    # Retrieve data
    print("Retrieving cached data...")
    pv_module = cache.get("pv_module_123", CacheLevel.COMPONENT)
    inverter = cache.get("inverter_456", CacheLevel.COMPONENT)
    system = cache.get("system_pv_001", CacheLevel.SYSTEM)

    print(f"PV Module: {pv_module}")
    print(f"Inverter: {inverter}")
    print(f"System: {system}")

    # Test cache miss
    missing = cache.get("nonexistent_key", CacheLevel.COMPONENT)
    print(f"Missing key result: {missing}")

    # Get cache statistics
    stats = cache.get_stats()
    print("\nCache Statistics:")
    for level, stat in stats.items():
        print(
            f"  {level}: {
                stat.hits} hits, {
                stat.misses} misses, {
                stat.hit_rate:.1%} hit rate")


def demo_cache_manager():
    """Demonstrate cache manager functionality"""
    print("\n=== Cache Manager Demo ===")

    manager = get_cache_manager()

    # Generate cache keys
    component_key = manager.generate_component_key(123, 5)
    system_key = manager.generate_system_key([
        {"product_id": 123, "quantity": 5},
        {"product_id": 456, "quantity": 2}
    ], "pv")

    print(f"Component cache key: {component_key[:16]}...")
    print(f"System cache key: {system_key[:16]}...")

    # Cache some pricing data
    component_data = {
        "product_id": 123,
        "unit_price": 200.0,
        "quantity": 5,
        "total_price": 1000.0
    }

    system_data = {
        "base_price": 1500.0,
        "components": ["pv_module", "inverter"],
        "total_components": 2
    }

    manager.cache_component_pricing(component_key, component_data)
    manager.cache_system_pricing(system_key, system_data, [component_key])

    # Retrieve cached data
    cached_component = manager.get_component_pricing(component_key)
    cached_system = manager.get_system_pricing(system_key)

    print(f"Cached component: {cached_component}")
    print(f"Cached system: {cached_system}")

    # Test invalidation
    print("\nTesting cache invalidation...")
    invalidated = manager.invalidate_product_cache(123)
    print(f"Invalidated {invalidated} entries for product 123")


def demo_performance_monitoring():
    """Demonstrate performance monitoring"""
    print("\n=== Performance Monitoring Demo ===")

    cache = PricingCache(max_size=5000, enable_monitoring=True)
    monitor = PerformanceMonitor(cache, window_size=100)

    monitor.start_monitoring()

    print("Performing monitored cache operations...")

    # Simulate pricing calculations with monitoring
    from cache_performance import PerformanceMetrics

    for i in range(50):
        # Simulate component pricing calculation
        start_time = time.time()

        # Mock calculation work
        time.sleep(0.001)  # Simulate 1ms calculation

        # Cache the result
        cache.put(f"component_{i}", {"price": i * 10}, CacheLevel.COMPONENT)

        end_time = time.time()

        # Record performance metric
        metric = PerformanceMetrics(
            operation_name="component_pricing",
            start_time=start_time,
            cache_hit=False
        )
        metric.end_time = end_time
        metric.duration_ms = (end_time - start_time) * 1000
        monitor.record_operation(metric)

        # Simulate cache retrieval
        start_time = time.time()
        result = cache.get(f"component_{i}", CacheLevel.COMPONENT)
        end_time = time.time()

        metric = PerformanceMetrics(
            operation_name="cache_retrieval",
            start_time=start_time,
            cache_hit=(result is not None)
        )
        metric.end_time = end_time
        metric.duration_ms = (end_time - start_time) * 1000
        monitor.record_operation(metric)

    # Get monitoring results
    stats = monitor.get_current_stats()
    print("Monitoring Results:")
    print(f"  Total operations: {stats['total_operations']}")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
    print(
        f"  Average duration: {
            stats['duration_stats'].get(
                'avg_duration_ms',
                0):.2f}ms")

    for op_name, op_stats in stats['operation_stats'].items():
        print(
            f"  {op_name}: {
                op_stats['count']} ops, {
                op_stats['avg_duration_ms']:.2f}ms avg")


def demo_benchmarking():
    """Demonstrate benchmarking capabilities"""
    print("\n=== Benchmarking Demo ===")

    cache = PricingCache(max_size=10000, enable_monitoring=True)
    benchmark = CacheBenchmark(cache)

    print("Running cache operations benchmark...")
    result = benchmark.benchmark_cache_operations(
        num_operations=500,
        value_size_bytes=1024
    )

    print("Benchmark Results:")
    print(f"  Operation: {result.operation_name}")
    print(f"  Total operations: {result.total_operations}")
    print(f"  Average duration: {result.avg_duration_ms:.2f}ms")
    print(f"  Operations per second: {result.operations_per_second:.0f}")
    print(f"  Cache hit rate: {result.cache_hit_rate:.1%}")
    print(f"  Memory usage: {result.memory_usage_mb:.2f}MB")

    print("\nRunning concurrent access benchmark...")
    concurrent_result = benchmark.benchmark_concurrent_access(
        num_threads=4,
        operations_per_thread=50
    )

    print("Concurrent Benchmark Results:")
    print(f"  Total operations: {concurrent_result.total_operations}")
    print(f"  Average duration: {concurrent_result.avg_duration_ms:.2f}ms")
    print(
        f"  Operations per second: {
            concurrent_result.operations_per_second:.0f}")


def demo_comprehensive_benchmark():
    """Demonstrate comprehensive benchmark suite"""
    print("\n=== Comprehensive Benchmark Demo ===")

    cache = PricingCache(max_size=5000, enable_monitoring=True)
    benchmark = CacheBenchmark(cache)

    print("Running comprehensive benchmark suite...")
    print("This may take a few seconds...")

    report = benchmark.run_comprehensive_benchmark()

    print(f"\nBenchmark Report: {report.report_id}")
    print(f"Duration: {report.duration_minutes:.2f} minutes")
    print(f"Total benchmarks: {len(report.benchmarks)}")

    print("\nBenchmark Summary:")
    for key, value in report.summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\nRecommendations:")
    for i, recommendation in enumerate(report.recommendations, 1):
        print(f"  {i}. {recommendation}")

    # Export report
    json_report = export_performance_report(report, "json")
    print("\nJSON Report (first 200 chars):")
    print(json_report[:200] + "...")


def demo_cache_invalidation():
    """Demonstrate cache invalidation strategies"""
    print("\n=== Cache Invalidation Demo ===")

    cache = PricingCache(max_size=1000)

    # Populate cache with test data
    print("Populating cache with test data...")
    for i in range(20):
        cache.put(
            f"product_{i}_pricing", {
                "price": i * 100}, CacheLevel.COMPONENT)
        cache.put(f"system_{i}_total", {"total": i * 1000}, CacheLevel.SYSTEM)

    print(
        f"Cache populated. Component entries: {len(cache._caches[CacheLevel.COMPONENT])}")
    print(f"System entries: {len(cache._caches[CacheLevel.SYSTEM])}")

    # Test pattern-based invalidation
    print("\nTesting pattern-based invalidation...")
    invalidated = cache.invalidate_by_pattern("product_1")
    print(f"Invalidated {invalidated} entries matching 'product_1'")

    # Test specific key invalidation
    print("\nTesting specific key invalidation...")
    invalidated = cache.invalidate("system_5_total", CacheLevel.SYSTEM)
    print(f"Invalidated {invalidated} entries for 'system_5_total'")

    # Test TTL expiration
    print("\nTesting TTL expiration...")
    cache.put("short_lived", {"data": "expires soon"},
              CacheLevel.COMPONENT, ttl=1)

    # Check immediately
    result = cache.get("short_lived", CacheLevel.COMPONENT)
    print(f"Immediate retrieval: {result}")

    # Wait and check again
    time.sleep(1.1)
    result = cache.get("short_lived", CacheLevel.COMPONENT)
    print(f"After TTL expiration: {result}")

    # Cleanup expired entries
    cleaned = cache.cleanup_expired()
    print(f"Cleaned up {cleaned} expired entries")


def main():
    """Run all demos"""
    print("Pricing Cache System Demo")
    print("=" * 50)

    try:
        demo_basic_caching()
        demo_cache_manager()
        demo_performance_monitoring()
        demo_benchmarking()
        demo_comprehensive_benchmark()
        demo_cache_invalidation()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
