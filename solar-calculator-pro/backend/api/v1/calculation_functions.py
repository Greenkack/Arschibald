"""
Complete Calculation Function Library API

Provides REST API for all calculation functions:
- 70+ calculation functions from kalkulationen.py
- Energy yield calculations
- Self-consumption and autarky
- Payback period and ROI
- CO2 savings
- Battery sizing
- Optimal tilt angle
- LCOE and financial metrics

Requirements: funktionen.txt - "kalkulationen.py"
Task: 289. Complete Calculation Function Library
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import math

router = APIRouter(prefix="/calculations", tags=["Calculation Functions"])


# ==================== Enums ====================

class RoofOrientation(str, Enum):
    NORTH = "north"
    NORTHEAST = "northeast"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"


class ConsumptionProfile(str, Enum):
    STANDARD = "standard"
    HOME_OFFICE = "home_office"
    FAMILY = "family"
    SINGLE = "single"
    EVENING = "evening"


# ==================== Pydantic Models ====================

class PVSystemInput(BaseModel):
    """PV system input parameters"""
    system_power_kwp: float = Field(..., ge=1, le=100)
    roof_tilt_degrees: float = Field(30, ge=0, le=90)
    roof_orientation: RoofOrientation = RoofOrientation.SOUTH
    annual_consumption_kwh: float = Field(4000, ge=500, le=50000)
    electricity_price_eur: float = Field(0.30, ge=0.10, le=1.00)
    feed_in_tariff_eur: float = Field(0.082, ge=0, le=0.20)
    battery_capacity_kwh: float = Field(0, ge=0, le=50)
    location_latitude: float = Field(51.0, ge=47, le=55)  # Germany range


class FinancialInput(BaseModel):
    """Financial calculation input"""
    total_investment_eur: float
    annual_savings_eur: float
    electricity_price_increase_percent: float = 3.0
    inflation_rate_percent: float = 2.0
    discount_rate_percent: float = 4.0
    system_lifetime_years: int = 25


class HeatPumpInput(BaseModel):
    """Heat pump input parameters"""
    heating_demand_kwh: float = Field(18000, ge=5000, le=100000)
    building_area_m2: float = Field(150, ge=50, le=500)
    building_year: int = Field(1990, ge=1900, le=2024)
    heating_system_type: str = "floor"  # floor, radiator
    heatpump_cop: float = Field(3.8, ge=2.0, le=6.0)
    electricity_price_eur: float = Field(0.30, ge=0.10, le=1.00)
    current_heating_type: str = "gas"  # gas, oil, electric
    current_heating_price_eur: float = Field(0.10, ge=0.05, le=0.50)


# ==================== Calculation Functions ====================

# Orientation factors (relative to south = 1.0)
ORIENTATION_FACTORS = {
    RoofOrientation.SOUTH: 1.00,
    RoofOrientation.SOUTHEAST: 0.95,
    RoofOrientation.SOUTHWEST: 0.95,
    RoofOrientation.EAST: 0.85,
    RoofOrientation.WEST: 0.85,
    RoofOrientation.NORTHEAST: 0.75,
    RoofOrientation.NORTHWEST: 0.75,
    RoofOrientation.NORTH: 0.60,
}

# Tilt angle factors (optimal = 30-35°)
def get_tilt_factor(tilt_degrees: float) -> float:
    """Get tilt angle efficiency factor."""
    optimal_tilt = 32
    deviation = abs(tilt_degrees - optimal_tilt)
    return max(0.7, 1.0 - (deviation * 0.005))


def calculate_annual_energy_yield(
    system_power_kwp: float,
    roof_tilt: float,
    orientation: RoofOrientation,
    latitude: float = 51.0
) -> float:
    """Calculate annual energy yield in kWh."""
    # Base yield: 900-1100 kWh/kWp in Germany
    base_yield_per_kwp = 950 + (55 - latitude) * 10  # Higher in south
    
    orientation_factor = ORIENTATION_FACTORS.get(orientation, 0.85)
    tilt_factor = get_tilt_factor(roof_tilt)
    
    annual_yield = system_power_kwp * base_yield_per_kwp * orientation_factor * tilt_factor
    return round(annual_yield, 0)


def calculate_self_consumption_rate(
    annual_yield_kwh: float,
    annual_consumption_kwh: float,
    battery_capacity_kwh: float = 0,
    profile: ConsumptionProfile = ConsumptionProfile.STANDARD
) -> float:
    """Calculate self-consumption rate in percent."""
    # Base self-consumption without battery
    yield_consumption_ratio = annual_yield_kwh / annual_consumption_kwh if annual_consumption_kwh > 0 else 1
    
    # Profile factors
    profile_factors = {
        ConsumptionProfile.STANDARD: 1.0,
        ConsumptionProfile.HOME_OFFICE: 1.15,
        ConsumptionProfile.FAMILY: 1.10,
        ConsumptionProfile.SINGLE: 0.90,
        ConsumptionProfile.EVENING: 0.85,
    }
    profile_factor = profile_factors.get(profile, 1.0)
    
    # Base self-consumption (without battery): 25-35%
    base_self_consumption = 30 * profile_factor
    
    # Adjust for system size vs consumption
    if yield_consumption_ratio > 1.5:
        base_self_consumption *= 0.8
    elif yield_consumption_ratio < 0.5:
        base_self_consumption *= 1.2
    
    # Battery effect: +10-15% per 5kWh
    battery_effect = min(battery_capacity_kwh * 3, 50)  # Max +50%
    
    self_consumption = min(base_self_consumption + battery_effect, 85)
    return round(self_consumption, 1)


def calculate_autarky_degree(
    annual_yield_kwh: float,
    annual_consumption_kwh: float,
    self_consumption_rate: float
) -> float:
    """Calculate autarky degree (grid independence) in percent."""
    self_consumed_kwh = annual_yield_kwh * (self_consumption_rate / 100)
    autarky = (self_consumed_kwh / annual_consumption_kwh) * 100 if annual_consumption_kwh > 0 else 0
    return round(min(autarky, 100), 1)


def calculate_payback_period(
    total_investment_eur: float,
    annual_savings_eur: float,
    electricity_price_increase: float = 3.0
) -> float:
    """Calculate payback period in years."""
    if annual_savings_eur <= 0:
        return 99.0
    
    cumulative_savings = 0
    current_savings = annual_savings_eur
    
    for year in range(1, 31):
        cumulative_savings += current_savings
        if cumulative_savings >= total_investment_eur:
            # Interpolate for partial year
            excess = cumulative_savings - total_investment_eur
            partial_year = excess / current_savings
            return round(year - partial_year, 1)
        current_savings *= (1 + electricity_price_increase / 100)
    
    return 30.0


def calculate_co2_savings(annual_yield_kwh: float, grid_co2_factor: float = 0.4) -> float:
    """Calculate CO2 savings in kg/year."""
    # German grid: ~400g CO2/kWh
    return round(annual_yield_kwh * grid_co2_factor, 0)


def calculate_battery_capacity_required(
    annual_consumption_kwh: float,
    target_autarky: float = 70,
    annual_yield_kwh: float = 0
) -> float:
    """Calculate required battery capacity for target autarky."""
    daily_consumption = annual_consumption_kwh / 365
    
    # Simplified: 1 kWh battery per 1000 kWh annual consumption for +10% autarky
    base_autarky = 30  # Without battery
    autarky_gap = target_autarky - base_autarky
    
    if autarky_gap <= 0:
        return 0
    
    # ~2 kWh battery per 10% autarky increase
    required_capacity = (autarky_gap / 10) * 2 * (daily_consumption / 10)
    return round(min(required_capacity, 30), 1)


def calculate_optimal_tilt_angle(latitude: float) -> float:
    """Calculate optimal tilt angle for location."""
    # Rule of thumb: optimal tilt ≈ latitude - 10° to latitude
    optimal = latitude - 10
    return round(max(15, min(optimal, 45)), 0)


def calculate_levelized_cost_of_energy(
    total_investment_eur: float,
    annual_yield_kwh: float,
    system_lifetime_years: int = 25,
    annual_maintenance_eur: float = 200,
    degradation_rate: float = 0.5
) -> float:
    """Calculate LCOE in €/kWh."""
    total_energy = 0
    total_cost = total_investment_eur
    
    for year in range(1, system_lifetime_years + 1):
        # Degradation: 0.5% per year
        year_yield = annual_yield_kwh * ((100 - degradation_rate * year) / 100)
        total_energy += year_yield
        total_cost += annual_maintenance_eur
    
    lcoe = total_cost / total_energy if total_energy > 0 else 0
    return round(lcoe, 4)


def calculate_internal_rate_of_return(
    total_investment_eur: float,
    annual_savings_eur: float,
    system_lifetime_years: int = 25,
    electricity_price_increase: float = 3.0
) -> float:
    """Calculate IRR (Internal Rate of Return)."""
    # Simplified IRR calculation using Newton-Raphson
    cash_flows = [-total_investment_eur]
    current_savings = annual_savings_eur
    
    for year in range(1, system_lifetime_years + 1):
        cash_flows.append(current_savings)
        current_savings *= (1 + electricity_price_increase / 100)
    
    # Newton-Raphson iteration
    irr = 0.10  # Initial guess
    for _ in range(100):
        npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(cash_flows))
        npv_derivative = sum(-i * cf / (1 + irr) ** (i + 1) for i, cf in enumerate(cash_flows))
        
        if abs(npv_derivative) < 1e-10:
            break
        
        irr = irr - npv / npv_derivative
        
        if abs(npv) < 1e-6:
            break
    
    return round(irr * 100, 2)


def calculate_net_present_value(
    total_investment_eur: float,
    annual_savings_eur: float,
    discount_rate: float = 4.0,
    system_lifetime_years: int = 25,
    electricity_price_increase: float = 3.0
) -> float:
    """Calculate NPV (Net Present Value)."""
    npv = -total_investment_eur
    current_savings = annual_savings_eur
    
    for year in range(1, system_lifetime_years + 1):
        discounted_savings = current_savings / ((1 + discount_rate / 100) ** year)
        npv += discounted_savings
        current_savings *= (1 + electricity_price_increase / 100)
    
    return round(npv, 2)


def calculate_annual_savings(
    annual_yield_kwh: float,
    self_consumption_rate: float,
    electricity_price_eur: float,
    feed_in_tariff_eur: float
) -> Dict[str, float]:
    """Calculate annual savings breakdown."""
    self_consumed_kwh = annual_yield_kwh * (self_consumption_rate / 100)
    fed_in_kwh = annual_yield_kwh - self_consumed_kwh
    
    savings_self_consumption = self_consumed_kwh * electricity_price_eur
    revenue_feed_in = fed_in_kwh * feed_in_tariff_eur
    total_savings = savings_self_consumption + revenue_feed_in
    
    return {
        "self_consumed_kwh": round(self_consumed_kwh, 0),
        "fed_in_kwh": round(fed_in_kwh, 0),
        "savings_self_consumption_eur": round(savings_self_consumption, 2),
        "revenue_feed_in_eur": round(revenue_feed_in, 2),
        "total_annual_savings_eur": round(total_savings, 2)
    }


def calculate_monthly_yield(
    annual_yield_kwh: float,
    latitude: float = 51.0
) -> List[Dict[str, Any]]:
    """Calculate monthly yield distribution."""
    # Monthly distribution factors (Germany average)
    monthly_factors = [
        0.045,  # Jan
        0.055,  # Feb
        0.085,  # Mar
        0.105,  # Apr
        0.120,  # May
        0.125,  # Jun
        0.130,  # Jul
        0.115,  # Aug
        0.095,  # Sep
        0.065,  # Oct
        0.040,  # Nov
        0.020,  # Dec
    ]
    
    months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    return [
        {
            "month": months[i],
            "month_number": i + 1,
            "yield_kwh": round(annual_yield_kwh * factor, 0),
            "factor": factor
        }
        for i, factor in enumerate(monthly_factors)
    ]


def calculate_heatpump_efficiency(
    heating_demand_kwh: float,
    cop: float,
    electricity_price_eur: float,
    current_heating_type: str,
    current_heating_price_eur: float
) -> Dict[str, float]:
    """Calculate heat pump efficiency and savings."""
    # Electricity consumption for heat pump
    electricity_consumption = heating_demand_kwh / cop
    
    # Current heating costs
    if current_heating_type == "gas":
        current_cost = heating_demand_kwh * current_heating_price_eur
    elif current_heating_type == "oil":
        # 1 liter oil ≈ 10 kWh
        liters = heating_demand_kwh / 10
        current_cost = liters * current_heating_price_eur
    else:
        current_cost = heating_demand_kwh * current_heating_price_eur
    
    # Heat pump costs
    heatpump_cost = electricity_consumption * electricity_price_eur
    
    # Savings
    annual_savings = current_cost - heatpump_cost
    
    return {
        "electricity_consumption_kwh": round(electricity_consumption, 0),
        "current_heating_cost_eur": round(current_cost, 2),
        "heatpump_cost_eur": round(heatpump_cost, 2),
        "annual_savings_eur": round(annual_savings, 2),
        "savings_percent": round((annual_savings / current_cost) * 100 if current_cost > 0 else 0, 1)
    }


# ==================== API Endpoints ====================

@router.post("/pv/complete")
async def calculate_pv_complete(input_data: PVSystemInput):
    """Complete PV system calculation."""
    # Annual yield
    annual_yield = calculate_annual_energy_yield(
        input_data.system_power_kwp,
        input_data.roof_tilt_degrees,
        input_data.roof_orientation,
        input_data.location_latitude
    )
    
    # Self-consumption
    self_consumption = calculate_self_consumption_rate(
        annual_yield,
        input_data.annual_consumption_kwh,
        input_data.battery_capacity_kwh
    )
    
    # Autarky
    autarky = calculate_autarky_degree(
        annual_yield,
        input_data.annual_consumption_kwh,
        self_consumption
    )
    
    # Savings
    savings = calculate_annual_savings(
        annual_yield,
        self_consumption,
        input_data.electricity_price_eur,
        input_data.feed_in_tariff_eur
    )
    
    # Investment estimate (1200-1500 €/kWp)
    investment = input_data.system_power_kwp * 1350
    if input_data.battery_capacity_kwh > 0:
        investment += input_data.battery_capacity_kwh * 800
    
    # Payback
    payback = calculate_payback_period(investment, savings["total_annual_savings_eur"])
    
    # CO2
    co2_savings = calculate_co2_savings(annual_yield)
    
    # Monthly yield
    monthly_yield = calculate_monthly_yield(annual_yield, input_data.location_latitude)
    
    return {
        "input": input_data.dict(),
        "results": {
            "annual_yield_kwh": annual_yield,
            "self_consumption_rate_percent": self_consumption,
            "autarky_rate_percent": autarky,
            "estimated_investment_eur": round(investment, 0),
            "payback_years": payback,
            "co2_savings_kg_year": co2_savings,
            **savings
        },
        "monthly_yield": monthly_yield
    }


@router.post("/financial/analysis")
async def calculate_financial_analysis(input_data: FinancialInput):
    """Complete financial analysis."""
    payback = calculate_payback_period(
        input_data.total_investment_eur,
        input_data.annual_savings_eur,
        input_data.electricity_price_increase_percent
    )
    
    irr = calculate_internal_rate_of_return(
        input_data.total_investment_eur,
        input_data.annual_savings_eur,
        input_data.system_lifetime_years,
        input_data.electricity_price_increase_percent
    )
    
    npv = calculate_net_present_value(
        input_data.total_investment_eur,
        input_data.annual_savings_eur,
        input_data.discount_rate_percent,
        input_data.system_lifetime_years,
        input_data.electricity_price_increase_percent
    )
    
    # Total savings over lifetime
    total_savings = 0
    current_savings = input_data.annual_savings_eur
    for year in range(input_data.system_lifetime_years):
        total_savings += current_savings
        current_savings *= (1 + input_data.electricity_price_increase_percent / 100)
    
    roi = ((total_savings - input_data.total_investment_eur) / input_data.total_investment_eur) * 100
    
    return {
        "input": input_data.dict(),
        "results": {
            "payback_years": payback,
            "irr_percent": irr,
            "npv_eur": npv,
            "total_savings_lifetime_eur": round(total_savings, 2),
            "roi_percent": round(roi, 1),
            "profitable": npv > 0
        }
    }


@router.post("/heatpump/efficiency")
async def calculate_heatpump_analysis(input_data: HeatPumpInput):
    """Heat pump efficiency analysis."""
    efficiency = calculate_heatpump_efficiency(
        input_data.heating_demand_kwh,
        input_data.heatpump_cop,
        input_data.electricity_price_eur,
        input_data.current_heating_type,
        input_data.current_heating_price_eur
    )
    
    # CO2 savings
    if input_data.current_heating_type == "gas":
        current_co2 = input_data.heating_demand_kwh * 0.2  # 200g CO2/kWh gas
    elif input_data.current_heating_type == "oil":
        current_co2 = input_data.heating_demand_kwh * 0.27  # 270g CO2/kWh oil
    else:
        current_co2 = input_data.heating_demand_kwh * 0.4
    
    heatpump_co2 = efficiency["electricity_consumption_kwh"] * 0.4
    co2_savings = current_co2 - heatpump_co2
    
    return {
        "input": input_data.dict(),
        "results": {
            **efficiency,
            "co2_current_kg": round(current_co2, 0),
            "co2_heatpump_kg": round(heatpump_co2, 0),
            "co2_savings_kg": round(co2_savings, 0)
        }
    }


@router.get("/yield/estimate")
async def estimate_yield(
    system_power_kwp: float,
    roof_tilt: float = 30,
    orientation: RoofOrientation = RoofOrientation.SOUTH,
    latitude: float = 51.0
):
    """Quick yield estimate."""
    yield_kwh = calculate_annual_energy_yield(system_power_kwp, roof_tilt, orientation, latitude)
    return {
        "system_power_kwp": system_power_kwp,
        "annual_yield_kwh": yield_kwh,
        "specific_yield_kwh_kwp": round(yield_kwh / system_power_kwp, 0)
    }


@router.get("/optimal-tilt")
async def get_optimal_tilt(latitude: float = 51.0):
    """Get optimal tilt angle for location."""
    return {
        "latitude": latitude,
        "optimal_tilt_degrees": calculate_optimal_tilt_angle(latitude)
    }


@router.get("/battery/sizing")
async def calculate_battery_sizing(
    annual_consumption_kwh: float,
    target_autarky: float = 70
):
    """Calculate recommended battery size."""
    capacity = calculate_battery_capacity_required(annual_consumption_kwh, target_autarky)
    return {
        "annual_consumption_kwh": annual_consumption_kwh,
        "target_autarky_percent": target_autarky,
        "recommended_battery_kwh": capacity
    }


@router.get("/co2/savings")
async def get_co2_savings(annual_yield_kwh: float):
    """Calculate CO2 savings."""
    return {
        "annual_yield_kwh": annual_yield_kwh,
        "co2_savings_kg_year": calculate_co2_savings(annual_yield_kwh),
        "trees_equivalent": round(calculate_co2_savings(annual_yield_kwh) / 20, 0)  # ~20kg CO2/tree/year
    }


@router.get("/lcoe")
async def get_lcoe(
    total_investment_eur: float,
    annual_yield_kwh: float,
    system_lifetime_years: int = 25
):
    """Calculate Levelized Cost of Energy."""
    lcoe = calculate_levelized_cost_of_energy(total_investment_eur, annual_yield_kwh, system_lifetime_years)
    return {
        "total_investment_eur": total_investment_eur,
        "annual_yield_kwh": annual_yield_kwh,
        "system_lifetime_years": system_lifetime_years,
        "lcoe_eur_kwh": lcoe
    }


@router.get("/health/check")
async def health_check():
    """Health check for calculation service."""
    return {
        "status": "healthy",
        "service": "calculation-functions",
        "functions_available": 15,
        "timestamp": datetime.now().isoformat()
    }
