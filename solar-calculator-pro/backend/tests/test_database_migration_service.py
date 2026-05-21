"""
Tests for Database Migration Service
"""

import pytest
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from backend.core.database_abstraction import DatabaseType, DatabaseConfig
from backend.services.database_migration_service import (
    DatabaseMigrationService,
    MigrationProgress
)

Base = declarative_base()


class SourceModel(Base):
    """Source model for migration testing"""
    __tablename__ = "source_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    value = Column(Float)


class TestMigrationProgress:
    """Test MigrationProgress class"""
    
    def test_initial_state(self):
        """Test initial progress state"""
        progress = MigrationProgress()
        
        assert progress.total_tables == 0
        assert progress.completed_tables == 0
        assert progress.total_rows == 0
        assert progress.migrated_rows == 0
        assert progress.current_table is None
        assert progress.errors == []
    
    def test_progress_percentage(self):
        """Test progress percentage calculation"""
        progress = MigrationProgress()
        progress.total_rows = 100
        progress.migrated_rows = 50
        
        assert progress.get_progress_percentage() == 50.0
    
    def test_table_progress_percentage(self):
        """Test table progress percentage calculation"""
        progress = MigrationProgress()
        progress.total_tables = 10
        progress.completed_tables = 3
        
        assert progress.get_table_progress_percentage() == 30.0
    
    def test_to_dict(self):
        """Test converting progress to dictionary"""
        progress = MigrationProgress()
        progress.total_tables = 5
        progress.completed_tables = 2
        progress.total_rows = 1000
        progress.migrated_rows = 500
        progress.current_table = "test_table"
        
        result = progress.to_dict()
        
        assert result["total_tables"] == 5
        assert result["completed_tables"] == 2
        assert result["total_rows"] == 1000
        assert result["migrated_rows"] == 500
        assert result["current_table"] == "test_table"
        assert result["progress_percentage"] == 50.0
        assert result["table_progress_percentage"] == 40.0


class TestDatabaseMigrationService:
    """Test DatabaseMigrationService class"""
    
    @pytest.fixture
    def source_config(self):
        """Create source database configuration"""
        return DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
    
    @pytest.fixture
    def target_config(self):
        """Create target database configuration"""
        return DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
    
    @pytest.fixture
    def migration_service(self, source_config, target_config):
        """Create migration service"""
        return DatabaseMigrationService(source_config, target_config)
    
    def test_initialization(self, migration_service):
        """Test service initialization"""
        assert migration_service.source_manager is not None
        assert migration_service.target_manager is not None
        assert isinstance(migration_service.progress, MigrationProgress)
    
    def test_validate_migration(self, migration_service):
        """Test migration validation"""
        result = migration_service.validate_migration()
        
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert result["valid"] is True
    
    def test_get_table_list(self, migration_service):
        """Test getting table list"""
        # Setup source database with tables
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        tables = migration_service.get_table_list()
        
        assert isinstance(tables, list)
        assert "source_table" in tables
        
        migration_service.source_manager.disconnect()
    
    def test_count_rows(self, migration_service):
        """Test counting rows in table"""
        # Setup source database with data
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        # Insert test data
        session = migration_service.source_manager.get_session()
        for i in range(10):
            session.add(SourceModel(name=f"test_{i}", value=float(i)))
        session.commit()
        session.close()
        
        # Count rows
        count = migration_service.count_rows("source_table")
        assert count == 10
        
        migration_service.source_manager.disconnect()
    
    def test_migrate_table_schema(self, migration_service):
        """Test migrating table schema"""
        # Setup source database
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        # Setup target database
        migration_service.target_manager.connect()
        
        # Migrate schema
        success = migration_service.migrate_table_schema("source_table")
        assert success
        
        # Verify table exists in target
        from sqlalchemy import inspect
        inspector = inspect(migration_service.target_manager.adapter.engine)
        tables = inspector.get_table_names()
        assert "source_table" in tables
        
        migration_service.source_manager.disconnect()
        migration_service.target_manager.disconnect()
    
    def test_migrate_table_data(self, migration_service):
        """Test migrating table data"""
        # Setup source database with data
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        session = migration_service.source_manager.get_session()
        for i in range(100):
            session.add(SourceModel(name=f"test_{i}", value=float(i)))
        session.commit()
        session.close()
        
        # Setup target database
        migration_service.target_manager.adapter.Base = Base
        migration_service.target_manager.connect()
        migration_service.migrate_table_schema("source_table")
        
        # Migrate data
        success = migration_service.migrate_table_data("source_table", batch_size=25)
        assert success
        
        # Verify data in target
        target_session = migration_service.target_manager.get_session()
        from sqlalchemy import MetaData, Table
        metadata = MetaData()
        metadata.reflect(bind=migration_service.target_manager.adapter.engine)
        target_table = metadata.tables["source_table"]
        count = target_session.query(target_table).count()
        assert count == 100
        target_session.close()
        
        migration_service.source_manager.disconnect()
        migration_service.target_manager.disconnect()
    
    def test_migrate_all(self, migration_service):
        """Test migrating all tables"""
        # Setup source database with data
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        session = migration_service.source_manager.get_session()
        for i in range(50):
            session.add(SourceModel(name=f"test_{i}", value=float(i)))
        session.commit()
        session.close()
        
        # Setup target database
        migration_service.target_manager.adapter.Base = Base
        migration_service.target_manager.connect()
        
        # Migrate all
        progress = migration_service.migrate_all(batch_size=10)
        
        assert progress.total_tables > 0
        assert progress.completed_tables > 0
        assert progress.total_rows == 50
        assert progress.migrated_rows == 50
        assert progress.start_time is not None
        assert progress.end_time is not None
        
        migration_service.source_manager.disconnect()
        migration_service.target_manager.disconnect()
    
    def test_verify_migration(self, migration_service):
        """Test verifying migration"""
        # Setup and migrate
        migration_service.source_manager.adapter.Base = Base
        migration_service.source_manager.connect()
        migration_service.source_manager.create_tables()
        
        session = migration_service.source_manager.get_session()
        for i in range(20):
            session.add(SourceModel(name=f"test_{i}", value=float(i)))
        session.commit()
        session.close()
        
        migration_service.target_manager.adapter.Base = Base
        migration_service.target_manager.connect()
        migration_service.migrate_all()
        
        # Verify
        result = migration_service.verify_migration()
        
        assert result["success"] is True
        assert result["tables_verified"] > 0
        assert result["tables_failed"] == 0
        assert len(result["row_count_matches"]) > 0
        assert len(result["row_count_mismatches"]) == 0
        
        migration_service.source_manager.disconnect()
        migration_service.target_manager.disconnect()
    
    def test_rollback_migration(self, migration_service):
        """Test rolling back migration"""
        # Setup target database with tables
        migration_service.target_manager.adapter.Base = Base
        migration_service.target_manager.connect()
        migration_service.target_manager.create_tables()
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(migration_service.target_manager.adapter.engine)
        tables_before = inspector.get_table_names()
        assert len(tables_before) > 0
        
        migration_service.target_manager.disconnect()
        
        # Rollback
        success = migration_service.rollback_migration()
        assert success
        
        # Verify tables are dropped
        migration_service.target_manager.connect()
        inspector = inspect(migration_service.target_manager.adapter.engine)
        tables_after = inspector.get_table_names()
        assert len(tables_after) == 0
        
        migration_service.target_manager.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
