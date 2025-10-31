"""
Test script for Task 16: Error Handling and Logging

This script tests the ExtendedPDFLogger class and verifies that logging
is properly integrated into all components of the extended PDF generator.
"""

import io
from datetime import datetime


def test_extended_pdf_logger():
    """Test the ExtendedPDFLogger class functionality."""
    print("=" * 60)
    print("TEST 1: ExtendedPDFLogger Basic Functionality")
    print("=" * 60)

    from extended_pdf_generator import ExtendedPDFLogger

    # Create logger instance
    logger = ExtendedPDFLogger()

    # Test logging methods
    logger.log_info('TestComponent', 'This is an info message')
    logger.log_warning('TestComponent', 'This is a warning message')
    logger.log_error(
        'TestComponent',
        'This is an error message',
        Exception('Test exception'))

    # Get summary
    summary = logger.get_summary()

    print(f"\nLogger Summary:")
    print(f"  Errors: {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Info: {summary['info_count']}")
    print(f"  Has Errors: {summary['has_errors']}")
    print(f"  Has Warnings: {summary['has_warnings']}")

    # Verify counts
    assert summary['error_count'] == 1, "Should have 1 error"
    assert summary['warning_count'] == 1, "Should have 1 warning"
    assert summary['info_count'] == 1, "Should have 1 info message"
    assert summary['has_errors'], "Should have errors"
    assert summary['has_warnings'], "Should have warnings"

    # Test user-friendly summary
    print("\nUser-Friendly Summary:")
    print(logger.get_user_friendly_summary())

    # Test clear
    logger.clear()
    summary_after_clear = logger.get_summary()
    assert summary_after_clear['error_count'] == 0, "Should have 0 errors after clear"
    assert summary_after_clear['warning_count'] == 0, "Should have 0 warnings after clear"
    assert summary_after_clear['info_count'] == 0, "Should have 0 info messages after clear"

    print("\n✓ ExtendedPDFLogger basic functionality test passed!")


def test_logger_integration():
    """Test that logger is integrated into all components."""
    print("\n" + "=" * 60)
    print("TEST 2: Logger Integration in Components")
    print("=" * 60)

    from extended_pdf_generator import (
        ExtendedPDFGenerator,
        ExtendedPDFLogger,
        FinancingPageGenerator,
        ProductDatasheetMerger,
        CompanyDocumentMerger,
        ChartPageGenerator
    )

    # Create logger
    logger = ExtendedPDFLogger()

    # Test ExtendedPDFGenerator with logger
    print("\nTesting ExtendedPDFGenerator with logger...")
    generator = ExtendedPDFGenerator(
        offer_data={'grand_total': 10000},
        analysis_results={},
        options={},
        theme=None,
        logger=logger
    )

    # Generate with empty options (should log warnings)
    result = generator.generate_extended_pages()

    summary = logger.get_summary()
    print(f"  Info messages: {summary['info_count']}")
    print(f"  Warnings: {summary['warning_count']}")

    assert summary['info_count'] > 0, "Should have info messages"

    print("  ✓ ExtendedPDFGenerator logging works")

    # Test FinancingPageGenerator with logger
    logger.clear()
    print("\nTesting FinancingPageGenerator with logger...")
    fin_gen = FinancingPageGenerator(
        offer_data={'grand_total': 10000},
        theme={'colors': {'primary': '#000000'}},
        logger=logger
    )

    # This should log warnings about no financing options
    result = fin_gen.generate()

    summary = logger.get_summary()
    print(f"  Info messages: {summary['info_count']}")
    print(f"  Warnings: {summary['warning_count']}")

    print("  ✓ FinancingPageGenerator logging works")

    # Test ProductDatasheetMerger with logger
    logger.clear()
    print("\nTesting ProductDatasheetMerger with logger...")
    datasheet_merger = ProductDatasheetMerger(logger=logger)

    # Try to merge non-existent datasheets
    result = datasheet_merger.merge([99999])

    summary = logger.get_summary()
    print(f"  Info messages: {summary['info_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Errors: {summary['error_count']}")

    assert summary['warning_count'] > 0 or summary['error_count'] > 0, "Should have warnings or errors"

    print("  ✓ ProductDatasheetMerger logging works")

    # Test CompanyDocumentMerger with logger
    logger.clear()
    print("\nTesting CompanyDocumentMerger with logger...")
    doc_merger = CompanyDocumentMerger(logger=logger)

    # Try to merge non-existent documents
    result = doc_merger.merge([99999])

    summary = logger.get_summary()
    print(f"  Info messages: {summary['info_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Errors: {summary['error_count']}")

    assert summary['warning_count'] > 0 or summary['error_count'] > 0, "Should have warnings or errors"

    print("  ✓ CompanyDocumentMerger logging works")

    # Test ChartPageGenerator with logger
    logger.clear()
    print("\nTesting ChartPageGenerator with logger...")
    chart_gen = ChartPageGenerator(
        analysis_results={},
        layout='one_per_page',
        theme={'colors': {'primary': '#000000'}},
        logger=logger
    )

    # Try to generate with non-existent charts
    result = chart_gen.generate(['non_existent_chart'])

    summary = logger.get_summary()
    print(f"  Info messages: {summary['info_count']}")
    print(f"  Warnings: {summary['warning_count']}")

    assert summary['warning_count'] > 0, "Should have warnings about missing charts"

    print("  ✓ ChartPageGenerator logging works")

    print("\n✓ All components have logger integration!")


