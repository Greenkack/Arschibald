"""
Test suite for Task 9: Finanzierungsinformationen priorisieren

Tests all subtasks:
- 9.1: Finanzierungsabschnitt ab Seite 9 einfügen
- 9.2: Kreditfinanzierung berechnen und darstellen
- 9.3: Leasingfinanzierung berechnen und darstellen
- 9.4: Amortisationsplan erstellen
- 9.5: Finanzierungsvergleich erstellen
- 9.6: Finanzierungsdiagramme einfügen
"""

import pytest
import io
from pypdf import PdfReader


def test_financing_page_generator_imports():
    """Test that all required modules can be imported."""
    try:
        from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger
        from financial_tools import calculate_annuity, calculate_leasing_costs, calculate_financing_comparison
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_get_final_price():
    """Test Subtask 9.1: Extract final_end_preis from offer_data."""
    from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger

    # Test with analysis_results.final_price (highest priority)
    offer_data = {}
    analysis_results = {
        'final_price': 25000.0
    }

    theme = {'colors': {'primary': '#1E3A8A'}}
    logger = ExtendedPDFLogger()
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)

    final_price = generator._get_final_price()
    assert final_price == 25000.0, f"Expected 25000.0, got {final_price}"

    # Test with pv_details
    offer_data = {
        'pv_details': {
            'final_end_preis': 30000.0
        }
    }
    analysis_results = {}
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)
    final_price = generator._get_final_price()
    assert final_price == 30000.0, f"Expected 30000.0, got {final_price}"

    # Test with fallback to grand_total
    offer_data = {
        'grand_total': 35000.0
    }
    analysis_results = {}
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)
    final_price = generator._get_final_price()
    assert final_price == 35000.0, f"Expected 35000.0, got {final_price}"

    # Test with missing data
    offer_data = {}
    analysis_results = {}
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)
    final_price = generator._get_final_price()
    assert final_price == 0.0, f"Expected 0.0, got {final_price}"


def test_format_currency():
    """Test Requirement 9.29: Format currency with 2 decimals and thousand separators."""
    from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger

    offer_data = {'grand_total': 25000.0}
    analysis_results = {}
    theme = {'colors': {'primary': '#1E3A8A'}}
    logger = ExtendedPDFLogger()
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)

    # Test various amounts
    assert generator._format_currency(1234.56) == "1.234,56 €"
    assert generator._format_currency(25000.00) == "25.000,00 €"
    assert generator._format_currency(123456.78) == "123.456,78 €"
    assert generator._format_currency(0) == "0,00 €"


def test_credit_financing_calculation():
    """Test Subtask 9.2: Kreditfinanzierung berechnen."""
    from financial_tools import calculate_annuity

    # Test with realistic values
    principal = 25000.0
    interest_rate = 4.0
    duration_years = 20

    result = calculate_annuity(principal, interest_rate, duration_years)

    assert 'error' not in result, f"Calculation error: {result.get('error')}"
    assert 'monatliche_rate' in result
    assert 'gesamtkosten' in result
    assert 'gesamtzinsen' in result

    # Verify monthly rate is reasonable
    monthly_rate = result['monatliche_rate']
    assert 100 < monthly_rate < 200, f"Monthly rate {monthly_rate} seems unrealistic"

    # Verify total cost is greater than principal
    total_cost = result['gesamtkosten']
    assert total_cost > principal, f"Total cost {total_cost} should be greater than principal {principal}"


def test_leasing_financing_calculation():
    """Test Subtask 9.3: Leasingfinanzierung berechnen."""
    from financial_tools import calculate_leasing_costs

    # Test with realistic values
    total_investment = 25000.0
    leasing_factor = 1.2
    duration_months = 240  # 20 years
    residual_value_percent = 1.0

    result = calculate_leasing_costs(
        total_investment,
        leasing_factor,
        duration_months,
        residual_value_percent
    )

    assert 'error' not in result, f"Calculation error: {result.get('error')}"
    assert 'monatliche_rate' in result
    assert 'gesamtkosten' in result
    assert 'restwert' in result

    # Verify monthly rate is reasonable
    monthly_rate = result['monatliche_rate']
    assert monthly_rate > 0, f"Monthly rate {monthly_rate} should be positive"

    # Verify residual value
    residual_value = result['restwert']
    expected_residual = total_investment * (residual_value_percent / 100)
    assert abs(residual_value -
               expected_residual) < 1, f"Residual value {residual_value} doesn't match expected {expected_residual}"


