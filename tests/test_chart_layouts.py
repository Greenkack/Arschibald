"""
Unit Tests for Chart Layout Generation

Tests the chart page generation with different layouts (1, 2, 4 per page)
and validates page count calculations.

Requirements: 12.3, 17.1, 17.2
"""

from PIL import Image
from pypdf import PdfReader
from extended_pdf_generator import ChartPageGenerator
import sys
import os
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_mock_chart_bytes(width=800, height=600, color='lightblue') -> bytes:
    """Creates mock chart image bytes for testing."""
    img = Image.new('RGB', (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_one_chart_per_page_layout():
    """Test one chart per page layout with various chart counts."""
    print("\n=== Test 1: One Chart Per Page Layout ===")

    test_cases = [
        (1, 1, "Single chart"),
        (3, 3, "Three charts"),
        (5, 5, "Five charts"),
        (10, 10, "Ten charts")
    ]

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for num_charts, expected_pages, description in test_cases:
        # Create mock analysis results
        analysis_results = {}
        chart_keys = []
        for i in range(num_charts):
            key = f'chart_{i}_bytes'
            analysis_results[key] = create_mock_chart_bytes()
            chart_keys.append(key)

        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout='one_per_page',
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)

        assert pdf_bytes, f"PDF should be generated for {description}"

        reader = PdfReader(io.BytesIO(pdf_bytes))
        actual_pages = len(reader.pages)

        assert actual_pages == expected_pages, \
            f"{description}: Expected {expected_pages} pages, got {actual_pages}"

        print(f"✓ {description}: {num_charts} charts → {actual_pages} pages")

    print("✓ One chart per page layout tests passed")
    return True


def test_two_charts_per_page_layout():
    """Test two charts per page layout with various chart counts."""
    print("\n=== Test 2: Two Charts Per Page Layout ===")

    test_cases = [
        (1, 1, "Single chart (1 page)"),
        (2, 1, "Two charts (1 page)"),
        (3, 2, "Three charts (2 pages: 2+1)"),
        (4, 2, "Four charts (2 pages: 2+2)"),
        (5, 3, "Five charts (3 pages: 2+2+1)"),
        (6, 3, "Six charts (3 pages: 2+2+2)"),
        (7, 4, "Seven charts (4 pages: 2+2+2+1)"),
        (10, 5, "Ten charts (5 pages: 2+2+2+2+2)")
    ]

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for num_charts, expected_pages, description in test_cases:
        # Create mock analysis results
        analysis_results = {}
        chart_keys = []
        for i in range(num_charts):
            key = f'chart_{i}_bytes'
            analysis_results[key] = create_mock_chart_bytes()
            chart_keys.append(key)

        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout='two_per_page',
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)

        assert pdf_bytes, f"PDF should be generated for {description}"

        reader = PdfReader(io.BytesIO(pdf_bytes))
        actual_pages = len(reader.pages)

        assert actual_pages == expected_pages, \
            f"{description}: Expected {expected_pages} pages, got {actual_pages}"

        print(f"✓ {description}: {num_charts} charts → {actual_pages} pages")

    print("✓ Two charts per page layout tests passed")
    return True


def test_four_charts_per_page_layout():
    """Test four charts per page layout with various chart counts."""
    print("\n=== Test 3: Four Charts Per Page Layout ===")

    test_cases = [
        (1, 1, "Single chart (1 page)"),
        (2, 1, "Two charts (1 page)"),
        (3, 1, "Three charts (1 page)"),
        (4, 1, "Four charts (1 page: 4)"),
        (5, 2, "Five charts (2 pages: 4+1)"),
        (8, 2, "Eight charts (2 pages: 4+4)"),
        (9, 3, "Nine charts (3 pages: 4+4+1)"),
        (12, 3, "Twelve charts (3 pages: 4+4+4)"),
        (15, 4, "Fifteen charts (4 pages: 4+4+4+3)"),
        (16, 4, "Sixteen charts (4 pages: 4+4+4+4)")
    ]

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for num_charts, expected_pages, description in test_cases:
        # Create mock analysis results
        analysis_results = {}
        chart_keys = []
        for i in range(num_charts):
            key = f'chart_{i}_bytes'
            analysis_results[key] = create_mock_chart_bytes()
            chart_keys.append(key)

        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout='four_per_page',
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)

        assert pdf_bytes, f"PDF should be generated for {description}"

        reader = PdfReader(io.BytesIO(pdf_bytes))
        actual_pages = len(reader.pages)

        assert actual_pages == expected_pages, \
            f"{description}: Expected {expected_pages} pages, got {actual_pages}"

        print(f"✓ {description}: {num_charts} charts → {actual_pages} pages")

    print("✓ Four charts per page layout tests passed")
    return True


