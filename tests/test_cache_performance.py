"""Performance tests and benchmarks for pricing cache system

This module contains performance-focused tests that measure cache performance
under various conditions and loads.
"""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from pricing.cache_performance import CacheBenchmark, PerformanceMonitor
from pricing.pricing_cache import CacheLevel, CacheStrategy, PricingCache


class TestCachePerformance:
    """Performance tests for pricing cache"""

    def setup_method(self):
        """Set up performance test environment"""
        # Use larger cache size to avoid evictions during performance tests
        self.cache = PricingCache(max_size=50000, enable_monitoring=True)
        self.benchmark = CacheBenchmark(self.cache)

    def test_single_threaded_performance(self):
        """Test single-threaded cache performance"""
        num_operations = 1000
        start_time = time.time()

        # Perform put operations
        for i in range(num_operations):
            self.cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

        put_time = time.time() - start_time

        # Perform get operations
        start_time = time.time()
        hits = 0
        for i in range(num_operations):
            result = self.cache.get(f"key_{i}", CacheLevel.COMPONENT)
            if result is not None:
                hits += 1

        get_time = time.time() - start_time

        # Performance assertions
        assert put_time < 1.0, f"Put operations too slow: {put_time:.3f}s"
        assert get_time < 0.5, f"Get operations too slow: {get_time:.3f}s"
        assert hits == num_operations, f"Cache hit rate too low: {hits}/{num_operations}"

        # Calculate operations per second
        put_ops_per_sec = num_operations / put_time
        get_ops_per_sec = num_operations / get_time

        print(f"Put operations: {put_ops_per_sec:.0f} ops/sec")
        print(f"Get operations: {get_ops_per_sec:.0f} ops/sec")

        # Performance thresholds
        assert put_ops_per_sec > 1000, f"Put performance too low: {
            put_ops_per_sec:.0f} ops/sec"
        assert get_ops_per_sec > 2000, f"Get performance too low: {
            get_ops_per_sec:.0f} ops/sec"

    def test_multi_threaded_performance(self):
        """Test multi-threaded cache performance"""
        num_threads = 10
        operations_per_thread = 100

        def worker_thread(thread_id: int) -> dict[str, float]:
            """Worker thread for concurrent testing"""
            start_time = time.time()

            # Each thread works with its own key space
            for i in range(operations_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"

                # Put operation
                self.cache.put(key, value, CacheLevel.COMPONENT)

                # Get operation
                result = self.cache.get(key, CacheLevel.COMPONENT)
                assert result == value

            end_time = time.time()
            return {
                "thread_id": thread_id,
                "duration": end_time - start_time,
                "operations": operations_per_thread * 2  # put + get
            }

        # Run concurrent threads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i)
                       for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time

        # Analyze results
        total_operations = sum(r["operations"] for r in results)
        avg_thread_duration = statistics.mean([r["duration"] for r in results])
        overall_ops_per_sec = total_operations / total_time

        print(f"Total operations: {total_operations}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Average thread duration: {avg_thread_duration:.3f}s")
        print(f"Overall ops/sec: {overall_ops_per_sec:.0f}")

        # Performance assertions
        assert total_time < 5.0, f"Multi-threaded test too slow: {
            total_time:.3f}s"
        assert overall_ops_per_sec > 500, f"Multi-threaded performance too low: {
            overall_ops_per_sec:.0f} ops/sec"

    def test_cache_size_impact_on_performance(self):
        """Test how cache size affects performance"""
        cache_sizes = [100, 500, 1000, 5000]
        results = {}

        for cache_size in cache_sizes:
            cache = PricingCache(max_size=cache_size)

            # Fill cache to capacity
            start_time = time.time()
            for i in range(cache_size * 2):  # Overfill to test eviction
                cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

            fill_time = time.time() - start_time

            # Test retrieval performance
            start_time = time.time()
            hits = 0
            for i in range(cache_size):
                result = cache.get(
                    f"key_{
                        i + cache_size}",
                    CacheLevel.COMPONENT)  # Recent keys
                if result is not None:
                    hits += 1

            retrieval_time = time.time() - start_time
            hit_rate = hits / cache_size

            results[cache_size] = {
                "fill_time": fill_time,
                "retrieval_time": retrieval_time,
                "hit_rate": hit_rate,
                "fill_ops_per_sec": (cache_size * 2) / fill_time,
                "retrieval_ops_per_sec": cache_size / retrieval_time
            }

            print(f"Cache size {cache_size}: "
                  f"fill={results[cache_size]['fill_ops_per_sec']:.0f} ops/sec, "
                  f"retrieval={results[cache_size]['retrieval_ops_per_sec']:.0f} ops/sec, "
                  f"hit_rate={hit_rate:.2%}")

        # Verify that larger caches don't significantly degrade performance
        small_cache_perf = results[100]["retrieval_ops_per_sec"]
        large_cache_perf = results[5000]["retrieval_ops_per_sec"]

        # Large cache should be at least 50% as fast as small cache
        assert large_cache_perf > small_cache_perf * 0.5, \
            f"Large cache too slow: {large_cache_perf:.0f} vs {small_cache_perf:.0f}"

    def test_ttl_cleanup_performance(self):
        """Test performance of TTL-based cleanup"""
        num_entries = 1000

        # Add entries with short TTL
        start_time = time.time()
        for i in range(num_entries):
            self.cache.put(
                f"key_{i}",
                f"value_{i}",
                CacheLevel.COMPONENT,
                ttl=1)

        add_time = time.time() - start_time

        # Wait for expiration
        time.sleep(1.1)

        # Measure cleanup performance
        start_time = time.time()
        cleaned_count = self.cache.cleanup_expired()
        cleanup_time = time.time() - start_time

        print(f"Added {num_entries} entries in {add_time:.3f}s")
        print(f"Cleaned {cleaned_count} entries in {cleanup_time:.3f}s")

        # Performance assertions
        assert cleanup_time < 0.1, f"Cleanup too slow: {cleanup_time:.3f}s"
        assert cleaned_count >= num_entries * \
            0.8, f"Cleanup incomplete: {cleaned_count}/{num_entries}"

    def test_invalidation_performance(self):
        """Test performance of cache invalidation operations"""
        num_entries = 1000
        patterns = ["pattern_1", "pattern_2", "pattern_3"]

        # Populate cache with patterned keys
        for i in range(num_entries):
            pattern = patterns[i % len(patterns)]
            key = f"{pattern}_key_{i}"
            self.cache.put(key, f"value_{i}", CacheLevel.COMPONENT)

        # Test pattern-based invalidation performance
        start_time = time.time()
        total_invalidated = 0

        for pattern in patterns:
            invalidated = self.cache.invalidate_by_pattern(pattern)
            total_invalidated += invalidated

        invalidation_time = time.time() - start_time

        print(
            f"Invalidated {total_invalidated} entries in {
                invalidation_time:.3f}s")

        # Performance assertions
        assert invalidation_time < 0.5, f"Invalidation too slow: {
            invalidation_time:.3f}s"
        assert total_invalidated > 0, "No entries were invalidated"

    def test_memory_usage_estimation(self):
        """Test memory usage estimation accuracy"""
        # This is a basic test since actual memory measurement is complex
        initial_memory = self.benchmark._estimate_memory_usage()

        # Add significant amount of data
        large_value = "x" * 10240  # 10KB value
        for i in range(100):
            self.cache.put(f"large_key_{i}", large_value, CacheLevel.COMPONENT)

        final_memory = self.benchmark._estimate_memory_usage()

        # Memory usage should increase
        assert final_memory > initial_memory, "Memory usage estimation not working"

        print(
            f"Memory usage: {initial_memory:.2f} MB -> {final_memory:.2f} MB")


