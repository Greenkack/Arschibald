"""
Tests für Task 9.1: Farb-System (Module Colors & Materials)

Diese Tests validieren die Implementierung des Farb- und Material-Systems
für PV-Module.

Requirements:
- 6.1: Support für verschiedene Modulfarben
- 6.2: Support für verschiedene Oberflächen-Materialien
"""

import pytest
from utils.pv3d_module_colors import (
    ModuleMaterial,
    SurfaceFinish,
    MATERIAL_BLACK,
    MATERIAL_DARK_BLUE,
    MATERIAL_DARK_RED,
    MATERIAL_ANTHRACITE,
    MATERIAL_SILVER,
    MATERIAL_BLACK_GLOSSY,
    MATERIAL_GLASS_GLASS,
    ALL_MATERIALS,
    MATERIALS_BY_FINISH,
    DEFAULT_MATERIAL,
    apply_material_to_module,
    get_material_by_name,
    get_materials_by_finish,
    hex_to_rgb,
    rgb_to_hex,
    get_selected_material_from_session,
    set_selected_material_in_session,
    get_module_materials_from_session,
    set_module_material_in_session,
    get_material_info
)


# ============================================================================
# TEST: MATERIAL DATACLASS
# ============================================================================

def test_material_creation():
    """Test 1: Material kann erstellt werden."""
    material = ModuleMaterial(
        name="Test Material",
        color="#ff0000",
        finish=SurfaceFinish.MATTE,
        opacity=0.8,
        reflectivity=0.3,
        description="Test description"
    )
    
    assert material.name == "Test Material"
    assert material.color == "#ff0000"
    assert material.finish == SurfaceFinish.MATTE
    assert material.opacity == 0.8
    assert material.reflectivity == 0.3
    assert material.description == "Test description"


def test_material_to_dict():
    """Test 2: Material kann zu Dictionary konvertiert werden."""
    material = MATERIAL_BLACK
    material_dict = material.to_dict()
    
    assert material_dict["name"] == "Schwarz (Standard)"
    assert material_dict["color"] == "#1a1a1a"
    assert material_dict["finish"] == "matt"
    assert material_dict["opacity"] == 1.0
    assert material_dict["reflectivity"] == 0.1


def test_material_from_dict():
    """Test 3: Material kann aus Dictionary erstellt werden."""
    material_dict = {
        "name": "Test",
        "color": "#00ff00",
        "finish": "glänzend",
        "opacity": 0.9,
        "reflectivity": 0.4,
        "description": "Test"
    }
    
    material = ModuleMaterial.from_dict(material_dict)
    
    assert material.name == "Test"
    assert material.color == "#00ff00"
    assert material.finish == SurfaceFinish.GLOSSY
    assert material.opacity == 0.9
    assert material.reflectivity == 0.4


# ============================================================================
# TEST: PREDEFINED MATERIALS
# ============================================================================

def test_predefined_materials_count():
    """Test 4: 7 vordefinierte Materialien existieren."""
    # Requirement 6.1: 5 Farben + 6.2: 2 Spezial-Oberflächen = 7 total
    assert len(ALL_MATERIALS) == 7


def test_predefined_colors():
    """Test 5: Alle 5 Standard-Farben existieren."""
    # Requirement 6.1: 5 Standard-Farben
    colors = [m.color for m in ALL_MATERIALS]
    
    assert "#1a1a1a" in colors  # Schwarz
    assert "#1a1a2e" in colors  # Dunkelblau
    assert "#8b0000" in colors  # Dunkelrot
    assert "#2f4f4f" in colors  # Anthrazit
    assert "#c0c0c0" in colors  # Silber


def test_predefined_finishes():
    """Test 6: Alle 3 Oberflächen-Typen existieren."""
    # Requirement 6.2: Matt, Glänzend, Glas-Glas
    finishes = [m.finish for m in ALL_MATERIALS]
    
    assert SurfaceFinish.MATTE in finishes
    assert SurfaceFinish.GLOSSY in finishes
    assert SurfaceFinish.GLASS_GLASS in finishes


def test_material_black():
    """Test 7: Schwarzes Material hat korrekte Eigenschaften."""
    assert MATERIAL_BLACK.name == "Schwarz (Standard)"
    assert MATERIAL_BLACK.color == "#1a1a1a"
    assert MATERIAL_BLACK.finish == SurfaceFinish.MATTE
    assert MATERIAL_BLACK.opacity == 1.0


def test_material_glass_glass():
    """Test 8: Glas-Glas Material ist transparent."""
    assert MATERIAL_GLASS_GLASS.finish == SurfaceFinish.GLASS_GLASS
    assert MATERIAL_GLASS_GLASS.opacity < 1.0  # Transparent


def test_default_material():
    """Test 9: Default Material ist Schwarz."""
    assert DEFAULT_MATERIAL == MATERIAL_BLACK


