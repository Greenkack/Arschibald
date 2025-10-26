"""Verification Script for Enhanced Database Layer"""

import sys
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import (
    Base,
    Repository,
    UnitOfWork,
    get_audit_logs,
    get_db_manager,
    init_database,
    run_tx,
)


# Test model
class TestEntity(Base):
    """Test entity for verification"""
    __tablename__ = 'test_entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


def verify_database_manager():
    """Verify DatabaseManager functionality"""
    print("\n=== Verifying DatabaseManager ===")

    try:
        db_manager = get_db_manager()
        assert db_manager is not None, "Failed to get database manager"
        print("✓ Database manager initialized")

        # Test session creation
        session = db_manager.get_session()
        assert session is not None, "Failed to create session"
        session.close()
        print("✓ Session creation works")

        # Test health check
        health = db_manager.health_check()
        assert health['healthy'] is True, "Database health check failed"
        assert health['connection_test'] is True, "Connection test failed"
        print("✓ Health check passed")

        # Test metrics
        metrics = db_manager.get_metrics()
        assert 'query_count' in metrics, "Metrics missing query_count"
        print("✓ Metrics collection works")

        return True

    except Exception as e:
        print(f"✗ DatabaseManager verification failed: {e}")
        return False


def verify_repository():
    """Verify Repository functionality"""
    print("\n=== Verifying Repository ===")

    try:
        db_manager = get_db_manager()
        db_manager.create_tables()

        repo = Repository(TestEntity, db_manager, enable_audit=True)
        repo.set_context(user_id="test_user", session_id="test_session")

        # Test create
        entity = repo.create(name="Test", value=100)
        assert entity.id is not None, "Create failed"
        print("✓ Create works")

        # Test get_by_id
        retrieved = repo.get_by_id(entity.id)
        assert retrieved is not None, "Get by ID failed"
        assert retrieved.name == "Test", "Retrieved wrong entity"
        print("✓ Get by ID works")

        # Test update
        updated = repo.update(entity.id, value=200)
        assert updated.value == 200, "Update failed"
        print("✓ Update works")

        # Test soft delete
        result = repo.delete(entity.id, soft=True)
        assert result is True, "Soft delete failed"

        retrieved = repo.get_by_id(entity.id)
        assert retrieved is None, "Soft deleted entity still visible"
        print("✓ Soft delete works")

        # Test restore
        restored = repo.restore(entity.id)
        assert restored is not None, "Restore failed"
        assert restored.deleted_at is None, "Entity not properly restored"
        print("✓ Restore works")

        # Test bulk operations
        data = [{"name": f"Bulk {i}", "value": i} for i in range(5)]
        entities = repo.bulk_create(data)
        assert len(entities) == 5, "Bulk create failed"
        print("✓ Bulk create works")

        updates = [{"id": e.id, "value": e.value * 2} for e in entities[:3]]
        count = repo.bulk_update(updates)
        assert count == 3, "Bulk update failed"
        print("✓ Bulk update works")

        ids = [e.id for e in entities[3:]]
        count = repo.bulk_delete(ids, soft=True)
        assert count == 2, "Bulk delete failed"
        print("✓ Bulk delete works")

        # Test pagination
        page = repo.paginate(page=1, page_size=10)
        assert 'items' in page, "Pagination failed"
        assert 'total' in page, "Pagination missing total"
        print("✓ Pagination works")

        # Test find_by
        results = repo.find_by(name="Test")
        assert len(results) > 0, "Find by failed"
        print("✓ Find by works")

        # Test count
        count = repo.count()
        assert count > 0, "Count failed"
        print("✓ Count works")

        # Test exists
        exists = repo.exists(entity.id)
        assert exists is True, "Exists failed"
        print("✓ Exists works")

        return True

    except Exception as e:
        print(f"✗ Repository verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_unit_of_work():
    """Verify UnitOfWork functionality"""
    print("\n=== Verifying UnitOfWork ===")

    try:
        db_manager = get_db_manager()

        # Test basic transaction
        with UnitOfWork(db_manager, user_id="test_user") as uow:
            repo = uow.get_repository(TestEntity, enable_audit=True)
            entity = repo.create(name="UoW Test", value=300)
            assert entity.id is not None, "UoW create failed"
        print("✓ Basic transaction works")

        # Test rollback
        try:
            with UnitOfWork(db_manager) as uow:
                repo = uow.get_repository(TestEntity)
                repo.create(name="Will Rollback", value=400)
                raise Exception("Test error")
        except Exception:
            pass

        # Verify entity was not created
        with db_manager.session_scope() as session:
            count = session.query(TestEntity).filter(
                TestEntity.name == "Will Rollback"
            ).count()
            assert count == 0, "Rollback failed"
        print("✓ Rollback works")

        # Test run_tx helper
        def create_entity(uow):
            repo = uow.get_repository(TestEntity)
            return repo.create(name="run_tx Test", value=500)

        entity = run_tx(create_entity, user_id="test_user")
        assert entity.id is not None, "run_tx failed"
        print("✓ run_tx helper works")

        return True

    except Exception as e:
        print(f"✗ UnitOfWork verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_audit_logging():
    """Verify audit logging functionality"""
    print("\n=== Verifying Audit Logging ===")

    try:
        db_manager = get_db_manager()
        repo = Repository(TestEntity, db_manager, enable_audit=True)
        repo.set_context(user_id="audit_user", session_id="audit_session")

        # Create entity
        entity = repo.create(name="Audit Test", value=600)

        # Check audit log
        logs = get_audit_logs(
            resource_type="test_entities",
            resource_id=str(entity.id),
            action="CREATE"
        )

        assert len(logs) > 0, "No audit logs found"
        assert logs[0].user_id == "audit_user", "Wrong user in audit log"
        assert logs[0].action == "CREATE", "Wrong action in audit log"
        print("✓ Audit logging works")

        # Update entity
        repo.update(entity.id, value=700)

        # Check update audit log
        logs = get_audit_logs(
            resource_type="test_entities",
            resource_id=str(entity.id),
            action="UPDATE"
        )

        assert len(logs) > 0, "No update audit logs found"
        print("✓ Update audit logging works")

        return True

    except Exception as e:
        print(f"✗ Audit logging verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_caching():
    """Verify repository caching"""
    print("\n=== Verifying Caching ===")

    try:
        db_manager = get_db_manager()
        repo = Repository(TestEntity, db_manager, enable_cache=True)

        # Create entity
        entity = repo.create(name="Cache Test", value=800)

        # First get - from database
        entity1 = repo.get_by_id(entity.id)
        assert entity1 is not None, "First get failed"

        # Second get - from cache
        entity2 = repo.get_by_id(entity.id)
        assert entity2 is not None, "Second get failed"

        # Update should invalidate cache
        repo.update(entity.id, value=900)

        # Next get should fetch from database
        entity3 = repo.get_by_id(entity.id)
        assert entity3.value == 900, "Cache invalidation failed"

        print("✓ Caching works")
        return True

    except Exception as e:
        print(f"✗ Caching verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_performance_monitoring():
    """Verify performance monitoring"""
    print("\n=== Verifying Performance Monitoring ===")

    try:
        db_manager = get_db_manager()

        # Reset metrics
        db_manager.reset_metrics()

        # Perform some operations
        with db_manager.session_scope() as session:
            session.execute("SELECT 1")

        # Check metrics
        metrics = db_manager.get_metrics()
        assert metrics['query_count'] > 0, "Query count not tracked"
        assert 'avg_query_time' in metrics, "Missing avg_query_time"

        print("✓ Performance monitoring works")
        return True

    except Exception as e:
        print(f"✗ Performance monitoring verification failed: {e}")
        return False


def main():
    """Run all verifications"""
    print("=" * 60)
    print("Enhanced Database Layer Verification")
    print("=" * 60)

    # Initialize database
    try:
        init_database(auto_migrate=False)
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

    # Run verifications
    results = []
    results.append(("DatabaseManager", verify_database_manager()))
    results.append(("Repository", verify_repository()))
    results.append(("UnitOfWork", verify_unit_of_work()))
    results.append(("Audit Logging", verify_audit_logging()))
    results.append(("Caching", verify_caching()))
    results.append(("Performance Monitoring", verify_performance_monitoring()))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")

    all_passed = all(result for _, result in results)

    print("=" * 60)
    if all_passed:
        print("✓ All verifications passed!")
        return True
    print("✗ Some verifications failed")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
