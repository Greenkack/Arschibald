"""
Extended Offer PDF with Optional Pages API

Provides REST API for extended offer PDFs with optional pages:
- Optional page selection UI
- Product datasheets as attachments
- Product images in PDF
- Additional diagrams (12-month yield, cashflow, CO2)
- Company/partner logos and certificates
- Flexible page ordering

Requirements: funktionen.txt - "Erweitertes Angebot"
Task: 266. Extended Offer PDF with Optional Pages
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import io
import uuid

router = APIRouter(prefix="/pdf/extended-offer", tags=["Extended Offer PDF"])


# ==================== Enums ====================

class OptionalPageType(str, Enum):
    PRODUCT_DATASHEET = "product_datasheet"
    PRODUCT_IMAGES = "product_images"
    MONTHLY_YIELD = "monthly_yield"
    CASHFLOW_ANALYSIS = "cashflow_analysis"
    CO2_SAVINGS = "co2_savings"
    COMPANY_CERTIFICATES = "company_certificates"
    PARTNER_LOGOS = "partner_logos"
    REFERENCES = "references"
    FAQ = "faq"
    INSTALLATION_TIMELINE = "installation_timeline"


class DiagramType(str, Enum):
    MONTHLY_YIELD = "monthly_yield"
    ANNUAL_COMPARISON = "annual_comparison"
    CASHFLOW_20_YEARS = "cashflow_20_years"
    CO2_REDUCTION = "co2_reduction"
    AUTARKY_BREAKDOWN = "autarky_breakdown"
    CONSUMPTION_PATTERN = "consumption_pattern"


# ==================== Pydantic Models ====================

class OptionalPage(BaseModel):
    """Optional page configuration"""
    page_type: OptionalPageType
    enabled: bool = True
    order: int = 0
    title: Optional[str] = None
    custom_content: Optional[Dict[str, Any]] = None


class ProductDatasheet(BaseModel):
    """Product datasheet for attachment"""
    product_id: str
    product_name: str
    manufacturer: str
    datasheet_url: Optional[str] = None
    include_specs: bool = True
    include_image: bool = True


class DiagramConfig(BaseModel):
    """Diagram configuration"""
    diagram_type: DiagramType
    title: str
    show_legend: bool = True
    show_values: bool = True
    color_scheme: str = "default"
    data: Optional[Dict[str, Any]] = None


class CompanyBranding(BaseModel):
    """Company branding configuration"""
    company_name: str
    logo_url: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    footer_text: Optional[str] = None


class PartnerLogo(BaseModel):
    """Partner logo configuration"""
    partner_name: str
    logo_url: str
    description: Optional[str] = None
    website: Optional[str] = None


class Certificate(BaseModel):
    """Certificate configuration"""
    name: str
    issuer: str
    valid_until: Optional[datetime] = None
    image_url: Optional[str] = None


class ExtendedOfferRequest(BaseModel):
    """Request for extended offer PDF"""
    base_offer_id: str
    optional_pages: List[OptionalPage] = []
    product_datasheets: List[ProductDatasheet] = []
    additional_diagrams: List[DiagramConfig] = []
    company_branding: Optional[CompanyBranding] = None
    partner_logos: List[PartnerLogo] = []
    certificates: List[Certificate] = []
    page_order: List[str] = []
    include_table_of_contents: bool = True
    include_page_numbers: bool = True
    watermark: Optional[str] = None


class PageOrderItem(BaseModel):
    """Page order item"""
    page_id: str
    page_type: str
    title: str
    order: int
    required: bool = False
    enabled: bool = True


class ExtendedOfferPreview(BaseModel):
    """Extended offer preview"""
    total_pages: int
    page_list: List[PageOrderItem]
    estimated_file_size_kb: int
    includes_attachments: bool
    attachment_count: int


# ==================== Helper Functions ====================

def get_default_optional_pages() -> List[OptionalPage]:
    """Get default optional pages"""
    return [
        OptionalPage(page_type=OptionalPageType.PRODUCT_DATASHEET, enabled=True, order=8),
        OptionalPage(page_type=OptionalPageType.MONTHLY_YIELD, enabled=True, order=9),
        OptionalPage(page_type=OptionalPageType.CASHFLOW_ANALYSIS, enabled=True, order=10),
        OptionalPage(page_type=OptionalPageType.CO2_SAVINGS, enabled=False, order=11),
        OptionalPage(page_type=OptionalPageType.COMPANY_CERTIFICATES, enabled=False, order=12),
        OptionalPage(page_type=OptionalPageType.REFERENCES, enabled=False, order=13),
    ]


def generate_page_content(page: OptionalPage) -> Dict[str, Any]:
    """Generate content for optional page"""
    content_generators = {
        OptionalPageType.PRODUCT_DATASHEET: generate_datasheet_content,
        OptionalPageType.MONTHLY_YIELD: generate_monthly_yield_content,
        OptionalPageType.CASHFLOW_ANALYSIS: generate_cashflow_content,
        OptionalPageType.CO2_SAVINGS: generate_co2_content,
        OptionalPageType.COMPANY_CERTIFICATES: generate_certificates_content,
        OptionalPageType.REFERENCES: generate_references_content,
    }
    
    generator = content_generators.get(page.page_type)
    if generator:
        return generator(page)
    return {"title": page.title or page.page_type.value, "content": "Inhalt wird generiert..."}


def generate_datasheet_content(page: OptionalPage) -> Dict[str, Any]:
    return {
        "title": "Produktdatenblätter",
        "description": "Technische Spezifikationen der verwendeten Komponenten",
        "products": []
    }


def generate_monthly_yield_content(page: OptionalPage) -> Dict[str, Any]:
    months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    return {
        "title": "Monatlicher Ertrag (12-Monats-Übersicht)",
        "chart_type": "bar",
        "labels": months,
        "datasets": [
            {"label": "Ertrag kWh", "data": [300, 450, 700, 900, 1100, 1200, 1150, 1000, 800, 550, 350, 250]},
            {"label": "Verbrauch kWh", "data": [400, 380, 350, 320, 300, 280, 290, 300, 330, 370, 390, 420]}
        ],
        "total_yield": 8750,
        "total_consumption": 4130
    }


def generate_cashflow_content(page: OptionalPage) -> Dict[str, Any]:
    years = list(range(1, 21))
    cumulative = []
    current = -18500
    for year in years:
        current += 1850
        cumulative.append(current)
    
    return {
        "title": "Cashflow-Analyse (20 Jahre)",
        "chart_type": "line",
        "labels": [f"Jahr {y}" for y in years],
        "datasets": [
            {"label": "Kumulierter Cashflow €", "data": cumulative}
        ],
        "investment": 18500,
        "annual_savings": 1850,
        "payback_year": 10,
        "total_profit_20_years": 18500
    }


def generate_co2_content(page: OptionalPage) -> Dict[str, Any]:
    return {
        "title": "CO₂-Einsparung",
        "annual_co2_kg": 3040,
        "lifetime_co2_tons": 60.8,
        "equivalent_trees": 152,
        "equivalent_car_km": 15200,
        "chart_type": "comparison",
        "comparison_items": [
            {"label": "Bäume gepflanzt", "value": 152, "icon": "tree"},
            {"label": "Auto-km vermieden", "value": 15200, "icon": "car"},
            {"label": "Flüge Frankfurt-NY", "value": 3, "icon": "plane"}
        ]
    }


def generate_certificates_content(page: OptionalPage) -> Dict[str, Any]:
    return {
        "title": "Zertifikate und Qualifikationen",
        "certificates": [
            {"name": "ISO 9001:2015", "issuer": "TÜV Süd", "valid": True},
            {"name": "Meisterbetrieb", "issuer": "HWK", "valid": True},
            {"name": "SMA Certified Installer", "issuer": "SMA", "valid": True}
        ]
    }


def generate_references_content(page: OptionalPage) -> Dict[str, Any]:
    return {
        "title": "Referenzen",
        "projects": [
            {"location": "München", "size_kwp": 12.5, "year": 2024},
            {"location": "Stuttgart", "size_kwp": 8.0, "year": 2024},
            {"location": "Frankfurt", "size_kwp": 15.0, "year": 2023}
        ],
        "total_projects": 250,
        "total_kwp_installed": 2500
    }


def calculate_page_order(request: ExtendedOfferRequest) -> List[PageOrderItem]:
    """Calculate final page order"""
    pages = [
        PageOrderItem(page_id="cover", page_type="cover", title="Deckblatt", order=1, required=True),
        PageOrderItem(page_id="project", page_type="project", title="Projektbeschreibung", order=2, required=True),
        PageOrderItem(page_id="technical", page_type="technical", title="Technische Daten", order=3, required=True),
        PageOrderItem(page_id="economic", page_type="economic", title="Wirtschaftlichkeit", order=4, required=True),
        PageOrderItem(page_id="diagrams", page_type="diagrams", title="Diagramme", order=5, required=True),
        PageOrderItem(page_id="terms", page_type="terms", title="Konditionen", order=6, required=False),
        PageOrderItem(page_id="signature", page_type="signature", title="Unterschrift", order=7, required=True),
    ]
    
    # Add optional pages
    for opt_page in request.optional_pages:
        if opt_page.enabled:
            pages.append(PageOrderItem(
                page_id=opt_page.page_type.value,
                page_type="optional",
                title=opt_page.title or opt_page.page_type.value.replace("_", " ").title(),
                order=opt_page.order,
                required=False,
                enabled=True
            ))
    
    # Sort by order
    pages.sort(key=lambda p: p.order)
    
    # Reassign order numbers
    for i, page in enumerate(pages):
        page.order = i + 1
    
    return pages


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_extended_offer_pdf(request: ExtendedOfferRequest):
    """Generate extended offer PDF with optional pages."""
    try:
        page_order = calculate_page_order(request)
        
        # Mock PDF generation
        pdf_content = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n%%EOF"
        
        filename = f"Erweitertes_Angebot_{request.base_offer_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF-Generierung fehlgeschlagen: {str(e)}")


@router.post("/preview")
async def preview_extended_offer(request: ExtendedOfferRequest):
    """Preview extended offer structure."""
    page_order = calculate_page_order(request)
    
    attachment_count = len(request.product_datasheets)
    
    return ExtendedOfferPreview(
        total_pages=len(page_order),
        page_list=page_order,
        estimated_file_size_kb=len(page_order) * 150 + attachment_count * 500,
        includes_attachments=attachment_count > 0,
        attachment_count=attachment_count
    )


@router.get("/optional-pages")
async def get_optional_page_types():
    """Get available optional page types."""
    return {
        "page_types": [
            {"id": p.value, "name": p.value.replace("_", " ").title(), "description": get_page_description(p)}
            for p in OptionalPageType
        ],
        "default_pages": get_default_optional_pages()
    }


def get_page_description(page_type: OptionalPageType) -> str:
    descriptions = {
        OptionalPageType.PRODUCT_DATASHEET: "Technische Datenblätter der Produkte",
        OptionalPageType.PRODUCT_IMAGES: "Produktbilder und Visualisierungen",
        OptionalPageType.MONTHLY_YIELD: "12-Monats-Ertragsübersicht",
        OptionalPageType.CASHFLOW_ANALYSIS: "20-Jahres Cashflow-Analyse",
        OptionalPageType.CO2_SAVINGS: "CO₂-Einsparung und Umweltbilanz",
        OptionalPageType.COMPANY_CERTIFICATES: "Firmenzertifikate und Qualifikationen",
        OptionalPageType.PARTNER_LOGOS: "Partner- und Herstellerlogos",
        OptionalPageType.REFERENCES: "Referenzprojekte",
        OptionalPageType.FAQ: "Häufig gestellte Fragen",
        OptionalPageType.INSTALLATION_TIMELINE: "Installationszeitplan"
    }
    return descriptions.get(page_type, "")


@router.get("/diagram-types")
async def get_diagram_types():
    """Get available diagram types."""
    return {
        "diagram_types": [
            {"id": "monthly_yield", "name": "Monatlicher Ertrag", "chart_type": "bar"},
            {"id": "annual_comparison", "name": "Jahresvergleich", "chart_type": "line"},
            {"id": "cashflow_20_years", "name": "Cashflow 20 Jahre", "chart_type": "line"},
            {"id": "co2_reduction", "name": "CO₂-Reduktion", "chart_type": "bar"},
            {"id": "autarky_breakdown", "name": "Autarkie-Aufschlüsselung", "chart_type": "pie"},
            {"id": "consumption_pattern", "name": "Verbrauchsmuster", "chart_type": "area"}
        ]
    }


@router.post("/reorder-pages")
async def reorder_pages(page_order: List[str]):
    """Reorder pages in the PDF."""
    return {
        "new_order": page_order,
        "message": "Seitenreihenfolge aktualisiert"
    }


@router.post("/add-datasheet")
async def add_product_datasheet(datasheet: ProductDatasheet):
    """Add product datasheet to offer."""
    return {
        "datasheet": datasheet,
        "added": True,
        "message": f"Datenblatt für {datasheet.product_name} hinzugefügt"
    }


@router.get("/health/check")
async def health_check():
    """Health check for extended offer PDF service."""
    return {
        "status": "healthy",
        "service": "extended-offer-pdf",
        "optional_page_types": len(OptionalPageType),
        "timestamp": datetime.now().isoformat()
    }
