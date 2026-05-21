# Validation System Reference

## Overview

The Validation System provides comprehensive validation for text element positions in the Multi-PDF Positioning System. It validates positions against PDF bounds, detects collisions, resolves conflicts, and generates detailed validation reports.

## Requirements Coverage

- **Requirement 6.1**: Position validation within PDF bounds (0-595, 0-842)
- **Requirement 6.2**: Collision detection and minimum spacing validation
- **Requirement 6.3**: Minimum margin validation (10 points from edges)
- **Requirement 6.4**: Validation report generation
- **Requirement 6.5**: Warning and error documentation
- **Requirement 3.4**: Automatic collision resolution

## Core Components

### ValidationSystem Class

Main class for performing validation operations.

```python
from multi_pdf_positioning.validation_system import ValidationSystem

# Initialize with default settings (A4 page)
validator = ValidationSystem()

# Or customize settings
validator = ValidationSystem(
    page_width=595,
    page_height=842,
    min_margin=10,
    min_spacing=5
)
```

### ValidationReport Class

Contains comprehensive validation results.

```python
@dataclass
class ValidationReport:
    firma: Optional[int]
    seite: Optional[int]
    timestamp: str
    total_elements: int
    messages: List[ValidationMessage]
    collisions: List[CollisionInfo]
    is_valid: bool
    summary: Dict[str, int]
```

### ValidationMessage Class

Represents a single validation message.

```python
@dataclass
class ValidationMessage:
    level: ValidationLevel  # INFO, WARNING, ERROR
    message: str
    element_index: Optional[int]
    position: Optional[Tuple[float, float, float, float]]
    details: Optional[str]
```

### CollisionInfo Class

Contains information about detected collisions.

```python
@dataclass
class CollisionInfo:
    element1_index: int
    element2_index: int
    element1_position: Tuple[float, float, float, float]
    element2_position: Tuple[float, float, float, float]
    overlap_area: float
    overlap_rect: Tuple[float, float, float, float]
```

## Main Functions

### 1. Position Validation

Validates that positions meet all requirements.

```python
# Validate positions
report = validator.validate_positions(positions, elements)

# Check validation status
if report.is_valid:
    print("All positions are valid")
else:
    print(f"Validation failed with {len(report.get_errors())} errors")
```

**Validation Checks:**
- ✓ Positions within PDF bounds (0-595, 0-842)
- ✓ Minimum margin from edges (10 points)
- ✓ Valid dimensions (x2 > x1, y2 > y1)
- ✓ No collisions between elements
- ✓ Minimum spacing between elements (5 points)

### 2. Collision Detection

Detects overlapping or too-close elements.

```python
# Detect collisions
collisions = validator.detect_collisions(positions)

# Process collisions
for collision in collisions:
    print(f"Collision between elements {collision.element1_index} "
          f"and {collision.element2_index}")
    print(f"Overlap area: {collision.overlap_area:.2f} sq pts")
```

**Collision Criteria:**
- Elements overlap
- Elements are closer than `min_spacing` (default: 5 points)

### 3. Collision Resolution

Automatically resolves collisions by adjusting positions.

```python
# Resolve collisions
adjusted_positions = validator.resolve_collisions(
    positions,
    collisions,
    max_iterations=10
)

# Verify resolution
new_collisions = validator.detect_collisions(adjusted_positions)
print(f"Collisions reduced from {len(collisions)} to {len(new_collisions)}")
```

**Resolution Strategy:**
- Moves elements away from each other
- Maintains page bounds
- Iterative approach for complex cases
- Preserves element dimensions

### 4. Validation Report Generation

Generates comprehensive validation reports.

```python
# Generate report
report = validator.generate_validation_report(
    positions,
    elements,
    firma=1,
    seite=1
)

# Print formatted report
print(validator.format_report(report))

# Access report data
print(f"Errors: {len(report.get_errors())}")
print(f"Warnings: {len(report.get_warnings())}")
print(f"Collisions: {len(report.collisions)}")
```

