"""
Standard WP PDF API Endpoints

This module provides REST API endpoints for generating standard 8-page
heat pump (WP) PDF documents.

Author: Kiro AI
Date: 2025-01-22
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging

from services.standard_wp_pdf_service import StandardWPPDFService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/standard-wp-pdf", tags=["Standard WP PDF"])

# Initialize service
wp_pdf_service = StandardWPPDFService()


class WPCustomerData(BaseModel):
    """Customer information for WP PDF"""
    anrede_kunde: str = Field(..., description="Customer salutation (Herr/Frau)")
    kunde_vorname_und_nachname: str = Field(..., description="Customer full name")
    kunde_wohnort: str = Field(..., description="Customer city")


class WPCalculationData(BaseModel):
    """Heat pump calculation data for PDF"""
    wp_leistung_kw: float = Field(..., description="Heat pump power in kW")
    wp_cop_wert: float = Field(..., description="COP value")
    wp_jahresarbeitszahl: float = Field(..., description="Annual performance factor (JAZ)")
    wp_heizkosten_jahr: float = Field(..., description="Annual heating costs")
    wp_heizkosten_monat: float = Field(..., description="Monthly heating costs")
    wp_einsparung_jahr: float = Field(..., description="Annual savings")
    wp_einsparung_prozent: str = Field(..., description="Savings percentage")
    wp_amortisationszeit: str = Field(..., description="Payback period")
    wp_co2_einsparung: str = Field(..., description="CO2 savings")
    wp_effizienzklasse: str = Field(..., description="Efficiency class")
    wp_vorlauftemperatur: str = Field(..., description="Flow temperature")
    wp_heizlast_kw: float = Field(..., description="Heating load in kW")
    wp_warmwasser_liter: int = Field(..., description="Hot water capacity in liters")
    wp_modell_name: str = Field(..., description="Heat pump model name")
    wp_hersteller: str = Field(..., description="Manufacturer")


class WPPricingData(BaseModel):
    """Pricing data for WP PDF"""
    total_price: float = Field(..., description="Total price")
    additional_costs: Optional[Dict[str, float]] = Field(default=None, description="Additional costs breakdown")


class WPPDFGenerationRequest(BaseModel):
    """Request model for WP PDF generation"""
    customer_data: WPCustomerData
    calculation_data: WPCalculationData
    pricing_data: WPPricingData
    include_pages: Optional[List[int]] = Field(
        default=None,
        description="Optional list of page numbers to include (1-8). If not provided, all pages are included."
    )
    langes_datum_heute: Optional[str] = Field(
        default=None,
        description="Date string in German format (e.g., '22. Januar 2025')"
    )


class WPPDFGenerationResponse(BaseModel):
    """Response model for WP PDF generation"""
    success: bool
    message: str
    pdf_size_bytes: Optional[int] = None


@router.post("/generate", response_class=Response)
async def generate_wp_pdf(request: WPPDFGenerationRequest):
    """
    Generate a standard 8-page heat pump PDF document.
    
    This endpoint generates a complete WP PDF with:
    - Customer information
    - Heat pump calculations (COP, JAZ, heating costs)
    - Cost analysis and savings
    - Efficiency ratings
    - Technical specifications
    - Comparison charts
    
    All numeric values are formatted in German format (e.g., 16.999,00 €).
    
    Args:
        request: WP PDF generation request with customer, calculation, and pricing data
        
    Returns:
        PDF file as binary response
        
    Raises:
        HTTPException: If PDF generation fails
    """
    try:
        # Prepare data dictionaries
        customer_dict = request.customer_data.dict()
        calculation_dict = request.calculation_data.dict()
        pricing_dict = request.pricing_data.dict()
        
        # Add date if provided
        if request.langes_datum_heute:
            customer_dict['langes_datum_heute'] = request.langes_datum_heute
        
        # Generate PDF
        pdf_bytes = wp_pdf_service.generate_pdf_with_german_formatting(
            calculation_data=calculation_dict,
            customer_data=customer_dict,
            pricing_data=pricing_dict
        )
        
        if not pdf_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate WP PDF"
            )
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=wp_angebot_{customer_dict.get('kunde_vorname_und_nachname', 'kunde').replace(' ', '_')}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating WP PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating WP PDF: {str(e)}"
        )


@router.post("/generate-custom", response_class=Response)
async def generate_custom_wp_pdf(
    data: Dict[str, Any],
    include_pages: Optional[List[int]] = None
):
    """
    Generate a WP PDF with custom data structure.
    
    This endpoint allows more flexibility in the data structure,
    accepting any dictionary of key-value pairs that match the
    placeholders in the WP templates.
    
    Args:
        data: Dictionary containing all placeholder values
        include_pages: Optional list of page numbers to include (1-8)
        
    Returns:
        PDF file as binary response
        
    Raises:
        HTTPException: If PDF generation fails
    """
    try:
        pdf_bytes = wp_pdf_service.generate_complete_pdf(
            data=data,
            include_pages=include_pages
        )
        
        if not pdf_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate custom WP PDF"
            )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=wp_angebot_custom.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating custom WP PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating custom WP PDF: {str(e)}"
        )


@router.get("/templates")
async def get_available_templates():
    """
    Get information about available WP PDF templates.
    
    Returns:
        Dictionary with template information
    """
    try:
        templates = wp_pdf_service.template_loader.get_all_templates()
        
        return {
            "success": True,
            "total_pages": 8,
            "available_templates": list(templates.keys()),
            "template_directory": str(wp_pdf_service.template_loader.template_dir),
            "coordinates_directory": str(wp_pdf_service.coords_dir),
            "template_files": [f"hp_nt_{i:02d}.pdf" for i in range(1, 9)],
            "coordinate_files": [f"wp_seite{i}.yml" for i in range(1, 9)]
        }
        
    except Exception as e:
        logger.error(f"Error getting WP template information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting template information: {str(e)}"
        )


@router.get("/placeholders")
async def get_available_placeholders():
    """
    Get list of available placeholders for WP PDFs.
    
    Returns:
        Dictionary with static and dynamic placeholders
    """
    from services.standard_wp_pdf_service import WPPlaceholderSystem
    
    return {
        "success": True,
        "static_placeholders": list(WPPlaceholderSystem.STATIC_PLACEHOLDERS.keys()),
        "dynamic_placeholders": WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS,
        "description": {
            "static": "Static text that appears in templates",
            "dynamic": "Placeholders that get replaced with actual data"
        }
    }


@router.post("/validate-data")
async def validate_wp_data(data: Dict[str, Any]):
    """
    Validate WP data before PDF generation.
    
    Checks if all required placeholders are present and properly formatted.
    
    Args:
        data: Dictionary containing placeholder values
        
    Returns:
        Validation result with missing fields and warnings
    """
    from services.standard_wp_pdf_service import WPPlaceholderSystem
    
    missing_fields = []
    warnings = []
    
    # Check for required dynamic placeholders
    required_fields = [
        'anrede_kunde',
        'kunde_vorname_und_nachname',
        'kunde_wohnort',
        'wp_leistung_kw',
        'wp_cop_wert',
        'wp_modell_name',
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    # Check numeric fields
    numeric_fields = [
        'wp_leistung_kw',
        'wp_cop_wert',
        'wp_jahresarbeitszahl',
        'wp_heizkosten_jahr',
        'wp_heizkosten_monat',
        'wp_einsparung_jahr',
        'wp_heizlast_kw',
        'total_price'
    ]
    
    for field in numeric_fields:
        if field in data and not isinstance(data[field], (int, float)):
            warnings.append(f"{field} should be numeric")
    
    is_valid = len(missing_fields) == 0
    
    return {
        "valid": is_valid,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "message": "Data is valid" if is_valid else "Data validation failed"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for WP PDF service.
    
    Returns:
        Service health status
    """
    try:
        # Check if templates directory exists
        template_dir_exists = wp_pdf_service.template_loader.template_dir.exists()
        
        # Check if coordinates directory exists
        coords_dir_exists = wp_pdf_service.coords_dir.exists()
        
        # Check if at least one template exists
        templates = wp_pdf_service.template_loader.get_all_templates()
        has_templates = len(templates) > 0
        
        is_healthy = template_dir_exists and coords_dir_exists and has_templates
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "template_directory_exists": template_dir_exists,
            "coordinates_directory_exists": coords_dir_exists,
            "available_templates": len(templates),
            "service": "Standard WP PDF Service"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "Standard WP PDF Service"
        }
