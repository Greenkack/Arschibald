"""
Solar Calculator Pydantic Models

This module defines request and response schemas for the Solar Calculator Service.
All models use Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class RoofOrientation(str, Enum):
    """Roof orientation options"""
    SOUTH = "Süd"
    SOUTHEAST = "Südost"
    SOUTHWEST = "Südwest"
    EAST = "Ost"
    WEST = "West"
    NORTH = "Nord"
    NORTHEAST = "Nordost"
    NORTHWEST = "Nordwest"
    FLAT = "Flachdach"
    OTHER = "Sonstige"


class RoofType(str, Enum):
    """Roof type options"""
    GABLE = "Satteldach"
    FLAT = "Flachdach"
    HIP = "Walmdach"
    SHED = "Pultdach"
    OTHER = "Sonstige"


class SolarCalculationRequest(BaseModel):
    """Request model for solar system calculation"""
    
    # Customer data
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    
    # Location data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Installation address")
    
    # Roof configuration
    roof_area_m2: Optional[float] = Field(None, gt=0, description="Available roof area in m²")
    roof_orientation: RoofOrientation = Field(RoofOrientation.SOUTH, description="Roof orientation")
    roof_inclination_deg: float = Field(30.0, ge=0, le=90, description="Roof inclination in degrees")
    roof_type: Optional[RoofType] = Field(None, description="Type of roof")
    
    # Module configuration
    selected_module_id: Optional[int] = Field(None, description="Selected PV module product ID")
    module_quantity: int = Field(0, ge=0, description="Number of modules")
    module_capacity_w: Optional[float] = Field(None, gt=0, description="Module capacity in Watts")
    
    # Consumption data
    annual_consumption_kwh_yr: float = Field(0.0, ge=0, description="Annual household consumption in kWh/year")
    consumption_heating_kwh_yr: float = Field(0.0, ge=0, description="Annual heating consumption in kWh/year")
    electricity_price_kwh: float = Field(0.30, gt=0, description="Current electricity price in €/kWh")
    
    # Storage configuration
    include_storage: bool = Field(False, description="Include battery storage")
    selected_storage_id: Optional[int] = Field(None, description="Selected storage product ID")
    selected_storage_capacity_kwh: float = Field(0.0, ge=0, description="Storage capacity in kWh")
    
    # Economic parameters
    simulation_period_years: Optional[int] = Field(None, ge=1, le=50, description="Simulation period in years")
    electricity_price_increase_annual_percent: Optional[float] = Field(None, ge=0, le=20, description="Annual electricity price increase in %")
    
    # Additional options
    use_pvgis: bool = Field(True, description="Use PVGIS for yield calculation")
    global_yield_adjustment_percent: float = Field(0.0, ge=-50, le=50, description="Global yield adjustment in %")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "customer_name": "Max Mustermann",
                "latitude": 48.1351,
                "longitude": 11.5820,
                "roof_area_m2": 50.0,
                "roof_orientation": "Süd",
                "roof_inclination_deg": 30.0,
                "module_quantity": 20,
                "annual_consumption_kwh_yr": 4000.0,
                "electricity_price_kwh": 0.30,
                "include_storage": False
            }
        }
    
    @validator('latitude', 'longitude', allow_reuse=True)
    def validate_coordinates(cls, v):
        """Validate that coordinates are not default (0,0) if provided"""
        if v is not None and abs(v) < 1e-5:
            # Allow 0,0 but warn that it might be invalid
            pass
        return v


class MonthlyData(BaseModel):
    """Monthly data for production/consumption"""
    january: float = 0.0
    february: float = 0.0
    march: float = 0.0
    april: float = 0.0
    may: float = 0.0
    june: float = 0.0
    july: float = 0.0
    august: float = 0.0
    september: float = 0.0
    october: float = 0.0
    november: float = 0.0
    december: float = 0.0
    
    def to_list(self) -> List[float]:
        """Convert to list of 12 months"""
        return [
            self.january, self.february, self.march, self.april,
            self.may, self.june, self.july, self.august,
            self.september, self.october, self.november, self.december
        ]
    
    @classmethod
    def from_list(cls, values: List[float]) -> 'MonthlyData':
        """Create from list of 12 values"""
        if len(values) != 12:
            raise ValueError("Monthly data must have exactly 12 values")
        return cls(
            january=values[0], february=values[1], march=values[2], april=values[3],
            may=values[4], june=values[5], july=values[6], august=values[7],
            september=values[8], october=values[9], november=values[10], december=values[11]
        )


class SolarSystemSizing(BaseModel):
    """Solar system sizing information"""
    system_size_kwp: float = Field(..., description="System size in kWp")
    module_count: int = Field(..., description="Number of modules")
    module_capacity_w: float = Field(..., description="Individual module capacity in W")
    total_roof_area_required_m2: Optional[float] = Field(None, description="Required roof area in m²")
    specific_yield_kwh_kwp: float = Field(..., description="Specific annual yield in kWh/kWp")


class EnergyProduction(BaseModel):
    """Energy production data"""
    annual_production_kwh: float = Field(..., description="Annual PV production in kWh")
    monthly_production_kwh: MonthlyData = Field(..., description="Monthly production breakdown")
    pvgis_data_used: bool = Field(..., description="Whether PVGIS data was used")
    pvgis_source: str = Field(..., description="Data source (PVGIS or Manual)")


class SelfConsumption(BaseModel):
    """Self-consumption analysis"""
    annual_self_consumption_kwh: float = Field(..., description="Annual self-consumption in kWh")
    self_consumption_rate_percent: float = Field(..., description="Self-consumption rate in %")
    autarky_degree_percent: float = Field(..., description="Autarky degree in %")
    annual_grid_feed_in_kwh: float = Field(..., description="Annual grid feed-in in kWh")
    annual_grid_purchase_kwh: float = Field(..., description="Annual grid purchase in kWh")
    monthly_self_consumption_kwh: Optional[MonthlyData] = Field(None, description="Monthly self-consumption")


class EconomicAnalysis(BaseModel):
    """Economic analysis results"""
    total_investment_cost_net: float = Field(..., description="Total investment cost (net) in €")
    total_investment_cost_gross: float = Field(..., description="Total investment cost (gross) in €")
    annual_savings_year1: float = Field(..., description="Annual savings in year 1 in €")
    payback_period_years: float = Field(..., description="Payback period in years")
    total_savings_20years: float = Field(..., description="Total savings over 20 years in €")
    total_savings_25years: float = Field(..., description="Total savings over 25 years in €")
    net_present_value: Optional[float] = Field(None, description="Net present value in €")
    internal_rate_of_return_percent: Optional[float] = Field(None, description="Internal rate of return in %")
    annual_feed_in_revenue: float = Field(..., description="Annual feed-in revenue in €")


class EnvironmentalImpact(BaseModel):
    """Environmental impact analysis"""
    annual_co2_savings_kg: float = Field(..., description="Annual CO2 savings in kg")
    total_co2_savings_25years_kg: float = Field(..., description="Total CO2 savings over 25 years in kg")
    equivalent_trees: int = Field(..., description="Equivalent number of trees")
    equivalent_car_km: float = Field(..., description="Equivalent car kilometers")
    co2_payback_time_years: Optional[float] = Field(None, description="CO2 payback time in years")


class StorageAnalysis(BaseModel):
    """Battery storage analysis (if included)"""
    storage_capacity_kwh: float = Field(..., description="Storage capacity in kWh")
    storage_efficiency_percent: float = Field(..., description="Storage efficiency in %")
    annual_storage_cycles: int = Field(..., description="Annual storage cycles")
    additional_self_consumption_kwh: float = Field(..., description="Additional self-consumption from storage in kWh")
    storage_contribution_to_autarky_percent: float = Field(..., description="Storage contribution to autarky in %")


class SolarCalculationResponse(BaseModel):
    """Response model for solar system calculation"""
    
    # Calculation metadata
    calculation_id: Optional[str] = Field(None, description="Unique calculation ID")
    calculation_timestamp: datetime = Field(default_factory=datetime.now, description="Calculation timestamp")
    calculation_duration_ms: Optional[float] = Field(None, description="Calculation duration in milliseconds")
    
    # System sizing
    system_sizing: SolarSystemSizing = Field(..., description="System sizing information")
    
    # Energy production
    energy_production: EnergyProduction = Field(..., description="Energy production data")
    
    # Self-consumption
    self_consumption: SelfConsumption = Field(..., description="Self-consumption analysis")
    
    # Economic analysis
    economic_analysis: EconomicAnalysis = Field(..., description="Economic analysis")
    
    # Environmental impact
    environmental_impact: EnvironmentalImpact = Field(..., description="Environmental impact")
    
    # Storage analysis (optional)
    storage_analysis: Optional[StorageAnalysis] = Field(None, description="Battery storage analysis")
    
    # Warnings and errors
    warnings: List[str] = Field(default_factory=list, description="Calculation warnings")
    errors: List[str] = Field(default_factory=list, description="Calculation errors")
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "calculation_timestamp": "2024-01-15T10:30:00",
                "system_sizing": {
                    "system_size_kwp": 10.5,
                    "module_count": 30,
                    "module_capacity_w": 350,
                    "specific_yield_kwh_kwp": 1000
                },
                "energy_production": {
                    "annual_production_kwh": 10500,
                    "pvgis_data_used": True,
                    "pvgis_source": "PVGIS"
                },
                "economic_analysis": {
                    "total_investment_cost_net": 15000,
                    "total_investment_cost_gross": 17850,
                    "annual_savings_year1": 1200,
                    "payback_period_years": 12.5,
                    "total_savings_20years": 28000
                }
            }
        }


class SolarProjectCreate(BaseModel):
    """Model for creating a new solar project"""
    project_name: str = Field(..., min_length=1, max_length=200, description="Project name")
    calculation_request: SolarCalculationRequest = Field(..., description="Calculation parameters")
    notes: Optional[str] = Field(None, description="Project notes")


class SolarProjectResponse(BaseModel):
    """Response model for solar project"""
    project_id: int = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    calculation_request: SolarCalculationRequest = Field(..., description="Calculation parameters")
    calculation_result: Optional[SolarCalculationResponse] = Field(None, description="Calculation results")
    notes: Optional[str] = Field(None, description="Project notes")
    status: str = Field("draft", description="Project status")


class SolarProjectUpdate(BaseModel):
    """Model for updating a solar project"""
    project_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Project name")
    calculation_request: Optional[SolarCalculationRequest] = Field(None, description="Updated calculation parameters")
    notes: Optional[str] = Field(None, description="Updated notes")
    status: Optional[str] = Field(None, description="Updated status")


class SolarProjectList(BaseModel):
    """List of solar projects"""
    projects: List[SolarProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")
