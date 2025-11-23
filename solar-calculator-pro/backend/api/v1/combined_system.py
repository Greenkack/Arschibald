"""
API endpoints for combined Heat Pump + PV system integration.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ...models.combined_system_schemas import (
    CombinedSystemRequest,
    CombinedSystemResponse,
    SystemMonitoringData,
    OptimizationRequest,
    OptimizationResponse
)
from ...services.combined_system_service import CombinedSystemService

router = APIRouter(prefix="/combined-system", tags=["Combined System"])


def get_combined_system_service() -> CombinedSystemService:
    """Dependency to get combined system service instance"""
    return CombinedSystemService()


@router.post("/analyze", response_model=CombinedSystemResponse)
async def analyze_combined_system(
    request: CombinedSystemRequest,
    service: CombinedSystemService = Depends(get_combined_system_service)
):
    """
    Analyze combined heat pump + PV system.
    
    Performs comprehensive analysis including:
    - System optimization
    - Self-consumption maximization
    - Synergy calculations
    - Smart control strategies
    - Combined financial analysis
    - Environmental impact
    
    Returns complete analysis with recommendations.
    """
    try:
        return service.analyze_combined_system(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_system_operation(
    request: OptimizationRequest,
    service: CombinedSystemService = Depends(get_combined_system_service)
):
    """
    Optimize system operation for given time horizon.
    
    Uses predictive control to:
    - Minimize energy costs
    - Maximize self-consumption
    - Optimize comfort levels
    
    Returns optimized control schedule.
    """
    try:
        return service.optimize_system(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/monitoring/{system_id}", response_model=SystemMonitoringData)
async def get_system_monitoring(
    system_id: int,
    service: CombinedSystemService = Depends(get_combined_system_service)
):
    """
    Get real-time monitoring data for combined system.
    
    Returns current status and performance metrics for:
    - PV system
    - Heat pump
    - Battery storage
    - Grid interaction
    - Performance metrics
    """
    try:
        return service.get_monitoring_data(system_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"System not found: {str(e)}")
