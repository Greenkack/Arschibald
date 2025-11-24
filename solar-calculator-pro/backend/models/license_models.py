# License Management Database Models

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from backend.core.database import Base


class LicenseType(str, enum.Enum):
    """License type enumeration"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    LIFETIME = "lifetime"


class LicenseStatus(str, enum.Enum):
    """License status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING = "pending"


class License(Base):
    """License model for managing application licenses"""
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(255), unique=True, nullable=False, index=True)
    license_type = Column(SQLEnum(LicenseType), nullable=False)
    status = Column(SQLEnum(LicenseStatus), default=LicenseStatus.PENDING, nullable=False)
    
    # User/Organization info
    user_email = Column(String(255), nullable=False, index=True)
    organization_name = Column(String(255), nullable=True)
    
    # License validity
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feature flags
    enabled_features = Column(JSON, default=dict, nullable=False)
    
    # Usage limits
    max_users = Column(Integer, default=1, nullable=False)
    max_projects = Column(Integer, default=10, nullable=False)
    max_calculations_per_month = Column(Integer, default=100, nullable=False)
    
    # Hardware binding (optional)
    hardware_id = Column(String(255), nullable=True, index=True)
    machine_name = Column(String(255), nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict, nullable=False)
    notes = Column(String(1000), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)


class LicenseValidation(Base):
    """License validation history"""
    __tablename__ = "license_validations"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, nullable=False, index=True)
    license_key = Column(String(255), nullable=False, index=True)
    
    # Validation result
    is_valid = Column(Boolean, nullable=False)
    validation_message = Column(String(500), nullable=True)
    
    # Client info
    hardware_id = Column(String(255), nullable=True)
    machine_name = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    validated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Additional data
    metadata = Column(JSON, default=dict, nullable=False)


class LicenseFeature(Base):
    """Available features that can be licensed"""
    __tablename__ = "license_features"

    id = Column(Integer, primary_key=True, index=True)
    feature_key = Column(String(100), unique=True, nullable=False, index=True)
    feature_name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # Feature availability by license type
    available_in_trial = Column(Boolean, default=False, nullable=False)
    available_in_basic = Column(Boolean, default=False, nullable=False)
    available_in_professional = Column(Boolean, default=True, nullable=False)
    available_in_enterprise = Column(Boolean, default=True, nullable=False)
    available_in_lifetime = Column(Boolean, default=True, nullable=False)
    
    # Feature metadata
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class LicenseRenewal(Base):
    """License renewal history"""
    __tablename__ = "license_renewals"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, nullable=False, index=True)
    license_key = Column(String(255), nullable=False, index=True)
    
    # Renewal details
    old_expires_at = Column(DateTime(timezone=True), nullable=True)
    new_expires_at = Column(DateTime(timezone=True), nullable=False)
    renewal_period_days = Column(Integer, nullable=False)
    
    # Payment info (if applicable)
    payment_reference = Column(String(255), nullable=True)
    payment_amount = Column(Integer, nullable=True)  # in cents
    payment_currency = Column(String(3), default="EUR", nullable=False)
    
    # Timestamp
    renewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    renewed_by = Column(String(255), nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict, nullable=False)
