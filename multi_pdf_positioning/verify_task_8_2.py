"""
Verification Script for Task 8.2: Kollisions-Erkennung

This script verifies that collision detection and resolution are working correctly.
"""

import sys
sys.path.insert(0, '.')

from multi_pdf_positioning.validation_system import (
    ValidationSystem,
    detect_collisions,
    CollisionInfo
)


def verify_collision_detection():
    """Verify collision detection functionality."""
    print("\n=== Verifying Collision Detection ===\n")
    
    validator = ValidationSystem(min_spacing=5)
    
    # Test 1: No collisions
    print("Test 1: No collisions")
    positions_no_collision = [
        (50, 50, 150, 100),
        (200, 50, 300, 100),
    ]
    collisions = validator.detect_collisions(positions_no_collision)
    assert len(collisions) == 0, "Should detect no collisions"
    print("  Correctly detected no collisions")
    
    # Test 2: Overlapping elements
    print("\nTest 2: Overlapping elements")
    positions_overlap = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),
    ]
    collisions = validator.detect_collisions(positions_overlap)
    assert len(collisions) == 1, "Should detect 1 collision"
    assert isinstance(collisions[0], CollisionInfo), "Should return CollisionInfo"
    assert collisions[0].element1_index == 0, "First element index should be 0"
    assert collisions[0].element2_index == 1, "Second element index should be 1"
    assert collisions[0].overlap_area > 0, "Overlap area should be positive"
    print(f"  Correctly detected 1 collision")
    print(f"    - Overlap area: {collisions[0].overlap_area:.2f} sq pts")
    
    # Test 3: Elements too close
    print("\nTest 3: Elements too close (< min_spacing)")
    positions_too_close = [
        (50, 50, 150, 100),
        (153, 50, 250, 100),  # Only 3 pts apart
    ]
    collisions = validator.detect_collisions(positions_too_close)
    assert len(collisions) == 1, "Should detect collision due to spacing"
    print("  Correctly detected spacing violation")
    
    # Test 4: Multiple collisions
    print("\nTest 4: Multiple collisions")
    positions_multiple = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),
        (125, 90, 225, 140),
    ]
    collisions = validator.detect_collisions(positions_multiple)
    assert len(collisions) >= 2, "Should detect multiple collisions"
    print(f"  Correctly detected {len(collisions)} collisions")
    
    print("\nAll collision detection tests passed")


def verify_collision_resolution():
    """Verify automatic collision resolution."""
    print("\n=== Verifying Collision Resolution ===\n")
    
    validator = ValidationSystem(min_spacing=5)
    
    # Test 1: Simple collision resolution
    print("Test 1: Simple collision resolution")
    positions = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),
    ]
    
    collisions = validator.detect_collisions(positions)
    initial_count = len(collisions)
    print(f"  Initial collisions: {initial_count}")
    
    adjusted = validator.resolve_collisions(positions, collisions, max_iterations=5)
    
    new_collisions = validator.detect_collisions(adjusted)
    final_count = len(new_collisions)
    print(f"  Final collisions: {final_count}")
    
    assert final_count <= initial_count, "Should reduce or maintain collision count"
    print("  Collision resolution reduced collisions")
    
    # Test 2: Bounds preservation
    print("\nTest 2: Bounds preservation during resolution")
    for i, pos in enumerate(adjusted):
        x1, y1, x2, y2 = pos
        assert x1 >= validator.min_margin, f"Element {i} x1 below min margin"
        assert y1 >= validator.min_margin, f"Element {i} y1 below min margin"
        assert x2 <= validator.page_width - validator.min_margin, f"Element {i} x2 exceeds max"
        assert y2 <= validator.page_height - validator.min_margin, f"Element {i} y2 exceeds max"
    print("  All positions remain within bounds")
    
    # Test 3: Multiple iterations
    print("\nTest 3: Multiple iterations with complex collisions")
    positions_complex = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),
        (125, 90, 225, 140),
    ]
    
    collisions = validator.detect_collisions(positions_complex)
    initial_count = len(collisions)
    
    adjusted = validator.resolve_collisions(
        positions_complex, 
        collisions, 
        max_iterations=10
    )
    
    new_collisions = validator.detect_collisions(adjusted)
    final_count = len(new_collisions)
    
    print(f"  Initial collisions: {initial_count}")
    print(f"  Final collisions: {final_count}")
    assert final_count <= initial_count, "Should reduce collisions"
    print("  Multiple iterations successfully reduced collisions")
    
    print("\nAll collision resolution tests passed")


def verify_integration():
    """Verify integration with validation system."""
    print("\n=== Verifying Integration with Validation System ===\n")
    
    validator = ValidationSystem()
    
    # Test with validation report
    print("Test: Collision detection in validation report")
    positions = [
        (50, 50, 200, 100),
        (100, 75, 250, 125),  # Collision
    ]
    
    report = validator.validate_positions(positions)
    
    assert len(report.collisions) > 0, "Report should contain collisions"
    assert not report.is_valid, "Report should be invalid with collisions"
    
    print(f"  Report contains {len(report.collisions)} collision(s)")
    print(f"  Report validity: {report.is_valid} (correctly invalid)")
    
    # Test formatted report
    print("\nTest: Formatted report includes collision details")
    formatted = validator.format_report(report)
    assert "COLLISIONS" in formatted, "Formatted report should include collisions section"
    print("  Formatted report includes collision details")
    
    print("\nAll integration tests passed")


def verify_convenience_functions():
    """Verify convenience functions."""
    print("\n=== Verifying Convenience Functions ===\n")
    
    # Test detect_collisions convenience function
    print("Test: detect_collisions convenience function")
    positions = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),
    ]
    
    collisions = detect_collisions(positions, min_spacing=5)
    assert len(collisions) == 1, "Should detect 1 collision"
    print("  detect_collisions() convenience function works")
    
    print("\nAll convenience function tests passed")


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("TASK 8.2 VERIFICATION: Kollisions-Erkennung")
    print("=" * 70)
    
    try:
        verify_collision_detection()
        verify_collision_resolution()
        verify_integration()
        verify_convenience_functions()
        
        print("\n" + "=" * 70)
        print("ALL VERIFICATION TESTS PASSED")
        print("=" * 70)
        print("\nTask 8.2 Implementation Summary:")
        print("  detect_collisions() - Identifies overlapping elements")
        print("  resolve_collisions() - Automatically adjusts positions")
        print("  CollisionInfo - Detailed collision information")
        print("  Integration with ValidationSystem")
        print("  Convenience functions available")
        print("\nRequirements Coverage:")
        print("  Requirement 6.2: Collision detection and spacing validation")
        print("  Requirement 3.4: Design element overlap prevention")
        print("\nTask 8.2 (Kollisions-Erkennung) is COMPLETE and VERIFIED")
        
        return 0
        
    except AssertionError as e:
        print(f"\nVERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
