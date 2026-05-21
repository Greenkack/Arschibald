"""
Interactive 3D Editing API

Provides REST API for interactive 3D editing:
- Real-time parameter changes
- Update 3D model on input change
- Dimension adjustment controls
- Color customization
- Refresh button for complex changes

Requirements: funktionen.txt - "Interaktive Bearbeitung"
Task: 272. Interactive 3D Editing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/3d/interactive", tags=["Interactive 3D Editing"])


# ==================== Enums ====================

class ParameterType(str, Enum):
    DIMENSION = "dimension"
    ANGLE = "angle"
    COLOR = "color"
    MATERIAL = "material"
    VISIBILITY = "visibility"


class MaterialType(str, Enum):
    ROOF_TILE = "roof_tile"
    METAL = "metal"
    GLASS = "glass"
    CONCRETE = "concrete"
    WOOD = "wood"
    SOLAR_PANEL = "solar_panel"


# ==================== Pydantic Models ====================

class ColorRGB(BaseModel):
    """RGB color"""
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    a: float = Field(default=1.0, ge=0, le=1)


class ParameterChange(BaseModel):
    """Single parameter change"""
    parameter_id: str
    parameter_type: ParameterType
    old_value: Any
    new_value: Any
    timestamp: datetime = datetime.now()


class DimensionUpdate(BaseModel):
    """Dimension update request"""
    width: Optional[float] = None
    length: Optional[float] = None
    height: Optional[float] = None
    roof_pitch: Optional[float] = None
    roof_overhang: Optional[float] = None


class ColorUpdate(BaseModel):
    """Color update request"""
    element_id: str
    color: ColorRGB
    apply_to_similar: bool = False


class MaterialUpdate(BaseModel):
    """Material update request"""
    element_id: str
    material: MaterialType
    texture_scale: float = 1.0


class VisibilityUpdate(BaseModel):
    """Visibility update request"""
    element_id: str
    visible: bool
    opacity: float = Field(default=1.0, ge=0, le=1)


class SceneState(BaseModel):
    """Current 3D scene state"""
    scene_id: str
    building_dimensions: Dict[str, float]
    roof_parameters: Dict[str, float]
    colors: Dict[str, ColorRGB]
    materials: Dict[str, MaterialType]
    visibility: Dict[str, bool]
    module_count: int
    last_updated: datetime


class UpdateResult(BaseModel):
    """Result of parameter update"""
    success: bool
    parameter_id: str
    old_value: Any
    new_value: Any
    requires_rebuild: bool
    affected_elements: List[str]


class EditSession(BaseModel):
    """Interactive editing session"""
    session_id: str
    scene_id: str
    changes: List[ParameterChange] = []
    can_undo: bool = False
    can_redo: bool = False
    created_at: datetime
    last_activity: datetime


# ==================== Mock Data Store ====================

_sessions_store: Dict[str, EditSession] = {}
_scene_states: Dict[str, SceneState] = {}
_undo_stack: Dict[str, List[ParameterChange]] = {}
_redo_stack: Dict[str, List[ParameterChange]] = {}


def generate_session_id() -> str:
    return f"edit_{uuid.uuid4().hex[:8]}"


def generate_scene_id() -> str:
    return f"scene_{uuid.uuid4().hex[:8]}"


def get_default_scene_state(scene_id: str) -> SceneState:
    """Create default scene state"""
    return SceneState(
        scene_id=scene_id,
        building_dimensions={"width": 10.0, "length": 12.0, "height": 6.0},
        roof_parameters={"pitch": 30.0, "overhang": 0.5, "ridge_height": 2.89},
        colors={
            "walls": ColorRGB(r=245, g=245, b=240),
            "roof": ColorRGB(r=139, g=69, b=19),
            "modules": ColorRGB(r=30, g=30, b=50),
            "frame": ColorRGB(r=192, g=192, b=192)
        },
        materials={
            "walls": MaterialType.CONCRETE,
            "roof": MaterialType.ROOF_TILE,
            "modules": MaterialType.SOLAR_PANEL
        },
        visibility={
            "building": True,
            "roof": True,
            "modules": True,
            "grid": False,
            "dimensions": True
        },
        module_count=20,
        last_updated=datetime.now()
    )


# ==================== API Endpoints ====================

@router.post("/session/start")
async def start_edit_session(scene_id: Optional[str] = None):
    """Start a new interactive editing session."""
    session_id = generate_session_id()
    if not scene_id:
        scene_id = generate_scene_id()
        _scene_states[scene_id] = get_default_scene_state(scene_id)
    
    session = EditSession(
        session_id=session_id,
        scene_id=scene_id,
        created_at=datetime.now(),
        last_activity=datetime.now()
    )
    
    _sessions_store[session_id] = session
    _undo_stack[session_id] = []
    _redo_stack[session_id] = []
    
    return {
        "session": session,
        "scene_state": _scene_states.get(scene_id)
    }


@router.post("/session/{session_id}/end")
async def end_edit_session(session_id: str, save_changes: bool = True):
    """End editing session."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    
    if not save_changes:
        # Revert all changes
        pass
    
    del _sessions_store[session_id]
    del _undo_stack[session_id]
    del _redo_stack[session_id]
    
    return {
        "session_id": session_id,
        "ended": True,
        "changes_saved": save_changes,
        "total_changes": len(session.changes)
    }


