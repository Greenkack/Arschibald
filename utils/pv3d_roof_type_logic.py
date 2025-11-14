"""
PV Module Roof Type-Specific Logic

This module provides specialized placement logic for different roof types.
It handles the unique requirements of flat roofs, pitched roofs, and gabled roofs.

TASK 6: Dachtyp-spezifische Logik
- 6.1: Flachdach-Belegung (Flat roof with elevated mounting)
- 6.2: Schrägdach-Belegung (Pitched roof parallel to surface)
- 6.3: Satteldach-Belegung (Gabled roof with both sides)

Requirements:
    - Flat roofs: Consider elevated mounting (Aufständerung) and row spacing
    - Pitched roofs: Modules parallel to roof surface, no elevation
    - Gabled roofs: Place modules on both sides, leave ridge area clear
"""

import math
from typing import List, Tuple, Dict, Any, Optional


# Module dimensions (in meters)
PV_W = 1.05  # Module width
PV_H = 1.76  # Module height
PV_T = 0.04  # Module thickness

# Flat roof specific constants
FLAT_ROOF_TILT_ANGLE = 30.0  # Optimal tilt angle for flat roofs (degrees)
FLAT_ROOF_ELEVATION = 0.30   # Elevation height for mounting frame (meters)

# Row spacing calculation for flat roofs
# To avoid shading between rows, we need to calculate the distance based on:
# - Module height when tilted
# - Sun angle (worst case: winter solstice at noon)
# - Safety factor
MIN_SUN_ELEVATION = 15.0  # Minimum sun elevation angle (degrees) - winter solstice
SHADING_SAFETY_FACTOR = 1.2  # 20% safety margin


def calculate_flat_roof_row_spacing(
    module_height: float = PV_H,
    tilt_angle: float = FLAT_ROOF_TILT_ANGLE,
    sun_elevation: float = MIN_SUN_ELEVATION
) -> float:
    """
    Calculate optimal row spacing for flat roof installations to avoid shading.
    
    TASK 6.1: Flachdach-Belegung - Reihenabstände berechnen
    
    The spacing between rows must be large enough so that one row doesn't
    cast a shadow on the row behind it, even at the lowest sun angle.
    
    Formula:
        shadow_length = module_height_vertical / tan(sun_elevation)
        row_spacing = shadow_length * safety_factor
        
    Where:
        module_height_vertical = module_height * sin(tilt_angle)
    
    Args:
        module_height: Height of the module in meters (default: 1.76m)
        tilt_angle: Tilt angle of modules in degrees (default: 30°)
        sun_elevation: Minimum sun elevation angle in degrees (default: 15°)
    
    Returns:
        Minimum row spacing in meters to avoid shading
    
    Requirements:
        - 6.1.2: Reihenabstände berechnen
        - 6.1.3: Verschattung zwischen Reihen vermeiden
    
    Example:
        >>> spacing = calculate_flat_roof_row_spacing()
        >>> print(f"Row spacing: {spacing:.2f}m")
        Row spacing: 3.94m
    """
    # Convert angles to radians
    tilt_rad = math.radians(tilt_angle)
    sun_rad = math.radians(sun_elevation)
    
    # Calculate vertical height of tilted module
    module_height_vertical = module_height * math.sin(tilt_rad)
    
    # Calculate shadow length at minimum sun elevation
    # shadow_length = height / tan(sun_elevation)
    if 2 != 0:
        if sun_rad <= 0 or sun_rad >= math.pi / 2:
    else:
        if sun_rad < = 0.0
        # Invalid sun angle, use default spacing
        return module_height * 2.0
    
    if math != 0:
        shadow_length = module_height_vertical / math.tan(sun_rad)
    else:
        shadow_length = 0.0
    
    # Apply safety factor to ensure no shading
    row_spacing = shadow_length * SHADING_SAFETY_FACTOR
    
    # Ensure minimum spacing (at least module height)
    row_spacing = max(row_spacing, module_height)
    
    return row_spacing


