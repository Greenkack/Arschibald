"""Database Management & Repository Pattern"""

import logging
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_config

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


class DatabaseManager:
    """Database connection and session management"""

    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize database engine"""
        database_url = self.config.get_database_url()

        # Engine configuration based on database type
        if "duckdb" in database_url or "sqlite" in database_url:
            self.engine = create_engine(
                database_url,
                echo=self.config.database.echo,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        else:  # PostgreSQL
            self.engine = create_engine(
                database_url,
                echo=self.config.database.echo,
                pool_size=self.config.database.pool_size,
                max_overflow=self.config.database.max_overflow,
            )

        # Add query logging
        if self.config.debug:
            event.listen(self.engine, "before_cursor_execute", self._log_query)

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _log_query(
            self,
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany):
        """Log SQL queries in debug mode"""
        logger.debug("SQL Query", query=statement, params=parameters)

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

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

    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)

    def execute_raw(self,
                    query: str,
                    params: dict[str,
                                 Any] | None = None) -> Any:
        """Execute raw SQL query"""
        with self.session_scope() as session:
            return session.execute(text(query), params or {})

    def health_check(self) -> bool:
        """Check database health"""
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False


class Repository(Generic[T]):
    """Base repository for CRUD operations"""

    def __init__(self, model_class: type[T], db_manager: DatabaseManager):
        self.model_class = model_class
        self.db_manager = db_manager

    def create(self, **kwargs) -> T:
        """Create new entity"""
        with self.db_manager.session_scope() as session:
            entity = self.model_class(**kwargs)
            session.add(entity)
            session.flush()
            session.refresh(entity)
            return entity

    def get_by_id(self, entity_id: Any) -> T | None:
        """Get entity by ID"""
        with self.db_manager.session_scope() as session:
            return session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[T]:
        """Get all entities"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            # Apply soft delete filter if model supports it
            if hasattr(self.model_class, 'deleted_at'):
                query = query.filter(self.model_class.deleted_at.is_(None))

            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            return query.all()

    def update(self, entity_id: Any, **kwargs) -> T | None:
        """Update entity"""
        with self.db_manager.session_scope() as session:
            entity = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)

                # Update timestamp if available
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = datetime.utcnow()

                session.flush()
                session.refresh(entity)

            return entity

    def delete(self, entity_id: Any, soft: bool = True) -> bool:
        """Delete entity (soft delete by default)"""
        with self.db_manager.session_scope() as session:
            entity = session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()

            if not entity:
                return False

            if soft and hasattr(entity, 'deleted_at'):
                entity.deleted_at = datetime.utcnow()
            else:
                session.delete(entity)

            return True

    def find_by(self, **kwargs) -> list[T]:
        """Find entities by criteria"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            # Apply soft delete filter
            if hasattr(self.model_class, 'deleted_at'):
                query = query.filter(self.model_class.deleted_at.is_(None))

            # Apply filters
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(
                        getattr(
                            self.model_class,
                            key) == value)

            return query.all()

    def count(self) -> int:
        """Count entities"""
        with self.db_manager.session_scope() as session:
            query = session.query(self.model_class)

            if hasattr(self.model_class, 'deleted_at'):
                query = query.filter(self.model_class.deleted_at.is_(None))

            return query.count()

    def exists(self, entity_id: Any) -> bool:
        """Check if entity exists"""
        return self.get_by_id(entity_id) is not None


class UnitOfWork:
    """Unit of Work pattern for managing transactions"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.session: Session | None = None
        self._repositories: dict[str, Repository] = {}

    def __enter__(self):
        self.session = self.db_manager.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self):
        """Commit transaction"""
        if self.session:
            self.session.commit()

    def rollback(self):
        """Rollback transaction"""
        if self.session:
            self.session.rollback()

    def get_repository(self, model_class: type[T]) -> Repository[T]:
        """Get repository for model class"""
        class_name = model_class.__name__
        if class_name not in self._repositories:
            self._repositories[class_name] = Repository(
                model_class, self.db_manager)
        return self._repositories[class_name]


def run_tx(fn: Callable[[UnitOfWork], Any]) -> Any:
    """Run function in transaction"""
    db_manager = get_db_manager()
    with UnitOfWork(db_manager) as uow:
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
    """Get database connection"""
    return get_db_manager().get_session()


def init_database():
    """Initialize database"""
    db_manager = get_db_manager()
    db_manager.create_tables()
    logger.info("Database initialized")
