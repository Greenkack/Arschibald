"""
Standard Offer PDF (7-8 Pages) API

Provides REST API for generating standard offer PDFs:
- 7-8 page standard offer PDF
- Cover page with customer data
- Project description page
- Technical data overview page
- Economic analysis page
- Diagram page (yield, autarky)
- Closing page with signature field

Requirements: funktionen.txt - "Standard-Angebot"
Task: 265. Standard Offer PDF (7-8 Pages)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import io
import uuid

router = APIRouter(prefix="/pdf/standard-offer", tags=["Standard Offer PDF"])


# ==================== Enums ====================

class OfferType(str, Enum):
    PV_ONLY = "pv_only"
    HEATPUMP_ONLY = "heatpump_only"
    COMBINED = "combined"


class PageType(str, Enum):
    COVER = "cover"
    PROJECT_DESCRIPTION = "project_description"
    TECHNICAL_DATA = "technical_data"
    ECONOMIC_ANALYSIS = "economic_analysis"
    DIAGRAMS = "diagrams"
    TERMS = "terms"
    SIGNATURE = "signature"


# ==================== Pydantic Models ====================

class CustomerData(BaseModel):
    """Customer data for offer"""
    salutation: str = "Herr"
    first_name: str
    last_name: str
    company: Optional[str] = None
    street: str
    postal_code: str
    city: str
    email: Optional[str] = None
    phone: Optional[str] = None


class ProjectLocation(BaseModel):
    """Project location data"""
    street: str
    postal_code: str
    city: str
    building_type: str = "Einfamilienhaus"
    roof_type: str = "Satteldach"
    roof_orientation: str = "Süd"
    roof_tilt: float = 30


class PVSystemData(BaseModel):
    """PV system technical data"""
    module_manufacturer: str
    module_model: str
    module_power_wp: int
    module_count: int
    system_power_kwp: float
    inverter_manufacturer: str
    inverter_model: str
    inverter_power_kw: float
    battery_manufacturer: Optional[str] = None
    battery_model: Optional[str] = None
    battery_capacity_kwh: Optional[float] = None
    mounting_system: str = "Aufdach"
    cable_length_m: float = 50


class HeatPumpData(BaseModel):
    """Heat pump technical data"""
    manufacturer: str
    model: str
    heating_power_kw: float
    cop: float
    energy_class: str = "A++"
    refrigerant: str = "R290"
    noise_level_db: float = 45
    hot_water_tank_l: Optional[int] = None


class EconomicData(BaseModel):
    """Economic analysis data"""
    total_investment_eur: float
    annual_yield_kwh: float
    self_consumption_percent: float
    feed_in_percent: float
    electricity_price_eur_kwh: float = 0.30
    feed_in_tariff_eur_kwh: float = 0.082
    annual_savings_eur: float
    payback_years: float
    roi_20_years_percent: float
    co2_savings_kg_year: float
    subsidies_eur: float = 0


class DiagramData(BaseModel):
    """Data for diagrams"""
    monthly_yield_kwh: List[float]
    monthly_consumption_kwh: List[float]
    monthly_self_consumption_kwh: List[float]
    monthly_feed_in_kwh: List[float]
    autarky_percent: float
    self_consumption_rate_percent: float


class CompanyBranding(BaseModel):
    """Company branding for PDF"""
    company_name: str
    logo_url: Optional[str] = None
    address: str
    phone: str
    email: str
    website: Optional[str] = None
    tax_id: Optional[str] = None
    bank_details: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"


class StandardOfferRequest(BaseModel):
    """Request for standard offer PDF"""
    offer_number: Optional[str] = None
    offer_type: OfferType = OfferType.PV_ONLY
    customer: CustomerData
    project_location: ProjectLocation
    pv_system: Optional[PVSystemData] = None
    heat_pump: Optional[HeatPumpData] = None
    economic_data: EconomicData
    diagram_data: Optional[DiagramData] = None
    branding: Optional[CompanyBranding] = None
    validity_days: int = 30
    payment_terms: str = "50% bei Auftragserteilung, 50% nach Fertigstellung"
    notes: Optional[str] = None
    include_terms: bool = True


class PageContent(BaseModel):
    """Content for a single PDF page"""
    page_number: int
    page_type: PageType
    title: str
    content: Dict[str, Any]


class OfferPDFMetadata(BaseModel):
    """Metadata for generated PDF"""
    offer_id: str
    offer_number: str
    generated_at: datetime
    page_count: int
    file_size_bytes: int
    customer_name: str
    total_value_eur: float


# ==================== Helper Functions ====================

def generate_offer_number() -> str:
    """Generate unique offer number"""
    return f"ANG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_cover_page(request: StandardOfferRequest) -> PageContent:
    """Generate cover page content"""
    return PageContent(
        page_number=1,
        page_type=PageType.COVER,
        title="Angebot",
        content={
            "offer_number": request.offer_number,
            "date": datetime.now().strftime("%d.%m.%Y"),
            "validity_until": (datetime.now().replace(day=1) + 
                             __import__('datetime').timedelta(days=request.validity_days)).strftime("%d.%m.%Y"),
            "customer": {
                "salutation": request.customer.salutation,
                "name": f"{request.customer.first_name} {request.customer.last_name}",
                "company": request.customer.company,
                "address": f"{request.customer.street}, {request.customer.postal_code} {request.customer.city}"
            },
            "project_address": f"{request.project_location.street}, {request.project_location.postal_code} {request.project_location.city}",
            "offer_type": request.offer_type.value,
            "headline": get_offer_headline(request.offer_type),
            "intro_text": "Vielen Dank für Ihr Interesse an einer nachhaltigen Energielösung. Gerne unterbreiten wir Ihnen folgendes Angebot:"
        }
    )


def get_offer_headline(offer_type: OfferType) -> str:
    """Get headline based on offer type"""
    headlines = {
        OfferType.PV_ONLY: "Photovoltaikanlage",
        OfferType.HEATPUMP_ONLY: "Wärmepumpenanlage",
        OfferType.COMBINED: "Solar- und Wärmepumpenlösung"
    }
    return headlines.get(offer_type, "Energielösung")


def generate_project_description_page(request: StandardOfferRequest) -> PageContent:
    """Generate project description page"""
    return PageContent(
        page_number=2,
        page_type=PageType.PROJECT_DESCRIPTION,
        title="Projektbeschreibung",
        content={
            "location": {
                "address": f"{request.project_location.street}, {request.project_location.postal_code} {request.project_location.city}",
                "building_type": request.project_location.building_type,
                "roof_type": request.project_location.roof_type,
                "roof_orientation": request.project_location.roof_orientation,
                "roof_tilt": f"{request.project_location.roof_tilt}°"
            },
            "scope": get_project_scope(request),
            "benefits": get_project_benefits(request.offer_type)
        }
    )


def get_project_scope(request: StandardOfferRequest) -> List[str]:
    """Get project scope items"""
    scope = []
    if request.pv_system:
        scope.extend([
            f"Photovoltaikanlage mit {request.pv_system.system_power_kwp} kWp Leistung",
            f"{request.pv_system.module_count} Solarmodule {request.pv_system.module_manufacturer} {request.pv_system.module_model}",
            f"Wechselrichter {request.pv_system.inverter_manufacturer} {request.pv_system.inverter_model}"
        ])
        if request.pv_system.battery_capacity_kwh:
            scope.append(f"Batteriespeicher {request.pv_system.battery_manufacturer} {request.pv_system.battery_capacity_kwh} kWh")
    if request.heat_pump:
        scope.extend([
            f"Wärmepumpe {request.heat_pump.manufacturer} {request.heat_pump.model}",
            f"Heizleistung {request.heat_pump.heating_power_kw} kW"
        ])
    scope.extend([
        "Komplette Montage und Installation",
        "Inbetriebnahme und Einweisung",
        "Anmeldung beim Netzbetreiber"
    ])
    return scope


def get_project_benefits(offer_type: OfferType) -> List[str]:
    """Get project benefits"""
    benefits = [
        "Unabhängigkeit von steigenden Energiepreisen",
        "Aktiver Beitrag zum Klimaschutz",
        "Wertsteigerung Ihrer Immobilie"
    ]
    if offer_type in [OfferType.PV_ONLY, OfferType.COMBINED]:
        benefits.append("Eigenstromproduktion und Einspeisevergütung")
    if offer_type in [OfferType.HEATPUMP_ONLY, OfferType.COMBINED]:
        benefits.append("Effiziente und umweltfreundliche Heizung")
    return benefits


def generate_technical_data_page(request: StandardOfferRequest) -> PageContent:
    """Generate technical data page"""
    tech_data = {}
    
    if request.pv_system:
        tech_data["pv_system"] = {
            "title": "Photovoltaikanlage",
            "items": [
                {"label": "Anlagenleistung", "value": f"{request.pv_system.system_power_kwp} kWp"},
                {"label": "Module", "value": f"{request.pv_system.module_count}x {request.pv_system.module_manufacturer} {request.pv_system.module_model}"},
                {"label": "Modulleistung", "value": f"{request.pv_system.module_power_wp} Wp"},
                {"label": "Wechselrichter", "value": f"{request.pv_system.inverter_manufacturer} {request.pv_system.inverter_model}"},
                {"label": "WR-Leistung", "value": f"{request.pv_system.inverter_power_kw} kW"},
                {"label": "Montagesystem", "value": request.pv_system.mounting_system}
            ]
        }
        if request.pv_system.battery_capacity_kwh:
            tech_data["battery"] = {
                "title": "Batteriespeicher",
                "items": [
                    {"label": "Hersteller", "value": request.pv_system.battery_manufacturer},
                    {"label": "Modell", "value": request.pv_system.battery_model},
                    {"label": "Kapazität", "value": f"{request.pv_system.battery_capacity_kwh} kWh"}
                ]
            }
    
    if request.heat_pump:
        tech_data["heat_pump"] = {
            "title": "Wärmepumpe",
            "items": [
                {"label": "Hersteller", "value": request.heat_pump.manufacturer},
                {"label": "Modell", "value": request.heat_pump.model},
                {"label": "Heizleistung", "value": f"{request.heat_pump.heating_power_kw} kW"},
                {"label": "COP", "value": str(request.heat_pump.cop)},
                {"label": "Energieeffizienzklasse", "value": request.heat_pump.energy_class},
                {"label": "Kältemittel", "value": request.heat_pump.refrigerant},
                {"label": "Schallleistung", "value": f"{request.heat_pump.noise_level_db} dB(A)"}
            ]
        }
    
    return PageContent(
        page_number=3,
        page_type=PageType.TECHNICAL_DATA,
        title="Technische Daten",
        content=tech_data
    )


def generate_economic_analysis_page(request: StandardOfferRequest) -> PageContent:
    """Generate economic analysis page"""
    eco = request.economic_data
    
    return PageContent(
        page_number=4,
        page_type=PageType.ECONOMIC_ANALYSIS,
        title="Wirtschaftlichkeitsanalyse",
        content={
            "investment": {
                "title": "Investition",
                "total": f"{eco.total_investment_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."),
                "subsidies": f"{eco.subsidies_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".") if eco.subsidies_eur > 0 else None,
                "net_investment": f"{eco.total_investment_eur - eco.subsidies_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            },
            "yield": {
                "title": "Ertrag & Verbrauch",
                "annual_yield": f"{eco.annual_yield_kwh:,.0f} kWh/Jahr".replace(",", "."),
                "self_consumption": f"{eco.self_consumption_percent:.1f}%",
                "feed_in": f"{eco.feed_in_percent:.1f}%"
            },
            "savings": {
                "title": "Einsparungen",
                "annual_savings": f"{eco.annual_savings_eur:,.2f} €/Jahr".replace(",", "X").replace(".", ",").replace("X", "."),
                "electricity_price": f"{eco.electricity_price_eur_kwh:.2f} €/kWh".replace(".", ","),
                "feed_in_tariff": f"{eco.feed_in_tariff_eur_kwh:.3f} €/kWh".replace(".", ",")
            },
            "profitability": {
                "title": "Rentabilität",
                "payback_period": f"{eco.payback_years:.1f} Jahre".replace(".", ","),
                "roi_20_years": f"{eco.roi_20_years_percent:.1f}%".replace(".", ","),
                "co2_savings": f"{eco.co2_savings_kg_year:,.0f} kg CO₂/Jahr".replace(",", ".")
            },
            "summary_text": f"Mit einer Amortisationszeit von {eco.payback_years:.1f} Jahren und einer Rendite von {eco.roi_20_years_percent:.1f}% über 20 Jahre ist diese Investition wirtschaftlich sehr attraktiv."
        }
    )


def generate_diagrams_page(request: StandardOfferRequest) -> PageContent:
    """Generate diagrams page"""
    diagram_data = request.diagram_data
    
    if not diagram_data:
        # Generate mock data if not provided
        diagram_data = DiagramData(
            monthly_yield_kwh=[300, 450, 700, 900, 1100, 1200, 1150, 1000, 800, 550, 350, 250],
            monthly_consumption_kwh=[400, 380, 350, 320, 300, 280, 290, 300, 330, 370, 390, 420],
            monthly_self_consumption_kwh=[250, 300, 320, 300, 290, 270, 280, 290, 310, 340, 300, 240],
            monthly_feed_in_kwh=[50, 150, 380, 600, 810, 930, 870, 710, 490, 210, 50, 10],
            autarky_percent=65,
            self_consumption_rate_percent=35
        )
    
    months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    return PageContent(
        page_number=5,
        page_type=PageType.DIAGRAMS,
        title="Ertrags- und Verbrauchsdiagramme",
        content={
            "yield_chart": {
                "title": "Monatlicher Ertrag und Verbrauch",
                "type": "bar",
                "labels": months,
                "datasets": [
                    {"label": "PV-Ertrag", "data": diagram_data.monthly_yield_kwh, "color": "#F59E0B"},
                    {"label": "Verbrauch", "data": diagram_data.monthly_consumption_kwh, "color": "#3B82F6"}
                ]
            },
            "autarky_chart": {
                "title": "Autarkiegrad",
                "type": "donut",
                "value": diagram_data.autarky_percent,
                "label": "Autarkie",
                "description": f"{diagram_data.autarky_percent}% Ihres Strombedarfs decken Sie selbst"
            },
            "self_consumption_chart": {
                "title": "Eigenverbrauchsquote",
                "type": "donut",
                "value": diagram_data.self_consumption_rate_percent,
                "label": "Eigenverbrauch",
                "description": f"{diagram_data.self_consumption_rate_percent}% des erzeugten Stroms nutzen Sie selbst"
            },
            "energy_flow": {
                "title": "Energiefluss",
                "total_yield": sum(diagram_data.monthly_yield_kwh),
                "self_consumption": sum(diagram_data.monthly_self_consumption_kwh),
                "feed_in": sum(diagram_data.monthly_feed_in_kwh),
                "grid_purchase": sum(diagram_data.monthly_consumption_kwh) - sum(diagram_data.monthly_self_consumption_kwh)
            }
        }
    )


def generate_terms_page(request: StandardOfferRequest) -> PageContent:
    """Generate terms and conditions page"""
    return PageContent(
        page_number=6,
        page_type=PageType.TERMS,
        title="Konditionen und Leistungen",
        content={
            "price": {
                "title": "Preis",
                "total": f"{request.economic_data.total_investment_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."),
                "includes_vat": True,
                "vat_rate": "19%"
            },
            "payment_terms": {
                "title": "Zahlungsbedingungen",
                "terms": request.payment_terms
            },
            "validity": {
                "title": "Gültigkeit",
                "days": request.validity_days,
                "text": f"Dieses Angebot ist {request.validity_days} Tage gültig."
            },
            "included_services": [
                "Lieferung aller Komponenten frei Haus",
                "Fachgerechte Montage durch zertifizierte Installateure",
                "Elektrische Installation und Anschluss",
                "Inbetriebnahme und Funktionsprüfung",
                "Einweisung in die Bedienung",
                "Anmeldung beim Netzbetreiber",
                "Dokumentation und Übergabe"
            ],
            "warranty": {
                "title": "Garantie",
                "items": [
                    "Produktgarantie Module: 12 Jahre",
                    "Leistungsgarantie Module: 25 Jahre (mind. 80%)",
                    "Garantie Wechselrichter: 5 Jahre (erweiterbar)",
                    "Installationsgarantie: 2 Jahre"
                ]
            },
            "notes": request.notes
        }
    )


def generate_signature_page(request: StandardOfferRequest) -> PageContent:
    """Generate signature page"""
    return PageContent(
        page_number=7,
        page_type=PageType.SIGNATURE,
        title="Auftragserteilung",
        content={
            "order_text": "Hiermit erteile ich den Auftrag zur Lieferung und Installation der im Angebot beschriebenen Anlage zu den genannten Konditionen.",
            "customer_signature": {
                "label": "Unterschrift Auftraggeber",
                "name": f"{request.customer.first_name} {request.customer.last_name}",
                "date_field": True,
                "place_field": True
            },
            "company_signature": {
                "label": "Unterschrift Auftragnehmer",
                "date_field": True
            },
            "cancellation_policy": {
                "title": "Widerrufsbelehrung",
                "text": "Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen."
            },
            "data_protection": {
                "title": "Datenschutz",
                "text": "Ihre Daten werden gemäß DSGVO verarbeitet und nicht an Dritte weitergegeben."
            }
        }
    )


def generate_all_pages(request: StandardOfferRequest) -> List[PageContent]:
    """Generate all pages for standard offer"""
    pages = [
        generate_cover_page(request),
        generate_project_description_page(request),
        generate_technical_data_page(request),
        generate_economic_analysis_page(request),
        generate_diagrams_page(request),
    ]
    
    if request.include_terms:
        pages.append(generate_terms_page(request))
    
    pages.append(generate_signature_page(request))
    
    # Update page numbers
    for i, page in enumerate(pages):
        page.page_number = i + 1
    
    return pages


def generate_pdf_bytes(pages: List[PageContent], branding: Optional[CompanyBranding]) -> bytes:
    """Generate PDF bytes from pages (mock implementation)"""
    # In production, use ReportLab or similar library
    pdf_content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count {len(pages)} >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >> endobj
xref
0 4
trailer << /Size 4 /Root 1 0 R >>
startxref
%%EOF
"""
    return pdf_content.encode('utf-8')


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_standard_offer_pdf(request: StandardOfferRequest):
    """Generate standard offer PDF (7-8 pages)."""
    try:
        # Generate offer number if not provided
        if not request.offer_number:
            request.offer_number = generate_offer_number()
        
        # Generate all pages
        pages = generate_all_pages(request)
        
        # Generate PDF bytes
        pdf_bytes = generate_pdf_bytes(pages, request.branding)
        
        # Create filename
        customer_name = f"{request.customer.last_name}_{request.customer.first_name}".replace(" ", "_")
        filename = f"Angebot_{request.offer_number}_{customer_name}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF-Generierung fehlgeschlagen: {str(e)}")


