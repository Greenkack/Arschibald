# PDF Byte Generation Core

## Overview

The PDF Byte Generation Core provides a comprehensive system for generating PDF documents from any data model. It includes mixins, rendering engines, and utilities for creating professional PDF documents with German number formatting.

## Requirements

- **14.5**: PDF byte generation for all data types
- **14.8**: PDF rendering engine with metadata system

## Features

- **PDFByteMixin**: Add PDF generation capabilities to any class
- **PDFRenderingEngine**: Core rendering engine with German formatting
- **PDFMetadata**: Comprehensive metadata management
- **Utility Functions**: Quick PDF generation from dicts and text
- **German Number Formatting**: Automatic formatting (1.234,56)

## Installation

```bash
pip install reportlab
```

## Quick Start

### Using PDFByteMixin

```python
from core.pdf_bytes import PDFByteMixin, PDFMetadata
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class MyDataModel(PDFByteMixin):
    def __init__(self, title, data):
        super().__init__()
        self.title = title
        self.data = data
    
    def _get_default_title(self):
        return self.title
    
    def _render_to_pdf(self, story, doc):
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add data
        for key, value in self.data.items():
            text = f"<b>{key}:</b> {value}"
            story.append(Paragraph(text, styles['BodyText']))

# Usage
model = MyDataModel("Report", {"Price": 1234.56, "Quantity": 100})

# Generate PDF bytes
pdf_bytes = model.to_pdf_bytes()

# Generate base64-encoded PDF
pdf_base64 = model.to_pdf_base64()

# Save to file
model.save_pdf("report.pdf")
```

### Using Utility Functions

```python
from core.pdf_bytes import create_pdf_from_dict, create_pdf_from_text

# Create PDF from dictionary
data = {
    "Customer": "John Doe",
    "Price": 1234.56,
    "Total": 123456.00
}
pdf_bytes = create_pdf_from_dict(data, title="Invoice")

# Create PDF from text
text = "This is my document content.\n\nWith multiple paragraphs."
pdf_bytes = create_pdf_from_text(text, title="Document")
```

## Core Components

### PDFMetadata

Manages PDF document metadata:

```python
from core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(
    title="Sales Report",
    author="John Doe",
    subject="Q4 2024 Sales",
    creator="Solar Calculator Pro",
    keywords=["sales", "report", "Q4"]
)

# Convert to dictionary
metadata_dict = metadata.to_dict()
```

### PDFRenderingEngine

Core rendering engine with utilities:

```python
from core.pdf_bytes import PDFRenderingEngine
import io

engine = PDFRenderingEngine()

# Format German numbers
formatted = engine.format_german_number(1234.56)  # "1.234,56"

# Create document
buffer = io.BytesIO()
doc = engine.create_document(buffer, metadata)

# Create table
data = [
    ['Product', 'Price', 'Quantity'],
    ['Solar Panel', '1.234,56', '100'],
    ['Inverter', '2.345,67', '50']
]
table = engine.create_table(data)
```

### PDFByteMixin

Base mixin for adding PDF generation to any class:

```python
from core.pdf_bytes import PDFByteMixin
from abc import ABC

class MyModel(PDFByteMixin):
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def _render_to_pdf(self, story, doc):
        # Implement your PDF rendering logic
        pass
    
    def _get_default_title(self):
        return "My Document"
    
    def _get_default_subject(self):
        return "Generated Report"

# Usage
model = MyModel({"test": "data"})

# Set custom metadata
metadata = PDFMetadata(title="Custom Title")
model.set_pdf_metadata(metadata)

# Generate PDF
pdf_bytes = model.to_pdf_bytes()
pdf_base64 = model.to_pdf_base64()
model.save_pdf("output.pdf")
```

## German Number Formatting

The system automatically formats numbers in German format:

```python
from core.pdf_bytes import PDFRenderingEngine

engine = PDFRenderingEngine()

# Format numbers
engine.format_german_number(1234.56)      # "1.234,56"
engine.format_german_number(1000000.99)   # "1.000.000,99"
engine.format_german_number(0.5)          # "0,50"

# Custom decimal places
engine.format_german_number(1234.567, decimals=3)  # "1.234,567"
engine.format_german_number(1234.5, decimals=0)    # "1.235"
```

## Advanced Usage

### Custom Canvas Rendering

For low-level control, override `_render_to_canvas`:

```python
class CustomPDFModel(PDFByteMixin):
    def _render_to_canvas(self, canvas_obj):
        # Low-level drawing
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.drawString(100, 750, "Custom Text")
        canvas_obj.line(100, 740, 500, 740)

# Use canvas rendering
model = CustomPDFModel()
pdf_bytes = model.to_pdf_canvas()
```

### Adding Headers and Footers

```python
from core.pdf_bytes import PDFRenderingEngine
import io

engine = PDFRenderingEngine()
buffer = io.BytesIO()
canvas = engine.create_canvas(buffer)

# Add header
engine.add_header(canvas, "My Report Header")

# Add footer with page number
engine.add_footer(canvas, "Company Name", page_number=1)

canvas.save()
```

### Creating Tables

```python
from core.pdf_bytes import PDFRenderingEngine
from reportlab.lib import colors

engine = PDFRenderingEngine()

# Data with German-formatted numbers
data = [
    ['Product', 'Price (€)', 'Quantity', 'Total (€)'],
    ['Solar Panel', '1.234,56', '100', '123.456,00'],
    ['Inverter', '2.345,67', '50', '117.283,50']
]

# Custom style
style = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Right-align numbers
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]

table = engine.create_table(data, style=style)
```

