"""
Inverter Pydantic Schemas

Data validation and serialization schemas for inverter management.

Requirements: 1.3, 6.1
"""

from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional
from datetime import datetime


class InverterBase(BaseModel):
    """Base inverter schema"""
    model_name: str = Field(..., description="Inverter model name")
    manufacturer: str = Field(..., description="Manufacturer/brand name")
    power_kw: float = Field(..., gt=0, description="Rated AC power in kW")
    efficiency_percent: float = Field(default=97.0, ge=90, le=100, description="Peak efficiency percentage")
    max_dc_voltage: float = Field(default=1000.0, gt=0, description="Maximum DC input voltage")
    mppt_count: int = Field(default=2, ge=1, le=12, description="Number of MPPT trackers")
    max_dc_current: float = Field(default=30.0, gt=0, description="Maximum DC input current per MPPT")


class InverterCreate(InverterBase):
    """Schema for creating a new inverter"""
    price_netto: float = Field(default=0.0, ge=0, description="Net price in EUR")
    additional_cost_netto: float = Field(default=0.0, ge=0, description="Additional costs in EUR")
    warranty_years: int = Field(default=10, ge=0, description="Warranty period in years")
    weight_kg: float = Field(default=0.0, ge=0, description="Weight in kg")
    description: Optional[str] = Field(default="", description="Product description")
    technology: Optional[str] = Field(default="", description="Technology type")
    
    @validator('efficiency_percent')
    def validate_efficiency(cls, v):
        if v < 90 or v > 100:
            raise ValueError('Efficiency must be between 90% and 100%')
        return v


class InverterUpdate(BaseModel):
    """Schema for updating an inverter"""
    model_name: Optional[str] = None
    manufacturer: Optional[str] = None
    power_kw: Optional[float] = Field(None, gt=0)
    efficiency_percent: Optional[float] = Field(None, ge=90, le=100)
    max_dc_voltage: Optional[float] = Field(None, gt=0)
    mppt_count: Optional[int] = Field(None, ge=1, le=12)
    max_dc_current: Optional[float] = Field(None, gt=0)
    price_netto: Optional[float] = Field(None, ge=0)
    additional_cost_netto: Optional[float] = Field(None, ge=0)
    warranty_years: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    technology: Optional[str] = None


class InverterResponse(InverterBase):
    """Schema for inverter response"""
    id: int
    price_netto: float
    additional_cost_netto: float
    warranty_years: int
    weight_kg: float
    description: str
    technology: str
    features: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True


class InverterSpecifications(BaseModel):
    """Detailed inverter specifications"""
    power_kw: float = Field(..., description="Rated AC power")
    efficiency_percent: float = Field(..., description="Peak efficiency")
    max_dc_voltage: float = Field(..., description="Maximum DC voltage")
    mppt_count: int = Field(..., description="Number of MPPT trackers")
    max_dc_current: float = Field(..., description="Maximum DC current per MPPT")
    input_voltage_range: Optional[Dict[str, float]] = Field(
        default=None,
        description="DC input voltage range (min/max)"
    )
    output_voltage: Optional[float] = Field(default=230.0, description="AC output voltage")
    output_frequency: Optional[float] = Field(default=50.0, description="AC output frequency")
    protection_class: Optional[str] = Field(default="IP65", description="Protection class")
    cooling_method: Optional[str] = Field(default="Natural convection", description="Cooling method")
    operating_temperature_range: Optional[Dict[str, float]] = Field(
        default=None,
        description="Operating temperature range (min/max)"
    )


class InverterSelectionCriteria(BaseModel):
    """Criteria for inverter selection"""
    pv_power_kwp: float = Field(..., gt=0, description="PV system power in kWp")
    system_voltage: float = Field(default=400.0, description="System voltage")
    preferred_manufacturer: Optional[str] = Field(default=None, description="Preferred manufacturer")
    required_features: Optional[List[str]] = Field(default_factory=list, description="Required features")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    min_efficiency: Optional[float] = Field(default=95.0, ge=90, le=100, description="Minimum efficiency")


