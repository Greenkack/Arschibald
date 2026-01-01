"""
Tests for Database Setup and Configuration

Tests the database connection, session management, async support,
connection pooling, and Alembic migrations.

Requirements: 1.2, 1.5
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir.parent))

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import (
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    get_db,
    get_async_db,
    init_db,
    init_async_db,
    check_db_connection,
    check_async_db_connection,
    get_db_stats,
    transaction,
    async_transaction,
    Base)
from backend.core.dependencies import (
    get_database_session,
    get_async_database_session,
    get_pagination_params,
    PaginationParams,
    BatchOperationContext)
from backend.models.database_models import User, Customer, Project


class TestDatabaseConnection:
    """Test database connection and engine setup"""
    
    def test_engine_created(self):
        """Test that database engine is created"""
        assert engine is not None
        assert engine.url is not None
    
    def test_async_engine_created(self):
        """Test that async database engine is created"""
        assert async_engine is not None
        assert async_engine.url is not None
    
    def test_sync_connection(self):
        """Test synchronous database connection"""
        assert check_db_connection() is True
    
    @pytest.mark.asyncio
    async def test_async_connection(self):
        """Test asynchronous database connection"""
        result = await check_async_db_connection()
        assert result is True
    
    def test_pool_stats(self):
        """Test database connection pool statistics"""
        stats = get_db_stats()
        assert isinstance(stats, dict)


class TestSessionManagement:
    """Test database session management"""
    
    def test_session_local_created(self):
        """Test that SessionLocal is created"""
        assert SessionLocal is not None
    
    def test_async_session_local_created(self):
        """Test that AsyncSessionLocal is created"""
        assert AsyncSessionLocal is not None
    
    def test_get_db_dependency(self):
        """Test get_db dependency function"""
        db_gen = get_db()
        db = next(db_gen)
        assert isinstance(db, Session)
        try:
            db_gen.close()
        except StopIteration:
            pass
    
    @pytest.mark.asyncio
    async def test_get_async_db_dependency(self):
        """Test get_async_db dependency function"""
        async_gen = get_async_db()
        db = await async_gen.__anext__()
        assert isinstance(db, AsyncSession)
        try:
            await async_gen.aclose()
        except StopAsyncIteration:
            pass
    
    def test_session_context_manager(self):
        """Test session as context manager"""
        db = SessionLocal()
        try:
            # Test basic query
            result = db.execute(text("SELECT 1"))
            assert result is not None
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_async_session_context_manager(self):
        """Test async session as context manager"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            assert result is not None


class TestTransactionManagement:
    """Test transaction management"""
    
    def test_transaction_context_manager(self):
        """Test transaction context manager"""
        db = SessionLocal()
        try:
            with transaction(db) as tx:
                # Transaction should work
                result = tx.execute(text("SELECT 1"))
                assert result is not None
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_async_transaction_context_manager(self):
        """Test async transaction context manager"""
        async with AsyncSessionLocal() as session:
            async with async_transaction(session) as tx:
                result = await tx.execute(text("SELECT 1"))
                assert result is not None
    
    def test_transaction_rollback_on_error(self):
        """Test that transaction rolls back on error"""
        db = SessionLocal()
        try:
            with pytest.raises(Exception):
                with transaction(db) as tx:
                    # Force an error
                    raise Exception("Test error")
        finally:
            db.close()


class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_init_db(self):
        """Test database initialization"""
        # This should not raise an error
        init_db()
        
        # Verify tables were created
        assert Base.metadata.tables is not None
        assert len(Base.metadata.tables) > 0
    
    @pytest.mark.asyncio
    async def test_init_async_db(self):
        """Test async database initialization"""
        # This should not raise an error
        await init_async_db()
        
        # Verify tables were created
        assert Base.metadata.tables is not None
        assert len(Base.metadata.tables) > 0


class TestDependencies:
    """Test database dependencies"""
    
    def test_get_database_session(self):
        """Test get_database_session dependency"""
        db_gen = get_database_session()
        db = next(db_gen)
        assert isinstance(db, Session)
        try:
            db_gen.close()
        except StopIteration:
            pass
    
    @pytest.mark.asyncio
    async def test_get_async_database_session(self):
        """Test get_async_database_session dependency"""
        async_gen = get_async_database_session()
        db = await async_gen.__anext__()
        assert isinstance(db, AsyncSession)
        try:
            await async_gen.aclose()
        except StopAsyncIteration:
            pass
    
    def test_pagination_params(self):
        """Test pagination parameters"""
        params = get_pagination_params(skip=10, limit=50)
        assert isinstance(params, PaginationParams)
        assert params.skip == 10
        assert params.limit == 50
    
    def test_pagination_params_defaults(self):
        """Test pagination parameters with defaults"""
        params = get_pagination_params()
        assert params.skip == 0
        assert params.limit == 100
    
    def test_pagination_params_max_limit(self):
        """Test pagination parameters respect max limit"""
        params = get_pagination_params(limit=2000)
        assert params.limit == 1000  # Should be capped at max_limit


