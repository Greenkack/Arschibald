"""
Multi-PDF Batch Generation Service

This service handles the generation of multiple PDFs for different companies
with a single request. It implements:
- Queue-based parallel PDF generation
- Progress tracking for batch operations
- Per-company error handling
- Batch result reporting
- ZIP download for all generated PDFs
"""

import asyncio
import io
import zipfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BatchPDFRequest(BaseModel):
    """Request model for batch PDF generation"""
    company_ids: List[int]
    analysis_data: Dict[str, Any]  # Same analysis data for all offers
    template_type: str = "standard_pv"  # standard_pv, extended_pv, standard_wp, etc.
    options: Dict[str, Any] = {}


class CompanyPDFResult(BaseModel):
    """Result for a single company PDF generation"""
    company_id: int
    company_name: str
    success: bool
    pdf_path: Optional[str] = None
    pdf_bytes: Optional[bytes] = None
    error_message: Optional[str] = None
    generation_time: float = 0.0
    file_size: Optional[int] = None


class BatchPDFResult(BaseModel):
    """Result for batch PDF generation"""
    batch_id: str
    total_companies: int
    successful: int
    failed: int
    results: List[CompanyPDFResult]
    total_time: float
    zip_path: Optional[str] = None
    zip_size: Optional[int] = None


class BatchPDFProgress(BaseModel):
    """Progress tracking for batch generation"""
    batch_id: str
    total: int
    completed: int
    current_company: Optional[str] = None
    percentage: float
    status: str  # 'queued', 'processing', 'completed', 'failed'


