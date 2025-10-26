"""Tests for Database Performance Monitoring System"""

from datetime import datetime

import pytest

from core.db_performance_monitor import (
    AlertSeverity,
    DatabasePerformanceMonitor,
    OptimizationRecommendation,
    PerformanceAlert,
    PerformanceThresholds,
    QueryMetrics,
    QueryType,
    create_performance_monitor,
)


class TestQueryMetrics:
    """Test QueryMetrics dataclass"""

    def test_query_metrics_creation(self):
        """Test creating query metrics"""
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            query_type=QueryType.SELECT,
            duration=0.5,
            timestamp=datetime.utcnow()
        )

        assert metrics.query == "SELECT * FROM users"
        assert metrics.query_type == QueryType.SELECT
        assert metrics.duration == 0.5
        assert metrics.error is None

    def test_is_slow(self):
        """Test slow query detection"""
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            query_type=QueryType.SELECT,
            duration=1.5,
            timestamp=datetime.utcnow()
        )

        assert metrics.is_slow(1.0) is True
        assert metrics.is_slow(2.0) is False

    def test_to_dict(self):
        """Test converting to dictionary"""
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            query_type=QueryType.SELECT,
            duration=0.5,
            timestamp=datetime.utcnow(),
            rows_affected=10
        )

        data = metrics.to_dict()
        assert 'query' in data
        assert 'query_type' in data
        assert 'duration' in data
        assert data['rows_affected'] == 10


class TestPerformanceAlert:
    """Test PerformanceAlert dataclass"""

    def test_alert_creation(self):
        """Test creating performance alert"""
        alert = PerformanceAlert(
            severity=AlertSeverity.WARNING,
            message="Slow query detected",
            timestamp=datetime.utcnow(),
            metric_name="query_duration",
            current_value=1.5,
            threshold_value=1.0
        )

        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "Slow query detected"
        assert alert.current_value == 1.5

    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = PerformanceAlert(
            severity=AlertSeverity.ERROR,
            message="High error rate",
            timestamp=datetime.utcnow(),
            metric_name="error_rate",
            current_value=0.1,
            threshold_value=0.05
        )

        data = alert.to_dict()
        assert data['severity'] == 'error'
        assert data['message'] == "High error rate"
        assert data['metric_name'] == "error_rate"


