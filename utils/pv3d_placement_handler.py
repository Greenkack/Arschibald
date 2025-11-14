"""
PV Module Placement Handler

This module handles the business logic for placing PV modules on roof surfaces.
It manages automatic placement, manual placement, reset operations, collision
detection, and session state management.

Key Functions:
    - check_module_collision: Check for module overlaps and boundary violations
    - handle_auto_placement: Automatic module placement
    - handle_reset_placement: Reset all modules
    - handle_manual_add: Add single module manually with collision detection
    - handle_remove_selected: Remove selected modules
    - calculate_z_position: Calculate height based on roof type
    - calculate_tilt_angle: Calculate tilt angle based on roof type
    - initialize_session_state: Initialize session state variables

Requirements: 2.2, 2.6, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3,
              7.4, 9.1, 9.2, 11.1, 11.2, 11.3, 11.4, 11.5
"""

from typing import Dict, Any, List, Tuple
import streamlit as st
import hashlib
import json

try:
    from utils.pv3d_grid_calculator import (
        calculate_module_grid,
        DEFAULT_SPACING,
        DEFAULT_MARGIN,
        PV_W,
        PV_H,
        MAX_MODULES
    )
except ImportError:
    # Fallback if grid calculator is not available
    def calculate_module_grid(*args, **kwargs):
        return []
    DEFAULT_SPACING = 0.05
    DEFAULT_MARGIN = 0.30
    PV_W = 1.05
    PV_H = 1.76
    MAX_MODULES = 200

# TASK 6: Import roof-type-specific logic
try:
    from utils.pv3d_roof_type_logic import get_roof_type_placement
    ROOF_TYPE_LOGIC_AVAILABLE = True
except ImportError:
    ROOF_TYPE_LOGIC_AVAILABLE = False
    print("[WARNING] Roof-type-specific logic not available, using generic placement")


# TASK 13: Position cache for performance
# Caches calculated positions to avoid recalculation
_position_cache: Dict[str, List[Tuple[float, float]]] = {}


