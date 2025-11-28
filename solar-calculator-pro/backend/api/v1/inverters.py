"""
Inverter API Endpoints

Provides REST API for inverter selection, sizing, and compatibility checks.
Based on existing InverterService.

Requirements: funktionen.txt - "Wechselrichter"
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/inverters", tags=["Inverters"])


# ==================== Pydantic Models ====================

class InverterBase(BaseModel):
    """Base inverter model"""
    id: Optional[int] = None
    manufacturer: str
    model_name: str
    power_kw: float = Field(..., description="AC power output in kW")
    efficiency_percent: float = Field(default=97.0, description="Efficiency in %")
    max_dc_voltage: float = Field(default=1000.0, description="Max DC voltage in V")
    mppt_count: int = Field(default=2, description="Number of MPPT trackers")
    max_dc_current: float = Field(default=30.0, description="Max DC current per MPPT in A")
    price_net: float = Field(default=0.0, description="Net price in EUR")
    price_gross: float = Field(default=0.0, description="Gross price in EUR")
    warranty_years: int = Field(default=10)
    weight_kg: float = Field(default=0.0)
    features: List[str] = Field(default_factory=list)
    is_hybrid: bool = Field(default=False, description="Supports battery storage")
    is_active: bool = Field(default=True)


class InverterResponse(InverterBase):
    """Inverter response with additional fields"""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class InverterSizingRequest(BaseModel):
    """Request for inverter sizing calculation"""
    pv_power_kwp: float = Field(..., description="PV system power in kWp")
    module_voltage_vmp: float = Field(default=40.0, description="Module voltage at MPP")
    module_current_imp: float = Field(default=10.0, description="Module current at MPP")
    modules_per_string: int = Field(default=10)
    number_of_strings: int = Field(default=2)


class InverterSizingResponse(BaseModel):
    """Response with sizing calculations"""
    required_power_kw: float
    recommended_power_range: Dict[str, float]
    dc_specifications: Dict[str, float]
    mppt_configuration: Dict[str, Any]
    sizing_ratio: Dict[str, Any]


class InverterSelectionRequest(BaseModel):
    """Request for inverter selection"""
    pv_power_kwp: float
    system_voltage: float = Field(default=400.0)
    preferred_manufacturer: Optional[str] = None
    required_features: List[str] = Field(default_factory=list)
    is_hybrid_required: bool = Field(default=False)


class CompatibilityCheckRequest(BaseModel):
    """Request for compatibility check"""
    inverter_id: int
    pv_power_kwp: float
    string_voltage: float
    total_current: float
    number_of_strings: int


class MultiInverterRequest(BaseModel):
    """Request for multi-inverter configuration"""
    pv_power_kwp: float
    roof_sections: List[Dict[str, Any]] = Field(default_factory=list)


# ==================== Sample Data ====================

SAMPLE_INVERTERS = [
    {
        "id": 1, "manufacturer": "Fronius", "model_name": "Symo 10.0-3-M",
        "power_kw": 10.0, "efficiency_percent": 98.0, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 27.0, "price_net": 2100.0, "price_gross": 2499.0,
        "warranty_years": 10, "weight_kg": 21.9, "features": ["Smart Home", "WLAN"],
        "is_hybrid": False, "is_active": True
    },
    {
        "id": 2, "manufacturer": "Fronius", "model_name": "Symo GEN24 10.0 Plus",
        "power_kw": 10.0, "efficiency_percent": 98.4, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 25.0, "price_net": 3200.0, "price_gross": 3808.0,
        "warranty_years": 10, "weight_kg": 26.0, "features": ["Hybrid", "Notstrom", "WLAN"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 3, "manufacturer": "SMA", "model_name": "Sunny Tripower 10.0",
        "power_kw": 10.0, "efficiency_percent": 98.3, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 33.0, "price_net": 2300.0, "price_gross": 2737.0,
        "warranty_years": 10, "weight_kg": 29.0, "features": ["SMA Smart Connected"],
        "is_hybrid": False, "is_active": True
    },
    {
        "id": 4, "manufacturer": "SMA", "model_name": "Sunny Tripower 8.0 Smart Energy",
        "power_kw": 8.0, "efficiency_percent": 97.5, "max_dc_voltage": 800,
        "mppt_count": 2, "max_dc_current": 15.0, "price_net": 3500.0, "price_gross": 4165.0,
        "warranty_years": 10, "weight_kg": 60.0, "features": ["Hybrid", "Notstrom", "Speicher integriert"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 5, "manufacturer": "Huawei", "model_name": "SUN2000-10KTL-M1",
        "power_kw": 10.0, "efficiency_percent": 98.6, "max_dc_voltage": 1100,
        "mppt_count": 2, "max_dc_current": 27.5, "price_net": 1800.0, "price_gross": 2142.0,
        "warranty_years": 10, "weight_kg": 23.0, "features": ["AI-Optimierung", "WLAN"],
        "is_hybrid": False, "is_active": True
    },
    {
        "id": 6, "manufacturer": "Huawei", "model_name": "SUN2000-8KTL-M1 (Hybrid)",
        "power_kw": 8.0, "efficiency_percent": 98.4, "max_dc_voltage": 1100,
        "mppt_count": 2, "max_dc_current": 25.0, "price_net": 2200.0, "price_gross": 2618.0,
        "warranty_years": 10, "weight_kg": 24.0, "features": ["Hybrid", "LUNA2000 kompatibel"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 7, "manufacturer": "Kostal", "model_name": "PLENTICORE plus 10",
        "power_kw": 10.0, "efficiency_percent": 98.5, "max_dc_voltage": 1000,
        "mppt_count": 3, "max_dc_current": 16.5, "price_net": 2400.0, "price_gross": 2856.0,
        "warranty_years": 10, "weight_kg": 22.0, "features": ["3 MPPT", "Hybrid-fähig"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 8, "manufacturer": "GoodWe", "model_name": "GW10K-ET",
        "power_kw": 10.0, "efficiency_percent": 98.0, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 26.0, "price_net": 1600.0, "price_gross": 1904.0,
        "warranty_years": 10, "weight_kg": 28.0, "features": ["Hybrid", "Notstrom"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 9, "manufacturer": "Sungrow", "model_name": "SG10RT",
        "power_kw": 10.0, "efficiency_percent": 98.5, "max_dc_voltage": 1100,
        "mppt_count": 2, "max_dc_current": 30.0, "price_net": 1500.0, "price_gross": 1785.0,
        "warranty_years": 10, "weight_kg": 24.0, "features": ["Kompakt", "Leise"],
        "is_hybrid": False, "is_active": True
    },
    {
        "id": 10, "manufacturer": "Sungrow", "model_name": "SH10RT (Hybrid)",
        "power_kw": 10.0, "efficiency_percent": 97.8, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 25.0, "price_net": 2000.0, "price_gross": 2380.0,
        "warranty_years": 10, "weight_kg": 26.0, "features": ["Hybrid", "Notstrom", "200% PV-Überbelegung"],
        "is_hybrid": True, "is_active": True
    },
    {
        "id": 11, "manufacturer": "Fronius", "model_name": "Primo 5.0-1",
        "power_kw": 5.0, "efficiency_percent": 98.0, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 18.0, "price_net": 1400.0, "price_gross": 1666.0,
        "warranty_years": 10, "weight_kg": 21.5, "features": ["Einphasig", "Kompakt"],
        "is_hybrid": False, "is_active": True
    },
    {
        "id": 12, "manufacturer": "SMA", "model_name": "Sunny Tripower 15.0",
        "power_kw": 15.0, "efficiency_percent": 98.4, "max_dc_voltage": 1000,
        "mppt_count": 2, "max_dc_current": 33.0, "price_net": 2800.0, "price_gross": 3332.0,
        "warranty_years": 10, "weight_kg": 33.0, "features": ["Große Anlagen"],
        "is_hybrid": False, "is_active": True
    },
]


# ==================== Helper Functions ====================

def get_inverter_by_id(inverter_id: int) -> Optional[Dict]:
    """Get inverter by ID from sample data"""
    for inv in SAMPLE_INVERTERS:
        if inv["id"] == inverter_id:
            return inv
    return None


def calculate_sizing(request: InverterSizingRequest) -> Dict[str, Any]:
    """Calculate inverter sizing requirements"""
    pv_power = request.pv_power_kwp
    string_voltage = request.module_voltage_vmp * request.modules_per_string
    total_current = request.module_current_imp * request.number_of_strings
    
    return {
        "required_power_kw": round(pv_power * 0.9, 2),
        "recommended_power_range": {
            "min_kw": round(pv_power * 0.8, 2),
            "optimal_kw": round(pv_power * 0.9, 2),
            "max_kw": round(pv_power * 1.0, 2)
        },
        "dc_specifications": {
            "string_voltage": round(string_voltage, 1),
            "required_max_voltage": round(string_voltage * 1.2, 1),
            "total_current": round(total_current, 1),
            "required_max_current": round(total_current * 1.1, 1)
        },
        "mppt_configuration": {
            "recommended_mppt_count": 2 if request.number_of_strings <= 4 else 3,
            "strings_per_mppt": request.number_of_strings // 2,
            "current_per_mppt": round(total_current / 2, 1)
        },
        "sizing_ratio": {
            "dc_ac_ratio": 1.11,
            "description": "DC/AC-Verhältnis (PV-Leistung / Wechselrichterleistung)"
        }
    }


def select_best_inverter(request: InverterSelectionRequest) -> Dict[str, Any]:
    """Select best inverter based on requirements"""
    candidates = SAMPLE_INVERTERS.copy()
    
    # Filter by hybrid requirement
    if request.is_hybrid_required:
        candidates = [inv for inv in candidates if inv["is_hybrid"]]
    
    # Filter by manufacturer preference
    if request.preferred_manufacturer:
        preferred = [inv for inv in candidates 
                    if inv["manufacturer"].lower() == request.preferred_manufacturer.lower()]
        if preferred:
            candidates = preferred
    
    # Score and sort candidates
    scored = []
    optimal_power = request.pv_power_kwp * 0.9
    
    for inv in candidates:
        score = 0
        
        # Power match (40 points)
        power_diff = abs(inv["power_kw"] - optimal_power)
        if power_diff <= optimal_power * 0.2:
            score += 40 * (1 - power_diff / optimal_power)
        
        # Efficiency (30 points)
        score += (inv["efficiency_percent"] - 95) * 6
        
        # Price (20 points) - lower is better
        max_price = 4000
        score += 20 * (1 - min(inv["price_net"], max_price) / max_price)
        
        # Features (10 points)
        if request.required_features:
            matching = sum(1 for f in request.required_features 
                         if any(f.lower() in feat.lower() for feat in inv["features"]))
            score += 10 * (matching / len(request.required_features))
        
        scored.append((score, inv))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    
    return {
        "selected_inverter": best,
        "selection_score": round(scored[0][0], 1),
        "sizing_ratio": round(request.pv_power_kwp / best["power_kw"], 2),
        "alternatives": [inv for _, inv in scored[1:4]],
        "reasoning": f"Wechselrichter {best['model_name']} ausgewählt: "
                    f"{best['power_kw']}kW, {best['efficiency_percent']}% Wirkungsgrad"
    }


# ==================== API Endpoints ====================

@router.get("/", response_model=List[InverterResponse])
async def list_inverters(
    active_only: bool = Query(True),
    hybrid_only: bool = Query(False),
    manufacturer: Optional[str] = Query(None)
):
    """Get all inverters with optional filters"""
    result = SAMPLE_INVERTERS.copy()
    
    if active_only:
        result = [inv for inv in result if inv["is_active"]]
    if hybrid_only:
        result = [inv for inv in result if inv["is_hybrid"]]
    if manufacturer:
        result = [inv for inv in result 
                 if inv["manufacturer"].lower() == manufacturer.lower()]
    
    return result


@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers():
    """Get list of all inverter manufacturers"""
    manufacturers = list(set(inv["manufacturer"] for inv in SAMPLE_INVERTERS))
    return sorted(manufacturers)


@router.get("/{inverter_id}", response_model=InverterResponse)
async def get_inverter(inverter_id: int):
    """Get inverter by ID"""
    inverter = get_inverter_by_id(inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
    return inverter


@router.post("/calculate-sizing", response_model=InverterSizingResponse)
async def calculate_inverter_sizing(request: InverterSizingRequest):
    """Calculate inverter sizing requirements based on PV system"""
    return calculate_sizing(request)


@router.post("/select")
async def select_inverter(request: InverterSelectionRequest):
    """Select optimal inverter for PV system"""
    return select_best_inverter(request)


@router.post("/check-compatibility")
async def check_compatibility(request: CompatibilityCheckRequest):
    """Check inverter compatibility with PV system"""
    inverter = get_inverter_by_id(request.inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
    
    checks = []
    is_compatible = True
    
    # Power check
    sizing_ratio = request.pv_power_kwp / inverter["power_kw"]
    if 0.8 <= sizing_ratio <= 1.2:
        checks.append({"check": "Leistung", "status": "OK", 
                      "details": f"DC/AC: {sizing_ratio:.2f}"})
    else:
        is_compatible = False
        checks.append({"check": "Leistung", "status": "FEHLER",
                      "details": f"DC/AC: {sizing_ratio:.2f} (optimal: 0.8-1.2)"})
    
    # Voltage check
    if request.string_voltage <= inverter["max_dc_voltage"] * 0.9:
        checks.append({"check": "Spannung", "status": "OK",
                      "details": f"{request.string_voltage}V <= {inverter['max_dc_voltage']}V"})
    else:
        is_compatible = False
        checks.append({"check": "Spannung", "status": "FEHLER",
                      "details": f"{request.string_voltage}V > {inverter['max_dc_voltage']}V"})
    
    # Current check
    current_per_mppt = request.total_current / inverter["mppt_count"]
    if current_per_mppt <= inverter["max_dc_current"]:
        checks.append({"check": "Strom", "status": "OK",
                      "details": f"{current_per_mppt:.1f}A <= {inverter['max_dc_current']}A"})
    else:
        is_compatible = False
        checks.append({"check": "Strom", "status": "FEHLER",
                      "details": f"{current_per_mppt:.1f}A > {inverter['max_dc_current']}A"})
    
    return {
        "is_compatible": is_compatible,
        "compatibility_score": sum(1 for c in checks if c["status"] == "OK") / len(checks) * 100,
        "checks": checks,
        "inverter": inverter
    }


@router.post("/multi-inverter")
async def create_multi_inverter_config(request: MultiInverterRequest):
    """Create multi-inverter configuration for large systems"""
    pv_power = request.pv_power_kwp
    
    # Determine if multi-inverter is needed
    if pv_power <= 15 and len(request.roof_sections) <= 1:
        # Single inverter sufficient
        selection = select_best_inverter(InverterSelectionRequest(pv_power_kwp=pv_power))
        return {
            "configuration_type": "single",
            "inverter_count": 1,
            "inverters": [selection["selected_inverter"]],
            "total_power_kw": selection["selected_inverter"]["power_kw"],
            "reasoning": "Einzelwechselrichter ausreichend"
        }
    
    # Multi-inverter configuration
    if len(request.roof_sections) > 1:
        inverter_count = len(request.roof_sections)
    else:
        inverter_count = max(2, int(pv_power / 10))
    
    power_per_inverter = pv_power / inverter_count
    
    inverters = []
    for i in range(inverter_count):
        selection = select_best_inverter(
            InverterSelectionRequest(pv_power_kwp=power_per_inverter)
        )
        inverters.append(selection["selected_inverter"])
    
    total_power = sum(inv["power_kw"] for inv in inverters)
    
    return {
        "configuration_type": "multi",
        "inverter_count": inverter_count,
        "inverters": inverters,
        "total_power_kw": total_power,
        "sizing_ratio": round(pv_power / total_power, 2),
        "power_distribution": [
            {"inverter_index": i, "assigned_kwp": round(power_per_inverter, 2)}
            for i in range(inverter_count)
        ],
        "reasoning": f"Multi-Wechselrichter: {inverter_count}x für {pv_power}kWp"
    }


@router.get("/health/check")
async def health_check():
    """Check inverter service health"""
    return {
        "status": "healthy",
        "inverter_count": len(SAMPLE_INVERTERS),
        "manufacturers": len(set(inv["manufacturer"] for inv in SAMPLE_INVERTERS))
    }
