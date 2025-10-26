"""Example usage of Enhanced Connection Manager"""

import time
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from core.connection_manager import (
    ConnectionPoolConfig,
    EnhancedConnectionManager,
    create_connection_manager,
)
from core.database import Base, get_db_manager


# Example model
class User(Base):
    """Example user model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def example_basic_usage():
    """Example: Basic connection manager usage"""
    print("\n=== Basic Connection Manager Usage ===\n")

    # Create connection manager with defaults
    manager = create_connection_manager(
        database_url="sqlite:///example.db",
        pool_size=5,
        max_overflow=10
    )

    # Create tables
    Base.metadata.create_all(bind=manager.engine)

    # Use session scope for operations
    with manager.session_scope() as session:
        user = User(name="John Doe", email="john@example.com")
        session.add(user)

    print("✓ User created successfully")

    # Query data
    with manager.session_scope() as session:
        users = session.query(User).all()
        print(f"✓ Found {len(users)} users")
        for user in users:
            print(f"  - {user.name} ({user.email})")

    # Clean up
    manager.dispose()
    print("\n✓ Connection manager disposed")


def example_health_monitoring():
    """Example: Health monitoring"""
    print("\n=== Health Monitoring ===\n")

    # Create manager with health monitoring
    manager = create_connection_manager(
        database_url="sqlite:///example.db",
        health_monitoring=True
    )

    # Wait for some health checks
    print("Waiting for health checks...")
    time.sleep(3)

    # Get health status
    status = manager.get_health_status()
    print(f"\n✓ Database healthy: {status['healthy']}")

    if status.get('health_stats'):
        stats = status['health_stats']
        print(f"✓ Total health checks: {stats['total_checks']}")
        print(f"✓ Success rate: {stats['success_rate']:.1f}%")
        print(f"✓ Avg response time: {stats['avg_response_time']:.3f}s")

    # Get last health check
    if manager.health_monitor:
        last_check = manager.health_monitor.get_last_check()
        if last_check:
            print(f"\n✓ Last check at: {last_check.timestamp}")
            print(f"✓ Response time: {last_check.response_time:.3f}s")

    manager.dispose()


def example_connection_pool_metrics():
    """Example: Connection pool metrics"""
    print("\n=== Connection Pool Metrics ===\n")

    manager = create_connection_manager(
        database_url="sqlite:///example.db",
        pool_size=3,
        max_overflow=2
    )

    Base.metadata.create_all(bind=manager.engine)

    # Generate some activity
    sessions = []
    for i in range(4):
        session = manager.get_session()
        sessions.append(session)
        print(f"✓ Checked out session {i + 1}")

    # Get pool metrics
    metrics = manager.get_pool_metrics()
    print("\n✓ Pool metrics:")
    print(f"  - Pool size: {metrics.size}")
    print(f"  - Checked out: {metrics.checked_out}")
    print(f"  - Checked in: {metrics.checked_in}")
    print(f"  - Overflow: {metrics.overflow}")
    print(f"  - Total checkouts: {metrics.total_checkouts}")
    print(f"  - Utilization: {metrics.to_dict()['utilization']}")

    # Close sessions
    for session in sessions:
        session.close()

    # Get updated metrics
    metrics = manager.get_pool_metrics()
    print("\n✓ After closing sessions:")
    print(f"  - Checked out: {metrics.checked_out}")
    print(f"  - Checked in: {metrics.checked_in}")

    manager.dispose()


def example_leak_detection():
    """Example: Connection leak detection"""
    print("\n=== Connection Leak Detection ===\n")

    # Create manager with short leak threshold for demo
    config = ConnectionPoolConfig(
        pool_size=2,
        leak_detection_enabled=True,
        leak_threshold_seconds=2.0,  # 2 seconds for demo
        health_check_enabled=False
    )

    manager = EnhancedConnectionManager(config, "sqlite:///example.db")

    # Create a potential leak (don't close session)
    print("Creating session without closing (simulating leak)...")
    leaked_session = manager.get_session()

    # Wait for leak threshold
    print("Waiting for leak detection threshold...")
    time.sleep(2.5)

    # Check for leaks
    metrics = manager.get_pool_metrics()
    print(f"\n✓ Leaked connections detected: {metrics.leaked_connections}")

    if manager.leak_detector:
        leaked = manager.leak_detector.detect_leaks()
        for leak in leaked:
            print("\n✓ Leak details:")
            print(f"  - Connection ID: {leak.connection_id}")
            print(f"  - Duration: {leak.duration:.1f}s")
            print(f"  - Thread: {leak.checked_out_by}")

    # Clean up
    leaked_session.close()
    manager.dispose()


def example_failover():
    """Example: Database failover"""
    print("\n=== Database Failover ===\n")

    # Create manager with failover URLs
    manager = create_connection_manager(
        database_url="sqlite:///primary.db",
        failover_urls=["sqlite:///backup1.db", "sqlite:///backup2.db"]
    )

    # Get failover status
    if manager.failover_manager:
        stats = manager.failover_manager.get_failover_stats()
        print("✓ Failover enabled: True")
        print(f"✓ Current database: {stats['current_url']}")
        print(f"✓ Is primary: {stats['is_primary']}")
        print(f"✓ Available failovers: {stats['available_failovers']}")
        print(f"✓ Failover count: {stats['failover_count']}")
    else:
        print("✗ Failover not enabled")

    manager.dispose()


def example_with_database_manager():
    """Example: Using enhanced connection manager with DatabaseManager"""
    print("\n=== Integration with DatabaseManager ===\n")

    # Get database manager (uses enhanced connection manager by default)
    db_manager = get_db_manager()

    # Create tables
    Base.metadata.create_all(bind=db_manager.engine)

    # Use database manager methods
    with db_manager.session_scope() as session:
        user = User(name="Jane Smith", email="jane@example.com")
        session.add(user)

    print("✓ User created via DatabaseManager")

    # Get connection pool metrics
    pool_metrics = db_manager.get_connection_pool_metrics()
    print("\n✓ Pool metrics:")
    for key, value in pool_metrics.items():
        print(f"  - {key}: {value}")

    # Check for leaks
    leaks = db_manager.detect_connection_leaks()
    print(f"\n✓ Connection leaks detected: {len(leaks)}")

    # Get health status
    health = db_manager.health_check()
    print(f"\n✓ Database healthy: {health['healthy']}")

    # Get failover status
    failover = db_manager.get_failover_status()
    print(f"\n✓ Failover enabled: {failover.get('failover_enabled', False)}")


def example_advanced_configuration():
    """Example: Advanced configuration"""
    print("\n=== Advanced Configuration ===\n")

    # Create custom configuration
    config = ConnectionPoolConfig(
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        leak_detection_enabled=True,
        leak_threshold_seconds=300.0,
        health_check_enabled=True,
        health_check_interval=60,
        failover_enabled=True,
        failover_urls=["sqlite:///backup.db"],
        failover_retry_attempts=3,
        failover_retry_delay=1.0
    )

    print("✓ Custom configuration created:")
    print(f"  - Pool size: {config.pool_size}")
    print(f"  - Max overflow: {config.max_overflow}")
    print(f"  - Pool timeout: {config.pool_timeout}s")
    print(f"  - Pool recycle: {config.pool_recycle}s")
    print(f"  - Leak detection: {config.leak_detection_enabled}")
    print(f"  - Leak threshold: {config.leak_threshold_seconds}s")
    print(f"  - Health monitoring: {config.health_check_enabled}")
    print(f"  - Health check interval: {config.health_check_interval}s")
    print(f"  - Failover enabled: {config.failover_enabled}")

    # Create manager with custom config
    manager = EnhancedConnectionManager(config, "sqlite:///example.db")

    print("\n✓ Connection manager created with custom configuration")

    manager.dispose()


def example_concurrent_access():
    """Example: Concurrent database access"""
    print("\n=== Concurrent Database Access ===\n")

    import threading

    manager = create_connection_manager(
        database_url="sqlite:///example.db",
        pool_size=5
    )

    Base.metadata.create_all(bind=manager.engine)

    def create_user(user_id: int):
        """Create user in separate thread"""
        with manager.session_scope() as session:
            user = User(
                name=f"User {user_id}",
                email=f"user{user_id}@example.com"
            )
            session.add(user)
        print(f"✓ Thread {user_id}: User created")

    # Create users concurrently
    threads = []
    for i in range(10):
        thread = threading.Thread(target=create_user, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Verify all users created
    with manager.session_scope() as session:
        count = session.query(User).count()
        print(f"\n✓ Total users created: {count}")

    # Get pool metrics
    metrics = manager.get_pool_metrics()
    print("\n✓ Pool metrics after concurrent access:")
    print(f"  - Total checkouts: {metrics.total_checkouts}")
    print(f"  - Avg checkout time: {metrics.avg_checkout_time:.3f}s")

    manager.dispose()


def main():
    """Run all examples"""
    print("=" * 60)
    print("Enhanced Connection Manager Examples")
    print("=" * 60)

    try:
        example_basic_usage()
        example_connection_pool_metrics()
        example_leak_detection()
        example_failover()
        example_health_monitoring()
        example_with_database_manager()
        example_advanced_configuration()
        example_concurrent_access()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
