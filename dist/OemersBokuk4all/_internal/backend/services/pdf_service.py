"""
PDF Generation Service

This service wraps the legacy pdf_generator.py module and provides
a clean API interface for PDF generation with templates, preview, and async support.
"""

import sys
import os
import asyncio
import io
import base64
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime
from pathlib import Path
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import tempfile

# Add parent directory to path to import pdf_generator module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors, ErrorContext
from backend.core.logging_decorator import log_service_call


class PDFGenerationService(BaseService):
    """
    Service wrapper for PDF generation functionality.
    
    Wraps the legacy pdf_generator.py module and provides:
    - Template-based PDF generation
    - PDF preview functionality
    - Async PDF generation for large documents
    - PDF storage and retrieval
    - Caching for repeated generations
    """
    
    def __init__(self):
        super().__init__("pdf_generation")
        self._cache: Dict[str, tuple[bytes, float]] = {}
        self._cache_ttl_seconds = 600  # 10 minutes cache TTL
        self._pdf_generator_module = None
        self._storage_path = Path("backend/pdf_storage")
        self._executor = ThreadPoolExecutor(max_workers=4)
        
    def initialize(self) -> None:
        """Initialize the service and load legacy pdf_generator module"""
        try:
            # Import the legacy pdf_generator module
            import pdf_generator
            self._pdf_generator_module = pdf_generator
            self._set_legacy_module(pdf_generator)
            
            # Create storage directory if it doesn't exist
            self._storage_path.mkdir(parents=True, exist_ok=True)
            
            self._set_initialized(True)
            self.logger.info("PDF Generation Service initialized successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import pdf_generator module: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize PDF Generation Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check on the service"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        if self._pdf_generator_module is None:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="PDF generator module not loaded"
            )
        
        # Check if key functions are available
        required_functions = ['generate_offer_pdf', 'create_offer_pdf']
        missing_functions = []
        
        for func_name in required_functions:
            if not hasattr(self._pdf_generator_module, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message=f"Missing functions: {', '.join(missing_functions)}",
                details={"missing_functions": missing_functions}
            )
        
        # Check storage directory
        if not self._storage_path.exists():
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message="PDF storage directory not accessible",
                details={"storage_path": str(self._storage_path)}
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy",
            details={
                "cache_size": len(self._cache),
                "storage_path": str(self._storage_path),
                "executor_workers": self._executor._max_workers
            }
        )
    
    def _generate_cache_key(self, offer_data: Dict[str, Any], template: str) -> str:
        """Generate cache key from offer data and template"""
        # Create a deterministic hash from the data
        data_str = json.dumps(offer_data, sort_keys=True) + template
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached PDF is still valid"""
        if cache_key not in self._cache:
            return False
        
        _, timestamp = self._cache[cache_key]
        age = datetime.now().timestamp() - timestamp
        return age < self._cache_ttl_seconds
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="generate_pdf",
        error_message="Failed to generate PDF"
    ))
    def generate_pdf(
        self,
        offer_data: Dict[str, Any],
        template: str = "main",
        use_cache: bool = True
    ) -> bytes:
        """
        Generate PDF from offer data using specified template.
        
        Args:
            offer_data: Dictionary containing offer/project data
            template: Template name to use ('main', 'simple', 'extended')
            use_cache: Whether to use cached PDF if available
            
        Returns:
            PDF content as bytes
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Check cache
        cache_key = self._generate_cache_key(offer_data, template)
        if use_cache and self._is_cache_valid(cache_key):
            self.logger.info(f"Returning cached PDF for key: {cache_key}")
            pdf_bytes, _ = self._cache[cache_key]
            return pdf_bytes
        
        # Generate PDF using legacy module
        self.logger.info(f"Generating PDF with template: {template}")
        
        try:
            if template == "main":
                pdf_bytes = self._pdf_generator_module.generate_offer_pdf(
                    project_data=offer_data,
                    analysis_results=offer_data.get('analysis_results')
                )
            elif template == "simple":
                pdf_bytes = self._pdf_generator_module.generate_offer_pdf_simple(
                    project_data=offer_data,
                    analysis_results=offer_data.get('analysis_results')
                )
            else:
                # Default to main template
                pdf_bytes = self._pdf_generator_module.generate_offer_pdf(
                    project_data=offer_data,
                    analysis_results=offer_data.get('analysis_results')
                )
            
            # Cache the result
            self._cache[cache_key] = (pdf_bytes, datetime.now().timestamp())
            
            self.logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="generate_pdf_async",
        error_message="Failed to generate PDF asynchronously"
    ))
    async def generate_pdf_async(
        self,
        offer_data: Dict[str, Any],
        template: str = "main",
        use_cache: bool = True
    ) -> bytes:
        """
        Generate PDF asynchronously for large documents.
        
        Args:
            offer_data: Dictionary containing offer/project data
            template: Template name to use
            use_cache: Whether to use cached PDF if available
            
        Returns:
            PDF content as bytes
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Run PDF generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        pdf_bytes = await loop.run_in_executor(
            self._executor,
            self.generate_pdf,
            offer_data,
            template,
            use_cache
        )
        
        return pdf_bytes
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="generate_pdf_preview",
        error_message="Failed to generate PDF preview"
    ))
    def generate_pdf_preview(
        self,
        offer_data: Dict[str, Any],
        template: str = "main",
        page_limit: int = 3
    ) -> bytes:
        """
        Generate PDF preview (first few pages only).
        
        Args:
            offer_data: Dictionary containing offer/project data
            template: Template name to use
            page_limit: Maximum number of pages to include in preview
            
        Returns:
            PDF preview content as bytes
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Generate full PDF
        full_pdf = self.generate_pdf(offer_data, template, use_cache=True)
        
        # Extract first N pages for preview
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            from PyPDF2 import PdfReader, PdfWriter
        
        reader = PdfReader(io.BytesIO(full_pdf))
        writer = PdfWriter()
        
        # Add limited pages
        for i in range(min(page_limit, len(reader.pages))):
            writer.add_page(reader.pages[i])
        
        # Write to bytes
        preview_buffer = io.BytesIO()
        writer.write(preview_buffer)
        preview_buffer.seek(0)
        
        preview_bytes = preview_buffer.getvalue()
        self.logger.info(f"PDF preview generated: {len(reader.pages)} pages -> {page_limit} pages")
        
        return preview_bytes
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="store_pdf",
        error_message="Failed to store PDF"
    ))
    def store_pdf(
        self,
        pdf_bytes: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store PDF to disk with metadata.
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Filename for the PDF
            metadata: Optional metadata to store with PDF
            
        Returns:
            File path where PDF was stored
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        if not safe_filename.endswith('.pdf'):
            safe_filename += '.pdf'
        
        file_path = self._storage_path / safe_filename
        
        # Write PDF to disk
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Store metadata if provided
        if metadata:
            metadata_path = file_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump({
                    **metadata,
                    'filename': safe_filename,
                    'size_bytes': len(pdf_bytes),
                    'created_at': datetime.now().isoformat()
                }, f, indent=2)
        
        self.logger.info(f"PDF stored at: {file_path}")
        return str(file_path)
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="retrieve_pdf",
        error_message="Failed to retrieve PDF"
    ))
    def retrieve_pdf(self, filename: str) -> Optional[bytes]:
        """
        Retrieve stored PDF by filename.
        
        Args:
            filename: Name of the PDF file to retrieve
            
        Returns:
            PDF content as bytes, or None if not found
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        file_path = self._storage_path / filename
        
        if not file_path.exists():
            self.logger.warning(f"PDF not found: {filename}")
            return None
        
        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()
        
        self.logger.info(f"PDF retrieved: {filename}, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="list_stored_pdfs",
        error_message="Failed to list stored PDFs"
    ))
    def list_stored_pdfs(self) -> List[Dict[str, Any]]:
        """
        List all stored PDFs with metadata.
        
        Returns:
            List of PDF metadata dictionaries
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        pdfs = []
        
        for pdf_file in self._storage_path.glob("*.pdf"):
            metadata_file = pdf_file.with_suffix('.json')
            
            pdf_info = {
                'filename': pdf_file.name,
                'size_bytes': pdf_file.stat().st_size,
                'created_at': datetime.fromtimestamp(pdf_file.stat().st_ctime).isoformat()
            }
            
            # Load metadata if available
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    stored_metadata = json.load(f)
                    pdf_info.update(stored_metadata)
            
            pdfs.append(pdf_info)
        
        # Sort by creation time, newest first
        pdfs.sort(key=lambda x: x['created_at'], reverse=True)
        
        self.logger.info(f"Found {len(pdfs)} stored PDFs")
        return pdfs
    
    @log_service_call
    @handle_service_errors(ErrorContext(
        operation="delete_pdf",
        error_message="Failed to delete PDF"
    ))
    def delete_pdf(self, filename: str) -> bool:
        """
        Delete stored PDF and its metadata.
        
        Args:
            filename: Name of the PDF file to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        file_path = self._storage_path / filename
        metadata_path = file_path.with_suffix('.json')
        
        if not file_path.exists():
            self.logger.warning(f"PDF not found for deletion: {filename}")
            return False
        
        # Delete PDF file
        file_path.unlink()
        
        # Delete metadata if exists
        if metadata_path.exists():
            metadata_path.unlink()
        
        self.logger.info(f"PDF deleted: {filename}")
        return True
    
    @log_service_call
    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available PDF templates.
        
        Returns:
            List of template information dictionaries
        """
        templates = [
            {
                'name': 'main',
                'display_name': 'Main Template',
                'description': 'Full-featured PDF with all sections and visualizations'
            },
            {
                'name': 'simple',
                'display_name': 'Simple Template',
                'description': 'Simplified PDF with essential information only'
            },
            {
                'name': 'extended',
                'display_name': 'Extended Template',
                'description': 'Extended PDF with detailed analysis and charts'
            }
        ]
        
        return templates
    
    @log_service_call
    def clear_cache(self) -> int:
        """
        Clear the PDF generation cache.
        
        Returns:
            Number of cached items cleared
        """
        count = len(self._cache)
        self._cache.clear()
        self.logger.info(f"Cleared {count} cached PDFs")
        return count
    
    @log_service_call
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = sum(len(pdf_bytes) for pdf_bytes, _ in self._cache.values())
        
        return {
            'cached_items': len(self._cache),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_ttl_seconds': self._cache_ttl_seconds
        }
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.clear_cache()
        self._executor.shutdown(wait=True)
        self.logger.info("PDF Generation Service cleaned up")


# Singleton instance
_pdf_service_instance: Optional[PDFGenerationService] = None


def get_pdf_service() -> PDFGenerationService:
    """Get or create PDF service singleton instance"""
    global _pdf_service_instance
    
    if _pdf_service_instance is None:
        _pdf_service_instance = PDFGenerationService()
        _pdf_service_instance.initialize()
    
    return _pdf_service_instance
