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
    print("Roof-type-specific logic not available, using generic placement")


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
                f"Modul überschreitet linke Dachkante "
                f"(Modul-Kante: {module_left:.2f}m < Dachkante: {roof_left:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_right > roof_right:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"Modul überschreitet rechte Dachkante "
                f"(Modul-Kante: {module_right:.2f}m > Dachkante: {roof_right:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_bottom < roof_bottom:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"Modul überschreitet untere Dachkante "
                f"(Modul-Kante: {module_bottom:.2f}m < Dachkante: {roof_bottom:.2f}m)"
            ),
            "colliding_index": None
        }

    if module_top > roof_top:
        return {
            "collision": True,
            "type": "boundary",
            "message": (
                f"Modul überschreitet obere Dachkante "
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
                    f"Modul überlappt mit bestehendem Modul #{idx + 1} "
                    f"(Abstand: X={dx:.2f}m, Y={dy:.2f}m)"
                ),
                "colliding_index": idx
            }

    # No collision detected
    return {
        "collision": False,
        "type": "none",
        "message": "Keine Kollision erkannt",
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
            print(f"Module quantity limited to {MAX_MODULES} for performance")
            module_quantity = MAX_MODULES
        # Requirement 11.1: Validate roof dimensions (> 0)
        if roof_length <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "Fehler: Dachlänge muss größer als 0 sein "
                    f"(aktuell: {roof_length:.2f}m)"
                )
            }
        
        if roof_width <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "Fehler: Dachbreite muss größer als 0 sein "
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
                    "Fehler: Modulanzahl muss größer als 0 sein "
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
                    "Fehler: Dach-Dimensionen unrealistisch groß "
                    f"(Länge: {roof_length:.2f}m, Breite: {roof_width:.2f}m)"
                )
            }
        
        if module_quantity > 1000:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "Fehler: Modulanzahl zu groß "
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
                            "Keine Module konnten platziert werden. "
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
                        f"{actual_count} Module platziert "
                        f"(gewünscht: {module_quantity}). "
                        "Nicht genug Platz für alle Module."
                    )
                else:
                    message = f"{actual_count} Module erfolgreich platziert!"

                return {
                    "success": True,
                    "positions": positions_3d,
                    "count": actual_count,
                    "message": message
                }
                
            except Exception as roof_error:
                print(f"Fehler bei dachtyp-spezifischer Logik: {roof_error}")
                print("   Fallback zu generischer Grid-Berechnung")
                # Fall through to generic logic below
        
        # TASK 13: Check cache first for performance
        # Requirement 10.5: Caching von berechneten Positionen
        cache_key = _get_cache_key(
            roof_length, roof_width, module_quantity,
            spacing, margin, orientation
        )
        
        if cache_key in _position_cache:
            print(f"Using cached positions for {module_quantity} modules")
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
                print(f"Cached positions for {module_quantity} modules")
                
            except Exception as grid_error:
                # Requirement 11.4: Meaningful error messages
                return {
                    "success": False,
                    "positions": [],
                    "count": 0,
                    "message": (
                        f"Fehler bei der Grid-Berechnung: {str(grid_error)}"
                    )
                }

        if not grid_positions_2d:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "Keine Module konnten platziert werden. "
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
            
            # PHASE 1 - TASK 1.2: Update handle_auto_placement() to use new calculate_z_position()
            # Requirement 1.1-1.6: Berechne Z-Position individuell für jedes Modul
            
            # Für ALLE Dachtypen: Berechne Z-Position individuell pro Modul
            # Die neue calculate_z_position() Funktion behandelt alle Fälle intern
            for x, y in grid_positions_2d:
                # Übergebe Y-Position an calculate_z_position()
                z = calculate_z_position(
                    roof_type=roof_type,
                    roof_pitch=roof_pitch,
                    roof_width=roof_width,
                    y_position=y  # NEU: Y-Position für geneigte Dächer
                )
                positions_3d.append((float(x), float(y), float(z)))
            
            # Logging für Debug-Zwecke
            if positions_3d:
                z_values = [z for _, _, z in positions_3d]
                z_min = min(z_values)
                z_max = max(z_values)
                
                if roof_type_normalized == "flachdach":
                    print(f"   Flachdach: Z-Position = {z_min:.2f}m (konstant)")
                elif z_min == z_max:
                    print(f"   {roof_type}: Z-Position = {z_min:.2f}m (konstant, keine Neigung)")
                else:
                    print(f"   {roof_type}: Z-Position variiert von {z_min:.2f}m bis {z_max:.2f}m")
                
        except (TypeError, ValueError, Exception) as conv_error:
            # Requirement 11.4: Meaningful error messages
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    f"Fehler bei der Positions-Berechnung: "
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
                f"{actual_count} Module platziert "
                f"(gewünscht: {module_quantity}). "
                "Nicht genug Platz für alle Module."
            )
        else:
            message = f"{actual_count} Module erfolgreich platziert!"

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
            f"Unerwarteter Fehler bei der automatischen Platzierung: "
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
            "message": "Alle Module wurden zurückgesetzt"
        }

    except Exception as e:
        # Requirement 11.2: Error handling
        error_message = f"Fehler beim Zurücksetzen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "message": error_message
        }


