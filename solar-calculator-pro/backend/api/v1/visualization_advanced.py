"""
Advanced 3D Visualization API Endpoints

Provides REST API endpoints for advanced 3D visualization features.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import logging

from backend.services.visualization_advanced_service import (
    VisualizationAdvancedService,
    PlacementConstraints
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualization/advanced", tags=["3D Visualization Advanced"])

# Initialize service
viz_service = VisualizationAdvancedService()


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
    type: str = Field("auto", description="Roof type (flat, gable, hip, auto)")
    angle: Optional[float] = Field(None, ge=0, le=90, description="Roof angle in degrees")
    orientation: Optional[str] = Field(None, description="Roof orientation (north, south, east, west)")


class ModuleConfigModel(BaseModel):
    """Module configuration model."""
    count: int = Field(..., gt=0, description="Number of modules")
    module_power_w: float = Field(400, gt=0, description="Module power in watts")
    module_weight_kg: float = Field(20.0, gt=0, description="Module weight in kg")
    module_efficiency: float = Field(0.20, gt=0, le=1, description="Module efficiency")
    min_spacing: float = Field(0.02, ge=0, description="Minimum spacing between modules")
    min_edge_distance: float = Field(0.5, ge=0, description="Minimum distance from edge")
    avoid_shading: bool = Field(True, description="Avoid shading areas")
    optimize_for: str = Field("max_modules", description="Optimization goal")
    manual_positions: Optional[List[Dict[str, Any]]] = Field(None, description="Manual positions")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints")


class RenderingOptionsModel(BaseModel):
    """Rendering options model."""
    show_mounting: bool = Field(True, description="Show mounting system")
    show_labels: bool = Field(False, description="Show module labels")
    color_scheme: str = Field("default", description="Color scheme")
    lighting: str = Field("realistic", description="Lighting mode")


class Complete3DModelRequest(BaseModel):
    """Request model for complete 3D model generation."""
    building_dims: BuildingDimsModel
    roof_config: RoofConfigModel
    module_config: ModuleConfigModel
    placement_mode: str = Field("auto", description="Placement mode (auto or manual)")
    rendering_options: Optional[RenderingOptionsModel] = None


class MultiViewExportRequest(BaseModel):
    """Request model for multi-view export."""
    scene_data: Dict[str, Any]
    views: Optional[List[str]] = Field(None, description="List of views to export")
    format: str = Field("png", description="Image format")
    resolution: List[int] = Field([1920, 1080], description="Resolution [width, height]")


class AnimationRequest(BaseModel):
    """Request model for animation generation."""
    scene_data: Dict[str, Any]
    frames: int = Field(60, gt=0, description="Number of frames")
    duration_seconds: float = Field(6.0, gt=0, description="Duration in seconds")
    format: str = Field("gif", description="Animation format")


class PresentationAnimationRequest(BaseModel):
    """Request model for presentation animation."""
    scene_data: Dict[str, Any]
    animation_type: str = Field("assembly", description="Animation type")
    options: Optional[Dict[str, Any]] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate-complete-model")
async def generate_complete_3d_model(request: Complete3DModelRequest) -> Dict[str, Any]:
    """
    Generate a complete 3D model with all advanced features.
    
    This endpoint provides:
    - Complete 3D scene generation
    - Automatic or manual module placement
    - Collision detection
    - Mounting system calculations
    - Comprehensive statistics
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        result = viz_service.generate_complete_3d_model(
            building_dims=request.building_dims.dict(),
            roof_config=request.roof_config.dict(),
            module_config=request.module_config.dict(),
            placement_mode=request.placement_mode,
            rendering_options=request.rendering_options.dict() if request.rendering_options else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating complete 3D model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-roof-type")
async def detect_roof_type(
    building_dims: BuildingDimsModel,
    roof_hints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Detect roof type from building dimensions and optional hints.
    
    Returns detected roof type, confidence, and calculated parameters.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        result = viz_service.detect_roof_type(
            building_dims=building_dims.dict(),
            roof_hints=roof_hints
        )
        
        return {
            "roof_type": result.roof_type,
            "confidence": result.confidence,
            "angle_deg": result.angle_deg,
            "orientation": result.orientation,
            "area_m2": result.area_m2,
            "usable_area_m2": result.usable_area_m2,
            "parameters": result.parameters
        }
        
    except Exception as e:
        logger.error(f"Error detecting roof type: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-collisions")
async def detect_collisions(
    module_positions: List[Dict[str, Any]],
    building_dims: BuildingDimsModel,
    roof_config: RoofConfigModel,
    tolerance: float = Query(0.01, ge=0, description="Collision tolerance in meters")
) -> Dict[str, Any]:
    """
    Detect collisions between modules and with boundaries.
    
    Returns detailed collision information with severity and recommendations.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        result = viz_service.detect_collisions_advanced(
            module_positions=module_positions,
            building_dims=building_dims.dict(),
            roof_config=roof_config.dict(),
            tolerance=tolerance
        )
        
        return {
            "has_collisions": result.has_collisions,
            "collision_count": result.collision_count,
            "collisions": result.collisions,
            "severity": result.severity,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error detecting collisions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-automatic-placement")
async def calculate_automatic_placement(
    building_dims: BuildingDimsModel,
    roof_config: RoofConfigModel,
    module_config: ModuleConfigModel
) -> Dict[str, Any]:
    """
    Calculate automatic module placement with optimization.
    
    Returns optimized module positions based on constraints.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        positions = viz_service.calculate_automatic_placement(
            building_dims=building_dims.dict(),
            roof_config=roof_config.dict(),
            module_config=module_config.dict()
        )
        
        return {
            "positions": positions,
            "count": len(positions)
        }
        
    except Exception as e:
        logger.error(f"Error calculating automatic placement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-manual-placement")
async def validate_manual_placement(
    positions: List[Dict[str, Any]],
    building_dims: BuildingDimsModel,
    roof_config: RoofConfigModel,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate manual module placement against constraints.
    
    Returns validated positions with any warnings.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        validated = viz_service.validate_manual_placement(
            positions=positions,
            building_dims=building_dims.dict(),
            roof_config=roof_config.dict(),
            constraints=constraints or {}
        )
        
        return {
            "validated_positions": validated,
            "count": len(validated)
        }
        
    except Exception as e:
        logger.error(f"Error validating manual placement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-mounting-system")
async def calculate_mounting_system(
    module_positions: List[Dict[str, Any]],
    roof_config: RoofConfigModel,
    module_config: ModuleConfigModel
) -> Dict[str, Any]:
    """
    Calculate mounting system requirements and BOM.
    
    Returns mounting system details, BOM, and cost estimate.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        result = viz_service.calculate_mounting_system(
            module_positions=module_positions,
            roof_config=roof_config.dict(),
            module_config=module_config.dict()
        )
        
        return {
            "rail_count": result.rail_count,
            "clamp_count": result.clamp_count,
            "total_weight_kg": result.total_weight_kg,
            "cost_estimate": result.cost_estimate,
            "bom": result.bom,
            "installation_time_hours": result.installation_time_hours
        }
        
    except Exception as e:
        logger.error(f"Error calculating mounting system: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-multi-view")
async def export_multi_view(request: MultiViewExportRequest) -> Dict[str, Any]:
    """
    Export multiple views of the 3D model.
    
    Returns base64-encoded images for each requested view.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        result = viz_service.export_multi_view(
            scene_data=request.scene_data,
            views=request.views,
            format=request.format,
            resolution=tuple(request.resolution)
        )
        
        # Convert bytes to base64 for JSON response
        import base64
        encoded_result = {}
        for view_name, image_bytes in result.items():
            encoded_result[view_name] = base64.b64encode(image_bytes).decode('utf-8')
        
        return {
            "views": encoded_result,
            "format": request.format,
            "resolution": request.resolution
        }
        
    except Exception as e:
        logger.error(f"Error exporting multi-view: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-360-animation")
async def create_360_animation(request: AnimationRequest) -> Dict[str, Any]:
    """
    Create 360-degree rotation animation.
    
    Returns base64-encoded animation data.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        animation_data = viz_service.create_360_animation(
            scene_data=request.scene_data,
            frames=request.frames,
            duration_seconds=request.duration_seconds,
            format=request.format
        )
        
        # Convert to base64
        import base64
        encoded_animation = base64.b64encode(animation_data).decode('utf-8')
        
        return {
            "animation": encoded_animation,
            "format": request.format,
            "frames": request.frames,
            "duration_seconds": request.duration_seconds
        }
        
    except Exception as e:
        logger.error(f"Error creating 360 animation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-presentation-animation")
async def create_presentation_animation(request: PresentationAnimationRequest) -> Dict[str, Any]:
    """
    Create presentation-quality animation.
    
    Supports assembly, flythrough, and exploded view animations.
    """
    try:
        if not viz_service.is_available():
            raise HTTPException(status_code=503, detail="3D visualization service not available")
        
        animation_data = viz_service.create_presentation_animation(
            scene_data=request.scene_data,
            animation_type=request.animation_type,
            options=request.options
        )
        
        # Convert to base64
        import base64
        encoded_animation = base64.b64encode(animation_data).decode('utf-8')
        
        return {
            "animation": encoded_animation,
            "animation_type": request.animation_type,
            "format": "gif"
        }
        
    except Exception as e:
        logger.error(f"Error creating presentation animation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check if the advanced visualization service is available."""
    return {
        "status": "available" if viz_service.is_available() else "unavailable",
        "service": "3D Visualization Advanced"
    }
