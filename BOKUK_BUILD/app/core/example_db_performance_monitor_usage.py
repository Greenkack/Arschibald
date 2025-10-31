"""Example usage of Database Performance Monitoring System"""

import time

from core.db_performance_monitor import (
    DatabasePerformanceMonitor,
    PerformanceThresholds,
    create_performance_monitor,
)


def alert_callback(alert):
    """Callback function for performance alerts"""
    print(f"\n🚨 ALERT [{alert.severity.value.upper()}]: {alert.message}")
    print(f"   Metric: {alert.metric_name}")
    print(
        f"   Current: {
            alert.current_value}, Threshold: {
            alert.threshold_value}")
    if alert.details:
        print(f"   Details: {alert.details}")


def example_basic_usage():
    """Example: Basic performance monitoring"""
    print("=" * 60)
    print("Example 1: Basic Performance Monitoring")
    print("=" * 60)

    # Create monitor with default settings
    monitor = create_performance_monitor(
        slow_query_threshold=0.5,
        enable_recommendations=True
    )

    # Register alert callback
    monitor.register_alert_callback(alert_callback)

    # Simulate some queries
    queries = [
        ("SELECT * FROM users WHERE id = 1", 0.1),
        ("SELECT * FROM orders WHERE user_id = 1", 0.3),
        ("INSERT INTO logs (message) VALUES ('test')", 0.05),
        ("SELECT * FROM products WHERE category = 'electronics'", 0.8),  # Slow
        ("UPDATE users SET last_login = NOW() WHERE id = 1", 0.2),
        ("SELECT * FROM orders JOIN users ON orders.user_id = users.id", 1.5),  # Very slow
    ]

    print("\nRecording queries...")
    for query, duration in queries:
        monitor.record_query(
            query=query,
            duration=duration,
            rows_affected=1,
            connection_id="conn_1",
            user_id="user_123"
        )
        print(f"  ✓ Recorded: {query[:50]}... ({duration}s)")
        time.sleep(0.1)

    # Get statistics
    stats = monitor.get_stats()
    print("\n📊 Performance Statistics:")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Slow Queries: {stats.slow_queries}")
    print(f"   Very Slow Queries: {stats.very_slow_queries}")
    print(f"   Average Query Time: {stats.avg_query_time:.3f}s")
    print(f"   Error Rate: {stats.error_rate:.1%}")

    # Get slow queries
    slow_queries = monitor.get_slow_queries(limit=5)
    if slow_queries:
        print("\n🐌 Slow Queries:")
        for sq in slow_queries:
            print(f"   - {sq.query[:60]}... ({sq.duration:.2f}s)")

    # Get alerts
    alerts = monitor.get_alerts(limit=10)
    if alerts:
        print(f"\n🚨 Recent Alerts: {len(alerts)}")
        for alert in alerts[-3:]:
            print(f"   - [{alert.severity.value}] {alert.message}")


