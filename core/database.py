"""Database Management & Repository Pattern with Audit Logging and Soft Delete"""

import logging
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

from .config import get_config
from .connection_manager import (
    EnhancedConnectionManager,
    create_connection_manager,
)

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Base model for all entities
Base = declarative_base()

# Generic type for repositories
T = TypeVar('T', bound=Base)


class AuditLog(Base):
    """Audit log model for tracking all database changes"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=True, index=True)
    # CREATE, UPDATE, DELETE, RESTORE
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(255), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    old_values = Column(Text, nullable=True)  # JSON
    new_values = Column(Text, nullable=True)  # JSON
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    correlation_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)

    def __repr__(self):
        return f"<AuditLog(action='{
            self.action}', resource='{
            self.resource_type}:{
            self.resource_id}')>"


class DatabaseMetrics:
    """Database performance metrics"""

    def __init__(self):
        self.query_count = 0
        self.slow_query_count = 0
        self.error_count = 0
        self.total_query_time = 0.0
        self.connection_count = 0
        self.slow_queries: list[dict[str, Any]] = []
        self.slow_query_threshold = 1.0  # seconds

    def record_query(
            self,
            query: str,
            duration: float,
            error: Exception | None = None):
        """Record query execution metrics"""
        self.query_count += 1
        self.total_query_time += duration

        if error:
            self.error_count += 1

        if duration > self.slow_query_threshold:
            self.slow_query_count += 1
            self.slow_queries.append({
                'query': query[:500],  # Truncate long queries
                'duration': duration,
                'timestamp': datetime.utcnow(),
                'error': str(error) if error else None
            })

            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics"""
        avg_query_time = self.total_query_time / \
            self.query_count if self.query_count > 0 else 0

        return {
            'query_count': self.query_count,
            'slow_query_count': self.slow_query_count,
            'error_count': self.error_count,
            'total_query_time': self.total_query_time,
            'avg_query_time': avg_query_time,
            'connection_count': self.connection_count,
            'slow_queries': self.slow_queries[-10:]  # Last 10 slow queries
        }


