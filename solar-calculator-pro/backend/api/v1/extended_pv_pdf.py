"""
Extended PV PDF API Endpoints

API endpoints for generating extended PV PDF documents with optional additional pages.

Author: Kiro AI
Date: 2025-01-22
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from fastapi.responses import Response
import logging

from ...services.extended_pv_pdf_service import (
    ExtendedPVPDFService,
    ComponentSelection,
    ComponentType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extended-pv-pdf", tags=["Extended PV PDF"])


# Request/Response Models

class ComponentSelectionRequest(BaseModel):
    """Request model for component selection"""
    include_detailed_calculations: bool = Field(False, description="Include detailed calculations")
    include_additional_diagrams: bool = Field(False, description="Include additional diagrams")
    include_product_datasheets: bool = Field(False, description="Include product datasheets")
    include_documents: bool = Field(False, description="Include documents from database")
    include_images: bool = Field(False, description="Include images from database")
    include_extended_visualizations: bool = Field(False, description="Include extended visualizations")
    
    selected_diagram_types: List[str] = Field(default_factory=list, description="Selected diagram types")
    selected_product_ids: List[str] = Field(default_factory=list, description="Selected product IDs")
    selected_document_ids: List[str] = Field(default_factory=list, description="Selected document IDs")
    selected_image_ids: List[str] = Field(default_factory=list, description="Selected image IDs")


class ExtendedPDFGenerationRequest(BaseModel):
    """Request model for extended PDF generation"""
    customer_data: Dict[str, Any] = Field(..., description="Customer information")
    calculation_data: Dict[str, Any] = Field(..., description="Solar calculation results")
    pricing_data: Dict[str, Any] = Field(..., description="Pricing information")
    component_selection: ComponentSelectionRequest = Field(..., description="Component selection")


class AvailableComponentsRequest(BaseModel):
    """Request model for getting available components"""
    product_ids: Optional[List[str]] = Field(None, description="Product IDs to get specific components")


class AvailableComponentsResponse(BaseModel):
    """Response model for available components"""
    calculations: List[Dict[str, str]] = Field(..., description="Available calculation types")
    diagrams: List[Dict[str, str]] = Field(..., description="Available diagram types")
    datasheets: List[Dict[str, str]] = Field(..., description="Available datasheets")
    documents: List[Dict[str, str]] = Field(..., description="Available documents")
    images: List[Dict[str, str]] = Field(..., description="Available images")


class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation"""
    success: bool = Field(..., description="Whether generation was successful")
    message: str = Field(..., description="Status message")
    total_pages: int = Field(..., description="Total number of pages in PDF")
    standard_pages: int = Field(8, description="Number of standard pages")
    additional_pages: int = Field(..., description="Number of additional pages")


# Dependency to get service instance
def get_extended_pdf_service() -> ExtendedPVPDFService:
    """Get Extended PV PDF service instance"""
    # In production, this would get the service from dependency injection
    return ExtendedPVPDFService()


# API Endpoints

@router.post(
    "/generate",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Extended PDF document"
        }
    },
    summary="Generate Extended PV PDF",
    description="Generate extended PV PDF with standard 8 pages plus optional additional pages"
)
async def generate_extended_pdf(
    request: ExtendedPDFGenerationRequest,
    service: ExtendedPVPDFService = Depends(get_extended_pdf_service)
):
    """
    Generate extended PV PDF document.
    
    This endpoint generates a PDF with:
    - Standard 8 pages (always included)
    - Optional additional pages based on component selection
    - Dynamic content from database (datasheets, documents, images)
    """
    try:
        # Merge all data
        data = {
            **request.customer_data,
            **request.calculation_data,
            **request.pricing_data
        }
        
        # Convert request to ComponentSelection
        component_selection = ComponentSelection(
            include_detailed_calculations=request.component_selection.include_detailed_calculations,
            include_additional_diagrams=request.component_selection.include_additional_diagrams,
            include_product_datasheets=request.component_selection.include_product_datasheets,
            include_documents=request.component_selection.include_documents,
            include_images=request.component_selection.include_images,
            include_extended_visualizations=request.component_selection.include_extended_visualizations,
            selected_diagram_types=request.component_selection.selected_diagram_types,
            selected_product_ids=request.component_selection.selected_product_ids,
            selected_document_ids=request.component_selection.selected_document_ids,
            selected_image_ids=request.component_selection.selected_image_ids
        )
        
        # Generate PDF
        pdf_bytes = service.generate_extended_pdf(data, component_selection)
        
        if not pdf_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF"
            )
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=extended_pv_offer.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating extended PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )


