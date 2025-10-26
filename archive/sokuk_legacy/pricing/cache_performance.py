"""Performance monitoring and benchmarking for pricing cache system

This module provides comprehensive performance monitoring, benchmarking,
and analysis tools for the pricing cache system.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .pricing_cache import CacheLevel, PerformanceMetrics, PricingCache

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""
    operation_name: str
    total_operations: int
    total_duration_ms: float
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    median_duration_ms: float
    std_dev_ms: float
    operations_per_second: float
    cache_hit_rate: float
    memory_usage_mb: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    benchmarks: list[BenchmarkResult]
    cache_stats: dict[str, Any]
    recommendations: list[str]
    summary: dict[str, Any]


class PerformanceMonitor:
    """Real-time performance monitoring for pricing cache"""

    def __init__(self, cache: PricingCache, window_size: int = 1000):
        """Initialize performance monitor

        Args:
            cache: PricingCache instance to monitor
            window_size: Size of sliding window for metrics
        """
        self.cache = cache
        self.window_size = window_size
        self.metrics_window: deque = deque(maxlen=window_size)
        self.operation_counters: dict[str, int] = defaultdict(int)
        self.operation_durations: dict[str, list[float]] = defaultdict(list)
        self.lock = threading.RLock()
        self.monitoring_active = False

    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        with self.lock:
            self.monitoring_active = True
            logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        with self.lock:
            self.monitoring_active = False
            logger.info("Performance monitoring stopped")

    def record_operation(self, metric: PerformanceMetrics) -> None:
        """Record operation performance metric

        Args:
            metric: Performance metric to record
        """
        if not self.monitoring_active:
            return

        with self.lock:
            self.metrics_window.append(metric)
            self.operation_counters[metric.operation_name] += 1

            if metric.duration_ms is not None:
                self.operation_durations[metric.operation_name].append(
                    metric.duration_ms)

                # Keep only recent durations to prevent memory growth
                if len(
                        self.operation_durations[metric.operation_name]) > self.window_size:
                    self.operation_durations[metric.operation_name] = \
                        self.operation_durations[metric.operation_name][-self.window_size:]

    def get_current_stats(self) -> dict[str, Any]:
        """Get current performance statistics

        Returns:
            Dictionary with current performance stats
        """
        with self.lock:
            if not self.metrics_window:
                return {}

            # Calculate overall stats
            total_operations = len(self.metrics_window)
            cache_hits = sum(1 for m in self.metrics_window if m.cache_hit)
            hit_rate = (
                cache_hits /
                total_operations) if total_operations > 0 else 0.0

            # Calculate duration stats
            durations = [
                m.duration_ms for m in self.metrics_window if m.duration_ms is not None]

            duration_stats = {}
            if durations:
                duration_stats = {
                    "avg_duration_ms": statistics.mean(durations),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "median_duration_ms": statistics.median(durations),
                    "std_dev_ms": statistics.stdev(durations) if len(durations) > 1 else 0.0}

            # Operation-specific stats
            operation_stats = {}
            for op_name, count in self.operation_counters.items():
                op_durations = self.operation_durations.get(op_name, [])
                if op_durations:
                    operation_stats[op_name] = {
                        "count": count,
                        "avg_duration_ms": statistics.mean(op_durations),
                        "min_duration_ms": min(op_durations),
                        "max_duration_ms": max(op_durations)
                    }

            return {
                "total_operations": total_operations,
                "cache_hit_rate": hit_rate,
                "window_size": len(self.metrics_window),
                "duration_stats": duration_stats,
                "operation_stats": operation_stats,
                "timestamp": datetime.now().isoformat()
            }

    def reset_stats(self) -> None:
        """Reset all performance statistics"""
        with self.lock:
            self.metrics_window.clear()
            self.operation_counters.clear()
            self.operation_durations.clear()
            logger.info("Performance statistics reset")


class CacheBenchmark:
    """Benchmarking suite for pricing cache performance"""

    def __init__(self, cache: PricingCache):
        """Initialize benchmark suite

        Args:
            cache: PricingCache instance to benchmark
        """
        self.cache = cache
        self.monitor = PerformanceMonitor(cache)

    def benchmark_cache_operations(
            self,
            num_operations: int = 1000,
            key_pattern: str = "benchmark_key_{i}",
            value_size_bytes: int = 1024) -> BenchmarkResult:
        """Benchmark basic cache operations (put/get)

        Args:
            num_operations: Number of operations to perform
            key_pattern: Pattern for generating keys
            value_size_bytes: Size of values to cache

        Returns:
            BenchmarkResult with performance metrics
        """
        logger.info(
            f"Starting cache operations benchmark: {num_operations} operations")

        # Generate test data
        test_value = "x" * value_size_bytes
        durations = []
        cache_hits = 0

        start_time = time.time()

        # Benchmark put operations
        for i in range(num_operations // 2):
            key = key_pattern.format(i=i)

            op_start = time.time()
            self.cache.put(key, test_value, CacheLevel.SYSTEM)
            op_end = time.time()

            durations.append((op_end - op_start) * 1000)

        # Benchmark get operations
        for i in range(num_operations // 2):
            key = key_pattern.format(i=i)

            op_start = time.time()
            result = self.cache.get(key, CacheLevel.SYSTEM)
            op_end = time.time()

            durations.append((op_end - op_start) * 1000)
            if result is not None:
                cache_hits += 1

        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000

        # Calculate statistics
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        median_duration = statistics.median(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
        ops_per_second = num_operations / (total_duration_ms / 1000)
        hit_rate = (cache_hits / (num_operations // 2)
                    ) if num_operations > 0 else 0.0

        return BenchmarkResult(
            operation_name="cache_operations",
            total_operations=num_operations,
            total_duration_ms=total_duration_ms,
            avg_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            median_duration_ms=median_duration,
            std_dev_ms=std_dev,
            operations_per_second=ops_per_second,
            cache_hit_rate=hit_rate,
            memory_usage_mb=self._estimate_memory_usage()
        )

    def benchmark_concurrent_access(
            self,
            num_threads: int = 10,
            operations_per_thread: int = 100) -> BenchmarkResult:
        """Benchmark concurrent cache access

        Args:
            num_threads: Number of concurrent threads
            operations_per_thread: Operations per thread

        Returns:
            BenchmarkResult with concurrent performance metrics
        """
        logger.info(f"Starting concurrent access benchmark: {num_threads} threads, "
                    f"{operations_per_thread} ops/thread")

        import concurrent.futures

        def worker_thread(thread_id: int) -> list[float]:
            """Worker thread function"""
            durations = []
            for i in range(operations_per_thread):
                key = f"concurrent_key_{thread_id}_{i}"
                value = f"value_{thread_id}_{i}"

                # Put operation
                start = time.time()
                self.cache.put(key, value, CacheLevel.SYSTEM)
                end = time.time()
                durations.append((end - start) * 1000)

                # Get operation
                start = time.time()
                self.cache.get(key, CacheLevel.SYSTEM)
                end = time.time()
                durations.append((end - start) * 1000)

            return durations

        start_time = time.time()
        all_durations = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i)
                       for i in range(num_threads)]

            for future in concurrent.futures.as_completed(futures):
                all_durations.extend(future.result())

        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000
        total_operations = num_threads * operations_per_thread * 2  # put + get

        # Calculate statistics
        avg_duration = statistics.mean(all_durations)
        min_duration = min(all_durations)
        max_duration = max(all_durations)
        median_duration = statistics.median(all_durations)
        std_dev = statistics.stdev(all_durations) if len(
            all_durations) > 1 else 0.0
        ops_per_second = total_operations / (total_duration_ms / 1000)

        return BenchmarkResult(
            operation_name="concurrent_access",
            total_operations=total_operations,
            total_duration_ms=total_duration_ms,
            avg_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            median_duration_ms=median_duration,
            std_dev_ms=std_dev,
            operations_per_second=ops_per_second,
            cache_hit_rate=0.5,  # Approximate for concurrent test
            memory_usage_mb=self._estimate_memory_usage()
        )

    def benchmark_cache_invalidation(
            self,
            num_entries: int = 1000,
            invalidation_patterns: list[str] = None) -> BenchmarkResult:
        """Benchmark cache invalidation performance

        Args:
            num_entries: Number of cache entries to create
            invalidation_patterns: Patterns to test for invalidation

        Returns:
            BenchmarkResult with invalidation performance metrics
        """
        if invalidation_patterns is None:
            invalidation_patterns = ["pattern_1", "pattern_2", "pattern_3"]

        logger.info(
            f"Starting cache invalidation benchmark: {num_entries} entries")

        # Populate cache with test data
        for i in range(num_entries):
            pattern = invalidation_patterns[i % len(invalidation_patterns)]
            key = f"{pattern}_key_{i}"
            self.cache.put(key, f"value_{i}", CacheLevel.SYSTEM)

        durations = []
        total_invalidated = 0

        start_time = time.time()

        # Test pattern-based invalidation
        for pattern in invalidation_patterns:
            op_start = time.time()
            invalidated = self.cache.invalidate_by_pattern(pattern)
            op_end = time.time()

            durations.append((op_end - op_start) * 1000)
            total_invalidated += invalidated

        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000

        # Calculate statistics
        avg_duration = statistics.mean(durations) if durations else 0.0
        min_duration = min(durations) if durations else 0.0
        max_duration = max(durations) if durations else 0.0
        median_duration = statistics.median(durations) if durations else 0.0
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
        ops_per_second = len(invalidation_patterns) / \
            (total_duration_ms / 1000) if total_duration_ms > 0 else 0.0

        return BenchmarkResult(
            operation_name="cache_invalidation",
            total_operations=len(invalidation_patterns),
            total_duration_ms=total_duration_ms,
            avg_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            median_duration_ms=median_duration,
            std_dev_ms=std_dev,
            operations_per_second=ops_per_second,
            cache_hit_rate=0.0,  # Not applicable for invalidation
            memory_usage_mb=self._estimate_memory_usage()
        )

    def run_comprehensive_benchmark(self) -> PerformanceReport:
        """Run comprehensive benchmark suite

        Returns:
            PerformanceReport with all benchmark results
        """
        logger.info("Starting comprehensive benchmark suite")

        start_time = datetime.now()
        benchmarks = []

        # Clear cache before benchmarking
        self.cache.clear()

        try:
            # Basic operations benchmark
            benchmarks.append(self.benchmark_cache_operations(
                num_operations=1000,
                value_size_bytes=1024
            ))

            # Concurrent access benchmark
            benchmarks.append(self.benchmark_concurrent_access(
                num_threads=5,
                operations_per_thread=50
            ))

            # Cache invalidation benchmark
            benchmarks.append(self.benchmark_cache_invalidation(
                num_entries=500
            ))

            # Large value benchmark
            benchmarks.append(self.benchmark_cache_operations(
                num_operations=100,
                key_pattern="large_value_key_{i}",
                value_size_bytes=10240  # 10KB values
            ))

        except Exception as e:
            logger.error(f"Error during benchmarking: {e}")
            raise

        end_time = datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60

        # Get cache statistics
        cache_stats = self.cache.get_stats()

        # Generate recommendations
        recommendations = self._generate_recommendations(
            benchmarks, cache_stats)

        # Create summary
        summary = self._create_summary(benchmarks)

        report_id = f"benchmark_{int(start_time.timestamp())}"

        return PerformanceReport(
            report_id=report_id,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            benchmarks=benchmarks,
            cache_stats=cache_stats,
            recommendations=recommendations,
            summary=summary
        )

    def _estimate_memory_usage(self) -> float:
        """Estimate current memory usage in MB

        Returns:
            Estimated memory usage in MB
        """
        try:
            total_entries = 0

            for level in CacheLevel:
                cache = self.cache._caches[level]
                total_entries += len(cache)

            # Rough estimate: 1KB per cache entry on average
            estimated_bytes = total_entries * 1024
            return estimated_bytes / (1024 * 1024)  # Convert to MB

        except Exception:
            return 0.0

    def _generate_recommendations(self,
                                  benchmarks: list[BenchmarkResult],
                                  cache_stats: dict[str, Any]) -> list[str]:
        """Generate performance recommendations

        Args:
            benchmarks: Benchmark results
            cache_stats: Cache statistics

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Analyze operation performance
        for benchmark in benchmarks:
            if benchmark.avg_duration_ms > 10.0:  # > 10ms average
                recommendations.append(
                    f"High latency detected in {benchmark.operation_name} "
                    f"(avg: {benchmark.avg_duration_ms:.2f}ms). "
                    f"Consider optimizing cache size or TTL settings."
                )

            if benchmark.operations_per_second < 100:  # < 100 ops/sec
                recommendations.append(
                    f"Low throughput in {benchmark.operation_name} "
                    f"({benchmark.operations_per_second:.1f} ops/sec). "
                    f"Consider increasing cache size or using faster storage."
                )

            if benchmark.cache_hit_rate < 0.8:  # < 80% hit rate
                recommendations.append(
                    f"Low cache hit rate in {benchmark.operation_name} "
                    f"({benchmark.cache_hit_rate:.1%}). "
                    f"Consider increasing TTL or cache size."
                )

        # Analyze cache statistics
        for level_name, stats in cache_stats.items():
            if hasattr(stats, 'hit_rate') and stats.hit_rate < 0.7:
                recommendations.append(
                    f"Low hit rate for {level_name} cache ({
                        stats.hit_rate:.1%}). " f"Consider tuning cache parameters.")

            if hasattr(stats, 'evictions') and stats.evictions > stats.hits:
                recommendations.append(
                    f"High eviction rate for {level_name} cache. "
                    f"Consider increasing cache size."
                )

        if not recommendations:
            recommendations.append(
                "Cache performance is within acceptable parameters.")

        return recommendations

    def _create_summary(
            self, benchmarks: list[BenchmarkResult]) -> dict[str, Any]:
        """Create performance summary

        Args:
            benchmarks: Benchmark results

        Returns:
            Summary dictionary
        """
        if not benchmarks:
            return {}

        total_operations = sum(b.total_operations for b in benchmarks)
        avg_duration = statistics.mean([b.avg_duration_ms for b in benchmarks])
        avg_throughput = statistics.mean(
            [b.operations_per_second for b in benchmarks])
        avg_hit_rate = statistics.mean([b.cache_hit_rate for b in benchmarks])
        max_memory = max([b.memory_usage_mb for b in benchmarks])

        return {
            "total_operations": total_operations,
            "avg_duration_ms": avg_duration,
            "avg_throughput_ops_sec": avg_throughput,
            "avg_hit_rate": avg_hit_rate,
            "max_memory_usage_mb": max_memory,
            "benchmark_count": len(benchmarks)
        }