def check_module_collision(
    new_position: tuple,
    existing_positions: List[tuple],
    roof_length: float,
    roof_width: float,
    margin: float = DEFAULT_MARGIN,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Check if a new module position collides with existing modules or roof edges.

    This function performs two types of collision detection:
    1. Module-to-module overlap detection
    2. Roof boundary violation detection

    Args:
        new_position: (x, y, z) tuple for the new module position
        existing_positions: List of (x, y, z) tuples for existing modules
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis)
        margin: Minimum margin from roof edges in meters
        orientation: Module orientation ("portrait" or "landscape")

    Returns:
        Dictionary with:
            - collision: bool - True if collision detected
            - type: str - Type of collision ("module", "boundary", "none")
            - message: str - Description of the collision
            - colliding_index: int or None - Index of colliding module (if any)

    Requirements:
        - 7.1: Check for module-to-module overlap
        - 7.2: Check for roof edge violation
        - 7.3: Display warning when collision detected
        - 7.4: Prevent placement when collision detected

    Algorithm:
        1. Extract x, y coordinates from new position
        2. Calculate module bounding box based on orientation
        3. Check if module exceeds roof boundaries (with margin)
        4. Check if module overlaps with any existing module
        5. Return collision status and details
    """
    # Extract coordinates
    new_x, new_y = new_position[0], new_position[1]

    # Determine module dimensions based on orientation
    if orientation == "landscape":
        module_width = PV_H  # 1.76m
        module_height = PV_W  # 1.05m
    else:  # portrait (default)
        module_width = PV_W  # 1.05m
        module_height = PV_H  # 1.76m

    # Calculate half-dimensions for bounding box
    half_width = module_width / 2
    half_height = module_height / 2

    # Requirement 7.2: Check for roof boundary violations
    # FIX: Die Grid-Berechnung platziert Module bereits MIT Margin
    # Die Kollisionserkennung sollte nur prüfen, ob die Modul-KANTEN
    # über die Dachkante hinausgehen (nicht das Zentrum!)
    
    # Berechne die Modul-Kanten
    module_left = new_x - half_width
    module_right = new_x + half_width
    module_bottom = new_y - half_height
    module_top = new_y + half_height
    
    # Berechne die Dach-Grenzen (ohne zusätzlichen Margin-Abzug)
    roof_left = -(roof_length / 2)
    roof_right = (roof_length / 2)
    roof_bottom = -(roof_width / 2)
    roof_top = (roof_width / 2)

    # Check if module EDGES extend beyond roof boundaries
    if module_left < roof_left:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"[WARNING] Modul überschreitet linke Dachkante "
                f"(Modul-Kante: {module_left:.2f}m < Dachkante: {roof_left:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_right > roof_right:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"[WARNING] Modul überschreitet rechte Dachkante "
                f"(Modul-Kante: {module_right:.2f}m > Dachkante: {roof_right:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_bottom < roof_bottom:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"[WARNING] Modul überschreitet untere Dachkante "
                f"(Modul-Kante: {module_bottom:.2f}m < Dachkante: {roof_bottom:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_top > roof_top:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"[WARNING] Modul überschreitet obere Dachkante "
                f"(Modul-Kante: {module_top:.2f}m > Dachkante: {roof_top:.2f}m)"
            ),
            "colliding_index": None
        }

    # Requirement 7.1: Check for module-to-module overlap
    for idx, existing_pos in enumerate(existing_positions):
        existing_x, existing_y = existing_pos[0], existing_pos[1]

        # Calculate distance between module centers
        dx = abs(new_x - existing_x)
        dy = abs(new_y - existing_y)

        # Check for overlap using bounding box collision detection
        # Two rectangles overlap if:
        # - Distance between centers in X < sum of half-widths
        # - Distance between centers in Y < sum of half-heights
        if dx < module_width and dy < module_height:
            return {
                "collision": True,
                "type": "module",
                "message": (
                    f"[WARNING] Modul überlappt mit bestehendem Modul #{idx + 1} "
                    f"(Abstand: X={dx:.2f}m, Y={dy:.2f}m)"
                ),
                "colliding_index": idx
            }

    # No collision detected
    return {
        "collision": False,
        "type": "none",
        "message": "[OK] Keine Kollision erkannt",
        "colliding_index": None
    }


def _get_cache_key(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    spacing: float,
    margin: float,
    orientation: str
) -> str:
    """
    Generate a cache key for position calculations.
    
    TASK 13: Caching of calculated positions for performance.
    
    Args:
        roof_length: Length of the roof
        roof_width: Width of the roof
        module_quantity: Number of modules
        spacing: Spacing between modules
        margin: Margin from edges
        orientation: Module orientation
    
    Returns:
        Hash string to use as cache key
    
    Requirements:
        - 10.5: Caching von berechneten Positionen
    """
    # Create a dictionary of parameters
    params = {
        "length": round(roof_length, 2),
        "width": round(roof_width, 2),
        "quantity": module_quantity,
        "spacing": round(spacing, 3),
        "margin": round(margin, 3),
        "orientation": orientation
    }
    
    # Convert to JSON string and hash it
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(params_str.encode()).hexdigest()


def handle_auto_placement(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    roof_type: str,
    roof_pitch: float = 0.0,
    spacing: float = DEFAULT_SPACING,
    margin: float = DEFAULT_MARGIN,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Handle automatic module placement on roof surface.

    TASK 13: Performance-optimized version with caching and module limit.

    This function calculates optimal module positions using the grid
    calculator, converts 2D positions to 3D positions with appropriate
    Z-coordinates based on roof type, and stores results in session state.

    Args:
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis)
        module_quantity: Desired number of modules to place
        roof_type: Type of roof ("Flachdach", "Satteldach", "Pultdach", etc.)
        roof_pitch: Roof pitch angle in degrees (default: 0.0)
        spacing: Spacing between modules in meters
        margin: Margin from roof edges in meters
        orientation: Module orientation ("portrait" or "landscape")

    Returns:
        Dictionary with:
            - success: bool - Whether placement was successful
            - positions: List of (x, y, z) tuples - 3D positions
            - count: int - Number of modules placed
            - message: str - Status or error message

    Requirements:
        - 2.2: Automatic placement when button clicked
        - 2.6: Display number of placed modules
        - 6.1-6.5: Roof type specific placement
        - 9.1-9.2: Session state management
        - 11.1-11.5: Error handling
        - 10.5: Performance optimization with caching
    """
    # Requirement 11.5: Store previous state for fallback
    previous_positions = st.session_state.get("placed_module_positions", [])
    previous_count = st.session_state.get("placed_module_count", 0)
    
    try:
        # TASK 13: Limit module quantity for performance
        # Requirement 10.5: Begrenzung auf maximal 200 Module
        if module_quantity > MAX_MODULES:
            print(f"[WARNING] Module quantity limited to {MAX_MODULES} for performance")
            module_quantity = MAX_MODULES
        # Requirement 11.1: Validate roof dimensions (> 0)
        if roof_length <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[ERROR] Fehler: Dachlänge muss größer als 0 sein "
                    f"(aktuell: {roof_length:.2f}m)"
                )
            }
        
        if roof_width <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[ERROR] Fehler: Dachbreite muss größer als 0 sein "
                    f"(aktuell: {roof_width:.2f}m)"
                )
            }

        # Requirement 11.1: Validate module quantity (> 0)
        if module_quantity <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[ERROR] Fehler: Modulanzahl muss größer als 0 sein "
                    f"(aktuell: {module_quantity})"
                )
            }
        
        # Additional validation for reasonable values
        if roof_length > 1000 or roof_width > 1000:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[ERROR] Fehler: Dach-Dimensionen unrealistisch groß "
                    f"(Länge: {roof_length:.2f}m, Breite: {roof_width:.2f}m)"
                )
            }
        
        if module_quantity > 1000:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[ERROR] Fehler: Modulanzahl zu groß "
                    f"(aktuell: {module_quantity}, Maximum: 1000)"
                )
            }

        # FIX: Unterscheide zwischen Flachdach und geneigten Dächern
        # Normalisiere roof_type (lowercase für case-insensitive Vergleich)
        roof_type_normalized = roof_type.strip().lower() if roof_type else "flachdach"
        
        # TASK 6: Use roof-type-specific logic if available
        if ROOF_TYPE_LOGIC_AVAILABLE:
            print(f"   Verwende dachtyp-spezifische Logik für '{roof_type}'")
            try:
                # Use roof-type-specific placement logic
                positions_3d = get_roof_type_placement(
                    roof_type=roof_type,
                    roof_length=roof_length,
                    roof_width=roof_width,
                    roof_pitch=roof_pitch,
                    module_quantity=module_quantity,
                    module_width=PV_W,
                    module_height=PV_H,
                    margin=margin,
                    orientation=orientation
                )
                
                if not positions_3d:
                    return {
                        "success": False,
                        "positions": [],
                        "count": 0,
                        "message": (
                            "[WARNING] Keine Module konnten platziert werden. "
                            "Die Dachfläche ist zu klein oder die Ränder zu groß."
                        )
                    }
                
                # Requirement 9.1: Store positions in session state
                st.session_state["placed_module_positions"] = positions_3d

                # Requirement 9.2: Store count in session state
                st.session_state["placed_module_count"] = len(positions_3d)

                # Requirement 2.6: Return success with count
                actual_count = len(positions_3d)
                if actual_count < module_quantity:
                    message = (
                        f"[OK] {actual_count} Module platziert "
                        f"(gewünscht: {module_quantity}). "
                        "Nicht genug Platz für alle Module."
                    )
                else:
                    message = f"[OK] {actual_count} Module erfolgreich platziert!"

                return {
                    "success": True,
                    "positions": positions_3d,
                    "count": actual_count,
                    "message": message
                }
                
            except Exception as roof_error:
                print(f"[WARNING] Fehler bei dachtyp-spezifischer Logik: {roof_error}")
                print("   Fallback zu generischer Grid-Berechnung")
                # Fall through to generic logic below
        
        # TASK 13: Check cache first for performance
        # Requirement 10.5: Caching von berechneten Positionen
        cache_key = _get_cache_key(
            roof_length, roof_width, module_quantity,
            spacing, margin, orientation
        )
        
        if cache_key in _position_cache:
            print(f"[OK] Using cached positions for {module_quantity} modules")
            grid_positions_2d = _position_cache[cache_key]
        else:
            # Requirement 11.3: Try-Catch around grid calculation
            try:
                grid_positions_2d = calculate_module_grid(
                    roof_length=roof_length,
                    roof_width=roof_width,
                    module_quantity=module_quantity,
                    spacing=spacing,
                    margin=margin,
                    orientation=orientation
                )
                
                # TASK 13: Cache the result for future use
                # Requirement 10.5: Caching von berechneten Positionen
                _position_cache[cache_key] = grid_positions_2d
                print(f"[OK] Cached positions for {module_quantity} modules")
                
            except Exception as grid_error:
                # Requirement 11.4: Meaningful error messages
                return {
                    "success": False,
                    "positions": [],
                    "count": 0,
                    "message": (
                        f"[ERROR] Fehler bei der Grid-Berechnung: {str(grid_error)}"
                    )
                }

        if not grid_positions_2d:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "[WARNING] Keine Module konnten platziert werden. "
                    "Die Dachfläche ist zu klein oder die Ränder zu groß."
                )
            }

        # TASK 2.2: Modul-Positionierung korrigieren
        # Requirement 2.2.1: Berechne korrekte X, Y, Z Koordinaten
        # Requirement 2.2.2: Berücksichtige Dachtyp (Flach vs. Schrägdach)
        # Requirement 2.2.3: Berücksichtige Aufständerung
        
        # Für geneigte Dächer muss die Z-Position für jedes Modul individuell berechnet werden
        # da die Dachfläche geneigt ist und Module auf unterschiedlichen Höhen liegen
        import math
        
        try:
            positions_3d = []
            
            # Requirement 2.2.2: Unterscheide zwischen Flachdach und geneigten Dächern
            if roof_type_normalized == "flachdach":
                # Flachdach: Alle Module auf gleicher Höhe
                # Requirement 2.2.3: Mit Aufständerung (0.30m)
                z_position = calculate_z_position(roof_type, roof_pitch, roof_width)
                positions_3d = [
                    (float(x), float(y), float(z_position))
                    for x, y in grid_positions_2d
                ]
                print(f"   Flachdach: Z-Position = {z_position:.2f}m (konstant)")
                
            elif roof_type_normalized in ["satteldach", "satteldach mit gaube"]:
                # Satteldach: Z steigt vom Rand zur Mitte (First)
                # Module liegen auf der Dachfläche
                base_z = calculate_z_position(roof_type, roof_pitch, roof_width)
                
                if roof_pitch > 0:
                    inclination_rad = math.radians(roof_pitch)
                    for x, y in grid_positions_2d:
                        # Requirement 2.2.1: Berechne Z basierend auf Y-Position
                        # Abstand von Traufe (y = -roof_width/2)
                        dist_from_eave = y + roof_width / 2
                        z_offset = dist_from_eave * math.tan(inclination_rad)
                        z = base_z + z_offset
                        positions_3d.append((float(x), float(y), float(z)))
                    print(f"   Satteldach: Z-Position variiert von {base_z:.2f}m bis {base_z + roof_width/2 * math.tan(inclination_rad):.2f}m")
                else:
                    # Keine Neigung (sollte nicht vorkommen)
                    positions_3d = [
                        (float(x), float(y), float(base_z))
                        for x, y in grid_positions_2d
                    ]
                    print(f"   Satteldach (keine Neigung): Z-Position = {base_z:.2f}m (konstant)")
                    
            elif roof_type_normalized in ["walmdach", "krüppelwalmdach"]:
                # Walmdach/Krüppelwalmdach: Ähnlich wie Satteldach
                # Z steigt vom Rand zur Mitte
                base_z = calculate_z_position(roof_type, roof_pitch, roof_width)
                
                if roof_pitch > 0:
                    inclination_rad = math.radians(roof_pitch)
                    for x, y in grid_positions_2d:
                        # Requirement 2.2.1: Berechne Z basierend auf Y-Position
                        dist_from_eave = y + roof_width / 2
                        z_offset = dist_from_eave * math.tan(inclination_rad)
                        z = base_z + z_offset
                        positions_3d.append((float(x), float(y), float(z)))
                    print(f"   {roof_type}: Z-Position variiert von {base_z:.2f}m bis {base_z + roof_width/2 * math.tan(inclination_rad):.2f}m")
                else:
                    positions_3d = [
                        (float(x), float(y), float(base_z))
                        for x, y in grid_positions_2d
                    ]
                    print(f"   {roof_type} (keine Neigung): Z-Position = {base_z:.2f}m (konstant)")
                    
            elif roof_type_normalized == "pultdach":
                # Pultdach: Z steigt linear von vorne nach hinten
                base_z = calculate_z_position(roof_type, roof_pitch, roof_width)
                
                if roof_pitch > 0:
                    inclination_rad = math.radians(roof_pitch)
                    for x, y in grid_positions_2d:
                        # Requirement 2.2.1: Berechne Z basierend auf Y-Position
                        # Abstand von vorderer Kante (y = -roof_width/2)
                        dist_from_front = y + roof_width / 2
                        z_offset = dist_from_front * math.tan(inclination_rad)
                        z = base_z + z_offset
                        positions_3d.append((float(x), float(y), float(z)))
                    print(f"   Pultdach: Z-Position variiert von {base_z:.2f}m bis {base_z + roof_width * math.tan(inclination_rad):.2f}m")
                else:
                    positions_3d = [
                        (float(x), float(y), float(base_z))
                        for x, y in grid_positions_2d
                    ]
                    print(f"   Pultdach (keine Neigung): Z-Position = {base_z:.2f}m (konstant)")
                    
            elif roof_type_normalized == "zeltdach":
                # Zeltdach: Z steigt vom Rand zur Mitte (pyramidenförmig)
                base_z = calculate_z_position(roof_type, roof_pitch, roof_width)
                
                if roof_pitch > 0:
                    inclination_rad = math.radians(roof_pitch)
                    for x, y in grid_positions_2d:
                        # Requirement 2.2.1: Berechne Z basierend auf Abstand vom Rand
                        # Minimaler Abstand von allen 4 Kanten
                        dist_from_edge = min(
                            y + roof_width / 2,   # Abstand von vorderer Kante
                            roof_width / 2 - y,   # Abstand von hinterer Kante
                            x + roof_length / 2,  # Abstand von linker Kante
                            roof_length / 2 - x   # Abstand von rechter Kante
                        )
                        z_offset = dist_from_edge * math.tan(inclination_rad)
                        z = base_z + z_offset
                        positions_3d.append((float(x), float(y), float(z)))
                    print(f"   Zeltdach: Z-Position variiert von {base_z:.2f}m bis {base_z + min(roof_width, roof_length)/2 * math.tan(inclination_rad):.2f}m")
                else:
                    positions_3d = [
                        (float(x), float(y), float(base_z))
                        for x, y in grid_positions_2d
                    ]
                    print(f"   Zeltdach (keine Neigung): Z-Position = {base_z:.2f}m (konstant)")
                    
            else:
                # Andere/Unbekannte Dachtypen: Konstante Z-Höhe (Fallback)
                z_position = calculate_z_position(roof_type, roof_pitch, roof_width)
                positions_3d = [
                    (float(x), float(y), float(z_position))
                    for x, y in grid_positions_2d
                ]
                print(f"   {roof_type} (Fallback): Z-Position = {z_position:.2f}m (konstant)")
                
        except (TypeError, ValueError, Exception) as conv_error:
            # Requirement 11.4: Meaningful error messages
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    f"[ERROR] Fehler bei der Positions-Berechnung: "
                    f"{str(conv_error)}"
                )
            }

        # Requirement 9.1: Store positions in session state
        st.session_state["placed_module_positions"] = positions_3d

        # Requirement 9.2: Store count in session state
        st.session_state["placed_module_count"] = len(positions_3d)

        # Requirement 2.6: Return success with count
        actual_count = len(positions_3d)
        if actual_count < module_quantity:
            message = (
                f"[OK] {actual_count} Module platziert "
                f"(gewünscht: {module_quantity}). "
                "Nicht genug Platz für alle Module."
            )
        else:
            message = f"[OK] {actual_count} Module erfolgreich platziert!"

        return {
            "success": True,
            "positions": positions_3d,
            "count": actual_count,
            "message": message
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling with meaningful messages
        # Requirement 11.5: Fallback to previous state on error
        st.session_state["placed_module_positions"] = previous_positions
        st.session_state["placed_module_count"] = previous_count
        
        error_message = (
            f"[ERROR] Unerwarteter Fehler bei der automatischen Platzierung: "
            f"{str(e)}. Vorheriger Zustand wiederhergestellt."
        )
        print(error_message)
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "positions": previous_positions,
            "count": previous_count,
            "message": error_message
        }


