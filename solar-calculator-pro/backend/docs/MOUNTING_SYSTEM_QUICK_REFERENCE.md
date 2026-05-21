# 3D Mounting System Visualization - Quick Reference

## Quick Start

```python
from services.mounting_system_service import MountingSystemService, MountingType, RailOrientation

service = MountingSystemService()
visualization = service.create_complete_visualization(
    module_positions=[...],
    mounting_type=MountingType.PITCHED_ROOF,
    rail_orientation=RailOrientation.HORIZONTAL,
    roof_angle=30.0,
    inverter_position=(5.0, 0.5, 0.0)
)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mounting-system/rails` | POST | Generate mounting rails |
| `/mounting-system/clamps` | POST | Generate mounting clamps |
| `/mounting-system/penetrations` | POST | Generate roof penetrations |
| `/mounting-system/cable-routing` | POST | Generate cable routes |
| `/mounting-system/complete` | POST | Complete system (all-in-one) |
| `/mounting-system/component-prices` | GET | Get current prices |
| `/mounting-system/mounting-types` | GET | List mounting types |

## Mounting Types

- `flat_roof` - Ballast system, no penetrations
- `pitched_roof` - Hook penetrations, waterproofing required
- `ground_mount` - Ground anchors
- `facade` - Wall anchors, vertical installation

## Rail Orientations

- `horizontal` - Rails parallel to ground (landscape modules)
- `vertical` - Rails perpendicular to ground (portrait modules)

## Clamp Types

- `end_clamp` - At array edges
- `mid_clamp` - Between modules
- `corner_clamp` - At corners

## Penetration Types

- `hook` - Pitched roof attachment
- `anchor` - Ground/wall anchor
- `ballast` - Flat roof (no penetration)
- `none` - No penetration required

## Component Prices (EUR)

| Component | Price |
|-----------|-------|
| Rail (per meter) | €12.50 |
| End Clamp | €3.50 |
| Mid Clamp | €2.80 |
| Hook Penetration | €8.50 |
| DC Cable (per meter) | €2.50 |
| AC Cable (per meter) | €3.20 |

## Response Structure

```json
{
  "rails": [...],
  "clamps": [...],
  "penetrations": [...],
  "cable_routes": [...],
  "bom": [
    {
      "item_id": "BOM_001",
      "description": "Mounting Rails (Aluminum)",
      "quantity": 21,
      "unit": "meter",
      "unit_price": 12.50,
      "total_price": 262.50,
      "category": "Mounting Structure"
    }
  ],
  "total_cost": 1250.75,
  "summary": {
    "total_rails": 4,
    "total_clamps": 24,
    "total_penetrations": 12,
    "total_cable_routes": 3,
    "total_bom_items": 8,
    "total_rail_length": 21.0,
    "total_dc_cable_length": 45.5,
    "total_ac_cable_length": 10.0
  }
}
```

## Common Patterns

### Generate Complete System
```http
POST /api/v1/mounting-system/complete
Content-Type: application/json

{
  "module_positions": [...],
  "mounting_type": "pitched_roof",
  "rail_orientation": "horizontal",
  "roof_angle": 30.0,
  "inverter_position": {"x": 5.0, "y": 0.5, "z": 0.0}
}
```

### Get Component Prices
```http
GET /api/v1/mounting-system/component-prices
```

### List Available Options
```http
GET /api/v1/mounting-system/mounting-types
GET /api/v1/mounting-system/rail-orientations
GET /api/v1/mounting-system/clamp-types
GET /api/v1/mounting-system/penetration-types
```

## Module Position Format

```json
{
  "id": "module_1",
  "position": {"x": 0.0, "y": 0.0, "z": 0.0},
  "width": 1.6,
  "height": 1.0,
  "orientation": "landscape"
}
```

## Error Codes

- `400` - Invalid input (check mounting_type, rail_orientation)
- `500` - Server error (check logs)

## Testing

```bash
# Run tests
pytest backend/tests/test_mounting_system_service.py -v

# Run specific test
pytest backend/tests/test_mounting_system_service.py::TestMountingRailGeneration -v
```

## Key Features

✅ Automatic rail generation  
✅ Intelligent clamp placement  
✅ Roof penetration calculation  
✅ Cable routing optimization  
✅ Complete BOM generation  
✅ Automatic cost calculation  
✅ Support for 4 mounting types  
✅ Horizontal and vertical orientations  
✅ German number formatting ready  

## Requirements

- Python 3.10+
- FastAPI
- Pydantic
- Math library (standard)

## See Also

- [Complete Guide](MOUNTING_SYSTEM_GUIDE.md)
- [API Documentation](/docs)
- [Test Suite](../tests/test_mounting_system_service.py)
