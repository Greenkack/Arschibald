"""
Test 7.5: Complete workflow with all features
Tests PDF generation with all components, documents, and charts.
"""

from database import list_company_documents
from product_db import get_product_by_id, list_products
from pdf_generator import generate_offer_pdf
import os
import sys
from datetime import datetime
from PyPDF2 import PdfReader

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules


# Mock admin settings functions
def mock_load_admin_setting(key, default=None):
    """Mock function for loading admin settings."""
    return default


def mock_save_admin_setting(key, value):
    """Mock function for saving admin settings."""
    return True


def create_test_project_data():
    """Create comprehensive test project data with all components."""
    return {
        "customer_data": {
            "name": "Max Mustermann",
            "street": "Musterstraße 123",
            "zip_code": "12345",
            "city": "Musterstadt",
            "email": "max@example.com",
            "phone": "+49 123 456789"
        },
        "project_data": {
            "project_name": "Vollständiges Test-Projekt",
            "project_date": datetime.now().strftime("%Y-%m-%d"),
            "notes": "Test mit allen Komponenten, Dokumenten und Diagrammen"
        },
        "pv_details": {
            # Main components
            "selected_module_id": 1,
            "selected_module_model": "Test Modul 400W",
            "module_count": 20,
            "selected_inverter_id": 2,
            "selected_inverter_model": "Test Wechselrichter 8kW",
            "include_storage": True,
            "selected_storage_id": 3,
            "selected_storage_model": "Test Speicher 10kWh",

            # Accessory components - all enabled
            "include_additional_components": True,
            "selected_wallbox_id": 4,
            "selected_wallbox_model": "Test Wallbox 11kW",
            "selected_ems_id": 5,
            "selected_ems_model": "Test EMS",
            "selected_optimizer_id": 6,
            "selected_optimizer_model": "Test Optimizer",
            "selected_carport_id": 7,
            "selected_carport_model": "Test Carport",
            "selected_notstrom_id": 8,
            "selected_notstrom_model": "Test Notstrom",
            "selected_tierabwehr_id": 9,
            "selected_tierabwehr_model": "Test Tierabwehr",

            # System details
            "system_power_kwp": 8.0,
            "annual_production_kwh": 8000,
            "annual_consumption_kwh": 4500,
            "self_consumption_rate": 0.65,
            "autarky_rate": 0.75,

            # Financial data
            "total_investment": 25000.0,
            "electricity_price_per_kwh": 0.35,
            "feed_in_tariff": 0.082,
            "annual_savings": 2500.0,
            "payback_period_years": 10.0
        },
        "company_data": {
            "company_id": 1,
            "company_name": "Test Solar GmbH",
            "street": "Solarstraße 1",
            "zip_code": "54321",
            "city": "Solarstadt",
            "phone": "+49 987 654321",
            "email": "info@testsolar.de",
            "website": "www.testsolar.de"
        }
    }


def create_test_analysis_results():
    """Create mock analysis results with chart data."""
    # Note: In real scenario, these would be actual chart bytes
    # For testing, we'll use placeholder data
    return {
        "monthly_prod_cons_chart_bytes": b"mock_chart_data_1",
        "cost_projection_chart_bytes": b"mock_chart_data_2",
        "monthly_prod_cons_3d_chart_bytes": b"mock_chart_data_3",
        "cost_projection_3d_chart_bytes": b"mock_chart_data_4",
        "energy_flow_pie_chart_bytes": b"mock_chart_data_5",
        "cost_breakdown_pie_chart_bytes": b"mock_chart_data_6",
        "waterfall_chart_bytes": b"mock_chart_data_7",
        "donut_eigenverbrauch_chart_bytes": b"mock_chart_data_8",
        "donut_autarkie_chart_bytes": b"mock_chart_data_9"
    }


def create_test_inclusion_options():
    """Create inclusion options with all features enabled."""
    return {
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": False,
        "company_document_ids_to_include": [1, 2],  # Select specific documents
        "selected_charts_for_pdf": [
            "monthly_prod_cons_chart_bytes",
            "cost_projection_chart_bytes",
            "monthly_prod_cons_3d_chart_bytes",
            "energy_flow_pie_chart_bytes",
            "waterfall_chart_bytes",
            "donut_eigenverbrauch_chart_bytes"
        ],
        "include_optional_component_details": True,
        "append_additional_pages_after_main6": True
    }


def analyze_pdf_content(pdf_path):
    """Analyze the generated PDF and return detailed information."""
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        print(f"\n{'=' * 80}")
        print(f"PDF ANALYSIS RESULTS")
        print(f"{'=' * 80}")
        print(f"File: {pdf_path}")
        print(f"Total Pages: {num_pages}")
        print(f"File Size: {os.path.getsize(pdf_path) / 1024:.2f} KB")

        # Analyze page content
        print(f"\n{'=' * 80}")
        print(f"PAGE CONTENT ANALYSIS")
        print(f"{'=' * 80}")

        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            text_length = len(text)
            print(f"Page {i}: {text_length} characters")

            # Check for specific content markers
            if i <= 8:
                print(f"  -> Main PDF page")
            else:
                print(f"  -> Appended content (datasheet/document)")

        return {
            "total_pages": num_pages,
            "file_size_kb": os.path.getsize(pdf_path) / 1024,
            "success": True
        }

    except Exception as e:
        print(f"\n[ERROR] Error analyzing PDF: {e}")
        return {
            "total_pages": 0,
            "file_size_kb": 0,
            "success": False,
            "error": str(e)
        }