def calculate_z_position(
    roof_type: str, 
    roof_pitch: float = 0.0, 
    roof_width: float = 10.0,
    y_position: float = 0.0  # NEU: Y-Position des Moduls für geneigte Dächer
) -> float:
    """
    Calculate Z-position (height) for modules based on roof type and Y-position.

    PHASE 1 - TASK 1.1: CRITICAL BUGFIX - Korrekte Modulplatzierung auf geneigten Dächern
    
    Diese Funktion wurde erweitert um den y_position Parameter, damit Module auf
    geneigten Dächern (Satteldach, Walmdach, Pultdach, Zeltdach) korrekt auf der
    Dachfläche platziert werden, anstatt wie auf Flachdächern behandelt zu werden.

    Different roof types require different mounting heights:
    - Flat roofs: Modules are mounted on elevated frames (Aufständerung) at 30cm (constant)
    - Pitched roofs: Modules follow the roof surface, Z varies based on Y-position

    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_pitch: Roof pitch angle in degrees
        roof_width: Width of the roof in meters (Y-axis)
        y_position: Y-position of the module center (NEW - required for pitched roofs)

    Returns:
        Z-position in meters above the wall height (relative to roof base)
        This is a RELATIVE position that will be added to wall_height_m

    Requirements:
        - Requirement 1.1: Module auf Satteldach direkt auf geneigte Dachflächen platzieren
        - Requirement 1.2: Module auf Walmdach parallel zur Dachfläche ausrichten
        - Requirement 1.3: Module auf Pultdach mit Dachneigung ausrichten
        - Requirement 1.4: Module auf Flachdach mit Aufständerung platzieren
        - Requirement 1.5: Z-Position basierend auf Dachgeometrie und Y-Position berechnen
        - Requirement 1.6: Korrekte Neigung entsprechend Dachtyp anwenden
    
    Mathematical Formula for Pitched Roofs:
        z = base_z + (y_offset * tan(roof_pitch))
        
        Where:
        - base_z = 0.15m (clearance above roof base / Traufhöhe)
        - y_offset = distance from eave (lower roof edge)
        - roof_pitch = roof inclination angle in degrees
    """
    import math
    
    # Normalize roof type string (case-insensitive, strip whitespace)
    roof_type_normalized = roof_type.strip().lower() if roof_type else "flachdach"

    # Requirement 1.4: Flat roof with elevated mounting (constant height)
    if "flach" in roof_type_normalized:
        # Flachdach: Module werden auf Aufständerung montiert
        # 30cm Höhe für Montagegestell (ermöglicht 30° Neigung)
        # Z-Position ist KONSTANT für alle Module
        return 0.30  # 30cm elevation for mounting frame (Aufständerung)

    # Requirement 1.1: Satteldach - Z steigt vom Rand zur Mitte (First)
    elif roof_type_normalized in ["satteldach", "satteldach mit gaube"]:
        base_z = 0.15  # 15cm clearance above roof base (Traufhöhe)
        
        if roof_pitch > 0:
            # Berechne Abstand von Traufe (untere Dachkante bei y = -roof_width/2)
            dist_from_eave = y_position + roof_width / 2
            
            # Berechne Z-Offset basierend auf Dachneigung
            inclination_rad = math.radians(roof_pitch)
            z_offset = dist_from_eave * math.tan(inclination_rad)
            
            return base_z + z_offset
        else:
            # Keine Neigung (sollte nicht vorkommen, aber Fallback)
            return base_z

    # Requirement 1.3: Pultdach - Z steigt linear von vorne nach hinten
    elif roof_type_normalized == "pultdach":
        base_z = 0.15  # 15cm clearance above roof base
        
        if roof_pitch > 0:
            # Berechne Abstand von vorderer Kante (y = -roof_width/2)
            dist_from_front = y_position + roof_width / 2
            
            # Berechne Z-Offset basierend auf Dachneigung
            inclination_rad = math.radians(roof_pitch)
            z_offset = dist_from_front * math.tan(inclination_rad)
            
            return base_z + z_offset
        else:
            return base_z

    # Requirement 1.2: Walmdach/Krüppelwalmdach - Ähnlich wie Satteldach
    elif roof_type_normalized in ["walmdach", "krüppelwalmdach"]:
        base_z = 0.15  # 15cm clearance above roof base
        
        if roof_pitch > 0:
            # Berechne Abstand von Traufe
            dist_from_eave = y_position + roof_width / 2
            
            # Berechne Z-Offset basierend auf Dachneigung
            inclination_rad = math.radians(roof_pitch)
            z_offset = dist_from_eave * math.tan(inclination_rad)
            
            return base_z + z_offset
        else:
            return base_z

    # Requirement 1.5: Zeltdach - Z steigt vom Rand zur Mitte (pyramidenförmig)
    elif roof_type_normalized == "zeltdach":
        base_z = 0.15  # 15cm clearance above roof base
        
        if roof_pitch > 0:
            # Minimaler Abstand von allen 4 Kanten
            # Für Zeltdach steigt die Höhe pyramidenförmig zur Mitte
            dist_from_edge = min(
                y_position + roof_width / 2,   # Abstand von vorderer Kante
                roof_width / 2 - y_position    # Abstand von hinterer Kante
            )
            
            # Berechne Z-Offset basierend auf Dachneigung
            inclination_rad = math.radians(roof_pitch)
            z_offset = dist_from_edge * math.tan(inclination_rad)
            
            return base_z + z_offset
        else:
            return base_z

    # Fallback für andere/unbekannte Dachtypen: Konstante Höhe
    else:
        # Geneigte Dächer (unbekannter Typ): Verwende Basis-Höhe
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

        # PHASE 1 - TASK 1.3: Update handle_manual_add() to use new calculate_z_position()
        # Requirement 1.5: Calculate Z-position based on roof geometry and Y-position
        z = calculate_z_position(
            roof_type=roof_type,
            roof_pitch=roof_pitch,
            roof_width=roof_width,
            y_position=y  # NEU: Übergebe Y-Position für geneigte Dächer
        )

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
                f"Modul hinzugefügt an Position "
                f"({x:.2f}, {y:.2f}, {z:.2f})"
            )
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"Fehler beim Hinzufügen: {str(e)}"
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
                "message": "Keine Module zum Entfernen vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module zum Entfernen vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module ausgewählt"
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
            "message": f"{removed_count} Module entfernt"
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"Fehler beim Entfernen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "count": 0,
            "message": error_message
        }