class DatabaseManager:
    """Enhanced database connection and session management with monitoring"""

    def __init__(self, use_enhanced_connection_manager: bool = True):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        self.metrics = DatabaseMetrics()
        self._connection_pool_size = 0
        self._max_retries = 3
        self._retry_delay = 1.0
        self.use_enhanced_connection_manager = use_enhanced_connection_manager
        self.connection_manager: EnhancedConnectionManager | None = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize database engine with connection pooling"""
        database_url = self.config.get_database_url()

        # Use enhanced connection manager if enabled
        if self.use_enhanced_connection_manager:
            # Get failover URLs from environment if available
            import os
            failover_urls_str = os.getenv("DATABASE_FAILOVER_URLS", "")
            failover_urls = [
                url.strip() for url in failover_urls_str.split(",") if url.strip()]

            # Create enhanced connection manager
            self.connection_manager = create_connection_manager(
                database_url=database_url,
                pool_size=self.config.database.pool_size,
                max_overflow=self.config.database.max_overflow,
                leak_detection=True,
                health_monitoring=True,
                failover_urls=failover_urls if failover_urls else None
            )

            self.engine = self.connection_manager.engine
            self.SessionLocal = self.connection_manager.SessionLocal
            self._connection_pool_size = self.config.database.pool_size + \
                self.config.database.max_overflow

            logger.info(
                "Database engine initialized with enhanced connection manager",
                database_type=self._get_db_type(),
                failover_enabled=bool(failover_urls)
            )
            return

        # Fallback to standard engine initialization
        # Engine configuration based on database type
        if "duckdb" in database_url or "sqlite" in database_url:
            self.engine = create_engine(
                database_url,
                echo=self.config.database.echo,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        else:  # PostgreSQL
            pool_size = self.config.database.pool_size
            max_overflow = self.config.database.max_overflow

            self.engine = create_engine(
                database_url,
                echo=self.config.database.echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,  # Recycle connections after 1 hour
            )

            self._connection_pool_size = pool_size + max_overflow

        # Add query logging and monitoring
        if self.config.debug:
            event.listen(self.engine, "before_cursor_execute", self._log_query)

        event.listen(self.engine, "before_cursor_execute", self._before_query)
        event.listen(self.engine, "after_cursor_execute", self._after_query)
        event.listen(self.engine, "connect", self._on_connect)
        event.listen(self.engine, "checkout", self._on_checkout)

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(
            "Database engine initialized",
            database_type=self._get_db_type())

    def _get_db_type(self) -> str:
        """Get database type from URL"""
        url = self.config.get_database_url()
        if "postgresql" in url:
            return "postgresql"
        if "duckdb" in url:
            return "duckdb"
        if "sqlite" in url:
            return "sqlite"
        return "unknown"

    def _log_query(
            self,
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany):
        """Log SQL queries in debug mode"""
        logger.debug("SQL Query", query=statement[:200], params=parameters)

    def _before_query(
            self,
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany):
        """Track query start time"""
        context._query_start_time = time.time()

    def _after_query(
            self,
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany):
        """Track query completion and metrics"""
        if hasattr(context, '_query_start_time'):
            duration = time.time() - context._query_start_time
            self.metrics.record_query(statement, duration)

            if duration > self.metrics.slow_query_threshold:
                logger.warning(
                    "Slow query detected",
                    query=statement[:200],
                    duration=duration
                )

    def _on_connect(self, dbapi_conn, connection_record):
        """Handle new database connection"""
        self.metrics.connection_count += 1
        logger.debug("Database connection established")

    def _on_checkout(self, dbapi_conn, connection_record, connection_proxy):
        """Handle connection checkout from pool"""
        # Check for connection leaks
        pool = self.engine.pool
        if hasattr(pool, 'size'):
            checked_out = pool.size() - pool.checkedin()
            if checked_out > self._connection_pool_size * 0.8:
                logger.warning(
                    "High connection pool usage",
                    checked_out=checked_out,
                    pool_size=self._connection_pool_size
                )

    def get_session(self) -> Session:
        """Get database session with retry logic and automatic failover"""
        # Use enhanced connection manager if available
        if self.connection_manager:
            return self.connection_manager.get_session()

        # Fallback to standard retry logic
        for attempt in range(self._max_retries):
            try:
                return self.SessionLocal()
            except OperationalError as e:
                if attempt < self._max_retries - 1:
                    logger.warning(
                        "Database connection failed, retrying",
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    time.sleep(self._retry_delay * (2 ** attempt))
                else:
                    logger.error(
                        "Database connection failed after retries",
                        error=str(e))
                    raise

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")

    def execute_raw(self,
                    query: str,
                    params: dict[str,
                                 Any] | None = None) -> Any:
        """Execute raw SQL query"""
        with self.session_scope() as session:
            return session.execute(text(query), params or {})

    def health_check(self) -> dict[str, Any]:
        """
        Comprehensive database health check

        Returns:
            Dictionary with health status and metrics
        """
        # Use enhanced connection manager health check if available
        if self.connection_manager:
            enhanced_status = self.connection_manager.get_health_status()

            # Add database-specific checks
            try:
                with self.session_scope() as session:
                    session.execute(text("SELECT 1"))

                    # Count tables
                    if self._get_db_type() == 'postgresql':
                        result = session.execute(text(
                            "SELECT COUNT(*) FROM information_schema.tables "
                            "WHERE table_schema = 'public'"
                        ))
                    else:
                        result = session.execute(
                            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))

                    enhanced_status['table_count'] = result.scalar()
                    enhanced_status['database_type'] = self._get_db_type()
                    enhanced_status['connection_test'] = True

            except Exception as e:
                enhanced_status['error'] = str(e)
                enhanced_status['healthy'] = False
                logger.error("Database health check failed", error=str(e))

            return enhanced_status

        # Fallback to standard health check
        health_status = {
            'healthy': False,
            'database_type': self._get_db_type(),
            'connection_test': False,
            'table_count': 0,
            'metrics': {},
            'pool_status': {},
            'error': None
        }

        try:
            # Test connection
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
                health_status['connection_test'] = True

                # Count tables
                if self._get_db_type() == 'postgresql':
                    result = session.execute(text(
                        "SELECT COUNT(*) FROM information_schema.tables "
                        "WHERE table_schema = 'public'"
                    ))
                else:
                    result = session.execute(text(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                    ))

                health_status['table_count'] = result.scalar()

            # Get pool status
            pool = self.engine.pool
            if hasattr(pool, 'size'):
                health_status['pool_status'] = {
                    'size': pool.size(),
                    'checked_in': pool.checkedin(),
                    'checked_out': pool.size() - pool.checkedin(),
                    'overflow': pool.overflow(),
                    'total_connections': self.metrics.connection_count
                }

            # Get metrics
            health_status['metrics'] = self.metrics.get_stats()

            health_status['healthy'] = True

        except Exception as e:
            health_status['error'] = str(e)
            logger.error("Database health check failed", error=str(e))

        return health_status

    def get_metrics(self) -> dict[str, Any]:
        """Get database performance metrics"""
        return self.metrics.get_stats()

    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = DatabaseMetrics()

        if self.connection_manager:
            self.connection_manager.reset_metrics()

        logger.info("Database metrics reset")

    def get_connection_pool_metrics(self) -> dict[str, Any]:
        """Get connection pool metrics"""
        if self.connection_manager:
            return self.connection_manager.get_pool_metrics().to_dict()

        # Fallback to basic pool status
        pool = self.engine.pool
        if hasattr(pool, 'size'):
            return {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.size() - pool.checkedin(),
                'overflow': pool.overflow()
            }

        return {}

    def detect_connection_leaks(self) -> list[dict[str, Any]]:
        """Detect potential connection leaks"""
        if self.connection_manager and self.connection_manager.leak_detector:
            leaked = self.connection_manager.leak_detector.detect_leaks()
            return [
                {
                    'connection_id': conn.connection_id,
                    'duration': conn.duration,
                    'checked_out_by': conn.checked_out_by,
                    'checked_out_at': conn.checked_out_at.isoformat()
                }
                for conn in leaked
            ]

        return []

    def get_health_monitor_stats(self) -> dict[str, Any]:
        """Get health monitoring statistics"""
        if self.connection_manager and self.connection_manager.health_monitor:
            return self.connection_manager.health_monitor.get_health_stats()

        return {}

    def get_failover_status(self) -> dict[str, Any]:
        """Get failover status"""
        if self.connection_manager and self.connection_manager.failover_manager:
            return self.connection_manager.failover_manager.get_failover_stats()

        return {'failover_enabled': False}

    def dispose_connections(self):
        """Dispose of all connections in pool"""
        if self.connection_manager:
            self.connection_manager.dispose()
        elif self.engine:
            self.engine.dispose()

        logger.info("Database connections disposed")


class Repository(Generic[T]):
    """Enhanced repository with audit logging, soft delete, and bulk operations"""

    def __init__(
        self,
        model_class: type[T],
        db_manager: DatabaseManager,
        enable_audit: bool = True,
        enable_cache: bool = False
    ):
        self.model_class = model_class
        self.db_manager = db_manager
        self.enable_audit = enable_audit
        self.enable_cache = enable_cache
        self._cache: dict[Any, T] = {}
        self._current_user_id: str | None = None
        self._current_session_id: str | None = None
        self._correlation_id: str | None = None

    def set_context(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        correlation_id: str | None = None
    ):
        """Set audit context for operations"""
        self._current_user_id = user_id
        self._current_session_id = session_id
        self._correlation_id = correlation_id

    def _log_audit(
        self,
        session: Session,
        action: str,
        resource_id: str,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None
    ):
        """Log audit entry"""
        if not self.enable_audit:
            return

        import json

        audit_log = AuditLog(
            user_id=self._current_user_id,
            action=action,
            resource_type=self.model_class.__tablename__,
            resource_id=str(resource_id),
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            timestamp=datetime.utcnow(),
            correlation_id=self._correlation_id,
            session_id=self._current_session_id
        )
        session.add(audit_log)

    def _entity_to_dict(self, entity: T) -> dict[str, Any]:
        """Convert entity to dictionary for audit logging"""
        result = {}
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def _invalidate_cache(self, entity_id: Any = None):
        """Invalidate cache entry or entire cache"""
        if not self.enable_cache:
            return

        if entity_id is not None:
            self._cache.pop(entity_id, None)
        else:
            self._cache.clear()

    def create(self, **kwargs) -> T:
        """Create new entity with audit logging"""
        with self.db_manager.session_scope() as session:
            entity = self.model_class(**kwargs)
            session.add(entity)
            session.flush()
            session.refresh(entity)

            # Log audit
            entity_id = getattr(entity, 'id', None)
            if entity_id:
                self._log_audit(
                    session,
                    'CREATE',
                    entity_id,
                    new_values=self._entity_to_dict(entity)
                )

            # Cache entity
            if self.enable_cache and entity_id:
                self._cache[entity_id] = entity

            logger.debug(
                "Entity created",
                model=self.model_class.__name__,
                entity_id=entity_id
            )

            return entity

    def get_by_id(self, entity_id: Any, use_cache: bool = True) -> T | None:
        """Get entity by ID with optional caching"""
        # Check cache first
        if self.enable_cache and use_cache and entity_id in self._cache:
            logger.debug(
                "Cache hit",
                model=self.model_class.__name__,
                entity_id=entity_id)
            return self._cache[entity_id]

        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            )

            # Apply soft delete filter
            if hasattr(self.model_class, 'deleted_at'):
                query = query.filter(self.model_class.deleted_at.is_(None))

            entity = query.first()

            # Cache entity
            if entity and self.enable_cache:
                self._cache[entity_id] = entity

            return entity

    def get_all(
        self,
        limit: int | None = None,
        offset: int = 0,
        include_deleted: bool = False
    ) -> list[T]:
        """Get all entities with pagination"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            # Apply soft delete filter
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            return query.all()

    def update(self, entity_id: Any, **kwargs) -> T | None:
        """Update entity with audit logging"""
        with self.db_manager.session_scope() as session:
            entity = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

            if not entity:
                return None

            # Capture old values for audit
            old_values = self._entity_to_dict(
                entity) if self.enable_audit else None

            # Update fields
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            # Update timestamp if available
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()

            session.flush()
            session.refresh(entity)

            # Log audit
            self._log_audit(
                session,
                'UPDATE',
                entity_id,
                old_values=old_values,
                new_values=self._entity_to_dict(entity)
            )

            # Invalidate cache
            self._invalidate_cache(entity_id)

            logger.debug(
                "Entity updated",
                model=self.model_class.__name__,
                entity_id=entity_id
            )

            return entity

    def delete(self, entity_id: Any, soft: bool = True) -> bool:
        """Delete entity with soft delete support and audit logging"""
        with self.db_manager.session_scope() as session:
            entity = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

            if not entity:
                return False

            # Capture old values for audit
            old_values = self._entity_to_dict(
                entity) if self.enable_audit else None

            if soft and hasattr(entity, 'deleted_at'):
                entity.deleted_at = datetime.utcnow()
                action = 'SOFT_DELETE'
            else:
                session.delete(entity)
                action = 'DELETE'

            # Log audit
            self._log_audit(
                session,
                action,
                entity_id,
                old_values=old_values
            )

            # Invalidate cache
            self._invalidate_cache(entity_id)

            logger.info(
                "Entity deleted",
                model=self.model_class.__name__,
                entity_id=entity_id,
                soft=soft
            )

            return True

    def restore(self, entity_id: Any) -> T | None:
        """Restore soft-deleted entity"""
        if not hasattr(self.model_class, 'deleted_at'):
            raise ValueError(
                f"{self.model_class.__name__} does not support soft delete")

        with self.db_manager.session_scope() as session:
            entity = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

            if not entity or entity.deleted_at is None:
                return None

            # Restore entity
            entity.deleted_at = None

            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()

            session.flush()
            session.refresh(entity)

            # Log audit
            self._log_audit(
                session,
                'RESTORE',
                entity_id,
                new_values=self._entity_to_dict(entity)
            )

            # Invalidate cache
            self._invalidate_cache(entity_id)

            logger.info(
                "Entity restored",
                model=self.model_class.__name__,
                entity_id=entity_id
            )

            return entity

    def find_by(self, include_deleted: bool = False, **kwargs) -> list[T]:
        """Find entities by criteria"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            # Apply soft delete filter
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            # Apply filters
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(
                        getattr(
                            self.model_class,
                            key) == value)

            return query.all()

    def bulk_create(self, entities_data: list[dict[str, Any]]) -> list[T]:
        """Bulk create entities for performance"""
        with self.db_manager.session_scope() as session:
            entities = []

            for data in entities_data:
                entity = self.model_class(**data)
                entities.append(entity)
                session.add(entity)

            session.flush()

            # Refresh all entities to get IDs
            for entity in entities:
                session.refresh(entity)

                # Log audit for each
                entity_id = getattr(entity, 'id', None)
                if entity_id and self.enable_audit:
                    self._log_audit(
                        session,
                        'BULK_CREATE',
                        entity_id,
                        new_values=self._entity_to_dict(entity)
                    )

            # Invalidate cache
            self._invalidate_cache()

            logger.info(
                "Bulk create completed",
                model=self.model_class.__name__,
                count=len(entities)
            )

            return entities

    def bulk_update(self, updates: list[dict[str, Any]]) -> int:
        """
        Bulk update entities

        Args:
            updates: List of dicts with 'id' and fields to update

        Returns:
            Number of entities updated
        """
        with self.db_manager.session_scope() as session:
            count = 0

            for update_data in updates:
                entity_id = update_data.pop('id', None)
                if not entity_id:
                    continue

                entity = session.query(self.model_class).filter(
                    self.model_class.id == entity_id
                ).first()

                if not entity:
                    continue

                # Capture old values
                old_values = self._entity_to_dict(
                    entity) if self.enable_audit else None

                # Update fields
                for key, value in update_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)

                if hasattr(entity, 'updated_at'):
                    entity.updated_at = datetime.utcnow()

                # Log audit
                if self.enable_audit:
                    self._log_audit(
                        session,
                        'BULK_UPDATE',
                        entity_id,
                        old_values=old_values,
                        new_values=self._entity_to_dict(entity)
                    )

                count += 1

            # Invalidate cache
            self._invalidate_cache()

            logger.info(
                "Bulk update completed",
                model=self.model_class.__name__,
                count=count
            )

            return count

    def bulk_delete(self, entity_ids: list[Any], soft: bool = True) -> int:
        """Bulk delete entities"""
        with self.db_manager.session_scope() as session:
            count = 0

            for entity_id in entity_ids:
                entity = session.query(self.model_class).filter(
                    self.model_class.id == entity_id
                ).first()

                if not entity:
                    continue

                # Capture old values
                old_values = self._entity_to_dict(
                    entity) if self.enable_audit else None

                if soft and hasattr(entity, 'deleted_at'):
                    entity.deleted_at = datetime.utcnow()
                    action = 'BULK_SOFT_DELETE'
                else:
                    session.delete(entity)
                    action = 'BULK_DELETE'

                # Log audit
                if self.enable_audit:
                    self._log_audit(
                        session,
                        action,
                        entity_id,
                        old_values=old_values
                    )

                count += 1

            # Invalidate cache
            self._invalidate_cache()

            logger.info(
                "Bulk delete completed",
                model=self.model_class.__name__,
                count=count,
                soft=soft
            )

            return count

    def count(self, include_deleted: bool = False) -> int:
        """Count entities"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            return query.count()

    def exists(self, entity_id: Any) -> bool:
        """Check if entity exists"""
        return self.get_by_id(entity_id) is not None

    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
        **filters
    ) -> dict[str, Any]:
        """
        Paginate entities with filters

        Returns:
            Dictionary with items, total, page, page_size, total_pages
        """
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            # Apply soft delete filter
            if hasattr(self.model_class, 'deleted_at') and not include_deleted:
                query = query.filter(self.model_class.deleted_at.is_(None))

            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.filter(
                        getattr(
                            self.model_class,
                            key) == value)

            # Get total count
            total = query.count()

            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total + page_size - 1) // page_size

            # Get page items
            items = query.limit(page_size).offset(offset).all()

            return {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }


