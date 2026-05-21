# YML Parser Quick Reference

## Overview

The YML Parser module provides tools to parse, analyze, and update YML coordinate files while preserving their original formatting.

## Core Classes

### YMLElement

Dataclass representing a text element from a YML file.

```python
@dataclass
class YMLElement:
    text: str                                    # Text content
    position: Tuple[float, float, float, float]  # (x1, y1, x2, y2)
    font: str                                    # Font name
    font_size: float                             # Font size in points
    color: int                                   # Color as integer
    index: int                                   # Original position in file
    raw_block: str                               # Original raw text block
```

### YMLParser

Main parser class for reading YML files.

```python
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `parse_yml(yml_path)` | Parse YML file | `List[YMLElement]` |
| `get_elements()` | Get all elements | `List[YMLElement]` |
| `get_element_by_text(text)` | Find by text | `Optional[YMLElement]` |
| `get_elements_by_font(font)` | Filter by font | `List[YMLElement]` |
| `get_non_empty_elements()` | Get elements with text | `List[YMLElement]` |
| `get_empty_elements()` | Get placeholder elements | `List[YMLElement]` |
| `validate_elements()` | Validate all elements | `Tuple[bool, List[str]]` |
| `get_statistics()` | Get parsing statistics | `dict` |

### YMLFormatPreserver

Class for preserving original YML formatting.

```python
preserver = YMLFormatPreserver()
preserver.load_original("coords_multi/seite1_f1.yml")
new_content = preserver.reconstruct_yml(elements, new_positions)
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `load_original(yml_path)` | Load and analyze file | `None` |
| `preserve_formatting(element, new_pos)` | Format element | `str` |
| `reconstruct_yml(elements, positions)` | Rebuild YML file | `str` |
| `validate_preservation(path, content)` | Validate format | `Tuple[bool, List[str]]` |
| `get_structure_info()` | Get structure info | `dict` |

## Quick Start Examples

### 1. Parse a YML File

```python
from multi_pdf_positioning.yml_parser import parse_yml

# Simple parsing
elements = parse_yml("coords_multi/seite1_f1.yml")

print(f"Found {len(elements)} elements")
for elem in elements[:3]:
    print(f"{elem.text}: {elem.position}")
```

### 2. Find Specific Elements

```python
from multi_pdf_positioning.yml_parser import YMLParser

parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# Find by text
photovoltaik = parser.get_element_by_text("PHOTOVOLTAIK")
if photovoltaik:
    print(f"Found at: {photovoltaik.position}")

# Find all bold elements
bold = parser.get_elements_by_font("Helvetica-Bold")
print(f"Found {len(bold)} bold elements")

# Get only non-empty elements
non_empty = parser.get_non_empty_elements()
print(f"Found {len(non_empty)} elements with text")
```

### 3. Update Positions with Format Preservation

```python
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.yml_format_preserver import preserve_yml_format

# Parse original
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# Create new positions (example: shift right by 50 points)
new_positions = []
for elem in elements:
    x1, y1, x2, y2 = elem.position
    new_positions.append((x1 + 50, y1, x2 + 50, y2))

# Generate new YML with preserved format
new_content = preserve_yml_format(
    "coords_multi/seite1_f1.yml",
    elements,
    new_positions
)

# Save to file
with open("output.yml", "w", encoding="utf-8") as f:
    f.write(new_content)
```

### 4. Validate Elements

```python
from multi_pdf_positioning.yml_parser import YMLParser

parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# Validate all elements
is_valid, errors = parser.validate_elements()

if is_valid:
    print("✓ All elements are valid")
else:
    print("✗ Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### 5. Get Statistics

```python
from multi_pdf_positioning.yml_parser import YMLParser

parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

stats = parser.get_statistics()
print(f"Total elements: {stats['total_elements']}")
print(f"Non-empty: {stats['non_empty_elements']}")
print(f"Empty: {stats['empty_elements']}")
print(f"Unique fonts: {stats['unique_fonts']}")
print(f"Unique colors: {stats['unique_colors']}")
```

### 6. Batch Processing

```python
from pathlib import Path
from multi_pdf_positioning.yml_parser import parse_yml