# ============================================================================
# TASK 7.2: SNAP-TO-GRID (MAGNET-FUNKTION)
# ============================================================================

def snap_to_grid(
    x: float,
    y: float,
    grid_spacing: float = 0.5
) -> Tuple[float, float]:
    """
    Richtet Position am Raster aus (Magnet-Funktion).
    
    TASK 7.2: Snap-to-Grid
    - Rundet Koordinaten auf nächstes Raster-Vielfaches
    - Konfigurierbare Raster-Größe (0.1m - 1.0m)
    - Hilft bei präziser Modulplatzierung
    
    Args:
        x: Ursprüngliche X-Position in Metern
        y: Ursprüngliche Y-Position in Metern
        grid_spacing: Raster-Abstand in Metern (default: 0.5m)
    
    Returns:
        Tuple (x_snapped, y_snapped): An Raster ausgerichtete Position
    
    Requirements:
        - 5.2: Magnet-Funktion für automatische Raster-Ausrichtung
    
    Examples:
        >>> snap_to_grid(1.23, 2.67, grid_spacing=0.5)
        (1.0, 2.5)
        
        >>> snap_to_grid(1.23, 2.67, grid_spacing=0.1)
        (1.2, 2.7)
        
        >>> snap_to_grid(1.23, 2.67, grid_spacing=1.0)
        (1.0, 3.0)
    """
    # Runde auf nächstes Vielfaches von grid_spacing
    x_snapped = round(x / grid_spacing) * grid_spacing
    y_snapped = round(y / grid_spacing) * grid_spacing
    
    return x_snapped, y_snapped


