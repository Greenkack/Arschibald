# 3D Model Advanced Features Guide

## Overview

The 3D Model Advanced Features service provides photo-realistic rendering capabilities for solar PV system visualizations. This includes realistic materials, advanced lighting, weather effects, time-of-day simulation, seasonal visualization, and complete photo-realistic rendering.

**Task**: 134  
**Requirements**: 1.3, 6.1

## Features

### 1. Realistic Material Rendering (PBR)

Physical-Based Rendering (PBR) materials provide realistic surface properties:

- **PV Module Glass**: Dark blue-gray with high reflectivity
- **PV Module Frame**: Metallic aluminum with medium roughness
- **Roof Materials**: Clay tiles, metal, asphalt shingles
- **Mounting Rails**: Aluminum with metallic properties
- **Ground**: Grass with seasonal color variations
- **Sky**: Self-illuminated atmospheric rendering

**Material Properties**:
- Base Color (RGB)
- Metallic (0-1)
- Roughness (0-1)
- Reflectivity (0-1)
- Opacity (0-1)
- Emissive Color (RGB)

### 2. Lighting and Shadow Simulation

Advanced lighting system with multiple light sources:

**Light Types**:
- **Directional**: Sun light with accurate position calculation
- **Ambient**: Sky and ground bounce lighting
- **Point**: Fill lights for low-light conditions
- **Spot**: Focused lighting (optional)

**Shadow Features**:
- Real-time shadow mapping
- Cascade shadow maps for large scenes
- Soft shadows with configurable softness
- Ambient occlusion for contact shadows
- Quality levels: low, medium, high, ultra

### 3. Weather Visualization

Realistic weather effects:

**Cloud System**:
- Dynamic cloud coverage (0-100%)
- Volumetric clouds with thickness
- Animated cloud movement based on wind speed

**Fog Effects**:
- Distance-based fog density
- Atmospheric fog color
- Near/far plane configuration

**Precipitation**:
- Rain particles with velocity
- Snow particles with wind effect
- Configurable particle count and size

**Atmospheric Scattering**:
- Rayleigh scattering (blue sky)
- Mie scattering (haze, clouds)
- Realistic atmosphere thickness

### 4. Sun Path Visualization

Accurate solar position calculation:

- Based on date, time, latitude, and longitude
- Solar declination and hour angle
- Elevation and azimuth angles
- Full-day sun path with 15-minute intervals
- Visual arc showing sun trajectory
- Time labels at hourly intervals

### 5. Time-of-Day Simulation

Simulate scene across different times:

- Configurable time range (e.g., 6 AM to 6 PM)
- Multiple snapshots at regular intervals
- Dynamic sky colors (dawn, day, dusk, night)
- Automatic lighting adjustments
- Ambient color changes
- Weather effects at each time

**Sky Colors**:
- Night: Dark blue (0.05, 0.05, 0.15)
- Dawn/Dusk: Orange (0.8, 0.4, 0.2)
- Day: Sky blue (0.5, 0.7, 1.0)
- Cloudy: Gray (0.6, 0.6, 0.65)

### 6. Seasonal Visualization

Simulate all four seasons:

**Spring**:
- Fresh green ground color
- Moderate cloud coverage (40%)
- Medium sun intensity
- Light fog
- Temperature: 15°C

**Summer**:
- Darker green ground
- Low cloud coverage (20%)
- Maximum sun intensity
- Clear atmosphere
- Temperature: 25°C

**Autumn**:
- Brown/orange ground
- High cloud coverage (50%)
- Reduced sun intensity
- Moderate fog
- Temperature: 12°C

**Winter**:
- Snow white/gray ground
- High cloud coverage (60%)
- Low sun intensity
- Light fog
- Temperature: 2°C

### 7. Photo-Realistic Rendering

Complete render configuration:

**Camera Settings**:
- Position and target
- Field of view (FOV)
- Aspect ratio
- Depth of field with bokeh

**Render Settings**:
- Quality levels: low, medium, high, ultra
- Sample count (32-512)
- Max light bounces (4-8)
- Resolution (HD to 4K)
- Denoising
- Render time estimation

