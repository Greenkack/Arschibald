"""
Tests for PDF Byte Generation Core

Tests the PDFByteMixin, PDFRenderingEngine, and related functionality.
"""

import pytest
import io
import base64
from datetime import datetime
from typing import List

# Import the module to test
import sys
from pathlib import Path
parent_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_path))

from backend.core.pdf_bytes import (
    PDFMetadata,
    PDFRenderingEngine,
    PDFByteMixin,
    SimplePDFDocument,
    create_pdf_from_dict,
    create_pdf_from_text,
    REPORTLAB_AVAILABLE
)

# Skip all tests if reportlab is not available
pytestmark = pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)


class TestPDFMetadata:
    """Test PDF metadata functionality"""
    
    def test_create_metadata(self):
        """Test creating PDF metadata"""
        metadata = PDFMetadata(
            title="Test Document",
            author="Test Author",
            subject="Test Subject",
            keywords=["test", "pdf"]
        )
        
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.subject == "Test Subject"
        assert metadata.keywords == ["test", "pdf"]
        assert isinstance(metadata.creation_date, datetime)
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary"""
        metadata = PDFMetadata(
            title="Test",
            author="Author",
            keywords=["key1", "key2"]
        )
        
        data = metadata.to_dict()
        
        assert data['title'] == "Test"
        assert data['author'] == "Author"
        assert data['keywords'] == "key1, key2"
        assert 'creation_date' in data
    
    def test_default_metadata(self):
        """Test default metadata values"""
        metadata = PDFMetadata()
        
        assert metadata.title == ""
        assert metadata.creator == "Solar Calculator Pro"
        assert metadata.keywords == []


class TestPDFRenderingEngine:
    """Test PDF rendering engine"""
    
    def test_create_engine(self):
        """Test creating rendering engine"""
        engine = PDFRenderingEngine()
        
        assert engine.page_size is not None
        assert engine.width > 0
        assert engine.height > 0
    
    def test_create_document(self):
        """Test creating PDF document"""
        engine = PDFRenderingEngine()
        buffer = io.BytesIO()
        metadata = PDFMetadata(title="Test")
        
        doc = engine.create_document(buffer, metadata)
        
        assert doc is not None
        assert doc.title == "Test"
    
    def test_create_canvas(self):
        """Test creating PDF canvas"""
        engine = PDFRenderingEngine()
        buffer = io.BytesIO()
        metadata = PDFMetadata(title="Test Canvas")
        
        canvas = engine.create_canvas(buffer, metadata)
        
        assert canvas is not None
    
    def test_format_german_number(self):
        """Test German number formatting"""
        engine = PDFRenderingEngine()
        
        # Test basic formatting
        assert engine.format_german_number(1234.56) == "1.234,56"
        assert engine.format_german_number(1000000.99) == "1.000.000,99"
        assert engine.format_german_number(0.5) == "0,50"
        
        # Test with different decimal places
        assert engine.format_german_number(1234.567, decimals=3) == "1.234,567"
        assert engine.format_german_number(1234.5, decimals=0) == "1.234"  # Rounds down
    
    def test_create_table(self):
        """Test creating PDF table"""
        engine = PDFRenderingEngine()
        
        data = [
            ['Header 1', 'Header 2'],
            ['Value 1', 'Value 2'],
            ['Value 3', 'Value 4']
        ]
        
        table = engine.create_table(data)
        
        assert table is not None


class SamplePDFModel(PDFByteMixin):
    """Sample model for testing PDFByteMixin"""
    
    def __init__(self, title: str, data: dict):
        super().__init__()
        self.title = title
        self.data = data
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _render_to_pdf(self, story: List, doc):
        """Render sample data to PDF"""
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, Spacer
        
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add data
        for key, value in self.data.items():
            text = f"<b>{key}:</b> {value}"
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 6))


class TestPDFByteMixin:
    """Test PDFByteMixin functionality"""
    
    def test_to_pdf_bytes(self):
        """Test generating PDF bytes"""
        model = SamplePDFModel(
            title="Test Document",
            data={"key1": "value1", "key2": "value2"}
        )
        
        pdf_bytes = model.to_pdf_bytes()
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF magic number
    
    def test_to_pdf_base64(self):
        """Test generating base64-encoded PDF"""
        model = SamplePDFModel(
            title="Test Document",
            data={"key1": "value1"}
        )
        
        pdf_base64 = model.to_pdf_base64()
        
        assert isinstance(pdf_base64, str)
        assert len(pdf_base64) > 0
        
        # Verify it's valid base64
        decoded = base64.b64decode(pdf_base64)
        assert decoded.startswith(b'%PDF')
    
    def test_set_pdf_metadata(self):
        """Test setting PDF metadata"""
        model = SamplePDFModel(
            title="Test",
            data={}
        )
        
        metadata = PDFMetadata(
            title="Custom Title",
            author="Custom Author"
        )
        model.set_pdf_metadata(metadata)
        
        retrieved = model.get_pdf_metadata()
        assert retrieved.title == "Custom Title"
        assert retrieved.author == "Custom Author"
    
    def test_save_pdf(self, tmp_path):
        """Test saving PDF to file"""
        model = SamplePDFModel(
            title="Test Document",
            data={"test": "data"}
        )
        
        filepath = tmp_path / "test.pdf"
        model.save_pdf(str(filepath))
        
        assert filepath.exists()
        assert filepath.stat().st_size > 0
        
        # Verify it's a valid PDF
        with open(filepath, 'rb') as f:
            content = f.read()
            assert content.startswith(b'%PDF')
    
    def test_pdf_with_german_numbers(self):
        """Test PDF generation with German-formatted numbers"""
        model = SamplePDFModel(
            title="Numbers Test",
            data={
                "price": 1234.56,
                "quantity": 1000,
                "total": 1234560.00
            }
        )
        
        pdf_bytes = model.to_pdf_bytes()
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestSimplePDFDocument:
    """Test SimplePDFDocument class"""
    
    def test_create_simple_document(self):
        """Test creating a simple PDF document"""
        doc = SimplePDFDocument(
            title="Simple Test",
            content="This is test content.\n\nThis is a second paragraph."
        )
        
        pdf_bytes = doc.to_pdf_bytes()
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_empty_document(self):
        """Test creating an empty document"""
        doc = SimplePDFDocument()
        
        pdf_bytes = doc.to_pdf_bytes()
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_pdf_from_dict(self):
        """Test creating PDF from dictionary"""
        data = {
            "Name": "Test User",
            "Age": 30,
            "Price": 1234.56,
            "Quantity": 1000
        }
        
        pdf_bytes = create_pdf_from_dict(data, title="Test Report")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_create_pdf_from_text(self):
        """Test creating PDF from text"""
        text = "This is a test document.\n\nIt has multiple paragraphs."
        
        pdf_bytes = create_pdf_from_text(text, title="Text Document")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_create_pdf_with_metadata(self):
        """Test creating PDF with custom metadata"""
        metadata = PDFMetadata(
            title="Custom Report",
            author="Test Author",
            subject="Testing",
            keywords=["test", "report"]
        )
        
        data = {"test": "value"}
        pdf_bytes = create_pdf_from_dict(data, metadata=metadata)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestGermanNumberFormatting:
    """Test German number formatting in PDFs"""
    
    def test_format_various_numbers(self):
        """Test formatting various number types"""
        engine = PDFRenderingEngine()
        
        test_cases = [
            (0, "0,00"),
            (1, "1,00"),
            (10, "10,00"),
            (100, "100,00"),
            (1000, "1.000,00"),
            (10000, "10.000,00"),
            (100000, "100.000,00"),
            (1000000, "1.000.000,00"),
            (0.5, "0,50"),
            (0.99, "0,99"),
            (1234.56, "1.234,56"),
            (9999.99, "9.999,99"),
        ]
        
        for value, expected in test_cases:
            result = engine.format_german_number(value)
            assert result == expected, f"Failed for {value}: got {result}, expected {expected}"
    
    def test_format_negative_numbers(self):
        """Test formatting negative numbers"""
        engine = PDFRenderingEngine()
        
        assert engine.format_german_number(-1234.56) == "-1.234,56"
        assert engine.format_german_number(-0.5) == "-0,50"


class TestPDFIntegration:
    """Integration tests for PDF generation"""
    
    def test_complete_pdf_workflow(self, tmp_path):
        """Test complete PDF generation workflow"""
        # Create model with data
        model = SamplePDFModel(
            title="Integration Test",
            data={
                "Customer": "Test Customer",
                "Price": 1234.56,
                "Quantity": 100,
                "Total": 123456.00
            }
        )
        
        # Set metadata
        metadata = PDFMetadata(
            title="Integration Test Report",
            author="Test System",
            subject="Testing",
            keywords=["integration", "test"]
        )
        model.set_pdf_metadata(metadata)
        
        # Generate PDF bytes
        pdf_bytes = model.to_pdf_bytes()
        assert len(pdf_bytes) > 0
        
        # Generate base64
        pdf_base64 = model.to_pdf_base64()
        assert len(pdf_base64) > 0
        
        # Save to file
        filepath = tmp_path / "integration_test.pdf"
        model.save_pdf(str(filepath))
        assert filepath.exists()
        
        # Verify file content is valid PDF (content may differ due to timestamps)
        with open(filepath, 'rb') as f:
            file_content = f.read()
            assert file_content.startswith(b'%PDF')
            assert len(file_content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
