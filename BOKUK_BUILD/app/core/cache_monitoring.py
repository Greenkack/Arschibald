"""Cache Performance Monitoring System

This module provides comprehensive cache performance monitoring including:
- Detailed hit rate tracking with historical data
- Performance analytics with trend analysis
- Cache size monitoring with automatic cleanup
- Performance degradation alerts
"""

import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .cache import get_cache


@dataclass
class CacheMetric:
    """Single cache metric data point"""
    timestamp: datetime
    layer: str
    metric_type: str
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheAlert:
    """Cache performance alert"""
    alert_id: str
    severity: str  # info, warning, critical
    message: str
    metric_type: str
    threshold: float
    actual_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class CacheMetricsCollector:
    """Collect and track cache performance metrics"""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self._metrics: deque[CacheMetric] = deque(maxlen=history_size)
        self._lock = threading.RLock()

    def record_metric(
        self,
        layer: str,
        metric_type: str,
        value: float,
        metadata: dict[str, Any] = None
    ) -> None:
        """Record a cache metric"""
        metric = CacheMetric(
            timestamp=datetime.now(),
            layer=layer,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )

        with self._lock:
            self._metrics.append(metric)

    def get_metrics(
        self,
        layer: str = None,
        metric_type: str = None,
        since: datetime = None
    ) -> list[CacheMetric]:
        """Get metrics with optional filtering"""
        with self._lock:
            metrics = list(self._metrics)

        # Apply filters
        if layer:
            metrics = [m for m in metrics if m.layer == layer]

        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]

        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        return metrics

    def get_latest_metric(
        self,
        layer: str,
        metric_type: str
    ) -> CacheMetric | None:
        """Get latest metric for layer and type"""
        metrics = self.get_metrics(layer=layer, metric_type=metric_type)
        return metrics[-1] if metrics else None

    def calculate_average(
        self,
        layer: str,
        metric_type: str,
        window_minutes: int = 5
    ) -> float | None:
        """Calculate average metric value over time window"""
        since = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(
            layer=layer,
            metric_type=metric_type,
            since=since
        )

        if not metrics:
            return None

        return sum(m.value for m in metrics) / len(metrics)

    def calculate_trend(
        self,
        layer: str,
        metric_type: str,
        window_minutes: int = 5
    ) -> str | None:
        """
        Calculate metric trend (improving, degrading, stable)

        Returns:
            'improving', 'degrading', 'stable', or None
        """
        since = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(
            layer=layer,
            metric_type=metric_type,
            since=since
        )

        if len(metrics) < 2:
            return None

        # Split into two halves
        mid = len(metrics) // 2
        first_half = metrics[:mid]
        second_half = metrics[mid:]

        avg_first = sum(m.value for m in first_half) / len(first_half)
        avg_second = sum(m.value for m in second_half) / len(second_half)

        # Determine trend based on metric type
        if metric_type in ["hit_rate", "performance"]:
            # Higher is better
            if avg_second > avg_first * 1.05:
                return "improving"
            if avg_second < avg_first * 0.95:
                return "degrading"
        else:
            # Lower is better (e.g., miss_rate, latency)
            if avg_second < avg_first * 0.95:
                return "improving"
            if avg_second > avg_first * 1.05:
                return "degrading"

        return "stable"

    def clear(self) -> None:
        """Clear all metrics"""
        with self._lock:
            self._metrics.clear()


