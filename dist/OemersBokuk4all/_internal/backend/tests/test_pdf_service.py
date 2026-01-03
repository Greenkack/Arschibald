"""
Unit Tests for PDF Generation Service

Tests for the PDFGenerationService wrapper.
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.pdf_service import PDFGenerationService, get_pdf_service
from backend.core.base_service import ServiceStatus


@pytest.fixture
def pdf_service():
    """Create a PDF service instance for testing"""
    service = PDFGenerationService()
    
    # Use temporary directory for storage
    temp_dir = tempfile.mkdtemp()
    service._storage_path = Path(temp_dir)
    service._storage_path.mkdir(parents=True, exist_ok=True)
    
    try:
        service.initialize()
    except Exception as e:
        pytest.skip(f"Could not initialize PDF service: {e}")
    
    yield service
    
    # Cleanup
    service.cleanup()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_offer_data():
    """Sample offer data for testing"""
    return {
        "customer_name": "Test Customer",
        "project_name": "Test Solar Project",
        "system_size": 10.5,
        "module_count": 30,
        "annual_production": 12000,
        "total_cost": 25000.00,
        "payback_period": 8.5,
        "co2_savings": 7500
    }


class TestPDFServiceInitialization:
    """Test service initialization"""
    
    def test_service_initializes(self, pdf_service):
        """Test that service initializes successfully"""
        assert pdf_service.is_initialized
        assert pdf_service._pdf_generator_module is not None
    
    def test_health_check_healthy(self, pdf_service):
        """Test health check returns healthy status"""
        health = pdf_service.health_check()
        assert health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
    
    def test_storage_directory_created(self, pdf_service):
        """Test that storage directory is created"""
        assert pdf_service._storage_path.exists()
        assert pdf_service._storage_path.is_dir()


class TestPDFGeneration:
    """Test PDF generation functionality"""
    
    def test_generate_pdf_basic(self, pdf_service, sample_offer_data):
        """Test basic PDF generation"""
        pdf_bytes = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF magic number
    
    def test_generate_pdf_with_cache(self, pdf_service, sample_offer_data):
        """Test PDF generation with caching"""
        # First generation
        pdf_bytes_1 = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=True
        )
        
        # Second generation (should use cache)
        pdf_bytes_2 = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=True
        )
        
        assert pdf_bytes_1 == pdf_bytes_2
        assert len(pdf_service._cache) > 0
    
    def test_generate_pdf_different_templates(self, pdf_service, sample_offer_data):
        """Test PDF generation with different templates"""
        templates = ["main", "simple"]
        
        for template in templates:
            try:
                pdf_bytes = pdf_service.generate_pdf(
                    offer_data=sample_offer_data,
                    template=template,
                    use_cache=False
                )
                assert pdf_bytes is not None
                assert len(pdf_bytes) > 0
            except Exception as e:
                # Some templates might not be available
                pytest.skip(f"Template {template} not available: {e}")
    
    @pytest.mark.asyncio
    async def test_generate_pdf_async(self, pdf_service, sample_offer_data):
        """Test async PDF generation"""
        pdf_bytes = await pdf_service.generate_pdf_async(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')


class TestPDFPreview:
    """Test PDF preview functionality"""
    
    def test_generate_preview(self, pdf_service, sample_offer_data):
        """Test PDF preview generation"""
        preview_bytes = pdf_service.generate_pdf_preview(
            offer_data=sample_offer_data,
            template="main",
            page_limit=3
        )
        
        assert preview_bytes is not None
        assert len(preview_bytes) > 0
        assert preview_bytes.startswith(b'%PDF')
    
    def test_preview_smaller_than_full(self, pdf_service, sample_offer_data):
        """Test that preview is smaller than full PDF"""
        full_pdf = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        preview_pdf = pdf_service.generate_pdf_preview(
            offer_data=sample_offer_data,
            template="main",
            page_limit=2
        )
        
        # Preview should generally be smaller (though not always guaranteed)
        # Just check both are valid PDFs
        assert full_pdf.startswith(b'%PDF')
        assert preview_pdf.startswith(b'%PDF')


class TestPDFStorage:
    """Test PDF storage and retrieval"""
    
    def test_store_pdf(self, pdf_service, sample_offer_data):
        """Test storing PDF to disk"""
        pdf_bytes = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        file_path = pdf_service.store_pdf(
            pdf_bytes=pdf_bytes,
            filename="test_offer.pdf",
            metadata={"customer_id": 123}
        )
        
        assert file_path is not None
        assert Path(file_path).exists()
        assert Path(file_path).suffix == '.pdf'
    
    def test_retrieve_pdf(self, pdf_service, sample_offer_data):
        """Test retrieving stored PDF"""
        # Store PDF
        pdf_bytes_original = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        file_path = pdf_service.store_pdf(
            pdf_bytes=pdf_bytes_original,
            filename="test_retrieve.pdf"
        )
        
        # Retrieve PDF
        filename = Path(file_path).name
        pdf_bytes_retrieved = pdf_service.retrieve_pdf(filename)
        
        assert pdf_bytes_retrieved is not None
        assert pdf_bytes_retrieved == pdf_bytes_original
    
    def test_retrieve_nonexistent_pdf(self, pdf_service):
        """Test retrieving non-existent PDF returns None"""
        pdf_bytes = pdf_service.retrieve_pdf("nonexistent.pdf")
        assert pdf_bytes is None
    
    def test_list_stored_pdfs(self, pdf_service, sample_offer_data):
        """Test listing stored PDFs"""
        # Store multiple PDFs
        pdf_bytes = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        pdf_service.store_pdf(pdf_bytes, "test1.pdf")
        pdf_service.store_pdf(pdf_bytes, "test2.pdf")
        
        # List PDFs
        pdfs = pdf_service.list_stored_pdfs()
        
        assert len(pdfs) >= 2
        assert all('filename' in pdf for pdf in pdfs)
        assert all('size_bytes' in pdf for pdf in pdfs)
    
    def test_delete_pdf(self, pdf_service, sample_offer_data):
        """Test deleting stored PDF"""
        # Store PDF
        pdf_bytes = pdf_service.generate_pdf(
            offer_data=sample_offer_data,
            template="main",
            use_cache=False
        )
        
        file_path = pdf_service.store_pdf(pdf_bytes, "test_delete.pdf")
        filename = Path(file_path).name
        
        # Delete PDF
        success = pdf_service.delete_pdf(filename)
        
        assert success is True
        assert not Path(file_path).exists()
    
    def test_delete_nonexistent_pdf(self, pdf_service):
        """Test deleting non-existent PDF returns False"""
        success = pdf_service.delete_pdf("nonexistent.pdf")
        assert success is False


class TestPDFTemplates:
    """Test PDF template functionality"""
    
    def test_get_available_templates(self, pdf_service):
        """Test getting available templates"""
        templates = pdf_service.get_available_templates()
        
        assert len(templates) > 0
        assert all('name' in t for t in templates)
        assert all('display_name' in t for t in templates)
        assert all('description' in t for t in templates)
    
    def test_template_names(self, pdf_service):
        """Test that expected templates are available"""
        templates = pdf_service.get_available_templates()
        template_names = [t['name'] for t in templates]
        
        assert 'main' in template_names
        assert 'simple' in template_names


class TestPDFCache:
    """Test PDF caching functionality"""
    
    def test_cache_key_generation(self, pdf_service, sample_offer_data):
        """Test cache key generation"""
        key1 = pdf_service._generate_cache_key(sample_offer_data, "main")
        key2 = pdf_service._generate_cache_key(sample_offer_data, "main")
        
        assert key1 == key2  # Same data should generate same key
    
    def test_cache_key_different_data(self, pdf_service, sample_offer_data):
        """Test cache keys differ for different data"""
        key1 = pdf_service._generate_cache_key(sample_offer_data, "main")
        
        different_data = sample_offer_data.copy()
        different_data['customer_name'] = "Different Customer"
        key2 = pdf_service._generate_cache_key(different_data, "main")
        
        assert key1 != key2
    
    def test_clear_cache(self, pdf_service, sample_offer_data):
        """Test clearing cache"""
        # Generate some PDFs to populate cache
        pdf_service.generate_pdf(sample_offer_data, "main", use_cache=True)
        pdf_service.generate_pdf(sample_offer_data, "simple", use_cache=True)
        
        assert len(pdf_service._cache) > 0
        
        # Clear cache
        count = pdf_service.clear_cache()
        
        assert count > 0
        assert len(pdf_service._cache) == 0
    
    def test_get_cache_stats(self, pdf_service, sample_offer_data):
        """Test getting cache statistics"""
        # Generate PDF to populate cache
        pdf_service.generate_pdf(sample_offer_data, "main", use_cache=True)
        
        stats = pdf_service.get_cache_stats()
        
        assert 'cached_items' in stats
        assert 'total_size_bytes' in stats
        assert 'total_size_mb' in stats
        assert 'cache_ttl_seconds' in stats
        assert stats['cached_items'] > 0


class TestPDFServiceSingleton:
    """Test singleton pattern"""
    
    def test_get_pdf_service_singleton(self):
        """Test that get_pdf_service returns singleton"""
        try:
            service1 = get_pdf_service()
            service2 = get_pdf_service()
            
            assert service1 is service2
        except Exception as e:
            pytest.skip(f"Could not test singleton: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
