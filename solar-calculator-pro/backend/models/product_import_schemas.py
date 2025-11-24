"""
Product Import/Export Schemas

Pydantic models for product import/export operations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum


class ProductExportFormat(str, Enum):
    """Supported export formats"""
    EXCEL = "excel"
    CSV = "csv"
    XML = "xml"
    JSON = "json"


class ProductImportMapping(BaseModel):
    """Column mapping configuration for import"""
    name_column: Optional[str] = Field(None, description="Column name for product name")
    sku_column: Optional[str] = Field(None, description="Column name for SKU")
    category_column: Optional[str] = Field(None, description="Column name for category")
    manufacturer_column: Optional[str] = Field(None, description="Column name for manufacturer")
    price_column: Optional[str] = Field(None, description="Column name for price")
    description_column: Optional[str] = Field(None, description="Column name for description")
    custom_mappings: Optional[Dict[str, str]] = Field(None, description="Additional custom column mappings")


class ProductImportResult(BaseModel):
    """Result of product import operation"""
    success: bool = Field(..., description="Whether import was successful")
    total_rows: int = Field(..., description="Total number of rows processed")
    imported_count: int = Field(..., description="Number of products successfully imported")
    failed_count: int = Field(..., description="Number of products that failed to import")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors encountered")
    message: Optional[str] = Field(None, description="Additional message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_rows": 100,
                "imported_count": 98,
                "failed_count": 2,
                "errors": [
                    {"row": 5, "error": "Duplicate SKU"},
                    {"row": 23, "error": "Invalid price format"}
                ],
                "message": "Import completed with 2 errors"
            }
        }


class ProductImportRequest(BaseModel):
    """Request for product import"""
    file_name: str = Field(..., description="Name of the file being imported")
    file_format: str = Field(..., description="Format of the file (excel, csv, xml)")
    mapping: Optional[ProductImportMapping] = Field(None, description="Column mapping configuration")
    validate_only: bool = Field(False, description="Only validate without importing")
    
    @validator('file_format')
    def validate_format(cls, v):
        allowed_formats = ['excel', 'csv', 'xml', 'json']
        if v.lower() not in allowed_formats:
            raise ValueError(f"Format must be one of: {', '.join(allowed_formats)}")
        return v.lower()


class ProductExportRequest(BaseModel):
    """Request for product export"""
    format: ProductExportFormat = Field(..., description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    columns: Optional[List[str]] = Field(None, description="Specific columns to export")
    include_metadata: bool = Field(True, description="Include metadata sheet (Excel only)")
    
    class Config:
        schema_extra = {
            "example": {
                "format": "excel",
                "filters": {
                    "category": "Solar Modules",
                    "min_price": 100,
                    "max_price": 1000
                },
                "columns": ["name", "sku", "price", "manufacturer"],
                "include_metadata": True
            }
        }


class CSVImportOptions(BaseModel):
    """Options for CSV import"""
    delimiter: str = Field(',', description="CSV delimiter character")
    encoding: str = Field('utf-8', description="File encoding")
    has_header: bool = Field(True, description="Whether file has header row")
    skip_rows: int = Field(0, description="Number of rows to skip")


class XMLImportOptions(BaseModel):
    """Options for XML import"""
    root_element: str = Field('products', description="Root XML element name")
    product_element: str = Field('product', description="Product XML element name")
    namespace: Optional[str] = Field(None, description="XML namespace")


class APIImportOptions(BaseModel):
    """Options for API import"""
    api_url: str = Field(..., description="API endpoint URL")
    api_key: Optional[str] = Field(None, description="API authentication key")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional HTTP headers")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    response_path: Optional[str] = Field(None, description="JSON path to products array")
    
    class Config:
        schema_extra = {
            "example": {
                "api_url": "https://api.example.com/products",
                "api_key": "your-api-key",
                "headers": {"Accept": "application/json"},
                "params": {"category": "solar", "limit": 100},
                "response_path": "data.products"
            }
        }


class ProductValidationError(BaseModel):
    """Validation error for a product"""
    row: int = Field(..., description="Row number (1-indexed)")
    field: Optional[str] = Field(None, description="Field name with error")
    error: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class ProductValidationResult(BaseModel):
    """Result of product validation"""
    valid: bool = Field(..., description="Whether validation passed")
    total_rows: int = Field(..., description="Total number of rows validated")
    valid_rows: int = Field(..., description="Number of valid rows")
    invalid_rows: int = Field(..., description="Number of invalid rows")
    errors: List[ProductValidationError] = Field(default_factory=list, description="List of validation errors")
    warnings: Optional[List[Dict[str, Any]]] = Field(None, description="List of warnings")


class ProductImportTemplate(BaseModel):
    """Template for product import"""
    format: ProductExportFormat = Field(..., description="Template format")
    columns: List[str] = Field(..., description="Required columns")
    sample_data: Optional[List[Dict[str, Any]]] = Field(None, description="Sample data rows")
    instructions: Optional[str] = Field(None, description="Import instructions")
    
    class Config:
        schema_extra = {
            "example": {
                "format": "excel",
                "columns": ["name", "sku", "category", "manufacturer", "price", "description"],
                "sample_data": [
                    {
                        "name": "Solar Module 400W",
                        "sku": "SM-400-001",
                        "category": "Solar Modules",
                        "manufacturer": "SolarTech",
                        "price": 299.99,
                        "description": "High-efficiency monocrystalline solar module"
                    }
                ],
                "instructions": "Fill in all required fields. SKU must be unique."
            }
        }


class ProductBulkUpdateRequest(BaseModel):
    """Request for bulk product updates"""
    product_ids: List[int] = Field(..., description="List of product IDs to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")
    
    class Config:
        schema_extra = {
            "example": {
                "product_ids": [1, 2, 3, 4, 5],
                "updates": {
                    "category": "Premium Solar Modules",
                    "price_multiplier": 1.1
                }
            }
        }


class ProductBulkDeleteRequest(BaseModel):
    """Request for bulk product deletion"""
    product_ids: List[int] = Field(..., description="List of product IDs to delete")
    confirm: bool = Field(..., description="Confirmation flag")
    
    @validator('confirm')
    def must_confirm(cls, v):
        if not v:
            raise ValueError("Confirmation required for bulk delete")
        return v
