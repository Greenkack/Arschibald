## Chart PDF Bytes Generation

## Overview

The Chart PDF Service provides comprehensive PDF generation for all chart types with automatic German number formatting. It supports line charts, bar charts, pie charts, area charts, and scatter plots.

## Requirements

- **14.8**: Chart PDF byte generation with German formatting

## Features

- **5 Chart Types**: Line, Bar, Pie, Area, Scatter
- **German Formatting**: Automatic formatting (1.234,56)
- **Multi-Series Support**: Multiple data series per chart
- **Custom Colors**: Configurable color palettes
- **Data Tables**: Automatic data tables with German formatting
- **Legends**: Automatic legend generation
- **Metadata Support**: Full PDF metadata support

## Installation

```bash
pip install reportlab
```

## Quick Start

### Line Chart

```python
from backend.services.chart_pdf_service import create_line_chart_pdf

pdf_bytes = create_line_chart_pdf(
    title="Sales Over Time",
    data=[[100, 150, 200, 250]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Revenue"]
)

# Save to file
with open("line_chart.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Bar Chart

```python
from backend.services.chart_pdf_service import create_bar_chart_pdf

pdf_bytes = create_bar_chart_pdf(
    title="Product Comparison",
    data=[[1000, 1500, 2000], [800, 1200, 1800]],
    labels=["Product A", "Product B", "Product C"],
    series_names=["2023", "2024"]
)
```

### Pie Chart

```python
from backend.services.chart_pdf_service import create_pie_chart_pdf

pdf_bytes = create_pie_chart_pdf(
    title="Market Share",
    data=[35, 25, 20, 15, 5],
    labels=["Product A", "Product B", "Product C", "Product D", "Others"]
)
```

### Area Chart

```python
from backend.services.chart_pdf_service import create_area_chart_pdf

pdf_bytes = create_area_chart_pdf(
    title="Cumulative Savings",
    data=[[500, 1000, 1500, 2000]],
    labels=["Year 1", "Year 2", "Year 3", "Year 4"],
    series_names=["Savings (€)"]
)
```

### Scatter Plot

```python
from backend.services.chart_pdf_service import create_scatter_plot_pdf

pdf_bytes = create_scatter_plot_pdf(
    title="Temperature vs Efficiency",
    data=[[20, 25, 30, 35], [95, 92, 88, 85]],
    labels=["Point 1", "Point 2", "Point 3", "Point 4"],
    series_names=["Temperature (°C)", "Efficiency (%)"]
)
```

## Core Components

### ChartData

Container for chart data with German formatting support:

```python
from backend.services.chart_pdf_service import ChartData

chart_data = ChartData(
    title="My Chart",
    data=[[100, 200, 300]],
    labels=["A", "B", "C"],
    series_names=["Series 1"],
    x_axis_label="Categories",
    y_axis_label="Values",
    colors=["#2E86AB", "#A23B72", "#F18F01"]
)

# Format values in German
formatted = chart_data.format_value(1234.56)  # "1.234,56"

# Format all data
formatted_data = chart_data.format_data_german()
```

### ChartPDFService

Main service for generating chart PDFs:

```python
from backend.services.chart_pdf_service import ChartPDFService
from backend.core.pdf_bytes import PDFMetadata

service = ChartPDFService()

# Create chart data
chart_data = ChartData(
    title="Sales Report",
    data=[[1000, 1500, 2000]],
    labels=["Q1", "Q2", "Q3"]
)

# Generate PDF with metadata
metadata = PDFMetadata(
    title="Sales Report Q1-Q3",
    author="John Doe",
    subject="Quarterly Sales",
    keywords=["sales", "report", "quarterly"]
)

pdf_bytes = service.create_line_chart_pdf(chart_data, metadata)
```

## German Number Formatting

All numbers are automatically formatted in German format:

```python
from backend.services.chart_pdf_service import ChartData

chart_data = ChartData(
    title="German Numbers",
    data=[[1234.56, 2345.67, 3456.78]],
    labels=["A", "B", "C"]
)

# Numbers in PDF will appear as:
# 1.234,56
# 2.345,67
# 3.456,78
```

### Formatting Examples

| Original | German Format |
|----------|---------------|
| 1234.56 | 1.234,56 |
| 1000000.99 | 1.000.000,99 |
| 0.5 | 0,50 |
| 15.75 | 15,75 |

## Advanced Usage

### Multiple Series

```python
from backend.services.chart_pdf_service import ChartPDFService, ChartData