def handle_manual_move_with_snap(
    module_index: int,
    new_x: float,
    new_y: float,
    roof_type: str,
    roof_pitch: float,
    roof_width: float,
    roof_length: float,
    enable_snap: bool = True,
    grid_spacing: float = 0.5,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Verschiebt Modul mit optionaler Raster-Ausrichtung.
    
    TASK 7.2: Snap-to-Grid
    - Verschiebt Modul zu neuer Position
    - Optional: Richtet Position am Raster aus
    - Prüft Kollisionen an neuer Position
    - Aktualisiert Session State
    
    Args:
        module_index: Index des zu verschiebenden Moduls
        new_x: Neue X-Position
        new_y: Neue Y-Position
        roof_type: Dachtyp
        roof_pitch: Dachneigung in Grad
        roof_width: Dachbreite in Metern
        roof_length: Dachlänge in Metern
        enable_snap: Snap-to-Grid aktivieren? (default: True)
        grid_spacing: Raster-Größe in Metern (default: 0.5m)
        orientation: Modul-Orientierung
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Verschiebung erfolgreich war
            - message: str - Status oder Fehlermeldung
            - old_position: Tuple - Alte Position
            - new_position: Tuple - Neue Position
    
    Requirements:
        - 5.2: Snap-to-Grid Funktionalität
        - 7.1-7.4: Kollisionserkennung
        - 9.1-9.2: Session State Management
    """
    try:
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        
        # Validiere Index
        if module_index < 0 or module_index >= len(positions):
            return {
                "success": False,
                "message": f"Ungültiger Modul-Index: {module_index}",
                "old_position": None,
                "new_position": None
            }
        
        # Speichere alte Position
        old_position = positions[module_index]
        
        # Snap-to-Grid wenn aktiviert
        if enable_snap:
            new_x, new_y = snap_to_grid(new_x, new_y, grid_spacing)
        
        # Berechne neue Z-Position basierend auf Dachtyp
        new_z = calculate_z_position(
            roof_type=roof_type,
            roof_pitch=roof_pitch,
            roof_width=roof_width,
            y_position=new_y
        )
        
        new_position = (new_x, new_y, new_z)
        
        # Prüfe Kollision (ohne das zu verschiebende Modul)
        other_positions = [pos for i, pos in enumerate(positions) if i != module_index]
        
        collision_result = check_module_collision(
            new_position=new_position,
            existing_positions=other_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            orientation=orientation
        )
        
        # Verhindere Verschiebung bei Kollision
        if collision_result["collision"]:
            return {
                "success": False,
                "message": f"Kollision erkannt: {collision_result['message']}",
                "old_position": old_position,
                "new_position": new_position
            }
        
        # Verschiebe Modul
        positions[module_index] = new_position
        st.session_state["placed_module_positions"] = positions
        
        # Erstelle Erfolgsmeldung
        snap_info = " (am Raster ausgerichtet)" if enable_snap else ""
        message = (
            f"Modul #{module_index + 1} verschoben{snap_info}\n"
            f"Von: ({old_position[0]:.2f}, {old_position[1]:.2f}, {old_position[2]:.2f})\n"
            f"Nach: ({new_x:.2f}, {new_y:.2f}, {new_z:.2f})"
        )
        
        return {
            "success": True,
            "message": message,
            "old_position": old_position,
            "new_position": new_position
        }
        
    except Exception as e:
        error_message = f"Fehler beim Verschieben: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "old_position": None,
            "new_position": None
        }


# ============================================================================
# TASK 7.3: KOPIEREN & EINFÜGEN (COPY & PASTE)
# ============================================================================

def copy_module_group(
    module_indices: List[int]
) -> Dict[str, Any]:
    """
    Kopiert ausgewählte Module in Zwischenablage.
    
    TASK 7.3: Copy & Paste
    - Kopiert Modul-Positionen in Session State
    - Ermöglicht Duplizierung von Modul-Gruppen
    - Speichert relative Positionen für präzises Einfügen
    
    Args:
        module_indices: Liste der zu kopierenden Modul-Indizes
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Kopieren erfolgreich war
            - message: str - Status oder Fehlermeldung
            - clipboard_data: List - Kopierte Modul-Daten
            - count: int - Anzahl kopierter Module
    
    Requirements:
        - 5.3: Kopieren & Einfügen von Modulen
        - 9.1-9.2: Session State Management
    
    Example:
        >>> result = copy_module_group([0, 1, 2])
        >>> print(result["message"])
        "3 Module kopiert"
    """
    try:
        # Validiere Eingabe
        if not module_indices:
            return {
                "success": False,
                "message": "Keine Module ausgewählt",
                "clipboard_data": [],
                "count": 0
            }
        
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        
        if not positions:
            return {
                "success": False,
                "message": "Keine Module zum Kopieren vorhanden",
                "clipboard_data": [],
                "count": 0
            }
        
        # Kopiere Modul-Daten
        clipboard = []
        for idx in module_indices:
            if 0 <= idx < len(positions):
                x, y, z = positions[idx]
                clipboard.append({
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "original_index": idx
                })
        
        if not clipboard:
            return {
                "success": False,
                "message": "Keine gültigen Module zum Kopieren",
                "clipboard_data": [],
                "count": 0
            }
        
        # Speichere in Session State
        st.session_state["module_clipboard"] = clipboard
        
        return {
            "success": True,
            "message": f"{len(clipboard)} Module kopiert",
            "clipboard_data": clipboard,
            "count": len(clipboard)
        }
        
    except Exception as e:
        error_message = f"Fehler beim Kopieren: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "clipboard_data": [],
            "count": 0
        }


def paste_module_group(
    offset_x: float = 1.0,
    offset_y: float = 1.0,
    roof_type: str = "Flachdach",
    roof_pitch: float = 0.0,
    roof_width: float = 10.0,
    roof_length: float = 10.0,
    orientation: str = "portrait",
    check_collisions: bool = True
) -> Dict[str, Any]:
    """
    Fügt kopierte Module mit Offset ein.
    
    TASK 7.3: Copy & Paste
    - Fügt Module aus Zwischenablage ein
    - Wendet X/Y-Offset an
    - Berechnet neue Z-Positionen basierend auf Dachtyp
    - Optional: Kollisionsprüfung
    
    Args:
        offset_x: X-Offset in Metern (default: 1.0m)
        offset_y: Y-Offset in Metern (default: 1.0m)
        roof_type: Dachtyp
        roof_pitch: Dachneigung in Grad
        roof_width: Dachbreite in Metern
        roof_length: Dachlänge in Metern
        orientation: Modul-Orientierung
        check_collisions: Kollisionsprüfung aktivieren? (default: True)
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Einfügen erfolgreich war
            - message: str - Status oder Fehlermeldung
            - pasted_positions: List - Eingefügte Positionen
            - pasted_count: int - Anzahl eingefügter Module
            - skipped_count: int - Anzahl übersprungener Module (Kollision)
    
    Requirements:
        - 5.3: Kopieren & Einfügen von Modulen
        - 7.1-7.4: Kollisionserkennung
        - 9.1-9.2: Session State Management
    
    Example:
        >>> result = paste_module_group(offset_x=2.0, offset_y=1.0)
        >>> print(result["message"])
        "3 Module eingefügt"
    """
    try:
        # Hole Zwischenablage
        clipboard = st.session_state.get("module_clipboard", [])
        
        if not clipboard:
            return {
                "success": False,
                "message": "Zwischenablage leer - zuerst Module kopieren",
                "pasted_positions": [],
                "pasted_count": 0,
                "skipped_count": 0
            }
        
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        new_positions = []
        skipped_count = 0
        
        # Füge jedes Modul mit Offset ein
        for module_data in clipboard:
            # Berechne neue Position
            new_x = module_data["x"] + offset_x
            new_y = module_data["y"] + offset_y
            
            # Berechne neue Z-Position basierend auf Dachtyp
            new_z = calculate_z_position(
                roof_type=roof_type,
                roof_pitch=roof_pitch,
                roof_width=roof_width,
                y_position=new_y
            )
            
            new_position = (new_x, new_y, new_z)
            
            # Optional: Prüfe Kollision
            if check_collisions:
                collision_result = check_module_collision(
                    new_position=new_position,
                    existing_positions=positions + new_positions,
                    roof_length=roof_length,
                    roof_width=roof_width,
                    orientation=orientation
                )
                
                if collision_result["collision"]:
                    skipped_count += 1
                    print(f"Modul übersprungen (Kollision): {collision_result['message']}")
                    continue
            
            # Füge Modul hinzu
            new_positions.append(new_position)
        
        if not new_positions:
            return {
                "success": False,
                "message": (
                    f"Keine Module eingefügt - "
                    f"{skipped_count} Module übersprungen (Kollision)"
                ),
                "pasted_positions": [],
                "pasted_count": 0,
                "skipped_count": skipped_count
            }
        
        # Update Session State
        positions.extend(new_positions)
        st.session_state["placed_module_positions"] = positions
        st.session_state["placed_module_count"] = len(positions)
        
        # Erstelle Erfolgsmeldung
        message = f"{len(new_positions)} Module eingefügt"
        if skipped_count > 0:
            message += f" ({skipped_count} übersprungen wegen Kollision)"
        
        return {
            "success": True,
            "message": message,
            "pasted_positions": new_positions,
            "pasted_count": len(new_positions),
            "skipped_count": skipped_count
        }
        
    except Exception as e:
        error_message = f"Fehler beim Einfügen: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "pasted_positions": [],
            "pasted_count": 0,
            "skipped_count": 0
        }


# ============================================================================
# TASK 7.4: VORSCHAU BEI VERSCHIEBEN (MOVE PREVIEW)
# ============================================================================

def create_move_preview(
    module_index: int,
    new_x: float,
    new_y: float,
    roof_type: str,
    roof_pitch: float,
    roof_width: float,
    roof_length: float,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Erstellt Vorschau für Modul-Verschiebung.
    
    TASK 7.4: Move Preview
    - Zeigt Vorschau der neuen Position
    - Prüft Kollisionen in Echtzeit
    - Gibt visuelles Feedback (grün = OK, rot = Kollision)
    
    Args:
        module_index: Index des zu verschiebenden Moduls
        new_x: Neue X-Position
        new_y: Neue Y-Position
        roof_type: Dachtyp
        roof_pitch: Dachneigung in Grad
        roof_width: Dachbreite in Metern
        roof_length: Dachlänge in Metern
        orientation: Modul-Orientierung
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Vorschau erstellt wurde
            - preview_position: Tuple - Vorschau-Position (x, y, z)
            - has_collision: bool - Ob Kollision erkannt wurde
            - collision_type: str - Art der Kollision ("none", "module", "boundary")
            - collision_message: str - Kollisions-Beschreibung
            - color: str - Farbe für Vorschau ("green", "red")
    
    Requirements:
        - 5.4: Vorschau bei Verschieben
        - 7.1-7.4: Kollisionserkennung
    
    Example:
        >>> preview = create_move_preview(0, 1.5, 2.0, "Flachdach", 0, 10, 10)
        >>> if preview["has_collision"]:
        >>>     print(f"Warnung: {preview['collision_message']}")
    """
    try:
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        
        # Validiere Index
        if module_index < 0 or module_index >= len(positions):
            return {
                "success": False,
                "preview_position": None,
                "has_collision": False,
                "collision_type": "none",
                "collision_message": f"Ungültiger Modul-Index: {module_index}",
                "color": "red"
            }
        
        # Berechne neue Z-Position
        new_z = calculate_z_position(
            roof_type=roof_type,
            roof_pitch=roof_pitch,
            roof_width=roof_width,
            y_position=new_y
        )
        
        preview_position = (new_x, new_y, new_z)
        
        # Prüfe Kollision (ohne das zu verschiebende Modul)
        other_positions = [pos for i, pos in enumerate(positions) if i != module_index]
        
        collision_result = check_module_collision(
            new_position=preview_position,
            existing_positions=other_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            orientation=orientation
        )
        
        # Bestimme Farbe basierend auf Kollision
        color = "red" if collision_result["collision"] else "green"
        
        return {
            "success": True,
            "preview_position": preview_position,
            "has_collision": collision_result["collision"],
            "collision_type": collision_result["type"],
            "collision_message": collision_result["message"],
            "color": color
        }
        
    except Exception as e:
        error_message = f"Fehler bei Vorschau-Erstellung: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "preview_position": None,
            "has_collision": False,
            "collision_type": "none",
            "collision_message": error_message,
            "color": "red"
        }


