"""Tests for Database Migration Manager"""

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import Column, String

from .config import reset_config
from .database import Base, get_db_manager
from .migration_manager import (
    MigrationManager,
    get_migration_manager,
    get_migration_status,
    migrate,
)
from .migration_templates import MigrationTemplates, generate_migration_code


# Test model for migrations
class TestUser(Base):
    """Test user model"""

    __tablename__ = "test_users"

    id = Column(String(36), primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Set environment variable
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    reset_config()

    yield db_path

    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()
    reset_config()


@pytest.fixture
def migration_manager(temp_db):
    """Create migration manager for testing"""
    return MigrationManager()


class TestMigrationManager:
    """Test MigrationManager class"""

    def test_initialization(self, migration_manager):
        """Test migration manager initialization"""
        assert migration_manager is not None
        assert migration_manager.alembic_cfg is not None
        assert migration_manager.script_dir is not None

    def test_get_current_revision_no_migrations(self, migration_manager):
        """Test getting current revision when no migrations applied"""
        # Initialize database first
        db_manager = get_db_manager()
        db_manager.create_tables()

        current = migration_manager.get_current_revision()
        # Should be None when no migrations have been applied
        assert current is None or current == "base"

    def test_get_head_revision(self, migration_manager):
        """Test getting head revision"""
        head = migration_manager.get_head_revision()
        # May be None if no migrations exist yet
        assert head is None or isinstance(head, str)

    def test_has_pending_migrations(self, migration_manager):
        """Test checking for pending migrations"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        has_pending = migration_manager.has_pending_migrations()
        assert isinstance(has_pending, bool)

    def test_get_pending_migrations(self, migration_manager):
        """Test getting list of pending migrations"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        pending = migration_manager.get_pending_migrations()
        assert isinstance(pending, list)

    def test_verify_migrations(self, migration_manager):
        """Test migration verification"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        results = migration_manager.verify_migrations()

        assert "status" in results
        assert "current_revision" in results
        assert "head_revision" in results
        assert "pending_migrations" in results
        assert "issues" in results
        assert results["status"] in ["ok", "warning", "error"]

    def test_get_migration_history(self, migration_manager):
        """Test getting migration history"""
        history = migration_manager.get_migration_history()
        assert isinstance(history, list)


class TestMigrationFunctions:
    """Test migration helper functions"""

    def test_get_migration_manager(self, temp_db):
        """Test getting global migration manager"""
        manager1 = get_migration_manager()
        manager2 = get_migration_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_get_migration_status(self, temp_db):
        """Test getting migration status"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        status = get_migration_status()

        assert "current_revision" in status
        assert "head_revision" in status
        assert "pending_migrations" in status
        assert "has_pending" in status
        assert isinstance(status["has_pending"], bool)

    def test_migrate_no_pending(self, temp_db):
        """Test migrate function with no pending migrations"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        # Should succeed even with no migrations
        result = migrate(auto_run=True)
        assert result is True

    def test_migrate_auto_run_false(self, temp_db):
        """Test migrate function with auto_run=False"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        result = migrate(auto_run=False)
        assert result is True


class TestMigrationTemplates:
    """Test migration templates"""

    def test_add_column_template(self):
        """Test add column template"""
        result = MigrationTemplates.add_column_template(
            table_name="users",
            column_name="age",
            column_type="sa.Integer()",
            nullable=True,
            default=0,
            comment="User age",
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "users" in result["upgrade"]
        assert "age" in result["upgrade"]
        assert "drop_column" in result["downgrade"]

    def test_add_index_template(self):
        """Test add index template"""
        result = MigrationTemplates.add_index_template(
            table_name="users",
            column_names=["email"],
            unique=True,
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "create_index" in result["upgrade"]
        assert "drop_index" in result["downgrade"]
        assert "unique" in result["upgrade"]

    def test_add_foreign_key_template(self):
        """Test add foreign key template"""
        result = MigrationTemplates.add_foreign_key_template(
            table_name="posts",
            column_name="user_id",
            ref_table="users",
            ref_column="id",
            ondelete="CASCADE",
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "create_foreign_key" in result["upgrade"]
        assert "drop_constraint" in result["downgrade"]
        assert "CASCADE" in result["upgrade"]

    def test_create_table_template(self):
        """Test create table template"""
        columns = [
            {"name": "username", "type": "sa.String(100)", "nullable": False},
            {"name": "email", "type": "sa.String(255)", "nullable": False},
        ]

        result = MigrationTemplates.create_table_template(
            table_name="users",
            columns=columns,
            with_timestamps=True,
            with_soft_delete=True,
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "create_table" in result["upgrade"]
        assert "drop_table" in result["downgrade"]
        assert "username" in result["upgrade"]
        assert "created_at" in result["upgrade"]
        assert "deleted_at" in result["upgrade"]

    def test_rename_column_template(self):
        """Test rename column template"""
        result = MigrationTemplates.rename_column_template(
            table_name="users",
            old_name="name",
            new_name="full_name",
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "alter_column" in result["upgrade"]
        assert "full_name" in result["upgrade"]

    def test_add_check_constraint_template(self):
        """Test add check constraint template"""
        result = MigrationTemplates.add_check_constraint_template(
            table_name="users",
            constraint_name="check_age_positive",
            condition="age >= 0",
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "create_check_constraint" in result["upgrade"]
        assert "drop_constraint" in result["downgrade"]

    def test_data_migration_template(self):
        """Test data migration template"""
        result = MigrationTemplates.data_migration_template(
            description="Update user status",
            upgrade_sql="UPDATE users SET status = 'active' WHERE status IS NULL",
            downgrade_sql="UPDATE users SET status = NULL WHERE status = 'active'",
        )

        assert "upgrade" in result
        assert "downgrade" in result
        assert "UPDATE users" in result["upgrade"]

    def test_generate_migration_code(self):
        """Test generate_migration_code function"""
        result = generate_migration_code(
            "add_column",
            table_name="users",
            column_name="age",
            column_type="sa.Integer()",
        )

        assert "upgrade" in result
        assert "downgrade" in result

    def test_generate_migration_code_invalid_template(self):
        """Test generate_migration_code with invalid template"""
        with pytest.raises(ValueError, match="Unknown template"):
            generate_migration_code("invalid_template")


class TestMigrationIntegration:
    """Integration tests for migration system"""

    def test_full_migration_workflow(self, temp_db):
        """Test complete migration workflow"""
        # Initialize database
        db_manager = get_db_manager()
        db_manager.create_tables()

        # Get migration status
        status = get_migration_status()
        assert status is not None

        # Verify migrations
        manager = get_migration_manager()
        results = manager.verify_migrations()
        assert results["status"] in ["ok", "warning", "error"]

    def test_migration_with_auto_run(self, temp_db):
        """Test migration with automatic execution"""
        # This should initialize database and run migrations
        from .database import init_database

        init_database(auto_migrate=True)

        # Verify database is initialized
        db_manager = get_db_manager()
        assert db_manager.health_check()


def test_migration_templates_comprehensive():
    """Comprehensive test of all migration templates"""
    templates = MigrationTemplates()

    # Test all template methods exist and return correct structure
    template_methods = [
        ("add_column_template", {
            "table_name": "test",
            "column_name": "col",
            "column_type": "sa.String()",
        }),
        ("add_index_template", {
            "table_name": "test",
            "column_names": ["col"],
        }),
        ("add_foreign_key_template", {
            "table_name": "test",
            "column_name": "ref_id",
            "ref_table": "ref",
        }),
        ("create_table_template", {
            "table_name": "test",
            "columns": [{"name": "col", "type": "sa.String()"}],
        }),
        ("rename_column_template", {
            "table_name": "test",
            "old_name": "old",
            "new_name": "new",
        }),
        ("add_check_constraint_template", {
            "table_name": "test",
            "constraint_name": "check",
            "condition": "col > 0",
        }),
        ("data_migration_template", {
            "description": "test",
            "upgrade_sql": "SELECT 1",
        }),
    ]

    for method_name, kwargs in template_methods:
        method = getattr(templates, method_name)
        result = method(**kwargs)

        assert isinstance(result, dict)
        assert "upgrade" in result
        assert "downgrade" in result
        assert isinstance(result["upgrade"], str)
        assert isinstance(result["downgrade"], str)
        assert len(result["upgrade"]) > 0
        assert len(result["downgrade"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
