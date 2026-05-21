# Multi-PDF Positioning Optimization System

## Overview

This system analyzes 48 PDF templates (6 firms × 8 pages) and optimizes the positioning of text elements in corresponding YML coordinate files. Each firm has a unique design, and the system creates individualized positioning strategies for optimal visual presentation.

## Project Structure

```
multi_pdf_positioning/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration and paths
├── yml_analyzer.py             # YML file analysis (Task 1)
├── pdf_inventory.py            # PDF template inventory (Task 1)
├── yml_parser.py               # YML parsing module (Task 2)
├── yml_format_preserver.py     # Format preservation (Task 2)
├── test_yml_parser.py          # YML parser tests (Task 2)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── TASK_1_COMPLETE.md          # Task 1 completion report
├── TASK_2_COMPLETE.md          # Task 2 completion report
├── analysis/                   # Analysis outputs
│   ├── yml_analysis.json
│   └── pdf_inventory.json
└── output/                     # Generated outputs
```

## Installation

All required packages are already installed in the main project:
- PyPDF2 >= 3.0.0
- PyYAML >= 6.0
- Pillow >= 10.0.0

## Data Structure Analysis

### YML File Structure

Each YML file contains text elements with the following attributes:

```yaml
Text: ERSTELLT FÜR:
Position: (48.0, 70.0, 220.0, 87.0)
Schriftart: Helvetica-Bold
Schriftgröße: 20.0
Farbe: 30920
----------------------------------------
```

**Attributes:**
- **Text**: The text content (static or dynamic placeholder)
- **Position**: Rectangle coordinates (x1, y1, x2, y2) in PDF points
- **Schriftart**: Font family (e.g., Helvetica-Bold, Helvetica-Regular)
- **Schriftgröße**: Font size in points
- **Farbe**: Color as integer value

**Element separator:** `----------------------------------------`

### Analysis Results

#### YML Files (48 total)
- **Total elements**: 2,262
  - Dynamic elements: 234 (placeholders like `kunde_vorname_und_nachname`)
  - Static elements: 1,656 (fixed text like "PHOTOVOLTAIK")
  - Empty elements: 372

- **Unique texts**:
  - 252 unique static texts
  - 34 unique dynamic placeholders

- **Fonts used**:
  - Helvetica
  - Helvetica-Bold
  - Helvetica-Medium
  - Helvetica-Regular

- **Font sizes**: Range from 6.0 to 100.0 points (75 unique sizes)

- **Colors**: 4 unique colors used

- **Position ranges**:
  - X: 33.14 - 730.66
  - Y: 40.60 - 920.00

#### PDF Templates (48 total)
- **All 48 PDFs found** ✓
- **All 48 YML mappings complete** ✓
- **Dimensions**:
  - 595.0 × 842.0 points (A4): 16 files
  - 595.3 × 841.9 points (A4): 32 files

### Per Firma Statistics

Each firma has 8 pages with 377 elements total:
- 39 dynamic elements
- 276 static elements
- 62 empty elements

### Per Seite Statistics

| Seite | Files | Total Elements | Dynamic | Static |
|-------|-------|----------------|---------|--------|
| 1     | 6     | 168            | 48      | 30     |
| 2     | 6     | 288            | 24      | 234    |
| 3     | 6     | 330            | 18      | 306    |
| 4     | 6     | 354            | 12      | 330    |
| 5     | 6     | 396            | 12      | 366    |
| 6     | 6     | 354            | 36      | 168    |
| 7     | 6     | 6              | 0       | 6      |
| 8     | 6     | 366            | 84      | 216    |

## Common Dynamic Placeholders

- `kunde_vorname_und_nachname` - Customer name
- `kunde_wohnort` - Customer city
- `anrede_kunde` - Customer salutation
- `kWp_anlage_anlage` - System kWp rating
- `langes_datum_heute` - Current date
- And 29 more...

## Common Static Texts

- "ERSTELLT FÜR:" - Created for
- "PHOTOVOLTAIK" - Photovoltaic
- "ANGEBOT" - Offer
- "erstellt am:" - Created on
- "Angebotsnummer:" - Offer number
- And 247 more...

## Usage

### Analyze YML Files (Task 1)

```bash
python -m multi_pdf_positioning.yml_analyzer
```

This will:
1. Parse all 48 YML files
2. Extract and categorize all text elements
3. Generate statistics
4. Save analysis to `analysis/yml_analysis.json`