## Convenience Functions

For quick validation without creating a ValidationSystem instance:

```python
from multi_pdf_positioning.validation_system import (
    validate_positions,
    detect_collisions,
    generate_validation_report
)

# Quick validation
report = validate_positions(positions, elements)

# Quick collision detection
collisions = detect_collisions(positions, min_spacing=5)

# Quick report generation
report = generate_validation_report(positions, elements, firma=1, seite=1)
```

## Validation Levels

### ERROR (Critical Issues)
- Position outside PDF bounds
- Invalid dimensions (x2 <= x1 or y2 <= y1)
- Collisions between elements

### WARNING (Non-Critical Issues)
- Position too close to page edges (< min_margin)
- Very small element dimensions (< 5 points)

### INFO (Informational Messages)
- Validation success messages
- Summary information

## Usage Examples

### Example 1: Basic Validation

```python
from multi_pdf_positioning.validation_system import ValidationSystem

validator = ValidationSystem()

positions = [
    (50, 50, 200, 100),
    (250, 150, 400, 250),
]

report = validator.validate_positions(positions)

if report.is_valid:
    print("✓ All positions are valid")
else:
    for error in report.get_errors():
        print(f"✗ {error.message}")
```

### Example 2: Collision Detection and Resolution

```python
from multi_pdf_positioning.validation_system import ValidationSystem

validator = ValidationSystem(min_spacing=5)

# Positions with collision
positions = [
    (50, 50, 150, 100),
    (100, 75, 200, 125),  # Overlaps with first
]

# Detect collisions
collisions = validator.detect_collisions(positions)
print(f"Found {len(collisions)} collision(s)")

# Resolve collisions
if collisions:
    adjusted = validator.resolve_collisions(positions, collisions)
    
    # Verify resolution
    new_collisions = validator.detect_collisions(adjusted)
    print(f"Collisions after resolution: {len(new_collisions)}")
```

### Example 3: Batch Validation

```python
from multi_pdf_positioning.validation_system import ValidationSystem

validator = ValidationSystem()

# Validate multiple firma-seite combinations
combinations = [
    (1, 1, positions_f1_s1),
    (1, 2, positions_f1_s2),
    (2, 1, positions_f2_s1),
]

for firma, seite, positions in combinations:
    report = validator.generate_validation_report(
        positions, firma=firma, seite=seite
    )
    
    status = "✓" if report.is_valid else "✗"
    print(f"{status} Firma {firma}, Seite {seite}: "
          f"{len(report.get_errors())} errors, "
          f"{len(report.collisions)} collisions")
```

### Example 4: Detailed Report

```python
from multi_pdf_positioning.validation_system import ValidationSystem
from multi_pdf_positioning.yml_parser import parse_yml

# Parse YML file
elements = parse_yml("coords_multi/seite1_f1.yml")
positions = [elem.position for elem in elements]

# Generate report
validator = ValidationSystem()
report = validator.generate_validation_report(
    positions, elements, firma=1, seite=1
)

# Print formatted report
print(validator.format_report(report))

# Save report to file
with open("validation_report_f1_s1.txt", "w") as f:
    f.write(validator.format_report(report))
```

## Integration with Other Modules

### With YML Parser

```python
from multi_pdf_positioning.yml_parser import parse_yml
from multi_pdf_positioning.validation_system import validate_positions

# Parse YML file
elements = parse_yml("coords_multi/seite1_f1.yml")
positions = [elem.position for elem in elements]

# Validate
report = validate_positions(positions, elements)
```

### With Position Calculator

```python
from multi_pdf_positioning.position_calculator import calculate_positions
from multi_pdf_positioning.validation_system import ValidationSystem

# Calculate new positions
new_positions = calculate_positions(elements, pdf_analysis)

# Validate new positions
validator = ValidationSystem()
report = validator.validate_positions(new_positions, elements)

# Resolve any collisions
if report.collisions:
    new_positions = validator.resolve_collisions(
        new_positions, report.collisions
    )
```