class UnitOfWork:
    """Enhanced Unit of Work pattern with transaction nesting and monitoring"""

    def __init__(
        self,
        db_manager: DatabaseManager,
        user_id: str | None = None,
        session_id: str | None = None,
        correlation_id: str | None = None
    ):
        self.db_manager = db_manager
        self.session: Session | None = None
        self._repositories: dict[str, Repository] = {}
        self._user_id = user_id
        self._session_id = session_id
        self._correlation_id = correlation_id
        self._start_time: float | None = None
        self._nested_level = 0
        self._savepoints: list[str] = []

    def __enter__(self):
        self._start_time = time.time()

        if self.session is None:
            self.session = self.db_manager.get_session()
            self._nested_level = 0
        else:
            # Nested transaction - use savepoint
            self._nested_level += 1
            savepoint_name = f"sp_{
                self._nested_level}_{
                int(
                    time.time() *
                    1000)}"
            self.session.begin_nested()
            self._savepoints.append(savepoint_name)

            logger.debug(
                "Nested transaction started",
                level=self._nested_level,
                savepoint=savepoint_name
            )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self._start_time if self._start_time else 0

        try:
            if exc_type is not None:
                self.rollback()
                logger.error(
                    "Transaction rolled back",
                    error=str(exc_val),
                    duration=duration,
                    nested_level=self._nested_level
                )
            else:
                self.commit()
                logger.debug(
                    "Transaction committed",
                    duration=duration,
                    nested_level=self._nested_level
                )
        finally:
            if self._nested_level == 0:
                self.session.close()
                self.session = None
            else:
                self._nested_level -= 1
                if self._savepoints:
                    self._savepoints.pop()

    def commit(self):
        """Commit transaction"""
        if self.session:
            try:
                self.session.commit()
            except IntegrityError as e:
                logger.error("Integrity error during commit", error=str(e))
                self.rollback()
                raise
            except Exception as e:
                logger.error("Error during commit", error=str(e))
                self.rollback()
                raise

    def rollback(self):
        """Rollback transaction"""
        if self.session:
            self.session.rollback()

    def flush(self):
        """Flush pending changes without committing"""
        if self.session:
            self.session.flush()

    def get_repository(
        self,
        model_class: type[T],
        enable_audit: bool = True,
        enable_cache: bool = False
    ) -> Repository[T]:
        """Get repository for model class with context"""
        class_name = model_class.__name__

        if class_name not in self._repositories:
            repo = Repository(
                model_class,
                self.db_manager,
                enable_audit=enable_audit,
                enable_cache=enable_cache
            )

            # Set audit context
            repo.set_context(
                user_id=self._user_id,
                session_id=self._session_id,
                correlation_id=self._correlation_id
            )

            self._repositories[class_name] = repo

        return self._repositories[class_name]

    def execute_raw(self, query: str, params: dict[str, Any] = None) -> Any:
        """Execute raw SQL within transaction"""
        if not self.session:
            raise RuntimeError("No active session")

        return self.session.execute(text(query), params or {})

    def refresh(self, entity: T):
        """Refresh entity from database"""
        if not self.session:
            raise RuntimeError("No active session")

        self.session.refresh(entity)


