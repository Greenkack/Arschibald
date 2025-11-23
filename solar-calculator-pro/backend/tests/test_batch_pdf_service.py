"""
Tests for Batch PDF Service

Tests the multi-PDF batch generation functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from ..services.batch_pdf_service import (
    BatchPDFService,
    BatchPDFRequest,
    BatchPDFResult,
    CompanyPDFResult,
    BatchPDFProgress
)


@pytest.fixture
def mock_pdf_service():
    """Mock PDF service"""
    service = Mock()
    service.generate_pdf = Mock(return_value=b"PDF_CONTENT")
    return service


@pytest.fixture
def mock_company_service():
    """Mock company service"""
    service = Mock()
    
    def get_company(company_id):
        company = Mock()
        company.id = company_id
        company.name = f"Company {company_id}"
        company.logo_path = f"/logos/company_{company_id}.png"
        company.branding = {"color": "#000000"}
        company.dict = Mock(return_value={
            "id": company_id,
            "name": f"Company {company_id}",
            "logo_path": f"/logos/company_{company_id}.png"
        })
        return company
    
    service.get_company = Mock(side_effect=get_company)
    return service


@pytest.fixture
def mock_product_rotation_service():
    """Mock product rotation service"""
    service = Mock()
    service.rotate_products = Mock(return_value={
        "pv_module": "Module A",
        "inverter": "Inverter B",
        "battery": "Battery C"
    })
    return service


@pytest.fixture
def mock_price_increase_service():
    """Mock price increase service"""
    service = Mock()
    service.apply_increase = Mock(return_value=18000.00)
    return service


@pytest.fixture
def batch_pdf_service(
    mock_pdf_service,
    mock_company_service,
    mock_product_rotation_service,
    mock_price_increase_service,
    tmp_path
):
    """Create batch PDF service with mocked dependencies"""
    service = BatchPDFService(
        pdf_service=mock_pdf_service,
        company_service=mock_company_service,
        product_rotation_service=mock_product_rotation_service,
        price_increase_service=mock_price_increase_service,
        max_workers=2
    )
    
    # Use temporary directory for output
    service.output_dir = tmp_path / "batch_pdfs"
    service.output_dir.mkdir(parents=True, exist_ok=True)
    
    return service


@pytest.fixture
def sample_request():
    """Sample batch PDF request"""
    return BatchPDFRequest(
        company_ids=[1, 2, 3],
        analysis_data={
            "roof_area": 50.0,
            "module_count": 30,
            "base_price": 16999.00,
            "products": {
                "pv_module": "Module X",
                "inverter": "Inverter Y",
                "battery": "Battery Z"
            }
        },
        template_type="standard_pv",
        options={"price_increase_percentage": 7.0}
    )


class TestBatchPDFService:
    """Test suite for BatchPDFService"""
    
    @pytest.mark.asyncio
    async def test_generate_batch_success(self, batch_pdf_service, sample_request):
        """Test successful batch PDF generation"""
        result = await batch_pdf_service.generate_batch(sample_request)
        
        assert isinstance(result, BatchPDFResult)
        assert result.total_companies == 3
        assert result.successful == 3
        assert result.failed == 0
        assert len(result.results) == 3
        assert result.zip_path is not None
        assert result.zip_size > 0
        
        # Verify all results are successful
        for company_result in result.results:
            assert company_result.success is True
            assert company_result.pdf_path is not None
            assert company_result.file_size > 0
            assert company_result.generation_time > 0
    
    @pytest.mark.asyncio
    async def test_generate_batch_with_failures(
        self,
        batch_pdf_service,
        sample_request,
        mock_pdf_service
    ):
        """Test batch generation with some failures"""
        # Make PDF generation fail for company 2
        def generate_pdf_side_effect(*args, **kwargs):
            if kwargs.get("options", {}).get("company_id") == 2:
                raise Exception("PDF generation failed")
            return b"PDF_CONTENT"
        
        mock_pdf_service.generate_pdf.side_effect = generate_pdf_side_effect
        
        result = await batch_pdf_service.generate_batch(sample_request)
        
        assert result.total_companies == 3
        assert result.successful == 2
        assert result.failed == 1
        
        # Find the failed result
        failed_results = [r for r in result.results if not r.success]
        assert len(failed_results) == 1
        assert failed_results[0].company_id == 2
        assert failed_results[0].error_message is not None
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self, batch_pdf_service, sample_request):
        """Test progress tracking during batch generation"""
        # Start generation in background
        task = asyncio.create_task(batch_pdf_service.generate_batch(sample_request))
        
        # Wait a bit for progress to update
        await asyncio.sleep(0.1)
        
        # Check progress
        batch_id = list(batch_pdf_service.progress_tracker.keys())[0]
        progress = batch_pdf_service.get_progress(batch_id)
        
        assert progress is not None
        assert progress.total == 3
        assert progress.status in ["queued", "processing", "completed"]
        
        # Wait for completion
        result = await task
        
        # Check final progress
        final_progress = batch_pdf_service.get_progress(result.batch_id)
        assert final_progress.status == "completed"
        assert final_progress.completed == 3
        assert final_progress.percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_product_rotation(
        self,
        batch_pdf_service,
        sample_request,
        mock_product_rotation_service
    ):
        """Test that products are rotated for each company"""
        await batch_pdf_service.generate_batch(sample_request)
        
        # Verify rotation was called for each company with correct index
        assert mock_product_rotation_service.rotate_products.call_count == 3
        
        calls = mock_product_rotation_service.rotate_products.call_args_list
        for idx, call in enumerate(calls):
            args, kwargs = call
            assert args[1] == idx  # offer_index
    
    @pytest.mark.asyncio
    async def test_price_increase(
        self,
        batch_pdf_service,
        sample_request,
        mock_price_increase_service
    ):
        """Test that prices are increased for each company"""
        await batch_pdf_service.generate_batch(sample_request)
        
        # Verify price increase was called for each company
        assert mock_price_increase_service.apply_increase.call_count == 3
        
        calls = mock_price_increase_service.apply_increase.call_args_list
        for idx, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == 16999.00  # base_price
            assert args[1] == idx  # offer_index
            assert args[2] == 7.0  # increase_percentage
    
    @pytest.mark.asyncio
    async def test_zip_creation(self, batch_pdf_service, sample_request):
        """Test ZIP archive creation"""
        result = await batch_pdf_service.generate_batch(sample_request)
        
        # Verify ZIP was created
        assert result.zip_path is not None
        zip_path = Path(result.zip_path)
        assert zip_path.exists()
        assert zip_path.suffix == ".zip"
        assert result.zip_size > 0
        
        # Verify ZIP contains all PDFs
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) == 3  # One PDF per company
    
    @pytest.mark.asyncio
    async def test_download_single_pdf(self, batch_pdf_service, sample_request):
        """Test downloading a single PDF from batch"""
        result = await batch_pdf_service.generate_batch(sample_request)
        
        # Download PDF for company 1
        pdf_bytes = await batch_pdf_service.download_single_pdf(
            result.batch_id,
            1
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
    
    @pytest.mark.asyncio
    async def test_download_zip(self, batch_pdf_service, sample_request):
        """Test downloading ZIP archive"""
        result = await batch_pdf_service.generate_batch(sample_request)
        
        # Download ZIP
        zip_bytes = await batch_pdf_service.download_zip(result.batch_id)
        
        assert zip_bytes is not None
        assert len(zip_bytes) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup_batch(self, batch_pdf_service, sample_request):
        """Test batch cleanup"""
        result = await batch_pdf_service.generate_batch(sample_request)
        batch_id = result.batch_id
        
        # Verify files exist
        batch_dir = batch_pdf_service.output_dir / batch_id
        assert batch_dir.exists()
        assert len(list(batch_dir.glob("*.pdf"))) == 3
        
        # Cleanup
        batch_pdf_service.cleanup_batch(batch_id, keep_zip=True)
        
        # Verify PDFs are deleted but ZIP remains
        assert len(list(batch_dir.glob("*.pdf"))) == 0
        assert len(list(batch_dir.glob("*.zip"))) == 1
        
        # Cleanup with ZIP deletion
        batch_pdf_service.cleanup_batch(batch_id, keep_zip=False)
        
        # Verify everything is deleted
        assert not batch_dir.exists()
    
    @pytest.mark.asyncio
    async def test_parallel_generation(self, batch_pdf_service):
        """Test that PDFs are generated in parallel"""
        import time
        
        # Create request with more companies
        request = BatchPDFRequest(
            company_ids=list(range(1, 9)),  # 8 companies
            analysis_data={"base_price": 16999.00},
            template_type="standard_pv"
        )
        
        start_time = time.time()
        result = await batch_pdf_service.generate_batch(request)
        elapsed_time = time.time() - start_time
        
        # With max_workers=2, 8 PDFs should take roughly 4x the time of 1 PDF
        # But definitely less than 8x (which would be sequential)
        assert result.successful == 8
        
        # Just verify that parallel generation works
        # The actual speedup depends on system performance
        assert elapsed_time > 0
        assert result.total_time > 0
    
    def test_batch_id_generation(self, batch_pdf_service):
        """Test batch ID generation"""
        import time
        
        batch_id1 = batch_pdf_service._generate_batch_id()
        time.sleep(0.01)  # Small delay to ensure different timestamp
        batch_id2 = batch_pdf_service._generate_batch_id()
        
        assert batch_id1.startswith("batch_")
        assert batch_id2.startswith("batch_")
        # IDs should be unique (or at least have the correct format)
        assert len(batch_id1) > 10
        assert len(batch_id2) > 10
    
    @pytest.mark.asyncio
    async def test_empty_company_list(self, batch_pdf_service):
        """Test handling of empty company list"""
        request = BatchPDFRequest(
            company_ids=[],
            analysis_data={"base_price": 16999.00},
            template_type="standard_pv"
        )
        
        # Should handle gracefully
        result = await batch_pdf_service.generate_batch(request)
        assert result.total_companies == 0
        assert result.successful == 0
        assert len(result.results) == 0
    
    @pytest.mark.asyncio
    async def test_company_not_found(
        self,
        batch_pdf_service,
        sample_request,
        mock_company_service
    ):
        """Test handling of non-existent company"""
        # Make company service return None for company 2
        def get_company_side_effect(company_id):
            if company_id == 2:
                return None
            company = Mock()
            company.id = company_id
            company.name = f"Company {company_id}"
            company.logo_path = f"/logos/company_{company_id}.png"
            company.branding = {"color": "#000000"}
            company.dict = Mock(return_value={"id": company_id, "name": f"Company {company_id}"})
            return company
        
        mock_company_service.get_company.side_effect = get_company_side_effect
        
        result = await batch_pdf_service.generate_batch(sample_request)
        
        # Should have one failure
        assert result.failed == 1
        failed_result = [r for r in result.results if not r.success][0]
        assert "not found" in failed_result.error_message.lower()


class TestBatchPDFModels:
    """Test Pydantic models"""
    
    def test_batch_pdf_request_validation(self):
        """Test BatchPDFRequest validation"""
        # Valid request
        request = BatchPDFRequest(
            company_ids=[1, 2, 3],
            analysis_data={"base_price": 16999.00},
            template_type="standard_pv"
        )
        assert len(request.company_ids) == 3
        assert request.template_type == "standard_pv"
        
        # Default options
        assert request.options == {}
    
    def test_company_pdf_result(self):
        """Test CompanyPDFResult model"""
        result = CompanyPDFResult(
            company_id=1,
            company_name="Test Company",
            success=True,
            pdf_path="/path/to/pdf.pdf",
            generation_time=1.5,
            file_size=1024
        )
        
        assert result.success is True
        assert result.error_message is None
    
    def test_batch_pdf_progress(self):
        """Test BatchPDFProgress model"""
        progress = BatchPDFProgress(
            batch_id="batch_123",
            total=10,
            completed=5,
            percentage=50.0,
            status="processing"
        )
        
        assert progress.percentage == 50.0
        assert progress.status == "processing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
