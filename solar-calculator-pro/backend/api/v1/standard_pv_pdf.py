"""
Standard PV PDF API Endpoints

API endpoints for generating standard 8-page PV PDF documents.

Author: Kiro AI
Date: 2025-01-22
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from services.standard_pv_pdf_service import StandardPVPDFService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/standard-pv-pdf", tags=["Standard PV PDF"])


class CustomerData(BaseModel):
    """Customer information for PDF generation"""
    anrede: str = Field(..., description="Customer salutation (Herr/Frau)")
    vorname: str = Field(..., description="First name")
    nachname: str = Field(..., description="Last name")
    wohnort: str = Field(..., description="City/Location")
    strasse: Optional[str] = Field(None, description="Street address")
    plz: Optional[str] = Field(None, description="Postal code")


class CalculationData(BaseModel):
    """Solar calculation data for PDF generation"""
    kwp_anlage: float = Field(..., description="System size in kWp")
    module_count: int = Field(..., description="Number of modules")
    annual_production: float = Field(..., description="Annual production in kWh")
    self_consumption_rate: float = Field(..., description="Self-consumption rate in %")
    payback_period: float = Field(..., description="Payback period in years")
    co2_savings: float = Field(..., description="CO2 savings in kg")


class PricingData(BaseModel):
    """Pricing information for PDF generation"""
    total_price: float = Field(..., description="Total system price in EUR")
    module_price: Optional[float] = Field(None, description="Module price")
    inverter_price: Optional[float] = Field(None, description="Inverter price")
    battery_price: Optional[float] = Field(None, description="Battery price")
    installation_price: Optional[float] = Field(None, description="Installation price")


class PDFGenerationRequest(BaseModel):
    """Request model for PDF generation"""
    customer: CustomerData
    calculation: CalculationData
    pricing: PricingData
    include_pages: Optional[List[int]] = Field(
        None,
        description="Optional list of page numbers to include (1-8). If not provided, all pages are included."
    )
    offer_number: Optional[str] = Field(None, description="Custom offer number")


class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation"""
    success: bool
    message: str
    pdf_size_bytes: Optional[int] = None
    pages_generated: Optional[int] = None