@router.put("/dimensions")
async def update_dimensions(session_id: str, update: DimensionUpdate):
    """Update building dimensions in real-time."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    scene = _scene_states.get(session.scene_id)
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    changes = []
    affected = []
    
    if update.width is not None:
        old_val = scene.building_dimensions["width"]
        scene.building_dimensions["width"] = update.width
        changes.append(ParameterChange(
            parameter_id="width",
            parameter_type=ParameterType.DIMENSION,
            old_value=old_val,
            new_value=update.width
        ))
        affected.extend(["building", "roof", "modules"])
    
    if update.length is not None:
        old_val = scene.building_dimensions["length"]
        scene.building_dimensions["length"] = update.length
        changes.append(ParameterChange(
            parameter_id="length",
            parameter_type=ParameterType.DIMENSION,
            old_value=old_val,
            new_value=update.length
        ))
        affected.extend(["building", "roof", "modules"])
    
    if update.height is not None:
        old_val = scene.building_dimensions["height"]
        scene.building_dimensions["height"] = update.height
        changes.append(ParameterChange(
            parameter_id="height",
            parameter_type=ParameterType.DIMENSION,
            old_value=old_val,
            new_value=update.height
        ))
        affected.append("building")
    
    if update.roof_pitch is not None:
        old_val = scene.roof_parameters["pitch"]
        scene.roof_parameters["pitch"] = update.roof_pitch
        # Recalculate ridge height
        scene.roof_parameters["ridge_height"] = (scene.building_dimensions["width"] / 2) * \
            __import__('math').tan(__import__('math').radians(update.roof_pitch))
        changes.append(ParameterChange(
            parameter_id="roof_pitch",
            parameter_type=ParameterType.ANGLE,
            old_value=old_val,
            new_value=update.roof_pitch
        ))
        affected.extend(["roof", "modules"])
    
    scene.last_updated = datetime.now()
    session.changes.extend(changes)
    session.last_activity = datetime.now()
    _undo_stack[session_id].extend(changes)
    session.can_undo = True
    
    return {
        "updated": True,
        "changes": len(changes),
        "affected_elements": list(set(affected)),
        "requires_rebuild": "modules" in affected,
        "scene_state": scene
    }


@router.put("/color")
async def update_color(session_id: str, update: ColorUpdate):
    """Update element color."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    scene = _scene_states.get(session.scene_id)
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    old_color = scene.colors.get(update.element_id)
    scene.colors[update.element_id] = update.color
    
    change = ParameterChange(
        parameter_id=f"color_{update.element_id}",
        parameter_type=ParameterType.COLOR,
        old_value=old_color.dict() if old_color else None,
        new_value=update.color.dict()
    )
    
    session.changes.append(change)
    _undo_stack[session_id].append(change)
    session.can_undo = True
    scene.last_updated = datetime.now()
    
    return {
        "updated": True,
        "element_id": update.element_id,
        "new_color": update.color,
        "requires_rebuild": False
    }