class InverterSelectionResult(BaseModel):
    """Result of inverter selection"""
    selected_inverter: InverterResponse
    selection_score: float = Field(..., ge=0, le=100, description="Selection score (0-100)")
    sizing_ratio: float = Field(..., description="DC/AC sizing ratio")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative inverters")
    selection_reasoning: str = Field(..., description="Reasoning for selection")


class StringConfiguration(BaseModel):
    """PV string configuration"""
    modules_per_string: int = Field(..., gt=0, description="Number of modules per string")
    number_of_strings: int = Field(..., gt=0, description="Total number of strings")
    module_voltage: float = Field(..., gt=0, description="Module voltage (Vmp)")
    module_current: float = Field(..., gt=0, description="Module current (Imp)")


class InverterSizingRequest(BaseModel):
    """Request for inverter sizing calculations"""
    pv_power_kwp: float = Field(..., gt=0, description="PV system power in kWp")
    module_voltage: float = Field(..., gt=0, description="Module voltage (Vmp)")
    module_current: float = Field(..., gt=0, description="Module current (Imp)")
    string_configuration: StringConfiguration


class InverterSizingResult(BaseModel):
    """Result of inverter sizing calculations"""
    required_power_kw: float = Field(..., description="Required inverter power")
    recommended_power_range: Dict[str, float] = Field(..., description="Recommended power range")
    dc_specifications: Dict[str, float] = Field(..., description="DC input specifications")
    mppt_configuration: Dict[str, Any] = Field(..., description="MPPT configuration")
    sizing_ratio: Dict[str, Any] = Field(..., description="DC/AC sizing ratio")
    safety_margins: Dict[str, int] = Field(..., description="Safety margins")


class PVSystemSpecifications(BaseModel):
    """PV system specifications for compatibility check"""
    pv_power_kwp: float = Field(..., gt=0, description="PV system power")
    string_voltage: float = Field(..., gt=0, description="String voltage")
    total_current: float = Field(..., gt=0, description="Total DC current")
    number_of_strings: int = Field(..., gt=0, description="Number of strings")
    module_type: Optional[str] = Field(default=None, description="Module type")


class CompatibilityCheck(BaseModel):
    """Single compatibility check result"""
    check: str = Field(..., description="Check name")
    status: str = Field(..., description="Status: OK, WARNUNG, FEHLER")
    details: str = Field(..., description="Check details")


class CompatibilityCheckResult(BaseModel):
    """Result of compatibility check"""
    is_compatible: bool = Field(..., description="Overall compatibility")
    compatibility_score: float = Field(..., ge=0, le=100, description="Compatibility score")
    checks: List[CompatibilityCheck] = Field(..., description="Individual checks")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    recommendation: str = Field(..., description="Recommendation")


class RoofSection(BaseModel):
    """Roof section specification"""
    section_id: str = Field(..., description="Section identifier")
    orientation: float = Field(..., ge=0, le=360, description="Azimuth angle")
    tilt: float = Field(..., ge=0, le=90, description="Tilt angle")
    area_sqm: float = Field(..., gt=0, description="Area in square meters")
    power_kwp: float = Field(..., gt=0, description="Assigned PV power")


class SystemLayout(BaseModel):
    """System layout with multiple roof sections"""
    roof_sections: List[RoofSection] = Field(..., description="Roof sections")
    total_power_kwp: float = Field(..., gt=0, description="Total system power")


class InverterAssignment(BaseModel):
    """Inverter assignment to roof section"""
    inverter_index: int = Field(..., description="Inverter index")
    inverter: InverterResponse
    assigned_power_kwp: float = Field(..., description="Assigned PV power")
    roof_section: Optional[RoofSection] = Field(default=None, description="Assigned roof section")


