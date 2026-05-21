"""
Tests for Database Migration System
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from migrations.migration_manager import (
    MigrationManager, MigrationStep, MigrationType, MigrationStatus
)
from migrations.data_transformer import DataTransformer
from migrations.data_validator import DataValidator
from migrations.progress_tracker import ProgressTracker


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    
    # Create test tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                full_name TEXT,
                status TEXT
            )
        """))
        
        # Insert test data
        conn.execute(text("""
            INSERT INTO users (username, full_name, status)
            VALUES 
                ('john_doe', 'John Doe', '1'),
                ('jane_smith', 'Jane Smith', '1'),
                ('bob_jones', 'Bob Jones', '0')
        """))
        conn.commit()
    
    return engine


@pytest.fixture
def migration_manager(test_db):
    """Create migration manager"""
    return MigrationManager(str(test_db.url))


@pytest.fixture
def session(test_db):
    """Create database session"""
    SessionLocal = sessionmaker(bind=test_db)
    session = SessionLocal()
    yield session
    session.close()


class TestMigrationManager:
    """Test migration manager functionality"""
    
    def test_register_migration(self, migration_manager):
        """Test migration registration"""
        migration = MigrationStep(
            id="test_001",
            name="Test Migration",
            description="Test migration step",
            type=MigrationType.SCHEMA,
            up_sql="SELECT 1"
        )
        
        migration_manager.register_migration(migration)
        
        assert len(migration_manager.migrations) == 1
        assert migration_manager.migrations[0].id == "test_001"
    
    def test_duplicate_migration_rejected(self, migration_manager):
        """Test that duplicate migrations are rejected"""
        migration = MigrationStep(
            id="test_001",
            name="Test Migration",
            description="Test",
            type=MigrationType.SCHEMA,
            up_sql="SELECT 1"
        )
        
        migration_manager.register_migration(migration)
        
        with pytest.raises(ValueError, match="already registered"):
            migration_manager.register_migration(migration)
    
    def test_dependency_resolution(self, migration_manager):
        """Test dependency resolution"""
        migration_1 = MigrationStep(
            id="test_001",
            name="Migration 1",
            description="First migration",
            type=MigrationType.SCHEMA,
            up_sql="SELECT 1",
            dependencies=[]
        )
        
        migration_2 = MigrationStep(
            id="test_002",
            name="Migration 2",
            description="Second migration",
            type=MigrationType.SCHEMA,
            up_sql="SELECT 1",
            dependencies=["test_001"]
        )
        
        # Register in wrong order
        migration_manager.register_migration(migration_2)
        migration_manager.register_migration(migration_1)
        
        # Should resolve to correct order
        ordered = migration_manager._resolve_dependencies()
        
        assert ordered[0].id == "test_001"
        assert ordered[1].id == "test_002"
    
    def test_migration_execution(self, migration_manager):
        """Test migration execution"""
        migration = MigrationStep(
            id="test_add_column",
            name="Add Email Column",
            description="Add email column to users",
            type=MigrationType.SCHEMA,
            up_sql="ALTER TABLE users ADD COLUMN email TEXT",
            down_sql="ALTER TABLE users DROP COLUMN email"
        )
        
        migration_manager.register_migration(migration)
        result = migration_manager.migrate()
        
        assert result['status'] == 'completed'
        assert result['migrations_executed'] == 1
        assert result['migrations_failed'] == 0
    
    def test_migration_rollback(self, migration_manager):
        """Test migration rollback"""
        migration = MigrationStep(
            id="test_add_column",
            name="Add Email Column",
            description="Add email column",
            type=MigrationType.SCHEMA,
            up_sql="ALTER TABLE users ADD COLUMN email TEXT",
            down_sql="ALTER TABLE users DROP COLUMN email"
        )
        
        migration_manager.register_migration(migration)
        
        # Execute migration
        migration_manager.migrate()
        
        # Rollback
        result = migration_manager.rollback()
        
        assert result['status'] == 'completed'
        assert result['migrations_rolled_back'] == 1
    
    def test_dry_run(self, migration_manager):
        """Test dry run mode"""
        migration = MigrationStep(
            id="test_001",
            name="Test Migration",
            description="Test",
            type=MigrationType.SCHEMA,
            up_sql="ALTER TABLE users ADD COLUMN test TEXT"
        )
        
        migration_manager.register_migration(migration)
        result = migration_manager.migrate(dry_run=True)
        
        assert result['status'] == 'dry_run'
        assert len(result['migrations_to_execute']) == 1
        
        # Verify migration was not actually executed
        status = migration_manager.get_migration_status()
        assert status['applied_migrations'] == 0


