"""
Configuration Database Models

This module defines the database models for the dynamic configuration system.
Supports configuration versioning, inheritance, validation, backup, and audit logging.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from backend.core.database import Base


class Configuration(Base):
    """
    Main configuration table storing key-value configuration data.
    Supports hierarchical configuration with parent-child relationships.
    """
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=True)  # JSON string for complex values
    value_type = Column(String(50), nullable=False, default='string')  # string, number, boolean, json, array
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)  # system, user, module, feature
    namespace = Column(String(100), nullable=False, default='global', index=True)  # global, solar, heatpump, pdf, etc.
    
    # Inheritance support
    parent_id = Column(Integer, ForeignKey('configurations.id'), nullable=True, index=True)
    parent = relationship("Configuration", remote_side=[id], backref="children")
    
    # Versioning
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Validation
    validation_schema = Column(JSON, nullable=True)  # JSON schema for validation
    is_required = Column(Boolean, nullable=False, default=False)
    default_value = Column(Text, nullable=True)
    
    # Metadata
    is_system = Column(Boolean, nullable=False, default=False)  # System configs cannot be deleted
    is_encrypted = Column(Boolean, nullable=False, default=False)
    is_sensitive = Column(Boolean, nullable=False, default=False)  # Hide in UI
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Relationships
    versions = relationship("ConfigurationVersion", back_populates="configuration", cascade="all, delete-orphan")
    audit_logs = relationship("ConfigurationAuditLog", back_populates="configuration", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_config_key_namespace', 'key', 'namespace'),
        Index('idx_config_category_active', 'category', 'is_active'),
        Index('idx_config_namespace_active', 'namespace', 'is_active'))
    
    def __repr__(self):
        return f"<Configuration(id={self.id}, key='{self.key}', namespace='{self.namespace}', version={self.version})>"


class ConfigurationVersion(Base):
    """
    Configuration version history table.
    Stores all historical versions of configuration changes.
    """
    __tablename__ = "configuration_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=False, index=True)
    
    # Version data
    version_number = Column(Integer, nullable=False)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False)
    
    # Change tracking
    change_type = Column(String(50), nullable=False)  # created, updated, deleted, restored
    change_description = Column(Text, nullable=True)
    previous_value = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    
    # Relationships
    configuration = relationship("Configuration", back_populates="versions")
    
    # Indexes
    __table_args__ = (
        Index('idx_version_config_version', 'configuration_id', 'version_number'),
        Index('idx_version_created_at', 'created_at'))
    
    def __repr__(self):
        return f"<ConfigurationVersion(id={self.id}, config_id={self.configuration_id}, version={self.version_number})>"


class ConfigurationAuditLog(Base):
    """
    Configuration audit log table.
    Tracks all access and modification events for compliance and debugging.
    """
    __tablename__ = "configuration_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=True, index=True)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # read, create, update, delete, export, import
    action_details = Column(JSON, nullable=True)  # Additional context
    
    # User information
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(255), nullable=True)
    
    # Change data
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='success')  # success, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    configuration = relationship("Configuration", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_config_timestamp', 'configuration_id', 'timestamp'))
    
    def __repr__(self):
        return f"<ConfigurationAuditLog(id={self.id}, action='{self.action}', timestamp={self.timestamp})>"


class ConfigurationBackup(Base):
    """
    Configuration backup table.
    Stores complete snapshots of configuration state for disaster recovery.
    """
    __tablename__ = "configuration_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Backup metadata
    backup_name = Column(String(255), nullable=False)
    backup_type = Column(String(50), nullable=False, default='manual')  # manual, automatic, scheduled
    description = Column(Text, nullable=True)
    
    # Backup data
    configuration_data = Column(JSON, nullable=False)  # Complete configuration snapshot
    configuration_count = Column(Integer, nullable=False, default=0)
    
    # Compression and encryption
    is_compressed = Column(Boolean, nullable=False, default=True)
    is_encrypted = Column(Boolean, nullable=False, default=False)
    compression_algorithm = Column(String(50), nullable=True)  # gzip, bzip2, lzma
    
    # File information
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256 checksum
    
    # Status
    status = Column(String(50), nullable=False, default='completed')  # pending, in_progress, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Retention
    retention_days = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_by = Column(String(100), nullable=True)
    
    # Restore tracking
    restored_at = Column(DateTime(timezone=True), nullable=True)
    restored_by = Column(String(100), nullable=True)
    restore_count = Column(Integer, nullable=False, default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_backup_type_created', 'backup_type', 'created_at'),
        Index('idx_backup_status', 'status'),
        Index('idx_backup_expires', 'expires_at'))
    
    def __repr__(self):
        return f"<ConfigurationBackup(id={self.id}, name='{self.backup_name}', created_at={self.created_at})>"


class ConfigurationValidationRule(Base):
    """
    Configuration validation rules table.
    Defines validation schemas and rules for configuration values.
    """
    __tablename__ = "configuration_validation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule identification
    rule_name = Column(String(255), nullable=False, unique=True, index=True)
    rule_type = Column(String(50), nullable=False)  # schema, regex, range, enum, custom
    description = Column(Text, nullable=True)
    
    # Rule definition
    rule_definition = Column(JSON, nullable=False)  # JSON schema or rule parameters
    error_message = Column(Text, nullable=True)
    
    # Applicability
    applies_to_namespace = Column(String(100), nullable=True)
    applies_to_category = Column(String(100), nullable=True)
    applies_to_key_pattern = Column(String(255), nullable=True)  # Regex pattern
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    severity = Column(String(50), nullable=False, default='error')  # error, warning, info
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_validation_namespace', 'applies_to_namespace'),
        Index('idx_validation_active', 'is_active'))
    
    def __repr__(self):
        return f"<ConfigurationValidationRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"


class ConfigurationTemplate(Base):
    """
    Configuration templates table.
    Stores predefined configuration templates for quick setup.
    """
    __tablename__ = "configuration_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template metadata
    template_name = Column(String(255), nullable=False, unique=True, index=True)
    template_type = Column(String(50), nullable=False)  # system, module, feature, custom
    description = Column(Text, nullable=True)
    
    # Template data
    configuration_data = Column(JSON, nullable=False)  # Template configuration values
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Array of tags for searching
    
    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_system = Column(Boolean, nullable=False, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_template_type_active', 'template_type', 'is_active'),
        Index('idx_template_category', 'category'))
    
    def __repr__(self):
        return f"<ConfigurationTemplate(id={self.id}, name='{self.template_name}', type='{self.template_type}')>"
