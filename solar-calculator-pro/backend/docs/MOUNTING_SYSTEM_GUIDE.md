# 3D Mounting System Visualization Guide

## Overview

The 3D Mounting System Visualization service provides comprehensive tools for designing and visualizing solar panel mounting systems. This includes rail placement, clamp positioning, roof penetrations, cable routing, and complete Bill of Materials (BOM) generation with cost calculations.

## Features

### 1. Mounting Rail Visualization
- Automatic rail generation based on module layout
- Support for horizontal and vertical orientations
- Optimized rail lengths and positioning
- Material specifications (aluminum, steel)

### 2. Mounting Clamp Placement
- Intelligent clamp positioning at module edges
- Automatic clamp type selection (end, mid, corner)
- Torque specifications for installation
- Module-to-rail attachment mapping

### 3. Roof Penetration Visualization
- Penetration point calculation based on mounting type
- Support for hooks, anchors, and ballast systems
- Waterproofing requirements
- Load capacity specifications

### 4. Cable Routing Visualization
- DC string routing from modules to inverter
- AC routing from inverter to grid connection
- Automatic cable length calculation
- Cable type and diameter specifications

### 5. Bill of Materials (BOM) Generation
- Complete component list with quantities
- Unit and total pricing
- Component categorization
- Manufacturer and part number tracking

### 6. Cost Calculation
- Automatic total cost calculation
- Component-level pricing
- Labor cost estimation (optional)
- Price breakdown by category

## API Endpoints

### Generate Mounting Rails

```http
POST /api/v1/mounting-system/rails
```

**Request Body:**
```json
{
  "module_positions": [
    {
      "id": "module_1",
      "position": {"x": 0.0, "y": 0.0, "z": 0.0},
      "width": 1.6,
      "height": 1.0,
      "orientation": "landscape"
    }
  ],
  "mounting_type": "pitched_roof",
  "rail_orientation": "horizontal"
}
```

**Response:**
```json
[
  {
    "id": "rail_row0_top",
    "start_point": {"x": -0.1, "y": 0.3, "z": 0.0},
    "end_point": {"x": 5.1, "y": 0.3, "z": 0.0},
    "length": 5.2,
    "orientation": "horizontal",
    "material": "aluminum",
    "profile": "standard"
  }
]
```

### Generate Mounting Clamps

```http
POST /api/v1/mounting-system/clamps
```

**Request Body:**
```json
{
  "rails": [...],
  "module_positions": [...]
}
```

**Response:**
```json
[
  {
    "id": "clamp_0",
    "position": {"x": 0.8, "y": 0.3, "z": 0.0},
    "clamp_type": "end_clamp",
    "rail_id": "rail_row0_top",
    "module_id": "module_1",
    "torque_spec": 15.0
  }
]
```

### Generate Roof Penetrations

```http
POST /api/v1/mounting-system/penetrations
```

**Request Body:**
```json
{
  "rails": [...],
  "mounting_type": "pitched_roof",
  "roof_angle": 30.0
}
```

**Response:**
```json
[
  {
    "id": "penetration_0",
    "position": {"x": 1.0, "y": 0.3, "z": 0.0},
    "penetration_type": "hook",
    "rail_id": "rail_row0_top",
    "waterproofing": true,
    "load_capacity": 500.0
  }
]
```

### Generate Cable Routing

```http
POST /api/v1/mounting-system/cable-routing
```

**Request Body:**
```json
{
  "module_positions": [...],
  "inverter_position": {"x": 5.0, "y": 0.5, "z": 0.0},
  "mounting_type": "pitched_roof"
}
```

**Response:**
```json
[
  {
    "id": "dc_route_0",
    "waypoints": [
      {"x": 0.0, "y": 0.0, "z": 0.0},
      {"x": 1.7, "y": 0.0, "z": 0.0},
      {"x": 5.0, "y": 0.5, "z": 0.0}
    ],
    "cable_type": "DC",
    "diameter": 6.0,
    "length": 6.8
  }
]
```

