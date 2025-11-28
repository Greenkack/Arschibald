"""
Encryption Database Models

SQLAlchemy models for encryption settings and configuration.

Requirements: 11.3
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class EncryptionSettings(Base):
    """
    Encryption settings and configuration.
    """
    __tablename__ = "encryption_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(255), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EncryptionSettings(key='{self.setting_key}', active={self.is_active})>"


class EncryptedField(Base):
    """
    Registry of encrypted database fields.
    Tracks which fields in which tables are encrypted.
    """
    __tablename__ = "encrypted_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False, index=True)
    field_name = Column(String(255), nullable=False, index=True)
    encryption_algorithm = Column(String(100), default="Fernet")
    key_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EncryptedField(table='{self.table_name}', field='{self.field_name}')>"


class EncryptionKey(Base):
    """
    Encryption key metadata (not the actual key).
    Stores information about encryption keys without storing the keys themselves.
    """
    __tablename__ = "encryption_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(255), unique=True, nullable=False, index=True)
    key_type = Column(String(100), default="symmetric")  # symmetric, asymmetric
    algorithm = Column(String(100), default="Fernet")
    purpose = Column(String(255))  # database, file, communication
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_rotated_at = Column(DateTime(timezone=True))
    rotation_schedule = Column(String(100))  # daily, weekly, monthly, yearly
    
    def __repr__(self):
        return f"<EncryptionKey(name='{self.key_name}', type='{self.key_type}')>"


class EncryptionAuditLog(Base):
    """
    Audit log for encryption operations.
    Stores detailed logs of all encryption/decryption operations.
    """
    __tablename__ = "encryption_audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    operation = Column(String(100), nullable=False, index=True)  # encrypt, decrypt, key_rotation, etc.
    data_type = Column(String(100), nullable=False, index=True)  # database, file, communication
    user_id = Column(String(255), index=True)
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text)
    metadata = Column(JSON)  # Additional operation metadata
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    
    def __repr__(self):
        return f"<EncryptionAuditLog(operation='{self.operation}', success={self.success})>"


class EncryptionPolicy(Base):
    """
    Encryption policies and rules.
    Defines which data should be encrypted and how.
    """
    __tablename__ = "encryption_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    data_classification = Column(String(100))  # public, internal, confidential, restricted
    encryption_required = Column(Boolean, default=True)
    encryption_algorithm = Column(String(100), default="Fernet")
    key_rotation_days = Column(Integer, default=90)
    applies_to_tables = Column(JSON)  # List of table names
    applies_to_fields = Column(JSON)  # List of field patterns
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EncryptionPolicy(name='{self.policy_name}', classification='{self.data_classification}')>"