@router.post("/preview")
async def preview_standard_offer(request: StandardOfferRequest):
    """Preview standard offer content without generating PDF."""
    if not request.offer_number:
        request.offer_number = generate_offer_number()
    
    pages = generate_all_pages(request)
    
    return {
        "offer_number": request.offer_number,
        "page_count": len(pages),
        "pages": [{"page_number": p.page_number, "page_type": p.page_type.value, "title": p.title} for p in pages],
        "full_content": pages,
        "metadata": {
            "customer": f"{request.customer.first_name} {request.customer.last_name}",
            "offer_type": request.offer_type.value,
            "total_value": request.economic_data.total_investment_eur,
            "validity_days": request.validity_days
        }
    }


@router.get("/templates")
async def get_offer_templates():
    """Get available offer templates."""
    return {
        "templates": [
            {
                "id": "standard_pv",
                "name": "Standard PV-Angebot",
                "description": "7-seitiges Angebot für Photovoltaikanlagen",
                "pages": 7,
                "offer_type": "pv_only"
            },
            {
                "id": "standard_hp",
                "name": "Standard Wärmepumpen-Angebot",
                "description": "7-seitiges Angebot für Wärmepumpen",
                "pages": 7,
                "offer_type": "heatpump_only"
            },
            {
                "id": "standard_combined",
                "name": "Kombiniertes Angebot",
                "description": "8-seitiges Angebot für PV + Wärmepumpe",
                "pages": 8,
                "offer_type": "combined"
            }
        ]
    }