@router.put("/material")
async def update_material(session_id: str, update: MaterialUpdate):
    """Update element material."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    scene = _scene_states.get(session.scene_id)
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    old_material = scene.materials.get(update.element_id)
    scene.materials[update.element_id] = update.material
    scene.last_updated = datetime.now()
    
    return {
        "updated": True,
        "element_id": update.element_id,
        "old_material": old_material,
        "new_material": update.material,
        "requires_rebuild": False
    }


@router.put("/visibility")
async def update_visibility(session_id: str, update: VisibilityUpdate):
    """Update element visibility."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    scene = _scene_states.get(session.scene_id)
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    scene.visibility[update.element_id] = update.visible
    scene.last_updated = datetime.now()
    
    return {
        "updated": True,
        "element_id": update.element_id,
        "visible": update.visible,
        "opacity": update.opacity
    }


@router.post("/undo")
async def undo_change(session_id: str):
    """Undo last change."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    if not _undo_stack.get(session_id):
        return {"undone": False, "message": "Nichts zum Rückgängigmachen"}
    
    change = _undo_stack[session_id].pop()
    _redo_stack[session_id].append(change)
    
    session = _sessions_store[session_id]
    session.can_undo = len(_undo_stack[session_id]) > 0
    session.can_redo = True
    
    return {
        "undone": True,
        "change": change,
        "can_undo": session.can_undo,
        "can_redo": session.can_redo
    }


@router.post("/redo")
async def redo_change(session_id: str):
    """Redo last undone change."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    if not _redo_stack.get(session_id):
        return {"redone": False, "message": "Nichts zum Wiederholen"}
    
    change = _redo_stack[session_id].pop()
    _undo_stack[session_id].append(change)
    
    session = _sessions_store[session_id]
    session.can_undo = True
    session.can_redo = len(_redo_stack[session_id]) > 0
    
    return {
        "redone": True,
        "change": change,
        "can_undo": session.can_undo,
        "can_redo": session.can_redo
    }


@router.post("/refresh")
async def refresh_scene(session_id: str):
    """Force refresh/rebuild of 3D scene."""
    if session_id not in _sessions_store:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session = _sessions_store[session_id]
    scene = _scene_states.get(session.scene_id)
    
    if scene:
        scene.last_updated = datetime.now()
    
    return {
        "refreshed": True,
        "scene_id": session.scene_id,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/scene/{scene_id}")
async def get_scene_state(scene_id: str):
    """Get current scene state."""
    if scene_id not in _scene_states:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    return {"scene": _scene_states[scene_id]}


@router.get("/materials")
async def get_available_materials():
    """Get available materials."""
    return {
        "materials": [
            {"id": "roof_tile", "name": "Dachziegel", "category": "roof"},
            {"id": "metal", "name": "Metall", "category": "roof"},
            {"id": "glass", "name": "Glas", "category": "window"},
            {"id": "concrete", "name": "Beton", "category": "wall"},
            {"id": "wood", "name": "Holz", "category": "wall"},
            {"id": "solar_panel", "name": "Solarmodul", "category": "pv"}
        ]
    }


@router.get("/presets/colors")
async def get_color_presets():
    """Get color presets."""
    return {
        "presets": [
            {"name": "Standard", "walls": "#F5F5F0", "roof": "#8B4513", "modules": "#1E1E32"},
            {"name": "Modern", "walls": "#FFFFFF", "roof": "#2F4F4F", "modules": "#000033"},
            {"name": "Mediterran", "walls": "#FFF8DC", "roof": "#CD853F", "modules": "#1E1E32"},
            {"name": "Skandinavisch", "walls": "#F0F0F0", "roof": "#696969", "modules": "#1E1E32"}
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for interactive 3D service."""
    return {
        "status": "healthy",
        "service": "interactive-3d",
        "active_sessions": len(_sessions_store),
        "timestamp": datetime.now().isoformat()
    }
