"""Verification script for Database Performance Monitoring System"""

from core.db_performance_monitor import create_performance_monitor


def verify_basic_functionality():
    """Verify basic monitoring functionality"""
    print("\n" + "=" * 60)
    print("Verifying Basic Functionality")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Test query recording
    monitor.record_query("SELECT * FROM users", 0.1)
    monitor.record_query("INSERT INTO logs VALUES ('test')", 0.05)
    monitor.record_query("UPDATE users SET name = 'John'", 0.08)

    stats = monitor.get_stats()

    assert stats.total_queries == 3, "Query count mismatch"
    assert stats.select_queries == 1, "SELECT count mismatch"
    assert stats.insert_queries == 1, "INSERT count mismatch"
    assert stats.update_queries == 1, "UPDATE count mismatch"

    print("✅ Basic query recording works")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Average Query Time: {stats.avg_query_time:.3f}s")

    return True


def verify_slow_query_detection():
    """Verify slow query detection"""
    print("\n" + "=" * 60)
    print("Verifying Slow Query Detection")
    print("=" * 60)

    monitor = create_performance_monitor(slow_query_threshold=0.5)

    # Fast queries
    for i in range(5):
        monitor.record_query(f"SELECT * FROM users WHERE id = {i}", 0.1)

    # Slow queries
    for i in range(3):
        monitor.record_query(f"SELECT * FROM large_table_{i}", 0.8)

    stats = monitor.get_stats()
    slow_queries = monitor.get_slow_queries()

    assert stats.slow_queries == 3, "Slow query count mismatch"
    assert len(slow_queries) == 3, "Slow query list mismatch"

    print("✅ Slow query detection works")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Slow Queries: {stats.slow_queries}")
    print(
        f"   Slow Query Rate: {
            stats.slow_queries /
            stats.total_queries:.1%}")

    return True


def verify_error_tracking():
    """Verify error tracking"""
    print("\n" + "=" * 60)
    print("Verifying Error Tracking")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Successful queries
    for i in range(7):
        monitor.record_query(f"SELECT * FROM users WHERE id = {i}", 0.1)

    # Failed queries
    for i in range(3):
        monitor.record_query(
            f"SELECT * FROM invalid_table_{i}",
            0.1,
            error=Exception("Table does not exist")
        )

    stats = monitor.get_stats()

    assert stats.total_queries == 10, "Total query count mismatch"
    assert stats.failed_queries == 3, "Failed query count mismatch"
    assert abs(stats.error_rate - 0.3) < 0.01, "Error rate mismatch"

    print("✅ Error tracking works")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Failed Queries: {stats.failed_queries}")
    print(f"   Error Rate: {stats.error_rate:.1%}")

    return True


def verify_connection_monitoring():
    """Verify connection pool monitoring"""
    print("\n" + "=" * 60)
    print("Verifying Connection Pool Monitoring")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Create connections
    for i in range(5):
        monitor.record_connection_event("create", f"conn_{i}")

    # Checkout connections
    for i in range(3):
        monitor.record_connection_event("checkout", f"conn_{i}")

    # Update pool metrics
    monitor.update_pool_metrics(
        pool_size=5,
        checked_out=3,
        checked_in=2,
        overflow=0
    )

    stats = monitor.get_stats()

    assert stats.total_connections == 5, "Connection count mismatch"
    assert stats.active_connections == 3, "Active connection count mismatch"
    assert stats.idle_connections == 2, "Idle connection count mismatch"
    assert abs(stats.connection_pool_usage - 0.6) < 0.01, "Pool usage mismatch"

    print("✅ Connection monitoring works")
    print(f"   Total Connections: {stats.total_connections}")
    print(f"   Active: {stats.active_connections}")
    print(f"   Idle: {stats.idle_connections}")
    print(f"   Pool Usage: {stats.connection_pool_usage:.1%}")

    return True


def verify_alert_system():
    """Verify alert system"""
    print("\n" + "=" * 60)
    print("Verifying Alert System")
    print("=" * 60)

    monitor = create_performance_monitor(slow_query_threshold=0.5)

    alert_count = {'count': 0}

    def test_callback(alert):
        alert_count['count'] += 1

    monitor.register_alert_callback(test_callback)

    # Trigger slow query alert
    monitor.record_query("SELECT * FROM large_table", 0.8)

    # Trigger very slow query alert
    monitor.record_query("SELECT * FROM huge_table", 6.0)

    alerts = monitor.get_alerts()

    assert len(alerts) > 0, "No alerts generated"
    assert alert_count['count'] > 0, "Callback not called"

    print("✅ Alert system works")
    print(f"   Total Alerts: {len(alerts)}")
    print(f"   Callback Invocations: {alert_count['count']}")

    for alert in alerts[:3]:
        print(f"   - [{alert.severity.value}] {alert.message}")

    return True