**Post-Processing**:
- Bloom effect
- Tone mapping (ACES, Reinhard, Filmic)
- Color grading (temperature, tint, saturation)
- Vignette
- Chromatic aberration
- Film grain (optional)

## API Endpoints

### Apply Materials

```http
POST /api/v1/visualization/3d/advanced/materials/apply
```

Apply PBR materials to scene objects.

**Request**:
```json
{
  "scene_data": {...},
  "material_mapping": {
    "pv_modules": "pv_module_glass",
    "roof": "roof_tile_clay",
    "mounting": "mounting_rail"
  }
}
```

### Get Material Library

```http
GET /api/v1/visualization/3d/advanced/materials/library
```

Get all available PBR materials.

### Create Lighting Setup

```http
POST /api/v1/visualization/3d/advanced/lighting/setup
```

Create complete lighting based on time and weather.

**Request**:
```json
{
  "time_of_day": {
    "hour": 12,
    "minute": 0,
    "date": "2024-06-21T00:00:00",
    "latitude": 51.5,
    "longitude": 0.0,
    "timezone_offset": 0
  },
  "weather": {
    "cloud_coverage": 0.2,
    "sun_intensity": 1.0,
    "ambient_light": 0.5,
    "fog_density": 0.0,
    "precipitation": "none",
    "wind_speed_ms": 2.0,
    "temperature_c": 25.0
  },
  "quality": "high"
}
```

### Calculate Shadows

```http
POST /api/v1/visualization/3d/advanced/shadows/calculate
```

Calculate shadow maps for the scene.

### Create Weather Effects

```http
POST /api/v1/visualization/3d/advanced/weather/effects
```

Create weather effects (clouds, fog, precipitation).

### Calculate Sun Path

```http
POST /api/v1/visualization/3d/advanced/sun-path/calculate
```

Calculate sun path for entire day.

**Request**:
```json
{
  "date": "2024-06-21",
  "latitude": 51.5,
  "longitude": 0.0,
  "timezone_offset": 0
}
```

### Simulate Time of Day

```http
POST /api/v1/visualization/3d/advanced/time/simulate
```

Simulate scene at different times of day.

**Request**:
```json
{
  "scene_data": {...},
  "start_time": {...},
  "duration_hours": 12.0,
  "steps": 24,
  "weather": {...}
}
```

### Simulate Seasons

```http
POST /api/v1/visualization/3d/advanced/seasons/simulate
```

Simulate scene across all four seasons.

**Request**:
```json
{
  "scene_data": {...},
  "latitude": 51.5,
  "longitude": 0.0,
  "year": 2024
}
```

### Create Photorealistic Render

```http
POST /api/v1/visualization/3d/advanced/render/photorealistic
```

Create complete photo-realistic render configuration.

**Request**:
```json
{
  "scene_data": {...},
  "time_of_day": {...},
  "weather": {...},
  "camera_config": {
    "position": [20.0, -30.0, 15.0],
    "target": [0.0, 0.0, 5.0],
    "fov": 45.0,
    "aspect_ratio": 1.777
  },
  "render_settings": {
    "quality": "ultra",
    "samples": 256,
    "max_bounces": 8,
    "resolution": [3840, 2160],
    "denoise": true,
    "bloom": true,
    "tone_mapping": "aces",
    "exposure": 1.0
  }
}
```

### Get Weather Presets

```http
GET /api/v1/visualization/3d/advanced/presets/weather
```

Get predefined weather configurations.

**Presets**:
- `clear_sunny`: Perfect sunny day
- `partly_cloudy`: Mixed sun and clouds
- `overcast`: Fully cloudy
- `rainy`: Rain with heavy clouds
- `foggy`: Dense fog

## Usage Examples

### Example 1: Basic Material Application

```python
from services.visualization_3d_advanced_features import Visualization3DAdvancedFeatures

viz = Visualization3DAdvancedFeatures()

scene_data = {
    "building": {...},
    "modules": [...]
}

# Apply materials
scene_with_materials = viz.apply_materials_to_scene(scene_data)
```

### Example 2: Time-of-Day Simulation

