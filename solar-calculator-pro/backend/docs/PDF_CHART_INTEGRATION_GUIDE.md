# PDF Chart Integration Guide

## Overview

The PDF Chart Service provides comprehensive chart rendering capabilities for PDF export with 10 different chart types, 5 color schemes, and full German number formatting support.

## Features

### 10 Chart Types

1. **PIE** - Kreisdiagramm (Pie Chart)
2. **DONUT** - Ringdiagramm (Donut Chart)
3. **BAR** - Horizontales Balkendiagramm (Horizontal Bar Chart)
4. **COLUMN** - Vertikales Säulendiagramm (Vertical Column Chart)
5. **LINE** - Liniendiagramm (Line Chart)
6. **AREA** - Flächendiagramm (Area Chart)
7. **CIRCLE** - Kreisfortschritt (Circle Progress Chart)
8. **POLAR** - Polardiagramm (Polar Chart)
9. **RADAR** - Netzdiagramm (Radar/Spider Chart)
10. **WATERFALL** - Wasserfalldiagramm (Waterfall Chart)

### 5 Color Schemes

1. **SOLAR** - Yellow, orange, red tones (perfect for solar energy)
2. **NATURE** - Green, blue, earth tones (environmental themes)
3. **PROFESSIONAL** - Blue, gray, corporate colors (business reports)
4. **VIBRANT** - Bright, high-contrast colors (presentations)
5. **MONOCHROME** - Grayscale variations (print-optimized)

### German Number Formatting

All numbers are formatted according to German locale:
- **Decimal separator**: Comma (,)
- **Thousand separator**: Dot (.)
- **Currency**: 16.999,00 €
- **Percentage**: 85,5%
- **Energy**: 12.500 kWh

### 3D Effects

Optional 3D effects can be enabled for enhanced visual appeal:
- 3D pie slices with popout effect
- Enhanced shadows and depth
- Optimized for print quality

## Installation

```python
from backend.services.pdf_chart_service import (
    PDFChartService,
    ChartType,
    ColorScheme
)

# Create service instance
service = PDFChartService()
```

## Usage Examples

### 1. Pie Chart

```python
# Prepare data
data = {
    'labels': ['PV-Module', 'Wechselrichter', 'Speicher', 'Installation'],
    'values': [8500, 3200, 4500, 2800]
}

# Generate chart
chart = service.generate_chart(
    ChartType.PIE,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.SOLAR,
    title="Kostenverteilung",
    show_legend=True,
    show_values=True
)
```

### 2. Donut Chart

```python
# Same data as pie chart
chart = service.generate_chart(
    ChartType.DONUT,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.NATURE,
    enable_3d=True
)
```

### 3. Bar Chart (Horizontal)

```python
data = {
    'categories': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun'],
    'series': [[1200, 1350, 1500, 1650, 1800, 1900]]
}

chart = service.generate_chart(
    ChartType.BAR,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.PROFESSIONAL,
    title="Monatliche Produktion",
    x_label="Produktion (kWh)",
    y_label="Monat"
)
```

### 4. Column Chart (Vertical)

```python
# Same data structure as bar chart
chart = service.generate_chart(
    ChartType.COLUMN,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.VIBRANT,
    x_label="Monat",
    y_label="Produktion (kWh)"
)
```

### 5. Line Chart

```python
data = {
    'categories': ['Q1', 'Q2', 'Q3', 'Q4'],
    'series': [[1000, 1200, 1100, 1400], [900, 1100, 1300, 1350]],
    'series_names': ['2023', '2024']
}

chart = service.generate_chart(
    ChartType.LINE,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.PROFESSIONAL,
    title="Quartalsproduktion",
    show_legend=True
)
```

### 6. Area Chart

```python
# Same data structure as line chart
chart = service.generate_chart(
    ChartType.AREA,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.SOLAR,
    enable_3d=True
)
```

### 7. Circle Chart (Progress)

```python
data = {
    'value': 85.5,
    'max_value': 100,
    'label': 'Effizienz'
}

chart = service.generate_chart(
    ChartType.CIRCLE,
    data,
    width=300,
    height=300,
    color_scheme=ColorScheme.NATURE,
    title="System-Effizienz",
    show_values=True
)
```

### 8. Polar Chart

```python
data = {
    'categories': ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW'],
    'values': [60, 70, 85, 90, 95, 90, 75, 65]
}

chart = service.generate_chart(
    ChartType.POLAR,
    data,
    width=400,
    height=400,
    color_scheme=ColorScheme.PROFESSIONAL,
    title="Ausrichtungsanalyse"
)
```

### 9. Radar Chart (Spider)

```python
data = {
    'categories': ['Leistung', 'Effizienz', 'Kosten', 'Wartung', 'Garantie'],
    'series': [[85, 90, 70, 80, 95], [75, 85, 85, 75, 90]],
    'series_names': ['Produkt A', 'Produkt B']
}

chart = service.generate_chart(
    ChartType.RADAR,
    data,
    width=400,
    height=400,
    color_scheme=ColorScheme.VIBRANT,
    title="Produktvergleich",
    show_legend=True
)
```

### 10. Waterfall Chart

```python
data = {
    'categories': ['Start', 'Einnahmen', 'Ausgaben', 'Steuern', 'Ende'],
    'values': [10000, 5000, -3000, -1000, 0]
}

chart = service.generate_chart(
    ChartType.WATERFALL,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.PROFESSIONAL,
    title="Cash-Flow-Analyse",
    show_values=True
)
```