### Create Complete Mounting System

```http
POST /api/v1/mounting-system/complete
```

**Request Body:**
```json
{
  "module_positions": [...],
  "mounting_type": "pitched_roof",
  "rail_orientation": "horizontal",
  "roof_angle": 30.0,
  "inverter_position": {"x": 5.0, "y": 0.5, "z": 0.0}
}
```

**Response:**
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
  "mounting_type": "pitched_roof",
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

## Mounting Types

### Pitched Roof
- **Penetration Type:** Hooks
- **Waterproofing:** Required
- **Typical Angle:** 15-45 degrees
- **Rail Orientation:** Usually horizontal

### Flat Roof
- **Penetration Type:** Ballast blocks
- **Waterproofing:** Not required (no penetration)
- **Typical Angle:** 0-15 degrees
- **Rail Orientation:** Horizontal or vertical

### Ground Mount
- **Penetration Type:** Ground anchors
- **Waterproofing:** Not applicable
- **Typical Angle:** Optimized for location
- **Rail Orientation:** Horizontal or vertical

### Facade
- **Penetration Type:** Wall anchors
- **Waterproofing:** Required
- **Typical Angle:** 90 degrees (vertical)
- **Rail Orientation:** Vertical

## Rail Orientations

### Horizontal
- Rails run parallel to ground/horizon
- Modules typically in landscape orientation
- Better for wide, shallow roofs
- Easier cable management

### Vertical
- Rails run perpendicular to ground
- Modules typically in portrait orientation
- Better for narrow, tall roofs
- More structural support

## Component Pricing

Default component prices (EUR):

| Component | Unit | Price |
|-----------|------|-------|
| Mounting Rail | per meter | €12.50 |
| End Clamp | piece | €3.50 |
| Mid Clamp | piece | €2.80 |
| Corner Clamp | piece | €4.20 |
| Hook Penetration | piece | €8.50 |
| Anchor Penetration | piece | €12.00 |
| Ballast Block | piece | €15.00 |
| DC Cable (6mm²) | per meter | €2.50 |
| AC Cable (10mm²) | per meter | €3.20 |
| Cable Tray | per meter | €8.00 |
| Junction Box | piece | €25.00 |
| MC4 Connector | piece | €1.50 |

## Usage Examples

### Python Example

```python
from services.mounting_system_service import (
    MountingSystemService,
    MountingType,
    RailOrientation
)

# Initialize service
service = MountingSystemService()

# Define module positions
module_positions = [
    {
        'id': 'module_1',
        'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'width': 1.6,
        'height': 1.0,
        'orientation': 'landscape'
    },
    # ... more modules
]

# Create complete visualization
visualization = service.create_complete_visualization(
    module_positions=module_positions,
    mounting_type=MountingType.PITCHED_ROOF,
    rail_orientation=RailOrientation.HORIZONTAL,
    roof_angle=30.0,
    inverter_position=(5.0, 0.5, 0.0)
)

# Access results
print(f"Total Rails: {len(visualization.rails)}")
print(f"Total Clamps: {len(visualization.clamps)}")
print(f"Total Cost: €{visualization.total_cost:,.2f}")

# Print BOM
for item in visualization.bom:
    print(f"{item.description}: {item.quantity} {item.unit} @ €{item.unit_price} = €{item.total_price}")
```

### JavaScript/TypeScript Example

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

