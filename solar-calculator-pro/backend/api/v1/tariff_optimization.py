"""
API endpoints for dynamic tariff optimization
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ...models.tariff_schemas import (
    OptimizationRequest, OptimizationResult, TariffStructure,
    TariffComparison, DemandResponseEvent, RealTimeTariffData,
    HeatingSchedule
)
from ...services.tariff_optimization_service import TariffOptimizationService

router = APIRouter(prefix="/tariff-optimization", tags=["Tariff Optimization"])


def get_tariff_service() -> TariffOptimizationService:
    """Dependency to get tariff optimization service"""
    return TariffOptimizationService()


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_heating_schedule(
    request: OptimizationRequest,
    service: TariffOptimizationService = Depends(get_tariff_service)
):
    """
    Optimize heating schedule based on dynamic tariff structure
    
    This endpoint analyzes the provided tariff structure and heating requirements
    to generate an optimized schedule that minimizes costs while maintaining comfort.
    
    **Features:**
    - Time-of-use tariff optimization
    - Load shifting to cheaper periods
    - Comfort vs. cost balancing
    - Peak load reduction
    
    **Returns:**
    - Optimized heating schedule
    - Cost savings analysis
    - Comfort score
    - Peak load reduction
    """
    try:
        result = service.optimize_schedule(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/compare-tariffs", response_model=List[TariffComparison])
async def compare_tariff_options(
    tariffs: List[TariffStructure],
    annual_heating_demand: float,
    heat_pump_cop: float = 3.0,
    service: TariffOptimizationService = Depends(get_tariff_service)
):
    """
    Compare different tariff options for heat pump operation
    
    Analyzes multiple tariff structures to determine which offers the best
    value for your specific heating profile.
    
    **Parameters:**
    - tariffs: List of tariff structures to compare
    - annual_heating_demand: Annual heating demand in kWh
    - heat_pump_cop: Coefficient of Performance of heat pump
    
    **Returns:**
    - Comparison of all tariffs with costs and recommendations
    - Pros and cons for each tariff
    - Potential savings
    """
    try:
        # Create heating profile
        heating_profile = {
            hour: annual_heating_demand / (24 * 365)
            for hour in range(24)
        }
        
        comparisons = service.compare_tariffs(tariffs, heating_profile)
        return comparisons
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/demand-response/evaluate")
async def evaluate_demand_response_event(
    event: DemandResponseEvent,
    current_schedule: List[HeatingSchedule],
    service: TariffOptimizationService = Depends(get_tariff_service)
):
    """
    Evaluate participation in demand response event
    
    Analyzes a demand response event to determine if participation is beneficial
    and provides an adjusted heating schedule.
    
    **Features:**
    - Participation feasibility analysis
    - Incentive earnings calculation
    - Adjusted schedule generation
    - Comfort impact assessment
    
    **Returns:**
    - Participation recommendation
    - Adjusted heating schedule
    - Incentive earnings
    - Load reduction details
    """
    try:
        result = service.process_demand_response(event, current_schedule)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/real-time/monitor")
async def monitor_real_time_tariff(
    tariff_data: RealTimeTariffData,
    current_schedule: List[HeatingSchedule],
    service: TariffOptimizationService = Depends(get_tariff_service)
):
    """
    Monitor real-time tariff rates and provide recommendations
    
    Analyzes current and forecasted tariff rates to provide real-time
    recommendations for heat pump operation.
    
    **Features:**
    - Real-time rate monitoring
    - 24-hour forecast analysis
    - Optimal timing recommendations
    - Grid load awareness
    
    **Returns:**
    - Current rate analysis
    - Action recommendations
    - Optimal heating hours
    - Savings opportunities
    """
    try:
        result = service.monitor_real_time_tariff(tariff_data, current_schedule)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


@router.get("/tariff-types")
async def get_tariff_types():
    """
    Get available tariff types and their descriptions
    
    Returns information about different tariff types supported by the system.
    """
    return {
        "tariff_types": [
            {
                "type": "flat_rate",
                "name": "Flat Rate",
                "description": "Single rate for all hours",
                "best_for": "Simple, predictable billing"
            },
            {
                "type": "time_of_use",
                "name": "Time of Use",
                "description": "Different rates for peak and off-peak periods",
                "best_for": "Flexible heating schedules"
            },
            {
                "type": "dynamic",
                "name": "Dynamic Pricing",
                "description": "Rates vary based on market conditions",
                "best_for": "Maximum savings with active management"
            },
            {
                "type": "real_time",
                "name": "Real-Time Pricing",
                "description": "Rates change hourly based on grid conditions",
                "best_for": "Smart home integration"
            }
        ]
    }


@router.post("/smart-schedule/generate")
async def generate_smart_schedule(
    annual_heating_demand: float,
    heat_pump_cop: float,
    tariff_structure: TariffStructure,
    comfort_priority: float = 0.7,
    service: TariffOptimizationService = Depends(get_tariff_service)
):
    """
    Generate a smart heating schedule from scratch
    
    Creates an optimized heating schedule based on typical heating patterns
    and the provided tariff structure.
    
    **Parameters:**
    - annual_heating_demand: Annual heating demand in kWh
    - heat_pump_cop: Coefficient of Performance
    - tariff_structure: Tariff structure to optimize for
    - comfort_priority: Priority between cost (0) and comfort (1)
    
    **Returns:**
    - Complete 24-hour heating schedule
    - Cost analysis
    - Optimization recommendations
    """
    try:
        # Generate typical heating schedule
        typical_schedule = [
            HeatingSchedule(hour=h, target_temperature=20.0 if 6 <= h <= 22 else 18.0, flexible=True)
            for h in range(24)
        ]
        
        # Create optimization request
        request = OptimizationRequest(
            tariff_structure=tariff_structure,
            heat_pump_cop=heat_pump_cop,
            annual_heating_demand=annual_heating_demand,
            current_schedule=typical_schedule,
            comfort_priority=comfort_priority
        )
        
        # Optimize
        result = service.optimize_schedule(request)
        
        return {
            "schedule": result.optimized_schedule,
            "annual_cost": result.optimized_cost,
            "savings_vs_baseline": result.savings,
            "comfort_score": result.comfort_score,
            "recommendations": [
                "Schedule optimized for your tariff structure",
                f"Potential annual savings: {result.savings:.2f} EUR",
                f"Comfort score: {result.comfort_score * 100:.1f}%"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule generation failed: {str(e)}")
