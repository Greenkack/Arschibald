"""
Verification test for Grid Calculator implementation against requirements.
Tests Requirements 3.1 through 3.6
"""

from utils.pv3d_grid_calculator import (
    calculate_module_grid,
    calculate_max_modules,
    get_module_dimensions,
    PV_W,
    PV_H,
    DEFAULT_SPACING,
    DEFAULT_MARGIN
)


def test_requirement_3_1():
    """Requirement 3.1: Calculate (x, y) coordinates for each module"""
    print("Testing Requirement 3.1: Calculate (x, y) coordinates...")
    
    positions = calculate_module_grid(10.0, 8.0, 5)
    
    assert len(positions) == 5, "Should return 5 positions"
    assert all(isinstance(pos, tuple) and len(pos) == 2 for pos in positions), \
        "Each position should be a (x, y) tuple"
    assert all(isinstance(pos[0], float) and isinstance(pos[1], float) for pos in positions), \
        "Coordinates should be floats"
    
    print("✓ Requirement 3.1 satisfied: (x, y) coordinates calculated")


def test_requirement_3_2():
    """Requirement 3.2: Consider roof dimensions (length x width)"""
    print("\nTesting Requirement 3.2: Consider roof dimensions...")
    
    # Small roof should fit fewer modules
    small_positions = calculate_module_grid(5.0, 4.0, 100)
    
    # Large roof should fit more modules
    large_positions = calculate_module_grid(15.0, 12.0, 100)
    
    assert len(small_positions) < len(large_positions), \
        "Larger roof should accommodate more modules"
    
    # Verify positions are within roof bounds
    for x, y in large_positions:
        assert -15.0/2 <= x <= 15.0/2, f"X position {x} outside roof length bounds"
        assert -12.0/2 <= y <= 12.0/2, f"Y position {y} outside roof width bounds"
    
    print("✓ Requirement 3.2 satisfied: Roof dimensions considered")


def test_requirement_3_3():
    """Requirement 3.3: Consider module dimensions (1.05m x 1.76m)"""
    print("\nTesting Requirement 3.3: Consider module dimensions...")
    
    # Verify module dimensions are used
    assert PV_W == 1.05, "Module width should be 1.05m"
    assert PV_H == 1.76, "Module height should be 1.76m"
    
    # Test that module dimensions affect grid calculation
    # A roof barely larger than one module should fit exactly 1 module
    roof_length = PV_W + 2 * DEFAULT_MARGIN + 0.1
    roof_width = PV_H + 2 * DEFAULT_MARGIN + 0.1
    
    positions = calculate_module_grid(roof_length, roof_width, 10)
    assert len(positions) == 1, "Should fit exactly 1 module on minimal roof"
    
    # Test landscape orientation uses swapped dimensions
    width, height, _ = get_module_dimensions("landscape")
    assert width == PV_H and height == PV_W, "Landscape should swap dimensions"
    
    print("✓ Requirement 3.3 satisfied: Module dimensions (1.05m x 1.76m) considered")


def test_requirement_3_4():
    """Requirement 3.4: Consider spacing between modules"""
    print("\nTesting Requirement 3.4: Consider spacing between modules...")
    
    # Calculate with default spacing
    positions_default = calculate_module_grid(10.0, 8.0, 20, spacing=DEFAULT_SPACING)
    
    # Calculate with larger spacing
    positions_large_spacing = calculate_module_grid(10.0, 8.0, 20, spacing=0.20)
    
    # Larger spacing should result in fewer modules fitting
    assert len(positions_large_spacing) <= len(positions_default), \
        "Larger spacing should reduce module count"
    
    # Verify spacing is maintained (check distance between adjacent modules)
    if len(positions_default) >= 2:
        x1, y1 = positions_default[0]
        x2, y2 = positions_default[1]
        
        # Distance should be module width + spacing
        expected_distance = PV_W + DEFAULT_SPACING
        actual_distance = abs(x2 - x1)
        
        assert abs(actual_distance - expected_distance) < 0.01, \
            f"Spacing not maintained: expected {expected_distance}, got {actual_distance}"
    
    print("✓ Requirement 3.4 satisfied: Spacing between modules considered")


