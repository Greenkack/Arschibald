# backend/models/branding_schemas.py

"""
Pydantic schemas for PDF Branding & Multi-Logo System
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class LogoPositionBase(BaseModel):
    """Base schema for logo position"""
    page_number: Optional[int] = None
    context: str = Field(default="header", pattern="^(header|footer|body|watermark)$")
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation: float = Field(default=0.0, ge=-360.0, le=360.0)
    scale: float = Field(default=1.0, gt=0.0, le=5.0)


class LogoPositionCreate(LogoPositionBase):
    """Schema for creating logo position"""
    pass


class LogoPositionResponse(LogoPositionBase):
    """Schema for logo position response"""
    id: int
    branding_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanyBrandingBase(BaseModel):
    """Base schema for company branding"""
    # Logo configuration
    logo_path: Optional[str] = None
    logo_base64: Optional[str] = None
    logo_width: float = Field(default=100.0, gt=0)
    logo_height: float = Field(default=50.0, gt=0)
    logo_position_x: float = Field(default=50.0)
    logo_position_y: float = Field(default=750.0)
    logo_page: str = Field(default="all", pattern="^(all|first|header|footer)$")
    
    # Color scheme
    primary_color: str = Field(default="#0066CC", pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#003366", pattern="^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field(default="#FF6600", pattern="^#[0-9A-Fa-f]{6}$")
    text_color: str = Field(default="#333333", pattern="^#[0-9A-Fa-f]{6}$")
    background_color: str = Field(default="#FFFFFF", pattern="^#[0-9A-Fa-f]{6}$")
    header_color: str = Field(default="#0066CC", pattern="^#[0-9A-Fa-f]{6}$")
    footer_color: str = Field(default="#666666", pattern="^#[0-9A-Fa-f]{6}$")
    
    # Typography
    font_family: str = Field(default="Helvetica", max_length=100)
    font_size_base: int = Field(default=10, ge=6, le=24)
    font_size_heading: int = Field(default=16, ge=10, le=48)
    font_size_subheading: int = Field(default=12, ge=8, le=32)
    font_weight: str = Field(default="normal", pattern="^(normal|bold)$")
    
    # Header configuration
    header_enabled: bool = True
    header_text: Optional[str] = Field(None, max_length=500)
    header_height: float = Field(default=80.0, ge=0, le=200)
    header_background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    header_text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    header_logo_enabled: bool = True
    
    # Footer configuration
    footer_enabled: bool = True
    footer_text: Optional[str] = Field(None, max_length=500)
    footer_height: float = Field(default=60.0, ge=0, le=200)
    footer_background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    footer_text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    footer_logo_enabled: bool = False
    footer_page_numbers: bool = True
    
    # Watermark configuration
    watermark_enabled: bool = False
    watermark_text: Optional[str] = Field(None, max_length=200)
    watermark_opacity: float = Field(default=0.1, ge=0.0, le=1.0)
    watermark_rotation: float = Field(default=45.0, ge=-360.0, le=360.0)
    watermark_font_size: int = Field(default=60, ge=20, le=200)
    watermark_color: str = Field(default="#CCCCCC", pattern="^#[0-9A-Fa-f]{6}$")
    
    # Template configuration
    template_path: Optional[str] = None
    template_type: str = Field(default="standard", pattern="^(standard|extended|custom)$")
    
    # YML coordinates override
    yml_coordinates: Optional[Dict[str, Any]] = None
    
    # Status
    is_active: bool = True


class CompanyBrandingCreate(CompanyBrandingBase):
    """Schema for creating company branding"""
    company_id: int


class CompanyBrandingUpdate(BaseModel):
    """Schema for updating company branding"""
    # All fields optional for partial updates
    logo_path: Optional[str] = None
    logo_base64: Optional[str] = None
    logo_width: Optional[float] = Field(None, gt=0)
    logo_height: Optional[float] = Field(None, gt=0)
    logo_position_x: Optional[float] = None
    logo_position_y: Optional[float] = None
    logo_page: Optional[str] = Field(None, pattern="^(all|first|header|footer)$")
    
    primary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    header_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    footer_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    font_family: Optional[str] = Field(None, max_length=100)
    font_size_base: Optional[int] = Field(None, ge=6, le=24)
    font_size_heading: Optional[int] = Field(None, ge=10, le=48)
    font_size_subheading: Optional[int] = Field(None, ge=8, le=32)
    font_weight: Optional[str] = Field(None, pattern="^(normal|bold)$")
    
    header_enabled: Optional[bool] = None
    header_text: Optional[str] = Field(None, max_length=500)
    header_height: Optional[float] = Field(None, ge=0, le=200)
    header_background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    header_text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    header_logo_enabled: Optional[bool] = None
    
    footer_enabled: Optional[bool] = None
    footer_text: Optional[str] = Field(None, max_length=500)
    footer_height: Optional[float] = Field(None, ge=0, le=200)
    footer_background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    footer_text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    footer_logo_enabled: Optional[bool] = None
    footer_page_numbers: Optional[bool] = None
    
    watermark_enabled: Optional[bool] = None
    watermark_text: Optional[str] = Field(None, max_length=200)
    watermark_opacity: Optional[float] = Field(None, ge=0.0, le=1.0)
    watermark_rotation: Optional[float] = Field(None, ge=-360.0, le=360.0)
    watermark_font_size: Optional[int] = Field(None, ge=20, le=200)
    watermark_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    template_path: Optional[str] = None
    template_type: Optional[str] = Field(None, pattern="^(standard|extended|custom)$")
    yml_coordinates: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CompanyBrandingResponse(CompanyBrandingBase):
    """Schema for company branding response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    logo_positions: List[LogoPositionResponse] = []
    
    class Config:
        from_attributes = True


class BrandingTemplateBase(BaseModel):
    """Base schema for branding template"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    config: Dict[str, Any]
    preview_image: Optional[str] = None
    is_public: bool = True


class BrandingTemplateCreate(BrandingTemplateBase):
    """Schema for creating branding template"""
    pass


class BrandingTemplateResponse(BrandingTemplateBase):
    """Schema for branding template response"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BrandingAssetBase(BaseModel):
    """Base schema for branding asset"""
    asset_type: str = Field(..., pattern="^(logo|image|font|icon)$")
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_base64: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_primary: bool = False
    tags: Optional[List[str]] = None


class BrandingAssetCreate(BrandingAssetBase):
    """Schema for creating branding asset"""
    company_id: int


class BrandingAssetResponse(BrandingAssetBase):
    """Schema for branding asset response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BrandingPreviewRequest(BaseModel):
    """Schema for branding preview request"""
    branding_id: int
    page_type: str = Field(default="standard", pattern="^(standard|extended|custom)$")
    include_watermark: bool = True
    include_header: bool = True
    include_footer: bool = True


class BrandingPreviewResponse(BaseModel):
    """Schema for branding preview response"""
    pdf_base64: str
    preview_image: str  # Base64 encoded preview image
    branding_applied: Dict[str, Any]