def test_page_count_calculation_formula():
    """Test that page count calculation follows correct formula."""
    print("\n=== Test 4: Page Count Calculation Formula ===")

    import math

    layouts = {
        'one_per_page': 1,
        'two_per_page': 2,
        'four_per_page': 4
    }

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for layout_name, charts_per_page in layouts.items():
        print(
            f"\n  Testing {layout_name} (formula: ceil(n/{charts_per_page})):")

        for num_charts in [1, 2, 3, 5, 7, 10, 15, 20]:
            # Calculate expected pages using formula
            expected_pages = math.ceil(num_charts / charts_per_page)

            # Create mock data
            analysis_results = {}
            chart_keys = []
            for i in range(num_charts):
                key = f'chart_{i}_bytes'
                analysis_results[key] = create_mock_chart_bytes()
                chart_keys.append(key)

            generator = ChartPageGenerator(
                analysis_results=analysis_results,
                layout=layout_name,
                theme=theme
            )

            pdf_bytes = generator.generate(chart_keys)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            actual_pages = len(reader.pages)

            assert actual_pages == expected_pages, \
                f"{layout_name} with {num_charts} charts: " \
                f"Expected {expected_pages} pages, got {actual_pages}"

            print(f"    {num_charts} charts → {actual_pages} pages ✓")

    print("\n✓ Page count calculation formula verified for all layouts")
    return True


def test_layout_comparison():
    """Test that different layouts produce different page counts for same charts."""
    print("\n=== Test 5: Layout Comparison ===")

    num_charts = 12

    # Create mock analysis results
    analysis_results = {}
    chart_keys = []
    for i in range(num_charts):
        key = f'chart_{i}_bytes'
        analysis_results[key] = create_mock_chart_bytes()
        chart_keys.append(key)

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    layouts = ['one_per_page', 'two_per_page', 'four_per_page']
    expected_pages = [12, 6, 3]  # For 12 charts

    results = []

    for layout, expected in zip(layouts, expected_pages):
        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout=layout,
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        actual_pages = len(reader.pages)

        assert actual_pages == expected, \
            f"{layout}: Expected {expected} pages, got {actual_pages}"

        results.append((layout, actual_pages))
        print(f"  {layout}: {actual_pages} pages")

    # Verify that more charts per page = fewer pages
    assert results[0][1] > results[1][1] > results[2][1], \
        "More charts per page should result in fewer total pages"

    print(f"\n✓ Layout comparison verified: {num_charts} charts")
    print(f"  - one_per_page: {results[0][1]} pages")
    print(f"  - two_per_page: {results[1][1]} pages")
    print(f"  - four_per_page: {results[2][1]} pages")

    return True


def test_empty_chart_list():
    """Test handling of empty chart list."""
    print("\n=== Test 6: Empty Chart List ===")

    analysis_results = {}
    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for layout in ['one_per_page', 'two_per_page', 'four_per_page']:
        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout=layout,
            theme=theme
        )

        pdf_bytes = generator.generate([])

        assert pdf_bytes == b'', f"{layout}: Empty list should return empty bytes"
        print(f"  ✓ {layout}: Empty list handled correctly")

    print("✓ Empty chart list tests passed")
    return True


def test_missing_charts_in_analysis_results():
    """Test handling when requested charts are not in analysis_results."""
    print("\n=== Test 7: Missing Charts in Analysis Results ===")

    # Analysis results with only 2 charts
    analysis_results = {
        'chart_1_bytes': create_mock_chart_bytes(),
        'chart_2_bytes': create_mock_chart_bytes()
    }

    # Request 4 charts (2 exist, 2 don't)
    chart_keys = [
        'chart_1_bytes',
        'chart_2_bytes',
        'chart_3_bytes',
        'chart_4_bytes']

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF should be generated with available charts"

    reader = PdfReader(io.BytesIO(pdf_bytes))
    actual_pages = len(reader.pages)

    # Should only generate pages for the 2 available charts
    assert actual_pages == 2, f"Expected 2 pages (only available charts), got {actual_pages}"

    print(f"✓ Missing charts handled gracefully")
    print(f"  - Requested: {len(chart_keys)} charts")
    print(f"  - Available: 2 charts")
    print(f"  - Generated: {actual_pages} pages")

    return True


def test_large_chart_count():
    """Test handling of large number of charts."""
    print("\n=== Test 8: Large Chart Count ===")

    num_charts = 50

    # Create mock analysis results
    analysis_results = {}
    chart_keys = []
    for i in range(num_charts):
        key = f'chart_{i}_bytes'
        analysis_results[key] = create_mock_chart_bytes()
        chart_keys.append(key)

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    # Test with four_per_page layout (most efficient)
    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='four_per_page',
        theme=theme
    )

    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF should be generated for large chart count"

    reader = PdfReader(io.BytesIO(pdf_bytes))
    actual_pages = len(reader.pages)

    import math
    expected_pages = math.ceil(num_charts / 4)

    assert actual_pages == expected_pages, \
        f"Expected {expected_pages} pages, got {actual_pages}"

    print(f"✓ Large chart count handled successfully")
    print(f"  - Charts: {num_charts}")
    print(f"  - Layout: four_per_page")
    print(f"  - Pages: {actual_pages}")
    print(f"  - PDF size: {len(pdf_bytes):,} bytes")

    return True


