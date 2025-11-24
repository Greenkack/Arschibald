# License Management Pydantic Schemas

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class LicenseTypeEnum(str, Enum):
    """License type enumeration"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    LIFETIME = "lifetime"


class LicenseStatusEnum(str, Enum):
    """License status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING = "pending"


class LicenseCreate(BaseModel):
    """Schema for creating a new license"""
    license_type: LicenseTypeEnum
    user_email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    organization_name: Optional[str] = None
    expires_at: Optional[datetime] = None
    enabled_features: Dict[str, bool] = Field(default_factory=dict)
    max_users: int = Field(default=1, ge=1)
    max_projects: int = Field(default=10, ge=1)
    max_calculations_per_month: int = Field(default=100, ge=1)
    hardware_id: Optional[str] = None
    machine_name: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LicenseUpdate(BaseModel):
    """Schema for updating a license"""
    status: Optional[LicenseStatusEnum] = None
    expires_at: Optional[datetime] = None
    enabled_features: Optional[Dict[str, bool]] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_projects: Optional[int] = Field(None, ge=1)
    max_calculations_per_month: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LicenseResponse(BaseModel):
    """Schema for license response"""
    id: int
    license_key: str
    license_type: LicenseTypeEnum
    status: LicenseStatusEnum
    user_email: str
    organization_name: Optional[str]
    issued_at: datetime
    expires_at: Optional[datetime]
    activated_at: Optional[datetime]
    last_validated_at: Optional[datetime]
    enabled_features: Dict[str, bool]
    max_users: int
    max_projects: int
    max_calculations_per_month: int
    hardware_id: Optional[str]
    machine_name: Optional[str]
    metadata: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    is_expired: bool
    days_until_expiry: Optional[int]
    is_active: bool
    
    class Config:
        orm_mode = True


class LicenseValidationRequest(BaseModel):
    """Schema for license validation request"""
    license_key: str = Field(..., min_length=10)
    hardware_id: Optional[str] = None
    machine_name: Optional[str] = None
    features_to_check: Optional[List[str]] = None


class LicenseValidationResponse(BaseModel):
    """Schema for license validation response"""
    is_valid: bool
    license_key: str
    status: LicenseStatusEnum
    license_type: LicenseTypeEnum
    message: str
    expires_at: Optional[datetime]
    days_until_expiry: Optional[int]
    enabled_features: Dict[str, bool]
    feature_access: Dict[str, bool]
    warnings: List[str] = Field(default_factory=list)


class LicenseRenewalRequest(BaseModel):
    """Schema for license renewal request"""
    license_key: str
    renewal_period_days: int = Field(..., ge=1, le=3650)  # Max 10 years
    payment_reference: Optional[str] = None
    payment_amount: Optional[int] = None  # in cents
    payment_currency: str = Field(default="EUR", regex=r'^[A-Z]{3}$')


class LicenseRenewalResponse(BaseModel):
    """Schema for license renewal response"""
    license_id: int
    license_key: str
    old_expires_at: Optional[datetime]
    new_expires_at: datetime
    renewal_period_days: int
    renewed_at: datetime
    message: str


class LicenseFeatureCreate(BaseModel):
    """Schema for creating a license feature"""
    feature_key: str = Field(..., regex=r'^[a-z0-9_]+$')
    feature_name: str
    description: Optional[str] = None
    available_in_trial: bool = False
    available_in_basic: bool = False
    available_in_professional: bool = True
    available_in_enterprise: bool = True
    available_in_lifetime: bool = True
    category: Optional[str] = None


class LicenseFeatureResponse(BaseModel):
    """Schema for license feature response"""
    id: int
    feature_key: str
    feature_name: str
    description: Optional[str]
    available_in_trial: bool
    available_in_basic: bool
    available_in_professional: bool
    available_in_enterprise: bool
    available_in_lifetime: bool
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class LicenseReportRequest(BaseModel):
    """Schema for license report request"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    license_types: Optional[List[LicenseTypeEnum]] = None
    statuses: Optional[List[LicenseStatusEnum]] = None
    include_validations: bool = False
    include_renewals: bool = False


class LicenseReportResponse(BaseModel):
    """Schema for license report response"""
    total_licenses: int
    active_licenses: int
    expired_licenses: int
    suspended_licenses: int
    revoked_licenses: int
    pending_licenses: int
    licenses_by_type: Dict[str, int]
    licenses_expiring_soon: List[Dict[str, Any]]
    recent_validations: Optional[List[Dict[str, Any]]] = None
    recent_renewals: Optional[List[Dict[str, Any]]] = None
    generated_at: datetime


class LicenseActivationRequest(BaseModel):
    """Schema for license activation"""
    license_key: str
    hardware_id: str
    machine_name: Optional[str] = None


class LicenseActivationResponse(BaseModel):
    """Schema for license activation response"""
    success: bool
    message: str
    license: Optional[LicenseResponse] = None
