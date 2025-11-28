"""
Dynamic Building Geometry API

Provides REST API for dynamic building geometry:
- Building type selection (single family, multi-family)
- All roof types (Satteldach, Pultdach, Flachdach, Walmdach, Krüppelwalmdach, Zeltdach)
- Dormer (Gaube) support
- Calculate building dimensions from input data
- Automatic geometry generation

Requirements: funktionen.txt - "Dynamische Geometrie"
Task: 270. Dynamic Building Geometry
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import math
import uuid

router = APIRouter(prefix="/3d/building", tags=["Building Geometry"])


# ==================== Enums ====================

class BuildingType(str, Enum):
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    TOWNHOUSE = "townhouse"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"


class RoofType(str, Enum):
    SATTELDACH = "satteldach"  # Gable roof
    PULTDACH = "pultdach"  # Mono-pitch/Shed roof
    FLACHDACH = "flachdach"  # Flat roof
    WALMDACH = "walmdach"  # Hip roof
    KRUEPPELWALMDACH = "krueppelwalmdach"  # Jerkinhead/Clipped gable
    ZELTDACH = "zeltdach"  # Pyramid/Tent roof
    MANSARDDACH = "mansarddach"  # Mansard roof


class DormerType(str, Enum):
    NONE = "none"
    SCHLEPPGAUBE = "schleppgaube"  # Shed dormer
    SPITZGAUBE = "spitzgaube"  # Gable dormer
    FLACHDACHGAUBE = "flachdachgaube"  # Flat roof dormer
    RUNDGAUBE = "rundgaube"  # Eyebrow dormer


class RoofOrientation(str, Enum):
    NORTH = "north"
    NORTH_EAST = "north_east"
    EAST = "east"
    SOUTH_EAST = "south_east"
    SOUTH = "south"
    SOUTH_WEST = "south_west"
    WEST = "west"
    NORTH_WEST = "north_west"


# ==================== Pydantic Models ====================

class Dimensions(BaseModel):
    """3D dimensions"""
    width: float = Field(ge=1, le=100, description="Width in meters")
    length: float = Field(ge=1, le=100, description="Length in meters")
    height: float = Field(ge=1, le=50, description="Height in meters")


class RoofParameters(BaseModel):
    """Roof parameters"""
    roof_type: RoofType
    pitch_angle: float = Field(default=30, ge=0, le=60, description="Roof pitch in degrees")
    overhang: float = Field(default=0.5, ge=0, le=2, description="Roof overhang in meters")
    ridge_height: Optional[float] = None
    orientation: RoofOrientation = RoofOrientation.SOUTH


class DormerParameters(BaseModel):
    """Dormer parameters"""
    dormer_type: DormerType = DormerType.NONE
    count: int = Field(default=0, ge=0, le=10)
    width: float = Field(default=1.5, ge=0.5, le=4)
    height: float = Field(default=1.5, ge=0.5, le=3)
    position_from_edge: float = Field(default=2, ge=0.5, le=10)
    spacing: float = Field(default=3, ge=1, le=10)


class BuildingInput(BaseModel):
    """Building input parameters"""
    building_type: BuildingType = BuildingType.SINGLE_FAMILY
    dimensions: Dimensions
    roof: RoofParameters
    dormers: DormerParameters = DormerParameters()
    floors: int = Field(default=2, ge=1, le=10)
    floor_height: float = Field(default=2.8, ge=2.2, le=4)
    basement: bool = False
    garage_attached: bool = False
    garage_dimensions: Optional[Dimensions] = None


class Vertex(BaseModel):
    """3D vertex"""
    x: float
    y: float
    z: float


class Face(BaseModel):
    """3D face (polygon)"""
    vertices: List[int]
    normal: Optional[List[float]] = None
    material: str = "default"


class RoofSurface(BaseModel):
    """Roof surface for PV placement"""
    surface_id: str
    orientation: RoofOrientation
    pitch_angle: float
    area_m2: float
    usable_area_m2: float
    vertices: List[Vertex]
    center: Vertex
    suitable_for_pv: bool


class BuildingGeometry(BaseModel):
    """Complete building geometry"""
    building_id: str
    building_type: BuildingType
    vertices: List[Vertex]
    faces: List[Face]
    roof_surfaces: List[RoofSurface]
    total_roof_area_m2: float
    usable_roof_area_m2: float
    building_footprint_m2: float
    total_volume_m3: float
    bounding_box: Dict[str, float]
    generated_at: datetime


class GeometryPreset(BaseModel):
    """Geometry preset"""
    preset_id: str
    name: str
    description: str
    building_type: BuildingType
    roof_type: RoofType
    typical_dimensions: Dimensions
    typical_roof_pitch: float


# ==================== Helper Functions ====================

def generate_building_id() -> str:
    return f"bld_{uuid.uuid4().hex[:8]}"


def calculate_roof_height(width: float, pitch_angle: float, roof_type: RoofType) -> float:
    """Calculate roof ridge height based on pitch angle"""
    if roof_type == RoofType.FLACHDACH:
        return 0.3  # Minimal height for flat roof
    
    half_width = width / 2
    return half_width * math.tan(math.radians(pitch_angle))


def calculate_roof_area(dimensions: Dimensions, roof: RoofParameters) -> float:
    """Calculate total roof area"""
    width = dimensions.width
    length = dimensions.length
    pitch = roof.pitch_angle
    
    if roof.roof_type == RoofType.FLACHDACH:
        return width * length
    
    elif roof.roof_type == RoofType.SATTELDACH:
        # Two rectangular surfaces
        slope_length = (width / 2) / math.cos(math.radians(pitch))
        return 2 * slope_length * length
    
    elif roof.roof_type == RoofType.PULTDACH:
        # Single sloped surface
        slope_length = width / math.cos(math.radians(pitch))
        return slope_length * length
    
    elif roof.roof_type == RoofType.WALMDACH:
        # Four surfaces (2 trapezoids + 2 triangles)
        slope_length = (width / 2) / math.cos(math.radians(pitch))
        main_area = 2 * slope_length * length * 0.8  # Approximate
        hip_area = 2 * (width * slope_length * 0.5)
        return main_area + hip_area
    
    elif roof.roof_type == RoofType.ZELTDACH:
        # Four triangular surfaces
        slope_length = (width / 2) / math.cos(math.radians(pitch))
        return 4 * (0.5 * (width / 2) * slope_length)
    
    else:
        # Default calculation
        slope_length = (width / 2) / math.cos(math.radians(pitch))
        return 2 * slope_length * length


def generate_vertices_satteldach(dimensions: Dimensions, roof: RoofParameters) -> List[Vertex]:
    """Generate vertices for Satteldach (gable roof)"""
    w, l, h = dimensions.width, dimensions.length, dimensions.height
    ridge_h = calculate_roof_height(w, roof.pitch_angle, roof.roof_type)
    overhang = roof.overhang
    
    vertices = [
        # Base corners
        Vertex(x=0, y=0, z=0),
        Vertex(x=w, y=0, z=0),
        Vertex(x=w, y=l, z=0),
        Vertex(x=0, y=l, z=0),
        # Wall top corners
        Vertex(x=0, y=0, z=h),
        Vertex(x=w, y=0, z=h),
        Vertex(x=w, y=l, z=h),
        Vertex(x=0, y=l, z=h),
        # Ridge points
        Vertex(x=w/2, y=-overhang, z=h+ridge_h),
        Vertex(x=w/2, y=l+overhang, z=h+ridge_h),
        # Eave points with overhang
        Vertex(x=-overhang, y=-overhang, z=h),
        Vertex(x=w+overhang, y=-overhang, z=h),
        Vertex(x=w+overhang, y=l+overhang, z=h),
        Vertex(x=-overhang, y=l+overhang, z=h),
    ]
    
    return vertices


def generate_roof_surfaces(dimensions: Dimensions, roof: RoofParameters) -> List[RoofSurface]:
    """Generate roof surfaces for PV placement"""
    surfaces = []
    w, l = dimensions.width, dimensions.length
    pitch = roof.pitch_angle
    
    if roof.roof_type == RoofType.FLACHDACH:
        surfaces.append(RoofSurface(
            surface_id="roof_flat",
            orientation=RoofOrientation.SOUTH,
            pitch_angle=0,
            area_m2=w * l,
            usable_area_m2=w * l * 0.7,  # 70% usable
            vertices=[
                Vertex(x=0, y=0, z=dimensions.height),
                Vertex(x=w, y=0, z=dimensions.height),
                Vertex(x=w, y=l, z=dimensions.height),
                Vertex(x=0, y=l, z=dimensions.height)
            ],
            center=Vertex(x=w/2, y=l/2, z=dimensions.height),
            suitable_for_pv=True
        ))
    
    elif roof.roof_type == RoofType.SATTELDACH:
        slope_length = (w / 2) / math.cos(math.radians(pitch))
        area_per_side = slope_length * l
        
        # South-facing side
        surfaces.append(RoofSurface(
            surface_id="roof_south",
            orientation=roof.orientation,
            pitch_angle=pitch,
            area_m2=area_per_side,
            usable_area_m2=area_per_side * 0.8,
            vertices=[],  # Simplified
            center=Vertex(x=w*0.25, y=l/2, z=dimensions.height + calculate_roof_height(w, pitch, roof.roof_type)/2),
            suitable_for_pv=True
        ))
        
        # North-facing side
        north_orientation = RoofOrientation.NORTH if roof.orientation == RoofOrientation.SOUTH else RoofOrientation.SOUTH
        surfaces.append(RoofSurface(
            surface_id="roof_north",
            orientation=north_orientation,
            pitch_angle=pitch,
            area_m2=area_per_side,
            usable_area_m2=area_per_side * 0.8,
            vertices=[],
            center=Vertex(x=w*0.75, y=l/2, z=dimensions.height + calculate_roof_height(w, pitch, roof.roof_type)/2),
            suitable_for_pv=north_orientation != RoofOrientation.NORTH  # North not ideal for PV
        ))
    
    elif roof.roof_type == RoofType.PULTDACH:
        slope_length = w / math.cos(math.radians(pitch))
        surfaces.append(RoofSurface(
            surface_id="roof_main",
            orientation=roof.orientation,
            pitch_angle=pitch,
            area_m2=slope_length * l,
            usable_area_m2=slope_length * l * 0.85,
            vertices=[],
            center=Vertex(x=w/2, y=l/2, z=dimensions.height + calculate_roof_height(w, pitch, roof.roof_type)/2),
            suitable_for_pv=True
        ))
    
    return surfaces


def generate_building_geometry(input_data: BuildingInput) -> BuildingGeometry:
    """Generate complete building geometry"""
    building_id = generate_building_id()
    
    # Generate vertices based on roof type
    if input_data.roof.roof_type == RoofType.SATTELDACH:
        vertices = generate_vertices_satteldach(input_data.dimensions, input_data.roof)
    else:
        # Simplified vertices for other roof types
        w, l, h = input_data.dimensions.width, input_data.dimensions.length, input_data.dimensions.height
        vertices = [
            Vertex(x=0, y=0, z=0), Vertex(x=w, y=0, z=0),
            Vertex(x=w, y=l, z=0), Vertex(x=0, y=l, z=0),
            Vertex(x=0, y=0, z=h), Vertex(x=w, y=0, z=h),
            Vertex(x=w, y=l, z=h), Vertex(x=0, y=l, z=h)
        ]
    
    # Generate roof surfaces
    roof_surfaces = generate_roof_surfaces(input_data.dimensions, input_data.roof)
    
    # Calculate areas
    total_roof_area = calculate_roof_area(input_data.dimensions, input_data.roof)
    usable_roof_area = sum(s.usable_area_m2 for s in roof_surfaces)
    footprint = input_data.dimensions.width * input_data.dimensions.length
    
    # Calculate volume
    wall_height = input_data.floors * input_data.floor_height
    roof_height = calculate_roof_height(input_data.dimensions.width, input_data.roof.pitch_angle, input_data.roof.roof_type)
    volume = footprint * wall_height + (footprint * roof_height / 3)  # Approximate
    
    return BuildingGeometry(
        building_id=building_id,
        building_type=input_data.building_type,
        vertices=vertices,
        faces=[],  # Simplified
        roof_surfaces=roof_surfaces,
        total_roof_area_m2=round(total_roof_area, 2),
        usable_roof_area_m2=round(usable_roof_area, 2),
        building_footprint_m2=round(footprint, 2),
        total_volume_m3=round(volume, 2),
        bounding_box={
            "min_x": 0, "max_x": input_data.dimensions.width,
            "min_y": 0, "max_y": input_data.dimensions.length,
            "min_z": 0, "max_z": input_data.dimensions.height + roof_height
        },
        generated_at=datetime.now()
    )


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_geometry(input_data: BuildingInput):
    """Generate building geometry from input parameters."""
    geometry = generate_building_geometry(input_data)
    
    return {
        "geometry": geometry,
        "summary": {
            "building_type": input_data.building_type.value,
            "roof_type": input_data.roof.roof_type.value,
            "total_roof_area_m2": geometry.total_roof_area_m2,
            "usable_for_pv_m2": geometry.usable_roof_area_m2,
            "pv_suitable_surfaces": len([s for s in geometry.roof_surfaces if s.suitable_for_pv])
        }
    }


@router.get("/building-types")
async def get_building_types():
    """Get available building types."""
    return {
        "building_types": [
            {"id": "single_family", "name": "Einfamilienhaus", "typical_floors": 2},
            {"id": "multi_family", "name": "Mehrfamilienhaus", "typical_floors": 4},
            {"id": "townhouse", "name": "Reihenhaus", "typical_floors": 2},
            {"id": "commercial", "name": "Gewerbegebäude", "typical_floors": 1},
            {"id": "industrial", "name": "Industriegebäude", "typical_floors": 1}
        ]
    }


@router.get("/roof-types")
async def get_roof_types():
    """Get available roof types with descriptions."""
    return {
        "roof_types": [
            {"id": "satteldach", "name": "Satteldach", "name_en": "Gable roof", "typical_pitch": 30, "pv_suitability": "excellent"},
            {"id": "pultdach", "name": "Pultdach", "name_en": "Mono-pitch roof", "typical_pitch": 15, "pv_suitability": "excellent"},
            {"id": "flachdach", "name": "Flachdach", "name_en": "Flat roof", "typical_pitch": 0, "pv_suitability": "good"},
            {"id": "walmdach", "name": "Walmdach", "name_en": "Hip roof", "typical_pitch": 25, "pv_suitability": "good"},
            {"id": "krueppelwalmdach", "name": "Krüppelwalmdach", "name_en": "Jerkinhead roof", "typical_pitch": 30, "pv_suitability": "good"},
            {"id": "zeltdach", "name": "Zeltdach", "name_en": "Pyramid roof", "typical_pitch": 25, "pv_suitability": "moderate"},
            {"id": "mansarddach", "name": "Mansarddach", "name_en": "Mansard roof", "typical_pitch": 60, "pv_suitability": "moderate"}
        ]
    }


@router.get("/dormer-types")
async def get_dormer_types():
    """Get available dormer types."""
    return {
        "dormer_types": [
            {"id": "none", "name": "Keine Gaube"},
            {"id": "schleppgaube", "name": "Schleppgaube", "name_en": "Shed dormer"},
            {"id": "spitzgaube", "name": "Spitzgaube", "name_en": "Gable dormer"},
            {"id": "flachdachgaube", "name": "Flachdachgaube", "name_en": "Flat roof dormer"},
            {"id": "rundgaube", "name": "Rundgaube", "name_en": "Eyebrow dormer"}
        ]
    }


@router.get("/presets")
async def get_geometry_presets():
    """Get predefined building geometry presets."""
    return {
        "presets": [
            GeometryPreset(
                preset_id="efh_standard",
                name="Einfamilienhaus Standard",
                description="Typisches Einfamilienhaus mit Satteldach",
                building_type=BuildingType.SINGLE_FAMILY,
                roof_type=RoofType.SATTELDACH,
                typical_dimensions=Dimensions(width=10, length=12, height=6),
                typical_roof_pitch=30
            ),
            GeometryPreset(
                preset_id="efh_modern",
                name="Einfamilienhaus Modern",
                description="Modernes Einfamilienhaus mit Flachdach",
                building_type=BuildingType.SINGLE_FAMILY,
                roof_type=RoofType.FLACHDACH,
                typical_dimensions=Dimensions(width=12, length=14, height=6),
                typical_roof_pitch=0
            ),
            GeometryPreset(
                preset_id="mfh_standard",
                name="Mehrfamilienhaus",
                description="Mehrfamilienhaus mit Walmdach",
                building_type=BuildingType.MULTI_FAMILY,
                roof_type=RoofType.WALMDACH,
                typical_dimensions=Dimensions(width=15, length=20, height=12),
                typical_roof_pitch=25
            ),
            GeometryPreset(
                preset_id="gewerbe_halle",
                name="Gewerbehalle",
                description="Gewerbehalle mit Pultdach",
                building_type=BuildingType.COMMERCIAL,
                roof_type=RoofType.PULTDACH,
                typical_dimensions=Dimensions(width=20, length=30, height=6),
                typical_roof_pitch=10
            )
        ]
    }


@router.post("/from-preset/{preset_id}")
async def generate_from_preset(preset_id: str, modifications: Optional[Dict[str, Any]] = None):
    """Generate geometry from preset with optional modifications."""
    presets = {
        "efh_standard": BuildingInput(
            building_type=BuildingType.SINGLE_FAMILY,
            dimensions=Dimensions(width=10, length=12, height=6),
            roof=RoofParameters(roof_type=RoofType.SATTELDACH, pitch_angle=30)
        ),
        "efh_modern": BuildingInput(
            building_type=BuildingType.SINGLE_FAMILY,
            dimensions=Dimensions(width=12, length=14, height=6),
            roof=RoofParameters(roof_type=RoofType.FLACHDACH, pitch_angle=0)
        ),
        "mfh_standard": BuildingInput(
            building_type=BuildingType.MULTI_FAMILY,
            dimensions=Dimensions(width=15, length=20, height=12),
            roof=RoofParameters(roof_type=RoofType.WALMDACH, pitch_angle=25),
            floors=4
        )
    }
    
    if preset_id not in presets:
        raise HTTPException(status_code=404, detail="Preset nicht gefunden")
    
    input_data = presets[preset_id]
    
    # Apply modifications if provided
    if modifications:
        if "width" in modifications:
            input_data.dimensions.width = modifications["width"]
        if "length" in modifications:
            input_data.dimensions.length = modifications["length"]
        if "pitch_angle" in modifications:
            input_data.roof.pitch_angle = modifications["pitch_angle"]
    
    geometry = generate_building_geometry(input_data)
    
    return {
        "preset_id": preset_id,
        "geometry": geometry,
        "modifications_applied": modifications or {}
    }


@router.post("/calculate-roof-area")
async def calculate_roof_area_endpoint(dimensions: Dimensions, roof: RoofParameters):
    """Calculate roof area without full geometry generation."""
    total_area = calculate_roof_area(dimensions, roof)
    usable_area = total_area * 0.75  # Approximate 75% usable
    
    return {
        "total_roof_area_m2": round(total_area, 2),
        "usable_area_m2": round(usable_area, 2),
        "roof_type": roof.roof_type.value,
        "pitch_angle": roof.pitch_angle
    }


@router.post("/estimate-pv-capacity")
async def estimate_pv_capacity(dimensions: Dimensions, roof: RoofParameters, module_power_wp: int = 400):
    """Estimate PV capacity for building."""
    total_area = calculate_roof_area(dimensions, roof)
    usable_area = total_area * 0.75
    
    # Assume ~2m² per module
    module_area = 2.0
    max_modules = int(usable_area / module_area)
    
    # Consider orientation factor
    orientation_factor = 1.0 if roof.orientation == RoofOrientation.SOUTH else 0.85
    
    return {
        "usable_roof_area_m2": round(usable_area, 2),
        "max_modules": max_modules,
        "estimated_capacity_kwp": round(max_modules * module_power_wp / 1000, 2),
        "estimated_annual_yield_kwh": round(max_modules * module_power_wp * 0.95 * orientation_factor, 0),
        "orientation_factor": orientation_factor
    }


@router.get("/export/{building_id}")
async def export_geometry(building_id: str, format: str = "obj"):
    """Export building geometry in various formats."""
    # Mock export - in production would generate actual 3D file
    return {
        "building_id": building_id,
        "format": format,
        "download_url": f"/api/v1/3d/building/download/{building_id}.{format}",
        "supported_formats": ["obj", "stl", "gltf", "fbx"]
    }


@router.get("/health/check")
async def health_check():
    """Health check for building geometry service."""
    return {
        "status": "healthy",
        "service": "building-geometry",
        "supported_roof_types": len(RoofType),
        "supported_building_types": len(BuildingType),
        "timestamp": datetime.now().isoformat()
    }