@router.get("/page-types")
async def get_page_types():
    """Get available page types for standard offer."""
    return {
        "page_types": [
            {"id": "cover", "name": "Deckblatt", "required": True, "order": 1},
            {"id": "project_description", "name": "Projektbeschreibung", "required": True, "order": 2},
            {"id": "technical_data", "name": "Technische Daten", "required": True, "order": 3},
            {"id": "economic_analysis", "name": "Wirtschaftlichkeit", "required": True, "order": 4},
            {"id": "diagrams", "name": "Diagramme", "required": True, "order": 5},
            {"id": "terms", "name": "Konditionen", "required": False, "order": 6},
            {"id": "signature", "name": "Unterschrift", "required": True, "order": 7}
        ]
    }


@router.post("/validate")
async def validate_offer_data(request: StandardOfferRequest):
    """Validate offer data before PDF generation."""
    errors = []
    warnings = []
    
    # Validate customer data
    if not request.customer.first_name or not request.customer.last_name:
        errors.append("Kundenname ist erforderlich")
    if not request.customer.street or not request.customer.postal_code:
        errors.append("Kundenadresse ist erforderlich")
    
    # Validate system data based on offer type
    if request.offer_type in [OfferType.PV_ONLY, OfferType.COMBINED]:
        if not request.pv_system:
            errors.append("PV-Systemdaten sind erforderlich")
        elif request.pv_system.system_power_kwp <= 0:
            errors.append("PV-Leistung muss größer als 0 sein")
    
    if request.offer_type in [OfferType.HEATPUMP_ONLY, OfferType.COMBINED]:
        if not request.heat_pump:
            errors.append("Wärmepumpendaten sind erforderlich")
    
    # Validate economic data
    if request.economic_data.total_investment_eur <= 0:
        errors.append("Investitionssumme muss größer als 0 sein")
    if request.economic_data.payback_years <= 0:
        warnings.append("Amortisationszeit sollte berechnet werden")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "can_generate": len(errors) == 0
    }