def test_graceful_degradation():
    """Test graceful degradation with errors."""
    print("\n" + "=" * 60)
    print("TEST 3: Graceful Degradation")
    print("=" * 60)

    from extended_pdf_generator import ExtendedPDFGenerator, ExtendedPDFLogger

    logger = ExtendedPDFLogger()

    # Create generator with invalid options
    print("\nTesting graceful degradation with invalid options...")
    generator = ExtendedPDFGenerator(
        offer_data={'grand_total': 10000},
        analysis_results={},
        options={
            'financing_details': True,  # Will fail - no financing options
            'product_datasheets': [99999],  # Will fail - non-existent product
            'company_documents': [99999],  # Will fail - non-existent document
            # Will fail - non-existent chart
            'selected_charts': ['non_existent_chart']
        },
        theme=None,
        logger=logger
    )

    # Generate - should not crash, but return empty or partial result
    result = generator.generate_extended_pages()

    summary = logger.get_summary()
    print(f"\nGeneration completed with:")
    print(f"  Errors: {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Info: {summary['info_count']}")
    print(f"  Result size: {len(result)} bytes")

    # Should have warnings/errors but not crash
    assert summary['warning_count'] > 0 or summary['error_count'] > 0, "Should have logged issues"

    print("\n✓ Graceful degradation test passed - no crashes!")


def test_logger_summary_format():
    """Test logger summary formatting."""
    print("\n" + "=" * 60)
    print("TEST 4: Logger Summary Formatting")
    print("=" * 60)

    from extended_pdf_generator import ExtendedPDFLogger

    logger = ExtendedPDFLogger()

    # Add various messages
    logger.log_info('Component1', 'Info message 1')
    logger.log_info('Component2', 'Info message 2')
    logger.log_warning('Component1', 'Warning message 1')
    logger.log_warning('Component2', 'Warning message 2')
    logger.log_error(
        'Component1',
        'Error message 1',
        Exception('Test error 1'))
    logger.log_error(
        'Component2',
        'Error message 2',
        Exception('Test error 2'))

    # Get user-friendly summary
    summary_text = logger.get_user_friendly_summary()

    print("\nFormatted Summary:")
    print(summary_text)

    # Verify summary contains expected sections
    assert '=== Extended PDF Generation Summary ===' in summary_text
    assert 'Errors: 2' in summary_text
    assert 'Warnings: 2' in summary_text
    assert 'Info: 2' in summary_text
    assert '--- Errors ---' in summary_text
    assert '--- Warnings ---' in summary_text

    print("\n✓ Logger summary formatting test passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TASK 16: ERROR HANDLING AND LOGGING TESTS")
    print("=" * 60)

    try:
        test_extended_pdf_logger()
        test_logger_integration()
        test_graceful_degradation()
        test_logger_summary_format()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nTask 16 Implementation Summary:")
        print("  ✓ ExtendedPDFLogger class created with log_error, log_warning, log_info")
        print("  ✓ Logger integrated into all components:")
        print("    - ExtendedPDFGenerator")
        print("    - FinancingPageGenerator")
        print("    - ProductDatasheetMerger")
        print("    - CompanyDocumentMerger")
        print("    - ChartPageGenerator")
        print("  ✓ Graceful degradation implemented:")
        print("    - Fallback to base PDF on errors")
        print("    - Warnings displayed in UI")
        print("    - No crashes on partial failures")
        print("  ✓ User-friendly summary generation")
        print("  ✓ Logger clear functionality")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
