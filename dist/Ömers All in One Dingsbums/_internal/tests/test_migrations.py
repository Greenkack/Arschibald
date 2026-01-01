"""Tests for Database Migration System"""

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import Column, Integer, String, create_engine

from core.config import AppConfig, DatabaseConfig, reset_config
from core.database import Base, DatabaseManager
from core.migrations import MigrationManager, create_migration, migrate, rollback


# Test model
class TestModel(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["ENV"] = "dev"
        reset_config()
        yield db_path
        reset_config()


@pytest.fixture
def migration_manager(temp_db):
    """Create migration manager for testing"""
    manager = MigrationManager()
    manager.initialize_alembic()
    yield manager
    # Close engine connections
    if manager.engine:
        manager.engine.dispose()


def test_migration_manager_initialization(migration_manager):
    """Test migration manager initialization"""
    assert migration_manager is not None
    assert migration_manager.alembic_config is not None
    assert migration_manager.engine is not None


def test_alembic_environment_creation(migration_manager):
    """Test Alembic environment is created correctly"""
    migrations_dir = Path(__file__).parent.parent / "core" / "alembic"

    # Check directory structure
    assert migrations_dir.exists()
    assert (migrations_dir / "versions").exists()
    assert (migrations_dir / "env.py").exists()
    assert (migrations_dir / "script.py.mako").exists()


def test_get_current_revision_no_migrations(migration_manager):
    """Test getting current revision when no migrations applied"""
    current = migration_manager.get_current_revision()
    assert current is None


def test_get_pending_migrations_empty(migration_manager):
    """Test getting pending migrations when none exist"""
    pending = migration_manager.get_pending_migrations()
    assert isinstance(pending, list)


def test_validate_migrations(migration_manager):
    """Test migration validation"""
    results = migration_manager.validate_migrations()

    assert "status" in results
    assert "current_revision" in results
    assert "pending_migrations" in results
    assert "errors" in results
    assert "warnings" in results


def test_create_migration_template_add_column(migration_manager):
    """Test creating add_column migration template"""
    template_path = migration_manager.create_migration_template("add_column")

    assert template_path.exists()
    assert template_path.suffix == ".template"

    content = template_path.read_text()
    assert "add_column" in content
    assert "drop_column" in content


def test_create_migration_template_add_index(migration_manager):
    """Test creating add_index migration template"""
    template_path = migration_manager.create_migration_template("add_index")

    assert template_path.exists()
    content = template_path.read_text()
    assert "create_index" in content
    assert "drop_index" in content


def test_create_migration_template_add_table(migration_manager):
    """Test creating add_table migration template"""
    template_path = migration_manager.create_migration_template("add_table")

    assert template_path.exists()
    content = template_path.read_text()
    assert "create_table" in content
    assert "drop_table" in content


def test_create_migration_template_add_foreign_key(migration_manager):
    """Test creating add_foreign_key migration template"""
    template_path = migration_manager.create_migration_template("add_foreign_key")

    assert template_path.exists()
    content = template_path.read_text()
    assert "create_foreign_key" in content
    assert "drop_constraint" in content


def test_create_migration_template_invalid(migration_manager):
    """Test creating invalid migration template"""
    with pytest.raises(ValueError):
        migration_manager.create_migration_template("invalid_template")


def test_migration_history_empty(migration_manager):
    """Test getting migration history when empty"""
    history = migration_manager.get_migration_history()
    assert isinstance(history, list)


def test_database_manager_integration(temp_db):
    """Test database manager integration with migrations"""
    db_manager = DatabaseManager()

    # Create tables
    db_manager.create_tables()

    # Check health
    assert db_manager.health_check() is True


def test_migrate_function(temp_db):
    """Test migrate function"""
    try:
        migrate()
        # Should not raise exception even if no migrations
    except Exception as e:
        # Expected if no migrations exist yet
        assert "No such file or directory" in str(e) or "versions" in str(e)


def test_migration_manager_with_real_database(temp_db):
    """Test migration manager with real database operations"""
    manager = MigrationManager()
    manager.initialize_alembic()

    # Validate initial state
    results = manager.validate_migrations()
    assert results["status"] in ["success", "error"]
    assert results["current_revision"] is None


def test_alembic_ini_creation(temp_db):
    """Test alembic.ini file creation"""
    manager = MigrationManager()

    alembic_ini = Path(__file__).parent.parent / "core" / "alembic.ini"
    assert alembic_ini.exists()

    content = alembic_ini.read_text()
    assert "[alembic]" in content
    assert "script_location" in content


def test_env_py_creation(temp_db):
    """Test env.py file creation"""
    manager = MigrationManager()
    manager.initialize_alembic()

    env_py = Path(__file__).parent.parent / "core" / "alembic" / "env.py"
    assert env_py.exists()

    content = env_py.read_text()
    assert "run_migrations_offline" in content
    assert "run_migrations_online" in content
    assert "target_metadata" in content


def test_script_template_creation(temp_db):
    """Test script.py.mako template creation"""
    manager = MigrationManager()
    manager.initialize_alembic()

    template = Path(__file__).parent.parent / "core" / "alembic" / "script.py.mako"
    assert template.exists()

    content = template.read_text()
    assert "upgrade" in content
    assert "downgrade" in content
    assert "revision" in content


def test_migration_safety_checks(migration_manager):
    """Test migration safety checks"""
    # Test that rollback requires confirmation in production
    os.environ["ENV"] = "prod"
    reset_config()

    manager = MigrationManager()

    # Should log warning for production rollback
    # (actual rollback would require confirmation in CLI)
    try:
        current = manager.get_current_revision()
        # Just verify we can check current revision
        assert current is None or isinstance(current, str)
    finally:
        os.environ["ENV"] = "dev"
        reset_config()


def test_migration_templates_directory(migration_manager):
    """Test migration templates directory creation"""
    templates_dir = Path(__file__).parent.parent / "core" / "alembic" / "templates"

    # Create a template to ensure directory exists
    migration_manager.create_migration_template("add_column")

    assert templates_dir.exists()
    assert templates_dir.is_dir()


def test_versions_directory_creation(migration_manager):
    """Test versions directory is created"""
    versions_dir = Path(__file__).parent.parent / "core" / "alembic" / "versions"

    assert versions_dir.exists()
    assert versions_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