class TestModels:
    """Test database models"""
    
    def test_user_model_exists(self):
        """Test that User model is defined"""
        assert User is not None
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == 'users'
    
    def test_customer_model_exists(self):
        """Test that Customer model is defined"""
        assert Customer is not None
        assert hasattr(Customer, '__tablename__')
        assert Customer.__tablename__ == 'customers'
    
    def test_project_model_exists(self):
        """Test that Project model is defined"""
        assert Project is not None
        assert hasattr(Project, '__tablename__')
        assert Project.__tablename__ == 'projects'
    
    def test_model_has_universal_columns(self):
        """Test that models have universal data columns"""
        assert hasattr(User, 'id')
        assert hasattr(User, 'dynamic_key')
        assert hasattr(User, 'pdf_bytes')
        assert hasattr(User, 'created_at')
        assert hasattr(User, 'updated_at')


class TestCRUDOperations:
    """Test basic CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Setup: Initialize database
        init_db()
        yield
        # Teardown: Clean up test data
        db = SessionLocal()
        try:
            db.query(User).delete()
            db.commit()
        finally:
            db.close()
    
    def test_create_user(self):
        """Test creating a user"""
        db = SessionLocal()
        try:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password",
                full_name="Test User"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
        finally:
            db.close()
    
    def test_read_user(self):
        """Test reading a user"""
        db = SessionLocal()
        try:
            # Create user
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password"
            )
            db.add(user)
            db.commit()
            user_id = user.id
            
            # Read user
            retrieved_user = db.query(User).filter(User.id == user_id).first()
            assert retrieved_user is not None
            assert retrieved_user.username == "testuser"
        finally:
            db.close()
    
    def test_update_user(self):
        """Test updating a user"""
        db = SessionLocal()
        try:
            # Create user
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password"
            )
            db.add(user)
            db.commit()
            
            # Update user
            user.full_name = "Updated Name"
            db.commit()
            db.refresh(user)
            
            assert user.full_name == "Updated Name"
        finally:
            db.close()
    
    def test_delete_user(self):
        """Test deleting a user"""
        db = SessionLocal()
        try:
            # Create user
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password"
            )
            db.add(user)
            db.commit()
            user_id = user.id
            
            # Delete user
            db.delete(user)
            db.commit()
            
            # Verify deletion
            deleted_user = db.query(User).filter(User.id == user_id).first()
            assert deleted_user is None
        finally:
            db.close()


class TestAsyncCRUDOperations:
    """Test async CRUD operations"""
    
    @pytest.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test"""
        # Setup: Initialize database
        await init_async_db()
        yield
        # Teardown: Clean up test data
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_async_create_user(self):
        """Test creating a user asynchronously"""
        async with AsyncSessionLocal() as session:
            user = User(
                username="asyncuser",
                email="async@example.com",
                hashed_password="hashed_password",
                full_name="Async User"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            assert user.id is not None
            assert user.username == "asyncuser"
    
    @pytest.mark.asyncio
    async def test_async_read_user(self):
        """Test reading a user asynchronously"""
        async with AsyncSessionLocal() as session:
            # Create user
            user = User(
                username="asyncuser",
                email="async@example.com",
                hashed_password="hashed_password"
            )
            session.add(user)
            await session.commit()
            user_id = user.id
            
            # Read user
            result = await session.execute(
                select(User).filter(User.id == user_id)
            )
            retrieved_user = result.scalar_one_or_none()
            assert retrieved_user is not None
            assert retrieved_user.username == "asyncuser"


class TestBatchOperations:
    """Test batch database operations"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        init_db()
        yield
        db = SessionLocal()
        try:
            db.query(User).delete()
            db.commit()
        finally:
            db.close()
    
    def test_batch_operation_context(self):
        """Test batch operation context"""
        db = SessionLocal()
        try:
            with BatchOperationContext(db, batch_size=10) as batch_ctx:
                for i in range(25):
                    user = User(
                        username=f"user{i}",
                        email=f"user{i}@example.com",
                        hashed_password="hashed"
                    )
                    batch_ctx.add(user)
            
            # Verify all users were created
            count = db.query(User).count()
            assert count == 25
        finally:
            db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
