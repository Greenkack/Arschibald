"""
Battery Storage Pydantic Schemas

Request and response models for battery storage API endpoints.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BatterySpecsResponse(BaseModel):
    """Battery specifications response"""
    capacity_kwh: float
    usable_capacity_kwh: float
    max_charge_rate_kw: float
    max_discharge_rate_kw: float
    efficiency: float
    depth_of_discharge: float
    warranty_years: int
    warranty_cycles: int
    cost_per_kwh: float
    degradation_rate_per_year: float


class BatterySizingRequest(BaseModel):
    """Request for battery sizing calculation"""
    daily_consumption_kwh: float = Field(..., gt=0, description="Daily energy consumption in kWh")
    pv_system_size_kwp: float = Field(..., gt=0, description="PV system size in kWp")
    annual_production_kwh: float = Field(..., gt=0, description="Annual PV production in kWh")
    self_consumption_rate: float = Field(..., ge=0, le=1, description="Current self-consumption rate (0-1)")
    grid_feed_in_tariff: float = Field(..., ge=0, description="Grid feed-in tariff in €/kWh")
    electricity_price: float = Field(..., gt=0, description="Electricity price in €/kWh")
    backup_hours: Optional[int] = Field(None, ge=0, description="Hours of backup power needed")
    target_self_sufficiency: Optional[float] = Field(None, ge=0, le=1, description="Target self-sufficiency rate (0-1)")


class BatterySizingResponse(BaseModel):
    """Response for battery sizing calculation"""
    recommended_capacity_kwh: float
    selected_battery: str
    battery_specs: BatterySpecsResponse
    performance: Dict[str, Any]
    sizing_rationale: Dict[str, Any]


class BatteryROIRequest(BaseModel):
    """Request for battery ROI analysis"""
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    daily_consumption_kwh: float = Field(..., gt=0, description="Daily energy consumption in kWh")
    pv_system_size_kwp: float = Field(..., gt=0, description="PV system size in kWp")
    annual_production_kwh: float = Field(..., gt=0, description="Annual PV production in kWh")
    self_consumption_rate: float = Field(..., ge=0, le=1, description="Current self-consumption rate (0-1)")
    grid_feed_in_tariff: float = Field(..., ge=0, description="Grid feed-in tariff in €/kWh")
    electricity_price: float = Field(..., gt=0, description="Electricity price in €/kWh")
    analysis_years: int = Field(20, ge=1, le=30, description="Years to analyze")


class BatteryROIResponse(BaseModel):
    """Response for battery ROI analysis"""
    initial_investment: float
    annual_savings_year_1: float
    lifetime_savings: float
    simple_payback_years: float
    payback_year: Optional[int]
    npv: float
    roi_percent: float
    cash_flow_analysis: List[Dict[str, Any]]
    savings_breakdown: Dict[str, float]


class DischargeStrategyRequest(BaseModel):
    """Request for discharge strategy simulation"""
    strategy_type: str = Field(..., description="Strategy type: peak_shaving, self_consumption, time_of_use, backup")
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    hourly_production: List[float] = Field(..., min_items=24, max_items=24, description="Hourly production for 24 hours")
    hourly_consumption: List[float] = Field(..., min_items=24, max_items=24, description="Hourly consumption for 24 hours")
    peak_hours: Optional[List[int]] = Field(None, description="Peak hours (0-23)")
    min_soc: float = Field(0.2, ge=0, le=1, description="Minimum state of charge (0-1)")
    max_soc: float = Field(1.0, ge=0, le=1, description="Maximum state of charge (0-1)")
    priority: str = Field("self_consumption", description="Priority: self_consumption, grid_export, backup")


class DischargeStrategyResponse(BaseModel):
    """Response for discharge strategy simulation"""
    strategy_type: str
    schedule: List[Dict[str, Any]]
    performance: Dict[str, Any]


class GridIndependenceRequest(BaseModel):
    """Request for grid independence calculation"""
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    daily_consumption_kwh: float = Field(..., gt=0, description="Daily energy consumption in kWh")
    pv_system_size_kwp: float = Field(..., gt=0, description="PV system size in kWp")
    annual_production_kwh: float = Field(..., gt=0, description="Annual PV production in kWh")
    self_consumption_rate: float = Field(..., ge=0, le=1, description="Current self-consumption rate (0-1)")
    monthly_production: List[float] = Field(..., min_items=12, max_items=12, description="Monthly production in kWh")
    monthly_consumption: List[float] = Field(..., min_items=12, max_items=12, description="Monthly consumption in kWh")


class GridIndependenceResponse(BaseModel):
    """Response for grid independence calculation"""
    monthly_analysis: List[Dict[str, Any]]
    annual_metrics: Dict[str, Any]
    comparison: Dict[str, float]


class LifecycleAnalysisRequest(BaseModel):
    """Request for lifecycle analysis"""
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    daily_cycles: float = Field(1.0, ge=0, le=5, description="Average daily cycles")
    analysis_years: int = Field(20, ge=1, le=30, description="Years to analyze")


class LifecycleAnalysisResponse(BaseModel):
    """Response for lifecycle analysis"""
    battery_specs: BatterySpecsResponse
    lifecycle_parameters: Dict[str, Any]
    capacity_timeline: List[Dict[str, Any]]
    replacement_schedule: List[Dict[str, Any]]
    cost_analysis: Dict[str, float]
    end_of_life: Dict[str, Any]


class MonitoringIntegrationRequest(BaseModel):
    """Request for monitoring integration configuration"""
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    monitoring_system: str = Field("generic", description="Monitoring system: generic, tesla_powerwall, sonnen_battery, lg_resu")


class MonitoringIntegrationResponse(BaseModel):
    """Response for monitoring integration configuration"""
    battery_specs: BatterySpecsResponse
    monitoring_system: str
    configuration: Dict[str, Any]
    data_points: Dict[str, List[Dict[str, Any]]]
    alert_thresholds: Dict[str, List[Dict[str, Any]]]
    recommended_polling_intervals: Dict[str, str]
    integration_endpoints: Dict[str, str]
