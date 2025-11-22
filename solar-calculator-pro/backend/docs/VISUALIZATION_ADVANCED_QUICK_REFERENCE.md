# 3D Visualization Advanced Service - Quick Reference

## Quick Start

```python
from backend.services.visualization_advanced_service import VisualizationAdvancedService

# Initialize service
viz = VisualizationAdvancedService()

# Generate complete 3D model
result = viz.generate_complete_3d_model(
    building_dims={"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0},
    roof_config={"type": "auto"},
    module_config={"count": 20, "module_power_w": 400},
    placement_mode="auto"
)
```

## Key Features

| Feature | Method | Description |
|---------|--------|-------------|
| Complete Model | `generate_complete_3d_model()` | Full 3D model with all features |
| Collision Detection | `detect_collisions_advanced()` | Advanced collision analysis |
| Auto Placement | `calculate_automatic_placement()` | Optimized module placement |
| Manual Validation | `validate_manual_placement()` | Validate manual positions |
| Roof Detection | `detect_roof_type()` | Automatic roof type detection |
| Mounting System | `calculate_mounting_system()` | BOM and cost calculation |
| Multi-View Export | `export_multi_view()` | Export multiple views |
| 360 Animation | `create_360_animation()` | Rotation animation |
| Presentation | `create_presentation_animation()` | Assembly/flythrough/exploded |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate-complete-model` | POST | Generate full 3D model |
| `/detect-roof-type` | POST | Detect roof type |
| `/detect-collisions` | POST | Check for collisions |
| `/calculate-automatic-placement` | POST | Auto-place modules |
| `/validate-manual-placement` | POST | Validate positions |
| `/calculate-mounting-system` | POST | Calculate mounting |
| `/export-multi-view` | POST | Export views |
| `/create-360-animation` | POST | Create rotation |
| `/create-presentation-animation` | POST | Create presentation |
| `/health` | GET | Service status |

## Common Parameters

### Building Dimensions
```json
{
  "length_m": 10.0,
  "width_m": 6.0,
  "wall_height_m": 6.0
}
```

### Roof Configuration
```json
{
  "type": "auto",  // or "flat", "gable", "hip"
  "angle": 15.0,
  "orientation": "south"
}
```

### Module Configuration
```json
{
  "count": 20,
  "module_power_w": 400,
  "module_weight_kg": 20.0,
  "min_spacing": 0.02,
  "min_edge_distance": 0.5,
  "optimize_for": "max_modules"
}
```

## Optimization Goals

- `max_modules`: Maximum number of modules
- `max_power`: Maximum power output
- `aesthetics`: Visual appeal

## Collision Severity

- `none`: No collisions
- `warning`: Minor issues
- `critical`: Must be fixed

## Animation Types

- `assembly`: Modules being placed
- `flythrough`: Camera movement
- `exploded`: Component breakdown
- `360`: Rotation animation

## Export Formats

- Images: `png`, `jpg`, `svg`
- 3D Models: `stl`, `obj`, `gltf`, `glb`
- Animations: `gif`, `mp4`

## Views

- `front`: Front view
- `side`: Side view
- `top`: Top-down view
- `perspective`: 3D perspective

## Response Structure

```json
{
  "scene_data": { ... },
  "module_positions": [ ... ],
  "collision_result": {
    "has_collisions": false,
    "severity": "none",
    "recommendations": [ ... ]
  },
  "mounting_result": {
    "rail_count": 40,
    "clamp_count": 80,
    "bom": [ ... ]
  },
  "statistics": {
    "total_modules": 20,
    "total_power_kw": 8.0,
    "roof_coverage_percent": 61.6
  }
}
```

## Error Codes

- `200`: Success
- `400`: Invalid input
- `500`: Server error
- `503`: Service unavailable

## Performance Tips

1. Use auto placement for speed
2. Limit animation frames (60-120)
3. Use reasonable resolutions
4. Cache repeated requests
5. Process large models in batches

## Common Use Cases

### 1. Quick Model Generation
```python
result = viz.generate_complete_3d_model(
    building_dims=dims,
    roof_config={"type": "auto"},
    module_config={"count": 20},
    placement_mode="auto"
)
```

### 2. Collision Check
```python
collisions = viz.detect_collisions_advanced(
    module_positions=positions,
    building_dims=dims,
    roof_config=roof
)
```

### 3. Export Views
```python
views = viz.export_multi_view(
    scene_data=scene,
    views=["front", "top"],
    format="png"
)
```

### 4. Create Animation
```python
animation = viz.create_360_animation(
    scene_data=scene,
    frames=60,
    duration_seconds=6.0
)
```

## Requirements

- Python 3.10+
- FastAPI
- pv3d modules
- Plotly
- NumPy

## See Also

- [Complete Guide](./VISUALIZATION_ADVANCED_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Examples](../examples/)
