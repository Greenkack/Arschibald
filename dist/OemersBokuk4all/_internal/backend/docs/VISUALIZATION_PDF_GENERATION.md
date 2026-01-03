# Visualization PDF Bytes Generation

Complete guide for generating PDF bytes from various visualization types with German number formatting and dynamic keys.

## Overview

The `VisualizationPDFService` provides comprehensive PDF generation capabilities for:

- **3D Visualizations**: Solar panel layouts, building models, 3D scenes
- **Diagrams**: System architecture, component diagrams, network diagrams
- **Flowcharts**: Process flows, decision trees, workflow diagrams
- **Infographics**: Statistics, comparisons, visual data presentations
- **Dashboards**: Multi-chart layouts, KPI displays, performance metrics

All PDFs include:
- German number formatting (1.234,56)
- Dynamic keys for tracking and retrieval
- Professional layouts and styling
- Metadata support

## Installation

```python
from backend.services.visualization_pdf_service import VisualizationPDFService

service = VisualizationPDFService()
```

## 3D Visualization PDF Export

### Basic Usage

```python
viz_data = {
    'views': {
        'front': {
            'vertices': [[0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0]],
            'faces': [[[0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0]]],
            'title': 'Front View',
            'stats': {
                'Modules': 24,
                'Power (kWp)': 9.6
            }
        }
    },
    'modules': [{'id': 1}, {'id': 2}],
    'total_power': 9.6,
    'area_coverage': 45.2
}

pdf_bytes = service.create_3d_visualization_pdf(
    viz_data,
    title="Solar Panel 3D Layout",
    include_metadata=True
)
```

### With Metadata

```python
viz_data = {
    'views': {...},
    'metadata': {
        'Project': 'Residential Solar',
        'Location': 'Munich',
        'Date': '15.01.2024',
        'Module Type': 'Trina Solar 400W'
    }
}

pdf_bytes = service.create_3d_visualization_pdf(viz_data, include_metadata=True)
```

### Features

- Multiple view support (front, top, side, perspective)
- Module placement details
- Power and area statistics
- German-formatted numbers (9,60 kWp, 45,20 m²)
- Optional metadata page

## Diagram PDF Generation

### System Architecture Diagram

```python
diagram_data = {
    'nodes': [
        {
            'id': 'solar',
            'x': 0,
            'y': 4,
            'label': 'Solar Panels',
            'shape': 'rectangle',  # or 'circle'
            'color': '#fbbf24',
            'width': 2,
            'height': 1,
            'value': 9.6  # Will be formatted as 9,60
        },
        {
            'id': 'inverter',
            'x': 0,
            'y': 2,
            'label': 'Inverter',
            'shape': 'rectangle',
            'color': '#60a5fa'
        }
    ],
    'edges': [
        {
            'from': 'solar',
            'to': 'inverter',
            'label': 'DC Power',
            'color': 'gray'
        }
    ],
    'legend': {
        'items': [
            {'color': '#fbbf24', 'label': 'Generation'},
            {'color': '#60a5fa', 'label': 'Conversion'}
        ]
    }
}

pdf_bytes = service.create_diagram_pdf(
    diagram_data,
    diagram_type="system",
    title="Solar Energy System"
)
```

### Node Shapes

- `rectangle`: Standard rectangular node
- `circle`: Circular node

### Features

- Automatic arrow routing between nodes
- Edge labels
- Color-coded nodes
- Optional legend
- German-formatted numeric values

## Flowchart PDF Export

### Process Flow

```python
flowchart_data = {
    'steps': [
        {
            'id': 1,
            'x': 0,
            'y': 6,
            'type': 'start',  # start, end, process, decision
            'label': 'Start Installation'
        },
        {
            'id': 2,
            'x': 0,
            'y': 4,
            'type': 'process',
            'label': 'Site Assessment'
        },
        {
            'id': 3,
            'x': 0,
            'y': 2,
            'type': 'decision',
            'label': 'Roof Suitable?'
        }
    ],
    'connections': [
        {'from': 1, 'to': 2},
        {'from': 2, 'to': 3},
        {'from': 3, 'to': 4, 'label': 'No'},
        {'from': 3, 'to': 5, 'label': 'Yes'}
    ]
}

pdf_bytes = service.create_flowchart_pdf(
    flowchart_data,
    title="Installation Process"
)
```

### Step Types

- `start`: Rounded rectangle (green)
- `end`: Rounded rectangle (red)
- `process`: Rectangle (blue)
- `decision`: Diamond (yellow)

### Features

- Automatic shape rendering based on type
- Connection labels (Yes/No, etc.)
- Text wrapping for long labels
- Professional flowchart styling

## Infographic PDF Generation

### Statistics and Comparisons

```python
infographic_data = {
    'sections': [
        {
            'type': 'stat_box',
            'stats': [
                {
                    'value': 9876.54,  # Formatted as 9.876,54
                    'label': 'Annual Production',
                    'unit': 'kWh'
                },
                {
                    'value': 1234.56,  # Formatted as 1.234,56
                    'label': 'Cost Savings',
                    'unit': '€'
                }
            ]
        },
        {
            'type': 'text',
            'title': 'Environmental Impact',
            'text': 'This installation will offset 4.5 tons of CO₂...'
        },
        {
            'type': 'comparison',
            'title': 'Energy Sources',
            'items': [
                {'name': 'Solar', 'value': 95, 'max': 100},
                {'name': 'Wind', 'value': 75, 'max': 100}
            ]
        },
        {
            'type': 'chart',
            'chart_type': 'bar',  # bar, line, pie
            'data': {
                'x': ['Jan', 'Feb', 'Mar'],
                'y': [650, 720, 890],
                'title': 'Monthly Production'
            }
        }
    ]
}

pdf_bytes = service.create_infographic_pdf(
    infographic_data,
    title="Solar Impact Report"
)
```