# ============================================================================
# TEST: MATERIAL COLLECTIONS
# ============================================================================

def test_materials_by_finish_matte():
    """Test 10: 5 matte Materialien existieren."""
    matte_materials = MATERIALS_BY_FINISH[SurfaceFinish.MATTE]
    assert len(matte_materials) == 5


def test_materials_by_finish_glossy():
    """Test 11: 1 glänzendes Material existiert."""
    glossy_materials = MATERIALS_BY_FINISH[SurfaceFinish.GLOSSY]
    assert len(glossy_materials) == 1


def test_materials_by_finish_glass():
    """Test 12: 1 Glas-Glas Material existiert."""
    glass_materials = MATERIALS_BY_FINISH[SurfaceFinish.GLASS_GLASS]
    assert len(glass_materials) == 1


# ============================================================================
# TEST: MATERIAL APPLICATION
# ============================================================================

def test_apply_material_to_module():
    """Test 13: Material kann auf Modul angewendet werden."""
    # Requirement 6.3: Material auf Module anwenden
    module_mesh = {
        "x": [0, 1, 1, 0],
        "y": [0, 0, 1, 1],
        "z": [0, 0, 0, 0]
    }
    
    updated_mesh = apply_material_to_module(module_mesh, MATERIAL_DARK_BLUE)
    
    assert updated_mesh["color"] == "#1a1a2e"
    assert updated_mesh["opacity"] == 1.0
    assert "lighting" in updated_mesh
    assert "customdata" in updated_mesh


def test_apply_material_matte_lighting():
    """Test 14: Mattes Material hat korrekte Beleuchtung."""
    module_mesh = {}
    updated_mesh = apply_material_to_module(module_mesh, MATERIAL_BLACK)
    
    lighting = updated_mesh["lighting"]
    assert lighting["specular"] == 0.2  # Low specular for matte
    assert lighting["roughness"] == 0.8  # High roughness for matte


def test_apply_material_glossy_lighting():
    """Test 15: Glänzendes Material hat korrekte Beleuchtung."""
    module_mesh = {}
    updated_mesh = apply_material_to_module(module_mesh, MATERIAL_BLACK_GLOSSY)
    
    lighting = updated_mesh["lighting"]
    assert lighting["specular"] == 0.8  # High specular for glossy
    assert lighting["roughness"] == 0.2  # Low roughness for glossy


def test_apply_material_glass_lighting():
    """Test 16: Glas-Glas Material hat korrekte Beleuchtung."""
    module_mesh = {}
    updated_mesh = apply_material_to_module(module_mesh, MATERIAL_GLASS_GLASS)
    
    lighting = updated_mesh["lighting"]
    assert lighting["fresnel"] == 0.7  # High fresnel for glass


# ============================================================================
# TEST: MATERIAL LOOKUP
# ============================================================================

def test_get_material_by_name_found():
    """Test 17: Material kann per Name gefunden werden."""
    material = get_material_by_name("Dunkelblau")
    
    assert material is not None
    assert material.name == "Dunkelblau"
    assert material.color == "#1a1a2e"


def test_get_material_by_name_not_found():
    """Test 18: Nicht existierendes Material gibt None zurück."""
    material = get_material_by_name("Nicht Existent")
    
    assert material is None


def test_get_materials_by_finish():
    """Test 19: Materialien können nach Oberfläche gefiltert werden."""
    matte_materials = get_materials_by_finish(SurfaceFinish.MATTE)
    
    assert len(matte_materials) == 5
    assert all(m.finish == SurfaceFinish.MATTE for m in matte_materials)


# ============================================================================
# TEST: COLOR CONVERSION
# ============================================================================

def test_hex_to_rgb():
    """Test 20: Hex zu RGB Konvertierung."""
    rgb = hex_to_rgb("#1a1a1a")
    
    assert rgb == (26, 26, 26)


def test_hex_to_rgb_without_hash():
    """Test 21: Hex zu RGB ohne # funktioniert."""
    rgb = hex_to_rgb("1a1a1a")
    
    assert rgb == (26, 26, 26)


def test_rgb_to_hex():
    """Test 22: RGB zu Hex Konvertierung."""
    hex_color = rgb_to_hex(26, 26, 26)
    
    assert hex_color == "#1a1a1a"


def test_hex_rgb_roundtrip():
    """Test 23: Hex → RGB → Hex Roundtrip."""
    original = "#ff00aa"
    rgb = hex_to_rgb(original)
    result = rgb_to_hex(*rgb)
    
    assert result == original


# ============================================================================
# TEST: SESSION STATE HELPERS
# ============================================================================

def test_get_selected_material_from_session_default():
    """Test 24: Default Material aus leerem Session State."""
    session_state = {}
    material = get_selected_material_from_session(session_state)
    
    assert material == DEFAULT_MATERIAL


