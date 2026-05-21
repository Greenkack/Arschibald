# Solar Shading Analysis Service - Complete Guide

## Overview

The Solar Shading Analysis Service provides comprehensive analysis of shading effects on solar installations. It calculates energy losses, generates visualizations, and provides optimization suggestions to minimize shading impact.

## Features

### 1. **Time-Based Shading Simulation**
- Accurate sun position calculations for any location and time
- Complete sun path tracking throughout the year
- Hourly shading profile generation
- Seasonal variation analysis

### 2. **Obstacle Detection and Modeling**
- Support for multiple obstacle types (buildings, trees, chimneys, etc.)
- 3D obstacle modeling with height, distance, and azimuth
- Shadow length and angle calculations
- Multi-obstacle interaction analysis

### 3. **Shading Loss Calculations**
- Annual energy loss estimation
- Monthly loss breakdown
- Hourly irradiance calculations
- Critical period identification
- Affected area percentage

### 4. **Optimization Suggestions**
- Tilt angle adjustments
- Azimuth angle modifications
- Module relocation recommendations
- Obstacle removal/trimming suggestions
- Cost-benefit analysis

### 5. **Visualization Data**
- Sun path diagrams
- Shading timeline charts
- Annual heatmaps
- Obstacle shadow visualizations
- Interactive 3D representations

## Quick Start

### Basic Analysis

```python
from services.shading_analysis_service import (
    ShadingAnalysisService,
    ShadingAnalysisRequest,
    ObstacleModel,
    LocationModel
)
from datetime import datetime

# Define location
location = LocationModel(
    latitude=52.52,
    longitude=13.405,
    timezone="Europe/Berlin",
    elevation=34.0
)

# Define obstacles
obstacles = [
    ObstacleModel(
        id="building_1",
        type="building",
        height=15.0,
        distance=20.0,
        azimuth=180.0,
        width=10.0,
        description="Neighboring building"
    )
]

# Create request
request = ShadingAnalysisRequest(
    location=location,
    obstacles=obstacles,
    module_tilt=30.0,
    module_azimuth=180.0,
    module_area=50.0,
    analysis_start_date=datetime(2024, 1, 1),
    analysis_end_date=datetime(2024, 12, 31),
    time_resolution=60
)

# Perform analysis
service = ShadingAnalysisService()
result = service.analyze_shading(request)

# Access results
print(f"Annual Loss: {result.losses.total_annual_loss_percent}%")
print(f"Suggestions: {len(result.suggestions)}")
```

### Quick Shading Check

```python
# Check current shading status
result = service.quick_shading_check(
    location,
    obstacles,
    module_azimuth=180.0
)

print(f"Currently Shaded: {result['currently_shaded']}")
print(f"Shading Percentage: {result['shading_percent']}%")
```

## API Endpoints

### POST /api/v1/shading/analyze

Perform comprehensive shading analysis.

**Request Body:**
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

**Response:**
```json
{
  "losses": {
    "total_annual_loss_percent": 12.5,
    "monthly_losses": {
      "2024-01": 15.2,
      "2024-02": 14.8,
      ...
    },
    "critical_periods": [...],
    "affected_area_percent": 12.5
  },
  "visualization": {
    "sun_path_data": [...],
    "shading_timeline": [...],
    "obstacle_shadows": [...],
    "heatmap_data": {...}
  },
  "suggestions": [...],
  "analysis_metadata": {...}
}
```

### POST /api/v1/shading/quick-check

Quick shading status check.

**Request Body:**
```json
{
  "location": {...},
  "obstacles": [...],
  "module_azimuth": 180.0
}
```

**Response:**
```json
{
  "timestamp": "2024-01-15T12:00:00",
  "sun_altitude": 25.5,
  "sun_azimuth": 180.0,
  "currently_shaded": true,
  "shading_percent": 35.0,
  "shading_obstacles": [...]
}
```

### POST /api/v1/shading/sun-path

