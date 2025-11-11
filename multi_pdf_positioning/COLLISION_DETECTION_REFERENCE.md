# Collision Detection Reference Guide

## Overview

The collision detection system identifies and resolves overlapping text elements in PDF positioning. It ensures that text elements maintain proper spacing and don't overlap with each other.

## Quick Start

```python
from multi_pdf_positioning.validation_system import ValidationSystem

# Create validator
validator = ValidationSystem(min_spacing=5)

# Detect collisions
positions = [
    (50, 50, 150, 100),
    (100, 75, 200, 125),  # Overlaps with first
]

collisions = validator.detect_collisions(positions)
print(f"Found {len(collisions)} collision(s)")

# Resolve collisions
if collisions:
    adjusted = validator.resolve_collisions(positions, collisions)
    print("Collisions resolved!")
```

## Core Functions

### detect_collisions()

Detects collisions between text elements.

**Signature:**
```python
def detect_collisions(
    positions: List[Tuple[float, float, float, float]]
) -> List[CollisionInfo]
```

**Parameters:**
- `positions`: List of position tuples (x1, y1, x2, y2)

**Returns:**
- List of `CollisionInfo` objects describing each collision

**Collision Criteria:**
- Elements overlap (rectangles intersect)
- Elements are closer than `min_spacing` (default: 5 points)

**Example:**
```python
validator = ValidationSystem(min_spacing=5)

positions = [
    (50, 50, 150, 100),
    (100, 75, 200, 125),
]

collisions = validator.detect_collisions(positions)

for collision in collisions:
    print(f"Collision between elements {collision.element1_index} and {collision.element2_index}")
    print(f"Overlap area: {collision.overlap_area:.2f} sq pts")
```

### resolve_collisions()

Automatically resolves collisions by adjusting positions.

**Signature:**
```python
def resolve_collisions(
    positions: List[Tuple[float, float, float, float]],
    collisions: List[CollisionInfo],
    max_iterations: int = 10
) -> List[Tuple[float, float, float, float]]
```

**Parameters:**
- `positions`: Original positions
- `collisions`: List of detected collisions
- `max_iterations`: Maximum adjustment iterations (default: 10)

**Returns:**
- List of adjusted positions with reduced/eliminated collisions

**Algorithm:**
1. Calculate direction between element centers
2. Move elements apart by `min_spacing + 2`
3. Ensure positions stay within page bounds
4. Repeat until collisions resolved or max iterations reached

**Example:**
```python
# Detect collisions
collisions = validator.detect_collisions(positions)

# Resolve
adjusted = validator.resolve_collisions(
    positions, 
    collisions, 
    max_iterations=10
)

# Verify
new_collisions = validator.detect_collisions(adjusted)
print(f"Reduced from {len(collisions)} to {len(new_collisions)} collisions")
```

## Data Structures

### CollisionInfo

Contains detailed information about a collision.

**Attributes:**
```python
@dataclass
class CollisionInfo:
    element1_index: int                                    # Index of first element
    element2_index: int                                    # Index of second element
    element1_position: Tuple[float, float, float, float]   # Position of first element
    element2_position: Tuple[float, float, float, float]   # Position of second element
    overlap_area: float                                    # Area of overlap in sq pts
    overlap_rect: Tuple[float, float, float, float]        # Rectangle of overlap
```

**Example:**
```python
collision = collisions[0]
print(f"Elements: {collision.element1_index} ↔ {collision.element2_index}")
print(f"Overlap: {collision.overlap_area:.2f} sq pts")
print(f"Overlap rect: {collision.overlap_rect}")
```

## Configuration

### ValidationSystem Parameters

```python
ValidationSystem(
    page_width: float = 595,      # PDF page width (A4)
    page_height: float = 842,     # PDF page height (A4)
    min_margin: float = 10,       # Minimum distance from edges
    min_spacing: float = 5        # Minimum spacing between elements
)
```

**min_spacing:**
- Default: 5 points
- Elements closer than this are considered colliding
- Increased spacing = more conservative collision detection

**Example:**
```python
# Strict collision detection (10 pts spacing)
strict_validator = ValidationSystem(min_spacing=10)

# Lenient collision detection (2 pts spacing)
lenient_validator = ValidationSystem(min_spacing=2)
```

## Integration with Validation

Collision detection is integrated into the validation workflow:

```python
# Validate positions (includes collision detection)
report = validator.validate_positions(positions)

# Check for collisions
if report.collisions:
    print(f"Found {len(report.collisions)} collision(s)")
    
    # Automatically resolve
    adjusted = validator.resolve_collisions(positions, report.collisions)
    
    # Re-validate
    new_report = validator.validate_positions(adjusted)
    print(f"Status: {'✓ VALID' if new_report.is_valid else '✗ INVALID'}")
```

## Common Use Cases

### 1. Validate YML Positions