### With YML Generator

```python
from multi_pdf_positioning.yml_generator import generate_yml
from multi_pdf_positioning.validation_system import ValidationSystem

# Validate before generating YML
validator = ValidationSystem()
report = validator.validate_positions(new_positions, elements)

if report.is_valid:
    # Generate YML with validated positions
    generate_yml(elements, new_positions, output_path)
else:
    print("Validation failed, cannot generate YML")
    print(validator.format_report(report))
```

## Configuration

### Default Settings

```python
# A4 page dimensions (in points)
page_width = 595
page_height = 842

# Minimum distance from page edges
min_margin = 10

# Minimum spacing between elements
min_spacing = 5
```

### Custom Settings

```python
# For different page sizes
validator = ValidationSystem(
    page_width=612,   # US Letter width
    page_height=792,  # US Letter height
    min_margin=15,    # Larger margin
    min_spacing=10    # More spacing
)
```

## Performance Considerations

- **Collision Detection**: O(n²) complexity for n elements
- **Collision Resolution**: Iterative, typically converges in 5-10 iterations
- **Validation**: O(n) for position checks, O(n²) for collision detection

For large numbers of elements (>100), consider:
- Spatial indexing for collision detection
- Parallel validation of multiple firma-seite combinations
- Caching validation results

## Error Handling

```python
from multi_pdf_positioning.validation_system import ValidationSystem

validator = ValidationSystem()

try:
    report = validator.validate_positions(positions, elements)
    
    if not report.is_valid:
        # Handle validation errors
        for error in report.get_errors():
            print(f"Error: {error.message}")
            
        # Attempt automatic resolution
        if report.collisions:
            adjusted = validator.resolve_collisions(
                positions, report.collisions
            )
            # Re-validate
            new_report = validator.validate_positions(adjusted)
            
except Exception as e:
    print(f"Validation failed: {e}")
```

## Testing

Run the test suite:

```bash
pytest multi_pdf_positioning/test_validation_system.py -v
```

Run the demo:

```bash
python multi_pdf_positioning/demo_validation_system.py
```

## Best Practices

1. **Always validate before generating YML files**
   ```python
   report = validator.validate_positions(positions, elements)
   if report.is_valid:
       generate_yml(elements, positions, output_path)
   ```

2. **Use collision resolution for automatic fixes**
   ```python
   if report.collisions:
       positions = validator.resolve_collisions(positions, report.collisions)
   ```

3. **Include element context for better error messages**
   ```python
   report = validator.validate_positions(positions, elements)
   # Error messages will include element text
   ```

4. **Save validation reports for documentation**
   ```python
   with open(f"validation_f{firma}_s{seite}.txt", "w") as f:
       f.write(validator.format_report(report))
   ```

5. **Batch validate all combinations**
   ```python
   for firma in range(1, 7):
       for seite in range(1, 9):
           # Validate each combination
           report = validator.generate_validation_report(...)
   ```

## Troubleshooting

### Issue: Too many collision warnings

**Solution**: Increase `min_spacing` or adjust positioning strategy
```python
validator = ValidationSystem(min_spacing=3)  # Reduce spacing requirement
```

### Issue: Elements adjusted outside bounds

**Solution**: Collision resolution respects bounds, but check margin settings
```python
validator = ValidationSystem(min_margin=5)  # Reduce margin requirement
```

### Issue: Validation too strict

**Solution**: Warnings don't invalidate the report, only errors do
```python
# Check only errors
if len(report.get_errors()) == 0:
    # Proceed even with warnings
    generate_yml(elements, positions, output_path)
```

## See Also

- [YML Parser Reference](YML_PARSER_REFERENCE.md)
- [Position Calculator Reference](POSITION_CALCULATOR_REFERENCE.md)
- [YML Generator Reference](YML_GENERATOR_REFERENCE.md)
- [Positioning Strategies Reference](POSITIONING_STRATEGIES_REFERENCE.md)