Calculate sun path for visualization.

### POST /api/v1/shading/shadow-profile

Calculate daily shadow profile.

### POST /api/v1/shading/optimization-suggestions

Get optimization suggestions.

### POST /api/v1/shading/visualization-data

Get comprehensive visualization data.

## Algorithms

### Sun Position Calculation

The service uses astronomical algorithms to calculate sun position:

```
altitude = arcsin(sin(latitude) * sin(declination) + 
                  cos(latitude) * cos(declination) * cos(hour_angle))

azimuth = arccos((sin(declination) - sin(latitude) * sin(altitude)) /
                 (cos(latitude) * cos(altitude)))
```

Where:
- `declination` = 23.45° * sin(360° * (284 + day_of_year) / 365)
- `hour_angle` = 15° * (hour - 12)

### Shadow Angle Calculation

Shadow angle from obstacles:

```
shadow_length = obstacle_height / tan(sun_altitude)
shadow_angle = arctan(obstacle_height / (obstacle_distance + shadow_length))
```

### Energy Loss Calculation

Hourly irradiance with shading:

```
base_irradiance = clear_sky_irradiance * sin(sun_altitude)
actual_irradiance = base_irradiance * (1 - shading_percent / 100)
energy_loss = (potential_energy - actual_energy) / potential_energy * 100
```

## Obstacle Types

### Supported Types

1. **Building**
   - Permanent structures
   - Fixed height and position
   - Typically causes consistent shading

2. **Tree**
   - Variable height (seasonal growth)
   - Can be trimmed or removed
   - Irregular shadow patterns

3. **Chimney**
   - Small but tall obstacles
   - Localized shading effect
   - Usually on same building

4. **Other**
   - Custom obstacles
   - Flexible modeling

### Obstacle Parameters

- **height**: Vertical height in meters
- **distance**: Horizontal distance from modules in meters
- **azimuth**: Direction in degrees (0=North, 90=East, 180=South, 270=West)
- **width**: Horizontal width in meters
- **type**: Obstacle category
- **description**: Optional text description

## Optimization Strategies

### 1. Tilt Adjustment

**When to use:**
- Low obstacles (< 5m)
- Current tilt < 35°
- Morning/evening shading

**Benefits:**
- Easy to implement
- Low cost (€500-1000)
- 5-10% improvement potential

### 2. Azimuth Adjustment

**When to use:**
- Obstacles concentrated in one direction
- Flexible mounting system
- Azimuth difference < 45°

**Benefits:**
- Moderate implementation
- Medium cost (€1500-3000)
- 10-20% improvement potential

### 3. Module Relocation

**When to use:**
- Multiple close obstacles (< 10m)
- Alternative mounting locations available
- High shading losses (> 20%)

**Benefits:**
- Significant improvement
- High cost (€5000+)
- 20-30% improvement potential

### 4. Obstacle Removal

**When to use:**
- Trees causing shading
- Removable structures
- Owner has control

**Benefits:**
- Permanent solution
- Variable cost (€300-2000)
- 10-25% improvement potential

## Visualization Examples

### Sun Path Diagram

Shows sun trajectory throughout the day:
- X-axis: Azimuth angle (0-360°)
- Y-axis: Altitude angle (0-90°)
- Multiple curves for different seasons

### Shading Timeline

Hourly shading percentage:
- X-axis: Time of day
- Y-axis: Shading percentage (0-100%)
- Color-coded by severity

### Annual Heatmap

Year-long shading overview:
- X-axis: Day of year (1-365)
- Y-axis: Hour of day (0-23)
- Color intensity: Shading percentage

### Obstacle Shadows

3D visualization of shadows:
- Obstacle positions and heights
- Shadow lengths and directions
- Module placement overlay

## Best Practices

### 1. Data Collection

- Measure obstacle heights accurately
- Use GPS for precise distances
- Document all nearby structures
- Consider seasonal changes (tree foliage)

### 2. Analysis Period

