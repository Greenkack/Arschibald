"""
API endpoints for advanced 3D visualization features.

Provides endpoints for:
- Material rendering
- Lighting and shadows
- Weather visualization
- Time-of-day simulation
- Seasonal visualization
- Photo-realistic rendering

Requirements: 1.3, 6.1
Task: 134
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from services.visualization_3d_advanced_features import (
    Visualization3DAdvancedFeatures,
    MaterialProperties,
    LightSource,
    WeatherConditions,
    TimeOfDay
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualization/3d/advanced", tags=["3D Visualization Advanced"])

# Initialize service
viz_service = Visualization3DAdvancedFeatures()


# ========================================================================
# Request/Response Models
# ========================================================================

class MaterialRequest(BaseModel):
    """Request for material application."""
    scene_data: Dict[str, Any]
    material_mapping: Optional[Dict[str, str]] = None


class LightingRequest(BaseModel):
    """Request for lighting setup."""
    time_of_day: Dict[str, Any]
    weather: Dict[str, Any]
    quality: str = Field(default="high", pattern="^(low|medium|high|ultra)$")


class ShadowRequest(BaseModel):
    """Request for shadow calculation."""
    scene_data: Dict[str, Any]
    light_sources: List[Dict[str, Any]]
    quality: str = Field(default="high", pattern="^(low|medium|high|ultra)$")


class WeatherRequest(BaseModel):
    """Request for weather effects."""
    weather: Dict[str, Any]
    scene_bounds: List[float] = Field(default=[50.0, 50.0, 20.0])


class SunPathRequest(BaseModel):
    """Request for sun path calculation."""
    date: str  # ISO format
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone_offset: int = Field(default=0, ge=-12, le=14)


class TimeSimulationRequest(BaseModel):
    """Request for time-of-day simulation."""
    scene_data: Dict[str, Any]
    start_time: Dict[str, Any]
    duration_hours: float = Field(default=12.0, gt=0, le=24)
    steps: int = Field(default=24, ge=4, le=96)
    weather: Optional[Dict[str, Any]] = None


class SeasonalRequest(BaseModel):
    """Request for seasonal simulation."""
    scene_data: Dict[str, Any]
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    year: int = Field(default=2024, ge=2020, le=2030)


class PhotorealisticRequest(BaseModel):
    """Request for photorealistic rendering."""
    scene_data: Dict[str, Any]
    time_of_day: Dict[str, Any]
    weather: Dict[str, Any]
    camera_config: Optional[Dict[str, Any]] = None
    render_settings: Optional[Dict[str, Any]] = None


# ========================================================================
# Endpoints
# ========================================================================

@router.post("/materials/apply")
async def apply_materials(request: MaterialRequest) -> Dict[str, Any]:
    """
    Apply PBR materials to scene objects.
    
    Returns scene data with realistic materials applied.
    """
    try:
        result = viz_service.apply_materials_to_scene(
            scene_data=request.scene_data,
            material_mapping=request.material_mapping
        )
        return {
            "success": True,
            "scene_data": result
        }
    except Exception as e:
        logger.error(f"Error applying materials: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials/library")
async def get_material_library() -> Dict[str, Any]:
    """
    Get available materials from the library.
    
    Returns list of all available PBR materials.
    """
    try:
        materials = {
            name: {
                "name": mat.name,
                "base_color": mat.base_color,
                "metallic": mat.metallic,
                "roughness": mat.roughness,
                "reflectivity": mat.reflectivity
            }
            for name, mat in viz_service.material_library.items()
        }
        return {
            "success": True,
            "materials": materials
        }
    except Exception as e:
        logger.error(f"Error getting material library: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lighting/setup")
async def create_lighting(request: LightingRequest) -> Dict[str, Any]:
    """
    Create complete lighting setup for scene.
    
    Returns configured light sources based on time and weather.
    """
    try:
        time_of_day = TimeOfDay(**request.time_of_day)
        weather = WeatherConditions(**request.weather)
        
        lights = viz_service.create_lighting_setup(
            time_of_day=time_of_day,
            weather=weather,
            quality=request.quality
        )
        
        return {
            "success": True,
            "lights": [
                {
                    "type": light.type,
                    "position": light.position,
                    "direction": light.direction,
                    "color": light.color,
                    "intensity": light.intensity,
                    "cast_shadows": light.cast_shadows
                }
                for light in lights
            ]
        }
    except Exception as e:
        logger.error(f"Error creating lighting: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shadows/calculate")
async def calculate_shadows(request: ShadowRequest) -> Dict[str, Any]:
    """
    Calculate shadow maps for the scene.
    
    Returns shadow configuration data.
    """
    try:
        # Convert dict light sources to LightSource objects
        light_objects = [
            LightSource(**light_data)
            for light_data in request.light_sources
        ]
        
        shadows = viz_service.calculate_shadows(
            scene_data=request.scene_data,
            light_sources=light_objects,
            quality=request.quality
        )
        
        return {
            "success": True,
            "shadows": shadows
        }
    except Exception as e:
        logger.error(f"Error calculating shadows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/effects")
async def create_weather_effects(request: WeatherRequest) -> Dict[str, Any]:
    """
    Create weather effects for the scene.
    
    Returns weather effect configuration (clouds, fog, precipitation).
    """
    try:
        weather = WeatherConditions(**request.weather)
        
        effects = viz_service.create_weather_effects(
            weather=weather,
            scene_bounds=tuple(request.scene_bounds)
        )
        
        return {
            "success": True,
            "effects": effects
        }
    except Exception as e:
        logger.error(f"Error creating weather effects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sun-path/calculate")
async def calculate_sun_path(request: SunPathRequest) -> Dict[str, Any]:
    """
    Calculate sun path for entire day.
    
    Returns list of sun positions throughout the day.
    """
    try:
        date = datetime.fromisoformat(request.date)
        
        sun_path = viz_service.calculate_sun_path(
            date=date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_offset=request.timezone_offset
        )
        
        return {
            "success": True,
            "sun_path": sun_path,
            "daylight_hours": len(sun_path) / 4  # Approximate
        }
    except Exception as e:
        logger.error(f"Error calculating sun path: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/time/simulate")
async def simulate_time_of_day(request: TimeSimulationRequest) -> Dict[str, Any]:
    """
    Simulate scene at different times of day.
    
    Returns list of scene snapshots across time range.
    """
    try:
        start_time = TimeOfDay(**request.start_time)
        weather = WeatherConditions(**request.weather) if request.weather else None
        
        snapshots = viz_service.simulate_time_of_day(
            scene_data=request.scene_data,
            start_time=start_time,
            duration_hours=request.duration_hours,
            steps=request.steps,
            weather=weather
        )
        
        # Convert TimeOfDay objects to dicts for JSON serialization
        serialized_snapshots = []
        for snapshot in snapshots:
            serialized_snapshot = snapshot.copy()
            serialized_snapshot["time"] = {
                "hour": snapshot["time"].hour,
                "minute": snapshot["time"].minute,
                "date": snapshot["time"].date.isoformat()
            }
            serialized_snapshots.append(serialized_snapshot)
        
        return {
            "success": True,
            "snapshots": serialized_snapshots,
            "count": len(serialized_snapshots)
        }
    except Exception as e:
        logger.error(f"Error simulating time of day: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seasons/simulate")
async def simulate_seasons(request: SeasonalRequest) -> Dict[str, Any]:
    """
    Simulate scene across all four seasons.
    
    Returns seasonal variations with lighting, weather, and colors.
    """
    try:
        seasons = viz_service.simulate_seasons(
            scene_data=request.scene_data,
            location=(request.latitude, request.longitude),
            year=request.year
        )
        
        return {
            "success": True,
            "seasons": seasons
        }
    except Exception as e:
        logger.error(f"Error simulating seasons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render/photorealistic")
async def create_photorealistic_render(request: PhotorealisticRequest) -> Dict[str, Any]:
    """
    Create photo-realistic render configuration.
    
    Returns complete render setup with all advanced features.
    """
    try:
        time_of_day = TimeOfDay(**request.time_of_day)
        weather = WeatherConditions(**request.weather)
        
        render_config = viz_service.create_photorealistic_render(
            scene_data=request.scene_data,
            time_of_day=time_of_day,
            weather=weather,
            camera_config=request.camera_config,
            render_settings=request.render_settings
        )
        
        # Convert TimeOfDay in metadata
        render_config["metadata"]["time_of_day"] = {
            "hour": time_of_day.hour,
            "minute": time_of_day.minute,
            "date": time_of_day.date.isoformat()
        }
        
        return {
            "success": True,
            "render_config": render_config
        }
    except Exception as e:
        logger.error(f"Error creating photorealistic render: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/weather")
async def get_weather_presets() -> Dict[str, Any]:
    """
    Get predefined weather presets.
    
    Returns common weather configurations.
    """
    presets = {
        "clear_sunny": {
            "cloud_coverage": 0.0,
            "sun_intensity": 1.0,
            "ambient_light": 0.5,
            "fog_density": 0.0,
            "precipitation": "none",
            "wind_speed_ms": 2.0,
            "temperature_c": 25.0
        },
        "partly_cloudy": {
            "cloud_coverage": 0.3,
            "sun_intensity": 0.8,
            "ambient_light": 0.4,
            "fog_density": 0.0,
            "precipitation": "none",
            "wind_speed_ms": 3.0,
            "temperature_c": 20.0
        },
        "overcast": {
            "cloud_coverage": 0.9,
            "sun_intensity": 0.3,
            "ambient_light": 0.3,
            "fog_density": 0.1,
            "precipitation": "none",
            "wind_speed_ms": 4.0,
            "temperature_c": 15.0
        },
        "rainy": {
            "cloud_coverage": 0.95,
            "sun_intensity": 0.2,
            "ambient_light": 0.2,
            "fog_density": 0.2,
            "precipitation": "rain",
            "wind_speed_ms": 5.0,
            "temperature_c": 12.0
        },
        "foggy": {
            "cloud_coverage": 0.7,
            "sun_intensity": 0.3,
            "ambient_light": 0.25,
            "fog_density": 0.8,
            "precipitation": "none",
            "wind_speed_ms": 1.0,
            "temperature_c": 10.0
        }
    }
    
    return {
        "success": True,
        "presets": presets
    }
