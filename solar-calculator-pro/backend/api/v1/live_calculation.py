"""
Live Calculation Engine API Endpoints

Provides REST API for real-time PV system calculations:
- Total system power (kWp)
- Annual yield (kWh/Jahr)
- Self-consumption and autarky rates
- Storage usage
- Grid feed-in

Requirements: funktionen.txt - "Live-Berechnungen"
Task: 252. Live Calculation Engine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

router = APIRouter(prefix="/live-calculation", tags=["Live Calculation"])


# ==================== Enums ====================

class RoofOrientation(str, Enum):
    SOUTH = "south"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"
    EAST = "east"
    WEST = "west"
    NORTH = "north"
    FLAT = "flat"


class ConsumptionProfile(str, Enum):
    STANDARD = "standard"  # Normal household
    HOME_OFFICE = "home_office"  # More daytime consumption
    EVENING = "evening"  # More evening consumption
    INDUSTRIAL = "industrial"  # Constant consumption


# ==================== Pydantic Models ====================

class LiveCalculationRequest(BaseModel):
    """Request for live calculation"""
    # PV System
    module_count: int = Field(..., ge=1, le=200, description="Number of PV modules")
    module_power_wp: int = Field(default=400, ge=100, le=700, description="Module power in Wp")
    
    # Location & Orientation
    location: str = Field(default="Deutschland", description="Location for yield calculation")
    roof_orientation: RoofOrientation = Field(default=RoofOrientation.SOUTH)
    roof_angle: float = Field(default=30.0, ge=0, le=90, description="Roof angle in degrees")
    
    # Consumption
    annual_consumption_kwh: float = Field(default=4500, ge=0, description="Annual consumption in kWh")
    consumption_profile: ConsumptionProfile = Field(default=ConsumptionProfile.STANDARD)
    
    # Battery Storage
    battery_capacity_kwh: float = Field(default=0.0, ge=0, description="Battery capacity in kWh")
    battery_efficiency: float = Field(default=0.95, ge=0.5, le=1.0)
    
    # Optional: Electricity prices
    electricity_price: float = Field(default=0.35, description="EUR/kWh")
    feed_in_tariff: float = Field(default=0.082, description="EUR/kWh")


class LiveCalculationResponse(BaseModel):
    """Response with all calculated values"""
    # System Power
    system_power_kwp: float
    module_count: int
    module_power_wp: int
    
    # Annual Yield
    annual_yield_kwh: float
    specific_yield_kwh_kwp: float
    yield_factor: float
    
    # Self-Consumption & Autarky
    direct_consumption_kwh: float
    direct_consumption_rate: float
    self_consumption_kwh: float
    self_consumption_rate: float
    autarky_rate: float
    
    # Storage
    storage_charge_kwh: float
    storage_discharge_kwh: float
    storage_cycles_per_year: float
    storage_contribution_kwh: float
    
    # Grid
    grid_feed_in_kwh: float
    grid_purchase_kwh: float
    
    # Financial
    annual_savings_eur: float
    feed_in_revenue_eur: float
    total_benefit_eur: float
    
    # CO2
    co2_savings_kg: float


class QuickCalculationRequest(BaseModel):
    """Simplified request for quick calculations"""
    module_count: int
    module_power_wp: int = 400
    annual_consumption_kwh: float = 4500
    battery_capacity_kwh: float = 0.0


class MonthlyYieldResponse(BaseModel):
    """Monthly yield breakdown"""
    months: List[str]
    production_kwh: List[float]
    consumption_kwh: List[float]
    self_consumption_kwh: List[float]
    grid_feed_in_kwh: List[float]
    grid_purchase_kwh: List[float]


# ==================== Yield Factors ====================

# Static yield factors by orientation (kWh/kWp for Germany average)
ORIENTATION_FACTORS = {
    RoofOrientation.SOUTH: 1.0,
    RoofOrientation.SOUTH_EAST: 0.95,
    RoofOrientation.SOUTH_WEST: 0.95,
    RoofOrientation.EAST: 0.85,
    RoofOrientation.WEST: 0.85,
    RoofOrientation.NORTH: 0.55,
    RoofOrientation.FLAT: 0.90,
}

# Angle correction factors (optimal is ~30-35° for Germany)
def get_angle_factor(angle: float) -> float:
    """Get correction factor based on roof angle"""
    if 25 <= angle <= 40:
        return 1.0
    elif 15 <= angle < 25 or 40 < angle <= 50:
        return 0.97
    elif 5 <= angle < 15 or 50 < angle <= 60:
        return 0.93
    elif angle < 5:
        return 0.90
    else:  # > 60
        return 0.85

# Base specific yield for Germany (kWh/kWp)
BASE_SPECIFIC_YIELD = 950  # Average for Germany

# Monthly distribution factors (sum = 12)
MONTHLY_DISTRIBUTION = [
    0.04,  # January
    0.05,  # February
    0.08,  # March
    0.10,  # April
    0.12,  # May
    0.13,  # June
    0.13,  # July
    0.12,  # August
    0.09,  # September
    0.07,  # October
    0.04,  # November
    0.03,  # December
]

# Consumption profile factors (daytime consumption ratio)
CONSUMPTION_PROFILES = {
    ConsumptionProfile.STANDARD: 0.30,  # 30% during PV production hours
    ConsumptionProfile.HOME_OFFICE: 0.45,  # 45% during daytime
    ConsumptionProfile.EVENING: 0.20,  # Only 20% during daytime
    ConsumptionProfile.INDUSTRIAL: 0.50,  # 50% constant
}

# CO2 factor (kg CO2 per kWh from grid)
CO2_FACTOR = 0.4  # German grid average


# ==================== Calculation Functions ====================

def calculate_system_power(module_count: int, module_power_wp: int) -> float:
    """Calculate total system power in kWp"""
    return (module_count * module_power_wp) / 1000


def calculate_annual_yield(
    system_power_kwp: float,
    orientation: RoofOrientation,
    roof_angle: float
) -> tuple[float, float, float]:
    """Calculate annual yield with factors"""
    orientation_factor = ORIENTATION_FACTORS.get(orientation, 1.0)
    angle_factor = get_angle_factor(roof_angle)
    total_factor = orientation_factor * angle_factor
    
    specific_yield = BASE_SPECIFIC_YIELD * total_factor
    annual_yield = system_power_kwp * specific_yield
    
    return annual_yield, specific_yield, total_factor


def calculate_self_consumption(
    annual_yield_kwh: float,
    annual_consumption_kwh: float,
    consumption_profile: ConsumptionProfile,
    battery_capacity_kwh: float,
    battery_efficiency: float
) -> Dict[str, float]:
    """Calculate self-consumption and autarky rates"""
    
    # Base direct consumption (without storage)
    daytime_ratio = CONSUMPTION_PROFILES.get(consumption_profile, 0.30)
    daytime_consumption = annual_consumption_kwh * daytime_ratio
    
    # Direct consumption is limited by both production and daytime consumption
    direct_consumption = min(annual_yield_kwh * 0.7, daytime_consumption)
    
    # Surplus available for storage
    surplus = annual_yield_kwh - direct_consumption
    
    # Storage contribution
    if battery_capacity_kwh > 0:
        # Estimate daily cycles (0.8-1.0 per day in summer, less in winter)
        avg_daily_cycles = 0.7
        annual_storage_throughput = battery_capacity_kwh * avg_daily_cycles * 365
        
        # Storage can only store what's available as surplus
        storage_charge = min(surplus, annual_storage_throughput)
        storage_discharge = storage_charge * battery_efficiency
        
        # Storage cycles
        storage_cycles = storage_charge / battery_capacity_kwh if battery_capacity_kwh > 0 else 0
    else:
        storage_charge = 0
        storage_discharge = 0
        storage_cycles = 0
    
    # Total self-consumption
    self_consumption = direct_consumption + storage_discharge
    
    # Grid feed-in (what's not consumed or stored)
    grid_feed_in = annual_yield_kwh - direct_consumption - storage_charge
    grid_feed_in = max(0, grid_feed_in)
    
    # Grid purchase (what's still needed from grid)
    grid_purchase = annual_consumption_kwh - self_consumption
    grid_purchase = max(0, grid_purchase)
    
    # Rates
    self_consumption_rate = (self_consumption / annual_yield_kwh * 100) if annual_yield_kwh > 0 else 0
    autarky_rate = (self_consumption / annual_consumption_kwh * 100) if annual_consumption_kwh > 0 else 0
    direct_consumption_rate = (direct_consumption / annual_yield_kwh * 100) if annual_yield_kwh > 0 else 0
    
    return {
        "direct_consumption_kwh": round(direct_consumption, 1),
        "direct_consumption_rate": round(direct_consumption_rate, 1),
        "self_consumption_kwh": round(self_consumption, 1),
        "self_consumption_rate": round(self_consumption_rate, 1),
        "autarky_rate": round(autarky_rate, 1),
        "storage_charge_kwh": round(storage_charge, 1),
        "storage_discharge_kwh": round(storage_discharge, 1),
        "storage_cycles_per_year": round(storage_cycles, 0),
        "storage_contribution_kwh": round(storage_discharge, 1),
        "grid_feed_in_kwh": round(grid_feed_in, 1),
        "grid_purchase_kwh": round(grid_purchase, 1),
    }


def calculate_financials(
    self_consumption_kwh: float,
    grid_feed_in_kwh: float,
    electricity_price: float,
    feed_in_tariff: float
) -> Dict[str, float]:
    """Calculate financial benefits"""
    annual_savings = self_consumption_kwh * electricity_price
    feed_in_revenue = grid_feed_in_kwh * feed_in_tariff
    total_benefit = annual_savings + feed_in_revenue
    
    return {
        "annual_savings_eur": round(annual_savings, 2),
        "feed_in_revenue_eur": round(feed_in_revenue, 2),
        "total_benefit_eur": round(total_benefit, 2),
    }


def calculate_co2_savings(self_consumption_kwh: float) -> float:
    """Calculate CO2 savings in kg"""
    return round(self_consumption_kwh * CO2_FACTOR, 1)


def calculate_monthly_breakdown(
    annual_yield_kwh: float,
    annual_consumption_kwh: float,
    self_consumption_rate: float
) -> MonthlyYieldResponse:
    """Calculate monthly breakdown"""
    months = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    
    monthly_consumption = annual_consumption_kwh / 12
    
    production = []
    consumption = []
    self_consumption = []
    grid_feed_in = []
    grid_purchase = []
    
    for factor in MONTHLY_DISTRIBUTION:
        monthly_production = annual_yield_kwh * factor
        monthly_self = min(monthly_production * (self_consumption_rate / 100), monthly_consumption)
        monthly_feed_in = monthly_production - monthly_self
        monthly_purchase = monthly_consumption - monthly_self
        
        production.append(round(monthly_production, 1))
        consumption.append(round(monthly_consumption, 1))
        self_consumption.append(round(monthly_self, 1))
        grid_feed_in.append(round(max(0, monthly_feed_in), 1))
        grid_purchase.append(round(max(0, monthly_purchase), 1))
    
    return MonthlyYieldResponse(
        months=months,
        production_kwh=production,
        consumption_kwh=consumption,
        self_consumption_kwh=self_consumption,
        grid_feed_in_kwh=grid_feed_in,
        grid_purchase_kwh=grid_purchase
    )


# ==================== API Endpoints ====================

@router.post("/calculate", response_model=LiveCalculationResponse)
async def calculate_live(request: LiveCalculationRequest):
    """
    Perform complete live calculation for PV system.
    
    Returns all calculated values including:
    - System power
    - Annual yield
    - Self-consumption and autarky rates
    - Storage usage
    - Grid interaction
    - Financial benefits
    - CO2 savings
    """
    # Calculate system power
    system_power_kwp = calculate_system_power(request.module_count, request.module_power_wp)
    
    # Calculate annual yield
    annual_yield, specific_yield, yield_factor = calculate_annual_yield(
        system_power_kwp,
        request.roof_orientation,
        request.roof_angle
    )
    
    # Calculate self-consumption
    consumption_data = calculate_self_consumption(
        annual_yield,
        request.annual_consumption_kwh,
        request.consumption_profile,
        request.battery_capacity_kwh,
        request.battery_efficiency
    )
    
    # Calculate financials
    financial_data = calculate_financials(
        consumption_data["self_consumption_kwh"],
        consumption_data["grid_feed_in_kwh"],
        request.electricity_price,
        request.feed_in_tariff
    )
    
    # Calculate CO2 savings
    co2_savings = calculate_co2_savings(consumption_data["self_consumption_kwh"])
    
    return LiveCalculationResponse(
        system_power_kwp=round(system_power_kwp, 2),
        module_count=request.module_count,
        module_power_wp=request.module_power_wp,
        annual_yield_kwh=round(annual_yield, 1),
        specific_yield_kwh_kwp=round(specific_yield, 1),
        yield_factor=round(yield_factor, 3),
        **consumption_data,
        **financial_data,
        co2_savings_kg=co2_savings
    )


@router.post("/quick")
async def quick_calculate(request: QuickCalculationRequest):
    """
    Quick calculation with minimal inputs.
    
    Uses default values for orientation, angle, and prices.
    """
    full_request = LiveCalculationRequest(
        module_count=request.module_count,
        module_power_wp=request.module_power_wp,
        annual_consumption_kwh=request.annual_consumption_kwh,
        battery_capacity_kwh=request.battery_capacity_kwh
    )
    
    return await calculate_live(full_request)


@router.post("/monthly-breakdown", response_model=MonthlyYieldResponse)
async def get_monthly_breakdown(request: LiveCalculationRequest):
    """
    Get monthly breakdown of production and consumption.
    """
    system_power_kwp = calculate_system_power(request.module_count, request.module_power_wp)
    annual_yield, _, _ = calculate_annual_yield(
        system_power_kwp,
        request.roof_orientation,
        request.roof_angle
    )
    
    consumption_data = calculate_self_consumption(
        annual_yield,
        request.annual_consumption_kwh,
        request.consumption_profile,
        request.battery_capacity_kwh,
        request.battery_efficiency
    )
    
    return calculate_monthly_breakdown(
        annual_yield,
        request.annual_consumption_kwh,
        consumption_data["self_consumption_rate"]
    )


@router.get("/system-power")
async def calculate_system_power_endpoint(
    module_count: int,
    module_power_wp: int = 400
):
    """Calculate system power from module count and power"""
    power_kwp = calculate_system_power(module_count, module_power_wp)
    return {
        "module_count": module_count,
        "module_power_wp": module_power_wp,
        "system_power_kwp": round(power_kwp, 2),
        "system_power_wp": module_count * module_power_wp
    }


@router.get("/annual-yield")
async def calculate_annual_yield_endpoint(
    system_power_kwp: float,
    orientation: RoofOrientation = RoofOrientation.SOUTH,
    roof_angle: float = 30.0
):
    """Calculate annual yield for given system power"""
    annual_yield, specific_yield, yield_factor = calculate_annual_yield(
        system_power_kwp, orientation, roof_angle
    )
    return {
        "system_power_kwp": system_power_kwp,
        "orientation": orientation.value,
        "roof_angle": roof_angle,
        "annual_yield_kwh": round(annual_yield, 1),
        "specific_yield_kwh_kwp": round(specific_yield, 1),
        "yield_factor": round(yield_factor, 3),
        "orientation_factor": ORIENTATION_FACTORS.get(orientation, 1.0),
        "angle_factor": round(get_angle_factor(roof_angle), 3)
    }


@router.get("/self-consumption")
async def calculate_self_consumption_endpoint(
    annual_yield_kwh: float,
    annual_consumption_kwh: float,
    battery_capacity_kwh: float = 0.0,
    consumption_profile: ConsumptionProfile = ConsumptionProfile.STANDARD
):
    """Calculate self-consumption and autarky rates"""
    return calculate_self_consumption(
        annual_yield_kwh,
        annual_consumption_kwh,
        consumption_profile,
        battery_capacity_kwh,
        0.95  # Default battery efficiency
    )


@router.get("/autarky-comparison")
async def compare_autarky(
    annual_yield_kwh: float,
    annual_consumption_kwh: float
):
    """Compare autarky rates with different battery sizes"""
    battery_sizes = [0, 5, 7.5, 10, 12.5, 15, 20]
    results = []
    
    for size in battery_sizes:
        data = calculate_self_consumption(
            annual_yield_kwh,
            annual_consumption_kwh,
            ConsumptionProfile.STANDARD,
            size,
            0.95
        )
        results.append({
            "battery_kwh": size,
            "autarky_rate": data["autarky_rate"],
            "self_consumption_rate": data["self_consumption_rate"],
            "grid_purchase_kwh": data["grid_purchase_kwh"]
        })
    
    return {
        "annual_yield_kwh": annual_yield_kwh,
        "annual_consumption_kwh": annual_consumption_kwh,
        "comparison": results
    }


@router.get("/orientation-factors")
async def get_orientation_factors():
    """Get all orientation factors"""
    return {
        orientation.value: factor 
        for orientation, factor in ORIENTATION_FACTORS.items()
    }


@router.get("/consumption-profiles")
async def get_consumption_profiles():
    """Get all consumption profile factors"""
    return {
        profile.value: {
            "daytime_ratio": factor,
            "description": {
                "standard": "Normaler Haushalt",
                "home_office": "Home Office - mehr Tagesverbrauch",
                "evening": "Abendverbrauch - weniger Tagesverbrauch",
                "industrial": "Gewerblich - konstanter Verbrauch"
            }.get(profile.value, "")
        }
        for profile, factor in CONSUMPTION_PROFILES.items()
    }


@router.get("/health/check")
async def health_check():
    """Check live calculation service health"""
    return {
        "status": "healthy",
        "base_specific_yield": BASE_SPECIFIC_YIELD,
        "orientations": len(ORIENTATION_FACTORS),
        "consumption_profiles": len(CONSUMPTION_PROFILES)
    }
