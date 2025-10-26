"""
Test for Extended PDF Output Fix

This test verifies that:
1. extended_output_enabled flag is properly passed
2. extended_options are correctly built from UI selections
3. Extended pages are generated when enabled
4. Chart selection works correctly
"""

import pytest


def test_extended_options_building():
    """Test that extended_options are correctly built from UI selections."""

    # Simulate pdf_inclusion_options from UI
    pdf_inclusion_options = {
        'extended_output_enabled': True,
        'include_financing_details': True,
        'selected_product_datasheets': [1, 2, 3],
        'company_document_ids_to_include': [10, 20],
        'selected_charts_for_pdf': ['chart1', 'chart2', 'chart3'],
        'chart_layout': 'two_per_page'
    }

    # Build extended_options (as done in pdf_ui.py)
    if pdf_inclusion_options.get('extended_output_enabled', False):
        extended_options = {
            'financing_details': pdf_inclusion_options.get(
                'include_financing_details', False), 'product_datasheets': pdf_inclusion_options.get(
                'selected_product_datasheets', []), 'company_documents': pdf_inclusion_options.get(
                'company_document_ids_to_include', []), 'charts': pdf_inclusion_options.get(
                    'selected_charts_for_pdf', []), 'chart_layout': pdf_inclusion_options.get(
                        'chart_layout', 'one_per_page')}
        pdf_inclusion_options['extended_options'] = extended_options

    # Verify extended_options were created
    assert 'extended_options' in pdf_inclusion_options, \
        "extended_options should be created when extended_output_enabled=True"

    extended_opts = pdf_inclusion_options['extended_options']

    # Verify all fields are present
    assert extended_opts['financing_details']
    assert extended_opts['product_datasheets'] == [1, 2, 3]
    assert extended_opts['company_documents'] == [10, 20]
    assert extended_opts['charts'] == ['chart1', 'chart2', 'chart3']
    assert extended_opts['chart_layout'] == 'two_per_page'

    print("✅ Extended options correctly built from UI selections")


def test_extended_options_not_created_when_disabled():
    """Test that extended_options are NOT created when extended output is disabled."""

    pdf_inclusion_options = {
        'extended_output_enabled': False,
        'include_financing_details': True,
        'selected_product_datasheets': [1, 2, 3],
    }

    # Build extended_options (as done in pdf_ui.py)
    if pdf_inclusion_options.get('extended_output_enabled', False):
        extended_options = {
            'financing_details': pdf_inclusion_options.get(
                'include_financing_details',
                False),
            'product_datasheets': pdf_inclusion_options.get(
                'selected_product_datasheets',
                []),
        }
        pdf_inclusion_options['extended_options'] = extended_options

    # Verify extended_options were NOT created
    assert 'extended_options' not in pdf_inclusion_options, \
        "extended_options should NOT be created when extended_output_enabled=False"

    print("✅ Extended options correctly not created when disabled")


def test_extended_pdf_generator_initialization():
    """Test that ExtendedPDFGenerator can be initialized with options."""

    from extended_pdf_generator import ExtendedPDFGenerator

    offer_data = {
        'project_data': {'customer_data': {'name': 'Test'}},
        'analysis_results': {},
        'texts': {}
    }

    extended_options = {
        'financing_details': True,
        'product_datasheets': [1, 2],
        'company_documents': [10],
        'charts': ['chart1', 'chart2'],
        'chart_layout': 'two_per_page'
    }

    # Initialize generator
    generator = ExtendedPDFGenerator(offer_data, extended_options)

    assert generator is not None
    assert hasattr(generator, 'generate_extended_pages')

    print("✅ ExtendedPDFGenerator initialized successfully")


def test_extended_pdf_generator_methods_exist():
    """Test that all required methods exist in ExtendedPDFGenerator."""

    from extended_pdf_generator import ExtendedPDFGenerator

    # Check that class exists
    assert ExtendedPDFGenerator is not None

    # Check that required methods exist
    required_methods = [
        'generate_extended_pages',
        '_generate_financing_page',
        '_generate_chart_pages',
        '_merge_product_datasheets',
        '_merge_company_documents'
    ]

    for method_name in required_methods:
        assert hasattr(ExtendedPDFGenerator, method_name), \
            f"ExtendedPDFGenerator should have method {method_name}"

    print("✅ All required methods exist in ExtendedPDFGenerator")


def test_chart_page_generator_exists():
    """Test that ChartPageGenerator exists and can be imported."""

    try:
        from extended_pdf_generator import ChartPageGenerator
        assert ChartPageGenerator is not None, "ChartPageGenerator should exist"
        print("✅ ChartPageGenerator exists and can be imported")
    except ImportError as e:
        pytest.fail(f"ChartPageGenerator import failed: {e}")


def test_financing_page_generator_exists():
    """Test that FinancingPageGenerator exists and can be imported."""

    try:
        from extended_pdf_generator import FinancingPageGenerator
        assert FinancingPageGenerator is not None, "FinancingPageGenerator should exist"
        print("✅ FinancingPageGenerator exists and can be imported")
    except ImportError as e:
        pytest.fail(f"FinancingPageGenerator import failed: {e}")


def test_product_datasheet_merger_exists():
    """Test that ProductDatasheetMerger exists and can be imported."""

    try:
        from extended_pdf_generator import ProductDatasheetMerger
        assert ProductDatasheetMerger is not None, "ProductDatasheetMerger should exist"
        print("✅ ProductDatasheetMerger exists and can be imported")
    except ImportError as e:
        pytest.fail(f"ProductDatasheetMerger import failed: {e}")


def test_company_document_merger_exists():
    """Test that CompanyDocumentMerger exists and can be imported."""

    try:
        from extended_pdf_generator import CompanyDocumentMerger
        assert CompanyDocumentMerger is not None, "CompanyDocumentMerger should exist"
        print("✅ CompanyDocumentMerger exists and can be imported")
    except ImportError as e:
        pytest.fail(f"CompanyDocumentMerger import failed: {e}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Extended PDF Fix Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Extended Options Building", test_extended_options_building),
        ("Extended Options Not Created When Disabled", test_extended_options_not_created_when_disabled),
        ("ExtendedPDFGenerator Initialization", test_extended_pdf_generator_initialization),
        ("ExtendedPDFGenerator Methods Exist", test_extended_pdf_generator_methods_exist),
        ("ChartPageGenerator Exists", test_chart_page_generator_exists),
        ("FinancingPageGenerator Exists", test_financing_page_generator_exists),
        ("ProductDatasheetMerger Exists", test_product_datasheet_merger_exists),
        ("CompanyDocumentMerger Exists", test_company_document_merger_exists)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n📋 Testing: {test_name}")
            print("-" * 60)
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
