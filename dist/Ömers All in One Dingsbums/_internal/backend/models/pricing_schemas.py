"""
Pydantic schemas for Pricing API

Requirements: 1.3, 4.5, 14.1, 14.2
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Price Calculation Schemas
# ============================================================================

class PriceCalculationRequest(BaseModel):
    """Request for price calculation"""
    module_count: int = Field(..., gt=0, description="Number of PV modules")
    storage_model: Optional[str] = Field(None, description="Battery storage model or None for 'kein Speicher'")
    matrix_id: Optional[int] = Field(None, description="Matrix ID (None = active matrix)")
    enable_fallback: bool = Field(True, description="Enable fallback strategies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "module_count": 20,
                "storage_model": "15kWh",
                "matrix_id": None,
                "enable_fallback": True
            }
        }


class PriceCalculationResponse(BaseModel):
    """Response from price calculation"""
    success: bool
    base_price: Optional[float] = None
    row_used: Optional[str] = None
    row_id: Optional[int] = None
    column_used: Optional[str] = None
    column_id: Optional[int] = None
    matrix_id: Optional[int] = None
    matrix_name: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    user_message: Optional[str] = None
    fallback_used: bool = False
    fallback_info: Optional[Dict[str, Any]] = None
    admin_notified: bool = False
    error_info: Optional[Dict[str, Any]] = None
    error_severity: Optional[str] = None
    error_category: Optional[str] = None
    suggestions: Optional[List[str]] = None


# ============================================================================
# Matrix Management Schemas
# ============================================================================

class MatrixCreateRequest(BaseModel):
    """Request to create a new matrix"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=1000)
    pricing_mode: str = Field('pauschal', pattern='^(pauschal|additiv)$')
    include_accessories: bool = True
    include_misc: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Preismatrix 2024",
                "description": "Aktuelle Preise für PV-Anlagen",
                "pricing_mode": "pauschal",
                "include_accessories": True,
                "include_misc": True
            }
        }


class MatrixResponse(BaseModel):
    """Response with matrix data"""
    success: bool
    matrix_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


class MatrixListResponse(BaseModel):
    """Response with list of matrices"""
    success: bool
    matrices: List[Dict[str, Any]] = []
    count: int = 0
    error: Optional[str] = None


class MatrixFullResponse(BaseModel):
    """Response with full matrix data"""
    success: bool
    matrix: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# Matrix Upload Schemas
# ============================================================================

class MatrixUploadCSVRequest(BaseModel):
    """Request to upload matrix from CSV"""
    name: str = Field(..., min_length=1, max_length=255)
    csv_content: str = Field(..., min_length=1)
    delimiter: str = Field(';', max_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Imported Matrix",
                "csv_content": "ROW_LABEL;10kWh;15kWh;Kein Speicher\n10;15000;17500;12000\n15;18000;20500;15000",
                "delimiter": ";"
            }
        }


class MatrixUploadResponse(BaseModel):
    """Response from matrix upload"""
    success: bool
    matrix_id: Optional[int] = None
    validation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class MatrixValidationResponse(BaseModel):
    """Response from matrix validation"""
    valid: bool
    validation_result: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Matrix Export Schemas
# ============================================================================

class MatrixExportCSVRequest(BaseModel):
    """Request to export matrix to CSV"""
    matrix_id: int = Field(..., gt=0)
    delimiter: str = Field(';', max_length=1)


class MatrixExportCSVResponse(BaseModel):
    """Response from matrix export"""
    success: bool
    csv_content: Optional[str] = None
    matrix_id: Optional[int] = None
    error: Optional[str] = None


# ============================================================================
# CRUD Operation Schemas
# ============================================================================

class AddRowRequest(BaseModel):
    """Request to add row to matrix"""
    matrix_id: int = Field(..., gt=0)
    label: str = Field(..., min_length=1, max_length=255)
    position: Optional[int] = None


class AddColumnRequest(BaseModel):
    """Request to add column to matrix"""
    matrix_id: int = Field(..., gt=0)
    label: str = Field(..., min_length=1, max_length=255)
    position: Optional[int] = None


class SetCellValueRequest(BaseModel):
    """Request to set cell value"""
    matrix_id: int = Field(..., gt=0)
    row_id: int = Field(..., gt=0)
    column_id: int = Field(..., gt=0)
    value: Optional[float] = None
    raw_input: Optional[str] = None
    data_type: str = Field('number', pattern='^(text|number|formula|date)$')
    
    class Config:
        json_schema_extra = {
            "example": {
                "matrix_id": 1,
                "row_id": 5,
                "column_id": 3,
                "value": 18500.00,
                "raw_input": None,
                "data_type": "number"
            }
        }


class CRUDResponse(BaseModel):
    """Generic response for CRUD operations"""
    success: bool
    row_id: Optional[int] = None
    column_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Cache Schemas
# ============================================================================

class CacheStatsResponse(BaseModel):
    """Response with cache statistics"""
    cache_size: int
    cache_keys: List[str]