def handle_reset_placement() -> Dict[str, Any]:
    """
    Reset all placed modules by clearing session state.

    This function removes all module positions from session state and
    resets the module count to zero.

    Returns:
        Dictionary with:
            - success: bool - Always True
            - message: str - Confirmation message

    Requirements:
        - 4.4: Reset button functionality
        - 9.1-9.2: Session state management
    """
    try:
        # Requirement 9.1, 9.2: Clear session state
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Also clear selected modules if they exist
        if "selected_module_indices" in st.session_state:
            st.session_state["selected_module_indices"] = []

        return {
            "success": True,
            "message": "[OK] Alle Module wurden zurückgesetzt"
        }

    except Exception as e:
        # Requirement 11.2: Error handling
        error_message = f"[ERROR] Fehler beim Zurücksetzen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "message": error_message
        }


def calculate_z_position(roof_type: str, roof_pitch: float = 0.0, roof_width: float = 10.0) -> float:
    """
    Calculate Z-position (height) for modules based on roof type.

    TASK 2.2: Modul-Positionierung korrigieren
    - Berechnet korrekte Z-Position basierend auf Dachtyp
    - Berücksichtigt Aufständerung für Flachdächer
    - Berücksichtigt Dachflächen-Position für geneigte Dächer

    Different roof types require different mounting heights:
    - Flat roofs: Modules are mounted on elevated frames (Aufständerung) at 30cm
    - Pitched roofs: Modules are mounted on the roof surface with 15cm clearance

    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_pitch: Roof pitch angle in degrees (not used for z-position, only for tilt)
        roof_width: Width of the roof in meters (not used for base z-position)

    Returns:
        Z-position in meters above the wall height (relative to roof base)
        This is a RELATIVE position that will be added to wall_height_m

    Requirements:
        - 2.2.1: Korrekte Z-Koordinaten berechnen
        - 2.2.2: Dachtyp berücksichtigen (Flach vs. Schrägdach)
        - 2.2.3: Aufständerung für Flachdächer
        - 6.1: Flat roof with elevated mounting (30° tilt)
        - 6.2: Gable roof parallel to surface
        - 6.3: Shed roof parallel to surface
        - 6.4: Calculate Z-position based on roof type
    """
    import math
    
    # Normalize roof type string (case-insensitive, strip whitespace)
    roof_type_normalized = roof_type.strip().lower() if roof_type else "flachdach"

    # Requirement 2.2.2, 2.2.3, 6.1: Flat roof with elevated mounting
    if "flach" in roof_type_normalized:
        # Flachdach: Module werden auf Aufständerung montiert
        # 30cm Höhe für Montagegestell (ermöglicht 30° Neigung)
        return 0.30  # 30cm elevation for mounting frame (Aufständerung)

    # Requirement 2.2.2, 6.2, 6.3: Pitched roofs (Satteldach, Pultdach, etc.)
    # Modules are mounted on the roof surface
    else:
        # Geneigte Dächer: Module liegen auf der Dachfläche
        # Kleine Erhöhung über Dachbasis für Montage-Schienen
        # Die tatsächliche Dachneigung wird durch die Dachgeometrie selbst dargestellt
        # Module folgen der Dachneigung (siehe calculate_tilt_angle)
        return 0.15  # 15cm clearance above roof base (Traufhöhe)


