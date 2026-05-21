"""
Feature Flag Pydantic Schemas

This module defines the Pydantic models for feature flag API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FeatureFlagType(str, Enum):
    """Feature flag types"""
    GLOBAL = "global"
    USER = "user"
    ROLE = "role"
    PERCENTAGE = "percentage"


class FeatureFlagBase(BaseModel):
    """Base feature flag schema"""
    key: str = Field(..., min_length=1, max_length=255, description="Unique feature flag key")
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable name")
    description: Optional[str] = Field(None, description="Feature flag description")
    enabled: bool = Field(default=False, description="Whether the feature is enabled")
    flag_type: FeatureFlagType = Field(default=FeatureFlagType.GLOBAL, description="Type of feature flag")
    rollout_percentage: int = Field(default=0, ge=0, le=100, description="Percentage rollout (0-100)")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate feature flag key format"""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('Key must contain only alphanumeric characters, underscores, hyphens, and dots')
        return v.lower()


class FeatureFlagCreate(FeatureFlagBase):
    """Schema for creating a feature flag"""
    user_ids: Optional[List[int]] = Field(default=[], description="List of user IDs for user-based flags")
    role_ids: Optional[List[int]] = Field(default=[], description="List of role IDs for role-based flags")


class FeatureFlagUpdate(BaseModel):
    """Schema for updating a feature flag"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    flag_type: Optional[FeatureFlagType] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)
    user_ids: Optional[List[int]] = None
    role_ids: Optional[List[int]] = None


class FeatureFlagResponse(FeatureFlagBase):
    """Schema for feature flag response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    user_ids: List[int] = []
    role_ids: List[int] = []
    
    class Config:
        from_attributes = True


class FeatureFlagCheck(BaseModel):
    """Schema for checking if a feature is enabled"""
    key: str = Field(..., description="Feature flag key to check")
    user_id: Optional[int] = Field(None, description="User ID to check against")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate feature flag key format"""
        return v.lower()


class FeatureFlagCheckResponse(BaseModel):
    """Schema for feature flag check response"""
    key: str
    enabled: bool
    reason: str = Field(..., description="Reason why the flag is enabled/disabled")


class FeatureFlagBulkCheck(BaseModel):
    """Schema for checking multiple feature flags"""
    keys: List[str] = Field(..., description="List of feature flag keys to check")
    user_id: Optional[int] = Field(None, description="User ID to check against")


class FeatureFlagBulkCheckResponse(BaseModel):
    """Schema for bulk feature flag check response"""
    flags: dict[str, bool] = Field(..., description="Dictionary of flag keys to enabled status")


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    
    class Config:
        from_attributes = True