def example_custom_thresholds():
    """Example: Custom performance thresholds"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Performance Thresholds")
    print("=" * 60)

    # Create custom thresholds
    thresholds = PerformanceThresholds(
        slow_query_threshold=0.3,
        very_slow_query_threshold=1.0,
        error_rate_threshold=0.1,
        connection_pool_usage_threshold=0.7,
        avg_query_time_threshold=0.2
    )

    monitor = DatabasePerformanceMonitor(
        thresholds=thresholds,
        max_slow_queries=50,
        enable_recommendations=True
    )

    print("\n⚙️  Custom Thresholds:")
    print(f"   Slow Query: {thresholds.slow_query_threshold}s")
    print(f"   Very Slow Query: {thresholds.very_slow_query_threshold}s")
    print(f"   Error Rate: {thresholds.error_rate_threshold:.1%}")
    print(f"   Pool Usage: {thresholds.connection_pool_usage_threshold:.1%}")

    # Simulate queries with errors
    print("\nSimulating queries with errors...")
    for i in range(10):
        error = Exception("Connection timeout") if i % 3 == 0 else None
        monitor.record_query(
            query=f"SELECT * FROM table_{i}",
            duration=0.1 + (i * 0.05),
            error=error
        )

    stats = monitor.get_stats()
    print("\n📊 Statistics:")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Failed Queries: {stats.failed_queries}")
    print(f"   Error Rate: {stats.error_rate:.1%}")


def example_connection_monitoring():
    """Example: Connection pool monitoring"""
    print("\n" + "=" * 60)
    print("Example 3: Connection Pool Monitoring")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Simulate connection events
    print("\nSimulating connection pool events...")

    # Create connections
    for i in range(5):
        monitor.record_connection_event("create", f"conn_{i}")
        print(f"  ✓ Connection created: conn_{i}")

    # Checkout connections
    for i in range(4):
        monitor.record_connection_event("checkout", f"conn_{i}")
        print(f"  ✓ Connection checked out: conn_{i}")

    # Update pool metrics
    monitor.update_pool_metrics(
        pool_size=5,
        checked_out=4,
        checked_in=1,
        overflow=0
    )

    stats = monitor.get_stats()
    print("\n📊 Connection Statistics:")
    print(f"   Total Connections: {stats.total_connections}")
    print(f"   Active Connections: {stats.active_connections}")
    print(f"   Idle Connections: {stats.idle_connections}")
    print(f"   Pool Usage: {stats.connection_pool_usage:.1%}")

    # Checkin connections
    for i in range(2):
        monitor.record_connection_event("checkin", f"conn_{i}")
        print(f"  ✓ Connection checked in: conn_{i}")

    # Update pool metrics again
    monitor.update_pool_metrics(
        pool_size=5,
        checked_out=2,
        checked_in=3,
        overflow=0
    )

    stats = monitor.get_stats()
    print("\n📊 Updated Connection Statistics:")
    print(f"   Active Connections: {stats.active_connections}")
    print(f"   Idle Connections: {stats.idle_connections}")
    print(f"   Pool Usage: {stats.connection_pool_usage:.1%}")


def example_query_analysis():
    """Example: Query type and table analysis"""
    print("\n" + "=" * 60)
    print("Example 4: Query Analysis by Type and Table")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Simulate various query types
    queries = [
        ("SELECT * FROM users WHERE id = 1", 0.1),
        ("SELECT * FROM users WHERE email = 'test@example.com'", 0.2),
        ("SELECT * FROM orders WHERE user_id = 1", 0.15),
        ("INSERT INTO users (name, email) VALUES ('John', 'john@example.com')", 0.05),
        ("UPDATE users SET last_login = NOW() WHERE id = 1", 0.08),
        ("DELETE FROM sessions WHERE expired = true", 0.12),
        ("SELECT * FROM products WHERE category = 'electronics'", 0.3),
        ("INSERT INTO orders (user_id, total) VALUES (1, 99.99)", 0.06),
        ("UPDATE orders SET status = 'shipped' WHERE id = 1", 0.09),
        ("SELECT * FROM users JOIN orders ON users.id = orders.user_id", 0.5),
    ]

    print("\nRecording queries...")
    for query, duration in queries:
        monitor.record_query(query, duration)

    # Get query stats by type
    stats_by_type = monitor.get_query_stats_by_type()
    print("\n📊 Query Statistics by Type:")
    for query_type, stats in stats_by_type.items():
        print(f"\n   {query_type}:")
        print(f"      Count: {stats['count']}")
        print(f"      Avg Duration: {stats['avg_duration']:.3f}s")
        print(f"      Min Duration: {stats['min_duration']:.3f}s")
        print(f"      Max Duration: {stats['max_duration']:.3f}s")

    # Get query stats by table
    stats_by_table = monitor.get_query_stats_by_table(limit=10)
    print("\n📊 Query Counts by Table:")
    for table, count in stats_by_table.items():
        print(f"   {table}: {count} queries")


def example_optimization_recommendations():
    """Example: Performance optimization recommendations"""
    print("\n" + "=" * 60)
    print("Example 5: Optimization Recommendations")
    print("=" * 60)

    monitor = create_performance_monitor(slow_query_threshold=0.3)

    # Simulate workload with performance issues
    print("\nSimulating workload with performance issues...")

    # Many slow SELECT queries (missing indexes)
    for i in range(20):
        monitor.record_query(
            f"SELECT * FROM large_table WHERE column_{i} = 'value'",
            duration=0.8  # Slow
        )

    # Some fast queries
    for i in range(30):
        monitor.record_query(
            f"SELECT * FROM users WHERE id = {i}",
            duration=0.05
        )

    # Some failed queries
    for i in range(5):
        monitor.record_query(
            "SELECT * FROM invalid_table",
            duration=0.1,
            error=Exception("Table does not exist")
        )

    # High connection pool usage
    monitor.update_pool_metrics(
        pool_size=10,
        checked_out=9,
        checked_in=1,
        overflow=2
    )

    # Get recommendations
    recommendations = monitor.get_recommendations(force_refresh=True)

    print(f"\n💡 Optimization Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. [{rec.priority.upper()}] {rec.title}")
        print(f"      Category: {rec.category}")
        print(f"      Description: {rec.description}")
        print(f"      Impact: {rec.impact} | Effort: {rec.effort}")
        if rec.details:
            print(f"      Details: {rec.details}")


def example_real_time_monitoring():
    """Example: Real-time monitoring with alerts"""
    print("\n" + "=" * 60)
    print("Example 6: Real-time Monitoring with Alerts")
    print("=" * 60)

    monitor = create_performance_monitor(slow_query_threshold=0.2)

    # Register alert callback
    alert_count = {'count': 0}

    def counting_callback(alert):
        alert_count['count'] += 1
        print(f"\n   🚨 Alert #{alert_count['count']}: {alert.message}")

    monitor.register_alert_callback(counting_callback)

    print("\nMonitoring queries in real-time...")

    # Simulate real-time query stream
    query_stream = [
        ("SELECT * FROM users", 0.05, None),
        ("SELECT * FROM orders", 0.1, None),
        ("SELECT * FROM products", 0.5, None),  # Slow
        ("INSERT INTO logs", 0.03, None),
        ("SELECT * FROM large_table", 1.2, None),  # Very slow
        ("UPDATE users", 0.08, None),
        ("SELECT * FROM invalid", 0.1, Exception("Error")),  # Error
        ("DELETE FROM temp", 0.06, None),
    ]

    for query, duration, error in query_stream:
        monitor.record_query(query, duration, error=error)
        time.sleep(0.2)

    print("\n📊 Final Statistics:")
    stats = monitor.get_stats()
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Slow Queries: {stats.slow_queries}")
    print(f"   Failed Queries: {stats.failed_queries}")
    print(f"   Total Alerts: {alert_count['count']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("DATABASE PERFORMANCE MONITORING EXAMPLES")
    print("=" * 60)

    try:
        example_basic_usage()
        example_custom_thresholds()
        example_connection_monitoring()
        example_query_analysis()
        example_optimization_recommendations()
        example_real_time_monitoring()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
