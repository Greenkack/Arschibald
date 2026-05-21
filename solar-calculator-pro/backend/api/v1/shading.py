"""
Shading Analysis API Endpoints

Provides REST API for solar shading analysis functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ...services.shading_analysis_service import (
    ShadingAnalysisService,
    ShadingAnalysisRequest,
    ShadingAnalysisResponse,
    ObstacleModel,
    LocationModel
)

router = APIRouter(prefix="/shading", tags=["shading"])

# Initialize service
shading_service = ShadingAnalysisService()


@router.post("/analyze", response_model=ShadingAnalysisResponse)
async def analyze_shading(request: ShadingAnalysisRequest):
    """
    Perform comprehensive shading analysis
    
    This endpoint analyzes shading effects on solar installations considering:
    - Multiple obstacles (buildings, trees, etc.)
    - Time-based sun position calculations
    - Annual energy loss estimates
    - Optimization suggestions
    - Visualization data
    
    **Example Request:**
    ```json
    {
      "location": {
        "latitude": 52.52,
        "longitude": 13.405,
        "timezone": "Europe/Berlin",
        "elevation": 34.0
      },
      "obstacles": [
        {
          "id": "building_1",
          "type": "building",
          "height": 15.0,
          "distance": 20.0,
          "azimuth": 180.0,
          "width": 10.0,
          "description": "Neighboring building"
        }
      ],
      "module_tilt": 30.0,
      "module_azimuth": 180.0,
      "module_area": 50.0,
      "analysis_start_date": "2024-01-01T00:00:00",
      "analysis_end_date": "2024-12-31T23:59:59",
      "time_resolution": 60
    }
    ```
    
    **Returns:**
    - Detailed shading loss analysis
    - Monthly and annual loss percentages
    - Visualization data for charts
    - Optimization suggestions
    """
    try:
        result = shading_service.analyze_shading(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shading analysis failed: {str(e)}"
        )


@router.post("/quick-check")
async def quick_shading_check(
    location: LocationModel,
    obstacles: List[ObstacleModel],
    module_azimuth: float
):
    """
    Perform quick shading check for current conditions
    
    Returns immediate shading status without full analysis.
    Useful for real-time monitoring and quick assessments.
    
    **Example Request:**
    ```json
    {
      "location": {
        "latitude": 52.52,
        "longitude": 13.405,
        "timezone": "Europe/Berlin"
      },
      "obstacles": [...],
      "module_azimuth": 180.0
    }
    ```
    
    **Returns:**
    - Current sun position
    - Current shading status
    - Shading percentage
    - Affected obstacles
    """
    try:
        result = shading_service.quick_shading_check(
            location,
            obstacles,
            module_azimuth
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick shading check failed: {str(e)}"
        )


@router.post("/sun-path")
async def calculate_sun_path(
    location: LocationModel,
    date: datetime,
    time_resolution: int = 60
):
    """
    Calculate sun path for a specific date and location
    
    Returns sun position data throughout the day for visualization.
    
    **Parameters:**
    - location: Geographic location
    - date: Date for calculation
    - time_resolution: Minutes between calculations (default: 60)
    
    **Returns:**
    List of sun positions with altitude and azimuth angles
    """
    try:
        from ...services.shading_analysis_service import SunPositionCalculator
        
        sun_path = SunPositionCalculator.calculate_sun_path(
            location,
            date,
            time_resolution
        )
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude
            },
            "sun_path": sun_path,
            "data_points": len(sun_path)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sun path calculation failed: {str(e)}"
        )


@router.post("/shadow-profile")
async def calculate_shadow_profile(
    obstacles: List[ObstacleModel],
    location: LocationModel,
    module_azimuth: float,
    date: datetime,
    time_resolution: int = 60
):
    """
    Calculate shadow profile for a specific day
    
    Shows when and how much shading occurs throughout the day.
    
    **Returns:**
    Hourly shading profile with percentages and affected obstacles
    """
    try:
        from ...services.shading_analysis_service import (
            SunPositionCalculator,
            ObstacleShadowCalculator
        )
        
        # Calculate sun path
        sun_path = SunPositionCalculator.calculate_sun_path(
            location,
            date,
            time_resolution
        )
        
        # Calculate shadow profile
        shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
            obstacles,
            sun_path,
            module_azimuth
        )
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "shadow_profile": shadow_profile,
            "total_shaded_periods": sum(1 for p in shadow_profile if p['shaded']),
            "max_shading_percent": max(p['shading_percent'] for p in shadow_profile) if shadow_profile else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shadow profile calculation failed: {str(e)}"
        )


@router.post("/optimization-suggestions")
async def get_optimization_suggestions(
    current_tilt: float,
    current_azimuth: float,
    obstacles: List[ObstacleModel],
    location: LocationModel
):
    """
    Get optimization suggestions to reduce shading
    
    Analyzes current configuration and provides actionable recommendations.
    
    **Returns:**
    List of optimization suggestions with:
    - Type of optimization
    - Description
    - Potential improvement percentage
    - Implementation difficulty
    - Estimated cost
    """
    try:
        from ...services.shading_analysis_service import ShadingOptimizationSuggester
        
        suggestions = ShadingOptimizationSuggester.generate_all_suggestions(
            current_tilt,
            current_azimuth,
            obstacles,
            location
        )
        
        return {
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "max_potential_improvement": max(
                s.potential_improvement_percent for s in suggestions
            ) if suggestions else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization suggestions failed: {str(e)}"
        )


@router.post("/visualization-data")
async def get_visualization_data(
    location: LocationModel,
    obstacles: List[ObstacleModel],
    module_azimuth: float,
    start_date: datetime,
    days: int = 365
):
    """
    Get comprehensive visualization data for shading analysis
    
    Provides data for:
    - Sun path diagrams
    - Shading heatmaps
    - Obstacle shadow visualizations
    - Timeline charts
    
    **Parameters:**
    - days: Number of days to analyze (default: 365 for full year)
    
    **Returns:**
    Complete visualization dataset
    """
    try:
        from ...services.shading_analysis_service import ShadingVisualizationGenerator
        
        viz_gen = ShadingVisualizationGenerator()
        
        # Generate sun path for sample day
        sun_path = viz_gen.generate_sun_path_data(location, start_date)
        
        # Generate heatmap data
        heatmap = viz_gen.generate_heatmap_data(
            location,
            obstacles,
            module_azimuth,
            start_date,
            days
        )
        
        # Get noon sun position for obstacle shadows
        noon_sun = [s for s in sun_path if s['hour'] == 12]
        if noon_sun:
            obstacle_shadows = viz_gen.generate_obstacle_shadows(
                obstacles,
                noon_sun[0]['altitude'],
                noon_sun[0]['azimuth']
            )
        else:
            obstacle_shadows = []
        
        return {
            "sun_path": sun_path,
            "heatmap": heatmap,
            "obstacle_shadows": obstacle_shadows,
            "analysis_period_days": days
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Visualization data generation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for shading analysis service"""
    return {
        "status": "healthy",
        "service": "shading_analysis",
        "version": "1.0.0"
    }
