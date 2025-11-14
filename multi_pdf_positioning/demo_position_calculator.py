"""
Demo script for Position Calculator

This script demonstrates the position calculator functionality
with a real YML file and PDF analysis.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
from multi_pdf_positioning.position_calculator import (
    PositionCalculator,
    POSITIONING_RULES
)


def main():
    """Run position calculator demo."""
    print("\n" + "=" * 70)
    print("Position Calculator Demo")
    print("=" * 70)
    
    # Configuration (relative to parent directory)
    base_dir = Path(__file__).parent.parent
    yml_file = base_dir / "coords_multi" / "seite1_f1.yml"
    pdf_file = base_dir / "pdf_templates_static" / "multi" / "multi_nt_01_f1.pdf"
    
    # Check if files exist
    if not yml_file.exists():
        print(f"\n[ERROR] YML file not found: {yml_file}")
        print("  Please ensure the file exists in the coords_multi directory")
        return 1
    
    if not pdf_file.exists():
        print(f"\n[ERROR] PDF file not found: {pdf_file}")
        print("  Please ensure the file exists in the pdf_templates_static/multi directory")
        return 1
    
    print("\n--- Step 1: Parse YML File ---")
    try:
        parser = YMLParser()
        elements = parser.parse_yml(str(yml_file))
        print(f"[OK] Parsed {len(elements)} elements from {yml_file}")
        
        # Show first few elements
        print("\nFirst 3 elements:")
        for elem in elements[:3]:
            print(f"  [{elem.index}] '{elem.text}' at {elem.position}")
    
    except Exception as e:
        print(f"[ERROR] Failed to parse YML: {e}")
        return 1
    
    print("\n--- Step 2: Analyze PDF ---")
    try:
        analyzer = PDFAnalyzer()
        analysis = analyzer.analyze_pdf(str(pdf_file))
        print(f"[OK] Analyzed PDF: Firma {analysis.firma}, Seite {analysis.seite}")
        print(f"  Page size: {analysis.page_size['width']} x {analysis.page_size['height']}")
        print(f"  Design regions: {len(analysis.design_regions)}")
        print(f"  Safe zones: {len(analysis.safe_zones)}")
        print(f"  Color palette: {', '.join(analysis.color_palette)}")
    
    except Exception as e:
        print(f"[ERROR] Failed to analyze PDF: {e}")
        return 1
    
    print("\n--- Step 3: Calculate New Positions ---")
    try:
        calculator = PositionCalculator()
        
        # Show positioning rules
        print("\nPositioning Rules:")
        print(f"  Min margin: {POSITIONING_RULES['min_margin']} points")
        print(f"  Min spacing: {POSITIONING_RULES['min_spacing']} points")
        print(f"  Page size: {POSITIONING_RULES['page_width']} x {POSITIONING_RULES['page_height']}")
        print(f"  Grid: {POSITIONING_RULES['grid_columns']}x{POSITIONING_RULES['grid_rows']}")
        
        # Calculate positions using grid strategy
        print("\nCalculating positions using grid strategy...")
        new_positions = calculator.calculate_positions(
            elements,
            analysis,
            strategy="grid"
        )
        
        print(f"[OK] Calculated {len(new_positions)} new positions")
        
        # Show comparison for first few elements
        print("\nPosition comparison (first 3 elements):")
        for i in range(min(3, len(elements))):
            elem = elements[i]
            old_pos = elem.position
            new_pos = new_positions[i]
            
            print(f"\n  Element {i}: '{elem.text}'")
            print(f"    Old: ({old_pos[0]:.1f}, {old_pos[1]:.1f}) to ({old_pos[2]:.1f}, {old_pos[3]:.1f})")
            print(f"    New: ({new_pos[0]:.1f}, {new_pos[1]:.1f}) to ({new_pos[2]:.1f}, {new_pos[3]:.1f})")
            
            # Calculate movement
            dx = new_pos[0] - old_pos[0]
            dy = new_pos[1] - old_pos[1]
            print(f"    Movement: ({dx:+.1f}, {dy:+.1f})")
    
    except Exception as e:
        print(f"[ERROR] Failed to calculate positions: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n--- Step 4: Validate Positions ---")
    try:
        is_valid, errors = calculator.validate_positions(new_positions)
        
        if is_valid:
            print("[OK] All positions are valid!")
        else:
            print(f"[ERROR] Validation found {len(errors)} issue(s):")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
    
    except Exception as e:
        print(f"[ERROR] Failed to validate positions: {e}")
        return 1
    
    print("\n--- Step 5: Check Collisions ---")
    try:
        collisions = calculator.check_collisions(new_positions)
        
        if len(collisions) == 0:
            print("[OK] No collisions detected!")
        else:
            print(f"⚠ Found {len(collisions)} collision(s):")
            for collision in collisions[:5]:  # Show first 5
                elem1 = elements[collision.element1_index]
                elem2 = elements[collision.element2_index]
                print(f"  - Elements {collision.element1_index} and {collision.element2_index}:")
                print(f"    '{elem1.text}' overlaps with '{elem2.text}'")
                print(f"    Overlap area: {collision.overlap_area:.1f} sq pts")
            if len(collisions) > 5:
                print(f"  ... and {len(collisions) - 5} more")
    
    except Exception as e:
        print(f"[ERROR] Failed to check collisions: {e}")
        return 1
    
    print("\n--- Step 6: Element Importance ---")
    try:
        print("\nElement importance weights:")
        
        # Get importance for first few elements
        for elem in elements[:5]:
            importance = calculator.get_element_importance(elem)
            print(f"  '{elem.text}': {importance:.2f}")
    
    except Exception as e:
        print(f"[ERROR] Failed to calculate importance: {e}")
        return 1
    
    print("\n--- Summary ---")
    print(f"[OK] Successfully processed {len(elements)} elements")
    print(f"[OK] Generated {len(new_positions)} new positions")
    print(f"[OK] Validation: {'PASSED' if is_valid else 'FAILED'}")
    print(f"[OK] Collisions: {len(collisions)}")
    
    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
