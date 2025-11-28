"""
PV + Heat Pump Integration API

Provides REST API for combined PV and heat pump calculations:
- Combined PV+WP calculation mode
- Heat pump electricity consumption from PV
- Adjusted autarky calculation for WP electricity demand
- Combined savings visualization
- Synergy analysis (PV powering WP)

Requirements: funktionen.txt - "Integration PV + WP"
Task: 258. PV + Heat Pump Integration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

router = APIRouter(prefix="/integration/pv-heatpump", tags=["PV + Heat Pump Integration"])


# ==================== Pydantic Models ====================

class PVSystemData(BaseModel):
    """PV system input data"""
    system_power_kwp: float = Field(..., gt=0, description="PV-Anlagenleistung in kWp")
    annual_production_kwh: float = Field(..., gt=0, description="Jahresproduktion in kWh")
    battery_capacity_kwh: float = Field(default=0, ge=0, description="Batteriekapazität in kWh")
    electricity_price_eur_kwh: float = Field(default=0.30, ge=0.1, le=1.0)
    feed_in_tariff_eur_kwh: float = Field(default=0.08, ge=0, le=0.20)


class HeatPumpData(BaseModel):
    """Heat pump input data"""
    heating_demand_kwh: float = Field(..., gt=0, description="Jahresheizwärmebedarf in kWh")
    hot_water_demand_kwh: float = Field(default=0, ge=0)
    jaz: float = Field(default=4.0, ge=2.0, le=6.0, description="Jahresarbeitszahl")
    electricity_consumption_kwh: Optional[float] = Field(None, description="WP-Stromverbrauch")


class HouseholdData(BaseModel):
    """Household consumption data"""
    annual_consumption_kwh: float = Field(..., gt=0, description="Haushaltsstromverbrauch")
    persons: int = Field(default=4, ge=1, le=10)


class CombinedCalculationRequest(BaseModel):
    """Request for combined PV + heat pump calculation"""
    pv_system: PVSystemData
    heat_pump: HeatPumpData
    household: HouseholdData


class SynergyResult(BaseModel):
    """Synergy analysis result"""
    pv_to_heatpump_kwh: float
    pv_to_heatpump_percent: float
    heatpump_from_grid_kwh: float
    heatpump_self_sufficiency_percent: float
    synergy_savings_eur: float


class CombinedResult(BaseModel):
    """Combined calculation result"""
    # Total consumption
    total_electricity_demand_kwh: float
    household_demand_kwh: float
    heatpump_demand_kwh: float
    
    # PV production and usage
    pv_production_kwh: float
    self_consumption_kwh: float
    self_consumption_percent: float
    grid_feed_in_kwh: float
    grid_consumption_kwh: float
    
    # Autarky
    autarky_percent: float
    autarky_without_hp_percent: float
    
    # Synergy
    synergy: SynergyResult
    
    # Savings
    annual_savings_eur: float
    pv_savings_eur: float
    heatpump_savings_eur: float
    combined_bonus_eur: float
    
    # Monthly breakdown
    monthly_data: List[Dict[str, float]]


# ==================== Constants ====================

# Monthly PV production distribution (Germany)
MONTHLY_PV_SHARE = [0.04, 0.05, 0.08, 0.10, 0.12, 0.13, 0.13, 0.12, 0.09, 0.07, 0.04, 0.03]

# Monthly heating demand distribution
MONTHLY_HEATING_SHARE = [0.18, 0.15, 0.12, 0.06, 0.01, 0.00, 0.00, 0.00, 0.02, 0.08, 0.14, 0.17]

# Hot water is constant throughout the year
MONTHLY_HOT_WATER_SHARE = [1/12] * 12

# Household consumption is relatively constant
MONTHLY_HOUSEHOLD_SHARE = [0.09, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09]

MONTH_NAMES = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


# ==================== Helper Functions ====================

def calculate_heatpump_consumption(heating_kwh: float, hot_water_kwh: float, jaz: float) -> float:
    """Calculate heat pump electricity consumption"""
    return (heating_kwh + hot_water_kwh) / jaz


def calculate_monthly_data(
    pv_production: float,
    household_demand: float,
    hp_heating_demand: float,
    hp_hot_water_demand: float,
    jaz: float,
    battery_kwh: float
) -> List[Dict[str, float]]:
    """Calculate monthly breakdown"""
    monthly_data = []
    
    for i in range(12):
        # Monthly values
        pv_month = pv_production * MONTHLY_PV_SHARE[i]
        household_month = household_demand * MONTHLY_HOUSEHOLD_SHARE[i]
        hp_heating_month = hp_heating_demand * MONTHLY_HEATING_SHARE[i]
        hp_hot_water_month = hp_hot_water_demand * MONTHLY_HOT_WATER_SHARE[i]
        hp_electricity_month = (hp_heating_month + hp_hot_water_month) / jaz
        
        total_demand_month = household_month + hp_electricity_month
        
        # Self-consumption calculation (simplified)
        # With battery, assume 70% self-consumption, without 30%
        base_self_consumption_rate = 0.70 if battery_kwh > 0 else 0.30
        
        # Adjust for seasonal mismatch (less self-consumption in winter)
        seasonal_factor = 0.5 + 0.5 * (MONTHLY_PV_SHARE[i] / max(MONTHLY_PV_SHARE))
        self_consumption_rate = base_self_consumption_rate * seasonal_factor
        
        self_consumption_month = min(pv_month * self_consumption_rate, total_demand_month)
        grid_feed_in_month = pv_month - self_consumption_month
        grid_consumption_month = total_demand_month - self_consumption_month
        
        # PV to heat pump (proportional to HP share of total demand)
        hp_share = hp_electricity_month / total_demand_month if total_demand_month > 0 else 0
        pv_to_hp_month = self_consumption_month * hp_share
        
        monthly_data.append({
            "month": MONTH_NAMES[i],
            "month_number": i + 1,
            "pv_production_kwh": round(pv_month, 1),
            "household_demand_kwh": round(household_month, 1),
            "heatpump_demand_kwh": round(hp_electricity_month, 1),
            "total_demand_kwh": round(total_demand_month, 1),
            "self_consumption_kwh": round(self_consumption_month, 1),
            "grid_feed_in_kwh": round(grid_feed_in_month, 1),
            "grid_consumption_kwh": round(grid_consumption_month, 1),
            "pv_to_heatpump_kwh": round(pv_to_hp_month, 1)
        })
    
    return monthly_data


def calculate_synergy(
    monthly_data: List[Dict],
    electricity_price: float,
    feed_in_tariff: float
) -> SynergyResult:
    """Calculate synergy between PV and heat pump"""
    total_pv_to_hp = sum(m["pv_to_heatpump_kwh"] for m in monthly_data)
    total_hp_demand = sum(m["heatpump_demand_kwh"] for m in monthly_data)
    
    pv_to_hp_percent = (total_pv_to_hp / total_hp_demand * 100) if total_hp_demand > 0 else 0
    hp_from_grid = total_hp_demand - total_pv_to_hp
    hp_self_sufficiency = pv_to_hp_percent
    
    # Synergy savings: using PV electricity instead of grid for HP
    synergy_savings = total_pv_to_hp * (electricity_price - feed_in_tariff)
    
    return SynergyResult(
        pv_to_heatpump_kwh=round(total_pv_to_hp, 1),
        pv_to_heatpump_percent=round(pv_to_hp_percent, 1),
        heatpump_from_grid_kwh=round(hp_from_grid, 1),
        heatpump_self_sufficiency_percent=round(hp_self_sufficiency, 1),
        synergy_savings_eur=round(synergy_savings, 2)
    )


# ==================== API Endpoints ====================

@router.post("/calculate", response_model=CombinedResult)
async def calculate_combined(request: CombinedCalculationRequest):
    """
    Calculate combined PV + heat pump system performance.
    """
    pv = request.pv_system
    hp = request.heat_pump
    hh = request.household
    
    # Heat pump electricity consumption
    hp_consumption = hp.electricity_consumption_kwh or calculate_heatpump_consumption(
        hp.heating_demand_kwh, hp.hot_water_demand_kwh, hp.jaz
    )
    
    # Total electricity demand
    total_demand = hh.annual_consumption_kwh + hp_consumption
    
    # Monthly breakdown
    monthly_data = calculate_monthly_data(
        pv.annual_production_kwh,
        hh.annual_consumption_kwh,
        hp.heating_demand_kwh,
        hp.hot_water_demand_kwh,
        hp.jaz,
        pv.battery_capacity_kwh
    )
    
    # Aggregate from monthly data
    total_self_consumption = sum(m["self_consumption_kwh"] for m in monthly_data)
    total_grid_feed_in = sum(m["grid_feed_in_kwh"] for m in monthly_data)
    total_grid_consumption = sum(m["grid_consumption_kwh"] for m in monthly_data)
    
    # Autarky calculations
    autarky = (total_self_consumption / total_demand * 100) if total_demand > 0 else 0
    
    # Autarky without heat pump (household only)
    household_self_consumption = sum(
        min(m["self_consumption_kwh"], m["household_demand_kwh"]) 
        for m in monthly_data
    )
    autarky_without_hp = (household_self_consumption / hh.annual_consumption_kwh * 100) if hh.annual_consumption_kwh > 0 else 0
    
    # Synergy analysis
    synergy = calculate_synergy(monthly_data, pv.electricity_price_eur_kwh, pv.feed_in_tariff_eur_kwh)
    
    # Savings calculations
    # PV savings: self-consumption value + feed-in revenue
    pv_savings = (total_self_consumption * pv.electricity_price_eur_kwh + 
                  total_grid_feed_in * pv.feed_in_tariff_eur_kwh)
    
    # Heat pump savings vs. gas heating (assumed)
    gas_price = 0.10  # EUR/kWh
    gas_efficiency = 0.9
    old_heating_cost = (hp.heating_demand_kwh + hp.hot_water_demand_kwh) / gas_efficiency * gas_price
    new_heating_cost = hp_consumption * pv.electricity_price_eur_kwh
    hp_savings = old_heating_cost - new_heating_cost
    
    # Combined bonus: additional savings from synergy
    combined_bonus = synergy.synergy_savings_eur
    
    total_savings = pv_savings + hp_savings + combined_bonus
    
    return CombinedResult(
        total_electricity_demand_kwh=round(total_demand, 1),
        household_demand_kwh=round(hh.annual_consumption_kwh, 1),
        heatpump_demand_kwh=round(hp_consumption, 1),
        pv_production_kwh=round(pv.annual_production_kwh, 1),
        self_consumption_kwh=round(total_self_consumption, 1),
        self_consumption_percent=round(total_self_consumption / pv.annual_production_kwh * 100, 1),
        grid_feed_in_kwh=round(total_grid_feed_in, 1),
        grid_consumption_kwh=round(total_grid_consumption, 1),
        autarky_percent=round(autarky, 1),
        autarky_without_hp_percent=round(autarky_without_hp, 1),
        synergy=synergy,
        annual_savings_eur=round(total_savings, 2),
        pv_savings_eur=round(pv_savings, 2),
        heatpump_savings_eur=round(hp_savings, 2),
        combined_bonus_eur=round(combined_bonus, 2),
        monthly_data=monthly_data
    )


@router.get("/quick-synergy")
async def quick_synergy_calculation(
    pv_production_kwh: float = Query(..., gt=0),
    heatpump_consumption_kwh: float = Query(..., gt=0),
    household_consumption_kwh: float = Query(..., gt=0),
    battery_kwh: float = Query(0, ge=0),
    electricity_price: float = Query(0.30, ge=0.1, le=1.0)
):
    """
    Quick synergy calculation with minimal input.
    """
    total_demand = household_consumption_kwh + heatpump_consumption_kwh
    
    # Simplified self-consumption estimate
    base_rate = 0.70 if battery_kwh > 0 else 0.30
    self_consumption = min(pv_production_kwh * base_rate, total_demand)
    
    # HP share of self-consumption
    hp_share = heatpump_consumption_kwh / total_demand
    pv_to_hp = self_consumption * hp_share
    
    # Autarky
    autarky = (self_consumption / total_demand * 100)
    hp_self_sufficiency = (pv_to_hp / heatpump_consumption_kwh * 100)
    
    # Synergy savings
    synergy_savings = pv_to_hp * (electricity_price - 0.08)  # vs. feed-in
    
    return {
        "total_demand_kwh": round(total_demand, 1),
        "self_consumption_kwh": round(self_consumption, 1),
        "autarky_percent": round(autarky, 1),
        "pv_to_heatpump_kwh": round(pv_to_hp, 1),
        "heatpump_self_sufficiency_percent": round(hp_self_sufficiency, 1),
        "synergy_savings_eur": round(synergy_savings, 2),
        "recommendation": "PV und Wärmepumpe ergänzen sich optimal" if hp_self_sufficiency > 30 else "Batteriespeicher empfohlen für bessere Synergie"
    }


@router.get("/sizing-recommendation")
async def get_sizing_recommendation(
    heating_demand_kwh: float = Query(..., gt=0),
    household_consumption_kwh: float = Query(..., gt=0),
    jaz: float = Query(4.0, ge=2.0, le=6.0),
    target_autarky_percent: float = Query(50, ge=20, le=90)
):
    """
    Get PV system sizing recommendation for combined PV + heat pump.
    """
    hp_consumption = heating_demand_kwh / jaz
    total_demand = household_consumption_kwh + hp_consumption
    
    # Estimate required PV production for target autarky
    # Assuming 35% self-consumption rate without battery
    self_consumption_rate = 0.35
    required_self_consumption = total_demand * (target_autarky_percent / 100)
    required_pv_production = required_self_consumption / self_consumption_rate
    
    # Convert to kWp (assuming 950 kWh/kWp in Germany)
    specific_yield = 950
    recommended_kwp = required_pv_production / specific_yield
    
    # Battery recommendation
    recommended_battery = hp_consumption * 0.1  # 10% of HP consumption
    
    return {
        "total_demand_kwh": round(total_demand, 0),
        "household_demand_kwh": round(household_consumption_kwh, 0),
        "heatpump_demand_kwh": round(hp_consumption, 0),
        "target_autarky_percent": target_autarky_percent,
        "recommended_pv_kwp": round(recommended_kwp, 1),
        "recommended_pv_production_kwh": round(required_pv_production, 0),
        "recommended_battery_kwh": round(recommended_battery, 1),
        "note": f"Für {target_autarky_percent}% Autarkie empfehlen wir eine {recommended_kwp:.1f} kWp PV-Anlage"
    }


@router.get("/health/check")
async def health_check():
    """Health check for PV + heat pump integration service."""
    return {
        "status": "healthy",
        "service": "pv-heatpump-integration",
        "timestamp": datetime.now().isoformat()
    }
