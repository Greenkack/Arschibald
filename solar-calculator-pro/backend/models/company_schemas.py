"""
Pydantic Schemas for Company Management

This module defines the request/response schemas for the company API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Company Schemas
# ============================================================================

class CompanyBase(BaseModel):
    """Base schema for company data"""
    name: str = Field(..., min_length=1, max_length=255, description="Unique company identifier")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name for company")
    
    # Contact Information
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address_street: Optional[str] = Field(None, max_length=255)
    address_city: Optional[str] = Field(None, max_length=100)
    address_postal_code: Optional[str] = Field(None, max_length=20)
    address_country: str = Field("Deutschland", max_length=100)
    
    # Tax and Legal
    tax_id: Optional[str] = Field(None, max_length=50)
    vat_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)
    
    # Branding
    logo_path: Optional[str] = Field(None, max_length=500)
    logo_position_x: float = Field(50.0, ge=0, le=210, description="X position in mm")
    logo_position_y: float = Field(20.0, ge=0, le=297, description="Y position in mm")
    logo_width: float = Field(50.0, ge=1, le=200, description="Logo width in mm")
    logo_height: float = Field(30.0, ge=1, le=200, description="Logo height in mm")
    
    # Color Scheme
    primary_color: str = Field("#0066CC", regex="^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field("#FF6600", regex="^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field("#00CC66", regex="^#[0-9A-Fa-f]{6}$")
    
    # Pricing Rules
    base_markup_percentage: float = Field(0.0, ge=0, le=100, description="Base markup percentage")
    price_increase_percentage: float = Field(7.0, ge=0, le=100, description="Multi-PDF price increase")
    
    # Template Configuration
    template_prefix: Optional[str] = Field(None, max_length=50)
    template_folder: Optional[str] = Field(None, max_length=255)
    
    # Status
    is_active: bool = Field(True)
    is_default: bool = Field(False)
    sort_order: int = Field(0, ge=0)
    notes: Optional[str] = None
    
    # Additional Configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address_street: Optional[str] = Field(None, max_length=255)
    address_city: Optional[str] = Field(None, max_length=100)
    address_postal_code: Optional[str] = Field(None, max_length=20)
    address_country: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    vat_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)
    logo_path: Optional[str] = Field(None, max_length=500)
    logo_position_x: Optional[float] = Field(None, ge=0, le=210)
    logo_position_y: Optional[float] = Field(None, ge=0, le=297)
    logo_width: Optional[float] = Field(None, ge=1, le=200)
    logo_height: Optional[float] = Field(None, ge=1, le=200)
    primary_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    base_markup_percentage: Optional[float] = Field(None, ge=0, le=100)
    price_increase_percentage: Optional[float] = Field(None, ge=0, le=100)
    template_prefix: Optional[str] = Field(None, max_length=50)
    template_folder: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Counts
    document_count: int = 0
    image_count: int = 0
    pricing_rule_count: int = 0
    
    class Config:
        orm_mode = True


# ============================================================================
# Company Document Schemas
# ============================================================================

class CompanyDocumentBase(BaseModel):
    """Base schema for company documents"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: str = Field(..., max_length=50)
    file_path: str = Field(..., max_length=500)
    file_name: str = Field(..., max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # PDF Integration
    include_in_pdf: bool = Field(False)
    pdf_page_number: Optional[int] = Field(None, ge=1)
    pdf_position_x: Optional[float] = Field(None, ge=0, le=210)
    pdf_position_y: Optional[float] = Field(None, ge=0, le=297)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    sort_order: int = Field(0, ge=0)
    is_active: bool = Field(True)


class CompanyDocumentCreate(CompanyDocumentBase):
    """Schema for creating a company document"""
    company_id: int = Field(..., gt=0)


class CompanyDocumentUpdate(BaseModel):
    """Schema for updating a company document"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: Optional[str] = Field(None, max_length=50)
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    include_in_pdf: Optional[bool] = None
    pdf_page_number: Optional[int] = Field(None, ge=1)
    pdf_position_x: Optional[float] = Field(None, ge=0, le=210)
    pdf_position_y: Optional[float] = Field(None, ge=0, le=297)
    tags: Optional[List[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CompanyDocumentResponse(CompanyDocumentBase):
    """Schema for company document response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# Company Image Schemas
# ============================================================================

class CompanyImageBase(BaseModel):
    """Base schema for company images"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image_type: str = Field(..., max_length=50)
    file_path: str = Field(..., max_length=500)
    file_name: str = Field(..., max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # Image Properties
    width: Optional[int] = Field(None, ge=1)
    height: Optional[int] = Field(None, ge=1)
    
    # PDF Integration
    include_in_pdf: bool = Field(False)
    pdf_page_number: Optional[int] = Field(None, ge=1)
    pdf_position_x: Optional[float] = Field(None, ge=0, le=210)
    pdf_position_y: Optional[float] = Field(None, ge=0, le=297)
    pdf_width: Optional[float] = Field(None, ge=1, le=200)
    pdf_height: Optional[float] = Field(None, ge=1, le=200)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    sort_order: int = Field(0, ge=0)
    is_active: bool = Field(True)


class CompanyImageCreate(CompanyImageBase):
    """Schema for creating a company image"""
    company_id: int = Field(..., gt=0)


class CompanyImageUpdate(BaseModel):
    """Schema for updating a company image"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image_type: Optional[str] = Field(None, max_length=50)
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    width: Optional[int] = Field(None, ge=1)
    height: Optional[int] = Field(None, ge=1)
    include_in_pdf: Optional[bool] = None
    pdf_page_number: Optional[int] = Field(None, ge=1)
    pdf_position_x: Optional[float] = Field(None, ge=0, le=210)
    pdf_position_y: Optional[float] = Field(None, ge=0, le=297)
    pdf_width: Optional[float] = Field(None, ge=1, le=200)
    pdf_height: Optional[float] = Field(None, ge=1, le=200)
    tags: Optional[List[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CompanyImageResponse(CompanyImageBase):
    """Schema for company image response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# Company Pricing Rule Schemas
# ============================================================================

class CompanyPricingRuleBase(BaseModel):
    """Base schema for company pricing rules"""
    rule_name: str = Field(..., min_length=1, max_length=255)
    rule_type: str = Field(..., max_length=50)
    
    # Target
    target_id: Optional[int] = Field(None, gt=0)
    target_name: Optional[str] = Field(None, max_length=255)
    
    # Pricing Adjustments
    markup_percentage: float = Field(0.0, ge=0, le=100)
    markup_fixed: float = Field(0.0, ge=0)
    discount_percentage: float = Field(0.0, ge=0, le=100)
    discount_fixed: float = Field(0.0, ge=0)
    
    # Conditions
    min_quantity: Optional[int] = Field(None, ge=1)
    max_quantity: Optional[int] = Field(None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Priority and Status
    priority: int = Field(0, ge=0)
    is_active: bool = Field(True)


class CompanyPricingRuleCreate(CompanyPricingRuleBase):
    """Schema for creating a pricing rule"""
    company_id: int = Field(..., gt=0)


class CompanyPricingRuleUpdate(BaseModel):
    """Schema for updating a pricing rule"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=255)
    rule_type: Optional[str] = Field(None, max_length=50)
    target_id: Optional[int] = Field(None, gt=0)
    target_name: Optional[str] = Field(None, max_length=255)
    markup_percentage: Optional[float] = Field(None, ge=0, le=100)
    markup_fixed: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_fixed: Optional[float] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=1)
    max_quantity: Optional[int] = Field(None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CompanyPricingRuleResponse(CompanyPricingRuleBase):
    """Schema for pricing rule response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# Multi-PDF Generation Schemas
# ============================================================================

class MultiPDFRequest(BaseModel):
    """Request schema for multi-PDF generation"""
    company_ids: List[int] = Field(..., min_items=1, description="List of company IDs to generate PDFs for")
    project_data: Dict[str, Any] = Field(..., description="Solar calculator project data")
    include_documents: bool = Field(True, description="Include company documents in PDFs")
    include_images: bool = Field(True, description="Include company images in PDFs")
    apply_pricing_rules: bool = Field(True, description="Apply company-specific pricing rules")
    
    @validator('company_ids')
    def validate_company_ids(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 companies allowed per batch')
        if len(v) != len(set(v)):
            raise ValueError('Duplicate company IDs not allowed')
        return v


class MultiPDFResponse(BaseModel):
    """Response schema for multi-PDF generation"""
    success: bool
    total_companies: int
    successful_pdfs: int
    failed_pdfs: int
    results: List[Dict[str, Any]]
    zip_download_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_companies": 8,
                "successful_pdfs": 8,
                "failed_pdfs": 0,
                "results": [
                    {
                        "company_id": 1,
                        "company_name": "Solar GmbH",
                        "status": "success",
                        "pdf_url": "/api/v1/pdfs/download/abc123.pdf",
                        "price": "16.999,00 €"
                    }
                ],
                "zip_download_url": "/api/v1/pdfs/download/batch_abc123.zip"
            }
        }


class CompanySelectionResponse(BaseModel):
    """Response schema for company selection UI"""
    companies: List[CompanyResponse]
    total: int
    active_count: int
    default_company_id: Optional[int] = None