@router.post(
    "/generate-async",
    response_model=PDFGenerationResponse,
    summary="Generate Extended PV PDF Asynchronously",
    description="Generate extended PV PDF in background and return status"
)
async def generate_extended_pdf_async(
    request: ExtendedPDFGenerationRequest,
    background_tasks: BackgroundTasks,
    service: ExtendedPVPDFService = Depends(get_extended_pdf_service)
):
    """
    Generate extended PV PDF asynchronously.
    
    This endpoint starts PDF generation in the background and returns immediately.
    Useful for large PDFs with many additional pages.
    """
    try:
        # Add PDF generation to background tasks
        background_tasks.add_task(
            _generate_pdf_background,
            service,
            request
        )
        
        return PDFGenerationResponse(
            success=True,
            message="PDF generation started in background",
            total_pages=8,  # Will be updated when complete
            standard_pages=8,
            additional_pages=0
        )
        
    except Exception as e:
        logger.error(f"Error starting PDF generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting PDF generation: {str(e)}"
        )


@router.post(
    "/available-components",
    response_model=AvailableComponentsResponse,
    summary="Get Available Components",
    description="Get list of available components that can be added to extended PDF"
)
async def get_available_components(
    request: AvailableComponentsRequest,
    service: ExtendedPVPDFService = Depends(get_extended_pdf_service)
):
    """
    Get available components for extended PDF.
    
    Returns lists of:
    - Available calculation types
    - Available diagram types
    - Available datasheets (product-specific)
    - Available documents (product-specific)
    - Available images
    """
    try:
        components = service.get_available_components(request.product_ids)
        
        return AvailableComponentsResponse(
            calculations=components.get('calculations', []),
            diagrams=components.get('diagrams', []),
            datasheets=components.get('datasheets', []),
            documents=components.get('documents', []),
            images=components.get('images', [])
        )
        
    except Exception as e:
        logger.error(f"Error getting available components: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available components: {str(e)}"
        )


@router.post(
    "/preview",
    response_model=PDFGenerationResponse,
    summary="Preview Extended PDF Configuration",
    description="Preview how many pages will be generated with current selection"
)
async def preview_extended_pdf(
    request: ComponentSelectionRequest,
    service: ExtendedPVPDFService = Depends(get_extended_pdf_service)
):
    """
    Preview extended PDF configuration.
    
    Returns information about how many pages will be generated
    without actually generating the PDF.
    """
    try:
        # Calculate number of additional pages
        additional_pages = 0
        
        if request.include_detailed_calculations:
            additional_pages += 1
        
        if request.include_additional_diagrams:
            additional_pages += len(request.selected_diagram_types)
        
        if request.include_product_datasheets:
            additional_pages += len(request.selected_product_ids)
        
        if request.include_documents:
            additional_pages += len(request.selected_document_ids)
        
        if request.include_images:
            additional_pages += len(request.selected_image_ids)
        
        if request.include_extended_visualizations:
            additional_pages += 1
        
        total_pages = 8 + additional_pages
        
        return PDFGenerationResponse(
            success=True,
            message=f"PDF will have {total_pages} pages ({additional_pages} additional)",
            total_pages=total_pages,
            standard_pages=8,
            additional_pages=additional_pages
        )
        
    except Exception as e:
        logger.error(f"Error previewing PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error previewing PDF: {str(e)}"
        )


# Background task function
async def _generate_pdf_background(
    service: ExtendedPVPDFService,
    request: ExtendedPDFGenerationRequest
):
    """Background task for PDF generation"""
    try:
        # Merge all data
        data = {
            **request.customer_data,
            **request.calculation_data,
            **request.pricing_data
        }
        
        # Convert request to ComponentSelection
        component_selection = ComponentSelection(
            include_detailed_calculations=request.component_selection.include_detailed_calculations,
            include_additional_diagrams=request.component_selection.include_additional_diagrams,
            include_product_datasheets=request.component_selection.include_product_datasheets,
            include_documents=request.component_selection.include_documents,
            include_images=request.component_selection.include_images,
            include_extended_visualizations=request.component_selection.include_extended_visualizations,
            selected_diagram_types=request.component_selection.selected_diagram_types,
            selected_product_ids=request.component_selection.selected_product_ids,
            selected_document_ids=request.component_selection.selected_document_ids,
            selected_image_ids=request.component_selection.selected_image_ids
        )
        
        # Generate PDF
        pdf_bytes = service.generate_extended_pdf(data, component_selection)
        
        if pdf_bytes:
            logger.info("Background PDF generation completed successfully")
            # In production, this would save to database or send notification
        else:
            logger.error("Background PDF generation failed")
            
    except Exception as e:
        logger.error(f"Error in background PDF generation: {e}")


# Health check endpoint
@router.get(
    "/health",
    summary="Health Check",
    description="Check if Extended PV PDF service is available"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Extended PV PDF Service",
        "version": "1.0.0"
    }
