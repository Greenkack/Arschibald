"""
Database Management API

Provides REST API for database management:
- Customer database (CRM)
- Company database
- Product database (PV & WP)
- Tariff database
- Data import/export
- Backup and restore

Requirements: funktionen.txt - "Kundendatenbank", "Firmendatenbank", "Produktdatenbank", "Tarifdatenbank"
Tasks: 285-288. Database Management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import uuid

router = APIRouter(prefix="/database", tags=["Database Management"])


# ==================== Enums ====================

class CustomerStatus(str, Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    INACTIVE = "inactive"


class ProductCategory(str, Enum):
    PV_MODULE = "pv_module"
    INVERTER = "inverter"
    BATTERY = "battery"
    HEATPUMP = "heatpump"
    WALLBOX = "wallbox"
    MOUNTING = "mounting"
    ACCESSORY = "accessory"


class TariffType(str, Enum):
    ELECTRICITY = "electricity"
    FEED_IN = "feed_in"
    GAS = "gas"
    OIL = "oil"


# ==================== Pydantic Models ====================

# Customer Models
class CustomerAddress(BaseModel):
    """Customer address"""
    street: str
    house_number: str
    postal_code: str
    city: str
    country: str = "Deutschland"


class Customer(BaseModel):
    """Customer data"""
    id: str
    salutation: str = "Herr"
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[CustomerAddress] = None
    status: CustomerStatus = CustomerStatus.LEAD
    source: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class CustomerCreate(BaseModel):
    """Customer creation data"""
    salutation: str = "Herr"
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[CustomerAddress] = None
    status: CustomerStatus = CustomerStatus.LEAD
    source: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []


# Company Models
class CompanyContact(BaseModel):
    """Company contact person"""
    name: str
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class Company(BaseModel):
    """Company data"""
    id: str
    name: str
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[CustomerAddress] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    contacts: List[CompanyContact] = []
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class CompanyCreate(BaseModel):
    """Company creation data"""
    name: str
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[CustomerAddress] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    contacts: List[CompanyContact] = []


# Product Models
class ProductSpecification(BaseModel):
    """Product specification"""
    key: str
    value: str
    unit: Optional[str] = None


class Product(BaseModel):
    """Product data"""
    id: str
    category: ProductCategory
    manufacturer: str
    model: str
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "EUR"
    specifications: List[ProductSpecification] = []
    image_url: Optional[str] = None
    datasheet_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class ProductCreate(BaseModel):
    """Product creation data"""
    category: ProductCategory
    manufacturer: str
    model: str
    name: str
    description: Optional[str] = None
    price: float
    specifications: List[ProductSpecification] = []


# Tariff Models
class Tariff(BaseModel):
    """Tariff data"""
    id: str
    tariff_type: TariffType
    name: str
    provider: Optional[str] = None
    price_per_unit: float
    unit: str
    valid_from: date
    valid_until: Optional[date] = None
    region: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class TariffCreate(BaseModel):
    """Tariff creation data"""
    tariff_type: TariffType
    name: str
    provider: Optional[str] = None
    price_per_unit: float
    unit: str
    valid_from: date
    valid_until: Optional[date] = None
    region: Optional[str] = None
    notes: Optional[str] = None


# ==================== Data Storage ====================

_customers: Dict[str, Customer] = {}
_companies: Dict[str, Company] = {}
_products: Dict[str, Product] = {}
_tariffs: Dict[str, Tariff] = {}


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# Initialize sample data
def init_sample_data():
    """Initialize sample data."""
    # Sample customers
    _customers["cust_001"] = Customer(
        id="cust_001",
        salutation="Herr",
        first_name="Max",
        last_name="Mustermann",
        email="max.mustermann@example.com",
        phone="0123 456789",
        address=CustomerAddress(
            street="Musterstraße",
            house_number="1",
            postal_code="12345",
            city="Musterstadt"
        ),
        status=CustomerStatus.CUSTOMER,
        source="Website",
        tags=["PV", "Interesse Speicher"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Sample companies
    _companies["comp_001"] = Company(
        id="comp_001",
        name="Solar GmbH",
        legal_form="GmbH",
        address=CustomerAddress(
            street="Solarweg",
            house_number="10",
            postal_code="54321",
            city="Solarstadt"
        ),
        email="info@solar-gmbh.de",
        phone="0800 123456",
        website="https://solar-gmbh.de",
        contacts=[
            CompanyContact(name="Hans Müller", position="Geschäftsführer", email="mueller@solar-gmbh.de")
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Sample products
    _products["prod_001"] = Product(
        id="prod_001",
        category=ProductCategory.PV_MODULE,
        manufacturer="Trina Solar",
        model="TSM-430NEG9R.28",
        name="Trina Vertex S+ 430W",
        description="Hochleistungs-Solarmodul mit n-type TOPCon Technologie",
        price=189.00,
        specifications=[
            ProductSpecification(key="Leistung", value="430", unit="Wp"),
            ProductSpecification(key="Wirkungsgrad", value="21.8", unit="%"),
            ProductSpecification(key="Abmessungen", value="1762x1134x30", unit="mm"),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _products["prod_002"] = Product(
        id="prod_002",
        category=ProductCategory.INVERTER,
        manufacturer="Fronius",
        model="Symo GEN24 10.0 Plus",
        name="Fronius Symo GEN24 10.0 Plus",
        description="Hybrid-Wechselrichter mit Notstromfunktion",
        price=2890.00,
        specifications=[
            ProductSpecification(key="AC-Leistung", value="10", unit="kW"),
            ProductSpecification(key="Max. DC-Leistung", value="15", unit="kW"),
            ProductSpecification(key="Wirkungsgrad", value="98.0", unit="%"),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _products["prod_003"] = Product(
        id="prod_003",
        category=ProductCategory.BATTERY,
        manufacturer="BYD",
        model="HVS 10.2",
        name="BYD Battery-Box Premium HVS 10.2",
        description="Hochvolt-Batteriespeicher",
        price=6500.00,
        specifications=[
            ProductSpecification(key="Kapazität", value="10.2", unit="kWh"),
            ProductSpecification(key="Spannung", value="409", unit="V"),
            ProductSpecification(key="Zyklen", value="10000", unit=""),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Sample tariffs
    _tariffs["tariff_001"] = Tariff(
        id="tariff_001",
        tariff_type=TariffType.ELECTRICITY,
        name="Grundversorgung",
        provider="Stadtwerke",
        price_per_unit=0.32,
        unit="kWh",
        valid_from=date(2024, 1, 1),
        created_at=datetime.now()
    )
    
    _tariffs["tariff_002"] = Tariff(
        id="tariff_002",
        tariff_type=TariffType.FEED_IN,
        name="EEG Einspeisevergütung 2024",
        price_per_unit=0.082,
        unit="kWh",
        valid_from=date(2024, 1, 1),
        notes="Für Anlagen bis 10 kWp",
        created_at=datetime.now()
    )


init_sample_data()


# ==================== Customer Endpoints ====================

@router.get("/customers")
async def get_customers(
    status: Optional[CustomerStatus] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get customers with filtering."""
    customers = list(_customers.values())
    
    if status:
        customers = [c for c in customers if c.status == status]
    
    if search:
        search_lower = search.lower()
        customers = [c for c in customers if 
                    search_lower in c.first_name.lower() or
                    search_lower in c.last_name.lower() or
                    (c.email and search_lower in c.email.lower())]
    
    total = len(customers)
    customers = customers[offset:offset + limit]
    
    return {
        "customers": customers,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer by ID."""
    if customer_id not in _customers:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return {"customer": _customers[customer_id]}


@router.post("/customers")
async def create_customer(customer: CustomerCreate):
    """Create new customer."""
    customer_id = generate_id("cust")
    new_customer = Customer(
        id=customer_id,
        **customer.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _customers[customer_id] = new_customer
    return {"customer": new_customer, "created": True}


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, customer: CustomerCreate):
    """Update customer."""
    if customer_id not in _customers:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    
    existing = _customers[customer_id]
    updated = Customer(
        id=customer_id,
        **customer.dict(),
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    _customers[customer_id] = updated
    return {"customer": updated, "updated": True}


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete customer."""
    if customer_id not in _customers:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    del _customers[customer_id]
    return {"deleted": True, "customer_id": customer_id}


# ==================== Company Endpoints ====================

@router.get("/companies")
async def get_companies(
    search: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50
):
    """Get companies."""
    companies = list(_companies.values())
    
    if active_only:
        companies = [c for c in companies if c.is_active]
    
    if search:
        search_lower = search.lower()
        companies = [c for c in companies if search_lower in c.name.lower()]
    
    return {
        "companies": companies[:limit],
        "total": len(companies)
    }


@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Get company by ID."""
    if company_id not in _companies:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    return {"company": _companies[company_id]}


@router.post("/companies")
async def create_company(company: CompanyCreate):
    """Create new company."""
    company_id = generate_id("comp")
    new_company = Company(
        id=company_id,
        **company.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _companies[company_id] = new_company
    return {"company": new_company, "created": True}


@router.put("/companies/{company_id}")
async def update_company(company_id: str, company: CompanyCreate):
    """Update company."""
    if company_id not in _companies:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    
    existing = _companies[company_id]
    updated = Company(
        id=company_id,
        **company.dict(),
        logo_url=existing.logo_url,
        is_active=existing.is_active,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    _companies[company_id] = updated
    return {"company": updated, "updated": True}


@router.delete("/companies/{company_id}")
async def delete_company(company_id: str):
    """Delete company."""
    if company_id not in _companies:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    del _companies[company_id]
    return {"deleted": True, "company_id": company_id}


# ==================== Product Endpoints ====================

@router.get("/products")
async def get_products(
    category: Optional[ProductCategory] = None,
    manufacturer: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    limit: int = 100
):
    """Get products with filtering."""
    products = list(_products.values())
    
    if active_only:
        products = [p for p in products if p.is_active]
    
    if category:
        products = [p for p in products if p.category == category]
    
    if manufacturer:
        products = [p for p in products if p.manufacturer.lower() == manufacturer.lower()]
    
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
                   search_lower in p.name.lower() or
                   search_lower in p.manufacturer.lower() or
                   search_lower in p.model.lower()]
    
    return {
        "products": products[:limit],
        "total": len(products)
    }


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID."""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return {"product": _products[product_id]}


@router.post("/products")
async def create_product(product: ProductCreate):
    """Create new product."""
    product_id = generate_id("prod")
    new_product = Product(
        id=product_id,
        **product.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    _products[product_id] = new_product
    return {"product": new_product, "created": True}


@router.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductCreate):
    """Update product."""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    existing = _products[product_id]
    updated = Product(
        id=product_id,
        **product.dict(),
        image_url=existing.image_url,
        datasheet_url=existing.datasheet_url,
        is_active=existing.is_active,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    _products[product_id] = updated
    return {"product": updated, "updated": True}


@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product."""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    del _products[product_id]
    return {"deleted": True, "product_id": product_id}


@router.get("/products/categories/list")
async def get_product_categories():
    """Get product categories with counts."""
    categories = {}
    for cat in ProductCategory:
        count = len([p for p in _products.values() if p.category == cat and p.is_active])
        categories[cat.value] = {
            "name": cat.value,
            "count": count
        }
    return {"categories": categories}


@router.get("/products/manufacturers/list")
async def get_manufacturers(category: Optional[ProductCategory] = None):
    """Get manufacturers list."""
    products = list(_products.values())
    if category:
        products = [p for p in products if p.category == category]
    
    manufacturers = list(set(p.manufacturer for p in products))
    return {"manufacturers": sorted(manufacturers)}


# ==================== Tariff Endpoints ====================

@router.get("/tariffs")
async def get_tariffs(
    tariff_type: Optional[TariffType] = None,
    active_only: bool = True,
    limit: int = 50
):
    """Get tariffs."""
    tariffs = list(_tariffs.values())
    
    if active_only:
        tariffs = [t for t in tariffs if t.is_active]
    
    if tariff_type:
        tariffs = [t for t in tariffs if t.tariff_type == tariff_type]
    
    return {
        "tariffs": tariffs[:limit],
        "total": len(tariffs)
    }


@router.get("/tariffs/{tariff_id}")
async def get_tariff(tariff_id: str):
    """Get tariff by ID."""
    if tariff_id not in _tariffs:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")
    return {"tariff": _tariffs[tariff_id]}


@router.post("/tariffs")
async def create_tariff(tariff: TariffCreate):
    """Create new tariff."""
    tariff_id = generate_id("tariff")
    new_tariff = Tariff(
        id=tariff_id,
        **tariff.dict(),
        created_at=datetime.now()
    )
    _tariffs[tariff_id] = new_tariff
    return {"tariff": new_tariff, "created": True}


@router.put("/tariffs/{tariff_id}")
async def update_tariff(tariff_id: str, tariff: TariffCreate):
    """Update tariff."""
    if tariff_id not in _tariffs:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")
    
    existing = _tariffs[tariff_id]
    updated = Tariff(
        id=tariff_id,
        **tariff.dict(),
        is_active=existing.is_active,
        created_at=existing.created_at
    )
    _tariffs[tariff_id] = updated
    return {"tariff": updated, "updated": True}


@router.delete("/tariffs/{tariff_id}")
async def delete_tariff(tariff_id: str):
    """Delete tariff."""
    if tariff_id not in _tariffs:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")
    del _tariffs[tariff_id]
    return {"deleted": True, "tariff_id": tariff_id}


@router.get("/tariffs/current/{tariff_type}")
async def get_current_tariff(tariff_type: TariffType):
    """Get current active tariff for type."""
    today = date.today()
    tariffs = [t for t in _tariffs.values() 
               if t.tariff_type == tariff_type 
               and t.is_active 
               and t.valid_from <= today
               and (t.valid_until is None or t.valid_until >= today)]
    
    if not tariffs:
        raise HTTPException(status_code=404, detail="Kein aktiver Tarif gefunden")
    
    # Return most recent
    tariffs.sort(key=lambda t: t.valid_from, reverse=True)
    return {"tariff": tariffs[0]}


# ==================== Export/Import Endpoints ====================

@router.get("/export/{entity_type}")
async def export_data(entity_type: str, format: str = "json"):
    """Export database data."""
    if entity_type == "customers":
        data = [c.dict() for c in _customers.values()]
    elif entity_type == "companies":
        data = [c.dict() for c in _companies.values()]
    elif entity_type == "products":
        data = [p.dict() for p in _products.values()]
    elif entity_type == "tariffs":
        data = [t.dict() for t in _tariffs.values()]
    else:
        raise HTTPException(status_code=400, detail="Unbekannter Entity-Typ")
    
    return {
        "entity_type": entity_type,
        "format": format,
        "count": len(data),
        "data": data,
        "exported_at": datetime.now().isoformat()
    }


@router.get("/statistics")
async def get_database_statistics():
    """Get database statistics."""
    return {
        "customers": {
            "total": len(_customers),
            "by_status": {
                status.value: len([c for c in _customers.values() if c.status == status])
                for status in CustomerStatus
            }
        },
        "companies": {
            "total": len(_companies),
            "active": len([c for c in _companies.values() if c.is_active])
        },
        "products": {
            "total": len(_products),
            "active": len([p for p in _products.values() if p.is_active]),
            "by_category": {
                cat.value: len([p for p in _products.values() if p.category == cat])
                for cat in ProductCategory
            }
        },
        "tariffs": {
            "total": len(_tariffs),
            "active": len([t for t in _tariffs.values() if t.is_active]),
            "by_type": {
                tt.value: len([t for t in _tariffs.values() if t.tariff_type == tt])
                for tt in TariffType
            }
        }
    }


@router.get("/health/check")
async def health_check():
    """Health check for database service."""
    return {
        "status": "healthy",
        "service": "database-management",
        "customers": len(_customers),
        "companies": len(_companies),
        "products": len(_products),
        "tariffs": len(_tariffs),
        "timestamp": datetime.now().isoformat()
    }
