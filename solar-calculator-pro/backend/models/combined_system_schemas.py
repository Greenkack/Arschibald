"""
Pydantic schemas for combined Heat Pump + PV system integration.
Defines request/response models for combined system optimization and analysis.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ControlStrategy(str, Enum):
    """Smart control strategies for combined systems"""
    SELF_CONSUMPTION = "self_consumption"  # Maximize PV self-consumption
    COST_OPTIMIZATION = "cost_optimization"  # Minimize total energy costs
    GRID_INDEPENDENCE = "grid_independence"  # Maximize independence from grid
    COMFORT_PRIORITY = "comfort_priority"  # Prioritize heating comfort
    BALANCED = "balanced"  # Balance all factors


class TimeOfUseProfile(BaseModel):
    """Time-of-use electricity tariff profile"""
    hour: int = Field(..., ge=0, le=23)
    price_per_kwh: float = Field(..., gt=0)
    is_peak: bool = False


class CombinedSystemRequest(BaseModel):
    """Request for combined heat pump + PV system analysis"""
    # PV System Parameters
    pv_system_size: float = Field(..., gt=0, description="PV system size in kWp")
    pv_annual_production: float = Field(..., gt=0, description="Annual PV production in kWh")
    pv_module_count: int = Field(..., gt=0)
    pv_orientation: str
    pv_tilt_angle: float = Field(..., ge=0, le=90)
    
    # Heat Pump Parameters
    hp_model: str
    hp_cop: float = Field(..., gt=1, le=6, description="Coefficient of Performance")
    hp_heating_capacity: float = Field(..., gt=0, description="Heating capacity in kW")
    hp_power_consumption: float = Field(..., gt=0, description="Electrical power consumption in kW")
    
    # Building Parameters
    annual_heating_demand: float = Field(..., gt=0, description="Annual heating demand in kWh")
    building_insulation_quality: str = Field(..., description="poor, average, good, excellent")
    
    # Battery Storage (optional)
    battery_capacity: Optional[float] = Field(None, ge=0, description="Battery capacity in kWh")
    battery_efficiency: Optional[float] = Field(0.95, ge=0.8, le=1.0)
    
    # Tariff Information
    electricity_price: float = Field(..., gt=0, description="Electricity price in €/kWh")
    feed_in_tariff: float = Field(..., ge=0, description="Feed-in tariff in €/kWh")
    time_of_use_tariff: Optional[List[TimeOfUseProfile]] = None
    
    # Control Strategy
    control_strategy: ControlStrategy = ControlStrategy.BALANCED
    
    # Location
    location: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class HourlyEnergyFlow(BaseModel):
    """Hourly energy flow in the combined system"""
    hour: int = Field(..., ge=0, le=23)
    pv_production: float = Field(..., ge=0)
    hp_consumption: float = Field(..., ge=0)
    household_consumption: float = Field(..., ge=0)
    battery_charge: float = 0.0
    battery_discharge: float = 0.0
    grid_import: float = 0.0
    grid_export: float = 0.0
    self_consumption: float = 0.0
    electricity_cost: float = 0.0


class SynergyAnalysis(BaseModel):
    """Analysis of synergies between PV and heat pump"""
    pv_to_hp_direct: float = Field(..., description="PV energy directly used by heat pump in kWh")
    pv_to_hp_via_battery: float = Field(..., description="PV energy used by HP via battery in kWh")
    total_pv_for_heating: float = Field(..., description="Total PV energy for heating in kWh")
    heating_cost_reduction: float = Field(..., description="Heating cost reduction in €")
    heating_cost_reduction_percent: float = Field(..., description="Heating cost reduction in %")
    cop_improvement: float = Field(..., description="Effective COP improvement due to PV")
    grid_independence_heating: float = Field(..., description="Grid independence for heating in %")


class SmartControlSchedule(BaseModel):
    """Smart control schedule for heat pump operation"""
    hour: int = Field(..., ge=0, le=23)
    hp_operation_mode: str = Field(..., description="on, off, modulated")
    hp_power_level: float = Field(..., ge=0, le=1, description="Power level 0-1")
    reason: str = Field(..., description="Reason for this control decision")
    expected_pv_production: float = 0.0
    expected_electricity_price: float = 0.0


class CombinedFinancialAnalysis(BaseModel):
    """Financial analysis for combined system"""
    # Investment
    total_investment: float
    pv_system_cost: float
    heat_pump_cost: float
    battery_cost: float
    installation_cost: float
    
    # Annual Costs and Savings
    annual_electricity_cost_baseline: float = Field(..., description="Without PV+HP")
    annual_electricity_cost_combined: float = Field(..., description="With PV+HP")
    annual_savings: float
    annual_heating_cost_baseline: float = Field(..., description="Conventional heating")
    annual_heating_cost_hp: float = Field(..., description="With heat pump")
    annual_heating_savings: float
    
    # PV Economics
    annual_pv_self_consumption_value: float
    annual_pv_feed_in_revenue: float
    pv_self_consumption_rate: float = Field(..., ge=0, le=1)
    
    # ROI Metrics
    simple_payback_years: float
    npv_20_years: float = Field(..., description="Net Present Value over 20 years")
    irr: float = Field(..., description="Internal Rate of Return in %")
    lcoe: float = Field(..., description="Levelized Cost of Energy in €/kWh")
    
    # Cumulative Cash Flow
    cumulative_cash_flow_10_years: float
    cumulative_cash_flow_20_years: float


class SystemMonitoringData(BaseModel):
    """Real-time monitoring data for combined system"""
    timestamp: datetime
    
    # PV System
    pv_current_power: float = Field(..., ge=0, description="Current PV power in kW")
    pv_daily_production: float = Field(..., ge=0)
    pv_monthly_production: float = Field(..., ge=0)
    pv_annual_production: float = Field(..., ge=0)
    
    # Heat Pump
    hp_status: str = Field(..., description="on, off, standby")
    hp_current_power: float = Field(..., ge=0)
    hp_current_cop: float = Field(..., gt=0)
    hp_daily_consumption: float = Field(..., ge=0)
    hp_supply_temperature: float
    hp_return_temperature: float
    
    # Battery (if present)
    battery_soc: Optional[float] = Field(None, ge=0, le=100, description="State of Charge in %")
    battery_power: Optional[float] = None  # Positive = charging, negative = discharging
    
    # Grid
    grid_power: float  # Positive = import, negative = export
    grid_daily_import: float = Field(..., ge=0)
    grid_daily_export: float = Field(..., ge=0)
    
    # Performance Metrics
    self_consumption_rate_today: float = Field(..., ge=0, le=1)
    grid_independence_rate_today: float = Field(..., ge=0, le=1)
    cost_savings_today: float


class CombinedSystemResponse(BaseModel):
    """Response with complete combined system analysis"""
    # System Configuration
    system_configuration: Dict[str, Any]
    
    # Optimization Results
    optimized_control_strategy: ControlStrategy
    annual_energy_flow: Dict[str, float]
    hourly_energy_flows: List[HourlyEnergyFlow]
    
    # Synergy Analysis
    synergy_analysis: SynergyAnalysis
    
    # Smart Control
    smart_control_schedule: List[SmartControlSchedule]
    control_recommendations: List[str]
    
    # Financial Analysis
    financial_analysis: CombinedFinancialAnalysis
    
    # Performance Metrics
    self_consumption_rate: float = Field(..., ge=0, le=1, description="Overall self-consumption rate")
    grid_independence_rate: float = Field(..., ge=0, le=1, description="Grid independence rate")
    renewable_energy_rate: float = Field(..., ge=0, le=1, description="Renewable energy rate")
    
    # Environmental Impact
    annual_co2_savings: float = Field(..., description="CO2 savings in kg")
    equivalent_trees_planted: int
    
    # Comparison with Alternatives
    comparison_pv_only: Dict[str, float]
    comparison_hp_only: Dict[str, float]
    comparison_conventional: Dict[str, float]
    synergy_benefit: float = Field(..., description="Additional benefit from combination in €")


class OptimizationRequest(BaseModel):
    """Request for system optimization"""
    system_id: int
    optimization_goal: str = Field(..., description="minimize_cost, maximize_self_consumption, maximize_comfort")
    constraints: Dict[str, Any] = {}
    time_horizon_days: int = Field(7, ge=1, le=365)


class OptimizationResponse(BaseModel):
    """Response with optimization results"""
    optimized_schedule: List[SmartControlSchedule]
    expected_savings: float
    expected_self_consumption_rate: float
    optimization_quality: float = Field(..., ge=0, le=1, description="Quality score 0-1")
    computation_time_ms: float
