"""
Grid Integration API Endpoints
RESTful API for solar grid integration calculations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from ...models.grid_schemas import (
    FeedInTariffRequest, FeedInTariffResponse,
    NetMeteringRequest, NetMeteringResponse,
    GridConnectionRequest, GridConnectionResponse,
    PowerQualityRequest, PowerQualityResponse,
    GridStabilityRequest, GridStabilityResponse,
    SmartGridRequest, SmartGridResponse,
    GridIntegrationAnalysisRequest, GridIntegrationAnalysisResponse
)
from ...services.grid_integration_service import GridIntegrationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/grid", tags=["Grid Integration"])


def get_grid_service() -> GridIntegrationService:
    """Dependency to get grid integration service"""
    return GridIntegrationService()


@router.post("/feed-in-tariff", response_model=FeedInTariffResponse)
async def calculate_feed_in_tariff(
    request: FeedInTariffRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Calculate feed-in tariff benefits over system lifetime
    
    This endpoint calculates the financial benefits of feed-in tariffs,
    including annual and lifetime revenue from excess energy fed into the grid.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - annual_production_kwh: Expected annual production
    - self_consumption_rate: Percentage of energy consumed on-site (0-1)
    - feed_in_tariff_per_kwh: Feed-in tariff rate in €/kWh
    - electricity_price_per_kwh: Retail electricity price in €/kWh
    - contract_duration_years: Feed-in tariff contract duration
    - degradation_rate: Annual system degradation rate
    
    **Returns:**
    - Detailed financial analysis including annual and lifetime benefits
    - Payback period calculation
    - Average benefit per kWp
    """
    try:
        logger.info(f"Feed-in tariff calculation requested for {request.system_size_kwp} kWp")
        result = service.calculate_feed_in_tariff(request)
        return result
    except Exception as e:
        logger.error(f"Feed-in tariff calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/net-metering", response_model=NetMeteringResponse)