def export_performance_report(report: PerformanceReport,
                              format: str = "json") -> str:
    """Export performance report to string format

    Args:
        report: Performance report to export
        format: Export format ("json" or "csv")

    Returns:
        Formatted report string
    """
    if format.lower() == "json":
        return json.dumps({
            "report_id": report.report_id,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat(),
            "duration_minutes": report.duration_minutes,
            "benchmarks": [
                {
                    "operation_name": b.operation_name,
                    "total_operations": b.total_operations,
                    "avg_duration_ms": b.avg_duration_ms,
                    "operations_per_second": b.operations_per_second,
                    "cache_hit_rate": b.cache_hit_rate,
                    "memory_usage_mb": b.memory_usage_mb
                }
                for b in report.benchmarks
            ],
            "recommendations": report.recommendations,
            "summary": report.summary
        }, indent=2)

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "Operation", "Total Ops", "Avg Duration (ms)",
            "Ops/Sec", "Hit Rate", "Memory (MB)"
        ])

        # Write benchmark data
        for benchmark in report.benchmarks:
            writer.writerow([
                benchmark.operation_name,
                benchmark.total_operations,
                f"{benchmark.avg_duration_ms:.2f}",
                f"{benchmark.operations_per_second:.1f}",
                f"{benchmark.cache_hit_rate:.2%}",
                f"{benchmark.memory_usage_mb:.2f}"
            ])

        return output.getvalue()

    raise ValueError(f"Unsupported format: {format}")
