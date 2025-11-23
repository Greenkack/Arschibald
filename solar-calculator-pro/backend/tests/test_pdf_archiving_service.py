"""
Tests for PDF Archiving Service

Tests the automatic PDF archiving to CRM customer records.

Requirements: 1.3, 6.1
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from services.pdf_archiving_service import PDFArchivingService, PDFMetadata


class TestPDFMetadata:
    """Test PDF metadata structure"""
    
    def test_create_metadata(self):
        """Test creating PDF metadata"""
        metadata = PDFMetadata(
            creation_date=datetime.now(),
            company_id=1,
            company_name="Test Company",
            products=[{"name": "PV Module", "quantity": 20}],
            total_price=15000.00,
            pdf_type="offer_pdf",
            project_type="pv",
            version=1,
            file_size=1024,
            checksum="abc123"
        )
        
        assert metadata.company_id == 1
        assert metadata.company_name == "Test Company"
        assert len(metadata.products) == 1
        assert metadata.total_price == 15000.00
        assert metadata.pdf_type == "offer_pdf"
        assert metadata.version == 1
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary"""
        metadata = PDFMetadata(
            creation_date=datetime(2025, 1, 15, 10, 30),
            company_id=1,
            company_name="Test Company",
            total_price=15000.00
        )
        
        data = metadata.to_dict()
        
        assert data['company_id'] == 1
        assert data['company_name'] == "Test Company"
        assert data['total_price'] == 15000.00
        assert 'creation_date' in data
    
    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary"""
        data = {
            'creation_date': '2025-01-15T10:30:00',
            'company_id': 1,
            'company_name': "Test Company",
            'total_price': 15000.00,
            'pdf_type': 'offer_pdf',
            'version': 2
        }
        
        metadata = PDFMetadata.from_dict(data)
        
        assert metadata.company_id == 1
        assert metadata.company_name == "Test Company"
        assert metadata.total_price == 15000.00
        assert metadata.version == 2


class TestPDFArchivingService:
    """Test PDF archiving service"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return PDFArchivingService()
    
    @pytest.fixture
    def sample_pdf_bytes(self):
        """Create sample PDF bytes"""
        return b"%PDF-1.4\n%Test PDF content\n%%EOF"
    
    def test_calculate_checksum(self, service, sample_pdf_bytes):
        """Test calculating PDF checksum"""
        checksum = service.calculate_checksum(sample_pdf_bytes)
        
        assert checksum is not None
        assert len(checksum) == 64  # SHA-256 produces 64 hex characters
        
        # Same content should produce same checksum
        checksum2 = service.calculate_checksum(sample_pdf_bytes)
        assert checksum == checksum2
    
    def test_extract_metadata_from_filename_offer(self, service):
        """Test extracting metadata from offer filename"""
        filename = "Angebot_Kunde_v2_2025-01-15.pdf"
        
        metadata = service.extract_metadata_from_filename(filename)
        
        assert metadata['pdf_type'] == 'offer_pdf'
        assert metadata['version'] == 2
        assert 'date' in metadata
    
    def test_extract_metadata_from_filename_invoice(self, service):
        """Test extracting metadata from invoice filename"""
        filename = "Rechnung_12345_v1.pdf"
        
        metadata = service.extract_metadata_from_filename(filename)
        
        assert metadata['pdf_type'] == 'invoice_pdf'
        assert metadata['version'] == 1
    
    def test_extract_metadata_from_filename_contract(self, service):
        """Test extracting metadata from contract filename"""
        filename = "Vertrag_Kunde_2025-01-15.pdf"
        
        metadata = service.extract_metadata_from_filename(filename)
        
        assert metadata['pdf_type'] == 'contract_pdf'
    
    def test_create_metadata(self, service, sample_pdf_bytes):
        """Test creating comprehensive metadata"""
        metadata = service.create_metadata(
            pdf_bytes=sample_pdf_bytes,
            filename="Angebot_Test_v1.pdf",
            company_id=1,
            company_name="Test Company",
            products=[{"name": "PV Module", "quantity": 20}],
            total_price=15000.00
        )
        
        assert metadata.company_id == 1
        assert metadata.company_name == "Test Company"
        assert metadata.total_price == 15000.00
        assert metadata.pdf_type == 'offer_pdf'
        assert metadata.file_size == len(sample_pdf_bytes)
        assert metadata.checksum is not None
    
    def test_create_metadata_with_offer_data(self, service, sample_pdf_bytes):
        """Test creating metadata with offer data"""
        offer_data = {
            'customer_id': 1,
            'customer': {'name': 'Test Customer'},
            'products': [{"name": "PV Module"}],
            'total_cost': 15000.00,
            'project_type': 'pv'
        }
        
        metadata = service.create_metadata(
            pdf_bytes=sample_pdf_bytes,
            filename="Angebot_Test.pdf",
            offer_data=offer_data
        )
        
        assert metadata.company_id == 1
        assert metadata.company_name == 'Test Customer'
        assert metadata.total_price == 15000.00
        assert metadata.project_type == 'pv'
    
    def test_create_versioned_filename(self, service):
        """Test creating versioned filename"""
        metadata = PDFMetadata(
            creation_date=datetime(2025, 1, 15),
            company_id=1
        )
        
        filename = service.create_versioned_filename(
            "Angebot_Test.pdf",
            2,
            metadata
        )
        
        assert "v2" in filename
        assert "2025-01-15" in filename
        assert filename.endswith(".pdf")
    
    @patch('services.pdf_archiving_service.get_next_version_number')
    def test_get_next_version_number(self, mock_get_version, service):
        """Test getting next version number"""
        mock_get_version.return_value = 3
        
        version = service.get_next_version_number(
            customer_id=1,
            pdf_type='offer_pdf',
            project_id=10
        )
        
        assert version == 3
        mock_get_version.assert_called_once_with(1, 'offer_pdf', 10)
    
    @patch('services.pdf_archiving_service.add_customer_document')
    @patch('services.pdf_archiving_service.get_next_version_number')
    def test_auto_save_to_crm(self, mock_get_version, mock_add_doc, service, sample_pdf_bytes):
        """Test auto-saving PDF to CRM"""
        mock_get_version.return_value = 1
        mock_add_doc.return_value = 123
        
        doc_id = service.auto_save_to_crm(
            pdf_bytes=sample_pdf_bytes,
            filename="Angebot_Test.pdf",
            customer_id=1,
            project_id=10,
            company_name="Test Company",
            total_price=15000.00
        )
        
        assert doc_id == 123
        mock_add_doc.assert_called_once()
    
    @patch('services.pdf_archiving_service.list_customer_documents')
    def test_get_pdf_history(self, mock_list_docs, service):
        """Test getting PDF history"""
        mock_list_docs.return_value = [
            {
                'id': 1,
                'display_name': 'Angebot_v1.pdf',
                'doc_type': 'offer_pdf',
                'uploaded_at': '2025-01-15 10:00:00'
            },
            {
                'id': 2,
                'display_name': 'Angebot_v2.pdf',
                'doc_type': 'offer_pdf',
                'uploaded_at': '2025-01-16 10:00:00'
            }
        ]
        
        history = service.get_pdf_history(customer_id=1)
        
        assert len(history) == 2
        assert history[0]['id'] == 1
        assert history[1]['id'] == 2
    
    @patch('services.pdf_archiving_service.list_customer_documents')
    def test_get_pdf_history_with_filters(self, mock_list_docs, service):
        """Test getting PDF history with filters"""
        mock_list_docs.return_value = [
            {
                'id': 1,
                'display_name': 'Angebot_v1.pdf',
                'doc_type': 'offer_pdf',
                'uploaded_at': '2025-01-15 10:00:00'
            },
            {
                'id': 2,
                'display_name': 'Rechnung_v1.pdf',
                'doc_type': 'invoice_pdf',
                'uploaded_at': '2025-01-16 10:00:00'
            }
        ]
        
        # Filter by PDF type
        history = service.get_pdf_history(
            customer_id=1,
            pdf_type='offer_pdf'
        )
        
        assert len(history) == 1
        assert history[0]['doc_type'] == 'offer_pdf'
    
    @patch('services.pdf_archiving_service.get_db_connection')
    def test_search_pdfs(self, mock_get_conn, service):
        """Test searching PDFs"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'display_name': 'Angebot_Test.pdf',
                'doc_type': 'offer_pdf',
                'customer_name': 'Test Customer'
            }
        ]
        mock_get_conn.return_value = mock_conn
        
        results = service.search_pdfs(
            search_term='Test',
            pdf_type='offer_pdf'
        )
        
        assert len(results) == 1
        assert results[0]['display_name'] == 'Angebot_Test.pdf'
    
    @patch('services.pdf_archiving_service.get_customer_document')
    def test_export_pdf(self, mock_get_doc, service, sample_pdf_bytes):
        """Test exporting PDF"""
        mock_get_doc.return_value = {
            'id': 1,
            'file_bytes': sample_pdf_bytes
        }
        
        pdf_bytes = service.export_pdf(document_id=1)
        
        assert pdf_bytes == sample_pdf_bytes
    
    @patch('services.pdf_archiving_service.get_customer_document')
    def test_export_pdf_to_file(self, mock_get_doc, service, sample_pdf_bytes):
        """Test exporting PDF to file"""
        mock_get_doc.return_value = {
            'id': 1,
            'file_bytes': sample_pdf_bytes
        }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            output_path = tmp.name
        
        try:
            pdf_bytes = service.export_pdf(
                document_id=1,
                output_path=output_path
            )
            
            assert pdf_bytes == sample_pdf_bytes
            assert os.path.exists(output_path)
            
            with open(output_path, 'rb') as f:
                saved_bytes = f.read()
            assert saved_bytes == sample_pdf_bytes
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('services.pdf_archiving_service.get_customer_document')
    def test_export_multiple_pdfs(self, mock_get_doc, service, sample_pdf_bytes):
        """Test exporting multiple PDFs"""
        mock_get_doc.side_effect = [
            {
                'id': 1,
                'file_bytes': sample_pdf_bytes,
                'display_name': 'doc1.pdf'
            },
            {
                'id': 2,
                'file_bytes': sample_pdf_bytes,
                'display_name': 'doc2.pdf'
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results = service.export_multiple_pdfs(
                document_ids=[1, 2],
                output_dir=tmpdir
            )
            
            assert len(results) == 2
            assert 1 in results
            assert 2 in results
            assert os.path.exists(results[1])
            assert os.path.exists(results[2])
    
    @patch('services.pdf_archiving_service.get_db_connection')
    def test_get_pdf_statistics(self, mock_get_conn, service):
        """Test getting PDF statistics"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'doc_type': 'offer_pdf', 'count_by_type': 10},
            {'doc_type': 'invoice_pdf', 'count_by_type': 5}
        ]
        mock_cursor.fetchone.return_value = {'total_customers': 3}
        mock_get_conn.return_value = mock_conn
        
        stats = service.get_pdf_statistics()
        
        assert stats['total_pdfs'] == 15
        assert stats['total_customers'] == 3
        assert stats['by_type']['offer_pdf'] == 10
        assert stats['by_type']['invoice_pdf'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
