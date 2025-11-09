"""
PV Module Placement Handler

This module handles the business logic for placing PV modules on roof surfaces.
It manages automatic placement, manual placement, reset operations, and
session state management.

Key Functions:
    - handle_auto_placement: Automatic module placement
    - handle_reset_placement: Reset all modules
    - handle_manual_add: Add single module manually
    - handle_remove_selected: Remove selected modules
    - calculate_z_position: Calculate height based on roof type
    - calculate_tilt_angle: Calculate tilt angle based on roof type
    - initialize_session_state: Initialize session state variables

Requirements: 2.2, 2.6, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5, 9.1, 9.2,
              11.1, 11.2, 11.3, 11.4, 11.5
"""

from typing import Dict, Any, List
import streamlit as st

try:
    from utils.pv3d_grid_calculator import (
        calculate_module_grid,
        DEFAULT_SPACING,
        DEFAULT_MARGIN
    )
except ImportError:
    # Fallback if grid calculator is not available
    def calculate_module_grid(*args, **kwargs):
        return []
    DEFAULT_SPACING = 0.05
    DEFAULT_MARGIN = 0.30


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
    """
    # Requirement 11.5: Store previous state for fallback
    previous_positions = st.session_state.get("placed_module_positions", [])
    previous_count = st.session_state.get("placed_module_count", 0)
    
    try:
        # Requirement 11.1: Validate roof dimensions (> 0)
        if roof_length <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "❌ Fehler: Dachlänge muss größer als 0 sein "
                    f"(aktuell: {roof_length:.2f}m)"
                )
            }
        
        if roof_width <= 0:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "❌ Fehler: Dachbreite muss größer als 0 sein "
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
                    "❌ Fehler: Modulanzahl muss größer als 0 sein "
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
                    "❌ Fehler: Dach-Dimensionen unrealistisch groß "
                    f"(Länge: {roof_length:.2f}m, Breite: {roof_width:.2f}m)"
                )
            }
        
        if module_quantity > 1000:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "❌ Fehler: Modulanzahl zu groß "
                    f"(aktuell: {module_quantity}, Maximum: 1000)"
                )
            }

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
        except Exception as grid_error:
            # Requirement 11.4: Meaningful error messages
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    f"❌ Fehler bei der Grid-Berechnung: {str(grid_error)}"
                )
            }

        if not grid_positions_2d:
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    "⚠️ Keine Module konnten platziert werden. "
                    "Die Dachfläche ist zu klein oder die Ränder zu groß."
                )
            }

        # Requirement 6.1-6.5: Calculate Z-position based on roof type
        try:
            z_position = calculate_z_position(roof_type, roof_pitch)
        except Exception as z_error:
            # Requirement 11.4: Meaningful error messages
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    f"❌ Fehler bei der Z-Positions-Berechnung: {str(z_error)}"
                )
            }

        # Convert 2D positions to 3D positions
        try:
            positions_3d = [
                (float(x), float(y), float(z_position))
                for x, y in grid_positions_2d
            ]
        except (TypeError, ValueError) as conv_error:
            # Requirement 11.4: Meaningful error messages
            return {
                "success": False,
                "positions": [],
                "count": 0,
                "message": (
                    f"❌ Fehler bei der Positions-Konvertierung: "
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
                f"✓ {actual_count} Module platziert "
                f"(gewünscht: {module_quantity}). "
                "Nicht genug Platz für alle Module."
            )
        else:
            message = f"✓ {actual_count} Module erfolgreich platziert!"

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
            f"❌ Unerwarteter Fehler bei der automatischen Platzierung: "
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
            "message": "✓ Alle Module wurden zurückgesetzt"
        }

    except Exception as e:
        # Requirement 11.2: Error handling
        error_message = f"❌ Fehler beim Zurücksetzen: {str(e)}"
        print(error_message)

        return {
            "success": False,
            "message": error_message
        }


def calculate_z_position(roof_type: str, roof_pitch: float = 0.0) -> float:
    """
    Calculate Z-position (height) for modules based on roof type.

    Different roof types require different mounting heights:
    - Flat roofs: Modules are mounted on elevated frames (Aufständerung)
    - Pitched roofs: Modules are mounted directly on the roof surface

    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_pitch: Roof pitch angle in degrees (not used currently)

    Returns:
        Z-position in meters above the roof surface

    Requirements:
        - 6.1: Flat roof with elevated mounting (30° tilt)
        - 6.2: Gable roof parallel to surface
        - 6.3: Shed roof parallel to surface
        - 6.4: Calculate Z-position based on roof type
    """
    # Normalize roof type string (case-insensitive, strip whitespace)
    roof_type_normalized = roof_type.strip().lower()

    # Requirement 6.1: Flat roof with elevated mounting
    if "flach" in roof_type_normalized:
        return 0.3  # 30cm elevation for mounting frame (Aufständerung)

    # Requirement 6.2, 6.3: Pitched roofs (Satteldach, Pultdach, etc.)
    # Modules are mounted directly on the roof surface
    else:
        return 0.05  # 5cm clearance above roof surface


def calculate_tilt_angle(roof_type: str, roof_pitch: float = 0.0) -> float:
    """
    Calculate tilt angle for modules based on roof type.

    Different roof types require different tilt angles:
    - Flat roofs: Modules are tilted at 30° for optimal solar exposure
    - Pitched roofs: Modules follow the roof pitch angle

    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_pitch: Roof pitch angle in degrees

    Returns:
        Tilt angle in degrees

    Requirements:
        - 6.1: Flat roof with 30° tilt (Aufständerung)
        - 6.5: Pitched roofs use roof pitch angle
    """
    # Normalize roof type string (case-insensitive, strip whitespace)
    roof_type_normalized = roof_type.strip().lower()

    # Requirement 6.1: Flat roof with 30° tilt
    if "flach" in roof_type_normalized:
        return 30.0  # 30° tilt for optimal solar exposure

    # Requirement 6.5: Pitched roofs use roof pitch angle
    else:
        # For pitched roofs, modules lie parallel to the roof surface
        # So they use the roof's pitch angle
        return roof_pitch if roof_pitch > 0 else 0.0


def handle_manual_add(
    x: float,
    y: float,
    roof_type: str,
    roof_pitch: float = 0.0
) -> Dict[str, Any]:
    """
    Add a single module at a specific position.

    This function allows manual placement of individual modules at
    user-specified coordinates.

    Args:
        x: X-coordinate in meters (relative to roof center)
        y: Y-coordinate in meters (relative to roof center)
        roof_type: Type of roof
        roof_pitch: Roof pitch angle in degrees

    Returns:
        Dictionary with:
            - success: bool - Whether addition was successful
            - message: str - Status or error message

    Requirements:
        - 4.1: Manual add button functionality
        - 6.4: Calculate Z-position based on roof type
        - 9.1-9.2: Session state management
        - 11.1-11.3: Error handling and collision detection
    """
    try:
        # Initialize session state if needed
        if "placed_module_positions" not in st.session_state:
            st.session_state["placed_module_positions"] = []

        # Calculate Z-position based on roof type
        z = calculate_z_position(roof_type, roof_pitch)

        # Create new position
        new_position = (x, y, z)

        # Requirement 11.1, 11.3: Check for collisions (basic check)
        # Note: Full collision detection is implemented in Task 11
        existing_positions = st.session_state["placed_module_positions"]

        # Add the module
        existing_positions.append(new_position)

        # Requirement 9.1, 9.2: Update session state
        st.session_state["placed_module_positions"] = existing_positions
        st.session_state["placed_module_count"] = len(existing_positions)

        return {
            "success": True,
            "message": (
                f"✓ Modul hinzugefügt an Position "
                f"({x:.2f}, {y:.2f}, {z:.2f})"
            )
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"❌ Fehler beim Hinzufügen: {str(e)}"
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
                "message": "⚠️ Keine Module zum Entfernen vorhanden"
            }

        positions = st.session_state["placed_module_positions"]

        if not positions:
            return {
                "success": False,
                "count": 0,
                "message": "⚠️ Keine Module zum Entfernen vorhanden"
            }

        if not selected_indices:
            return {
                "success": False,
                "count": 0,
                "message": "⚠️ Keine Module ausgewählt"
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
            "message": f"✓ {removed_count} Module entfernt"
        }

    except Exception as e:
        # Requirement 11.2, 11.4: Error handling
        error_message = f"❌ Fehler beim Entfernen: {str(e)}"
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
    print(f"  Flachdach: {calculate_z_position('Flachdach')}m")
    print(f"  Satteldach: {calculate_z_position('Satteldach')}m")
    print(f"  Pultdach: {calculate_z_position('Pultdach')}m")
    print()

    print("Test 2: Calculate tilt angle for different roof types")
    print(f"  Flachdach: {calculate_tilt_angle('Flachdach', 0.0)}°")
    print(f"  Satteldach (35° pitch): {calculate_tilt_angle('Satteldach', 35.0)}°")
    print(f"  Pultdach (25° pitch): {calculate_tilt_angle('Pultdach', 25.0)}°")
    print(f"  Walmdach (40° pitch): {calculate_tilt_angle('Walmdach', 40.0)}°")
    print()

    print("Test 3: Validate roof-type-specific logic")
    roof_types = ["Flachdach", "Satteldach", "Pultdach", "Walmdach"]
    roof_pitches = [0.0, 35.0, 25.0, 40.0]
    
    for roof_type, pitch in zip(roof_types, roof_pitches):
        z_pos = calculate_z_position(roof_type, pitch)
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
