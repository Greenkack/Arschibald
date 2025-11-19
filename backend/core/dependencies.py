"""
Database Dependencies

Provides dependency injection functions for FastAPI endpoints.
Includes both sync and async database session dependencies.

Requirements: 1.2, 1.5
"""

from typing import Generator, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from backend.core.database import (
    get_db,
    get_async_db,
    SessionLocal,
    AsyncSessionLocal,
    transaction,
    async_transaction,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Basic Database Dependencies
# ============================================================================

def get_database_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.
    
    This is an alias for get_db() for clarity in endpoint signatures.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_database_session)):
            return db.query(Item).all()
    """
    yield from get_db()


async def get_async_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session for dependency injection.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_database_session)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async for session in get_async_db():
        yield session


# ============================================================================
# Transaction-Wrapped Dependencies
# ============================================================================

def get_db_with_transaction() -> Generator[Session, None, None]:
    """
    Get a database session wrapped in a transaction.
    
    The transaction will automatically commit on success or rollback on error.
    
    Usage:
        @app.post("/items")
        def create_item(item: ItemCreate, db: Session = Depends(get_db_with_transaction)):
            new_item = Item(**item.dict())
            db.add(new_item)
            # Transaction commits automatically
            return new_item
    """
    db = SessionLocal()
    try:
        with transaction(db) as tx:
            yield tx
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed"
        )
    finally:
        db.close()


async def get_async_db_with_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session wrapped in a transaction.
    
    Usage:
        @app.post("/items")
        async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_async_db_with_transaction)):
            new_item = Item(**item.dict())
            db.add(new_item)
            # Transaction commits automatically
            return new_item
    """
    async with AsyncSessionLocal() as session:
        try:
            async with async_transaction(session) as tx:
                yield tx
        except Exception as e:
            logger.error(f"Async transaction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database transaction failed"
            )


# ============================================================================
# Read-Only Dependencies
# ============================================================================

def get_readonly_db() -> Generator[Session, None, None]:
    """
    Get a read-only database session.
    
    This session will not commit any changes, useful for read-only endpoints.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_readonly_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Read-only session error: {e}")
        raise
    finally:
        db.rollback()  # Ensure no changes are committed
        db.close()


async def get_async_readonly_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async read-only database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_readonly_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async read-only session error: {e}")
            raise
        finally:
            await session.rollback()  # Ensure no changes are committed
            await session.close()


# ============================================================================
# Pagination Dependencies
# ============================================================================

class PaginationParams:
    """Pagination parameters for list endpoints"""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        max_limit: int = 1000
    ):
        self.skip = max(0, skip)
        self.limit = min(limit, max_limit)
        self.max_limit = max_limit
    
    def apply_to_query(self, query):
        """Apply pagination to a SQLAlchemy query"""
        return query.offset(self.skip).limit(self.limit)


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> PaginationParams:
    """
    Get pagination parameters for list endpoints.
    
    Usage:
        @app.get("/items")
        def get_items(
            db: Session = Depends(get_db),
            pagination: PaginationParams = Depends(get_pagination_params)
        ):
            query = db.query(Item)
            return pagination.apply_to_query(query).all()
    """
    return PaginationParams(skip=skip, limit=limit)


# ============================================================================
# Database Health Check Dependencies
# ============================================================================

async def check_database_health() -> bool:
    """
    Check if database is healthy and accessible.
    
    Usage:
        @app.get("/health")
        async def health_check(db_healthy: bool = Depends(check_database_health)):
            return {"database": "healthy" if db_healthy else "unhealthy"}
    """
    from backend.core.database import check_async_db_connection
    return await check_async_db_connection()


def check_sync_database_health() -> bool:
    """
    Check if sync database is healthy and accessible.
    
    Usage:
        @app.get("/health")
        def health_check(db_healthy: bool = Depends(check_sync_database_health)):
            return {"database": "healthy" if db_healthy else "unhealthy"}
    """
    from backend.core.database import check_db_connection
    return check_db_connection()


# ============================================================================
# Batch Operation Dependencies
# ============================================================================

class BatchOperationContext:
    """Context for batch database operations"""
    
    def __init__(self, session: Session, batch_size: int = 100):
        self.session = session
        self.batch_size = batch_size
        self.items = []
    
    def add(self, item):
        """Add item to batch"""
        self.items.append(item)
        if len(self.items) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Flush current batch to database"""
        if self.items:
            self.session.bulk_save_objects(self.items)
            self.session.commit()
            self.items = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.flush()
        else:
            self.session.rollback()
        return False


def get_batch_operation_context(
    batch_size: int = 100
) -> Generator[BatchOperationContext, None, None]:
    """
    Get a context for batch database operations.
    
    Usage:
        @app.post("/items/batch")
        def create_items_batch(
            items: List[ItemCreate],
            batch_ctx: BatchOperationContext = Depends(get_batch_operation_context)
        ):
            for item_data in items:
                item = Item(**item_data.dict())
                batch_ctx.add(item)
            return {"created": len(items)}
    """
    db = SessionLocal()
    try:
        with BatchOperationContext(db, batch_size) as ctx:
            yield ctx
    finally:
        db.close()


# ============================================================================
# Database URL Dependency
# ============================================================================

def get_database_url() -> str:
    """
    Get the database URL from configuration.
    
    Usage:
        @app.get("/database/info")
        def get_db_info(db_url: str = Depends(get_database_url)):
            return {"database_url": db_url}
    """
    from backend.config import settings
    return settings.DATABASE_URL


# ============================================================================
# Export commonly used dependencies
# ============================================================================

__all__ = [
    'get_database_session',
    'get_async_database_session',
    'get_db_with_transaction',
    'get_async_db_with_transaction',
    'get_readonly_db',
    'get_async_readonly_db',
    'get_pagination_params',
    'check_database_health',
    'check_sync_database_health',
    'get_batch_operation_context',
    'get_database_url',
    'PaginationParams',
    'BatchOperationContext',
]