### Inventory PDF Templates (Task 1)

```bash
python -m multi_pdf_positioning.pdf_inventory
```

This will:
1. List all PDF templates
2. Extract PDF metadata (dimensions, pages)
3. Validate PDF-YML mappings
4. Save inventory to `analysis/pdf_inventory.json`

### Parse YML Files (Task 2)

```python
from multi_pdf_positioning.yml_parser import parse_yml

# Parse a YML file
elements = parse_yml("coords_multi/seite1_f1.yml")

# Access element data
for elem in elements:
    print(f"Text: {elem.text}")
    print(f"Position: {elem.position}")
    print(f"Font: {elem.font} ({elem.font_size}pt)")
```

### Preserve YML Format (Task 2)

```python
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.yml_format_preserver import preserve_yml_format

# Parse original file
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# Create new positions
new_positions = [(x1+10, y1+10, x2+10, y2+10) 
                 for x1, y1, x2, y2 in [e.position for e in elements]]

# Generate new YML with preserved format
new_content = preserve_yml_format(
    "coords_multi/seite1_f1.yml",
    elements,
    new_positions
)
```

### Test YML Parser (Task 2)

```bash
python multi_pdf_positioning/test_yml_parser.py
```

This will:
1. Test YML parsing with multiple files
2. Test format preservation
3. Test integration of parser and preserver
4. Display comprehensive test results

### Analyze PDF Templates (Task 3)

```bash
# Analyze single PDF
python multi_pdf_positioning/pdf_analyzer.py pdf_templates_static/multi/multi_nt_01_f1.pdf

# Batch analyze all PDFs
python multi_pdf_positioning/batch_analyze_pdfs.py

# Run PDF analyzer tests
python multi_pdf_positioning/test_pdf_analyzer.py
```

This will:
1. Extract page dimensions and metadata
2. Identify design regions (header, content, footer)
3. Define safe zones for text placement
4. Extract color palettes per firma
5. Save analysis results to JSON

### Use PDF Analyzer in Code (Task 3)

```python
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer, analyze_pdf

# Analyze single PDF
analysis = analyze_pdf("pdf_templates_static/multi/multi_nt_01_f1.pdf")
print(f"Firma: {analysis.firma}, Seite: {analysis.seite}")
print(f"Colors: {analysis.color_palette}")
print(f"Safe zones: {len(analysis.safe_zones)}")

# Batch analysis
analyzer = PDFAnalyzer(pdf_dir="pdf_templates_static/multi")
results = analyzer.analyze_all_pdfs(firmen=[1, 2], seiten=[1, 2, 3])

# Filter results
firma1_results = analyzer.get_analysis_by_firma(1)
seite1_results = analyzer.get_analysis_by_seite(1)

# Save to JSON
analyzer.save_analysis_results("output/analysis.json", include_summary=True)
```

## File Naming Convention

### PDF Files
Format: `multi_nt_{seite:02d}_f{firma}.pdf`

Examples:
- `multi_nt_01_f1.pdf` - Firma 1, Seite 1
- `multi_nt_08_f6.pdf` - Firma 6, Seite 8

### YML Files
Format: `seite{seite}_f{firma}.yml`

Examples:
- `seite1_f1.yml` - Firma 1, Seite 1
- `seite8_f6.yml` - Firma 6, Seite 8

## Mapping Table

All 48 combinations are complete:

```
Seite | F1 | F2 | F3 | F4 | F5 | F6
------+----+----+----+----+----+----
  1   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  2   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  3   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  4   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  5   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  6   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  7   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
  8   | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  |
```

## Implementation Status

✅ **Task 1: Projekt-Setup und Datenstruktur-Analyse** - Complete  
✅ **Task 2: YML Parser implementieren** - Complete  
✅ **Task 3: PDF Analyzer implementieren** - Complete  
⏳ **Task 4: Position Calculator implementieren** - Next

### Completed Components

1. ✅ **YML Analyzer** - Analyzes all 48 YML files and extracts statistics
2. ✅ **PDF Inventory** - Inventories all 48 PDF templates and validates mappings
3. ✅ **YML Parser** - Parses YML files and extracts text elements with attributes
4. ✅ **Format Preserver** - Preserves original YML formatting when updating positions
5. ✅ **PDF Analyzer** - Analyzes PDF templates and extracts design characteristics