async function createMountingSystem() {
  const request = {
    module_positions: [
      {
        id: 'module_1',
        position: { x: 0.0, y: 0.0, z: 0.0 },
        width: 1.6,
        height: 1.0,
        orientation: 'landscape'
      },
      // ... more modules
    ],
    mounting_type: 'pitched_roof',
    rail_orientation: 'horizontal',
    roof_angle: 30.0,
    inverter_position: { x: 5.0, y: 0.5, z: 0.0 }
  };

  const response = await axios.post(
    `${API_BASE}/mounting-system/complete`,
    request
  );

  const { rails, clamps, penetrations, cable_routes, bom, total_cost, summary } = response.data;

  console.log(`Total Rails: ${summary.total_rails}`);
  console.log(`Total Clamps: ${summary.total_clamps}`);
  console.log(`Total Cost: €${total_cost.toFixed(2)}`);

  return response.data;
}
```

## Best Practices

### 1. Module Positioning
- Ensure modules are properly spaced (typically 1-2cm gap)
- Maintain consistent orientation within rows/columns
- Consider roof obstacles and edges
- Account for maintenance access

### 2. Rail Selection
- Use horizontal rails for landscape modules
- Use vertical rails for portrait modules
- Ensure rails extend beyond module edges
- Consider wind and snow loads

### 3. Clamp Placement
- Use end clamps at array edges
- Use mid clamps between modules
- Maintain proper torque specifications
- Consider thermal expansion

### 4. Roof Penetrations
- Minimize penetration count
- Ensure proper waterproofing
- Distribute load evenly
- Follow manufacturer specifications

### 5. Cable Routing
- Minimize cable length
- Avoid sharp bends
- Protect from weather
- Follow electrical codes

## Troubleshooting

### Issue: No rails generated
**Solution:** Check that module_positions is not empty and contains valid position data.

### Issue: Clamps not aligning with modules
**Solution:** Verify that rail orientation matches module orientation and positions are correct.

### Issue: Incorrect penetration type
**Solution:** Ensure mounting_type is correctly specified (pitched_roof, flat_roof, ground_mount, facade).

### Issue: Cable routes too long
**Solution:** Optimize inverter position or adjust module string configuration.

### Issue: BOM costs seem incorrect
**Solution:** Verify component prices are up to date using GET /component-prices endpoint.

## Integration with 3D Visualization

The mounting system data can be integrated with 3D visualization libraries:

```typescript
import * as THREE from 'three';

function visualizeMountingSystem(mountingData) {
  const scene = new THREE.Scene();
  
  // Visualize rails
  mountingData.rails.forEach(rail => {
    const geometry = new THREE.BoxGeometry(
      rail.length, 0.05, 0.05
    );
    const material = new THREE.MeshStandardMaterial({ color: 0x888888 });
    const railMesh = new THREE.Mesh(geometry, material);
    
    railMesh.position.set(
      (rail.start_point.x + rail.end_point.x) / 2,
      (rail.start_point.y + rail.end_point.y) / 2,
      (rail.start_point.z + rail.end_point.z) / 2
    );
    
    scene.add(railMesh);
  });
  
  // Visualize clamps
  mountingData.clamps.forEach(clamp => {
    const geometry = new THREE.SphereGeometry(0.03);
    const material = new THREE.MeshStandardMaterial({ color: 0x444444 });
    const clampMesh = new THREE.Mesh(geometry, material);
    
    clampMesh.position.set(
      clamp.position.x,
      clamp.position.y,
      clamp.position.z
    );
    
    scene.add(clampMesh);
  });
  
  // Visualize cable routes
  mountingData.cable_routes.forEach(route => {
    const points = route.waypoints.map(wp => 
      new THREE.Vector3(wp.x, wp.y, wp.z)
    );
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ 
      color: route.cable_type === 'DC' ? 0xff0000 : 0x0000ff 
    });
    const line = new THREE.Line(geometry, material);
    
    scene.add(line);
  });
  
  return scene;
}
```

## Requirements Validation

This implementation satisfies:
- **Requirement 1.3:** Backend Service integration with 3D visualization
- **Requirement 6.1:** Modular code extraction and service architecture

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review test cases in `tests/test_mounting_system_service.py`
- Contact development team

## Version History

- **v1.0.0** - Initial implementation with complete mounting system visualization
