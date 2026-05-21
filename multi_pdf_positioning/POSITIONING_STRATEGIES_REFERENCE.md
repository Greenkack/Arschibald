# Positioning Strategies Quick Reference

## Overview

The Multi-PDF Positioning System includes 6 unique positioning strategies, each optimized for a specific firma's design characteristics. This document provides a quick reference for understanding and using these strategies.

## Strategy Selection

Strategies are automatically selected based on the firma number:

| Firma | Strategy | Layout Pattern |
|-------|----------|----------------|
| 1 | Header-Focused | Traditional hierarchy |
| 2 | Center-Prominent | Centered emphasis |
| 3 | Asymmetric-Modern | Dynamic asymmetry |
| 4 | Grid-Based | Structured 3×3 grid |
| 5 | Diagonal-Flow | Progressive diagonal |
| 6 | Sidebar-Layout | Two-column sidebar |

## Strategy Details

### 1. Header-Focused Strategy (Firma 1)

**Philosophy**: Traditional top-down information hierarchy

**Layout**:
```
┌─────────────────────────────────┐
│ HEADERS (Top-Left)              │
│ ┌─────────────┐                 │
│ │ PHOTOVOLTAIK│                 │
│ │ ANGEBOT     │                 │
│ └─────────────┘                 │
│                                 │
│    CUSTOMER INFO (Centered)     │
│    ┌──────────────────┐         │
│    │ Name             │         │
│    │ Address          │         │
│    └──────────────────┘         │
│                                 │
│                                 │
│                  ┌────────────┐ │
│                  │ VALUES     │ │
│                  │ (Bottom-   │ │
│                  │  Right)    │ │
│                  └────────────┘ │
└─────────────────────────────────┘
```

**Best For**: Professional, formal documents

**Element Placement**:
- Headers: Top-left, stacked vertically
- Customer Info: Centered horizontally, below headers
- Important Values: Bottom-right corner
- Other Elements: Left side, middle section

---

### 2. Center-Prominent Strategy (Firma 2)

**Philosophy**: Centered emphasis for maximum visibility

**Layout**:
```
┌─────────────────────────────────┐
│ CUSTOMER  ┌──────────┐  VALUES │
│ INFO      │ HEADERS  │  (Top-  │
│ (Top-     │(Centered)│  Right) │
│  Left)    └──────────┘          │
│                                 │
│                                 │
│      OTHER ELEMENTS             │
│      (Centered, Middle)         │
│                                 │
│                                 │
│                                 │
└─────────────────────────────────┘
```

**Best For**: Modern, balanced designs

**Element Placement**:
- Headers: Centered at top with extra spacing
- Customer Info: Top-left corner
- Important Values: Top-right corner
- Other Elements: Centered, middle section

---

### 3. Asymmetric-Modern Strategy (Firma 3)

**Philosophy**: Dynamic asymmetry for visual interest

**Layout**:
```
┌─────────────────────────────────┐
│                    ┌──────────┐ │
│                    │ HEADERS  │ │
│                    │(Top-Right│ │
│                    └──────────┘ │
│                                 │
│ OTHER              ┌──────────┐ │
│ ELEMENTS           │ CUSTOMER │ │
│ (Left              │ INFO     │ │
│  Middle)           │(Right-   │ │
│                    │ Middle)  │ │
│                    └──────────┘ │
│ ┌────────────┐                 │
│ │ VALUES     │                 │
│ │(Bottom-    │                 │
│ │ Left)      │                 │
│ └────────────┘                 │
└─────────────────────────────────┘
```

**Best For**: Contemporary, eye-catching layouts

**Element Placement**:
- Headers: Top-right corner
- Customer Info: Right-middle section
- Important Values: Bottom-left corner
- Other Elements: Left-middle section

---

### 4. Grid-Based Strategy (Firma 4)

**Philosophy**: Structured organization in a 3×3 grid

**Layout**:
```
┌─────────────────────────────────┐
│ HEADER1 │ HEADER2 │ HEADER3    │
├─────────┼─────────┼────────────┤
│ CUSTOMER│ VALUES  │ OTHER      │
│ INFO    │(Center) │ ELEMENTS   │
├─────────┼─────────┼────────────┤
│ OTHER   │ OTHER   │ OTHER      │
│ ELEM    │ ELEM    │ ELEM       │
└─────────┴─────────┴────────────┘
```

