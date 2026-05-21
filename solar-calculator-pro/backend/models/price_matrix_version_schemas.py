"""
Price Matrix Version Pydantic Schemas

This module defines the Pydantic schemas for price matrix versioning API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class VersionStatus(str, Enum):
    """Version status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Change type enumeration"""
    CREATED = "created"
    UPDATED = "updated"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVATED = "activated"
    ARCHIVED = "archived"
    ROLLED_BACK = "rolled_back"


# Request Schemas

class PriceMatrixVersionCreate(BaseModel):
    """Schema for creating a new price matrix version"""
    matrix_id: int
    version_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    matrix_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class PriceMatrixVersionUpdate(BaseModel):
    """Schema for updating a price matrix version"""
    version_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    matrix_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[VersionStatus] = None


class PriceMatrixVersionApprove(BaseModel):
    """Schema for approving a version"""
    approval_notes: Optional[str] = None


class PriceMatrixVersionReject(BaseModel):
    """Schema for rejecting a version"""
    rejection_reason: str = Field(..., min_length=1)


class PriceMatrixVersionRollback(BaseModel):
    """Schema for rolling back to a version"""
    rollback_reason: Optional[str] = None
    create_backup: bool = True


class PriceMatrixVersionCompare(BaseModel):
    """Schema for comparing two versions"""
    version_a_id: int
    version_b_id: int
    include_details: bool = True


# Response Schemas

class PriceMatrixVersionChangeResponse(BaseModel):
    """Schema for version change response"""
    id: int
    version_id: int
    change_type: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    change_description: Optional[str]
    changed_by: int
    changed_at: datetime

    class Config:
        from_attributes = True


class PriceMatrixVersionResponse(BaseModel):
    """Schema for price matrix version response"""
    id: int
    matrix_id: int
    version_number: int
    version_name: str
    description: Optional[str]
    matrix_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    status: str
    is_active: bool
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    changes: Optional[List[PriceMatrixVersionChangeResponse]] = None

    class Config:
        from_attributes = True


class PriceMatrixVersionListResponse(BaseModel):
    """Schema for version list response"""
    id: int
    matrix_id: int
    version_number: int
    version_name: str
    description: Optional[str]
    status: str
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceMatrixVersionComparisonResponse(BaseModel):
    """Schema for version comparison response"""
    id: int
    version_a_id: int
    version_b_id: int
    differences: Dict[str, Any]
    summary: Optional[Dict[str, Any]]
    compared_by: int
    compared_at: datetime

    class Config:
        from_attributes = True


class PriceMatrixVersionHistoryResponse(BaseModel):
    """Schema for version history response"""
    versions: List[PriceMatrixVersionListResponse]
    total_count: int
    active_version: Optional[PriceMatrixVersionListResponse]


class PriceMatrixVersionMigrationResult(BaseModel):
    """Schema for version migration result"""
    success: bool
    from_version: int
    to_version: int
    migrated_records: int
    errors: List[str] = []
    warnings: List[str] = []
    migration_time: float


class PriceMatrixVersionRollbackResult(BaseModel):
    """Schema for version rollback result"""
    success: bool
    rolled_back_to_version: int
    previous_version: int
    backup_version_id: Optional[int]
    rollback_time: float