service = ChartPDFService()

chart_data = ChartData(
    title="Multi-Series Comparison",
    data=[
        [100, 150, 200, 250],  # Series 1
        [80, 120, 180, 220],   # Series 2
        [90, 140, 190, 240]    # Series 3
    ],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Product A", "Product B", "Product C"]
)

pdf_bytes = service.create_line_chart_pdf(chart_data)
```

### Custom Colors

```python
chart_data = ChartData(
    title="Custom Colors",
    data=[[100, 200, 300]],
    labels=["A", "B", "C"],
    colors=["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue
)
```

### Axis Labels

```python
chart_data = ChartData(
    title="Energy Production",
    data=[[1000, 1200, 1400]],
    labels=["Jan", "Feb", "Mar"],
    x_axis_label="Month",
    y_axis_label="Energy (kWh)"
)
```

### With Metadata

```python
from backend.core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(
    title="Annual Report 2024",
    author="Solar Calculator Pro",
    subject="Energy Production Analysis",
    keywords=["solar", "energy", "production", "2024"],
    creator="Solar Calculator Pro"
)

pdf_bytes = service.create_line_chart_pdf(chart_data, metadata)
```

## Chart Types Details

### Line Chart

Best for showing trends over time:

```python
pdf_bytes = create_line_chart_pdf(
    title="Temperature Trend",
    data=[[20, 22, 25, 28, 30, 28, 25]],
    labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    series_names=["Temperature (°C)"]
)
```

**Features:**
- Multiple series support
- Trend visualization
- Time series data
- Continuous data

### Bar Chart

Best for comparing categories:

```python
pdf_bytes = create_bar_chart_pdf(
    title="Product Sales",
    data=[[1000, 1500, 2000]],
    labels=["Product A", "Product B", "Product C"],
    series_names=["Sales (€)"]
)
```

**Features:**
- Category comparison
- Multiple series
- Grouped bars
- Discrete data

### Pie Chart

Best for showing proportions:

```python
pdf_bytes = create_pie_chart_pdf(
    title="Market Share",
    data=[35, 25, 20, 15, 5],
    labels=["A", "B", "C", "D", "Others"]
)
```

**Features:**
- Percentage display
- Automatic total calculation
- Color-coded slices
- Legend with values

### Area Chart

Best for cumulative data:

```python
pdf_bytes = create_area_chart_pdf(
    title="Cumulative Revenue",
    data=[[100, 250, 450, 700]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Revenue (€)"]
)
```

**Features:**
- Filled areas
- Cumulative visualization
- Multiple series
- Trend emphasis

### Scatter Plot

Best for correlation analysis:

```python
pdf_bytes = create_scatter_plot_pdf(
    title="Price vs Quality",
    data=[[100, 150, 200, 250], [8.5, 9.0, 9.2, 9.5]],
    labels=["P1", "P2", "P3", "P4"],
    series_names=["Price (€)", "Quality Score"]
)
```

**Features:**
- Point markers
- Correlation visualization
- Multiple series
- No connecting lines

## Data Tables

All charts automatically include a data table with German-formatted numbers:

```python
# Line/Bar/Area/Scatter charts include:
# - Header row with series names
# - Data rows with category labels
# - German-formatted values

# Pie charts include:
# - Category column
# - Value column (German formatted)
# - Percentage column (German formatted)
# - Total row
```

## Integration Examples

### Solar Calculator Integration

```python
from backend.services.chart_pdf_service import create_line_chart_pdf

def generate_production_chart(monthly_production):
    """Generate solar production chart PDF"""
    pdf_bytes = create_line_chart_pdf(
        title="Monthly Solar Energy Production",
        data=[monthly_production],
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        series_names=["Production (kWh)"],
        x_axis_label="Month",
        y_axis_label="Energy Production (kWh)"
    )
    return pdf_bytes
```

### Financial Analysis Integration

```python
from backend.services.chart_pdf_service import create_area_chart_pdf

def generate_savings_chart(yearly_savings):
    """Generate cumulative savings chart PDF"""
    pdf_bytes = create_area_chart_pdf(
        title="Cumulative Energy Cost Savings",
        data=[yearly_savings],
        labels=[f"Year {i+1}" for i in range(len(yearly_savings))],
        series_names=["Savings (€)"],
        x_axis_label="Time Period",
        y_axis_label="Cumulative Savings (€)"
    )
    return pdf_bytes
```

### Market Analysis Integration

```python
from backend.services.chart_pdf_service import create_pie_chart_pdf

def generate_market_share_chart(market_data):
    """Generate market share pie chart PDF"""
    pdf_bytes = create_pie_chart_pdf(
        title="Solar Panel Market Share 2024",
        data=list(market_data.values()),
        labels=list(market_data.keys())
    )
    return pdf_bytes
```

## Error Handling

```python
from backend.services.chart_pdf_service import (
    ChartPDFService,
    REPORTLAB_AVAILABLE
)

if not REPORTLAB_AVAILABLE:
    print("Error: reportlab not installed")
    print("Install with: pip install reportlab")
else:
    service = ChartPDFService()
    try:
        pdf_bytes = service.create_line_chart_pdf(chart_data)
    except Exception as e:
        print(f"PDF generation failed: {e}")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_chart_pdf_service.py -v

# Run specific test class
pytest backend/tests/test_chart_pdf_service.py::TestChartPDFService -v

# Run with coverage
pytest backend/tests/test_chart_pdf_service.py \
    --cov=backend.services.chart_pdf_service
```

## Demo

Run the demo to see all chart types:

```bash
python backend/demo_chart_pdf.py
```

This will generate:
- `demo_line_chart.pdf`
- `demo_bar_chart.pdf`
- `demo_pie_chart.pdf`
- `demo_area_chart.pdf`
- `demo_scatter_plot.pdf`
- `demo_german_formatting.pdf`
- `demo_multi_series.pdf`

## Best Practices

1. **Use appropriate chart types** for your data
2. **Provide meaningful labels** for axes and series
3. **Use custom colors** for brand consistency
4. **Include metadata** for professional documents
5. **Test with various data sizes** (small, medium, large)
6. **Handle edge cases** (empty data, single points, zeros)
7. **Format numbers consistently** (German format throughout)

## Performance Considerations

- **Chart generation**: ~100-500ms per chart
- **PDF size**: ~50-200KB per chart
- **Memory usage**: Minimal (< 10MB)
- **Concurrent generation**: Thread-safe

## Limitations

- Maximum data points: ~1000 per series (for readability)
- Maximum series: ~10 (for legend clarity)
- Chart size: Fixed at 400x250 points
- Colors: 8 default colors (can be customized)

## API Reference

### ChartData

```python
ChartData(
    title: str,
    data: List[List[float]],
    labels: List[str],
    series_names: Optional[List[str]] = None,
    x_axis_label: str = "",
    y_axis_label: str = "",
    colors: Optional[List[str]] = None
)

# Methods
format_value(value: float, decimals: int = 2) -> str
format_data_german() -> List[List[str]]
```

### ChartPDFService

```python
ChartPDFService()

# Methods
create_line_chart_pdf(chart_data, metadata=None) -> bytes
create_bar_chart_pdf(chart_data, metadata=None) -> bytes
create_pie_chart_pdf(chart_data, metadata=None) -> bytes
create_area_chart_pdf(chart_data, metadata=None) -> bytes
create_scatter_plot_pdf(chart_data, metadata=None) -> bytes
```

### Convenience Functions

```python
create_line_chart_pdf(title, data, labels, series_names=None, **kwargs) -> bytes
create_bar_chart_pdf(title, data, labels, series_names=None, **kwargs) -> bytes
create_pie_chart_pdf(title, data, labels, **kwargs) -> bytes
create_area_chart_pdf(title, data, labels, series_names=None, **kwargs) -> bytes
create_scatter_plot_pdf(title, data, labels, series_names=None, **kwargs) -> bytes
```

## Troubleshooting

### ImportError: reportlab not installed

```bash
pip install reportlab
```

### Chart appears empty

Ensure data is not empty:

```python
chart_data = ChartData(
    title="Test",
    data=[[100, 200, 300]],  # Must have data
    labels=["A", "B", "C"]    # Must have labels
)
```

### Numbers not formatted correctly

The service automatically formats numbers. If you see issues, check:

```python
# Verify formatter is working
from backend.core.german_formatter import format_german
print(format_german(1234.56))  # Should print "1.234,56"
```

### PDF generation is slow

For large datasets, consider:
- Reducing data points
- Using fewer series
- Generating PDFs asynchronously

## Related Documentation

- [PDF Byte Generation](PDF_BYTE_GENERATION.md)
- [German Number Formatting](GERMAN_FORMATTING.md)
- [Universal Data Model](UNIVERSAL_DATA_MODEL.md)

## Support

For issues or questions, please refer to the main project documentation or create an issue in the project repository.
