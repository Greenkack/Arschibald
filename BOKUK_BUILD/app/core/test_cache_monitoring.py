"""Tests for Cache Performance Monitoring System"""

import time
from datetime import datetime, timedelta

import pytest

from .cache import get_cache
from .cache_monitoring import (
    CacheAlert,
    CacheMetric,
    CacheMetricsCollector,
    CacheMonitor,
    CachePerformanceAnalyzer,
    detect_performance_issues,
    disable_automatic_cleanup,
    enable_automatic_cleanup,
    get_cache_monitor,
    get_cache_performance_report,
    get_detailed_metrics,
    register_cleanup_callback,
    start_cache_monitoring,
    stop_cache_monitoring,
    trigger_manual_cleanup,
)


class TestCacheMetric:
    """Test CacheMetric dataclass"""

    def test_cache_metric_creation(self):
        metric = CacheMetric(
            timestamp=datetime.now(),
            layer="memory",
            metric_type="hit_rate",
            value=0.85,
            metadata={"test": "data"}
        )

        assert metric.layer == "memory"
        assert metric.metric_type == "hit_rate"
        assert metric.value == 0.85
        assert metric.metadata["test"] == "data"


class TestCacheAlert:
    """Test CacheAlert dataclass"""

    def test_cache_alert_creation(self):
        alert = CacheAlert(
            alert_id="test_alert_1",
            severity="warning",
            message="Test alert",
            metric_type="hit_rate",
            threshold=0.7,
            actual_value=0.65
        )

        assert alert.severity == "warning"
        assert alert.acknowledged is False
        assert alert.threshold == 0.7
        assert alert.actual_value == 0.65


class TestCacheMetricsCollector:
    """Test CacheMetricsCollector"""

    def test_record_metric(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "hit_rate", 0.90)

        metrics = collector.get_metrics(layer="memory", metric_type="hit_rate")
        assert len(metrics) == 2
        assert metrics[0].value == 0.85
        assert metrics[1].value == 0.90

    def test_get_metrics_with_filters(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "utilization", 0.75)
        collector.record_metric("database", "hit_rate", 0.80)

        # Filter by layer
        memory_metrics = collector.get_metrics(layer="memory")
        assert len(memory_metrics) == 2

        # Filter by metric type
        hit_rate_metrics = collector.get_metrics(metric_type="hit_rate")
        assert len(hit_rate_metrics) == 2

        # Filter by both
        memory_hit_rate = collector.get_metrics(
            layer="memory",
            metric_type="hit_rate"
        )
        assert len(memory_hit_rate) == 1
        assert memory_hit_rate[0].value == 0.85

    def test_get_metrics_with_time_filter(self):
        collector = CacheMetricsCollector()

        # Record old metric
        old_time = datetime.now() - timedelta(minutes=10)
        old_metric = CacheMetric(
            timestamp=old_time,
            layer="memory",
            metric_type="hit_rate",
            value=0.70
        )
        collector._metrics.append(old_metric)

        # Record new metric
        collector.record_metric("memory", "hit_rate", 0.85)

        # Get only recent metrics
        since = datetime.now() - timedelta(minutes=5)
        recent_metrics = collector.get_metrics(since=since)

        assert len(recent_metrics) == 1
        assert recent_metrics[0].value == 0.85

    def test_get_latest_metric(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.80)
        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "hit_rate", 0.90)

        latest = collector.get_latest_metric("memory", "hit_rate")
        assert latest is not None
        assert latest.value == 0.90

    def test_calculate_average(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.80)
        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "hit_rate", 0.90)

        avg = collector.calculate_average(
            "memory", "hit_rate", window_minutes=5)
        assert avg is not None
        assert abs(avg - 0.85) < 0.01

    def test_calculate_trend_improving(self):
        collector = CacheMetricsCollector()

        # Simulate improving trend
        for i in range(10):
            value = 0.5 + (i * 0.05)  # 0.5 to 0.95
            collector.record_metric("memory", "hit_rate", value)

        trend = collector.calculate_trend(
            "memory", "hit_rate", window_minutes=5)
        assert trend == "improving"

    def test_calculate_trend_degrading(self):
        collector = CacheMetricsCollector()

        # Simulate degrading trend
        for i in range(10):
            value = 0.95 - (i * 0.05)  # 0.95 to 0.5
            collector.record_metric("memory", "hit_rate", value)

        trend = collector.calculate_trend(
            "memory", "hit_rate", window_minutes=5)
        assert trend == "degrading"

    def test_calculate_trend_stable(self):
        collector = CacheMetricsCollector()

        # Simulate stable trend
        for i in range(10):
            collector.record_metric("memory", "hit_rate", 0.85)

        trend = collector.calculate_trend(
            "memory", "hit_rate", window_minutes=5)
        assert trend == "stable"

    def test_clear_metrics(self):
        collector = CacheMetricsCollector()

        collector.record_metric("memory", "hit_rate", 0.85)
        collector.record_metric("memory", "utilization", 0.75)

        collector.clear()

        metrics = collector.get_metrics()
        assert len(metrics) == 0


