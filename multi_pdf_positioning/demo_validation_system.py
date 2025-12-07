"""
Demo script for Validation System

This script demonstrates all features of the validation system including:
- Position validation
- Collision detection
- Collision resolution
- Validation reporting
"""

from multi_pdf_positioning.validation_system import (
    ValidationSystem,
    validate_positions,
    detect_collisions,
    generate_validation_report
)
from multi_pdf_positioning.yml_parser import YMLElement


def demo_basic_validation():
    """Demonstrate basic position validation."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Position Validation")
    print("=" * 70)
    
    validator = ValidationSystem()
    
    # Test various positions
    positions = [
        (50, 50, 200, 100),      # Valid position
        (-10, 50, 200, 100),     # x1 out of bounds (error)
        (5, 50, 200, 100),       # x1 too close to edge (warning)
        (400, 50, 600, 100),     # x2 exceeds page width (error)
        (50, 50, 52, 100),       # Very small width (warning)
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(positions):
        print(f"  {i}: {pos}")
    
    print("\nRunning validation...")
    report = validator.validate_positions(positions)
    
    print(f"\nResults:")
    print(f"  Total elements: {report.total_elements}")
    print(f"  Valid: {report.is_valid}")
    print(f"  Errors: {len(report.get_errors())}")
    print(f"  Warnings: {len(report.get_warnings())}")
    
    print("\nErrors:")
    for error in report.get_errors():
        print(f"  {error.message}")
    
    print("\nWarnings:")
    for warning in report.get_warnings():
        print(f"   {warning.message}")


def demo_collision_detection():
    """Demonstrate collision detection."""
    print("\n" + "=" * 70)
    print("DEMO 2: Collision Detection")
    print("=" * 70)
    
    validator = ValidationSystem(min_spacing=5)
    
    # Positions with collisions
    positions = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),     # Overlaps with first
        (125, 90, 225, 140),     # Overlaps with second
        (300, 300, 400, 400),    # No overlap
    ]
    
    print("\nTest Positions:")
    for i, pos in enumerate(positions):
        print(f"  {i}: {pos}")
    
    print("\nDetecting collisions...")
    collisions = validator.detect_collisions(positions)
    
    print(f"\nFound {len(collisions)} collision(s):")
    for collision in collisions:
        print(f"\n  Collision between elements {collision.element1_index} "
              f"and {collision.element2_index}")
        print(f"    Element 1: {collision.element1_position}")
        print(f"    Element 2: {collision.element2_position}")
        print(f"    Overlap area: {collision.overlap_area:.2f} sq pts")
        print(f"    Overlap rect: {collision.overlap_rect}")


def demo_collision_resolution():
    """Demonstrate automatic collision resolution."""
    print("\n" + "=" * 70)
    print("DEMO 3: Collision Resolution")
    print("=" * 70)
    
    validator = ValidationSystem(min_spacing=5)
    
    # Positions with collisions
    positions = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),     # Overlaps with first
        (125, 90, 225, 140),     # Overlaps with second
    ]
    
    print("\nOriginal Positions:")
    for i, pos in enumerate(positions):
        print(f"  {i}: {pos}")
    
    # Detect collisions
    collisions = validator.detect_collisions(positions)
    print(f"\nInitial collisions: {len(collisions)}")
    
    # Resolve collisions
    print("\nResolving collisions...")
    adjusted = validator.resolve_collisions(
        positions, collisions, max_iterations=10
    )
    
    print("\nAdjusted Positions:")
    for i, pos in enumerate(adjusted):
        print(f"  {i}: {pos}")
    
    # Re-check collisions
    new_collisions = validator.detect_collisions(adjusted)
    print(f"\nCollisions after resolution: {len(new_collisions)}")
    
    # Validate adjusted positions
    report = validator.validate_positions(adjusted)
    print(f"\nValidation after resolution:")
    print(f"  Valid: {report.is_valid}")
    print(f"  Errors: {len(report.get_errors())}")
    print(f"  Warnings: {len(report.get_warnings())}")


def demo_validation_report():
    """Demonstrate comprehensive validation reporting."""
    print("\n" + "=" * 70)
    print("DEMO 4: Validation Report Generation")
    print("=" * 70)
    
    validator = ValidationSystem()
    
    # Create test elements
    elements = [
        YMLElement(
            text="ERSTELLT FÜR:",
            position=(48, 70, 220, 87),
            font="Helvetica-Bold",
            font_size=20,
            color=30920,
            index=0
        ),
        YMLElement(
            text="kunde_vorname_und_nachname",
            position=(90, 87, 220, 105),
            font="Helvetica-Bold",
            font_size=14,
            color=3487029,
            index=1
        ),
        YMLElement(
            text="Invalid Element",
            position=(-10, 50, 200, 100),  # Out of bounds
            font="Helvetica",
            font_size=12,
            color=0,
            index=2
        ),
    ]
    
    positions = [elem.position for elem in elements]
    
    print("\nGenerating validation report...")
    report = validator.generate_validation_report(
        positions, elements, firma=1, seite=1
    )
    
    # Print formatted report
    print("\n" + validator.format_report(report))


def demo_batch_validation():
    """Demonstrate batch validation for multiple firma-seite combinations."""
    print("\n" + "=" * 70)
    print("DEMO 5: Batch Validation")
    print("=" * 70)
    
    validator = ValidationSystem()
    
    # Simulate validation for multiple combinations
    test_cases = [
        (1, 1, [(50, 50, 200, 100), (250, 150, 400, 250)]),
        (1, 2, [(50, 50, 200, 100), (100, 75, 200, 125)]),  # Has collision
        (2, 1, [(-10, 50, 200, 100)]),  # Out of bounds
    ]
    
    results = []
    
    for firma, seite, positions in test_cases:
        report = validator.generate_validation_report(
            positions, firma=firma, seite=seite
        )
        results.append((firma, seite, report))
    
    print("\nBatch Validation Results:")
    print("-" * 70)
    
    for firma, seite, report in results:
        status = "VALID" if report.is_valid else "INVALID"
        print(f"\nFirma {firma}, Seite {seite}: {status}")
        print(f"  Elements: {report.total_elements}")
        print(f"  Errors: {len(report.get_errors())}")
        print(f"  Warnings: {len(report.get_warnings())}")
        print(f"  Collisions: {len(report.collisions)}")


def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n" + "=" * 70)
    print("DEMO 6: Convenience Functions")
    print("=" * 70)
    
    positions = [
        (50, 50, 200, 100),
        (100, 75, 200, 125),
    ]
    
    print("\nUsing validate_positions():")
    report = validate_positions(positions)
    print(f"  Valid: {report.is_valid}")
    print(f"  Errors: {len(report.get_errors())}")
    
    print("\nUsing detect_collisions():")
    collisions = detect_collisions(positions, min_spacing=5)
    print(f"  Collisions found: {len(collisions)}")
    
    print("\nUsing generate_validation_report():")
    report = generate_validation_report(positions, firma=1, seite=1)
    print(f"  Firma: {report.firma}")
    print(f"  Seite: {report.seite}")
    print(f"  Valid: {report.is_valid}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("VALIDATION SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    demo_basic_validation()
    demo_collision_detection()
    demo_collision_resolution()
    demo_validation_report()
    demo_batch_validation()
    demo_convenience_functions()
    
    print("\n" + "=" * 70)
    print("All demos completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
