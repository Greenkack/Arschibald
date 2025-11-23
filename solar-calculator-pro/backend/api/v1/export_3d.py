"""
3D Export API Endpoints

Provides REST API endpoints for exporting 3D models in various formats.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import Response
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

from backend.services.export_3d_service import Export3DService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export-3d", tags=["3D Export"])

# Initialize service
export_service = Export3DService()


# ============================================================================
# Request/Response Models
# ============================================================================

class BuildingDimsModel(BaseModel):
    """Building dimensions model."""
    length_m: float = Field(..., gt=0, description="Building length in meters")
    width_m: float = Field(..., gt=0, description="Building width in meters")
    wall_height_m: float = Field(..., gt=0, description="Wall height in meters")


class RoofConfigModel(BaseModel):
    """Roof configuration model."""
    type: str = Field(..., description="Roof type (flat, gable, hip, etc.)")
    angle: float = Field(default=15.0, ge=0, le=90, description="Roof angle in degrees")
    orientation: str = Field(default="south", description="Roof orientation")


class ModuleConfigModel(BaseModel):
    """Module configuration model."""
    count: int = Field(..., gt=0, description="Number of PV modules")
    spacing: float = Field(default=0.02, ge=0, description="Spacing between modules in meters")
    margin: float = Field(default=0.5, ge=0, description="Margin from roof edge in meters")


class ExportRequest(BaseModel):
    """3D export request model."""
    format: str = Field(..., description="Export format (stl, obj, gltf, glb, dxf, pdf, png, jpg)")
    project_data: Dict[str, Any] = Field(default_factory=dict, description="Project data")
    building_dims: BuildingDimsModel = Field(..., description="Building dimensions")
    roof_config: RoofConfigModel = Field(..., description="Roof configuration")
    module_config: ModuleConfigModel = Field(..., description="Module configuration")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Format-specific options")


class FormatInfoResponse(BaseModel):
    """Format information response."""
    name: str
    description: str
    mime_type: str
    extension: str
    use_cases: List[str]
    binary: bool
    supported: bool


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/export")
async def export_3d_model(request: ExportRequest) -> Response:
    """
    Export 3D model in the specified format.
    
    Supported formats:
    - STL: Stereolithography (3D printing)
    - OBJ: Wavefront OBJ (universal 3D)
    - GLTF/GLB: GL Transmission Format (web-optimized)
    - DXF: AutoCAD Drawing Exchange Format
    - PDF: PDF with embedded 3D model
    - PNG/JPG: High-quality images
    
    Returns the exported file as binary data with appropriate content type.
    """
    try:
        # Validate format
        if not export_service.is_format_supported(request.format):
            raise HTTPException(
                status_code=400,
                detail=f"Format '{request.format}' is not supported"
            )
        
        # Export model
        file_bytes = export_service.export(
            format=request.format,
            project_data=request.project_data,
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict(),
            module_config=request.module_config.dict(),
            options=request.options
        )
        
        # Get format info for content type
        format_info = export_service.get_format_info(request.format)
        
        # Return file
        return Response(
            content=file_bytes,
            media_type=format_info.get("mime_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=model{format_info.get('extension', '')}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting 3D model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/formats")
async def get_supported_formats() -> Dict[str, bool]:
    """
    Get list of supported export formats.
    
    Returns a dictionary mapping format names to their availability status.
    """
    return export_service.supported_formats


@router.get("/formats/{format}")
async def get_format_info(format: str) -> FormatInfoResponse:
    """
    Get detailed information about a specific export format.
    
    Args:
        format: Format name (stl, obj, gltf, glb, dxf, pdf, png, jpg)
        
    Returns:
        Detailed format information including description, use cases, and availability.
    """
    info = export_service.get_format_info(format)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Format '{format}' not found"
        )
    
    return FormatInfoResponse(**info)
