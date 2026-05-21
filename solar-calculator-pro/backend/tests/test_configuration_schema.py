"""
Tests for Configuration Database Schema

This module tests the configuration database models, relationships, and constraints.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create Base for testing
Base = declarative_base()

# Import models after Base is defined
from models.configuration_models import (
    Configuration,
    ConfigurationVersion,
    ConfigurationAuditLog,
    ConfigurationBackup,
    ConfigurationValidationRule,
    ConfigurationTemplate
)

# Update Base reference in models
Configuration.__bases__ = (Base)
ConfigurationVersion.__bases__ = (Base)
ConfigurationAuditLog.__bases__ = (Base)
ConfigurationBackup.__bases__ = (Base)
ConfigurationValidationRule.__bases__ = (Base)
ConfigurationTemplate.__bases__ = (Base)


@pytest.fixture
def db_session():
    """Create in-memory database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestConfigurationModel:
    """Test Configuration model"""
    
    def test_create_configuration(self, db_session):
        """Test creating a basic configuration"""
        config = Configuration(
            key="test.setting",
            value="test_value",
            value_type="string",
            category="system",
            namespace="global",
            description="Test configuration"
        )
        db_session.add(config)
        db_session.commit()
        
        assert config.id is not None
        assert config.key == "test.setting"
        assert config.version == 1
        assert config.is_active is True
        assert config.created_at is not None
    
    def test_configuration_with_parent(self, db_session):
        """Test configuration inheritance"""
        parent = Configuration(
            key="theme.colors",
            value='{"primary": "#007bff"}',
            value_type="json",
            category="system",
            namespace="global"
        )
        db_session.add(parent)
        db_session.commit()
        
        child = Configuration(
            key="theme.colors.primary",
            value="#ff0000",
            value_type="string",
            category="system",
            namespace="solar",
            parent_id=parent.id
        )
        db_session.add(child)
        db_session.commit()
        
        assert child.parent_id == parent.id
        assert child.parent == parent
        assert child in parent.children
    
    def test_configuration_validation_schema(self, db_session):
        """Test configuration with validation schema"""
        validation_schema = {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        }
        
        config = Configuration(
            key="efficiency_percentage",
            value="85.5",
            value_type="number",
            category="module",
            namespace="solar",
            validation_schema=validation_schema
        )
        db_session.add(config)
        db_session.commit()
        
        assert config.validation_schema == validation_schema
    
    def test_configuration_defaults(self, db_session):
        """Test configuration default values"""
        config = Configuration(
            key="test.setting",
            value="custom_value",
            category="system"
        )
        db_session.add(config)
        db_session.commit()
        
        assert config.namespace == "global"
        assert config.version == 1
        assert config.is_active is True
        assert config.is_system is False
        assert config.is_encrypted is False
        assert config.is_sensitive is False
        assert config.is_required is False


class TestConfigurationVersion:
    """Test ConfigurationVersion model"""
    
    def test_create_version(self, db_session):
        """Test creating a version record"""
        config = Configuration(
            key="test.setting",
            value="initial_value",
            value_type="string",
            category="system",
            namespace="global"
        )
        db_session.add(config)
        db_session.commit()
        
        version = ConfigurationVersion(
            configuration_id=config.id,
            version_number=1,
            value="initial_value",
            value_type="string",
            change_type="created",
            created_by="admin"
        )
        db_session.add(version)
        db_session.commit()
        
        assert version.id is not None
        assert version.configuration_id == config.id
        assert version.configuration == config
    
    def test_version_history(self, db_session):
        """Test tracking version history"""
        config = Configuration(
            key="test.setting",
            value="v1",
            value_type="string",
            category="system",
            namespace="global"
        )
        db_session.add(config)
        db_session.commit()
        
        # Create multiple versions
        for i in range(1, 4):
            version = ConfigurationVersion(
                configuration_id=config.id,
                version_number=i,
                value=f"v{i}",
                value_type="string",
                change_type="updated" if i > 1 else "created",
                previous_value=f"v{i-1}" if i > 1 else None
            )
            db_session.add(version)
        
        db_session.commit()
        
        versions = db_session.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config.id
        ).order_by(ConfigurationVersion.version_number).all()
        
        assert len(versions) == 3
        assert versions[0].value == "v1"
        assert versions[2].value == "v3"
        assert versions[2].previous_value == "v2"


