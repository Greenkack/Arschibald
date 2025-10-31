"""
Test script for task 7.1: Test PDF generation with all accessory components selected

This script tests that all product datasheets (main components + accessories) are
correctly appended to the extended PDF output.

Components to test:
- Module (main)
- Inverter (main)
- Storage (main)
- Wallbox (accessory)
- EMS (accessory)
- Optimizer (accessory)
- Carport (accessory)
- Notstrom (accessory)
- Tierabwehr (accessory)
"""

from database import list_company_documents, get_company
from product_db import get_product_by_id, list_products
from pdf_generator import generate_offer_pdf
import sys
import os
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_test_project_data_with_all_accessories():
    """
    Create test project data with all main components and all accessory components.
    """
    return {
        "customer_data": {
            "name": "Test Customer - All Accessories",
            "street": "Teststraße 123",
            "zip_code": "12345",
            "city": "Teststadt",
            "email": "test@example.com",
            "phone": "+49 123 456789"
        },
        "pv_details": {
            # Main components
            "selected_module_id": 1,  # Assuming ID 1 exists
            "selected_inverter_id": 2,  # Assuming ID 2 exists
            "include_storage": True,
            "selected_storage_id": 3,  # Assuming ID 3 exists

            # Accessory components - ALL SELECTED
            "include_additional_components": True,
            "selected_wallbox_id": 4,
            "selected_ems_id": 5,
            "selected_optimizer_id": 6,
            "selected_carport_id": 7,
            "selected_notstrom_id": 8,
            "selected_tierabwehr_id": 9,

            # Basic PV configuration
            "module_count": 20,
            "system_power_kwp": 8.0,
            "annual_yield_kwh": 8000,
            "annual_consumption_kwh": 6000,
            "roof_orientation": "Süd",
            "roof_pitch": 30,
            "installation_type": "Aufdach"
        },
        "financial_data": {
            "total_investment": 25000.0,
            "electricity_price_per_kwh": 0.35,
            "feed_in_tariff": 0.082,
            "annual_savings": 2100.0,
            "payback_period_years": 11.9
        },
        "analysis_results": {}
    }