class TestDatabasePerformanceMonitor:
    """Test DatabasePerformanceMonitor class"""

    def test_monitor_creation(self):
        """Test creating performance monitor"""
        monitor = create_performance_monitor()

        assert monitor is not None
        assert isinstance(monitor, DatabasePerformanceMonitor)
        assert monitor.thresholds is not None

    def test_record_query(self):
        """Test recording query metrics"""
        monitor = create_performance_monitor()

        monitor.record_query(
            query="SELECT * FROM users WHERE id = 1",
            duration=0.1
        )

        stats = monitor.get_stats()
        assert stats.total_queries == 1
        assert stats.select_queries == 1
        assert stats.total_query_time == 0.1

    def test_record_multiple_queries(self):
        """Test recording multiple queries"""
        monitor = create_performance_monitor()

        queries = [
            ("SELECT * FROM users", 0.1),
            ("INSERT INTO logs VALUES ('test')", 0.05),
            ("UPDATE users SET name = 'John'", 0.08),
            ("DELETE FROM sessions WHERE expired = true", 0.06),
        ]

        for query, duration in queries:
            monitor.record_query(query, duration)

        stats = monitor.get_stats()
        assert stats.total_queries == 4
        assert stats.select_queries == 1
        assert stats.insert_queries == 1
        assert stats.update_queries == 1
        assert stats.delete_queries == 1

    def test_slow_query_detection(self):
        """Test slow query detection"""
        monitor = create_performance_monitor(slow_query_threshold=0.5)

        # Fast query
        monitor.record_query("SELECT * FROM users", 0.1)

        # Slow query
        monitor.record_query("SELECT * FROM large_table", 0.8)

        stats = monitor.get_stats()
        assert stats.total_queries == 2
        assert stats.slow_queries == 1

        slow_queries = monitor.get_slow_queries()
        assert len(slow_queries) == 1
        assert slow_queries[0].duration == 0.8

    def test_very_slow_query_detection(self):
        """Test very slow query detection"""
        thresholds = PerformanceThresholds(
            slow_query_threshold=1.0,
            very_slow_query_threshold=5.0
        )
        monitor = DatabasePerformanceMonitor(thresholds=thresholds)

        # Very slow query
        monitor.record_query("SELECT * FROM huge_table", 6.0)

        stats = monitor.get_stats()
        assert stats.slow_queries == 1
        assert stats.very_slow_queries == 1

        very_slow = monitor.get_very_slow_queries()
        assert len(very_slow) == 1

    def test_error_tracking(self):
        """Test error tracking"""
        monitor = create_performance_monitor()

        # Successful query
        monitor.record_query("SELECT * FROM users", 0.1)

        # Failed query
        monitor.record_query(
            "SELECT * FROM invalid_table",
            0.1,
            error=Exception("Table does not exist")
        )

        stats = monitor.get_stats()
        assert stats.total_queries == 2
        assert stats.failed_queries == 1
        assert stats.error_rate == 0.5

    def test_connection_event_tracking(self):
        """Test connection event tracking"""
        monitor = create_performance_monitor()

        # Create connections
        for i in range(5):
            monitor.record_connection_event("create", f"conn_{i}")

        stats = monitor.get_stats()
        assert stats.total_connections == 5

        # Checkout connections
        for i in range(3):
            monitor.record_connection_event("checkout", f"conn_{i}")

        stats = monitor.get_stats()
        assert stats.active_connections == 3

    def test_pool_metrics_update(self):
        """Test connection pool metrics update"""
        monitor = create_performance_monitor()

        monitor.update_pool_metrics(
            pool_size=10,
            checked_out=7,
            checked_in=3,
            overflow=0
        )

        stats = monitor.get_stats()
        assert stats.active_connections == 7
        assert stats.idle_connections == 3
        assert stats.connection_pool_usage == 0.7

    def test_query_stats_by_type(self):
        """Test query statistics by type"""
        monitor = create_performance_monitor()

        # Record various query types
        monitor.record_query("SELECT * FROM users", 0.1)
        monitor.record_query("SELECT * FROM orders", 0.2)
        monitor.record_query("INSERT INTO logs VALUES ('test')", 0.05)
        monitor.record_query("UPDATE users SET name = 'John'", 0.08)

        stats_by_type = monitor.get_query_stats_by_type()

        assert 'SELECT' in stats_by_type
        assert stats_by_type['SELECT']['count'] == 2
        assert 'INSERT' in stats_by_type
        assert stats_by_type['INSERT']['count'] == 1

    def test_query_stats_by_table(self):
        """Test query statistics by table"""
        monitor = create_performance_monitor()

        # Record queries on different tables
        monitor.record_query("SELECT * FROM users", 0.1)
        monitor.record_query("SELECT * FROM users WHERE id = 1", 0.1)
        monitor.record_query("SELECT * FROM orders", 0.1)

        stats_by_table = monitor.get_query_stats_by_table()

        assert 'users' in stats_by_table
        assert stats_by_table['users'] == 2
        assert 'orders' in stats_by_table
        assert stats_by_table['orders'] == 1

    def test_alert_creation(self):
        """Test alert creation"""
        monitor = create_performance_monitor(slow_query_threshold=0.5)

        # Trigger slow query alert
        monitor.record_query("SELECT * FROM large_table", 0.8)

        alerts = monitor.get_alerts()
        assert len(alerts) > 0
        assert alerts[0].severity in [
            AlertSeverity.WARNING, AlertSeverity.ERROR]

    def test_alert_callback(self):
        """Test alert callback registration"""
        monitor = create_performance_monitor(slow_query_threshold=0.5)

        callback_called = {'count': 0}

        def test_callback(alert):
            callback_called['count'] += 1

        monitor.register_alert_callback(test_callback)

        # Trigger alert
        monitor.record_query("SELECT * FROM large_table", 0.8)

        assert callback_called['count'] > 0

    def test_alert_filtering_by_severity(self):
        """Test filtering alerts by severity"""
        monitor = create_performance_monitor(slow_query_threshold=0.5)

        # Trigger different severity alerts
        monitor.record_query("SELECT * FROM table1", 0.8)  # WARNING
        monitor.record_query("SELECT * FROM table2", 6.0)  # ERROR (very slow)

        warning_alerts = monitor.get_alerts(severity=AlertSeverity.WARNING)
        error_alerts = monitor.get_alerts(severity=AlertSeverity.ERROR)

        assert len(warning_alerts) > 0
        assert len(error_alerts) > 0

    def test_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        monitor = create_performance_monitor(slow_query_threshold=0.3)

        # Create workload with issues
        # Many slow SELECT queries
        for i in range(15):
            monitor.record_query(f"SELECT * FROM table_{i}", 0.8)

        # Some fast queries
        for i in range(10):
            monitor.record_query(f"SELECT * FROM users WHERE id = {i}", 0.05)

        recommendations = monitor.get_recommendations(force_refresh=True)

        assert len(recommendations) > 0
        assert any(r.category == "index" for r in recommendations)

    def test_high_error_rate_recommendation(self):
        """Test high error rate recommendation"""
        monitor = create_performance_monitor()

        # Create high error rate
        for i in range(20):
            error = Exception("Error") if i % 2 == 0 else None
            monitor.record_query(f"SELECT * FROM table_{i}", 0.1, error=error)

        recommendations = monitor.get_recommendations(force_refresh=True)

        assert any(
            "error" in r.title.lower() or "error" in r.description.lower()
            for r in recommendations
        )

    def test_high_pool_usage_recommendation(self):
        """Test high connection pool usage recommendation"""
        monitor = create_performance_monitor()

        # Simulate high pool usage
        monitor.update_pool_metrics(
            pool_size=10,
            checked_out=9,
            checked_in=1,
            overflow=2
        )

        # Need some queries for recommendations
        for i in range(10):
            monitor.record_query(f"SELECT * FROM table_{i}", 0.1)

        recommendations = monitor.get_recommendations(force_refresh=True)

        assert any(
            "connection" in r.category.lower() or "pool" in r.title.lower()
            for r in recommendations
        )

    def test_stats_reset(self):
        """Test statistics reset"""
        monitor = create_performance_monitor()

        # Record some queries
        for i in range(5):
            monitor.record_query(f"SELECT * FROM table_{i}", 0.1)

        stats = monitor.get_stats()
        assert stats.total_queries == 5

        # Reset stats
        monitor.reset_stats()

        stats = monitor.get_stats()
        assert stats.total_queries == 0
        assert stats.total_query_time == 0.0

    def test_calculated_metrics(self):
        """Test calculated metrics"""
        monitor = create_performance_monitor()

        # Record queries
        queries = [0.1, 0.2, 0.3, 0.4, 0.5]
        for duration in queries:
            monitor.record_query("SELECT * FROM users", duration)

        stats = monitor.get_stats()

        # Check average
        expected_avg = sum(queries) / len(queries)
        assert abs(stats.avg_query_time - expected_avg) < 0.001

        # Check min/max
        assert stats.min_query_time == min(queries)
        assert stats.max_query_time == max(queries)

    def test_query_type_classification(self):
        """Test query type classification"""
        monitor = create_performance_monitor()

        test_cases = [
            ("SELECT * FROM users", QueryType.SELECT),
            ("INSERT INTO logs VALUES ('test')", QueryType.INSERT),
            ("UPDATE users SET name = 'John'", QueryType.UPDATE),
            ("DELETE FROM sessions", QueryType.DELETE),
            ("CREATE TABLE test (id INT)", QueryType.DDL),
            ("ALTER TABLE users ADD COLUMN age INT", QueryType.DDL),
            ("DROP TABLE temp", QueryType.DDL),
        ]

        for query, expected_type in test_cases:
            monitor.record_query(query, 0.1)

        stats = monitor.get_stats()
        assert stats.select_queries >= 1
        assert stats.insert_queries >= 1
        assert stats.update_queries >= 1
        assert stats.delete_queries >= 1
        assert stats.ddl_queries >= 3

    def test_concurrent_query_recording(self):
        """Test thread-safe query recording"""
        import threading

        monitor = create_performance_monitor()

        def record_queries():
            for i in range(10):
                monitor.record_query(f"SELECT * FROM table_{i}", 0.1)

        threads = [threading.Thread(target=record_queries) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        stats = monitor.get_stats()
        assert stats.total_queries == 50


class TestPerformanceThresholds:
    """Test PerformanceThresholds configuration"""

    def test_default_thresholds(self):
        """Test default threshold values"""
        thresholds = PerformanceThresholds()

        assert thresholds.slow_query_threshold == 1.0
        assert thresholds.very_slow_query_threshold == 5.0
        assert thresholds.error_rate_threshold == 0.05
        assert thresholds.connection_pool_usage_threshold == 0.8

    def test_custom_thresholds(self):
        """Test custom threshold values"""
        thresholds = PerformanceThresholds(
            slow_query_threshold=0.5,
            error_rate_threshold=0.1
        )

        assert thresholds.slow_query_threshold == 0.5
        assert thresholds.error_rate_threshold == 0.1


class TestOptimizationRecommendation:
    """Test OptimizationRecommendation dataclass"""

    def test_recommendation_creation(self):
        """Test creating optimization recommendation"""
        rec = OptimizationRecommendation(
            priority="high",
            category="index",
            title="Add Index",
            description="Add index on user_id column",
            impact="high",
            effort="low"
        )

        assert rec.priority == "high"
        assert rec.category == "index"
        assert rec.impact == "high"

    def test_recommendation_to_dict(self):
        """Test converting recommendation to dictionary"""
        rec = OptimizationRecommendation(
            priority="medium",
            category="query",
            title="Optimize Query",
            description="Rewrite query to use index",
            impact="medium",
            effort="medium",
            details={'table': 'users', 'column': 'email'}
        )

        data = rec.to_dict()
        assert data['priority'] == "medium"
        assert data['category'] == "query"
        assert 'details' in data
        assert data['details']['table'] == 'users'


def test_create_performance_monitor():
    """Test factory function"""
    monitor = create_performance_monitor(
        slow_query_threshold=0.5,
        enable_recommendations=True
    )

    assert monitor is not None
    assert monitor.thresholds.slow_query_threshold == 0.5
    assert monitor.enable_recommendations is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
