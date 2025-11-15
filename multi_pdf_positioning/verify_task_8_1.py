"""
Verification Script for Task 8.1: Position-Validierung

This script demonstrates that the validate_positions() function correctly:
1. Validates positions within PDF bounds (0-595, 0-842)
2. Checks minimum margin from edges (10 points)
3. Detects collisions and insufficient spacing (5 points)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.validation_system import (
    ValidationSystem,
    validate_positions
)


def verify_task_8_1():
    """Verify all requirements of Task 8.1."""
    
    print("=" * 70)
    print("TASK 8.1 VERIFICATION: Position-Validierung")
    print("=" * 70)
    print()
    
    # Create validator
    validator = ValidationSystem(
        page_width=595,
        page_height=842,
        min_margin=10,
        min_spacing=5
    )
    
    print("Configuration:")
    print(f"  Page size: {validator.page_width} x {validator.page_height} pts (A4)")
    print(f"  Min margin: {validator.min_margin} pts")
    print(f"  Min spacing: {validator.min_spacing} pts")
    print()
    
    # Test 1: Validate positions within PDF bounds (0-595, 0-842)
    print("=" * 70)
    print("TEST 1: PDF Bounds Validation (0-595, 0-842)")
    print("=" * 70)
    
    test_positions_1 = [
        (50, 50, 200, 100),      # Valid
        (-10, 50, 200, 100),     # x1 < 0 (ERROR)
        (50, -5, 200, 100),      # y1 < 0 (ERROR)
        (400, 50, 600, 100),     # x2 > 595 (ERROR)
        (50, 800, 200, 850),     # y2 > 842 (ERROR)
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(test_positions_1):
        print(f"  {i}: {pos}")
    
    report_1 = validator.validate_positions(test_positions_1)
    
    print(f"\nValidation Results:")
    print(f"  Total elements: {report_1.total_elements}")
    print(f"  Errors: {len(report_1.get_errors())}")
    print(f"  Warnings: {len(report_1.get_warnings())}")
    print(f"  Valid: {report_1.is_valid}")
    
    print("\nErrors detected:")
    for error in report_1.get_errors():
        print(f"  {error.message}")
    
    # Verify requirement
    errors_1 = report_1.get_errors()
    bounds_errors = [e for e in errors_1 if 'negative' in e.message or 'exceeds' in e.message]
    
    if len(bounds_errors) >= 4:
        print("\nREQUIREMENT 6.1 VERIFIED: Detects positions outside PDF bounds")
    else:
        print("\nREQUIREMENT 6.1 FAILED: Not all bounds violations detected")
    
    # Test 2: Check minimum margin from edges (10 points)
    print("\n" + "=" * 70)
    print("TEST 2: Minimum Margin Validation (10 points)")
    print("=" * 70)
    
    test_positions_2 = [
        (5, 50, 200, 100),       # x1 too close to left edge
        (50, 5, 200, 100),       # y1 too close to bottom edge
        (400, 50, 590, 100),     # x2 too close to right edge
        (50, 750, 200, 838),     # y2 too close to top edge
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(test_positions_2):
        print(f"  {i}: {pos}")
    
    report_2 = validator.validate_positions(test_positions_2)
    
    print(f"\nValidation Results:")
    print(f"  Total elements: {report_2.total_elements}")
    print(f"  Errors: {len(report_2.get_errors())}")
    print(f"  Warnings: {len(report_2.get_warnings())}")
    
    print("\nWarnings detected:")
    for warning in report_2.get_warnings():
        print(f"  ⚠ {warning.message}")
    
    # Verify requirement
    warnings_2 = report_2.get_warnings()
    margin_warnings = [w for w in warnings_2 if 'too close' in w.message and 'edge' in w.message]
    
    if len(margin_warnings) >= 4:
        print("\nREQUIREMENT 6.3 VERIFIED: Detects margin violations (< 10 pts)")
    else:
        print("\nREQUIREMENT 6.3 FAILED: Not all margin violations detected")
    
    # Test 3: Detect collisions and insufficient spacing (5 points)
    print("\n" + "=" * 70)
    print("TEST 3: Collision Detection (5 points minimum spacing)")
    print("=" * 70)
    
    test_positions_3 = [
        (50, 50, 150, 100),      # Element 1
        (100, 75, 200, 125),     # Overlaps with Element 1
        (155, 50, 250, 100),     # Too close to Element 1 (< 5 pts)
        (300, 300, 400, 400),    # No collision
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(test_positions_3):
        print(f"  {i}: {pos}")
    
    report_3 = validator.validate_positions(test_positions_3)
    
    print(f"\nValidation Results:")
    print(f"  Total elements: {report_3.total_elements}")
    print(f"  Collisions detected: {len(report_3.collisions)}")
    print(f"  Errors: {len(report_3.get_errors())}")
    
    print("\nCollisions detected:")
    for collision in report_3.collisions:
        print(f"  Elements {collision.element1_index} and {collision.element2_index}")
        print(f"    Overlap area: {collision.overlap_area:.2f} sq pts")
        print(f"    Overlap rect: {collision.overlap_rect}")
    
    # Verify requirement
    if len(report_3.collisions) >= 2:
        print("\nREQUIREMENT 6.2 VERIFIED: Detects collisions and insufficient spacing")
    else:
        print("\nREQUIREMENT 6.2 FAILED: Not all collisions detected")
    
    # Test 4: Complete validation workflow
    print("\n" + "=" * 70)
    print("TEST 4: Complete Validation Workflow")
    print("=" * 70)
    
    test_positions_4 = [
        (50, 50, 200, 100),      # Valid
        (-10, 50, 200, 100),     # Out of bounds
        (5, 50, 200, 100),       # Too close to edge
        (100, 75, 250, 125),     # Collision
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(test_positions_4):
        print(f"  {i}: {pos}")
    
    report_4 = validator.generate_validation_report(
        test_positions_4,
        firma=1,
        seite=1
    )
    
    print("\n" + validator.format_report(report_4))
    
    # Final summary
    print("\n" + "=" * 70)
    print("TASK 8.1 VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_verified = True
    
    # Check Requirement 6.1
    if len(bounds_errors) >= 4:
        print("Requirement 6.1: PDF bounds validation (0-595, 0-842)")
    else:
        print("Requirement 6.1: PDF bounds validation FAILED")
        all_verified = False
    
    # Check Requirement 6.3
    if len(margin_warnings) >= 4:
        print("Requirement 6.3: Minimum margin validation (10 points)")
    else:
        print("Requirement 6.3: Minimum margin validation FAILED")
        all_verified = False
    
    # Check Requirement 6.2
    if len(report_3.collisions) >= 2:
        print("Requirement 6.2: Collision detection (5 points spacing)")
    else:
        print("Requirement 6.2: Collision detection FAILED")
        all_verified = False
    
    print()
    
    if all_verified:
        print("=" * 70)
        print("TASK 8.1 FULLY VERIFIED ")
        print("=" * 70)
        print("\nAll requirements have been successfully implemented:")
        print("  • validate_positions() function is working correctly")
        print("  • PDF bounds validation (0-595, 0-842)")
        print("  • Minimum margin validation (10 points)")
        print("  • Collision detection (5 points spacing)")
        print("\nThe validation system is ready for production use.")
    else:
        print("=" * 70)
        print("TASK 8.1 VERIFICATION FAILED ")
        print("=" * 70)
        print("\nSome requirements were not met. Please review the implementation.")
    
    print()


if __name__ == "__main__":
    verify_task_8_1()