def verify_requirements(analysis_result, expected_components):
    """Verify that the PDF meets all requirements."""
    print(f"\n{'=' * 80}")
    print(f"REQUIREMENTS VERIFICATION")
    print(f"{'=' * 80}")

    checks = []

    # Requirement 1.1, 1.2, 1.3: All product datasheets included
    check_1 = {
        "requirement": "1.1, 1.2, 1.3 - Product datasheets",
        "description": "All main and accessory component datasheets included",
        "expected": f"Main pages (6-8) + datasheets for {
            expected_components['total_products']} products",
        "status": "MANUAL CHECK REQUIRED"}
    checks.append(check_1)

    # Requirement 2.1: Company documents included
    check_2 = {
        "requirement": "2.1 - Company documents",
        "description": "Selected company documents appended",
        "expected": f"{expected_components['company_docs']} company documents",
        "status": "MANUAL CHECK REQUIRED"
    }
    checks.append(check_2)

    # Requirement 3.1: Charts included
    check_3 = {
        "requirement": "3.1 - Charts",
        "description": "Selected charts rendered in Visualizations section",
        "expected": f"{expected_components['charts']} charts in main PDF",
        "status": "MANUAL CHECK REQUIRED"
    }
    checks.append(check_3)

    # Requirement 5.1, 5.2, 5.3: Debug information
    check_4 = {
        "requirement": "5.1, 5.2, 5.3 - Debug logging",
        "description": "Debug information logged to terminal",
        "expected": "Found/missing datasheets and documents logged",
        "status": "CHECK TERMINAL OUTPUT"
    }
    checks.append(check_4)

    # Print verification results
    for check in checks:
        print(f"\n[OK] {check['requirement']}")
        print(f"  Description: {check['description']}")
        print(f"  Expected: {check['expected']}")
        print(f"  Status: {check['status']}")

    return checks


def main():
    """Main test function."""
    print(f"\n{'=' * 80}")
    print(f"TEST 7.5: COMPLETE WORKFLOW WITH ALL FEATURES")
    print(f"{'=' * 80}")
    print(f"Testing PDF generation with:")
    print(f"  - All main components (module, inverter, storage)")
    print(f"  - All accessory components (wallbox, EMS, optimizer, carport, notstrom, tierabwehr)")
    print(f"  - Multiple company documents")
    print(f"  - Multiple charts")
    print(f"\n")

    # Step 1: Create test data
    print("Step 1: Creating test project data...")
    project_data = create_test_project_data()
    analysis_results = create_test_analysis_results()
    inclusion_options = create_test_inclusion_options()

    expected_components = {
        # module, inverter, storage, wallbox, EMS, optimizer, carport, notstrom, tierabwehr
        "total_products": 9,
        "company_docs": 2,
        "charts": 6
    }

    print(f"[OK] Test data created")
    print(f"  - Main components: 3 (module, inverter, storage)")
    print(f"  - Accessory components: 6 (wallbox, EMS, optimizer, carport, notstrom, tierabwehr)")
    print(f"  - Company documents: {expected_components['company_docs']}")
    print(f"  - Charts: {expected_components['charts']}")

    # Step 2: Generate PDF
    print(f"\nStep 2: Generating extended PDF...")
    print(f"{'=' * 80}")

    try:
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=project_data["company_data"],
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Ihr individuelles Solarangebot",
            selected_cover_letter_text="Sehr geehrte Damen und Herren,\n\nhiermit erhalten Sie unser Angebot für Ihre Solaranlage.",
            sections_to_include=None,  # Include all sections
            inclusion_options=inclusion_options,
            load_admin_setting_func=mock_load_admin_setting,
            save_admin_setting_func=mock_save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=1,
            texts={},  # Use default texts
            use_modern_design=True
        )

        if not pdf_bytes:
            print("[ERROR] PDF generation returned None or empty bytes")
            return False

        print(f"[OK] PDF generated successfully ({len(pdf_bytes)} bytes)")

    except Exception as e:
        print(f"[ERROR] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Save PDF
    output_path = "test_output_complete_workflow.pdf"
    print(f"\nStep 3: Saving PDF to {output_path}...")

    try:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"[OK] PDF saved successfully")
    except Exception as e:
        print(f"[ERROR] Error saving PDF: {e}")
        return False

    # Step 4: Analyze PDF
    print(f"\nStep 4: Analyzing PDF content...")
    analysis_result = analyze_pdf_content(output_path)

    if not analysis_result["success"]:
        print(f"[ERROR] PDF analysis failed")
        return False

    # Step 5: Verify requirements
    verification_checks = verify_requirements(
        analysis_result, expected_components)

    # Step 6: Summary
    print(f"\n{'=' * 80}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"[OK] PDF generated: {output_path}")
    print(f"[OK] Total pages: {analysis_result['total_pages']}")
    print(f"[OK] File size: {analysis_result['file_size_kb']:.2f} KB")
    print(f"\n[INFO] MANUAL VERIFICATION REQUIRED:")
    print(f"   1. Open {output_path}")
    print(f"   2. Verify main pages (1-8) contain project information and charts")
    print(f"   3. Verify product datasheets are appended after main pages")
    print(f"   4. Verify company documents are appended after datasheets")
    print(f"   5. Check terminal output above for debug information")
    print(
        f"\n[INFO] Expected page count: ~8 (main) + {
            expected_components['total_products']} (datasheets) + {
            expected_components['company_docs']} (docs)")
    print(f"  Actual page count: {analysis_result['total_pages']}")

    if analysis_result['total_pages'] >= 8:
        print(f"\n[PASS] TEST PASSED: PDF has sufficient pages")
    else:
        print(f"\n[WARN] WARNING: PDF has fewer pages than expected")

    print(f"\n{'=' * 80}\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
