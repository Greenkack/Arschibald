# 3D Advanced Features Quick Reference

## Quick Start

```python
from services.visualization_3d_advanced_features import (
    Visualization3DAdvancedFeatures,
    TimeOfDay,
    WeatherConditions
)
from datetime import datetime

# Initialize service
viz = Visualization3DAdvancedFeatures()

# Apply materials
scene = viz.apply_materials_to_scene(scene_data)

# Create lighting
time = TimeOfDay(hour=12, minute=0, date=datetime.now(), 
                 latitude=51.5, longitude=0.0, timezone_offset=0)
weather = WeatherConditions(cloud_coverage=0.2, sun_intensity=1.0,
                            ambient_light=0.5, fog_density=0.0,
                            precipitation="none", wind_speed_ms=2.0,
                            temperature_c=25.0)
lights = viz.create_lighting_setup(time, weather, "high")

# Create photorealistic render
render = viz.create_photorealistic_render(scene, time, weather)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/materials/apply` | POST | Apply PBR materials |
| `/materials/library` | GET | Get material list |
| `/lighting/setup` | POST | Create lighting |
| `/shadows/calculate` | POST | Calculate shadows |
| `/weather/effects` | POST | Create weather |
| `/sun-path/calculate` | POST | Calculate sun path |
| `/time/simulate` | POST | Simulate time |
| `/seasons/simulate` | POST | Simulate seasons |
| `/render/photorealistic` | POST | Create render config |
| `/presets/weather` | GET | Get weather presets |

## Material Types

- `pv_module_glass` - PV panel glass
- `pv_module_frame` - Aluminum frame
- `roof_tile_clay` - Clay roof tiles
- `roof_metal` - Metal roofing
- `roof_shingle` - Asphalt shingles
- `mounting_rail` - Mounting system
- `ground` - Ground/grass
- `sky` - Sky dome

## Quality Levels

| Quality | Samples | Shadows | AO | Render Time |
|---------|---------|---------|-----|-------------|
| low | 32 | Basic | No | Fast |
| medium | 64 | Good | No | Medium |
| high | 128 | Excellent | Yes | Slow |
| ultra | 256+ | Perfect | Yes | Very Slow |

## Weather Presets

- `clear_sunny` - Perfect sunny day
- `partly_cloudy` - Mixed conditions
- `overcast` - Fully cloudy
- `rainy` - Rain with clouds
- `foggy` - Dense fog

## Time of Day Colors

| Time | Sky Color (RGB) |
|------|----------------|
| Night | (0.05, 0.05, 0.15) |
| Dawn | (0.8, 0.4, 0.2) |
| Day | (0.5, 0.7, 1.0) |
| Dusk | (0.8, 0.4, 0.2) |

## Seasonal Ground Colors

| Season | Ground Color (RGB) |
|--------|-------------------|
| Spring | (0.3, 0.6, 0.2) |
| Summer | (0.3, 0.5, 0.2) |
| Autumn | (0.6, 0.4, 0.2) |
| Winter | (0.8, 0.8, 0.85) |

## Common Parameters

### TimeOfDay
```python
TimeOfDay(
    hour=12,              # 0-23
    minute=0,             # 0-59
    date=datetime.now(),  # Date object
    latitude=51.5,        # -90 to 90
    longitude=0.0,        # -180 to 180
    timezone_offset=0     # -12 to 14
)
```

### WeatherConditions
```python
WeatherConditions(
    cloud_coverage=0.2,    # 0-1
    sun_intensity=1.0,     # 0-1
    ambient_light=0.5,     # 0-1
    fog_density=0.0,       # 0-1
    precipitation="none",  # "none", "rain", "snow"
    wind_speed_ms=2.0,     # m/s
    temperature_c=25.0     # Celsius
)
```

### Render Settings
```python
{
    "quality": "high",           # low, medium, high, ultra
    "samples": 128,              # 32-512
    "max_bounces": 8,            # 4-12
    "resolution": [1920, 1080],  # [width, height]
    "denoise": True,             # True/False
    "bloom": True,               # True/False
    "tone_mapping": "aces",      # aces, reinhard, filmic
    "exposure": 1.0              # 0.1-10.0
}
```

## Performance Tips

1. Use `quality="medium"` for previews
2. Reduce `samples` for faster renders
3. Lower `resolution` for testing
4. Disable `bloom` and post-processing
5. Use cached sun paths
6. Limit time simulation steps

## Error Handling

```python
try:
    render = viz.create_photorealistic_render(...)
except Exception as e:
    logger.error(f"Render failed: {e}")
    # Fallback to lower quality
    render = viz.create_photorealistic_render(
        ..., render_settings={"quality": "low"}
    )
```

## Task: 134
## Requirements: 1.3, 6.1
