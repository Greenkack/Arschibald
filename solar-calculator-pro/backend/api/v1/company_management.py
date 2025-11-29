"""
Company and Logo Management API

Provides REST API for company and logo management:
- Multi-company support
- Company profile management
- Logo upload and positioning
- Support up to 6 companies for multi-offers
- Company-specific text templates

Requirements: funktionen.txt - "Firmen- und Logo-Verwaltung"
Task: 275. Company and Logo Management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/admin/companies", tags=["Company Management"])


# ==================== Enums ====================

class LogoPosition(str, Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class CompanyType(str, Enum):
    PRIMARY = "primary"
    PARTNER = "partner"
    SUBSIDIARY = "subsidiary"


# ==================== Pydantic Models ====================

class LogoConfig(BaseModel):
    """Logo configuration"""
    url: str
    position: LogoPosition = LogoPosition.TOP_RIGHT
    width_mm: float = Field(default=40, ge=10, le=100)
    height_mm: Optional[float] = None
    margin_x_mm: float = 15
    margin_y_mm: float = 15
    opacity: float = Field(default=1.0, ge=0, le=1)


class ContactInfo(BaseModel):
    """Company contact information"""
    phone: str
    fax: Optional[str] = None
    email: str
    website: Optional[str] = None
    contact_person: Optional[str] = None


class BankDetails(BaseModel):
    """Company bank details"""
    bank_name: str
    iban: str
    bic: str
    account_holder: Optional[str] = None


class TextTemplate(BaseModel):
    """Company-specific text template"""
    template_id: str
    name: str
    category: str  # "offer", "email", "contract", "footer"
    content: str
    placeholders: List[str] = []


class BrandingConfig(BaseModel):
    """Company branding configuration"""
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    accent_color: str = "#F59E0B"
    font_family: str = "Helvetica"
    header_style: str = "modern"


class Company(BaseModel):
    """Company profile"""
    id: str
    name: str
    company_type: CompanyType = CompanyType.PRIMARY
    legal_name: Optional[str] = None
    address: str
    postal_code: str
    city: str
    country: str = "Deutschland"
    contact: ContactInfo
    tax_id: Optional[str] = None
    vat_id: Optional[str] = None
    registration_number: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    logo: Optional[LogoConfig] = None
    branding: BrandingConfig = BrandingConfig()
    text_templates: List[TextTemplate] = []
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


class CreateCompanyRequest(BaseModel):
    """Request to create company"""
    name: str
    company_type: CompanyType = CompanyType.PRIMARY
    legal_name: Optional[str] = None
    address: str
    postal_code: str
    city: str
    country: str = "Deutschland"
    contact: ContactInfo
    tax_id: Optional[str] = None
    vat_id: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    branding: BrandingConfig = BrandingConfig()


class LogoUploadResult(BaseModel):
    """Logo upload result"""
    company_id: str
    logo_url: str
    width: int
    height: int
    file_size_bytes: int
    uploaded_at: datetime


# ==================== Mock Data Store ====================

_companies_store: Dict[str, Company] = {}
_max_companies = 6


def generate_company_id() -> str:
    return f"comp_{uuid.uuid4().hex[:8]}"


def create_mock_companies():
    """Create mock companies"""
    now = datetime.now()
    
    companies = [
        Company(
            id=generate_company_id(),
            name="SolarTech GmbH",
            company_type=CompanyType.PRIMARY,
            legal_name="SolarTech Energiesysteme GmbH",
            address="Solarstraße 1",
            postal_code="12345",
            city="Sonnenstadt",
            contact=ContactInfo(
                phone="+49 123 456789",
                email="info@solartech.de",
                website="www.solartech.de"
            ),
            tax_id="DE123456789",
            branding=BrandingConfig(primary_color="#F59E0B"),
            logo=LogoConfig(url="/logos/solartech.png", position=LogoPosition.TOP_RIGHT),
            sort_order=1,
            created_at=now, updated_at=now
        ),
        Company(
            id=generate_company_id(),
            name="GreenEnergy Partner",
            company_type=CompanyType.PARTNER,
            address="Grüner Weg 42",
            postal_code="54321",
            city="Ökostadt",
            contact=ContactInfo(
                phone="+49 987 654321",
                email="kontakt@greenenergy.de"
            ),
            branding=BrandingConfig(primary_color="#10B981"),
            sort_order=2,
            created_at=now, updated_at=now
        )
    ]
    
    for c in companies:
        _companies_store[c.id] = c


create_mock_companies()


# ==================== API Endpoints ====================

@router.get("/")
async def get_companies(
    company_type: Optional[CompanyType] = None,
    active_only: bool = True
):
    """Get all companies."""
    companies = list(_companies_store.values())
    
    if company_type:
        companies = [c for c in companies if c.company_type == company_type]
    if active_only:
        companies = [c for c in companies if c.is_active]
    
    companies.sort(key=lambda c: c.sort_order)
    
    return {
        "companies": companies,
        "total": len(companies),
        "max_allowed": _max_companies,
        "can_add_more": len(companies) < _max_companies
    }


@router.post("/")
async def create_company(request: CreateCompanyRequest):
    """Create a new company."""
    if len(_companies_store) >= _max_companies:
        raise HTTPException(status_code=400, detail=f"Maximal {_max_companies} Firmen erlaubt")
    
    company_id = generate_company_id()
    now = datetime.now()
    
    company = Company(
        id=company_id,
        name=request.name,
        company_type=request.company_type,
        legal_name=request.legal_name,
        address=request.address,
        postal_code=request.postal_code,
        city=request.city,
        country=request.country,
        contact=request.contact,
        tax_id=request.tax_id,
        vat_id=request.vat_id,
        bank_details=request.bank_details,
        branding=request.branding,
        sort_order=len(_companies_store) + 1,
        created_at=now,
        updated_at=now
    )
    
    _companies_store[company_id] = company
    
    return {"company": company, "message": "Firma erstellt"}


@router.get("/{company_id}")
async def get_company(company_id: str):
    """Get a specific company."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    return {"company": _companies_store[company_id]}