def calculate_tilt_angle(roof_type: str, roof_pitch: float = 0.0) -> float:
    """
    Calculate tilt angle for modules based on roof type.

    TASK 2.3: Modul-Rotation korrigieren
    - Berechnet korrekten Neigungs-Winkel basierend auf Dachtyp
    - Flachdächer: 30° Aufständerung für optimale Sonneneinstrahlung
    - Geneigte Dächer: Folgen der Dachneigung (parallel zur Dachfläche)

    Different roof types require different tilt angles:
    - Flat roofs: Modules are tilted at 30° for optimal solar exposure
    - Pitched roofs: Modules follow the roof pitch angle (parallel to roof surface)

    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_pitch: Roof pitch angle in degrees

    Returns:
        Tilt angle in degrees (0-90°)

    Requirements:
        - 2.3.1: Korrekte Rotation für Schrägdächer
        - 2.3.2: Aufständerungs-Winkel für Flachdächer
        - 2.3.3: Alle Dachtypen testen
        - 6.1: Flat roof with 30° tilt (Aufständerung)
        - 6.5: Pitched roofs use roof pitch angle
    """
    # Normalize roof type string (case-insensitive, strip whitespace)
    roof_type_normalized = roof_type.strip().lower() if roof_type else "flachdach"

    # Requirement 2.3.2, 6.1: Flat roof with 30° tilt
    if "flach" in roof_type_normalized:
        # Flachdach: Module werden mit 30° Neigung aufgeständert
        # Dies ist optimal für Sonneneinstrahlung in Mitteleuropa
        return 30.0  # 30° tilt for optimal solar exposure

    # Requirement 2.3.1, 6.5: Pitched roofs use roof pitch angle
    else:
        # Geneigte Dächer: Module liegen parallel zur Dachfläche
        # Sie verwenden die Dachneigung als Neigungs-Winkel
        # Wenn roof_pitch = 0, dann sind Module horizontal (sollte nicht vorkommen)
        return roof_pitch if roof_pitch > 0 else 0.0