- Analyze full year for complete picture
- Focus on critical months (winter)
- Consider local weather patterns
- Account for snow accumulation

### 3. Optimization

- Prioritize high-impact suggestions
- Consider implementation costs
- Evaluate long-term benefits
- Consult with installers

### 4. Monitoring

- Perform periodic re-analysis
- Track actual vs. predicted losses
- Update obstacle data as needed
- Adjust for new construction

## Troubleshooting

### High Shading Losses

**Problem:** Analysis shows > 20% annual loss

**Solutions:**
1. Review obstacle data accuracy
2. Consider module relocation
3. Evaluate obstacle removal options
4. Adjust tilt/azimuth angles

### Inconsistent Results

**Problem:** Results vary significantly between runs

**Solutions:**
1. Verify location coordinates
2. Check obstacle parameters
3. Ensure consistent time resolution
4. Review timezone settings

### Missing Suggestions

**Problem:** No optimization suggestions generated

**Solutions:**
1. Verify obstacles are defined
2. Check current configuration
3. Ensure losses are significant
4. Review suggestion thresholds

## Performance Considerations

### Analysis Duration

- Quick check: < 1 second
- Daily analysis: 1-2 seconds
- Monthly analysis: 10-20 seconds
- Annual analysis: 2-5 minutes

### Optimization Tips

1. **Time Resolution**
   - Use 60 minutes for quick analysis
   - Use 30 minutes for detailed analysis
   - Use 15 minutes for research purposes

2. **Date Range**
   - Analyze representative days for speed
   - Use full year for accuracy
   - Sample weekly for heatmaps

3. **Obstacle Count**
   - Limit to significant obstacles
   - Combine similar obstacles
   - Remove distant obstacles (> 100m)

## Integration Examples

### With Solar Calculator

```python
# Get solar system configuration
solar_config = solar_service.calculate(request)

# Perform shading analysis
shading_request = ShadingAnalysisRequest(
    location=solar_config.location,
    obstacles=detected_obstacles,
    module_tilt=solar_config.optimal_tilt,
    module_azimuth=solar_config.optimal_azimuth,
    module_area=solar_config.total_module_area,
    ...
)

result = shading_service.analyze_shading(shading_request)

# Adjust production estimate
adjusted_production = (
    solar_config.annual_production * 
    (1 - result.losses.total_annual_loss_percent / 100)
)
```

### With 3D Visualization

```python
# Get 3D model data
model_3d = visualization_service.generate_model(project_id)

# Extract obstacles from 3D model
obstacles = extract_obstacles_from_3d(model_3d)

# Perform shading analysis
result = shading_service.analyze_shading(
    ShadingAnalysisRequest(
        obstacles=obstacles,
        ...
    )
)

# Overlay shading data on 3D model
enhanced_model = overlay_shading_data(model_3d, result)
```

### With PDF Generation

```python
# Perform analysis
shading_result = shading_service.analyze_shading(request)

# Generate PDF with shading data
pdf_data = {
    'shading_loss': shading_result.losses.total_annual_loss_percent,
    'monthly_losses': shading_result.losses.monthly_losses,
    'suggestions': shading_result.suggestions,
    'visualizations': shading_result.visualization
}

pdf = pdf_service.generate(template='solar_analysis', data=pdf_data)
```

## References

### Astronomical Calculations
- NOAA Solar Calculator
- Astronomical Algorithms by Jean Meeus
- PVLib Python library

### Shading Models
- Perez Sky Model
- Hay-Davies Model
- Reindl Model

### Standards
- IEC 61724: Photovoltaic system performance monitoring
- IEC 61853: PV module performance testing
- DIN EN 62446: Grid connected PV systems

## Support

For issues or questions:
- Check the demo script: `demo_shading_analysis.py`
- Review test cases: `tests/test_shading_analysis_service.py`
- Consult API documentation: `/api/v1/docs`
- Contact: support@solar-calculator-pro.com
