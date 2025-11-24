"""
Contract Management Database Models

This module defines the database models for contract management including
contracts, contract templates, approval workflows, and e-signatures.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class ContractStatus(str, enum.Enum):
    """Contract status enumeration."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class ContractType(str, enum.Enum):
    """Contract type enumeration."""
    SERVICE = "service"
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    WARRANTY = "warranty"
    LEASE = "lease"
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class SignatureStatus(str, enum.Enum):
    """E-signature status enumeration."""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"


class Contract(Base):
    """Contract model."""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=True)
    
    # Contract details
    title = Column(String(200), nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False, index=True)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT, nullable=False, index=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    signed_date = Column(DateTime, nullable=True)
    renewal_date = Column(DateTime, nullable=True)
    termination_date = Column(DateTime, nullable=True)
    
    # Financial
    value = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    payment_terms = Column(Text, nullable=True)
    
    # Content
    terms_and_conditions = Column(Text, nullable=True)
    special_clauses = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Renewal
    auto_renew = Column(Boolean, default=False)
    renewal_notice_days = Column(Integer, default=30)
    renewal_count = Column(Integer, default=0)
    
    # Document
    document_url = Column(String(500), nullable=True)
    document_hash = Column(String(64), nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    approvals = relationship("ContractApproval", back_populates="contract", cascade="all, delete-orphan")
    signatures = relationship("ContractSignature", back_populates="contract", cascade="all, delete-orphan")
    renewals = relationship("ContractRenewal", back_populates="contract", cascade="all, delete-orphan")


class ContractTemplate(Base):
    """Contract template model."""
    __tablename__ = "contract_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False, index=True)
    
    # Template content
    title_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    terms_template = Column(Text, nullable=True)
    
    # Variables
    variables = Column(JSON, nullable=True)  # List of variable names used in template
    default_values = Column(JSON, nullable=True)  # Default values for variables
    
    # Settings
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    requires_signature = Column(Boolean, default=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class ContractApproval(Base):
    """Contract approval workflow model."""
    __tablename__ = "contract_approvals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Approval details
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_level = Column(Integer, default=1)  # For multi-level approvals
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    
    # Decision
    decision_date = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)
    
    # Tracking
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="approvals")


class ContractSignature(Base):
    """E-signature model."""
    __tablename__ = "contract_signatures"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Signer details
    signer_name = Column(String(200), nullable=False)
    signer_email = Column(String(200), nullable=False)
    signer_role = Column(String(100), nullable=True)
    
    # Signature details
    status = Column(SQLEnum(SignatureStatus), default=SignatureStatus.PENDING, nullable=False, index=True)
    signature_data = Column(Text, nullable=True)  # Base64 encoded signature image
    signature_method = Column(String(50), nullable=True)  # e.g., "drawn", "typed", "uploaded"
    
    # IP and device tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Dates
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    signed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Verification
    verification_code = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="signatures")


class ContractRenewal(Base):
    """Contract renewal tracking model."""
    __tablename__ = "contract_renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Renewal details
    renewal_number = Column(Integer, nullable=False)
    previous_end_date = Column(DateTime, nullable=False)
    new_end_date = Column(DateTime, nullable=False)
    
    # Financial
    previous_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    value_change_percent = Column(Float, nullable=True)
    
    # Status
    is_automatic = Column(Boolean, default=False)
    renewal_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    contract = relationship("Contract", back_populates="renewals")


class ContractAnalytics(Base):
    """Contract analytics and metrics model."""
    __tablename__ = "contract_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Metrics
    total_contracts = Column(Integer, default=0)
    active_contracts = Column(Integer, default=0)
    expired_contracts = Column(Integer, default=0)
    renewed_contracts = Column(Integer, default=0)
    terminated_contracts = Column(Integer, default=0)
    
    # Financial metrics
    total_value = Column(Float, default=0.0)
    average_value = Column(Float, default=0.0)
    renewal_rate = Column(Float, default=0.0)
    
    # By type
    metrics_by_type = Column(JSON, nullable=True)
    
    # Tracking
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