yml_dir = Path("coords_multi")
yml_files = list(yml_dir.glob("seite*.yml"))

for yml_file in yml_files:
    elements = parse_yml(str(yml_file))
    print(f"{yml_file.name}: {len(elements)} elements")
```

### 7. Filter and Transform

```python
from multi_pdf_positioning.yml_parser import YMLParser

parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# Get all large text elements (font size > 20)
large_text = [e for e in elements if e.font_size > 20]
print(f"Found {len(large_text)} large text elements")

# Get all elements in top half of page (y < 421)
top_half = [e for e in elements if e.position[1] < 421]
print(f"Found {len(top_half)} elements in top half")

# Get all dynamic placeholders (text contains underscore)
dynamic = [e for e in elements if '_' in e.text]
print(f"Found {len(dynamic)} dynamic placeholders")
```

## Common Patterns

### Pattern 1: Parse, Modify, Save

```python
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.yml_format_preserver import YMLFormatPreserver

# Parse
parser = YMLParser()
elements = parser.parse_yml("input.yml")

# Modify positions (your logic here)
new_positions = [calculate_new_position(e) for e in elements]

# Save with preserved format
preserver = YMLFormatPreserver()
preserver.load_original("input.yml")
new_content = preserver.reconstruct_yml(elements, new_positions)

with open("output.yml", "w", encoding="utf-8") as f:
    f.write(new_content)
```

### Pattern 2: Analyze Multiple Files

```python
from pathlib import Path
from multi_pdf_positioning.yml_parser import YMLParser

results = {}
for yml_file in Path("coords_multi").glob("seite1_*.yml"):
    parser = YMLParser()
    elements = parser.parse_yml(str(yml_file))
    
    results[yml_file.name] = {
        "total": len(elements),
        "non_empty": len(parser.get_non_empty_elements()),
        "fonts": len(set(e.font for e in elements))
    }

for name, stats in results.items():
    print(f"{name}: {stats}")
```

### Pattern 3: Validate Before Processing

```python
from multi_pdf_positioning.yml_parser import YMLParser

parser = YMLParser()
elements = parser.parse_yml("input.yml")

# Validate before processing
is_valid, errors = parser.validate_elements()
if not is_valid:
    print("Validation errors found:")
    for error in errors:
        print(f"  - {error}")
    exit(1)

# Continue with processing...
```

## Validation Rules

The parser validates:

1. **Position Bounds**
   - X coordinates: 0 ≤ x1 < x2 ≤ 595 (A4 width)
   - Y coordinates: 0 ≤ y1 < y2 ≤ 842 (A4 height)

2. **Font Size**
   - Must be > 0

3. **Color**
   - Must be ≥ 0

## Format Preservation

The format preserver maintains:

- ✅ Line endings (LF or CRLF)
- ✅ Separator lines (`----------------------------------------`)
- ✅ Block structure
- ✅ Attribute order
- ✅ Whitespace and indentation
- ✅ All non-position attributes

Only position coordinates are updated.

## Error Handling

```python
from multi_pdf_positioning.yml_parser import YMLParser

try:
    parser = YMLParser()
    elements = parser.parse_yml("nonexistent.yml")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid YML format: {e}")
```

## Performance Notes

- Parsing a typical YML file (28 elements): ~0.1 seconds
- Format preservation: ~0.2 seconds
- Batch processing 48 files: ~15 seconds

## Testing

Run the comprehensive test suite:

```bash
python multi_pdf_positioning/test_yml_parser.py
```

Tests include:
- Parsing multiple YML files
- Format preservation validation
- Integration testing
- Edge case handling

## See Also

- [TASK_2_COMPLETE.md](TASK_2_COMPLETE.md) - Implementation details
- [README.md](README.md) - Project overview
- [design.md](../.kiro/specs/multi-pdf-positioning/design.md) - System design