class CachePerformanceAnalyzer:
    """Analyze cache performance and generate insights"""

    def __init__(self, metrics_collector: CacheMetricsCollector):
        self.metrics_collector = metrics_collector
        self._alerts: list[CacheAlert] = []
        self._alert_thresholds = {
            "hit_rate_low": 0.7,  # Alert if hit rate < 70%
            "miss_rate_high": 0.3,  # Alert if miss rate > 30%
            "size_high": 0.9,  # Alert if cache > 90% full
            "eviction_rate_high": 100,  # Alert if > 100 evictions/min
            "degradation_threshold": 0.15,  # 15% degradation triggers alert
        }
        self._lock = threading.RLock()
        self._cleanup_callbacks: list[Callable[[], None]] = []
        self._last_cleanup: datetime | None = None

    def analyze_hit_rate(self, layer: str = "memory") -> dict[str, Any]:
        """Analyze cache hit rate"""
        cache = get_cache()
        stats = cache.get_stats()
        layer_stats = stats.get(layer, {})

        hit_rate = layer_stats.get("hit_rate", 0.0)
        hits = layer_stats.get("hits", 0)
        misses = layer_stats.get("misses", 0)
        total = hits + misses

        # Record metric
        self.metrics_collector.record_metric(
            layer=layer,
            metric_type="hit_rate",
            value=hit_rate
        )

        # Check for alert
        if hit_rate < self._alert_thresholds["hit_rate_low"] and total > 100:
            self._create_alert(
                severity="warning",
                message=f"Low cache hit rate: {hit_rate:.1%}",
                metric_type="hit_rate",
                threshold=self._alert_thresholds["hit_rate_low"],
                actual_value=hit_rate
            )

        # Calculate trend
        trend = self.metrics_collector.calculate_trend(
            layer=layer,
            metric_type="hit_rate",
            window_minutes=5
        )

        return {
            "layer": layer,
            "hit_rate": hit_rate,
            "hits": hits,
            "misses": misses,
            "total_requests": total,
            "trend": trend,
            "status": self._get_status(hit_rate, "hit_rate")
        }

    def analyze_cache_size(self, layer: str = "memory") -> dict[str, Any]:
        """Analyze cache size and capacity"""
        cache = get_cache()
        stats = cache.get_stats()
        layer_stats = stats.get(layer, {})

        entries = layer_stats.get("entries", 0)
        max_entries = layer_stats.get("max_entries", 1)
        utilization = entries / max_entries if max_entries > 0 else 0
        total_size = layer_stats.get("total_size_bytes", 0)

        # Record metric
        self.metrics_collector.record_metric(
            layer=layer,
            metric_type="utilization",
            value=utilization,
            metadata={"entries": entries, "size_bytes": total_size}
        )

        # Check for alert
        if utilization > self._alert_thresholds["size_high"]:
            self._create_alert(
                severity="warning",
                message=f"Cache nearly full: {utilization:.1%}",
                metric_type="utilization",
                threshold=self._alert_thresholds["size_high"],
                actual_value=utilization
            )

        return {
            "layer": layer,
            "entries": entries,
            "max_entries": max_entries,
            "utilization": utilization,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "status": self._get_status(utilization, "utilization")
        }

    def analyze_evictions(self, layer: str = "memory") -> dict[str, Any]:
        """Analyze cache eviction patterns"""
        cache = get_cache()
        stats = cache.get_stats()
        layer_stats = stats.get(layer, {})

        evictions = layer_stats.get("evictions", 0)
        expirations = layer_stats.get("expirations", 0)

        # Calculate eviction rate (evictions per minute)
        # This is simplified - real implementation would track over time
        eviction_rate = evictions  # Placeholder

        # Record metric
        self.metrics_collector.record_metric(
            layer=layer,
            metric_type="evictions",
            value=evictions,
            metadata={"expirations": expirations}
        )

        return {
            "layer": layer,
            "evictions": evictions,
            "expirations": expirations,
            "eviction_rate_per_min": eviction_rate,
            "status": "ok" if eviction_rate < 100 else "warning"
        }

    def get_comprehensive_report(self) -> dict[str, Any]:
        """Get comprehensive cache performance report"""
        cache = get_cache()
        all_stats = cache.get_stats()

        report = {
            "timestamp": datetime.now().isoformat(),
            "layers": {},
            "alerts": self.get_active_alerts(),
            "recommendations": []
        }

        # Analyze each layer
        for layer in ["memory", "streamlit", "database"]:
            if layer in all_stats:
                report["layers"][layer] = {
                    "hit_rate": self.analyze_hit_rate(layer),
                    "size": self.analyze_cache_size(layer),
                    "evictions": self.analyze_evictions(layer)
                }

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _create_alert(
        self,
        severity: str,
        message: str,
        metric_type: str,
        threshold: float,
        actual_value: float
    ) -> None:
        """Create performance alert"""
        alert = CacheAlert(
            alert_id=f"{metric_type}_{int(time.time())}",
            severity=severity,
            message=message,
            metric_type=metric_type,
            threshold=threshold,
            actual_value=actual_value
        )

        with self._lock:
            self._alerts.append(alert)

        logger.warning(
            "Cache performance alert",
            severity=severity,
            message=message,
            metric_type=metric_type
        )

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get active (unacknowledged) alerts"""
        with self._lock:
            return [
                {
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "message": alert.message,
                    "metric_type": alert.metric_type,
                    "threshold": alert.threshold,
                    "actual_value": alert.actual_value,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in self._alerts
                if not alert.acknowledged
            ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self._lock:
            for alert in self._alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    return True
        return False

    def _get_status(self, value: float, metric_type: str) -> str:
        """Get status based on metric value"""
        if metric_type == "hit_rate":
            if value >= 0.9:
                return "excellent"
            if value >= 0.7:
                return "good"
            if value >= 0.5:
                return "fair"
            return "poor"
        if metric_type == "utilization":
            if value < 0.7:
                return "good"
            if value < 0.9:
                return "fair"
            return "critical"
        return "unknown"

    def register_cleanup_callback(self, callback: Callable[[], None]) -> None:
        """
        Register callback for automatic cleanup

        Args:
            callback: Function to call when cleanup is needed
        """
        with self._lock:
            self._cleanup_callbacks.append(callback)
            logger.info("Cleanup callback registered")

    def trigger_automatic_cleanup(
            self, reason: str = "size_threshold") -> dict:
        """
        Trigger automatic cache cleanup

        Args:
            reason: Reason for cleanup

        Returns:
            Cleanup results
        """
        with self._lock:
            self._last_cleanup = datetime.now()

        logger.info("Automatic cache cleanup triggered", reason=reason)

        results = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "callbacks_executed": 0,
            "entries_before": 0,
            "entries_after": 0,
            "space_freed_bytes": 0
        }

        # Get stats before cleanup
        cache = get_cache()
        stats_before = cache.get_stats()
        memory_before = stats_before.get("memory", {})
        results["entries_before"] = memory_before.get("entries", 0)
        size_before = memory_before.get("total_size_bytes", 0)

        # Execute cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
                results["callbacks_executed"] += 1
            except Exception as e:
                logger.error(
                    "Cleanup callback failed",
                    error=str(e)
                )

        # Get stats after cleanup
        stats_after = cache.get_stats()
        memory_after = stats_after.get("memory", {})
        results["entries_after"] = memory_after.get("entries", 0)
        size_after = memory_after.get("total_size_bytes", 0)
        results["space_freed_bytes"] = size_before - size_after

        logger.info(
            "Automatic cleanup completed",
            entries_freed=results["entries_before"] - results["entries_after"],
            space_freed_mb=results["space_freed_bytes"] / (1024 * 1024)
        )

        return results

    def check_and_cleanup_if_needed(self) -> dict | None:
        """
        Check if cleanup is needed and trigger if necessary

        Returns:
            Cleanup results if cleanup was triggered, None otherwise
        """
        cache = get_cache()
        stats = cache.get_stats()
        memory_stats = stats.get("memory", {})

        utilization = (
            memory_stats.get("entries", 0) /
            memory_stats.get("max_entries", 1)
        )

        # Trigger cleanup if utilization > 90%
        if utilization > 0.9:
            return self.trigger_automatic_cleanup("high_utilization")

        return None

    def detect_performance_degradation(
        self,
        layer: str = "memory",
        window_minutes: int = 10
    ) -> dict | None:
        """
        Detect performance degradation over time window

        Args:
            layer: Cache layer to analyze
            window_minutes: Time window for comparison

        Returns:
            Degradation details if detected, None otherwise
        """
        # Get current hit rate
        current_report = self.analyze_hit_rate(layer)
        current_hit_rate = current_report.get("hit_rate", 0)

        # Get historical average
        historical_avg = self.metrics_collector.calculate_average(
            layer=layer,
            metric_type="hit_rate",
            window_minutes=window_minutes
        )

        if historical_avg is None or historical_avg == 0:
            return None

        # Calculate degradation
        degradation = (historical_avg - current_hit_rate) / historical_avg

        threshold = self._alert_thresholds["degradation_threshold"]

        if degradation > threshold:
            degradation_info = {
                "layer": layer,
                "current_hit_rate": current_hit_rate,
                "historical_avg": historical_avg,
                "degradation_percent": degradation * 100,
                "threshold_percent": threshold * 100,
                "window_minutes": window_minutes,
                "detected_at": datetime.now().isoformat()
            }

            # Create alert
            self._create_alert(
                severity="warning",
                message=(
                    f"Performance degradation detected: "
                    f"{degradation * 100:.1f}% drop in hit rate"
                ),
                metric_type="performance_degradation",
                threshold=threshold,
                actual_value=degradation
            )

            logger.warning(
                "Cache performance degradation detected",
                **degradation_info
            )

            return degradation_info

        return None

    def get_detailed_metrics(
        self,
        layer: str = "memory",
        window_minutes: int = 60
    ) -> dict[str, Any]:
        """
        Get detailed performance metrics with historical data

        Args:
            layer: Cache layer to analyze
            window_minutes: Time window for metrics

        Returns:
            Detailed metrics dictionary
        """
        since = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.metrics_collector.get_metrics(
            layer=layer,
            since=since
        )

        # Group metrics by type
        metrics_by_type: dict[str, list[float]] = {}
        for metric in metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric.value)

        # Calculate statistics for each metric type
        detailed = {
            "layer": layer,
            "window_minutes": window_minutes,
            "metrics": {}
        }

        for metric_type, values in metrics_by_type.items():
            if not values:
                continue

            detailed["metrics"][metric_type] = {
                "current": values[-1] if values else 0,
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "trend": self.metrics_collector.calculate_trend(
                    layer=layer,
                    metric_type=metric_type,
                    window_minutes=window_minutes
                )
            }

        return detailed

    def _generate_recommendations(
        self,
        report: dict[str, Any]
    ) -> list[str]:
        """Generate performance recommendations"""
        recommendations = []

        # Check memory layer
        memory_layer = report["layers"].get("memory", {})
        hit_rate_data = memory_layer.get("hit_rate", {})
        size_data = memory_layer.get("size", {})

        hit_rate = hit_rate_data.get("hit_rate", 0)
        utilization = size_data.get("utilization", 0)

        if hit_rate < 0.7:
            recommendations.append(
                "Consider increasing cache TTL or max_entries to improve "
                "hit rate"
            )

        if utilization > 0.9:
            recommendations.append(
                "Cache is nearly full. Consider increasing max_entries or "
                "implementing more aggressive eviction"
            )

        if hit_rate_data.get("trend") == "degrading":
            recommendations.append(
                "Cache hit rate is degrading. Review cache invalidation "
                "patterns"
            )

        # Check for performance degradation
        degradation = self.detect_performance_degradation()
        if degradation:
            recommendations.append(
                f"Performance degraded by "
                f"{degradation['degradation_percent']:.1f}%. "
                f"Investigate recent changes or increased load"
            )

        # Check if cleanup is needed
        if utilization > 0.85:
            recommendations.append(
                "Cache utilization is high. Consider enabling automatic "
                "cleanup or increasing cache size"
            )

        return recommendations


class CacheMonitor:
    """Automated cache monitoring with periodic collection"""

    def __init__(
        self,
        collection_interval_seconds: int = 60,
        enable_auto_cleanup: bool = True,
        cleanup_threshold: float = 0.9
    ):
        self.collection_interval = collection_interval_seconds
        self.enable_auto_cleanup = enable_auto_cleanup
        self.cleanup_threshold = cleanup_threshold
        self.metrics_collector = CacheMetricsCollector()
        self.analyzer = CachePerformanceAnalyzer(self.metrics_collector)
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._collection_count = 0
        self._last_alert_check: datetime | None = None

        # Register default cleanup callback
        if enable_auto_cleanup:
            self.analyzer.register_cleanup_callback(
                self._default_cleanup_callback
            )

    def start(self) -> None:
        """Start monitoring"""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._thread.start()

        logger.info(
            "Cache monitoring started",
            interval_seconds=self.collection_interval,
            auto_cleanup=self.enable_auto_cleanup
        )

    def stop(self) -> None:
        """Stop monitoring"""
        with self._lock:
            self._running = False

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("Cache monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self._running:
            try:
                # Collect metrics
                self._collect_metrics()

                # Check for alerts every 5 collections
                if self._collection_count % 5 == 0:
                    self._check_alerts()

                # Check if cleanup is needed
                if self.enable_auto_cleanup:
                    self.analyzer.check_and_cleanup_if_needed()

                self._collection_count += 1

                # Sleep until next collection
                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error("Cache monitoring error", error=str(e))

    def _collect_metrics(self) -> None:
        """Collect current cache metrics"""
        try:
            # Analyze all layers
            self.analyzer.analyze_hit_rate("memory")
            self.analyzer.analyze_cache_size("memory")
            self.analyzer.analyze_evictions("memory")

            # Check for performance degradation
            self.analyzer.detect_performance_degradation("memory")

            logger.debug(
                "Cache metrics collected",
                collection_count=self._collection_count
            )

        except Exception as e:
            logger.error("Failed to collect cache metrics", error=str(e))

    def _check_alerts(self) -> None:
        """Check for performance alerts"""
        try:
            self._last_alert_check = datetime.now()

            alerts = self.analyzer.get_active_alerts()

            if alerts:
                logger.warning(
                    "Active cache performance alerts",
                    count=len(alerts),
                    alerts=[a["message"] for a in alerts]
                )

        except Exception as e:
            logger.error("Failed to check alerts", error=str(e))

    def _default_cleanup_callback(self) -> None:
        """Default cleanup callback - clears expired entries"""
        try:
            cache = get_cache()

            # Get all keys and check for expired entries
            all_keys = cache.memory_cache.get_all_keys()
            expired_count = 0

            for key in all_keys:
                entry = cache.memory_cache.get_entry(key)
                if entry and entry.is_expired():
                    cache.delete(key)
                    expired_count += 1

            if expired_count > 0:
                logger.info(
                    "Default cleanup completed",
                    expired_entries=expired_count
                )

        except Exception as e:
            logger.error("Default cleanup failed", error=str(e))

    def get_report(self) -> dict[str, Any]:
        """Get current performance report"""
        return self.analyzer.get_comprehensive_report()

    def get_detailed_report(
        self,
        window_minutes: int = 60
    ) -> dict[str, Any]:
        """
        Get detailed performance report with historical data

        Args:
            window_minutes: Time window for historical data

        Returns:
            Detailed report dictionary
        """
        report = self.get_report()

        # Add detailed metrics
        report["detailed_metrics"] = self.analyzer.get_detailed_metrics(
            layer="memory",
            window_minutes=window_minutes
        )

        # Add monitoring status
        report["monitoring_status"] = {
            "running": self._running,
            "collection_interval_seconds": self.collection_interval,
            "collection_count": self._collection_count,
            "auto_cleanup_enabled": self.enable_auto_cleanup,
            "last_alert_check": (
                self._last_alert_check.isoformat()
                if self._last_alert_check
                else None
            )
        }

        return report


# Global cache monitor
_cache_monitor: CacheMonitor | None = None
_monitor_lock = threading.Lock()


def get_cache_monitor() -> CacheMonitor:
    """Get global cache monitor"""
    global _cache_monitor
    with _monitor_lock:
        if _cache_monitor is None:
            _cache_monitor = CacheMonitor()
    return _cache_monitor


def start_cache_monitoring(interval_seconds: int = 60) -> None:
    """Start cache monitoring"""
    monitor = get_cache_monitor()
    monitor.collection_interval = interval_seconds
    monitor.start()


def stop_cache_monitoring() -> None:
    """Stop cache monitoring"""
    monitor = get_cache_monitor()
    monitor.stop()


def get_cache_performance_report(detailed: bool = False) -> dict[str, Any]:
    """
    Get cache performance report

    Args:
        detailed: If True, include detailed historical metrics

    Returns:
        Performance report dictionary
    """
    monitor = get_cache_monitor()
    if detailed:
        return monitor.get_detailed_report()
    return monitor.get_report()


def enable_automatic_cleanup(threshold: float = 0.9) -> None:
    """
    Enable automatic cache cleanup

    Args:
        threshold: Utilization threshold to trigger cleanup (0.0-1.0)
    """
    monitor = get_cache_monitor()
    monitor.enable_auto_cleanup = True
    monitor.cleanup_threshold = threshold
    logger.info(
        "Automatic cleanup enabled",
        threshold=threshold
    )


def disable_automatic_cleanup() -> None:
    """Disable automatic cache cleanup"""
    monitor = get_cache_monitor()
    monitor.enable_auto_cleanup = False
    logger.info("Automatic cleanup disabled")


def register_cleanup_callback(callback: Callable[[], None]) -> None:
    """
    Register custom cleanup callback

    Args:
        callback: Function to call during cleanup
    """
    monitor = get_cache_monitor()
    monitor.analyzer.register_cleanup_callback(callback)


def trigger_manual_cleanup(reason: str = "manual") -> dict:
    """
    Manually trigger cache cleanup

    Args:
        reason: Reason for cleanup

    Returns:
        Cleanup results
    """
    monitor = get_cache_monitor()
    return monitor.analyzer.trigger_automatic_cleanup(reason)


def get_detailed_metrics(
    layer: str = "memory",
    window_minutes: int = 60
) -> dict[str, Any]:
    """
    Get detailed cache metrics with historical data

    Args:
        layer: Cache layer to analyze
        window_minutes: Time window for metrics

    Returns:
        Detailed metrics dictionary
    """
    monitor = get_cache_monitor()
    return monitor.analyzer.get_detailed_metrics(layer, window_minutes)


def detect_performance_issues() -> dict[str, Any]:
    """
    Detect current performance issues

    Returns:
        Dictionary with detected issues
    """
    monitor = get_cache_monitor()
    issues = {
        "degradation": None,
        "alerts": [],
        "recommendations": []
    }

    # Check for degradation
    degradation = monitor.analyzer.detect_performance_degradation()
    if degradation:
        issues["degradation"] = degradation

    # Get active alerts
    issues["alerts"] = monitor.analyzer.get_active_alerts()

    # Get recommendations
    report = monitor.get_report()
    issues["recommendations"] = report.get("recommendations", [])

    return issues
