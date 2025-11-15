"""
Test suite for positioning strategies module.

This test file validates all 6 positioning strategies and the strategy
selection logic.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.positioning_strategies import (
    HeaderFocusedStrategy,
    CenterProminentStrategy,
    AsymmetricModernStrategy,
    GridBasedStrategy,
    DiagonalFlowStrategy,
    SidebarLayoutStrategy,
    select_strategy,
    apply_strategy
)
from multi_pdf_positioning.yml_parser import YMLElement, parse_yml
from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, analyze_pdf


def create_test_elements() -> list:
    """Create test YML elements for testing."""
    return [
        YMLElement(
            text="PHOTOVOLTAIK",
            position=(50.0, 750.0, 200.0, 780.0),
            font="Helvetica-Bold",
            font_size=24.0,
            color=0,
            index=0
        ),
        YMLElement(
            text="ANGEBOT",
            position=(50.0, 720.0, 150.0, 745.0),
            font="Helvetica-Bold",
            font_size=20.0,
            color=0,
            index=1
        ),
        YMLElement(
            text="kunde_vorname_und_nachname",
            position=(50.0, 680.0, 250.0, 700.0),
            font="Helvetica",
            font_size=14.0,
            color=0,
            index=2
        ),
        YMLElement(
            text="kWp_anlage_anlage",
            position=(400.0, 100.0, 500.0, 120.0),
            font="Helvetica-Bold",
            font_size=16.0,
            color=0,
            index=3
        ),
        YMLElement(
            text="Datum: 10.01.2025",
            position=(50.0, 650.0, 180.0, 670.0),
            font="Helvetica",
            font_size=12.0,
            color=0,
            index=4
        ),
    ]


def create_test_pdf_analysis(firma: int, seite: int) -> PDFAnalysis:
    """Create test PDF analysis object."""
    from multi_pdf_positioning.pdf_analyzer import DesignRegion, SafeZone
    
    return PDFAnalysis(
        firma=firma,
        seite=seite,
        page_size={"width": 595.0, "height": 842.0},
        design_regions=[
            DesignRegion(
                type="header",
                bounds={"x1": 0, "y1": 673.6, "x2": 595, "y2": 842},
                dominant_color="#007BFF",
                suggested_text_color="#FFFFFF"
            ),
            DesignRegion(
                type="content",
                bounds={"x1": 0, "y1": 84.2, "x2": 595, "y2": 673.6},
                dominant_color="#FFFFFF",
                suggested_text_color="#000000"
            ),
        ],
        visual_elements=[],
        safe_zones=[
            SafeZone(x1=50, y1=50, x2=545, y2=792)
        ],
        color_palette=["#007BFF", "#FFFFFF", "#F8F9FA", "#000000"]
    )


def validate_positions(
    positions: list,
    num_elements: int,
    page_width: float = 595.0,
    page_height: float = 842.0
) -> tuple:
    """
    Validate that positions meet basic requirements.
    
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Check correct number of positions
    if len(positions) != num_elements:
        errors.append(
            f"Expected {num_elements} positions, got {len(positions)}"
        )
        return False, errors
    
    # Check each position
    for i, pos in enumerate(positions):
        if pos is None:
            errors.append(f"Position {i} is None")
            continue
        
        x1, y1, x2, y2 = pos
        
        # Check bounds
        if x1 < 0 or x1 >= page_width:
            errors.append(f"Position {i}: x1 ({x1}) out of bounds")
        if y1 < 0 or y1 >= page_height:
            errors.append(f"Position {i}: y1 ({y1}) out of bounds")
        if x2 <= x1 or x2 > page_width:
            errors.append(f"Position {i}: x2 ({x2}) invalid")
        if y2 <= y1 or y2 > page_height:
            errors.append(f"Position {i}: y2 ({y2}) invalid")
    
    return len(errors) == 0, errors


