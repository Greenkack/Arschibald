"""
Test script for PDF Analyzer module

This script tests all functionality of the PDF analyzer including:
- Single PDF analysis
- Batch analysis
- Data extraction
- JSON export
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer, analyze_pdf
from multi_pdf_positioning.config import PDF_DIR


def test_single_pdf_analysis():
    """Test analyzing a single PDF."""
    print("\n" + "=" * 60)
    print("Test 1: Single PDF Analysis")
    print("=" * 60)

    pdf_path = PDF_DIR / "multi_nt_01_f1.pdf"

    try:
        analysis = analyze_pdf(str(pdf_path))

        assert analysis.firma == 1, "Firma should be 1"
        assert analysis.seite == 1, "Seite should be 1"
        assert analysis.page_size["width"] > 0, "Width should be positive"
        assert analysis.page_size["height"] > 0, "Height should be positive"
        assert len(analysis.design_regions) > 0, "Should have design regions"
        assert len(analysis.safe_zones) > 0, "Should have safe zones"
        assert len(analysis.color_palette) > 0, "Should have color palette"

        print("[OK] Single PDF analysis successful")
        print(f"  Firma: {analysis.firma}")
        print(f"  Seite: {analysis.seite}")
        print(f"  Page size: {analysis.page_size}")
        print(f"  Design regions: {len(analysis.design_regions)}")
        print(f"  Safe zones: {len(analysis.safe_zones)}")
        print(f"  Colors: {len(analysis.color_palette)}")

        return True

    except Exception as e:
        print(f"[FAIL] Single PDF analysis failed: {e}")
        return False


def test_multiple_firmen():
    """Test that different firmen have different color palettes."""
    print("\n" + "=" * 60)
    print("Test 2: Multiple Firmen Color Palettes")
    print("=" * 60)

    try:
        analyzer = PDFAnalyzer(pdf_dir=str(PDF_DIR))

        palettes = {}
        for firma in [1, 2, 3]:
            if f != 0:
                pdf_path = PDF_DIR / f"multi_nt_01_f{firma}.pdf"
            else:
                pdf_path = 0.0
            analysis = analyzer.analyze_pdf(str(pdf_path))
            palettes[firma] = analysis.color_palette

        # Check that palettes are different
        assert palettes[1] != palettes[2], "F1 and F2 should differ"
        assert palettes[2] != palettes[3], "F2 and F3 should differ"
        assert palettes[1] != palettes[3], "F1 and F3 should differ"

        print("Color palettes are unique per firma")
        for firma, palette in palettes.items():
            print(f"  Firma {firma}: {palette[0]}")

        return True

    except Exception as e:
        print(f"[FAIL] Multiple firmen test failed: {e}")
        return False


def test_batch_analysis():
    """Test batch analysis of multiple PDFs."""
    print("\n" + "=" * 60)
    print("Test 3: Batch Analysis")
    print("=" * 60)

    try:
        analyzer = PDFAnalyzer(pdf_dir=str(PDF_DIR))

        # Analyze subset (first 2 firmen, first 3 seiten)
        results = analyzer.analyze_all_pdfs(
            firmen=[1, 2],
            seiten=[1, 2, 3]
        )

        expected_count = 2 * 3  # 6 PDFs
        assert len(results) == expected_count, \
            f"Should analyze {expected_count} PDFs"

        # Check that we can filter by firma
        firma1_results = analyzer.get_analysis_by_firma(1)
        assert len(firma1_results) == 3, "Should have 3 results for firma 1"

        # Check that we can filter by seite
        seite1_results = analyzer.get_analysis_by_seite(1)
        assert len(seite1_results) == 2, "Should have 2 results for seite 1"

        print("Batch analysis successful")
        print(f"  Total analyzed: {len(results)}")
        print(f"  Firma 1 results: {len(firma1_results)}")
        print(f"  Seite 1 results: {len(seite1_results)}")

        return True

    except Exception as e:
        print(f"[FAIL] Batch analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safe_zones():
    """Test that safe zones are properly defined."""
    print("\n" + "=" * 60)
    print("Test 4: Safe Zones Validation")
    print("=" * 60)

    try:
        pdf_path = PDF_DIR / "multi_nt_01_f1.pdf"
        analysis = analyze_pdf(str(pdf_path))

        for i, zone in enumerate(analysis.safe_zones):
            # Check that zones have positive dimensions
            width = zone.x2 - zone.x1
            height = zone.y2 - zone.y1

            assert width > 0, f"Zone {i} width should be positive"
            assert height > 0, f"Zone {i} height should be positive"

            # Check that zones are within page bounds
            assert zone.x1 >= 0, f"Zone {i} x1 should be >= 0"
            assert zone.y1 >= 0, f"Zone {i} y1 should be >= 0"
            assert zone.x2 <= analysis.page_size["width"], \
                f"Zone {i} x2 should be <= page width"
            assert zone.y2 <= analysis.page_size["height"], \
                f"Zone {i} y2 should be <= page height"

        print("Safe zones validation successful")
        print(f"  Total safe zones: {len(analysis.safe_zones)}")
        for i, zone in enumerate(analysis.safe_zones):
            width = zone.x2 - zone.x1
            height = zone.y2 - zone.y1
            print(f"  Zone {i+1}: {width:.1f} x {height:.1f} points")

        return True

    except Exception as e:
        print(f"[FAIL] Safe zones validation failed: {e}")
        return False


def test_json_export():
    """Test JSON export functionality."""
    print("\n" + "=" * 60)
    print("Test 5: JSON Export")
    print("=" * 60)

    try:
        analyzer = PDFAnalyzer(pdf_dir=str(PDF_DIR))

        # Analyze a few PDFs
        analyzer.analyze_all_pdfs(firmen=[1], seiten=[1, 2])

        # Export to JSON
        output_path = Path(__file__).parent / "output" / "test_analysis.json"
        analyzer.save_analysis_results(str(output_path), include_summary=True)

        # Verify file was created
        assert output_path.exists(), "JSON file should be created"

        # Read and validate JSON
        import json
        with open(output_path, 'r') as f:
            data = json.load(f)

        assert "total_pdfs" in data, "Should have total_pdfs"
        assert "analyses" in data, "Should have analyses"
        assert "summary" in data, "Should have summary"
        assert data["total_pdfs"] == 2, "Should have 2 PDFs"

        print("JSON export successful")
        print(f"  Output file: {output_path}")
        print(f"  Total PDFs: {data['total_pdfs']}")
        print(f"  Summary keys: {list(data['summary'].keys())}")

        return True

    except Exception as e:
        print(f"[FAIL] JSON export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PDF Analyzer Test Suite")
    print("=" * 60)

    tests = [
        test_single_pdf_analysis,
        test_multiple_firmen,
        test_batch_analysis,
        test_safe_zones,
        test_json_export
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[FAIL] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
