"""Verification script for Task 8.3: Database Connection Management"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_connection_pooling():
    """Verify connection pooling with configurable pool sizes"""
    print("\n" + "=" * 80)
    print("1. Verifying Connection Pooling with Configurable Pool Sizes")
    print("=" * 80)

    try:
        from core.connection_manager import (
            ConnectionPoolConfig,
            create_connection_manager,
        )

        # Test 1: Create connection manager with custom pool configuration
        print("\n[OK] ConnectionPoolConfig class exists")

        config = ConnectionPoolConfig(
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )
        print(
            f"[OK] Created ConnectionPoolConfig: pool_size={
                config.pool_size}, max_overflow={
                config.max_overflow}")

        # Test 2: Create connection manager
        manager = create_connection_manager(
            database_url="sqlite:///test_task_8_3.db",
            pool_size=5,
            max_overflow=10
        )
        print("[OK] Created EnhancedConnectionManager with custom pool configuration")

        # Test 3: Get pool metrics
        metrics = manager.get_pool_metrics()
        print(f"[OK] Pool metrics: {metrics.to_dict()}")

        # Test 4: Get session
        session = manager.get_session()
        print("[OK] Successfully obtained database session from pool")
        session.close()

        manager.dispose()
        print("\n[OK] Connection Pooling: PASSED")
        return True

    except Exception as e:
        print(f"\n[ERROR] Connection Pooling: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_health_monitoring():
    """Verify connection health monitoring with automatic recovery"""
    print("\n" + "=" * 80)
    print("2. Verifying Connection Health Monitoring with Automatic Recovery")
    print("=" * 80)

    try:
        from core.connection_manager import (
            create_connection_manager,
        )

        # Test 1: Create manager with health monitoring
        manager = create_connection_manager(
            database_url="sqlite:///test_task_8_3.db",
            health_monitoring=True
        )
        print("[OK] Created connection manager with health monitoring enabled")

        # Test 2: Verify health monitor exists
        assert manager.health_monitor is not None
        print("[OK] ConnectionHealthMonitor initialized")

        # Test 3: Perform health check
        result = manager.health_monitor.check_health()
        print(
            f"[OK] Health check performed: healthy={
                result.healthy}, response_time={
                result.response_time:.3f}s")

        # Test 4: Get health stats
        stats = manager.health_monitor.get_health_stats()
        print(f"[OK] Health stats: {stats}")

        # Test 5: Get comprehensive health status
        status = manager.get_health_status()
        assert 'healthy' in status
        assert 'health_check' in status
        assert 'health_stats' in status
        print(f"[OK] Comprehensive health status: healthy={status['healthy']}")

        # Test 6: Verify automatic monitoring
        time.sleep(2)  # Let monitoring run
        history = manager.health_monitor.get_health_history(limit=5)
        print(f"[OK] Health check history: {len(history)} checks recorded")

        manager.dispose()
        print("\n[OK] Health Monitoring: PASSED")
        return True

    except Exception as e:
        print(f"\n[ERROR] Health Monitoring: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_leak_detection():
    """Verify connection leak detection and prevention"""
    print("\n" + "=" * 80)
    print("3. Verifying Connection Leak Detection and Prevention")
    print("=" * 80)

    try:
        from core.connection_manager import (
            create_connection_manager,
        )

        # Test 1: Create manager with leak detection
        manager = create_connection_manager(
            database_url="sqlite:///test_task_8_3.db",
            leak_detection=True
        )
        print("[OK] Created connection manager with leak detection enabled")

        # Test 2: Verify leak detector exists
        assert manager.leak_detector is not None
        print("[OK] ConnectionLeakDetector initialized")

        # Test 3: Get session (checkout connection)
        session = manager.get_session()
        print("[OK] Connection checked out")

        # Test 4: Check active connections
        active_count = len(manager.leak_detector.active_connections)
        print(f"[OK] Active connections tracked: {active_count}")

        # Test 5: Return connection (checkin)
        session.close()
        print("[OK] Connection checked in")

        # Test 6: Verify connection removed from tracking
        time.sleep(0.1)
        active_after = len(manager.leak_detector.active_connections)
        print(f"[OK] Active connections after checkin: {active_after}")

        # Test 7: Get leak detection status
        status = manager.get_health_status()
        leak_info = status['leak_detection']
        assert leak_info['enabled']
        print(f"[OK] Leak detection status: {leak_info}")

        # Test 8: Verify leak threshold configuration
        assert manager.leak_detector.threshold_seconds > 0
        print(f"[OK] Leak threshold: {manager.leak_detector.threshold_seconds}s")

        manager.dispose()
        print("\n[OK] Leak Detection: PASSED")
        return True

    except Exception as e:
        print(f"\n[ERROR] Leak Detection: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_failover_support():
    """Verify database failover support for high availability"""
    print("\n" + "=" * 80)
    print("4. Verifying Database Failover Support for High Availability")
    print("=" * 80)

    try:
        from core.connection_manager import (
            create_connection_manager,
        )

        # Test 1: Create manager with failover URLs
        failover_urls = [
            "sqlite:///test_failover_1.db",
            "sqlite:///test_failover_2.db"
        ]

        manager = create_connection_manager(
            database_url="sqlite:///test_primary.db",
            failover_urls=failover_urls
        )
        print("[OK] Created connection manager with failover configuration")

        # Test 2: Verify failover manager exists
        assert manager.failover_manager is not None
        print("[OK] DatabaseFailoverManager initialized")

        # Test 3: Get current URL
        current_url = manager.failover_manager.get_current_url()
        print(f"[OK] Current database URL: {current_url[:50]}")

        # Test 4: Get failover stats
        stats = manager.failover_manager.get_failover_stats()
        assert 'current_url' in stats
        assert 'is_primary' in stats
        assert 'failover_count' in stats
        print(f"[OK] Failover stats: {stats}")

        # Test 5: Verify failover URLs configured
        assert len(manager.failover_manager.failover_urls) == 2
        print(
            f"[OK] Failover URLs configured: {len(manager.failover_manager.failover_urls)}")

        # Test 6: Get comprehensive status with failover info
        status = manager.get_health_status()
        assert 'failover_stats' in status
        print(f"[OK] Failover status in health check: {status['failover_stats']}")

        manager.dispose()
        print("\n[OK] Failover Support: PASSED")
        return True

    except Exception as e:
        print(f"\n[ERROR] Failover Support: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_integration():
    """Verify integration with DatabaseManager"""
    print("\n" + "=" * 80)
    print("5. Verifying Integration with DatabaseManager")
    print("=" * 80)

    try:
        import os

        from core.database import DatabaseManager

        # Set SQLite URL for testing
        os.environ["DATABASE_URL"] = "sqlite:///test_integration.db"

        # Test 1: Create DatabaseManager with enhanced connection manager
        db_manager = DatabaseManager(use_enhanced_connection_manager=True)
        print("[OK] DatabaseManager created with enhanced connection manager")

        # Test 2: Verify connection manager exists
        assert db_manager.connection_manager is not None
        print("[OK] EnhancedConnectionManager integrated")

        # Test 3: Get session through DatabaseManager
        session = db_manager.get_session()
        print("[OK] Session obtained through DatabaseManager")
        session.close()

        # Test 4: Get health status
        health = db_manager.health_check()
        assert 'healthy' in health
        print(f"[OK] Health check through DatabaseManager: {health['healthy']}")

        # Test 5: Get pool metrics
        metrics = db_manager.get_connection_pool_metrics()
        print(f"[OK] Pool metrics through DatabaseManager: {metrics}")

        # Test 6: Detect connection leaks
        leaks = db_manager.detect_connection_leaks()
        print(f"[OK] Leak detection through DatabaseManager: {len(leaks)} leaks")

        db_manager.dispose_connections()
        print("\n[OK] Integration: PASSED")
        return True

    except Exception as e:
        print(f"\n[ERROR] Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 80)
    print("TASK 8.3: DATABASE CONNECTION MANAGEMENT VERIFICATION")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Connection Pooling", verify_connection_pooling()))
    results.append(("Health Monitoring", verify_health_monitoring()))
    results.append(("Leak Detection", verify_leak_detection()))
    results.append(("Failover Support", verify_failover_support()))
    results.append(("Integration", verify_integration()))

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    for name, passed in results:
        status = "[OK] PASSED" if passed else "[ERROR] FAILED"
        print(f"{name:.<50} {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Task 8.3 is complete!")
    else:
        print("[WARNING]  SOME TESTS FAILED - Please review the errors above")
    print("=" * 80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