```python
from datetime import datetime

time_of_day = TimeOfDay(
    hour=12,
    minute=0,
    date=datetime(2024, 6, 21),
    latitude=51.5,
    longitude=0.0,
    timezone_offset=0
)

weather = WeatherConditions(
    cloud_coverage=0.2,
    sun_intensity=1.0,
    ambient_light=0.5,
    fog_density=0.0,
    precipitation="none",
    wind_speed_ms=2.0,
    temperature_c=25.0
)

# Simulate 12 hours with 24 snapshots
snapshots = viz.simulate_time_of_day(
    scene_data=scene_data,
    start_time=time_of_day,
    duration_hours=12.0,
    steps=24,
    weather=weather
)
```

### Example 3: Seasonal Comparison

```python
# Simulate all seasons
seasons = viz.simulate_seasons(
    scene_data=scene_data,
    location=(51.5, 0.0),  # London
    year=2024
)

# Access specific season
summer = seasons["summer"]
winter = seasons["winter"]

# Compare daylight hours
print(f"Summer daylight: {summer['daylight_hours']} hours")
print(f"Winter daylight: {winter['daylight_hours']} hours")
```

### Example 4: Photo-Realistic Render

```python
# Create complete render configuration
render_config = viz.create_photorealistic_render(
    scene_data=scene_data,
    time_of_day=time_of_day,
    weather=weather,
    camera_config={
        "position": (20.0, -30.0, 15.0),
        "target": (0.0, 0.0, 5.0),
        "fov": 45.0,
        "aspect_ratio": 16/9
    },
    render_settings={
        "quality": "ultra",
        "samples": 256,
        "resolution": (3840, 2160)
    }
)

# Estimate render time
print(f"Estimated render time: {render_config['metadata']['render_time_estimate_minutes']} minutes")
```

## Performance Considerations

### Quality vs. Performance

| Quality | Samples | Resolution | Render Time | Use Case |
|---------|---------|------------|-------------|----------|
| Low | 32 | 1280x720 | ~30s | Quick previews |
| Medium | 64 | 1920x1080 | ~2min | Standard renders |
| High | 128 | 1920x1080 | ~5min | High-quality renders |
| Ultra | 256+ | 3840x2160 | ~20min+ | Production renders |

### Optimization Tips

1. **Use appropriate quality**: Don't use "ultra" for previews
2. **Cache sun paths**: Sun path calculation is cached automatically
3. **Limit time steps**: Use fewer steps for faster simulation
4. **Reduce samples**: Lower sample count for faster renders
5. **Disable post-processing**: Turn off effects for previews

## Technical Details

### Sun Position Algorithm

The service uses the solar position algorithm based on:
- Solar declination angle
- Hour angle
- Latitude and longitude
- Date and time

Formula for solar elevation:
```
sin(elevation) = sin(latitude) * sin(declination) + 
                 cos(latitude) * cos(declination) * cos(hour_angle)
```

### Material Properties

PBR materials use the metallic-roughness workflow:
- **Metallic**: 0 = dielectric, 1 = metal
- **Roughness**: 0 = smooth/glossy, 1 = rough/matte
- **Reflectivity**: Fresnel reflection at normal incidence

### Shadow Mapping

Uses cascade shadow maps (CSM) for large scenes:
- Multiple shadow maps at different distances
- Reduces shadow aliasing
- Better shadow quality near camera

## Troubleshooting

### Issue: Shadows appear blocky

**Solution**: Increase shadow quality or resolution
```python
shadows = viz.calculate_shadows(scene_data, lights, quality="ultra")
```

### Issue: Render takes too long

**Solution**: Reduce quality settings
```python
render_settings = {
    "quality": "medium",
    "samples": 64,
    "resolution": (1920, 1080)
}
```

### Issue: Sky color looks wrong

**Solution**: Check time of day and weather settings
```python
# Ensure time is within daylight hours
time_of_day.hour = 12  # Noon
weather.cloud_coverage = 0.2  # Light clouds
```

## See Also

- [3D Visualization Guide](./VISUALIZATION_ADVANCED_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Performance Optimization](./BACKEND_PERFORMANCE_GUIDE.md)
