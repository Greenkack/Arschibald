"""
Component Toggle Pydantic Schemas

Request and response schemas for component toggle API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.models.component_toggle_models import (
    ComponentToggleCategory,
    ComponentToggleType
)


class ComponentToggleBase(BaseModel):
    """Base component toggle schema"""
    category: ComponentToggleCategory
    component_key: str = Field(..., min_length=1, max_length=255)
    component_name: str = Field(..., min_length=1, max_length=255)
    enabled: bool = True
    toggle_type: ComponentToggleType = ComponentToggleType.FEATURE
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = {}
    description: Optional[str] = Field(None, max_length=500)


class ComponentToggleCreate(ComponentToggleBase):
    """Schema for creating a component toggle"""
    pass


class ComponentToggleUpdate(BaseModel):
    """Schema for updating a component toggle"""
    enabled: Optional[bool] = None
    component_name: Optional[str] = Field(None, min_length=1, max_length=255)
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)


class ComponentToggleResponse(ComponentToggleBase):
    """Schema for component toggle response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ComponentToggleListResponse(BaseModel):
    """Schema for list of component toggles"""
    toggles: List[ComponentToggleResponse]
    total: int


# Specific toggle request schemas

class ChartToggleRequest(BaseModel):
    """Request to toggle a chart"""
    chart_type: str = Field(..., description="Type of chart (line_chart, bar_chart, etc.)")
    enabled: bool = Field(..., description="Whether the chart should be visible")


class FormFieldToggleRequest(BaseModel):
    """Request to toggle a form field"""
    form_name: str = Field(..., description="Name of the form")
    field_key: str = Field(..., description="Key of the field")
    enabled: bool = Field(..., description="Whether the field should be visible/editable")


class CalculationOptionToggleRequest(BaseModel):
    """Request to toggle a calculation option"""
    calculator_type: str = Field(..., description="Type of calculator (solar, heatpump, etc.)")
    option_key: str = Field(..., description="Key of the calculation option")
    enabled: bool = Field(..., description="Whether the option should be enabled")


class ExportFormatToggleRequest(BaseModel):
    """Request to toggle an export format"""
    format_key: str = Field(..., description="Export format key (pdf, excel, csv, etc.)")
    enabled: bool = Field(..., description="Whether the format should be available")


class ThemeToggleRequest(BaseModel):
    """Request to toggle a UI theme"""
    theme_key: str = Field(..., description="Theme key (light, dark, high_contrast, etc.)")
    enabled: bool = Field(..., description="Whether the theme should be available")


class LanguageToggleRequest(BaseModel):
    """Request to toggle a language"""
    language_code: str = Field(..., description="Language code (de, en, fr, etc.)")
    enabled: bool = Field(..., description="Whether the language should be available")


class BulkToggleRequest(BaseModel):
    """Request to bulk toggle components"""
    category: ComponentToggleCategory = Field(..., description="Category to toggle")
    enabled: bool = Field(..., description="Enable or disable all in category")


# Response schemas for specific queries

class VisibleChartsResponse(BaseModel):
    """Response with list of visible charts"""
    charts: List[str] = Field(..., description="List of visible chart types")


class EnabledFormFieldsResponse(BaseModel):
    """Response with list of enabled form fields"""
    form_name: str
    fields: List[str] = Field(..., description="List of enabled field keys")


class EnabledCalculationOptionsResponse(BaseModel):
    """Response with list of enabled calculation options"""
    calculator_type: str
    options: List[str] = Field(..., description="List of enabled option keys")


class AvailableExportFormatsResponse(BaseModel):
    """Response with list of available export formats"""
    formats: List[str] = Field(..., description="List of available export format keys")


class AvailableThemesResponse(BaseModel):
    """Response with list of available themes"""
    themes: List[str] = Field(..., description="List of available theme keys")


class AvailableLanguagesResponse(BaseModel):
    """Response with list of available languages"""
    languages: List[str] = Field(..., description="List of available language codes")