class MultiInverterConfiguration(BaseModel):
    """Multi-inverter system configuration"""
    configuration_type: str = Field(..., description="Configuration type: single or multi")
    inverter_count: int = Field(..., gt=0, description="Number of inverters")
    inverters: List[InverterResponse] = Field(..., description="Selected inverters")
    total_power_kw: float = Field(..., description="Total inverter power")
    power_distribution: Optional[List[InverterAssignment]] = Field(
        default=None,
        description="Power distribution across inverters"
    )
    sizing_ratio: Optional[float] = Field(default=None, description="Overall DC/AC ratio")
    reasoning: str = Field(..., description="Configuration reasoning")


class MonitoringConfiguration(BaseModel):
    """Monitoring system configuration"""
    protocol: str = Field(default="Modbus TCP", description="Communication protocol")
    update_interval: int = Field(default=60, ge=1, description="Update interval in seconds")
    retention_days: int = Field(default=365, ge=1, description="Data retention period")
    enable_alerts: bool = Field(default=True, description="Enable alert notifications")


class MonitoringDataPoint(BaseModel):
    """Monitoring data point"""
    name: str = Field(..., description="Data point name")
    unit: str = Field(..., description="Unit of measurement")
    description: str = Field(..., description="Data point description")


class MonitoringAlert(BaseModel):
    """Monitoring alert configuration"""
    type: str = Field(..., description="Alert type")
    threshold: Optional[float] = Field(default=None, description="Alert threshold")
    description: str = Field(..., description="Alert description")


class MonitoringIntegrationResult(BaseModel):
    """Result of monitoring integration"""
    monitoring_supported: bool = Field(..., description="Monitoring support status")
    inverter_id: Optional[int] = Field(default=None, description="Inverter ID")
    inverter_model: Optional[str] = Field(default=None, description="Inverter model")
    manufacturer: Optional[str] = Field(default=None, description="Manufacturer")
    communication_protocol: Optional[str] = Field(default=None, description="Protocol")
    data_points: Optional[List[str]] = Field(default=None, description="Available data points")
    update_interval_seconds: Optional[int] = Field(default=None, description="Update interval")
    data_retention_days: Optional[int] = Field(default=None, description="Data retention")
    alerts: Optional[List[MonitoringAlert]] = Field(default=None, description="Alert configuration")
    api_endpoints: Optional[Dict[str, str]] = Field(default=None, description="API endpoints")
    message: Optional[str] = Field(default=None, description="Status message")
    alternative: Optional[str] = Field(default=None, description="Alternative solution")


class InverterPerformanceData(BaseModel):
    """Inverter performance data"""
    timestamp: datetime = Field(..., description="Data timestamp")
    ac_power_kw: float = Field(..., description="AC power output")
    dc_power_kw: float = Field(..., description="DC power input")
    efficiency_percent: float = Field(..., description="Current efficiency")
    daily_energy_kwh: float = Field(..., description="Daily energy production")
    total_energy_kwh: float = Field(..., description="Total energy production")
    dc_voltage: float = Field(..., description="DC voltage")
    dc_current: float = Field(..., description="DC current")
    ac_voltage: float = Field(..., description="AC voltage")
    ac_current: float = Field(..., description="AC current")
    temperature_celsius: float = Field(..., description="Inverter temperature")
    status: str = Field(..., description="Inverter status")
    error_codes: List[str] = Field(default_factory=list, description="Active error codes")


class InverterStatistics(BaseModel):
    """Inverter statistics"""
    inverter_id: int = Field(..., description="Inverter ID")
    period_start: datetime = Field(..., description="Statistics period start")
    period_end: datetime = Field(..., description="Statistics period end")
    total_energy_kwh: float = Field(..., description="Total energy in period")
    average_efficiency_percent: float = Field(..., description="Average efficiency")
    peak_power_kw: float = Field(..., description="Peak power")
    operating_hours: float = Field(..., description="Operating hours")
    availability_percent: float = Field(..., description="Availability percentage")
    error_count: int = Field(..., description="Number of errors")
