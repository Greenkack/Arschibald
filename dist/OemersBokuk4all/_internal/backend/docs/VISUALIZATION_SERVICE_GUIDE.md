# 3D Visualization Service Guide

## Overview

The 3D Visualization Service provides comprehensive functionality for generating, manipulating, and exporting 3D models of photovoltaic (PV) systems on buildings. This service wraps the existing `pv3d.py` and related utility modules to provide a clean API interface.

## Features

- **3D Model Generation**: Create complete 3D models of buildings with PV modules
- **Automatic Placement**: Intelligent module placement algorithms
- **Manual Placement**: Validate and process manually specified positions
- **Collision Detection**: Detect overlaps and boundary violations
- **Multiple Export Formats**: STL, OBJ, GLTF, GLB
- **Multi-View Export**: Generate images from different angles
- **360° Animation**: Create rotating animations for presentations

## Architecture

```
VisualizationService
├── 3D Model Generation
│   ├── Building geometry
│   ├── Roof structure
│   └── Module placement
├── Placement Calculation
│   ├── Automatic optimization
│   └── Manual validation
├── Collision Detection
│   ├── Module overlaps
│   ├── Boundary violations
│   └── Clearance checks
└── Export Functions
    ├── 3D formats (STL, OBJ, GLTF)
    ├── Multi-view images
    └── 360° animations
```

## Installation

### Required Dependencies

```bash
# Core dependencies
pip install pyvista numpy

# Optional for advanced features
pip install plotly matplotlib pillow
```

### Verify Installation

```python
from backend.services.visualization_service import VisualizationService

service = VisualizationService()
if service.is_available():
    print("✓ 3D Visualization Service is ready!")
else:
    print("✗ Missing dependencies")
```

## Usage Examples

### 1. Generate 3D Model

```python
from backend.services.visualization_service import VisualizationService

service = VisualizationService()

# Define building
building_dims = {
    "length_m": 12.0,
    "width_m": 8.0,
    "wall_height_m": 6.0
}

# Define roof
roof_config = {
    "type": "gable",
    "angle": 35.0,
    "orientation": "south",
    "covering": "Ziegel"
}

# Define modules
module_config = {
    "count": 24,
    "type": "standard",
    "spacing": 0.02,
    "margin": 0.5
}

# Generate model
result = service.generate_3d_model(
    building_dims=building_dims,
    roof_config=roof_config,
    module_config=module_config,
    placement_mode="auto"
)

print(f"Modules placed: {len(result['module_positions'])}")
print(f"Roof coverage: {result['statistics']['roof_coverage_percent']}%")
```

### 2. Calculate Automatic Placement

```python
positions = service.calculate_auto_placement(
    building_dims=building_dims,
    roof_config=roof_config,
    module_config=module_config
)

for pos in positions[:5]:  # First 5 modules
    print(f"Module {pos['index']}: "
          f"x={pos['x']:.2f}m, y={pos['y']:.2f}m, z={pos['z']:.2f}m")
```

### 3. Validate Manual Placement

```python
manual_positions = [
    {"index": 0, "x": 1.0, "y": 1.0, "azimuth": 0.0},
    {"index": 1, "x": 2.5, "y": 1.0, "azimuth": 0.0},
    {"index": 2, "x": 4.0, "y": 1.0, "azimuth": 0.0}
]

validated = service.calculate_manual_placement(
    positions=manual_positions,
    building_dims=building_dims,
    roof_config=roof_config
)

# Z and tilt are automatically calculated
for pos in validated:
    print(f"Module {pos['index']}: z={pos['z']:.2f}m, tilt={pos['tilt']:.1f}°")
```

### 4. Detect Collisions

```python
collision_result = service.detect_collisions(
    module_positions=positions,
    building_dims=building_dims,
    roof_config=roof_config
)

if collision_result['has_collisions']:
    print(f"⚠ Found {len(collision_result['collisions'])} collisions:")
    for warning in collision_result['warnings']:
        print(f"  • {warning}")
else:
    print("✓ No collisions detected")
```

### 5. Export 3D Model

```python
# Export to STL
stl_data = service.export_3d_model(
    scene_data=result['scene_data'],
    format="stl",
    options={"binary": True}
)

# Save to file
with open("pv_system.stl", "wb") as f:
    f.write(stl_data)

# Export to GLTF
gltf_data = service.export_3d_model(
    scene_data=result['scene_data'],
    format="gltf",
    options={"embed_textures": True}
)
```

### 6. Export Multiple Views

```python
views = service.export_multi_view(
    scene_data=result['scene_data'],
    views=["front", "side", "top", "perspective"],
    options={"resolution": (1920, 1080)}
)

for view_name, image_data in views.items():
    with open(f"pv_system_{view_name}.png", "wb") as f:
        f.write(image_data)
```

