# 3D Visualization Advanced Service - Complete Guide

## Overview

The Advanced 3D Visualization Service provides comprehensive 3D modeling capabilities for PV systems, including automatic placement, collision detection, mounting system calculations, and multi-view exports.

## Features

### 1. Complete 3D Model Generation
- Realistic 3D rendering with materials and lighting
- Support for all roof types (flat, gable, hip, shed)
- Automatic roof type detection
- Customizable rendering options

### 2. Collision Detection Algorithms
- Module-to-module overlap detection
- Boundary violation detection
- Clearance validation
- Severity classification (none, warning, critical)
- Actionable recommendations

### 3. Automatic Module Placement
- Grid-based optimization
- Constraint-based placement
- Multiple optimization goals:
  - Maximum module count
  - Maximum power output
  - Aesthetic arrangement
- Shading avoidance

### 4. Manual Placement with Constraints
- Position validation
- Constraint checking
- Real-time feedback
- Automatic Z-position calculation

### 5. Roof Type Detection
- Automatic detection from dimensions
- Confidence scoring
- Parameter calculation
- Usable area estimation

### 6. Mounting System Calculations
- Rail and clamp count
- Weight calculations
- Bill of Materials (BOM)
- Cost estimation
- Installation time estimation

### 7. Multi-View Export
- Front, side, top, perspective views
- Customizable resolution
- Multiple formats (PNG, JPG, SVG)
- Batch export

### 8. Animation Generation
- 360-degree rotation
- Assembly animation
- Flythrough animation
- Exploded view
- Presentation-quality output

## API Endpoints

### Generate Complete 3D Model

```http
POST /api/v1/visualization/advanced/generate-complete-model
```

**Request Body:**
```json
{
  "building_dims": {
    "length_m": 10.0,
    "width_m": 6.0,
    "wall_height_m": 6.0
  },
  "roof_config": {
    "type": "auto",
    "angle": 15.0,
    "orientation": "south"
  },
  "module_config": {
    "count": 20,
    "module_power_w": 400,
    "module_weight_kg": 20.0,
    "module_efficiency": 0.20,
    "min_spacing": 0.02,
    "min_edge_distance": 0.5,
    "avoid_shading": true,
    "optimize_for": "max_modules"
  },
  "placement_mode": "auto",
  "rendering_options": {
    "show_mounting": true,
    "show_labels": false,
    "color_scheme": "default",
    "lighting": "realistic"
  }
}
```

**Response:**
```json
{
  "scene_data": { ... },
  "module_positions": [ ... ],
  "collision_result": {
    "has_collisions": false,
    "collision_count": 0,
    "collisions": [],
    "severity": "none",
    "recommendations": ["Module placement is optimal with no collisions"]
  },
  "mounting_result": {
    "rail_count": 40,
    "clamp_count": 80,
    "total_weight_kg": 450.0,
    "cost_estimate": 1200.0,
    "bom": [ ... ],
    "installation_time_hours": 7.0
  },
  "statistics": {
    "total_modules": 20,
    "total_area_m2": 36.96,
    "total_power_kw": 8.0,
    "roof_coverage_percent": 61.6,
    "average_spacing_m": 0.05,
    "total_weight_kg": 450.0,
    "installation_time_hours": 7.0
  },
  "metadata": {
    "placement_mode": "auto",
    "roof_type": "flat",
    "total_modules": 20,
    "generation_timestamp": "2024-01-15T10:30:00"
  }
}
```

### Detect Roof Type

```http
POST /api/v1/visualization/advanced/detect-roof-type
```

**Request Body:**
```json
{
  "building_dims": {
    "length_m": 10.0,
    "width_m": 6.0,
    "wall_height_m": 6.0
  },
  "roof_hints": {
    "has_ridge": true,
    "symmetrical": true
  }
}
```

**Response:**
```json
{
  "roof_type": "gable",
  "confidence": 0.85,
  "angle_deg": 30.0,
  "orientation": "south",
  "area_m2": 70.0,
  "usable_area_m2": 56.0,
  "parameters": {
    "ridge_height_m": 3.0,
    "eave_height_m": 6.0
  }
}
```

### Detect Collisions

```http
POST /api/v1/visualization/advanced/detect-collisions?tolerance=0.01
```

**Request Body:**
```json
{
  "module_positions": [
    {"x": 1.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
    {"x": 2.1, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15}
  ],
  "building_dims": {
    "length_m": 10.0,
    "width_m": 6.0,
    "wall_height_m": 6.0
  },
  "roof_config": {
    "type": "flat",
    "angle": 0.0,
    "orientation": "south"
  }
}
```

**Response:**
```json
{
  "has_collisions": false,
  "collision_count": 0,
  "collisions": [],
  "severity": "none",
  "recommendations": ["Module placement is optimal with no collisions"]
}
```

### Calculate Automatic Placement

```http
POST /api/v1/visualization/advanced/calculate-automatic-placement
```

**Response:**
```json
{
  "positions": [
    {
      "index": 0,
      "x": 1.0,
      "y": 1.0,
      "z": 6.0,
      "azimuth": 0.0,
      "tilt": 15.0,
      "power_w": 400,
      "efficiency": 0.20
    }
  ],
  "count": 20
}
```

### Calculate Mounting System

```http
POST /api/v1/visualization/advanced/calculate-mounting-system
```

