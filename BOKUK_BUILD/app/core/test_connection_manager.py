"""Tests for Enhanced Connection Manager"""

import threading
import time
from datetime import datetime

import pytest
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base

from .connection_manager import (
    ConnectionHealthMonitor,
    ConnectionInfo,
    ConnectionLeakDetector,
    ConnectionPoolConfig,
    DatabaseFailoverManager,
    EnhancedConnectionManager,
    create_connection_manager,
)

Base = declarative_base()


class TestModel(Base):
    """Test model for database operations"""
    __tablename__ = 'test_models'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))


@pytest.fixture
def pool_config():
    """Create test pool configuration"""
    return ConnectionPoolConfig(
        pool_size=2,
        max_overflow=3,
        pool_timeout=5,
        leak_detection_enabled=True,
        leak_threshold_seconds=1.0,
        health_check_enabled=False,  # Disable for most tests
        health_check_interval=1
    )


@pytest.fixture
def test_db_url():
    """Test database URL"""
    return "sqlite:///:memory:"


@pytest.fixture
def connection_manager(pool_config, test_db_url):
    """Create test connection manager"""
    manager = EnhancedConnectionManager(pool_config, test_db_url)
    yield manager
    manager.dispose()


class TestConnectionPoolConfig:
    """Test ConnectionPoolConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = ConnectionPoolConfig()

        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.pool_pre_ping is True
        assert config.leak_detection_enabled is True
        assert config.health_check_enabled is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = ConnectionPoolConfig(
            pool_size=10,
            max_overflow=20,
            leak_threshold_seconds=600.0
        )

        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.leak_threshold_seconds == 600.0


class TestConnectionInfo:
    """Test ConnectionInfo"""

    def test_connection_info_creation(self):
        """Test creating connection info"""
        info = ConnectionInfo(
            connection_id="conn_123",
            checked_out_at=datetime.utcnow(),
            checked_out_by="MainThread",
            stack_trace="test stack trace"
        )

        assert info.connection_id == "conn_123"
        assert info.checked_out_by == "MainThread"
        assert info.duration == 0.0

    def test_is_leaked(self):
        """Test leak detection"""
        # Create connection checked out 2 seconds ago
        past_time = datetime.utcnow()
        info = ConnectionInfo(
            connection_id="conn_123",
            checked_out_at=past_time,
            checked_out_by="MainThread",
            stack_trace="test"
        )

        # Wait a bit
        time.sleep(0.1)

        # Should not be leaked with high threshold
        assert not info.is_leaked(10.0)

        # Should be leaked with low threshold
        assert info.is_leaked(0.05)


class TestConnectionLeakDetector:
    """Test ConnectionLeakDetector"""

    def test_track_checkout_checkin(self):
        """Test tracking checkout and checkin"""
        detector = ConnectionLeakDetector(threshold_seconds=1.0)

        # Track checkout
        detector.track_checkout("conn_1", "Thread-1", "stack trace")
        assert len(detector.active_connections) == 1

        # Track checkin
        detector.track_checkin("conn_1")
        assert len(detector.active_connections) == 0

    def test_detect_leaks(self):
        """Test leak detection"""
        detector = ConnectionLeakDetector(threshold_seconds=0.1)

        # Track checkout
        detector.track_checkout("conn_1", "Thread-1", "stack trace")

        # Wait for leak threshold
        time.sleep(0.15)

        # Detect leaks
        leaked = detector.detect_leaks()
        assert len(leaked) == 1
        assert leaked[0].connection_id == "conn_1"
        assert detector.get_leaked_count() == 1

    def test_reset(self):
        """Test resetting leak detector"""
        detector = ConnectionLeakDetector()

        detector.track_checkout("conn_1", "Thread-1", "stack")
        detector._leaked_count = 5

        detector.reset()

        assert len(detector.active_connections) == 0
        assert detector.get_leaked_count() == 0


class TestConnectionHealthMonitor:
    """Test ConnectionHealthMonitor"""

    def test_health_check_success(self):
        """Test successful health check"""
        engine = create_engine("sqlite:///:memory:")
        monitor = ConnectionHealthMonitor(
            engine, check_interval=60, enabled=True)

        result = monitor.check_health()

        assert result.healthy is True
        assert result.response_time > 0
        assert result.error is None

        engine.dispose()

    def test_health_check_failure(self):
        """Test failed health check"""
        # Create engine with invalid URL
        engine = create_engine(
            "postgresql://invalid:invalid@localhost:9999/invalid")
        monitor = ConnectionHealthMonitor(
            engine, check_interval=60, enabled=True)

        result = monitor.check_health()

        assert result.healthy is False
        assert result.error is not None

        engine.dispose()

    def test_health_history(self):
        """Test health check history"""
        engine = create_engine("sqlite:///:memory:")
        monitor = ConnectionHealthMonitor(
            engine, check_interval=60, enabled=True)

        # Perform multiple checks
        for _ in range(3):
            monitor.check_health()

        history = monitor.get_health_history(limit=10)
        assert len(history) == 3

        stats = monitor.get_health_stats()
        assert stats['total_checks'] == 3
        assert stats['healthy_checks'] == 3
        assert stats['success_rate'] == 100.0

        engine.dispose()

    def test_monitoring_lifecycle(self):
        """Test starting and stopping monitoring"""
        engine = create_engine("sqlite:///:memory:")
        monitor = ConnectionHealthMonitor(
            engine, check_interval=1, enabled=True)

        # Start monitoring
        monitor.start_monitoring()
        assert monitor._monitoring_thread is not None

        # Wait a bit for checks
        time.sleep(1.5)

        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor._monitoring_thread is None

        # Should have performed at least one check
        stats = monitor.get_health_stats()
        assert stats['total_checks'] > 0

        engine.dispose()


class TestDatabaseFailoverManager:
    """Test DatabaseFailoverManager"""

    def test_initialization(self):
        """Test failover manager initialization"""
        manager = DatabaseFailoverManager(
            primary_url="sqlite:///primary.db",
            failover_urls=["sqlite:///backup1.db", "sqlite:///backup2.db"],
            retry_attempts=3,
            retry_delay=0.5
        )

        assert manager.current_url == "sqlite:///primary.db"
        assert manager.current_index == -1
        assert len(manager.failover_urls) == 2

    def test_get_current_url(self):
        """Test getting current URL"""
        manager = DatabaseFailoverManager(
            primary_url="sqlite:///primary.db",
            failover_urls=["sqlite:///backup.db"]
        )

        assert manager.get_current_url() == "sqlite:///primary.db"

    def test_failover_stats(self):
        """Test failover statistics"""
        manager = DatabaseFailoverManager(
            primary_url="sqlite:///primary.db",
            failover_urls=["sqlite:///backup.db"]
        )

        stats = manager.get_failover_stats()

        assert stats['is_primary'] is True
        assert stats['failover_count'] == 0
        assert stats['available_failovers'] == 1


class TestEnhancedConnectionManager:
    """Test EnhancedConnectionManager"""

    def test_initialization(self, connection_manager):
        """Test connection manager initialization"""
        assert connection_manager.engine is not None
        assert connection_manager.SessionLocal is not None
        assert connection_manager.leak_detector is not None

    def test_get_session(self, connection_manager):
        """Test getting database session"""
        session = connection_manager.get_session()

        assert session is not None

        # Test connection
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        session.close()

    def test_session_scope(self, connection_manager):
        """Test session scope context manager"""
        # Create tables
        Base.metadata.create_all(bind=connection_manager.engine)

        # Use session scope
        with connection_manager.session_scope() as session:
            model = TestModel(name="test")
            session.add(model)

        # Verify data was committed
        with connection_manager.session_scope() as session:
            result = session.query(TestModel).filter_by(name="test").first()
            assert result is not None
            assert result.name == "test"

    def test_session_scope_rollback(self, connection_manager):
        """Test session scope rollback on error"""
        Base.metadata.create_all(bind=connection_manager.engine)

        # Attempt operation that fails
        with pytest.raises(Exception):
            with connection_manager.session_scope() as session:
                model = TestModel(name="test")
                session.add(model)
                raise Exception("Test error")

        # Verify data was not committed
        with connection_manager.session_scope() as session:
            count = session.query(TestModel).count()
            assert count == 0

    def test_get_pool_metrics(self, connection_manager):
        """Test getting pool metrics"""
        metrics = connection_manager.get_pool_metrics()

        assert metrics.size >= 0
        assert metrics.checked_in >= 0
        assert metrics.checked_out >= 0
        assert metrics.total_checkouts >= 0

    def test_get_health_status(self, connection_manager):
        """Test getting health status"""
        status = connection_manager.get_health_status()

        assert 'healthy' in status
        assert 'pool_metrics' in status
        assert 'leak_detection' in status

        assert status['leak_detection']['enabled'] is True

    def test_leak_detection(self, pool_config, test_db_url):
        """Test connection leak detection"""
        # Create manager with short leak threshold
        pool_config.leak_threshold_seconds = 0.1
        manager = EnhancedConnectionManager(pool_config, test_db_url)

        # Get session and don't close it
        session = manager.get_session()

        # Wait for leak threshold
        time.sleep(0.15)

        # Check for leaks
        metrics = manager.get_pool_metrics()
        assert metrics.leaked_connections > 0

        # Clean up
        session.close()
        manager.dispose()

    def test_concurrent_sessions(self, connection_manager):
        """Test concurrent session access"""
        Base.metadata.create_all(bind=connection_manager.engine)

        def create_record(name: str):
            with connection_manager.session_scope() as session:
                model = TestModel(name=name)
                session.add(model)

        # Create records concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=create_record, args=(
                    f"test_{i}",))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all records created
        with connection_manager.session_scope() as session:
            count = session.query(TestModel).count()
            assert count == 5

    def test_dispose(self, connection_manager):
        """Test disposing connection pool"""
        # Get a session first
        session = connection_manager.get_session()
        session.close()

        # Dispose
        connection_manager.dispose()

        # Health monitor should be stopped
        if connection_manager.health_monitor:
            assert connection_manager.health_monitor._monitoring_thread is None

    def test_reset_metrics(self, connection_manager):
        """Test resetting metrics"""
        # Generate some activity
        session = connection_manager.get_session()
        session.close()

        # Get initial metrics
        metrics_before = connection_manager.get_pool_metrics()
        assert metrics_before.total_checkouts > 0

        # Reset
        connection_manager.reset_metrics()

        # Verify reset
        metrics_after = connection_manager.get_pool_metrics()
        assert metrics_after.total_checkouts == 0


class TestCreateConnectionManager:
    """Test create_connection_manager helper function"""

    def test_create_with_defaults(self):
        """Test creating connection manager with defaults"""
        manager = create_connection_manager("sqlite:///:memory:")

        assert manager is not None
        assert manager.config.pool_size == 5
        assert manager.config.max_overflow == 10
        assert manager.config.leak_detection_enabled is True
        assert manager.config.health_check_enabled is True

        manager.dispose()

    def test_create_with_custom_params(self):
        """Test creating connection manager with custom parameters"""
        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            pool_size=10,
            max_overflow=20,
            leak_detection=False,
            health_monitoring=False
        )

        assert manager.config.pool_size == 10
        assert manager.config.max_overflow == 20
        assert manager.config.leak_detection_enabled is False
        assert manager.config.health_check_enabled is False

        manager.dispose()

    def test_create_with_failover(self):
        """Test creating connection manager with failover"""
        manager = create_connection_manager(
            database_url="sqlite:///primary.db",
            failover_urls=["sqlite:///backup.db"]
        )

        assert manager.config.failover_enabled is True
        assert len(manager.config.failover_urls) == 1
        assert manager.failover_manager is not None

        manager.dispose()


class TestIntegration:
    """Integration tests for connection management"""

    def test_full_lifecycle(self):
        """Test complete connection manager lifecycle"""
        # Create manager
        manager = create_connection_manager(
            database_url="sqlite:///:memory:",
            pool_size=2,
            max_overflow=3,
            leak_detection=True,
            health_monitoring=False
        )

        # Create tables
        Base.metadata.create_all(bind=manager.engine)

        # Perform operations
        with manager.session_scope() as session:
            for i in range(5):
                model = TestModel(name=f"test_{i}")
                session.add(model)

        # Verify data
        with manager.session_scope() as session:
            count = session.query(TestModel).count()
            assert count == 5

        # Check health
        status = manager.get_health_status()
        assert status['healthy'] is True

        # Get metrics
        metrics = manager.get_pool_metrics()
        assert metrics.total_checkouts > 0

        # Clean up
        manager.dispose()

    def test_error_recovery(self):
        """Test error recovery and retry logic"""
        manager = create_connection_manager("sqlite:///:memory:")

        Base.metadata.create_all(bind=manager.engine)

        # Simulate error and recovery
        try:
            with manager.session_scope() as session:
                model = TestModel(name="test")
                session.add(model)
                raise Exception("Simulated error")
        except Exception:
            pass

        # Should be able to continue after error
        with manager.session_scope() as session:
            model = TestModel(name="test2")
            session.add(model)

        # Verify only second record exists
        with manager.session_scope() as session:
            count = session.query(TestModel).count()
            assert count == 1

        manager.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
