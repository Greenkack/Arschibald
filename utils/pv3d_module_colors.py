"""
PV Module Colors & Materials System

This module provides a comprehensive color and material system for PV modules,
allowing realistic visualization with different colors and surface finishes.

Key Features:
    - 7 predefined module materials (5 colors + 2 special finishes)
    - Material properties (color, finish, opacity, reflectivity)
    - Easy application to module meshes
    - Session state integration

Requirements: 6.1, 6.2, 6.3, 6.4
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class SurfaceFinish(Enum):
    """Surface finish types for PV modules."""
    MATTE = "matt"
    GLOSSY = "glänzend"
    GLASS_GLASS = "glas-glas"


@dataclass
class ModuleMaterial:
    """
    Material definition for PV modules.
    
    Attributes:
        name: Display name of the material
        color: Hex color code (e.g., "#1a1a1a")
        finish: Surface finish type
        opacity: Opacity value (0.0 = transparent, 1.0 = opaque)
        reflectivity: Reflectivity coefficient (0.0 = no reflection, 1.0 = mirror)
        description: Human-readable description
    
    Requirements:
        - 6.1: Support for different module colors
        - 6.2: Support for different surface materials
    """
    name: str
    color: str
    finish: SurfaceFinish
    opacity: float = 1.0
    reflectivity: float = 0.1
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert material to dictionary for serialization."""
        return {
            "name": self.name,
            "color": self.color,
            "finish": self.finish.value,
            "opacity": self.opacity,
            "reflectivity": self.reflectivity,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleMaterial':
        """Create material from dictionary."""
        return cls(
            name=data["name"],
            color=data["color"],
            finish=SurfaceFinish(data["finish"]),
            opacity=data.get("opacity", 1.0),
            reflectivity=data.get("reflectivity", 0.1),
            description=data.get("description", "")
        )


# ============================================================================
# PREDEFINED MATERIALS
# ============================================================================

# Requirement 6.1: 5 Standard-Farben
MATERIAL_BLACK = ModuleMaterial(
    name="Schwarz (Standard)",
    color="#1a1a1a",
    finish=SurfaceFinish.MATTE,
    opacity=1.0,
    reflectivity=0.1,
    description="Standard schwarze PV-Module, matt"
)

MATERIAL_DARK_BLUE = ModuleMaterial(
    name="Dunkelblau",
    color="#1a1a2e",
    finish=SurfaceFinish.MATTE,
    opacity=1.0,
    reflectivity=0.1,
    description="Dunkelblaue PV-Module, klassisches Design"
)

MATERIAL_DARK_RED = ModuleMaterial(
    name="Dunkelrot",
    color="#8b0000",
    finish=SurfaceFinish.MATTE,
    opacity=1.0,
    reflectivity=0.1,
    description="Dunkelrote PV-Module, auffälliges Design"
)

MATERIAL_ANTHRACITE = ModuleMaterial(
    name="Anthrazit",
    color="#2f4f4f",
    finish=SurfaceFinish.MATTE,
    opacity=1.0,
    reflectivity=0.1,
    description="Anthrazit PV-Module, dezentes Design"
)

MATERIAL_SILVER = ModuleMaterial(
    name="Silber",
    color="#c0c0c0",
    finish=SurfaceFinish.MATTE,
    opacity=1.0,
    reflectivity=0.2,
    description="Silberne PV-Module, helle Optik"
)

# Requirement 6.2: Spezial-Oberflächen
MATERIAL_BLACK_GLOSSY = ModuleMaterial(
    name="Schwarz Glänzend",
    color="#1a1a1a",
    finish=SurfaceFinish.GLOSSY,
    opacity=1.0,
    reflectivity=0.5,
    description="Schwarze PV-Module mit glänzender Oberfläche"
)

MATERIAL_GLASS_GLASS = ModuleMaterial(
    name="Glas-Glas",
    color="#e0e0e0",
    finish=SurfaceFinish.GLASS_GLASS,
    opacity=0.7,
    reflectivity=0.3,
    description="Transparente Glas-Glas Module (bifazial)"
)


# ============================================================================
# MATERIAL COLLECTIONS
# ============================================================================

# All predefined materials
ALL_MATERIALS = [
    MATERIAL_BLACK,
    MATERIAL_DARK_BLUE,
    MATERIAL_DARK_RED,
    MATERIAL_ANTHRACITE,
    MATERIAL_SILVER,
    MATERIAL_BLACK_GLOSSY,
    MATERIAL_GLASS_GLASS
]

# Materials grouped by finish
MATERIALS_BY_FINISH = {
    SurfaceFinish.MATTE: [
        MATERIAL_BLACK,
        MATERIAL_DARK_BLUE,
        MATERIAL_DARK_RED,
        MATERIAL_ANTHRACITE,
        MATERIAL_SILVER
    ],
    SurfaceFinish.GLOSSY: [
        MATERIAL_BLACK_GLOSSY
    ],
    SurfaceFinish.GLASS_GLASS: [
        MATERIAL_GLASS_GLASS
    ]
}

# Default material
DEFAULT_MATERIAL = MATERIAL_BLACK


# ============================================================================
# MATERIAL APPLICATION FUNCTIONS
# ============================================================================

def apply_material_to_module(
    module_mesh: Dict[str, Any],
    material: ModuleMaterial
) -> Dict[str, Any]:
    """
    Apply material properties to a module mesh.
    
    This function updates the color, opacity, and other visual properties
    of a Plotly mesh based on the selected material.
    
    Args:
        module_mesh: Plotly mesh dictionary (go.Mesh3d)
        material: Material to apply
    
    Returns:
        Updated mesh dictionary with material properties applied
    
    Requirements:
        - 6.3: Apply material to all modules
        - 6.4: Apply material to individual modules
    
    Example:
        >>> mesh = go.Mesh3d(x=[...], y=[...], z=[...])
        >>> mesh_dict = mesh.to_plotly_json()
        >>> updated_mesh = apply_material_to_module(mesh_dict, MATERIAL_DARK_BLUE)
    """
    # Update color
    module_mesh["color"] = material.color
    
    # Update opacity
    module_mesh["opacity"] = material.opacity
    
    # Update lighting based on finish
    if material.finish == SurfaceFinish.GLOSSY:
        # Glossy finish: high specular reflection
        module_mesh["lighting"] = {
            "ambient": 0.3,
            "diffuse": 0.5,
            "specular": 0.8,
            "roughness": 0.2,
            "fresnel": 0.5
        }
    elif material.finish == SurfaceFinish.GLASS_GLASS:
        # Glass-glass: transparent with reflections
        module_mesh["lighting"] = {
            "ambient": 0.5,
            "diffuse": 0.4,
            "specular": 0.6,
            "roughness": 0.1,
            "fresnel": 0.7
        }
    else:  # MATTE
        # Matte finish: low specular reflection
        module_mesh["lighting"] = {
            "ambient": 0.4,
            "diffuse": 0.6,
            "specular": 0.2,
            "roughness": 0.8,
            "fresnel": 0.1
        }
    
    # Store material info in mesh for reference
    module_mesh["customdata"] = {
        "material_name": material.name,
        "material_color": material.color,
        "material_finish": material.finish.value
    }
    
    return module_mesh


def get_material_by_name(name: str) -> Optional[ModuleMaterial]:
    """
    Get material by name.
    
    Args:
        name: Material name
    
    Returns:
        Material if found, None otherwise
    
    Example:
        >>> material = get_material_by_name("Dunkelblau")
        >>> print(material.color)
        "#1a1a2e"
    """
    for material in ALL_MATERIALS:
        if material.name == name:
            return material
    return None


def get_materials_by_finish(finish: SurfaceFinish) -> List[ModuleMaterial]:
    """
    Get all materials with a specific finish.
    
    Args:
        finish: Surface finish type
    
    Returns:
        List of materials with the specified finish
    
    Example:
        >>> matte_materials = get_materials_by_finish(SurfaceFinish.MATTE)
        >>> print(len(matte_materials))
        5
    """
    return MATERIALS_BY_FINISH.get(finish, [])


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color code (e.g., "#1a1a1a")
    
    Returns:
        RGB tuple (r, g, b) with values 0-255
    
    Example:
        >>> rgb = hex_to_rgb("#1a1a1a")
        >>> print(rgb)
        (26, 26, 26)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB tuple to hex color.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        Hex color code (e.g., "#1a1a1a")
    
    Example:
        >>> hex_color = rgb_to_hex(26, 26, 26)
        >>> print(hex_color)
        "#1a1a1a"
    """
    return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================================
# SESSION STATE HELPERS
# ============================================================================

def get_selected_material_from_session(session_state: Dict[str, Any]) -> ModuleMaterial:
    """
    Get currently selected material from session state.
    
    Args:
        session_state: Streamlit session state
    
    Returns:
        Selected material or default material
    
    Requirements:
        - 6.3: Store material selection in session state
    """
    material_name = session_state.get("selected_material", DEFAULT_MATERIAL.name)
    material = get_material_by_name(material_name)
    return material if material else DEFAULT_MATERIAL


def set_selected_material_in_session(
    session_state: Dict[str, Any],
    material: ModuleMaterial
) -> None:
    """
    Store selected material in session state.
    
    Args:
        session_state: Streamlit session state
        material: Material to store
    
    Requirements:
        - 6.3: Store material selection in session state
    """
    session_state["selected_material"] = material.name


def get_module_materials_from_session(
    session_state: Dict[str, Any]
) -> List[ModuleMaterial]:
    """
    Get individual module materials from session state.
    
    Args:
        session_state: Streamlit session state
    
    Returns:
        List of materials for each module
    
    Requirements:
        - 6.4: Individual material per module
    """
    module_materials = session_state.get("module_materials", [])
    
    # Convert material names to material objects
    materials = []
    for material_name in module_materials:
        material = get_material_by_name(material_name)
        materials.append(material if material else DEFAULT_MATERIAL)
    
    return materials


def set_module_material_in_session(
    session_state: Dict[str, Any],
    module_index: int,
    material: ModuleMaterial
) -> None:
    """
    Set material for a specific module in session state.
    
    Args:
        session_state: Streamlit session state
        module_index: Index of the module
        material: Material to apply
    
    Requirements:
        - 6.4: Individual material per module
    """
    # Initialize module_materials if not exists
    if "module_materials" not in session_state:
        module_count = len(session_state.get("placed_module_positions", []))
        session_state["module_materials"] = [DEFAULT_MATERIAL.name] * module_count
    
    # Update material for specific module
    module_materials = session_state["module_materials"]
    if 0 <= module_index < len(module_materials):
        module_materials[module_index] = material.name
        session_state["module_materials"] = module_materials


# ============================================================================
# MATERIAL INFO
# ============================================================================

def get_material_info() -> Dict[str, Any]:
    """
    Get information about all available materials.
    
    Returns:
        Dictionary with material information
    
    Example:
        >>> info = get_material_info()
        >>> print(info["total_materials"])
        7
    """
    return {
        "total_materials": len(ALL_MATERIALS),
        "materials_by_finish": {
            "matt": len(MATERIALS_BY_FINISH[SurfaceFinish.MATTE]),
            "glänzend": len(MATERIALS_BY_FINISH[SurfaceFinish.GLOSSY]),
            "glas-glas": len(MATERIALS_BY_FINISH[SurfaceFinish.GLASS_GLASS])
        },
        "default_material": DEFAULT_MATERIAL.name,
        "available_colors": [m.color for m in ALL_MATERIALS],
        "available_finishes": [f.value for f in SurfaceFinish]
    }