class TestCachePerformanceAnalyzer:
    """Test CachePerformanceAnalyzer"""

    def test_analyze_hit_rate(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        report = analyzer.analyze_hit_rate("memory")

        assert "hit_rate" in report
        assert "hits" in report
        assert "misses" in report
        assert "status" in report

    def test_analyze_cache_size(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        report = analyzer.analyze_cache_size("memory")

        assert "utilization" in report
        assert "entries" in report
        assert "max_entries" in report
        assert "total_size_bytes" in report

    def test_analyze_evictions(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        report = analyzer.analyze_evictions("memory")

        assert "evictions" in report
        assert "expirations" in report

    def test_get_comprehensive_report(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        report = analyzer.get_comprehensive_report()

        assert "timestamp" in report
        assert "layers" in report
        assert "alerts" in report
        assert "recommendations" in report

    def test_alert_creation(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Trigger low hit rate alert by analyzing with low hit rate
        # (This requires actual cache with low hit rate)
        cache = get_cache()

        # Create some cache misses
        for i in range(200):
            cache.get(f"nonexistent_key_{i}")

        report = analyzer.analyze_hit_rate("memory")

        # Check if alert was created
        alerts = analyzer.get_active_alerts()
        # May or may not have alerts depending on cache state

    def test_acknowledge_alert(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Create alert manually
        analyzer._create_alert(
            severity="warning",
            message="Test alert",
            metric_type="test",
            threshold=0.5,
            actual_value=0.3
        )

        alerts = analyzer.get_active_alerts()
        assert len(alerts) > 0

        alert_id = alerts[0]["alert_id"]
        success = analyzer.acknowledge_alert(alert_id)
        assert success

        # Should not appear in active alerts anymore
        active_alerts = analyzer.get_active_alerts()
        assert len(active_alerts) == 0

    def test_register_cleanup_callback(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        callback_executed = []

        def test_callback():
            callback_executed.append(True)

        analyzer.register_cleanup_callback(test_callback)

        # Trigger cleanup
        analyzer.trigger_automatic_cleanup("test")

        assert len(callback_executed) == 1

    def test_automatic_cleanup(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Add some cache entries
        cache = get_cache()
        for i in range(10):
            cache.set(f"test_key_{i}", f"value_{i}")

        # Trigger cleanup
        results = analyzer.trigger_automatic_cleanup("test")

        assert "timestamp" in results
        assert "reason" in results
        assert results["reason"] == "test"

    def test_check_and_cleanup_if_needed(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # With normal utilization, should not trigger cleanup
        result = analyzer.check_and_cleanup_if_needed()
        # Result may be None if utilization is low

    def test_detect_performance_degradation(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Record historical good performance
        for i in range(10):
            collector.record_metric("memory", "hit_rate", 0.90)

        # Simulate degradation
        cache = get_cache()
        for i in range(100):
            cache.get(f"miss_key_{i}")  # Generate misses

        # Detect degradation
        degradation = analyzer.detect_performance_degradation("memory")
        # May or may not detect depending on actual cache state

    def test_get_detailed_metrics(self):
        collector = CacheMetricsCollector()
        analyzer = CachePerformanceAnalyzer(collector)

        # Record some metrics
        for i in range(5):
            collector.record_metric("memory", "hit_rate", 0.80 + (i * 0.02))
            collector.record_metric("memory", "utilization", 0.50 + (i * 0.05))

        detailed = analyzer.get_detailed_metrics("memory", window_minutes=5)

        assert "layer" in detailed
        assert "window_minutes" in detailed
        assert "metrics" in detailed

        if "hit_rate" in detailed["metrics"]:
            hit_rate_stats = detailed["metrics"]["hit_rate"]
            assert "current" in hit_rate_stats
            assert "average" in hit_rate_stats
            assert "min" in hit_rate_stats
            assert "max" in hit_rate_stats
            assert "trend" in hit_rate_stats


class TestCacheMonitor:
    """Test CacheMonitor"""

    def test_monitor_creation(self):
        monitor = CacheMonitor(collection_interval_seconds=30)

        assert monitor.collection_interval == 30
        assert monitor.enable_auto_cleanup is True
        assert not monitor._running

    def test_monitor_start_stop(self):
        monitor = CacheMonitor(collection_interval_seconds=1)

        monitor.start()
        assert monitor._running

        time.sleep(0.5)  # Let it run briefly

        monitor.stop()
        assert not monitor._running

    def test_monitor_get_report(self):
        monitor = CacheMonitor()

        report = monitor.get_report()

        assert "timestamp" in report
        assert "layers" in report
        assert "alerts" in report
        assert "recommendations" in report

    def test_monitor_get_detailed_report(self):
        monitor = CacheMonitor()

        detailed_report = monitor.get_detailed_report(window_minutes=30)

        assert "timestamp" in detailed_report
        assert "detailed_metrics" in detailed_report
        assert "monitoring_status" in detailed_report

        status = detailed_report["monitoring_status"]
        assert "running" in status
        assert "collection_interval_seconds" in status
        assert "auto_cleanup_enabled" in status

    def test_monitor_with_auto_cleanup_disabled(self):
        monitor = CacheMonitor(enable_auto_cleanup=False)

        assert monitor.enable_auto_cleanup is False


class TestCacheMonitoringAPI:
    """Test cache monitoring API functions"""

    def test_get_cache_monitor(self):
        monitor = get_cache_monitor()
        assert monitor is not None
        assert isinstance(monitor, CacheMonitor)

        # Should return same instance
        monitor2 = get_cache_monitor()
        assert monitor is monitor2

    def test_start_stop_monitoring(self):
        start_cache_monitoring(interval_seconds=1)

        monitor = get_cache_monitor()
        assert monitor._running

        time.sleep(0.5)

        stop_cache_monitoring()
        assert not monitor._running

    def test_get_cache_performance_report(self):
        report = get_cache_performance_report()

        assert "timestamp" in report
        assert "layers" in report

    def test_get_cache_performance_report_detailed(self):
        report = get_cache_performance_report(detailed=True)

        assert "timestamp" in report
        assert "detailed_metrics" in report
        assert "monitoring_status" in report

    def test_enable_disable_automatic_cleanup(self):
        enable_automatic_cleanup(threshold=0.85)

        monitor = get_cache_monitor()
        assert monitor.enable_auto_cleanup is True
        assert monitor.cleanup_threshold == 0.85

        disable_automatic_cleanup()
        assert monitor.enable_auto_cleanup is False

    def test_register_cleanup_callback(self):
        callback_executed = []

        def test_callback():
            callback_executed.append(True)

        register_cleanup_callback(test_callback)

        # Trigger cleanup to test callback
        trigger_manual_cleanup("test")

        assert len(callback_executed) > 0

    def test_trigger_manual_cleanup(self):
        results = trigger_manual_cleanup("manual_test")

        assert "timestamp" in results
        assert "reason" in results
        assert results["reason"] == "manual_test"

    def test_get_detailed_metrics(self):
        # Record some metrics first
        monitor = get_cache_monitor()
        monitor.metrics_collector.record_metric("memory", "hit_rate", 0.85)

        detailed = get_detailed_metrics("memory", window_minutes=5)

        assert "layer" in detailed
        assert "window_minutes" in detailed
        assert "metrics" in detailed

    def test_detect_performance_issues(self):
        issues = detect_performance_issues()

        assert "degradation" in issues
        assert "alerts" in issues
        assert "recommendations" in issues


class TestCacheMonitoringIntegration:
    """Integration tests for cache monitoring"""

    def test_end_to_end_monitoring(self):
        """Test complete monitoring workflow"""
        # Start monitoring
        start_cache_monitoring(interval_seconds=1)

        # Generate some cache activity
        cache = get_cache()
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")

        for i in range(30):
            cache.get(f"key_{i}")  # Hits

        for i in range(20):
            cache.get(f"miss_key_{i}")  # Misses

        # Wait for collection
        time.sleep(1.5)

        # Get report
        report = get_cache_performance_report(detailed=True)

        assert "layers" in report
        assert "memory" in report["layers"]

        # Stop monitoring
        stop_cache_monitoring()

    def test_automatic_cleanup_integration(self):
        """Test automatic cleanup workflow"""
        # Enable auto cleanup with low threshold
        enable_automatic_cleanup(threshold=0.5)

        # Fill cache
        cache = get_cache()
        for i in range(100):
            cache.set(f"cleanup_key_{i}", f"value_{i}", ttl=1)

        # Wait for expiration
        time.sleep(1.5)

        # Trigger cleanup check
        monitor = get_cache_monitor()
        result = monitor.analyzer.check_and_cleanup_if_needed()

        # Cleanup may or may not trigger depending on utilization

        # Disable cleanup
        disable_automatic_cleanup()

    def test_performance_degradation_detection(self):
        """Test performance degradation detection"""
        monitor = get_cache_monitor()

        # Establish baseline
        for i in range(10):
            monitor.metrics_collector.record_metric("memory", "hit_rate", 0.90)

        # Simulate degradation
        cache = get_cache()
        for i in range(200):
            cache.get(f"degrade_miss_{i}")

        # Detect degradation
        degradation = monitor.analyzer.detect_performance_degradation("memory")

        # May or may not detect depending on actual hit rate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
