"""
Multi-Offer PDF Generation (ZIP) API

Provides REST API for multi-offer PDF generation:
- Multi-company offer generation
- Product rotation across offers
- Price increase rules per offer
- Generate all PDFs with one click
- Package all PDFs in ZIP file
- Individual PDF downloads

Requirements: funktionen.txt - "Multi-Angebot"
Task: 267. Multi-Offer PDF Generation (ZIP)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import io
import zipfile
import uuid

router = APIRouter(prefix="/pdf/multi-offer", tags=["Multi-Offer PDF"])


# ==================== Enums ====================

class PriceModificationType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    PER_KWP = "per_kwp"


class ProductRotationType(str, Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    BY_PRICE = "by_price"
    BY_QUALITY = "by_quality"


# ==================== Pydantic Models ====================

class CompanyConfig(BaseModel):
    """Company configuration for multi-offer"""
    company_id: str
    company_name: str
    logo_url: Optional[str] = None
    address: str
    phone: str
    email: str
    website: Optional[str] = None
    primary_color: str = "#3B82F6"


class PriceModification(BaseModel):
    """Price modification rule"""
    modification_type: PriceModificationType
    value: float
    apply_to: str = "total"  # "total", "products", "services"
    description: Optional[str] = None


class ProductRotation(BaseModel):
    """Product rotation configuration"""
    rotation_type: ProductRotationType = ProductRotationType.SEQUENTIAL
    product_ids: List[str]
    component_type: str  # "module", "inverter", "battery"


class OfferVariant(BaseModel):
    """Single offer variant configuration"""
    variant_id: str
    variant_name: str
    company: CompanyConfig
    price_modifications: List[PriceModification] = []
    product_overrides: Dict[str, str] = {}
    custom_notes: Optional[str] = None
    enabled: bool = True


class MultiOfferRequest(BaseModel):
    """Request for multi-offer generation"""
    base_offer_id: str
    customer_name: str
    project_address: str
    variants: List[OfferVariant]
    product_rotations: List[ProductRotation] = []
    generate_comparison_sheet: bool = True
    include_individual_pdfs: bool = True
    zip_filename: Optional[str] = None


class GeneratedOffer(BaseModel):
    """Generated offer info"""
    variant_id: str
    variant_name: str
    company_name: str
    filename: str
    page_count: int
    total_price_eur: float
    file_size_bytes: int


class MultiOfferResult(BaseModel):
    """Result of multi-offer generation"""
    job_id: str
    generated_at: datetime
    total_offers: int
    offers: List[GeneratedOffer]
    comparison_sheet_included: bool
    zip_filename: str
    total_size_bytes: int


# ==================== Mock Data ====================

_mock_companies = [
    CompanyConfig(
        company_id="comp_001",
        company_name="SolarTech GmbH",
        address="Solarstraße 1, 12345 Sonnenstadt",
        phone="+49 123 456789",
        email="info@solartech.de",
        primary_color="#F59E0B"
    ),
    CompanyConfig(
        company_id="comp_002",
        company_name="GreenEnergy AG",
        address="Grüner Weg 42, 54321 Ökostadt",
        phone="+49 987 654321",
        email="kontakt@greenenergy.de",
        primary_color="#10B981"
    ),
    CompanyConfig(
        company_id="comp_003",
        company_name="SunPower Solutions",
        address="Sonnenallee 100, 11111 Lichtstadt",
        phone="+49 111 222333",
        email="hello@sunpower.de",
        primary_color="#3B82F6"
    )
]


# ==================== Helper Functions ====================

def generate_offer_id() -> str:
    return f"offer_{uuid.uuid4().hex[:8]}"


def apply_price_modifications(base_price: float, modifications: List[PriceModification]) -> float:
    """Apply price modifications to base price"""
    price = base_price
    for mod in modifications:
        if mod.modification_type == PriceModificationType.PERCENTAGE:
            price *= (1 + mod.value / 100)
        elif mod.modification_type == PriceModificationType.FIXED_AMOUNT:
            price += mod.value
        elif mod.modification_type == PriceModificationType.PER_KWP:
            # Assuming 10 kWp system for mock
            price += mod.value * 10
    return round(price, 2)


def generate_single_offer_pdf(variant: OfferVariant, base_price: float) -> bytes:
    """Generate single offer PDF (mock)"""
    final_price = apply_price_modifications(base_price, variant.price_modifications)
    
    # Mock PDF content
    pdf_content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 7 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >> endobj
% Offer: {variant.variant_name}
% Company: {variant.company.company_name}
% Price: {final_price} EUR
xref
0 4
trailer << /Size 4 /Root 1 0 R >>
startxref
%%EOF
"""
    return pdf_content.encode('utf-8')


