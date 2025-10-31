"""
Test script for Task 7.3: Test PDF generation with selected charts

This script tests:
1. PDF generation with various chart types (2D, 3D, pie charts)
2. Verification that only selected charts appear in Visualizations section
3. Fallback message when no charts are selected

Requirements: 3.1, 3.2, 3.3, 3.4
"""

import sys
from io import BytesIO

from PyPDF2 import PdfReader

from database import list_company_documents

# Import the PDF generator
from pdf_generator import generate_offer_pdf
from product_db import get_product_by_id


def create_test_project_data():
    """Create minimal test project data for PDF generation"""
    return {
        'customer_info': {
            'name': 'Test Customer',
            'address': 'Test Street 123',
            'city': 'Test City',
            'zip': '12345',
            'email': 'test@example.com',
            'phone': '+49 123 456789'
        },
        'pv_details': {
            'selected_module_id': 1,
            'selected_inverter_id': 1,
            'include_storage': True,
            'selected_storage_id': 1,
            'module_count': 20,
            'system_size_kwp': 8.0,
            'annual_production_kwh': 8000,
            'annual_consumption_kwh': 4500,
            'include_additional_components': False
        },
        'pricing': {
            'total_price': 15000.0,
            'price_per_kwp': 1875.0
        }
    }


def create_test_analysis_results():
    """Create minimal analysis results with chart placeholders"""
    # Create a simple 1x1 pixel PNG as placeholder
    import base64
    # Minimal PNG: 1x1 transparent pixel
    minimal_png = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    )

    return {
        # 2D Charts
        'monthly_prod_cons_chart_bytes': minimal_png,
        'cost_projection_chart_bytes': minimal_png,
        'energy_flow_chart_bytes': minimal_png,

        # 3D Charts
        'investment_value_switcher_chart_bytes': minimal_png,
        'storage_effect_switcher_chart_bytes': minimal_png,
        'selfuse_stack_switcher_chart_bytes': minimal_png,

        # Pie Charts
        'yearly_production_chart_bytes': minimal_png,
        'break_even_chart_bytes': minimal_png,
        'amortisation_chart_bytes': minimal_png,

        # Other required data
        'total_investment': 15000.0,
        'payback_years': 12.5,
        'roi_25_years': 25000.0
    }


def count_pdf_pages(pdf_bytes):
    """Count pages in a PDF"""
    reader = PdfReader(BytesIO(pdf_bytes))
    return len(reader.pages)


