"""
PDF Advanced API Endpoints - Task 103

FastAPI endpoints for advanced PDF generation including:
- Template-based generation
- Multi-language support
- Custom branding
- Batch generation
- Multi-company offers
- Chart integration
- CRM archiving
- Preview and download

Requirements: 1.3, 6.1, 7.3
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Query
from fastapi.responses import Response, StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import io
import base64

from backend.services.pdf_advanced_service import (
    get_pdf_advanced_service,
    PDFGenerationOptions,
    PDFBrandingConfig,
    PDFTemplate,
    PDFLanguage,
    ChartType
)


router = APIRouter(prefix="/pdf-advanced", tags=["PDF Advanced"])


# Request/Response Models

class ChartTypeEnum(str, Enum):
    """Chart types"""
    CIRCLE = "circle"
    DONUT = "donut"
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    POLAR = "polar"
    RADAR = "radar"
    WATERFALL = "waterfall"


class LanguageEnum(str, Enum):
    """Supported languages"""
    GERMAN = "de"
    ENGLISH = "en"
    FRENCH = "fr"
    ITALIAN = "it"


class TemplateEnum(str, Enum):
    """PDF templates"""
    BASIS = "Basis_Angebot"
    STORAGE_5KWH = "Speicher_5kWh"
    STORAGE_10KWH = "Speicher_10kWh"
    STORAGE_15KWH = "Speicher_15kWh"
    STORAGE_20KWH = "Speicher_20kWh"
    STORAGE_25KWH = "Speicher_25kWh"
    STORAGE_30KWH = "Speicher_30kWh"
    HEATPUMP = "Waermepumpe"
    WALLBOX = "Wallbox"
    FINANCING = "Finanzierung"


class BrandingConfigRequest(BaseModel):
    """Branding configuration"""
    company_name: str
    logo_path: str
    logo_position: tuple[float, float] = (50, 50)
    logo_size: tuple[float, float] = (100, 50)
    primary_color: str = "#0066CC"
    secondary_color: str = "#FF6600"
    font_family: str = "Helvetica"
    watermark_text: Optional[str] = None
    watermark_opacity: float = 0.1


class PDFGenerationRequest(BaseModel):
    """PDF generation request"""
    offer_data: Dict[str, Any]
    template: TemplateEnum = TemplateEnum.BASIS
    language: LanguageEnum = LanguageEnum.GERMAN
    branding: Optional[BrandingConfigRequest] = None
    include_3d_visualization: bool = True
    include_charts: bool = True
    include_financing: bool = False
    include_heatpump: bool = False
    include_wallbox: bool = False
    compress: bool = True
    archive_to_crm: bool = True
    chart_types: Optional[List[ChartTypeEnum]] = None
    custom_sections: Optional[List[str]] = None


class BatchPDFGenerationRequest(BaseModel):
    """Batch PDF generation request"""
    offers: List[Dict[str, Any]]
    template: TemplateEnum = TemplateEnum.BASIS
    language: LanguageEnum = LanguageEnum.GERMAN
    branding: Optional[BrandingConfigRequest] = None
    include_3d_visualization: bool = True
    include_charts: bool = True
    compress: bool = True
    archive_to_crm: bool = True


class MultiCompanyOfferRequest(BaseModel):
    """Multi-company offer request"""
    offer_data: Dict[str, Any]
    companies: List[BrandingConfigRequest]


class PDFGenerationResponse(BaseModel):
    """PDF generation response"""
    pdf_id: str
    filename: str
    size_bytes: int
    created_at: datetime
    download_url: str
    preview_url: Optional[str] = None


class BatchPDFGenerationResponse(BaseModel):
    """Batch PDF generation response"""
    batch_id: str
    pdf_count: int
    total_size_bytes: int
    created_at: datetime
    download_url: str


class TemplateInfo(BaseModel):
    """Template information"""
    name: str
    display_name: str
    available: bool


class LanguageInfo(BaseModel):
    """Language information"""
    code: str
    name: str


class ChartTypeInfo(BaseModel):
    """Chart type information"""
    type: str
    name: str


class ServiceStatistics(BaseModel):
    """Service statistics"""
    total_generations: int
    batch_generations: int
    archived_pdfs: int
    yml_files_loaded: int
    templates_loaded: int
    branding_configs: int


# Helper functions

def _convert_branding_config(branding: Optional[BrandingConfigRequest]) -> Optional[PDFBrandingConfig]:
    """Convert request branding to service branding"""
    if not branding:
        return None
    
    return PDFBrandingConfig(
        company_name=branding.company_name,
        logo_path=branding.logo_path,
        logo_position=branding.logo_position,
        logo_size=branding.logo_size,
        primary_color=branding.primary_color,
        secondary_color=branding.secondary_color,
        font_family=branding.font_family,
        watermark_text=branding.watermark_text,
        watermark_opacity=branding.watermark_opacity
    )


def _convert_chart_types(chart_types: Optional[List[ChartTypeEnum]]) -> Optional[List[ChartType]]:
    """Convert request chart types to service chart types"""
    if not chart_types:
        return None
    
    return [ChartType(ct.value) for ct in chart_types]


def _create_pdf_options(request: PDFGenerationRequest) -> PDFGenerationOptions:
    """Create PDF generation options from request"""
    return PDFGenerationOptions(
        template=PDFTemplate(request.template.value),
        language=PDFLanguage(request.language.value),
        branding=_convert_branding_config(request.branding),
        include_3d_visualization=request.include_3d_visualization,
        include_charts=request.include_charts,
        include_financing=request.include_financing,
        include_heatpump=request.include_heatpump,
        include_wallbox=request.include_wallbox,
        compress=request.compress,
        archive_to_crm=request.archive_to_crm,
        chart_types=_convert_chart_types(request.chart_types),
        custom_sections=request.custom_sections
    )


# API Endpoints

@router.post("/generate", response_model=PDFGenerationResponse)
async def generate_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate advanced PDF with all features.
    
    - **offer_data**: Complete offer/project data
    - **template**: PDF template to use
    - **language**: PDF language (German primary)
    - **branding**: Custom branding configuration
    - **include_3d_visualization**: Include 3D visualization
    - **include_charts**: Include charts
    - **compress**: Compress PDF
    - **archive_to_crm**: Archive to CRM
    """
    try:
        service = get_pdf_advanced_service()
        options = _create_pdf_options(request)
        
        # Generate PDF
        pdf_bytes = service.generate_advanced_pdf(request.offer_data, options)
        
        # Generate PDF ID
        pdf_id = f"pdf_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = f"{pdf_id}_{request.template.value}.pdf"
        
        # Store PDF (in background)
        background_tasks.add_task(
            service.store_pdf,
            pdf_bytes,
            filename,
            {
                'template': request.template.value,
                'language': request.language.value,
                'size_bytes': len(pdf_bytes)
            }
        )
        
        return PDFGenerationResponse(
            pdf_id=pdf_id,
            filename=filename,
            size_bytes=len(pdf_bytes),
            created_at=datetime.now(),
            download_url=f"/api/v1/pdf-advanced/download/{pdf_id}",
            preview_url=f"/api/v1/pdf-advanced/preview/{pdf_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/generate-batch", response_model=BatchPDFGenerationResponse)
