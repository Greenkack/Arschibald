# backend/api/v1/branding.py

"""
API endpoints for PDF Branding & Multi-Logo System
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db
from backend.core.auth_dependencies import get_current_user
from backend.services.branding_service import BrandingService
from backend.models.branding_schemas import (
    CompanyBrandingCreate,
    CompanyBrandingUpdate,
    CompanyBrandingResponse,
    LogoPositionCreate,
    LogoPositionResponse,
    BrandingTemplateCreate,
    BrandingTemplateResponse,
    BrandingAssetCreate,
    BrandingAssetResponse,
    BrandingPreviewRequest,
    BrandingPreviewResponse
)
from backend.core.errors import NotFoundError, ValidationError


router = APIRouter(prefix="/branding", tags=["branding"])


# ==================== Company Branding Endpoints ====================

@router.post("/", response_model=CompanyBrandingResponse, status_code=status.HTTP_201_CREATED)
async def create_branding(
    branding_data: CompanyBrandingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new company branding configuration
    
    - **company_id**: ID of the company
    - **logo_***: Logo configuration (path, base64, dimensions, position)
    - **color_***: Color scheme (primary, secondary, accent, text, background, header, footer)
    - **font_***: Typography settings (family, sizes, weight)
    - **header_***: Header configuration
    - **footer_***: Footer configuration
    - **watermark_***: Watermark configuration
    - **template_***: Template configuration
    """
    service = BrandingService(db)
    try:
        branding = service.create_branding(branding_data)
        return branding
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{branding_id}", response_model=CompanyBrandingResponse)
async def get_branding(
    branding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get company branding by ID"""
    service = BrandingService(db)
    branding = service.get_branding(branding_id)
    
    if not branding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding not found")
    
    return branding


@router.get("/company/{company_id}", response_model=CompanyBrandingResponse)
async def get_branding_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get company branding by company ID"""
    service = BrandingService(db)
    branding = service.get_branding_by_company(company_id)
    
    if not branding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding not found for this company")
    
    return branding


@router.put("/{branding_id}", response_model=CompanyBrandingResponse)
async def update_branding(
    branding_id: int,
    branding_data: CompanyBrandingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update company branding (partial update supported)"""
    service = BrandingService(db)
    try:
        branding = service.update_branding(branding_id, branding_data)
        return branding
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{branding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branding(
    branding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete company branding"""
    service = BrandingService(db)
    try:
        service.delete_branding(branding_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=List[CompanyBrandingResponse])
async def list_brandings(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all company brandings"""
    service = BrandingService(db)
    brandings = service.list_brandings(skip=skip, limit=limit, active_only=active_only)
    return brandings


# ==================== Logo Position Endpoints ====================

@router.post("/{branding_id}/logo-positions", response_model=LogoPositionResponse, status_code=status.HTTP_201_CREATED)
async def add_logo_position(
    branding_id: int,
    position_data: LogoPositionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add logo position for branding
    
    - **page_number**: Specific page number (null for all pages)
    - **context**: Position context (header, footer, body, watermark)
    - **x, y**: Position coordinates from YML
    - **width, height**: Logo dimensions
    - **opacity**: Logo opacity (0.0 to 1.0)
    - **rotation**: Logo rotation in degrees
    - **scale**: Logo scale factor
    """
    service = BrandingService(db)
    try:
        position = service.add_logo_position(branding_id, position_data)
        return position
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{branding_id}/logo-positions", response_model=List[LogoPositionResponse])
async def get_logo_positions(
    branding_id: int,
    page_number: Optional[int] = None,
    context: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get logo positions for branding (optionally filtered by page and context)"""
    service = BrandingService(db)
    positions = service.get_logo_positions(branding_id, page_number, context)
    return positions


@router.delete("/logo-positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logo_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete logo position"""
    service = BrandingService(db)
    try:
        service.delete_logo_position(position_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== Logo Upload Endpoint ====================

@router.post("/{company_id}/upload-logo", response_model=BrandingAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_logo(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload company logo
    
    - Accepts image files (PNG, JPG, SVG)
    - Automatically processes and stores as base64
    - Updates company branding with logo
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Read file
    logo_bytes = await file.read()
    
    # Upload logo
    service = BrandingService(db)
    try:
        asset = service.upload_logo(company_id, logo_bytes, file.filename)
        return asset
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== YML Coordinates Endpoint ====================

@router.get("/{branding_id}/yml-coordinates/{page_number}")
async def get_yml_coordinates(
    branding_id: int,
    page_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get YML coordinates for specific page
    
    - Returns custom coordinates if defined in branding
    - Falls back to default YML file coordinates
    """
    service = BrandingService(db)
    try:
        coordinates = service.load_yml_coordinates(branding_id, page_number)
        return coordinates
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== Color Scheme Endpoint ====================

@router.get("/{branding_id}/colors")
async def get_color_scheme(
    branding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get complete color scheme for branding"""
    service = BrandingService(db)
    branding = service.get_branding(branding_id)
    
    if not branding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding not found")
    
    return {
        "primary": branding.primary_color,
        "secondary": branding.secondary_color,
        "accent": branding.accent_color,
        "text": branding.text_color,
        "background": branding.background_color,
        "header": branding.header_color,
        "footer": branding.footer_color
    }


# ==================== Branding Template Endpoints ====================

@router.post("/templates", response_model=BrandingTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: BrandingTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create branding template"""
    service = BrandingService(db)
    template = service.create_template(template_data, current_user.get("id"))
    return template


@router.get("/templates/{template_id}", response_model=BrandingTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get branding template"""
    service = BrandingService(db)
    template = service.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    return template


@router.get("/templates", response_model=List[BrandingTemplateResponse])
async def list_templates(
    public_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List branding templates"""
    service = BrandingService(db)
    templates = service.list_templates(public_only=public_only)
    return templates


@router.post("/{branding_id}/apply-template/{template_id}", response_model=CompanyBrandingResponse)
async def apply_template(
    branding_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply template to company branding"""
    service = BrandingService(db)
    try:
        branding = service.apply_template(branding_id, template_id)
        return branding
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== Preview Endpoint ====================

@router.post("/preview", response_model=BrandingPreviewResponse)
async def preview_branding(
    preview_request: BrandingPreviewRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate preview of branding applied to PDF
    
    - Returns base64 encoded PDF and preview image
    - Shows how branding will look on actual PDF
    """
    # This would integrate with the PDF generation service
    # For now, return a placeholder response
    return BrandingPreviewResponse(
        pdf_base64="",
        preview_image="",
        branding_applied={
            "branding_id": preview_request.branding_id,
            "page_type": preview_request.page_type,
            "watermark": preview_request.include_watermark,
            "header": preview_request.include_header,
            "footer": preview_request.include_footer
        }
    )
