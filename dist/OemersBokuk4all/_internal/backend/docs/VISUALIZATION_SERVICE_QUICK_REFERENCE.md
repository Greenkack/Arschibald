# 3D Visualization Service - Quick Reference

## Installation

```bash
pip install pyvista numpy plotly matplotlib pillow
```

## Basic Usage

```python
from backend.services.visualization_service import VisualizationService

service = VisualizationService()

# Check availability
if not service.is_available():
    print("3D modules not installed")
```

## Generate 3D Model

```python
result = service.generate_3d_model(
    building_dims={"length_m": 12.0, "width_m": 8.0, "wall_height_m": 6.0},
    roof_config={"type": "gable", "angle": 35.0, "orientation": "south"},
    module_config={"count": 24, "spacing": 0.02, "margin": 0.5},
    placement_mode="auto"
)
```

## Calculate Placement

```python
# Automatic
positions = service.calculate_auto_placement(
    building_dims={...},
    roof_config={...},
    module_config={...}
)

# Manual
validated = service.calculate_manual_placement(
    positions=[{"index": 0, "x": 1.0, "y": 1.0, "azimuth": 0.0}],
    building_dims={...},
    roof_config={...}
)
```

## Detect Collisions

```python
result = service.detect_collisions(
    module_positions=positions,
    building_dims={...},
    roof_config={...}
)

if result['has_collisions']:
    for warning in result['warnings']:
        print(warning)
```

## Export 3D Model

```python
# STL
stl_data = service.export_3d_model(
    scene_data=result['scene_data'],
    format="stl"
)

# GLTF
gltf_data = service.export_3d_model(
    scene_data=result['scene_data'],
    format="gltf"
)
```

## Export Views

```python
views = service.export_multi_view(
    scene_data=result['scene_data'],
    views=["front", "side", "top", "perspective"]
)
```

## Create Animation

```python
animation = service.create_360_animation(
    scene_data=result['scene_data'],
    options={"frames": 36, "duration": 3.6, "format": "gif"}
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/visualization/health` | GET | Check service availability |
| `/visualization/generate` | POST | Generate 3D model |
| `/visualization/placement/auto` | POST | Calculate automatic placement |
| `/visualization/placement/validate` | POST | Validate manual placement |
| `/visualization/collisions/detect` | POST | Detect collisions |
| `/visualization/export/model` | POST | Export 3D model |
| `/visualization/export/multi-view` | POST | Export multiple views |
| `/visualization/export/animation` | POST | Create 360° animation |

## Roof Types

- `flat` - Flat roof
- `gable` - Gable roof
- `hip` - Hip roof
- `shed` - Shed roof
- `mansard` - Mansard roof

## Export Formats

- `stl` - Standard Tessellation Language
- `obj` - Wavefront OBJ
- `gltf` - GL Transmission Format
- `glb` - Binary GLTF

## View Types

- `front` - Front elevation
- `side` - Side elevation
- `top` - Top view
- `perspective` - 3D perspective
- `isometric` - Isometric projection

## Common Parameters

### Building Dimensions
```python
{
    "length_m": 10.0,    # 0-100m
    "width_m": 6.0,      # 0-100m
    "wall_height_m": 6.0 # 0-50m
}
```

### Roof Configuration
```python
{
    "type": "gable",        # See roof types
    "angle": 30.0,          # 0-90°
    "orientation": "south", # north/south/east/west
    "covering": "Ziegel"    # Optional
}
```

### Module Configuration
```python
{
    "count": 20,      # 1-500
    "spacing": 0.02,  # 0-1.0m
    "margin": 0.5     # 0-5.0m
}
```

## Error Handling

```python
try:
    result = service.generate_3d_model(...)
except RuntimeError:
    # Service not available
    pass
except ValueError:
    # Invalid parameters
    pass
```

## Demo Script

```bash
python backend/demo_visualization_service.py
```

## Run Tests

```bash
pytest backend/tests/test_visualization_service.py -v
```
