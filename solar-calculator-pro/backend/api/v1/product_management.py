"""
Product and Component Management API

Provides REST API for product and component management:
- Product CRUD operations
- CSV/Excel product import
- Product category management
- Mounting component database (per roof type)
- Product image management

Requirements: funktionen.txt - "Produkt- und Komponentenverwaltung"
Task: 274. Product and Component Management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/admin/products", tags=["Product Management"])


# ==================== Enums ====================

class ProductCategory(str, Enum):
    PV_MODULE = "pv_module"
    INVERTER = "inverter"
    BATTERY = "battery"
    MOUNTING = "mounting"
    CABLE = "cable"
    CONNECTOR = "connector"
    HEATPUMP = "heatpump"
    ACCESSORY = "accessory"


class RoofType(str, Enum):
    PITCHED = "pitched"
    FLAT = "flat"
    METAL = "metal"
    TILE = "tile"
    SLATE = "slate"
    FACADE = "facade"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


# ==================== Pydantic Models ====================

class ProductSpecs(BaseModel):
    """Product specifications"""
    power_w: Optional[int] = None
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None
    efficiency_percent: Optional[float] = None
    weight_kg: Optional[float] = None
    dimensions_mm: Optional[Dict[str, float]] = None
    warranty_years: Optional[int] = None
    custom_specs: Dict[str, Any] = {}


class Product(BaseModel):
    """Product"""
    id: str
    sku: str
    name: str
    manufacturer: str
    category: ProductCategory
    status: ProductStatus = ProductStatus.ACTIVE
    description: Optional[str] = None
    specs: ProductSpecs = ProductSpecs()
    price_net_eur: float
    price_gross_eur: Optional[float] = None
    vat_percent: float = 19.0
    image_urls: List[str] = []
    datasheet_url: Optional[str] = None
    compatible_with: List[str] = []
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class CreateProductRequest(BaseModel):
    """Request to create product"""
    sku: str
    name: str
    manufacturer: str
    category: ProductCategory
    description: Optional[str] = None
    specs: ProductSpecs = ProductSpecs()
    price_net_eur: float
    vat_percent: float = 19.0
    tags: List[str] = []


class MountingComponent(BaseModel):
    """Mounting component for specific roof type"""
    id: str
    name: str
    roof_types: List[RoofType]
    description: Optional[str] = None
    material: str
    price_per_unit_eur: float
    units_per_module: float
    weight_kg: float
    image_url: Optional[str] = None


class ProductCategory_Info(BaseModel):
    """Product category information"""
    id: str
    name: str
    description: str
    product_count: int
    icon: Optional[str] = None


class ImportResult(BaseModel):
    """Import result"""
    total_rows: int
    imported: int
    updated: int
    skipped: int
    errors: List[Dict[str, Any]]


# ==================== Mock Data Store ====================

_products_store: Dict[str, Product] = {}
_mounting_store: Dict[str, MountingComponent] = {}
_product_counter = 1000


def generate_product_id() -> str:
    global _product_counter
    _product_counter += 1
    return f"prod_{_product_counter}"


def generate_sku(category: ProductCategory, manufacturer: str) -> str:
    prefix = category.value[:3].upper()
    mfr = manufacturer[:3].upper()
    return f"{prefix}-{mfr}-{uuid.uuid4().hex[:6].upper()}"


def create_mock_products():
    """Create mock products"""
    now = datetime.now()
    
    products = [
        Product(
            id=generate_product_id(),
            sku="MOD-TRI-001",
            name="Trina Vertex S+ 440W",
            manufacturer="Trina Solar",
            category=ProductCategory.PV_MODULE,
            specs=ProductSpecs(power_w=440, efficiency_percent=21.8, weight_kg=21.0,
                             dimensions_mm={"width": 1134, "height": 1762, "depth": 30}),
            price_net_eur=145.00,
            price_gross_eur=172.55,
            tags=["premium", "monokristallin"],
            created_at=now, updated_at=now
        ),
        Product(
            id=generate_product_id(),
            sku="INV-SMA-001",
            name="SMA Sunny Tripower 10.0",
            manufacturer="SMA",
            category=ProductCategory.INVERTER,
            specs=ProductSpecs(power_w=10000, efficiency_percent=98.0, weight_kg=28.0),
            price_net_eur=1850.00,
            price_gross_eur=2201.50,
            tags=["3-phasig", "hybrid-ready"],
            created_at=now, updated_at=now
        ),
        Product(
            id=generate_product_id(),
            sku="BAT-BYD-001",
            name="BYD Battery-Box HVS 10.2",
            manufacturer="BYD",
            category=ProductCategory.BATTERY,
            specs=ProductSpecs(power_w=10200, efficiency_percent=95.3, weight_kg=164.0, warranty_years=10),
            price_net_eur=5200.00,
            price_gross_eur=6188.00,
            tags=["hochvolt", "modular"],
            created_at=now, updated_at=now
        )
    ]
    
    for p in products:
        _products_store[p.id] = p
    
    # Mock mounting components
    mounting = [
        MountingComponent(
            id="mnt_001",
            name="Dachhaken Ziegel",
            roof_types=[RoofType.TILE, RoofType.PITCHED],
            material="Edelstahl A2",
            price_per_unit_eur=8.50,
            units_per_module=4,
            weight_kg=0.35
        ),
        MountingComponent(
            id="mnt_002",
            name="Montageschiene 4.2m",
            roof_types=[RoofType.TILE, RoofType.PITCHED, RoofType.SLATE],
            material="Aluminium",
            price_per_unit_eur=45.00,
            units_per_module=0.5,
            weight_kg=2.8
        ),
        MountingComponent(
            id="mnt_003",
            name="Flachdach-Aufständerung 15°",
            roof_types=[RoofType.FLAT],
            material="Aluminium/Stahl",
            price_per_unit_eur=65.00,
            units_per_module=1,
            weight_kg=4.5
        )
    ]
    
    for m in mounting:
        _mounting_store[m.id] = m


create_mock_products()


# ==================== API Endpoints ====================

@router.get("/")
async def get_products(
    category: Optional[ProductCategory] = None,
    manufacturer: Optional[str] = None,
    status: Optional[ProductStatus] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0
):
    """Get all products with optional filters."""
    products = list(_products_store.values())
    
    if category:
        products = [p for p in products if p.category == category]
    if manufacturer:
        products = [p for p in products if manufacturer.lower() in p.manufacturer.lower()]
    if status:
        products = [p for p in products if p.status == status]
    if search:
        search_lower = search.lower()
        products = [p for p in products if search_lower in p.name.lower() or search_lower in p.sku.lower()]
    
    return {
        "products": products[offset:offset + limit],
        "total": len(products),
        "has_more": len(products) > offset + limit
    }


@router.post("/")
async def create_product(request: CreateProductRequest):
    """Create a new product."""
    product_id = generate_product_id()
    now = datetime.now()
    
    product = Product(
        id=product_id,
        sku=request.sku or generate_sku(request.category, request.manufacturer),
        name=request.name,
        manufacturer=request.manufacturer,
        category=request.category,
        description=request.description,
        specs=request.specs,
        price_net_eur=request.price_net_eur,
        price_gross_eur=round(request.price_net_eur * (1 + request.vat_percent / 100), 2),
        vat_percent=request.vat_percent,
        tags=request.tags,
        created_at=now,
        updated_at=now
    )
    
    _products_store[product_id] = product
    
    return {"product": product, "message": "Produkt erstellt"}


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a specific product."""
    if product_id not in _products_store:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    return {"product": _products_store[product_id]}


