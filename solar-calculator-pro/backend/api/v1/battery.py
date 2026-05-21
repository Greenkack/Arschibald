"""
Battery Storage API Endpoints

Provides REST API for battery storage calculations, ROI analysis,
discharge strategies, grid independence, lifecycle analysis, and monitoring integration.

Requirements: 1.3, 6.1
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from models.battery_schemas import (
    BatterySizingRequest,
    BatterySizingResponse,
    BatteryROIRequest,
    BatteryROIResponse,
    DischargeStrategyRequest,
    DischargeStrategyResponse,
    GridIndependenceRequest,
    GridIndependenceResponse,
    LifecycleAnalysisRequest,
    LifecycleAnalysisResponse,
    MonitoringIntegrationRequest,
    MonitoringIntegrationResponse
)
from services.battery_storage_service import (
    BatteryStorageService,
    BatterySpecs,
    DischargeStrategy
)

router = APIRouter(prefix="/battery", tags=["battery"])
battery_service = BatteryStorageService()


@router.post("/sizing", response_model=BatterySizingResponse)
async def calculate_battery_sizing(request: BatterySizingRequest):
    """
    Calculate optimal battery size based on consumption and production patterns
    
    Returns recommended battery size, expected performance, and cost analysis.
    """
    try:
        result = battery_service.calculate_battery_sizing(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Battery sizing calculation failed: {str(e)}"
        )


@router.post("/roi", response_model=BatteryROIResponse)
async def calculate_battery_roi(request: BatteryROIRequest):
    """
    Calculate comprehensive ROI analysis for battery storage
    
    Includes payback period, NPV, IRR, and lifetime savings.
    """
    try:
        # Get battery specs based on capacity
        battery_category = battery_service._select_battery_category(request.battery_capacity_kwh)
        battery_specs = battery_service.default_battery_specs[battery_category]
        
        # Create sizing request for ROI calculation
        sizing_request = BatterySizingRequest(
            daily_consumption_kwh=request.daily_consumption_kwh,
            pv_system_size_kwp=request.pv_system_size_kwp,
            annual_production_kwh=request.annual_production_kwh,
            self_consumption_rate=request.self_consumption_rate,
            grid_feed_in_tariff=request.grid_feed_in_tariff,
            electricity_price=request.electricity_price
        )
        
        result = battery_service.calculate_battery_roi(
            battery_specs,
            sizing_request,
            request.analysis_years
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Battery ROI calculation failed: {str(e)}"
        )


@router.post("/discharge-strategy", response_model=DischargeStrategyResponse)
async def calculate_discharge_strategy(request: DischargeStrategyRequest):
    """
    Simulate battery discharge strategy over 24-hour period
    
    Returns optimal charge/discharge schedule and performance metrics.
    """
    try:
        # Validate hourly data
        if len(request.hourly_production) != 24 or len(request.hourly_consumption) != 24:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hourly production and consumption must have exactly 24 values"
            )
        
        # Get battery specs
        battery_category = battery_service._select_battery_category(request.battery_capacity_kwh)
        battery_specs = battery_service.default_battery_specs[battery_category]
        
        # Create discharge strategy
        strategy = DischargeStrategy(
            strategy_type=request.strategy_type,
            peak_hours=request.peak_hours,
            min_soc=request.min_soc,
            max_soc=request.max_soc,
            priority=request.priority
        )
        
        result = battery_service.calculate_discharge_strategy(
            strategy,
            battery_specs,
            request.hourly_production,
            request.hourly_consumption
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discharge strategy calculation failed: {str(e)}"
        )


@router.post("/grid-independence", response_model=GridIndependenceResponse)
async def calculate_grid_independence(request: GridIndependenceRequest):
    """
    Calculate grid independence metrics with battery storage
    
    Returns self-sufficiency rate, autarky level, and grid dependency.
    """
    try:
        # Validate monthly data
        if len(request.monthly_production) != 12 or len(request.monthly_consumption) != 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly production and consumption must have exactly 12 values"
            )
        
        # Get battery specs
        battery_category = battery_service._select_battery_category(request.battery_capacity_kwh)
        battery_specs = battery_service.default_battery_specs[battery_category]
        
        # Create sizing request
        sizing_request = BatterySizingRequest(
            daily_consumption_kwh=request.daily_consumption_kwh,
            pv_system_size_kwp=request.pv_system_size_kwp,
            annual_production_kwh=request.annual_production_kwh,
            self_consumption_rate=request.self_consumption_rate,
            grid_feed_in_tariff=0.08,  # Default value
            electricity_price=0.30  # Default value
        )
        
        result = battery_service.calculate_grid_independence(
            battery_specs,
            sizing_request,
            request.monthly_production,
            request.monthly_consumption
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grid independence calculation failed: {str(e)}"
        )


@router.post("/lifecycle", response_model=LifecycleAnalysisResponse)
async def calculate_lifecycle_analysis(request: LifecycleAnalysisRequest):
    """
    Calculate battery lifecycle analysis including degradation and replacement
    
    Returns capacity over time, cycle life, and replacement schedule.
    """
    try:
        # Get battery specs
        battery_category = battery_service._select_battery_category(request.battery_capacity_kwh)
        battery_specs = battery_service.default_battery_specs[battery_category]
        
        result = battery_service.calculate_lifecycle_analysis(
            battery_specs,
            request.daily_cycles,
            request.analysis_years
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lifecycle analysis calculation failed: {str(e)}"
        )


@router.post("/monitoring-integration", response_model=MonitoringIntegrationResponse)
async def get_monitoring_integration_config(request: MonitoringIntegrationRequest):
    """
    Generate monitoring integration configuration
    
    Returns API endpoints, data points, and alert thresholds.
    """
    try:
        # Validate monitoring system
        valid_systems = ['generic', 'tesla_powerwall', 'sonnen_battery', 'lg_resu']
        if request.monitoring_system not in valid_systems:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid monitoring system. Must be one of: {', '.join(valid_systems)}"
            )
        
        # Get battery specs
        battery_category = battery_service._select_battery_category(request.battery_capacity_kwh)
        battery_specs = battery_service.default_battery_specs[battery_category]
        
        result = battery_service.get_monitoring_integration_config(
            battery_specs,
            request.monitoring_system
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring integration configuration failed: {str(e)}"
        )


@router.get("/battery-specs")
async def get_battery_specs() -> Dict[str, Any]:
    """
    Get available battery specifications
    
    Returns all predefined battery specs (small, medium, large).
    """
    try:
        return {
            category: specs.dict()
            for category, specs in battery_service.default_battery_specs.items()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve battery specs: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for battery service"""
    return {
        "status": "healthy",
        "service": "battery_storage",
        "version": "1.0.0"
    }