class TestBenchmarkSuite:
    """Test the benchmark suite functionality"""

    def setup_method(self):
        """Set up benchmark test environment"""
        self.cache = PricingCache(max_size=5000, enable_monitoring=True)
        self.benchmark = CacheBenchmark(self.cache)

    def test_benchmark_operations_accuracy(self):
        """Test accuracy of benchmark measurements"""
        # Run benchmark with known parameters
        result = self.benchmark.benchmark_cache_operations(
            num_operations=200,
            value_size_bytes=1024
        )

        # Verify benchmark results
        assert result.total_operations == 200
        assert result.avg_duration_ms > 0
        assert result.operations_per_second > 0
        # Should be around 50% (get operations)
        assert result.cache_hit_rate >= 0.4
        assert result.memory_usage_mb >= 0

        # Verify statistical measures make sense
        assert result.min_duration_ms <= result.avg_duration_ms <= result.max_duration_ms
        assert result.median_duration_ms > 0

    def test_concurrent_benchmark_accuracy(self):
        """Test accuracy of concurrent benchmark measurements"""
        result = self.benchmark.benchmark_concurrent_access(
            num_threads=4,
            operations_per_thread=25
        )

        # Verify concurrent benchmark results
        # threads * ops_per_thread * (put + get)
        expected_operations = 4 * 25 * 2
        assert result.total_operations == expected_operations
        assert result.avg_duration_ms > 0
        assert result.operations_per_second > 0

    def test_benchmark_consistency(self):
        """Test consistency of benchmark results across runs"""
        results = []

        # Run same benchmark multiple times
        for _ in range(3):
            result = self.benchmark.benchmark_cache_operations(
                num_operations=100,
                value_size_bytes=512
            )
            results.append(result.operations_per_second)

            # Clear cache between runs for consistency
            self.cache.clear()

        # Calculate coefficient of variation
        mean_ops = statistics.mean(results)
        std_ops = statistics.stdev(results) if len(results) > 1 else 0
        cv = (std_ops / mean_ops) if mean_ops > 0 else 0

        print(f"Operations per second across runs: {results}")
        print(f"Mean: {mean_ops:.0f}, Std: {std_ops:.0f}, CV: {cv:.2%}")

        # Results should be reasonably consistent (CV < 20%)
        assert cv < 0.2, f"Benchmark results too inconsistent: CV={cv:.2%}"

    def test_comprehensive_benchmark_completeness(self):
        """Test that comprehensive benchmark covers all important aspects"""
        report = self.benchmark.run_comprehensive_benchmark()

        # Verify report completeness
        assert report.report_id is not None
        # Should have multiple benchmark types
        assert len(report.benchmarks) >= 3
        assert report.duration_minutes > 0
        assert len(report.recommendations) > 0
        assert "total_operations" in report.summary

        # Verify different benchmark types are included
        benchmark_names = [b.operation_name for b in report.benchmarks]
        assert "cache_operations" in benchmark_names
        assert "concurrent_access" in benchmark_names
        assert "cache_invalidation" in benchmark_names

        # Verify recommendations are meaningful
        assert all(len(rec) > 10 for rec in report.recommendations), \
            "Recommendations should be descriptive"


