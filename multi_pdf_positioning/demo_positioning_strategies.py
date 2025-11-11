"""
Demo script for positioning strategies.

This script demonstrates all 6 positioning strategies with real YML and PDF files.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.positioning_strategies import (
    select_strategy,
    apply_strategy
)
from multi_pdf_positioning.yml_parser import parse_yml
from multi_pdf_positioning.pdf_analyzer import analyze_pdf
from multi_pdf_positioning.position_calculator import PositionCalculator


def demo_strategy_for_firma(firma: int, seite: int = 1):
    """
    Demonstrate positioning strategy for a specific firma.
    
    Args:
        firma: Firma number (1-6)
        seite: Seite number (1-8)
    """
    print(f"\n{'=' * 60}")
    print(f"FIRMA {firma} - SEITE {seite}")
    print(f"{'=' * 60}")
    
    # File paths
    yml_file = Path(f"coords_multi/seite{seite}_f{firma}.yml")
    pdf_file = Path(f"pdf_templates_static/multi/multi_nt_{seite:02d}_f{firma}.pdf")
    
    # Check if files exist
    if not yml_file.exists():
        print(f"⚠ YML file not found: {yml_file}")
        return
    
    if not pdf_file.exists():
        print(f"⚠ PDF file not found: {pdf_file}")
        return
    
    try:
        # Parse YML
        print(f"\n1. Parsing YML file...")
        elements = parse_yml(str(yml_file))
        print(f"   ✓ Parsed {len(elements)} elements")
        
        # Analyze PDF
        print(f"\n2. Analyzing PDF template...")
        pdf_analysis = analyze_pdf(str(pdf_file))
        print(f"   ✓ Analyzed PDF: {pdf_analysis.page_size['width']}x{pdf_analysis.page_size['height']} points")
        print(f"   ✓ Color palette: {', '.join(pdf_analysis.color_palette[:3])}")
        
        # Select strategy
        print(f"\n3. Selecting positioning strategy...")
        strategy = select_strategy(firma, seite, pdf_analysis)
        print(f"   ✓ Strategy: {strategy.__class__.__name__}")
        
        # Apply strategy
        print(f"\n4. Applying strategy to elements...")
        positions = apply_strategy(firma, seite, elements, pdf_analysis)
        print(f"   ✓ Generated {len(positions)} positions")
        
        # Validate positions
        print(f"\n5. Validating positions...")
        calculator = PositionCalculator()
        is_valid, errors = calculator.validate_positions(positions)
        
        if is_valid:
            print(f"   ✓ All positions valid")
        else:
            print(f"   ✗ Validation errors:")
            for error in errors[:5]:
                print(f"     - {error}")
        
        # Show statistics
        print(f"\n6. Position Statistics:")
        
        # Calculate average position changes
        total_distance = 0
        for i, (elem, new_pos) in enumerate(zip(elements, positions)):
            old_x1, old_y1, old_x2, old_y2 = elem.position
            new_x1, new_y1, new_x2, new_y2 = new_pos
            
            # Calculate center point distance
            old_center_x = (old_x1 + old_x2) / 2
            old_center_y = (old_y1 + old_y2) / 2
            new_center_x = (new_x1 + new_x2) / 2
            new_center_y = (new_y1 + new_y2) / 2
            
            distance = ((new_center_x - old_center_x) ** 2 + 
                       (new_center_y - old_center_y) ** 2) ** 0.5
            total_distance += distance
        
        avg_distance = total_distance / len(elements) if elements else 0
        print(f"   Average position change: {avg_distance:.1f} points")
        
        # Show sample positions
        print(f"\n7. Sample Positions (first 5 elements):")
        for i in range(min(5, len(elements))):
            elem = elements[i]
            old_pos = elem.position
            new_pos = positions[i]
            
            print(f"\n   Element {i}: '{elem.text[:30]}...' " if len(elem.text) > 30 else f"\n   Element {i}: '{elem.text}'")
            print(f"     Old: ({old_pos[0]:.1f}, {old_pos[1]:.1f}) to ({old_pos[2]:.1f}, {old_pos[3]:.1f})")
            print(f"     New: ({new_pos[0]:.1f}, {new_pos[1]:.1f}) to ({new_pos[2]:.1f}, {new_pos[3]:.1f})")
        
        print(f"\n{'=' * 60}")
        print(f"✓ Demo completed successfully for Firma {firma}")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def demo_all_strategies():
    """Demonstrate all 6 positioning strategies."""
    print("\n" + "=" * 60)
    print("POSITIONING STRATEGIES DEMONSTRATION")
    print("=" * 60)
    
    strategy_descriptions = {
        1: "Header-Focused: Headers top-left, values bottom-right, customer info centered",
        2: "Center-Prominent: Headers centered, values top-right, customer info top-left",
        3: "Asymmetric-Modern: Headers top-right, values bottom-left, customer info right-middle",
        4: "Grid-Based: Elements distributed in 3x3 grid, values in center",
        5: "Diagonal-Flow: Elements flow diagonally from top-left to bottom-right",
        6: "Sidebar-Layout: Main info in left column, values in right column"
    }
    
    print("\nAvailable Strategies:")
    for firma, description in strategy_descriptions.items():
        print(f"  Firma {firma}: {description}")
    
    # Demo each firma
    for firma in range(1, 7):
        demo_strategy_for_firma(firma, seite=1)
    
    print("\n" + "=" * 60)
    print("ALL DEMONSTRATIONS COMPLETED")
    print("=" * 60)


def demo_single_firma():
    """Demo a single firma with user input."""
    print("\n" + "=" * 60)
    print("SINGLE FIRMA DEMONSTRATION")
    print("=" * 60)
    
    try:
        firma = int(input("\nEnter Firma number (1-6): "))
        if firma < 1 or firma > 6:
            print("Invalid firma number. Must be between 1 and 6.")
            return
        
        seite = int(input("Enter Seite number (1-8): "))
        if seite < 1 or seite > 8:
            print("Invalid seite number. Must be between 1 and 8.")
            return
        
        demo_strategy_for_firma(firma, seite)
        
    except ValueError:
        print("Invalid input. Please enter numbers only.")
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command line arguments provided
        if sys.argv[1] == "--all":
            demo_all_strategies()
        elif sys.argv[1] == "--firma":
            if len(sys.argv) >= 3:
                try:
                    firma = int(sys.argv[2])
                    seite = int(sys.argv[3]) if len(sys.argv) >= 4 else 1
                    demo_strategy_for_firma(firma, seite)
                except ValueError:
                    print("Usage: python demo_positioning_strategies.py --firma <firma> [seite]")
            else:
                print("Usage: python demo_positioning_strategies.py --firma <firma> [seite]")
        else:
            print("Usage:")
            print("  python demo_positioning_strategies.py --all")
            print("  python demo_positioning_strategies.py --firma <firma> [seite]")
            print("  python demo_positioning_strategies.py  (interactive mode)")
    else:
        # Interactive mode
        demo_single_firma()


if __name__ == "__main__":
    main()
