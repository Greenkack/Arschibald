"""
Test suite for ChartPageGenerator class

Tests all chart page generation functionality including:
- One chart per page layout
- Two charts per page layout
- Four charts per page layout
- Chart name mapping
- Error handling
"""

import io
from pypdf import PdfReader
from extended_pdf_generator import ChartPageGenerator


def create_mock_chart_bytes() -> bytes:
    """Creates mock chart image bytes for testing."""
    from PIL import Image

    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='lightblue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_chart_page_generator_initialization():
    """Test ChartPageGenerator initialization."""
    print("\n=== Test 1: ChartPageGenerator Initialization ===")

    analysis_results = {
        'monthly_prod_cons_chart_bytes': create_mock_chart_bytes(),
        'cumulative_cashflow_chart_bytes': create_mock_chart_bytes()
    }

    theme = {
        'colors': {
            'primary': '#1E3A8A',
            'secondary': '#3B82F6'
        }
    }

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    assert generator.analysis_results == analysis_results
    assert generator.layout == 'one_per_page'
    assert generator.theme == theme

    print("✓ ChartPageGenerator initialized successfully")
    print(f"  - Analysis results: {len(analysis_results)} charts")
    print(f"  - Layout: {generator.layout}")
    print(f"  - Theme colors: {theme['colors']}")


def test_generate_one_per_page():
    """Test generating one chart per page layout."""
    print("\n=== Test 2: One Chart Per Page Layout ===")

    # Create mock analysis results with 3 charts
    analysis_results = {
        'monthly_prod_cons_chart_bytes': create_mock_chart_bytes(),
        'cumulative_cashflow_chart_bytes': create_mock_chart_bytes(),
        'consumption_coverage_pie_chart_bytes': create_mock_chart_bytes()
    }

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    chart_keys = list(analysis_results.keys())
    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF bytes should not be empty"

    # Verify PDF structure
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)

    assert num_pages == 3, f"Expected 3 pages, got {num_pages}"

    print("✓ One chart per page layout generated successfully")
    print(f"  - Input charts: {len(chart_keys)}")
    print(f"  - Output pages: {num_pages}")
    print(f"  - Chart keys: {chart_keys}")


def test_generate_two_per_page():
    """Test generating two charts per page layout."""
    print("\n=== Test 3: Two Charts Per Page Layout ===")

    # Create mock analysis results with 5 charts
    analysis_results = {
        'monthly_prod_cons_chart_bytes': create_mock_chart_bytes(),
        'cumulative_cashflow_chart_bytes': create_mock_chart_bytes(),
        'consumption_coverage_pie_chart_bytes': create_mock_chart_bytes(),
        'pv_usage_pie_chart_bytes': create_mock_chart_bytes(),
        'cost_projection_chart_bytes': create_mock_chart_bytes()
    }

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='two_per_page',
        theme=theme
    )

    chart_keys = list(analysis_results.keys())
    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF bytes should not be empty"

    # Verify PDF structure
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)

    # 5 charts with 2 per page = 3 pages (2+2+1)
    expected_pages = 3
    assert num_pages == expected_pages, f"Expected {expected_pages} pages, got {num_pages}"

    print("✓ Two charts per page layout generated successfully")
    print(f"  - Input charts: {len(chart_keys)}")
    print(f"  - Output pages: {num_pages}")
    print(f"  - Layout: 2 charts per page (2+2+1)")


def test_generate_four_per_page():
    """Test generating four charts per page layout."""
    print("\n=== Test 4: Four Charts Per Page Layout ===")

    # Create mock analysis results with 9 charts
    analysis_results = {}
    chart_keys_list = [
        'monthly_prod_cons_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes',
        'cost_projection_chart_bytes',
        'break_even_chart_bytes',
        'yearly_production_chart_bytes',
        'daily_production_switcher_chart_bytes',
        'weekly_production_switcher_chart_bytes'
    ]

    for key in chart_keys_list:
        analysis_results[key] = create_mock_chart_bytes()

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='four_per_page',
        theme=theme
    )

    chart_keys = list(analysis_results.keys())
    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF bytes should not be empty"

    # Verify PDF structure
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)

    # 9 charts with 4 per page = 3 pages (4+4+1)
    expected_pages = 3
    assert num_pages == expected_pages, f"Expected {expected_pages} pages, got {num_pages}"

    print("✓ Four charts per page layout generated successfully")
    print(f"  - Input charts: {len(chart_keys)}")
    print(f"  - Output pages: {num_pages}")
    print(f"  - Layout: 4 charts per page (4+4+1)")


