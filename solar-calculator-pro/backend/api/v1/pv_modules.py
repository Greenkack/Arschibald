"""
PV Module API Endpoints

Provides REST API for PV module selection and calculations.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ...services.pv_module_service import pv_module_service

router = APIRouter(prefix="/pv-modules", tags=["PV Modules"])


# ==================== Pydantic Models ====================

class PVModuleResponse(BaseModel):
    id: int
    manufacturer: str
    model: str
    power_wp: int
    efficiency: float
    width_mm: int
    height_mm: int
    weight_kg: float
    cell_type: str
    warranty_years: int
    price_net: float
    price_gross: float
    datasheet_url: Optional[str]
    image_url: Optional[str]
    is_active: bool


class SystemPowerRequest(BaseModel):
    module_id: int
    module_count: int


class SystemPowerResponse(BaseModel):
    module: Dict[str, Any]
    module_count: int
    total_power_wp: int
    total_power_kwp: float
    module_area_m2: float
    total_area_m2: float
    total_weight_kg: float
    price_net: float
    price_gross: float
    price_per_kwp_net: float


class RoofRecommendationRequest(BaseModel):
    roof_area_m2: float
    target_kwp: Optional[float] = None


class YieldEstimationRequest(BaseModel):
    module_id: int
    module_count: int
    location_factor: float = 1000
    orientation_factor: float = 1.0


# ==================== Module Endpoints ====================

@router.get("/", response_model=List[PVModuleResponse])
async def list_modules(active_only: bool = Query(True)):
    """Get all PV modules."""
    modules = pv_module_service.get_all_modules(active_only=active_only)
    return [vars(m) for m in modules]


@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers():
    """Get list of all manufacturers."""
    return pv_module_service.get_manufacturers()


@router.get("/by-manufacturer/{manufacturer}", response_model=List[PVModuleResponse])
async def get_modules_by_manufacturer(manufacturer: str):
    """Get modules by manufacturer."""
    modules = pv_module_service.get_modules_by_manufacturer(manufacturer)
    return [vars(m) for m in modules]


@router.get("/{module_id}", response_model=PVModuleResponse)
async def get_module(module_id: int):
    """Get module by ID."""
    module = pv_module_service.get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return vars(module)


# ==================== Calculation Endpoints ====================

@router.post("/calculate-system", response_model=SystemPowerResponse)
async def calculate_system_power(request: SystemPowerRequest):
    """Calculate total system power from module count."""
    try:
        return pv_module_service.calculate_system_power(
            request.module_id, 
            request.module_count
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recommend")
async def recommend_modules(request: RoofRecommendationRequest):
    """Recommend modules based on roof size."""
    return pv_module_service.recommend_modules_for_roof(
        request.roof_area_m2,
        request.target_kwp
    )


@router.get("/compare")
async def compare_modules(module_ids: str = Query(..., description="Comma-separated module IDs")):
    """Compare multiple modules."""
    ids = [int(id.strip()) for id in module_ids.split(",")]
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 modules required for comparison")
    if len(ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 modules for comparison")
    return pv_module_service.compare_modules(ids)


@router.post("/estimate-yield")
async def estimate_yield(request: YieldEstimationRequest):
    """Estimate annual energy yield."""
    try:
        return pv_module_service.estimate_annual_yield(
            request.module_id,
            request.module_count,
            request.location_factor,
            request.orientation_factor
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Health Check ====================

@router.get("/health/check")
async def health_check():
    """Check PV module service health."""
    return pv_module_service.health_check()