class TestConfigurationAuditLog:
    """Test ConfigurationAuditLog model"""
    
    def test_create_audit_log(self, db_session):
        """Test creating an audit log entry"""
        config = Configuration(
            key="test.setting",
            value="test_value",
            value_type="string",
            category="system",
            namespace="global"
        )
        db_session.add(config)
        db_session.commit()
        
        audit_log = ConfigurationAuditLog(
            configuration_id=config.id,
            action="create",
            user_id=1,
            username="admin",
            ip_address="192.168.1.100",
            new_value="test_value",
            status="success"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.configuration_id == config.id
        assert audit_log.action == "create"
        assert audit_log.timestamp is not None
    
    def test_audit_log_with_details(self, db_session):
        """Test audit log with action details"""
        audit_log = ConfigurationAuditLog(
            action="export",
            action_details={
                "format": "json",
                "namespace": "solar",
                "count": 50
            },
            user_id=1,
            username="admin",
            status="success"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.action_details["format"] == "json"
        assert audit_log.action_details["count"] == 50


class TestConfigurationBackup:
    """Test ConfigurationBackup model"""
    
    def test_create_backup(self, db_session):
        """Test creating a backup"""
        backup_data = {
            "configs": [
                {"key": "setting1", "value": "value1"},
                {"key": "setting2", "value": "value2"}
            ]
        }
        
        backup = ConfigurationBackup(
            backup_name="test_backup",
            backup_type="manual",
            description="Test backup",
            configuration_data=backup_data,
            configuration_count=2,
            status="completed",
            created_by="admin"
        )
        db_session.add(backup)
        db_session.commit()
        
        assert backup.id is not None
        assert backup.configuration_count == 2
        assert backup.status == "completed"
        assert backup.restore_count == 0
    
    def test_backup_with_retention(self, db_session):
        """Test backup with retention policy"""
        expires_at = datetime.now() + timedelta(days=30)
        
        backup = ConfigurationBackup(
            backup_name="retention_test",
            backup_type="automatic",
            configuration_data={"configs": []},
            configuration_count=0,
            retention_days=30,
            expires_at=expires_at,
            status="completed"
        )
        db_session.add(backup)
        db_session.commit()
        
        assert backup.retention_days == 30
        assert backup.expires_at is not None
    
    def test_backup_compression(self, db_session):
        """Test backup with compression"""
        backup = ConfigurationBackup(
            backup_name="compressed_backup",
            backup_type="manual",
            configuration_data={"configs": []},
            configuration_count=0,
            is_compressed=True,
            compression_algorithm="gzip",
            status="completed"
        )
        db_session.add(backup)
        db_session.commit()
        
        assert backup.is_compressed is True
        assert backup.compression_algorithm == "gzip"


class TestConfigurationValidationRule:
    """Test ConfigurationValidationRule model"""
    
    def test_create_validation_rule(self, db_session):
        """Test creating a validation rule"""
        rule = ConfigurationValidationRule(
            rule_name="positive_number",
            rule_type="range",
            description="Ensure number is positive",
            rule_definition={
                "type": "number",
                "minimum": 0
            },
            error_message="Value must be positive",
            applies_to_namespace="global",
            severity="error"
        )
        db_session.add(rule)
        db_session.commit()
        
        assert rule.id is not None
        assert rule.rule_name == "positive_number"
        assert rule.is_active is True
    
    def test_validation_rule_with_pattern(self, db_session):
        """Test validation rule with key pattern"""
        rule = ConfigurationValidationRule(
            rule_name="solar_settings",
            rule_type="schema",
            rule_definition={"type": "number"},
            applies_to_key_pattern="^solar\\..*",
            applies_to_namespace="solar",
            severity="warning"
        )
        db_session.add(rule)
        db_session.commit()
        
        assert rule.applies_to_key_pattern == "^solar\\..*"
        assert rule.severity == "warning"


class TestConfigurationTemplate:
    """Test ConfigurationTemplate model"""
    
    def test_create_template(self, db_session):
        """Test creating a configuration template"""
        template_data = {
            "efficiency": 0.85,
            "degradation": 0.005,
            "warranty_years": 25
        }
        
        template = ConfigurationTemplate(
            template_name="solar_defaults",
            template_type="module",
            description="Default solar calculator settings",
            configuration_data=template_data,
            category="solar",
            tags=["solar", "defaults", "calculator"]
        )
        db_session.add(template)
        db_session.commit()
        
        assert template.id is not None
        assert template.usage_count == 0
        assert template.is_active is True
    
    def test_template_usage_tracking(self, db_session):
        """Test template usage tracking"""
        template = ConfigurationTemplate(
            template_name="test_template",
            template_type="custom",
            configuration_data={"key": "value"}
        )
        db_session.add(template)
        db_session.commit()
        
        # Simulate usage
        template.usage_count += 1
        template.last_used_at = datetime.now()
        db_session.commit()
        
        assert template.usage_count == 1
        assert template.last_used_at is not None


class TestRelationships:
    """Test model relationships"""
    
    def test_configuration_versions_relationship(self, db_session):
        """Test configuration to versions relationship"""
        config = Configuration(
            key="test.setting",
            value="v1",
            value_type="string",
            category="system",
            namespace="global"
        )
        db_session.add(config)
        db_session.commit()
        
        # Add versions
        for i in range(1, 4):
            version = ConfigurationVersion(
                configuration_id=config.id,
                version_number=i,
                value=f"v{i}",
                value_type="string",
                change_type="updated"
            )
            db_session.add(version)
        db_session.commit()
        
        assert len(config.versions) == 3
    
    def test_configuration_audit_logs_relationship(self, db_session):
        """Test configuration to audit logs relationship"""
        config = Configuration(
            key="test.setting",
            value="test_value",
            value_type="string",
            category="system",
            namespace="global"
        )
        db_session.add(config)
        db_session.commit()
        
        # Add audit logs
        for action in ["create", "read", "update"]:
            log = ConfigurationAuditLog(
                configuration_id=config.id,
                action=action,
                username="admin",
                status="success"
            )
            db_session.add(log)
        db_session.commit()
        
        assert len(config.audit_logs) == 3


class TestConstraints:
    """Test database constraints"""
    
    def test_unique_template_name(self, db_session):
        """Test unique constraint on template name"""
        template1 = ConfigurationTemplate(
            template_name="unique_template",
            template_type="custom",
            configuration_data={}
        )
        db_session.add(template1)
        db_session.commit()
        
        template2 = ConfigurationTemplate(
            template_name="unique_template",
            template_type="custom",
            configuration_data={}
        )
        db_session.add(template2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_unique_validation_rule_name(self, db_session):
        """Test unique constraint on validation rule name"""
        rule1 = ConfigurationValidationRule(
            rule_name="unique_rule",
            rule_type="schema",
            rule_definition={}
        )
        db_session.add(rule1)
        db_session.commit()
        
        rule2 = ConfigurationValidationRule(
            rule_name="unique_rule",
            rule_type="schema",
            rule_definition={}
        )
        db_session.add(rule2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestIndexes:
    """Test database indexes"""
    
    def test_query_by_key_namespace(self, db_session):
        """Test querying by key and namespace (indexed)"""
        # Create multiple configurations
        for i in range(10):
            config = Configuration(
                key=f"test.setting{i}",
                value=f"value{i}",
                value_type="string",
                category="system",
                namespace="global" if i % 2 == 0 else "solar"
            )
            db_session.add(config)
        db_session.commit()
        
        # Query should use index
        result = db_session.query(Configuration).filter(
            Configuration.key == "test.setting0",
            Configuration.namespace == "global"
        ).first()
        
        assert result is not None
        assert result.key == "test.setting0"
    
    def test_query_by_category_active(self, db_session):
        """Test querying by category and is_active (indexed)"""
        # Create configurations
        for i in range(10):
            config = Configuration(
                key=f"test.setting{i}",
                value=f"value{i}",
                value_type="string",
                category="system" if i % 2 == 0 else "module",
                namespace="global",
                is_active=i % 3 != 0
            )
            db_session.add(config)
        db_session.commit()
        
        # Query should use index
        results = db_session.query(Configuration).filter(
            Configuration.category == "system",
            Configuration.is_active == True
        ).all()
        
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