## Integration with Data Models

### Example: Solar Calculation Result

```python
from core.pdf_bytes import PDFByteMixin, PDFMetadata
from reportlab.platypus import Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

class SolarCalculationResult(PDFByteMixin):
    def __init__(self, system_size, module_count, annual_production, 
                 total_cost, savings):
        super().__init__()
        self.system_size = system_size
        self.module_count = module_count
        self.annual_production = annual_production
        self.total_cost = total_cost
        self.savings = savings
    
    def _get_default_title(self):
        return "Solar System Calculation"
    
    def _render_to_pdf(self, story, doc):
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph("Solar System Calculation", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Results table
        data = [
            ['Parameter', 'Value'],
            ['System Size', f"{self._pdf_engine.format_german_number(self.system_size)} kWp"],
            ['Module Count', str(self.module_count)],
            ['Annual Production', f"{self._pdf_engine.format_german_number(self.annual_production)} kWh"],
            ['Total Cost', f"{self._pdf_engine.format_german_number(self.total_cost)} €"],
            ['25-Year Savings', f"{self._pdf_engine.format_german_number(self.savings)} €"]
        ]
        
        table = self._pdf_engine.create_table(data)
        story.append(table)

# Usage
result = SolarCalculationResult(
    system_size=10.5,
    module_count=30,
    annual_production=12000.50,
    total_cost=15000.00,
    savings=45000.75
)

# Generate PDF with metadata
metadata = PDFMetadata(
    title="Solar Calculation - Customer XYZ",
    author="Solar Calculator Pro",
    subject="Solar System Sizing",
    keywords=["solar", "calculation", "pv"]
)

pdf_bytes = result.to_pdf_bytes(metadata)
result.save_pdf("solar_calculation.pdf", metadata)
```

## Error Handling

```python
from core.pdf_bytes import PDFByteMixin, REPORTLAB_AVAILABLE

if not REPORTLAB_AVAILABLE:
    print("Warning: reportlab not installed. PDF generation unavailable.")
else:
    # Safe to use PDF generation
    model = MyPDFModel()
    try:
        pdf_bytes = model.to_pdf_bytes()
    except Exception as e:
        print(f"PDF generation failed: {e}")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_pdf_bytes.py -v

# Run specific test class
pytest backend/tests/test_pdf_bytes.py::TestPDFByteMixin -v

# Run with coverage
pytest backend/tests/test_pdf_bytes.py --cov=backend.core.pdf_bytes
```

## Best Practices

1. **Always set metadata** for professional documents
2. **Use German formatting** for all numbers in German locale
3. **Implement _render_to_pdf** for custom content
4. **Test PDF generation** with various data types
5. **Handle missing reportlab** gracefully
6. **Use tables** for structured data
7. **Add headers/footers** for multi-page documents

## API Reference

### PDFMetadata

```python
PDFMetadata(
    title: str = "",
    author: str = "",
    subject: str = "",
    creator: str = "Solar Calculator Pro",
    keywords: List[str] = None,
    creation_date: Optional[datetime] = None
)
```

### PDFRenderingEngine

```python
PDFRenderingEngine(page_size=A4)

# Methods
create_document(buffer, metadata) -> SimpleDocTemplate
create_canvas(buffer, metadata) -> Canvas
add_header(canvas_obj, text, y_position)
add_footer(canvas_obj, text, page_number)
format_german_number(value, decimals=2) -> str
create_table(data, col_widths, style) -> Table
```

### PDFByteMixin

```python
# Methods
to_pdf_bytes(metadata=None) -> bytes
to_pdf_base64(metadata=None) -> str
to_pdf_canvas(metadata=None) -> bytes
save_pdf(filepath, metadata=None)
set_pdf_metadata(metadata)
get_pdf_metadata() -> PDFMetadata

# Abstract methods (must implement)
_render_to_pdf(story, doc)

# Optional overrides
_render_to_canvas(canvas_obj)
_get_default_title() -> str
_get_default_subject() -> str
```

### Utility Functions

```python
create_pdf_from_dict(
    data: Dict[str, Any],
    title: str = "Data Report",
    metadata: Optional[PDFMetadata] = None
) -> bytes

create_pdf_from_text(
    text: str,
    title: str = "Document",
    metadata: Optional[PDFMetadata] = None
) -> bytes
```

## Troubleshooting

### ImportError: reportlab not installed

```bash
pip install reportlab
```

### PDF appears empty

Ensure you're implementing `_render_to_pdf` and adding elements to the story:

```python
def _render_to_pdf(self, story, doc):
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    
    styles = getSampleStyleSheet()
    story.append(Paragraph("Content", styles['BodyText']))
```

### Numbers not formatted correctly

Use the engine's `format_german_number` method:

```python
formatted = self._pdf_engine.format_german_number(1234.56)
# Result: "1.234,56"
```

## Related Documentation

- [Dynamic Keys System](DYNAMIC_KEY_SYSTEM.md)
- [German Number Formatting](GERMAN_FORMATTING.md)
- [Universal Data Model](UNIVERSAL_DATA_MODEL.md)

## Support

For issues or questions, please refer to the main project documentation or create an issue in the project repository.
