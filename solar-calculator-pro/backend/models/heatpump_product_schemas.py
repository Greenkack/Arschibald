"""
Heat Pump Product Data Models and Schemas

This module defines Pydantic models for heat pump product data,
including specifications, filtering, comparison, and recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class HeatPumpType(str, Enum):
    """Heat pump types"""
    AIR_WATER = "Luft-Wasser-Wärmepumpe"
    WATER_WATER = "Wasser-Wasser-Wärmepumpe"
    BRINE_WATER = "Sole-Wasser-Wärmepumpe"
    AIR_AIR = "Luft-Luft-Wärmepumpe"
    HYBRID = "Hybrid-Wärmepumpe"


class RefrigerantType(str, Enum):
    """Refrigerant types"""
    R32 = "R32"
    R290 = "R290"
    R410A = "R410A"
    R407C = "R407C"
    R134A = "R134A"


class InstallationType(str, Enum):
    """Installation types"""
    INDOOR = "Innenaufstellung"
    OUTDOOR = "Außenaufstellung"
    SPLIT = "Split-Gerät"
    MONOBLOCK = "Monoblock"


class HeatPumpSpecification(BaseModel):
    """Heat pump technical specifications"""
    model: str = Field(..., description="Model name")
    manufacturer: str = Field(..., description="Manufacturer name")
    heatpump_type: HeatPumpType = Field(..., description="Type of heat pump")
    
    # Power specifications
    heating_power_kw: List[float] = Field(..., description="Heating power options in kW")
    cooling_power_kw: Optional[List[float]] = Field(None, description="Cooling power options in kW")
    
    # Efficiency ratings
    cop: Optional[float] = Field(None, description="Coefficient of Performance")
    scop: Optional[float] = Field(None, description="Seasonal Coefficient of Performance")
    eer: Optional[float] = Field(None, description="Energy Efficiency Ratio")
    seer: Optional[float] = Field(None, description="Seasonal Energy Efficiency Ratio")
    
    # Temperature ranges
    min_operating_temp: Optional[float] = Field(None, description="Minimum operating temperature in °C")
    max_operating_temp: Optional[float] = Field(None, description="Maximum operating temperature in °C")
    max_flow_temp: Optional[float] = Field(None, description="Maximum flow temperature in °C")
    
    # Physical specifications
    refrigerant: Optional[RefrigerantType] = Field(None, description="Refrigerant type")
    installation_type: Optional[InstallationType] = Field(None, description="Installation type")
    noise_level_db: Optional[float] = Field(None, description="Noise level in dB(A)")
    weight_kg: Optional[float] = Field(None, description="Weight in kg")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Dimensions (width, height, depth) in mm")
    
    # Features
    smart_grid_ready: bool = Field(False, description="Smart grid ready")
    internet_connectivity: bool = Field(False, description="Internet connectivity")
    modulating: bool = Field(False, description="Modulating operation")
    inverter_technology: bool = Field(False, description="Inverter technology")
    
    # Pricing
    base_price: Optional[float] = Field(None, description="Base price in EUR")
    installation_cost: Optional[float] = Field(None, description="Estimated installation cost in EUR")
    
    # Availability
    available: bool = Field(True, description="Product availability")
    lead_time_days: Optional[int] = Field(None, description="Lead time in days")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    
    # Additional data
    datasheet_url: Optional[str] = Field(None, description="URL to product datasheet")
    image_url: Optional[str] = Field(None, description="URL to product image")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('heating_power_kw')
    def validate_heating_power(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one heating power value required")
        if any(p <= 0 for p in v):
            raise ValueError("Heating power must be positive")
        return sorted(v)
    
    @validator('cop', 'scop', 'eer', 'seer')
    def validate_efficiency(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Efficiency rating must be positive")
        return v


class HeatPumpFilterRequest(BaseModel):
    """Request model for filtering heat pumps"""
    manufacturers: Optional[List[str]] = Field(None, description="Filter by manufacturers")
    heatpump_types: Optional[List[HeatPumpType]] = Field(None, description="Filter by heat pump types")
    
    # Power range
    min_heating_power: Optional[float] = Field(None, description="Minimum heating power in kW")
    max_heating_power: Optional[float] = Field(None, description="Maximum heating power in kW")
    
    # Efficiency range
    min_cop: Optional[float] = Field(None, description="Minimum COP")
    min_scop: Optional[float] = Field(None, description="Minimum SCOP")
    
    # Temperature requirements
    min_operating_temp_required: Optional[float] = Field(None, description="Required minimum operating temperature")
    max_flow_temp_required: Optional[float] = Field(None, description="Required maximum flow temperature")
    
    # Features
    smart_grid_required: Optional[bool] = Field(None, description="Require smart grid capability")
    internet_required: Optional[bool] = Field(None, description="Require internet connectivity")
    inverter_required: Optional[bool] = Field(None, description="Require inverter technology")
    
    # Price range
    max_price: Optional[float] = Field(None, description="Maximum price in EUR")
    
    # Availability
    available_only: bool = Field(True, description="Show only available products")
    max_lead_time_days: Optional[int] = Field(None, description="Maximum acceptable lead time")
    
    # Sorting
    sort_by: Optional[str] = Field("scop", description="Sort field (scop, cop, price, power)")
    sort_order: str = Field("desc", description="Sort order (asc, desc)")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class HeatPumpComparisonRequest(BaseModel):
    """Request model for comparing heat pumps"""
    product_ids: List[str] = Field(..., min_items=2, max_items=5, description="Product IDs to compare")
    comparison_criteria: Optional[List[str]] = Field(
        None,
        description="Specific criteria to compare (efficiency, cost, features, etc.)"
    )


class HeatPumpRecommendationRequest(BaseModel):
    """Request model for heat pump recommendations"""
    # Building specifications
    building_area_sqm: float = Field(..., gt=0, description="Building area in square meters")
    building_insulation: str = Field(..., description="Insulation quality (poor, average, good, excellent)")
    building_age: Optional[int] = Field(None, description="Building age in years")
    
    # Heating requirements
    desired_indoor_temp: float = Field(20.0, description="Desired indoor temperature in °C")
    climate_zone: str = Field(..., description="Climate zone or location")
    lowest_outdoor_temp: float = Field(..., description="Lowest expected outdoor temperature in °C")
    
    # System requirements
    existing_heating_system: Optional[str] = Field(None, description="Existing heating system type")
    radiator_type: Optional[str] = Field(None, description="Radiator type (high-temp, low-temp, underfloor)")
    hot_water_required: bool = Field(True, description="Hot water heating required")
    cooling_required: bool = Field(False, description="Cooling functionality required")
    
    # Budget and preferences
    max_budget: Optional[float] = Field(None, description="Maximum budget in EUR")
    prefer_quiet: bool = Field(False, description="Prefer quieter models")
    prefer_smart_features: bool = Field(False, description="Prefer smart grid and connectivity")
    
    # Energy goals
    target_cop: Optional[float] = Field(None, description="Target COP value")
    target_scop: Optional[float] = Field(None, description="Target SCOP value")


class HeatPumpRecommendation(BaseModel):
    """Heat pump recommendation result"""
    product: HeatPumpSpecification
    suitability_score: float = Field(..., ge=0, le=100, description="Suitability score (0-100)")
    recommendation_reasons: List[str] = Field(..., description="Reasons for recommendation")
    estimated_annual_cost: Optional[float] = Field(None, description="Estimated annual operating cost")
    estimated_savings: Optional[float] = Field(None, description="Estimated annual savings vs. existing system")
    payback_period_years: Optional[float] = Field(None, description="Estimated payback period")
    environmental_impact: Optional[Dict[str, Any]] = Field(None, description="Environmental impact metrics")


class HeatPumpFilterResponse(BaseModel):
    """Response model for filtered heat pumps"""
    products: List[HeatPumpSpecification]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: Dict[str, Any]


class HeatPumpComparisonResponse(BaseModel):
    """Response model for heat pump comparison"""
    products: List[HeatPumpSpecification]
    comparison_matrix: Dict[str, Dict[str, Any]]
    best_in_category: Dict[str, str]
    summary: Dict[str, Any]


class HeatPumpRecommendationResponse(BaseModel):
    """Response model for heat pump recommendations"""
    recommendations: List[HeatPumpRecommendation]
    building_analysis: Dict[str, Any]
    estimated_heat_load_kw: float
    recommended_power_range: Dict[str, float]


class HeatPumpAvailability(BaseModel):
    """Heat pump availability information"""
    product_id: str
    manufacturer: str
    model: str
    available: bool
    stock_level: Optional[str] = Field(None, description="Stock level (in_stock, low_stock, out_of_stock)")
    lead_time_days: Optional[int] = Field(None, description="Lead time in days")
    next_delivery_date: Optional[datetime] = Field(None, description="Next expected delivery date")
    alternative_models: Optional[List[str]] = Field(None, description="Alternative model suggestions")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class HeatPumpAvailabilityUpdate(BaseModel):
    """Update heat pump availability"""
    product_id: str
    available: bool
    stock_level: Optional[str] = None
    lead_time_days: Optional[int] = None
    next_delivery_date: Optional[datetime] = None


class HeatPumpBulkAvailabilityRequest(BaseModel):
    """Request for bulk availability check"""
    product_ids: List[str] = Field(..., min_items=1, description="Product IDs to check")


class HeatPumpBulkAvailabilityResponse(BaseModel):
    """Response for bulk availability check"""
    availability: List[HeatPumpAvailability]
    summary: Dict[str, int]  # available_count, unavailable_count, etc.
