"""
Extended WP PDF API Endpoints

This module provides REST API endpoints for generating extended WP (Heat Pump) PDF documents
with optional additional pages.

Author: Kiro AI
Date: 2025-01-22
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from ...services.extended_wp_pdf_service import (
    ExtendedWPPDFService,
    WPComponentSelection,
    WPComponentType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extended-wp-pdf", tags=["Extended WP PDF"])


# Request/Response Models
class WPComponentSelectionRequest(BaseModel):
    """Request model for WP component selection"""
    include_detailed_wp_calculations: bool = Field(False, description="Include detailed WP calculations")
    include_additional_wp_diagrams: bool = Field(False, description="Include additional WP diagrams")
    include_wp_product_datasheets: bool = Field(False, description="Include WP product datasheets")
    include_wp_documents: bool = Field(False, description="Include WP documents from database")
    include_wp_images: bool = Field(False, description="Include WP images from database")
    include_extended_wp_visualizations: bool = Field(False, description="Include extended WP visualizations")
    
    selected_wp_diagram_types: List[str] = Field(default_factory=list, description="Selected WP diagram types")
    selected_wp_product_ids: List[str] = Field(default_factory=list, description="Selected WP product IDs")
    selected_wp_document_ids: List[str] = Field(default_factory=list, description="Selected WP document IDs")
    selected_wp_image_ids: List[str] = Field(default_factory=list, description="Selected WP image IDs")


class ExtendedWPPDFGenerationRequest(BaseModel):
    """Request model for extended WP PDF generation"""
    customer_data: Dict[str, Any] = Field(..., description="Customer information")
    calculation_data: Dict[str, Any] = Field(..., description="WP calculation results")
    pricing_data: Dict[str, Any] = Field(..., description="Pricing information")
    component_selection: WPComponentSelectionRequest = Field(..., description="Component selection")


class AvailableWPComponentsResponse(BaseModel):
    """Response model for available WP components"""
    wp_calculations: List[Dict[str, str]]
    wp_diagrams: List[Dict[str, str]]
    wp_datasheets: List[Dict[str, str]]
    wp_documents: List[Dict[str, str]]
    wp_images: List[Dict[str, str]]


# Dependency to get service instance
def get_extended_wp_pdf_service() -> ExtendedWPPDFService:
    """Get ExtendedWPPDFService instance"""
    return ExtendedWPPDFService()


@router.post("/generate", response_class=Response)
async def generate_extended_wp_pdf(
    request: ExtendedWPPDFGenerationRequest,
    service: ExtendedWPPDFService = Depends(get_extended_wp_pdf_service)
):
    """
    Generate extended WP PDF with optional additional pages.
    
    Args:
        request: PDF generation request with data and component selection
        service: ExtendedWPPDFService instance
        
    Returns:
        PDF file as binary response
    """
    try:
        # Merge all data
        data = {
            **request.customer_data,
            **request.calculation_data,
            **request.pricing_data
        }
        
        # Convert request to WPComponentSelection
        component_selection = WPComponentSelection(
            include_detailed_wp_calculations=request.component_selection.include_detailed_wp_calculations,
            include_additional_wp_diagrams=request.component_selection.include_additional_wp_diagrams,
            include_wp_product_datasheets=request.component_selection.include_wp_product_datasheets,
            include_wp_documents=request.component_selection.include_wp_documents,
            include_wp_images=request.component_selection.include_wp_images,
            include_extended_wp_visualizations=request.component_selection.include_extended_wp_visualizations,
            selected_wp_diagram_types=request.component_selection.selected_wp_diagram_types,
            selected_wp_product_ids=request.component_selection.selected_wp_product_ids,
            selected_wp_document_ids=request.component_selection.selected_wp_document_ids,
            selected_wp_image_ids=request.component_selection.selected_wp_image_ids
        )
        
        # Generate PDF
        pdf_bytes = service.generate_extended_wp_pdf(data, component_selection)
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate extended WP PDF")
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=extended_wp_offer.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating extended WP PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-components", response_model=AvailableWPComponentsResponse)
async def get_available_wp_components(
    product_ids: Optional[List[str]] = None,
    service: ExtendedWPPDFService = Depends(get_extended_wp_pdf_service)
):
    """
    Get available WP components that can be added to extended PDF.
    
    Args:
        product_ids: Optional list of WP product IDs
        service: ExtendedWPPDFService instance
        
    Returns:
        Dictionary of available WP components by type
    """
    try:
        components = service.get_available_wp_components(product_ids)
        return AvailableWPComponentsResponse(**components)
        
    except Exception as e:
        logger.error(f"Error getting available WP components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview", response_class=Response)
async def preview_extended_wp_pdf(
    request: ExtendedWPPDFGenerationRequest,
    service: ExtendedWPPDFService = Depends(get_extended_wp_pdf_service)
):
    """
    Generate preview of extended WP PDF (same as generate but for preview purposes).
    
    Args:
        request: PDF generation request
        service: ExtendedWPPDFService instance
        
    Returns:
        PDF file as binary response
    """
    # Preview is the same as generate for now
    return await generate_extended_wp_pdf(request, service)
