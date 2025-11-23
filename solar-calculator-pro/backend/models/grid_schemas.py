"""
Grid Integration Schemas
Pydantic models for solar grid integration calculations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GridConnectionType(str, Enum):
    """Types of grid connections"""
    SINGLE_PHASE = "single_phase"
    THREE_PHASE = "three_phase"
    MICRO_GRID = "micro_grid"


class MeteringType(str, Enum):
    """Types of metering systems"""
    NET_METERING = "net_metering"
    FEED_IN_TARIFF = "feed_in_tariff"
    GROSS_METERING = "gross_metering"
    SELF_CONSUMPTION = "self_consumption"


class PowerQualityStandard(str, Enum):
    """Power quality standards"""
    IEEE_1547 = "ieee_1547"
    EN_50160 = "en_50160"
    VDE_AR_N_4105 = "vde_ar_n_4105"
    IEC_61727 = "iec_61727"


class FeedInTariffRequest(BaseModel):
    """Request for feed-in tariff calculations"""
    system_size_kwp: float = Field(..., gt=0, description="System size in kWp")
    annual_production_kwh: float = Field(..., gt=0, description="Annual production in kWh")
    self_consumption_rate: float = Field(..., ge=0, le=1, description="Self-consumption rate (0-1)")
    feed_in_tariff_per_kwh: float = Field(..., gt=0, description="Feed-in tariff in €/kWh")
    electricity_price_per_kwh: float = Field(..., gt=0, description="Electricity price in €/kWh")
    contract_duration_years: int = Field(20, ge=1, le=30, description="Contract duration in years")
    degradation_rate: float = Field(0.005, ge=0, le=0.02, description="Annual degradation rate")


class FeedInTariffResponse(BaseModel):
    """Response for feed-in tariff calculations"""
    annual_feed_in_kwh: float
    annual_feed_in_revenue: float
    annual_self_consumption_kwh: float
    annual_self_consumption_savings: float
    total_annual_benefit: float
    lifetime_feed_in_revenue: float
    lifetime_self_consumption_savings: float
    total_lifetime_benefit: float
    average_benefit_per_kwp: float
    payback_period_years: Optional[float]


class NetMeteringRequest(BaseModel):
    """Request for net metering analysis"""
    system_size_kwp: float = Field(..., gt=0)
    annual_production_kwh: float = Field(..., gt=0)
    annual_consumption_kwh: float = Field(..., gt=0)
    electricity_price_per_kwh: float = Field(..., gt=0)
    net_metering_credit_per_kwh: float = Field(..., gt=0)
    monthly_production: List[float] = Field(..., min_length=12, max_length=12)
    monthly_consumption: List[float] = Field(..., min_length=12, max_length=12)
    rollover_allowed: bool = Field(True, description="Allow credit rollover to next month")
    max_rollover_months: int = Field(12, ge=1, le=12)


class NetMeteringResponse(BaseModel):
    """Response for net metering analysis"""
    annual_net_export_kwh: float
    annual_net_import_kwh: float
    annual_credits_earned: float
    annual_credits_used: float
    annual_net_savings: float
    monthly_analysis: List[Dict[str, float]]
    self_sufficiency_rate: float
    grid_independence_rate: float
    optimal_system_size_kwp: float


class GridConnectionRequest(BaseModel):
    """Request for grid connection requirements"""
    system_size_kwp: float = Field(..., gt=0)
    connection_type: GridConnectionType
    voltage_level: int = Field(..., description="Voltage level in V (e.g., 230, 400)")
    distance_to_grid_m: float = Field(..., ge=0)
    inverter_power_kw: float = Field(..., gt=0)
    location: str
    building_type: str = Field("residential", description="residential, commercial, industrial")


class GridConnectionResponse(BaseModel):
    """Response for grid connection requirements"""
    connection_feasible: bool
    required_cable_size_mm2: float
    estimated_connection_cost: float
    voltage_drop_percent: float
    max_fault_current_a: float
    required_protection_devices: List[str]
    grid_capacity_sufficient: bool
    additional_requirements: List[str]
    estimated_approval_time_days: int
    connection_type_recommended: GridConnectionType


class PowerQualityRequest(BaseModel):
    """Request for power quality analysis"""
    system_size_kwp: float = Field(..., gt=0)
    inverter_specs: Dict[str, float]
    grid_voltage: int
    grid_frequency: float = Field(50.0, description="Grid frequency in Hz")
    standard: PowerQualityStandard
    harmonic_limits: Optional[Dict[str, float]] = None


class PowerQualityResponse(BaseModel):
    """Response for power quality analysis"""
    compliant: bool
    voltage_regulation_percent: float
    frequency_deviation_hz: float
    power_factor: float
    total_harmonic_distortion_percent: float
    individual_harmonics: Dict[str, float]
    flicker_severity: float
    dc_injection_ma: float
    compliance_issues: List[str]
    recommendations: List[str]


class GridStabilityRequest(BaseModel):
    """Request for grid stability calculations"""
    system_size_kwp: float = Field(..., gt=0)
    grid_short_circuit_power_mva: float = Field(..., gt=0)
    grid_impedance_ohm: float = Field(..., gt=0)
    inverter_response_time_ms: float = Field(..., gt=0)
    enable_reactive_power_support: bool = True
    enable_voltage_regulation: bool = True


class GridStabilityResponse(BaseModel):
    """Response for grid stability calculations"""
    stability_index: float = Field(..., ge=0, le=1, description="0=unstable, 1=very stable")
    short_circuit_ratio: float
    voltage_stability_margin: float
    frequency_stability_margin: float
    reactive_power_capability_kvar: float
    grid_support_services: List[str]
    stability_concerns: List[str]
    recommended_settings: Dict[str, float]


class SmartGridRequest(BaseModel):
    """Request for smart grid integration"""
    system_size_kwp: float = Field(..., gt=0)
    battery_capacity_kwh: Optional[float] = None
    enable_demand_response: bool = True
    enable_frequency_regulation: bool = True
    enable_voltage_support: bool = True
    time_of_use_tariff: Optional[Dict[str, float]] = None


class SmartGridResponse(BaseModel):
    """Response for smart grid integration"""
    smart_grid_ready: bool
    available_services: List[str]
    potential_revenue_streams: Dict[str, float]
    annual_grid_services_revenue: float
    demand_response_capacity_kw: float
    frequency_regulation_capability: bool
    voltage_support_capability: bool
    recommended_upgrades: List[str]
    integration_cost: float
    payback_period_years: Optional[float]


class GridIntegrationAnalysisRequest(BaseModel):
    """Comprehensive grid integration analysis request"""
    system_size_kwp: float = Field(..., gt=0)
    annual_production_kwh: float = Field(..., gt=0)
    annual_consumption_kwh: float = Field(..., gt=0)
    location: str
    connection_type: GridConnectionType
    metering_type: MeteringType
    feed_in_tariff_per_kwh: float = Field(..., gt=0)
    electricity_price_per_kwh: float = Field(..., gt=0)
    grid_voltage: int
    distance_to_grid_m: float = Field(..., ge=0)
    battery_capacity_kwh: Optional[float] = None
    enable_smart_grid: bool = False


class GridIntegrationAnalysisResponse(BaseModel):
    """Comprehensive grid integration analysis response"""
    feed_in_analysis: FeedInTariffResponse
    net_metering_analysis: Optional[NetMeteringResponse]
    connection_requirements: GridConnectionResponse
    power_quality: PowerQualityResponse
    grid_stability: GridStabilityResponse
    smart_grid_potential: Optional[SmartGridResponse]
    total_annual_benefit: float
    total_lifetime_benefit: float
    recommended_configuration: Dict[str, Any]
    compliance_status: str
    overall_feasibility_score: float = Field(..., ge=0, le=100)
