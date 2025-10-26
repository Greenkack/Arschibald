"""Database Connection Management with Pooling, Health Monitoring, Leak Detection, and Failover"""

import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import DBAPIError, DisconnectionError, OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, Pool, QueuePool, StaticPool

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pooling"""
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # Recycle connections after 1 hour
    pool_pre_ping: bool = True  # Enable connection health checks
    echo_pool: bool = False

    # Leak detection
    leak_detection_enabled: bool = True
    leak_threshold_seconds: float = 300.0  # 5 minutes

    # Health monitoring
    health_check_interval: int = 60  # seconds
    health_check_enabled: bool = True

    # Failover
    failover_enabled: bool = False
    failover_urls: list[str] = field(default_factory=list)
    failover_retry_attempts: int = 3
    failover_retry_delay: float = 1.0


@dataclass
class ConnectionInfo:
    """Information about a database connection"""
    connection_id: str
    checked_out_at: datetime
    checked_out_by: str  # Thread name
    stack_trace: str
    duration: float = 0.0

    def is_leaked(self, threshold_seconds: float) -> bool:
        """Check if connection is potentially leaked"""
        self.duration = (
            datetime.utcnow() -
            self.checked_out_at).total_seconds()
        return self.duration > threshold_seconds


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    healthy: bool
    timestamp: datetime
    response_time: float
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PoolMetrics:
    """Connection pool metrics"""
    size: int = 0
    checked_in: int = 0
    checked_out: int = 0
    overflow: int = 0
    total_checkouts: int = 0
    total_connections_created: int = 0
    leaked_connections: int = 0
    failed_checkouts: int = 0
    avg_checkout_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'size': self.size,
            'checked_in': self.checked_in,
            'checked_out': self.checked_out,
            'overflow': self.overflow,
            'total_checkouts': self.total_checkouts,
            'total_connections_created': self.total_connections_created,
            'leaked_connections': self.leaked_connections,
            'failed_checkouts': self.failed_checkouts,
            'avg_checkout_time': self.avg_checkout_time,
            'utilization': f"{(self.checked_out / max(self.size, 1)) * 100:.1f}%"
        }


class ConnectionLeakDetector:
    """Detects and reports connection leaks"""

    def __init__(self, threshold_seconds: float = 300.0):
        self.threshold_seconds = threshold_seconds
        self.active_connections: dict[str, ConnectionInfo] = {}
        self._lock = threading.Lock()
        self._leaked_count = 0

    def track_checkout(
            self,
            connection_id: str,
            thread_name: str,
            stack_trace: str):
        """Track connection checkout"""
        with self._lock:
            self.active_connections[connection_id] = ConnectionInfo(
                connection_id=connection_id,
                checked_out_at=datetime.utcnow(),
                checked_out_by=thread_name,
                stack_trace=stack_trace
            )

    def track_checkin(self, connection_id: str):
        """Track connection checkin"""
        with self._lock:
            self.active_connections.pop(connection_id, None)

    def detect_leaks(self) -> list[ConnectionInfo]:
        """Detect potentially leaked connections"""
        leaked = []

        with self._lock:
            for conn_info in list(self.active_connections.values()):
                if conn_info.is_leaked(self.threshold_seconds):
                    leaked.append(conn_info)
                    self._leaked_count += 1

                    logger.warning(
                        "Potential connection leak detected",
                        connection_id=conn_info.connection_id,
                        duration=conn_info.duration,
                        thread=conn_info.checked_out_by,
                        stack_trace=conn_info.stack_trace[:500]
                    )

        return leaked

    def get_leaked_count(self) -> int:
        """Get total number of leaked connections detected"""
        return self._leaked_count

    def reset(self):
        """Reset leak detector"""
        with self._lock:
            self.active_connections.clear()
            self._leaked_count = 0


class ConnectionHealthMonitor:
    """Monitors connection health and performs automatic recovery"""

    def __init__(
        self,
        engine,
        check_interval: int = 60,
        enabled: bool = True
    ):
        self.engine = engine
        self.check_interval = check_interval
        self.enabled = enabled
        self._last_check: HealthCheckResult | None = None
        self._check_history: list[HealthCheckResult] = []
        self._max_history = 100
        self._monitoring_thread: threading.Thread | None = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.Lock()

    def start_monitoring(self):
        """Start background health monitoring"""
        if not self.enabled or self._monitoring_thread is not None:
            return

        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ConnectionHealthMonitor"
        )
        self._monitoring_thread.start()
        logger.info("Connection health monitoring started")

    def stop_monitoring(self):
        """Stop background health monitoring"""
        if self._monitoring_thread is None:
            return

        self._stop_monitoring.set()
        self._monitoring_thread.join(timeout=5)
        self._monitoring_thread = None
        logger.info("Connection health monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                result = self.check_health()

                if not result.healthy:
                    logger.error(
                        "Database health check failed",
                        error=result.error,
                        response_time=result.response_time
                    )
                    self._attempt_recovery()

            except Exception as e:
                logger.error("Error in health monitoring loop", error=str(e))

            self._stop_monitoring.wait(self.check_interval)

    def check_health(self) -> HealthCheckResult:
        """Perform health check on database connection"""
        start_time = time.time()

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.close()

            response_time = time.time() - start_time

            # Get pool status
            pool_status = {}
            if hasattr(self.engine.pool, 'size'):
                pool_status = {
                    'size': self.engine.pool.size(),
                    'checked_in': self.engine.pool.checkedin(),
                    'checked_out': self.engine.pool.size() - self.engine.pool.checkedin(),
                    'overflow': self.engine.pool.overflow()}

            result = HealthCheckResult(
                healthy=True,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                details=pool_status
            )

        except Exception as e:
            response_time = time.time() - start_time
            result = HealthCheckResult(
                healthy=False,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                error=str(e)
            )

        with self._lock:
            self._last_check = result
            self._check_history.append(result)

            # Keep only recent history
            if len(self._check_history) > self._max_history:
                self._check_history = self._check_history[-self._max_history:]

        return result

    def _attempt_recovery(self):
        """Attempt to recover from connection issues"""
        try:
            logger.info("Attempting connection recovery")

            # Dispose of all connections in pool
            self.engine.dispose()

            # Wait a bit before checking again
            time.sleep(2)

            # Try to establish new connection
            result = self.check_health()

            if result.healthy:
                logger.info("Connection recovery successful")
            else:
                logger.error("Connection recovery failed", error=result.error)

        except Exception as e:
            logger.error("Error during connection recovery", error=str(e))

    def get_last_check(self) -> HealthCheckResult | None:
        """Get last health check result"""
        with self._lock:
            return self._last_check

    def get_health_history(self, limit: int = 10) -> list[HealthCheckResult]:
        """Get recent health check history"""
        with self._lock:
            return self._check_history[-limit:]

    def get_health_stats(self) -> dict[str, Any]:
        """Get health statistics"""
        with self._lock:
            if not self._check_history:
                return {
                    'total_checks': 0,
                    'healthy_checks': 0,
                    'failed_checks': 0,
                    'success_rate': 0.0,
                    'avg_response_time': 0.0
                }

            total = len(self._check_history)
            healthy = sum(1 for r in self._check_history if r.healthy)
            failed = total - healthy
            avg_response = sum(
                r.response_time for r in self._check_history) / total

            return {
                'total_checks': total,
                'healthy_checks': healthy,
                'failed_checks': failed,
                'success_rate': (healthy / total) * 100,
                'avg_response_time': avg_response
            }


class DatabaseFailoverManager:
    """Manages database failover to backup connections"""

    def __init__(
        self,
        primary_url: str,
        failover_urls: list[str],
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        self.primary_url = primary_url
        self.failover_urls = failover_urls
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.current_url = primary_url
        self.current_index = -1  # -1 means primary
        self._failover_count = 0
        self._lock = threading.Lock()

    def get_current_url(self) -> str:
        """Get current active database URL"""
        with self._lock:
            return self.current_url

    def attempt_failover(self) -> tuple[bool, str]:
        """
        Attempt to failover to next available database

        Returns:
            Tuple of (success, new_url)
        """
        with self._lock:
            # Try failover URLs
            for i, url in enumerate(self.failover_urls):
                if i <= self.current_index:
                    continue  # Already tried this one

                logger.info(
                    "Attempting failover",
                    from_url=self.current_url[:50],
                    to_url=url[:50],
                    attempt=i + 1
                )

                if self._test_connection(url):
                    self.current_url = url
                    self.current_index = i
                    self._failover_count += 1

                    logger.info(
                        "Failover successful",
                        new_url=url[:50],
                        failover_count=self._failover_count
                    )

                    return True, url

            # All failover URLs failed, try primary again
            if self.current_index >= 0:
                logger.info("Attempting to restore primary connection")

                if self._test_connection(self.primary_url):
                    self.current_url = self.primary_url
                    self.current_index = -1

                    logger.info("Primary connection restored")
                    return True, self.primary_url

            logger.error("All failover attempts failed")
            return False, self.current_url

    def _test_connection(self, url: str) -> bool:
        """Test if database URL is accessible"""
        for attempt in range(self.retry_attempts):
            try:
                # Create temporary engine to test connection
                test_engine = create_engine(
                    url,
                    poolclass=NullPool,  # No pooling for test
                    connect_args={"connect_timeout": 5}
                )

                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    conn.commit()

                test_engine.dispose()
                return True

            except Exception as e:
                logger.warning(
                    "Connection test failed",
                    url=url[:50],
                    attempt=attempt + 1,
                    error=str(e)
                )

                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))

        return False

    def get_failover_stats(self) -> dict[str, Any]:
        """Get failover statistics"""
        with self._lock:
            return {
                'current_url': self.current_url[:50],
                'is_primary': self.current_index == -1,
                'failover_count': self._failover_count,
                'available_failovers': len(self.failover_urls)
            }


class EnhancedConnectionManager:
    """
    Enhanced connection manager with pooling, health monitoring,
    leak detection, and failover support
    """

    def __init__(self, config: ConnectionPoolConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None

        # Components
        self.leak_detector = ConnectionLeakDetector(
            threshold_seconds=config.leak_threshold_seconds
        ) if config.leak_detection_enabled else None

        self.health_monitor: ConnectionHealthMonitor | None = None

        self.failover_manager: DatabaseFailoverManager | None = None
        if config.failover_enabled and config.failover_urls:
            self.failover_manager = DatabaseFailoverManager(
                primary_url=database_url,
                failover_urls=config.failover_urls,
                retry_attempts=config.failover_retry_attempts,
                retry_delay=config.failover_retry_delay
            )

        # Metrics
        self.metrics = PoolMetrics()
        self._checkout_times: list[float] = []
        self._lock = threading.Lock()

        # Initialize
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize database engine with enhanced configuration"""
        current_url = self.database_url

        # Use failover URL if available
        if self.failover_manager:
            current_url = self.failover_manager.get_current_url()

        # Determine pool class and parameters based on database type
        if "duckdb" in current_url or "sqlite" in current_url:
            # SQLite/DuckDB: Use StaticPool without pool parameters
            self.engine = create_engine(
                current_url,
                poolclass=StaticPool,
                echo_pool=self.config.echo_pool,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL/MySQL: Use QueuePool with full configuration
            self.engine = create_engine(
                current_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo_pool=self.config.echo_pool
            )

        # Register event listeners
        self._register_event_listeners()

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Initialize health monitor
        if self.config.health_check_enabled:
            self.health_monitor = ConnectionHealthMonitor(
                engine=self.engine,
                check_interval=self.config.health_check_interval,
                enabled=True
            )
            self.health_monitor.start_monitoring()

        logger.info(
            "Enhanced connection manager initialized",
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            leak_detection=self.config.leak_detection_enabled,
            health_monitoring=self.config.health_check_enabled,
            failover=self.config.failover_enabled
        )

    def _register_event_listeners(self):
        """Register SQLAlchemy event listeners"""

        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_conn, connection_record):
            """Handle new connection creation"""
            with self._lock:
                self.metrics.total_connections_created += 1

            logger.debug("New database connection created")

        @event.listens_for(self.engine, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout from pool"""
            checkout_time = time.time()
            connection_record.info['checkout_time'] = checkout_time

            with self._lock:
                self.metrics.total_checkouts += 1

            # Track for leak detection
            if self.leak_detector:
                import traceback
                connection_id = str(id(dbapi_conn))
                thread_name = threading.current_thread().name
                stack_trace = ''.join(traceback.format_stack())

                self.leak_detector.track_checkout(
                    connection_id,
                    thread_name,
                    stack_trace
                )

        @event.listens_for(self.engine, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            """Handle connection checkin to pool"""
            checkout_time = connection_record.info.get('checkout_time')

            if checkout_time:
                duration = time.time() - checkout_time

                with self._lock:
                    self._checkout_times.append(duration)

                    # Keep only recent checkout times
                    if len(self._checkout_times) > 1000:
                        self._checkout_times = self._checkout_times[-1000:]

                    # Update average
                    if self._checkout_times:
                        self.metrics.avg_checkout_time = sum(
                            self._checkout_times) / len(self._checkout_times)

            # Track for leak detection
            if self.leak_detector:
                connection_id = str(id(dbapi_conn))
                self.leak_detector.track_checkin(connection_id)

        @event.listens_for(Pool, "connect")
        def on_pool_connect(dbapi_conn, connection_record):
            """Handle pool connection events"""
            # Set connection timeout if supported
            try:
                if hasattr(dbapi_conn, 'set_isolation_level'):
                    # PostgreSQL specific
                    pass
            except Exception:
                pass

    def get_session(self) -> Session:
        """
        Get database session with automatic failover

        Returns:
            SQLAlchemy Session
        """
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                session = self.SessionLocal()

                # Test connection
                session.execute(text("SELECT 1"))

                return session

            except (OperationalError, DBAPIError, DisconnectionError) as e:
                logger.warning(
                    "Failed to get database session",
                    attempt=attempt + 1,
                    error=str(e)
                )

                with self._lock:
                    self.metrics.failed_checkouts += 1

                # Attempt failover if enabled
                if self.failover_manager and attempt < max_attempts - 1:
                    success, new_url = self.failover_manager.attempt_failover()

                    if success:
                        # Reinitialize engine with new URL
                        self.dispose()
                        self.database_url = new_url
                        self._initialize_engine()
                        continue

                # Last attempt failed
                if attempt == max_attempts - 1:
                    raise

                time.sleep(1.0 * (2 ** attempt))

        raise OperationalError(
            "Failed to get database session after all attempts")

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_pool_metrics(self) -> PoolMetrics:
        """Get current connection pool metrics"""
        with self._lock:
            # Update current pool status
            if hasattr(self.engine.pool, 'size'):
                self.metrics.size = self.engine.pool.size()
                self.metrics.checked_in = self.engine.pool.checkedin()
                self.metrics.checked_out = self.engine.pool.size() - self.engine.pool.checkedin()
                self.metrics.overflow = self.engine.pool.overflow()

            # Update leaked connections count
            if self.leak_detector:
                leaked = self.leak_detector.detect_leaks()
                self.metrics.leaked_connections = len(leaked)

            return self.metrics

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status"""
        status = {
            'healthy': True,
            'pool_metrics': self.get_pool_metrics().to_dict(),
            'health_check': None,
            'health_stats': None,
            'failover_stats': None,
            'leak_detection': None
        }

        # Health monitoring
        if self.health_monitor:
            last_check = self.health_monitor.get_last_check()
            if last_check:
                status['health_check'] = {
                    'healthy': last_check.healthy,
                    'timestamp': last_check.timestamp.isoformat(),
                    'response_time': last_check.response_time,
                    'error': last_check.error
                }
                status['healthy'] = status['healthy'] and last_check.healthy

            status['health_stats'] = self.health_monitor.get_health_stats()

        # Failover status
        if self.failover_manager:
            status['failover_stats'] = self.failover_manager.get_failover_stats()

        # Leak detection
        if self.leak_detector:
            status['leak_detection'] = {
                'enabled': True,
                'threshold_seconds': self.leak_detector.threshold_seconds,
                'active_connections': len(
                    self.leak_detector.active_connections),
                'total_leaked': self.leak_detector.get_leaked_count()}

        return status

    def dispose(self):
        """Dispose of all connections in pool"""
        if self.health_monitor:
            self.health_monitor.stop_monitoring()

        if self.engine:
            self.engine.dispose()
            logger.info("Connection pool disposed")

    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.metrics = PoolMetrics()
            self._checkout_times.clear()

        if self.leak_detector:
            self.leak_detector.reset()

        logger.info("Connection metrics reset")


def create_connection_manager(
    database_url: str,
    pool_size: int = 5,
    max_overflow: int = 10,
    leak_detection: bool = True,
    health_monitoring: bool = True,
    failover_urls: list[str] | None = None
) -> EnhancedConnectionManager:
    """
    Create enhanced connection manager with default configuration

    Args:
        database_url: Primary database URL
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        leak_detection: Enable connection leak detection
        health_monitoring: Enable health monitoring
        failover_urls: List of failover database URLs

    Returns:
        EnhancedConnectionManager instance
    """
    config = ConnectionPoolConfig(
        pool_size=pool_size,
        max_overflow=max_overflow,
        leak_detection_enabled=leak_detection,
        health_check_enabled=health_monitoring,
        failover_enabled=bool(failover_urls),
        failover_urls=failover_urls or []
    )

    return EnhancedConnectionManager(config, database_url)