**Best For**: Organized, systematic presentations

**Element Placement**:
- Headers: Top row, distributed evenly
- Important Values: Center cell (row 1, col 1)
- Customer Info: Left column (rows 1-2)
- Other Elements: Remaining grid cells

**Grid Configuration**:
- 3 columns × 3 rows
- Elements centered within cells
- Symmetric distribution

---

### 5. Diagonal-Flow Strategy (Firma 5)

**Philosophy**: Progressive diagonal narrative

**Layout**:
```
┌─────────────────────────────────┐
│ ●                               │
│   ●                             │
│     ●                           │
│       ●                         │
│         ●                       │
│           ●                     │
│             ●                   │
│               ●                 │
│                 ●               │
│                   ●             │
│                     ●           │
│                       ●         │
└─────────────────────────────────┘
```

**Best For**: Dynamic, progressive narratives

**Element Placement**:
- All elements flow diagonally from top-left to bottom-right
- Headers appear first (top-left)
- Important values follow along diagonal
- Customer info continues the flow
- Other elements complete the diagonal

**Advantages**:
- Natural reading flow
- Minimal collisions
- Visually dynamic

---

### 6. Sidebar-Layout Strategy (Firma 6)

**Philosophy**: Clear two-column information separation

**Layout**:
```
┌─────────────────────────────────┐
│ LEFT SIDEBAR  │ RIGHT SIDEBAR   │
│               │                 │
│ ┌───────────┐ │ ┌────────────┐ │
│ │ HEADERS   │ │ │ VALUES     │ │
│ └───────────┘ │ │            │ │
│               │ │            │ │
│ ┌───────────┐ │ │            │ │
│ │ CUSTOMER  │ │ │            │ │
│ │ INFO      │ │ │            │ │
│ └───────────┘ │ │            │ │
│               │ │            │ │
│ ┌───────────┐ │ └────────────┘ │
│ │ OTHER     │ │                 │
│ │ ELEMENTS  │ │                 │
│ └───────────┘ │                 │
└─────────────────────────────────┘
```

**Best For**: Information-dense documents

**Element Placement**:
- Left Sidebar: Headers, customer info, other elements
- Right Sidebar: Important values and metrics
- Clear vertical separation at page center
- Each sidebar width: ~45% of page width

---

## Usage

### Automatic Strategy Selection

```python
from multi_pdf_positioning.positioning_strategies import apply_strategy
from multi_pdf_positioning.yml_parser import parse_yml
from multi_pdf_positioning.pdf_analyzer import analyze_pdf

# Parse files
elements = parse_yml("coords_multi/seite1_f1.yml")
pdf_analysis = analyze_pdf("pdf_templates_static/multi/multi_nt_01_f1.pdf")

# Apply strategy (automatically selects based on firma)
positions = apply_strategy(
    firma=pdf_analysis.firma,
    seite=pdf_analysis.seite,
    elements=elements,
    pdf_analysis=pdf_analysis
)
```

### Manual Strategy Selection

```python
from multi_pdf_positioning.positioning_strategies import (
    HeaderFocusedStrategy,
    select_strategy
)

# Option 1: Direct instantiation
strategy = HeaderFocusedStrategy(pdf_analysis)
positions = strategy.apply(elements)

# Option 2: Selection function
strategy = select_strategy(firma=1, seite=1, pdf_analysis=pdf_analysis)
positions = strategy.apply(elements)
```

### Integration with Position Calculator

```python
from multi_pdf_positioning.position_calculator import calculate_positions

# Automatically uses appropriate strategy
positions = calculate_positions(elements, pdf_analysis)
```

## Element Categorization

All strategies categorize elements into 4 groups:

### 1. Headers
Static labels and titles:
- "PHOTOVOLTAIK"
- "ANGEBOT"
- "ERSTELLT FÜR"
- "ÜBERSICHT"
- "ZUSAMMENFASSUNG"

### 2. Important Values
Dynamic data and metrics:
- kWp values
- Prices
- Energy yield
- Amortization
- Performance metrics

