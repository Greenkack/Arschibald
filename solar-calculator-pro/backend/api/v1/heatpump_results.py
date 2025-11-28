"""
Heat Pump Calculation Results API

Provides REST API for heat pump calculation results:
- Annual performance factor (JAZ) calculation
- Annual cost savings vs. old heating system
- Amortization period with financing
- "Amortisations-Cheat" factor for demonstrations
- Heating cost comparison (old vs. new)

Requirements: funktionen.txt - "Ergebnisgrößen"
Task: 257. Heat Pump Calculation Results
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/heatpump/results", tags=["Heat Pump Results"])


# ==================== Enums ====================

class OldHeatingSystem(str, Enum):
    """Old heating system type"""
    OIL = "oil"
    GAS = "gas"
    ELECTRIC = "electric"
    COAL = "coal"
    WOOD = "wood"
    DISTRICT = "district"
    LPG = "lpg"


class HeatingSystemType(str, Enum):
    """Heating distribution system"""
    FLOOR_HEATING = "floor_heating"
    RADIATORS_LOW = "radiators_low"
    RADIATORS_HIGH = "radiators_high"
    MIXED = "mixed"


# ==================== Pydantic Models ====================

class CalculationRequest(BaseModel):
    """Request for heat pump calculation"""
    heating_demand_kwh: float = Field(..., gt=0, description="Jahresheizwärmebedarf in kWh")
    hot_water_demand_kwh: float = Field(default=0, ge=0, description="Warmwasserbedarf in kWh")
    heat_pump_cop: float = Field(default=4.0, ge=2.0, le=6.0, description="COP der Wärmepumpe")
    heating_system_type: HeatingSystemType = Field(default=HeatingSystemType.FLOOR_HEATING)
    old_heating_system: OldHeatingSystem = Field(default=OldHeatingSystem.GAS)
    old_system_efficiency: float = Field(default=0.9, ge=0.5, le=1.0)
    electricity_price_eur_kwh: float = Field(default=0.30, ge=0.1, le=1.0)
    old_fuel_price_eur_kwh: Optional[float] = Field(None, description="Alter Brennstoffpreis")
    heat_pump_price_eur: float = Field(default=15000, gt=0)
    installation_cost_eur: float = Field(default=5000, ge=0)
    subsidy_percent: float = Field(default=30, ge=0, le=70)
    amortization_cheat_factor: float = Field(default=1.0, ge=0.5, le=2.0, description="Demo-Faktor")


class JAZCalculationRequest(BaseModel):
    """Request for JAZ calculation"""
    cop_a7w35: float = Field(..., ge=2.0, le=7.0, description="COP bei A7/W35")
    cop_a2w35: float = Field(..., ge=2.0, le=6.0, description="COP bei A2/W35")
    cop_a_7w35: Optional[float] = Field(None, ge=1.5, le=5.0, description="COP bei A-7/W35")
    heating_system_type: HeatingSystemType = Field(default=HeatingSystemType.FLOOR_HEATING)
    climate_zone: str = Field(default="moderate", description="Klimazone")
    hot_water_share_percent: float = Field(default=15, ge=0, le=50)


class HeatingCostComparison(BaseModel):
    """Heating cost comparison result"""
    old_system: Dict[str, Any]
    new_system: Dict[str, Any]
    annual_savings_eur: float
    savings_percent: float
    co2_savings_kg: float


class AmortizationResult(BaseModel):
    """Amortization calculation result"""
    simple_payback_years: float
    adjusted_payback_years: float
    net_investment_eur: float
    annual_savings_eur: float
    total_savings_20_years_eur: float
    roi_20_years_percent: float


class CalculationResult(BaseModel):
    """Complete calculation result"""
    jaz: float
    electricity_consumption_kwh: float
    annual_electricity_cost_eur: float
    old_heating_cost_eur: float
    annual_savings_eur: float
    savings_percent: float
    co2_savings_kg: float
    amortization: AmortizationResult
    cost_comparison: HeatingCostComparison
    monthly_breakdown: List[Dict[str, float]]


# ==================== Constants ====================

# Fuel prices (EUR/kWh) - Default values
FUEL_PRICES = {
    OldHeatingSystem.OIL: 0.12,
    OldHeatingSystem.GAS: 0.10,
    OldHeatingSystem.ELECTRIC: 0.30,
    OldHeatingSystem.COAL: 0.08,
    OldHeatingSystem.WOOD: 0.06,
    OldHeatingSystem.DISTRICT: 0.11,
    OldHeatingSystem.LPG: 0.14
}

# CO2 factors (kg/kWh)
CO2_FACTORS = {
    OldHeatingSystem.OIL: 0.266,
    OldHeatingSystem.GAS: 0.201,
    OldHeatingSystem.ELECTRIC: 0.420,
    OldHeatingSystem.COAL: 0.338,
    OldHeatingSystem.WOOD: 0.036,
    OldHeatingSystem.DISTRICT: 0.180,
    OldHeatingSystem.LPG: 0.234
}

# Heat pump electricity CO2 factor
HP_ELECTRICITY_CO2 = 0.420  # kg/kWh (German grid mix)

# Flow temperature factors for JAZ calculation
FLOW_TEMP_FACTORS = {
    HeatingSystemType.FLOOR_HEATING: 1.0,      # 35°C
    HeatingSystemType.RADIATORS_LOW: 0.92,     # 45°C
    HeatingSystemType.RADIATORS_HIGH: 0.82,    # 55°C
    HeatingSystemType.MIXED: 0.90
}

# Climate zone factors
CLIMATE_FACTORS = {
    "mild": 1.05,
    "moderate": 1.0,
    "cold": 0.92,
    "very_cold": 0.85
}

# Monthly heating distribution (Germany average)
MONTHLY_HEATING_SHARE = [
    0.15,  # January
    0.13,  # February
    0.10,  # March
    0.06,  # April
    0.02,  # May
    0.00,  # June
    0.00,  # July
    0.00,  # August
    0.02,  # September
    0.08,  # October
    0.12,  # November
    0.14   # December
]

MONTH_NAMES = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]


# ==================== Helper Functions ====================

def calculate_jaz(
    cop_a7w35: float,
    cop_a2w35: float,
    cop_a_7w35: Optional[float],
    heating_system: HeatingSystemType,
    climate_zone: str,
    hot_water_share: float
) -> float:
    """Calculate annual performance factor (JAZ)"""
    # Weighted average COP based on temperature distribution
    # Simplified: 40% A7, 40% A2, 20% A-7
    if cop_a_7w35:
        weighted_cop = cop_a7w35 * 0.4 + cop_a2w35 * 0.4 + cop_a_7w35 * 0.2
    else:
        weighted_cop = cop_a7w35 * 0.5 + cop_a2w35 * 0.5
    
    # Apply flow temperature factor
    flow_factor = FLOW_TEMP_FACTORS.get(heating_system, 1.0)
    
    # Apply climate factor
    climate_factor = CLIMATE_FACTORS.get(climate_zone, 1.0)
    
    # Hot water reduces JAZ slightly (higher temperature needed)
    hot_water_factor = 1.0 - (hot_water_share / 100 * 0.1)
    
    jaz = weighted_cop * flow_factor * climate_factor * hot_water_factor
    
    return round(jaz, 2)


def calculate_electricity_consumption(
    heating_demand_kwh: float,
    hot_water_demand_kwh: float,
    jaz: float
) -> float:
    """Calculate annual electricity consumption"""
    total_demand = heating_demand_kwh + hot_water_demand_kwh
    return round(total_demand / jaz, 0)


def calculate_old_heating_cost(
    heating_demand_kwh: float,
    hot_water_demand_kwh: float,
    old_system: OldHeatingSystem,
    efficiency: float,
    fuel_price: Optional[float]
) -> float:
    """Calculate old heating system annual cost"""
    total_demand = heating_demand_kwh + hot_water_demand_kwh
    fuel_consumption = total_demand / efficiency
    price = fuel_price if fuel_price else FUEL_PRICES.get(old_system, 0.10)
    return round(fuel_consumption * price, 2)


def calculate_co2_savings(
    heating_demand_kwh: float,
    hot_water_demand_kwh: float,
    old_system: OldHeatingSystem,
    old_efficiency: float,
    electricity_consumption_kwh: float
) -> float:
    """Calculate CO2 savings"""
    total_demand = heating_demand_kwh + hot_water_demand_kwh
    old_fuel_consumption = total_demand / old_efficiency
    
    old_co2 = old_fuel_consumption * CO2_FACTORS.get(old_system, 0.2)
    new_co2 = electricity_consumption_kwh * HP_ELECTRICITY_CO2
    
    return round(old_co2 - new_co2, 0)


def calculate_amortization(
    investment: float,
    subsidy_percent: float,
    annual_savings: float,
    cheat_factor: float = 1.0
) -> AmortizationResult:
    """Calculate amortization period"""
    subsidy = investment * subsidy_percent / 100
    net_investment = investment - subsidy
    
    # Apply cheat factor to savings (for demo purposes)
    adjusted_savings = annual_savings * cheat_factor
    
    # Simple payback
    simple_payback = net_investment / annual_savings if annual_savings > 0 else 99
    
    # Adjusted payback (with cheat factor)
    adjusted_payback = net_investment / adjusted_savings if adjusted_savings > 0 else 99
    
    # 20-year totals
    total_savings_20y = adjusted_savings * 20
    roi_20y = ((total_savings_20y - net_investment) / net_investment * 100) if net_investment > 0 else 0
    
    return AmortizationResult(
        simple_payback_years=round(simple_payback, 1),
        adjusted_payback_years=round(adjusted_payback, 1),
        net_investment_eur=round(net_investment, 2),
        annual_savings_eur=round(adjusted_savings, 2),
        total_savings_20_years_eur=round(total_savings_20y, 2),
        roi_20_years_percent=round(roi_20y, 1)
    )


def generate_monthly_breakdown(
    electricity_consumption_kwh: float,
    electricity_price: float,
    old_heating_cost: float
) -> List[Dict[str, float]]:
    """Generate monthly cost breakdown"""
    breakdown = []
    
    for i, share in enumerate(MONTHLY_HEATING_SHARE):
        monthly_elec = electricity_consumption_kwh * share
        monthly_elec_cost = monthly_elec * electricity_price
        monthly_old_cost = old_heating_cost * share
        
        breakdown.append({
            "month": MONTH_NAMES[i],
            "month_number": i + 1,
            "heating_share_percent": round(share * 100, 1),
            "electricity_kwh": round(monthly_elec, 0),
            "electricity_cost_eur": round(monthly_elec_cost, 2),
            "old_system_cost_eur": round(monthly_old_cost, 2),
            "savings_eur": round(monthly_old_cost - monthly_elec_cost, 2)
        })
    
    return breakdown


# ==================== API Endpoints ====================

@router.post("/calculate", response_model=CalculationResult)
async def calculate_heat_pump_results(request: CalculationRequest):
    """
    Calculate complete heat pump results including JAZ, costs, and amortization.
    """
    # Calculate JAZ (simplified - use dedicated endpoint for detailed)
    jaz = request.heat_pump_cop * FLOW_TEMP_FACTORS.get(request.heating_system_type, 1.0)
    
    # Electricity consumption
    total_demand = request.heating_demand_kwh + request.hot_water_demand_kwh
    electricity_consumption = calculate_electricity_consumption(
        request.heating_demand_kwh,
        request.hot_water_demand_kwh,
        jaz
    )
    
    # Costs
    annual_electricity_cost = electricity_consumption * request.electricity_price_eur_kwh
    old_heating_cost = calculate_old_heating_cost(
        request.heating_demand_kwh,
        request.hot_water_demand_kwh,
        request.old_heating_system,
        request.old_system_efficiency,
        request.old_fuel_price_eur_kwh
    )
    
    # Savings
    annual_savings = old_heating_cost - annual_electricity_cost
    savings_percent = (annual_savings / old_heating_cost * 100) if old_heating_cost > 0 else 0
    
    # CO2 savings
    co2_savings = calculate_co2_savings(
        request.heating_demand_kwh,
        request.hot_water_demand_kwh,
        request.old_heating_system,
        request.old_system_efficiency,
        electricity_consumption
    )
    
    # Amortization
    total_investment = request.heat_pump_price_eur + request.installation_cost_eur
    amortization = calculate_amortization(
        total_investment,
        request.subsidy_percent,
        annual_savings,
        request.amortization_cheat_factor
    )
    
    # Cost comparison
    cost_comparison = HeatingCostComparison(
        old_system={
            "type": request.old_heating_system.value,
            "efficiency": request.old_system_efficiency,
            "annual_cost_eur": round(old_heating_cost, 2),
            "fuel_consumption_kwh": round(total_demand / request.old_system_efficiency, 0),
            "co2_emissions_kg": round(total_demand / request.old_system_efficiency * CO2_FACTORS.get(request.old_heating_system, 0.2), 0)
        },
        new_system={
            "type": "heat_pump",
            "jaz": jaz,
            "annual_cost_eur": round(annual_electricity_cost, 2),
            "electricity_consumption_kwh": electricity_consumption,
            "co2_emissions_kg": round(electricity_consumption * HP_ELECTRICITY_CO2, 0)
        },
        annual_savings_eur=round(annual_savings, 2),
        savings_percent=round(savings_percent, 1),
        co2_savings_kg=co2_savings
    )
    
    # Monthly breakdown
    monthly_breakdown = generate_monthly_breakdown(
        electricity_consumption,
        request.electricity_price_eur_kwh,
        old_heating_cost
    )
    
    return CalculationResult(
        jaz=round(jaz, 2),
        electricity_consumption_kwh=electricity_consumption,
        annual_electricity_cost_eur=round(annual_electricity_cost, 2),
        old_heating_cost_eur=round(old_heating_cost, 2),
        annual_savings_eur=round(annual_savings, 2),
        savings_percent=round(savings_percent, 1),
        co2_savings_kg=co2_savings,
        amortization=amortization,
        cost_comparison=cost_comparison,
        monthly_breakdown=monthly_breakdown
    )


@router.post("/jaz", response_model=Dict[str, Any])
async def calculate_jaz_detailed(request: JAZCalculationRequest):
    """
    Calculate detailed annual performance factor (JAZ).
    """
    jaz = calculate_jaz(
        request.cop_a7w35,
        request.cop_a2w35,
        request.cop_a_7w35,
        request.heating_system_type,
        request.climate_zone,
        request.hot_water_share_percent
    )
    
    return {
        "jaz": jaz,
        "input_cops": {
            "cop_a7w35": request.cop_a7w35,
            "cop_a2w35": request.cop_a2w35,
            "cop_a_7w35": request.cop_a_7w35
        },
        "factors": {
            "flow_temperature_factor": FLOW_TEMP_FACTORS.get(request.heating_system_type, 1.0),
            "climate_factor": CLIMATE_FACTORS.get(request.climate_zone, 1.0),
            "hot_water_factor": 1.0 - (request.hot_water_share_percent / 100 * 0.1)
        },
        "rating": "Sehr gut" if jaz >= 4.0 else "Gut" if jaz >= 3.5 else "Befriedigend" if jaz >= 3.0 else "Ausreichend"
    }


@router.get("/cost-comparison")
async def get_cost_comparison(
    heating_demand_kwh: float = Query(..., gt=0),
    hot_water_demand_kwh: float = Query(0, ge=0),
    jaz: float = Query(4.0, ge=2.0, le=6.0),
    electricity_price_eur_kwh: float = Query(0.30, ge=0.1, le=1.0),
    old_system: OldHeatingSystem = Query(OldHeatingSystem.GAS),
    old_efficiency: float = Query(0.9, ge=0.5, le=1.0)
):
    """
    Quick cost comparison between old and new heating system.
    """
    total_demand = heating_demand_kwh + hot_water_demand_kwh
    
    # New system (heat pump)
    electricity_consumption = total_demand / jaz
    new_cost = electricity_consumption * electricity_price_eur_kwh
    
    # Old system
    fuel_consumption = total_demand / old_efficiency
    old_cost = fuel_consumption * FUEL_PRICES.get(old_system, 0.10)
    
    # Savings
    savings = old_cost - new_cost
    savings_percent = (savings / old_cost * 100) if old_cost > 0 else 0
    
    return {
        "old_system": {
            "type": old_system.value,
            "annual_cost_eur": round(old_cost, 2),
            "fuel_consumption_kwh": round(fuel_consumption, 0)
        },
        "new_system": {
            "type": "heat_pump",
            "annual_cost_eur": round(new_cost, 2),
            "electricity_consumption_kwh": round(electricity_consumption, 0)
        },
        "savings": {
            "annual_eur": round(savings, 2),
            "percent": round(savings_percent, 1),
            "monthly_eur": round(savings / 12, 2)
        }
    }


@router.get("/amortization-cheat")
async def calculate_amortization_with_cheat(
    investment_eur: float = Query(..., gt=0),
    annual_savings_eur: float = Query(..., gt=0),
    subsidy_percent: float = Query(30, ge=0, le=70),
    cheat_factor: float = Query(1.0, ge=0.5, le=2.0, description="Demo-Faktor für Präsentationen")
):
    """
    Calculate amortization with optional "cheat" factor for demonstrations.
    
    The cheat factor allows adjusting the savings for demo purposes:
    - 1.0 = realistic calculation
    - 1.2 = 20% optimistic
    - 0.8 = 20% conservative
    """
    amortization = calculate_amortization(
        investment_eur,
        subsidy_percent,
        annual_savings_eur,
        cheat_factor
    )
    
    return {
        "input": {
            "investment_eur": investment_eur,
            "subsidy_percent": subsidy_percent,
            "annual_savings_eur": annual_savings_eur,
            "cheat_factor": cheat_factor
        },
        "result": amortization,
        "note": "Cheat-Faktor nur für Demonstrationszwecke" if cheat_factor != 1.0 else None
    }


@router.get("/fuel-prices")
async def get_fuel_prices():
    """
    Get current fuel prices for comparison.
    """
    return {
        "prices": [
            {"fuel": k.value, "price_eur_kwh": v, "label_de": get_fuel_label(k)}
            for k, v in FUEL_PRICES.items()
        ],
        "electricity_price_eur_kwh": 0.30,
        "note": "Durchschnittspreise Deutschland, Stand 2024"
    }


def get_fuel_label(fuel: OldHeatingSystem) -> str:
    """Get German label for fuel type"""
    labels = {
        OldHeatingSystem.OIL: "Heizöl",
        OldHeatingSystem.GAS: "Erdgas",
        OldHeatingSystem.ELECTRIC: "Strom (Direktheizung)",
        OldHeatingSystem.COAL: "Kohle",
        OldHeatingSystem.WOOD: "Holz/Pellets",
        OldHeatingSystem.DISTRICT: "Fernwärme",
        OldHeatingSystem.LPG: "Flüssiggas"
    }
    return labels.get(fuel, fuel.value)


@router.get("/co2-factors")
async def get_co2_factors():
    """
    Get CO2 emission factors for different fuels.
    """
    return {
        "factors": [
            {"fuel": k.value, "co2_kg_kwh": v, "label_de": get_fuel_label(k)}
            for k, v in CO2_FACTORS.items()
        ],
        "heat_pump_electricity_co2_kg_kwh": HP_ELECTRICITY_CO2,
        "note": "CO2-Emissionsfaktoren nach GEMIS"
    }


@router.get("/quick-savings")
async def quick_savings_calculation(
    heating_demand_kwh: float = Query(..., gt=0),
    old_system: OldHeatingSystem = Query(OldHeatingSystem.GAS),
    jaz: float = Query(4.0, ge=2.0, le=6.0)
):
    """
    Quick savings calculation with minimal input.
    """
    # Simplified calculation
    old_cost = heating_demand_kwh / 0.9 * FUEL_PRICES.get(old_system, 0.10)
    new_cost = heating_demand_kwh / jaz * 0.30
    savings = old_cost - new_cost
    
    return {
        "heating_demand_kwh": heating_demand_kwh,
        "old_system": old_system.value,
        "jaz": jaz,
        "old_annual_cost_eur": round(old_cost, 2),
        "new_annual_cost_eur": round(new_cost, 2),
        "annual_savings_eur": round(savings, 2),
        "monthly_savings_eur": round(savings / 12, 2)
    }


@router.get("/health/check")
async def health_check():
    """
    Health check for heat pump results service.
    """
    return {
        "status": "healthy",
        "service": "heatpump-results",
        "fuel_types": len(OldHeatingSystem),
        "heating_systems": len(HeatingSystemType),
        "timestamp": datetime.now().isoformat()
    }
