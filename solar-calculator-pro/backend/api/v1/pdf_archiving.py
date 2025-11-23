"""
PDF Archiving API Endpoints

Provides REST API endpoints for PDF archiving and CRM integration.

Requirements: 1.3, 6.1
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from services.pdf_archiving_service import PDFArchivingService, PDFMetadata

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf-archiving", tags=["PDF Archiving"])


# ==================== Request/Response Models ====================

class PDFArchiveRequest(BaseModel):
    """Request model for archiving a PDF"""
    customer_id: int = Field(..., description="Customer ID")
    project_id: Optional[int] = Field(None, description="Project ID")
    company_name: Optional[str] = Field(None, description="Company name")
    products: Optional[List[Dict[str, Any]]] = Field(None, description="List of products")
    total_price: Optional[float] = Field(None, description="Total price")
    offer_data: Optional[Dict[str, Any]] = Field(None, description="Additional offer data")


class PDFMetadataResponse(BaseModel):
    """Response model for PDF metadata"""
    creation_date: str
    company_id: Optional[int]
    company_name: Optional[str]
    products: Optional[List[Dict[str, Any]]]
    total_price: Optional[float]
    pdf_type: str
    project_type: str
    version: int
    file_size: int
    checksum: Optional[str]


class PDFHistoryResponse(BaseModel):
    """Response model for PDF history"""
    documents: List[Dict[str, Any]]
    total_count: int


class PDFSearchRequest(BaseModel):
    """Request model for PDF search"""
    customer_id: Optional[int] = None
    search_term: Optional[str] = None
    pdf_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    company_name: Optional[str] = None


class PDFExportRequest(BaseModel):
    """Request model for PDF export"""
    document_ids: List[int] = Field(..., description="List of document IDs to export")
    output_dir: Optional[str] = Field(None, description="Output directory")


class PDFStatisticsResponse(BaseModel):
    """Response model for PDF statistics"""
    total_pdfs: int
    total_customers: int
    by_type: Dict[str, int]


# ==================== Dependency ====================

def get_pdf_archiving_service() -> PDFArchivingService:
    """Get PDF archiving service instance"""
    return PDFArchivingService()


# ==================== Endpoints ====================

@router.post("/archive", response_model=Dict[str, Any])
async def archive_pdf(
    file: UploadFile = File(...),
    request: PDFArchiveRequest = Depends(),
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Archive a PDF to customer documents.
    
    - **file**: PDF file to archive
    - **customer_id**: Customer ID
    - **project_id**: Optional project ID
    - **company_name**: Optional company name
    - **products**: Optional list of products
    - **total_price**: Optional total price
    - **offer_data**: Optional additional offer data
    
    Returns document ID and metadata.
    """
    try:
        # Read PDF file
        pdf_bytes = await file.read()
        
        # Archive PDF
        doc_id = service.auto_save_to_crm(
            pdf_bytes=pdf_bytes,
            filename=file.filename,
            customer_id=request.customer_id,
            project_id=request.project_id,
            company_name=request.company_name,
            products=request.products,
            total_price=request.total_price,
            offer_data=request.offer_data
        )
        
        if not doc_id:
            raise HTTPException(status_code=500, detail="Failed to archive PDF")
        
        # Create metadata
        metadata = service.create_metadata(
            pdf_bytes=pdf_bytes,
            filename=file.filename,
            company_id=request.customer_id,
            company_name=request.company_name,
            products=request.products,
            total_price=request.total_price,
            offer_data=request.offer_data
        )
        
        return {
            "document_id": doc_id,
            "metadata": metadata.to_dict(),
            "message": "PDF archived successfully"
        }
        
    except Exception as e:
        logger.error(f"Error archiving PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{customer_id}", response_model=PDFHistoryResponse)
async def get_pdf_history(
    customer_id: int,
    project_id: Optional[int] = Query(None),
    pdf_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Get PDF history for a customer.
    
    - **customer_id**: Customer ID
    - **project_id**: Optional project ID filter
    - **pdf_type**: Optional PDF type filter
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    
    Returns list of PDF documents with metadata.
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Get history
        documents = service.get_pdf_history(
            customer_id=customer_id,
            project_id=project_id,
            pdf_type=pdf_type,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "documents": documents,
            "total_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error getting PDF history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=PDFHistoryResponse)
async def search_pdfs(
    request: PDFSearchRequest,
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Search PDFs in archive with various filters.
    
    - **customer_id**: Optional customer ID filter
    - **search_term**: Optional search term
    - **pdf_type**: Optional PDF type filter
    - **min_price**: Optional minimum price filter
    - **max_price**: Optional maximum price filter
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    - **company_name**: Optional company name filter
    
    Returns list of matching PDF documents.
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(request.start_date) if request.start_date else None
        end_dt = datetime.fromisoformat(request.end_date) if request.end_date else None
        
        # Search PDFs
        documents = service.search_pdfs(
            customer_id=request.customer_id,
            search_term=request.search_term,
            pdf_type=request.pdf_type,
            min_price=request.min_price,
            max_price=request.max_price,
            start_date=start_dt,
            end_date=end_dt,
            company_name=request.company_name
        )
        
        return {
            "documents": documents,
            "total_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error searching PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{document_id}")
async def export_pdf(
    document_id: int,
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Export a PDF from archive.
    
    - **document_id**: Document ID
    
    Returns PDF file bytes.
    """
    try:
        pdf_bytes = service.export_pdf(document_id)
        
        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        from fastapi.responses import Response
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=document_{document_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-multiple")
async def export_multiple_pdfs(
    request: PDFExportRequest,
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Export multiple PDFs from archive.
    
    - **document_ids**: List of document IDs
    - **output_dir**: Optional output directory
    
    Returns dictionary mapping document ID to output path.
    """
    try:
        if not request.output_dir:
            raise HTTPException(status_code=400, detail="output_dir is required")
        
        results = service.export_multiple_pdfs(
            document_ids=request.document_ids,
            output_dir=request.output_dir
        )
        
        return {
            "exported_count": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting multiple PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=PDFStatisticsResponse)
async def get_pdf_statistics(
    customer_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Get PDF archive statistics.
    
    - **customer_id**: Optional customer ID filter
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    
    Returns statistics about PDFs in archive.
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Get statistics
        stats = service.get_pdf_statistics(
            customer_id=customer_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting PDF statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-version/{customer_id}")
async def get_next_version(
    customer_id: int,
    pdf_type: str = Query(...),
    project_id: Optional[int] = Query(None),
    service: PDFArchivingService = Depends(get_pdf_archiving_service)
):
    """
    Get the next version number for a PDF type.
    
    - **customer_id**: Customer ID
    - **pdf_type**: PDF type (e.g., 'offer_pdf')
    - **project_id**: Optional project ID
    
    Returns next version number.
    """
    try:
        version = service.get_next_version_number(
            customer_id=customer_id,
            pdf_type=pdf_type,
            project_id=project_id
        )
        
        return {
            "next_version": version
        }
        
    except Exception as e:
        logger.error(f"Error getting next version: {e}")
        raise HTTPException(status_code=500, detail=str(e))
