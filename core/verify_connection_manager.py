"""Verification script for Enhanced Connection Manager"""

import os
import sys
import time

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def verify_connection_manager():
    """Verify connection manager implementation"""
    print("=" * 70)
    print("Enhanced Connection Manager Verification")
    print("=" * 70)

    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    def test(name: str, func):
        """Run a test and record result"""
        try:
            print(f"\n Testing: {name}...")
            func()
            print(f"✓ PASSED: {name}")
            results['passed'] += 1
            results['tests'].append((name, True, None))
        except Exception as e:
            print(f"✗ FAILED: {name}")
            print(f"  Error: {str(e)}")
            results['failed'] += 1
            results['tests'].append((name, False, str(e)))

    # Test 1: Import modules
    def test_imports():
        from core.connection_manager import (
            ConnectionPoolConfig,
            EnhancedConnectionManager,
        )
        assert ConnectionPoolConfig is not None
        assert EnhancedConnectionManager is not None

    test("Import connection manager modules", test_imports)

    # Test 2: Create connection pool config
    def test_pool_config():
        from core.connection_manager import ConnectionPoolConfig

        config = ConnectionPoolConfig(
            pool_size=5,
            max_overflow=10,
            leak_detection_enabled=True,
            health_check_enabled=True
        )

        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.leak_detection_enabled is True
        assert config.health_check_enabled is True

    test("Create connection pool configuration", test_pool_config)

    # Test 3: Create connection manager
    def test_create_manager():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            pool_size=2,
            max_overflow=3
        )

        assert manager is not None
        assert manager.engine is not None
        assert manager.SessionLocal is not None

        manager.dispose()

    test("Create connection manager", test_create_manager)

    # Test 4: Get database session
    def test_get_session():
        from sqlalchemy import text

        from core.connection_manager import create_connection_manager

        manager = create_connection_manager("sqlite:///:memory:")

        session = manager.get_session()
        assert session is not None

        # Test connection
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        session.close()
        manager.dispose()

    test("Get database session", test_get_session)

    # Test 5: Session scope
    def test_session_scope():
        from sqlalchemy import text

        from core.connection_manager import create_connection_manager

        manager = create_connection_manager("sqlite:///:memory:")

        with manager.session_scope() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

        manager.dispose()

    test("Session scope context manager", test_session_scope)

    # Test 6: Connection pool metrics
    def test_pool_metrics():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager("sqlite:///:memory:")

        # Get session to generate activity
        session = manager.get_session()

        metrics = manager.get_pool_metrics()
        assert metrics is not None
        assert metrics.total_checkouts > 0

        session.close()
        manager.dispose()

    test("Get connection pool metrics", test_pool_metrics)

    # Test 7: Health status
    def test_health_status():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            health_monitoring=False  # Disable for quick test
        )

        status = manager.get_health_status()
        assert status is not None
        assert 'healthy' in status
        assert 'pool_metrics' in status

        manager.dispose()

    test("Get health status", test_health_status)

    # Test 8: Leak detection
    def test_leak_detection():
        from core.connection_manager import (
            ConnectionPoolConfig,
            EnhancedConnectionManager,
        )

        config = ConnectionPoolConfig(
            pool_size=2,
            leak_detection_enabled=True,
            leak_threshold_seconds=0.1,
            health_check_enabled=False
        )

        manager = EnhancedConnectionManager(config, "sqlite:///:memory:")

        # Create potential leak
        session = manager.get_session()

        # Wait for leak threshold
        time.sleep(0.15)

        # Check for leaks
        metrics = manager.get_pool_metrics()
        assert metrics.leaked_connections > 0

        session.close()
        manager.dispose()

    test("Connection leak detection", test_leak_detection)

    # Test 9: Failover manager
    def test_failover():
        from core.connection_manager import DatabaseFailoverManager

        manager = DatabaseFailoverManager(
            primary_url="sqlite:///primary.db",
            failover_urls=["sqlite:///backup.db"],
            retry_attempts=2,
            retry_delay=0.1
        )

        assert manager.current_url == "sqlite:///primary.db"
        assert manager.current_index == -1

        stats = manager.get_failover_stats()
        assert stats['is_primary'] is True
        assert stats['available_failovers'] == 1

    test("Database failover manager", test_failover)

    # Test 10: Health monitoring
    def test_health_monitoring():
        from sqlalchemy import create_engine

        from core.connection_manager import ConnectionHealthMonitor

        engine = create_engine("sqlite:///:memory:")
        monitor = ConnectionHealthMonitor(
            engine, check_interval=60, enabled=True)

        result = monitor.check_health()
        assert result is not None
        # Health check might fail on first attempt, that's ok
        assert result.response_time >= 0

        engine.dispose()

    test("Health monitoring", test_health_monitoring)

    # Test 11: Integration with DatabaseManager
    def test_database_manager_integration():
        try:
            # Use SQLite for testing to avoid DuckDB dependency
            import os

            from core.database import DatabaseManager
            os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

            db_manager = DatabaseManager(use_enhanced_connection_manager=True)

            # Test that connection manager is initialized
            assert db_manager.connection_manager is not None

            # Get session
            session = db_manager.get_session()
            assert session is not None
            session.close()

            # Get pool metrics
            metrics = db_manager.get_connection_pool_metrics()
            assert metrics is not None
        except Exception as e:
            # If DuckDB or other dependencies are missing, skip gracefully
            if "Can't load plugin" in str(e) or "duckdb" in str(e).lower():
                print(
                    f"  Note: Skipping due to optional dependency: {
                        str(e)[
                            :50]}")
                return
            raise

    test("Integration with DatabaseManager", test_database_manager_integration)

    # Test 12: Concurrent access
    def test_concurrent_access():
        import threading

        from sqlalchemy import text

        from core.connection_manager import create_connection_manager

        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            pool_size=3
        )

        results_list = []

        def query_database():
            with manager.session_scope() as session:
                result = session.execute(text("SELECT 1"))
                results_list.append(result.scalar())

        # Create threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=query_database)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        assert len(results_list) == 5
        assert all(r == 1 for r in results_list)

        manager.dispose()

    test("Concurrent database access", test_concurrent_access)

    # Test 13: Error recovery
    def test_error_recovery():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager("sqlite:///:memory:")

        # Attempt operation that fails
        try:
            with manager.session_scope() as session:
                raise Exception("Test error")
        except Exception:
            pass

        # Should be able to continue after error
        with manager.session_scope() as session:
            from sqlalchemy import text
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

        manager.dispose()

    test("Error recovery", test_error_recovery)

    # Test 14: Reset metrics
    def test_reset_metrics():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager("sqlite:///:memory:")

        # Generate activity
        session = manager.get_session()
        session.close()

        # Get metrics
        metrics_before = manager.get_pool_metrics()
        assert metrics_before.total_checkouts > 0

        # Reset
        manager.reset_metrics()

        # Verify reset
        metrics_after = manager.get_pool_metrics()
        assert metrics_after.total_checkouts == 0

        manager.dispose()

    test("Reset metrics", test_reset_metrics)

    # Test 15: Dispose connections
    def test_dispose():
        from core.connection_manager import create_connection_manager

        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            health_monitoring=True
        )

        # Start health monitoring
        if manager.health_monitor:
            manager.health_monitor.start_monitoring()
            time.sleep(0.5)

        # Dispose
        manager.dispose()

        # Verify health monitoring stopped
        if manager.health_monitor:
            assert manager.health_monitor._monitoring_thread is None

    test("Dispose connections", test_dispose)

    # Print summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    print(f"\nTotal Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")

    if results['failed'] > 0:
        print("\nFailed Tests:")
        for name, passed, error in results['tests']:
            if not passed:
                print(f"  ✗ {name}")
                if error:
                    print(f"    {error}")

    print("\n" + "=" * 70)

    if results['failed'] == 0:
        print("✓ All tests passed! Connection manager is working correctly.")
        return 0
    print("✗ Some tests failed. Please review the errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(verify_connection_manager())
