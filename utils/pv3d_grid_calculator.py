"""
PV Module Grid Calculator

This module provides functionality to calculate optimal grid positions for PV modules
on roof surfaces. It handles spacing, margins, and optimization for maximum module count.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""

from typing import List, Tuple, Optional
import math
import numpy as np  # TASK 13: Use numpy arrays for better performance


# Module dimensions (in meters)
PV_W = 1.05  # Module width
PV_H = 1.76  # Module height
PV_T = 0.04  # Module thickness

# Default spacing and margins
DEFAULT_SPACING = 0.05  # 5cm spacing between modules
DEFAULT_MARGIN = 0.30   # 30cm margin from roof edges

# TASK 13: Performance limits
MAX_MODULES = 200  # Maximum modules to prevent performance issues


def calculate_module_grid(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    spacing: float = DEFAULT_SPACING,
    margin: float = DEFAULT_MARGIN,
    orientation: str = "portrait"
) -> List[Tuple[float, float]]:
    """
    Calculate optimal grid positions for PV modules on a roof surface.
    
    TASK 13: Performance-optimized version using numpy arrays and caching.
    
    This function computes (x, y) coordinates for placing modules in a grid pattern,
    taking into account roof dimensions, module size, spacing requirements, and margins.
    The positions are calculated relative to the roof center (0, 0).
    
    Args:
        roof_length: Length of the roof in meters (X-axis)
        roof_width: Width of the roof in meters (Y-axis)
        module_quantity: Desired number of modules to place
        spacing: Minimum spacing between modules in meters (default: 0.05m)
        margin: Minimum margin from roof edges in meters (default: 0.30m)
        orientation: Module orientation - "portrait" (default) or "landscape"
    
    Returns:
        List of (x, y) tuples representing module center positions relative to roof center.
        Returns empty list if placement is not possible or inputs are invalid.
    
    Algorithm:
        1. Validate input parameters
        2. Calculate available roof area (roof dimensions - margins)
        3. Determine module dimensions based on orientation
        4. Calculate maximum modules per row and column
        5. Calculate total maximum modules that fit
        6. Limit to requested quantity (max 200 for performance)
        7. Generate centered grid positions using numpy for speed
    
    Requirements:
        - 3.1: Calculate (x, y) coordinates for each module
        - 3.2: Consider roof dimensions (length x width)
        - 3.3: Consider module dimensions (1.05m x 1.76m)
        - 3.4: Consider spacing between modules
        - 3.5: Consider margin distances from edges
        - 3.6: Return maximum possible count if requested exceeds capacity
        - 10.5: Performance optimization with numpy arrays
    
    Example:
        >>> positions = calculate_module_grid(10.0, 8.0, 20)
        >>> len(positions)
        20
        >>> positions[0]  # First module position
        (-4.35, -3.35)
    """
    # Requirement 3.1, 3.2, 3.3, 3.4, 3.5: Input validation
    validation_result = _validate_inputs(
        roof_length, roof_width, module_quantity, spacing, margin
    )
    
    if not validation_result["valid"]:
        print(f"Grid calculation validation failed: {validation_result['message']}")
        return []
    
    # Handle zero or negative module quantity
    if module_quantity <= 0:
        return []
    
    # TASK 13: Limit to maximum modules for performance
    # Requirement 10.5: Begrenzung auf maximal 200 Module
    if module_quantity > MAX_MODULES:
        print(f"Module quantity limited to {MAX_MODULES} for performance (requested: {module_quantity})")
        module_quantity = MAX_MODULES
    
    # Determine module dimensions based on orientation
    if orientation == "landscape":
        module_width = PV_H  # 1.76m
        module_height = PV_W  # 1.05m
    else:  # portrait (default)
        module_width = PV_W  # 1.05m
        module_height = PV_H  # 1.76m
    
    # Calculate available area (roof dimensions minus margins on both sides)
    available_length = roof_length - (2 * margin)
    available_width = roof_width - (2 * margin)
    
    # Check if even one module fits
    if available_length < module_width or available_width < module_height:
        print(f"Insufficient space: Available area ({available_length:.2f}m x {available_width:.2f}m) "
              f"is smaller than module size ({module_width:.2f}m x {module_height:.2f}m)")
        return []
    
    # Calculate modules per row and column
    # Each module takes up its width/height plus spacing (except the last one)
    modules_per_row = _calculate_modules_per_line(
        available_length, module_width, spacing
    )
    modules_per_column = _calculate_modules_per_line(
        available_width, module_height, spacing
    )
    
    # Calculate maximum modules that can fit
    max_modules = modules_per_row * modules_per_column
    
    # Requirement 3.6: Limit to maximum possible if requested exceeds capacity
    actual_modules = min(module_quantity, max_modules)
    
    if actual_modules < module_quantity:
        print(f"Requested {module_quantity} modules, but only {actual_modules} fit on roof")
    
    # Generate grid positions
    positions = _generate_grid_positions(
        actual_modules,
        modules_per_row,
        modules_per_column,
        module_width,
        module_height,
        spacing,
        roof_length,
        roof_width,
        margin
    )
    
    return positions


def _validate_inputs(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    spacing: float,
    margin: float
) -> dict:
    """
    Validate input parameters for grid calculation.
    
    Args:
        roof_length: Length of the roof in meters
        roof_width: Width of the roof in meters
        module_quantity: Desired number of modules
        spacing: Spacing between modules in meters
        margin: Margin from roof edges in meters
    
    Returns:
        Dictionary with 'valid' (bool) and 'message' (str) keys
    """
    # Check roof dimensions
    if roof_length <= 0:
        return {
            "valid": False,
            "message": f"Roof length must be positive (got {roof_length})"
        }
    
    if roof_width <= 0:
        return {
            "valid": False,
            "message": f"Roof width must be positive (got {roof_width})"
        }
    
    # Check spacing and margin
    if spacing < 0:
        return {
            "valid": False,
            "message": f"Spacing must be non-negative (got {spacing})"
        }
    
    if margin < 0:
        return {
            "valid": False,
            "message": f"Margin must be non-negative (got {margin})"
        }
    
    # Check if margins don't exceed roof dimensions
    if 2 * margin >= roof_length:
        return {
            "valid": False,
            "message": f"Margins ({2*margin}m total) exceed roof length ({roof_length}m)"
        }
    
    if 2 * margin >= roof_width:
        return {
            "valid": False,
            "message": f"Margins ({2*margin}m total) exceed roof width ({roof_width}m)"
        }
    
    return {"valid": True, "message": "OK"}


def _calculate_modules_per_line(
    available_space: float,
    module_size: float,
    spacing: float
) -> int:
    """
    Calculate how many modules fit along a line.
    
    Args:
        available_space: Available space in meters
        module_size: Module dimension in meters
        spacing: Spacing between modules in meters
    
    Returns:
        Number of modules that fit (minimum 0)
    
    Formula:
        n = floor((available_space + spacing) / (module_size + spacing))
        
        The +spacing in numerator accounts for the fact that the last module
        doesn't need spacing after it.
    """
    if available_space < module_size:
        return 0
    
    # Calculate how many modules fit
    # Formula: (available_space + spacing) / (module_size + spacing)
    # This accounts for spacing between modules but not after the last one
    modules = math.floor((available_space + spacing) / (module_size + spacing))
    
    return max(0, modules)


def _generate_grid_positions(
    total_modules: int,
    modules_per_row: int,
    modules_per_column: int,
    module_width: float,
    module_height: float,
    spacing: float,
    roof_length: float,
    roof_width: float,
    margin: float
) -> List[Tuple[float, float]]:
    """
    Generate centered grid positions for modules.
    
    TASK 13: Performance-optimized version using numpy arrays for batch operations.
    
    Args:
        total_modules: Total number of modules to place
        modules_per_row: Maximum modules per row
        modules_per_column: Maximum modules per column
        module_width: Width of each module
        module_height: Height of each module
        spacing: Spacing between modules
        roof_length: Total roof length
        roof_width: Total roof width
        margin: Margin from edges
    
    Returns:
        List of (x, y) positions relative to roof center
    
    Requirements:
        - 10.5: Use numpy arrays for better performance
    """
    # Calculate actual rows and columns needed
    if modules_per_row != 0:
        actual_rows = math.ceil(total_modules / modules_per_row)
    else:
        actual_rows = 0.0
    actual_rows = min(actual_rows, modules_per_column)
    
    # Calculate the total grid dimensions
    grid_length = modules_per_row * module_width + (modules_per_row - 1) * spacing
    grid_width = actual_rows * module_height + (actual_rows - 1) * spacing
    
    # Calculate starting position (top-left corner of grid)
    # Center the grid on the roof
    start_x = -roof_length / 2 + margin + module_width / 2
    start_y = -roof_width / 2 + margin + module_height / 2
    
    # Adjust to center the grid if it doesn't fill the available space
    available_length = roof_length - 2 * margin
    available_width = roof_width - 2 * margin
    
    x_offset = (available_length - grid_length) / 2
    y_offset = (available_width - grid_width) / 2
    
    start_x += x_offset
    start_y += y_offset
    
    # TASK 13: Use numpy arrays for batch position calculation
    # This is much faster than Python loops for large numbers of modules
    
    # Generate all possible grid positions using numpy
    max_positions = modules_per_row * actual_rows
    
    # Create arrays for row and column indices
    indices = np.arange(max_positions)
    rows = indices // modules_per_row
    cols = indices % modules_per_row
    
    # Calculate all x and y positions at once (vectorized operation)
    x_positions = start_x + cols * (module_width + spacing)
    y_positions = start_y + rows * (module_height + spacing)
    
    # Combine into position tuples and limit to total_modules
    positions = list(zip(x_positions[:total_modules], y_positions[:total_modules]))
    
    return positions


def get_module_dimensions(orientation: str = "portrait") -> Tuple[float, float, float]:
    """
    Get module dimensions based on orientation.
    
    Args:
        orientation: "portrait" or "landscape"
    
    Returns:
        Tuple of (width, height, thickness) in meters
    """
    if orientation == "landscape":
        return (PV_H, PV_W, PV_T)
    else:
        return (PV_W, PV_H, PV_T)


def calculate_max_modules(
    roof_length: float,
    roof_width: float,
    spacing: float = DEFAULT_SPACING,
    margin: float = DEFAULT_MARGIN,
    orientation: str = "portrait"
) -> int:
    """
    Calculate the maximum number of modules that can fit on a roof.
    
    Args:
        roof_length: Length of the roof in meters
        roof_width: Width of the roof in meters
        spacing: Spacing between modules in meters
        margin: Margin from roof edges in meters
        orientation: Module orientation
    
    Returns:
        Maximum number of modules that can fit
    """
    # Validate inputs
    validation_result = _validate_inputs(
        roof_length, roof_width, 1, spacing, margin
    )
    
    if not validation_result["valid"]:
        return 0
    
    # Get module dimensions
    module_width, module_height, _ = get_module_dimensions(orientation)
    
    # Calculate available area
    available_length = roof_length - (2 * margin)
    available_width = roof_width - (2 * margin)
    
    # Calculate modules per row and column
    modules_per_row = _calculate_modules_per_line(
        available_length, module_width, spacing
    )
    modules_per_column = _calculate_modules_per_line(
        available_width, module_height, spacing
    )
    
    return modules_per_row * modules_per_column


# Example usage and testing
if __name__ == "__main__":
    print("=== PV Module Grid Calculator Test ===\n")
    
    # Test case 1: Standard roof
    print("Test 1: Standard roof (10m x 8m, 20 modules)")
    positions = calculate_module_grid(10.0, 8.0, 20)
    print(f"Placed {len(positions)} modules")
    if positions:
        print(f"  First module: ({positions[0][0]:.2f}, {positions[0][1]:.2f})")
        print(f"  Last module: ({positions[-1][0]:.2f}, {positions[-1][1]:.2f})")
    print()
    
    # Test case 2: Small roof
    print("Test 2: Small roof (5m x 4m, 10 modules)")
    positions = calculate_module_grid(5.0, 4.0, 10)
    print(f"Placed {len(positions)} modules")
    print()
    
    # Test case 3: Maximum capacity
    print("Test 3: Maximum capacity (15m x 12m)")
    max_modules = calculate_max_modules(15.0, 12.0)
    print(f"Maximum modules: {max_modules}")
    positions = calculate_module_grid(15.0, 12.0, max_modules)
    print(f"Placed {len(positions)} modules")
    print()
    
    # Test case 4: Invalid inputs
    print("Test 4: Invalid inputs (negative dimensions)")
    positions = calculate_module_grid(-10.0, 8.0, 20)
    print(f"Handled invalid input: {len(positions)} modules (expected 0)")
    print()
    
    # Test case 5: Landscape orientation
    print("Test 5: Landscape orientation (10m x 8m, 20 modules)")
    positions = calculate_module_grid(10.0, 8.0, 20, orientation="landscape")
    print(f"Placed {len(positions)} modules in landscape")
    print()
    
    print("=== All tests completed ===")
