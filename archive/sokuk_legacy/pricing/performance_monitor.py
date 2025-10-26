#!/usr/bin/env python3
"""
Performance Monitoring and Benchmarking for Enhanced Pricing System
Provides tools to monitor and benchmark database performance for pricing operations.
"""

import json
import logging
import os
import sqlite3
import statistics
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics"""
    operation_name: str
    execution_time_ms: float
    timestamp: datetime
    query_type: str
    result_count: int
    parameters: dict[str, Any]
    success: bool
    error_message: str | None = None


@dataclass
class BenchmarkResult:
    """Data class for benchmark results"""
    test_name: str
    total_operations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    median_time_ms: float
    std_dev_ms: float
    operations_per_second: float
    success_rate: float
    timestamp: datetime


class PerformanceMonitor:
    """
    Monitor and track performance of database operations.
    """

    def __init__(self, max_metrics: int = 10000):
        self.metrics: list[PerformanceMetric] = []
        self.max_metrics = max_metrics
        self.lock = threading.Lock()
        self._start_time = time.time()

    @contextmanager
    def measure_operation(self,
                          operation_name: str,
                          query_type: str = "unknown",
                          parameters: dict[str,
                                           Any] = None):
        """Context manager to measure operation performance"""
        start_time = time.time()
        success = True
        error_message = None
        result_count = 0

        try:
            yield self
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            metric = PerformanceMetric(
                operation_name=operation_name,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now(),
                query_type=query_type,
                result_count=result_count,
                parameters=parameters or {},
                success=success,
                error_message=error_message
            )

            self.add_metric(metric)

    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        with self.lock:
            self.metrics.append(metric)

            # Keep only the most recent metrics
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]

    def set_result_count(self, count: int):
        """Set result count for the most recent metric"""
        with self.lock:
            if self.metrics:
                self.metrics[-1].result_count = count

    def get_metrics_summary(self, operation_name: str = None,
                            since: datetime = None) -> dict[str, Any]:
        """Get summary statistics for metrics"""
        with self.lock:
            filtered_metrics = self.metrics

            if operation_name:
                filtered_metrics = [
                    m for m in filtered_metrics if m.operation_name == operation_name]

            if since:
                filtered_metrics = [
                    m for m in filtered_metrics if m.timestamp >= since]

            if not filtered_metrics:
                return {}

            execution_times = [
                m.execution_time_ms for m in filtered_metrics if m.success]

            if not execution_times:
                return {"error": "No successful operations found"}

            return {
                "operation_name": operation_name or "all",
                "total_operations": len(filtered_metrics),
                "successful_operations": len(execution_times),
                "success_rate": len(execution_times) / len(filtered_metrics),
                "avg_time_ms": statistics.mean(execution_times),
                "min_time_ms": min(execution_times),
                "max_time_ms": max(execution_times),
                "median_time_ms": statistics.median(execution_times),
                "std_dev_ms": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                "operations_per_second": len(execution_times) / (
                    sum(execution_times) / 1000) if sum(execution_times) > 0 else 0,
                "time_range": {
                    "start": min(
                        m.timestamp for m in filtered_metrics),
                    "end": max(
                        m.timestamp for m in filtered_metrics)}}

    def get_slow_operations(
            self,
            threshold_ms: float = 100.0,
            limit: int = 10) -> list[PerformanceMetric]:
        """Get the slowest operations above threshold"""
        with self.lock:
            slow_ops = [
                m for m in self.metrics if m.execution_time_ms > threshold_ms and m.success]
            return sorted(
                slow_ops,
                key=lambda x: x.execution_time_ms,
                reverse=True)[
                :limit]

    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        with self.lock:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_metrics": len(self.metrics),
                "metrics": [asdict(m) for m in self.metrics]
            }

            # Convert datetime objects to strings
            for metric in data["metrics"]:
                metric["timestamp"] = metric["timestamp"].isoformat()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)


class DatabaseBenchmark:
    """
    Comprehensive benchmarking suite for database operations.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            try:
                from database import DB_PATH
                self.db_path = DB_PATH
            except ImportError:
                self.db_path = os.path.join('data', 'app_data.db')
        else:
            self.db_path = db_path

        self.monitor = PerformanceMonitor()
        self.results: list[BenchmarkResult] = []

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def benchmark_product_queries(
            self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark common product queries"""
        test_name = "product_queries"
        execution_times = []
        successful_operations = 0

        queries = [
            ("SELECT * FROM products WHERE category = ?", ("Modul",)),
            ("SELECT * FROM products WHERE calculate_per = ?", ("Stück",)),
            ("SELECT * FROM products WHERE purchase_price_net > ?", (100.0,)),
            ("SELECT COUNT(*) FROM products GROUP BY category", ()),
            ("SELECT * FROM products WHERE model_name LIKE ?", ("%Test%",)),
        ]

        start_time = time.time()

        for i in range(iterations):
            query, params = queries[i % len(queries)]

            try:
                with self.monitor.measure_operation(f"query_{i}", "SELECT", {"query": query}):
                    conn = self._get_connection()
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    self.monitor.set_result_count(len(results))
                    conn.close()

                execution_times.append(
                    self.monitor.metrics[-1].execution_time_ms)
                successful_operations += 1

            except Exception as e:
                logger.error(f"Query failed: {e}")

        total_time = time.time() - start_time

        result = BenchmarkResult(
            test_name=test_name,
            total_operations=iterations,
            total_time_ms=total_time *
            1000,
            avg_time_ms=statistics.mean(execution_times) if execution_times else 0,
            min_time_ms=min(execution_times) if execution_times else 0,
            max_time_ms=max(execution_times) if execution_times else 0,
            median_time_ms=statistics.median(execution_times) if execution_times else 0,
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=successful_operations /
            total_time if total_time > 0 else 0,
            success_rate=successful_operations /
            iterations,
            timestamp=datetime.now())

        self.results.append(result)
        return result

    def benchmark_pricing_calculations(
            self, iterations: int = 50) -> BenchmarkResult:
        """Benchmark pricing calculation operations"""
        test_name = "pricing_calculations"
        execution_times = []
        successful_operations = 0

        start_time = time.time()

        for i in range(iterations):
            try:
                with self.monitor.measure_operation(f"pricing_calc_{i}", "CALCULATION"):
                    # Simulate complex pricing calculation
                    conn = self._get_connection()
                    cursor = conn.cursor()

                    # Get product with pricing info
                    cursor.execute("""
                        SELECT p.*,
                               CASE
                                   WHEN p.purchase_price_net > 0 AND p.margin_type = 'percentage'
                                   THEN p.purchase_price_net * (1 + p.margin_value / 100.0)
                                   WHEN p.purchase_price_net > 0 AND p.margin_type = 'fixed'
                                   THEN p.purchase_price_net + p.margin_value
                                   ELSE p.price_euro
                               END as calculated_price
                        FROM products p
                        WHERE p.id = ?
                    """, (i % 10 + 1,))  # Cycle through first 10 products

                    result = cursor.fetchone()
                    self.monitor.set_result_count(1 if result else 0)
                    conn.close()

                execution_times.append(
                    self.monitor.metrics[-1].execution_time_ms)
                successful_operations += 1

            except Exception as e:
                logger.error(f"Pricing calculation failed: {e}")

        total_time = time.time() - start_time

        result = BenchmarkResult(
            test_name=test_name,
            total_operations=iterations,
            total_time_ms=total_time *
            1000,
            avg_time_ms=statistics.mean(execution_times) if execution_times else 0,
            min_time_ms=min(execution_times) if execution_times else 0,
            max_time_ms=max(execution_times) if execution_times else 0,
            median_time_ms=statistics.median(execution_times) if execution_times else 0,
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=successful_operations /
            total_time if total_time > 0 else 0,
            success_rate=successful_operations /
            iterations,
            timestamp=datetime.now())

        self.results.append(result)
        return result

    def benchmark_concurrent_access(
            self,
            num_threads: int = 5,
            operations_per_thread: int = 20) -> BenchmarkResult:
        """Benchmark concurrent database access"""
        test_name = "concurrent_access"
        execution_times = []
        successful_operations = 0
        total_operations = num_threads * operations_per_thread

        def worker_thread(thread_id: int):
            thread_times = []
            thread_successes = 0

            for i in range(operations_per_thread):
                try:
                    with self.monitor.measure_operation(f"concurrent_{thread_id}_{i}", "CONCURRENT"):
                        conn = self._get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT COUNT(*) FROM products WHERE category = ?", ("Modul",))
                        result = cursor.fetchone()
                        self.monitor.set_result_count(1)
                        conn.close()

                    thread_times.append(
                        self.monitor.metrics[-1].execution_time_ms)
                    thread_successes += 1

                except Exception as e:
                    logger.error(f"Concurrent operation failed: {e}")

            return thread_times, thread_successes

        start_time = time.time()

        # Run concurrent threads
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i)
                       for i in range(num_threads)]

            for future in concurrent.futures.as_completed(futures):
                thread_times, thread_successes = future.result()
                execution_times.extend(thread_times)
                successful_operations += thread_successes

        total_time = time.time() - start_time

        result = BenchmarkResult(
            test_name=test_name,
            total_operations=total_operations,
            total_time_ms=total_time *
            1000,
            avg_time_ms=statistics.mean(execution_times) if execution_times else 0,
            min_time_ms=min(execution_times) if execution_times else 0,
            max_time_ms=max(execution_times) if execution_times else 0,
            median_time_ms=statistics.median(execution_times) if execution_times else 0,
            std_dev_ms=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            operations_per_second=successful_operations /
            total_time if total_time > 0 else 0,
            success_rate=successful_operations /
            total_operations,
            timestamp=datetime.now())

        self.results.append(result)
        return result

    def run_full_benchmark_suite(self) -> dict[str, BenchmarkResult]:
        """Run complete benchmark suite"""
        print("Starting comprehensive database benchmark suite...")

        results = {}

        # Product queries benchmark
        print("Running product queries benchmark...")
        results['product_queries'] = self.benchmark_product_queries(100)

        # Pricing calculations benchmark
        print("Running pricing calculations benchmark...")
        results['pricing_calculations'] = self.benchmark_pricing_calculations(
            50)

        # Concurrent access benchmark
        print("Running concurrent access benchmark...")
        results['concurrent_access'] = self.benchmark_concurrent_access(5, 20)

        return results

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        report = []
        report.append("=" * 60)
        report.append("DATABASE PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 60)
        report.append(
            f"Generated: {
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Database: {self.db_path}")
        report.append("")

        if not self.results:
            report.append("No benchmark results available.")
            return "\n".join(report)

        for result in self.results:
            report.append(f"Test: {result.test_name.upper()}")
            report.append("-" * 40)
            report.append(f"Total Operations: {result.total_operations}")
            report.append(f"Success Rate: {result.success_rate:.2%}")
            report.append(f"Total Time: {result.total_time_ms:.2f} ms")
            report.append(f"Average Time: {result.avg_time_ms:.2f} ms")
            report.append(f"Min Time: {result.min_time_ms:.2f} ms")
            report.append(f"Max Time: {result.max_time_ms:.2f} ms")
            report.append(f"Median Time: {result.median_time_ms:.2f} ms")
            report.append(f"Std Deviation: {result.std_dev_ms:.2f} ms")
            report.append(
                f"Operations/Second: {result.operations_per_second:.2f}")
            report.append("")

        # Performance summary
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)

        avg_ops_per_sec = statistics.mean(
            [r.operations_per_second for r in self.results])
        avg_success_rate = statistics.mean(
            [r.success_rate for r in self.results])

        report.append(f"Average Operations/Second: {avg_ops_per_sec:.2f}")
        report.append(f"Average Success Rate: {avg_success_rate:.2%}")

        # Slow operations
        slow_ops = self.monitor.get_slow_operations(threshold_ms=50.0, limit=5)
        if slow_ops:
            report.append("")
            report.append("SLOWEST OPERATIONS (>50ms)")
            report.append("-" * 40)
            for op in slow_ops:
                report.append(
                    f"{op.operation_name}: {op.execution_time_ms:.2f} ms")

        return "\n".join(report)

    def export_results(self, filepath: str):
        """Export benchmark results to JSON file"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "database_path": self.db_path,
            "results": []
        }

        for result in self.results:
            result_dict = asdict(result)
            result_dict["timestamp"] = result_dict["timestamp"].isoformat()
            data["results"].append(result_dict)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def run_performance_analysis():
    """Run comprehensive performance analysis"""
    benchmark = DatabaseBenchmark()

    # Run benchmark suite
    results = benchmark.run_full_benchmark_suite()

    # Generate and print report
    report = benchmark.generate_performance_report()
    print(report)

    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark.export_results(f"performance_results_{timestamp}.json")
    benchmark.monitor.export_metrics(f"performance_metrics_{timestamp}.json")

    return results


if __name__ == "__main__":
    # Run performance analysis
    results = run_performance_analysis()

    print("\nPerformance analysis completed!")
    print("Results exported to JSON files.")
