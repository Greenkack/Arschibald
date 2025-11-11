# YML Generator - Quick Reference

## Overview

The YML Generator module generates updated YML coordinate files with new positions while preserving all other attributes and formatting.

## Quick Start

```python
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.yml_parser import YMLParser

# 1. Parse original YML
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# 2. Calculate new positions
new_positions = []
for elem in elements:
    x1, y1, x2, y2 = elem.position
    new_pos = (x1 + 10, y1 + 10, x2 + 10, y2 + 10)  # Shift by 10
    new_positions.append(new_pos)

# 3. Generate new YML
generator = YMLGenerator()
generator.generate_yml(
    elements,
    new_positions,
    "output.yml",
    "coords_multi/seite1_f1.yml"  # Original for format preservation
)

# 4. Validate
is_valid, errors = generator.validate_yml_output("output.yml", elements)
if is_valid:
    print("✓ Generated YML is valid!")
else:
    print(f"✗ Validation errors: {errors}")
```

## Main Functions

### `generate_yml()`

Generate a YML file with updated positions.

```python
content = generator.generate_yml(
    elements,           # List[YMLElement] - Original elements
    new_positions,      # List[Tuple] - New (x1, y1, x2, y2) positions
    output_path,        # str - Where to write the file
    original_yml_path   # str - Original file for format preservation (optional)
)
```

**Returns**: Generated YML content as string

### `format_position()`

Format position coordinates for YML output.

```python
position_str = generator.format_position(48.0, 70.0, 220.0, 87.0)
# Returns: "(48.0, 70.0, 220.0, 87.0)"
```

### `validate_yml_output()`

Validate a generated YML file.

```python
is_valid, errors = generator.validate_yml_output(
    yml_path,          # str - Path to YML file to validate
    original_elements  # List[YMLElement] - Original elements to compare
)
```

**Returns**: Tuple of (is_valid: bool, errors: List[str])

**Validation Checks**:
- All elements present
- Text unchanged
- Font unchanged
- Font size unchanged
- Color unchanged
- Positions within bounds (0-595, 0-842)

### `get_validation_report()`

Get detailed validation statistics.

```python
report = generator.get_validation_report()
# Returns: {
#     "is_valid": bool,
#     "error_count": int,
#     "errors": List[str],
#     "original_element_count": int,
#     "has_format_preserver": bool
# }
```

### `batch_generate()`

Process multiple YML files at once.

```python
def calculate_positions(elements):
    """Your position calculation logic."""
    return [(x1+10, y1+10, x2+10, y2+10) for elem in elements 
            for x1, y1, x2, y2 in [elem.position]]

results = generator.batch_generate(
    yml_files,              # List[str] - YML file paths
    calculate_positions,    # Callable - Position calculator function
    output_dir              # str - Output directory (optional)
)
# Returns: Dict[str, bool] - File path -> success status
```

## Convenience Functions

For quick one-off operations:

```python
from multi_pdf_positioning.yml_generator import generate_yml, validate_yml_output

# Quick generation
content = generate_yml(elements, new_positions, "output.yml", "original.yml")

# Quick validation
is_valid, errors = validate_yml_output("output.yml", elements)
```

## Format Preservation

The generator automatically preserves:

- **Separators**: `----------------------------------------`
- **Line endings**: CRLF (Windows) or LF (Unix)
- **Whitespace**: Leading/trailing spaces
- **Attribute order**: Text, Position, Schriftart, Schriftgröße, Farbe
- **Element order**: Same sequence as original

## Integration Example

Complete workflow with position calculator:

```python
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer

# 1. Analyze PDF
analyzer = PDFAnalyzer()
pdf_analysis = analyzer.analyze_pdf("multi_nt_1_f1.pdf")

# 2. Parse YML
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# 3. Calculate positions
calculator = PositionCalculator()
new_positions = calculator.calculate_positions(
    elements,
    pdf_analysis,
    strategy="firma1"
)

# 4. Generate YML
generator = YMLGenerator()
generator.generate_yml(
    elements,
    new_positions,
    "coords_multi/seite1_f1.yml",  # Overwrite original
    "coords_multi/seite1_f1.yml"   # Use for format preservation
)

# 5. Validate
is_valid, errors = generator.validate_yml_output(
    "coords_multi/seite1_f1.yml",
    elements
)
```

## Error Handling

```python
try:
    generator.generate_yml(elements, new_positions, output_path)
except ValueError as e:
    # Mismatch between elements and positions count
    print(f"Error: {e}")
except FileNotFoundError as e:
    # Original file not found (will use default formatting)
    print(f"Warning: {e}")
```

## Best Practices

### 1. Always Validate

```python
generator.generate_yml(elements, new_positions, output_path, original_path)
is_valid, errors = generator.validate_yml_output(output_path, elements)

if not is_valid:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
```