@router.get("/sample-data")
async def get_sample_offer_data():
    """Get sample data for testing PDF generation."""
    return {
        "sample_request": {
            "offer_type": "pv_only",
            "customer": {
                "salutation": "Herr",
                "first_name": "Max",
                "last_name": "Mustermann",
                "street": "Musterstraße 123",
                "postal_code": "12345",
                "city": "Musterstadt",
                "email": "max@example.com",
                "phone": "+49 123 456789"
            },
            "project_location": {
                "street": "Musterstraße 123",
                "postal_code": "12345",
                "city": "Musterstadt",
                "building_type": "Einfamilienhaus",
                "roof_type": "Satteldach",
                "roof_orientation": "Süd",
                "roof_tilt": 30
            },
            "pv_system": {
                "module_manufacturer": "SolarTech",
                "module_model": "ST-400M",
                "module_power_wp": 400,
                "module_count": 20,
                "system_power_kwp": 8.0,
                "inverter_manufacturer": "SMA",
                "inverter_model": "Sunny Tripower 8.0",
                "inverter_power_kw": 8.0,
                "battery_manufacturer": "BYD",
                "battery_model": "HVS 10.2",
                "battery_capacity_kwh": 10.2,
                "mounting_system": "Aufdach"
            },
            "economic_data": {
                "total_investment_eur": 18500,
                "annual_yield_kwh": 7600,
                "self_consumption_percent": 65,
                "feed_in_percent": 35,
                "electricity_price_eur_kwh": 0.30,
                "feed_in_tariff_eur_kwh": 0.082,
                "annual_savings_eur": 1850,
                "payback_years": 10.0,
                "roi_20_years_percent": 156,
                "co2_savings_kg_year": 3040
            }
        }
    }


@router.get("/health/check")
async def health_check():
    """Health check for standard offer PDF service."""
    return {
        "status": "healthy",
        "service": "standard-offer-pdf",
        "supported_pages": len(PageType),
        "timestamp": datetime.now().isoformat()
    }