```python
from multi_pdf_positioning.yml_parser import parse_yml
from multi_pdf_positioning.validation_system import ValidationSystem

# Parse YML file
elements = parse_yml("coords_multi/seite1_f1.yml")
positions = [elem.position for elem in elements]

# Validate
validator = ValidationSystem()
report = validator.generate_validation_report(
    positions,
    elements=elements,
    firma=1,
    seite=1
)

# Check collisions
if report.collisions:
    print(f"Found {len(report.collisions)} collision(s)")
    for collision in report.collisions:
        elem1 = elements[collision.element1_index]
        elem2 = elements[collision.element2_index]
        print(f"  {elem1.text} ↔ {elem2.text}")
```

### 2. Batch Validation

```python
# Validate all 48 combinations
for firma in range(1, 7):
    for seite in range(1, 9):
        yml_path = f"coords_multi/seite{seite}_f{firma}.yml"
        elements = parse_yml(yml_path)
        positions = [elem.position for elem in elements]
        
        report = validator.validate_positions(positions)
        
        if report.collisions:
            print(f"Firma {firma}, Seite {seite}: {len(report.collisions)} collision(s)")
```

### 3. Automatic Correction

```python
# Load positions
elements = parse_yml("coords_multi/seite1_f1.yml")
positions = [elem.position for elem in elements]

# Detect and resolve collisions
collisions = validator.detect_collisions(positions)

if collisions:
    # Resolve
    adjusted = validator.resolve_collisions(positions, collisions)
    
    # Update elements with new positions
    for i, elem in enumerate(elements):
        elem.position = adjusted[i]
    
    # Generate new YML with adjusted positions
    # (use yml_generator module)
```

## Performance

- **Detection**: O(n²) for n elements
- **Resolution**: O(k × n²) for k iterations
- **Typical**: < 0.1s for 20-30 elements

## Best Practices

1. **Always validate after positioning:**
   ```python
   report = validator.validate_positions(positions)
   if not report.is_valid:
       # Handle errors
   ```

2. **Use appropriate min_spacing:**
   - Headers/titles: 10-15 pts
   - Body text: 5-8 pts
   - Dense layouts: 3-5 pts

3. **Limit resolution iterations:**
   ```python
   # For simple layouts
   adjusted = validator.resolve_collisions(positions, collisions, max_iterations=5)
   
   # For complex layouts
   adjusted = validator.resolve_collisions(positions, collisions, max_iterations=15)
   ```

4. **Check resolution success:**
   ```python
   initial_count = len(collisions)
   adjusted = validator.resolve_collisions(positions, collisions)
   new_collisions = validator.detect_collisions(adjusted)
   
   if len(new_collisions) < initial_count:
       print("✓ Collisions reduced")
   else:
       print("⚠ Manual adjustment needed")
   ```

## Troubleshooting

### Issue: Too many collisions detected

**Solution:** Adjust `min_spacing` parameter
```python
# Reduce spacing requirement
validator = ValidationSystem(min_spacing=3)
```

### Issue: Resolution doesn't eliminate all collisions

**Solution:** Increase iterations or adjust manually
```python
# More iterations
adjusted = validator.resolve_collisions(positions, collisions, max_iterations=20)

# Or manually adjust problematic positions
```

### Issue: Elements moved out of bounds during resolution

**Solution:** Check page dimensions and margins
```python
# Verify configuration
print(f"Page: {validator.page_width} x {validator.page_height}")
print(f"Margins: {validator.min_margin}")

# Ensure bounds are enforced
adjusted = validator.resolve_collisions(positions, collisions)
for pos in adjusted:
    x1, y1, x2, y2 = pos
    assert x1 >= validator.min_margin
    assert x2 <= validator.page_width - validator.min_margin
```

## API Reference

### ValidationSystem Methods

| Method | Description |
|--------|-------------|
| `detect_collisions(positions)` | Detect collisions between elements |
| `resolve_collisions(positions, collisions, max_iterations)` | Resolve collisions automatically |
| `validate_positions(positions, elements)` | Comprehensive validation including collisions |
| `generate_validation_report(positions, elements, firma, seite)` | Generate detailed report |
| `format_report(report)` | Format report as string |

### Convenience Functions

| Function | Description |
|----------|-------------|
| `detect_collisions(positions, min_spacing)` | Quick collision detection |
| `validate_positions(positions, elements, ...)` | Quick validation |
| `generate_validation_report(positions, ...)` | Quick report generation |

## Examples

See the following files for complete examples:
- `test_validation_system.py` - Comprehensive test suite
- `verify_task_8_2.py` - Verification script
- `demo_validation_system.py` - Usage demonstrations

## Requirements Coverage

✅ **Requirement 6.2**: Collision detection and spacing validation
- Detects overlapping elements
- Identifies spacing violations
- Provides detailed collision information

✅ **Requirement 3.4**: Design element overlap prevention
- Ensures text doesn't overlap
- Maintains minimum spacing
- Automatic resolution available

## Related Documentation

- [Validation System Reference](VALIDATION_SYSTEM_REFERENCE.md)
- [Task 8.1 Complete](TASK_8_1_COMPLETE.md)
- [Task 8.2 Complete](TASK_8_2_COMPLETE.md)
