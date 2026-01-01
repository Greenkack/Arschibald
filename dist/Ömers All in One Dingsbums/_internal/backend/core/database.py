"""
Database Connection and Session Management

Handles SQLAlchemy database connections and session management with both
sync and async support, connection pooling, and proper lifecycle management.

Requirements: 1.2, 1.5
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()


# ============================================================================
# Synchronous Database Setup
# ============================================================================

def get_engine_config():
    """Get engine configuration based on database type"""
    config = {
        "echo": settings.DATABASE_ECHO,
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 3600,   # Recycle connections after 1 hour
    }
    
    if "sqlite" in settings.DATABASE_URL:
        # SQLite-specific configuration
        config["connect_args"] = {"check_same_thread": False}
        config["poolclass"] = NullPool  # SQLite doesn't need connection pooling
    else:
        # PostgreSQL/MySQL configuration with connection pooling
        config["poolclass"] = QueuePool
        config["pool_size"] = settings.DATABASE_POOL_SIZE
        config["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        config["pool_timeout"] = settings.DATABASE_POOL_TIMEOUT
    
    return config


# Create synchronous database engine
engine = create_engine(
    settings.DATABASE_URL,
    **get_engine_config()
)


# Configure SQLite for better concurrency if using SQLite
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set SQLite pragmas for better performance and concurrency"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety and speed
        cursor.execute("PRAGMA foreign_keys=ON")  # Enable foreign keys
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.close()


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Don't expire objects after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Asynchronous Database Setup
# ============================================================================

def get_async_database_url():
    """Convert sync database URL to async URL"""
    url = settings.DATABASE_URL
    
    if url.startswith("sqlite:///"):
        # SQLite async URL
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif url.startswith("postgresql://"):
        # PostgreSQL async URL
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("mysql://"):
        # MySQL async URL
        return url.replace("mysql://", "mysql+aiomysql://")
    
    return url


# Create asynchronous database engine
async_engine = create_async_engine(
    get_async_database_url(),
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=settings.DATABASE_POOL_SIZE if "sqlite" not in settings.DATABASE_URL else 5,
    max_overflow=settings.DATABASE_MAX_OVERFLOW if "sqlite" not in settings.DATABASE_URL else 10)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function to get database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for async database sessions.
    
    Usage:
        async with get_async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Async session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# Database Initialization and Management
# ============================================================================

def init_db():
    """
    Initialize database by creating all tables.
    This should be called on application startup.
    """
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def init_async_db():
    """
    Initialize database asynchronously by creating all tables.
    """
    try:
        logger.info("Initializing async database...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Async database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize async database: {e}")
        raise


def drop_db():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


async def drop_async_db():
    """
    Drop all database tables asynchronously.
    WARNING: This will delete all data!
    """
    logger.warning("Dropping all async database tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("All async tables dropped")


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def check_async_db_connection() -> bool:
    """
    Check if async database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Async database connection successful")
        return True
    except Exception as e:
        logger.error(f"Async database connection failed: {e}")
        return False


def get_db_stats() -> dict:
    """
    Get database connection pool statistics.
    
    Returns:
        dict: Pool statistics
    """
    if hasattr(engine.pool, 'size'):
        return {
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "total_connections": engine.pool.size() + engine.pool.overflow(),
        }
    return {"message": "Pool statistics not available (using NullPool)"}


# ============================================================================
# Transaction Management Utilities
# ============================================================================

class DatabaseTransaction:
    """Context manager for database transactions"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            self.session.commit()
        return False


class AsyncDatabaseTransaction:
    """Async context manager for database transactions"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            logger.error(f"Async transaction rolled back due to: {exc_val}")
        else:
            await self.session.commit()
        return False


def transaction(session: Session) -> DatabaseTransaction:
    """
    Create a transaction context manager.
    
    Usage:
        with transaction(db) as tx:
            tx.add(user)
            tx.add(project)
    """
    return DatabaseTransaction(session)


def async_transaction(session: AsyncSession) -> AsyncDatabaseTransaction:
    """
    Create an async transaction context manager.
    
    Usage:
        async with async_transaction(db) as tx:
            tx.add(user)
            tx.add(project)
    """
    return AsyncDatabaseTransaction(session)