def test_get_selected_material_from_session_custom():
    """Test 25: Custom Material aus Session State."""
    session_state = {"selected_material": "Dunkelblau"}
    material = get_selected_material_from_session(session_state)
    
    assert material.name == "Dunkelblau"


def test_set_selected_material_in_session():
    """Test 26: Material in Session State speichern."""
    session_state = {}
    set_selected_material_in_session(session_state, MATERIAL_DARK_RED)
    
    assert session_state["selected_material"] == "Dunkelrot"


def test_get_module_materials_from_session_empty():
    """Test 27: Leere Modul-Materialien aus Session State."""
    session_state = {}
    materials = get_module_materials_from_session(session_state)
    
    assert materials == []


def test_get_module_materials_from_session_with_data():
    """Test 28: Modul-Materialien aus Session State."""
    session_state = {
        "module_materials": ["Schwarz (Standard)", "Dunkelblau", "Dunkelrot"]
    }
    materials = get_module_materials_from_session(session_state)
    
    assert len(materials) == 3
    assert materials[0] == MATERIAL_BLACK
    assert materials[1] == MATERIAL_DARK_BLUE
    assert materials[2] == MATERIAL_DARK_RED


def test_set_module_material_in_session():
    """Test 29: Material für einzelnes Modul setzen."""
    # Requirement 6.4: Individuelle Farbe pro Modul
    session_state = {
        "placed_module_positions": [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    }
    
    set_module_material_in_session(session_state, 1, MATERIAL_DARK_BLUE)
    
    assert "module_materials" in session_state
    assert session_state["module_materials"][1] == "Dunkelblau"


def test_set_module_material_in_session_initializes():
    """Test 30: Material-Liste wird initialisiert wenn nicht vorhanden."""
    session_state = {
        "placed_module_positions": [(0, 0, 0), (1, 1, 1)]
    }
    
    set_module_material_in_session(session_state, 0, MATERIAL_SILVER)
    
    assert len(session_state["module_materials"]) == 2
    assert session_state["module_materials"][0] == "Silber"
    assert session_state["module_materials"][1] == "Schwarz (Standard)"  # Default


# ============================================================================
# TEST: MATERIAL INFO
# ============================================================================

def test_get_material_info():
    """Test 31: Material-Info kann abgerufen werden."""
    info = get_material_info()
    
    assert info["total_materials"] == 7
    assert info["materials_by_finish"]["matt"] == 5
    assert info["materials_by_finish"]["glänzend"] == 1
    assert info["materials_by_finish"]["glas-glas"] == 1
    assert info["default_material"] == "Schwarz (Standard)"
    assert len(info["available_colors"]) == 7
    assert len(info["available_finishes"]) == 3


# ============================================================================
# TEST: REQUIREMENTS VALIDATION
# ============================================================================

def test_requirement_6_1_five_colors():
    """Test 32: Requirement 6.1 - 5 Standard-Farben."""
    # Requirement 6.1: THE System SHALL folgende Modulfarben unterstützen
    colors = {m.color for m in ALL_MATERIALS}
    
    required_colors = {"#1a1a1a", "#1a1a2e", "#8b0000", "#2f4f4f", "#c0c0c0"}
    assert required_colors.issubset(colors)


def test_requirement_6_2_three_finishes():
    """Test 33: Requirement 6.2 - 3 Oberflächen-Materialien."""
    # Requirement 6.2: THE System SHALL verschiedene Oberflächen-Materialien simulieren
    finishes = {m.finish for m in ALL_MATERIALS}
    
    required_finishes = {SurfaceFinish.MATTE, SurfaceFinish.GLOSSY, SurfaceFinish.GLASS_GLASS}
    assert required_finishes == finishes


def test_requirement_6_3_apply_to_all():
    """Test 34: Requirement 6.3 - Material auf alle Module anwenden."""
    # Requirement 6.3: WHEN die Farbe geändert wird, THE System SHALL alle Module sofort aktualisieren
    # Tested by apply_material_to_module function
    module_mesh = {}
    updated_mesh = apply_material_to_module(module_mesh, MATERIAL_ANTHRACITE)
    
    assert updated_mesh["color"] == "#2f4f4f"


def test_requirement_6_4_individual_per_module():
    """Test 35: Requirement 6.4 - Individuelle Farbe pro Modul."""
    # Requirement 6.4: THE System SHALL die Farbe pro Modul individuell einstellbar machen
    session_state = {
        "placed_module_positions": [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    }
    
    # Set different materials for each module
    set_module_material_in_session(session_state, 0, MATERIAL_BLACK)
    set_module_material_in_session(session_state, 1, MATERIAL_DARK_BLUE)
    set_module_material_in_session(session_state, 2, MATERIAL_DARK_RED)
    
    materials = get_module_materials_from_session(session_state)
    
    assert materials[0] == MATERIAL_BLACK
    assert materials[1] == MATERIAL_DARK_BLUE
    assert materials[2] == MATERIAL_DARK_RED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