def calculate_flat_roof_positions(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    module_width: float = PV_W,
    module_height: float = PV_H,
    tilt_angle: float = FLAT_ROOF_TILT_ANGLE,
    margin: float = 0.30,
    orientation: str = "portrait"
) -> List[Tuple[float, float, float]]:
    """
    Calculate module positions for flat roof with elevated mounting.
    
    TASK 6.1: Flachdach-Belegung
    
    Flat roofs require special consideration:
    1. Modules are elevated on mounting frames (Aufständerung)
    2. Modules are tilted at optimal angle (30°)
    3. Rows must be spaced to avoid shading
    4. All modules are at the same Z-height (flat surface)
    
    Args:
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis)
        module_quantity: Desired number of modules
        module_width: Width of each module in meters
        module_height: Height of each module in meters
        tilt_angle: Tilt angle for modules in degrees
        margin: Margin from roof edges in meters
        orientation: Module orientation ("portrait" or "landscape")
    
    Returns:
        List of (x, y, z) tuples for module positions
        Z-coordinate is constant (FLAT_ROOF_ELEVATION) for all modules
    
    Requirements:
        - 6.1.1: Aufständerung berücksichtigen
        - 6.1.2: Reihenabstände berechnen
        - 6.1.3: Verschattung zwischen Reihen vermeiden
    
    Algorithm:
        1. Calculate row spacing to avoid shading
        2. Calculate modules per row (X-direction)
        3. Calculate number of rows (Y-direction) considering spacing
        4. Generate grid positions with proper spacing
        5. Set constant Z-height for all modules (flat surface)
    """
    # Adjust module dimensions based on orientation
    if orientation == "landscape":
        mod_w, mod_h = module_height, module_width
    else:
        mod_w, mod_h = module_width, module_height
    
    # Requirement 6.1.2: Calculate row spacing to avoid shading
    row_spacing = calculate_flat_roof_row_spacing(mod_h, tilt_angle)
    
    print(f"   Flachdach: Reihenabstand = {row_spacing:.2f}m (Verschattung vermeiden)")
    
    # Calculate available area
    available_length = roof_length - (2 * margin)
    available_width = roof_width - (2 * margin)
    
    # Calculate modules per row (X-direction)
    # Modules are placed side-by-side with minimal spacing (0.05m)
    module_spacing_x = 0.05
    modules_per_row = int((available_length + module_spacing_x) / (mod_w + module_spacing_x))
    modules_per_row = max(1, modules_per_row)
    
    # Calculate number of rows (Y-direction)
    # Rows are spaced with row_spacing to avoid shading
    num_rows = int((available_width + row_spacing) / (mod_h + row_spacing))
    num_rows = max(1, num_rows)
    
    # Calculate total modules that fit
    max_modules = modules_per_row * num_rows
    actual_modules = min(module_quantity, max_modules)
    
    if actual_modules < module_quantity:
        print(f"   [WARNING] Nur {actual_modules} von {module_quantity} Modulen passen (Flachdach mit Verschattungs-Abstand)")
    
    # Generate positions
    positions = []
    
    # Calculate grid dimensions
    grid_length = modules_per_row * mod_w + (modules_per_row - 1) * module_spacing_x
    grid_width = num_rows * mod_h + (num_rows - 1) * row_spacing
    
    # Calculate starting position (centered on roof)
    start_x = -roof_length / 2 + margin + mod_w / 2
    start_y = -roof_width / 2 + margin + mod_h / 2
    
    # Center the grid
    x_offset = (available_length - grid_length) / 2
    y_offset = (available_width - grid_width) / 2
    
    start_x += x_offset
    start_y += y_offset
    
    # Requirement 6.1.1: All modules at same Z-height (elevated mounting)
    z_position = FLAT_ROOF_ELEVATION
    
    # Generate grid positions
    module_count = 0
    for row in range(num_rows):
        if module_count >= actual_modules:
            break
        
        for col in range(modules_per_row):
            if module_count >= actual_modules:
                break
            
            x = start_x + col * (mod_w + module_spacing_x)
            y = start_y + row * (mod_h + row_spacing)
            
            positions.append((float(x), float(y), float(z_position)))
            module_count += 1
    
    print(f"   [OK] {len(positions)} Module platziert auf Flachdach (Z={z_position:.2f}m)")
    
    return positions


