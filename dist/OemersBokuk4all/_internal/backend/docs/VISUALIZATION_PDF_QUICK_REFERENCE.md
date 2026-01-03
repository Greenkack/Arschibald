# Visualization PDF - Quick Reference

Fast reference for generating visualization PDFs with German formatting.

## Quick Start

```python
from backend.services.visualization_pdf_service import VisualizationPDFService

service = VisualizationPDFService()
```

## 3D Visualization

```python
viz_data = {
    'views': {
        'front': {
            'vertices': [[0,0,0], [10,0,0], [10,8,0], [0,8,0]],
            'faces': [[[0,0,0], [10,0,0], [10,8,0], [0,8,0]]],
            'stats': {'Power': 9.6}
        }
    },
    'total_power': 9.6,
    'area_coverage': 45.2
}

pdf = service.create_3d_visualization_pdf(viz_data, "3D Layout")
```

## Diagram

```python
diagram_data = {
    'nodes': [
        {'id': 'A', 'x': 0, 'y': 0, 'label': 'Node A', 'shape': 'rectangle'},
        {'id': 'B', 'x': 3, 'y': 0, 'label': 'Node B', 'shape': 'circle'}
    ],
    'edges': [
        {'from': 'A', 'to': 'B', 'label': 'Connection'}
    ]
}

pdf = service.create_diagram_pdf(diagram_data, title="System Diagram")
```

## Flowchart

```python
flowchart_data = {
    'steps': [
        {'id': 1, 'x': 0, 'y': 0, 'type': 'start', 'label': 'Start'},
        {'id': 2, 'x': 0, 'y': -2, 'type': 'process', 'label': 'Process'},
        {'id': 3, 'x': 0, 'y': -4, 'type': 'decision', 'label': 'Decision?'},
        {'id': 4, 'x': 0, 'y': -6, 'type': 'end', 'label': 'End'}
    ],
    'connections': [
        {'from': 1, 'to': 2},
        {'from': 2, 'to': 3},
        {'from': 3, 'to': 4, 'label': 'Yes'}
    ]
}

pdf = service.create_flowchart_pdf(flowchart_data, "Process Flow")
```

## Infographic

```python
infographic_data = {
    'sections': [
        {
            'type': 'stat_box',
            'stats': [
                {'value': 1234.56, 'label': 'Revenue', 'unit': '€'},
                {'value': 9876.54, 'label': 'Production', 'unit': 'kWh'}
            ]
        },
        {
            'type': 'comparison',
            'title': 'Comparison',
            'items': [
                {'name': 'Solar', 'value': 95, 'max': 100},
                {'name': 'Wind', 'value': 75, 'max': 100}
            ]
        },
        {
            'type': 'chart',
            'chart_type': 'bar',
            'data': {
                'x': ['Jan', 'Feb', 'Mar'],
                'y': [100, 150, 200],
                'title': 'Monthly Data'
            }
        }
    ]
}

pdf = service.create_infographic_pdf(infographic_data, "Report")
```

## Dashboard

```python
dashboard_data = {
    'kpis': [
        {'value': 1234.56, 'label': 'Revenue', 'trend': 12.5},
        {'value': 89.5, 'label': 'Efficiency', 'trend': -2.1}
    ],
    'widgets': [
        {
            'title': 'Trend',
            'type': 'chart',
            'chart_type': 'line',
            'data': {
                'x': [1, 2, 3, 4],
                'y': [100, 120, 110, 130]
            }
        }
    ]
}

pdf = service.create_dashboard_pdf(dashboard_data, "Dashboard")
```

## Batch Export

```python
visualizations = [
    {'type': 'diagram', 'title': 'Diagram 1', 'data': {...}},
    {'type': 'flowchart', 'title': 'Flow 1', 'data': {...}}
]

results = service.export_multiple_visualizations(visualizations)
# Returns: {dynamic_key: pdf_bytes}
```

## Common Patterns

### Save to File

```python
pdf_bytes = service.create_dashboard_pdf(data)

with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Convert to Base64

```python
pdf_bytes = service.create_diagram_pdf(data)
base64_str = service.to_base64(pdf_bytes)
```

### Get PDF Size

```python
pdf_bytes = service.create_3d_visualization_pdf(data)
size_kb = len(pdf_bytes) / 1024
print(f"PDF size: {size_kb:.2f} KB")
```

## German Formatting

All numbers automatically formatted:

```python
# Input: 1234.56  →  Output: "1.234,56"
# Input: 9876543.21  →  Output: "9.876.543,21"
```

## Node Shapes

- `rectangle`: Standard box
- `circle`: Round node

## Step Types

- `start`: Green rounded box
- `end`: Red rounded box
- `process`: Blue rectangle
- `decision`: Yellow diamond

## Chart Types

- `line`: Line chart
- `bar`: Bar chart
- `pie`: Pie chart

## Section Types

- `stat_box`: Large statistics
- `text`: Text content
- `comparison`: Progress bars
- `chart`: Embedded chart

## Dynamic Keys

Format: `{type}_{timestamp}_{random}`

Examples:
- `3d_viz_20240115_143022_abc123`
- `diagram_20240115_143045_def456`

## Error Handling

```python
try:
    pdf = service.create_dashboard_pdf(data)
except ValueError as e:
    print(f"Invalid data: {e}")
except Exception as e:
    print(f"Generation failed: {e}")
```

## Tips

✓ Validate data before generation  
✓ Keep labels concise  
✓ Use accessible colors  
✓ Store dynamic keys  
✓ Cache generated PDFs  

## Examples

Run demo: `python backend/demo_visualization_pdf.py`

## See Also

- Full documentation: `VISUALIZATION_PDF_GENERATION.md`
- Tests: `backend/tests/test_visualization_pdf_service.py`
- Demo: `backend/demo_visualization_pdf.py`
