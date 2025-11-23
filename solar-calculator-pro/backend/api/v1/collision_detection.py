"""
Collision Detection API Endpoints

This module provides REST API endpoints for 3D collision detection functionality.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from backend.services.collision_detection_service import (
    CollisionDetectionService,
    Obstacle,
    BoundingBox
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collision-detection", tags=["Collision Detection"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ModulePosition(BaseModel):
    """Module position model."""
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")
    azimuth: float = Field(0.0, description="Azimuth angle in degrees")
    tilt: float = Field(0.0, description="Tilt angle in degrees")
    index: Optional[int] = Field(None, description="Module index")


class RoofBoundaries(BaseModel):
    """Roof boundary model."""
    min_x: float = Field(..., description="Minimum X coordinate")
    max_x: float = Field(..., description="Maximum X coordinate")
    min_y: float = Field(..., description="Minimum Y coordinate")
    max_y: float = Field(..., description="Maximum Y coordinate")
    min_z: float = Field(0.0, description="Minimum Z coordinate")
    max_z: float = Field(100.0, description="Maximum Z coordinate")


class ObstacleModel(BaseModel):
    """Obstacle model."""
    id: int = Field(..., description="Obstacle ID")
    name: str = Field(..., description="Obstacle name")
    obstacle_type: str = Field(..., description="Type of obstacle")
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float


class RoofEdge(BaseModel):
    """Roof edge model."""
    position: List[float] = Field(..., description="Edge position [x, y, z]")
    normal: List[float] = Field(..., description="Edge normal vector [x, y, z]")


class DetectModuleCollisionsRequest(BaseModel):
    """Request model for module collision detection."""
    module_positions: List[ModulePosition] = Field(..., description="List of module positions")
    module_width: Optional[float] = Field(1.05, description="Module width in meters")
    module_height: Optional[float] = Field(1.76, description="Module height in meters")
    module_thickness: Optional[float] = Field(0.04, description="Module thickness in meters")


class DetectObstacleCollisionsRequest(BaseModel):
    """Request model for obstacle collision detection."""
    module_positions: List[ModulePosition]
    obstacles: List[ObstacleModel]
    module_width: Optional[float] = 1.05
    module_height: Optional[float] = 1.76
    module_thickness: Optional[float] = 0.04


class DetectBoundaryViolationsRequest(BaseModel):
    """Request model for boundary violation detection."""
    module_positions: List[ModulePosition]
    roof_boundaries: RoofBoundaries
    module_width: Optional[float] = 1.05
    module_height: Optional[float] = 1.76
    module_thickness: Optional[float] = 0.04


class DetectOverhangsRequest(BaseModel):
    """Request model for overhang detection."""
    module_positions: List[ModulePosition]
    roof_edges: List[RoofEdge]
    module_width: Optional[float] = 1.05
    module_height: Optional[float] = 1.76
    module_thickness: Optional[float] = 0.04
    max_overhang: Optional[float] = 0.1


class ValidateClearancesRequest(BaseModel):
    """Request model for clearance validation."""
    module_positions: List[ModulePosition]
    module_width: Optional[float] = 1.05
    module_height: Optional[float] = 1.76
    module_thickness: Optional[float] = 0.04
    min_clearance: Optional[float] = 0.02


class ComprehensiveCollisionDetectionRequest(BaseModel):
    """Request model for comprehensive collision detection."""
    module_positions: List[ModulePosition]
    roof_boundaries: RoofBoundaries
    obstacles: Optional[List[ObstacleModel]] = None
    roof_edges: Optional[List[RoofEdge]] = None
    module_width: Optional[float] = 1.05
    module_height: Optional[float] = 1.76
    module_thickness: Optional[float] = 0.04
    min_clearance: Optional[float] = 0.02
    max_overhang: Optional[float] = 0.1


class CollisionResponse(BaseModel):
    """Response model for collision detection."""
    has_collisions: bool
    total_collisions: int
    collisions_by_type: Dict[str, List[Dict[str, Any]]]
    critical_count: int
    warning_count: int
    all_collisions: List[Dict[str, Any]]


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/module-collisions", response_model=Dict[str, Any])
async def detect_module_collisions(request: DetectModuleCollisionsRequest):
    """
    Detect collisions between modules.
    
    This endpoint checks for overlaps and intersections between PV modules.
    
    **Returns:**
    - List of collision information objects
    - Each collision includes type, severity, affected modules, and resolution suggestions
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        collisions = service.detect_module_collisions(module_positions)
        
        return {
            "success": True,
            "collision_count": len(collisions),
            "collisions": [service._collision_to_dict(c) for c in collisions]
        }
        
    except Exception as e:
        logger.error(f"Error detecting module collisions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect module collisions: {str(e)}"
        )