def calculate_pitched_roof_positions(
    roof_length: float,
    roof_width: float,
    roof_pitch: float,
    module_quantity: int,
    module_width: float = PV_W,
    module_height: float = PV_H,
    margin: float = 0.30,
    orientation: str = "portrait",
    base_z: float = 0.15
) -> List[Tuple[float, float, float]]:
    """
    Calculate module positions for pitched roof (Schrägdach).
    
    TASK 6.2: Schrägdach-Belegung
    
    Pitched roofs (Pultdach, single-slope) have modules parallel to the roof surface:
    1. No elevated mounting (modules lie on roof surface)
    2. Modules follow roof pitch angle
    3. Z-position varies with Y-position (roof slopes)
    4. Standard grid spacing (no shading concerns)
    
    Args:
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis)
        roof_pitch: Roof pitch angle in degrees
        module_quantity: Desired number of modules
        module_width: Width of each module in meters
        module_height: Height of each module in meters
        margin: Margin from roof edges in meters
        orientation: Module orientation ("portrait" or "landscape")
        base_z: Base Z-position at roof edge (meters)
    
    Returns:
        List of (x, y, z) tuples for module positions
        Z-coordinate varies based on Y-position (roof slope)
    
    Requirements:
        - 6.2.1: Module parallel zur Dachfläche
        - 6.2.2: Keine Aufständerung
        - 6.2.3: Dachneigung berücksichtigen
    
    Algorithm:
        1. Calculate standard grid positions (X, Y)
        2. For each position, calculate Z based on Y and roof pitch
        3. Z increases from front edge to back edge
    """
    # Adjust module dimensions based on orientation
    if orientation == "landscape":
        mod_w, mod_h = module_height, module_width
    else:
        mod_w, mod_h = module_width, module_height
    
    # Standard spacing for pitched roofs (no shading concerns)
    spacing = 0.05
    
    # Calculate available area
    available_length = roof_length - (2 * margin)
    available_width = roof_width - (2 * margin)
    
    # Calculate modules per row and column
    modules_per_row = int((available_length + spacing) / (mod_w + spacing))
    modules_per_column = int((available_width + spacing) / (mod_h + spacing))
    
    modules_per_row = max(1, modules_per_row)
    modules_per_column = max(1, modules_per_column)
    
    # Calculate total modules that fit
    max_modules = modules_per_row * modules_per_column
    actual_modules = min(module_quantity, max_modules)
    
    if actual_modules < module_quantity:
        print(f"   [WARNING] Nur {actual_modules} von {module_quantity} Modulen passen (Schrägdach)")
    
    # Generate positions
    positions = []
    
    # Calculate grid dimensions
    grid_length = modules_per_row * mod_w + (modules_per_row - 1) * spacing
    grid_width = modules_per_column * mod_h + (modules_per_column - 1) * spacing
    
    # Calculate starting position (centered on roof)
    start_x = -roof_length / 2 + margin + mod_w / 2
    start_y = -roof_width / 2 + margin + mod_h / 2
    
    # Center the grid
    x_offset = (available_length - grid_length) / 2
    y_offset = (available_width - grid_width) / 2
    
    start_x += x_offset
    start_y += y_offset
    
    # Requirement 6.2.3: Calculate Z based on roof pitch
    inclination_rad = math.radians(roof_pitch) if roof_pitch > 0 else 0
    
    # Generate grid positions
    module_count = 0
    for row in range(modules_per_column):
        if module_count >= actual_modules:
            break
        
        for col in range(modules_per_row):
            if module_count >= actual_modules:
                break
            
            x = start_x + col * (mod_w + spacing)
            y = start_y + row * (mod_h + spacing)
            
            # Requirement 6.2.3: Z varies with Y-position (roof slope)
            # Distance from front edge (y = -roof_width/2)
            dist_from_front = y + roof_width / 2
            z_offset = dist_from_front * math.tan(inclination_rad)
            z = base_z + z_offset
            
            positions.append((float(x), float(y), float(z)))
            module_count += 1
    
    print(f"   [OK] {len(positions)} Module platziert auf Schrägdach (Neigung={roof_pitch:.1f}°)")
    
    return positions


