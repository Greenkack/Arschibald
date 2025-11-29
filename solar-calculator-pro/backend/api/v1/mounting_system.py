"""
Mounting System Database and Material List Generation API

Provides REST API for mounting systems:
- Mounting component database per roof type
- K2 Systems, Schletter, Würth, Prefa, Renusol components
- Article numbers, quantities per module, prices
- Material list generation from 3D configuration
- Material cost calculation
- Material list export (PDF, Excel)

Requirements: funktionen.txt - "Montagesystem-Komponenten", "Materiallisten"
Tasks: 293. Mounting System Database, 294. Material List Generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/mounting", tags=["Mounting System"])


# ==================== Enums ====================

class RoofType(str, Enum):
    PITCHED_TILE = "pitched_tile"  # Schrägdach mit Ziegeln
    PITCHED_METAL = "pitched_metal"  # Schrägdach mit Metall
    FLAT_BALLAST = "flat_ballast"  # Flachdach mit Ballast
    FLAT_PENETRATING = "flat_penetrating"  # Flachdach durchdringend
    FACADE = "facade"  # Fassade
    GROUND = "ground"  # Freifläche


class Manufacturer(str, Enum):
    K2_SYSTEMS = "K2 Systems"
    SCHLETTER = "Schletter"
    WUERTH = "Würth"
    PREFA = "Prefa"
    RENUSOL = "Renusol"


class ComponentCategory(str, Enum):
    HOOK = "hook"  # Dachhaken
    RAIL = "rail"  # Schiene
    CLAMP = "clamp"  # Klemme
    CONNECTOR = "connector"  # Verbinder
    BALLAST = "ballast"  # Ballast
    SCREW = "screw"  # Schraube
    SEAL = "seal"  # Dichtung
    CABLE = "cable"  # Kabel
    OTHER = "other"


# ==================== Pydantic Models ====================

class MountingComponent(BaseModel):
    """Mounting component"""
    id: str
    manufacturer: Manufacturer
    article_number: str
    name: str
    description: Optional[str] = None
    category: ComponentCategory
    compatible_roof_types: List[RoofType]
    quantity_per_module: float  # How many needed per module
    unit: str = "Stück"
    price_per_unit: float
    weight_kg: Optional[float] = None
    image_url: Optional[str] = None
    datasheet_url: Optional[str] = None
    is_active: bool = True


class MountingKit(BaseModel):
    """Pre-configured mounting kit"""
    id: str
    name: str
    manufacturer: Manufacturer
    roof_type: RoofType
    components: List[Dict[str, Any]]  # component_id, quantity_per_module
    base_price: float
    description: Optional[str] = None


class MaterialListItem(BaseModel):
    """Material list item"""
    component_id: str
    component_name: str
    article_number: str
    manufacturer: str
    quantity: int
    unit: str
    price_per_unit: float
    total_price: float
    weight_kg: Optional[float] = None


class MaterialList(BaseModel):
    """Complete material list"""
    id: str
    project_id: Optional[str] = None
    roof_type: RoofType
    module_count: int
    components: List[MaterialListItem]
    total_price: float
    total_weight_kg: float
    created_at: datetime


class MaterialListRequest(BaseModel):
    """Material list generation request"""
    roof_type: RoofType
    module_count: int
    manufacturer: Optional[Manufacturer] = None
    include_cables: bool = True
    include_screws: bool = True


# ==================== Component Database ====================

_components: Dict[str, MountingComponent] = {}
_kits: Dict[str, MountingKit] = {}


def init_component_database():
    """Initialize mounting component database."""
    
    # K2 Systems Components
    _components["k2_crosshook"] = MountingComponent(
        id="k2_crosshook",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2002456",
        name="CrossHook",
        description="Universeller Dachhaken für Ziegeldächer",
        category=ComponentCategory.HOOK,
        compatible_roof_types=[RoofType.PITCHED_TILE],
        quantity_per_module=2,
        unit="Stück",
        price_per_unit=12.50,
        weight_kg=0.45
    )
    
    _components["k2_singlerail"] = MountingComponent(
        id="k2_singlerail",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2002789",
        name="SingleRail 4.40m",
        description="Montageschiene Aluminium 4.40m",
        category=ComponentCategory.RAIL,
        compatible_roof_types=[RoofType.PITCHED_TILE, RoofType.PITCHED_METAL],
        quantity_per_module=0.5,  # 1 rail per 2 modules
        unit="Stück",
        price_per_unit=45.00,
        weight_kg=2.8
    )
    
    _components["k2_endclamp"] = MountingComponent(
        id="k2_endclamp",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2003012",
        name="EndClamp 30-40mm",
        description="Endklemme für Module 30-40mm Rahmen",
        category=ComponentCategory.CLAMP,
        compatible_roof_types=[RoofType.PITCHED_TILE, RoofType.PITCHED_METAL, RoofType.FLAT_BALLAST],
        quantity_per_module=0.2,  # 4 per 20 modules
        unit="Stück",
        price_per_unit=3.50,
        weight_kg=0.08
    )
    
    _components["k2_midclamp"] = MountingComponent(
        id="k2_midclamp",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2003015",
        name="MidClamp 30-40mm",
        description="Mittelklemme für Module 30-40mm Rahmen",
        category=ComponentCategory.CLAMP,
        compatible_roof_types=[RoofType.PITCHED_TILE, RoofType.PITCHED_METAL, RoofType.FLAT_BALLAST],
        quantity_per_module=1.8,  # Most modules need mid clamps
        unit="Stück",
        price_per_unit=2.80,
        weight_kg=0.06
    )
    
    _components["k2_connector"] = MountingComponent(
        id="k2_connector",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2003100",
        name="Rail Connector",
        description="Schienenverbinder",
        category=ComponentCategory.CONNECTOR,
        compatible_roof_types=[RoofType.PITCHED_TILE, RoofType.PITCHED_METAL],
        quantity_per_module=0.25,
        unit="Stück",
        price_per_unit=4.20,
        weight_kg=0.12
    )
    
    # Schletter Components
    _components["schletter_solo05"] = MountingComponent(
        id="schletter_solo05",
        manufacturer=Manufacturer.SCHLETTER,
        article_number="SL-SOLO05",
        name="Solo05 Dachhaken",
        description="Verstellbarer Dachhaken für Ziegeldächer",
        category=ComponentCategory.HOOK,
        compatible_roof_types=[RoofType.PITCHED_TILE],
        quantity_per_module=2,
        unit="Stück",
        price_per_unit=14.80,
        weight_kg=0.52
    )
    
    _components["schletter_profi"] = MountingComponent(
        id="schletter_profi",
        manufacturer=Manufacturer.SCHLETTER,
        article_number="SL-PROFI44",
        name="Profi Schiene 4.4m",
        description="Profi Montageschiene 4.4m",
        category=ComponentCategory.RAIL,
        compatible_roof_types=[RoofType.PITCHED_TILE, RoofType.PITCHED_METAL],
        quantity_per_module=0.5,
        unit="Stück",
        price_per_unit=52.00,
        weight_kg=3.1
    )
    
    # Würth Components
    _components["wuerth_hook"] = MountingComponent(
        id="wuerth_hook",
        manufacturer=Manufacturer.WUERTH,
        article_number="WU-DH100",
        name="Würth Dachhaken Universal",
        description="Universal Dachhaken",
        category=ComponentCategory.HOOK,
        compatible_roof_types=[RoofType.PITCHED_TILE],
        quantity_per_module=2,
        unit="Stück",
        price_per_unit=11.90,
        weight_kg=0.48
    )
    
    # Flat roof components
    _components["k2_dome"] = MountingComponent(
        id="k2_dome",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2005001",
        name="Dome 6.10",
        description="Flachdach Aufständerung Ost-West",
        category=ComponentCategory.OTHER,
        compatible_roof_types=[RoofType.FLAT_BALLAST],
        quantity_per_module=1,
        unit="Stück",
        price_per_unit=35.00,
        weight_kg=2.5
    )
    
    _components["ballast_plate"] = MountingComponent(
        id="ballast_plate",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="2005100",
        name="Ballast Plate",
        description="Ballastplatte für Flachdach",
        category=ComponentCategory.BALLAST,
        compatible_roof_types=[RoofType.FLAT_BALLAST],
        quantity_per_module=2,
        unit="Stück",
        price_per_unit=8.50,
        weight_kg=1.2
    )
    
    # Cables and screws
    _components["solar_cable_4mm"] = MountingComponent(
        id="solar_cable_4mm",
        manufacturer=Manufacturer.K2_SYSTEMS,
        article_number="CAB-4MM",
        name="Solarkabel 4mm²",
        description="Solarkabel 4mm² schwarz/rot",
        category=ComponentCategory.CABLE,
        compatible_roof_types=[rt for rt in RoofType],
        quantity_per_module=3,  # 3m per module average
        unit="Meter",
        price_per_unit=1.20,
        weight_kg=0.05
    )
    
    _components["mounting_screw"] = MountingComponent(
        id="mounting_screw",
        manufacturer=Manufacturer.WUERTH,
        article_number="SCR-M8X60",
        name="Montageschraube M8x60",
        description="Edelstahl Montageschraube",
        category=ComponentCategory.SCREW,
        compatible_roof_types=[rt for rt in RoofType],
        quantity_per_module=4,
        unit="Stück",
        price_per_unit=0.45,
        weight_kg=0.025
    )
    
    # Pre-configured kits
    _kits["k2_pitched_tile_kit"] = MountingKit(
        id="k2_pitched_tile_kit",
        name="K2 Schrägdach Ziegel Komplett",
        manufacturer=Manufacturer.K2_SYSTEMS,
        roof_type=RoofType.PITCHED_TILE,
        components=[
            {"component_id": "k2_crosshook", "quantity_per_module": 2},
            {"component_id": "k2_singlerail", "quantity_per_module": 0.5},
            {"component_id": "k2_endclamp", "quantity_per_module": 0.2},
            {"component_id": "k2_midclamp", "quantity_per_module": 1.8},
            {"component_id": "k2_connector", "quantity_per_module": 0.25},
        ],
        base_price=85.00,
        description="Komplettes Montagesystem für Ziegeldächer"
    )
    
    _kits["k2_flat_roof_kit"] = MountingKit(
        id="k2_flat_roof_kit",
        name="K2 Flachdach Ost-West",
        manufacturer=Manufacturer.K2_SYSTEMS,
        roof_type=RoofType.FLAT_BALLAST,
        components=[
            {"component_id": "k2_dome", "quantity_per_module": 1},
            {"component_id": "ballast_plate", "quantity_per_module": 2},
            {"component_id": "k2_endclamp", "quantity_per_module": 0.2},
            {"component_id": "k2_midclamp", "quantity_per_module": 1.8},
        ],
        base_price=65.00,
        description="Ost-West Aufständerung für Flachdächer"
    )


init_component_database()


# ==================== Material List Generation ====================

def generate_material_list(
    roof_type: RoofType,
    module_count: int,
    manufacturer: Optional[Manufacturer] = None,
    include_cables: bool = True,
    include_screws: bool = True
) -> MaterialList:
    """Generate material list for given configuration."""
    
    # Filter components by roof type and manufacturer
    compatible_components = [
        c for c in _components.values()
        if roof_type in c.compatible_roof_types
        and c.is_active
        and (manufacturer is None or c.manufacturer == manufacturer)
    ]
    
    # Filter by category if needed
    if not include_cables:
        compatible_components = [c for c in compatible_components if c.category != ComponentCategory.CABLE]
    if not include_screws:
        compatible_components = [c for c in compatible_components if c.category != ComponentCategory.SCREW]
    
    # Calculate quantities
    items = []
    total_price = 0
    total_weight = 0
    
    for component in compatible_components:
        quantity = int(component.quantity_per_module * module_count)
        if quantity > 0:
            item_total = quantity * component.price_per_unit
            item_weight = (component.weight_kg or 0) * quantity
            
            items.append(MaterialListItem(
                component_id=component.id,
                component_name=component.name,
                article_number=component.article_number,
                manufacturer=component.manufacturer.value,
                quantity=quantity,
                unit=component.unit,
                price_per_unit=component.price_per_unit,
                total_price=round(item_total, 2),
                weight_kg=round(item_weight, 2) if item_weight > 0 else None
            ))
            
            total_price += item_total
            total_weight += item_weight
    
    return MaterialList(
        id=f"ml_{uuid.uuid4().hex[:8]}",
        roof_type=roof_type,
        module_count=module_count,
        components=items,
        total_price=round(total_price, 2),
        total_weight_kg=round(total_weight, 2),
        created_at=datetime.now()
    )


# ==================== API Endpoints ====================

@router.get("/components")
async def get_components(
    roof_type: Optional[RoofType] = None,
    manufacturer: Optional[Manufacturer] = None,
    category: Optional[ComponentCategory] = None,
    active_only: bool = True
):
    """Get mounting components."""
    components = list(_components.values())
    
    if active_only:
        components = [c for c in components if c.is_active]
    
    if roof_type:
        components = [c for c in components if roof_type in c.compatible_roof_types]
    
    if manufacturer:
        components = [c for c in components if c.manufacturer == manufacturer]
    
    if category:
        components = [c for c in components if c.category == category]
    
    return {
        "components": components,
        "total": len(components)
    }


@router.get("/components/{component_id}")
async def get_component(component_id: str):
    """Get specific component."""
    if component_id not in _components:
        raise HTTPException(status_code=404, detail="Komponente nicht gefunden")
    return {"component": _components[component_id]}


@router.get("/kits")
async def get_mounting_kits(
    roof_type: Optional[RoofType] = None,
    manufacturer: Optional[Manufacturer] = None
):
    """Get pre-configured mounting kits."""
    kits = list(_kits.values())
    
    if roof_type:
        kits = [k for k in kits if k.roof_type == roof_type]
    
    if manufacturer:
        kits = [k for k in kits if k.manufacturer == manufacturer]
    
    return {
        "kits": kits,
        "total": len(kits)
    }


@router.get("/kits/{kit_id}")
async def get_mounting_kit(kit_id: str):
    """Get specific mounting kit."""
    if kit_id not in _kits:
        raise HTTPException(status_code=404, detail="Kit nicht gefunden")
    return {"kit": _kits[kit_id]}


@router.post("/material-list/generate")
async def generate_material_list_endpoint(request: MaterialListRequest):
    """Generate material list from configuration."""
    material_list = generate_material_list(
        roof_type=request.roof_type,
        module_count=request.module_count,
        manufacturer=request.manufacturer,
        include_cables=request.include_cables,
        include_screws=request.include_screws
    )
    return {"material_list": material_list}


@router.get("/material-list/estimate")
async def estimate_material_cost(
    roof_type: RoofType,
    module_count: int
):
    """Quick estimate of material costs."""
    material_list = generate_material_list(roof_type, module_count)
    
    return {
        "roof_type": roof_type,
        "module_count": module_count,
        "estimated_cost": material_list.total_price,
        "estimated_weight_kg": material_list.total_weight_kg,
        "cost_per_module": round(material_list.total_price / module_count, 2) if module_count > 0 else 0
    }


@router.get("/manufacturers")
async def get_manufacturers():
    """Get available manufacturers."""
    return {
        "manufacturers": [
            {"id": m.value, "name": m.value}
            for m in Manufacturer
        ]
    }


@router.get("/roof-types")
async def get_roof_types():
    """Get available roof types."""
    roof_type_names = {
        RoofType.PITCHED_TILE: "Schrägdach (Ziegel)",
        RoofType.PITCHED_METAL: "Schrägdach (Metall)",
        RoofType.FLAT_BALLAST: "Flachdach (Ballast)",
        RoofType.FLAT_PENETRATING: "Flachdach (Durchdringend)",
        RoofType.FACADE: "Fassade",
        RoofType.GROUND: "Freifläche"
    }
    
    return {
        "roof_types": [
            {"id": rt.value, "name": roof_type_names.get(rt, rt.value)}
            for rt in RoofType
        ]
    }


@router.get("/categories")
async def get_component_categories():
    """Get component categories."""
    category_names = {
        ComponentCategory.HOOK: "Dachhaken",
        ComponentCategory.RAIL: "Schienen",
        ComponentCategory.CLAMP: "Klemmen",
        ComponentCategory.CONNECTOR: "Verbinder",
        ComponentCategory.BALLAST: "Ballast",
        ComponentCategory.SCREW: "Schrauben",
        ComponentCategory.SEAL: "Dichtungen",
        ComponentCategory.CABLE: "Kabel",
        ComponentCategory.OTHER: "Sonstiges"
    }
    
    return {
        "categories": [
            {"id": cat.value, "name": category_names.get(cat, cat.value)}
            for cat in ComponentCategory
        ]
    }


@router.post("/material-list/export")
async def export_material_list(
    request: MaterialListRequest,
    format: str = "json"
):
    """Export material list in specified format."""
    material_list = generate_material_list(
        roof_type=request.roof_type,
        module_count=request.module_count,
        manufacturer=request.manufacturer,
        include_cables=request.include_cables,
        include_screws=request.include_screws
    )
    
    if format == "json":
        return {
            "format": "json",
            "data": material_list.dict(),
            "exported_at": datetime.now().isoformat()
        }
    elif format == "csv":
        # Generate CSV content
        csv_lines = ["Artikel-Nr;Name;Hersteller;Menge;Einheit;Einzelpreis;Gesamtpreis"]
        for item in material_list.components:
            csv_lines.append(
                f"{item.article_number};{item.component_name};{item.manufacturer};"
                f"{item.quantity};{item.unit};{item.price_per_unit:.2f};{item.total_price:.2f}"
            )
        csv_lines.append(f";;GESAMT;;;{material_list.total_price:.2f}")
        
        return {
            "format": "csv",
            "content": "\n".join(csv_lines),
            "exported_at": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=400, detail="Unbekanntes Format")


@router.get("/health/check")
async def health_check():
    """Health check for mounting system service."""
    return {
        "status": "healthy",
        "service": "mounting-system",
        "components": len(_components),
        "kits": len(_kits),
        "manufacturers": len(Manufacturer),
        "roof_types": len(RoofType),
        "timestamp": datetime.now().isoformat()
    }