class TestPerformanceMonitoring:
    """Test performance monitoring functionality"""

    def setup_method(self):
        """Set up performance monitoring test environment"""
        self.cache = PricingCache(enable_monitoring=True)
        self.monitor = PerformanceMonitor(self.cache, window_size=100)

    def test_real_time_monitoring(self):
        """Test real-time performance monitoring"""
        self.monitor.start_monitoring()

        # Simulate cache operations with monitoring
        start_time = time.time()

        for i in range(50):
            # Simulate put operation
            op_start = time.time()
            self.cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)
            op_end = time.time()

            # Record metric
            from pricing.cache_performance import PerformanceMetrics
            metric = PerformanceMetrics(
                operation_name="cache_put",
                start_time=op_start,
                cache_hit=False
            )
            metric.end_time = op_end
            metric.duration_ms = (op_end - op_start) * 1000
            self.monitor.record_operation(metric)

            # Simulate get operation
            op_start = time.time()
            result = self.cache.get(f"key_{i}", CacheLevel.COMPONENT)
            op_end = time.time()

            metric = PerformanceMetrics(
                operation_name="cache_get",
                start_time=op_start,
                cache_hit=(result is not None)
            )
            metric.end_time = op_end
            metric.duration_ms = (op_end - op_start) * 1000
            self.monitor.record_operation(metric)

        # Get monitoring statistics
        stats = self.monitor.get_current_stats()

        # Verify monitoring data
        assert stats["total_operations"] == 100  # 50 puts + 50 gets
        assert stats["cache_hit_rate"] == 0.5  # Only gets can be hits
        assert "cache_put" in stats["operation_stats"]
        assert "cache_get" in stats["operation_stats"]

        # Verify operation-specific stats
        put_stats = stats["operation_stats"]["cache_put"]
        get_stats = stats["operation_stats"]["cache_get"]

        assert put_stats["count"] == 50
        assert get_stats["count"] == 50
        assert put_stats["avg_duration_ms"] > 0
        assert get_stats["avg_duration_ms"] > 0

    def test_monitoring_window_management(self):
        """Test monitoring window size management"""
        small_monitor = PerformanceMonitor(self.cache, window_size=10)
        small_monitor.start_monitoring()

        # Add more metrics than window size
        from pricing.cache_performance import PerformanceMetrics

        for i in range(20):
            metric = PerformanceMetrics(
                operation_name="test_op",
                start_time=time.time(),
                cache_hit=(i % 2 == 0)
            )
            metric.finish()
            small_monitor.record_operation(metric)

        stats = small_monitor.get_current_stats()

        # Should only keep last 10 operations
        assert stats["total_operations"] == 10
        assert stats["window_size"] == 10