def test_strategy(
    strategy_class,
    strategy_name: str,
    firma: int
) -> bool:
    """Test a single positioning strategy."""
    print(f"\n--- Testing {strategy_name} (Firma {firma}) ---")
    
    try:
        # Create test data
        elements = create_test_elements()
        pdf_analysis = create_test_pdf_analysis(firma, 1)
        
        # Create strategy instance
        strategy = strategy_class(pdf_analysis)
        
        # Apply strategy
        positions = strategy.apply(elements)
        
        # Validate positions
        is_valid, errors = validate_positions(positions, len(elements))
        
        if is_valid:
            print(f"{strategy_name}: All positions valid")
            
            # Show sample positions
            print(f"  Sample positions:")
            for i, pos in enumerate(positions[:3]):
                x1, y1, x2, y2 = pos
                print(f"    Element {i}: ({x1:.1f}, {y1:.1f}) to ({x2:.1f}, {y2:.1f})")
            
            return True
        else:
            print(f"{strategy_name}: Validation failed")
            for error in errors[:5]:
                print(f"    - {error}")
            return False
    
    except Exception as e:
        print(f"{strategy_name}: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_strategies():
    """Test all positioning strategies."""
    print("\n=== Testing All Positioning Strategies ===")
    
    strategies = [
        (HeaderFocusedStrategy, "Header-Focused", 1),
        (CenterProminentStrategy, "Center-Prominent", 2),
        (AsymmetricModernStrategy, "Asymmetric-Modern", 3),
        (GridBasedStrategy, "Grid-Based", 4),
        (DiagonalFlowStrategy, "Diagonal-Flow", 5),
        (SidebarLayoutStrategy, "Sidebar-Layout", 6),
    ]
    
    results = []
    for strategy_class, name, firma in strategies:
        result = test_strategy(strategy_class, name, firma)
        results.append((name, result))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} strategies passed")
    
    return passed == total


def test_strategy_selection():
    """Test strategy selection logic."""
    print("\n=== Testing Strategy Selection ===")
    
    try:
        elements = create_test_elements()
        
        # Test each firma
        for firma in range(1, 7):
            pdf_analysis = create_test_pdf_analysis(firma, 1)
            
            # Test select_strategy
            strategy = select_strategy(firma, 1, pdf_analysis)
            print(f"  Firma {firma}: {strategy.__class__.__name__}")
            
            # Test apply_strategy convenience function
            positions = apply_strategy(firma, 1, elements, pdf_analysis)
            is_valid, _ = validate_positions(positions, len(elements))
            
            if not is_valid:
                print(f"    Invalid positions for firma {firma}")
                return False
        
        # Test invalid firma
        try:
            select_strategy(7, 1, pdf_analysis)
            print("  Should have raised ValueError for invalid firma")
            return False
        except ValueError:
            print("  Correctly raises ValueError for invalid firma")
        
        print("\nStrategy selection tests passed")
        return True
    
    except Exception as e:
        print(f"\nStrategy selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_real_files():
    """Test strategies with real YML and PDF files if available."""
    print("\n=== Testing with Real Files (if available) ===")
    
    # Check if files exist
    yml_dir = Path("coords_multi")
    pdf_dir = Path("pdf_templates_static/multi")
    
    if not yml_dir.exists():
        print("  ⚠ coords_multi directory not found, skipping real file tests")
        return True
    
    if not pdf_dir.exists():
        print("  ⚠ PDF directory not found, skipping real file tests")
        return True
    
    try:
        # Test with Firma 1, Seite 1
        yml_file = yml_dir / "seite1_f1.yml"
        pdf_file = pdf_dir / "multi_nt_01_f1.pdf"
        
        if yml_file.exists() and pdf_file.exists():
            print(f"  Testing with {yml_file.name} and {pdf_file.name}")
            
            # Parse YML
            elements = parse_yml(str(yml_file))
            print(f"    Parsed {len(elements)} elements from YML")
            
            # Analyze PDF
            pdf_analysis = analyze_pdf(str(pdf_file))
            print(f"    Analyzed PDF: Firma {pdf_analysis.firma}, Seite {pdf_analysis.seite}")
            
            # Apply strategy
            positions = apply_strategy(
                pdf_analysis.firma,
                pdf_analysis.seite,
                elements,
                pdf_analysis
            )
            
            # Validate
            is_valid, errors = validate_positions(
                positions,
                len(elements),
                pdf_analysis.page_size["width"],
                pdf_analysis.page_size["height"]
            )
            
            if is_valid:
                print(f"    Generated {len(positions)} valid positions")
                return True
            else:
                print(f"    Validation failed:")
                for error in errors[:5]:
                    print(f"      - {error}")
                return False
        else:
            print("  ⚠ Test files not found, skipping")
            return True
    
    except Exception as e:
        print(f"  Real file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("POSITIONING STRATEGIES TEST SUITE")
    print("=" * 60)
    
    # Run tests
    test1 = test_all_strategies()
    test2 = test_strategy_selection()
    test3 = test_with_real_files()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print("\nALL TESTS PASSED")
        return 0
    else:
        print("\nSOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