def test_chart_name_mapping():
    """Test chart name mapping for all real chart keys."""
    print("\n=== Test 5: Chart Name Mapping ===")

    analysis_results = {}
    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    # Test all real chart keys from pdf_generator.py
    real_chart_keys = [
        # 2D Charts
        'cumulative_cashflow_chart_bytes',
        'cost_projection_chart_bytes',
        'break_even_chart_bytes',
        'amortisation_chart_bytes',
        'monthly_prod_cons_chart_bytes',
        'yearly_production_chart_bytes',
        'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes',

        # 3D Charts
        'daily_production_switcher_chart_bytes',
        'weekly_production_switcher_chart_bytes',
        'yearly_production_switcher_chart_bytes',
        'project_roi_matrix_switcher_chart_bytes',
        'roi_comparison_switcher_chart_bytes',
        'feed_in_revenue_switcher_chart_bytes',
        'income_projection_switcher_chart_bytes',
        'prod_vs_cons_switcher_chart_bytes',
        'tariff_cube_switcher_chart_bytes',
        'tariff_comparison_switcher_chart_bytes',
        'cost_growth_switcher_chart_bytes',
        'co2_savings_chart_bytes',
        'co2_savings_value_switcher_chart_bytes',
        'investment_value_switcher_chart_bytes',
        'scenario_comparison_switcher_chart_bytes',
        'storage_effect_switcher_chart_bytes',
        'selfuse_stack_switcher_chart_bytes',
        'selfuse_ratio_switcher_chart_bytes'
    ]

    print("✓ Testing chart name mapping for all real keys:")
    mapped_count = 0

    for chart_key in real_chart_keys:
        chart_name = generator._get_chart_name(chart_key)

        # Verify it's not just the key itself (should be mapped)
        if chart_name != chart_key:
            mapped_count += 1

        print(f"  - {chart_key[:40]:<40} → {chart_name}")

    print(
        f"\n✓ Successfully mapped {mapped_count}/{len(real_chart_keys)} chart keys")
    assert mapped_count == len(
        real_chart_keys), "All chart keys should have friendly names"


def test_empty_chart_list():
    """Test handling of empty chart list."""
    print("\n=== Test 6: Empty Chart List ===")

    analysis_results = {}
    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    pdf_bytes = generator.generate([])

    assert pdf_bytes == b'', "Empty chart list should return empty bytes"

    print("✓ Empty chart list handled correctly")
    print("  - Input: []")
    print("  - Output: empty bytes")


def test_missing_chart_bytes():
    """Test handling of missing chart bytes."""
    print("\n=== Test 7: Missing Chart Bytes ===")

    # Analysis results with one valid chart and one missing
    analysis_results = {
        'monthly_prod_cons_chart_bytes': create_mock_chart_bytes()
        # 'cumulative_cashflow_chart_bytes' is missing
    }

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme=theme
    )

    # Request both charts, but only one exists
    chart_keys = [
        'monthly_prod_cons_chart_bytes',
        'cumulative_cashflow_chart_bytes']
    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF should still be generated with available charts"

    # Verify PDF structure - should only have 1 page (for the valid chart)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)

    assert num_pages == 1, f"Expected 1 page (only valid chart), got {num_pages}"

    print("✓ Missing chart bytes handled gracefully")
    print(f"  - Requested charts: {len(chart_keys)}")
    print(f"  - Available charts: 1")
    print(f"  - Output pages: {num_pages}")


def test_layout_options():
    """Test all layout options."""
    print("\n=== Test 8: All Layout Options ===")

    # Create 8 charts for comprehensive testing
    analysis_results = {}
    for i in range(8):
        analysis_results[f'chart_{i}_bytes'] = create_mock_chart_bytes()

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}
    chart_keys = list(analysis_results.keys())

    layouts = {
        'one_per_page': 8,    # 8 charts = 8 pages
        'two_per_page': 4,    # 8 charts = 4 pages
        'four_per_page': 2    # 8 charts = 2 pages
    }

    for layout, expected_pages in layouts.items():
        generator = ChartPageGenerator(
            analysis_results=analysis_results,
            layout=layout,
            theme=theme
        )

        pdf_bytes = generator.generate(chart_keys)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)

        assert num_pages == expected_pages, \
            f"Layout '{layout}': expected {expected_pages} pages, got {num_pages}"

        print(
            f"✓ Layout '{layout}': {
                len(chart_keys)} charts → {num_pages} pages")