## PDF Integration

### Generate PDF Bytes

```python
# Generate chart as PDF bytes
pdf_bytes = service.generate_chart_pdf_bytes(
    ChartType.PIE,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.SOLAR
)

# Save to file
with open('chart.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Position Chart Using YML Coordinates

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Create PDF canvas
pdf_canvas = canvas.Canvas("output.pdf", pagesize=A4)

# Generate chart
chart = service.generate_chart(ChartType.PIE, data, 400, 300)

# YML coordinates
yml_coords = {
    'x': 100,
    'y': 500,
    'width': 400,
    'height': 300
}

# Position chart on PDF
service.position_chart_from_yml(pdf_canvas, chart, yml_coords)

pdf_canvas.save()
```

## Number Formatting Methods

```python
# German number formatting
formatted = service.format_german_number(1234.56, 2)  # "1.234,56"

# Currency formatting
currency = service.format_currency(16999.00)  # "16.999,00 €"

# Percentage formatting
percentage = service.format_percentage(85.5)  # "85,5%"

# kWh formatting
kwh = service.format_kwh(12500)  # "12.500 kWh"
```

## Chart Options

### Common Options

- `width`: Chart width in points (default: 400)
- `height`: Chart height in points (default: 300)
- `color_scheme`: Color scheme enum (default: PROFESSIONAL)
- `enable_3d`: Enable 3D effects (default: False)
- `title`: Chart title string
- `show_legend`: Show legend (default: True)
- `show_values`: Show data values on chart (default: True)

### Axis Options (Bar, Column, Line, Area, Waterfall)

- `x_label`: X-axis label
- `y_label`: Y-axis label

## Data Structures

### Pie/Donut Chart Data

```python
{
    'labels': ['Label1', 'Label2', 'Label3'],
    'values': [value1, value2, value3]
}
```

### Bar/Column Chart Data

```python
{
    'categories': ['Cat1', 'Cat2', 'Cat3'],
    'series': [[val1, val2, val3]]  # Single or multiple series
}
```

### Line/Area Chart Data

```python
{
    'categories': ['Cat1', 'Cat2', 'Cat3'],
    'series': [[series1_vals], [series2_vals]],
    'series_names': ['Series 1', 'Series 2']
}
```

### Circle Chart Data

```python
{
    'value': 75,
    'max_value': 100,
    'label': 'Label'
}
```

### Polar/Radar Chart Data

```python
{
    'categories': ['Cat1', 'Cat2', 'Cat3'],
    'values': [val1, val2, val3]  # For polar
    # OR
    'series': [[series1], [series2]],  # For radar
    'series_names': ['Name1', 'Name2']
}
```

### Waterfall Chart Data

```python
{
    'categories': ['Cat1', 'Cat2', 'Cat3'],
    'values': [val1, val2, val3]  # Can be positive or negative
}
```

## Best Practices

1. **Choose Appropriate Chart Type**
   - Pie/Donut: Part-to-whole relationships
   - Bar/Column: Comparisons across categories
   - Line/Area: Trends over time
   - Circle: Single value progress
   - Polar/Radar: Multi-dimensional comparisons
   - Waterfall: Cumulative effects

2. **Color Scheme Selection**
   - SOLAR: Energy and sustainability reports
   - NATURE: Environmental data
   - PROFESSIONAL: Business presentations
   - VIBRANT: Marketing materials
   - MONOCHROME: Print documents

3. **German Formatting**
   - Always use provided formatting methods
   - Consistent decimal places (2 for currency, 1 for percentage)
   - Include units (€, %, kWh)

4. **3D Effects**
   - Use sparingly for emphasis
   - Better for presentations than technical reports
   - May increase file size

5. **Chart Sizing**
   - Standard: 400x300 points
   - Large: 600x400 points
   - Small: 300x200 points
   - Maintain aspect ratio

## Integration with Solar Calculator

```python
# Example: Generate production chart from calculation results
calculation_results = solar_calculator.calculate(...)

data = {
    'categories': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
    'series': [calculation_results['monthly_production']]
}

chart = service.generate_chart(
    ChartType.COLUMN,
    data,
    width=500,
    height=300,
    color_scheme=ColorScheme.SOLAR,
    title="Monatliche Energieproduktion",
    x_label="Monat",
    y_label="Produktion (kWh)"
)
```

## Troubleshooting

### Chart Not Displaying

- Check data structure matches chart type requirements
- Verify all required fields are present
- Ensure values are numeric

### Formatting Issues

- Use provided formatting methods
- Check decimal places parameter
- Verify locale settings

### PDF Generation Errors

- Ensure ReportLab is installed
- Check file permissions
- Verify PDF canvas is properly initialized

## Performance Considerations

- Chart generation is fast (<100ms per chart)
- PDF bytes generation adds ~50ms
- 3D effects add minimal overhead
- Large datasets (>100 points) may slow rendering

## Requirements

- Python 3.10+
- ReportLab 3.6+
- Standard library (math, io, enum)

## See Also

- [PDF Generation Service Guide](PDF_ADVANCED_SERVICE_GUIDE.md)
- [German Formatting Guide](../GERMAN_FORMATTING_GUIDE.md)
- [YML Coordinates System](YML_COORDINATES_GUIDE.md)
