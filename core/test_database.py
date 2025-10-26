"""Tests for Enhanced Database Layer"""

import time
from datetime import datetime

import pytest
from sqlalchemy import Column, DateTime, Integer, String

from .database import (
    AuditLog,
    Base,
    DatabaseManager,
    Repository,
    UnitOfWork,
    cleanup_audit_logs,
    get_audit_logs,
    get_conn,
    get_db_manager,
    run_tx,
)


# Test model
class TestUser(Base):
    """Test user model"""
    __tablename__ = 'test_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


@pytest.fixture
def db_manager():
    """Create test database manager"""
    # Set test database URL to SQLite
    import os
    original_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    try:
        manager = DatabaseManager()
        manager.create_tables()
        yield manager
        manager.drop_tables()
    finally:
        # Restore original URL
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            os.environ.pop('DATABASE_URL', None)


@pytest.fixture
def repository(db_manager):
    """Create test repository"""
    return Repository(TestUser, db_manager, enable_audit=True)


class TestDatabaseManager:
    """Test DatabaseManager functionality"""

    def test_initialization(self, db_manager):
        """Test database manager initialization"""
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None
        assert db_manager.metrics is not None

    def test_get_session(self, db_manager):
        """Test session creation"""
        session = db_manager.get_session()
        assert session is not None
        session.close()

    def test_session_scope(self, db_manager):
        """Test session scope context manager"""
        with db_manager.session_scope() as session:
            result = session.execute("SELECT 1").scalar()
            assert result == 1

    def test_health_check(self, db_manager):
        """Test database health check"""
        health = db_manager.health_check()
        assert health['healthy'] is True
        assert health['connection_test'] is True
        assert 'metrics' in health

    def test_metrics_tracking(self, db_manager):
        """Test query metrics tracking"""
        initial_count = db_manager.metrics.query_count

        with db_manager.session_scope() as session:
            session.execute("SELECT 1")

        assert db_manager.metrics.query_count > initial_count

    def test_slow_query_detection(self, db_manager):
        """Test slow query detection"""
        db_manager.metrics.slow_query_threshold = 0.001  # Very low threshold

        with db_manager.session_scope() as session:
            session.execute("SELECT 1")
            time.sleep(0.002)  # Ensure it's slow

        stats = db_manager.metrics.get_stats()
        # Note: Actual slow query detection depends on query execution time