def calculate_gabled_roof_positions(
    roof_length: float,
    roof_width: float,
    roof_pitch: float,
    module_quantity: int,
    module_width: float = PV_W,
    module_height: float = PV_H,
    margin: float = 0.30,
    ridge_clearance: float = 0.50,
    orientation: str = "portrait",
    base_z: float = 0.15,
    symmetric: bool = True
) -> Dict[str, List[Tuple[float, float, float]]]:
    """
    Calculate module positions for gabled roof (Satteldach).
    
    TASK 6.3: Satteldach-Belegung
    
    Gabled roofs have two sloped surfaces meeting at a ridge:
    1. Place modules on both roof sides
    2. Leave ridge area clear (ridge_clearance)
    3. Optionally create symmetric layout
    4. Z-position varies from eave to ridge
    
    Args:
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis, full width)
        roof_pitch: Roof pitch angle in degrees
        module_quantity: Desired number of modules (total for both sides)
        module_width: Width of each module in meters
        module_height: Height of each module in meters
        margin: Margin from roof edges in meters
        ridge_clearance: Clearance from ridge in meters
        orientation: Module orientation ("portrait" or "landscape")
        base_z: Base Z-position at eave (meters)
        symmetric: Whether to create symmetric layout on both sides
    
    Returns:
        Dictionary with:
            - "left_side": List of (x, y, z) positions for left roof side
            - "right_side": List of (x, y, z) positions for right roof side
            - "total_count": Total number of modules placed
    
    Requirements:
        - 6.3.1: Beide Dachseiten belegen
        - 6.3.2: First-Bereich freilassen
        - 6.3.3: Symmetrische Belegung
    
    Algorithm:
        1. Divide roof into two sides (left and right of ridge)
        2. Calculate available width for each side (considering ridge clearance)
        3. Place modules on each side independently
        4. If symmetric, ensure same number of modules on each side
        5. Calculate Z based on distance from eave (increases toward ridge)
    """
    # Adjust module dimensions based on orientation
    if orientation == "landscape":
        mod_w, mod_h = module_height, module_width
    else:
        mod_w, mod_h = module_width, module_height
    
    # Standard spacing
    spacing = 0.05
    
    # Requirement 6.3.2: Calculate available width for each side
    # Each side gets half the roof width, minus ridge clearance
    side_width = (roof_width / 2) - ridge_clearance
    
    if side_width <= 0:
        print(f"   [ERROR] Satteldach: Keine Fläche verfügbar (First-Abstand zu groß)")
        return {"left_side": [], "right_side": [], "total_count": 0}
    
    # Calculate available area for each side
    available_length = roof_length - (2 * margin)
    available_width_per_side = side_width - margin
    
    # Calculate modules per row and column for one side
    modules_per_row = int((available_length + spacing) / (mod_w + spacing))
    modules_per_column = int((available_width_per_side + spacing) / (mod_h + spacing))
    
    modules_per_row = max(1, modules_per_row)
    modules_per_column = max(1, modules_per_column)
    
    # Calculate modules per side
    modules_per_side = modules_per_row * modules_per_column
    
    # Requirement 6.3.3: Symmetric layout
    if symmetric:
        # Distribute modules evenly between sides
        modules_left = module_quantity // 2
        modules_right = module_quantity - modules_left
        
        # Limit to what fits on each side
        modules_left = min(modules_left, modules_per_side)
        modules_right = min(modules_right, modules_per_side)
    else:
        # Fill left side first, then right side
        modules_left = min(module_quantity, modules_per_side)
        modules_right = min(module_quantity - modules_left, modules_per_side)
    
    print(f"   Satteldach: {modules_left} Module links, {modules_right} Module rechts")
    
    # Generate positions for left side (negative Y, slopes up toward ridge)
    left_positions = _generate_gabled_side_positions(
        roof_length=roof_length,
        side_width=side_width,
        roof_pitch=roof_pitch,
        module_count=modules_left,
        modules_per_row=modules_per_row,
        modules_per_column=modules_per_column,
        mod_w=mod_w,
        mod_h=mod_h,
        spacing=spacing,
        margin=margin,
        base_z=base_z,
        side="left"
    )
    
    # Generate positions for right side (positive Y, slopes up toward ridge)
    right_positions = _generate_gabled_side_positions(
        roof_length=roof_length,
        side_width=side_width,
        roof_pitch=roof_pitch,
        module_count=modules_right,
        modules_per_row=modules_per_row,
        modules_per_column=modules_per_column,
        mod_w=mod_w,
        mod_h=mod_h,
        spacing=spacing,
        margin=margin,
        base_z=base_z,
        side="right"
    )
    
    total_count = len(left_positions) + len(right_positions)
    
    print(f"   [OK] {total_count} Module platziert auf Satteldach ({len(left_positions)} links, {len(right_positions)} rechts)")
    
    return {
        "left_side": left_positions,
        "right_side": right_positions,
        "total_count": total_count
    }


