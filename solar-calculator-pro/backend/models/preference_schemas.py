# backend/models/preference_schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class PreferenceBase(BaseModel):
    """Base schema for preferences"""
    category: str = Field(..., description="Preference category (ui, calculation, pdf, etc.)")
    key: str = Field(..., description="Preference key")
    value: Any = Field(..., description="Preference value")
    data_type: str = Field(..., description="Data type (string, number, boolean, object, array)")

    @validator('data_type')
    def validate_data_type(cls, v):
        allowed_types = ['string', 'number', 'boolean', 'object', 'array']
        if v not in allowed_types:
            raise ValueError(f"data_type must be one of {allowed_types}")
        return v


class PreferenceCreate(PreferenceBase):
    """Schema for creating a preference"""
    pass


class PreferenceUpdate(BaseModel):
    """Schema for updating a preference"""
    value: Any = Field(..., description="New preference value")


class PreferenceResponse(PreferenceBase):
    """Schema for preference response"""
    id: int
    user_id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreferenceBulkUpdate(BaseModel):
    """Schema for bulk updating preferences"""
    preferences: List[Dict[str, Any]] = Field(..., description="List of preferences to update")


class PreferenceExport(BaseModel):
    """Schema for exporting preferences"""
    version: str = Field(default="1.0", description="Export format version")
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int
    preferences: Dict[str, Dict[str, Any]] = Field(..., description="Categorized preferences")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PreferenceImport(BaseModel):
    """Schema for importing preferences"""
    version: str = Field(..., description="Import format version")
    preferences: Dict[str, Dict[str, Any]] = Field(..., description="Categorized preferences")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing preferences")


class PreferenceTemplateBase(BaseModel):
    """Base schema for preference templates"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category")
    preferences: Dict[str, Any] = Field(..., description="Template preferences")


class PreferenceTemplateCreate(PreferenceTemplateBase):
    """Schema for creating a preference template"""
    pass


class PreferenceTemplateResponse(PreferenceTemplateBase):
    """Schema for preference template response"""
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreferenceSyncRequest(BaseModel):
    """Schema for preference sync request"""
    device_id: str = Field(..., description="Unique device identifier")
    device_name: Optional[str] = Field(None, description="Device name")
    preferences: Dict[str, Dict[str, Any]] = Field(..., description="Preferences to sync")


class PreferenceSyncResponse(BaseModel):
    """Schema for preference sync response"""
    sync_id: int
    status: str
    synced_at: datetime
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Conflicting preferences")

    class Config:
        from_attributes = True


class PreferenceResetRequest(BaseModel):
    """Schema for resetting preferences"""
    category: Optional[str] = Field(None, description="Category to reset (all if not specified)")
    keys: Optional[List[str]] = Field(None, description="Specific keys to reset")
    reset_to_defaults: bool = Field(default=True, description="Reset to system defaults")


class PreferenceSearchRequest(BaseModel):
    """Schema for searching preferences"""
    category: Optional[str] = Field(None, description="Filter by category")
    key_pattern: Optional[str] = Field(None, description="Search pattern for keys")
    include_defaults: bool = Field(default=True, description="Include default preferences")


class PreferenceStatistics(BaseModel):
    """Schema for preference statistics"""
    total_preferences: int
    categories: Dict[str, int]
    last_updated: Optional[datetime]
    sync_status: str
    device_count: int