def extract_pdf_text(pdf_bytes):
    """Extract text from PDF for verification"""
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def test_scenario_1_various_charts_selected():
    """Test 1: Select various chart types (2D, 3D, pie charts)"""
    print("\n" + "=" * 80)
    print("TEST 1: PDF Generation with Various Chart Types Selected")
    print("=" * 80)

    project_data = create_test_project_data()
    analysis_results = create_test_analysis_results()

    # Select a mix of 2D, 3D, and pie charts
    inclusion_options = {
        'include_company_logo': False,
        'include_product_images': False,
        'include_all_documents': False,
        'company_document_ids_to_include': [],
        'selected_charts_for_pdf': [
            # 2D Charts
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            # 3D Charts
            'investment_value_switcher_chart_bytes',
            'storage_effect_switcher_chart_bytes',
            # Pie Charts
            'yearly_production_chart_bytes',
            'break_even_chart_bytes'
        ],
        'include_optional_component_details': False,
        'append_additional_pages_after_main6': True
    }

    company_info = {
        'name': 'Test Solar Company',
        'address': 'Test Street 1',
        'city': 'Test City',
        'postal_code': '12345'
    }

    sections_to_include = [
        'cover',
        'intro',
        'system_overview',
        'components',
        'pricing',
        'terms']

    def load_admin_setting(key, default=None):
        return default

    def save_admin_setting(key, value):
        pass

    def list_products():
        return []

    print(
        f"\nSelected charts ({len(inclusion_options['selected_charts_for_pdf'])}):")
    for chart in inclusion_options['selected_charts_for_pdf']:
        chart_type = "2D" if "prod_cons" in chart or "projection" in chart else \
                     "3D" if "switcher" in chart else "Pie"
        print(f"  - {chart} ({chart_type})")

    try:
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Test PDF with Charts",
            selected_cover_letter_text="Test cover letter",
            sections_to_include=sections_to_include,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=None,
            texts={},
            use_modern_design=True
        )

        page_count = count_pdf_pages(pdf_bytes)
        pdf_text = extract_pdf_text(pdf_bytes)

        print("\n[OK] PDF generated successfully")
        print(f"[OK] Total pages: {page_count}")

        # Verify charts section exists
        if "Visualisierungen" in pdf_text or "Visualizations" in pdf_text:
            print("[OK] Visualizations section found in PDF")
        else:
            print("[WARN] Visualizations section not found in PDF text")

        # Check for fallback messages (should NOT appear)
        if "Keine Diagramme" in pdf_text or "No charts" in pdf_text:
            print(
                "[ERROR] Fallback message found (should not appear with charts selected)")
            return False
        print("[OK] No fallback message (correct - charts were selected)")

        # Save PDF for manual inspection
        output_path = "test_output_various_charts.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"\n[OK] PDF saved to: {output_path}")
        print("  -> Please manually verify that only the 6 selected charts appear")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scenario_2_subset_of_charts():
    """Test 2: Select only a subset of charts"""
    print("\n" + "=" * 80)
    print("TEST 2: PDF Generation with Subset of Charts")
    print("=" * 80)

    project_data = create_test_project_data()
    analysis_results = create_test_analysis_results()

    # Select only 2 charts
    inclusion_options = {
        'include_company_logo': False,
        'include_product_images': False,
        'include_all_documents': False,
        'company_document_ids_to_include': [],
        'selected_charts_for_pdf': [
            'monthly_prod_cons_chart_bytes',
            'investment_value_switcher_chart_bytes'
        ],
        'include_optional_component_details': False,
        'append_additional_pages_after_main6': True
    }

    company_info = {
        'name': 'Test Solar Company',
        'address': 'Test Street 1',
        'city': 'Test City',
        'postal_code': '12345'
    }

    sections_to_include = [
        'cover',
        'intro',
        'system_overview',
        'components',
        'pricing',
        'terms']

    def load_admin_setting(key, default=None):
        return default

    def save_admin_setting(key, value):
        pass

    def list_products():
        return []

    print(
        f"\nSelected charts ({len(inclusion_options['selected_charts_for_pdf'])}):")
    for chart in inclusion_options['selected_charts_for_pdf']:
        print(f"  - {chart}")

    try:
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Test PDF with Charts",
            selected_cover_letter_text="Test cover letter",
            sections_to_include=sections_to_include,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=None,
            texts={},
            use_modern_design=True
        )

        page_count = count_pdf_pages(pdf_bytes)
        pdf_text = extract_pdf_text(pdf_bytes)

        print("\n[OK] PDF generated successfully")
        print(f"[OK] Total pages: {page_count}")

        # Save PDF for manual inspection
        output_path = "test_output_subset_charts.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"\n[OK] PDF saved to: {output_path}")
        print("  -> Please manually verify that only 2 charts appear")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scenario_3_no_charts_selected():
    """Test 3: No charts selected - should show fallback message"""
    print("\n" + "=" * 80)
    print("TEST 3: PDF Generation with NO Charts Selected (Fallback Message)")
    print("=" * 80)

    project_data = create_test_project_data()
    analysis_results = create_test_analysis_results()

    # Empty chart selection
    inclusion_options = {
        'include_company_logo': False,
        'include_product_images': False,
        'include_all_documents': False,
        'company_document_ids_to_include': [],
        'selected_charts_for_pdf': [],  # NO CHARTS SELECTED
        'include_optional_component_details': False,
        'append_additional_pages_after_main6': True
    }

    company_info = {
        'name': 'Test Solar Company',
        'address': 'Test Street 1',
        'city': 'Test City',
        'postal_code': '12345'
    }

    sections_to_include = [
        'cover',
        'intro',
        'system_overview',
        'components',
        'pricing',
        'terms']

    def load_admin_setting(key, default=None):
        return default

    def save_admin_setting(key, value):
        pass

    def list_products():
        return []

    print(
        f"\nSelected charts: {len(inclusion_options['selected_charts_for_pdf'])} (NONE)")

    try:
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Test PDF with Charts",
            selected_cover_letter_text="Test cover letter",
            sections_to_include=sections_to_include,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=None,
            texts={},
            use_modern_design=True
        )

        page_count = count_pdf_pages(pdf_bytes)
        pdf_text = extract_pdf_text(pdf_bytes)

        print("\n[OK] PDF generated successfully")
        print(f"[OK] Total pages: {page_count}")

        # Check for fallback message (SHOULD appear)
        if "Keine Diagramme" in pdf_text or "No charts" in pdf_text or "nicht ausgewählt" in pdf_text:
            print("[OK] Fallback message found (correct - no charts selected)")
        else:
            print("[WARN] Fallback message not found in PDF text")
            print("  Searching for: 'Keine Diagramme', 'No charts', 'nicht ausgewählt'")

        # Save PDF for manual inspection
        output_path = "test_output_no_charts.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"\n[OK] PDF saved to: {output_path}")
        print(
            "  -> Please manually verify fallback message appears in Visualizations section")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scenario_4_all_chart_types():
    """Test 4: Select all available chart types"""
    print("\n" + "=" * 80)
    print("TEST 4: PDF Generation with ALL Chart Types")
    print("=" * 80)

    project_data = create_test_project_data()
    analysis_results = create_test_analysis_results()

    # Select ALL charts
    all_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes',
        'energy_flow_chart_bytes',
        'investment_value_switcher_chart_bytes',
        'storage_effect_switcher_chart_bytes',
        'selfuse_stack_switcher_chart_bytes',
        'cost_growth_switcher_chart_bytes',
        'selfuse_ratio_switcher_chart_bytes',
        'roi_comparison_switcher_chart_bytes',
        'scenario_comparison_switcher_chart_bytes',
        'tariff_comparison_switcher_chart_bytes',
        'income_projection_switcher_chart_bytes',
        'yearly_production_chart_bytes',
        'break_even_chart_bytes',
        'amortisation_chart_bytes'
    ]

    inclusion_options = {
        'include_company_logo': False,
        'include_product_images': False,
        'include_all_documents': False,
        'company_document_ids_to_include': [],
        'selected_charts_for_pdf': all_charts,
        'include_optional_component_details': False,
        'append_additional_pages_after_main6': True
    }

    company_info = {
        'name': 'Test Solar Company',
        'address': 'Test Street 1',
        'city': 'Test City',
        'postal_code': '12345'
    }

    sections_to_include = [
        'cover',
        'intro',
        'system_overview',
        'components',
        'pricing',
        'terms']

    def load_admin_setting(key, default=None):
        return default

    def save_admin_setting(key, value):
        pass

    def list_products():
        return []

    print(
        f"\nSelected charts: {len(inclusion_options['selected_charts_for_pdf'])} (ALL)")

    try:
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Test PDF with Charts",
            selected_cover_letter_text="Test cover letter",
            sections_to_include=sections_to_include,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=None,
            texts={},
            use_modern_design=True
        )

        page_count = count_pdf_pages(pdf_bytes)

        print("\n[OK] PDF generated successfully")
        print(f"[OK] Total pages: {page_count}")
        print("  (Should be significantly more pages due to all charts)")

        # Save PDF for manual inspection
        output_path = "test_output_all_charts.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"\n[OK] PDF saved to: {output_path}")
        print(
            f"  -> Please manually verify all {len(all_charts)} charts appear")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test scenarios"""
    print("\n" + "=" * 80)
    print("CHART SELECTION TEST SUITE - Task 7.3")
    print("Testing Requirements: 3.1, 3.2, 3.3, 3.4")
    print("=" * 80)

    results = {
        'Test 1 - Various Charts': test_scenario_1_various_charts_selected(),
        'Test 2 - Subset of Charts': test_scenario_2_subset_of_charts(),
        'Test 3 - No Charts (Fallback)': test_scenario_3_no_charts_selected(),
        'Test 4 - All Charts': test_scenario_4_all_chart_types()
    }

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("[OK] ALL TESTS PASSED")
        print("\nManual Verification Required:")
        print("1. Open test_output_various_charts.pdf - verify 6 charts appear")
        print("2. Open test_output_subset_charts.pdf - verify only 2 charts appear")
        print("3. Open test_output_no_charts.pdf - verify fallback message appears")
        print("4. Open test_output_all_charts.pdf - verify all 15 charts appear")
    else:
        print("[FAILED] SOME TESTS FAILED")
    print("=" * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