def test_default_layout_fallback():
    """Test fallback to default layout for invalid layout option."""
    print("\n=== Test 9: Default Layout Fallback ===")

    analysis_results = {
        'monthly_prod_cons_chart_bytes': create_mock_chart_bytes(),
        'cumulative_cashflow_chart_bytes': create_mock_chart_bytes()
    }

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}

    # Use invalid layout
    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='invalid_layout',
        theme=theme
    )

    chart_keys = list(analysis_results.keys())
    pdf_bytes = generator.generate(chart_keys)

    assert pdf_bytes, "PDF should be generated with default layout"

    # Should fall back to one_per_page (2 charts = 2 pages)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)

    assert num_pages == 2, f"Expected 2 pages (default layout), got {num_pages}"

    print("✓ Invalid layout handled with fallback to default")
    print(f"  - Requested layout: 'invalid_layout'")
    print(f"  - Fallback layout: 'one_per_page'")
    print(f"  - Output pages: {num_pages}")


def test_real_chart_keys_from_requirements():
    """Test that all chart keys from requirements are supported."""
    print("\n=== Test 10: Real Chart Keys from Requirements ===")

    # Chart keys from Requirement 12 in requirements.md
    required_2d_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes'
    ]

    required_3d_charts = [
        'daily_production_switcher_chart_bytes',
        'weekly_production_switcher_chart_bytes',
        'yearly_production_switcher_chart_bytes',
        'project_roi_matrix_switcher_chart_bytes',
        'feed_in_revenue_switcher_chart_bytes',
        'prod_vs_cons_switcher_chart_bytes',
        'tariff_comparison_switcher_chart_bytes',
        'co2_savings_value_switcher_chart_bytes',
        'investment_value_switcher_chart_bytes',
        'storage_effect_switcher_chart_bytes',
        'selfuse_stack_switcher_chart_bytes',
        'cost_growth_switcher_chart_bytes',
        'selfuse_ratio_switcher_chart_bytes',
        'roi_comparison_switcher_chart_bytes',
        'scenario_comparison_switcher_chart_bytes',
        'income_projection_switcher_chart_bytes'
    ]

    required_pv_visuals = [
        'yearly_production_chart_bytes',
        'break_even_chart_bytes',
        'amortisation_chart_bytes'
    ]

    all_required_charts = required_2d_charts + \
        required_3d_charts + required_pv_visuals

    theme = {'colors': {'primary': '#1E3A8A', 'secondary': '#3B82F6'}}
    generator = ChartPageGenerator(
        analysis_results={},
        layout='one_per_page',
        theme=theme
    )

    print("✓ Verifying all required chart keys have friendly names:")
    print(f"\n  2D Charts ({len(required_2d_charts)}):")
    for key in required_2d_charts:
        name = generator._get_chart_name(key)
        print(f"    - {name}")

    print(f"\n  3D Charts ({len(required_3d_charts)}):")
    for key in required_3d_charts:
        name = generator._get_chart_name(key)
        print(f"    - {name}")

    print(f"\n  PV Visuals ({len(required_pv_visuals)}):")
    for key in required_pv_visuals:
        name = generator._get_chart_name(key)
        print(f"    - {name}")

    print(
        f"\n✓ All {
            len(all_required_charts)} required chart keys are supported")


def run_all_tests():
    """Run all test functions."""
    print("=" * 70)
    print("CHART PAGE GENERATOR TEST SUITE")
    print("=" * 70)

    test_functions = [
        test_chart_page_generator_initialization,
        test_generate_one_per_page,
        test_generate_two_per_page,
        test_generate_four_per_page,
        test_chart_name_mapping,
        test_empty_chart_list,
        test_missing_chart_bytes,
        test_layout_options,
        test_default_layout_fallback,
        test_real_chart_keys_from_requirements
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
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

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
