"""
3D Visualization API Endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import base64
import logging

from backend.models.visualization_schemas import (
    Generate3DModelRequest,
    Generate3DModelResponse,
    CalculatePlacementRequest,
    CalculatePlacementResponse,
    ValidateManualPlacementRequest,
    DetectCollisionsRequest,
    DetectCollisionsResponse,
    Export3DModelRequest,
    Export3DModelResponse,
    ExportMultiViewRequest,
    ExportMultiViewResponse,
    Create360AnimationRequest,
    Create360AnimationResponse,
    VisualizationHealthResponse,
    RoofType,
    ExportFormat
)
from backend.services.visualization_service import VisualizationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualization", tags=["3D Visualization"])

# Initialize service
visualization_service = VisualizationService()


@router.get("/health", response_model=VisualizationHealthResponse)
async def health_check():
    """
    Check if 3D visualization service is available.
    """
    available = visualization_service.is_available()
    
    return VisualizationHealthResponse(
        available=available,
        version="1.0.0" if available else None,
        supported_formats=[fmt.value for fmt in ExportFormat] if available else [],
        supported_roof_types=[rt.value for rt in RoofType] if available else [],
        message="3D visualization service is operational" if available else "3D visualization modules not available"
    )



@router.post("/generate", response_model=Generate3DModelResponse)
async def generate_3d_model(request: Generate3DModelRequest):
    """
    Generate a complete 3D model of the PV system.
    
    This endpoint creates a 3D visualization including:
    - Building structure
    - Roof geometry
    - PV module placement
    - Scene data for rendering
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        result = visualization_service.generate_3d_model(
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict(),
            module_config=request.module_config.dict(),
            placement_mode=request.placement_mode.value
        )
        
        return Generate3DModelResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating 3D model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate 3D model: {str(e)}"
        )



@router.post("/placement/auto", response_model=CalculatePlacementResponse)
async def calculate_auto_placement(request: CalculatePlacementRequest):
    """
    Calculate automatic module placement.
    
    This endpoint uses optimization algorithms to automatically place
    modules on the roof surface, considering:
    - Roof dimensions and geometry
    - Module spacing requirements
    - Edge margins
    - Optimal orientation
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        positions = visualization_service.calculate_auto_placement(
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict(),
            module_config=request.module_config.dict()
        )
        
        # Calculate statistics
        statistics = visualization_service._calculate_placement_statistics(
            positions=positions,
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict()
        )
        
        return CalculatePlacementResponse(
            positions=positions,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Error calculating auto placement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate placement: {str(e)}"
        )



@router.post("/placement/validate", response_model=CalculatePlacementResponse)
async def validate_manual_placement(request: ValidateManualPlacementRequest):
    """
    Validate and process manual module placement.
    
    This endpoint validates manually specified module positions and
    calculates missing parameters (Z position, tilt angle, etc.).
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        positions = visualization_service.calculate_manual_placement(
            positions=[pos.dict() for pos in request.positions],
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict()
        )
        
        # Calculate statistics
        statistics = visualization_service._calculate_placement_statistics(
            positions=positions,
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict()
        )
        
        return CalculatePlacementResponse(
            positions=positions,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Error validating manual placement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate placement: {str(e)}"
        )



@router.post("/collisions/detect", response_model=DetectCollisionsResponse)
async def detect_collisions(request: DetectCollisionsRequest):
    """
    Detect collisions between modules and with building boundaries.
    
    This endpoint checks for:
    - Module-to-module overlaps
    - Boundary violations (modules outside roof area)
    - Clearance violations (insufficient spacing)
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        result = visualization_service.detect_collisions(
            module_positions=request.module_positions,
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict()
        )
        
        return DetectCollisionsResponse(**result)
        
    except Exception as e:
        logger.error(f"Error detecting collisions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect collisions: {str(e)}"
        )



@router.post("/export/model", response_model=Export3DModelResponse)
async def export_3d_model(request: Export3DModelRequest):
    """
    Export 3D model to specified format.
    
    Supported formats:
    - STL: Standard Tessellation Language (for 3D printing)
    - OBJ: Wavefront OBJ (widely supported)
    - GLTF: GL Transmission Format (web-friendly)
    - GLB: Binary GLTF (compact)
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        file_data = visualization_service.export_3d_model(
            scene_data=request.scene_data,
            format=request.format.value,
            options=request.options
        )
        
        # Encode to base64
        data_base64 = base64.b64encode(file_data).decode('utf-8')
        
        return Export3DModelResponse(
            file_name=f"pv_system.{request.format.value}",
            file_size_bytes=len(file_data),
            format=request.format.value,
            data_base64=data_base64
        )
        
    except Exception as e:
        logger.error(f"Error exporting 3D model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export 3D model: {str(e)}"
        )



@router.post("/export/multi-view", response_model=ExportMultiViewResponse)
async def export_multi_view(request: ExportMultiViewRequest):
    """
    Export multiple views of the 3D model.
    
    Available views:
    - front: Front elevation
    - side: Side elevation
    - top: Top view (plan)
    - perspective: 3D perspective view
    - isometric: Isometric projection
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        views_data = visualization_service.export_multi_view(
            scene_data=request.scene_data,
            views=[view.value for view in request.views],
            options=request.options
        )
        
        # Encode all views to base64
        views_base64 = {}
        file_sizes = {}
        
        for view_name, view_data in views_data.items():
            views_base64[view_name] = base64.b64encode(view_data).decode('utf-8')
            file_sizes[view_name] = len(view_data)
        
        return ExportMultiViewResponse(
            views=views_base64,
            file_sizes=file_sizes
        )
        
    except Exception as e:
        logger.error(f"Error exporting multi-view: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export multi-view: {str(e)}"
        )



@router.post("/export/animation", response_model=Create360AnimationResponse)
async def create_360_animation(request: Create360AnimationRequest):
    """
    Create 360-degree rotation animation.
    
    This endpoint generates an animated view of the 3D model rotating
    360 degrees around the vertical axis. Useful for presentations
    and marketing materials.
    
    Options:
    - frames: Number of frames (default: 36)
    - duration: Duration in seconds (default: 3.6)
    - format: "gif" or "mp4" (default: "gif")
    """
    if not visualization_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="3D visualization service not available"
        )
    
    try:
        options = request.options or {}
        frames = options.get("frames", 36)
        duration = options.get("duration", 3.6)
        anim_format = options.get("format", "gif")
        
        animation_data = visualization_service.create_360_animation(
            scene_data=request.scene_data,
            options=options
        )
        
        # Encode to base64
        data_base64 = base64.b64encode(animation_data).decode('utf-8')
        
        return Create360AnimationResponse(
            file_name=f"pv_system_360.{anim_format}",
            file_size_bytes=len(animation_data),
            format=anim_format,
            duration_seconds=duration,
            frames=frames,
            data_base64=data_base64
        )
        
    except Exception as e:
        logger.error(f"Error creating 360 animation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create animation: {str(e)}"
        )
