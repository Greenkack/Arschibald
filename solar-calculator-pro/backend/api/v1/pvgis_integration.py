"""
PVGIS API Integration
Task 253: PVGIS API connection for yield calculation
- PVGIS API connection
- Fallback to static yield factors
- Location-based yield optimization
- Roof angle and orientation correction
- Yield comparison (PVGIS vs. static)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
import httpx
import asyncio
from enum import Enum


router = APIRouter(prefix="/pvgis", tags=["PVGIS Integration"])


# PVGIS API Configuration
PVGIS_BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2"
PVGIS_TIMEOUT = 30  # seconds


class RoofOrientation(str, Enum):
    NORTH = "north"
    NORTHEAST = "northeast"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"


class PVGISRequest(BaseModel):
    """PVGIS API request parameters"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    peak_power_kwp: float = Field(..., gt=0, description="Peak power in kWp")
    roof_tilt: float = Field(30, ge=0, le=90, description="Roof tilt angle in degrees")
    roof_orientation: RoofOrientation = Field(RoofOrientation.SOUTH, description="Roof orientation")
    system_loss: float = Field(14, ge=0, le=100, description="System losses in %")
    mounting_type: str = Field("building", description="Mounting type: building, free")
    use_horizon: bool = Field(True, description="Use horizon data")


class PVGISResponse(BaseModel):
    """PVGIS API response"""
    annual_yield_kwh: float
    monthly_yields_kwh: List[float]
    specific_yield_kwh_kwp: float
    optimal_tilt: float
    optimal_azimuth: float
    data_source: str
    location: Dict[str, float]
    system_info: Dict[str, Any]


class StaticYieldFactors(BaseModel):
    """Static yield factors for fallback"""
    latitude: float
    base_yield_kwh_kwp: float
    tilt_correction: float
    orientation_correction: float
    final_yield_kwh_kwp: float


class YieldComparison(BaseModel):
    """Comparison between PVGIS and static yield"""
    pvgis_yield_kwh: Optional[float]
    static_yield_kwh: float
    difference_kwh: Optional[float]
    difference_percent: Optional[float]
    recommended_source: str
    notes: str


# Static yield factors by latitude (Germany-focused)
STATIC_YIELD_FACTORS = {
    # Latitude range: base yield in kWh/kWp
    (47, 48): 1050,  # Southern Germany
    (48, 49): 1020,
    (49, 50): 1000,
    (50, 51): 980,
    (51, 52): 960,
    (52, 53): 940,
    (53, 54): 920,
    (54, 55): 900,  # Northern Germany
    (55, 56): 880,
}

# Orientation correction factors
ORIENTATION_FACTORS = {
    RoofOrientation.SOUTH: 1.0,
    RoofOrientation.SOUTHEAST: 0.95,
    RoofOrientation.SOUTHWEST: 0.95,
    RoofOrientation.EAST: 0.85,
    RoofOrientation.WEST: 0.85,
    RoofOrientation.NORTHEAST: 0.75,
    RoofOrientation.NORTHWEST: 0.75,
    RoofOrientation.NORTH: 0.60,
}

# Tilt correction factors (optimal is ~30-35° for Germany)
def get_tilt_correction(tilt: float) -> float:
    """Get tilt correction factor"""
    optimal_tilt = 32
    deviation = abs(tilt - optimal_tilt)
    
    if deviation <= 5:
        return 1.0
    elif deviation <= 10:
        return 0.98
    elif deviation <= 15:
        return 0.95
    elif deviation <= 20:
        return 0.92
    elif deviation <= 30:
        return 0.87
    else:
        return 0.80


def get_azimuth_from_orientation(orientation: RoofOrientation) -> int:
    """Convert orientation to azimuth angle (0=North, 180=South)"""
    azimuth_map = {
        RoofOrientation.NORTH: 0,
        RoofOrientation.NORTHEAST: 45,
        RoofOrientation.EAST: 90,
        RoofOrientation.SOUTHEAST: 135,
        RoofOrientation.SOUTH: 180,
        RoofOrientation.SOUTHWEST: 225,
        RoofOrientation.WEST: 270,
        RoofOrientation.NORTHWEST: 315,
    }
    return azimuth_map.get(orientation, 180)


