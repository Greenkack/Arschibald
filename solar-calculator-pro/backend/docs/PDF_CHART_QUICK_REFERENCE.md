# PDF Chart Integration - Quick Reference

## Quick Start

```python
from backend.services.pdf_chart_service import PDFChartService, ChartType, ColorScheme

service = PDFChartService()
```

## Chart Types

| Type | Use Case | Data Format |
|------|----------|-------------|
| PIE | Part-to-whole | labels + values |
| DONUT | Part-to-whole with center | labels + values |
| BAR | Horizontal comparison | categories + series |
| COLUMN | Vertical comparison | categories + series |
| LINE | Trends over time | categories + series + names |
| AREA | Filled trends | categories + series + names |
| CIRCLE | Single progress | value + max_value + label |
| POLAR | Directional data | categories + values |
| RADAR | Multi-dimensional | categories + series + names |
| WATERFALL | Cumulative changes | categories + values |

## Color Schemes

- `SOLAR` - Yellow/Orange/Red (energy themes)
- `NATURE` - Green/Blue/Earth (environmental)
- `PROFESSIONAL` - Blue/Gray (business)
- `VIBRANT` - Bright colors (presentations)
- `MONOCHROME` - Grayscale (print)

## Common Patterns

### Generate Simple Chart

```python
data = {'labels': ['A', 'B', 'C'], 'values': [30, 40, 30]}
chart = service.generate_chart(ChartType.PIE, data, 400, 300)
```

### Generate with Options

```python
chart = service.generate_chart(
    ChartType.COLUMN,
    data,
    width=400,
    height=300,
    color_scheme=ColorScheme.SOLAR,
    enable_3d=True,
    title="My Chart",
    x_label="X Axis",
    y_label="Y Axis",
    show_legend=True,
    show_values=True
)
```

### Generate PDF Bytes

```python
pdf_bytes = service.generate_chart_pdf_bytes(ChartType.PIE, data, 400, 300)
```

### Position on PDF

```python
yml_coords = {'x': 100, 'y': 500}
service.position_chart_from_yml(pdf_canvas, chart, yml_coords)
```

## German Formatting

```python
service.format_german_number(1234.56, 2)  # "1.234,56"
service.format_currency(16999.00)          # "16.999,00 €"
service.format_percentage(85.5)            # "85,5%"
service.format_kwh(12500)                  # "12.500 kWh"
```

## Data Structures

### Pie/Donut
```python
{'labels': ['A', 'B'], 'values': [50, 50]}
```

### Bar/Column
```python
{'categories': ['Jan', 'Feb'], 'series': [[100, 150]]}
```

### Line/Area
```python
{
    'categories': ['Q1', 'Q2'],
    'series': [[100, 150], [90, 140]],
    'series_names': ['2023', '2024']
}
```

### Circle
```python
{'value': 75, 'max_value': 100, 'label': 'Progress'}
```

### Polar/Radar
```python
{
    'categories': ['N', 'E', 'S', 'W'],
    'values': [80, 70, 90, 75]  # Polar
    # OR
    'series': [[80, 70, 90, 75]],  # Radar
    'series_names': ['Series 1']
}
```

### Waterfall
```python
{
    'categories': ['Start', 'Add', 'Subtract', 'End'],
    'values': [1000, 500, -300, 0]
}
```

## Common Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| width | float | 400 | Chart width in points |
| height | float | 300 | Chart height in points |
| color_scheme | ColorScheme | PROFESSIONAL | Color palette |
| enable_3d | bool | False | Enable 3D effects |
| title | str | "" | Chart title |
| x_label | str | "" | X-axis label |
| y_label | str | "" | Y-axis label |
| show_legend | bool | True | Display legend |
| show_values | bool | True | Display data values |

## Chart Sizes

- **Small**: 300x200
- **Standard**: 400x300
- **Large**: 600x400
- **Full Width**: 500x300

## Best Practices

✅ **DO:**
- Use appropriate chart type for data
- Apply German formatting consistently
- Choose color scheme matching theme
- Include clear titles and labels
- Test with real data

❌ **DON'T:**
- Mix formatting styles
- Overuse 3D effects
- Create charts too small to read
- Use too many colors
- Forget axis labels

## Integration Examples

### With Solar Calculator
```python
results = calculator.calculate(...)
data = {
    'categories': months,
    'series': [results['production']]
}
chart = service.generate_chart(ChartType.COLUMN, data, 500, 300)
```

### With Price Matrix
```python
data = {
    'labels': price_matrix.get_categories(),
    'values': price_matrix.get_values()
}
chart = service.generate_chart(ChartType.PIE, data, 400, 300)
```

### With PDF Generator
```python
from reportlab.pdfgen import canvas

c = canvas.Canvas("report.pdf")
chart = service.generate_chart(ChartType.LINE, data, 400, 300)
chart.drawOn(c, 100, 500)
c.save()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chart not showing | Check data structure |
| Wrong formatting | Use service methods |
| PDF error | Verify ReportLab installed |
| Colors wrong | Check color scheme enum |
| Size issues | Adjust width/height |

## Performance

- Chart generation: <100ms
- PDF bytes: +50ms
- 3D effects: +10ms
- Large datasets (>100 points): +100ms

## Requirements

```
reportlab>=3.6.0
```

## See Also

- [Full Guide](PDF_CHART_INTEGRATION_GUIDE.md)
- [API Reference](API_DOCUMENTATION.md)
- [Examples](../demo_pdf_charts.py)
