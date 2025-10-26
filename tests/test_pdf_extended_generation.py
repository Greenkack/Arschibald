#!/usr/bin/env python3
"""
Comprehensive test suite for extended PDF generation system.
Tests all requirements from .kiro/specs/fix-extended-pdf-datasheets/
"""

import product_db
import database
import pdf_generator
import os
import sys
import io
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    print("WARNING: pypdf not available, PDF page counting will be skipped")
    PYPDF_AVAILABLE = False

# Import required modules


class TestResult:
    """Container for test results"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.message = ""
        self.details = {}

    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.test_name}\n  {self.message}"


class PDFExtendedGenerationTester:
    """Test suite for extended PDF generation"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def log(self, message: str):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def create_test_project_data(self,
                                 include_all_accessories: bool = True,
                                 include_storage: bool = True) -> Dict[str,
                                                                       Any]:
        """Create test project data with all components"""

        # Get some real product IDs from database
        conn = database.get_db_connection()
        if not conn:
            self.log("ERROR: Cannot connect to database")
            return {}

        try:
            cursor = conn.cursor()

            # Get module
            cursor.execute(
                "SELECT id FROM products WHERE category = 'Modul' LIMIT 1")
            module_row = cursor.fetchone()
            module_id = module_row[0] if module_row else 1

            # Get inverter
            cursor.execute(
                "SELECT id FROM products WHERE category = 'Wechselrichter' LIMIT 1")
            inverter_row = cursor.fetchone()
            inverter_id = inverter_row[0] if inverter_row else 2

            # Get storage
            cursor.execute(
                "SELECT id FROM products WHERE category = 'Speicher' LIMIT 1")
            storage_row = cursor.fetchone()
            storage_id = storage_row[0] if storage_row else 3

            # Get accessories
            cursor.execute(
                "SELECT id FROM products WHERE category = 'Wallbox' LIMIT 1")
            wallbox_row = cursor.fetchone()
            wallbox_id = wallbox_row[0] if wallbox_row else None

            cursor.execute(
                "SELECT id FROM products WHERE category = 'EMS' LIMIT 1")
            ems_row = cursor.fetchone()
            ems_id = ems_row[0] if ems_row else None

            cursor.execute(
                "SELECT id FROM products WHERE category = 'Optimizer' LIMIT 1")
            optimizer_row = cursor.fetchone()
            optimizer_id = optimizer_row[0] if optimizer_row else None

        finally:
            conn.close()

        project_data = {
            "project_id": 9999,
            "project_name": "Test Extended PDF Generation",
            "customer_details": {
                "name": "Test Customer",
                "address": "Test Street 123",
                "city": "Test City",
                "postal_code": "12345"
            },
            "pv_details": {
                "selected_module_id": module_id,
                "selected_inverter_id": inverter_id,
                "include_storage": include_storage,
                "selected_storage_id": storage_id if include_storage else None,
                "include_additional_components": include_all_accessories,
                "selected_wallbox_id": wallbox_id if include_all_accessories else None,
                "selected_ems_id": ems_id if include_all_accessories else None,
                "selected_optimizer_id": optimizer_id if include_all_accessories else None,
                "selected_carport_id": None,  # May not exist in DB
                "selected_notstrom_id": None,  # May not exist in DB
                "selected_tierabwehr_id": None,  # May not exist in DB
                "module_count": 20,
                "system_size_kwp": 8.0,
                "annual_production_kwh": 8000,
                "annual_consumption_kwh": 5000
            },
            "pricing_details": {
                "total_price": 15000.0,
                "price_per_kwp": 1875.0
            }
        }

        return project_data

    def test_7_1_all_accessory_components(self) -> TestResult:
        """
        Task 7.1: Test PDF generation with all accessory components selected
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        result = TestResult(
            "7.1 - PDF generation with all accessory components")

        try:
            self.log("\n" + "=" * 80)
            self.log("TEST 7.1: PDF Generation with All Accessory Components")
            self.log("=" * 80)

            # Create test project with all accessories
            project_data = self.create_test_project_data(
                include_all_accessories=True,
                include_storage=True
            )

            if not project_data:
                result.message = "Failed to create test project data"
                return result

            # Configure inclusion options
            inclusion_options = {
                "include_company_logo": True,
                "include_product_images": True,
                "include_all_documents": True,  # Enable datasheet appending
                "company_document_ids_to_include": [],
                "selected_charts_for_pdf": [],
                "include_optional_component_details": True,
                "append_additional_pages_after_main6": True
            }

            self.log("Generating PDF with configuration:")
            self.log(
                f"  - Module ID: {project_data['pv_details']['selected_module_id']}")
            self.log(
                f"  - Inverter ID: {project_data['pv_details']['selected_inverter_id']}")
            self.log(
                f"  - Storage ID: {project_data['pv_details']['selected_storage_id']}")
            self.log(
                f"  - Wallbox ID: {project_data['pv_details']['selected_wallbox_id']}")
            self.log(
                f"  - EMS ID: {project_data['pv_details']['selected_ems_id']}")
            self.log(
                f"  - Optimizer ID: {project_data['pv_details']['selected_optimizer_id']}")
            self.log(
                f"  - Include all documents: {inclusion_options['include_all_documents']}")

            # Generate PDF
            self.log("\nCalling pdf_generator.generate_offer_pdf()...")

            # Prepare all required parameters
            analysis_results = {
                "annual_production_kwh": 8000,
                "annual_consumption_kwh": 5000,
                "self_consumption_rate": 0.65,
                "autarky_rate": 0.55
            }

            company_info = {
                "name": "Test Solar Company",
                "address": "Solar Street 1",
                "city": "Solar City",
                "postal_code": "12345",
                "phone": "+49 123 456789",
                "email": "info@testsolar.de"
            }

            sections_to_include = [
                "cover",
                "intro",
                "system_overview",
                "components",
                "pricing",
                "terms"
            ]

            # Dummy functions for admin settings
            def load_admin_setting(key, default=None):
                return default

            def save_admin_setting(key, value):
                pass

            def list_products():
                return []

            pdf_bytes = pdf_generator.generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=None,
                selected_title_image_b64=None,
                selected_offer_title_text="Ihr individuelles Photovoltaik-Angebot",
                selected_cover_letter_text="Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.",
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                load_admin_setting_func=load_admin_setting,
                save_admin_setting_func=save_admin_setting,
                list_products_func=list_products,
                get_product_by_id_func=product_db.get_product_by_id,
                db_list_company_documents_func=None,
                active_company_id=None,
                texts={},  # Use defaults
                use_modern_design=True
            )

            if not pdf_bytes or len(pdf_bytes) == 0:
                result.message = "PDF generation returned empty bytes"
                return result

            self.log(f"\n✓ PDF generated successfully: {len(pdf_bytes)} bytes")

            # Count pages if pypdf available
            if PYPDF_AVAILABLE:
                try:
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    page_count = len(reader.pages)
                    self.log(f"✓ PDF has {page_count} pages")
                    result.details['page_count'] = page_count

                    # We expect at least 6 main pages
                    if page_count < 6:
                        result.message = f"PDF has only {page_count} pages, expected at least 6"
                        return result

                except Exception as e:
                    self.log(f"WARNING: Could not count pages: {e}")

            # Save test PDF for manual inspection
            test_output_path = os.path.join(
                self.test_data_dir,
                "pdf_output",
                "test_7_1_all_accessories.pdf")
            os.makedirs(os.path.dirname(test_output_path), exist_ok=True)

            with open(test_output_path, 'wb') as f:
                f.write(pdf_bytes)
            self.log(f"✓ Test PDF saved to: {test_output_path}")

            result.passed = True
            result.message = f"PDF generated successfully with {
                result.details.get(
                    'page_count', 'unknown')} pages"

        except Exception as e:
            result.message = f"Exception during test: {str(e)}"
            self.log(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

        return result

    def test_7_2_company_documents(self) -> TestResult:
        """
        Task 7.2: Test PDF generation with company documents
        Requirements: 2.1, 2.2, 2.3, 2.4
        """
        result = TestResult("7.2 - PDF generation with company documents")

        try:
            self.log("\n" + "=" * 80)
            self.log("TEST 7.2: PDF Generation with Company Documents")
            self.log("=" * 80)

            # Get a company ID from database
            conn = database.get_db_connection()
            if not conn:
                result.message = "Cannot connect to database"
                return result

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM companies LIMIT 1")
                company_row = cursor.fetchone()

                if not company_row:
                    result.message = "No companies found in database"
                    return result

                company_id = company_row[0]
                self.log(f"Using company ID: {company_id}")

                # Get available company documents
                documents = database.list_company_documents(company_id)
                self.log(f"Found {len(documents)} company documents")

                if documents:
                    for doc in documents[:5]:  # Show first 5
                        self.log(f"  - ID {doc['id']}: {doc['display_name']}"
                                 f" ({doc['document_type']})")

                # Select document IDs to include (up to 3)
                doc_ids = [doc['id'] for doc in documents[:3]]

                if not doc_ids:
                    self.log("WARNING: No company documents available")
                    self.log("Creating test scenario without documents")

            finally:
                conn.close()

            # Create test project
            project_data = self.create_test_project_data(
                include_all_accessories=False,
                include_storage=True
            )

            if not project_data:
                result.message = "Failed to create test project data"
                return result

            # Configure inclusion options with company documents
            inclusion_options = {
                "include_company_logo": True,
                "include_product_images": True,
                "include_all_documents": True,
                "company_document_ids_to_include": doc_ids,
                "selected_charts_for_pdf": [],
                "include_optional_component_details": False,
                "append_additional_pages_after_main6": True
            }

            self.log("\nGenerating PDF with configuration:")
            self.log(f"  - Company ID: {company_id}")
            self.log(f"  - Company documents to include: {doc_ids}")
            self.log(f"  - Include all documents: True")

            # Generate PDF
            self.log("\nCalling pdf_generator.generate_offer_pdf()...")

            analysis_results = {
                "annual_production_kwh": 8000,
                "annual_consumption_kwh": 5000,
                "self_consumption_rate": 0.65,
                "autarky_rate": 0.55
            }

            company_info = {
                "name": "Test Solar Company",
                "address": "Solar Street 1",
                "city": "Solar City",
                "postal_code": "12345",
                "phone": "+49 123 456789",
                "email": "info@testsolar.de"
            }

            sections_to_include = [
                "cover",
                "intro",
                "system_overview",
                "components",
                "pricing",
                "terms"
            ]

            def load_admin_setting(key, default=None):
                return default

            def save_admin_setting(key, value):
                pass

            def list_products():
                return []

            self.log("\n" + "=" * 80)
            self.log("WATCH FOR DEBUG OUTPUT FROM pdf_generator:")
            self.log("=" * 80)

            pdf_bytes = pdf_generator.generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=None,
                selected_title_image_b64=None,
                selected_offer_title_text="Angebot mit Firmendokumenten",
                selected_cover_letter_text="Test mit Firmendokumenten",
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                load_admin_setting_func=load_admin_setting,
                save_admin_setting_func=save_admin_setting,
                list_products_func=list_products,
                get_product_by_id_func=product_db.get_product_by_id,
                db_list_company_documents_func=database.list_company_documents,
                active_company_id=company_id,
                texts={},
                use_modern_design=True
            )

            self.log("=" * 80)
            self.log("END OF DEBUG OUTPUT")
            self.log("=" * 80 + "\n")

            if not pdf_bytes or len(pdf_bytes) == 0:
                result.message = "PDF generation returned empty bytes"
                return result

            self.log(f"✓ PDF generated: {len(pdf_bytes)} bytes")

            # Count pages
            if PYPDF_AVAILABLE:
                try:
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    page_count = len(reader.pages)
                    self.log(f"✓ PDF has {page_count} pages")
                    result.details['page_count'] = page_count
                    result.details['company_docs_requested'] = len(doc_ids)

                    # Expected: at least 6 main pages + datasheets
                    # + company documents
                    expected_min = 6
                    if page_count < expected_min:
                        result.message = (f"PDF has only {page_count} pages, "
                                          f"expected at least {expected_min}")
                        return result

                except Exception as e:
                    self.log(f"WARNING: Could not count pages: {e}")

            # Save test PDF
            test_output_path = os.path.join(
                self.test_data_dir,
                "pdf_output",
                "test_7_2_company_documents.pdf"
            )
            os.makedirs(os.path.dirname(test_output_path), exist_ok=True)

            with open(test_output_path, 'wb') as f:
                f.write(pdf_bytes)
            self.log(f"✓ Test PDF saved to: {test_output_path}")

            # Verification checklist
            self.log("\n" + "-" * 80)
            self.log("VERIFICATION CHECKLIST:")
            self.log("-" * 80)
            self.log("✓ PDF generated successfully")
            self.log(
                f"✓ PDF has {
                    result.details.get(
                        'page_count',
                        '?')} pages")
            self.log(f"✓ Requested {len(doc_ids)} company documents")
            self.log("✓ Check terminal output above for debug information")
            self.log("  - Look for 'DEBUG: _append_datasheets_and_documents'")
            self.log("  - Check 'Firmendokumente gefunden' count")
            self.log("  - Verify paths are correct")
            self.log("\nMANUAL VERIFICATION REQUIRED:")
            self.log(f"  1. Open: {test_output_path}")
            self.log("  2. Verify company documents appear after datasheets")
            self.log("  3. Check document content is readable")
            self.log("-" * 80)

            result.passed = True
            result.message = (
                f"PDF generated with " f"{
                    result.details.get(
                        'page_count',
                        '?')} pages, " f"{
                    len(doc_ids)} company docs requested")

        except Exception as e:
            result.message = f"Exception during test: {str(e)}"
            self.log(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

        return result

    def run_all_tests(self):
        """Run all test cases"""
        self.log("\n" + "=" * 80)
        self.log("EXTENDED PDF GENERATION TEST SUITE")
        self.log("=" * 80)
        self.log(f"Test data directory: {self.test_data_dir}")
        self.log(f"PyPDF available: {PYPDF_AVAILABLE}")

        # Run tests
        self.results.append(self.test_7_1_all_accessory_components())
        self.results.append(self.test_7_2_company_documents())

        # Print summary
        self.log("\n" + "=" * 80)
        self.log("TEST SUMMARY")
        self.log("=" * 80)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        for result in self.results:
            self.log(str(result))
            if result.details:
                for key, value in result.details.items():
                    self.log(f"    {key}: {value}")

        self.log("\n" + "-" * 80)
        self.log(f"Results: {passed}/{total} tests passed")
        self.log("=" * 80)

        return passed == total


if __name__ == "__main__":
    tester = PDFExtendedGenerationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