@router.put("/{product_id}")
async def update_product(product_id: str, request: CreateProductRequest):
    """Update a product."""
    if product_id not in _products_store:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    existing = _products_store[product_id]
    
    updated = Product(
        id=product_id,
        sku=request.sku or existing.sku,
        name=request.name,
        manufacturer=request.manufacturer,
        category=request.category,
        status=existing.status,
        description=request.description,
        specs=request.specs,
        price_net_eur=request.price_net_eur,
        price_gross_eur=round(request.price_net_eur * (1 + request.vat_percent / 100), 2),
        vat_percent=request.vat_percent,
        image_urls=existing.image_urls,
        datasheet_url=existing.datasheet_url,
        tags=request.tags,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )
    
    _products_store[product_id] = updated
    
    return {"product": updated, "updated": True}


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Delete a product."""
    if product_id not in _products_store:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    del _products_store[product_id]
    return {"deleted": True, "product_id": product_id}


@router.put("/{product_id}/status")
async def update_product_status(product_id: str, status: ProductStatus):
    """Update product status."""
    if product_id not in _products_store:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    _products_store[product_id].status = status
    _products_store[product_id].updated_at = datetime.now()
    
    return {"product": _products_store[product_id], "updated": True}


@router.post("/import")
async def import_products(file_format: str = "csv"):
    """Import products from CSV/Excel file."""
    # Mock import result
    return ImportResult(
        total_rows=50,
        imported=45,
        updated=3,
        skipped=2,
        errors=[{"row": 12, "error": "Ungültige Kategorie"}, {"row": 38, "error": "Preis fehlt"}]
    )


@router.get("/categories")
async def get_categories():
    """Get product categories with counts."""
    products = list(_products_store.values())
    
    return {
        "categories": [
            ProductCategory_Info(
                id=cat.value,
                name=cat.value.replace("_", " ").title(),
                description=get_category_description(cat),
                product_count=len([p for p in products if p.category == cat])
            )
            for cat in ProductCategory
        ]
    }


def get_category_description(cat: ProductCategory) -> str:
    descriptions = {
        ProductCategory.PV_MODULE: "Photovoltaik-Module",
        ProductCategory.INVERTER: "Wechselrichter",
        ProductCategory.BATTERY: "Batteriespeicher",
        ProductCategory.MOUNTING: "Montagesysteme",
        ProductCategory.CABLE: "Kabel und Leitungen",
        ProductCategory.CONNECTOR: "Stecker und Verbinder",
        ProductCategory.HEATPUMP: "Wärmepumpen",
        ProductCategory.ACCESSORY: "Zubehör"
    }
    return descriptions.get(cat, "")


@router.get("/mounting")
async def get_mounting_components(roof_type: Optional[RoofType] = None):
    """Get mounting components."""
    components = list(_mounting_store.values())
    
    if roof_type:
        components = [c for c in components if roof_type in c.roof_types]
    
    return {"components": components, "total": len(components)}


@router.post("/mounting")
async def create_mounting_component(component: MountingComponent):
    """Create mounting component."""
    _mounting_store[component.id] = component
    return {"component": component, "created": True}


@router.post("/{product_id}/image")
async def upload_product_image(product_id: str, image_url: str):
    """Add image to product."""
    if product_id not in _products_store:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    _products_store[product_id].image_urls.append(image_url)
    _products_store[product_id].updated_at = datetime.now()
    
    return {"product": _products_store[product_id], "image_added": True}


@router.get("/manufacturers")
async def get_manufacturers():
    """Get list of manufacturers."""
    products = list(_products_store.values())
    manufacturers = list(set(p.manufacturer for p in products))
    
    return {
        "manufacturers": [
            {"name": m, "product_count": len([p for p in products if p.manufacturer == m])}
            for m in sorted(manufacturers)
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for product management service."""
    return {
        "status": "healthy",
        "service": "product-management",
        "products_count": len(_products_store),
        "mounting_count": len(_mounting_store),
        "timestamp": datetime.now().isoformat()
    }
