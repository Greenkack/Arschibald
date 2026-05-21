# System Configuration Database Models

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class SystemConfiguration(Base):
    """Global system configuration settings"""
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False)  # string, number, boolean, json
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    versions = relationship("ConfigurationVersion", back_populates="configuration", cascade="all, delete-orphan")


class ModuleConfiguration(Base):
    """Module-specific configuration settings"""
    __tablename__ = "module_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(100), nullable=False, index=True)  # solar, heatpump, pdf, crm, etc.
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True)
    validation_rules = Column(JSON)  # JSON schema for validation
    default_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        # Unique constraint on module_name + key
        {'sqlite_autoincrement': True})


class ConfigurationVersion(Base):
    """Version history for configuration changes"""
    __tablename__ = "configuration_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey("system_configurations.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text, nullable=False)
    change_reason = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    configuration = relationship("SystemConfiguration", back_populates="versions")


class ConfigurationTemplate(Base):
    """Predefined configuration templates"""
    __tablename__ = "configuration_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    template_data = Column(JSON, nullable=False)  # Complete configuration set
    is_system = Column(Boolean, default=False)  # System templates cannot be deleted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))


class ConfigurationValidation(Base):
    """Validation rules for configuration values"""
    __tablename__ = "configuration_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), nullable=False, index=True)
    validation_type = Column(String(50), nullable=False)  # regex, range, enum, custom
    validation_rule = Column(Text, nullable=False)
    error_message = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