class TestDataTransformer:
    """Test data transformation functionality"""
    
    def test_transform_column(self, session):
        """Test column transformation"""
        transformer = DataTransformer(session)
        
        rows = transformer.transform_column(
            table='users',
            column='username',
            transform_func=lambda x: x.upper()
        )
        
        assert rows == 3
        
        # Verify transformation
        result = session.execute(text("SELECT username FROM users")).fetchall()
        assert all(row[0].isupper() for row in result)
    
    def test_map_values(self, session):
        """Test value mapping"""
        transformer = DataTransformer(session)
        
        status_map = {
            '0': 'inactive',
            '1': 'active'
        }
        
        rows = transformer.map_values(
            table='users',
            column='status',
            value_map=status_map
        )
        
        assert rows == 3
        
        # Verify mapping
        result = session.execute(text("SELECT status FROM users")).fetchall()
        statuses = [row[0] for row in result]
        assert 'active' in statuses
        assert 'inactive' in statuses
    
    def test_normalize_text(self, session):
        """Test text normalization"""
        # Add test data with messy text
        session.execute(text("""
            INSERT INTO users (username, full_name, status)
            VALUES ('  TEST_USER  ', '  Test   User  ', '1')
        """))
        session.commit()
        
        transformer = DataTransformer(session)
        
        rows = transformer.normalize_text(
            table='users',
            column='username',
            lowercase=True,
            strip=True,
            remove_extra_spaces=True
        )
        
        assert rows > 0
        
        # Verify normalization
        result = session.execute(text("""
            SELECT username FROM users WHERE id = 
            (SELECT MAX(id) FROM users)
        """)).scalar()
        
        assert result == 'test_user'
    
    def test_split_column(self, session):
        """Test column splitting"""
        # Add columns for split
        session.execute(text("ALTER TABLE users ADD COLUMN first_name TEXT"))
        session.execute(text("ALTER TABLE users ADD COLUMN last_name TEXT"))
        session.commit()
        
        transformer = DataTransformer(session)
        
        rows = transformer.split_column(
            table='users',
            source_column='full_name',
            target_columns=['first_name', 'last_name'],
            separator=' '
        )
        
        assert rows == 3
        
        # Verify split
        result = session.execute(text("""
            SELECT first_name, last_name FROM users WHERE username = 'john_doe'
        """)).fetchone()
        
        assert result[0] == 'John'
        assert result[1] == 'Doe'
    
    def test_deduplicate_rows(self, session):
        """Test row deduplication"""
        # Add duplicate
        session.execute(text("""
            INSERT INTO users (username, full_name, status)
            VALUES ('john_doe', 'John Doe Duplicate', '1')
        """))
        session.commit()
        
        transformer = DataTransformer(session)
        
        rows_deleted = transformer.deduplicate_rows(
            table='users',
            unique_columns=['username'],
            keep='first'
        )
        
        assert rows_deleted == 1
        
        # Verify only one john_doe remains
        count = session.execute(text("""
            SELECT COUNT(*) FROM users WHERE username = 'john_doe'
        """)).scalar()
        
        assert count == 1


class TestDataValidator:
    """Test data validation functionality"""
    
    def test_table_exists(self, session):
        """Test table existence validation"""
        validator = DataValidator(session)
        validator.add_table_exists('users')
        
        result = validator.validate()
        
        assert result['valid']
        assert result['passed'] == 1
    
    def test_column_exists(self, session):
        """Test column existence validation"""
        validator = DataValidator(session)
        validator.add_column_exists('users', 'username')
        
        result = validator.validate()
        
        assert result['valid']
    
    def test_not_null(self, session):
        """Test NOT NULL validation"""
        validator = DataValidator(session)
        validator.add_not_null('users', 'username')
        
        result = validator.validate()
        
        assert result['valid']
    
    def test_unique(self, session):
        """Test uniqueness validation"""
        validator = DataValidator(session)
        validator.add_unique('users', 'username')
        
        result = validator.validate()
        
        assert result['valid']
    
    def test_unique_fails_on_duplicates(self, session):
        """Test uniqueness validation fails on duplicates"""
        # Add duplicate
        session.execute(text("""
            INSERT INTO users (username, full_name, status)
            VALUES ('john_doe', 'Duplicate', '1')
        """))
        session.commit()
        
        validator = DataValidator(session)
        validator.add_unique('users', 'username')
        
        result = validator.validate()
        
        assert not result['valid']
        assert result['failed'] == 1
    
    def test_custom_validation(self, session):
        """Test custom validation"""
        def check_user_count(s):
            count = s.execute(text("SELECT COUNT(*) FROM users")).scalar()
            return count >= 3
        
        validator = DataValidator(session)
        validator.add_custom(
            name='min_users',
            description='At least 3 users must exist',
            validation_func=check_user_count
        )
        
        result = validator.validate()
        
        assert result['valid']


class TestProgressTracker:
    """Test progress tracking functionality"""
    
    def test_progress_tracking(self):
        """Test basic progress tracking"""
        tracker = ProgressTracker(total_steps=3)
        
        assert tracker.state.percentage == 0.0
        
        tracker.start_step("Step 1")
        tracker.complete_step()
        
        assert tracker.state.completed_steps == 1
        assert 30 < tracker.state.percentage < 40
        
        tracker.start_step("Step 2")
        tracker.complete_step()
        
        assert tracker.state.completed_steps == 2
        assert 60 < tracker.state.percentage < 70
        
        tracker.start_step("Step 3")
        tracker.complete_step()
        
        assert tracker.state.completed_steps == 3
        assert tracker.state.percentage == 100.0
        assert tracker.state.status == "completed"
    
    def test_step_progress(self):
        """Test step progress updates"""
        tracker = ProgressTracker(total_steps=1)
        
        tracker.start_step("Processing")
        tracker.update_step_progress(0.5)
        
        assert tracker.state.current_step_progress == 0.5
        assert 40 < tracker.state.percentage < 60
    
    def test_progress_callbacks(self):
        """Test progress callbacks"""
        callback_called = []
        
        def callback(state):
            callback_called.append(state.percentage)
        
        tracker = ProgressTracker(total_steps=2)
        tracker.add_callback(callback)
        
        tracker.start_step("Step 1")
        tracker.complete_step()
        
        assert len(callback_called) >= 2
        assert callback_called[-1] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
