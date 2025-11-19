"""
FastAPI endpoints for Pricing Service

Requirements: 1.3, 4.5, 14.1, 14.2
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from backend.services.pricing_service import get_pricing_service, PricingService
from backend.models.pricing_schemas import (
    PriceCalculationRequest,
    PriceCalculationResponse,
    MatrixCreateRequest,
    MatrixResponse,
    MatrixListResponse,
    MatrixFullResponse,
    MatrixUploadCSVRequest,
    MatrixUploadResponse,
    MatrixValidationResponse,
    MatrixExportCSVRequest,
    MatrixExportCSVResponse,
    AddRowRequest,
    AddColumnRequest,
    SetCellValueRequest,
    CRUDResponse,
    CacheStatsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["pricing"])


def get_service() -> PricingService:
    """Dependency to get pricing service"""
    return get_pricing_service()


# ============================================================================
# Price Calculation Endpoints
# ============================================================================

@router.post("/calculate", response_model=PriceCalculationResponse)
async def calculate_price(
    request: PriceCalculationRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Calculate price using Excel INDEX/MATCH logic
    
    This endpoint implements the core price calculation logic:
    - MATCH(module_count, column_A, 0) -> finds row index
    - MATCH(storage_model, row_1, 0) -> finds column index
    - INDEX(matrix, row_index, col_index) -> returns price
    """
    result = service.calculate_price(
        module_count=request.module_count,
        storage_model=request.storage_model,
        matrix_id=request.matrix_id,
        enable_fallback=request.enable_fallback
    )
    
    return result


# ============================================================================
# Matrix Management Endpoints
# ============================================================================

@router.post("/matrix", response_model=MatrixResponse)
async def create_matrix(
    request: MatrixCreateRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Create a new price matrix"""
    result = service.create_matrix(
        name=request.name,
        description=request.description,
        pricing_mode=request.pricing_mode,
        include_accessories=request.include_accessories,
        include_misc=request.include_misc
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
    
    return result


@router.get("/matrix", response_model=MatrixListResponse)
async def list_matrices(
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """List all price matrices"""
    result = service.list_matrices()
    return result


@router.get("/matrix/{matrix_id}", response_model=MatrixFullResponse)
async def get_matrix(
    matrix_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Get full matrix data"""
    result = service.get_matrix(matrix_id)
    
    if not result['success']:
        raise HTTPException(status_code=404, detail=result.get('error', 'Matrix not found'))
    
    return result


@router.put("/matrix/{matrix_id}/activate", response_model=MatrixResponse)
async def set_active_matrix(
    matrix_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Set active matrix"""
    result = service.set_active_matrix(matrix_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
    
    return result


@router.delete("/matrix/{matrix_id}", response_model=MatrixResponse)
async def delete_matrix(
    matrix_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Delete a matrix"""
    result = service.delete_matrix(matrix_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
    
    return result


# ============================================================================
# Matrix Upload and Validation Endpoints
# ============================================================================

@router.post("/matrix/upload/csv", response_model=MatrixUploadResponse)
async def upload_matrix_csv(
    request: MatrixUploadCSVRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Upload matrix from CSV"""
    result = service.upload_matrix_csv(
        name=request.name,
        csv_content=request.csv_content,
        delimiter=request.delimiter
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Upload failed'))
    
    return result


@router.get("/matrix/{matrix_id}/validate", response_model=MatrixValidationResponse)
async def validate_matrix(
    matrix_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Validate matrix structure and data"""
    result = service.validate_matrix(matrix_id)
    return result


# ============================================================================
# Matrix Export Endpoints
# ============================================================================

@router.post("/matrix/export/csv", response_model=MatrixExportCSVResponse)
async def export_matrix_csv(
    request: MatrixExportCSVRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Export matrix to CSV"""
    result = service.export_matrix_csv(
        matrix_id=request.matrix_id,
        delimiter=request.delimiter
    )
    
    if not result['success']:
        raise HTTPException(status_code=404, detail=result.get('error', 'Export failed'))
    
    return result


# ============================================================================
# CRUD Operation Endpoints
# ============================================================================

@router.post("/matrix/row", response_model=CRUDResponse)
async def add_row(
    request: AddRowRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Add row to matrix"""
    result = service.add_row(
        matrix_id=request.matrix_id,
        label=request.label,
        position=request.position
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to add row'))
    
    return result


@router.post("/matrix/column", response_model=CRUDResponse)
async def add_column(
    request: AddColumnRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Add column to matrix"""
    result = service.add_column(
        matrix_id=request.matrix_id,
        label=request.label,
        position=request.position
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to add column'))
    
    return result


@router.delete("/matrix/row/{row_id}", response_model=CRUDResponse)
async def remove_row(
    row_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Remove row from matrix"""
    result = service.remove_row(row_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to remove row'))
    
    return result


@router.delete("/matrix/column/{column_id}", response_model=CRUDResponse)
async def remove_column(
    column_id: int,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Remove column from matrix"""
    result = service.remove_column(column_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to remove column'))
    
    return result


@router.put("/matrix/cell", response_model=CRUDResponse)
async def set_cell_value(
    request: SetCellValueRequest,
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Set cell value in matrix"""
    result = service.set_cell_value(
        matrix_id=request.matrix_id,
        row_id=request.row_id,
        column_id=request.column_id,
        value=request.value,
        raw_input=request.raw_input,
        data_type=request.data_type
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to set cell value'))
    
    return result


# ============================================================================
# Cache Endpoints
# ============================================================================

@router.delete("/cache")
async def clear_cache(
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Clear price lookup cache"""
    result = service.clear_cache()
    return result


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    service: PricingService = Depends(get_service)
) -> Dict[str, Any]:
    """Get cache statistics"""
    result = service.get_cache_stats()
    return result
