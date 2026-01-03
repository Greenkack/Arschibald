"""
Pydantic schemas for 3D Visualization Service
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum


class RoofType(str, Enum):
    """Supported roof types."""
    FLAT = "flat"
    GABLE = "gable"
    HIP = "hip"
    SHED = "shed"
    MANSARD = "mansard"


class ExportFormat(str, Enum):
    """Supported 3D export formats."""
    STL = "stl"
    OBJ = "obj"
    GLTF = "gltf"
    GLB = "glb"


class ViewType(str, Enum):
    """Supported view types for multi-view export."""
    FRONT = "front"
    SIDE = "side"
    TOP = "top"
    PERSPECTIVE = "perspective"
    ISOMETRIC = "isometric"


class PlacementMode(str, Enum):
    """Module placement modes."""
    AUTO = "auto"
    MANUAL = "manual"


# ============================================================================
# Request Schemas
# ============================================================================

class BuildingDimsRequest(BaseModel):
    """Building dimensions for 3D modeling."""
    length_m: float = Field(..., gt=0, le=100, description="Building length in meters")
    width_m: float = Field(..., gt=0, le=100, description="Building width in meters")
    wall_height_m: float = Field(..., gt=0, le=50, description="Wall height in meters")


class RoofConfigRequest(BaseModel):
    """Roof configuration."""
    type: RoofType = Field(..., description="Roof type")
    angle: float = Field(15.0, ge=0, le=90, description="Roof angle in degrees")
    orientation: str = Field("south", description="Roof orientation (north, south, east, west)")
    covering: Optional[str] = Field("Ziegel", description="Roof covering material")


class ModuleConfigRequest(BaseModel):
    """Module configuration."""
    count: int = Field(..., gt=0, le=500, description="Number of modules")
    type: Optional[str] = Field("standard", description="Module type")
    spacing: float = Field(0.02, ge=0, le=1.0, description="Spacing between modules in meters")
    margin: float = Field(0.5, ge=0, le=5.0, description="Margin from roof edge in meters")
    manual_positions: Optional[List[Dict[str, Any]]] = Field(None, description="Manual positions for modules")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Placement constraints")


class Generate3DModelRequest(BaseModel):
    """Request to generate a 3D model."""
    building_dims: BuildingDimsRequest
    roof_config: RoofConfigRequest
    module_config: ModuleConfigRequest
    placement_mode: PlacementMode = Field(PlacementMode.AUTO, description="Placement mode")


class ModulePositionRequest(BaseModel):
    """Single module position."""
    index: int = Field(..., ge=0, description="Module index")
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: Optional[float] = Field(None, description="Z coordinate in meters (auto-calculated if not provided)")
    azimuth: float = Field(0.0, ge=0, le=360, description="Azimuth angle in degrees")
    tilt: Optional[float] = Field(None, ge=0, le=90, description="Tilt angle in degrees (auto-calculated if not provided)")


class CalculatePlacementRequest(BaseModel):
    """Request to calculate module placement."""
    building_dims: BuildingDimsRequest
    roof_config: RoofConfigRequest
    module_config: ModuleConfigRequest


class ValidateManualPlacementRequest(BaseModel):
    """Request to validate manual placement."""
    positions: List[ModulePositionRequest]
    building_dims: BuildingDimsRequest
    roof_config: RoofConfigRequest


class DetectCollisionsRequest(BaseModel):
    """Request to detect collisions."""
    module_positions: List[Dict[str, Any]]
    building_dims: BuildingDimsRequest
    roof_config: RoofConfigRequest


class Export3DModelRequest(BaseModel):
    """Request to export 3D model."""
    scene_data: Dict[str, Any]
    format: ExportFormat
    options: Optional[Dict[str, Any]] = Field(None, description="Export options")


class ExportMultiViewRequest(BaseModel):
    """Request to export multiple views."""
    scene_data: Dict[str, Any]
    views: List[ViewType]
    options: Optional[Dict[str, Any]] = Field(None, description="Export options")


class Create360AnimationRequest(BaseModel):
    """Request to create 360-degree animation."""
    scene_data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = Field(None, description="Animation options (frames, duration, etc.)")


# ============================================================================
# Response Schemas
# ============================================================================

class ModulePositionResponse(BaseModel):
    """Module position response."""
    index: int
    x: float
    y: float
    z: float
    azimuth: float
    tilt: float


class PlacementStatistics(BaseModel):
    """Statistics about module placement."""
    total_modules: int
    total_area_m2: float
    roof_coverage_percent: float
    average_spacing_m: float


class Generate3DModelResponse(BaseModel):
    """Response from 3D model generation."""
    scene_data: Dict[str, Any]
    module_positions: List[ModulePositionResponse]
    statistics: PlacementStatistics
    warnings: List[str]


class CalculatePlacementResponse(BaseModel):
    """Response from placement calculation."""
    positions: List[ModulePositionResponse]
    statistics: PlacementStatistics


class CollisionDetail(BaseModel):
    """Details about a collision."""
    type: str = Field(..., description="Collision type (module_overlap, boundary_violation, clearance_violation)")
    module: Optional[int] = Field(None, description="Module index")
    module1: Optional[int] = Field(None, description="First module index (for overlaps)")
    module2: Optional[int] = Field(None, description="Second module index (for overlaps)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class DetectCollisionsResponse(BaseModel):
    """Response from collision detection."""
    has_collisions: bool
    collisions: List[CollisionDetail]
    warnings: List[str]


class Export3DModelResponse(BaseModel):
    """Response from 3D model export."""
    file_name: str
    file_size_bytes: int
    format: str
    data_base64: str = Field(..., description="Base64-encoded file data")


class ExportMultiViewResponse(BaseModel):
    """Response from multi-view export."""
    views: Dict[str, str] = Field(..., description="Dictionary mapping view names to base64-encoded image data")
    file_sizes: Dict[str, int] = Field(..., description="Dictionary mapping view names to file sizes")


class Create360AnimationResponse(BaseModel):
    """Response from 360 animation creation."""
    file_name: str
    file_size_bytes: int
    format: str
    duration_seconds: float
    frames: int
    data_base64: str = Field(..., description="Base64-encoded animation data")


class VisualizationHealthResponse(BaseModel):
    """Health check response for visualization service."""
    available: bool
    version: Optional[str] = None
    supported_formats: List[str]
    supported_roof_types: List[str]
    message: Optional[str] = None
