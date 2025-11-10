"""
Test Suite for Task 11: Collision Detection

This test suite validates the collision detection functionality for PV module
placement, including module-to-module overlap detection and roof boundary
violation detection.

Requirements tested: 7.1, 7.2, 7.3, 7.4
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d_placement_handler import check_module_collision
from utils.pv3d_grid_calculator import PV_W, PV_H, DEFAULT_MARGIN


def test_no_collision():
    """Test that well-separated modules don't collide."""
    print("\n=== Test 1: No Collision (Well-Separated Modules) ===")

    # Module at origin
    new_position = (0.0, 0.0, 0.3)

    # Module far away (3 meters in X direction)
    existing_positions = [(3.0, 0.0, 0.3)]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Result: {result}")

    assert result["collision"] is False, "Should not detect collision"
    assert result["type"] == "none", "Type should be 'none'"
    print("✓ Test passed: No collision detected for well-separated modules")


def test_module_overlap():
    """Test that overlapping modules are detected."""
    print("\n=== Test 2: Module-to-Module Overlap ===")

    # Module at origin
    new_position = (0.0, 0.0, 0.3)

    # Module very close (0.5m away, less than module width)
    existing_positions = [(0.5, 0.0, 0.3)]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Module width: {PV_W}m")
    print(f"Distance: 0.5m (< {PV_W}m)")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect collision"
    assert result["type"] == "module", "Type should be 'module'"
    assert result["colliding_index"] == 0, "Should identify colliding module"
    print("✓ Test passed: Module overlap detected")


def test_exact_overlap():
    """Test that modules at the same position collide."""
    print("\n=== Test 3: Exact Overlap (Same Position) ===")

    # Module at origin
    new_position = (0.0, 0.0, 0.3)

    # Module at exact same position
    existing_positions = [(0.0, 0.0, 0.3)]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect collision"
    assert result["type"] == "module", "Type should be 'module'"
    print("✓ Test passed: Exact overlap detected")


def test_boundary_violation_left():
    """Test that modules exceeding left boundary are detected."""
    print("\n=== Test 4: Boundary Violation (Left Edge) ===")

    # Module too far left
    roof_length = 10.0
    roof_width = 8.0

    # Position that would place module beyond left boundary
    # Left boundary: -roof_length/2 + margin = -5.0 + 0.3 = -4.7
    # Module extends from x - PV_W/2 to x + PV_W/2
    # If x = -4.5, left edge = -4.5 - 0.525 = -5.025 (beyond -4.7)
    new_position = (-4.5, 0.0, 0.3)

    existing_positions = []

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Roof length: {roof_length}m")
    print(f"Left boundary: {-roof_length/2 + DEFAULT_MARGIN}m")
    print(f"Module left edge: {new_position[0] - PV_W/2}m")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect boundary violation"
    assert result["type"] == "boundary", "Type should be 'boundary'"
    print("✓ Test passed: Left boundary violation detected")


def test_boundary_violation_right():
    """Test that modules exceeding right boundary are detected."""
    print("\n=== Test 5: Boundary Violation (Right Edge) ===")

    # Module too far right
    roof_length = 10.0
    roof_width = 8.0

    # Position that would place module beyond right boundary
    new_position = (4.5, 0.0, 0.3)

    existing_positions = []

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Roof length: {roof_length}m")
    print(f"Right boundary: {roof_length/2 - DEFAULT_MARGIN}m")
    print(f"Module right edge: {new_position[0] + PV_W/2}m")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect boundary violation"
    assert result["type"] == "boundary", "Type should be 'boundary'"
    print("✓ Test passed: Right boundary violation detected")