# ============================================================================
# TASK 7.5: TASTATUR-SHORTCUTS (KEYBOARD SHORTCUTS)
# ============================================================================

def handle_keyboard_move(
    module_index: int,
    direction: str,
    step_size: float,
    roof_type: str,
    roof_pitch: float,
    roof_width: float,
    roof_length: float,
    orientation: str = "portrait"
) -> Dict[str, Any]:
    """
    Verschiebt Modul per Tastatur-Shortcut.
    
    TASK 7.5: Keyboard Shortcuts
    - Pfeiltasten: Verschieben in 4 Richtungen
    - Konfigurierbare Schrittweite (0.1m oder 0.5m)
    - Kollisionserkennung
    
    Args:
        module_index: Index des zu verschiebenden Moduls
        direction: Richtung ("up", "down", "left", "right")
        step_size: Schrittweite in Metern (0.1 oder 0.5)
        roof_type: Dachtyp
        roof_pitch: Dachneigung in Grad
        roof_width: Dachbreite in Metern
        roof_length: Dachlänge in Metern
        orientation: Modul-Orientierung
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Verschiebung erfolgreich war
            - message: str - Status oder Fehlermeldung
            - old_position: Tuple - Alte Position
            - new_position: Tuple - Neue Position
            - direction: str - Verwendete Richtung
            - step_size: float - Verwendete Schrittweite
    
    Requirements:
        - 5.5: Tastatur-Shortcuts
        - 7.1-7.4: Kollisionserkennung
        - 9.1-9.2: Session State Management
    
    Example:
        >>> # Pfeiltaste nach rechts (0.5m)
        >>> result = handle_keyboard_move(0, "right", 0.5, "Flachdach", 0, 10, 10)
        >>> # Shift + Pfeiltaste nach rechts (0.1m)
        >>> result = handle_keyboard_move(0, "right", 0.1, "Flachdach", 0, 10, 10)
    """
    try:
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        
        # Validiere Index
        if module_index < 0 or module_index >= len(positions):
            return {
                "success": False,
                "message": f"Ungültiger Modul-Index: {module_index}",
                "old_position": None,
                "new_position": None,
                "direction": direction,
                "step_size": step_size
            }
        
        # Speichere alte Position
        old_position = positions[module_index]
        old_x, old_y, old_z = old_position
        
        # Berechne neue Position basierend auf Richtung
        new_x, new_y = old_x, old_y
        
        if direction == "up":
            new_y += step_size  # Nach hinten (Y+)
        elif direction == "down":
            new_y -= step_size  # Nach vorne (Y-)
        elif direction == "left":
            new_x -= step_size  # Nach links (X-)
        elif direction == "right":
            new_x += step_size  # Nach rechts (X+)
        else:
            return {
                "success": False,
                "message": f"Ungültige Richtung: {direction}",
                "old_position": old_position,
                "new_position": None,
                "direction": direction,
                "step_size": step_size
            }
        
        # Berechne neue Z-Position
        new_z = calculate_z_position(
            roof_type=roof_type,
            roof_pitch=roof_pitch,
            roof_width=roof_width,
            y_position=new_y
        )
        
        new_position = (new_x, new_y, new_z)
        
        # Prüfe Kollision (ohne das zu verschiebende Modul)
        other_positions = [pos for i, pos in enumerate(positions) if i != module_index]
        
        collision_result = check_module_collision(
            new_position=new_position,
            existing_positions=other_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            orientation=orientation
        )
        
        # Verhindere Verschiebung bei Kollision
        if collision_result["collision"]:
            return {
                "success": False,
                "message": f"Kollision erkannt: {collision_result['message']}",
                "old_position": old_position,
                "new_position": new_position,
                "direction": direction,
                "step_size": step_size
            }
        
        # Verschiebe Modul
        positions[module_index] = new_position
        st.session_state["placed_module_positions"] = positions
        
        # Erstelle Erfolgsmeldung
        direction_text = {
            "up": "nach hinten",
            "down": "nach vorne",
            "left": "nach links",
            "right": "nach rechts"
        }.get(direction, direction)
        
        message = (
            f"Modul #{module_index + 1} {direction_text} verschoben ({step_size}m)\n"
            f"Von: ({old_x:.2f}, {old_y:.2f}, {old_z:.2f})\n"
            f"Nach: ({new_x:.2f}, {new_y:.2f}, {new_z:.2f})"
        )
        
        return {
            "success": True,
            "message": message,
            "old_position": old_position,
            "new_position": new_position,
            "direction": direction,
            "step_size": step_size
        }
        
    except Exception as e:
        error_message = f"Fehler beim Tastatur-Verschieben: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "old_position": None,
            "new_position": None,
            "direction": direction,
            "step_size": step_size
        }


