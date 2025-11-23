# 3D Export Formats - Quick Reference

## Supported Formats

| Format | Extension | Use Case | Binary |
|--------|-----------|----------|--------|
| STL | `.stl` | 3D Printing | Yes |
| OBJ | `.obj` | 3D Modeling | No |
| GLTF | `.gltf` | Web 3D (JSON) | No |
| GLB | `.glb` | Web 3D (Binary) | Yes |
| DXF | `.dxf` | CAD Software | No |
| PDF | `.pdf` | Documentation | Yes |
| PNG | `.png` | Images | Yes |
| JPG | `.jpg` | Images | Yes |

## Quick Start

### 1. Check Supported Formats
```bash
curl http://localhost:8000/api/v1/export-3d/formats
```

### 2. Export Model
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "stl",
    "building_dims": {"length_m": 10, "width_m": 6, "wall_height_m": 6},
    "roof_config": {"type": "gable", "angle": 30, "orientation": "south"},
    "module_config": {"count": 20}
  }' \
  --output model.stl
```

## Format Selection Guide

### For 3D Printing
```json
{"format": "stl"}
```

### For CAD Software
```json
{"format": "dxf", "options": {"version": "R2018"}}
```

### For Web Visualization
```json
{"format": "glb"}
```

### For Documentation
```json
{"format": "pdf", "options": {"image_quality": "high"}}
```

### For High-Quality Images
```json
{"format": "png", "options": {"width": 1920, "height": 1080, "scale": 2.0}}
```

## Common Options

### STL
```json
{"binary": true}
```

### OBJ
```json
{"include_mtl": true}
```

### GLTF/GLB
```json
{"binary": true, "compress": true}
```

### DXF
```json
{"version": "R2018", "units": "Meters"}
```

### PDF
```json
{"include_3d_data": true, "image_quality": "high"}
```

### PNG/JPG
```json
{"width": 1920, "height": 1080, "scale": 2.0, "quality": 95}
```

## Python Example

```python
import requests

# Export as STL
response = requests.post(
    "http://localhost:8000/api/v1/export-3d/export",
    json={
        "format": "stl",
        "building_dims": {
            "length_m": 10.0,
            "width_m": 6.0,
            "wall_height_m": 6.0
        },
        "roof_config": {
            "type": "gable",
            "angle": 30.0,
            "orientation": "south"
        },
        "module_config": {
            "count": 20
        }
    }
)

if response.status_code == 200:
    with open("model.stl", "wb") as f:
        f.write(response.content)
```

## JavaScript Example

```javascript
// Export as GLB
const response = await fetch('http://localhost:8000/api/v1/export-3d/export', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    format: 'glb',
    building_dims: {
      length_m: 10.0,
      width_m: 6.0,
      wall_height_m: 6.0
    },
    roof_config: {
      type: 'gable',
      angle: 30.0,
      orientation: 'south'
    },
    module_config: {
      count: 20
    }
  })
});

if (response.ok) {
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'model.glb';
  a.click();
}
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | File downloaded |
| 400 | Bad Request | Check format and parameters |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Check server logs |

## File Size Estimates

| Format | Typical Size | Notes |
|--------|--------------|-------|
| STL | 1-5 MB | Binary format |
| OBJ | 2-8 MB | Text format |
| GLTF | 1-3 MB | JSON format |
| GLB | 0.5-2 MB | Compressed binary |
| DXF | 0.5-2 MB | Text format |
| PDF | 2-10 MB | With embedded image |
| PNG | 0.5-3 MB | Lossless |
| JPG | 0.2-1 MB | Compressed |

## Dependencies

```bash
pip install trimesh ezdxf reportlab Pillow plotly
```

## See Also

- Full Guide: `3D_EXPORT_FORMATS_GUIDE.md`
- API Documentation: `/docs`
- Demo Script: `backend/demo_export_3d.py`