def test_requirement_3_5():
    """Requirement 3.5: Consider margin distances from edges"""
    print("\nTesting Requirement 3.5: Consider margin distances...")
    
    roof_length = 10.0
    roof_width = 8.0
    margin = DEFAULT_MARGIN
    
    positions = calculate_module_grid(roof_length, roof_width, 50, margin=margin)
    
    # Verify all positions respect margins
    for x, y in positions:
        # Check X bounds (considering module half-width)
        min_x = -roof_length/2 + margin + PV_W/2
        max_x = roof_length/2 - margin - PV_W/2
        
        assert min_x - 0.01 <= x <= max_x + 0.01, \
            f"X position {x} violates margin (should be between {min_x} and {max_x})"
        
        # Check Y bounds (considering module half-height)
        min_y = -roof_width/2 + margin + PV_H/2
        max_y = roof_width/2 - margin - PV_H/2
        
        assert min_y - 0.01 <= y <= max_y + 0.01, \
            f"Y position {y} violates margin (should be between {min_y} and {max_y})"
    
    # Test with larger margin - should fit fewer modules
    positions_large_margin = calculate_module_grid(roof_length, roof_width, 50, margin=0.50)
    assert len(positions_large_margin) < len(positions), \
        "Larger margin should reduce module count"
    
    print("✓ Requirement 3.5 satisfied: Margin distances considered")


def test_requirement_3_6():
    """Requirement 3.6: Return maximum possible if requested exceeds capacity"""
    print("\nTesting Requirement 3.6: Return maximum possible count...")
    
    roof_length = 10.0
    roof_width = 8.0
    
    # Calculate maximum capacity
    max_capacity = calculate_max_modules(roof_length, roof_width)
    
    # Request more than capacity
    requested = max_capacity + 50
    positions = calculate_module_grid(roof_length, roof_width, requested)
    
    # Should return maximum possible, not requested amount
    assert len(positions) == max_capacity, \
        f"Should return max capacity {max_capacity}, not requested {requested}"
    assert len(positions) < requested, \
        "Should limit to maximum possible"
    
    # Request less than capacity
    requested_small = max_capacity // 2
    positions_small = calculate_module_grid(roof_length, roof_width, requested_small)
    
    assert len(positions_small) == requested_small, \
        "Should return requested amount when within capacity"
    
    print(f"✓ Requirement 3.6 satisfied: Returns max possible ({max_capacity}) when requested exceeds capacity")


def test_input_validation():
    """Test input validation (part of requirements)"""
    print("\nTesting input validation...")
    
    # Negative roof dimensions
    assert calculate_module_grid(-10.0, 8.0, 20) == [], \
        "Should return empty list for negative length"
    assert calculate_module_grid(10.0, -8.0, 20) == [], \
        "Should return empty list for negative width"
    
    # Zero dimensions
    assert calculate_module_grid(0, 8.0, 20) == [], \
        "Should return empty list for zero length"
    
    # Zero or negative module quantity
    assert calculate_module_grid(10.0, 8.0, 0) == [], \
        "Should return empty list for zero modules"
    assert calculate_module_grid(10.0, 8.0, -5) == [], \
        "Should return empty list for negative modules"
    
    # Margins too large
    assert calculate_module_grid(2.0, 2.0, 10, margin=1.5) == [], \
        "Should return empty list when margins exceed roof dimensions"
    
    print("✓ Input validation working correctly")


def test_optimization():
    """Test optimization for maximum module count"""
    print("\nTesting optimization for maximum module count...")
    
    roof_length = 15.0
    roof_width = 12.0
    
    # Calculate maximum
    max_modules = calculate_max_modules(roof_length, roof_width)
    
    # Verify we can actually place that many
    positions = calculate_module_grid(roof_length, roof_width, max_modules)
    
    assert len(positions) == max_modules, \
        f"Should place exactly {max_modules} modules"
    
    # Verify we can't place more
    positions_more = calculate_module_grid(roof_length, roof_width, max_modules + 10)
    assert len(positions_more) == max_modules, \
        "Should not exceed maximum capacity"
    
    print(f"✓ Optimization working: Maximum {max_modules} modules calculated and placed")


def run_all_tests():
    """Run all requirement verification tests"""
    print("=" * 60)
    print("Grid Calculator Requirements Verification")
    print("=" * 60)
    
    try:
        test_requirement_3_1()
        test_requirement_3_2()
        test_requirement_3_3()
        test_requirement_3_4()
        test_requirement_3_5()
        test_requirement_3_6()
        test_input_validation()
        test_optimization()
        
        print("\n" + "=" * 60)
        print("✅ ALL REQUIREMENTS VERIFIED SUCCESSFULLY")
        print("=" * 60)
        print("\nRequirements 3.1 through 3.6 are fully satisfied:")
        print("  ✓ 3.1: (x, y) coordinates calculated")
        print("  ✓ 3.2: Roof dimensions considered")
        print("  ✓ 3.3: Module dimensions (1.05m x 1.76m) considered")
        print("  ✓ 3.4: Spacing between modules considered")
        print("  ✓ 3.5: Margin distances considered")
        print("  ✓ 3.6: Maximum possible count returned when requested exceeds capacity")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
