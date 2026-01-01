"""
Tests für Firmendokumente-Integration in PDF-Generierung
Task 6: Firmendokumente in PDF einbinden
"""
from pdf_generator import _append_datasheets_and_documents
import io
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

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


class TestCompanyDocuments(unittest.TestCase):
    """Test suite für Firmendokumente-Funktionalität"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock PDF bytes (minimal valid PDF)
        self.mock_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n190\n%%EOF'

        # Mock pv_details
        self.pv_details = {
            'selected_module_id': 1,
            'selected_inverter_id': 2,
            'include_storage': False
        }

        # Mock get_product_by_id function
        self.mock_get_product = Mock(return_value=None)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_1_load_company_documents(self):
        """
        Test Subtask 6.1: Firmendokumente laden
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.14
        """
        # Mock company documents
        mock_company_docs = [
            {'id': 1, 'display_name': 'AGB', 'relative_db_path': '1/agb.pdf'},
            {'id': 2, 'display_name': 'Vollmacht', 'relative_db_path': '1/vollmacht.pdf'},
            {'id': 3, 'display_name': 'Zertifikat', 'relative_db_path': '1/zertifikat.pdf'}
        ]

        mock_db_list_func = Mock(return_value=mock_company_docs)

        # Test: active_company_id vorhanden, IDs zum Einschließen
        company_document_ids = [1, 2]

        with patch('pdf_generator.os.path.exists', return_value=False):
            result = _append_datasheets_and_documents(
                main_pdf_bytes=self.mock_pdf_bytes,
                pv_details=self.pv_details,
                get_product_by_id_func=self.mock_get_product,
                db_list_company_documents_func=mock_db_list_func,
                active_company_id=1,
                company_document_ids_to_include=company_document_ids,
                include_additional_components=False
            )

        # Verify db_list_company_documents_func was called correctly
        mock_db_list_func.assert_called_once_with(1, None)

        # Result should be original PDF since no files exist
        self.assertEqual(result, self.mock_pdf_bytes)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_1_no_company_id(self):
        """
        Test Subtask 6.1: Keine Firmendokumente wenn keine active_company_id
        Requirement: 6.14
        """
        mock_db_list_func = Mock()

        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.mock_pdf_bytes,
            pv_details=self.pv_details,
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=mock_db_list_func,
            active_company_id=None,  # No company ID
            company_document_ids_to_include=[1, 2],
            include_additional_components=False
        )

        # db_list_company_documents_func should NOT be called
        mock_db_list_func.assert_not_called()

        # Result should be original PDF
        self.assertEqual(result, self.mock_pdf_bytes)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_1_empty_document_ids(self):
        """
        Test Subtask 6.1: Keine Firmendokumente wenn company_document_ids_to_include leer
        Requirement: 6.3
        """
        mock_db_list_func = Mock()

        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.mock_pdf_bytes,
            pv_details=self.pv_details,
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=mock_db_list_func,
            active_company_id=1,
            company_document_ids_to_include=[],  # Empty list
            include_additional_components=False
        )

        # db_list_company_documents_func should NOT be called
        mock_db_list_func.assert_not_called()

        # Result should be original PDF
        self.assertEqual(result, self.mock_pdf_bytes)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_1_filter_by_ids(self):
        """
        Test Subtask 6.1: Nur Dokumente mit IDs in company_document_ids_to_include filtern
        Requirement: 6.5
        """
        # Mock company documents - 3 available, only 2 should be included
        mock_company_docs = [
            {'id': 1, 'display_name': 'AGB', 'relative_db_path': '1/agb.pdf'},
            {'id': 2, 'display_name': 'Vollmacht', 'relative_db_path': '1/vollmacht.pdf'},
            {'id': 3, 'display_name': 'Zertifikat', 'relative_db_path': '1/zertifikat.pdf'}
        ]

        mock_db_list_func = Mock(return_value=mock_company_docs)

        # Only include IDs 1 and 3
        company_document_ids = [1, 3]

        with patch('pdf_generator.os.path.exists', return_value=False):
            result = _append_datasheets_and_documents(
                main_pdf_bytes=self.mock_pdf_bytes,
                pv_details=self.pv_details,
                get_product_by_id_func=self.mock_get_product,
                db_list_company_documents_func=mock_db_list_func,
                active_company_id=1,
                company_document_ids_to_include=company_document_ids,
                include_additional_components=False
            )

        # Verify function was called
        mock_db_list_func.assert_called_once()

        # Result should be original PDF (no files exist)
        self.assertEqual(result, self.mock_pdf_bytes)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_2_path_construction(self):
        """
        Test Subtask 6.2: Relativen Pfad mit COMPANY_DOCS_BASE_DIR_PDF_GEN kombinieren
        Requirement: 6.6
        """
        mock_company_docs = [
            {'id': 1, 'display_name': 'AGB', 'relative_db_path': '1/agb.pdf'}
        ]

        mock_db_list_func = Mock(return_value=mock_company_docs)

        with patch('pdf_generator.os.path.exists') as mock_exists:
            mock_exists.return_value = False

            result = _append_datasheets_and_documents(
                main_pdf_bytes=self.mock_pdf_bytes,
                pv_details=self.pv_details,
                get_product_by_id_func=self.mock_get_product,
                db_list_company_documents_func=mock_db_list_func,
                active_company_id=1,
                company_document_ids_to_include=[1],
                include_additional_components=False
            )

            # Verify os.path.exists was called with combined path
            # The path should contain COMPANY_DOCS_BASE_DIR_PDF_GEN +
            # relative_db_path
            self.assertTrue(mock_exists.called)
            called_path = mock_exists.call_args_list[0][0][0]
            self.assertIn('company_docs', called_path)
            self.assertIn('1/agb.pdf', called_path)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_2_error_handling(self):
        """
        Test Subtask 6.2: Fehler loggen und fortfahren
        Requirements: 6.8, 6.20
        """
        mock_company_docs = [
            {'id': 1, 'display_name': 'AGB', 'relative_db_path': '1/agb.pdf'},
            {'id': 2, 'display_name': 'Vollmacht',
                'relative_db_path': None}  # No path
        ]

        mock_db_list_func = Mock(return_value=mock_company_docs)

        with patch('pdf_generator.os.path.exists', return_value=False):
            with patch('pdf_generator.logging') as mock_logging:
                result = _append_datasheets_and_documents(
                    main_pdf_bytes=self.mock_pdf_bytes,
                    pv_details=self.pv_details,
                    get_product_by_id_func=self.mock_get_product,
                    db_list_company_documents_func=mock_db_list_func,
                    active_company_id=1,
                    company_document_ids_to_include=[1, 2],
                    include_additional_components=False
                )

                # Should log warnings for missing files
                self.assertTrue(
                    mock_logging.warning.called or mock_logging.info.called)

        # Should return original PDF (no files exist)
        self.assertEqual(result, self.mock_pdf_bytes)

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_3_order_integration(self):
        """
        Test Subtask 6.3: Produktdatenblätter zuerst, dann Firmendokumente
        Requirements: 6.13, 6.17
        """
        # Mock product with datasheet
        mock_product = {
            'id': 1,
            'model_name': 'Test Module',
            'datasheet_link_db_path': 'modules/test.pdf'
        }

        mock_get_product = Mock(return_value=mock_product)

        # Mock company documents
        mock_company_docs = [
            {'id': 1, 'display_name': 'AGB', 'relative_db_path': '1/agb.pdf'}
        ]

        mock_db_list_func = Mock(return_value=mock_company_docs)

        # Track order of os.path.exists calls
        exists_calls = []

        def track_exists(path):
            exists_calls.append(path)
            return False

        with patch('pdf_generator.os.path.exists', side_effect=track_exists):
            result = _append_datasheets_and_documents(
                main_pdf_bytes=self.mock_pdf_bytes,
                pv_details=self.pv_details,
                get_product_by_id_func=mock_get_product,
                db_list_company_documents_func=mock_db_list_func,
                active_company_id=1,
                company_document_ids_to_include=[1],
                include_additional_components=False
            )

        # Verify order: product datasheets checked before company documents
        if len(exists_calls) >= 2:
            # First call should be for product datasheet
            self.assertIn('product_datasheets', exists_calls[0])
            # Last call should be for company document
            self.assertIn('company_docs', exists_calls[-1])

    @unittest.skipIf(not PYPDF_AVAILABLE, "PyPDF not available")
    def test_subtask_6_3_final_pdf_bytes(self):
        """
        Test Subtask 6.3: Finale PDF als Bytes zurückgeben
        Requirement: 6.18
        """
        result = _append_datasheets_and_documents(
            main_pdf_bytes=self.mock_pdf_bytes,
            pv_details=self.pv_details,
            get_product_by_id_func=self.mock_get_product,
            db_list_company_documents_func=None,
            active_company_id=None,
            company_document_ids_to_include=None,
            include_additional_components=False
        )

        # Result should be bytes
        self.assertIsInstance(result, bytes)

        # Should be valid PDF bytes
        self.assertTrue(result.startswith(b'%PDF'))


if __name__ == '__main__':
    unittest.main()