### 7. Create 360° Animation

```python
animation = service.create_360_animation(
    scene_data=result['scene_data'],
    options={
        "frames": 36,
        "duration": 3.6,
        "format": "gif"
    }
)

with open("pv_system_360.gif", "wb") as f:
    f.write(animation)
```

## API Endpoints

### Health Check

```http
GET /api/v1/visualization/health
```

**Response:**
```json
{
  "available": true,
  "version": "1.0.0",
  "supported_formats": ["stl", "obj", "gltf", "glb"],
  "supported_roof_types": ["flat", "gable", "hip", "shed", "mansard"],
  "message": "3D visualization service is operational"
}
```

### Generate 3D Model

```http
POST /api/v1/visualization/generate
```

**Request Body:**
```json
{
  "building_dims": {
    "length_m": 12.0,
    "width_m": 8.0,
    "wall_height_m": 6.0
  },
  "roof_config": {
    "type": "gable",
    "angle": 35.0,
    "orientation": "south",
    "covering": "Ziegel"
  },
  "module_config": {
    "count": 24,
    "type": "standard",
    "spacing": 0.02,
    "margin": 0.5
  },
  "placement_mode": "auto"
}
```

**Response:**
```json
{
  "scene_data": {...},
  "module_positions": [...],
  "statistics": {
    "total_modules": 24,
    "total_area_m2": 44.35,
    "roof_coverage_percent": 46.2,
    "average_spacing_m": 0.52
  },
  "warnings": []
}
```

### Calculate Automatic Placement

```http
POST /api/v1/visualization/placement/auto
```

### Validate Manual Placement

```http
POST /api/v1/visualization/placement/validate
```

### Detect Collisions

```http
POST /api/v1/visualization/collisions/detect
```

### Export 3D Model

```http
POST /api/v1/visualization/export/model
```

### Export Multi-View

```http
POST /api/v1/visualization/export/multi-view
```

### Create 360° Animation

```http
POST /api/v1/visualization/export/animation
```

## Configuration

### Module Dimensions

Default PV module dimensions (can be customized):
- Width: 1.05m
- Height: 1.76m
- Thickness: 0.04m

### Roof Types

Supported roof types:
- `flat`: Flat roof
- `gable`: Gable (saddle) roof
- `hip`: Hip roof
- `shed`: Shed (mono-pitch) roof
- `mansard`: Mansard roof

### Export Formats

Supported 3D formats:
- **STL**: Standard Tessellation Language (3D printing)
- **OBJ**: Wavefront OBJ (widely supported)
- **GLTF**: GL Transmission Format (web-friendly)
- **GLB**: Binary GLTF (compact)

## Error Handling

The service provides comprehensive error handling:

```python
try:
    result = service.generate_3d_model(...)
except RuntimeError as e:
    # Service not available
    print(f"Service error: {e}")
except ValueError as e:
    # Invalid parameters
    print(f"Validation error: {e}")
except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Optimization Tips

1. **Module Count**: Keep module count reasonable (<500) for real-time generation
2. **Export Resolution**: Use lower resolutions for previews, higher for final exports
3. **Animation Frames**: 36 frames is usually sufficient for smooth 360° rotation
4. **Caching**: Cache generated models when possible

### Memory Usage

Typical memory usage:
- Small model (20 modules): ~50MB
- Medium model (50 modules): ~100MB
- Large model (200 modules): ~300MB

## Troubleshooting

### Service Not Available

**Problem**: `service.is_available()` returns `False`

**Solution**:
```bash
pip install pyvista numpy
```

### Import Errors

**Problem**: `ImportError: No module named 'utils.pv3d'`

**Solution**: Ensure the project root is in Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Collision Detection Issues

**Problem**: False positives in collision detection

**Solution**: Adjust clearance parameters in module_config:
```python
module_config = {
    "spacing": 0.05,  # Increase spacing
    "margin": 1.0     # Increase margin
}
```

## Best Practices

1. **Always check availability** before using the service
2. **Validate input parameters** before calling service methods
3. **Handle errors gracefully** with try-except blocks
4. **Use appropriate export formats** for your use case
5. **Cache results** when generating multiple views of the same model
6. **Monitor memory usage** for large models

## Related Documentation

- [API Reference](./VISUALIZATION_API_REFERENCE.md)
- [3D Visualization Quick Reference](./VISUALIZATION_QUICK_REFERENCE.md)
- [Legacy pv3d.py Documentation](../../utils/pv3d_help.py)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the demo script: `backend/demo_visualization_service.py`
3. Run tests: `pytest backend/tests/test_visualization_service.py`
