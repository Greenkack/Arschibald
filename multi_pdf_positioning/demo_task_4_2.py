"""
Demo: Task 4.2 - Basis-Positionierungs-Algorithmus

This demo showcases the calculate_positions() function and grid-based
positioning working with real YML files.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.yml_parser import parse_yml
from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, SafeZone
from multi_pdf_positioning.position_calculator import (
    PositionCalculator,
    calculate_positions,
    POSITIONING_RULES
)


def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("DEMO: Task 4.2 - Basis-Positionierungs-Algorithmus")
    print("=" * 70)
    
    # Configuration
    yml_file = "coords_multi/seite1_f1.yml"
    
    print(f"\n1️⃣  Loading YML file: {yml_file}")
    print("-" * 70)
    
    # Parse YML
    elements = parse_yml(yml_file)
    print(f"   Loaded {len(elements)} text elements")
    
    # Show some elements
    print(f"\n   Sample elements:")
    for i, elem in enumerate(elements[:3]):
        print(f"   {i+1}. '{elem.text[:30]}' at {elem.position}")
    
    # Create PDF analysis
    print(f"\n2️⃣  Creating PDF analysis")
    print("-" * 70)
    
    pdf_analysis = PDFAnalysis(
        firma=1,
        seite=1,
        page_size={"width": 595, "height": 842},
        design_regions=[],
        visual_elements=[],
        safe_zones=[
            SafeZone(x1=50, y1=50, x2=545, y2=792)
        ],
        color_palette=["#007BFF", "#FFFFFF"]
    )
    
    print(f"   Page size: {pdf_analysis.page_size['width']} x "
          f"{pdf_analysis.page_size['height']} points")
    print(f"   Safe zones: {len(pdf_analysis.safe_zones)}")
    
    # Show positioning rules
    print(f"\n3️⃣  Positioning rules")
    print("-" * 70)
    print(f"   Min margin: {POSITIONING_RULES['min_margin']} points")
    print(f"   Min spacing: {POSITIONING_RULES['min_spacing']} points")
    print(f"   Grid: {POSITIONING_RULES['grid_columns']}x"
          f"{POSITIONING_RULES['grid_rows']}")
    print(f"   Grid padding: {POSITIONING_RULES['grid_padding']} points")
    
    # Calculate positions using convenience function
    print(f"\n4️⃣  Calculating positions (convenience function)")
    print("-" * 70)
    
    new_positions = calculate_positions(elements, pdf_analysis)
    print(f"   Calculated {len(new_positions)} positions")
    
    # Show position changes
    print(f"\n   Position changes (first 3):")
    for i, (elem, new_pos) in enumerate(zip(elements[:3], new_positions[:3])):
        old_pos = elem.position
        dx = new_pos[0] - old_pos[0]
        dy = new_pos[1] - old_pos[1]
        print(f"   {i+1}. '{elem.text[:20]}'")
        print(f"      Old: ({old_pos[0]:.1f}, {old_pos[1]:.1f}) -> "
              f"({old_pos[2]:.1f}, {old_pos[3]:.1f})")
        print(f"      New: ({new_pos[0]:.1f}, {new_pos[1]:.1f}) -> "
              f"({new_pos[2]:.1f}, {new_pos[3]:.1f})")
        print(f"      Δ: ({dx:+.1f}, {dy:+.1f})")
    
    # Calculate positions using calculator class
    print(f"\n5️⃣  Calculating positions (calculator class)")
    print("-" * 70)
    
    calculator = PositionCalculator()
    new_positions_2 = calculator.calculate_positions(
        elements,
        pdf_analysis,
        strategy="grid"
    )
    print(f"   Calculated {len(new_positions_2)} positions")
    
    # Validate positions
    print(f"\n6️⃣  Validating positions")
    print("-" * 70)
    
    is_valid, errors = calculator.validate_positions(new_positions_2)
    
    if is_valid:
        print(f"   All positions are valid!")
    else:
        print(f"   ⚠ Found {len(errors)} validation issue(s)")
        for error in errors[:3]:
            print(f"      - {error}")
        if len(errors) > 3:
            print(f"      ... and {len(errors) - 3} more")
    
    # Check collisions
    print(f"\n7️⃣  Checking collisions")
    print("-" * 70)
    
    collisions = calculator.check_collisions(new_positions_2)
    
    if len(collisions) == 0:
        print(f"   No collisions detected!")
    else:
        print(f"   ⚠ Found {len(collisions)} collision(s)")
        print(f"   Note: Grid strategy may have collisions.")
        print(f"   Advanced strategies in Task 5 will reduce these.")
    
    # Statistics
    print(f"\n8️⃣  Statistics")
    print("-" * 70)
    
    # Calculate bounds coverage
    in_bounds = 0
    for pos in new_positions_2:
        x1, y1, x2, y2 = pos
        if (x1 >= 10 and y1 >= 10 and
            x2 <= 585 and y2 <= 832):
            in_bounds += 1
    
    print(f"   Total elements: {len(elements)}")
    print(f"   Positions calculated: {len(new_positions_2)}")
    print(f"   Within bounds: {in_bounds}/{len(new_positions_2)} "
          f"({100*in_bounds/len(new_positions_2):.1f}%)")
    print(f"   Collisions: {len(collisions)}")
    
    # Calculate average movement
    total_dx = sum(abs(new[0] - old.position[0])
                   for old, new in zip(elements, new_positions_2))
    total_dy = sum(abs(new[1] - old.position[1])
                   for old, new in zip(elements, new_positions_2))
    
    if len != 0:
        avg_dx = total_dx / len(elements)
    else:
        avg_dx = 0.0
    if len != 0:
        avg_dy = total_dy / len(elements)
    else:
        avg_dy = 0.0
    
    print(f"   Average movement: Δx={avg_dx:.1f}, Δy={avg_dy:.1f} points")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print(f"\nTask 4.2 successfully demonstrates:")
    print(f"  calculate_positions() main function")
    print(f"  Grid-based positioning as fallback")
    print(f"  Testing with real YML file")
    print(f"  Position validation")
    print(f"  Collision detection")
    print(f"\nNext: Task 5 - Implement specific positioning strategies")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