def test_financing_comparison():
    """Test Subtask 9.5: Finanzierungsvergleich erstellen."""
    from financial_tools import calculate_financing_comparison

    investment = 25000.0
    annual_interest_rate = 4.0
    duration_years = 20
    leasing_factor = 1.2

    result = calculate_financing_comparison(
        investment,
        annual_interest_rate,
        duration_years,
        leasing_factor
    )

    assert 'kredit' in result
    assert 'leasing' in result
    assert 'cash_kauf' in result
    assert 'empfehlung' in result

    # Verify each option has required fields
    assert 'monatliche_rate' in result['kredit']
    assert 'gesamtkosten' in result['kredit']

    assert 'monatliche_rate' in result['leasing']
    assert 'effektive_kosten' in result['leasing']

    assert 'investition' in result['cash_kauf']
    assert 'gesamtkosten' in result['cash_kauf']

    # Verify recommendation is a string
    assert isinstance(result['empfehlung'], str)
    assert len(result['empfehlung']) > 0


def test_generate_financing_pages():
    """Test complete financing page generation."""
    from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger

    offer_data = {
        'pv_details': {
            'final_end_preis': 25000.0
        },
        'grand_total': 25000.0
    }

    analysis_results = {
        'final_price': 25000.0,
        'annual_savings': 2500.0,
        'annual_costs': 200.0,
        'anlage_kwp': 10.0
    }

    theme = {
        'colors': {
            'primary': '#1E3A8A',
            'secondary': '#3B82F6'
        }
    }

    logger = ExtendedPDFLogger()
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)

    # Generate pages
    pdf_bytes = generator.generate()

    # Verify PDF was generated
    assert pdf_bytes is not None, "PDF bytes should not be None"
    assert len(pdf_bytes) > 0, "PDF bytes should not be empty"

    # Verify it's a valid PDF
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        assert page_count > 0, f"PDF should have at least 1 page, got {page_count}"
        print(f"✓ Generated {page_count} financing pages")
    except Exception as e:
        pytest.fail(f"Generated PDF is invalid: {e}")

    # Check logger for errors
    summary = logger.get_summary()
    if summary['has_errors']:
        print("Errors during generation:")
        for error in summary['errors']:
            print(f"  - [{error['component']}] {error['message']}")

    assert not summary['has_errors'], f"Generation had {
        summary['error_count']} errors"


def test_generate_without_final_price():
    """Test that generation fails gracefully without final_end_preis."""
    from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger

    offer_data = {}  # No price data
    analysis_results = {}  # No analysis data
    theme = {'colors': {'primary': '#1E3A8A'}}
    logger = ExtendedPDFLogger()
    generator = FinancingPageGenerator(
        offer_data, analysis_results, theme, logger)

    pdf_bytes = generator.generate()

    # Should return empty bytes
    assert pdf_bytes == b'', "Should return empty bytes when no price available"

    # Should have logged an error
    summary = logger.get_summary()
    assert summary['has_errors'], "Should have logged an error"


if __name__ == '__main__':
    print("Running Task 9 Financing Page Generator Tests...")
    print("=" * 60)

    # Run tests
    test_financing_page_generator_imports()
    print("✓ Module imports successful")

    test_get_final_price()
    print("✓ Final price extraction works")

    test_format_currency()
    print("✓ Currency formatting works")

    test_credit_financing_calculation()
    print("✓ Credit financing calculation works")

    test_leasing_financing_calculation()
    print("✓ Leasing financing calculation works")

    test_financing_comparison()
    print("✓ Financing comparison works")

    test_generate_financing_pages()
    print("✓ Complete financing page generation works")

    test_generate_without_final_price()
    print("✓ Graceful failure without price works")

    print("=" * 60)
    print("All tests passed! ✓")
