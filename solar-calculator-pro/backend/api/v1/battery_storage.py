"""
Battery Storage Configuration API Endpoints

Provides REST API for battery storage selection from product database,
specifications display, sizing calculations, and ROI analysis.

Requirements: funktionen.txt - "Batteriespeicher"
Task: 250. Battery Storage Configuration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/battery-storage", tags=["Battery Storage"])


# ==================== Pydantic Models ====================

class BatteryStorageBase(BaseModel):
    """Base battery storage model"""
    id: Optional[int] = None
    manufacturer: str
    model_name: str
    capacity_kwh: float = Field(..., description="Usable capacity in kWh")
    nominal_capacity_kwh: float = Field(default=0.0, description="Nominal capacity in kWh")
    max_power_kw: float = Field(default=0.0, description="Max charge/discharge power in kW")
    efficiency_percent: float = Field(default=95.0, description="Round-trip efficiency in %")
    cycle_life: int = Field(default=6000, description="Number of full cycles")
    warranty_years: int = Field(default=10)
    warranty_cycles: int = Field(default=0, description="Warranty cycles (if specified)")
    depth_of_discharge: float = Field(default=100.0, description="DoD in %")
    price_net: float = Field(default=0.0, description="Net price in EUR")
    price_gross: float = Field(default=0.0, description="Gross price in EUR")
    price_per_kwh: float = Field(default=0.0, description="Price per kWh in EUR")
    weight_kg: float = Field(default=0.0)
    dimensions: Optional[str] = None
    battery_type: str = Field(default="LiFePO4", description="Battery chemistry")
    features: List[str] = Field(default_factory=list)
    is_modular: bool = Field(default=False, description="Can be expanded")
    min_modules: int = Field(default=1)
    max_modules: int = Field(default=1)
    compatible_inverters: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)


class BatteryStorageResponse(BatteryStorageBase):
    """Battery storage response with additional fields"""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BatterySizingRequest(BaseModel):
    """Request for battery sizing calculation"""
    annual_consumption_kwh: float = Field(..., description="Annual electricity consumption in kWh")
    pv_system_kwp: float = Field(..., description="PV system size in kWp")
    self_consumption_target: float = Field(default=70.0, description="Target self-consumption rate in %")
    autarky_target: float = Field(default=60.0, description="Target autarky rate in %")
    daily_consumption_kwh: Optional[float] = None


class BatterySizingResponse(BaseModel):
    """Response with sizing calculations"""
    recommended_capacity_kwh: float
    capacity_range: Dict[str, float]
    expected_autarky: float
    expected_self_consumption: float
    daily_cycles: float
    sizing_factors: Dict[str, Any]


class BatterySelectionRequest(BaseModel):
    """Request for battery selection"""
    required_capacity_kwh: float
    preferred_manufacturer: Optional[str] = None
    max_budget: Optional[float] = None
    required_features: List[str] = Field(default_factory=list)
    compatible_inverter: Optional[str] = None
    is_modular_required: bool = Field(default=False)


class BatteryROIRequest(BaseModel):
    """Request for ROI analysis"""
    battery_id: int
    annual_consumption_kwh: float
    pv_production_kwh: float
    electricity_price: float = Field(default=0.35, description="EUR/kWh")
    feed_in_tariff: float = Field(default=0.082, description="EUR/kWh")
    electricity_price_increase: float = Field(default=3.0, description="Annual increase in %")
    analysis_years: int = Field(default=20)


class BatteryROIResponse(BaseModel):
    """Response with ROI analysis"""
    payback_years: float
    total_savings_eur: float
    annual_savings_eur: float
    roi_percent: float
    npv_eur: float
    yearly_breakdown: List[Dict[str, Any]]


# ==================== Sample Data ====================

SAMPLE_BATTERIES = [
    {
        "id": 1, "manufacturer": "BYD", "model_name": "Battery-Box Premium HVS 5.1",
        "capacity_kwh": 5.1, "nominal_capacity_kwh": 5.12, "max_power_kw": 5.0,
        "efficiency_percent": 95.3, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 3200.0, "price_gross": 3808.0, "price_per_kwh": 627.0,
        "weight_kg": 83.0, "dimensions": "585×298×625mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Hochvolt", "Notstromfähig"],
        "is_modular": True, "min_modules": 2, "max_modules": 4,
        "compatible_inverters": ["Fronius", "SMA", "Kostal", "Huawei"],
        "is_active": True
    },
    {
        "id": 2, "manufacturer": "BYD", "model_name": "Battery-Box Premium HVS 10.2",
        "capacity_kwh": 10.2, "nominal_capacity_kwh": 10.24, "max_power_kw": 10.0,
        "efficiency_percent": 95.3, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 5800.0, "price_gross": 6902.0, "price_per_kwh": 569.0,
        "weight_kg": 166.0, "dimensions": "585×298×1180mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Hochvolt", "Notstromfähig"],
        "is_modular": True, "min_modules": 2, "max_modules": 4,
        "compatible_inverters": ["Fronius", "SMA", "Kostal", "Huawei"],
        "is_active": True
    },
    {
        "id": 3, "manufacturer": "Huawei", "model_name": "LUNA2000-5-S0",
        "capacity_kwh": 5.0, "nominal_capacity_kwh": 5.0, "max_power_kw": 5.0,
        "efficiency_percent": 97.0, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 2900.0, "price_gross": 3451.0, "price_per_kwh": 580.0,
        "weight_kg": 63.8, "dimensions": "670×150×600mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Hochvolt", "Smart String ESS"],
        "is_modular": True, "min_modules": 1, "max_modules": 3,
        "compatible_inverters": ["Huawei"],
        "is_active": True
    },
    {
        "id": 4, "manufacturer": "Huawei", "model_name": "LUNA2000-10-S0",
        "capacity_kwh": 10.0, "nominal_capacity_kwh": 10.0, "max_power_kw": 5.0,
        "efficiency_percent": 97.0, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 5200.0, "price_gross": 6188.0, "price_per_kwh": 520.0,
        "weight_kg": 127.6, "dimensions": "670×150×1100mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Hochvolt", "Smart String ESS"],
        "is_modular": True, "min_modules": 2, "max_modules": 3,
        "compatible_inverters": ["Huawei"],
        "is_active": True
    },
    {
        "id": 5, "manufacturer": "Huawei", "model_name": "LUNA2000-15-S0",
        "capacity_kwh": 15.0, "nominal_capacity_kwh": 15.0, "max_power_kw": 5.0,
        "efficiency_percent": 97.0, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 7500.0, "price_gross": 8925.0, "price_per_kwh": 500.0,
        "weight_kg": 191.4, "dimensions": "670×150×1600mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Hochvolt", "Smart String ESS"],
        "is_modular": True, "min_modules": 3, "max_modules": 3,
        "compatible_inverters": ["Huawei"],
        "is_active": True
    },
    {
        "id": 6, "manufacturer": "SMA", "model_name": "Sunny Boy Storage 5.0",
        "capacity_kwh": 5.0, "nominal_capacity_kwh": 5.0, "max_power_kw": 5.0,
        "efficiency_percent": 96.0, "cycle_life": 5000, "warranty_years": 10,
        "warranty_cycles": 5000, "depth_of_discharge": 90.0,
        "price_net": 3500.0, "price_gross": 4165.0, "price_per_kwh": 700.0,
        "weight_kg": 60.0, "dimensions": "460×435×180mm", "battery_type": "Li-Ion",
        "features": ["Integrierter Wechselrichter", "Notstrom"],
        "is_modular": False, "min_modules": 1, "max_modules": 1,
        "compatible_inverters": ["SMA"],
        "is_active": True
    },
    {
        "id": 7, "manufacturer": "Fronius", "model_name": "BYD Battery-Box Premium HVM 8.3",
        "capacity_kwh": 8.3, "nominal_capacity_kwh": 8.28, "max_power_kw": 8.0,
        "efficiency_percent": 95.3, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 100.0,
        "price_net": 4800.0, "price_gross": 5712.0, "price_per_kwh": 578.0,
        "weight_kg": 132.0, "dimensions": "585×298×960mm", "battery_type": "LiFePO4",
        "features": ["Modular", "Mittelspannung", "Notstromfähig"],
        "is_modular": True, "min_modules": 3, "max_modules": 8,
        "compatible_inverters": ["Fronius", "SMA", "Kostal"],
        "is_active": True
    },
    {
        "id": 8, "manufacturer": "Sonnen", "model_name": "sonnenBatterie 10 5.5",
        "capacity_kwh": 5.5, "nominal_capacity_kwh": 5.5, "max_power_kw": 3.3,
        "efficiency_percent": 92.0, "cycle_life": 10000, "warranty_years": 10,
        "warranty_cycles": 10000, "depth_of_discharge": 100.0,
        "price_net": 6500.0, "price_gross": 7735.0, "price_per_kwh": 1182.0,
        "weight_kg": 88.0, "dimensions": "1370×660×220mm", "battery_type": "LiFePO4",
        "features": ["All-in-One", "Smart Home", "sonnenFlat"],
        "is_modular": True, "min_modules": 1, "max_modules": 4,
        "compatible_inverters": ["Sonnen (integriert)"],
        "is_active": True
    },
    {
        "id": 9, "manufacturer": "Sonnen", "model_name": "sonnenBatterie 10 11",
        "capacity_kwh": 11.0, "nominal_capacity_kwh": 11.0, "max_power_kw": 4.6,
        "efficiency_percent": 92.0, "cycle_life": 10000, "warranty_years": 10,
        "warranty_cycles": 10000, "depth_of_discharge": 100.0,
        "price_net": 11000.0, "price_gross": 13090.0, "price_per_kwh": 1000.0,
        "weight_kg": 132.0, "dimensions": "1370×660×220mm", "battery_type": "LiFePO4",
        "features": ["All-in-One", "Smart Home", "sonnenFlat"],
        "is_modular": True, "min_modules": 2, "max_modules": 4,
        "compatible_inverters": ["Sonnen (integriert)"],
        "is_active": True
    },
    {
        "id": 10, "manufacturer": "Tesla", "model_name": "Powerwall 2",
        "capacity_kwh": 13.5, "nominal_capacity_kwh": 14.0, "max_power_kw": 5.0,
        "efficiency_percent": 90.0, "cycle_life": 5000, "warranty_years": 10,
        "warranty_cycles": 0, "depth_of_discharge": 100.0,
        "price_net": 8500.0, "price_gross": 10115.0, "price_per_kwh": 630.0,
        "weight_kg": 114.0, "dimensions": "1150×755×155mm", "battery_type": "Li-Ion NMC",
        "features": ["Komplett integriert", "App-Steuerung", "Notstrom"],
        "is_modular": True, "min_modules": 1, "max_modules": 10,
        "compatible_inverters": ["Tesla Gateway"],
        "is_active": True
    },
    {
        "id": 11, "manufacturer": "LG", "model_name": "RESU 10H",
        "capacity_kwh": 9.8, "nominal_capacity_kwh": 9.8, "max_power_kw": 5.0,
        "efficiency_percent": 95.0, "cycle_life": 6000, "warranty_years": 10,
        "warranty_cycles": 6000, "depth_of_discharge": 95.0,
        "price_net": 4500.0, "price_gross": 5355.0, "price_per_kwh": 459.0,
        "weight_kg": 75.0, "dimensions": "452×483×227mm", "battery_type": "Li-Ion NMC",
        "features": ["Kompakt", "Hochvolt"],
        "is_modular": False, "min_modules": 1, "max_modules": 1,
        "compatible_inverters": ["SMA", "Fronius", "SolarEdge"],
        "is_active": True
    },
    {
        "id": 12, "manufacturer": "E3/DC", "model_name": "S10 E PRO",
        "capacity_kwh": 13.0, "nominal_capacity_kwh": 13.0, "max_power_kw": 6.0,
        "efficiency_percent": 94.0, "cycle_life": 8000, "warranty_years": 10,
        "warranty_cycles": 8000, "depth_of_discharge": 100.0,
        "price_net": 12000.0, "price_gross": 14280.0, "price_per_kwh": 923.0,
        "weight_kg": 180.0, "dimensions": "1040×1040×420mm", "battery_type": "LiFePO4",
        "features": ["All-in-One", "Notstrom", "Wallbox-Integration"],
        "is_modular": True, "min_modules": 1, "max_modules": 3,
        "compatible_inverters": ["E3/DC (integriert)"],
        "is_active": True
    },
]

# Special "kein Speicher" option
NO_STORAGE_OPTION = {
    "id": 0, "manufacturer": "-", "model_name": "Kein Speicher",
    "capacity_kwh": 0.0, "nominal_capacity_kwh": 0.0, "max_power_kw": 0.0,
    "efficiency_percent": 0.0, "cycle_life": 0, "warranty_years": 0,
    "warranty_cycles": 0, "depth_of_discharge": 0.0,
    "price_net": 0.0, "price_gross": 0.0, "price_per_kwh": 0.0,
    "weight_kg": 0.0, "dimensions": "-", "battery_type": "-",
    "features": [], "is_modular": False, "min_modules": 0, "max_modules": 0,
    "compatible_inverters": [], "is_active": True
}


# ==================== Helper Functions ====================

def get_battery_by_id(battery_id: int) -> Optional[Dict]:
    """Get battery by ID from sample data"""
    if battery_id == 0:
        return NO_STORAGE_OPTION
    for bat in SAMPLE_BATTERIES:
        if bat["id"] == battery_id:
            return bat
    return None


def calculate_battery_sizing(request: BatterySizingRequest) -> Dict[str, Any]:
    """Calculate optimal battery size based on consumption and PV system"""
    annual_consumption = request.annual_consumption_kwh
    pv_kwp = request.pv_system_kwp
    
    # Calculate daily consumption
    daily_consumption = request.daily_consumption_kwh or (annual_consumption / 365)
    
    # Estimate PV production (1000 kWh/kWp in Germany average)
    annual_pv_production = pv_kwp * 1000
    daily_pv_production = annual_pv_production / 365
    
    # Calculate surplus energy (potential for storage)
    # Assume 30% direct consumption, 70% available for storage/feed-in
    direct_consumption_rate = 0.30
    surplus_energy = daily_pv_production * (1 - direct_consumption_rate)
    
    # Evening/night consumption (typically 40% of daily)
    evening_consumption = daily_consumption * 0.40
    
    # Recommended capacity: cover evening consumption from surplus
    recommended_capacity = min(surplus_energy, evening_consumption)
    
    # Capacity range
    min_capacity = recommended_capacity * 0.7
    max_capacity = recommended_capacity * 1.5
    
    # Expected autarky with storage
    storage_contribution = min(recommended_capacity * 0.9, evening_consumption)
    total_self_consumed = (daily_pv_production * direct_consumption_rate) + storage_contribution
    expected_autarky = min(100, (total_self_consumed / daily_consumption) * 100)
    
    # Expected self-consumption
    total_used_from_pv = (daily_pv_production * direct_consumption_rate) + storage_contribution
    expected_self_consumption = min(100, (total_used_from_pv / daily_pv_production) * 100)
    
    # Daily cycles
    daily_cycles = storage_contribution / recommended_capacity if recommended_capacity > 0 else 0
    
    return {
        "recommended_capacity_kwh": round(recommended_capacity, 1),
        "capacity_range": {
            "min_kwh": round(min_capacity, 1),
            "optimal_kwh": round(recommended_capacity, 1),
            "max_kwh": round(max_capacity, 1)
        },
        "expected_autarky": round(expected_autarky, 1),
        "expected_self_consumption": round(expected_self_consumption, 1),
        "daily_cycles": round(daily_cycles, 2),
        "sizing_factors": {
            "daily_consumption_kwh": round(daily_consumption, 1),
            "daily_pv_production_kwh": round(daily_pv_production, 1),
            "surplus_energy_kwh": round(surplus_energy, 1),
            "evening_consumption_kwh": round(evening_consumption, 1)
        }
    }


def select_best_battery(request: BatterySelectionRequest) -> Dict[str, Any]:
    """Select best battery based on requirements"""
    candidates = SAMPLE_BATTERIES.copy()
    
    # Filter by capacity (within 30% of required)
    min_cap = request.required_capacity_kwh * 0.7
    max_cap = request.required_capacity_kwh * 1.5
    candidates = [bat for bat in candidates 
                 if min_cap <= bat["capacity_kwh"] <= max_cap]
    
    # Filter by manufacturer preference
    if request.preferred_manufacturer:
        preferred = [bat for bat in candidates 
                   if bat["manufacturer"].lower() == request.preferred_manufacturer.lower()]
        if preferred:
            candidates = preferred
    
    # Filter by budget
    if request.max_budget:
        candidates = [bat for bat in candidates if bat["price_gross"] <= request.max_budget]
    
    # Filter by modular requirement
    if request.is_modular_required:
        candidates = [bat for bat in candidates if bat["is_modular"]]
    
    # Filter by compatible inverter
    if request.compatible_inverter:
        compatible = [bat for bat in candidates 
                     if any(request.compatible_inverter.lower() in inv.lower() 
                           for inv in bat["compatible_inverters"])]
        if compatible:
            candidates = compatible
    
    if not candidates:
        return {
            "selected_battery": None,
            "selection_score": 0,
            "alternatives": [],
            "reasoning": "Keine passende Batterie gefunden"
        }
    
    # Score and sort candidates
    scored = []
    for bat in candidates:
        score = 0
        
        # Capacity match (30 points)
        cap_diff = abs(bat["capacity_kwh"] - request.required_capacity_kwh)
        cap_score = 30 * (1 - cap_diff / request.required_capacity_kwh)
        score += max(0, cap_score)
        
        # Price per kWh (25 points) - lower is better
        max_price_per_kwh = 1200
        price_score = 25 * (1 - min(bat["price_per_kwh"], max_price_per_kwh) / max_price_per_kwh)
        score += price_score
        
        # Efficiency (20 points)
        eff_score = (bat["efficiency_percent"] - 85) * 1.33
        score += min(20, max(0, eff_score))
        
        # Cycle life (15 points)
        cycle_score = min(15, bat["cycle_life"] / 1000 * 1.5)
        score += cycle_score
        
        # Features (10 points)
        if request.required_features:
            matching = sum(1 for f in request.required_features 
                         if any(f.lower() in feat.lower() for feat in bat["features"]))
            score += 10 * (matching / len(request.required_features))
        
        scored.append((score, bat))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    
    return {
        "selected_battery": best,
        "selection_score": round(scored[0][0], 1),
        "capacity_match": round(best["capacity_kwh"] / request.required_capacity_kwh * 100, 1),
        "alternatives": [bat for _, bat in scored[1:4]],
        "reasoning": f"Batterie {best['model_name']} ausgewählt: "
                    f"{best['capacity_kwh']}kWh, {best['efficiency_percent']}% Effizienz, "
                    f"{best['price_per_kwh']}€/kWh"
    }


def calculate_battery_roi(battery: Dict, request: BatteryROIRequest) -> Dict[str, Any]:
    """Calculate ROI for battery storage"""
    if battery["id"] == 0:  # No storage
        return {
            "payback_years": 0,
            "total_savings_eur": 0,
            "annual_savings_eur": 0,
            "roi_percent": 0,
            "npv_eur": 0,
            "yearly_breakdown": []
        }
    
    capacity = battery["capacity_kwh"]
    efficiency = battery["efficiency_percent"] / 100
    cycle_life = battery["cycle_life"]
    investment = battery["price_gross"]
    
    # Calculate annual storage throughput
    daily_cycles = 0.8  # Assume 0.8 cycles per day average
    annual_cycles = daily_cycles * 365
    annual_throughput = capacity * annual_cycles * efficiency
    
    # Calculate savings per kWh stored
    # Savings = electricity price - feed-in tariff (what you would have gotten)
    savings_per_kwh = request.electricity_price - request.feed_in_tariff
    
    yearly_breakdown = []
    cumulative_savings = 0
    payback_year = None
    
    for year in range(1, request.analysis_years + 1):
        # Adjust electricity price for inflation
        current_electricity_price = request.electricity_price * (
            (1 + request.electricity_price_increase / 100) ** (year - 1)
        )
        current_savings_per_kwh = current_electricity_price - request.feed_in_tariff
        
        # Calculate degradation (assume 2% per year)
        degradation_factor = max(0.7, 1 - 0.02 * (year - 1))
        
        # Check if within cycle life
        total_cycles = annual_cycles * year
        if total_cycles > cycle_life:
            degradation_factor *= 0.5  # Significant degradation after cycle life
        
        annual_savings = annual_throughput * current_savings_per_kwh * degradation_factor
        cumulative_savings += annual_savings
        
        if payback_year is None and cumulative_savings >= investment:
            payback_year = year
        
        yearly_breakdown.append({
            "year": year,
            "annual_savings_eur": round(annual_savings, 2),
            "cumulative_savings_eur": round(cumulative_savings, 2),
            "electricity_price_eur": round(current_electricity_price, 4),
            "degradation_percent": round((1 - degradation_factor) * 100, 1)
        })
    
    total_savings = cumulative_savings
    annual_average_savings = total_savings / request.analysis_years
    roi_percent = ((total_savings - investment) / investment) * 100
    
    # Simple NPV calculation (5% discount rate)
    discount_rate = 0.05
    npv = -investment
    for i, year_data in enumerate(yearly_breakdown):
        npv += year_data["annual_savings_eur"] / ((1 + discount_rate) ** (i + 1))
    
    return {
        "payback_years": payback_year or request.analysis_years,
        "total_savings_eur": round(total_savings, 2),
        "annual_savings_eur": round(annual_average_savings, 2),
        "roi_percent": round(roi_percent, 1),
        "npv_eur": round(npv, 2),
        "yearly_breakdown": yearly_breakdown
    }


# ==================== API Endpoints ====================

@router.get("/", response_model=List[BatteryStorageResponse])
async def list_batteries(
    active_only: bool = Query(True),
    include_no_storage: bool = Query(True),
    manufacturer: Optional[str] = Query(None),
    min_capacity: Optional[float] = Query(None),
    max_capacity: Optional[float] = Query(None),
    modular_only: bool = Query(False)
):
    """Get all battery storage options with optional filters"""
    result = SAMPLE_BATTERIES.copy()
    
    if active_only:
        result = [bat for bat in result if bat["is_active"]]
    if manufacturer:
        result = [bat for bat in result 
                 if bat["manufacturer"].lower() == manufacturer.lower()]
    if min_capacity is not None:
        result = [bat for bat in result if bat["capacity_kwh"] >= min_capacity]
    if max_capacity is not None:
        result = [bat for bat in result if bat["capacity_kwh"] <= max_capacity]
    if modular_only:
        result = [bat for bat in result if bat["is_modular"]]
    
    # Add "kein Speicher" option at the beginning
    if include_no_storage:
        result = [NO_STORAGE_OPTION] + result
    
    return result


@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers():
    """Get list of all battery manufacturers"""
    manufacturers = list(set(bat["manufacturer"] for bat in SAMPLE_BATTERIES))
    return sorted(manufacturers)


@router.get("/no-storage", response_model=BatteryStorageResponse)
async def get_no_storage_option():
    """Get the 'kein Speicher' (no storage) option"""
    return NO_STORAGE_OPTION


@router.get("/{battery_id}", response_model=BatteryStorageResponse)
async def get_battery(battery_id: int):
    """Get battery by ID"""
    battery = get_battery_by_id(battery_id)
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    return battery


@router.post("/calculate-sizing", response_model=BatterySizingResponse)
async def calculate_sizing(request: BatterySizingRequest):
    """Calculate optimal battery size based on consumption and PV system"""
    return calculate_battery_sizing(request)


@router.post("/select")
async def select_battery(request: BatterySelectionRequest):
    """Select optimal battery for requirements"""
    return select_best_battery(request)


@router.post("/calculate-roi", response_model=BatteryROIResponse)
async def calculate_roi(request: BatteryROIRequest):
    """Calculate ROI analysis for battery storage"""
    battery = get_battery_by_id(request.battery_id)
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    return calculate_battery_roi(battery, request)


@router.get("/compare/{battery_ids}")
async def compare_batteries(battery_ids: str):
    """Compare multiple batteries by IDs (comma-separated)"""
    ids = [int(id.strip()) for id in battery_ids.split(",")]
    batteries = []
    
    for bid in ids:
        battery = get_battery_by_id(bid)
        if battery:
            batteries.append(battery)
    
    if not batteries:
        raise HTTPException(status_code=404, detail="No batteries found")
    
    # Create comparison
    comparison = {
        "batteries": batteries,
        "comparison": {
            "capacity_range": {
                "min": min(b["capacity_kwh"] for b in batteries),
                "max": max(b["capacity_kwh"] for b in batteries)
            },
            "price_range": {
                "min": min(b["price_gross"] for b in batteries),
                "max": max(b["price_gross"] for b in batteries)
            },
            "price_per_kwh_range": {
                "min": min(b["price_per_kwh"] for b in batteries),
                "max": max(b["price_per_kwh"] for b in batteries)
            },
            "efficiency_range": {
                "min": min(b["efficiency_percent"] for b in batteries),
                "max": max(b["efficiency_percent"] for b in batteries)
            },
            "best_value": min(batteries, key=lambda b: b["price_per_kwh"])["model_name"],
            "highest_efficiency": max(batteries, key=lambda b: b["efficiency_percent"])["model_name"],
            "longest_warranty": max(batteries, key=lambda b: b["warranty_years"])["model_name"]
        }
    }
    
    return comparison


@router.get("/compatible/{inverter_manufacturer}")
async def get_compatible_batteries(inverter_manufacturer: str):
    """Get batteries compatible with a specific inverter manufacturer"""
    compatible = [
        bat for bat in SAMPLE_BATTERIES
        if any(inverter_manufacturer.lower() in inv.lower() 
              for inv in bat["compatible_inverters"])
    ]
    
    return {
        "inverter_manufacturer": inverter_manufacturer,
        "compatible_batteries": compatible,
        "count": len(compatible)
    }


@router.get("/health/check")
async def health_check():
    """Check battery storage service health"""
    return {
        "status": "healthy",
        "battery_count": len(SAMPLE_BATTERIES),
        "manufacturers": len(set(bat["manufacturer"] for bat in SAMPLE_BATTERIES)),
        "capacity_range": {
            "min_kwh": min(b["capacity_kwh"] for b in SAMPLE_BATTERIES),
            "max_kwh": max(b["capacity_kwh"] for b in SAMPLE_BATTERIES)
        }
    }
