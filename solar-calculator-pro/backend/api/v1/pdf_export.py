"""
PDF Export API Endpoints
Handles PDF download, email, preview, and history operations
"""

from fastapi import APIRouter, HTTPException, Depends, Response, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import io

from backend.services.pdf_export_service import PDFExportService
from backend.services.pdf_history_service import PDFHistoryService
from backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/pdf-export", tags=["PDF Export"])

# Initialize services
pdf_export_service = PDFExportService()


# Request/Response Models
class PDFDownloadRequest(BaseModel):
    pdf_id: int
    filename: Optional[str] = None


class BatchPDFDownloadRequest(BaseModel):
    pdf_ids: List[int]
    zip_filename: Optional[str] = None


class PDFEmailRequest(BaseModel):
    pdf_id: int
    recipient_email: EmailStr
    subject: str
    body: str
    filename: Optional[str] = None


class BatchPDFEmailRequest(BaseModel):
    pdf_ids: List[int]
    recipient_email: EmailStr
    subject: str
    body: str
    as_zip: bool = True
    zip_filename: Optional[str] = None


class PDFPreviewRequest(BaseModel):
    pdf_id: int


class PDFHistoryQuery(BaseModel):
    limit: int = 50
    offset: int = 0
    pdf_type: Optional[str] = None
    search_term: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Endpoints