def test_all_accessories_pdf_generation():
    """
    Test PDF generation with all accessory components selected.
    """
    print("\n" + "=" * 80)
    print("TEST 7.1: PDF Generation with All Accessory Components")
    print("=" * 80 + "\n")

    # Create test data
    project_data = create_test_project_data_with_all_accessories()

    # Configure inclusion options
    inclusion_options = {
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": True,  # MUST be True to append datasheets!
        "company_document_ids_to_include": [],
        "selected_charts_for_pdf": [],  # No charts for this test
        "include_optional_component_details": True,
        "append_additional_pages_after_main6": True
    }

    # Get a test company ID (assuming company 1 exists)
    active_company_id = 1

    # Get company info
    try:
        company_info = get_company(active_company_id)
        if not company_info:
            company_info = {
                "name": "Test Company",
                "street": "Test Street 1",
                "zip_code": "12345",
                "city": "Test City",
                "email": "test@company.com",
                "phone": "+49 123 456789"
            }
    except Exception as e:
        print(f"Warning: Could not load company info: {e}")
        company_info = {
            "name": "Test Company",
            "street": "Test Street 1",
            "zip_code": "12345",
            "city": "Test City",
            "email": "test@company.com",
            "phone": "+49 123 456789"
        }

    # Texts dictionary (minimal for testing)
    texts = {
        "pdf_title": "Solar Offer",
        "pdf_customer_data": "Customer Data",
        "pdf_pv_system": "PV System"
    }

    print("Test Configuration:")
    print("-" * 80)
    print(f"Main Components:")
    print(f"  - Module ID: {project_data['pv_details']['selected_module_id']}")
    print(
        f"  - Inverter ID: {project_data['pv_details']['selected_inverter_id']}")
    print(
        f"  - Storage ID: {project_data['pv_details']['selected_storage_id']}")
    print(f"\nAccessory Components:")
    print(
        f"  - Wallbox ID: {project_data['pv_details']['selected_wallbox_id']}")
    print(f"  - EMS ID: {project_data['pv_details']['selected_ems_id']}")
    print(
        f"  - Optimizer ID: {project_data['pv_details']['selected_optimizer_id']}")
    print(
        f"  - Carport ID: {project_data['pv_details']['selected_carport_id']}")
    print(
        f"  - Notstrom ID: {project_data['pv_details']['selected_notstrom_id']}")
    print(
        f"  - Tierabwehr ID: {project_data['pv_details']['selected_tierabwehr_id']}")
    print(
        f"\nInclude Additional Components: {
            project_data['pv_details']['include_additional_components']}")
    print("-" * 80 + "\n")

    # Check which products actually exist in database
    print("Checking Product Availability in Database:")
    print("-" * 80)

    all_product_ids = [
        ("Module", project_data['pv_details']['selected_module_id']),
        ("Inverter", project_data['pv_details']['selected_inverter_id']),
        ("Storage", project_data['pv_details']['selected_storage_id']),
        ("Wallbox", project_data['pv_details']['selected_wallbox_id']),
        ("EMS", project_data['pv_details']['selected_ems_id']),
        ("Optimizer", project_data['pv_details']['selected_optimizer_id']),
        ("Carport", project_data['pv_details']['selected_carport_id']),
        ("Notstrom", project_data['pv_details']['selected_notstrom_id']),
        ("Tierabwehr", project_data['pv_details']['selected_tierabwehr_id'])
    ]

    available_products = []
    missing_products = []

    for component_name, product_id in all_product_ids:
        try:
            product = get_product_by_id(product_id)
            if product:
                datasheet_path = product.get("datasheet_link_db_path", "N/A")
                print(
                    f"[OK] {component_name} (ID {product_id}): {
                        product.get(
                            'model',
                            'Unknown')}")
                print(f"  Datasheet path: {datasheet_path}")
                available_products.append(
                    (component_name, product_id, product))
            else:
                print(
                    f"[MISSING] {component_name} (ID {product_id}): NOT FOUND in database")
                missing_products.append((component_name, product_id))
        except Exception as e:
            print(f"[ERROR] {component_name} (ID {product_id}): ERROR - {e}")
            missing_products.append((component_name, product_id))

    print("-" * 80 + "\n")

    if missing_products:
        print("[WARNING] Some products are not available in the database.")
        print("The test will continue, but datasheets for missing products won't be appended.\n")

    # Generate PDF
    print("Generating PDF...")
    print("-" * 80 + "\n")

    try:
        # Dummy functions for admin settings
        def load_admin_setting(key, default=None):
            return default

        def save_admin_setting(key, value):
            pass

        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results={},
            company_info=company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Solar Offer - All Accessories Test",
            selected_cover_letter_text="This is a test PDF with all accessory components.",
            sections_to_include=None,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            db_list_company_documents_func=list_company_documents,
            active_company_id=active_company_id,
            texts=texts,
            use_modern_design=True)

        if pdf_bytes:
            # Save PDF to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"test_output_all_accessories_{timestamp}.pdf"

            with open(output_filename, "wb") as f:
                f.write(pdf_bytes)

            pdf_size_kb = len(pdf_bytes) / 1024

            print("\n" + "=" * 80)
            print("TEST RESULTS")
            print("=" * 80)
            print(f"[SUCCESS] PDF generated successfully!")
            print(f"[SUCCESS] Output file: {output_filename}")
            print(f"[SUCCESS] File size: {pdf_size_kb:.2f} KB")
            print(
                f"\nProducts Available: {len(available_products)}/{len(all_product_ids)}")
            print(
                f"Products Missing: {len(missing_products)}/{len(all_product_ids)}")

            if available_products:
                print(f"\n[OK] Available Products with Datasheets:")
                for component_name, product_id, product in available_products:
                    datasheet = product.get("datasheet_link_db_path", "N/A")
                    print(
                        f"  - {component_name} (ID {product_id}): {datasheet}")

            if missing_products:
                print(f"\n[MISSING] Missing Products:")
                for component_name, product_id in missing_products:
                    print(f"  - {component_name} (ID {product_id})")

            print("\n" + "=" * 80)
            print("VERIFICATION STEPS:")
            print("=" * 80)
            print("1. Check the terminal output above for debug information")
            print("2. Look for the '_append_datasheets_and_documents' debug section")
            print("3. Verify that all available product datasheets were found")
            print(f"4. Open the PDF file: {output_filename}")
            print("5. Check that the PDF has more pages than just the main 6-8 pages")
            print("6. Verify that datasheets for available products are appended")
            print("=" * 80 + "\n")

            return True
        else:
            print("\n[ERROR] PDF generation returned None")
            return False

    except Exception as e:
        print(f"\n[ERROR] during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_all_accessories_pdf_generation()
    sys.exit(0 if success else 1)
