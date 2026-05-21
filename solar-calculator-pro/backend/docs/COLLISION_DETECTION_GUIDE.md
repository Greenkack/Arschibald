# 3D Collision Detection Service - Complete Guide

## Overview

The Collision Detection Service provides comprehensive collision detection for 3D PV module placement in the Solar Calculator Pro application. It detects and reports various types of collisions and violations to ensure safe and optimal module placement.

## Features

### 1. Module-to-Module Collision Detection
Detects overlaps and intersections between PV modules.

**Capabilities:**
- Bounding box intersection testing
- Overlap volume calculation
- Overlap percentage reporting
- Distance measurement between module centers
- Automatic resolution suggestions

### 2. Module-to-Obstacle Collision Detection
Detects collisions with obstacles like chimneys, skylights, vents, antennas, etc.

**Supported Obstacle Types:**
- Chimney
- Skylight
- Vent
- Antenna
- Tree
- Building
- Custom obstacles

### 3. Boundary Detection
Validates that modules stay within defined roof boundaries.

**Checks:**
- Left/Right boundaries (X-axis)
- Front/Back boundaries (Y-axis)
- Top/Bottom boundaries (Z-axis)
- Multiple boundary violations per module

### 4. Overhang Detection
Detects modules that extend too far beyond roof edges.

**Features:**
- Configurable maximum overhang distance
- Edge-specific detection
- Severity levels (warning/critical)
- Distance-based suggestions

### 5. Clearance Validation
Ensures minimum spacing between modules for installation and maintenance.

**Features:**
- Configurable minimum clearance
- Pairwise distance calculation
- Clearance violation reporting
- Spacing increase suggestions

## API Endpoints

### POST /api/v1/collision-detection/module-collisions
Detect collisions between modules.

**Request:**
```json
{
  "module_positions": [
    {
      "x": 0.0,
      "y": 0.0,
      "z": 6.0,
      "azimuth": 0.0,
      "tilt": 30.0,
      "index": 0
    }
  ],
  "module_width": 1.05,
  "module_height": 1.76,
  "module_thickness": 0.04
}
```

**Response:**
```json
{
  "success": true,
  "collision_count": 1,
  "collisions": [
    {
      "collision_type": "module_overlap",
      "severity": "critical",
      "module_id": 0,
      "other_id": 1,
      "overlap_volume": 0.05,
      "overlap_percentage": 25.0,
      "distance": 0.5,
      "description": "Module 0 overlaps with module 1 by 25.0%",
      "suggestion": "Move one module horizontally by at least 1.07m",
      "position": [0.0, 0.0, 6.0]
    }
  ]
}
```

### POST /api/v1/collision-detection/obstacle-collisions
Detect collisions between modules and obstacles.

**Request:**
```json
{
  "module_positions": [...],
  "obstacles": [
    {
      "id": 1,
      "name": "Chimney",
      "obstacle_type": "chimney",
      "min_x": -0.5,
      "min_y": -0.5,
      "min_z": 5.5,
      "max_x": 0.5,
      "max_y": 0.5,
      "max_z": 7.0
    }
  ]
}
```

### POST /api/v1/collision-detection/boundary-violations
Detect modules exceeding roof boundaries.

**Request:**
```json
{
  "module_positions": [...],
  "roof_boundaries": {
    "min_x": -10.0,
    "max_x": 10.0,
    "min_y": -10.0,
    "max_y": 10.0,
    "min_z": 0.0,
    "max_z": 20.0
  }
}
```

### POST /api/v1/collision-detection/overhangs
Detect excessive module overhangs.

**Request:**
```json
{
  "module_positions": [...],
  "roof_edges": [
    {
      "position": [10.0, 0.0, 6.0],
      "normal": [1.0, 0.0, 0.0]
    }
  ],
  "max_overhang": 0.1
}
```

### POST /api/v1/collision-detection/clearance-validation
Validate minimum clearance between modules.

**Request:**
```json
{
  "module_positions": [...],
  "min_clearance": 0.02
}
```

### POST /api/v1/collision-detection/comprehensive
Perform all collision detection checks in one call.

**Request:**
```json
{
  "module_positions": [...],
  "roof_boundaries": {...},
  "obstacles": [...],
  "roof_edges": [...],
  "module_width": 1.05,
  "module_height": 1.76,
  "module_thickness": 0.04,
  "min_clearance": 0.02,
  "max_overhang": 0.1
}
```

**Response:**
```json
{
  "has_collisions": true,
  "total_collisions": 5,
  "collisions_by_type": {
    "module_overlap": [...],
    "boundary_violation": [...],
    "clearance_violation": [...]
  },
  "critical_count": 2,
  "warning_count": 3,
  "all_collisions": [...]
}
```

## Python Service Usage

### Basic Usage

```python
from backend.services.collision_detection_service import (
    CollisionDetectionService,
    Obstacle,
    BoundingBox
)

# Initialize service
service = CollisionDetectionService(
    module_width=1.05,
    module_height=1.76,
    module_thickness=0.04,
    min_clearance=0.02,
    max_overhang=0.1
)

# Define module positions
modules = [
    {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
    {"x": 2.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
]

# Detect module collisions
collisions = service.detect_module_collisions(modules)

for collision in collisions:
    print(f"{collision.description}")
    print(f"Suggestion: {collision.suggestion}")
```

