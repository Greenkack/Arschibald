"""
Batch PDF Generation API Endpoints

Provides REST API endpoints for multi-PDF batch generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Optional
import logging

from ...services.batch_pdf_service import (
    BatchPDFService,
    BatchPDFRequest,
    BatchPDFResult,
    BatchPDFProgress
)
from ...core.dependencies import get_batch_pdf_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/batch-pdf", tags=["Batch PDF"])


@router.post("/generate", response_model=BatchPDFResult)
async def generate_batch_pdfs(
    request: BatchPDFRequest,
    background_tasks: BackgroundTasks,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Generate PDFs for multiple companies in batch
    
    **Concept**: One click → All selected company PDFs generated simultaneously
    
    **Example**: 8 companies selected → 8 PDFs with one click
    
    **Data**: Same analysis data for all offers
    
    **Differences**: Company-specific data, rotated products, increased prices
    
    **Output**: All PDFs with same analysis data but different companies, products, and prices
    
    Args:
        request: Batch PDF generation request with company IDs and analysis data
        background_tasks: FastAPI background tasks for cleanup
        service: Batch PDF service instance
        
    Returns:
        BatchPDFResult with generation results for all companies
        
    Raises:
        HTTPException: If batch generation fails
    """
    try:
        logger.info(f"Received batch PDF request for {len(request.company_ids)} companies")
        
        # Validate request
        if not request.company_ids:
            raise HTTPException(
                status_code=400,
                detail="No companies selected for batch generation"
            )
        
        if len(request.company_ids) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 companies allowed per batch"
            )
        
        # Generate batch
        result = await service.generate_batch(request)
        
        # Schedule cleanup after 24 hours
        background_tasks.add_task(
            service.cleanup_batch,
            result.batch_id,
            keep_zip=True
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch PDF generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch PDF generation failed: {str(e)}"
        )


@router.get("/progress/{batch_id}", response_model=BatchPDFProgress)
async def get_batch_progress(
    batch_id: str,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Get progress for a batch PDF generation
    
    Args:
        batch_id: Unique batch identifier
        service: Batch PDF service instance
        
    Returns:
        BatchPDFProgress with current progress information
        
    Raises:
        HTTPException: If batch not found
    """
    progress = service.get_progress(batch_id)
    
    if not progress:
        raise HTTPException(
            status_code=404,
            detail=f"Batch {batch_id} not found"
        )
    
    return progress


@router.get("/download/zip/{batch_id}")
async def download_batch_zip(
    batch_id: str,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Download ZIP archive with all generated PDFs
    
    Args:
        batch_id: Unique batch identifier
        service: Batch PDF service instance
        
    Returns:
        ZIP file with all PDFs
        
    Raises:
        HTTPException: If ZIP not found
    """
    try:
        zip_bytes = await service.download_zip(batch_id)
        
        if not zip_bytes:
            raise HTTPException(
                status_code=404,
                detail=f"ZIP archive for batch {batch_id} not found"
            )
        
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={batch_id}_all_offers.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download ZIP: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download ZIP: {str(e)}"
        )


@router.get("/download/single/{batch_id}/{company_id}")
async def download_single_pdf(
    batch_id: str,
    company_id: int,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Download a single PDF from a batch
    
    Args:
        batch_id: Unique batch identifier
        company_id: Company ID
        service: Batch PDF service instance
        
    Returns:
        PDF file for the specified company
        
    Raises:
        HTTPException: If PDF not found
    """
    try:
        pdf_bytes = await service.download_single_pdf(batch_id, company_id)
        
        if not pdf_bytes:
            raise HTTPException(
                status_code=404,
                detail=f"PDF for company {company_id} in batch {batch_id} not found"
            )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=offer_company_{company_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download PDF: {str(e)}"
        )


@router.delete("/cleanup/{batch_id}")
async def cleanup_batch(
    batch_id: str,
    keep_zip: bool = True,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Clean up batch files
    
    Args:
        batch_id: Unique batch identifier
        keep_zip: Whether to keep the ZIP archive
        service: Batch PDF service instance
        
    Returns:
        Success message
    """
    try:
        service.cleanup_batch(batch_id, keep_zip=keep_zip)
        
        return {
            "message": f"Batch {batch_id} cleaned up successfully",
            "batch_id": batch_id,
            "zip_kept": keep_zip
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup batch: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup batch: {str(e)}"
        )


@router.post("/generate-async", response_model=dict)
async def generate_batch_pdfs_async(
    request: BatchPDFRequest,
    background_tasks: BackgroundTasks,
    service: BatchPDFService = Depends(get_batch_pdf_service)
):
    """
    Start batch PDF generation asynchronously
    
    Returns immediately with batch_id for progress tracking
    
    Args:
        request: Batch PDF generation request
        background_tasks: FastAPI background tasks
        service: Batch PDF service instance
        
    Returns:
        Dict with batch_id for progress tracking
    """
    try:
        # Validate request
        if not request.company_ids:
            raise HTTPException(
                status_code=400,
                detail="No companies selected for batch generation"
            )
        
        # Generate batch ID
        batch_id = service._generate_batch_id()
        
        # Initialize progress
        service._init_progress(batch_id, len(request.company_ids))
        
        # Start generation in background
        background_tasks.add_task(
            service.generate_batch,
            request
        )
        
        return {
            "batch_id": batch_id,
            "status": "queued",
            "total_companies": len(request.company_ids),
            "message": "Batch PDF generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start batch generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start batch generation: {str(e)}"
        )