def test_layout_with_different_chart_sizes():
    """Test layouts with charts of different sizes."""
    print("\n=== Test 9: Different Chart Sizes ===")

    # Create charts with different dimensions
    analysis_results = {
        'small_chart_bytes': create_mock_chart_bytes(400, 300, 'lightblue'),
        'medium_chart_bytes': create_mock_chart_bytes(800, 600, 'lightgreen'),
        'large_chart_bytes': create_mock_chart_bytes(1200, 900, 'lightcoral'),
        'wide_chart_bytes': create_mock_chart_bytes(1600, 400, 'lightyellow')
    }

    chart_keys = list(analysis_results.keys())
    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    for layout in ['one_per_page', 'two_per_page', 'four_per_page']:
        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout=layout,
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)

        assert pdf_bytes, f"PDF should be generated for {layout}"

        reader = PdfReader(io.BytesIO(pdf_bytes))
        actual_pages = len(reader.pages)

        print(
            f"  ✓ {layout}: {
                len(chart_keys)} charts (various sizes) → {actual_pages} pages")

    print("✓ Different chart sizes handled correctly")
    return True


def test_invalid_layout_fallback():
    """Test fallback to default layout when invalid layout is specified."""
    print("\n=== Test 10: Invalid Layout Fallback ===")

    num_charts = 6

    # Create mock analysis results
    analysis_results = {}
    chart_keys = []
    for i in range(num_charts):
        key = f'chart_{i}_bytes'
        analysis_results[key] = create_mock_chart_bytes()
        chart_keys.append(key)

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    # Use invalid layout
    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='invalid_layout',
        theme=theme
    )

    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF should be generated with fallback layout"

    reader = PdfReader(io.BytesIO(pdf_bytes))
    actual_pages = len(reader.pages)

    # Should fall back to one_per_page (6 charts = 6 pages)
    assert actual_pages == num_charts, \
        f"Should fall back to one_per_page: Expected {num_charts} pages, got {actual_pages}"

    print(f"✓ Invalid layout handled with fallback")
    print(f"  - Requested layout: 'invalid_layout'")
    print(f"  - Fallback layout: 'one_per_page'")
    print(f"  - Charts: {num_charts}")
    print(f"  - Pages: {actual_pages}")

    return True


def test_page_count_edge_cases():
    """Test edge cases for page count calculations."""
    print("\n=== Test 11: Page Count Edge Cases ===")

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    edge_cases = [
        # (num_charts, layout, expected_pages, description)
        (0, 'one_per_page', 0, "Zero charts"),
        (1, 'two_per_page', 1, "One chart with two_per_page"),
        (1, 'four_per_page', 1, "One chart with four_per_page"),
        (2, 'four_per_page', 1, "Two charts with four_per_page"),
        (3, 'four_per_page', 1, "Three charts with four_per_page"),
        (5, 'four_per_page', 2, "Five charts with four_per_page (4+1)"),
    ]

    for num_charts, layout, expected_pages, description in edge_cases:
        if num_charts == 0:
            # Special case: empty list
            generator = ChartPageGenerator(
                analysis_results={},
                layout=layout,
                theme=theme
            )
            pdf_bytes = generator.generate([])
            assert pdf_bytes == b'', f"{description}: Should return empty bytes"
            print(f"  ✓ {description}: empty bytes")
        else:
            # Create mock data
            analysis_results = {}
            chart_keys = []
            for i in range(num_charts):
                key = f'chart_{i}_bytes'
                analysis_results[key] = create_mock_chart_bytes()
                chart_keys.append(key)

            generator = ChartPageGenerator(
                analysis_results=analysis_results,
                layout=layout,
                theme=theme
            )

            pdf_bytes = generator.generate(chart_keys)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            actual_pages = len(reader.pages)

            assert actual_pages == expected_pages, \
                f"{description}: Expected {expected_pages} pages, got {actual_pages}"

            print(f"  ✓ {description}: {actual_pages} pages")

    print("✓ All edge cases handled correctly")
    return True


def run_all_tests():
    """Run all chart layout generation tests."""
    print("=" * 70)
    print("CHART LAYOUT GENERATION TEST SUITE")
    print("Testing: Requirements 12.3, 17.1, 17.2")
    print("=" * 70)

    test_functions = [
        test_one_chart_per_page_layout,
        test_two_charts_per_page_layout,
        test_four_charts_per_page_layout,
        test_page_count_calculation_formula,
        test_layout_comparison,
        test_empty_chart_list,
        test_missing_charts_in_analysis_results,
        test_large_chart_count,
        test_layout_with_different_chart_sizes,
        test_invalid_layout_fallback,
        test_page_count_edge_cases
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {test_func.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {test_func.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(test_functions)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)

    if passed == len(test_functions):
        print("✓ ALL TESTS PASSED - Task 18.3 Complete")
    else:
        print("✗ SOME TESTS FAILED - Task 18.3 Needs Work")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
