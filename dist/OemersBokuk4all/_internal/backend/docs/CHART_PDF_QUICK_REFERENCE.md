# Chart PDF Generation - Quick Reference

## Installation

```bash
pip install reportlab
```

## Quick Examples

### Line Chart

```python
from backend.services.chart_pdf_service import create_line_chart_pdf

pdf_bytes = create_line_chart_pdf(
    title="Sales Trend",
    data=[[100, 150, 200, 250]],
    labels=["Q1", "Q2", "Q3", "Q4"],
    series_names=["Revenue"]
)
```

### Bar Chart

```python
from backend.services.chart_pdf_service import create_bar_chart_pdf

pdf_bytes = create_bar_chart_pdf(
    title="Product Comparison",
    data=[[1000, 1500, 2000]],
    labels=["A", "B", "C"]
)
```

### Pie Chart

```python
from backend.services.chart_pdf_service import create_pie_chart_pdf

pdf_bytes = create_pie_chart_pdf(
    title="Market Share",
    data=[35, 25, 20, 15, 5],
    labels=["A", "B", "C", "D", "E"]
)
```

### Area Chart

```python
from backend.services.chart_pdf_service import create_area_chart_pdf

pdf_bytes = create_area_chart_pdf(
    title="Cumulative Growth",
    data=[[100, 250, 450, 700]],
    labels=["Q1", "Q2", "Q3", "Q4"]
)
```

### Scatter Plot

```python
from backend.services.chart_pdf_service import create_scatter_plot_pdf

pdf_bytes = create_scatter_plot_pdf(
    title="Correlation",
    data=[[10, 20, 30], [15, 25, 35]],
    labels=["P1", "P2", "P3"]
)
```

## Common Patterns

### Save to File

```python
with open("chart.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### With Metadata

```python
from backend.core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(
    title="Report",
    author="John Doe"
)

pdf_bytes = create_line_chart_pdf(
    title="Chart",
    data=[[1, 2, 3]],
    labels=["A", "B", "C"],
    metadata=metadata
)
```

### Multiple Series

```python
pdf_bytes = create_line_chart_pdf(
    title="Multi-Series",
    data=[
        [100, 150, 200],  # Series 1
        [80, 120, 180]    # Series 2
    ],
    labels=["A", "B", "C"],
    series_names=["Series 1", "Series 2"]
)
```

### Custom Colors

```python
pdf_bytes = create_bar_chart_pdf(
    title="Custom Colors",
    data=[[1, 2, 3]],
    labels=["A", "B", "C"],
    colors=["#FF0000", "#00FF00", "#0000FF"]
)
```

## German Formatting

All numbers automatically formatted:

| Input | Output |
|-------|--------|
| 1234.56 | 1.234,56 |
| 1000000 | 1.000.000,00 |
| 0.5 | 0,50 |

## Chart Types

| Type | Best For |
|------|----------|
| Line | Trends over time |
| Bar | Category comparison |
| Pie | Proportions/percentages |
| Area | Cumulative data |
| Scatter | Correlations |

## Testing

```bash
# Run tests
pytest backend/tests/test_chart_pdf_service.py -v

# Run demo
python backend/demo_chart_pdf.py
```

## Common Issues

### ImportError

```bash
pip install reportlab
```

### Empty Chart

Ensure data and labels are provided:

```python
data=[[100, 200]],  # Not empty
labels=["A", "B"]   # Same length
```

## Full Documentation

See [CHART_PDF_GENERATION.md](CHART_PDF_GENERATION.md) for complete documentation.