def calculate_static_yield(
    latitude: float,
    peak_power_kwp: float,
    roof_tilt: float,
    roof_orientation: RoofOrientation,
    system_loss: float = 14
) -> StaticYieldFactors:
    """Calculate yield using static factors"""
    # Get base yield for latitude
    base_yield = 950  # Default for Germany
    for (lat_min, lat_max), yield_value in STATIC_YIELD_FACTORS.items():
        if lat_min <= latitude < lat_max:
            base_yield = yield_value
            break
    
    # Apply corrections
    tilt_correction = get_tilt_correction(roof_tilt)
    orientation_correction = ORIENTATION_FACTORS.get(roof_orientation, 1.0)
    
    # Apply system loss
    loss_factor = 1 - (system_loss / 100)
    
    # Calculate final yield
    final_yield = base_yield * tilt_correction * orientation_correction * loss_factor
    
    return StaticYieldFactors(
        latitude=latitude,
        base_yield_kwh_kwp=base_yield,
        tilt_correction=tilt_correction,
        orientation_correction=orientation_correction,
        final_yield_kwh_kwp=final_yield
    )


async def fetch_pvgis_data(request: PVGISRequest) -> Optional[Dict[str, Any]]:
    """Fetch data from PVGIS API"""
    azimuth = get_azimuth_from_orientation(request.roof_orientation)
    
    params = {
        "lat": request.latitude,
        "lon": request.longitude,
        "peakpower": request.peak_power_kwp,
        "loss": request.system_loss,
        "angle": request.roof_tilt,
        "aspect": azimuth - 180,  # PVGIS uses -180 to 180 (0=South)
        "outputformat": "json",
        "mountingplace": request.mounting_type,
        "usehorizon": 1 if request.use_horizon else 0,
        "pvtechchoice": "crystSi",  # Crystalline silicon
    }
    
    try:
        async with httpx.AsyncClient(timeout=PVGIS_TIMEOUT) as client:
            response = await client.get(f"{PVGIS_BASE_URL}/PVcalc", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        print(f"PVGIS API error: {e}")
        return None


def parse_pvgis_response(data: Dict[str, Any], request: PVGISRequest) -> PVGISResponse:
    """Parse PVGIS API response"""
    outputs = data.get("outputs", {})
    inputs = data.get("inputs", {})
    
    # Get monthly data
    monthly_data = outputs.get("monthly", {}).get("fixed", [])
    monthly_yields = [month.get("E_m", 0) for month in monthly_data]
    
    # Get annual totals
    totals = outputs.get("totals", {}).get("fixed", {})
    annual_yield = totals.get("E_y", sum(monthly_yields))
    
    # Calculate specific yield
    specific_yield = annual_yield / request.peak_power_kwp if request.peak_power_kwp > 0 else 0
    
    return PVGISResponse(
        annual_yield_kwh=annual_yield,
        monthly_yields_kwh=monthly_yields,
        specific_yield_kwh_kwp=specific_yield,
        optimal_tilt=inputs.get("mounting_system", {}).get("slope", {}).get("optimal", request.roof_tilt),
        optimal_azimuth=inputs.get("mounting_system", {}).get("azimuth", {}).get("optimal", 0),
        data_source="PVGIS 5.2",
        location={
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        system_info={
            "peak_power_kwp": request.peak_power_kwp,
            "roof_tilt": request.roof_tilt,
            "roof_orientation": request.roof_orientation.value,
            "system_loss": request.system_loss
        }
    )


@router.post("/calculate", response_model=PVGISResponse)
async def calculate_yield(request: PVGISRequest):
    """
    Calculate PV yield using PVGIS API
    
    Falls back to static calculation if PVGIS is unavailable.
    """
    # Try PVGIS API first
    pvgis_data = await fetch_pvgis_data(request)
    
    if pvgis_data:
        return parse_pvgis_response(pvgis_data, request)
    
    # Fallback to static calculation
    static_factors = calculate_static_yield(
        latitude=request.latitude,
        peak_power_kwp=request.peak_power_kwp,
        roof_tilt=request.roof_tilt,
        roof_orientation=request.roof_orientation,
        system_loss=request.system_loss
    )
    
    annual_yield = static_factors.final_yield_kwh_kwp * request.peak_power_kwp
    
    # Estimate monthly distribution (simplified)
    monthly_distribution = [0.05, 0.06, 0.08, 0.10, 0.11, 0.12, 0.12, 0.11, 0.09, 0.08, 0.05, 0.03]
    monthly_yields = [annual_yield * factor for factor in monthly_distribution]
    
    return PVGISResponse(
        annual_yield_kwh=annual_yield,
        monthly_yields_kwh=monthly_yields,
        specific_yield_kwh_kwp=static_factors.final_yield_kwh_kwp,
        optimal_tilt=32,  # Optimal for Germany
        optimal_azimuth=180,  # South
        data_source="Static Calculation (PVGIS unavailable)",
        location={
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        system_info={
            "peak_power_kwp": request.peak_power_kwp,
            "roof_tilt": request.roof_tilt,
            "roof_orientation": request.roof_orientation.value,
            "system_loss": request.system_loss
        }
    )


@router.post("/static-yield", response_model=StaticYieldFactors)
async def get_static_yield(
    latitude: float = Query(..., ge=45, le=60, description="Latitude"),
    peak_power_kwp: float = Query(..., gt=0, description="Peak power in kWp"),
    roof_tilt: float = Query(30, ge=0, le=90, description="Roof tilt"),
    roof_orientation: RoofOrientation = Query(RoofOrientation.SOUTH),
    system_loss: float = Query(14, ge=0, le=100)
):
    """
    Calculate yield using static factors only
    
    Useful when PVGIS is not needed or for quick estimates.
    """
    return calculate_static_yield(
        latitude=latitude,
        peak_power_kwp=peak_power_kwp,
        roof_tilt=roof_tilt,
        roof_orientation=roof_orientation,
        system_loss=system_loss
    )


@router.post("/compare", response_model=YieldComparison)
async def compare_yields(request: PVGISRequest):
    """
    Compare PVGIS yield with static calculation
    
    Useful for validating calculations and understanding differences.
    """
    # Calculate static yield
    static_factors = calculate_static_yield(
        latitude=request.latitude,
        peak_power_kwp=request.peak_power_kwp,
        roof_tilt=request.roof_tilt,
        roof_orientation=request.roof_orientation,
        system_loss=request.system_loss
    )
    static_yield = static_factors.final_yield_kwh_kwp * request.peak_power_kwp
    
    # Try PVGIS
    pvgis_data = await fetch_pvgis_data(request)
    pvgis_yield = None
    
    if pvgis_data:
        pvgis_response = parse_pvgis_response(pvgis_data, request)
        pvgis_yield = pvgis_response.annual_yield_kwh
    
    # Calculate differences
    difference_kwh = None
    difference_percent = None
    recommended_source = "static"
    notes = ""
    
    if pvgis_yield is not None:
        difference_kwh = pvgis_yield - static_yield
        difference_percent = (difference_kwh / static_yield) * 100 if static_yield > 0 else 0
        
        # Recommend based on difference
        if abs(difference_percent) < 5:
            recommended_source = "either"
            notes = "Both calculations are within 5% - either can be used."
        elif pvgis_yield > static_yield:
            recommended_source = "pvgis"
            notes = f"PVGIS shows {difference_percent:.1f}% higher yield - location may have better conditions."
        else:
            recommended_source = "static"
            notes = f"Static calculation shows {abs(difference_percent):.1f}% higher yield - PVGIS may account for local shading."
    else:
        notes = "PVGIS unavailable - using static calculation only."
    
    return YieldComparison(
        pvgis_yield_kwh=pvgis_yield,
        static_yield_kwh=static_yield,
        difference_kwh=difference_kwh,
        difference_percent=difference_percent,
        recommended_source=recommended_source,
        notes=notes
    )


@router.get("/optimal-configuration")
async def get_optimal_configuration(
    latitude: float = Query(..., ge=45, le=60),
    longitude: float = Query(..., ge=5, le=16),
    peak_power_kwp: float = Query(..., gt=0)
):
    """
    Get optimal roof configuration for maximum yield
    
    Returns optimal tilt and orientation for the given location.
    """
    # Try PVGIS for optimal values
    request = PVGISRequest(
        latitude=latitude,
        longitude=longitude,
        peak_power_kwp=peak_power_kwp,
        roof_tilt=35,  # Will be optimized
        roof_orientation=RoofOrientation.SOUTH
    )
    
    pvgis_data = await fetch_pvgis_data(request)
    
    if pvgis_data:
        inputs = pvgis_data.get("inputs", {})
        mounting = inputs.get("mounting_system", {})
        
        optimal_tilt = mounting.get("slope", {}).get("optimal", 32)
        optimal_azimuth = mounting.get("azimuth", {}).get("optimal", 0)
        
        # Convert azimuth to orientation
        optimal_orientation = RoofOrientation.SOUTH
        if -45 <= optimal_azimuth < 45:
            optimal_orientation = RoofOrientation.SOUTH
        elif 45 <= optimal_azimuth < 90:
            optimal_orientation = RoofOrientation.SOUTHWEST
        elif -90 <= optimal_azimuth < -45:
            optimal_orientation = RoofOrientation.SOUTHEAST
        
        return {
            "optimal_tilt_degrees": optimal_tilt,
            "optimal_azimuth_degrees": optimal_azimuth,
            "optimal_orientation": optimal_orientation.value,
            "data_source": "PVGIS",
            "notes": "Optimal values calculated by PVGIS for maximum annual yield."
        }
    
    # Fallback to static optimal values for Germany
    return {
        "optimal_tilt_degrees": 32,
        "optimal_azimuth_degrees": 0,
        "optimal_orientation": "south",
        "data_source": "Static (Germany average)",
        "notes": "PVGIS unavailable - using average optimal values for Germany."
    }


@router.get("/monthly-profile")
async def get_monthly_profile(
    latitude: float = Query(..., ge=45, le=60),
    longitude: float = Query(..., ge=5, le=16),
    peak_power_kwp: float = Query(..., gt=0),
    roof_tilt: float = Query(30),
    roof_orientation: RoofOrientation = Query(RoofOrientation.SOUTH)
):
    """
    Get monthly yield profile
    
    Returns expected yield for each month of the year.
    """
    request = PVGISRequest(
        latitude=latitude,
        longitude=longitude,
        peak_power_kwp=peak_power_kwp,
        roof_tilt=roof_tilt,
        roof_orientation=roof_orientation
    )
    
    pvgis_data = await fetch_pvgis_data(request)
    
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    
    if pvgis_data:
        outputs = pvgis_data.get("outputs", {})
        monthly_data = outputs.get("monthly", {}).get("fixed", [])
        
        profile = []
        for i, month_data in enumerate(monthly_data):
            profile.append({
                "month": months[i],
                "month_number": i + 1,
                "yield_kwh": month_data.get("E_m", 0),
                "irradiance_kwh_m2": month_data.get("H(i)_m", 0),
                "data_source": "PVGIS"
            })
        
        return {
            "monthly_profile": profile,
            "annual_total_kwh": sum(m["yield_kwh"] for m in profile),
            "peak_month": max(profile, key=lambda x: x["yield_kwh"])["month"],
            "lowest_month": min(profile, key=lambda x: x["yield_kwh"])["month"]
        }
    
    # Fallback to static distribution
    static_factors = calculate_static_yield(
        latitude=latitude,
        peak_power_kwp=peak_power_kwp,
        roof_tilt=roof_tilt,
        roof_orientation=roof_orientation
    )
    
    annual_yield = static_factors.final_yield_kwh_kwp * peak_power_kwp
    monthly_distribution = [0.05, 0.06, 0.08, 0.10, 0.11, 0.12, 0.12, 0.11, 0.09, 0.08, 0.05, 0.03]
    
    profile = []
    for i, factor in enumerate(monthly_distribution):
        profile.append({
            "month": months[i],
            "month_number": i + 1,
            "yield_kwh": annual_yield * factor,
            "irradiance_kwh_m2": None,
            "data_source": "Static"
        })
    
    return {
        "monthly_profile": profile,
        "annual_total_kwh": annual_yield,
        "peak_month": "Juni",
        "lowest_month": "Dezember"
    }
