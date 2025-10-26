"""Database Performance Monitoring System

This module provides comprehensive database performance monitoring including:
- Query performance tracking with slow query detection
- Database metrics collection (connections, queries, errors)
- Database health checks with automated alerts
- Performance optimization recommendations
"""

import threading
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QueryType(Enum):
    """Query type classification"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DDL = "DDL"
    OTHER = "OTHER"


@dataclass
class QueryMetrics:
    """Metrics for a single query execution"""
    query: str
    query_type: QueryType
    duration: float
    timestamp: datetime
    error: str | None = None
    rows_affected: int | None = None
    connection_id: str | None = None
    user_id: str | None = None

    def is_slow(self, threshold: float) -> bool:
        """Check if query is slow"""
        return self.duration > threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query[:200],  # Truncate long queries
            'query_type': self.query_type.value,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'error': self.error,
            'rows_affected': self.rows_affected,
            'connection_id': self.connection_id,
            'user_id': self.user_id
        }


@dataclass
class PerformanceAlert:
    """Performance alert"""
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metric_name: str
    current_value: Any
    threshold_value: Any
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'severity': self.severity.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'details': self.details
        }


@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds"""
    slow_query_threshold: float = 1.0  # seconds
    very_slow_query_threshold: float = 5.0  # seconds
    error_rate_threshold: float = 0.05  # 5%
    connection_pool_usage_threshold: float = 0.8  # 80%
    avg_query_time_threshold: float = 0.5  # seconds
    queries_per_second_threshold: float = 100.0
    connection_leak_threshold: int = 5
    failed_connection_threshold: int = 10


@dataclass
class DatabasePerformanceStats:
    """Aggregated database performance statistics"""
    total_queries: int = 0
    slow_queries: int = 0
    very_slow_queries: int = 0
    failed_queries: int = 0
    total_query_time: float = 0.0
    avg_query_time: float = 0.0
    min_query_time: float = float('inf')
    max_query_time: float = 0.0
    queries_per_second: float = 0.0
    error_rate: float = 0.0

    # Connection metrics
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_pool_usage: float = 0.0

    # Query type breakdown
    select_queries: int = 0
    insert_queries: int = 0
    update_queries: int = 0
    delete_queries: int = 0
    ddl_queries: int = 0
    other_queries: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_queries': self.total_queries,
            'slow_queries': self.slow_queries,
            'very_slow_queries': self.very_slow_queries,
            'failed_queries': self.failed_queries,
            'total_query_time': self.total_query_time,
            'avg_query_time': self.avg_query_time,
            'min_query_time': self.min_query_time if self.min_query_time != float('inf') else 0.0,
            'max_query_time': self.max_query_time,
            'queries_per_second': self.queries_per_second,
            'error_rate': self.error_rate,
            'total_connections': self.total_connections,
            'active_connections': self.active_connections,
            'idle_connections': self.idle_connections,
            'failed_connections': self.failed_connections,
            'connection_pool_usage': self.connection_pool_usage,
            'query_type_breakdown': {
                'select': self.select_queries,
                'insert': self.insert_queries,
                'update': self.update_queries,
                'delete': self.delete_queries,
                'ddl': self.ddl_queries,
                'other': self.other_queries}}


@dataclass
class OptimizationRecommendation:
    """Database optimization recommendation"""
    priority: str  # high, medium, low
    category: str  # index, query, connection, configuration
    title: str
    description: str
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'priority': self.priority,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'impact': self.impact,
            'effort': self.effort,
            'details': self.details
        }