def run_tx(
    fn: Callable[[UnitOfWork], Any],
    user_id: str | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None
) -> Any:
    """
    Run function in transaction with audit context

    Args:
        fn: Function that takes UnitOfWork and returns result
        user_id: User ID for audit logging
        session_id: Session ID for audit logging
        correlation_id: Correlation ID for request tracing

    Returns:
        Result from function
    """
    db_manager = get_db_manager()
    with UnitOfWork(
        db_manager,
        user_id=user_id,
        session_id=session_id,
        correlation_id=correlation_id
    ) as uow:
        return fn(uow)


# Global database manager
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_conn() -> Session:
    """
    Get database connection

    Returns:
        SQLAlchemy Session
    """
    return get_db_manager().get_session()


def migrate(auto_run: bool = False) -> bool:
    """
    Run database migrations using Alembic

    Args:
        auto_run: If True, automatically run pending migrations

    Returns:
        True if migrations successful, False otherwise
    """
    try:
        from .migration_manager import MigrationManager

        migration_manager = MigrationManager(get_db_manager())

        if auto_run:
            migration_manager.run_migrations()
            logger.info("Database migrations completed successfully")
            return True
        # Just check for pending migrations
        pending = migration_manager.get_pending_migrations()
        if pending:
            logger.info(
                "Pending migrations found",
                count=len(pending),
                migrations=pending
            )
        else:
            logger.info("No pending migrations")
        return True

    except Exception as e:
        logger.error("Migration failed", error=str(e), exc_info=True)
        return False


