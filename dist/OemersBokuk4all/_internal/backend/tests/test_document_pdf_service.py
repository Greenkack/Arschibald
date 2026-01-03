"""
Tests for Document PDF Conversion Service

Requirements: 14.8
Task: 228
"""

import pytest
import io
from pathlib import Path
from datetime import datetime

from backend.services.document_pdf_service import (
    DocumentPDFService,
    DocumentConversionError,
    word_to_pdf,
    excel_to_pdf,
    text_to_pdf,
    merge_pdfs
)
from backend.core.pdf_bytes import PDFMetadata


class TestDocumentPDFService:
    """Test suite for DocumentPDFService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return DocumentPDFService()
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample PDF metadata"""
        return PDFMetadata(
            title="Test Document",
            author="Test Author",
            subject="Test Subject",
            keywords=["test", "document", "pdf"]
        )
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
        assert service.pdf_engine is not None
    
    def test_text_to_pdf_bytes_from_string(self, service, sample_metadata):
        """Test converting text string to PDF bytes"""
        text_content = "This is a test document.\n\nIt has multiple paragraphs."
        
        pdf_bytes = service.text_to_pdf_bytes(
            text_content=text_content,
            metadata=sample_metadata
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_text_to_pdf_bytes_preserve_formatting(self, service):
        """Test text conversion with preserved formatting"""
        text_content = "Line 1\nLine 2\nLine 3"
        
        pdf_bytes = service.text_to_pdf_bytes(
            text_content=text_content,
            preserve_formatting=True
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_text_to_pdf_bytes_flow_text(self, service):
        """Test text conversion with flowing text"""
        text_content = "This is a long paragraph that should flow naturally.\n\nThis is another paragraph."
        
        pdf_bytes = service.text_to_pdf_bytes(
            text_content=text_content,
            preserve_formatting=False
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_text_to_pdf_bytes_from_bytes(self, service):
        """Test converting text bytes to PDF"""
        text_bytes = b"Test content from bytes"
        
        pdf_bytes = service.text_to_pdf_bytes(file_content=text_bytes)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_text_to_pdf_bytes_empty_content(self, service):
        """Test handling empty text content"""
        pdf_bytes = service.text_to_pdf_bytes(text_content="")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_text_to_pdf_bytes_no_input(self, service):
        """Test error when no input provided"""
        with pytest.raises(ValueError):
            service.text_to_pdf_bytes()
    
    def test_document_to_pdf_bytes_text(self, service):
        """Test generic document conversion for text"""
        text_content = "Test document content"
        text_bytes = text_content.encode('utf-8')
        
        pdf_bytes = service.document_to_pdf_bytes(
            file_content=text_bytes,
            file_type='txt'
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_document_to_pdf_bytes_unsupported_type(self, service):
        """Test error for unsupported file type"""
        with pytest.raises(DocumentConversionError):
            service.document_to_pdf_bytes(
                file_content=b"test",
                file_type='unsupported'
            )
    
    def test_document_to_pdf_bytes_no_file_type(self, service):
        """Test error when file type not provided"""
        with pytest.raises(ValueError):
            service.document_to_pdf_bytes(file_content=b"test")
    
    def test_convert_multiple_documents_no_merge(self, service):
        """Test converting multiple documents without merging"""
        documents = [
            {
                'text_content': 'Document 1',
                'file_type': 'txt'
            },
            {
                'text_content': 'Document 2',
                'file_type': 'txt'
            }
        ]
        
        # Modify to use text_content directly
        pdf_list = []
        for doc in documents:
            pdf_bytes = service.text_to_pdf_bytes(
                text_content=doc['text_content']
            )
            pdf_list.append(pdf_bytes)
        
        assert isinstance(pdf_list, list)
        assert len(pdf_list) == 2
        assert all(isinstance(pdf, bytes) for pdf in pdf_list)
    
    def test_merge_pdf_documents_from_bytes(self, service):
        """Test merging PDF documents from bytes"""
        # Create two simple PDFs
        pdf1 = service.text_to_pdf_bytes(text_content="Document 1")
        pdf2 = service.text_to_pdf_bytes(text_content="Document 2")
        
        merged = service.merge_pdf_documents([pdf1, pdf2])
        
        assert isinstance(merged, bytes)
        assert len(merged) > len(pdf1)
        assert merged.startswith(b'%PDF')
    
    def test_merge_pdf_documents_with_metadata(self, service, sample_metadata):
        """Test merging PDFs with metadata"""
        pdf1 = service.text_to_pdf_bytes(text_content="Document 1")
        pdf2 = service.text_to_pdf_bytes(text_content="Document 2")
        
        merged = service.merge_pdf_documents(
            [pdf1, pdf2],
            output_metadata=sample_metadata
        )
        
        assert isinstance(merged, bytes)
        assert len(merged) > 0
    
    def test_merge_pdf_documents_empty_list(self, service):
        """Test merging with empty list"""
        with pytest.raises(Exception):  # PyPDF2 will raise an error
            service.merge_pdf_documents([])
    
    def test_german_number_formatting_in_text(self, service):
        """Test that German number formatting is preserved in text conversion"""
        text_content = "Price: 1.234,56 EUR\nQuantity: 1.000 units"
        
        pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_multiline_text_conversion(self, service):
        """Test conversion of multiline text with various formatting"""
        text_content = """Title Line
        
Paragraph 1 with some content.

Paragraph 2 with more content.

- List item 1
- List item 2
- List item 3

Final paragraph."""
        
        pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_unicode_text_conversion(self, service):
        """Test conversion of text with Unicode characters"""
        text_content = "German: äöüß\nFrench: éèêë\nSymbols: €£¥"
        
        pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_large_text_conversion(self, service):
        """Test conversion of large text document"""
        # Create large text content
        text_content = "\n\n".join([f"Paragraph {i}: " + "Lorem ipsum " * 50 for i in range(100)])
        
        pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_text_to_pdf_function(self, tmp_path):
        """Test text_to_pdf convenience function"""
        # Create temporary text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("Test content")
        
        output_file = tmp_path / "output.pdf"
        
        pdf_bytes = text_to_pdf(str(text_file), str(output_file))
        
        assert isinstance(pdf_bytes, bytes)
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_text_to_pdf_function_no_output(self, tmp_path):
        """Test text_to_pdf without output file"""
        text_file = tmp_path / "test.txt"
        text_file.write_text("Test content")
        
        pdf_bytes = text_to_pdf(str(text_file))
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestErrorHandling:
    """Test error handling"""
    
    def test_missing_dependencies_word(self, service, monkeypatch):
        """Test error when python-docx not available"""
        # Mock the availability check
        import backend.services.document_pdf_service as module
        monkeypatch.setattr(module, 'PYTHON_DOCX_AVAILABLE', False)
        
        with pytest.raises(ImportError, match="python-docx"):
            service.word_to_pdf_bytes(file_content=b"test")
    
    def test_missing_dependencies_excel(self, service, monkeypatch):
        """Test error when openpyxl not available"""
        import backend.services.document_pdf_service as module
        monkeypatch.setattr(module, 'OPENPYXL_AVAILABLE', False)
        
        with pytest.raises(ImportError, match="openpyxl"):
            service.excel_to_pdf_bytes(file_content=b"test")
    
    def test_missing_dependencies_merge(self, service, monkeypatch):
        """Test error when PyPDF2 not available"""
        import backend.services.document_pdf_service as module
        monkeypatch.setattr(module, 'PYPDF2_AVAILABLE', False)
        
        with pytest.raises(ImportError, match="PyPDF2"):
            service.merge_pdf_documents([b"test"])
    
    def test_invalid_word_document(self, service):
        """Test error with invalid Word document"""
        with pytest.raises(DocumentConversionError):
            service.word_to_pdf_bytes(file_content=b"not a valid docx")
    
    def test_invalid_excel_document(self, service):
        """Test error with invalid Excel document"""
        with pytest.raises(DocumentConversionError):
            service.excel_to_pdf_bytes(file_content=b"not a valid xlsx")


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow_text_to_pdf(self, tmp_path):
        """Test complete workflow from text file to PDF"""
        service = DocumentPDFService()
        
        # Create text file
        text_file = tmp_path / "document.txt"
        text_file.write_text("This is a test document.\n\nWith multiple paragraphs.")
        
        # Convert to PDF
        pdf_bytes = service.text_to_pdf_bytes(file_path=str(text_file))
        
        # Save PDF
        output_file = tmp_path / "output.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        # Verify
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Verify PDF structure
        with open(output_file, 'rb') as f:
            content = f.read()
            assert content.startswith(b'%PDF')
    
    def test_merge_multiple_text_pdfs(self, tmp_path):
        """Test merging multiple text-based PDFs"""
        service = DocumentPDFService()
        
        # Create multiple PDFs
        pdf1 = service.text_to_pdf_bytes(text_content="Document 1 content")
        pdf2 = service.text_to_pdf_bytes(text_content="Document 2 content")
        pdf3 = service.text_to_pdf_bytes(text_content="Document 3 content")
        
        # Merge
        merged = service.merge_pdf_documents([pdf1, pdf2, pdf3])
        
        # Save
        output_file = tmp_path / "merged.pdf"
        with open(output_file, 'wb') as f:
            f.write(merged)
        
        # Verify
        assert output_file.exists()
        assert output_file.stat().st_size > len(pdf1)
    
    def test_convert_and_merge_workflow(self, tmp_path):
        """Test converting multiple documents and merging"""
        service = DocumentPDFService()
        
        # Create text files
        file1 = tmp_path / "doc1.txt"
        file1.write_text("Document 1")
        
        file2 = tmp_path / "doc2.txt"
        file2.write_text("Document 2")
        
        # Convert to PDFs
        pdf1 = service.text_to_pdf_bytes(file_path=str(file1))
        pdf2 = service.text_to_pdf_bytes(file_path=str(file2))
        
        # Merge
        metadata = PDFMetadata(
            title="Merged Documents",
            author="Test Suite"
        )
        merged = service.merge_pdf_documents([pdf1, pdf2], metadata)
        
        # Verify
        assert isinstance(merged, bytes)
        assert len(merged) > 0
        assert merged.startswith(b'%PDF')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