def handle_keyboard_rotate(
    module_index: int
) -> Dict[str, Any]:
    """
    Rotiert Modul um 90° per Tastatur-Shortcut (R-Taste).
    
    TASK 7.5: Keyboard Shortcuts
    - Rotiert zwischen "portrait" und "landscape"
    - Speichert Orientierung in Session State
    
    Args:
        module_index: Index des zu rotierenden Moduls
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Rotation erfolgreich war
            - message: str - Status oder Fehlermeldung
            - old_orientation: str - Alte Orientierung
            - new_orientation: str - Neue Orientierung
    
    Requirements:
        - 5.5: Tastatur-Shortcuts (R-Taste)
        - 9.1-9.2: Session State Management
    
    Example:
        >>> result = handle_keyboard_rotate(0)
        >>> print(result["message"])
        "Modul #1 rotiert: portrait → landscape"
    """
    try:
        # Hole aktuelle Orientierungen (falls vorhanden)
        orientations = st.session_state.get("module_orientations", [])
        positions = st.session_state.get("placed_module_positions", [])
        
        # Validiere Index
        if module_index < 0 or module_index >= len(positions):
            return {
                "success": False,
                "message": f"Ungültiger Modul-Index: {module_index}",
                "old_orientation": None,
                "new_orientation": None
            }
        
        # Initialisiere Orientierungen falls nötig
        if not orientations or len(orientations) != len(positions):
            orientations = ["portrait"] * len(positions)
            st.session_state["module_orientations"] = orientations
        
        # Hole alte Orientierung
        old_orientation = orientations[module_index]
        
        # Rotiere: portrait ↔ landscape
        new_orientation = "landscape" if old_orientation == "portrait" else "portrait"
        
        # Speichere neue Orientierung
        orientations[module_index] = new_orientation
        st.session_state["module_orientations"] = orientations
        
        message = f"Modul #{module_index + 1} rotiert: {old_orientation} → {new_orientation}"
        
        return {
            "success": True,
            "message": message,
            "old_orientation": old_orientation,
            "new_orientation": new_orientation
        }
        
    except Exception as e:
        error_message = f"Fehler beim Rotieren: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "old_orientation": None,
            "new_orientation": None
        }