async def analyze_net_metering(
    request: NetMeteringRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Analyze net metering benefits and monthly credit flow
    
    This endpoint performs detailed net metering analysis including monthly
    credit accumulation, rollover, and grid independence calculations.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - annual_production_kwh: Expected annual production
    - annual_consumption_kwh: Annual energy consumption
    - electricity_price_per_kwh: Retail electricity price
    - net_metering_credit_per_kwh: Credit value per kWh
    - monthly_production: Array of 12 monthly production values
    - monthly_consumption: Array of 12 monthly consumption values
    - rollover_allowed: Whether credits can roll over
    - max_rollover_months: Maximum rollover period
    
    **Returns:**
    - Monthly analysis with credit flow
    - Annual net savings
    - Self-sufficiency and grid independence rates
    - Optimal system size recommendation
    """
    try:
        logger.info(f"Net metering analysis requested for {request.system_size_kwp} kWp")
        result = service.analyze_net_metering(request)
        return result
    except Exception as e:
        logger.error(f"Net metering analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connection-requirements", response_model=GridConnectionResponse)
async def calculate_connection_requirements(
    request: GridConnectionRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Calculate grid connection requirements and costs
    
    This endpoint determines the technical requirements and estimated costs
    for connecting a solar system to the grid.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - connection_type: Single-phase, three-phase, or micro-grid
    - voltage_level: Grid voltage in V
    - distance_to_grid_m: Distance to connection point
    - inverter_power_kw: Inverter rated power
    - location: Installation location
    - building_type: Residential, commercial, or industrial
    
    **Returns:**
    - Required cable size and specifications
    - Estimated connection cost
    - Voltage drop calculation
    - Required protection devices
    - Grid capacity assessment
    - Approval timeline estimate
    """
    try:
        logger.info(f"Connection requirements requested for {request.system_size_kwp} kWp")
        result = service.calculate_grid_connection_requirements(request)
        return result
    except Exception as e:
        logger.error(f"Connection requirements calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/power-quality", response_model=PowerQualityResponse)
async def analyze_power_quality(
    request: PowerQualityRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Analyze power quality compliance
    
    This endpoint checks compliance with power quality standards including
    voltage regulation, harmonics, power factor, and other quality metrics.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - inverter_specs: Inverter specifications dictionary
    - grid_voltage: Grid voltage level
    - grid_frequency: Grid frequency (default 50 Hz)
    - standard: Power quality standard to check against
    - harmonic_limits: Optional custom harmonic limits
    
    **Returns:**
    - Compliance status
    - Voltage and frequency regulation
    - Power factor
    - Total harmonic distortion (THD)
    - Individual harmonic analysis
    - Flicker severity
    - DC injection level
    - Compliance issues and recommendations
    """
    try:
        logger.info(f"Power quality analysis requested for {request.system_size_kwp} kWp")
        result = service.analyze_power_quality(request)
        return result
    except Exception as e:
        logger.error(f"Power quality analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grid-stability", response_model=GridStabilityResponse)
async def calculate_grid_stability(
    request: GridStabilityRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Calculate grid stability metrics
    
    This endpoint analyzes the impact of the solar system on grid stability
    and determines available grid support services.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - grid_short_circuit_power_mva: Grid short circuit power
    - grid_impedance_ohm: Grid impedance
    - inverter_response_time_ms: Inverter response time
    - enable_reactive_power_support: Enable Q/V control
    - enable_voltage_regulation: Enable voltage regulation
    
    **Returns:**
    - Overall stability index (0-1)
    - Short circuit ratio
    - Voltage and frequency stability margins
    - Reactive power capability
    - Available grid support services
    - Stability concerns
    - Recommended inverter settings
    """
    try:
        logger.info(f"Grid stability analysis requested for {request.system_size_kwp} kWp")
        result = service.calculate_grid_stability(request)
        return result
    except Exception as e:
        logger.error(f"Grid stability calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-grid", response_model=SmartGridResponse)
async def analyze_smart_grid_integration(
    request: SmartGridRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Analyze smart grid integration potential
    
    This endpoint evaluates the potential for smart grid services and
    calculates potential revenue streams from grid services.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - battery_capacity_kwh: Optional battery storage capacity
    - enable_demand_response: Enable demand response capability
    - enable_frequency_regulation: Enable frequency regulation
    - enable_voltage_support: Enable voltage support
    - time_of_use_tariff: Optional TOU tariff structure
    
    **Returns:**
    - Smart grid readiness assessment
    - Available grid services
    - Potential revenue streams
    - Annual grid services revenue
    - Demand response capacity
    - Frequency regulation capability
    - Recommended upgrades
    - Integration cost and payback period
    """
    try:
        logger.info(f"Smart grid analysis requested for {request.system_size_kwp} kWp")
        result = service.analyze_smart_grid_integration(request)
        return result
    except Exception as e:
        logger.error(f"Smart grid analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comprehensive-analysis", response_model=GridIntegrationAnalysisResponse)
async def comprehensive_grid_analysis(
    request: GridIntegrationAnalysisRequest,
    service: GridIntegrationService = Depends(get_grid_service)
):
    """
    Perform comprehensive grid integration analysis
    
    This endpoint performs a complete analysis of all grid integration aspects
    including financial benefits, technical requirements, power quality,
    stability, and smart grid potential.
    
    **Parameters:**
    - system_size_kwp: System size in kWp
    - annual_production_kwh: Expected annual production
    - annual_consumption_kwh: Annual energy consumption
    - location: Installation location
    - connection_type: Grid connection type
    - metering_type: Metering system type
    - feed_in_tariff_per_kwh: Feed-in tariff rate
    - electricity_price_per_kwh: Retail electricity price
    - grid_voltage: Grid voltage level
    - distance_to_grid_m: Distance to connection point
    - battery_capacity_kwh: Optional battery capacity
    - enable_smart_grid: Enable smart grid analysis
    
    **Returns:**
    - Complete analysis including:
      - Feed-in tariff analysis
      - Net metering analysis (if applicable)
      - Connection requirements
      - Power quality assessment
      - Grid stability analysis
      - Smart grid potential (if enabled)
    - Total annual and lifetime benefits
    - Recommended configuration
    - Compliance status
    - Overall feasibility score (0-100)
    """
    try:
        logger.info(f"Comprehensive grid analysis requested for {request.system_size_kwp} kWp")
        result = service.comprehensive_grid_analysis(request)
        return result
    except Exception as e:
        logger.error(f"Comprehensive grid analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for grid integration service"""
    return {
        "status": "healthy",
        "service": "grid_integration",
        "version": "1.0.0"
    }