@router.post("/obstacle-collisions", response_model=Dict[str, Any])
async def detect_obstacle_collisions(request: DetectObstacleCollisionsRequest):
    """
    Detect collisions between modules and obstacles.
    
    This endpoint checks for collisions with obstacles like chimneys, skylights, vents, etc.
    
    **Returns:**
    - List of collision information objects
    - Each collision includes affected module, obstacle details, and resolution suggestions
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        
        # Convert obstacle models to Obstacle objects
        obstacles = []
        for obs in request.obstacles:
            bbox = BoundingBox(
                min_x=obs.min_x,
                min_y=obs.min_y,
                min_z=obs.min_z,
                max_x=obs.max_x,
                max_y=obs.max_y,
                max_z=obs.max_z
            )
            obstacles.append(Obstacle(
                id=obs.id,
                name=obs.name,
                bbox=bbox,
                obstacle_type=obs.obstacle_type
            ))
        
        collisions = service.detect_obstacle_collisions(module_positions, obstacles)
        
        return {
            "success": True,
            "collision_count": len(collisions),
            "collisions": [service._collision_to_dict(c) for c in collisions]
        }
        
    except Exception as e:
        logger.error(f"Error detecting obstacle collisions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect obstacle collisions: {str(e)}"
        )


@router.post("/boundary-violations", response_model=Dict[str, Any])
async def detect_boundary_violations(request: DetectBoundaryViolationsRequest):
    """
    Detect modules that exceed roof boundaries.
    
    This endpoint checks if any modules extend beyond the defined roof boundaries.
    
    **Returns:**
    - List of boundary violation information
    - Each violation includes direction, distance, and resolution suggestions
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        roof_boundaries = request.roof_boundaries.dict()
        
        violations = service.detect_boundary_violations(module_positions, roof_boundaries)
        
        return {
            "success": True,
            "violation_count": len(violations),
            "violations": [service._collision_to_dict(v) for v in violations]
        }
        
    except Exception as e:
        logger.error(f"Error detecting boundary violations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect boundary violations: {str(e)}"
        )


@router.post("/overhangs", response_model=Dict[str, Any])
async def detect_overhangs(request: DetectOverhangsRequest):
    """
    Detect modules with excessive overhang beyond roof edges.
    
    This endpoint checks if modules extend too far beyond roof edges, which could
    cause structural or aesthetic issues.
    
    **Returns:**
    - List of overhang information
    - Each overhang includes distance and resolution suggestions
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness,
            max_overhang=request.max_overhang
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        roof_edges = [edge.dict() for edge in request.roof_edges]
        
        overhangs = service.detect_overhangs(module_positions, roof_edges)
        
        return {
            "success": True,
            "overhang_count": len(overhangs),
            "overhangs": [service._collision_to_dict(o) for o in overhangs]
        }
        
    except Exception as e:
        logger.error(f"Error detecting overhangs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect overhangs: {str(e)}"
        )


@router.post("/clearance-validation", response_model=Dict[str, Any])
async def validate_clearances(request: ValidateClearancesRequest):
    """
    Validate minimum clearance between modules.
    
    This endpoint checks if modules maintain the required minimum spacing for
    proper installation and maintenance access.
    
    **Returns:**
    - List of clearance violations
    - Each violation includes affected modules, current spacing, and required spacing
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness,
            min_clearance=request.min_clearance
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        
        violations = service.validate_clearances(module_positions)
        
        return {
            "success": True,
            "violation_count": len(violations),
            "violations": [service._collision_to_dict(v) for v in violations]
        }
        
    except Exception as e:
        logger.error(f"Error validating clearances: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate clearances: {str(e)}"
        )


@router.post("/comprehensive", response_model=CollisionResponse)
async def detect_all_collisions(request: ComprehensiveCollisionDetectionRequest):
    """
    Perform comprehensive collision detection.
    
    This endpoint performs all collision detection checks in one call:
    - Module-to-module collisions
    - Module-to-obstacle collisions
    - Boundary violations
    - Overhang detection
    - Clearance validation
    
    **Returns:**
    - Complete collision analysis with all detected issues
    - Grouped by collision type
    - Includes severity levels and resolution suggestions
    """
    try:
        service = CollisionDetectionService(
            module_width=request.module_width,
            module_height=request.module_height,
            module_thickness=request.module_thickness,
            min_clearance=request.min_clearance,
            max_overhang=request.max_overhang
        )
        
        module_positions = [pos.dict() for pos in request.module_positions]
        roof_boundaries = request.roof_boundaries.dict()
        
        # Convert obstacles if provided
        obstacles = None
        if request.obstacles:
            obstacles = []
            for obs in request.obstacles:
                bbox = BoundingBox(
                    min_x=obs.min_x,
                    min_y=obs.min_y,
                    min_z=obs.min_z,
                    max_x=obs.max_x,
                    max_y=obs.max_y,
                    max_z=obs.max_z
                )
                obstacles.append(Obstacle(
                    id=obs.id,
                    name=obs.name,
                    bbox=bbox,
                    obstacle_type=obs.obstacle_type
                ))
        
        # Convert roof edges if provided
        roof_edges = None
        if request.roof_edges:
            roof_edges = [edge.dict() for edge in request.roof_edges]
        
        result = service.detect_all_collisions(
            module_positions=module_positions,
            roof_boundaries=roof_boundaries,
            obstacles=obstacles,
            roof_edges=roof_edges
        )
        
        return CollisionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error performing comprehensive collision detection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform comprehensive collision detection: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for collision detection service."""
    return {
        "status": "healthy",
        "service": "collision_detection",
        "version": "1.0.0"
    }