def handle_keyboard_delete(
    module_indices: List[int]
) -> Dict[str, Any]:
    """
    Löscht Module per Tastatur-Shortcut (Delete-Taste).
    
    TASK 7.5: Keyboard Shortcuts
    - Löscht ausgewählte Module
    - Aktualisiert Session State
    
    Args:
        module_indices: Liste der zu löschenden Modul-Indizes
    
    Returns:
        Dictionary mit:
            - success: bool - Ob Löschen erfolgreich war
            - message: str - Status oder Fehlermeldung
            - deleted_count: int - Anzahl gelöschter Module
            - remaining_count: int - Verbleibende Module
    
    Requirements:
        - 5.5: Tastatur-Shortcuts (Delete-Taste)
        - 9.1-9.2: Session State Management
    
    Example:
        >>> result = handle_keyboard_delete([0, 2, 4])
        >>> print(result["message"])
        "3 Module gelöscht (5 verbleibend)"
    """
    try:
        # Validiere Eingabe
        if not module_indices:
            return {
                "success": False,
                "message": "Keine Module ausgewählt",
                "deleted_count": 0,
                "remaining_count": 0
            }
        
        # Hole aktuelle Positionen
        positions = st.session_state.get("placed_module_positions", [])
        
        if not positions:
            return {
                "success": False,
                "message": "Keine Module zum Löschen vorhanden",
                "deleted_count": 0,
                "remaining_count": 0
            }
        
        # Sortiere Indizes absteigend (von hinten löschen)
        sorted_indices = sorted(set(module_indices), reverse=True)
        
        # Validiere alle Indizes
        invalid_indices = [idx for idx in sorted_indices if idx < 0 or idx >= len(positions)]
        if invalid_indices:
            return {
                "success": False,
                "message": f"Ungültige Indizes: {invalid_indices}",
                "deleted_count": 0,
                "remaining_count": len(positions)
            }
        
        # Lösche Module (von hinten nach vorne)
        deleted_count = 0
        for idx in sorted_indices:
            del positions[idx]
            deleted_count += 1
        
        # Aktualisiere Session State
        st.session_state["placed_module_positions"] = positions
        st.session_state["placed_module_count"] = len(positions)
        
        # Lösche auch Orientierungen falls vorhanden
        if "module_orientations" in st.session_state:
            orientations = st.session_state["module_orientations"]
            for idx in sorted_indices:
                if idx < len(orientations):
                    del orientations[idx]
            st.session_state["module_orientations"] = orientations
        
        # Lösche Auswahl
        if "selected_module_indices" in st.session_state:
            st.session_state["selected_module_indices"] = []
        
        message = f"{deleted_count} Module gelöscht ({len(positions)} verbleibend)"
        
        return {
            "success": True,
            "message": message,
            "deleted_count": deleted_count,
            "remaining_count": len(positions)
        }
        
    except Exception as e:
        error_message = f"Fehler beim Löschen: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": error_message,
            "deleted_count": 0,
            "remaining_count": 0
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
                "message": "Keine Module zum Verschieben vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module zum Verschieben vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module ausgewählt"
            }

        # Validate offset values
        if abs(offset_x) < 0.01 and abs(offset_y) < 0.01:
            return {
                "success": False,
                "count": 0,
                "message": "Offset zu klein (mindestens 0.01m erforderlich)"
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
                
                # PHASE 1 - TASK 1.2: Use new calculate_z_position() with y_position
                # Requirement 1.5: Calculate Z-position based on roof geometry and Y-position
                new_z = calculate_z_position(
                    roof_type=roof_type,
                    roof_pitch=roof_pitch,
                    roof_width=roof_width,
                    y_position=new_y  # NEU: Übergebe neue Y-Position
                )

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
                            f"Verschieben nicht möglich: "
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
                    f"{moved_count} Module verschoben "
                    f"(Δx={offset_x:+.2f}m, Δy={offset_y:+.2f}m)"
                )
            }

    except Exception as e:
        error_message = f"Fehler beim Verschieben: {str(e)}"
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
                "message": "Keine Module zum Drehen vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module zum Drehen vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "Keine Module ausgewählt"
            }

        # Validate rotation angle
        if abs(rotation_degrees) < 1.0:
            return {
                "success": False,
                "count": 0,
                "message": "Rotationswinkel zu klein (mindestens 1° erforderlich)"
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
                "message": "Keine gültigen Module ausgewählt"
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
                f"{rotated_count} Module gedreht "
                f"({rotation_degrees:+.1f}° um Zentrum)"
            )
        }

    except Exception as e:
        error_message = f"Fehler beim Drehen: {str(e)}"
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