@router.post("/download/single")
async def download_single_pdf(
    request: PDFDownloadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Download a single PDF file
    
    Returns the PDF file as a downloadable attachment
    """
    try:
        # In a real implementation, fetch PDF from database
        # For now, return mock response
        
        # Get PDF bytes (mock)
        pdf_bytes = b"Mock PDF content"
        filename = request.filename or f"document_{request.pdf_id}.pdf"
        
        # Export PDF
        export_result = pdf_export_service.export_single_pdf(
            pdf_bytes,
            filename,
            metadata={'user_id': current_user['id'], 'pdf_id': request.pdf_id}
        )
        
        if not export_result['success']:
            raise HTTPException(status_code=500, detail=export_result.get('error'))
        
        # Return file for download
        pdf_file = pdf_export_service.get_pdf_for_download(export_result['file_path'])
        if not pdf_file:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return Response(
            content=pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_file))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download/batch")
async def download_batch_pdfs(
    request: BatchPDFDownloadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Download multiple PDFs as a ZIP file
    
    Returns a ZIP file containing all requested PDFs
    """
    try:
        # In a real implementation, fetch PDFs from database
        # For now, create mock PDFs
        pdfs = []
        for pdf_id in request.pdf_ids:
            pdfs.append({
                'bytes': b"Mock PDF content",
                'filename': f"document_{pdf_id}.pdf"
            })
        
        # Create ZIP
        zip_result = pdf_export_service.export_batch_pdfs(
            pdfs,
            request.zip_filename
        )
        
        if not zip_result['success']:
            raise HTTPException(status_code=500, detail=zip_result.get('error'))
        
        # Return ZIP for download
        zip_file = pdf_export_service.get_pdf_for_download(zip_result['zip_path'])
        if not zip_file:
            raise HTTPException(status_code=404, detail="ZIP file not found")
        
        return Response(
            content=zip_file,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{zip_result["zip_filename"]}"',
                "Content-Length": str(len(zip_file))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/single")
async def email_single_pdf(
    request: PDFEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a single PDF via email
    
    Sends the PDF as an email attachment to the specified recipient
    """
    try:
        # In a real implementation, fetch PDF from database
        pdf_bytes = b"Mock PDF content"
        filename = request.filename or f"document_{request.pdf_id}.pdf"
        
        # Get SMTP configuration (from settings or environment)
        smtp_config = {
            'host': 'smtp.example.com',
            'port': 587,
            'username': 'noreply@example.com',
            'password': 'password',
            'use_tls': True
        }
        
        # Send email in background
        def send_email():
            result = pdf_export_service.send_pdf_email(
                pdf_bytes,
                filename,
                request.recipient_email,
                request.subject,
                request.body,
                smtp_config
            )
            return result
        
        background_tasks.add_task(send_email)
        
        return {
            'message': 'Email is being sent',
            'recipient': request.recipient_email,
            'filename': filename,
            'queued_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/batch")
async def email_batch_pdfs(
    request: BatchPDFEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Send multiple PDFs via email
    
    Sends PDFs as a ZIP attachment or separate attachments
    """
    try:
        # In a real implementation, fetch PDFs from database
        pdfs = []
        for pdf_id in request.pdf_ids:
            pdfs.append({
                'bytes': b"Mock PDF content",
                'filename': f"document_{pdf_id}.pdf"
            })
        
        # Get SMTP configuration
        smtp_config = {
            'host': 'smtp.example.com',
            'port': 587,
            'username': 'noreply@example.com',
            'password': 'password',
            'use_tls': True
        }
        
        # Send email in background
        def send_email():
            result = pdf_export_service.send_batch_pdf_email(
                pdfs,
                request.recipient_email,
                request.subject,
                request.body,
                smtp_config,
                request.as_zip
            )
            return result
        
        background_tasks.add_task(send_email)
        
        return {
            'message': 'Email is being sent',
            'recipient': request.recipient_email,
            'pdf_count': len(request.pdf_ids),
            'as_zip': request.as_zip,
            'queued_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_pdf(
    request: PDFPreviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get PDF preview data
    
    Returns base64-encoded PDF for browser preview
    """
    try:
        # In a real implementation, fetch PDF from database
        pdf_bytes = b"Mock PDF content"
        
        # Convert to base64 for preview
        preview_data = pdf_export_service.get_pdf_for_preview(pdf_bytes)
        
        return {
            'pdf_id': request.pdf_id,
            'preview_data': preview_data,
            'content_type': 'application/pdf',
            'size': len(pdf_bytes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_pdf_history(
    limit: int = 50,
    offset: int = 0,
    pdf_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = None  # In real implementation, inject database session
):
    """
    Get PDF generation history for current user
    
    Returns list of previously generated PDFs
    """
    try:
        history_service = PDFHistoryService(db)
        
        history = history_service.get_user_history(
            user_id=current_user['id'],
            limit=limit,
            offset=offset,
            pdf_type=pdf_type
        )
        
        return {
            'history': history,
            'total': len(history),
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/recent")
async def get_recent_pdfs(
    count: int = 10,
    current_user: dict = Depends(get_current_user),
    db = None
):
    """
    Get most recent PDFs for current user
    
    Returns the most recently generated PDFs
    """
    try:
        history_service = PDFHistoryService(db)
        
        recent = history_service.get_recent_pdfs(
            user_id=current_user['id'],
            count=count
        )
        
        return {
            'recent_pdfs': recent,
            'count': len(recent)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/search")
async def search_pdf_history(
    query: PDFHistoryQuery,
    current_user: dict = Depends(get_current_user),
    db = None
):
    """
    Search PDF generation history
    
    Search by filename, type, date range, etc.
    """
    try:
        history_service = PDFHistoryService(db)
        
        results = history_service.search_history(
            user_id=current_user['id'],
            search_term=query.search_term or "",
            pdf_type=query.pdf_type,
            date_from=query.date_from,
            date_to=query.date_to
        )
        
        return {
            'results': results,
            'count': len(results),
            'query': query.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/statistics")
async def get_pdf_statistics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    db = None
):
    """
    Get PDF generation statistics
    
    Returns statistics about PDF generation for the user
    """
    try:
        history_service = PDFHistoryService(db)
        
        stats = history_service.get_statistics(
            user_id=current_user['id'],
            date_from=date_from,
            date_to=date_to
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{record_id}")
async def delete_history_record(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db = None
):
    """
    Delete a PDF history record
    
    Removes the history record and optionally the PDF file
    """
    try:
        history_service = PDFHistoryService(db)
        
        result = history_service.delete_history_record(
            user_id=current_user['id'],
            record_id=record_id
        )
        
        if not result.get('deleted'):
            raise HTTPException(status_code=404, detail="Record not found or already deleted")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_exports(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Clean up old exported PDF files
    
    Deletes PDF files older than specified days
    Requires admin privileges
    """
    try:
        # Check if user is admin (in real implementation)
        if not current_user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        result = pdf_export_service.cleanup_old_exports(days)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
