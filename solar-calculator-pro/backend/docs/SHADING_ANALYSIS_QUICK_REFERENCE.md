# Shading Analysis - Quick Reference

## Installation

```bash
# No additional dependencies required
# Uses standard Python libraries: math, numpy, datetime
```

## Basic Usage

```python
from services.shading_analysis_service import (
    ShadingAnalysisService,
    ShadingAnalysisRequest,
    ObstacleModel,
    LocationModel
)
from datetime import datetime

# 1. Create service
service = ShadingAnalysisService()

# 2. Define location
location = LocationModel(
    latitude=52.52,
    longitude=13.405,
    timezone="Europe/Berlin"
)

# 3. Define obstacles
obstacles = [
    ObstacleModel(
        id="building_1",
        type="building",
        height=15.0,
        distance=20.0,
        azimuth=180.0,
        width=10.0
    )
]

# 4. Create request
request = ShadingAnalysisRequest(
    location=location,
    obstacles=obstacles,
    module_tilt=30.0,
    module_azimuth=180.0,
    module_area=50.0,
    analysis_start_date=datetime(2024, 1, 1),
    analysis_end_date=datetime(2024, 12, 31)
)

# 5. Analyze
result = service.analyze_shading(request)

# 6. Get results
print(f"Loss: {result.losses.total_annual_loss_percent}%")
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/shading/analyze` | POST | Full analysis |
| `/api/v1/shading/quick-check` | POST | Current status |
| `/api/v1/shading/sun-path` | POST | Sun trajectory |
| `/api/v1/shading/shadow-profile` | POST | Daily shadows |
| `/api/v1/shading/optimization-suggestions` | POST | Recommendations |
| `/api/v1/shading/visualization-data` | POST | Chart data |

## Key Parameters

### Location
- `latitude`: -90 to 90 degrees
- `longitude`: -180 to 180 degrees
- `timezone`: IANA timezone string
- `elevation`: meters above sea level

### Obstacle
- `height`: meters (vertical)
- `distance`: meters (horizontal)
- `azimuth`: 0-360° (0=North, 180=South)
- `width`: meters (horizontal)
- `type`: building, tree, chimney, other

### Module Configuration
- `module_tilt`: 0-90° (0=flat, 90=vertical)
- `module_azimuth`: 0-360° (optimal: 180° in Northern Hemisphere)
- `module_area`: square meters

## Response Structure

```python
{
    "losses": {
        "total_annual_loss_percent": float,
        "monthly_losses": dict,
        "critical_periods": list,
        "affected_area_percent": float
    },
    "visualization": {
        "sun_path_data": list,
        "shading_timeline": list,
        "obstacle_shadows": list,
        "heatmap_data": dict
    },
    "suggestions": [
        {
            "type": str,
            "description": str,
            "potential_improvement_percent": float,
            "implementation_difficulty": str,
            "estimated_cost": float
        }
    ],
    "analysis_metadata": dict
}
```

## Common Patterns

### Quick Check
```python
result = service.quick_shading_check(location, obstacles, module_azimuth)
if result['currently_shaded']:
    print(f"⚠️ {result['shading_percent']}% shaded")
```

### Sun Path
```python
from services.shading_analysis_service import SunPositionCalculator

sun_path = SunPositionCalculator.calculate_sun_path(
    location, datetime(2024, 6, 21), time_resolution=60
)
```

### Shadow Profile
```python
from services.shading_analysis_service import ObstacleShadowCalculator

shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
    obstacles, sun_path, module_azimuth
)
```

### Optimization
```python
from services.shading_analysis_service import ShadingOptimizationSuggester

suggestions = ShadingOptimizationSuggester.generate_all_suggestions(
    current_tilt, current_azimuth, obstacles, location
)
```

## Optimization Types

| Type | Difficulty | Cost | Improvement |
|------|-----------|------|-------------|
| Tilt Adjustment | Easy | €500 | 5-10% |
| Azimuth Adjustment | Moderate | €1,500 | 10-20% |
| Module Relocation | Difficult | €5,000 | 20-30% |
| Obstacle Removal | Easy-Moderate | €300-2,000 | 10-25% |

## Performance Tips

1. **Time Resolution**
   - 60 min: Fast, good for overview
   - 30 min: Balanced
   - 15 min: Detailed, slower

2. **Analysis Period**
   - 1 day: Quick test
   - 1 week: Representative sample
   - 1 month: Seasonal analysis
   - 1 year: Complete picture

3. **Obstacle Count**
   - < 5: Fast
   - 5-10: Normal
   - > 10: Consider combining

## Error Handling

```python
try:
    result = service.analyze_shading(request)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
```

## Testing

```bash
# Run tests
pytest tests/test_shading_analysis_service.py -v

# Run demo
python demo_shading_analysis.py
```

## Formulas

### Sun Position
```
altitude = arcsin(sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(ha))
azimuth = arccos((sin(dec) - sin(lat) * sin(alt)) / (cos(lat) * cos(alt)))
```

### Shadow Length
```
shadow_length = obstacle_height / tan(sun_altitude)
```

### Energy Loss
```
loss_percent = (potential_energy - actual_energy) / potential_energy * 100
```

## Coordinate Systems

### Azimuth
- 0° = North
- 90° = East
- 180° = South
- 270° = West

### Altitude
- 0° = Horizon
- 90° = Zenith (directly overhead)

## Typical Values

### Module Tilt (Northern Hemisphere)
- Latitude 30°: 25-30° tilt
- Latitude 45°: 35-40° tilt
- Latitude 60°: 50-55° tilt

### Module Azimuth
- Northern Hemisphere: 180° (South)
- Southern Hemisphere: 0° (North)

### Acceptable Shading Loss
- Excellent: < 5%
- Good: 5-10%
- Acceptable: 10-15%
- Poor: 15-20%
- Unacceptable: > 20%

## Troubleshooting

| Issue | Solution |
|-------|----------|
| High losses | Check obstacle data, consider relocation |
| No suggestions | Verify obstacles exist, check thresholds |
| Slow analysis | Reduce time resolution, limit date range |
| Inconsistent results | Verify coordinates, check timezone |

## Examples

### Residential Installation
```python
# Typical house with tree
obstacles = [
    ObstacleModel(
        id="tree",
        type="tree",
        height=12.0,
        distance=15.0,
        azimuth=135.0,
        width=6.0
    )
]
```

### Commercial Installation
```python
# Building with multiple obstacles
obstacles = [
    ObstacleModel(id="building_north", type="building", 
                  height=20.0, distance=30.0, azimuth=0.0, width=15.0),
    ObstacleModel(id="building_east", type="building",
                  height=18.0, distance=25.0, azimuth=90.0, width=12.0)
]
```

### Urban Installation
```python
# Dense urban environment
obstacles = [
    ObstacleModel(id=f"building_{i}", type="building",
                  height=15.0 + i*3, distance=20.0 + i*5,
                  azimuth=i*60, width=10.0)
    for i in range(6)
]
```

## Resources

- Demo: `demo_shading_analysis.py`
- Tests: `tests/test_shading_analysis_service.py`
- Full Guide: `docs/SHADING_ANALYSIS_GUIDE.md`
- API Docs: `/api/v1/docs`