class DatabasePerformanceMonitor:
    """
    Comprehensive database performance monitoring system

    Features:
    - Query performance tracking with slow query detection
    - Database metrics collection (connections, queries, errors)
    - Health checks with automated alerts
    - Performance optimization recommendations
    """

    def __init__(
        self,
        thresholds: PerformanceThresholds | None = None,
        max_slow_queries: int = 100,
        max_alerts: int = 1000,
        enable_recommendations: bool = True
    ):
        self.thresholds = thresholds or PerformanceThresholds()
        self.max_slow_queries = max_slow_queries
        self.max_alerts = max_alerts
        self.enable_recommendations = enable_recommendations

        # Query tracking
        self._query_history: deque = deque(maxlen=10000)
        self._slow_queries: deque = deque(maxlen=max_slow_queries)
        self._very_slow_queries: deque = deque(maxlen=max_slow_queries)

        # Metrics
        self._stats = DatabasePerformanceStats()
        self._query_times_by_type: dict[QueryType,
                                        list[float]] = defaultdict(list)
        self._query_counts_by_table: dict[str, int] = defaultdict(int)

        # Alerts
        self._alerts: deque = deque(maxlen=max_alerts)
        self._alert_callbacks: list[Callable[[PerformanceAlert], None]] = []

        # Monitoring state
        self._start_time = datetime.utcnow()
        self._last_stats_update = datetime.utcnow()
        self._lock = threading.Lock()

        # Recommendations cache
        self._recommendations: list[OptimizationRecommendation] = []
        self._last_recommendation_update: datetime | None = None

        logger.info("Database performance monitor initialized")

    def record_query(
        self,
        query: str,
        duration: float,
        error: Exception | None = None,
        rows_affected: int | None = None,
        connection_id: str | None = None,
        user_id: str | None = None
    ):
        """
        Record query execution metrics

        Args:
            query: SQL query string
            duration: Query execution time in seconds
            error: Exception if query failed
            rows_affected: Number of rows affected
            connection_id: Connection identifier
            user_id: User who executed the query
        """
        query_type = self._classify_query(query)

        metrics = QueryMetrics(
            query=query,
            query_type=query_type,
            duration=duration,
            timestamp=datetime.utcnow(),
            error=str(error) if error else None,
            rows_affected=rows_affected,
            connection_id=connection_id,
            user_id=user_id
        )

        with self._lock:
            # Add to history
            self._query_history.append(metrics)

            # Update stats
            self._stats.total_queries += 1
            self._stats.total_query_time += duration
            self._stats.min_query_time = min(
                self._stats.min_query_time, duration)
            self._stats.max_query_time = max(
                self._stats.max_query_time, duration)

            # Update query type counts
            if query_type == QueryType.SELECT:
                self._stats.select_queries += 1
            elif query_type == QueryType.INSERT:
                self._stats.insert_queries += 1
            elif query_type == QueryType.UPDATE:
                self._stats.update_queries += 1
            elif query_type == QueryType.DELETE:
                self._stats.delete_queries += 1
            elif query_type == QueryType.DDL:
                self._stats.ddl_queries += 1
            else:
                self._stats.other_queries += 1

            # Track by type
            self._query_times_by_type[query_type].append(duration)

            # Track by table
            table_name = self._extract_table_name(query)
            if table_name:
                self._query_counts_by_table[table_name] += 1

            # Track errors
            if error:
                self._stats.failed_queries += 1

            # Track slow queries
            if metrics.is_slow(self.thresholds.slow_query_threshold):
                self._stats.slow_queries += 1
                self._slow_queries.append(metrics)

                logger.warning(
                    "Slow query detected",
                    duration=duration,
                    query=query[:200],
                    query_type=query_type.value
                )

                # Create alert for slow query
                if duration > self.thresholds.very_slow_query_threshold:
                    self._stats.very_slow_queries += 1
                    self._very_slow_queries.append(metrics)

                    self._create_alert(
                        AlertSeverity.ERROR,
                        f"Very slow query detected ({duration:.2f}s)",
                        "query_duration",
                        duration,
                        self.thresholds.very_slow_query_threshold,
                        {'query': query[:200], 'query_type': query_type.value}
                    )
                elif duration > self.thresholds.slow_query_threshold:
                    self._create_alert(
                        AlertSeverity.WARNING,
                        f"Slow query detected ({duration:.2f}s)",
                        "query_duration",
                        duration,
                        self.thresholds.slow_query_threshold,
                        {'query': query[:200], 'query_type': query_type.value}
                    )

            # Update calculated metrics periodically
            if (datetime.utcnow() - self._last_stats_update).total_seconds() > 10:
                self._update_calculated_stats()

    def record_connection_event(
        self,
        event_type: str,
        connection_id: str | None = None,
        error: Exception | None = None
    ):
        """
        Record connection pool events

        Args:
            event_type: Type of event (checkout, checkin, create, close, error)
            connection_id: Connection identifier
            error: Exception if event failed
        """
        with self._lock:
            if event_type == "create":
                self._stats.total_connections += 1
            elif event_type == "checkout":
                self._stats.active_connections += 1
                self._stats.idle_connections = max(
                    0, self._stats.idle_connections - 1)
            elif event_type == "checkin":
                self._stats.active_connections = max(
                    0, self._stats.active_connections - 1)
                self._stats.idle_connections += 1
            elif event_type == "error":
                self._stats.failed_connections += 1

                if self._stats.failed_connections > self.thresholds.failed_connection_threshold:
                    self._create_alert(
                        AlertSeverity.ERROR,
                        f"High connection failure rate ({self._stats.failed_connections} failures)",
                        "failed_connections",
                        self._stats.failed_connections,
                        self.thresholds.failed_connection_threshold,
                        {'error': str(error) if error else None}
                    )

    def update_pool_metrics(
        self,
        pool_size: int,
        checked_out: int,
        checked_in: int,
        overflow: int
    ):
        """
        Update connection pool metrics

        Args:
            pool_size: Total pool size
            checked_out: Number of checked out connections
            checked_in: Number of checked in connections
            overflow: Number of overflow connections
        """
        with self._lock:
            self._stats.active_connections = checked_out
            self._stats.idle_connections = checked_in

            if pool_size > 0:
                self._stats.connection_pool_usage = checked_out / pool_size

                # Alert on high pool usage
                if self._stats.connection_pool_usage > self.thresholds.connection_pool_usage_threshold:
                    self._create_alert(
                        AlertSeverity.WARNING,
                        f"High connection pool usage ({self._stats.connection_pool_usage:.1%})",
                        "connection_pool_usage",
                        self._stats.connection_pool_usage,
                        self.thresholds.connection_pool_usage_threshold,
                        {
                            'pool_size': pool_size,
                            'checked_out': checked_out,
                            'overflow': overflow
                        }
                    )

    def get_stats(self) -> DatabasePerformanceStats:
        """Get current performance statistics"""
        with self._lock:
            self._update_calculated_stats()
            return self._stats

    def get_slow_queries(self, limit: int = 10) -> list[QueryMetrics]:
        """
        Get recent slow queries

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of slow query metrics
        """
        with self._lock:
            return list(self._slow_queries)[-limit:]

    def get_very_slow_queries(self, limit: int = 10) -> list[QueryMetrics]:
        """
        Get recent very slow queries

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of very slow query metrics
        """
        with self._lock:
            return list(self._very_slow_queries)[-limit:]

    def get_alerts(
        self,
        severity: AlertSeverity | None = None,
        limit: int = 100
    ) -> list[PerformanceAlert]:
        """
        Get recent performance alerts

        Args:
            severity: Filter by severity level
            limit: Maximum number of alerts to return

        Returns:
            List of performance alerts
        """
        with self._lock:
            alerts = list(self._alerts)

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

            return alerts[-limit:]

    def get_query_stats_by_type(self) -> dict[str, dict[str, Any]]:
        """Get query statistics broken down by query type"""
        with self._lock:
            stats = {}

            for query_type, times in self._query_times_by_type.items():
                if times:
                    stats[query_type.value] = {
                        'count': len(times),
                        'avg_duration': sum(times) / len(times),
                        'min_duration': min(times),
                        'max_duration': max(times),
                        'total_duration': sum(times)
                    }

            return stats

    def get_query_stats_by_table(self, limit: int = 20) -> dict[str, int]:
        """
        Get query counts by table

        Args:
            limit: Maximum number of tables to return

        Returns:
            Dictionary of table names to query counts
        """
        with self._lock:
            sorted_tables = sorted(
                self._query_counts_by_table.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return dict(sorted_tables[:limit])

    def get_recommendations(
            self,
            force_refresh: bool = False) -> list[OptimizationRecommendation]:
        """
        Get performance optimization recommendations

        Args:
            force_refresh: Force regeneration of recommendations

        Returns:
            List of optimization recommendations
        """
        with self._lock:
            # Refresh recommendations if needed
            if (
                force_refresh or
                not self._recommendations or
                not self._last_recommendation_update or
                (datetime.utcnow() - self._last_recommendation_update).total_seconds() > 300
            ):
                self._generate_recommendations()

            return self._recommendations.copy()

    def register_alert_callback(
            self, callback: Callable[[PerformanceAlert], None]):
        """
        Register callback for performance alerts

        Args:
            callback: Function to call when alert is created
        """
        self._alert_callbacks.append(callback)
        logger.info("Alert callback registered")

    def reset_stats(self):
        """Reset all statistics"""
        with self._lock:
            self._stats = DatabasePerformanceStats()
            self._query_history.clear()
            self._slow_queries.clear()
            self._very_slow_queries.clear()
            self._query_times_by_type.clear()
            self._query_counts_by_table.clear()
            self._start_time = datetime.utcnow()
            self._last_stats_update = datetime.utcnow()

            logger.info("Performance statistics reset")

    def _update_calculated_stats(self):
        """Update calculated statistics"""
        if self._stats.total_queries > 0:
            self._stats.avg_query_time = (
                self._stats.total_query_time / self._stats.total_queries
            )
            self._stats.error_rate = (
                self._stats.failed_queries / self._stats.total_queries
            )

        # Calculate queries per second
        elapsed = (datetime.utcnow() - self._start_time).total_seconds()
        if elapsed > 0:
            self._stats.queries_per_second = self._stats.total_queries / elapsed

        self._last_stats_update = datetime.utcnow()

        # Check thresholds and create alerts
        self._check_thresholds()

    def _check_thresholds(self):
        """Check performance thresholds and create alerts"""
        # Check error rate
        if self._stats.error_rate > self.thresholds.error_rate_threshold:
            self._create_alert(
                AlertSeverity.ERROR,
                f"High error rate ({self._stats.error_rate:.1%})",
                "error_rate",
                self._stats.error_rate,
                self.thresholds.error_rate_threshold
            )

        # Check average query time
        if self._stats.avg_query_time > self.thresholds.avg_query_time_threshold:
            self._create_alert(
                AlertSeverity.WARNING,
                f"High average query time ({self._stats.avg_query_time:.3f}s)",
                "avg_query_time",
                self._stats.avg_query_time,
                self.thresholds.avg_query_time_threshold
            )

    def _create_alert(
        self,
        severity: AlertSeverity,
        message: str,
        metric_name: str,
        current_value: Any,
        threshold_value: Any,
        details: dict[str, Any] | None = None
    ):
        """Create performance alert"""
        alert = PerformanceAlert(
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            details=details or {}
        )

        self._alerts.append(alert)

        # Call registered callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error("Error in alert callback", error=str(e))

        logger.warning(
            "Performance alert created",
            severity=severity.value,
            message=message,
            metric=metric_name
        )

    def _classify_query(self, query: str) -> QueryType:
        """Classify query by type"""
        query_upper = query.strip().upper()

        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        if query_upper.startswith('INSERT'):
            return QueryType.INSERT
        if query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        if query_upper.startswith('DELETE'):
            return QueryType.DELETE
        if any(query_upper.startswith(cmd)
               for cmd in ['CREATE', 'ALTER', 'DROP', 'TRUNCATE']):
            return QueryType.DDL
        return QueryType.OTHER

    def _extract_table_name(self, query: str) -> str | None:
        """Extract table name from query"""
        try:
            query_upper = query.strip().upper()

            # Simple extraction for common patterns
            if 'FROM' in query_upper:
                parts = query_upper.split('FROM')[1].split()
                if parts:
                    return parts[0].strip('(),;').lower()
            elif 'INTO' in query_upper:
                parts = query_upper.split('INTO')[1].split()
                if parts:
                    return parts[0].strip('(),;').lower()
            elif 'UPDATE' in query_upper:
                parts = query_upper.split('UPDATE')[1].split()
                if parts:
                    return parts[0].strip('(),;').lower()

            return None
        except Exception:
            return None

    def _generate_recommendations(self):
        """Generate performance optimization recommendations"""
        recommendations = []

        # Recommendation: High slow query rate
        if self._stats.total_queries > 100:
            slow_query_rate = self._stats.slow_queries / self._stats.total_queries

            if slow_query_rate > 0.1:  # More than 10% slow queries
                recommendations.append(
                    OptimizationRecommendation(
                        priority="high",
                        category="query",
                        title="High Slow Query Rate",
                        description=f"{
                            slow_query_rate:.1%} of queries are slow. Consider optimizing frequently executed queries.",
                        impact="high",
                        effort="medium",
                        details={
                            'slow_query_rate': slow_query_rate,
                            'slow_queries': self._stats.slow_queries,
                            'total_queries': self._stats.total_queries}))

        # Recommendation: Missing indexes
        if self._slow_queries:
            select_slow_queries = [
                q for q in self._slow_queries
                if q.query_type == QueryType.SELECT
            ]

            if len(select_slow_queries) > 10:
                recommendations.append(OptimizationRecommendation(
                    priority="high",
                    category="index",
                    title="Potential Missing Indexes",
                    description=f"{len(select_slow_queries)} slow SELECT queries detected. Consider adding indexes on frequently queried columns.",
                    impact="high",
                    effort="low",
                    details={
                        'slow_select_count': len(select_slow_queries),
                        'sample_queries': [q.query[:200] for q in select_slow_queries[:5]]
                    }
                ))

        # Recommendation: High connection pool usage
        if self._stats.connection_pool_usage > 0.8:
            recommendations.append(
                OptimizationRecommendation(
                    priority="medium",
                    category="connection",
                    title="High Connection Pool Usage",
                    description=f"Connection pool usage is at {
                        self._stats.connection_pool_usage:.1%}. Consider increasing pool size.",
                    impact="medium",
                    effort="low",
                    details={
                        'current_usage': self._stats.connection_pool_usage,
                        'active_connections': self._stats.active_connections}))

        # Recommendation: High error rate
        if self._stats.error_rate > 0.05:
            recommendations.append(
                OptimizationRecommendation(
                    priority="high",
                    category="query",
                    title="High Query Error Rate",
                    description=f"Query error rate is {
                        self._stats.error_rate:.1%}. Investigate and fix failing queries.",
                    impact="high",
                    effort="medium",
                    details={
                        'error_rate': self._stats.error_rate,
                        'failed_queries': self._stats.failed_queries,
                        'total_queries': self._stats.total_queries}))

        # Recommendation: Unbalanced query types
        total_writes = (
            self._stats.insert_queries +
            self._stats.update_queries +
            self._stats.delete_queries
        )

        if total_writes > self._stats.select_queries and self._stats.total_queries > 100:
            recommendations.append(OptimizationRecommendation(
                priority="medium",
                category="query",
                title="Write-Heavy Workload",
                description="More write operations than reads detected. Consider read replicas or caching.",
                impact="medium",
                effort="high",
                details={
                    'select_queries': self._stats.select_queries,
                    'write_queries': total_writes,
                    'ratio': total_writes / max(self._stats.select_queries, 1)
                }
            ))

        # Recommendation: Hot tables
        hot_tables = self.get_query_stats_by_table(limit=5)
        if hot_tables:
            max_queries = max(hot_tables.values())
            if max_queries > self._stats.total_queries * 0.3:  # One table > 30% of queries
                recommendations.append(
                    OptimizationRecommendation(
                        priority="medium",
                        category="query",
                        title="Hot Table Detected",
                        description="One table is receiving a disproportionate number of queries. Consider partitioning or caching.",
                        impact="medium",
                        effort="high",
                        details={
                            'hot_tables': hot_tables,
                            'max_queries': max_queries,
                            'total_queries': self._stats.total_queries}))

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        self._recommendations = recommendations
        self._last_recommendation_update = datetime.utcnow()

        logger.info(
            "Performance recommendations generated",
            count=len(recommendations)
        )


def create_performance_monitor(
    slow_query_threshold: float = 1.0,
    enable_recommendations: bool = True
) -> DatabasePerformanceMonitor:
    """
    Create database performance monitor with default configuration

    Args:
        slow_query_threshold: Threshold for slow query detection (seconds)
        enable_recommendations: Enable optimization recommendations

    Returns:
        DatabasePerformanceMonitor instance
    """
    thresholds = PerformanceThresholds(
        slow_query_threshold=slow_query_threshold
    )

    return DatabasePerformanceMonitor(
        thresholds=thresholds,
        enable_recommendations=enable_recommendations
    )