### 3. Customer Info
Customer-specific data:
- Customer name
- Address
- Date
- Contact person

### 4. Other
All remaining elements

## Configuration

### Default Settings

```python
margin = 50        # Points from page edge
spacing = 15       # Points between elements
page_width = 595   # A4 width in points
page_height = 842  # A4 height in points
```

### Customization

To customize a strategy, subclass and override:

```python
from multi_pdf_positioning.positioning_strategies import HeaderFocusedStrategy

class CustomStrategy(HeaderFocusedStrategy):
    def __init__(self, pdf_analysis):
        super().__init__(pdf_analysis)
        self.margin = 60      # Custom margin
        self.spacing = 20     # Custom spacing
```

## Performance

### Benchmarks (28 elements)

| Strategy | Time (ms) | Collisions |
|----------|-----------|------------|
| Header-Focused | 1.2 | 21 |
| Center-Prominent | 1.1 | 29 |
| Asymmetric-Modern | 1.3 | 29 |
| Grid-Based | 1.5 | 15 |
| Diagonal-Flow | 1.0 | 1 |
| Sidebar-Layout | 1.2 | 18 |

**Note**: Collision counts are for 28-element test case. Fewer elements result in fewer collisions.

## Best Practices

### 1. Choose Strategy Based on Content
- **Many values**: Use Grid-Based or Sidebar-Layout
- **Few elements**: Use Header-Focused or Center-Prominent
- **Dynamic content**: Use Diagonal-Flow
- **Modern design**: Use Asymmetric-Modern

### 2. Test with Real Data
Always test strategies with actual YML files to ensure proper positioning.

### 3. Validate Positions
Use the validation system to check for collisions and boundary violations:

```python
from multi_pdf_positioning.position_calculator import PositionCalculator

calculator = PositionCalculator()
is_valid, errors = calculator.validate_positions(positions)
```

### 4. Handle Collisions
If collisions occur, consider:
- Reducing element count
- Increasing spacing
- Using a different strategy
- Implementing custom collision resolution

## Troubleshooting

### Problem: Too Many Collisions
**Solution**: 
- Use Diagonal-Flow strategy (fewest collisions)
- Increase spacing parameter
- Reduce number of elements

### Problem: Elements Out of Bounds
**Solution**:
- Strategies automatically clamp to margins
- Check margin settings
- Verify page dimensions

### Problem: Poor Visual Balance
**Solution**:
- Try different strategy
- Adjust element categorization
- Customize margin/spacing

## Demo Script

Test all strategies interactively:

```bash
# Demo all strategies
python multi_pdf_positioning/demo_positioning_strategies.py --all

# Demo specific firma
python multi_pdf_positioning/demo_positioning_strategies.py --firma 1

# Interactive mode
python multi_pdf_positioning/demo_positioning_strategies.py
```

## API Reference

### Functions

#### `select_strategy(firma, seite, pdf_analysis)`
Select appropriate strategy for firma.

**Parameters**:
- `firma` (int): Firma number (1-6)
- `seite` (int): Seite number (1-8)
- `pdf_analysis` (PDFAnalysis): PDF analysis object

**Returns**: PositioningStrategy instance

**Raises**: ValueError if firma invalid

---

#### `apply_strategy(firma, seite, elements, pdf_analysis)`
Convenience function to select and apply strategy.

**Parameters**:
- `firma` (int): Firma number (1-6)
- `seite` (int): Seite number (1-8)
- `elements` (List[YMLElement]): Elements to position
- `pdf_analysis` (PDFAnalysis): PDF analysis object

**Returns**: List of position tuples

---

### Classes

All strategy classes inherit from `PositioningStrategy` and implement:

#### `apply(elements)`
Apply positioning strategy to elements.

**Parameters**:
- `elements` (List[YMLElement]): Elements to position

**Returns**: List[Tuple[float, float, float, float]]

---

## See Also

- [Task 5 Complete Documentation](TASK_5_COMPLETE.md)
- [Position Calculator Reference](POSITION_CALCULATOR_REFERENCE.md)
- [YML Parser Reference](YML_PARSER_REFERENCE.md)
- [PDF Analyzer Documentation](pdf_analyzer.py)

---

**Last Updated**: January 10, 2025
**Version**: 1.0.0