def test_boundary_violation_top():
    """Test that modules exceeding top boundary are detected."""
    print("\n=== Test 6: Boundary Violation (Top Edge) ===")

    # Module too far up
    roof_length = 10.0
    roof_width = 8.0

    # Position that would place module beyond top boundary
    new_position = (0.0, 3.5, 0.3)

    existing_positions = []

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Roof width: {roof_width}m")
    print(f"Top boundary: {roof_width/2 - DEFAULT_MARGIN}m")
    print(f"Module top edge: {new_position[1] + PV_H/2}m")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect boundary violation"
    assert result["type"] == "boundary", "Type should be 'boundary'"
    print("✓ Test passed: Top boundary violation detected")


def test_boundary_violation_bottom():
    """Test that modules exceeding bottom boundary are detected."""
    print("\n=== Test 7: Boundary Violation (Bottom Edge) ===")

    # Module too far down
    roof_length = 10.0
    roof_width = 8.0

    # Position that would place module beyond bottom boundary
    new_position = (0.0, -3.5, 0.3)

    existing_positions = []

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Roof width: {roof_width}m")
    print(f"Bottom boundary: {-roof_width/2 + DEFAULT_MARGIN}m")
    print(f"Module bottom edge: {new_position[1] - PV_H/2}m")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect boundary violation"
    assert result["type"] == "boundary", "Type should be 'boundary'"
    print("✓ Test passed: Bottom boundary violation detected")


def test_multiple_existing_modules():
    """Test collision detection with multiple existing modules."""
    print("\n=== Test 8: Multiple Existing Modules ===")

    # New module
    new_position = (2.0, 0.0, 0.3)

    # Multiple existing modules
    existing_positions = [
        (0.0, 0.0, 0.3),   # Module 1
        (4.0, 0.0, 0.3),   # Module 2 (far away)
        (2.0, 2.0, 0.3),   # Module 3 (different row)
    ]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Result: {result}")

    # Should not collide with any of them
    assert result["collision"] is False, "Should not detect collision"
    print("✓ Test passed: No collision with multiple modules")


def test_landscape_orientation():
    """Test collision detection with landscape orientation."""
    print("\n=== Test 9: Landscape Orientation ===")

    # Module at origin
    new_position = (0.0, 0.0, 0.3)

    # Module close in Y direction (would collide in landscape)
    existing_positions = [(0.0, 0.8, 0.3)]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    # Test with landscape orientation
    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width,
        orientation="landscape"
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Orientation: landscape")
    print(f"Module dimensions (landscape): {PV_H}m x {PV_W}m")
    print(f"Result: {result}")

    assert result["collision"] is True, "Should detect collision in landscape"
    assert result["type"] == "module", "Type should be 'module'"
    print("✓ Test passed: Landscape orientation collision detected")


def test_edge_case_just_touching():
    """Test modules that are just touching (edge case)."""
    print("\n=== Test 10: Edge Case - Just Touching ===")

    # Module at origin
    new_position = (0.0, 0.0, 0.3)

    # Module exactly one module width away (should not collide)
    existing_positions = [(PV_W + 0.01, 0.0, 0.3)]

    # Roof dimensions
    roof_length = 10.0
    roof_width = 8.0

    result = check_module_collision(
        new_position=new_position,
        existing_positions=existing_positions,
        roof_length=roof_length,
        roof_width=roof_width
    )

    print(f"New position: {new_position}")
    print(f"Existing positions: {existing_positions}")
    print(f"Distance: {PV_W + 0.01}m")
    print(f"Result: {result}")

    assert result["collision"] is False, "Should not detect collision"
    print("✓ Test passed: Just-touching modules handled correctly")


def run_all_tests():
    """Run all collision detection tests."""
    print("=" * 70)
    print("COLLISION DETECTION TEST SUITE - TASK 11")
    print("=" * 70)

    tests = [
        test_no_collision,
        test_module_overlap,
        test_exact_overlap,
        test_boundary_violation_left,
        test_boundary_violation_right,
        test_boundary_violation_top,
        test_boundary_violation_bottom,
        test_multiple_existing_modules,
        test_landscape_orientation,
        test_edge_case_just_touching,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