class TestCacheStrategies:
    """Test different cache strategies performance"""

    def test_lru_strategy_performance(self):
        """Test LRU strategy performance"""
        lru_cache = PricingCache(
            max_size=100,
            strategy=CacheStrategy.LRU,
            enable_monitoring=True
        )

        # Fill cache beyond capacity with LRU pattern
        for i in range(150):
            lru_cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

        # Access some older entries to test LRU behavior
        for i in range(50, 100):
            result = lru_cache.get(f"key_{i}", CacheLevel.COMPONENT)
            # Some should still be available due to LRU

        stats = lru_cache.get_stats(CacheLevel.COMPONENT)
        component_stats = stats[CacheLevel.COMPONENT.value]

        # Should have reasonable hit rate with LRU
        assert component_stats.hits > 0
        assert component_stats.total_entries <= 100  # Respects max size

    def test_ttl_strategy_performance(self):
        """Test TTL strategy performance"""
        ttl_cache = PricingCache(
            max_size=1000,
            default_ttl=2,  # 2 second TTL
            strategy=CacheStrategy.TTL,
            enable_monitoring=True
        )

        # Add entries with TTL
        start_time = time.time()
        for i in range(100):
            ttl_cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

        add_time = time.time() - start_time

        # Immediate access should work
        hits_immediate = 0
        for i in range(100):
            if ttl_cache.get(f"key_{i}", CacheLevel.COMPONENT) is not None:
                hits_immediate += 1

        # Wait for TTL expiration
        time.sleep(2.1)

        # Access after TTL should mostly miss
        hits_after_ttl = 0
        for i in range(100):
            if ttl_cache.get(f"key_{i}", CacheLevel.COMPONENT) is not None:
                hits_after_ttl += 1

        print(f"Immediate hits: {hits_immediate}/100")
        print(f"Hits after TTL: {hits_after_ttl}/100")

        # Verify TTL behavior
        assert hits_immediate >= 95  # Should be nearly 100%
        assert hits_after_ttl <= 10   # Should be nearly 0%
        assert add_time < 0.5  # Should be fast to add


@pytest.mark.performance
class TestPerformanceRegression:
    """Performance regression tests to catch performance degradation"""

    def test_baseline_performance_metrics(self):
        """Test baseline performance metrics for regression detection"""
        cache = PricingCache(max_size=1000, enable_monitoring=True)

        # Baseline test: 1000 operations should complete in reasonable time
        num_ops = 1000

        start_time = time.time()

        # Mixed workload
        for i in range(num_ops // 2):
            cache.put(f"key_{i}", f"value_{i}", CacheLevel.COMPONENT)

        for i in range(num_ops // 2):
            cache.get(f"key_{i}", CacheLevel.COMPONENT)

        total_time = time.time() - start_time
        ops_per_second = num_ops / total_time

        print(f"Baseline performance: {ops_per_second:.0f} ops/sec")

        # Performance regression thresholds
        # These should be adjusted based on expected performance
        assert ops_per_second > 5000, f"Performance regression detected: {
            ops_per_second:.0f} ops/sec"
        assert total_time < 0.2, f"Total time regression detected: {
            total_time:.3f}s"

    def test_memory_usage_regression(self):
        """Test memory usage doesn't regress significantly"""
        cache = PricingCache(max_size=1000)
        benchmark = CacheBenchmark(cache)

        initial_memory = benchmark._estimate_memory_usage()

        # Add standard test data
        test_value = "x" * 1024  # 1KB per entry
        for i in range(500):
            cache.put(f"key_{i}", test_value, CacheLevel.COMPONENT)

        final_memory = benchmark._estimate_memory_usage()
        memory_per_entry = (final_memory - initial_memory) / 500

        print(f"Memory per entry: {memory_per_entry:.3f} MB")

        # Memory usage should be reasonable (allowing for overhead)
        assert memory_per_entry < 0.01, f"Memory usage regression: {
            memory_per_entry:.3f} MB per entry"


if __name__ == "__main__":
    # Run performance tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