### Next Steps

The following components will be implemented in subsequent tasks:

1. **Position Calculator** - Calculate optimal positions based on design
2. **YML Generator** - Generate updated YML files with new positions
3. **Backup Manager** - Backup and restore functionality
4. **Validation System** - Validate generated positions
5. **Visualization Tools** - Visualize position changes

## Configuration

Edit `config.py` to customize:
- Directory paths
- Positioning rules (margins, spacing)
- Processing options (backup, validation, parallel processing)
- Logging configuration

## Notes

- All YML attributes except Position will remain unchanged
- Original YML formatting and structure will be preserved
- Backups will be created before any modifications
- Position coordinates are in PDF points (1/72 inch)


## Visualization and Statistics (Task 10)

### Visualization Tools

The system provides comprehensive visualization capabilities to compare old and new positions:

#### Create Overlay Images

```python
from multi_pdf_positioning.visualization_tool import VisualizationTool

tool = VisualizationTool()

# Create overlay showing old (red) and new (green) positions
tool.create_overlay_image(
    old_positions,
    new_positions,
    elements,
    output_path="overlay.png",
    title="Position Comparison - Firma 1, Seite 1"
)
```

#### Create Comparison Views

```python
# Side-by-side comparison
tool.create_comparison_view(
    old_positions,
    new_positions,
    elements,
    output_path="comparison.png",
    firma=1,
    seite=1
)
```

#### Create Movement Visualizations

```python
# Show movement arrows from old to new positions
tool.create_movement_visualization(
    old_positions,
    new_positions,
    elements,
    output_path="movement.png",
    title="Position Movement Analysis"
)
```

#### Create Collision Visualizations

```python
# Highlight collisions between elements
collisions = [(0, 1), (2, 3)]  # Element pairs that collide
tool.create_collision_visualization(
    positions,
    collisions,
    elements,
    output_path="collisions.png"
)
```

#### Generate Complete Visualization Report

```python
# Generate all visualization types at once
results = tool.generate_visualization_report(
    old_positions,
    new_positions,
    elements,
    output_dir="visualizations/",
    firma=1,
    seite=1
)

# Results contains paths to all generated images
print(f"Overlay: {results['overlay']}")
print(f"Comparison: {results['comparison']}")
print(f"Movement: {results['movement']}")
```

### Statistics Generation

The system generates detailed statistics about position optimizations:

#### Calculate Position Changes

```python
from multi_pdf_positioning.statistics_generator import StatisticsGenerator

generator = StatisticsGenerator()

# Calculate average position changes
stats = generator.calculate_average_position_changes(
    old_positions,
    new_positions,
    elements
)

print(f"Average distance moved: {stats['avg_distance_moved']:.2f} pts")
print(f"Max distance moved: {stats['max_distance_moved']:.2f} pts")
print(f"Average X change: {stats['avg_x_change']:.2f} pts")
print(f"Average Y change: {stats['avg_y_change']:.2f} pts")
```

#### Generate Strategy Statistics

```python
# Generate statistics for a specific strategy application
strategy_stats = generator.generate_strategy_statistics(
    strategy_name="header-focused",
    firma=1,
    seite=1,
    old_positions=old_positions,
    new_positions=new_positions,
    elements=elements,
    collisions_before=2,
    collisions_after=0,
    validation_errors=0,
    validation_warnings=1
)

print(f"Strategy: {strategy_stats.strategy_name}")
print(f"Elements: {strategy_stats.elements_count}")
print(f"Avg distance: {strategy_stats.avg_distance_moved:.2f} pts")
print(f"Collisions resolved: {strategy_stats.collisions_before - strategy_stats.collisions_after}")
```

#### Generate Optimization Summary

```python
# Generate overall optimization summary
summary = generator.generate_optimization_summary(
    strategy_statistics=[strategy_stats1, strategy_stats2, ...],
    position_changes=all_position_changes
)

# Print formatted summary
print(generator.format_summary(summary))

# Export to JSON
generator.export_to_json(summary, "optimization_summary.json")

# Export to CSV
generator.export_to_csv(summary, "optimization_summary.csv")
```

### CLI Usage for Visualization and Statistics

#### Generate Visualizations via CLI

```bash
# Create all visualization types for specific combination
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize

# Create specific visualization type
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --viz-type overlay

# Create visualizations for all combinations
python -m multi_pdf_positioning.cli --all --visualize --viz-output visualizations/
```