**Response:**
```json
{
  "rail_count": 40,
  "clamp_count": 80,
  "total_weight_kg": 450.0,
  "cost_estimate": 1200.0,
  "bom": [
    {
      "item": "Mounting Rail 4m",
      "quantity": 40,
      "unit_price": 25.0,
      "total_price": 1000.0
    },
    {
      "item": "Module Clamp",
      "quantity": 80,
      "unit_price": 2.5,
      "total_price": 200.0
    }
  ],
  "installation_time_hours": 7.0
}
```

### Export Multi-View

```http
POST /api/v1/visualization/advanced/export-multi-view
```

**Request Body:**
```json
{
  "scene_data": { ... },
  "views": ["front", "side", "top", "perspective"],
  "format": "png",
  "resolution": [1920, 1080]
}
```

**Response:**
```json
{
  "views": {
    "front": "base64_encoded_image_data...",
    "side": "base64_encoded_image_data...",
    "top": "base64_encoded_image_data...",
    "perspective": "base64_encoded_image_data..."
  },
  "format": "png",
  "resolution": [1920, 1080]
}
```

### Create 360 Animation

```http
POST /api/v1/visualization/advanced/create-360-animation
```

**Request Body:**
```json
{
  "scene_data": { ... },
  "frames": 60,
  "duration_seconds": 6.0,
  "format": "gif"
}
```

**Response:**
```json
{
  "animation": "base64_encoded_animation_data...",
  "format": "gif",
  "frames": 60,
  "duration_seconds": 6.0
}
```

### Create Presentation Animation

```http
POST /api/v1/visualization/advanced/create-presentation-animation
```

**Request Body:**
```json
{
  "scene_data": { ... },
  "animation_type": "assembly",
  "options": {
    "frames": 90,
    "duration": 9.0
  }
}
```

**Response:**
```json
{
  "animation": "base64_encoded_animation_data...",
  "animation_type": "assembly",
  "format": "gif"
}
```

## Usage Examples

### Python Example

```python
import requests
import base64

# Generate complete 3D model
response = requests.post(
    "http://localhost:8000/api/v1/visualization/advanced/generate-complete-model",
    json={
        "building_dims": {
            "length_m": 10.0,
            "width_m": 6.0,
            "wall_height_m": 6.0
        },
        "roof_config": {
            "type": "auto"
        },
        "module_config": {
            "count": 20,
            "module_power_w": 400
        },
        "placement_mode": "auto"
    }
)

result = response.json()
print(f"Generated {result['statistics']['total_modules']} modules")
print(f"Total power: {result['statistics']['total_power_kw']} kW")
print(f"Collisions: {result['collision_result']['collision_count']}")

# Export multi-view
views_response = requests.post(
    "http://localhost:8000/api/v1/visualization/advanced/export-multi-view",
    json={
        "scene_data": result["scene_data"],
        "views": ["front", "top"],
        "format": "png",
        "resolution": [1920, 1080]
    }
)

views = views_response.json()["views"]
for view_name, base64_data in views.items():
    image_data = base64.b64decode(base64_data)
    with open(f"{view_name}.png", "wb") as f:
        f.write(image_data)
```

### JavaScript Example

```javascript
// Generate complete 3D model
const response = await fetch(
  'http://localhost:8000/api/v1/visualization/advanced/generate-complete-model',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      building_dims: {
        length_m: 10.0,
        width_m: 6.0,
        wall_height_m: 6.0
      },
      roof_config: {
        type: 'auto'
      },
      module_config: {
        count: 20,
        module_power_w: 400
      },
      placement_mode: 'auto'
    })
  }
);

const result = await response.json();
console.log(`Generated ${result.statistics.total_modules} modules`);
console.log(`Total power: ${result.statistics.total_power_kw} kW`);

// Create 360 animation
const animResponse = await fetch(
  'http://localhost:8000/api/v1/visualization/advanced/create-360-animation',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scene_data: result.scene_data,
      frames: 60,
      duration_seconds: 6.0,
      format: 'gif'
    })
  }
);

const animResult = await animResponse.json();
// Display animation
const img = document.createElement('img');
img.src = `data:image/gif;base64,${animResult.animation}`;
document.body.appendChild(img);
```

## Best Practices

### 1. Placement Optimization

- Use `optimize_for: "max_modules"` for maximum capacity
- Use `optimize_for: "max_power"` for highest power output
- Use `optimize_for: "aesthetics"` for visual appeal
- Always enable `avoid_shading: true` for optimal performance

### 2. Collision Detection

- Run collision detection after any placement changes
- Address critical collisions before proceeding
- Use recommendations to improve placement

### 3. Mounting System

- Calculate mounting system early for accurate cost estimates
- Review BOM for material planning
- Use installation time for project scheduling

### 4. Multi-View Export

- Export all views for comprehensive documentation
- Use high resolution (1920x1080 or higher) for presentations
- Choose PNG for quality, JPG for smaller file size

### 5. Animations

- Use 360 animation for quick overviews
- Use assembly animation for installation planning
- Use flythrough for impressive presentations
- Keep frame count reasonable (60-120) for file size

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: 3D visualization not available

Error responses include detailed messages:

```json
{
  "detail": "Error message describing the issue"
}
```

## Performance Considerations

- Large module counts (>100) may take longer to process
- High-resolution exports require more memory
- Animations with many frames take longer to generate
- Use caching for repeated requests with same parameters

## Requirements

- Python 3.10+
- FastAPI
- All pv3d utility modules
- Plotly for 3D rendering
- NumPy for calculations

## Related Documentation

- [3D Visualization Service Guide](./VISUALIZATION_SERVICE_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Solar Calculator Guide](./SOLAR_CALCULATOR_GUIDE.md)