@router.post("/generate", response_class=Response)
async def generate_standard_pv_pdf(request: PDFGenerationRequest):
    """
    Generate a standard 8-page PV PDF document.
    
    This endpoint generates a complete PDF using the template system from
    pdf_templates_static/notext/ and coordinates from coords/.
    
    **Content Includes:**
    - Page 1: Cover page (Deckblatt)
    - Page 2: Cover letter (Anschreiben)
    - Page 3: Offer positions (Angebotspositionen)
    - Page 4: Price breakdown (Preisaufstellung)
    - Page 5: Economic analysis (Wirtschaftlichkeit)
    - Page 6: Technical data (Technische Daten)
    - Page 7: 3D visualization (3D-Visualisierung)
    - Page 8: Summary (Zusammenfassung)
    
    **Features:**
    - Dynamic placeholder replacement
    - German number formatting (16.999,00 €)
    - YML-based positioning
    - Template-based design
    
    Returns:
        PDF file as binary response
    """
    try:
        # Initialize service
        service = StandardPVPDFService()
        
        # Prepare customer data
        customer_data = {
            'anrede_kunde': request.customer.anrede,
            'kunde_vorname_und_nachname': f"{request.customer.vorname} {request.customer.nachname}",
            'kunde_wohnort': request.customer.wohnort,
        }
        
        if request.customer.strasse:
            customer_data['kunde_strasse'] = request.customer.strasse
        if request.customer.plz:
            customer_data['kunde_plz'] = request.customer.plz
        
        # Prepare calculation data
        calculation_data = {
            'kWp_anlage_anlage': f"{request.calculation.kwp_anlage:,.1f} kWp".replace('.', ','),
            'module_count': str(request.calculation.module_count),
            'annual_production': f"{request.calculation.annual_production:,.0f} kWh".replace(',', '.'),
            'self_consumption_rate': f"{request.calculation.self_consumption_rate:.1f}%".replace('.', ','),
            'payback_period': f"{request.calculation.payback_period:.1f} Jahre".replace('.', ','),
            'co2_savings': f"{request.calculation.co2_savings:,.0f} kg".replace(',', '.'),
        }
        
        # Prepare pricing data with German formatting
        pricing_data = {
            'total_price': request.pricing.total_price,
        }
        
        if request.pricing.module_price:
            pricing_data['module_price'] = request.pricing.module_price
        if request.pricing.inverter_price:
            pricing_data['inverter_price'] = request.pricing.inverter_price
        if request.pricing.battery_price:
            pricing_data['battery_price'] = request.pricing.battery_price
        if request.pricing.installation_price:
            pricing_data['installation_price'] = request.pricing.installation_price
        
        # Add current date
        from datetime import datetime
        today = datetime.now()
        calculation_data['langes_datum_heute'] = today.strftime("%d. %B %Y")
        
        # Add offer number
        if request.offer_number:
            calculation_data['offer_number'] = request.offer_number
        else:
            calculation_data['offer_number'] = f"ANG-{today.year} / {today.strftime('%m%d%H%M')}"
        
        # Generate PDF
        pdf_bytes = service.generate_pdf_with_german_formatting(
            calculation_data=calculation_data,
            customer_data=customer_data,
            pricing_data=pricing_data
        )
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=angebot_{request.customer.nachname}_{today.strftime('%Y%m%d')}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.post("/generate-info", response_model=PDFGenerationResponse)
async def generate_standard_pv_pdf_info(request: PDFGenerationRequest):
    """
    Generate PDF and return information about it (without returning the PDF itself).
    
    Useful for testing and validation.
    
    Returns:
        Information about the generated PDF
    """
    try:
        # Initialize service
        service = StandardPVPDFService()
        
        # Prepare data (same as above)
        customer_data = {
            'anrede_kunde': request.customer.anrede,
            'kunde_vorname_und_nachname': f"{request.customer.vorname} {request.customer.nachname}",
            'kunde_wohnort': request.customer.wohnort,
        }
        
        calculation_data = {
            'kWp_anlage_anlage': f"{request.calculation.kwp_anlage:,.1f} kWp".replace('.', ','),
        }
        
        pricing_data = {
            'total_price': request.pricing.total_price,
        }
        
        from datetime import datetime
        today = datetime.now()
        calculation_data['langes_datum_heute'] = today.strftime("%d. %B %Y")
        
        # Generate PDF
        pdf_bytes = service.generate_pdf_with_german_formatting(
            calculation_data=calculation_data,
            customer_data=customer_data,
            pricing_data=pricing_data
        )
        
        if not pdf_bytes:
            return PDFGenerationResponse(
                success=False,
                message="Failed to generate PDF"
            )
        
        # Count pages
        pages_generated = len(request.include_pages) if request.include_pages else 8
        
        return PDFGenerationResponse(
            success=True,
            message="PDF generated successfully",
            pdf_size_bytes=len(pdf_bytes),
            pages_generated=pages_generated
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF info: {e}", exc_info=True)
        return PDFGenerationResponse(
            success=False,
            message=f"Error: {str(e)}"
        )


@router.get("/templates/available")
async def get_available_templates():
    """
    Get list of available PDF templates.
    
    Returns:
        List of available template pages
    """
    try:
        service = StandardPVPDFService()
        templates = service.template_loader.get_all_templates()
        
        return {
            "success": True,
            "templates": list(templates.keys()),
            "total_pages": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting templates: {str(e)}")


@router.get("/coordinates/page/{page_number}")
async def get_page_coordinates(page_number: int):
    """
    Get coordinate data for a specific page.
    
    Args:
        page_number: Page number (1-8)
        
    Returns:
        Coordinate data for the page
    """
    if page_number < 1 or page_number > 8:
        raise HTTPException(status_code=400, detail="Page number must be between 1 and 8")
    
    try:
        service = StandardPVPDFService()
        elements = service.load_page_coordinates(page_number)
        
        return {
            "success": True,
            "page_number": page_number,
            "elements_count": len(elements),
            "elements": elements
        }
        
    except Exception as e:
        logger.error(f"Error getting coordinates: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting coordinates: {str(e)}")