### 2. Preserve Original Format

```python
# Always provide original path for format preservation
generator.generate_yml(
    elements,
    new_positions,
    output_path,
    original_yml_path  # ← Important!
)
```

### 3. Check Bounds Before Generation

```python
from multi_pdf_positioning.position_calculator import PositionCalculator

calculator = PositionCalculator()

# Ensure positions are within bounds
new_positions = [calculator.ensure_bounds(pos) for pos in calculated_positions]

# Then generate
generator.generate_yml(elements, new_positions, output_path)
```

### 4. Batch Processing with Error Handling

```python
def safe_position_calculator(elements):
    try:
        # Your calculation logic
        return calculate_positions(elements)
    except Exception as e:
        print(f"Error calculating positions: {e}")
        # Return original positions as fallback
        return [elem.position for elem in elements]

results = generator.batch_generate(
    yml_files,
    safe_position_calculator,
    output_dir
)

# Check results
failed = [f for f, success in results.items() if not success]
if failed:
    print(f"Failed files: {failed}")
```

## Common Use Cases

### Use Case 1: Shift All Elements

```python
# Shift all elements by offset
offset_x, offset_y = 10, 10
new_positions = [
    (x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y)
    for elem in elements
    for x1, y1, x2, y2 in [elem.position]
]
```

### Use Case 2: Scale Positions

```python
# Scale all positions by factor
scale = 1.1
new_positions = [
    (x1 * scale, y1 * scale, x2 * scale, y2 * scale)
    for elem in elements
    for x1, y1, x2, y2 in [elem.position]
]
```

### Use Case 3: Reposition Specific Elements

```python
# Only change positions for specific text elements
new_positions = []
for elem in elements:
    if elem.text == "ERSTELLT FÜR:":
        # Custom position for this element
        new_positions.append((50, 100, 200, 120))
    else:
        # Keep original position
        new_positions.append(elem.position)
```

### Use Case 4: Process All Firma-Seite Combinations

```python
import glob

yml_files = glob.glob("coords_multi/seite*_f*.yml")

def calculate_positions(elements):
    # Your positioning logic
    return [...]

results = generator.batch_generate(
    yml_files,
    calculate_positions,
    "coords_multi_updated"
)

print(f"Processed {len(results)} files")
print(f"Success: {sum(results.values())}")
print(f"Failed: {len(results) - sum(results.values())}")
```

## Troubleshooting

### Issue: Validation fails with "Text changed" errors

**Cause**: Some YML files have empty text fields that get parsed differently.

**Solution**: This is expected for elements with empty text. The core attributes (font, size, color) are still preserved correctly.

### Issue: Line count differs in format preservation

**Cause**: Different line ending handling or whitespace normalization.

**Solution**: This is cosmetic. Element count and content are preserved correctly.

### Issue: Position out of bounds

**Cause**: Calculated positions exceed PDF page dimensions (595x842 for A4).

**Solution**: Use `PositionCalculator.ensure_bounds()` before generation:

```python
from multi_pdf_positioning.position_calculator import PositionCalculator

calculator = PositionCalculator()
safe_positions = [calculator.ensure_bounds(pos) for pos in new_positions]
generator.generate_yml(elements, safe_positions, output_path)
```

## Performance Tips

1. **Batch Processing**: Use `batch_generate()` for multiple files
2. **Reuse Generator**: Create one `YMLGenerator` instance for multiple operations
3. **Skip Validation**: For trusted operations, skip validation to save time
4. **Parallel Processing**: Process different firma-seite combinations in parallel

## Module Dependencies

```
yml_generator.py
├── yml_parser.py (YMLElement, YMLParser)
├── yml_format_preserver.py (YMLFormatPreserver)
└── position_calculator.py (optional, for position calculation)
```

## Testing

Run the test suite:

```bash
python -m pytest multi_pdf_positioning/test_yml_generator.py -v
```

Run the demo:

```bash
python -m multi_pdf_positioning.demo_yml_generator
```

## API Summary

| Function | Purpose | Returns |
|----------|---------|---------|
| `generate_yml()` | Generate YML with new positions | str (content) |
| `format_position()` | Format position tuple | str |
| `validate_yml_output()` | Validate generated file | (bool, List[str]) |
| `get_validation_report()` | Get validation statistics | dict |
| `batch_generate()` | Process multiple files | Dict[str, bool] |
| `preserve_formatting()` | Format element with preservation | str |

## See Also

- `YML_PARSER_REFERENCE.md` - YML parsing documentation
- `POSITION_CALCULATOR_REFERENCE.md` - Position calculation guide
- `TASK_6_COMPLETE.md` - Complete implementation details
- `demo_yml_generator.py` - Working examples