#### Generate Statistics via CLI

```bash
# Generate statistics for all combinations
python -m multi_pdf_positioning.cli --all --statistics

# Export statistics to JSON
python -m multi_pdf_positioning.cli --all --statistics --stats-format json --stats-output stats.json

# Export statistics to CSV
python -m multi_pdf_positioning.cli --all --statistics --stats-format csv --stats-output stats.csv

# Generate both visualizations and statistics
python -m multi_pdf_positioning.cli --all --visualize --statistics
```

### Visualization Configuration

Customize visualization appearance:

```python
from multi_pdf_positioning.visualization_tool import VisualizationConfig, VisualizationTool

# Create custom configuration
config = VisualizationConfig(
    scale_factor=3.0,  # Higher resolution
    old_position_color=(255, 0, 0),  # Red
    new_position_color=(0, 255, 0),  # Green
    collision_color=(255, 165, 0),  # Orange
    line_width=3,
    show_labels=True,
    show_indices=True,
    font_size=12
)

# Create tool with custom config
tool = VisualizationTool(config)
```

### Statistics Output Formats

#### Text Format (Human-Readable)

```
======================================================================
OPTIMIZATION SUMMARY
======================================================================
Generated: 2025-01-10T14:30:00

OVERALL STATISTICS
----------------------------------------------------------------------
  Total combinations processed: 48
  Total elements optimized: 1200
  Average distance moved: 45.30 pts
  Collisions resolved: 15
  Validation errors: 0
  Validation warnings: 3

STRATEGY DISTRIBUTION
----------------------------------------------------------------------
  header-focused: 8 (16.7%)
  center-prominent: 8 (16.7%)
  asymmetric-modern: 8 (16.7%)
  grid-based: 8 (16.7%)
  diagonal-flow: 8 (16.7%)
  sidebar-layout: 8 (16.7%)

TOP 10 POSITION CHANGES
----------------------------------------------------------------------
  1. Element 5 ('PHOTOVOLTAIK'): 125.45 pts
  2. Element 12 ('kWp_anlage_anlage'): 98.32 pts
  ...
```

#### JSON Format (Machine-Readable)

```json
{
  "timestamp": "2025-01-10T14:30:00",
  "total_combinations": 48,
  "total_elements": 1200,
  "avg_distance_moved": 45.3,
  "strategies_used": {
    "header-focused": 8,
    "center-prominent": 8
  },
  "strategy_statistics": [...],
  "position_changes": [...]
}
```

#### CSV Format (Spreadsheet-Compatible)

```csv
Strategy,Firma,Seite,Elements,Avg Distance Moved,Max Distance Moved,...
header-focused,1,1,25,45.30,125.45,...
center-prominent,2,1,25,38.20,98.32,...
```

## Complete Workflow Example

Here's a complete example showing all features:

```python
from multi_pdf_positioning.main_workflow import MainWorkflow
from multi_pdf_positioning.visualization_tool import VisualizationTool
from multi_pdf_positioning.statistics_generator import StatisticsGenerator

# Step 1: Run main workflow
workflow = MainWorkflow(
    create_backup=True,
    validate_output=True,
    show_progress=True
)

summary = workflow.run(firmen=[1, 2], seiten=[1, 2, 3])

# Step 2: Generate visualizations for each result
viz_tool = VisualizationTool()
stats_gen = StatisticsGenerator()

strategy_stats = []

for result in summary.results:
    if result.success:
        # Parse old and new YML files
        old_elements = parse_yml(result.yml_file)
        new_elements = parse_yml(f"output/{Path(result.yml_file).name}")
        
        old_positions = [e.position for e in old_elements]
        new_positions = [e.position for e in new_elements]
        
        # Create visualizations
        viz_tool.generate_visualization_report(
            old_positions,
            new_positions,
            old_elements,
            output_dir=f"visualizations/f{result.firma}_s{result.seite}/",
            firma=result.firma,
            seite=result.seite
        )
        
        # Generate statistics
        stat = stats_gen.generate_strategy_statistics(
            strategy_name=f"firma{result.firma}",
            firma=result.firma,
            seite=result.seite,
            old_positions=old_positions,
            new_positions=new_positions,
            elements=old_elements,
            collisions_before=len(result.validation_report.collisions) if result.validation_report else 0,
            collisions_after=0,
            validation_errors=len(result.validation_report.get_errors()) if result.validation_report else 0,
            validation_warnings=len(result.validation_report.get_warnings()) if result.validation_report else 0
        )
        strategy_stats.append(stat)

# Step 3: Generate overall summary
optimization_summary = stats_gen.generate_optimization_summary(strategy_stats)

# Step 4: Export results
print(stats_gen.format_summary(optimization_summary))
stats_gen.export_to_json(optimization_summary, "optimization_summary.json")
stats_gen.export_to_csv(optimization_summary, "optimization_summary.csv")

print(f"\n✓ Complete workflow finished!")
print(f"  Processed: {summary.successful}/{summary.total_combinations} combinations")
print(f"  Visualizations: visualizations/")
print(f"  Statistics: optimization_summary.json, optimization_summary.csv")
```

