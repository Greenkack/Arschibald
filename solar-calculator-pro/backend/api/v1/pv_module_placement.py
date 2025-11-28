"""
PV Module Placement on Roof API

Provides REST API for PV module placement:
- Automatic module placement algorithm
- Manual module placement mode
- Drag-and-drop module positioning
- Module removal functionality
- Optimal fill algorithm for roof area
- East-West mounting on flat roofs

Requirements: funktionen.txt - "PV-Modul-Platzierung"
Task: 271. PV Module Placement on Roof
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import math
import uuid

router = APIRouter(prefix="/3d/modules", tags=["PV Module Placement"])


# ==================== Enums ====================

class PlacementMode(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    OPTIMAL_FILL = "optimal_fill"
    EAST_WEST = "east_west"


class ModuleOrientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class MountingType(str, Enum):
    ROOF_PARALLEL = "roof_parallel"
    TILTED = "tilted"
    EAST_WEST_FLAT = "east_west_flat"
    FACADE = "facade"


# ==================== Pydantic Models ====================

class ModuleDimensions(BaseModel):
    """Module physical dimensions"""
    width_mm: int = Field(default=1134, ge=800, le=1500)
    height_mm: int = Field(default=2278, ge=1500, le=2500)
    depth_mm: int = Field(default=35, ge=20, le=60)


class ModuleSpecs(BaseModel):
    """Module specifications"""
    manufacturer: str
    model: str
    power_wp: int = Field(ge=200, le=800)
    dimensions: ModuleDimensions = ModuleDimensions()
    efficiency_percent: float = Field(default=21.0, ge=10, le=30)
    weight_kg: float = Field(default=22.0, ge=10, le=40)


class Position2D(BaseModel):
    """2D position on roof surface"""
    x: float
    y: float


class Position3D(BaseModel):
    """3D position"""
    x: float
    y: float
    z: float


class PlacedModule(BaseModel):
    """Placed module on roof"""
    module_id: str
    position: Position2D
    position_3d: Optional[Position3D] = None
    orientation: ModuleOrientation = ModuleOrientation.PORTRAIT
    rotation_deg: float = 0
    row: int
    column: int
    surface_id: str
    is_valid: bool = True
    collision: bool = False


class RoofSurfaceInput(BaseModel):
    """Roof surface for module placement"""
    surface_id: str
    width_m: float
    height_m: float
    pitch_angle: float = 30
    orientation_deg: float = 180  # 180 = South
    usable_area_m2: Optional[float] = None
    exclusion_zones: List[Dict[str, float]] = []


class PlacementConfig(BaseModel):
    """Module placement configuration"""
    mode: PlacementMode = PlacementMode.AUTOMATIC
    module_specs: ModuleSpecs
    orientation: ModuleOrientation = ModuleOrientation.PORTRAIT
    row_spacing_mm: int = Field(default=20, ge=0, le=200)
    column_spacing_mm: int = Field(default=20, ge=0, le=200)
    edge_margin_mm: int = Field(default=300, ge=0, le=1000)
    ridge_margin_mm: int = Field(default=500, ge=0, le=1500)
    eave_margin_mm: int = Field(default=300, ge=0, le=1000)
    max_modules: Optional[int] = None
    east_west_tilt_deg: float = Field(default=10, ge=5, le=20)


class PlacementResult(BaseModel):
    """Result of module placement"""
    placement_id: str
    surface_id: str
    modules: List[PlacedModule]
    total_modules: int
    total_power_kwp: float
    coverage_percent: float
    rows: int
    columns: int
    placement_mode: PlacementMode
    warnings: List[str] = []
    created_at: datetime


class ManualPlacementRequest(BaseModel):
    """Request for manual module placement"""
    surface_id: str
    position: Position2D
    orientation: ModuleOrientation = ModuleOrientation.PORTRAIT
    module_specs: ModuleSpecs


class ModuleMoveRequest(BaseModel):
    """Request to move a module"""
    module_id: str
    new_position: Position2D
    new_orientation: Optional[ModuleOrientation] = None


# ==================== Helper Functions ====================

def generate_placement_id() -> str:
    return f"plc_{uuid.uuid4().hex[:8]}"


def generate_module_id() -> str:
    return f"mod_{uuid.uuid4().hex[:6]}"


def calculate_module_area(specs: ModuleSpecs, orientation: ModuleOrientation) -> tuple:
    """Calculate module footprint based on orientation"""
    if orientation == ModuleOrientation.PORTRAIT:
        return specs.dimensions.width_mm / 1000, specs.dimensions.height_mm / 1000
    else:
        return specs.dimensions.height_mm / 1000, specs.dimensions.width_mm / 1000


def check_collision(module: PlacedModule, existing: List[PlacedModule], specs: ModuleSpecs) -> bool:
    """Check if module collides with existing modules"""
    mod_w, mod_h = calculate_module_area(specs, module.orientation)
    
    for existing_mod in existing:
        ex_w, ex_h = calculate_module_area(specs, existing_mod.orientation)
        
        # Simple AABB collision check
        if (module.position.x < existing_mod.position.x + ex_w and
            module.position.x + mod_w > existing_mod.position.x and
            module.position.y < existing_mod.position.y + ex_h and
            module.position.y + mod_h > existing_mod.position.y):
            return True
    
    return False


def automatic_placement(surface: RoofSurfaceInput, config: PlacementConfig) -> List[PlacedModule]:
    """Automatic module placement algorithm"""
    modules = []
    mod_w, mod_h = calculate_module_area(config.module_specs, config.orientation)
    
    # Calculate spacing in meters
    row_spacing = config.row_spacing_mm / 1000
    col_spacing = config.column_spacing_mm / 1000
    edge_margin = config.edge_margin_mm / 1000
    ridge_margin = config.ridge_margin_mm / 1000
    eave_margin = config.eave_margin_mm / 1000
    
    # Available area
    available_width = surface.width_m - 2 * edge_margin
    available_height = surface.height_m - ridge_margin - eave_margin
    
    # Calculate grid
    cols = int(available_width / (mod_w + col_spacing))
    rows = int(available_height / (mod_h + row_spacing))
    
    # Center the array
    total_width = cols * mod_w + (cols - 1) * col_spacing
    total_height = rows * mod_h + (rows - 1) * row_spacing
    start_x = edge_margin + (available_width - total_width) / 2
    start_y = eave_margin + (available_height - total_height) / 2
    
    for row in range(rows):
        for col in range(cols):
            if config.max_modules and len(modules) >= config.max_modules:
                break
            
            x = start_x + col * (mod_w + col_spacing)
            y = start_y + row * (mod_h + row_spacing)
            
            # Check exclusion zones
            in_exclusion = False
            for zone in surface.exclusion_zones:
                if (zone.get("x", 0) <= x <= zone.get("x", 0) + zone.get("width", 0) and
                    zone.get("y", 0) <= y <= zone.get("y", 0) + zone.get("height", 0)):
                    in_exclusion = True
                    break
            
            if not in_exclusion:
                modules.append(PlacedModule(
                    module_id=generate_module_id(),
                    position=Position2D(x=x, y=y),
                    orientation=config.orientation,
                    row=row,
                    column=col,
                    surface_id=surface.surface_id
                ))
    
    return modules


def east_west_placement(surface: RoofSurfaceInput, config: PlacementConfig) -> List[PlacedModule]:
    """East-West mounting placement for flat roofs"""
    modules = []
    mod_w, mod_h = calculate_module_area(config.module_specs, ModuleOrientation.LANDSCAPE)
    
    # E-W mounting uses landscape orientation in pairs
    pair_width = mod_w * 2 + 0.1  # 10cm gap between E-W pair
    row_spacing = 0.8  # Larger spacing for shadow avoidance
    
    edge_margin = config.edge_margin_mm / 1000
    available_width = surface.width_m - 2 * edge_margin
    available_height = surface.height_m - 2 * edge_margin
    
    pairs_per_row = int(available_width / (pair_width + 0.3))
    rows = int(available_height / (mod_h + row_spacing))
    
    for row in range(rows):
        for pair in range(pairs_per_row):
            if config.max_modules and len(modules) >= config.max_modules:
                break
            
            base_x = edge_margin + pair * (pair_width + 0.3)
            y = edge_margin + row * (mod_h + row_spacing)
            
            # East-facing module
            modules.append(PlacedModule(
                module_id=generate_module_id(),
                position=Position2D(x=base_x, y=y),
                orientation=ModuleOrientation.LANDSCAPE,
                rotation_deg=-config.east_west_tilt_deg,
                row=row,
                column=pair * 2,
                surface_id=surface.surface_id
            ))
            
            # West-facing module
            modules.append(PlacedModule(
                module_id=generate_module_id(),
                position=Position2D(x=base_x + mod_w + 0.1, y=y),
                orientation=ModuleOrientation.LANDSCAPE,
                rotation_deg=config.east_west_tilt_deg,
                row=row,
                column=pair * 2 + 1,
                surface_id=surface.surface_id
            ))
    
    return modules


# ==================== Mock Data Store ====================

_placements_store: Dict[str, PlacementResult] = {}


# ==================== API Endpoints ====================

@router.post("/place/automatic")
async def automatic_module_placement(surface: RoofSurfaceInput, config: PlacementConfig):
    """Automatically place modules on roof surface."""
    if config.mode == PlacementMode.EAST_WEST:
        modules = east_west_placement(surface, config)
    else:
        modules = automatic_placement(surface, config)
    
    total_power = len(modules) * config.module_specs.power_wp / 1000
    mod_area = (config.module_specs.dimensions.width_mm * config.module_specs.dimensions.height_mm) / 1_000_000
    coverage = (len(modules) * mod_area) / (surface.width_m * surface.height_m) * 100
    
    result = PlacementResult(
        placement_id=generate_placement_id(),
        surface_id=surface.surface_id,
        modules=modules,
        total_modules=len(modules),
        total_power_kwp=round(total_power, 2),
        coverage_percent=round(coverage, 1),
        rows=max((m.row for m in modules), default=0) + 1,
        columns=max((m.column for m in modules), default=0) + 1,
        placement_mode=config.mode,
        created_at=datetime.now()
    )
    
    _placements_store[result.placement_id] = result
    
    return {"result": result}


@router.post("/place/manual")
async def manual_module_placement(request: ManualPlacementRequest):
    """Manually place a single module."""
    module = PlacedModule(
        module_id=generate_module_id(),
        position=request.position,
        orientation=request.orientation,
        row=0,
        column=0,
        surface_id=request.surface_id
    )
    
    return {
        "module": module,
        "power_wp": request.module_specs.power_wp,
        "message": "Modul manuell platziert"
    }


@router.post("/place/{placement_id}/add")
async def add_module_to_placement(placement_id: str, request: ManualPlacementRequest):
    """Add a module to existing placement."""
    if placement_id not in _placements_store:
        raise HTTPException(status_code=404, detail="Platzierung nicht gefunden")
    
    placement = _placements_store[placement_id]
    
    new_module = PlacedModule(
        module_id=generate_module_id(),
        position=request.position,
        orientation=request.orientation,
        row=placement.rows,
        column=0,
        surface_id=request.surface_id
    )
    
    # Check collision
    collision = check_collision(new_module, placement.modules, request.module_specs)
    new_module.collision = collision
    new_module.is_valid = not collision
    
    if not collision:
        placement.modules.append(new_module)
        placement.total_modules = len(placement.modules)
        placement.total_power_kwp = round(len(placement.modules) * request.module_specs.power_wp / 1000, 2)
    
    return {
        "module": new_module,
        "collision": collision,
        "placement": placement
    }


@router.put("/place/{placement_id}/move")
async def move_module(placement_id: str, request: ModuleMoveRequest):
    """Move a module to new position."""
    if placement_id not in _placements_store:
        raise HTTPException(status_code=404, detail="Platzierung nicht gefunden")
    
    placement = _placements_store[placement_id]
    
    for module in placement.modules:
        if module.module_id == request.module_id:
            module.position = request.new_position
            if request.new_orientation:
                module.orientation = request.new_orientation
            return {"module": module, "moved": True}
    
    raise HTTPException(status_code=404, detail="Modul nicht gefunden")


@router.delete("/place/{placement_id}/module/{module_id}")
async def remove_module(placement_id: str, module_id: str):
    """Remove a module from placement."""
    if placement_id not in _placements_store:
        raise HTTPException(status_code=404, detail="Platzierung nicht gefunden")
    
    placement = _placements_store[placement_id]
    
    for i, module in enumerate(placement.modules):
        if module.module_id == module_id:
            removed = placement.modules.pop(i)
            placement.total_modules = len(placement.modules)
            return {"removed": removed, "remaining_modules": placement.total_modules}
    
    raise HTTPException(status_code=404, detail="Modul nicht gefunden")


@router.get("/place/{placement_id}")
async def get_placement(placement_id: str):
    """Get placement details."""
    if placement_id not in _placements_store:
        raise HTTPException(status_code=404, detail="Platzierung nicht gefunden")
    
    return {"placement": _placements_store[placement_id]}


@router.post("/optimize")
async def optimize_placement(surface: RoofSurfaceInput, config: PlacementConfig):
    """Find optimal module placement for maximum power."""
    # Try both orientations
    config_portrait = config.copy()
    config_portrait.orientation = ModuleOrientation.PORTRAIT
    modules_portrait = automatic_placement(surface, config_portrait)
    
    config_landscape = config.copy()
    config_landscape.orientation = ModuleOrientation.LANDSCAPE
    modules_landscape = automatic_placement(surface, config_landscape)
    
    # Compare results
    power_portrait = len(modules_portrait) * config.module_specs.power_wp
    power_landscape = len(modules_landscape) * config.module_specs.power_wp
    
    best_orientation = ModuleOrientation.PORTRAIT if power_portrait >= power_landscape else ModuleOrientation.LANDSCAPE
    best_modules = modules_portrait if power_portrait >= power_landscape else modules_landscape
    
    return {
        "optimal_orientation": best_orientation.value,
        "portrait_modules": len(modules_portrait),
        "portrait_power_kwp": round(power_portrait / 1000, 2),
        "landscape_modules": len(modules_landscape),
        "landscape_power_kwp": round(power_landscape / 1000, 2),
        "recommended_modules": len(best_modules),
        "recommended_power_kwp": round(max(power_portrait, power_landscape) / 1000, 2)
    }


@router.get("/placement-modes")
async def get_placement_modes():
    """Get available placement modes."""
    return {
        "modes": [
            {"id": "automatic", "name": "Automatisch", "description": "Optimale Rasterplatzierung"},
            {"id": "manual", "name": "Manuell", "description": "Einzelne Module per Drag & Drop"},
            {"id": "optimal_fill", "name": "Maximale Füllung", "description": "Maximale Modulanzahl"},
            {"id": "east_west", "name": "Ost-West", "description": "Für Flachdächer"}
        ]
    }


@router.get("/orientations")
async def get_module_orientations():
    """Get available module orientations."""
    return {
        "orientations": [
            {"id": "portrait", "name": "Hochformat", "description": "Modul vertikal"},
            {"id": "landscape", "name": "Querformat", "description": "Modul horizontal"}
        ]
    }


@router.post("/validate")
async def validate_placement(placement_id: str):
    """Validate module placement for collisions and constraints."""
    if placement_id not in _placements_store:
        raise HTTPException(status_code=404, detail="Platzierung nicht gefunden")
    
    placement = _placements_store[placement_id]
    issues = []
    
    # Check for overlapping modules
    for i, mod1 in enumerate(placement.modules):
        for mod2 in placement.modules[i+1:]:
            if abs(mod1.position.x - mod2.position.x) < 1.2 and abs(mod1.position.y - mod2.position.y) < 2.3:
                issues.append(f"Module {mod1.module_id} und {mod2.module_id} überlappen möglicherweise")
    
    return {
        "placement_id": placement_id,
        "valid": len(issues) == 0,
        "issues": issues,
        "module_count": placement.total_modules
    }


@router.get("/health/check")
async def health_check():
    """Health check for module placement service."""
    return {
        "status": "healthy",
        "service": "pv-module-placement",
        "placements_count": len(_placements_store),
        "timestamp": datetime.now().isoformat()
    }