async def generate_batch_pdfs(
    request: BatchPDFGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate multiple PDFs in batch.
    
    - **offers**: List of offer data
    - **template**: PDF template to use for all
    - **language**: PDF language
    - **compress**: Compress PDFs
    - **archive_to_crm**: Archive all to CRM
    """
    try:
        service = get_pdf_advanced_service()
        
        options = PDFGenerationOptions(
            template=PDFTemplate(request.template.value),
            language=PDFLanguage(request.language.value),
            branding=_convert_branding_config(request.branding),
            include_3d_visualization=request.include_3d_visualization,
            include_charts=request.include_charts,
            compress=request.compress,
            archive_to_crm=request.archive_to_crm
        )
        
        # Generate batch
        pdf_list = await service.generate_batch_pdfs(request.offers, options)
        
        # Calculate total size
        total_size = sum(len(pdf) for pdf in pdf_list)
        
        # Generate batch ID
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return BatchPDFGenerationResponse(
            batch_id=batch_id,
            pdf_count=len(pdf_list),
            total_size_bytes=total_size,
            created_at=datetime.now(),
            download_url=f"/api/v1/pdf-advanced/download-batch/{batch_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch PDF generation failed: {str(e)}")


@router.post("/generate-multi-company")
async def generate_multi_company_offer(
    request: MultiCompanyOfferRequest
):
    """
    Generate multi-company offer PDF (ZIP file).
    
    - **offer_data**: Offer data
    - **companies**: List of company branding configurations
    
    Returns ZIP file containing PDFs for all companies.
    """
    try:
        service = get_pdf_advanced_service()
        
        # Convert branding configs
        companies = [
            _convert_branding_config(company)
            for company in request.companies
        ]
        
        # Generate multi-company offer
        zip_bytes = service.generate_multi_company_offer(request.offer_data, companies)
        
        # Return ZIP file
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=multi_company_offer_{datetime.now().strftime('%Y%m%d')}.zip"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-company offer generation failed: {str(e)}")


@router.get("/download/{pdf_id}")
async def download_pdf(pdf_id: str):
    """
    Download generated PDF.
    
    - **pdf_id**: PDF identifier
    """
    try:
        service = get_pdf_advanced_service()
        
        # Retrieve PDF
        pdf_bytes = service.retrieve_pdf(f"{pdf_id}.pdf")
        
        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={pdf_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@router.get("/preview/{pdf_id}")
async def preview_pdf(
    pdf_id: str,
    page_limit: int = Query(default=3, ge=1, le=10)
):
    """
    Preview PDF (first few pages).
    
    - **pdf_id**: PDF identifier
    - **page_limit**: Number of pages to include in preview
    """
    try:
        service = get_pdf_advanced_service()
        
        # Retrieve full PDF
        pdf_bytes = service.retrieve_pdf(f"{pdf_id}.pdf")
        
        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Generate preview
        preview_bytes = service.generate_pdf_preview(
            {},  # Empty offer data since we're using stored PDF
            PDFTemplate.BASIS,
            page_limit
        )
        
        return Response(
            content=preview_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={pdf_id}_preview.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF preview failed: {str(e)}")


@router.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """
    Get list of available PDF templates.
    """
    try:
        service = get_pdf_advanced_service()
        templates = service.get_available_templates()
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/languages", response_model=List[LanguageInfo])
async def get_languages():
    """
    Get list of supported languages.
    """
    try:
        service = get_pdf_advanced_service()
        languages = service.get_available_languages()
        return languages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")


@router.get("/chart-types", response_model=List[ChartTypeInfo])
async def get_chart_types():
    """
    Get list of available chart types.
    """
    try:
        service = get_pdf_advanced_service()
        chart_types = service.get_available_chart_types()
        return chart_types
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chart types: {str(e)}")


@router.get("/statistics", response_model=ServiceStatistics)
async def get_statistics():
    """
    Get PDF service statistics.
    """
    try:
        service = get_pdf_advanced_service()
        stats = service.get_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/archive")
async def list_archived_pdfs(
    customer_id: Optional[int] = Query(default=None)
):
    """
    List archived PDFs.
    
    - **customer_id**: Optional customer ID filter
    """
    try:
        service = get_pdf_advanced_service()
        pdfs = service.list_stored_pdfs()
        
        # Filter by customer if provided
        if customer_id:
            pdfs = [pdf for pdf in pdfs if pdf.get('customer_id') == customer_id]
        
        return {"pdfs": pdfs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list archived PDFs: {str(e)}")


@router.delete("/archive/{filename}")
async def delete_archived_pdf(filename: str):
    """
    Delete archived PDF.
    
    - **filename**: PDF filename
    """
    try:
        service = get_pdf_advanced_service()
        success = service.delete_pdf(filename)
        
        if not success:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        return {"message": "PDF deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check PDF service health.
    """
    try:
        service = get_pdf_advanced_service()
        health = service.health_check()
        
        return {
            "status": health.status.value,
            "message": health.message,
            "details": health.details
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "details": {}
        }
