"""
Standalone Tests for Configuration Database Schema

This module tests the configuration database models without requiring
the full backend infrastructure. It creates its own Base and engine.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import json

# Create Base for testing
Base = declarative_base()


# Recreate models for testing (simplified versions)
class Configuration(Base):
    """Configuration model for testing"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False, server_default='string')
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    namespace = Column(String(100), nullable=False, server_default='global', index=True)
    parent_id = Column(Integer, ForeignKey('configurations.id'), nullable=True, index=True)
    version = Column(Integer, nullable=False, server_default='1')
    is_active = Column(Boolean, nullable=False, server_default='1')
    validation_schema = Column(JSON, nullable=True)
    is_required = Column(Boolean, nullable=False, server_default='0')
    default_value = Column(Text, nullable=True)
    is_system = Column(Boolean, nullable=False, server_default='0')
    is_encrypted = Column(Boolean, nullable=False, server_default='0')
    is_sensitive = Column(Boolean, nullable=False, server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    parent = relationship("Configuration", remote_side=[id], backref="children")
    versions = relationship("ConfigurationVersion", back_populates="configuration")
    audit_logs = relationship("ConfigurationAuditLog", back_populates="configuration")


class ConfigurationVersion(Base):
    """Configuration version model for testing"""
    __tablename__ = "configuration_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False)
    change_type = Column(String(50), nullable=False)
    change_description = Column(Text, nullable=True)
    previous_value = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    
    configuration = relationship("Configuration", back_populates="versions")


class ConfigurationAuditLog(Base):
    """Configuration audit log model for testing"""
    __tablename__ = "configuration_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    action_details = Column(JSON, nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, server_default='success')
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    configuration = relationship("Configuration", back_populates="audit_logs")


class ConfigurationBackup(Base):
    """Configuration backup model for testing"""
    __tablename__ = "configuration_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_name = Column(String(255), nullable=False)
    backup_type = Column(String(50), nullable=False, server_default='manual')
    description = Column(Text, nullable=True)
    configuration_data = Column(JSON, nullable=False)
    configuration_count = Column(Integer, nullable=False, server_default='0')
    is_compressed = Column(Boolean, nullable=False, server_default='1')
    is_encrypted = Column(Boolean, nullable=False, server_default='0')
    compression_algorithm = Column(String(50), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)
    status = Column(String(50), nullable=False, server_default='completed')
    error_message = Column(Text, nullable=True)
    retention_days = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    restored_at = Column(DateTime(timezone=True), nullable=True)
    restored_by = Column(String(100), nullable=True)
    restore_count = Column(Integer, nullable=False, server_default='0')


class ConfigurationValidationRule(Base):
    """Configuration validation rule model for testing"""
    __tablename__ = "configuration_validation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False, unique=True, index=True)
    rule_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    rule_definition = Column(JSON, nullable=False)
    error_message = Column(Text, nullable=True)
    applies_to_namespace = Column(String(100), nullable=True)
    applies_to_category = Column(String(100), nullable=True)
    applies_to_key_pattern = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='1')
    severity = Column(String(50), nullable=False, server_default='error')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)


class ConfigurationTemplate(Base):
    """Configuration template model for testing"""
    __tablename__ = "configuration_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False, unique=True, index=True)
    template_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    configuration_data = Column(JSON, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    usage_count = Column(Integer, nullable=False, server_default='0')
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='1')
    is_system = Column(Boolean, nullable=False, server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)


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
        print(" test_create_configuration passed")
    
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
        print(" test_configuration_with_parent passed")
    
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
        print(" test_configuration_validation_schema passed")


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
        print(" test_create_version passed")


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
        print(" test_create_backup passed")


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
        print(" test_create_template passed")


def run_all_tests():
    """Run all tests manually"""
    print("\n" + "="*60)
    print("Configuration Database Schema Tests")
    print("="*60 + "\n")
    
    # Create in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    # Run tests
    test_classes = [
        TestConfigurationModel,
        TestConfigurationVersion,
        TestConfigurationBackup,
        TestConfigurationTemplate
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 60)
        
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            session = Session()
            try:
                method = getattr(test_instance, method_name)
                method(session)
                passed_tests += 1
            except Exception as e:
                print(f" {method_name} failed: {e}")
            finally:
                session.close()
    
    print("\n" + "="*60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    print("="*60 + "\n")
    
    if passed_tests == total_tests:
        print(" All tests passed!")
        return 0
    else:
        print(f" {total_tests - passed_tests} tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