## Documentation

For detailed documentation, see:

- **[User Guide](USER_GUIDE.md)** - Comprehensive user documentation with CLI examples
- **[Positioning Strategies Reference](POSITIONING_STRATEGIES_REFERENCE.md)** - Detailed strategy documentation
- **[Validation System Reference](VALIDATION_SYSTEM_REFERENCE.md)** - Validation rules and error handling
- **[YML Parser Reference](YML_PARSER_REFERENCE.md)** - YML file format and parsing
- **[Backup Manager Reference](BACKUP_MANAGER_REFERENCE.md)** - Backup and restore functionality
- **[Visualization Tool Reference](docs/VISUALIZATION_TOOL_REFERENCE.md)** - Visualization API and examples
- **[Statistics Generator Reference](docs/STATISTICS_GENERATOR_REFERENCE.md)** - Statistics API and formats

## Implementation Status (Updated)

✅ **Task 1: Projekt-Setup und Datenstruktur-Analyse** - Complete  
✅ **Task 2: YML Parser implementieren** - Complete  
✅ **Task 3: PDF Analyzer implementieren** - Complete  
✅ **Task 4: Position Calculator implementieren** - Complete  
✅ **Task 5: Positionierungs-Strategien implementieren** - Complete  
✅ **Task 6: YML Generator implementieren** - Complete  
✅ **Task 7: Backup Manager implementieren** - Complete  
✅ **Task 8: Validierungs-System implementieren** - Complete  
✅ **Task 9: Haupt-Orchestrierung implementieren** - Complete  
✅ **Task 10: Visualisierung und Dokumentation** - Complete

### All Components Implemented

1. ✅ **YML Analyzer** - Analyzes all 48 YML files and extracts statistics
2. ✅ **PDF Inventory** - Inventories all 48 PDF templates and validates mappings
3. ✅ **YML Parser** - Parses YML files and extracts text elements with attributes
4. ✅ **Format Preserver** - Preserves original YML formatting when updating positions
5. ✅ **PDF Analyzer** - Analyzes PDF templates and extracts design characteristics
6. ✅ **Position Calculator** - Calculates optimal positions with collision detection
7. ✅ **Positioning Strategies** - 6 unique strategies for each firma
8. ✅ **YML Generator** - Generates updated YML files with preserved formatting
9. ✅ **Backup Manager** - Backup and restore functionality with validation
10. ✅ **Validation System** - Comprehensive position validation with reporting
11. ✅ **Main Workflow** - Complete orchestration with progress tracking
12. ✅ **Batch Processor** - Parallel processing of multiple combinations
13. ✅ **CLI Interface** - Command-line interface with all options
14. ✅ **Visualization Tool** - Multiple visualization types for position comparison
15. ✅ **Statistics Generator** - Detailed statistics and optimization reports

## System Ready for Production

The Multi-PDF Positioning System is now complete and ready for production use. All 48 combinations can be processed with:

```bash
python -m multi_pdf_positioning.cli --all --visualize --statistics
```

This will:
1. ✅ Create backup of all YML files
2. ✅ Analyze all 48 PDF templates
3. ✅ Calculate optimal positions using appropriate strategies
4. ✅ Generate new YML files with preserved formatting
5. ✅ Validate all positions
6. ✅ Create visualizations for each combination
7. ✅ Generate comprehensive statistics
8. ✅ Export results in multiple formats

**Total Processing Time**: ~3-5 minutes for all 48 combinations

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0  
**Status**: Production Ready ✅
