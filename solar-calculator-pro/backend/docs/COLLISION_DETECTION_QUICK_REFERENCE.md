# Collision Detection Service - Quick Reference

## Quick Start

```python
from backend.services.collision_detection_service import CollisionDetectionService

service = CollisionDetectionService()
modules = [
    {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
    {"x": 2.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
]
collisions = service.detect_module_collisions(modules)
```

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/collision-detection/module-collisions` | Module-to-module collisions |
| `/collision-detection/obstacle-collisions` | Module-to-obstacle collisions |
| `/collision-detection/boundary-violations` | Boundary violations |
| `/collision-detection/overhangs` | Overhang detection |
| `/collision-detection/clearance-validation` | Clearance validation |
| `/collision-detection/comprehensive` | All checks in one call |

## Collision Types

| Type | Severity | Description |
|------|----------|-------------|
| `module_overlap` | Critical/Warning | Modules physically overlap |
| `obstacle_collision` | Critical | Module hits obstacle |
| `boundary_violation` | Critical | Module exceeds boundaries |
| `overhang` | Warning/Critical | Excessive overhang |
| `clearance_violation` | Warning | Insufficient spacing |

## Configuration

```python
service = CollisionDetectionService(
    module_width=1.05,          # meters
    module_height=1.76,         # meters
    module_thickness=0.04,      # meters
    min_clearance=0.02,         # meters
    max_overhang=0.1            # meters
)
```

## Common Patterns

### Comprehensive Check
```python
result = service.detect_all_collisions(
    module_positions=modules,
    roof_boundaries=boundaries,
    obstacles=obstacles,
    roof_edges=roof_edges
)
```

### Handle Results
```python
if result['has_collisions']:
    print(f"Found {result['total_collisions']} issues")
    print(f"Critical: {result['critical_count']}")
    print(f"Warnings: {result['warning_count']}")
    
    for collision in result['all_collisions']:
        print(f"{collision['description']}")
        print(f"Fix: {collision['suggestion']}")
```

### Filter by Severity
```python
critical = [c for c in result['all_collisions'] if c['severity'] == 'critical']
warnings = [c for c in result['all_collisions'] if c['severity'] == 'warning']
```

## Response Structure

```json
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
```

## Testing

```bash
# Run all tests
pytest solar-calculator-pro/backend/tests/test_collision_detection_service.py -v

# Run specific test
pytest solar-calculator-pro/backend/tests/test_collision_detection_service.py::TestCollisionDetectionService::test_detect_module_collisions_with_overlap -v
```

## Performance

- **Small datasets (<10 modules)**: O(n²) brute force
- **Large datasets (>10 modules)**: O(n) with spatial hashing
- **Typical response time**: <10ms for 50 modules

## Common Issues

### No Collisions Detected
- Check module positions are correct
- Verify module dimensions match actual modules
- Ensure boundaries are properly defined

### Too Many False Positives
- Increase `min_clearance` tolerance
- Adjust `max_overhang` threshold
- Review module dimensions

### Performance Issues
- Spatial hashing activates automatically at 10+ modules
- Consider batching for very large datasets (>1000 modules)

## Related Documentation

- [Complete Guide](./COLLISION_DETECTION_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [3D Visualization Guide](./VISUALIZATION_ADVANCED_GUIDE.md)
