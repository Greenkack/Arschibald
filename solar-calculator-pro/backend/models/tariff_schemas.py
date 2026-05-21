"""
Pydantic schemas for dynamic tariff optimization
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, time
from enum import Enum


class TariffType(str, Enum):
    """Types of electricity tariffs"""
    FLAT_RATE = "flat_rate"
    TIME_OF_USE = "time_of_use"
    DYNAMIC = "dynamic"
    REAL_TIME = "real_time"


class TariffPeriod(BaseModel):
    """Time period with specific tariff rate"""
    start_time: time
    end_time: time
    rate: float = Field(..., description="Rate in EUR/kWh")
    name: str = Field(..., description="Period name (e.g., 'peak', 'off-peak')")


class TariffStructure(BaseModel):
    """Complete tariff structure"""
    tariff_id: str
    name: str
    type: TariffType
    base_rate: float = Field(..., description="Base rate in EUR/kWh")
    periods: List[TariffPeriod] = []
    weekday_periods: Optional[List[TariffPeriod]] = None
    weekend_periods: Optional[List[TariffPeriod]] = None
    seasonal_adjustment: Optional[Dict[str, float]] = None


class HeatingSchedule(BaseModel):
    """Heating schedule for optimization"""
    hour: int = Field(..., ge=0, lt=24)
    target_temperature: float = Field(..., description="Target temperature in °C")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1=low, 5=high)")
    flexible: bool = Field(default=True, description="Can be shifted to cheaper periods")


class OptimizationRequest(BaseModel):
    """Request for tariff optimization"""
    tariff_structure: TariffStructure
    heat_pump_cop: float = Field(..., gt=0, description="Coefficient of Performance")
    annual_heating_demand: float = Field(..., gt=0, description="Annual heating demand in kWh")
    building_thermal_mass: float = Field(default=50.0, description="Thermal mass in kWh/K")
    current_schedule: List[HeatingSchedule]
    optimization_horizon_days: int = Field(default=7, ge=1, le=30)
    comfort_priority: float = Field(default=0.7, ge=0, le=1, description="0=cost, 1=comfort")


class OptimizedSchedule(BaseModel):
    """Optimized heating schedule"""
    hour: int
    target_temperature: float
    estimated_consumption: float = Field(..., description="Estimated consumption in kWh")
    tariff_rate: float = Field(..., description="Tariff rate in EUR/kWh")
    cost: float = Field(..., description="Cost in EUR")
    shifted_from: Optional[int] = None


class OptimizationResult(BaseModel):
    """Result of tariff optimization"""
    original_cost: float = Field(..., description="Original annual cost in EUR")
    optimized_cost: float = Field(..., description="Optimized annual cost in EUR")
    savings: float = Field(..., description="Annual savings in EUR")
    savings_percent: float = Field(..., description="Savings percentage")
    optimized_schedule: List[OptimizedSchedule]
    peak_load_reduction: float = Field(..., description="Peak load reduction in kW")
    comfort_score: float = Field(..., ge=0, le=1, description="Comfort score (0-1)")


class TariffComparison(BaseModel):
    """Comparison of different tariffs"""
    tariff_name: str
    tariff_type: TariffType
    annual_cost: float
    potential_savings: float
    recommended: bool
    pros: List[str]
    cons: List[str]


class DemandResponseEvent(BaseModel):
    """Demand response event"""
    event_id: str
    start_time: datetime
    end_time: datetime
    incentive_rate: float = Field(..., description="Incentive in EUR/kWh")
    required_reduction: float = Field(..., description="Required load reduction in kW")
    participation_status: str = Field(default="pending")


class RealTimeTariffData(BaseModel):
    """Real-time tariff data"""
    timestamp: datetime
    current_rate: float = Field(..., description="Current rate in EUR/kWh")
    forecast_next_hour: float
    forecast_next_4_hours: List[float]
    forecast_next_24_hours: List[float]
    grid_load_level: str = Field(..., description="low, medium, high, critical")