### Section Types

1. **stat_box**: Large statistics with values, labels, and units
2. **text**: Text sections with optional titles
3. **comparison**: Progress bars comparing values
4. **chart**: Embedded charts (bar, line, pie)

### Features

- Color-coded stat boxes
- Progress bars with German-formatted values
- Embedded charts
- Professional infographic layout

## Dashboard PDF Export

### KPIs and Widgets

```python
dashboard_data = {
    'kpis': [
        {
            'value': 9876.54,  # Formatted as 9.876,54
            'label': 'Total Production (kWh)',
            'trend': 12.5  # Positive = green ▲, Negative = red ▼
        },
        {
            'value': 89.5,
            'label': 'Efficiency (%)',
            'trend': -2.1
        }
    ],
    'widgets': [
        {
            'title': 'Production Trend',
            'type': 'chart',
            'chart_type': 'line',
            'data': {
                'x': [1, 2, 3, 4, 5, 6],
                'y': [850, 920, 1050, 980, 1100, 1200],
                'title': 'Monthly Production'
            }
        },
        {
            'title': 'Distribution',
            'type': 'chart',
            'chart_type': 'pie',
            'data': {
                'x': ['Self-Use', 'Feed-in', 'Storage'],
                'y': [45, 35, 20]
            }
        }
    ]
}

pdf_bytes = service.create_dashboard_pdf(
    dashboard_data,
    title="Performance Dashboard"
)
```

### Features

- KPI cards with trend indicators
- Widget grid layout (2x2 or 2x3)
- Multiple chart types per dashboard
- Landscape orientation for better layout
- German-formatted numbers throughout

## Batch Export

### Export Multiple Visualizations

```python
visualizations = [
    {
        'type': '3d',
        'title': '3D Layout',
        'data': {...}
    },
    {
        'type': 'diagram',
        'title': 'System Diagram',
        'data': {...}
    },
    {
        'type': 'flowchart',
        'title': 'Process Flow',
        'data': {...}
    }
]

results = service.export_multiple_visualizations(
    visualizations,
    output_format="separate"  # or "combined"
)

# results is a dict: {dynamic_key: pdf_bytes}
for key, pdf_bytes in results.items():
    print(f"Generated: {key} ({len(pdf_bytes)} bytes)")
```

## German Number Formatting

All numeric values are automatically formatted with German locale:

```python
# Input: 1234.56
# Output in PDF: "1.234,56"

# Input: 9876543.21
# Output in PDF: "9.876.543,21"

# Always 2 decimal places
# Dot (.) as thousand separator
# Comma (,) as decimal separator
```

## Dynamic Keys

Every PDF gets a unique dynamic key for tracking:

```python
# Format: {type}_{timestamp}_{random}
# Examples:
# - "3d_viz_20240115_143022_abc123"
# - "diagram_20240115_143045_def456"
# - "dashboard_20240115_143102_ghi789"
```

Keys are included in the PDF metadata and can be used for:
- Tracking PDF generation
- Retrieving PDFs from storage
- Linking PDFs to database records
- Audit trails

## Base64 Encoding

Convert PDF bytes to base64 for transmission:

```python
pdf_bytes = service.create_dashboard_pdf(data)
base64_string = service.to_base64(pdf_bytes)

# Use in API responses, email attachments, etc.
```

## Error Handling

```python
try:
    pdf_bytes = service.create_3d_visualization_pdf(viz_data)
except ValueError as e:
    print(f"Invalid data: {e}")
except Exception as e:
    print(f"PDF generation failed: {e}")
```

## Best Practices

1. **Data Validation**: Validate input data before PDF generation
2. **Size Limits**: Keep visualizations reasonable in size
3. **Color Choices**: Use accessible color combinations
4. **Text Length**: Keep labels concise for better layout
5. **German Formatting**: All numbers use German locale automatically
6. **Dynamic Keys**: Store keys for later retrieval

## Performance Tips

1. **Batch Processing**: Use `export_multiple_visualizations()` for multiple PDFs
2. **Caching**: Cache generated PDFs if data doesn't change
3. **Async Generation**: Generate PDFs asynchronously for large datasets
4. **Compression**: PDFs are automatically optimized

## Examples

See `backend/demo_visualization_pdf.py` for complete working examples of all visualization types.

## API Integration

```python
from fastapi import APIRouter
from backend.services.visualization_pdf_service import VisualizationPDFService

router = APIRouter()
service = VisualizationPDFService()

@router.post("/api/v1/visualizations/3d/pdf")
async def generate_3d_pdf(data: dict):
    pdf_bytes = service.create_3d_visualization_pdf(data)
    return {
        "pdf_base64": service.to_base64(pdf_bytes),
        "size_bytes": len(pdf_bytes)
    }
```

## Support

For issues or questions:
- Check the demo script: `backend/demo_visualization_pdf.py`
- Review tests: `backend/tests/test_visualization_pdf_service.py`
- See examples in documentation