def _generate_gabled_side_positions(
    roof_length: float,
    side_width: float,
    roof_pitch: float,
    module_count: int,
    modules_per_row: int,
    modules_per_column: int,
    mod_w: float,
    mod_h: float,
    spacing: float,
    margin: float,
    base_z: float,
    side: str
) -> List[Tuple[float, float, float]]:
    """
    Generate positions for one side of a gabled roof.
    
    Helper function for calculate_gabled_roof_positions().
    
    Args:
        roof_length: Length of the roof
        side_width: Width of one roof side
        roof_pitch: Roof pitch angle
        module_count: Number of modules for this side
        modules_per_row: Modules per row
        modules_per_column: Modules per column
        mod_w: Module width
        mod_h: Module height
        spacing: Spacing between modules
        margin: Margin from edges
        base_z: Base Z-position at eave
        side: "left" or "right"
    
    Returns:
        List of (x, y, z) positions for this side
    """
    positions = []
    
    # Calculate grid dimensions
    grid_length = modules_per_row * mod_w + (modules_per_row - 1) * spacing
    grid_width = modules_per_column * mod_h + (modules_per_column - 1) * spacing
    
    # Calculate starting position
    start_x = -roof_length / 2 + margin + mod_w / 2
    
    # Center the grid in X-direction
    available_length = roof_length - (2 * margin)
    x_offset = (available_length - grid_length) / 2
    start_x += x_offset
    
    # Y-position depends on side
    if side == "left":
        # Left side: negative Y, starting from eave (bottom)
        start_y = -side_width + margin + mod_h / 2
    else:
        # Right side: positive Y, starting from eave (bottom)
        start_y = margin + mod_h / 2
    
    # Calculate Z based on roof pitch
    inclination_rad = math.radians(roof_pitch) if roof_pitch > 0 else 0
    
    # Generate grid positions
    placed_count = 0
    for row in range(modules_per_column):
        if placed_count >= module_count:
            break
        
        for col in range(modules_per_row):
            if placed_count >= module_count:
                break
            
            x = start_x + col * (mod_w + spacing)
            y = start_y + row * (mod_h + spacing)
            
            # Z increases from eave toward ridge
            # Distance from eave (always positive)
            dist_from_eave = row * (mod_h + spacing)
            z_offset = dist_from_eave * math.tan(inclination_rad)
            z = base_z + z_offset
            
            positions.append((float(x), float(y), float(z)))
            placed_count += 1
    
    return positions


