"""
Contract Management Pydantic Schemas

This module defines the request/response schemas for contract management API.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContractStatusEnum(str, Enum):
    """Contract status enumeration."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class ContractTypeEnum(str, Enum):
    """Contract type enumeration."""
    SERVICE = "service"
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    WARRANTY = "warranty"
    LEASE = "lease"
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"


class ApprovalStatusEnum(str, Enum):
    """Approval status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class SignatureStatusEnum(str, Enum):
    """E-signature status enumeration."""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"


# ==================== Contract Schemas ====================

class ContractBase(BaseModel):
    """Base contract schema."""
    title: str = Field(..., min_length=1, max_length=200)
    contract_type: ContractTypeEnum
    customer_id: int = Field(..., gt=0)
    template_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    value: float = Field(..., ge=0)
    currency: str = Field(default="EUR", max_length=3)
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    special_clauses: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_renew: bool = False
    renewal_notice_days: int = Field(default=30, ge=0)

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class ContractCreate(ContractBase):
    """Schema for creating a contract."""
    pass


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    contract_type: Optional[ContractTypeEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    value: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    special_clauses: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_renew: Optional[bool] = None
    renewal_notice_days: Optional[int] = Field(None, ge=0)


class ContractResponse(ContractBase):
    """Schema for contract response."""
    id: int
    contract_number: str
    status: ContractStatusEnum
    signed_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    termination_date: Optional[datetime] = None
    renewal_count: int
    document_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== Template Schemas ====================

class ContractTemplateBase(BaseModel):
    """Base contract template schema."""
    name: str = Field(..., min_length=1, max_length=200)
    contract_type: ContractTypeEnum
    title_template: str = Field(..., min_length=1, max_length=200)
    content_template: str = Field(..., min_length=1)
    terms_template: Optional[str] = None
    variables: Optional[List[str]] = None
    default_values: Optional[Dict[str, Any]] = None
    requires_approval: bool = True
    requires_signature: bool = True
    description: Optional[str] = None


class ContractTemplateCreate(ContractTemplateBase):
    """Schema for creating a contract template."""
    pass


class ContractTemplateUpdate(BaseModel):
    """Schema for updating a contract template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    title_template: Optional[str] = Field(None, min_length=1, max_length=200)
    content_template: Optional[str] = Field(None, min_length=1)
    terms_template: Optional[str] = None
    variables: Optional[List[str]] = None
    default_values: Optional[Dict[str, Any]] = None
    requires_approval: Optional[bool] = None
    requires_signature: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ContractTemplateResponse(ContractTemplateBase):
    """Schema for contract template response."""
    id: int
    is_active: bool
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== Approval Schemas ====================

class ContractApprovalCreate(BaseModel):
    """Schema for creating a contract approval request."""
    contract_id: int = Field(..., gt=0)
    approver_id: int = Field(..., gt=0)
    approval_level: int = Field(default=1, ge=1)
    comments: Optional[str] = None


class ContractApprovalDecision(BaseModel):
    """Schema for approval decision."""
    status: ApprovalStatusEnum
    comments: Optional[str] = None


class ContractApprovalResponse(BaseModel):
    """Schema for contract approval response."""
    id: int
    contract_id: int
    approver_id: int
    approval_level: int
    status: ApprovalStatusEnum
    decision_date: Optional[datetime] = None
    comments: Optional[str] = None
    requested_at: datetime

    class Config:
        from_attributes = True


# ==================== Signature Schemas ====================

class ContractSignatureRequest(BaseModel):
    """Schema for requesting a signature."""
    contract_id: int = Field(..., gt=0)
    signer_name: str = Field(..., min_length=1, max_length=200)
    signer_email: EmailStr
    signer_role: Optional[str] = Field(None, max_length=100)
    expires_in_days: int = Field(default=7, ge=1, le=30)


class ContractSignatureSubmit(BaseModel):
    """Schema for submitting a signature."""
    signature_data: str = Field(..., min_length=1)  # Base64 encoded
    signature_method: str = Field(..., max_length=50)
    verification_code: Optional[str] = None


class ContractSignatureResponse(BaseModel):
    """Schema for contract signature response."""
    id: int
    contract_id: int
    signer_name: str
    signer_email: str
    signer_role: Optional[str] = None
    status: SignatureStatusEnum
    signature_method: Optional[str] = None
    requested_at: datetime
    signed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_verified: bool

    class Config:
        from_attributes = True


# ==================== Renewal Schemas ====================

class ContractRenewalCreate(BaseModel):
    """Schema for creating a contract renewal."""
    contract_id: int = Field(..., gt=0)
    new_end_date: datetime
    new_value: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ContractRenewalResponse(BaseModel):
    """Schema for contract renewal response."""
    id: int
    contract_id: int
    renewal_number: int
    previous_end_date: datetime
    new_end_date: datetime
    previous_value: float
    new_value: float
    value_change_percent: Optional[float] = None
    is_automatic: bool
    renewal_date: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class ContractAnalyticsResponse(BaseModel):
    """Schema for contract analytics response."""
    period_start: datetime
    period_end: datetime
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    renewed_contracts: int
    terminated_contracts: int
    total_value: float
    average_value: float
    renewal_rate: float
    metrics_by_type: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ==================== List and Filter Schemas ====================

class ContractListFilters(BaseModel):
    """Schema for contract list filters."""
    customer_id: Optional[int] = None
    contract_type: Optional[ContractTypeEnum] = None
    status: Optional[ContractStatusEnum] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    auto_renew: Optional[bool] = None
    search: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class ContractListResponse(BaseModel):
    """Schema for contract list response."""
    total: int
    contracts: List[ContractResponse]


# ==================== Expiring Contracts Schema ====================

class ExpiringContractsRequest(BaseModel):
    """Schema for expiring contracts request."""
    days: int = Field(default=30, ge=1, le=365)
    include_auto_renew: bool = False