def handle_manual_add(
    x: float,
    y: float,
    roof_type: str,
    roof_pitch: float = 0.0,
    roof_length: float = 10.0,
    roof_width: float = 8.0,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Add a single module at a specific position with collision detection.

    This function allows manual placement of individual modules at
    user-specified coordinates. It performs collision detection to
    prevent overlapping modules and boundary violations.

    Args:
        x: X-coordinate in meters (relative to roof center)
        y: Y-coordinate in meters (relative to roof center)
        roof_type: Type of roof
        roof_pitch: Roof pitch angle in degrees
        roof_length: Length of the roof in meters
        roof_width: Width of the roof in meters
        orientation: Module orientation ("portrait" or "landscape")

    Returns:
        Dictionary with:
            - success: bool - Whether addition was successful
            - message: str - Status or error message

    Requirements:
        - 4.1: Manual add button functionality
        - 6.4: Calculate Z-position based on roof type
        - 7.1-7.4: Collision detection and prevention
        - 9.1-9.2: Session state management
        - 11.1-11.3: Error handling and collision detection
    """
    try:
        # Initialize session state if needed
        if "placed_module_positions" not in st.session_state:
            st.session_state["placed_module_positions"] = []

        # Calculate Z-position based on roof type
        z = calculate_z_position(roof_type, roof_pitch, roof_width)

        # Create new position
        new_position = (x, y, z)

        # Requirement 7.1-7.4: Check for collisions
        existing_positions = st.session_state["placed_module_positions"]

        collision_result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation=orientation
        )

        # Requirement 7.3, 7.4: Prevent placement if collision detected
        if collision_result["collision"]:
            return {
                "success": False,
                "message": collision_result["message"]
            }

        # Add the module (no collision)
        existing_positions.append(new_position)

        # Requirement 9.1, 9.2: Update session state
        st.session_state["placed_module_positions"] = existing_positions
        st.session_state["placed_module_count"] = len(existing_positions)

        return {
            "success": True,
            "message": (
                f"[OK] Modul hinzugefügt an Position "
                f"({x:.2f}, {y:.2f}, {z:.2f})"
            )
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"[ERROR] Fehler beim Hinzufügen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "message": error_message
        }


def handle_remove_selected(
    selected_indices: List[int]
) -> Dict[str, Any]:
    """
    Remove selected modules from placement.

    This function removes modules at the specified indices from the
    session state.

    Args:
        selected_indices: List of indices of modules to remove

    Returns:
        Dictionary with:
            - success: bool - Whether removal was successful
            - count: int - Number of modules removed
            - message: str - Status or error message

    Requirements:
        - 4.2: Remove selected button functionality
        - 9.1-9.2: Session state management
        - 11.2: Error handling
    """
    try:
        # Get current positions
        if "placed_module_positions" not in st.session_state:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Entfernen vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Entfernen vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module ausgewählt"
            }

        # Remove modules at selected indices (in reverse order to maintain
        # indices)
        removed_count = 0
        for index in sorted(selected_indices, reverse=True):
            if 0 <= index < len(positions):
                positions.pop(index)
                removed_count += 1

        # Requirement 9.1, 9.2: Update session state
        st.session_state["placed_module_positions"] = positions
        st.session_state["placed_module_count"] = len(positions)

        # Clear selected indices
        if "selected_module_indices" in st.session_state:
            st.session_state["selected_module_indices"] = []

        return {
            "success": True,
            "count": removed_count,
            "message": f"[OK] {removed_count} Module entfernt"
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"[ERROR] Fehler beim Entfernen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "count": 0,
            "message": error_message
        }


def initialize_session_state() -> None:
    """
    Initialize session state variables for module placement.

    This function ensures all required session state variables exist
    with appropriate default values.

    Requirements:
        - 9.1: Initialize placed_module_positions
        - 9.2: Initialize placed_module_count
        - 9.3: Initialize trigger_auto_placement
        - 9.4: Initialize before panel rendering
    """
    # Requirement 9.1: Module positions
    if "placed_module_positions" not in st.session_state:
        st.session_state["placed_module_positions"] = []

    # Requirement 9.2: Module count
    if "placed_module_count" not in st.session_state:
        st.session_state["placed_module_count"] = 0

    # Requirement 9.3: Auto-placement trigger
    if "trigger_auto_placement" not in st.session_state:
        st.session_state["trigger_auto_placement"] = False

    # Selected modules for manual operations
    if "selected_module_indices" not in st.session_state:
        st.session_state["selected_module_indices"] = []

    # Display options
    if "show_placement_grid" not in st.session_state:
        st.session_state["show_placement_grid"] = False

    if "show_module_numbers" not in st.session_state:
        st.session_state["show_module_numbers"] = False


def handle_move_selected(
    selected_indices: List[int],
    offset_x: float,
    offset_y: float,
    roof_length: float,
    roof_width: float,
    roof_type: str,
    roof_pitch: float = 0.0
) -> Dict[str, Any]:
    """
    Move selected modules by specified offset.

    TASK 4.2: Modul verschieben
    This function moves selected modules by the specified X and Y offsets,
    with collision detection to prevent overlaps and boundary violations.

    Args:
        selected_indices: List of indices of modules to move
        offset_x: X-offset in meters (positive = right, negative = left)
        offset_y: Y-offset in meters (positive = back, negative = front)
        roof_length: Length of the roof in meters
        roof_width: Width of the roof in meters
        roof_type: Type of roof
        roof_pitch: Roof pitch angle in degrees

    Returns:
        Dictionary with:
            - success: bool - Whether move was successful
            - count: int - Number of modules moved
            - message: str - Status or error message

    Requirements:
        - 4.2.3: Move button functionality
        - 7.1-7.4: Collision detection during move
        - 9.1-9.2: Session state management
        - 11.2: Error handling
    """
    try:
        # Get current positions
        if "placed_module_positions" not in st.session_state:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Verschieben vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Verschieben vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module ausgewählt"
            }

        # Validate offset values
        if abs(offset_x) < 0.01 and abs(offset_y) < 0.01:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Offset zu klein (mindestens 0.01m erforderlich)"
            }

        # Calculate new positions for selected modules
        new_positions = []
        moved_count = 0
        collision_detected = False

        for index in selected_indices:
            if 0 <= index < len(positions):
                old_x, old_y, old_z = positions[index]
                new_x = old_x + offset_x
                new_y = old_y + offset_y

                # Recalculate Z-position based on new X, Y and roof type
                # For flat roofs, Z stays the same
                # For pitched roofs, Z depends on position on roof surface
                if roof_type.lower().strip() == "flachdach":
                    new_z = old_z  # Z doesn't change for flat roofs
                else:
                    # For pitched roofs, recalculate Z based on new Y position
                    import math
                    base_z = calculate_z_position(roof_type, roof_pitch, roof_width)
                    
                    if roof_pitch > 0:
                        inclination_rad = math.radians(roof_pitch)
                        dist_from_eave = new_y + roof_width / 2
                        z_offset = dist_from_eave * math.tan(inclination_rad)
                        new_z = base_z + z_offset
                    else:
                        new_z = base_z

                new_position = (new_x, new_y, new_z)

                # Check for collisions with other modules (excluding selected ones)
                other_positions = [
                    pos for i, pos in enumerate(positions)
                    if i not in selected_indices
                ]

                collision_result = check_module_collision(
                    new_position=new_position,
                    existing_positions=other_positions,
                    roof_length=roof_length,
                    roof_width=roof_width,
                    margin=DEFAULT_MARGIN,
                    orientation="portrait"
                )

                if collision_result["collision"]:
                    collision_detected = True
                    return {
                        "success": False,
                        "count": 0,
                        "message": (
                            f"[ERROR] Verschieben nicht möglich: "
                            f"{collision_result['message']}"
                        )
                    }

                new_positions.append((index, new_position))
                moved_count += 1

        # If no collisions, apply all moves
        if not collision_detected:
            for index, new_position in new_positions:
                positions[index] = new_position

            # Update session state
            st.session_state["placed_module_positions"] = positions

            return {
                "success": True,
                "count": moved_count,
                "message": (
                    f"[OK] {moved_count} Module verschoben "
                    f"(Δx={offset_x:+.2f}m, Δy={offset_y:+.2f}m)"
                )
            }

    except Exception as e:
        error_message = f"[ERROR] Fehler beim Verschieben: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "count": 0,
            "message": error_message
        }


def handle_rotate_selected(
    selected_indices: List[int],
    rotation_degrees: float
) -> Dict[str, Any]:
    """
    Rotate selected modules by specified angle.

    TASK 4.2: Modul drehen
    This function rotates selected modules around their center point by
    the specified angle. Note: This is a simplified 2D rotation in the
    XY plane. For full 3D rotation (tilt), use module transforms.

    Args:
        selected_indices: List of indices of modules to rotate
        rotation_degrees: Rotation angle in degrees (positive = counterclockwise)

    Returns:
        Dictionary with:
            - success: bool - Whether rotation was successful
            - count: int - Number of modules rotated
            - message: str - Status or error message

    Requirements:
        - 4.2.4: Rotate button functionality
        - 9.1-9.2: Session state management
        - 11.2: Error handling

    Note:
        This function currently rotates module positions around the roof center.
        For individual module orientation (azimuth/tilt), use AdvancedLayoutConfig
        with module_transforms.
    """
    try:
        # Get current positions
        if "placed_module_positions" not in st.session_state:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Drehen vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module zum Drehen vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine Module ausgewählt"
            }

        # Validate rotation angle
        if abs(rotation_degrees) < 1.0:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Rotationswinkel zu klein (mindestens 1° erforderlich)"
            }

        # Calculate center of selected modules
        selected_positions = [
            positions[i] for i in selected_indices
            if 0 <= i < len(positions)
        ]

        if not selected_positions:
            return {
                "success": False,
                "count": 0,
                "message": "[WARNING] Keine gültigen Module ausgewählt"
            }

        # Calculate centroid (center point) of selected modules
        center_x = sum(pos[0] for pos in selected_positions) / len(selected_positions)
        center_y = sum(pos[1] for pos in selected_positions) / len(selected_positions)

        # Convert rotation angle to radians
        import math
        rotation_rad = math.radians(rotation_degrees)
        cos_angle = math.cos(rotation_rad)
        sin_angle = math.sin(rotation_rad)

        # Rotate each selected module around the centroid
        rotated_count = 0
        for index in selected_indices:
            if 0 <= index < len(positions):
                old_x, old_y, old_z = positions[index]

                # Translate to origin (relative to centroid)
                rel_x = old_x - center_x
                rel_y = old_y - center_y

                # Apply 2D rotation matrix
                new_rel_x = rel_x * cos_angle - rel_y * sin_angle
                new_rel_y = rel_x * sin_angle + rel_y * cos_angle

                # Translate back
                new_x = new_rel_x + center_x
                new_y = new_rel_y + center_y

                # Z-position stays the same for 2D rotation
                new_z = old_z

                # Update position
                positions[index] = (new_x, new_y, new_z)
                rotated_count += 1

        # Update session state
        st.session_state["placed_module_positions"] = positions

        return {
            "success": True,
            "count": rotated_count,
            "message": (
                f"[OK] {rotated_count} Module gedreht "
                f"({rotation_degrees:+.1f}° um Zentrum)"
            )
        }

    except Exception as e:
        error_message = f"[ERROR] Fehler beim Drehen: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "count": 0,
            "message": error_message
        }


def get_placement_statistics() -> Dict[str, Any]:
    """
    Get current placement statistics from session state.

    Returns:
        Dictionary with:
            - placed_count: int - Number of currently placed modules
            - positions: List[Tuple] - List of 3D positions
            - has_modules: bool - Whether any modules are placed
    """
    placed_count = st.session_state.get("placed_module_count", 0)
    positions = st.session_state.get("placed_module_positions", [])

    return {
        "placed_count": placed_count,
        "positions": positions,
        "has_modules": placed_count > 0
    }


# Example usage and testing
if __name__ == "__main__":
    print("=== PV Module Placement Handler Test ===\n")

    # Note: This test requires Streamlit session state
    # In a real environment, this would be run within a Streamlit app

    print("Test 1: Calculate Z-position for different roof types")
    print(f"  Flachdach: {calculate_z_position('Flachdach', 0.0, 10.0)}m")
    print(f"  Satteldach: {calculate_z_position('Satteldach', 35.0, 10.0)}m")
    print(f"  Pultdach: {calculate_z_position('Pultdach', 25.0, 10.0)}m")
    print()

    print("Test 2: Calculate tilt angle for different roof types")
    print(f"  Flachdach: {calculate_tilt_angle('Flachdach', 0.0)}°")
    print(
        f"  Satteldach (35° pitch): "
        f"{calculate_tilt_angle('Satteldach', 35.0)}°"
    )
    print(f"  Pultdach (25° pitch): {calculate_tilt_angle('Pultdach', 25.0)}°")
    print(f"  Walmdach (40° pitch): {calculate_tilt_angle('Walmdach', 40.0)}°")
    print()

    print("Test 3: Validate roof-type-specific logic")
    roof_types = ["Flachdach", "Satteldach", "Pultdach", "Walmdach"]
    roof_pitches = [0.0, 35.0, 25.0, 40.0]
    
    for roof_type, pitch in zip(roof_types, roof_pitches):
        z_pos = calculate_z_position(roof_type, pitch, 10.0)
        tilt = calculate_tilt_angle(roof_type, pitch)
        print(f"  {roof_type} (pitch={pitch}°):")
        print(f"    Z-position: {z_pos}m")
        print(f"    Tilt angle: {tilt}°")
    print()

    print("Test 4: Validate input handling")
    # These tests would need to be run in a Streamlit context
    print("  (Requires Streamlit session state - run in app context)")
    print()

    print("=== Tests completed ===")
    print("\nNote: Full testing requires Streamlit session state.")
    print("Run this module within a Streamlit app for complete testing.")