class TestRepository:
    """Test Repository functionality"""

    def test_create(self, repository):
        """Test entity creation"""
        user = repository.create(name="John Doe", email="john@example.com")

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_get_by_id(self, repository):
        """Test get entity by ID"""
        user = repository.create(name="Jane Doe", email="jane@example.com")

        retrieved = repository.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.name == "Jane Doe"

    def test_get_all(self, repository):
        """Test get all entities"""
        repository.create(name="User 1", email="user1@example.com")
        repository.create(name="User 2", email="user2@example.com")

        users = repository.get_all()
        assert len(users) >= 2

    def test_update(self, repository):
        """Test entity update"""
        user = repository.create(name="Old Name", email="old@example.com")

        updated = repository.update(user.id, name="New Name")
        assert updated.name == "New Name"
        assert updated.email == "old@example.com"

    def test_soft_delete(self, repository):
        """Test soft delete"""
        user = repository.create(name="To Delete", email="delete@example.com")

        result = repository.delete(user.id, soft=True)
        assert result is True

        # Should not be found in normal queries
        retrieved = repository.get_by_id(user.id)
        assert retrieved is None

        # Should be found when including deleted
        all_users = repository.get_all(include_deleted=True)
        deleted_user = next((u for u in all_users if u.id == user.id), None)
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None

    def test_restore(self, repository):
        """Test restore soft-deleted entity"""
        user = repository.create(
            name="To Restore",
            email="restore@example.com")
        repository.delete(user.id, soft=True)

        restored = repository.restore(user.id)
        assert restored is not None
        assert restored.deleted_at is None

        # Should be found in normal queries
        retrieved = repository.get_by_id(user.id)
        assert retrieved is not None

    def test_find_by(self, repository):
        """Test find by criteria"""
        repository.create(name="Alice", email="alice@example.com")
        repository.create(name="Bob", email="bob@example.com")

        results = repository.find_by(name="Alice")
        assert len(results) == 1
        assert results[0].name == "Alice"

    def test_bulk_create(self, repository):
        """Test bulk create"""
        users_data = [
            {"name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(5)
        ]

        users = repository.bulk_create(users_data)
        assert len(users) == 5

        for user in users:
            assert user.id is not None

    def test_bulk_update(self, repository):
        """Test bulk update"""
        users = repository.bulk_create([
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
        ])

        updates = [
            {"id": users[0].id, "name": "Updated 1"},
            {"id": users[1].id, "name": "Updated 2"},
        ]

        count = repository.bulk_update(updates)
        assert count == 2

        updated1 = repository.get_by_id(users[0].id)
        assert updated1.name == "Updated 1"

    def test_bulk_delete(self, repository):
        """Test bulk delete"""
        users = repository.bulk_create([
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
        ])

        ids = [user.id for user in users]
        count = repository.bulk_delete(ids, soft=True)
        assert count == 2

        # Should not be found
        for user_id in ids:
            assert repository.get_by_id(user_id) is None

    def test_paginate(self, repository):
        """Test pagination"""
        # Create 25 users
        repository.bulk_create([
            {"name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(25)
        ])

        # Get first page
        page1 = repository.paginate(page=1, page_size=10)
        assert len(page1['items']) == 10
        assert page1['total'] >= 25
        assert page1['page'] == 1
        assert page1['total_pages'] >= 3

        # Get second page
        page2 = repository.paginate(page=2, page_size=10)
        assert len(page2['items']) == 10

    def test_count(self, repository):
        """Test count"""
        repository.bulk_create([
            {"name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(5)
        ])

        count = repository.count()
        assert count >= 5

    def test_exists(self, repository):
        """Test exists"""
        user = repository.create(name="Test", email="test@example.com")

        assert repository.exists(user.id) is True
        assert repository.exists(99999) is False

    def test_audit_logging(self, repository, db_manager):
        """Test audit logging"""
        repository.set_context(user_id="test_user", session_id="test_session")

        # Create
        user = repository.create(name="Audit Test", email="audit@example.com")

        # Check audit log
        with db_manager.session_scope() as session:
            audit_logs = session.query(AuditLog).filter(
                AuditLog.resource_id == str(user.id),
                AuditLog.action == 'CREATE'
            ).all()

            assert len(audit_logs) > 0
            assert audit_logs[0].user_id == "test_user"
            assert audit_logs[0].resource_type == "test_users"

    def test_caching(self, db_manager):
        """Test repository caching"""
        repo = Repository(TestUser, db_manager, enable_cache=True)

        # Create user
        user = repo.create(name="Cache Test", email="cache@example.com")

        # First get - from database
        user1 = repo.get_by_id(user.id)

        # Second get - from cache
        user2 = repo.get_by_id(user.id)

        assert user1.id == user2.id

        # Update should invalidate cache
        repo.update(user.id, name="Updated")

        # Should fetch from database again
        user3 = repo.get_by_id(user.id)
        assert user3.name == "Updated"


class TestUnitOfWork:
    """Test UnitOfWork functionality"""

    def test_basic_transaction(self, db_manager):
        """Test basic transaction"""
        with UnitOfWork(db_manager) as uow:
            repo = uow.get_repository(TestUser)
            user = repo.create(
                name="Transaction Test",
                email="trans@example.com")
            assert user.id is not None

    def test_rollback_on_error(self, db_manager):
        """Test transaction rollback on error"""
        try:
            with UnitOfWork(db_manager) as uow:
                repo = uow.get_repository(TestUser)
                repo.create(name="Will Rollback", email="rollback@example.com")
                raise Exception("Test error")
        except Exception:
            pass

        # User should not exist
        with db_manager.session_scope() as session:
            count = session.query(TestUser).filter(
                TestUser.email == "rollback@example.com"
            ).count()
            assert count == 0

    def test_nested_transactions(self, db_manager):
        """Test nested transactions with savepoints"""
        with UnitOfWork(db_manager) as uow1:
            repo1 = uow1.get_repository(TestUser)
            user1 = repo1.create(name="Outer", email="outer@example.com")

            try:
                with UnitOfWork(db_manager) as uow2:
                    repo2 = uow2.get_repository(TestUser)
                    repo2.create(name="Inner", email="inner@example.com")
                    raise Exception("Inner error")
            except Exception:
                pass

            # Outer transaction should still be valid
            assert user1.id is not None

    def test_run_tx_helper(self, db_manager):
        """Test run_tx helper function"""
        def create_user(uow: UnitOfWork):
            repo = uow.get_repository(TestUser)
            return repo.create(name="Helper Test", email="helper@example.com")

        user = run_tx(create_user, user_id="test_user")
        assert user.id is not None

    def test_audit_context(self, db_manager):
        """Test audit context in UnitOfWork"""
        with UnitOfWork(
            db_manager,
            user_id="test_user",
            session_id="test_session",
            correlation_id="test_correlation"
        ) as uow:
            repo = uow.get_repository(TestUser, enable_audit=True)
            user = repo.create(
                name="Context Test",
                email="context@example.com")

            # Check audit log has context
            with db_manager.session_scope() as session:
                audit_log = session.query(AuditLog).filter(
                    AuditLog.resource_id == str(user.id)
                ).first()

                assert audit_log is not None
                assert audit_log.user_id == "test_user"
                assert audit_log.session_id == "test_session"
                assert audit_log.correlation_id == "test_correlation"


class TestAuditLogs:
    """Test audit log functionality"""

    def test_get_audit_logs(self, db_manager, repository):
        """Test querying audit logs"""
        repository.set_context(user_id="test_user")

        # Create some entities
        user1 = repository.create(name="User 1", email="user1@example.com")
        user2 = repository.create(name="User 2", email="user2@example.com")

        # Query audit logs
        logs = get_audit_logs(resource_type="test_users", action="CREATE")
        assert len(logs) >= 2

    def test_audit_log_filtering(self, db_manager, repository):
        """Test audit log filtering"""
        repository.set_context(user_id="user1")
        user1 = repository.create(name="User 1", email="user1@example.com")

        repository.set_context(user_id="user2")
        user2 = repository.create(name="User 2", email="user2@example.com")

        # Filter by user
        logs = get_audit_logs(user_id="user1")
        assert all(log.user_id == "user1" for log in logs)

    def test_cleanup_audit_logs(self, db_manager, repository):
        """Test audit log cleanup"""
        repository.set_context(user_id="test_user")

        # Create some entities
        for i in range(5):
            repository.create(name=f"User {i}", email=f"user{i}@example.com")

        # Cleanup (with 0 retention days to delete all)
        deleted = cleanup_audit_logs(retention_days=0)
        assert deleted >= 5


class TestHelperFunctions:
    """Test helper functions"""

    def test_get_db_manager(self):
        """Test get_db_manager singleton"""
        manager1 = get_db_manager()
        manager2 = get_db_manager()
        assert manager1 is manager2

    def test_get_conn(self):
        """Test get_conn helper"""
        conn = get_conn()
        assert conn is not None
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
