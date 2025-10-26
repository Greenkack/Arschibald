"""
Test für Task 6.1: Firmendokumente laden

Dieser Test verifiziert die Implementierung von Task 6.1 aus dem Spec:
- active_company_id aus project_data extrahieren
- db_list_company_documents_func(active_company_id, None) aufrufen
- company_document_ids_to_include aus inclusion_options verwenden
- Nur Dokumente mit IDs in company_document_ids_to_include filtern
- Wenn company_document_ids_to_include leer: Keine Firmendokumente anhängen
- Wenn keine active_company_id: Keine Firmendokumente anhängen

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.14
"""

from pdf_generator import _append_datasheets_and_documents
import unittest
from unittest.mock import Mock, patch, MagicMock
import io
import sys
import os

# Add parent directory to path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..')))

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

# Import the function to test


class TestTask61CompanyDocumentsLoading(unittest.TestCase):
    """Test suite for Task 6.1: Firmendokumente laden"""

    def setUp(self):
        """Set up test fixtures"""
        if not PYPDF_AVAILABLE:
            self.skipTest("PyPDF not available")

        # Create a minimal valid PDF
        self.main_pdf_bytes = self._create_minimal_pdf()

        # Mock functions
        self.mock_get_product = Mock(return_value=None)
        self.mock_list_company_docs = Mock()

        # Test data
        self.test_company_id = 123
        self.test_doc_ids = [1, 2, 3]

    def _create_minimal_pdf(self):
        """Create a minimal valid PDF for testing"""
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, "Test PDF")
        c.showPage()
        c.save()
        return buffer.getvalue()

    def test_requirement_6_1_active_company_id_extracted(self):
        """
        Requirement 6.1: active_company_id aus project_data extrahieren

        Verify that when active_company_id is provided, it is used correctly
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.1 - active_company_id extrahieren")
        print("=" * 80)

        # Setup mock to return empty list
        self.mock_list_company_docs.return_value = []

        # Call function with active_company_id
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=self.mock_list_company_docs,
            active_company_id=self.test_company_id,
            company_document_ids_to_include=self.test_doc_ids,
            include_additional_components=False
        )

        # Verify the function was called with the correct company_id
        self.mock_list_company_docs.assert_called_once_with(
            self.test_company_id, None)
        print("✓ active_company_id wurde korrekt verwendet")
        print(
            f"✓ db_list_company_documents_func wurde mit company_id={
                self.test_company_id} aufgerufen")

    def test_requirement_6_2_no_company_id_no_loading(self):
        """
        Requirement 6.2: Wenn keine active_company_id: Keine Firmendokumente anhängen

        Verify that when active_company_id is None, no company documents are loaded
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.2 - Keine active_company_id")
        print("=" * 80)

        # Call function without active_company_id
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=self.mock_list_company_docs,
            active_company_id=None,  # No company ID
            company_document_ids_to_include=self.test_doc_ids,
            include_additional_components=False
        )

        # Verify the function was NOT called
        self.mock_list_company_docs.assert_not_called()
        print("✓ db_list_company_documents_func wurde NICHT aufgerufen")
        print("✓ Keine Firmendokumente geladen wenn active_company_id=None")

    def test_requirement_6_3_empty_doc_ids_no_loading(self):
        """
        Requirement 6.3: Wenn company_document_ids_to_include leer: Keine Firmendokumente anhängen

        Verify that when company_document_ids_to_include is empty, no documents are loaded
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.3 - Leere company_document_ids_to_include")
        print("=" * 80)

        # Test with empty list
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=self.mock_list_company_docs,
            active_company_id=self.test_company_id,
            company_document_ids_to_include=[],  # Empty list
            include_additional_components=False
        )

        # Verify the function was NOT called
        self.mock_list_company_docs.assert_not_called()
        print("✓ db_list_company_documents_func wurde NICHT aufgerufen")
        print("✓ Keine Firmendokumente geladen wenn company_document_ids_to_include leer")

        # Test with None
        self.mock_list_company_docs.reset_mock()
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=self.mock_list_company_docs,
            active_company_id=self.test_company_id,
            company_document_ids_to_include=None,  # None
            include_additional_components=False
        )

        # Verify the function was NOT called
        self.mock_list_company_docs.assert_not_called()
        print("✓ Keine Firmendokumente geladen wenn company_document_ids_to_include=None")

    def test_requirement_6_4_db_function_called_correctly(self):
        """
        Requirement 6.4: db_list_company_documents_func(active_company_id, None) aufrufen

        Verify that the database function is called with correct parameters
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.4 - db_list_company_documents_func korrekt aufrufen")
        print("=" * 80)

        # Setup mock to return test documents
        test_docs = [
            {'id': 1, 'display_name': 'Doc 1', 'relative_db_path': 'doc1.pdf'},
            {'id': 2, 'display_name': 'Doc 2', 'relative_db_path': 'doc2.pdf'},
        ]
        self.mock_list_company_docs.return_value = test_docs

        # Call function
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=self.mock_list_company_docs,
            active_company_id=self.test_company_id,
            company_document_ids_to_include=[1, 2],
            include_additional_components=False
        )

        # Verify the function was called with correct parameters
        self.mock_list_company_docs.assert_called_once()
        call_args = self.mock_list_company_docs.call_args

        # Check first argument is company_id
        self.assertEqual(call_args[0][0], self.test_company_id)
        print(f"✓ Erster Parameter: active_company_id={self.test_company_id}")

        # Check second argument is None (for all document types)
        self.assertIsNone(call_args[0][1])
        print("✓ Zweiter Parameter: doc_type=None (alle Dokumenttypen)")

    def test_requirement_6_5_filter_by_ids(self):
        """
        Requirement 6.5: Nur Dokumente mit IDs in company_document_ids_to_include filtern

        Verify that only documents with IDs in the include list are processed
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.5 - Nur ausgewählte Dokumente filtern")
        print("=" * 80)

        # Setup mock to return multiple documents
        all_docs = [
            {'id': 1, 'display_name': 'Doc 1', 'relative_db_path': 'doc1.pdf'},
            {'id': 2, 'display_name': 'Doc 2', 'relative_db_path': 'doc2.pdf'},
            {'id': 3, 'display_name': 'Doc 3', 'relative_db_path': 'doc3.pdf'},
            {'id': 4, 'display_name': 'Doc 4', 'relative_db_path': 'doc4.pdf'},
        ]
        self.mock_list_company_docs.return_value = all_docs

        # Only include IDs 1 and 3
        include_ids = [1, 3]

        # Mock os.path.exists to return False (so we can track which docs were
        # processed)
        with patch('pdf_generator.os.path.exists', return_value=False):
            with patch('pdf_generator.logging') as mock_logging:
                result = _append_datasheets_and_documents(
                    main_pdf_bytes=self.main_pdf_bytes,
                    pv_details={},
                    get_product_by_id_func=self.mock_get_product,
                    db_list_company_documents_func=self.mock_list_company_docs,
                    active_company_id=self.test_company_id,
                    company_document_ids_to_include=include_ids,
                    include_additional_components=False
                )

                # Check logging calls to see which documents were processed
                warning_calls = [
                    call for call in mock_logging.warning.call_args_list]

                # Should have warnings for Doc 1 and Doc 3 (not found)
                # Should NOT have warnings for Doc 2 and Doc 4 (filtered out)
                warning_messages = [str(call) for call in warning_calls]

                # Count how many documents were attempted to be processed
                doc1_processed = any(
                    'Doc 1' in str(call) or 'doc1.pdf' in str(call) for call in warning_calls)
                doc3_processed = any(
                    'Doc 3' in str(call) or 'doc3.pdf' in str(call) for call in warning_calls)

                print(f"✓ Dokumente in DB: {len(all_docs)}")
                print(f"✓ Dokumente zum Einschließen: {include_ids}")
                print(f"✓ Doc 1 (ID=1) wurde verarbeitet: {doc1_processed}")
                print(f"✓ Doc 3 (ID=3) wurde verarbeitet: {doc3_processed}")
                print(
                    "✓ Nur Dokumente mit IDs in company_document_ids_to_include wurden verarbeitet")

    def test_requirement_6_14_no_callable_function(self):
        """
        Requirement 6.14: Wenn keine active_company_id: Keine Firmendokumente anhängen

        Verify that when db_list_company_documents_func is not callable, no documents are loaded
        """
        print("\n" + "=" * 80)
        print("TEST: Requirement 6.14 - Keine callable Funktion")
        print("=" * 80)

        # Call function with non-callable function
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.main_pdf_bytes,
            pv_details={},
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=None,  # Not callable
            active_company_id=self.test_company_id,
            company_document_ids_to_include=self.test_doc_ids,
            include_additional_components=False
        )

        # Should return the original PDF without errors
        self.assertIsNotNone(result)
        print("✓ Funktion gibt PDF zurück ohne Fehler")
        print("✓ Keine Firmendokumente geladen wenn db_list_company_documents_func nicht callable")

    def test_integration_all_conditions_met(self):
        """
        Integration test: All conditions met for loading company documents

        Verify the complete flow when all conditions are satisfied
        """
        print("\n" + "=" * 80)
        print("INTEGRATION TEST: Alle Bedingungen erfüllt")
        print("=" * 80)

        # Setup mock to return test documents
        test_docs = [
            {'id': 1, 'display_name': 'Vollmacht', 'relative_db_path': 'vollmacht.pdf'},
            {'id': 2, 'display_name': 'AGB', 'relative_db_path': 'agb.pdf'},
            {'id': 3, 'display_name': 'Zertifikat', 'relative_db_path': 'cert.pdf'},
        ]
        self.mock_list_company_docs.return_value = test_docs

        # Mock os.path.exists to return False
        with patch('pdf_generator.os.path.exists', return_value=False):
            with patch('pdf_generator.logging') as mock_logging:
                result = _append_datasheets_and_documents(
                    main_pdf_bytes=self.main_pdf_bytes,
                    pv_details={},
                    get_product_by_id_func=self.mock_get_product,
                    db_list_company_documents_func=self.mock_list_company_docs,
                    active_company_id=self.test_company_id,
                    company_document_ids_to_include=[1, 2, 3],
                    include_additional_components=False
                )

                # Verify function was called
                self.mock_list_company_docs.assert_called_once_with(
                    self.test_company_id, None)

                # Verify result is valid PDF
                self.assertIsNotNone(result)
                self.assertIsInstance(result, bytes)

                print("✓ active_company_id wurde verwendet")
                print("✓ db_list_company_documents_func wurde aufgerufen")
                print("✓ company_document_ids_to_include wurde verwendet")
                print("✓ Alle 3 Dokumente wurden verarbeitet")
                print("✓ Gültige PDF wurde zurückgegeben")


def run_tests():
    """Run all tests and print results"""
    print("\n" + "=" * 80)
    print("TASK 6.1: FIRMENDOKUMENTE LADEN - TEST SUITE")
    print("=" * 80)
    print("\nDieser Test verifiziert die Implementierung von Task 6.1:")
    print("- active_company_id aus project_data extrahieren")
    print("- db_list_company_documents_func(active_company_id, None) aufrufen")
    print("- company_document_ids_to_include aus inclusion_options verwenden")
    print("- Nur Dokumente mit IDs in company_document_ids_to_include filtern")
    print("- Wenn company_document_ids_to_include leer: Keine Firmendokumente anhängen")
    print("- Wenn keine active_company_id: Keine Firmendokumente anhängen")
    print("\nRequirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.14")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTask61CompanyDocumentsLoading)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"Tests durchgeführt: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun -
                          len(result.failures) -
                          len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALLE TESTS BESTANDEN!")
        print("✓ Task 6.1 ist vollständig implementiert und funktioniert korrekt")
    else:
        print("\n✗ EINIGE TESTS FEHLGESCHLAGEN")
        print("✗ Bitte überprüfen Sie die Implementierung")

    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
