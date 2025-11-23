"""
PDF Configuration API Endpoints
RESTful API for PDF configuration management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ...models.pdf_config_schemas import (
    PDFConfigurationRequest,
    PDFConfigurationResponse,
    PDFPreviewRequest,
    PDFPreviewResponse,
    PDFGenerationRequest,
    PDFGenerationResponse,
    PDFConfigurationListResponse,
    PDFType
)
from ...services.pdf_configuration_service import PDFConfigurationService

router = APIRouter(prefix="/pdf-configuration", tags=["PDF Configuration"])

# Service instance
pdf_config_service = PDFConfigurationService()


@router.post("/", response_model=PDFConfigurationResponse)
async def create_pdf_configuration(
    config_request: PDFConfigurationRequest
):
    """
    Create a new PDF configuration
    
    - **pdf_type**: Type of PDF to generate
    - **pages**: Page configurations
    - **components**: Component configurations
    - **companies**: Companies for multi-PDF (if applicable)
    - **product_rotation**: Product rotation settings
    - **price_increase**: Price increase settings
    
    Returns configuration ID and validation results
    """
    try:
        response = pdf_config_service.create_configuration(config_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{config_id}", response_model=PDFConfigurationRequest)
async def get_pdf_configuration(config_id: str):
    """
    Get PDF configuration by ID
    
    - **config_id**: Configuration ID
    
    Returns complete configuration
    """
    config = pdf_config_service.get_configuration(config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration {config_id} not found")
    return config


@router.put("/{config_id}", response_model=PDFConfigurationResponse)
async def update_pdf_configuration(
    config_id: str,
    config_request: PDFConfigurationRequest
):
    """
    Update existing PDF configuration
    
    - **config_id**: Configuration ID
    - **config_request**: Updated configuration
    
    Returns updated configuration with validation results
    """
    try:
        response = pdf_config_service.update_configuration(config_id, config_request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}")
async def delete_pdf_configuration(config_id: str):
    """
    Delete PDF configuration
    
    - **config_id**: Configuration ID
    
    Returns success status
    """
    success = pdf_config_service.delete_configuration(config_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Configuration {config_id} not found")
    return {"message": "Configuration deleted successfully", "config_id": config_id}


@router.get("/", response_model=PDFConfigurationListResponse)
async def list_pdf_configurations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    List all PDF configurations with pagination
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    
    Returns list of configurations
    """
    result = pdf_config_service.list_configurations(page, page_size)
    return PDFConfigurationListResponse(**result)


@router.post("/preview", response_model=PDFPreviewResponse)
async def generate_pdf_preview(preview_request: PDFPreviewRequest):
    """
    Generate preview image for a specific page
    
    - **config_id**: Configuration ID
    - **page_number**: Page number to preview
    - **resolution**: Preview resolution in DPI (default: 150)
    
    Returns preview image as base64
    """
    try:
        response = pdf_config_service.generate_preview(preview_request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=PDFGenerationResponse)
async def generate_pdf(generation_request: PDFGenerationRequest):
    """
    Generate PDF from configuration
    
    - **config_id**: Configuration ID
    - **output_format**: Output format (pdf or base64)
    - **filename**: Custom filename (optional)
    
    Returns PDF URL or base64 data
    """
    try:
        response = pdf_config_service.generate_pdf(generation_request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defaults/{pdf_type}", response_model=PDFConfigurationRequest)
async def get_default_configuration(pdf_type: PDFType):
    """
    Get default configuration for a PDF type
    
    - **pdf_type**: PDF type (standard_pv, extended_pv, standard_wp, extended_wp, multi_pdf)
    
    Returns default configuration
    """
    try:
        config = pdf_config_service.get_default_configuration(pdf_type)
        return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{config_id}/validate", response_model=PDFConfigurationResponse)
async def validate_pdf_configuration(config_id: str):
    """
    Validate PDF configuration without saving
    
    - **config_id**: Configuration ID
    
    Returns validation results
    """
    config = pdf_config_service.get_configuration(config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration {config_id} not found")
    
    # Re-validate configuration
    response = pdf_config_service.create_configuration(config)
    return response
