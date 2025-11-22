"""
Tests for Configuration Service

This module tests all functionality of the ConfigurationService including:
- CRUD operations
- Caching
- Validation
- Versioning and rollback
- Backup and restore
- Export and import
- Migration
"""

import sys
import os
import pytest
import json
import yaml
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.core.database import Base
except ImportError:
    # Fallback if backend.core.database doesn't exist
    Base = declarative_base()

from models.configuration_models import (
    Configuration,
    ConfigurationVersion,
    ConfigurationAuditLog,
    ConfigurationBackup
)
from models.configuration_schemas import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationSearch,
    ConfigurationExport,
    ConfigurationImport,
    ConfigurationBackupCreate,
    ConfigurationRestoreRequest,
    ValueType,
    ConfigCategory,
    BackupType
)
from services.configuration_service import ConfigurationService


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def config_service(db_session):
    """Create configuration service instance"""
    return ConfigurationService(db_session)


# ==================== CRUD Tests ====================

class TestConfigurationCRUD:
    """Test CRUD operations"""
    
    def test_create_configuration(self, config_service):
        """Test creating a configuration"""
        config_data = ConfigurationCreate(
            key="test.setting",
            value="test_value",
            value_type=ValueType.STRING,
            description="Test configuration",
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data, user="test_user")
        
        assert config.id is not None
        assert config.key == "test.setting"
        assert config.value == "test_value"
        assert config.namespace == "test"
        assert config.version == 1
        assert config.created_by == "test_user"
    
    def test_create_duplicate_key_fails(self, config_service):
        """Test that creating duplicate key in same namespace fails"""
        config_data = ConfigurationCreate(
            key="duplicate.key",
            value="value1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config_service.create_configuration(config_data)
        
        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise HTTPException
            config_service.create_configuration(config_data)
    
    def test_get_configuration_by_id(self, config_service):
        """Test getting configuration by ID"""
        config_data = ConfigurationCreate(
            key="test.get",
            value="get_value",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        created = config_service.create_configuration(config_data)
        retrieved = config_service.get_configuration(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.key == "test.get"
    
    def test_get_configuration_by_key(self, config_service):
        """Test getting configuration by key and namespace"""
        config_data = ConfigurationCreate(
            key="test.bykey",
            value="bykey_value",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config_service.create_configuration(config_data)
        retrieved = config_service.get_configuration_by_key("test.bykey", "test")
        
        assert retrieved is not None
        assert retrieved.key == "test.bykey"
        assert retrieved.namespace == "test"
    
    def test_get_configuration_value_with_type_conversion(self, config_service):
        """Test getting configuration value with type conversion"""
        # Number type
        config_service.create_configuration(ConfigurationCreate(
            key="test.number",
            value="42.5",
            value_type=ValueType.NUMBER,
            category=ConfigCategory.USER,
            namespace="test"
        ))
        
        value = config_service.get_configuration_value("test.number", "test")
        assert value == 42.5
        assert isinstance(value, float)
        
        # Boolean type
        config_service.create_configuration(ConfigurationCreate(
            key="test.bool",
            value="true",
            value_type=ValueType.BOOLEAN,
            category=ConfigCategory.USER,
            namespace="test"
        ))
        
        value = config_service.get_configuration_value("test.bool", "test")
        assert value is True
        assert isinstance(value, bool)
    
    def test_update_configuration(self, config_service):
        """Test updating configuration"""
        config_data = ConfigurationCreate(
            key="test.update",
            value="original",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data)
        original_version = config.version
        
        update_data = ConfigurationUpdate(value="updated")
        updated = config_service.update_configuration(config.id, update_data, user="updater")
        
        assert updated.value == "updated"
        assert updated.version == original_version + 1
        assert updated.updated_by == "updater"
    
    def test_delete_configuration(self, config_service):
        """Test deleting configuration (soft delete)"""
        config_data = ConfigurationCreate(
            key="test.delete",
            value="to_delete",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data)
        result = config_service.delete_configuration(config.id, user="deleter")
        
        assert result is True
        
        # Should still exist but inactive
        deleted = config_service.get_configuration(config.id, use_cache=False)
        assert deleted.is_active is False
    
    def test_search_configurations(self, config_service):
        """Test searching configurations"""
        # Create test configurations
        for i in range(5):
            config_service.create_configuration(ConfigurationCreate(
                key=f"search.test{i}",
                value=f"value{i}",
                value_type=ValueType.STRING,
                category=ConfigCategory.USER,
                namespace="search"
            ))
        
        search_params = ConfigurationSearch(
            namespace="search",
            limit=10,
            offset=0
        )
        
        results, total = config_service.search_configurations(search_params)
        
        assert len(results) == 5
        assert total == 5


# ==================== Caching Tests ====================

class TestConfigurationCaching:
    """Test caching functionality"""
    
    def test_cache_get_set(self, config_service):
        """Test cache get and set"""
        config_service.cache.set("test_key", "test_value")
        value = config_service.cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_expiration(self, config_service):
        """Test cache expiration"""
        config_service.cache._ttl_seconds = 1  # 1 second TTL
        config_service.cache.set("expire_key", "expire_value")
        
        # Should exist immediately
        assert config_service.cache.get("expire_key") == "expire_value"
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Should be expired
        assert config_service.cache.get("expire_key") is None
    
    def test_cache_clear_namespace(self, config_service):
        """Test clearing cache by namespace"""
        config_service.cache.set("ns1:key1", "value1")
        config_service.cache.set("ns1:key2", "value2")
        config_service.cache.set("ns2:key1", "value3")
        
        config_service.cache.clear_namespace("ns1")
        
        assert config_service.cache.get("ns1:key1") is None
        assert config_service.cache.get("ns1:key2") is None
        assert config_service.cache.get("ns2:key1") == "value3"


# ==================== Validation Tests ====================

class TestConfigurationValidation:
    """Test validation functionality"""
    
    def test_validate_with_json_schema(self, config_service):
        """Test validation with JSON schema"""
        schema = {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        }
        
        # Valid value
        result = config_service._validate_value("50", schema)
        assert result.is_valid is True
        
        # Invalid value
        result = config_service._validate_value("150", schema)
        assert result.is_valid is False
        assert len(result.errors) > 0


# ==================== Versioning Tests ====================

class TestConfigurationVersioning:
    """Test versioning and rollback functionality"""
    
    def test_version_created_on_create(self, config_service):
        """Test that version is created when configuration is created"""
        config_data = ConfigurationCreate(
            key="test.version",
            value="v1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data)
        versions = config_service.get_configuration_versions(config.id)
        
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert versions[0].value == "v1"
    
    def test_version_created_on_update(self, config_service):
        """Test that version is created when configuration is updated"""
        config_data = ConfigurationCreate(
            key="test.version.update",
            value="v1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data)
        
        # Update
        update_data = ConfigurationUpdate(value="v2")
        config_service.update_configuration(config.id, update_data)
        
        versions = config_service.get_configuration_versions(config.id)
        
        assert len(versions) == 2
        assert versions[0].version_number == 2  # Latest first
        assert versions[0].value == "v2"
        assert versions[1].version_number == 1
        assert versions[1].value == "v1"
    
    def test_rollback_configuration(self, config_service):
        """Test rolling back configuration to previous version"""
        config_data = ConfigurationCreate(
            key="test.rollback",
            value="v1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="test"
        )
        
        config = config_service.create_configuration(config_data)
        
        # Update to v2
        config_service.update_configuration(
            config.id,
            ConfigurationUpdate(value="v2")
        )
        
        # Update to v3
        config_service.update_configuration(
            config.id,
            ConfigurationUpdate(value="v3")
        )
        
        # Rollback to v1
        rolled_back = config_service.rollback_configuration(config.id, 1, user="rollback_user")
        
        assert rolled_back.value == "v1"
        assert rolled_back.version == 4  # New version created for rollback


# ==================== Backup and Restore Tests ====================

class TestConfigurationBackup:
    """Test backup and restore functionality"""
    
    def test_create_backup(self, config_service):
        """Test creating backup"""
        # Create some configurations
        for i in range(3):
            config_service.create_configuration(ConfigurationCreate(
                key=f"backup.test{i}",
                value=f"value{i}",
                value_type=ValueType.STRING,
                category=ConfigCategory.USER,
                namespace="backup"
            ))
        
        backup_data = ConfigurationBackupCreate(
            backup_name="test_backup",
            backup_type=BackupType.MANUAL,
            description="Test backup",
            namespace_filter=["backup"]
        )
        
        backup = config_service.create_backup(backup_data, user="backup_user")
        
        assert backup.id is not None
        assert backup.backup_name == "test_backup"
        assert backup.configuration_count == 3
        assert backup.status == "completed"
    
    def test_restore_backup_merge_mode(self, config_service):
        """Test restoring backup in merge mode"""
        # Create original configuration
        config_service.create_configuration(ConfigurationCreate(
            key="restore.test",
            value="original",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="restore"
        ))
        
        # Create backup
        backup_data = ConfigurationBackupCreate(
            backup_name="restore_test",
            backup_type=BackupType.MANUAL,
            namespace_filter=["restore"]
        )
        backup = config_service.create_backup(backup_data)
        
        # Update configuration
        config = config_service.get_configuration_by_key("restore.test", "restore")
        config_service.update_configuration(
            config.id,
            ConfigurationUpdate(value="modified")
        )
        
        # Restore backup
        restore_request = ConfigurationRestoreRequest(
            backup_id=backup.id,
            restore_mode="merge"
        )
        stats = config_service.restore_backup(restore_request, user="restore_user")
        
        assert stats["updated"] == 1
        
        # Verify restored value
        restored = config_service.get_configuration_by_key("restore.test", "restore", use_cache=False)
        assert restored.value == "original"


# ==================== Export/Import Tests ====================

class TestConfigurationExportImport:
    """Test export and import functionality"""
    
    def test_export_json(self, config_service):
        """Test exporting configurations to JSON"""
        # Create test configurations
        config_service.create_configuration(ConfigurationCreate(
            key="export.test1",
            value="value1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="export"
        ))
        
        export_params = ConfigurationExport(
            namespace_filter=["export"],
            format="json"
        )
        
        exported = config_service.export_configurations(export_params)
        
        assert exported is not None
        data = json.loads(exported)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["key"] == "export.test1"
    
    def test_export_yaml(self, config_service):
        """Test exporting configurations to YAML"""
        config_service.create_configuration(ConfigurationCreate(
            key="export.yaml",
            value="yaml_value",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="export"
        ))
        
        export_params = ConfigurationExport(
            namespace_filter=["export"],
            format="yaml"
        )
        
        exported = config_service.export_configurations(export_params)
        
        assert exported is not None
        data = yaml.safe_load(exported)
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_import_json(self, config_service):
        """Test importing configurations from JSON"""
        import_data = json.dumps([
            {
                "key": "import.test1",
                "value": "imported1",
                "value_type": "string",
                "category": "user",
                "namespace": "import"
            },
            {
                "key": "import.test2",
                "value": "imported2",
                "value_type": "string",
                "category": "user",
                "namespace": "import"
            }
        ])
        
        import_params = ConfigurationImport(
            data=import_data,
            format="json",
            merge_mode="merge"
        )
        
        stats = config_service.import_configurations(import_params, user="import_user")
        
        assert stats["created"] == 2
        assert stats["errors"] == []
        
        # Verify imported
        config1 = config_service.get_configuration_by_key("import.test1", "import")
        assert config1 is not None
        assert config1.value == "imported1"
    
    def test_import_with_dry_run(self, config_service):
        """Test import with dry run mode"""
        import_data = json.dumps([
            {
                "key": "dryrun.test",
                "value": "test",
                "value_type": "string",
                "category": "user",
                "namespace": "dryrun"
            }
        ])
        
        import_params = ConfigurationImport(
            data=import_data,
            format="json",
            dry_run=True
        )
        
        stats = config_service.import_configurations(import_params)
        
        assert stats["created"] == 1
        
        # Verify nothing was actually created
        config = config_service.get_configuration_by_key("dryrun.test", "dryrun")
        assert config is None


# ==================== Migration Tests ====================

class TestConfigurationMigration:
    """Test migration functionality"""
    
    def test_migrate_namespace(self, config_service):
        """Test migrating configurations between namespaces"""
        # Create configurations in source namespace
        for i in range(3):
            config_service.create_configuration(ConfigurationCreate(
                key=f"migrate.test{i}",
                value=f"value{i}",
                value_type=ValueType.STRING,
                category=ConfigCategory.USER,
                namespace="source"
            ))
        
        # Migrate
        stats = config_service.migrate_configuration(
            from_namespace="source",
            to_namespace="target",
            user="migrate_user"
        )
        
        assert stats["migrated"] == 3
        assert stats["errors"] == []
        
        # Verify migrated
        config = config_service.get_configuration_by_key("migrate.test0", "target")
        assert config is not None
        assert config.value == "value0"
    
    def test_migrate_with_key_mapping(self, config_service):
        """Test migration with key renaming"""
        config_service.create_configuration(ConfigurationCreate(
            key="old.key",
            value="value",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="source"
        ))
        
        key_mapping = {"old.key": "new.key"}
        
        stats = config_service.migrate_configuration(
            from_namespace="source",
            to_namespace="target",
            key_mapping=key_mapping
        )
        
        assert stats["migrated"] == 1
        
        # Verify new key
        config = config_service.get_configuration_by_key("new.key", "target")
        assert config is not None
        assert config.value == "value"


# ==================== Integration Tests ====================

class TestConfigurationServiceIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_lifecycle(self, config_service):
        """Test complete configuration lifecycle"""
        # 1. Create
        config_data = ConfigurationCreate(
            key="lifecycle.test",
            value="v1",
            value_type=ValueType.STRING,
            category=ConfigCategory.USER,
            namespace="lifecycle"
        )
        config = config_service.create_configuration(config_data, user="creator")
        assert config.version == 1
        
        # 2. Update
        config = config_service.update_configuration(
            config.id,
            ConfigurationUpdate(value="v2"),
            user="updater"
        )
        assert config.version == 2
        assert config.value == "v2"
        
        # 3. Get versions
        versions = config_service.get_configuration_versions(config.id)
        assert len(versions) == 2
        
        # 4. Rollback
        config = config_service.rollback_configuration(config.id, 1, user="rollbacker")
        assert config.value == "v1"
        assert config.version == 3
        
        # 5. Export
        export_params = ConfigurationExport(
            namespace_filter=["lifecycle"],
            format="json"
        )
        exported = config_service.export_configurations(export_params)
        assert "lifecycle.test" in exported
        
        # 6. Delete
        result = config_service.delete_configuration(config.id, user="deleter")
        assert result is True
        
        # 7. Verify inactive
        deleted = config_service.get_configuration(config.id, use_cache=False)
        assert deleted.is_active is False
    
    def test_backup_restore_workflow(self, config_service):
        """Test backup and restore workflow"""
        # Create configurations
        for i in range(5):
            config_service.create_configuration(ConfigurationCreate(
                key=f"workflow.test{i}",
                value=f"original{i}",
                value_type=ValueType.STRING,
                category=ConfigCategory.USER,
                namespace="workflow"
            ))
        
        # Create backup
        backup_data = ConfigurationBackupCreate(
            backup_name="workflow_backup",
            backup_type=BackupType.MANUAL,
            namespace_filter=["workflow"]
        )
        backup = config_service.create_backup(backup_data, user="backup_user")
        assert backup.configuration_count == 5
        
        # Modify configurations
        for i in range(5):
            config = config_service.get_configuration_by_key(f"workflow.test{i}", "workflow")
            config_service.update_configuration(
                config.id,
                ConfigurationUpdate(value=f"modified{i}")
            )
        
        # Restore backup
        restore_request = ConfigurationRestoreRequest(
            backup_id=backup.id,
            restore_mode="replace"
        )
        stats = config_service.restore_backup(restore_request, user="restore_user")
        assert stats["updated"] == 5
        
        # Verify restored
        for i in range(5):
            config = config_service.get_configuration_by_key(
                f"workflow.test{i}",
                "workflow",
                use_cache=False
            )
            assert config.value == f"original{i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