def generate_comparison_sheet(variants: List[OfferVariant], base_price: float) -> bytes:
    """Generate comparison sheet PDF"""
    content = "%PDF-1.4\n% Comparison Sheet\n"
    for v in variants:
        price = apply_price_modifications(base_price, v.price_modifications)
        content += f"% {v.company.company_name}: {price} EUR\n"
    content += "%%EOF"
    return content.encode('utf-8')


def create_zip_archive(offers: List[tuple], comparison_sheet: Optional[bytes] = None) -> bytes:
    """Create ZIP archive with all PDFs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, pdf_bytes in offers:
            zip_file.writestr(filename, pdf_bytes)
        
        if comparison_sheet:
            zip_file.writestr("Vergleichsübersicht.pdf", comparison_sheet)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_multi_offer(request: MultiOfferRequest):
    """Generate multiple offer PDFs and package in ZIP."""
    try:
        base_price = 18500.0  # Mock base price
        generated_offers = []
        pdf_files = []
        
        for idx, variant in enumerate(request.variants, start=1):
            if not variant.enabled:
                continue
            
            # Generate PDF
            pdf_bytes = generate_single_offer_pdf(variant, base_price)
            final_price = apply_price_modifications(base_price, variant.price_modifications)
            
            # Create unique filename with index and sanitized company name
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in variant.company.company_name).strip().replace(' ', '_')
            safe_customer = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in request.customer_name).strip().replace(' ', '_')
            filename = f"{idx:02d}_Angebot_{safe_name}_{safe_customer}.pdf"
            
            pdf_files.append((filename, pdf_bytes))
            
            generated_offers.append(GeneratedOffer(
                variant_id=variant.variant_id,
                variant_name=variant.variant_name,
                company_name=variant.company.company_name,
                filename=filename,
                page_count=7,
                total_price_eur=final_price,
                file_size_bytes=len(pdf_bytes)
            ))
        
        # Generate comparison sheet
        comparison_sheet = None
        if request.generate_comparison_sheet:
            comparison_sheet = generate_comparison_sheet(request.variants, base_price)
        
        # Create ZIP
        zip_bytes = create_zip_archive(pdf_files, comparison_sheet)
        
        zip_filename = request.zip_filename or f"Angebote_{request.customer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-Offer Generierung fehlgeschlagen: {str(e)}")


@router.post("/preview")
async def preview_multi_offer(request: MultiOfferRequest):
    """Preview multi-offer configuration."""
    base_price = 18500.0
    
    previews = []
    for variant in request.variants:
        if variant.enabled:
            final_price = apply_price_modifications(base_price, variant.price_modifications)
            previews.append({
                "variant_id": variant.variant_id,
                "variant_name": variant.variant_name,
                "company_name": variant.company.company_name,
                "base_price": base_price,
                "final_price": final_price,
                "price_difference": final_price - base_price,
                "price_difference_percent": round((final_price - base_price) / base_price * 100, 1)
            })
    
    return {
        "total_variants": len(previews),
        "variants": previews,
        "comparison_sheet": request.generate_comparison_sheet,
        "estimated_zip_size_kb": len(previews) * 200 + (50 if request.generate_comparison_sheet else 0)
    }


@router.get("/companies")
async def get_available_companies():
    """Get available companies for multi-offer."""
    return {"companies": _mock_companies}


@router.post("/companies")
async def add_company(company: CompanyConfig):
    """Add a new company for multi-offer."""
    _mock_companies.append(company)
    return {"company": company, "added": True}


@router.get("/price-modification-types")
async def get_price_modification_types():
    """Get available price modification types."""
    return {
        "types": [
            {"id": "percentage", "name": "Prozentual", "example": "+5% auf Gesamtpreis"},
            {"id": "fixed_amount", "name": "Festbetrag", "example": "+500€ auf Gesamtpreis"},
            {"id": "per_kwp", "name": "Pro kWp", "example": "+100€ pro kWp"}
        ]
    }


@router.get("/rotation-types")
async def get_rotation_types():
    """Get available product rotation types."""
    return {
        "types": [
            {"id": "sequential", "name": "Sequentiell", "description": "Produkte der Reihe nach"},
            {"id": "random", "name": "Zufällig", "description": "Zufällige Produktauswahl"},
            {"id": "by_price", "name": "Nach Preis", "description": "Sortiert nach Preis"},
            {"id": "by_quality", "name": "Nach Qualität", "description": "Sortiert nach Qualitätsstufe"}
        ]
    }


@router.get("/offer/{variant_id}")
async def download_single_offer(variant_id: str, base_offer_id: str):
    """Download a single offer from multi-offer set."""
    # Mock single offer download
    pdf_content = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n%%EOF"
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Angebot_{variant_id}.pdf"}
    )


@router.get("/health/check")
async def health_check():
    """Health check for multi-offer PDF service."""
    return {
        "status": "healthy",
        "service": "multi-offer-pdf",
        "companies_count": len(_mock_companies),
        "timestamp": datetime.now().isoformat()
    }