### Comprehensive Detection

```python
# Define boundaries
boundaries = {
    "min_x": -10.0,
    "max_x": 10.0,
    "min_y": -10.0,
    "max_y": 10.0,
    "min_z": 0.0,
    "max_z": 20.0
}

# Define obstacles
obstacles = [
    Obstacle(
        id=1,
        name="Chimney",
        bbox=BoundingBox(-0.5, -0.5, 5.5, 0.5, 0.5, 7.0),
        obstacle_type="chimney"
    )
]

# Perform comprehensive detection
result = service.detect_all_collisions(
    module_positions=modules,
    roof_boundaries=boundaries,
    obstacles=obstacles
)

print(f"Total collisions: {result['total_collisions']}")
print(f"Critical: {result['critical_count']}, Warnings: {result['warning_count']}")

# Process by type
for collision_type, collisions in result['collisions_by_type'].items():
    print(f"\n{collision_type}: {len(collisions)} issues")
    for collision in collisions:
        print(f"  - {collision['description']}")
```

## Collision Types

### 1. module_overlap
**Severity:** Critical or Warning  
**Description:** Two modules physically overlap  
**Resolution:** Move modules apart

### 2. obstacle_collision
**Severity:** Critical  
**Description:** Module collides with an obstacle  
**Resolution:** Move module away from obstacle

### 3. boundary_violation
**Severity:** Critical  
**Description:** Module exceeds roof boundaries  
**Resolution:** Move module inward

### 4. overhang
**Severity:** Warning or Critical  
**Description:** Module extends too far beyond roof edge  
**Resolution:** Move module inward

### 5. clearance_violation
**Severity:** Warning  
**Description:** Insufficient spacing between modules  
**Resolution:** Increase spacing

## Configuration

### Module Dimensions
```python
service = CollisionDetectionService(
    module_width=1.05,      # meters
    module_height=1.76,     # meters
    module_thickness=0.04   # meters
)
```

### Clearance Settings
```python
service = CollisionDetectionService(
    min_clearance=0.02  # minimum 2cm between modules
)
```

### Overhang Settings
```python
service = CollisionDetectionService(
    max_overhang=0.1  # maximum 10cm overhang
)
```

## Best Practices

### 1. Always Check Comprehensively
Use the comprehensive detection endpoint for complete validation:
```python
result = service.detect_all_collisions(
    module_positions=modules,
    roof_boundaries=boundaries,
    obstacles=obstacles,
    roof_edges=roof_edges
)
```

### 2. Handle Severity Levels
Prioritize critical issues over warnings:
```python
if result['critical_count'] > 0:
    # Handle critical issues first
    critical = [c for c in result['all_collisions'] if c['severity'] == 'critical']
    for collision in critical:
        # Fix critical issues
        pass
```

### 3. Use Suggestions
Apply the provided resolution suggestions:
```python
for collision in collisions:
    print(f"Issue: {collision['description']}")
    print(f"Fix: {collision['suggestion']}")
```

### 4. Validate After Changes
Re-run collision detection after moving modules:
```python
# Move module
modules[0]['x'] += 1.0

# Re-validate
new_collisions = service.detect_module_collisions(modules)
```

## Performance Considerations

### Spatial Hashing
For large numbers of modules (>10), the service automatically uses spatial hashing to optimize collision detection from O(n²) to O(n) average case.

### Bounding Box Optimization
The service uses axis-aligned bounding boxes (AABB) for fast intersection testing before performing detailed collision analysis.

## Error Handling

### Invalid Input
```python
try:
    collisions = service.detect_module_collisions(modules)
except ValueError as e:
    print(f"Invalid input: {e}")
```

### Empty Module List
```python
# Returns empty list, no error
collisions = service.detect_module_collisions([])
assert len(collisions) == 0
```

## Integration with 3D Visualization

The collision detection service integrates seamlessly with the 3D visualization service:

```python
from backend.services.visualization_service import VisualizationService
from backend.services.collision_detection_service import CollisionDetectionService

# Generate 3D model
viz_service = VisualizationService()
model = viz_service.generate_3d_model(building_dims, roof_config, module_config)

# Detect collisions
collision_service = CollisionDetectionService()
result = collision_service.detect_all_collisions(
    module_positions=model['module_positions'],
    roof_boundaries=roof_boundaries
)

# Highlight collisions in 3D view
if result['has_collisions']:
    # Update 3D visualization to show collision warnings
    pass
```

## Testing

Run the test suite:
```bash
pytest solar-calculator-pro/backend/tests/test_collision_detection_service.py -v
```

## Requirements

- Python 3.10+
- FastAPI
- Pydantic
- Math library (standard)

## Related Services

- **VisualizationService**: 3D model generation and rendering
- **ModulePlacementService**: Automatic and manual module placement
- **SolarService**: Solar system calculations

## Support

For issues or questions about collision detection:
1. Check the test suite for usage examples
2. Review the API documentation
3. Consult the design document at `.kiro/specs/streamlit-to-electron-migration/design.md`
