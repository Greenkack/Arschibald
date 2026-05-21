"""
Additional Components API Endpoints

Provides REST API for additional PV system components:
- Wallbox (EV charging stations)
- Energy Management System (EMS)
- Power Optimizers
- Emergency Power Systems (Notstrom)
- Animal Protection (Tierabwehr)

Requirements: funktionen.txt - "Zusatzkomponenten"
Task: 251. Additional Components (Wallbox, EMS, Optimizer)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/additional-components", tags=["Additional Components"])


# ==================== Enums ====================

class ComponentCategory(str, Enum):
    WALLBOX = "wallbox"
    EMS = "ems"
    OPTIMIZER = "optimizer"
    EMERGENCY_POWER = "emergency_power"
    ANIMAL_PROTECTION = "animal_protection"


class WallboxPhase(str, Enum):
    SINGLE_PHASE = "1-phase"
    THREE_PHASE = "3-phase"


# ==================== Pydantic Models ====================

class ComponentBase(BaseModel):
    """Base component model"""
    id: int
    category: ComponentCategory
    manufacturer: str
    model_name: str
    description: str
    price_net: float
    price_gross: float
    features: List[str] = Field(default_factory=list)
    is_active: bool = True


# Wallbox Models
class WallboxComponent(ComponentBase):
    """Wallbox (EV Charging Station) model"""
    category: ComponentCategory = ComponentCategory.WALLBOX
    power_kw: float = Field(..., description="Charging power in kW")
    phase: WallboxPhase
    cable_length_m: float = Field(default=5.0)
    has_cable: bool = True
    has_rfid: bool = False
    has_load_management: bool = False
    has_solar_charging: bool = False
    connector_type: str = Field(default="Type 2")


# EMS Models
class EMSComponent(ComponentBase):
    """Energy Management System model"""
    category: ComponentCategory = ComponentCategory.EMS
    max_devices: int = Field(default=10)
    has_app: bool = True
    has_cloud: bool = True
    supported_inverters: List[str] = Field(default_factory=list)
    supported_batteries: List[str] = Field(default_factory=list)


# Optimizer Models
class OptimizerComponent(ComponentBase):
    """Power Optimizer model"""
    category: ComponentCategory = ComponentCategory.OPTIMIZER
    max_power_w: int = Field(..., description="Max module power in W")
    efficiency_percent: float = Field(default=99.5)
    warranty_years: int = Field(default=25)
    price_per_module: float = Field(default=0.0, description="Price per optimizer")


# Emergency Power Models
class EmergencyPowerComponent(ComponentBase):
    """Emergency Power System (Notstrom) model"""
    category: ComponentCategory = ComponentCategory.EMERGENCY_POWER
    power_kw: float = Field(..., description="Backup power in kW")
    switchover_time_ms: int = Field(default=20)
    supported_inverters: List[str] = Field(default_factory=list)


# Animal Protection Models
class AnimalProtectionComponent(ComponentBase):
    """Animal Protection (Tierabwehr) model"""
    category: ComponentCategory = ComponentCategory.ANIMAL_PROTECTION
    protection_type: str = Field(default="Marderschutz")
    coverage_area_m2: float = Field(default=100.0)


# Selection Request/Response
class ComponentSelectionRequest(BaseModel):
    """Request for component selection"""
    category: ComponentCategory
    pv_system_kwp: Optional[float] = None
    module_count: Optional[int] = None
    inverter_manufacturer: Optional[str] = None
    battery_manufacturer: Optional[str] = None
    max_budget: Optional[float] = None


class ComponentCostCalculation(BaseModel):
    """Cost calculation for selected components"""
    components: List[Dict[str, Any]]
    subtotal_net: float
    subtotal_gross: float
    installation_cost: float
    total_net: float
    total_gross: float


# ==================== Sample Data ====================

WALLBOXES = [
    {
        "id": 101, "category": "wallbox", "manufacturer": "ABL", "model_name": "eMH1 Basic",
        "description": "Einfache Wallbox für Zuhause", "price_net": 599.0, "price_gross": 712.81,
        "power_kw": 11.0, "phase": "3-phase", "cable_length_m": 6.0, "has_cable": True,
        "has_rfid": False, "has_load_management": False, "has_solar_charging": False,
        "connector_type": "Type 2", "features": ["Einfache Installation", "Robust"],
        "is_active": True
    },
    {
        "id": 102, "category": "wallbox", "manufacturer": "ABL", "model_name": "eMH1 1W1101",
        "description": "Wallbox mit Ladekabel", "price_net": 799.0, "price_gross": 950.81,
        "power_kw": 11.0, "phase": "3-phase", "cable_length_m": 6.0, "has_cable": True,
        "has_rfid": True, "has_load_management": False, "has_solar_charging": False,
        "connector_type": "Type 2", "features": ["RFID", "Ladekabel inkl."],
        "is_active": True
    },
    {
        "id": 103, "category": "wallbox", "manufacturer": "Fronius", "model_name": "Wattpilot Home 11 J",
        "description": "Intelligente Wallbox mit Solar-Laden", "price_net": 899.0, "price_gross": 1069.81,
        "power_kw": 11.0, "phase": "3-phase", "cable_length_m": 5.0, "has_cable": True,
        "has_rfid": False, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["Solar-Laden", "App-Steuerung", "Lastmanagement"],
        "is_active": True
    },
    {
        "id": 104, "category": "wallbox", "manufacturer": "Fronius", "model_name": "Wattpilot Home 22 J",
        "description": "Schnelllader mit 22kW", "price_net": 999.0, "price_gross": 1188.81,
        "power_kw": 22.0, "phase": "3-phase", "cable_length_m": 5.0, "has_cable": True,
        "has_rfid": False, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["22kW", "Solar-Laden", "App-Steuerung"],
        "is_active": True
    },
    {
        "id": 105, "category": "wallbox", "manufacturer": "Huawei", "model_name": "Smart Charger 7.4kW",
        "description": "Einphasige Wallbox", "price_net": 549.0, "price_gross": 653.31,
        "power_kw": 7.4, "phase": "1-phase", "cable_length_m": 5.0, "has_cable": True,
        "has_rfid": False, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["Kompakt", "LUNA2000 Integration"],
        "is_active": True
    },
    {
        "id": 106, "category": "wallbox", "manufacturer": "Huawei", "model_name": "Smart Charger 22kW",
        "description": "Dreiphasige Schnelllader", "price_net": 799.0, "price_gross": 950.81,
        "power_kw": 22.0, "phase": "3-phase", "cable_length_m": 5.0, "has_cable": True,
        "has_rfid": True, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["22kW", "RFID", "FusionSolar App"],
        "is_active": True
    },
    {
        "id": 107, "category": "wallbox", "manufacturer": "Keba", "model_name": "KeContact P30 c-series",
        "description": "Premium Wallbox", "price_net": 1199.0, "price_gross": 1426.81,
        "power_kw": 22.0, "phase": "3-phase", "cable_length_m": 6.0, "has_cable": True,
        "has_rfid": True, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["Premium", "OCPP", "Lastmanagement"],
        "is_active": True
    },
    {
        "id": 108, "category": "wallbox", "manufacturer": "go-e", "model_name": "Charger Gemini flex 11kW",
        "description": "Flexible mobile Wallbox", "price_net": 699.0, "price_gross": 831.81,
        "power_kw": 11.0, "phase": "3-phase", "cable_length_m": 0.0, "has_cable": False,
        "has_rfid": False, "has_load_management": True, "has_solar_charging": True,
        "connector_type": "Type 2", "features": ["Mobil", "App", "Solar-Laden"],
        "is_active": True
    },
]

EMS_SYSTEMS = [
    {
        "id": 201, "category": "ems", "manufacturer": "SMA", "model_name": "Sunny Home Manager 2.0",
        "description": "Intelligentes Energiemanagement", "price_net": 599.0, "price_gross": 712.81,
        "max_devices": 12, "has_app": True, "has_cloud": True,
        "supported_inverters": ["SMA"], "supported_batteries": ["BYD", "LG"],
        "features": ["Prognosebasiert", "Lastmanagement", "Visualisierung"],
        "is_active": True
    },
    {
        "id": 202, "category": "ems", "manufacturer": "Fronius", "model_name": "Smart Meter TS 65A-3",
        "description": "Energiezähler mit EMS-Funktion", "price_net": 399.0, "price_gross": 474.81,
        "max_devices": 8, "has_app": True, "has_cloud": True,
        "supported_inverters": ["Fronius"], "supported_batteries": ["BYD", "Fronius"],
        "features": ["Bidirektional", "Modbus", "Solar.web"],
        "is_active": True
    },
    {
        "id": 203, "category": "ems", "manufacturer": "Huawei", "model_name": "Smart Power Sensor DTSU666-H",
        "description": "Smart Meter für Huawei Systeme", "price_net": 199.0, "price_gross": 236.81,
        "max_devices": 6, "has_app": True, "has_cloud": True,
        "supported_inverters": ["Huawei"], "supported_batteries": ["Huawei LUNA2000"],
        "features": ["FusionSolar", "Echtzeit-Monitoring"],
        "is_active": True
    },
    {
        "id": 204, "category": "ems", "manufacturer": "Solar-Log", "model_name": "Solar-Log Base",
        "description": "Universelles Monitoring-System", "price_net": 449.0, "price_gross": 534.31,
        "max_devices": 15, "has_app": True, "has_cloud": True,
        "supported_inverters": ["SMA", "Fronius", "Huawei", "Kostal", "SolarEdge"],
        "supported_batteries": ["BYD", "LG", "Sonnen", "Tesla"],
        "features": ["Multi-Hersteller", "Ertragsprognose", "Fernwartung"],
        "is_active": True
    },
]

OPTIMIZERS = [
    {
        "id": 301, "category": "optimizer", "manufacturer": "SolarEdge", "model_name": "P401",
        "description": "Leistungsoptimierer für 1 Modul", "price_net": 55.0, "price_gross": 65.45,
        "max_power_w": 400, "efficiency_percent": 99.5, "warranty_years": 25,
        "price_per_module": 55.0,
        "features": ["Moduloptimierung", "Monitoring", "Sicherheit"],
        "is_active": True
    },
    {
        "id": 302, "category": "optimizer", "manufacturer": "SolarEdge", "model_name": "P505",
        "description": "Leistungsoptimierer für große Module", "price_net": 65.0, "price_gross": 77.35,
        "max_power_w": 505, "efficiency_percent": 99.5, "warranty_years": 25,
        "price_per_module": 65.0,
        "features": ["Hochleistung", "Monitoring", "Sicherheit"],
        "is_active": True
    },
    {
        "id": 303, "category": "optimizer", "manufacturer": "Tigo", "model_name": "TS4-A-O",
        "description": "Universeller Optimierer", "price_net": 45.0, "price_gross": 53.55,
        "max_power_w": 700, "efficiency_percent": 99.6, "warranty_years": 25,
        "price_per_module": 45.0,
        "features": ["Universal", "Rapid Shutdown", "Monitoring"],
        "is_active": True
    },
    {
        "id": 304, "category": "optimizer", "manufacturer": "Huawei", "model_name": "Smart PV Optimizer SUN2000-450W-P",
        "description": "Huawei Optimierer", "price_net": 50.0, "price_gross": 59.50,
        "max_power_w": 450, "efficiency_percent": 99.5, "warranty_years": 25,
        "price_per_module": 50.0,
        "features": ["FusionSolar", "AI-Optimierung"],
        "is_active": True
    },
]

EMERGENCY_POWER = [
    {
        "id": 401, "category": "emergency_power", "manufacturer": "Fronius", "model_name": "GEN24 Notstrom-Box",
        "description": "Notstromversorgung für GEN24", "price_net": 899.0, "price_gross": 1069.81,
        "power_kw": 6.0, "switchover_time_ms": 20,
        "supported_inverters": ["Fronius GEN24"],
        "features": ["Automatische Umschaltung", "Inselbetrieb"],
        "is_active": True
    },
    {
        "id": 402, "category": "emergency_power", "manufacturer": "SMA", "model_name": "Backup Box",
        "description": "Notstrom für SMA Systeme", "price_net": 1299.0, "price_gross": 1545.81,
        "power_kw": 8.0, "switchover_time_ms": 20,
        "supported_inverters": ["SMA Sunny Tripower Smart Energy"],
        "features": ["Vollautomatisch", "Schwarzstartfähig"],
        "is_active": True
    },
    {
        "id": 403, "category": "emergency_power", "manufacturer": "Huawei", "model_name": "Backup Box-B1",
        "description": "Notstrom für Huawei Systeme", "price_net": 799.0, "price_gross": 950.81,
        "power_kw": 5.0, "switchover_time_ms": 10,
        "supported_inverters": ["Huawei SUN2000"],
        "features": ["Schnelle Umschaltung", "LUNA2000 kompatibel"],
        "is_active": True
    },
    {
        "id": 404, "category": "emergency_power", "manufacturer": "E3/DC", "model_name": "Notstrom integriert",
        "description": "Integrierte Notstromfunktion", "price_net": 0.0, "price_gross": 0.0,
        "power_kw": 6.0, "switchover_time_ms": 0,
        "supported_inverters": ["E3/DC S10"],
        "features": ["Integriert", "Keine Zusatzkosten"],
        "is_active": True
    },
]

ANIMAL_PROTECTION = [
    {
        "id": 501, "category": "animal_protection", "manufacturer": "K&K", "model_name": "Marderschutz M8700",
        "description": "Ultraschall Marderschutz", "price_net": 89.0, "price_gross": 105.91,
        "protection_type": "Ultraschall", "coverage_area_m2": 100.0,
        "features": ["Ultraschall", "Batteriebetrieb"],
        "is_active": True
    },
    {
        "id": 502, "category": "animal_protection", "manufacturer": "STOP&GO", "model_name": "Marderabwehr Plus-Minus",
        "description": "Hochspannungs-Marderschutz", "price_net": 149.0, "price_gross": 177.31,
        "protection_type": "Hochspannung", "coverage_area_m2": 150.0,
        "features": ["Hochspannung", "Effektiv", "Tierschutzkonform"],
        "is_active": True
    },
    {
        "id": 503, "category": "animal_protection", "manufacturer": "Gardigo", "model_name": "Marder-Frei Mobil",
        "description": "Mobiler Marderschutz", "price_net": 49.0, "price_gross": 58.31,
        "protection_type": "Ultraschall", "coverage_area_m2": 50.0,
        "features": ["Mobil", "Solar-betrieben"],
        "is_active": True
    },
    {
        "id": 504, "category": "animal_protection", "manufacturer": "Vogelabwehr Pro", "model_name": "Taubenspikes Set",
        "description": "Taubenabwehr für PV-Module", "price_net": 12.0, "price_gross": 14.28,
        "protection_type": "Mechanisch", "coverage_area_m2": 1.0,
        "features": ["Pro Meter", "Edelstahl", "Langlebig"],
        "is_active": True
    },
]

# Combine all components
ALL_COMPONENTS = WALLBOXES + EMS_SYSTEMS + OPTIMIZERS + EMERGENCY_POWER + ANIMAL_PROTECTION


# ==================== Helper Functions ====================

def get_component_by_id(component_id: int) -> Optional[Dict]:
    """Get component by ID"""
    for comp in ALL_COMPONENTS:
        if comp["id"] == component_id:
            return comp
    return None


def get_components_by_category(category: ComponentCategory) -> List[Dict]:
    """Get all components of a specific category"""
    return [c for c in ALL_COMPONENTS if c["category"] == category.value]


def calculate_optimizer_cost(module_count: int, optimizer_id: int) -> Dict[str, Any]:
    """Calculate total cost for optimizers based on module count"""
    optimizer = get_component_by_id(optimizer_id)
    if not optimizer:
        return {"error": "Optimizer not found"}
    
    total_net = optimizer["price_per_module"] * module_count
    total_gross = total_net * 1.19
    
    return {
        "optimizer": optimizer,
        "module_count": module_count,
        "price_per_module": optimizer["price_per_module"],
        "total_net": round(total_net, 2),
        "total_gross": round(total_gross, 2)
    }


def calculate_total_component_cost(component_ids: List[int], module_count: int = 0) -> Dict[str, Any]:
    """Calculate total cost for selected components"""
    components = []
    subtotal_net = 0.0
    
    for cid in component_ids:
        comp = get_component_by_id(cid)
        if comp:
            if comp["category"] == "optimizer" and module_count > 0:
                # Optimizers are priced per module
                cost = comp.get("price_per_module", comp["price_net"]) * module_count
            else:
                cost = comp["price_net"]
            
            components.append({
                "component": comp,
                "quantity": module_count if comp["category"] == "optimizer" else 1,
                "cost_net": round(cost, 2),
                "cost_gross": round(cost * 1.19, 2)
            })
            subtotal_net += cost
    
    # Installation cost estimate (10% of component cost, min 200€)
    installation_cost = max(200.0, subtotal_net * 0.10)
    
    return {
        "components": components,
        "subtotal_net": round(subtotal_net, 2),
        "subtotal_gross": round(subtotal_net * 1.19, 2),
        "installation_cost": round(installation_cost, 2),
        "total_net": round(subtotal_net + installation_cost, 2),
        "total_gross": round((subtotal_net + installation_cost) * 1.19, 2)
    }


# ==================== API Endpoints ====================

@router.get("/")
async def list_all_components(
    category: Optional[ComponentCategory] = Query(None),
    manufacturer: Optional[str] = Query(None),
    active_only: bool = Query(True)
):
    """Get all additional components with optional filters"""
    result = ALL_COMPONENTS.copy()
    
    if category:
        result = [c for c in result if c["category"] == category.value]
    if manufacturer:
        result = [c for c in result if c["manufacturer"].lower() == manufacturer.lower()]
    if active_only:
        result = [c for c in result if c["is_active"]]
    
    return result


@router.get("/categories")
async def list_categories():
    """Get all component categories with counts"""
    return {
        "categories": [
            {"id": "wallbox", "name": "Wallbox", "count": len(WALLBOXES)},
            {"id": "ems", "name": "Energiemanagement (EMS)", "count": len(EMS_SYSTEMS)},
            {"id": "optimizer", "name": "Leistungsoptimierer", "count": len(OPTIMIZERS)},
            {"id": "emergency_power", "name": "Notstrom", "count": len(EMERGENCY_POWER)},
            {"id": "animal_protection", "name": "Tierabwehr", "count": len(ANIMAL_PROTECTION)},
        ]
    }


@router.get("/wallboxes")
async def list_wallboxes(
    phase: Optional[WallboxPhase] = Query(None),
    min_power: Optional[float] = Query(None),
    max_power: Optional[float] = Query(None),
    has_solar_charging: Optional[bool] = Query(None)
):
    """Get all wallboxes with optional filters"""
    result = WALLBOXES.copy()
    
    if phase:
        result = [w for w in result if w["phase"] == phase.value]
    if min_power is not None:
        result = [w for w in result if w["power_kw"] >= min_power]
    if max_power is not None:
        result = [w for w in result if w["power_kw"] <= max_power]
    if has_solar_charging is not None:
        result = [w for w in result if w["has_solar_charging"] == has_solar_charging]
    
    return result


@router.get("/ems")
async def list_ems_systems(
    inverter_manufacturer: Optional[str] = Query(None)
):
    """Get all EMS systems with optional inverter compatibility filter"""
    result = EMS_SYSTEMS.copy()
    
    if inverter_manufacturer:
        result = [e for e in result 
                 if any(inverter_manufacturer.lower() in inv.lower() 
                       for inv in e["supported_inverters"])]
    
    return result


@router.get("/optimizers")
async def list_optimizers(
    min_power: Optional[int] = Query(None)
):
    """Get all power optimizers"""
    result = OPTIMIZERS.copy()
    
    if min_power is not None:
        result = [o for o in result if o["max_power_w"] >= min_power]
    
    return result


@router.get("/emergency-power")
async def list_emergency_power(
    inverter_manufacturer: Optional[str] = Query(None)
):
    """Get all emergency power systems"""
    result = EMERGENCY_POWER.copy()
    
    if inverter_manufacturer:
        result = [e for e in result 
                 if any(inverter_manufacturer.lower() in inv.lower() 
                       for inv in e["supported_inverters"])]
    
    return result


@router.get("/animal-protection")
async def list_animal_protection(
    protection_type: Optional[str] = Query(None)
):
    """Get all animal protection options"""
    result = ANIMAL_PROTECTION.copy()
    
    if protection_type:
        result = [a for a in result 
                 if a["protection_type"].lower() == protection_type.lower()]
    
    return result


@router.get("/manufacturers")
async def list_manufacturers(category: Optional[ComponentCategory] = Query(None)):
    """Get list of all manufacturers"""
    components = ALL_COMPONENTS if not category else get_components_by_category(category)
    manufacturers = list(set(c["manufacturer"] for c in components))
    return sorted(manufacturers)


@router.get("/{component_id}")
async def get_component(component_id: int):
    """Get component by ID"""
    component = get_component_by_id(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


@router.post("/calculate-optimizer-cost")
async def calculate_optimizer_cost_endpoint(
    optimizer_id: int,
    module_count: int
):
    """Calculate total optimizer cost based on module count"""
    result = calculate_optimizer_cost(module_count, optimizer_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/calculate-total-cost")
async def calculate_total_cost(
    component_ids: List[int],
    module_count: int = 0
):
    """Calculate total cost for selected components"""
    return calculate_total_component_cost(component_ids, module_count)


@router.post("/recommend")
async def recommend_components(request: ComponentSelectionRequest):
    """Recommend components based on system configuration"""
    recommendations = {
        "wallbox": None,
        "ems": None,
        "optimizer": None,
        "emergency_power": None,
        "animal_protection": None
    }
    
    # Recommend Wallbox (default 11kW 3-phase)
    wallbox_candidates = [w for w in WALLBOXES if w["power_kw"] == 11.0 and w["phase"] == "3-phase"]
    if wallbox_candidates:
        # Prefer ones with solar charging
        solar_wallboxes = [w for w in wallbox_candidates if w["has_solar_charging"]]
        recommendations["wallbox"] = solar_wallboxes[0] if solar_wallboxes else wallbox_candidates[0]
    
    # Recommend EMS based on inverter
    if request.inverter_manufacturer:
        ems_candidates = [e for e in EMS_SYSTEMS 
                        if any(request.inverter_manufacturer.lower() in inv.lower() 
                              for inv in e["supported_inverters"])]
        if ems_candidates:
            recommendations["ems"] = ems_candidates[0]
    
    # Recommend Optimizer if shading issues (always recommend for safety)
    if request.module_count and request.module_count > 0:
        recommendations["optimizer"] = OPTIMIZERS[0]  # SolarEdge P401
    
    # Recommend Emergency Power based on inverter
    if request.inverter_manufacturer:
        ep_candidates = [e for e in EMERGENCY_POWER 
                        if any(request.inverter_manufacturer.lower() in inv.lower() 
                              for inv in e["supported_inverters"])]
        if ep_candidates:
            recommendations["emergency_power"] = ep_candidates[0]
    
    # Always recommend basic animal protection
    recommendations["animal_protection"] = ANIMAL_PROTECTION[0]  # K&K Marderschutz
    
    return recommendations


@router.get("/health/check")
async def health_check():
    """Check additional components service health"""
    return {
        "status": "healthy",
        "total_components": len(ALL_COMPONENTS),
        "categories": {
            "wallboxes": len(WALLBOXES),
            "ems": len(EMS_SYSTEMS),
            "optimizers": len(OPTIMIZERS),
            "emergency_power": len(EMERGENCY_POWER),
            "animal_protection": len(ANIMAL_PROTECTION)
        }
    }
