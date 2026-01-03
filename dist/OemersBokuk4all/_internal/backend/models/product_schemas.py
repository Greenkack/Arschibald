"""
Product Management Schemas

Pydantic models for product management API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductBase(BaseModel):
    """Base product model with common fields"""
    category: str = Field(..., description="Product category")
    model_name: str = Field(..., description="Product model name (unique)")
    brand: Optional[str] = Field(None, description="Product brand/manufacturer")
    price_euro: Optional[float] = Field(None, ge=0, description="Price in euros")
    capacity_w: Optional[float] = Field(None, ge=0, description="Capacity in watts (for PV modules)")
    storage_power_kw: Optional[float] = Field(None, ge=0, description="Storage power in kW (for batteries)")
    power_kw: Optional[float] = Field(None, ge=0, description="Power in kW (for inverters)")
    max_cycles: Optional[int] = Field(None, ge=0, description="Maximum charge cycles (for batteries)")
    warranty_years: Optional[int] = Field(None, ge=0, description="Warranty period in years")
    length_m: Optional[float] = Field(None, ge=0, description="Length in meters")
    width_m: Optional[float] = Field(None, ge=0, description="Width in meters")
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")
    efficiency_percent: Optional[float] = Field(None, ge=0, le=100, description="Efficiency percentage")
    origin_country: Optional[str] = Field(None, description="Country of origin")
    description: Optional[str] = Field(None, description="Product description")
    pros: Optional[str] = Field(None, description="Product advantages")
    cons: Optional[str] = Field(None, description="Product disadvantages")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Product rating (0-5)")
    
    # Enhanced pricing fields
    calculate_per: Optional[str] = Field("Stück", description="Calculation method (Stück, Meter, pauschal, kWp, etc.)")
    purchase_price_net: Optional[float] = Field(None, ge=0, description="Purchase price (net)")
    margin_type: Optional[str] = Field(None, description="Margin type (percentage or fixed)")
    margin_value: Optional[float] = Field(None, ge=0, description="Margin value")
    margin_priority: Optional[int] = Field(0, description="Margin priority")
    pricing_category: Optional[str] = Field(None, description="Pricing category")
    
    # Technical attributes
    technology: Optional[str] = Field(None, description="Technology type")
    feature: Optional[str] = Field(None, description="Special features")
    design: Optional[str] = Field(None, description="Design variant")
    upgrade: Optional[str] = Field(None, description="Upgrade options")
    max_kwh_capacity: Optional[float] = Field(None, ge=0, description="Maximum kWh capacity")
    outdoor_opt: Optional[int] = Field(0, description="Outdoor optimization (0/1)")
    self_supply_feature: Optional[int] = Field(0, description="Self supply feature (0/1)")
    shadow_fading: Optional[int] = Field(0, description="Shadow fading feature (0/1)")
    smart_home: Optional[int] = Field(0, description="Smart home integration (0/1)")
    is_special_product: Optional[int] = Field(0, description="Special product flag (0/1)")
    
    # Module details
    cell_technology: Optional[str] = Field(None, description="Cell technology (e.g., N-Type, TOPCon)")
    module_structure: Optional[str] = Field(None, description="Module structure (e.g., Glas-Glas)")
    cell_type: Optional[str] = Field(None, description="Cell type (e.g., 108 Halbzellen)")
    version: Optional[str] = Field(None, description="Version (e.g., All-Black)")
    module_warranty_text: Optional[str] = Field(None, description="Warranty text")
    
    # Service fields
    labor_hours: Optional[float] = Field(None, ge=0, description="Labor hours for installation")
    additional_cost_netto: Optional[float] = Field(0.0, ge=0, description="Additional costs (net)")
    datasheet_link_db_path: Optional[str] = Field(None, description="Datasheet file path")
    company_id: Optional[int] = Field(None, description="Company ID")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)"""
    category: Optional[str] = None
    model_name: Optional[str] = None
    brand: Optional[str] = None
    price_euro: Optional[float] = Field(None, ge=0)
    capacity_w: Optional[float] = Field(None, ge=0)
    storage_power_kw: Optional[float] = Field(None, ge=0)
    power_kw: Optional[float] = Field(None, ge=0)
    max_cycles: Optional[int] = Field(None, ge=0)
    warranty_years: Optional[int] = Field(None, ge=0)
    length_m: Optional[float] = Field(None, ge=0)
    width_m: Optional[float] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    efficiency_percent: Optional[float] = Field(None, ge=0, le=100)
    origin_country: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    calculate_per: Optional[str] = None
    purchase_price_net: Optional[float] = Field(None, ge=0)
    margin_type: Optional[str] = None
    margin_value: Optional[float] = Field(None, ge=0)
    margin_priority: Optional[int] = None
    pricing_category: Optional[str] = None
    technology: Optional[str] = None
    feature: Optional[str] = None
    design: Optional[str] = None
    upgrade: Optional[str] = None
    max_kwh_capacity: Optional[float] = Field(None, ge=0)
    outdoor_opt: Optional[int] = None
    self_supply_feature: Optional[int] = None
    shadow_fading: Optional[int] = None
    smart_home: Optional[int] = None
    is_special_product: Optional[int] = None
    cell_technology: Optional[str] = None
    module_structure: Optional[str] = None
    cell_type: Optional[str] = None
    version: Optional[str] = None
    module_warranty_text: Optional[str] = None
    labor_hours: Optional[float] = Field(None, ge=0)
    additional_cost_netto: Optional[float] = Field(None, ge=0)
    datasheet_link_db_path: Optional[str] = None
    company_id: Optional[int] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int = Field(..., description="Product ID")
    image_base64: Optional[str] = Field(None, description="Product image (base64 encoded)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    last_price_update: Optional[str] = Field(None, description="Last price update timestamp")
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for product list response"""
    products: List[ProductResponse]
    total: int = Field(..., description="Total number of products")
    category: Optional[str] = Field(None, description="Filter category")
    company_id: Optional[int] = Field(None, description="Filter company ID")


class ProductSearchRequest(BaseModel):
    """Schema for product search request"""
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    company_id: Optional[int] = Field(None, description="Filter by company ID")
    brand: Optional[str] = Field(None, description="Filter by brand")
    price_min: Optional[float] = Field(None, ge=0, description="Minimum price")
    price_max: Optional[float] = Field(None, ge=0, description="Maximum price")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class ProductSearchResponse(BaseModel):
    """Schema for product search response"""
    products: List[ProductResponse]
    total: int = Field(..., description="Total number of matching products")
    query: str = Field(..., description="Search query used")


class ProductImageUploadRequest(BaseModel):
    """Schema for product image upload"""
    image_data: str = Field(..., description="Image data (base64 encoded)")
    image_format: str = Field("base64", description="Image format (base64 or file_path)")


class ProductImageUploadResponse(BaseModel):
    """Schema for product image upload response"""
    product_id: int = Field(..., description="Product ID")
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Status message")


class ProductExportRequest(BaseModel):
    """Schema for product export request"""
    category: Optional[str] = Field(None, description="Filter by category")
    company_id: Optional[int] = Field(None, description="Filter by company ID")
    format: str = Field("json", description="Export format (json, csv, excel)")


class ProductExportResponse(BaseModel):
    """Schema for product export response"""
    export_date: str = Field(..., description="Export timestamp")
    format: str = Field(..., description="Export format")
    product_count: int = Field(..., description="Number of products exported")
    filters: Dict[str, Any] = Field(..., description="Filters applied")
    products: Optional[List[Dict[str, Any]]] = Field(None, description="Product data (for JSON)")
    csv_data: Optional[str] = Field(None, description="CSV data (for CSV format)")
    excel_data: Optional[str] = Field(None, description="Excel data (for Excel format)")


class ProductImportRequest(BaseModel):
    """Schema for product import request"""
    format: str = Field("json", description="Import format (json, csv, excel)")
    update_existing: bool = Field(False, description="Whether to update existing products")
    products: Optional[List[Dict[str, Any]]] = Field(None, description="Product data (for JSON)")
    csv_data: Optional[str] = Field(None, description="CSV data (for CSV format)")


class ProductImportResponse(BaseModel):
    """Schema for product import response"""
    total: int = Field(..., description="Total products processed")
    created: int = Field(..., description="Number of products created")
    updated: int = Field(..., description="Number of products updated")
    failed: int = Field(..., description="Number of failed imports")
    errors: List[str] = Field(..., description="List of error messages")


class CategoryListResponse(BaseModel):
    """Schema for category list response"""
    categories: List[str] = Field(..., description="List of product categories")
    total: int = Field(..., description="Total number of categories")


class ProductDeleteResponse(BaseModel):
    """Schema for product deletion response"""
    product_id: int = Field(..., description="Deleted product ID")
    success: bool = Field(..., description="Deletion success status")
    message: str = Field(..., description="Status message")