class BatchPDFService:
    """Service for batch PDF generation"""
    
    def __init__(
        self,
        pdf_service,  # Standard PDF service
        company_service,  # Company service
        product_rotation_service,  # Product rotation service
        price_increase_service,  # Price increase service
        max_workers: int = 4
    ):
        self.pdf_service = pdf_service
        self.company_service = company_service
        self.product_rotation_service = product_rotation_service
        self.price_increase_service = price_increase_service
        self.max_workers = max_workers
        
        # Progress tracking
        self.progress_tracker: Dict[str, BatchPDFProgress] = {}
        
        # Output directory
        self.output_dir = Path("output/batch_pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_batch(
        self,
        request: BatchPDFRequest
    ) -> BatchPDFResult:
        """
        Generate PDFs for all selected companies in batch
        
        Args:
            request: Batch PDF generation request
            
        Returns:
            BatchPDFResult with all generation results
        """
        batch_id = self._generate_batch_id()
        start_time = datetime.now()
        
        logger.info(f"Starting batch PDF generation {batch_id} for {len(request.company_ids)} companies")
        
        # Initialize progress tracking
        self._init_progress(batch_id, len(request.company_ids))
        
        try:
            # Generate PDFs in parallel
            results = await self._generate_pdfs_parallel(
                batch_id,
                request
            )
            
            # Create ZIP file with all PDFs
            zip_path, zip_size = await self._create_zip_archive(
                batch_id,
                results
            )
            
            # Calculate statistics
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Update progress to completed
            self._update_progress(
                batch_id,
                len(results),
                len(results),
                None,
                "completed"
            )
            
            batch_result = BatchPDFResult(
                batch_id=batch_id,
                total_companies=len(request.company_ids),
                successful=successful,
                failed=failed,
                results=results,
                total_time=total_time,
                zip_path=str(zip_path) if zip_path else None,
                zip_size=zip_size
            )
            
            logger.info(
                f"Batch {batch_id} completed: {successful} successful, "
                f"{failed} failed in {total_time:.2f}s"
            )
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch {batch_id} failed: {str(e)}", exc_info=True)
            self._update_progress(batch_id, 0, 0, None, "failed")
            raise
    
    async def _generate_pdfs_parallel(
        self,
        batch_id: str,
        request: BatchPDFRequest
    ) -> List[CompanyPDFResult]:
        """Generate PDFs in parallel using thread pool"""
        results = []
        
        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_company = {}
            for idx, company_id in enumerate(request.company_ids):
                future = executor.submit(
                    self._generate_single_pdf,
                    batch_id,
                    company_id,
                    idx,
                    request.analysis_data,
                    request.template_type,
                    request.options
                )
                future_to_company[future] = company_id
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_company):
                company_id = future_to_company[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Update progress
                    self._update_progress(
                        batch_id,
                        len(request.company_ids),
                        completed,
                        result.company_name,
                        "processing"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Failed to generate PDF for company {company_id}: {str(e)}",
                        exc_info=True
                    )
                    # Add error result
                    results.append(CompanyPDFResult(
                        company_id=company_id,
                        company_name=f"Company {company_id}",
                        success=False,
                        error_message=str(e)
                    ))
                    completed += 1
        
        return results
    
    def _generate_single_pdf(
        self,
        batch_id: str,
        company_id: int,
        offer_index: int,
        analysis_data: Dict[str, Any],
        template_type: str,
        options: Dict[str, Any]
    ) -> CompanyPDFResult:
        """
        Generate PDF for a single company
        
        This method runs in a thread pool, so it's synchronous
        """
        start_time = datetime.now()
        
        try:
            # Get company data
            company = self.company_service.get_company(company_id)
            if not company:
                raise ValueError(f"Company {company_id} not found")
            
            logger.info(f"Generating PDF for company: {company.name}")
            
            # Apply product rotation (each offer gets different products)
            rotated_products = self.product_rotation_service.rotate_products(
                analysis_data.get("products", {}),
                offer_index
            )
            
            # Apply price increase (each offer is more expensive)
            increased_price = self.price_increase_service.apply_increase(
                analysis_data.get("base_price", 0),
                offer_index,
                options.get("price_increase_percentage", 7.0)
            )
            
            # Prepare PDF data with company-specific information
            pdf_data = {
                **analysis_data,
                "company": company.dict(),
                "products": rotated_products,
                "total_price": increased_price,
                "offer_number": offer_index + 1,
                "batch_id": batch_id
            }
            
            # Generate PDF
            pdf_bytes = self.pdf_service.generate_pdf(
                template_type=template_type,
                data=pdf_data,
                options={
                    **options,
                    "company_id": company_id,
                    "company_logo": company.logo_path,
                    "company_branding": company.branding
                }
            )
            
            # Save PDF to file
            pdf_filename = f"{batch_id}_{company.name.replace(' ', '_')}_offer_{offer_index + 1}.pdf"
            pdf_path = self.output_dir / batch_id / pdf_filename
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            file_size = len(pdf_bytes)
            
            logger.info(
                f"PDF generated for {company.name}: "
                f"{file_size} bytes in {generation_time:.2f}s"
            )
            
            return CompanyPDFResult(
                company_id=company_id,
                company_name=company.name,
                success=True,
                pdf_path=str(pdf_path),
                pdf_bytes=pdf_bytes,
                generation_time=generation_time,
                file_size=file_size
            )
            
        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Failed to generate PDF for company {company_id}: {str(e)}",
                exc_info=True
            )
            
            return CompanyPDFResult(
                company_id=company_id,
                company_name=f"Company {company_id}",
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
    
    async def _create_zip_archive(
        self,
        batch_id: str,
        results: List[CompanyPDFResult]
    ) -> tuple[Optional[Path], Optional[int]]:
        """Create ZIP archive with all generated PDFs"""
        try:
            # Filter successful results
            successful_results = [r for r in results if r.success and r.pdf_path]
            
            if not successful_results:
                logger.warning(f"No successful PDFs to archive for batch {batch_id}")
                return None, None
            
            # Create ZIP file
            zip_filename = f"{batch_id}_all_offers.zip"
            zip_path = self.output_dir / batch_id / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for result in successful_results:
                    pdf_path = Path(result.pdf_path)
                    if pdf_path.exists():
                        # Add to ZIP with just the filename (no path)
                        zipf.write(pdf_path, pdf_path.name)
            
            zip_size = zip_path.stat().st_size
            
            logger.info(
                f"Created ZIP archive: {zip_path} "
                f"({len(successful_results)} PDFs, {zip_size} bytes)"
            )
            
            return zip_path, zip_size
            
        except Exception as e:
            logger.error(f"Failed to create ZIP archive: {str(e)}", exc_info=True)
            return None, None
    
    def get_progress(self, batch_id: str) -> Optional[BatchPDFProgress]:
        """Get current progress for a batch"""
        return self.progress_tracker.get(batch_id)
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID"""
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _init_progress(self, batch_id: str, total: int):
        """Initialize progress tracking"""
        self.progress_tracker[batch_id] = BatchPDFProgress(
            batch_id=batch_id,
            total=total,
            completed=0,
            percentage=0.0,
            status="queued"
        )
    
    def _update_progress(
        self,
        batch_id: str,
        total: int,
        completed: int,
        current_company: Optional[str],
        status: str
    ):
        """Update progress tracking"""
        percentage = (completed / total * 100) if total > 0 else 0
        
        self.progress_tracker[batch_id] = BatchPDFProgress(
            batch_id=batch_id,
            total=total,
            completed=completed,
            current_company=current_company,
            percentage=percentage,
            status=status
        )
    
    async def download_single_pdf(
        self,
        batch_id: str,
        company_id: int
    ) -> Optional[bytes]:
        """Download a single PDF from a batch"""
        try:
            batch_dir = self.output_dir / batch_id
            if not batch_dir.exists():
                return None
            
            # Find PDF file for this company
            for pdf_file in batch_dir.glob(f"*_company_{company_id}_*.pdf"):
                with open(pdf_file, 'rb') as f:
                    return f.read()
            
            return None
            
        except Exception as e:
            logger.error(
                f"Failed to download PDF for company {company_id}: {str(e)}",
                exc_info=True
            )
            return None
    
    async def download_zip(self, batch_id: str) -> Optional[bytes]:
        """Download ZIP archive for a batch"""
        try:
            zip_path = self.output_dir / batch_id / f"{batch_id}_all_offers.zip"
            
            if not zip_path.exists():
                return None
            
            with open(zip_path, 'rb') as f:
                return f.read()
            
        except Exception as e:
            logger.error(f"Failed to download ZIP: {str(e)}", exc_info=True)
            return None
    
    def cleanup_batch(self, batch_id: str, keep_zip: bool = True):
        """Clean up batch files"""
        try:
            batch_dir = self.output_dir / batch_id
            if not batch_dir.exists():
                return
            
            # Delete individual PDFs
            for pdf_file in batch_dir.glob("*.pdf"):
                pdf_file.unlink()
            
            # Optionally delete ZIP
            if not keep_zip:
                zip_file = batch_dir / f"{batch_id}_all_offers.zip"
                if zip_file.exists():
                    zip_file.unlink()
            
            # Remove directory if empty
            if not any(batch_dir.iterdir()):
                batch_dir.rmdir()
            
            # Remove from progress tracker
            if batch_id in self.progress_tracker:
                del self.progress_tracker[batch_id]
            
            logger.info(f"Cleaned up batch {batch_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup batch {batch_id}: {str(e)}", exc_info=True)
