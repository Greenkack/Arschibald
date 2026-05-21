# Module Placement Algorithms - Quick Reference

## Overview

Advanced algorithms for optimal placement of PV modules on roof surfaces.

**Task**: 135 - 3D Module Placement Algorithms  
**Requirements**: 1.3, 6.1  
**Location**: `backend/services/module_placement_algorithms.py`

## Key Features

### 1. Automatic Optimal Placement
- Maximum coverage algorithm
- Intelligent spacing calculations
- Orientation optimization
- Boundary respect

### 2. Constraint-Based Placement
- Obstacle avoidance
- Shading area exclusion
- Custom exclusion zones
- Boundary constraints

### 3. Spacing Calculations
- Dynamic spacing based on module count
- Aspect ratio consideration
- Minimum spacing enforcement
- Optimal distribution

### 4. Orientation Optimization
- Portrait vs landscape analysis
- Capacity comparison
- Automatic selection
- Manual override support

### 5. Row/Column Layout
- Regular grid patterns
- Custom row/column specification
- Precise positioning
- Efficient space utilization

### 6. Custom Placement Patterns
- Grid pattern (regular)
- Staggered/brick pattern
- User-defined patterns
- Pattern function support

## Quick Start

```python
from backend.services.module_placement_algorithms import (
    ModulePlacementAlgorithms,
    PlacementConfig,
    RoofSurface,
    ModuleOrientation,
    PlacementStrategy
)

# Initialize
algorithms = ModulePlacementAlgorithms()

# Define roof
roof = RoofSurface(
    length=10.0,  # meters
    width=8.0,    # meters
    type="flat",
    pitch=0.0
)

# Configure placement
config = PlacementConfig(
    roof=roof,
    module_quantity=30,
    orientation=ModuleOrientation.AUTO,
    strategy=PlacementStrategy.OPTIMAL,
    spacing=0.05,  # 5cm between modules
    margin=0.30    # 30cm from edges
)

# Calculate optimal placement
result = algorithms.calculate_optimal_placement(config)

print(f"Placed {result.count} modules")
print(f"Coverage: {result.coverage:.1f}%")
print(f"Efficiency: {result.efficiency:.2f}")
```

## Placement Strategies

### OPTIMAL
Maximum coverage with optimal spacing
```python
config.strategy = PlacementStrategy.OPTIMAL
result = algorithms.calculate_optimal_placement(config)
```

### GRID
Regular grid pattern
```python
result = algorithms.generate_row_column_layout(config, rows=5, cols=6)
```

### STAGGERED
Brick/staggered pattern
```python
result = algorithms.generate_staggered_pattern(config)
```

### CONSTRAINT_BASED
Placement with obstacle avoidance
```python
from backend.services.module_placement_algorithms import PlacementConstraint

config.constraints = [
    PlacementConstraint(x=2.0, y=3.0, width=1.5, height=1.5, type="obstacle")
]
result = algorithms.calculate_constraint_based_placement(config)
```

### CUSTOM
User-defined pattern
```python
def my_pattern(config):
    # Generate custom positions
    return [(x, y, z), ...]

result = algorithms.generate_custom_pattern(config, my_pattern)
```

## Module Orientations

- **PORTRAIT**: 1.05m × 1.76m (vertical, standard)
- **LANDSCAPE**: 1.76m × 1.05m (horizontal)
- **AUTO**: Automatically determine best orientation

## Constraints

```python
# Add obstacle
obstacle = PlacementConstraint(
    x=2.0,        # X-coordinate of center
    y=3.0,        # Y-coordinate of center
    width=1.5,    # Width of obstacle
    height=1.5,   # Height of obstacle
    type="obstacle"
)

# Add shading area
shading = PlacementConstraint(
    x=-1.0, y=2.0, width=2.0, height=3.0, type="shading"
)

config.constraints = [obstacle, shading]
```

## Spacing Calculation

```python
# Calculate optimal spacing
spacing_x, spacing_y = algorithms.calculate_spacing(
    module_count=30,
    roof_length=10.0,
    roof_width=8.0,
    orientation=ModuleOrientation.PORTRAIT,
    margin=0.30
)
```

## Orientation Optimization

```python
# Determine optimal orientation
optimal = algorithms.optimize_orientation(
    roof=roof,
    module_quantity=30,
    margin=0.30
)
# Returns: ModuleOrientation.PORTRAIT or LANDSCAPE
```

## Result Structure

```python
@dataclass
class PlacementResult:
    positions: List[Tuple[float, float, float]]  # (x, y, z) coordinates
    orientations: List[ModuleOrientation]        # Orientation per module
    count: int                                   # Number placed
    coverage: float                              # % of roof covered
    efficiency: float                            # Placement efficiency (0-1)
    strategy_used: PlacementStrategy            # Strategy used
    message: str                                 # Status message
```

## Common Use Cases

### Maximum Coverage
```python
config.strategy = PlacementStrategy.OPTIMAL
result = algorithms.calculate_optimal_placement(config)
```

### Avoid Obstacles
```python
config.constraints = [obstacles...]
result = algorithms.calculate_constraint_based_placement(config)
```

### Specific Layout
```python
result = algorithms.generate_row_column_layout(config, rows=6, cols=5)
```

### Aesthetic Pattern
```python
result = algorithms.generate_staggered_pattern(config)
```

## Performance Notes

- Optimal placement: O(n) where n = module_quantity
- Constraint checking: O(n × m) where m = number of constraints
- Grid generation: O(rows × cols)
- Caching recommended for repeated calculations

## Integration Example

```python
# In FastAPI endpoint
from fastapi import APIRouter
from backend.services.module_placement_algorithms import *

router = APIRouter()

@router.post("/api/v1/placement/optimal")
async def calculate_placement(request: PlacementRequest):
    algorithms = ModulePlacementAlgorithms()
    
    config = PlacementConfig(
        roof=RoofSurface(**request.roof),
        module_quantity=request.module_quantity,
        orientation=ModuleOrientation[request.orientation],
        strategy=PlacementStrategy.OPTIMAL
    )
    
    result = algorithms.calculate_optimal_placement(config)
    
    return {
        "positions": result.positions,
        "count": result.count,
        "coverage": result.coverage,
        "efficiency": result.efficiency,
        "message": result.message
    }
```

## See Also

- Full documentation: `MODULE_PLACEMENT_ALGORITHMS_GUIDE.md`
- API endpoints: `API_DOCUMENTATION.md`
- 3D Visualization: `3D_VISUALIZATION_GUIDE.md`
