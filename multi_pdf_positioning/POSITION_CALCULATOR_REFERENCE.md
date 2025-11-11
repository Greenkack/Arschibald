# Position Calculator Quick Reference

## Overview

The Position Calculator module calculates optimal positions for text elements in PDF templates with collision detection and boundary validation.

## Quick Start

```python
from multi_pdf_positioning.position_calculator import (
    PositionCalculator,
    calculate_positions
)

# Create calculator
calculator = PositionCalculator()

# Calculate positions
new_positions = calculator.calculate_positions(
    elements=yml_elements,
    pdf_analysis=pdf_analysis,
    strategy="grid"  # or None for default
)

# Validate
is_valid, errors = calculator.validate_positions(new_positions)
collisions = calculator.check_collisions(new_positions)
```

## Core Functions

### ensure_bounds(position)
Ensures a position stays within PDF page bounds with margins.

**Input:** `(x1, y1, x2, y2)` tuple  
**Output:** Adjusted `(x1, y1, x2, y2)` tuple  
**Rules:**
- Minimum margin: 10 points from edges
- Maintains positive dimensions
- Clips to page size (595 x 842 points)

### check_collisions(positions)
Detects overlapping text elements.

**Input:** List of position tuples  
**Output:** List of `CollisionInfo` objects  
**Rules:**
- Minimum spacing: 5 points between elements
- Returns overlap area for each collision
- Checks all position pairs

### calculate_positions(elements, pdf_analysis, strategy)
Main function to calculate new positions.

**Input:**
- `elements`: List of YMLElement objects
- `pdf_analysis`: PDFAnalysis object
- `strategy`: Strategy name (optional, defaults to "grid")

**Output:** List of position tuples  
**Strategies:**
- `"grid"`: 3x3 grid layout (fallback)
- More strategies coming in Task 5

### validate_positions(positions)
Validates positions against all rules.

**Input:** List of position tuples  
**Output:** `(is_valid, list_of_errors)` tuple  
**Checks:**
- Positions within bounds
- Positive dimensions
- No collisions
- Minimum margins

### get_element_importance(element)
Gets importance weight for an element.

**Input:** YMLElement object  
**Output:** Float between 0.0 and 1.0  
**Weights:**
- "ANGEBOT": 1.0
- "kWp_anlage_anlage": 1.0
- "PHOTOVOLTAIK": 0.95
- "ERSTELLT FÜR:": 0.9
- "kunde_vorname_und_nachname": 0.85
- Default: 0.5

## Positioning Rules

```python
POSITIONING_RULES = {
    "min_margin": 10,          # Points from page edge
    "min_spacing": 5,          # Points between elements
    "page_width": 595,         # A4 width in points
    "page_height": 842,        # A4 height in points
    "grid_columns": 3,         # Grid columns
    "grid_rows": 3,            # Grid rows
    "grid_padding": 20,        # Padding between grid cells
    "importance_weights": {...},
    "default_importance": 0.5
}
```

## Data Structures

### CollisionInfo
```python
@dataclass
class CollisionInfo:
    element1_index: int      # First element index
    element2_index: int      # Second element index
    overlap_area: float      # Overlap in square points
```

## Examples

### Basic Usage
```python
calculator = PositionCalculator()

# Ensure a position is within bounds
safe_pos = calculator.ensure_bounds((50, 50, 200, 100))

# Check for collisions
positions = [(50, 50, 150, 100), (100, 75, 200, 125)]
collisions = calculator.check_collisions(positions)
print(f"Found {len(collisions)} collisions")
```

### With YML and PDF
```python
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer

# Parse and analyze
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

analyzer = PDFAnalyzer()
analysis = analyzer.analyze_pdf("pdf_templates_static/multi/multi_nt_01_f1.pdf")

# Calculate positions
calculator = PositionCalculator()
new_positions = calculator.calculate_positions(elements, analysis)

# Validate
is_valid, errors = calculator.validate_positions(new_positions)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Custom Rules
```python
custom_rules = {
    "min_margin": 20,
    "min_spacing": 10,
    "page_width": 595,
    "page_height": 842,
}

calculator = PositionCalculator(rules=custom_rules)
```

## Grid Strategy

The grid strategy distributes elements evenly across a 3x3 grid:

```
┌─────────┬─────────┬─────────┐
│ Cell 0  │ Cell 1  │ Cell 2  │
├─────────┼─────────┼─────────┤
│ Cell 3  │ Cell 4  │ Cell 5  │
├─────────┼─────────┼─────────┤
│ Cell 6  │ Cell 7  │ Cell 8  │
└─────────┴─────────┴─────────┘
```

- Elements placed left-to-right, top-to-bottom
- Wraps around if more than 9 elements
- Maintains original element dimensions when possible
- Respects margins and padding

## Testing

Run tests:
```bash
pytest multi_pdf_positioning/test_position_calculator.py -v
```

Run demo:
```bash
cd multi_pdf_positioning
python demo_position_calculator.py
```

## Error Handling

Common errors and solutions:

**Position out of bounds:**
- Use `ensure_bounds()` to adjust
- Check margin settings

**Collisions detected:**
- Increase `min_spacing` in rules
- Use different positioning strategy
- Reduce element sizes

**Invalid dimensions:**
- Ensure x2 > x1 and y2 > y1
- Check element size calculations

## Performance

- Position calculation: ~0.5 seconds per combination
- Collision detection: O(n²) for n elements
- Validation: O(n) for n positions

For 28 elements (typical YML file):
- Calculate: < 0.1 seconds
- Validate: < 0.01 seconds
- Check collisions: < 0.01 seconds

## Next Steps

Task 5 will add six positioning strategies:
1. Header-Focused
2. Center-Prominent
3. Asymmetric-Modern
4. Grid-Based (enhanced)
5. Diagonal-Flow
6. Sidebar-Layout

Each strategy will be optimized for specific firma designs.