def init_database(auto_migrate: bool = True):
    """
    Initialize database with optional automatic migrations

    Args:
        auto_migrate: If True, automatically run pending migrations
    """
    db_manager = get_db_manager()

    # Run migrations if enabled
    if auto_migrate:
        success = migrate(auto_run=True)

        if not success:
            logger.warning("Migration failed, falling back to create_tables")
            db_manager.create_tables()
    else:
        db_manager.create_tables()

    logger.info("Database initialized")


def get_audit_logs(
    resource_type: str | None = None,
    resource_id: str | None = None,
    user_id: str | None = None,
    action: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[AuditLog]:
    """
    Query audit logs with filters

    Args:
        resource_type: Filter by resource type
        resource_id: Filter by resource ID
        user_id: Filter by user ID
        action: Filter by action type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of AuditLog entries
    """
    db_manager = get_db_manager()

    with db_manager.session_scope() as session:
        query = session.query(AuditLog)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)

        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)

        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)

        return query.all()


def cleanup_audit_logs(retention_days: int = 90) -> int:
    """
    Clean up old audit logs

    Args:
        retention_days: Number of days to retain audit logs

    Returns:
        Number of audit logs deleted
    """
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    db_manager = get_db_manager()

    with db_manager.session_scope() as session:
        deleted = session.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()

        logger.info(
            "Audit logs cleaned up",
            count=deleted,
            retention_days=retention_days)
        return deleted