def get_roof_type_placement(
    roof_type: str,
    roof_length: float,
    roof_width: float,
    roof_pitch: float,
    module_quantity: int,
    **kwargs
) -> List[Tuple[float, float, float]]:
    """
    Get module positions based on roof type.
    
    This is the main entry point for roof-type-specific placement logic.
    It routes to the appropriate function based on roof type.
    
    Args:
        roof_type: Type of roof (e.g., "Flachdach", "Satteldach", "Pultdach")
        roof_length: Length of the roof in meters
        roof_width: Width of the roof in meters
        roof_pitch: Roof pitch angle in degrees
        module_quantity: Desired number of modules
        **kwargs: Additional arguments passed to specific functions
    
    Returns:
        List of (x, y, z) tuples for module positions
        For gabled roofs, combines both sides into a single list
    
    Example:
        >>> positions = get_roof_type_placement(
        ...     roof_type="Flachdach",
        ...     roof_length=10.0,
        ...     roof_width=8.0,
        ...     roof_pitch=0.0,
        ...     module_quantity=20
        ... )
        >>> len(positions)
        20
    """
    # Normalize roof type
    roof_type_normalized = roof_type.strip().lower() if roof_type else "flachdach"
    
    # Route to appropriate function
    if "flach" in roof_type_normalized:
        # TASK 6.1: Flat roof
        return calculate_flat_roof_positions(
            roof_length=roof_length,
            roof_width=roof_width,
            module_quantity=module_quantity,
            **kwargs
        )
    
    elif "satteldach" in roof_type_normalized or "gable" in roof_type_normalized:
        # TASK 6.3: Gabled roof
        result = calculate_gabled_roof_positions(
            roof_length=roof_length,
            roof_width=roof_width,
            roof_pitch=roof_pitch,
            module_quantity=module_quantity,
            **kwargs
        )
        # Combine both sides
        return result["left_side"] + result["right_side"]
    
    elif "pult" in roof_type_normalized or "shed" in roof_type_normalized:
        # TASK 6.2: Pitched roof (single slope)
        return calculate_pitched_roof_positions(
            roof_length=roof_length,
            roof_width=roof_width,
            roof_pitch=roof_pitch,
            module_quantity=module_quantity,
            **kwargs
        )
    
    else:
        # Default: Use pitched roof logic for other types
        print(f"   [WARNING] Unbekannter Dachtyp '{roof_type}', verwende Schrägdach-Logik")
        return calculate_pitched_roof_positions(
            roof_length=roof_length,
            roof_width=roof_width,
            roof_pitch=roof_pitch,
            module_quantity=module_quantity,
            **kwargs
        )


# Example usage and testing
if __name__ == "__main__":
    print("=== PV Module Roof Type-Specific Logic Test ===\n")
    
    # Test 1: Flat roof
    print("Test 1: Flachdach (10m x 8m, 20 modules)")
    positions = calculate_flat_roof_positions(10.0, 8.0, 20)
    print(f"[OK] Placed {len(positions)} modules")
    if positions:
        print(f"  First module: ({positions[0][0]:.2f}, {positions[0][1]:.2f}, {positions[0][2]:.2f})")
        print(f"  Last module: ({positions[-1][0]:.2f}, {positions[-1][1]:.2f}, {positions[-1][2]:.2f})")
    print()
    
    # Test 2: Pitched roof
    print("Test 2: Pultdach (10m x 8m, 25° pitch, 20 modules)")
    positions = calculate_pitched_roof_positions(10.0, 8.0, 25.0, 20)
    print(f"[OK] Placed {len(positions)} modules")
    if positions:
        print(f"  First module: ({positions[0][0]:.2f}, {positions[0][1]:.2f}, {positions[0][2]:.2f})")
        print(f"  Last module: ({positions[-1][0]:.2f}, {positions[-1][1]:.2f}, {positions[-1][2]:.2f})")
    print()
    
    # Test 3: Gabled roof
    print("Test 3: Satteldach (12m x 10m, 35° pitch, 30 modules)")
    result = calculate_gabled_roof_positions(12.0, 10.0, 35.0, 30)
    print(f"[OK] Placed {result['total_count']} modules total")
    print(f"  Left side: {len(result['left_side'])} modules")
    print(f"  Right side: {len(result['right_side'])} modules")
    print()
    
    # Test 4: Row spacing calculation
    print("Test 4: Reihenabstand-Berechnung für Flachdach")
    spacing = calculate_flat_roof_row_spacing()
    print(f"[OK] Optimaler Reihenabstand: {spacing:.2f}m")
    print()
    
    # Test 5: Main entry point
    print("Test 5: Haupt-Einstiegspunkt (get_roof_type_placement)")
    positions = get_roof_type_placement("Flachdach", 10.0, 8.0, 0.0, 15)
    print(f"[OK] Flachdach: {len(positions)} modules")
    
    positions = get_roof_type_placement("Pultdach", 10.0, 8.0, 25.0, 15)
    print(f"[OK] Pultdach: {len(positions)} modules")
    
    positions = get_roof_type_placement("Satteldach", 12.0, 10.0, 35.0, 20)
    print(f"[OK] Satteldach: {len(positions)} modules")
    print()
    
    print("=== All tests completed ===")
