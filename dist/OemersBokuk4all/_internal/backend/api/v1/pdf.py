"""
PDF Generation API Endpoints

FastAPI routes for PDF generation, preview, storage, and retrieval.
"""

from fastapi import APIRouter, HTTPException, status, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List
import base64
import io

from backend.services.pdf_service import get_pdf_service
from backend.models.pdf_schemas import (
    PDFGenerationRequest,
    PDFGenerationResponse,
    PDFPreviewRequest,
    PDFListResponse,
    PDFStorageInfo,
    PDFTemplatesResponse,
    PDFTemplateInfo,
    PDFCacheStats,
    PDFDeleteResponse
)

router = APIRouter(prefix="/pdf", tags=["PDF Generation"])


@router.post("/generate", response_model=PDFGenerationResponse)
async def generate_pdf(request: PDFGenerationRequest):
    """
    Generate PDF from offer data using specified template.
    
    - **offer_data**: Dictionary containing offer/project data
    - **template**: Template to use (main, simple, extended)
    - **use_cache**: Whether to use cached PDF if available
    - **store_pdf**: Whether to store the generated PDF
    - **filename**: Filename for stored PDF (optional)
    - **metadata**: Additional metadata to store (optional)
    
    Returns base64-encoded PDF content.
    """
    try:
        pdf_service = get_pdf_service()
        
        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf(
            offer_data=request.offer_data,
            template=request.template.value,
            use_cache=request.use_cache
        )
        
        # Store PDF if requested
        stored_path = None
        if request.store_pdf:
            # Generate filename in new format: anrede_nachname_angebot_anlagengröße.pdf
            if not request.filename:
                customer_data = request.offer_data.get('customer_data', {}) or request.offer_data.get('customer_details', {})
                anrede = customer_data.get('salutation') or customer_data.get('anrede', 'Kunde')
                nachname = customer_data.get('last_name') or customer_data.get('nachname', 'Unbekannt')
                
                analysis = request.offer_data.get('analysis_results', {})
                system_size = analysis.get('system_size_kwp', 0)
                anlagengroesse = f"{system_size:.1f}kWp".replace('.', ',') if system_size > 0 else 'PV'
                
                # Sanitize filename
                safe_anrede = str(anrede).replace(' ', '_').replace('/', '_')
                safe_nachname = str(nachname).replace(' ', '_').replace('/', '_')
                
                filename = f"{safe_anrede}_{safe_nachname}_Angebot_{anlagengroesse}.pdf"
            else:
                filename = request.filename
                
            stored_path = pdf_service.store_pdf(
                pdf_bytes=pdf_bytes,
                filename=filename,
                metadata=request.metadata
            )
        
        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Check if it was cached
        cache_key = pdf_service._generate_cache_key(request.offer_data, request.template.value)
        cached = pdf_service._is_cache_valid(cache_key)
        
        return PDFGenerationResponse(
            pdf_base64=pdf_base64,
            size_bytes=len(pdf_bytes),
            template=request.template.value,
            cached=cached,
            stored_path=stored_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )


@router.post("/generate-async", response_model=PDFGenerationResponse)
async def generate_pdf_async(request: PDFGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate PDF asynchronously for large documents.
    
    Same parameters as /generate but runs in background for better performance.
    """
    try:
        pdf_service = get_pdf_service()
        
        # Generate PDF asynchronously
        pdf_bytes = await pdf_service.generate_pdf_async(
            offer_data=request.offer_data,
            template=request.template.value,
            use_cache=request.use_cache
        )
        
        # Store PDF if requested (in background)
        stored_path = None
        if request.store_pdf:
            # Generate filename in new format: anrede_nachname_angebot_anlagengröße.pdf
            if not request.filename:
                customer_data = request.offer_data.get('customer_data', {}) or request.offer_data.get('customer_details', {})
                anrede = customer_data.get('salutation') or customer_data.get('anrede', 'Kunde')
                nachname = customer_data.get('last_name') or customer_data.get('nachname', 'Unbekannt')
                
                analysis = request.offer_data.get('analysis_results', {})
                system_size = analysis.get('anlage_kwp', 0)
                anlagengroesse = f"{system_size:.2f}kWp".replace('.', ',') if system_size > 0 else 'PV'
                
                # Sanitize filename
                safe_anrede = str(anrede).replace(' ', '_').replace('/', '_')
                safe_nachname = str(nachname).replace(' ', '_').replace('/', '_')
                
                filename = f"{safe_anrede}_{safe_nachname}_Angebot_{anlagengroesse}.pdf"
            else:
                filename = request.filename
            
            def store_in_background():
                pdf_service.store_pdf(
                    pdf_bytes=pdf_bytes,
                    filename=filename,
                    metadata=request.metadata
                )
            
            background_tasks.add_task(store_in_background)
            stored_path = f"(storing in background: {filename})"
        
        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Check if it was cached
        cache_key = pdf_service._generate_cache_key(request.offer_data, request.template.value)
        cached = pdf_service._is_cache_valid(cache_key)
        
        return PDFGenerationResponse(
            pdf_base64=pdf_base64,
            size_bytes=len(pdf_bytes),
            template=request.template.value,
            cached=cached,
            stored_path=stored_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Async PDF generation failed: {str(e)}"
        )


@router.post("/preview", response_model=PDFGenerationResponse)
async def generate_pdf_preview(request: PDFPreviewRequest):
    """
    Generate PDF preview (first few pages only).
    
    - **offer_data**: Dictionary containing offer/project data
    - **template**: Template to use
    - **page_limit**: Maximum number of pages (1-10)
    
    Returns base64-encoded PDF preview.
    """
    try:
        pdf_service = get_pdf_service()
        
        # Generate preview
        preview_bytes = pdf_service.generate_pdf_preview(
            offer_data=request.offer_data,
            template=request.template.value,
            page_limit=request.page_limit
        )
        
        # Encode to base64
        preview_base64 = base64.b64encode(preview_bytes).decode('utf-8')
        
        return PDFGenerationResponse(
            pdf_base64=preview_base64,
            size_bytes=len(preview_bytes),
            template=request.template.value,
            cached=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF preview generation failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download a stored PDF file.
    
    - **filename**: Name of the PDF file to download
    
    Returns PDF file as binary stream.
    """
    try:
        pdf_service = get_pdf_service()
        
        # Retrieve PDF
        pdf_bytes = pdf_service.retrieve_pdf(filename)
        
        if pdf_bytes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF not found: {filename}"
            )
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF download failed: {str(e)}"
        )


@router.get("/list", response_model=PDFListResponse)
async def list_stored_pdfs():
    """
    List all stored PDFs with metadata.
    
    Returns list of stored PDFs sorted by creation time (newest first).
    """
    try:
        pdf_service = get_pdf_service()
        
        # Get list of PDFs
        pdfs = pdf_service.list_stored_pdfs()
        
        # Calculate totals
        total_count = len(pdfs)
        total_size = sum(pdf['size_bytes'] for pdf in pdfs)
        
        return PDFListResponse(
            pdfs=[PDFStorageInfo(**pdf) for pdf in pdfs],
            total_count=total_count,
            total_size_bytes=total_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PDFs: {str(e)}"
        )


@router.delete("/{filename}", response_model=PDFDeleteResponse)
async def delete_pdf(filename: str):
    """
    Delete a stored PDF file.
    
    - **filename**: Name of the PDF file to delete
    
    Returns success status.
    """
    try:
        pdf_service = get_pdf_service()
        
        # Delete PDF
        success = pdf_service.delete_pdf(filename)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF not found: {filename}"
            )
        
        return PDFDeleteResponse(
            success=True,
            filename=filename,
            message="PDF deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF deletion failed: {str(e)}"
        )


@router.get("/templates", response_model=PDFTemplatesResponse)
async def get_templates():
    """
    Get list of available PDF templates.
    
    Returns list of template information.
    """
    try:
        pdf_service = get_pdf_service()
        
        templates = pdf_service.get_available_templates()
        
        return PDFTemplatesResponse(
            templates=[PDFTemplateInfo(**template) for template in templates]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.get("/cache/stats", response_model=PDFCacheStats)
async def get_cache_stats():
    """
    Get PDF generation cache statistics.
    
    Returns cache size, item count, and TTL information.
    """
    try:
        pdf_service = get_pdf_service()
        
        stats = pdf_service.get_cache_stats()
        
        return PDFCacheStats(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear the PDF generation cache.
    
    Returns number of items cleared.
    """
    try:
        pdf_service = get_pdf_service()
        
        count = pdf_service.clear_cache()
        
        return {
            "success": True,
            "items_cleared": count,
            "message": f"Cleared {count} cached PDFs"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Check PDF service health.
    
    Returns service status and details.
    """
    try:
        pdf_service = get_pdf_service()
        
        health = pdf_service.health_check()
        
        return {
            "status": health.status.value,
            "message": health.message,
            "details": health.details
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