def verify_query_analysis():
    """Verify query analysis features"""
    print("\n" + "=" * 60)
    print("Verifying Query Analysis")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Record various queries
    queries = [
        ("SELECT * FROM users", 0.1),
        ("SELECT * FROM users WHERE id = 1", 0.15),
        ("SELECT * FROM orders", 0.2),
        ("INSERT INTO logs VALUES ('test')", 0.05),
        ("UPDATE users SET name = 'John'", 0.08),
        ("DELETE FROM sessions WHERE expired = true", 0.06),
    ]

    for query, duration in queries:
        monitor.record_query(query, duration)

    # Get stats by type
    stats_by_type = monitor.get_query_stats_by_type()

    assert 'SELECT' in stats_by_type, "SELECT stats missing"
    assert 'INSERT' in stats_by_type, "INSERT stats missing"
    assert 'UPDATE' in stats_by_type, "UPDATE stats missing"
    assert 'DELETE' in stats_by_type, "DELETE stats missing"

    # Get stats by table
    stats_by_table = monitor.get_query_stats_by_table()

    assert 'users' in stats_by_table, "users table stats missing"
    assert 'orders' in stats_by_table, "orders table stats missing"

    print("✅ Query analysis works")
    print("\n   Query Stats by Type:")
    for query_type, stats in stats_by_type.items():
        print(f"      {query_type}: {stats['count']} queries, "
              f"avg {stats['avg_duration']:.3f}s")

    print("\n   Query Stats by Table:")
    for table, count in stats_by_table.items():
        print(f"      {table}: {count} queries")

    return True


def verify_recommendations():
    """Verify optimization recommendations"""
    print("\n" + "=" * 60)
    print("Verifying Optimization Recommendations")
    print("=" * 60)

    monitor = create_performance_monitor(slow_query_threshold=0.3)

    # Create workload with issues
    # Many slow SELECT queries
    for i in range(15):
        monitor.record_query(
            f"SELECT * FROM large_table WHERE col_{i} = 'value'", 0.8)

    # Some fast queries
    for i in range(10):
        monitor.record_query(f"SELECT * FROM users WHERE id = {i}", 0.05)

    # Some errors
    for i in range(3):
        monitor.record_query(
            "SELECT * FROM invalid",
            0.1,
            error=Exception("Error")
        )

    # High pool usage
    monitor.update_pool_metrics(
        pool_size=10,
        checked_out=9,
        checked_in=1,
        overflow=2
    )

    recommendations = monitor.get_recommendations(force_refresh=True)

    assert len(recommendations) > 0, "No recommendations generated"

    print("✅ Optimization recommendations work")
    print(f"   Total Recommendations: {len(recommendations)}")

    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n   {i}. [{rec.priority.upper()}] {rec.title}")
        print(f"      Category: {rec.category}")
        print(f"      Impact: {rec.impact} | Effort: {rec.effort}")

    return True


def verify_stats_reset():
    """Verify statistics reset"""
    print("\n" + "=" * 60)
    print("Verifying Statistics Reset")
    print("=" * 60)

    monitor = create_performance_monitor()

    # Record some queries
    for i in range(10):
        monitor.record_query(f"SELECT * FROM table_{i}", 0.1)

    stats_before = monitor.get_stats()
    assert stats_before.total_queries == 10, "Initial query count wrong"

    # Reset
    monitor.reset_stats()

    stats_after = monitor.get_stats()
    assert stats_after.total_queries == 0, "Stats not reset"
    assert stats_after.total_query_time == 0.0, "Query time not reset"

    print("✅ Statistics reset works")
    print(f"   Queries Before Reset: {stats_before.total_queries}")
    print(f"   Queries After Reset: {stats_after.total_queries}")

    return True


def verify_thread_safety():
    """Verify thread-safe operations"""
    print("\n" + "=" * 60)
    print("Verifying Thread Safety")
    print("=" * 60)

    import threading

    monitor = create_performance_monitor()

    def record_queries():
        for i in range(20):
            monitor.record_query(f"SELECT * FROM table_{i}", 0.1)

    threads = [threading.Thread(target=record_queries) for _ in range(5)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    stats = monitor.get_stats()

    assert stats.total_queries == 100, "Thread-safe query count mismatch"

    print("✅ Thread safety works")
    print(f"   Queries from 5 threads: {stats.total_queries}")

    return True


def run_all_verifications():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("DATABASE PERFORMANCE MONITORING SYSTEM VERIFICATION")
    print("=" * 70)

    tests = [
        ("Basic Functionality", verify_basic_functionality),
        ("Slow Query Detection", verify_slow_query_detection),
        ("Error Tracking", verify_error_tracking),
        ("Connection Monitoring", verify_connection_monitoring),
        ("Alert System", verify_alert_system),
        ("Query Analysis", verify_query_analysis),
        ("Optimization Recommendations", verify_recommendations),
        ("Statistics Reset", verify_stats_reset),
        ("Thread Safety", verify_thread_safety),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ {test_name} failed: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All verifications passed!")
        print("=" * 70)
        return True
    print("⚠️  Some verifications failed")
    print("=" * 70)
    return False


if __name__ == "__main__":
    success = run_all_verifications()
    exit(0 if success else 1)