@router.put("/{company_id}")
async def update_company(company_id: str, request: CreateCompanyRequest):
    """Update a company."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    existing = _companies_store[company_id]
    
    updated = Company(
        id=company_id,
        name=request.name,
        company_type=request.company_type,
        legal_name=request.legal_name,
        address=request.address,
        postal_code=request.postal_code,
        city=request.city,
        country=request.country,
        contact=request.contact,
        tax_id=request.tax_id,
        vat_id=request.vat_id,
        bank_details=request.bank_details,
        logo=existing.logo,
        branding=request.branding,
        text_templates=existing.text_templates,
        is_active=existing.is_active,
        sort_order=existing.sort_order,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    
    _companies_store[company_id] = updated
    
    return {"company": updated, "updated": True}


@router.delete("/{company_id}")
async def delete_company(company_id: str):
    """Delete a company."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    # Check if it's the primary company
    company = _companies_store[company_id]
    if company.company_type == CompanyType.PRIMARY:
        primary_count = len([c for c in _companies_store.values() if c.company_type == CompanyType.PRIMARY])
        if primary_count <= 1:
            raise HTTPException(status_code=400, detail="Mindestens eine Hauptfirma erforderlich")
    
    del _companies_store[company_id]
    return {"deleted": True, "company_id": company_id}


@router.put("/{company_id}/logo")
async def update_logo(company_id: str, logo: LogoConfig):
    """Update company logo configuration."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    _companies_store[company_id].logo = logo
    _companies_store[company_id].updated_at = datetime.now()
    
    return {"company": _companies_store[company_id], "logo_updated": True}


@router.post("/{company_id}/logo/upload")
async def upload_logo(company_id: str, url: str):
    """Upload company logo."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    # Mock upload result
    result = LogoUploadResult(
        company_id=company_id,
        logo_url=url,
        width=400,
        height=200,
        file_size_bytes=45000,
        uploaded_at=datetime.now()
    )
    
    _companies_store[company_id].logo = LogoConfig(url=url)
    _companies_store[company_id].updated_at = datetime.now()
    
    return {"result": result, "company": _companies_store[company_id]}


@router.put("/{company_id}/branding")
async def update_branding(company_id: str, branding: BrandingConfig):
    """Update company branding."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    _companies_store[company_id].branding = branding
    _companies_store[company_id].updated_at = datetime.now()
    
    return {"company": _companies_store[company_id], "branding_updated": True}


@router.get("/{company_id}/templates")
async def get_text_templates(company_id: str, category: Optional[str] = None):
    """Get company text templates."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    templates = _companies_store[company_id].text_templates
    
    if category:
        templates = [t for t in templates if t.category == category]
    
    return {"templates": templates, "total": len(templates)}


@router.post("/{company_id}/templates")
async def add_text_template(company_id: str, template: TextTemplate):
    """Add text template to company."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    _companies_store[company_id].text_templates.append(template)
    _companies_store[company_id].updated_at = datetime.now()
    
    return {"template": template, "added": True}


@router.put("/{company_id}/templates/{template_id}")
async def update_text_template(company_id: str, template_id: str, template: TextTemplate):
    """Update text template."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    company = _companies_store[company_id]
    for i, t in enumerate(company.text_templates):
        if t.template_id == template_id:
            company.text_templates[i] = template
            company.updated_at = datetime.now()
            return {"template": template, "updated": True}
    
    raise HTTPException(status_code=404, detail="Template nicht gefunden")


@router.put("/reorder")
async def reorder_companies(company_ids: List[str]):
    """Reorder companies."""
    for i, company_id in enumerate(company_ids):
        if company_id in _companies_store:
            _companies_store[company_id].sort_order = i + 1
    
    return {"reordered": True, "new_order": company_ids}


@router.put("/{company_id}/activate")
async def activate_company(company_id: str, active: bool):
    """Activate or deactivate company."""
    if company_id not in _companies_store:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    _companies_store[company_id].is_active = active
    _companies_store[company_id].updated_at = datetime.now()
    
    return {"company": _companies_store[company_id], "active": active}


@router.get("/logo-positions")
async def get_logo_positions():
    """Get available logo positions."""
    return {
        "positions": [
            {"id": "top_left", "name": "Oben links"},
            {"id": "top_center", "name": "Oben mittig"},
            {"id": "top_right", "name": "Oben rechts"},
            {"id": "bottom_left", "name": "Unten links"},
            {"id": "bottom_center", "name": "Unten mittig"},
            {"id": "bottom_right", "name": "Unten rechts"}
        ]
    }


@router.get("/template-categories")
async def get_template_categories():
    """Get available template categories."""
    return {
        "categories": [
            {"id": "offer", "name": "Angebot", "description": "Texte für Angebote"},
            {"id": "email", "name": "E-Mail", "description": "E-Mail-Vorlagen"},
            {"id": "contract", "name": "Vertrag", "description": "Vertragstexte"},
            {"id": "footer", "name": "Fußzeile", "description": "Fußzeilentexte"}
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for company management service."""
    return {
        "status": "healthy",
        "service": "company-management",
        "companies_count": len(_companies_store),
        "max_companies": _max_companies,
        "timestamp": datetime.now().isoformat()
    }
