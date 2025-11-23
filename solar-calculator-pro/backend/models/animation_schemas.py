"""
Pydantic schemas for 3D Animation system

Requirements: 1.3, 6.1
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from enum import Enum


class AnimationType(str, Enum):
    """Types of 3D animations"""
    ROTATION_360 = "rotation_360"
    FLY_THROUGH = "fly_through"
    ASSEMBLY = "assembly"
    TIME_LAPSE = "time_lapse"
    PRESENTATION = "presentation"
    CUSTOM = "custom"


class AnimationFormat(str, Enum):
    """Export formats for animations"""
    GIF = "gif"
    MP4 = "mp4"
    WEBM = "webm"
    FRAMES = "frames"


class AnimationQuality(str, Enum):
    """Quality presets for animation export"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class Vector3D(BaseModel):
    """3D vector/point"""
    x: float
    y: float
    z: float
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> 'Vector3D':
        return cls(x=t[0], y=t[1], z=t[2])


class CameraState(BaseModel):
    """Camera state for a single frame"""
    position: Vector3D
    target: Vector3D
    up: Vector3D = Field(default=Vector3D(x=0, y=0, z=1))
    fov: Optional[float] = Field(default=60, ge=10, le=120)


class AnimationFrameSchema(BaseModel):
    """Schema for a single animation frame"""
    frame_number: int = Field(ge=0)
    timestamp: float = Field(ge=0)
    camera: CameraState
    sun_position: Optional[Vector3D] = None
    visible_objects: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AnimationConfigSchema(BaseModel):
    """Configuration for animation generation"""
    animation_type: AnimationType
    duration: float = Field(gt=0, le=300, description="Duration in seconds (max 5 minutes)")
    fps: int = Field(ge=15, le=60, description="Frames per second")
    width: int = Field(ge=640, le=3840, description="Width in pixels")
    height: int = Field(ge=480, le=2160, description="Height in pixels")
    quality: AnimationQuality = AnimationQuality.MEDIUM
    loop: bool = True
    smooth_transitions: bool = True
    
    @validator('fps')
    def validate_fps(cls, v):
        """Ensure FPS is a reasonable value"""
        if v not in [15, 24, 30, 60]:
            raise ValueError('FPS must be one of: 15, 24, 30, 60')
        return v
    
    @property
    def resolution(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    @property
    def total_frames(self) -> int:
        return int(self.duration * self.fps)


class Rotation360Config(BaseModel):
    """Configuration for 360° rotation animation"""
    center_point: Vector3D
    radius: float = Field(gt=0, description="Distance from center point")
    height: float = Field(gt=0, description="Camera height above center")
    start_angle: float = Field(default=0, ge=0, lt=360, description="Starting angle in degrees")
    clockwise: bool = True


class Waypoint(BaseModel):
    """Waypoint for fly-through animation"""
    position: Vector3D
    look_at: Vector3D
    duration: Optional[float] = Field(default=None, gt=0, description="Time to spend at this waypoint")
    ease_in: bool = True
    ease_out: bool = True


class FlyThroughConfig(BaseModel):
    """Configuration for fly-through animation"""
    waypoints: List[Waypoint] = Field(min_items=2)
    
    @validator('waypoints')
    def validate_waypoints(cls, v):
        """Ensure at least 2 waypoints"""
        if len(v) < 2:
            raise ValueError('At least 2 waypoints required')
        return v


class AssemblyObject(BaseModel):
    """Object configuration for assembly animation"""
    id: str
    name: str
    position: Vector3D
    rotation: Optional[Vector3D] = None
    scale: Optional[Vector3D] = None
    appear_time: Optional[float] = None  # When object should appear (0-1)
    animation_duration: float = Field(default=0.5, gt=0, description="Time for object to appear")


class AssemblyConfig(BaseModel):
    """Configuration for assembly animation"""
    objects: List[AssemblyObject] = Field(min_items=1)
    camera_position: Vector3D
    camera_target: Vector3D
    sequential: bool = True  # If False, objects appear simultaneously
    
    @validator('objects')
    def validate_objects(cls, v):
        """Ensure unique object IDs"""
        ids = [obj.id for obj in v]
        if len(ids) != len(set(ids)):
            raise ValueError('Object IDs must be unique')
        return v


class TimeLapseConfig(BaseModel):
    """Configuration for time-lapse animation"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    date: datetime
    start_hour: float = Field(default=6, ge=0, lt=24, description="Start time (24h format)")
    end_hour: float = Field(default=18, ge=0, lt=24, description="End time (24h format)")
    camera_position: Vector3D
    camera_target: Vector3D
    show_sun: bool = True
    show_shadows: bool = True
    
    @validator('end_hour')
    def validate_hours(cls, v, values):
        """Ensure end_hour is after start_hour"""
        if 'start_hour' in values and v <= values['start_hour']:
            raise ValueError('end_hour must be after start_hour')
        return v


class PresentationScene(BaseModel):
    """Scene configuration for presentation mode"""
    name: str
    description: Optional[str] = None
    duration: float = Field(gt=0, description="Duration of this scene in seconds")
    camera: CameraState
    visible_objects: Optional[List[str]] = None
    transition_type: str = Field(default="fade", pattern="^(fade|cut|slide)$")
    annotations: Optional[List[Dict[str, Any]]] = None


class PresentationConfig(BaseModel):
    """Configuration for presentation mode animation"""
    scenes: List[PresentationScene] = Field(min_items=1)
    title: Optional[str] = None
    subtitle: Optional[str] = None
    show_scene_titles: bool = True
    
    @validator('scenes')
    def validate_scenes(cls, v):
        """Ensure unique scene names"""
        names = [scene.name for scene in v]
        if len(names) != len(set(names)):
            raise ValueError('Scene names must be unique')
        return v


class ExportConfig(BaseModel):
    """Configuration for animation export"""
    format: AnimationFormat
    filename: Optional[str] = None
    quality: AnimationQuality = AnimationQuality.MEDIUM
    optimize: bool = True
    watermark: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnimationMetadata(BaseModel):
    """Metadata about an animation"""
    animation_id: str
    animation_type: AnimationType
    created_at: datetime
    frame_count: int
    duration: float
    fps: int
    resolution: Tuple[int, int]
    file_size: Optional[int] = None
    has_sun_data: bool = False
    has_visibility_data: bool = False
    camera_path_length: Optional[float] = None
    tags: Optional[List[str]] = None


class AnimationCreateRequest(BaseModel):
    """Request to create an animation"""
    animation_type: AnimationType
    config: AnimationConfigSchema
    rotation_360: Optional[Rotation360Config] = None
    fly_through: Optional[FlyThroughConfig] = None
    assembly: Optional[AssemblyConfig] = None
    time_lapse: Optional[TimeLapseConfig] = None
    presentation: Optional[PresentationConfig] = None
    
    @validator('rotation_360', 'fly_through', 'assembly', 'time_lapse', 'presentation')
    def validate_type_config(cls, v, values, field):
        """Ensure the correct config is provided for the animation type"""
        if 'animation_type' not in values:
            return v
        
        animation_type = values['animation_type']
        field_name = field.name
        
        # Map animation types to their required config fields
        type_config_map = {
            AnimationType.ROTATION_360: 'rotation_360',
            AnimationType.FLY_THROUGH: 'fly_through',
            AnimationType.ASSEMBLY: 'assembly',
            AnimationType.TIME_LAPSE: 'time_lapse',
            AnimationType.PRESENTATION: 'presentation'
        }
        
        required_field = type_config_map.get(animation_type)
        
        if required_field == field_name and v is None:
            raise ValueError(f'{field_name} configuration required for {animation_type.value} animation')
        
        return v


class AnimationCreateResponse(BaseModel):
    """Response after creating an animation"""
    animation_id: str
    animation_type: AnimationType
    frame_count: int
    duration: float
    fps: int
    resolution: Tuple[int, int]
    status: str = "created"
    message: Optional[str] = None


class AnimationExportRequest(BaseModel):
    """Request to export an animation"""
    animation_id: str
    export_config: ExportConfig


class AnimationExportResponse(BaseModel):
    """Response after exporting an animation"""
    success: bool
    animation_id: str
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    format: AnimationFormat
    error: Optional[str] = None


class AnimationListResponse(BaseModel):
    """Response for listing animations"""
    animations: List[AnimationMetadata]
    total: int
    page: int
    page_size: int


class AnimationStatusResponse(BaseModel):
    """Response for animation status"""
    animation_id: str
    status: str  # "created", "rendering", "completed", "failed"
    progress: Optional[float] = Field(default=None, ge=0, le=1)
    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    error: Optional[str] = None
