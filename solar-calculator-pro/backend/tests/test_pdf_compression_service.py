"""
Tests for PDF Compression Service

Tests all PDF compression and optimization functionality.
"""

import pytest
import io
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    from pypdf import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

from ..services.pdf_compression_service import PDFCompressionService, pdf_compression_service


@pytest.fixture
def sample_pdf():
    """Create a sample PDF for testing"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Add multiple pages with content
    for i in range(3):
        pdf.drawString(100, 800, f"Page {i + 1}")
        pdf.drawString(100, 750, "This is a test PDF for compression testing")
        pdf.drawString(100, 700, "It contains multiple pages with text content")
        pdf.showPage()
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_pdf_with_image():
    """Create a sample PDF with an embedded image"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Create a test image
    img = Image.new('RGB', (800, 600), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Add image to PDF
    pdf.drawString(100, 800, "PDF with Image")
    pdf.drawImage(img_buffer, 100, 400, width=400, height=300)
    pdf.showPage()
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def service():
    """Get PDF compression service instance"""
    return PDFCompressionService()


class TestPDFCompression:
    """Test PDF compression functionality"""
    
    def test_compress_pdf_basic(self, service, sample_pdf):
        """Test basic PDF compression"""
        compressed = service.compress_pdf(sample_pdf)
        
        assert compressed is not None
        assert len(compressed) > 0
        assert len(compressed) <= len(sample_pdf)
        
        # Verify PDF is still valid
        reader = PdfReader(io.BytesIO(compressed))
        assert len(reader.pages) == 3
    
    def test_compress_pdf_with_options(self, service, sample_pdf):
        """Test PDF compression with custom options"""
        compressed = service.compress_pdf(
            sample_pdf,
            compression_level=9,
            optimize_images=True,
            image_quality=75,
            remove_duplicates=True,
            compress_streams=True
        )
        
        assert compressed is not None
        assert len(compressed) <= len(sample_pdf)
    
    def test_compress_pdf_with_images(self, service, sample_pdf_with_image):
        """Test PDF compression with images"""
        compressed = service.compress_pdf(
            sample_pdf_with_image,
            optimize_images=True,
            image_quality=85
        )
        
        assert compressed is not None
        assert len(compressed) <= len(sample_pdf_with_image)
    
    def test_compression_levels(self, service, sample_pdf):
        """Test different compression levels"""
        sizes = []
        
        for level in [0, 5, 9]:
            compressed = service.compress_pdf(
                sample_pdf,
                compression_level=level
            )
            sizes.append(len(compressed))
        
        # Higher compression should generally result in smaller files
        assert all(size > 0 for size in sizes)


class TestFontOptimization:
    """Test font optimization functionality"""
    
    def test_optimize_fonts_basic(self, service, sample_pdf):
        """Test basic font optimization"""
        optimized = service.optimize_fonts(sample_pdf)
        
        assert optimized is not None
        assert len(optimized) > 0
        
        # Verify PDF is still valid
        reader = PdfReader(io.BytesIO(optimized))
        assert len(reader.pages) == 3
    
    def test_optimize_fonts_with_options(self, service, sample_pdf):
        """Test font optimization with options"""
        optimized = service.optimize_fonts(
            sample_pdf,
            subset_fonts=True,
            embed_fonts=True
        )
        
        assert optimized is not None


class TestPDFStreaming:
    """Test PDF streaming functionality"""
    
    def test_stream_pdf_basic(self, service, sample_pdf):
        """Test basic PDF streaming"""
        chunks = list(service.stream_pdf(sample_pdf))
        
        assert len(chunks) > 0
        
        # Reconstruct PDF from chunks
        reconstructed = b''.join(chunks)
        assert reconstructed == sample_pdf
    
    def test_stream_pdf_custom_chunk_size(self, service, sample_pdf):
        """Test PDF streaming with custom chunk size"""
        chunk_size = 1024
        chunks = list(service.stream_pdf(sample_pdf, chunk_size=chunk_size))
        
        assert len(chunks) > 0
        
        # All chunks except last should be exactly chunk_size
        for chunk in chunks[:-1]:
            assert len(chunk) == chunk_size
        
        # Last chunk can be smaller
        assert len(chunks[-1]) <= chunk_size


class TestPDFEncryption:
    """Test PDF encryption functionality"""
    
    def test_encrypt_pdf_basic(self, service, sample_pdf):
        """Test basic PDF encryption"""
        encrypted = service.encrypt_pdf(
            sample_pdf,
            user_password="user123"
        )
        
        assert encrypted is not None
        assert len(encrypted) > 0
        
        # Verify PDF is encrypted
        reader = PdfReader(io.BytesIO(encrypted))
        assert reader.is_encrypted
    
    def test_encrypt_pdf_with_permissions(self, service, sample_pdf):
        """Test PDF encryption with permissions"""
        permissions = {
            'print': True,
            'modify': False,
            'copy': False,
            'annotate': False
        }
        
        encrypted = service.encrypt_pdf(
            sample_pdf,
            user_password="user123",
            owner_password="owner456",
            permissions=permissions
        )
        
        assert encrypted is not None
        
        reader = PdfReader(io.BytesIO(encrypted))
        assert reader.is_encrypted
    
    def test_encrypt_pdf_no_password(self, service, sample_pdf):
        """Test PDF encryption without password"""
        encrypted = service.encrypt_pdf(sample_pdf)
        
        assert encrypted is not None


class TestMetadataManagement:
    """Test PDF metadata management"""
    
    def test_add_metadata(self, service, sample_pdf):
        """Test adding metadata to PDF"""
        metadata = {
            '/Title': 'Test PDF',
            '/Author': 'Test Author',
            '/Subject': 'Testing',
            '/Keywords': 'test, pdf, compression'
        }
        
        updated = service.manage_metadata(sample_pdf, metadata=metadata)
        
        assert updated is not None
        
        # Verify metadata
        reader = PdfReader(io.BytesIO(updated))
        assert reader.metadata is not None
        assert reader.metadata.get('/Title') == 'Test PDF'
        assert reader.metadata.get('/Author') == 'Test Author'
    
    def test_remove_metadata(self, service, sample_pdf):
        """Test removing metadata from PDF"""
        # First add metadata
        metadata = {'/Title': 'Test PDF'}
        with_metadata = service.manage_metadata(sample_pdf, metadata=metadata)
        
        # Then remove it
        without_metadata = service.manage_metadata(
            with_metadata,
            remove_metadata=True
        )
        
        assert without_metadata is not None
        
        reader = PdfReader(io.BytesIO(without_metadata))
        # Metadata should be empty or None
        assert not reader.metadata or len(reader.metadata) == 0


class TestPDFInfo:
    """Test PDF information extraction"""
    
    def test_get_pdf_info(self, service, sample_pdf):
        """Test getting PDF information"""
        info = service.get_pdf_info(sample_pdf)
        
        assert info is not None
        assert 'num_pages' in info
        assert 'size_bytes' in info
        assert 'size_kb' in info
        assert 'size_mb' in info
        assert 'metadata' in info
        assert 'is_encrypted' in info
        assert 'page_sizes' in info
        
        assert info['num_pages'] == 3
        assert info['size_bytes'] == len(sample_pdf)
        assert not info['is_encrypted']
        assert len(info['page_sizes']) == 3


class TestCompleteOptimization:
    """Test complete PDF optimization"""
    
    def test_optimize_complete_basic(self, service, sample_pdf):
        """Test complete optimization with default options"""
        result = service.optimize_pdf_complete(sample_pdf)
        
        assert result is not None
        assert 'optimized_pdf' in result
        assert 'original_size_bytes' in result
        assert 'optimized_size_bytes' in result
        assert 'size_reduction_bytes' in result
        assert 'size_reduction_percent' in result
        
        assert result['optimized_size_bytes'] <= result['original_size_bytes']
        assert result['size_reduction_percent'] >= 0
    
    def test_optimize_complete_with_options(self, service, sample_pdf):
        """Test complete optimization with custom options"""
        options = {
            'compression_level': 9,
            'optimize_images': True,
            'image_quality': 75,
            'optimize_fonts': True,
            'add_metadata': True,
            'metadata': {
                '/Title': 'Optimized PDF',
                '/Author': 'Test'
            }
        }
        
        result = service.optimize_pdf_complete(sample_pdf, options=options)
        
        assert result is not None
        assert result['optimized_size_bytes'] <= result['original_size_bytes']
        
        # Verify metadata was added
        reader = PdfReader(io.BytesIO(result['optimized_pdf']))
        assert reader.metadata.get('/Title') == 'Optimized PDF'
    
    def test_optimize_complete_statistics(self, service, sample_pdf):
        """Test complete optimization statistics"""
        result = service.optimize_pdf_complete(sample_pdf)
        
        # Check original info
        assert 'original_info' in result
        assert result['original_info']['num_pages'] == 3
        
        # Check optimized info
        assert 'optimized_info' in result
        assert result['optimized_info']['num_pages'] == 3
        
        # Check options used
        assert 'options_used' in result


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_pdf(self, service):
        """Test handling of empty PDF"""
        with pytest.raises(Exception):
            service.compress_pdf(b'')
    
    def test_invalid_pdf(self, service):
        """Test handling of invalid PDF"""
        with pytest.raises(Exception):
            service.compress_pdf(b'not a pdf')
    
    def test_corrupted_pdf(self, service):
        """Test handling of corrupted PDF"""
        # Create a partially valid PDF
        corrupted = b'%PDF-1.4\n%%EOF'
        
        with pytest.raises(Exception):
            service.compress_pdf(corrupted)


class TestSingletonInstance:
    """Test singleton instance"""
    
    def test_singleton_exists(self):
        """Test that singleton instance exists"""
        assert pdf_compression_service is not None
        assert isinstance(pdf_compression_service, PDFCompressionService)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
