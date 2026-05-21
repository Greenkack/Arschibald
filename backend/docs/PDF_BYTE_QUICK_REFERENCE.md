# PDF Byte Generation - Quick Reference

## Installation

```bash
pip install reportlab
```

## Basic Usage

### Create PDF from Dictionary

```python
from core.pdf_bytes import create_pdf_from_dict

data = {"Price": 1234.56, "Quantity": 100}
pdf_bytes = create_pdf_from_dict(data, title="Report")

# Save to file
with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Create PDF from Text

```python
from core.pdf_bytes import create_pdf_from_text

text = "Document content here.\n\nSecond paragraph."
pdf_bytes = create_pdf_from_text(text, title="Document")
```

### Using PDFByteMixin

```python
from core.pdf_bytes import PDFByteMixin
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class MyModel(PDFByteMixin):
    def __init__(self, title, data):
        super().__init__()
        self.title = title
        self.data = data
    
    def _get_default_title(self):
        return self.title
    
    def _render_to_pdf(self, story, doc):
        styles = getSampleStyleSheet()
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        for key, value in self.data.items():
            story.append(Paragraph(f"{key}: {value}", styles['BodyText']))

# Usage
model = MyModel("Report", {"test": "data"})
pdf_bytes = model.to_pdf_bytes()
pdf_base64 = model.to_pdf_base64()
model.save_pdf("output.pdf")
```

## German Number Formatting

```python
from core.pdf_bytes import PDFRenderingEngine

engine = PDFRenderingEngine()

# Format numbers
engine.format_german_number(1234.56)     # "1.234,56"
engine.format_german_number(1000000.99)  # "1.000.000,99"
engine.format_german_number(0.5)         # "0,50"

# Custom decimals
engine.format_german_number(1234.567, decimals=3)  # "1.234,567"
```

## PDF Metadata

```python
from core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(
    title="Sales Report",
    author="John Doe",
    subject="Q4 2024",
    keywords=["sales", "report"]
)

# Use with model
model.set_pdf_metadata(metadata)
pdf_bytes = model.to_pdf_bytes()
```

## Creating Tables

```python
from core.pdf_bytes import PDFRenderingEngine

engine = PDFRenderingEngine()

data = [
    ['Product', 'Price', 'Quantity'],
    ['Solar Panel', '1.234,56', '100'],
    ['Inverter', '2.345,67', '50']
]

table = engine.create_table(data)
```

## Common Patterns

### Solar Calculation PDF

```python
class SolarResult(PDFByteMixin):
    def __init__(self, size, cost, savings):
        super().__init__()
        self.size = size
        self.cost = cost
        self.savings = savings
    
    def _render_to_pdf(self, story, doc):
        styles = getSampleStyleSheet()
        
        data = [
            ['Parameter', 'Value'],
            ['System Size', f"{self._pdf_engine.format_german_number(self.size)} kWp"],
            ['Total Cost', f"{self._pdf_engine.format_german_number(self.cost)} €"],
            ['Savings', f"{self._pdf_engine.format_german_number(self.savings)} €"]
        ]
        
        table = self._pdf_engine.create_table(data)
        story.append(table)
```

### Invoice PDF

```python
class Invoice(PDFByteMixin):
    def __init__(self, customer, items, total):
        super().__init__()
        self.customer = customer
        self.items = items
        self.total = total
    
    def _render_to_pdf(self, story, doc):
        styles = getSampleStyleSheet()
        
        # Header
        story.append(Paragraph(f"Invoice - {self.customer}", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Items table
        data = [['Item', 'Quantity', 'Price', 'Total']]
        for item in self.items:
            data.append([
                item['name'],
                str(item['qty']),
                self._pdf_engine.format_german_number(item['price']),
                self._pdf_engine.format_german_number(item['qty'] * item['price'])
            ])
        
        # Total row
        data.append(['', '', 'Total:', self._pdf_engine.format_german_number(self.total)])
        
        table = self._pdf_engine.create_table(data)
        story.append(table)
```

## Methods Reference

### PDFByteMixin

| Method | Description | Returns |
|--------|-------------|---------|
| `to_pdf_bytes(metadata)` | Generate PDF bytes | `bytes` |
| `to_pdf_base64(metadata)` | Generate base64 PDF | `str` |
| `save_pdf(filepath, metadata)` | Save PDF to file | `None` |
| `set_pdf_metadata(metadata)` | Set metadata | `None` |
| `get_pdf_metadata()` | Get metadata | `PDFMetadata` |

### PDFRenderingEngine

| Method | Description | Returns |
|--------|-------------|---------|
| `format_german_number(value, decimals)` | Format number | `str` |
| `create_document(buffer, metadata)` | Create document | `SimpleDocTemplate` |
| `create_canvas(buffer, metadata)` | Create canvas | `Canvas` |
| `create_table(data, col_widths, style)` | Create table | `Table` |
| `add_header(canvas, text, y_pos)` | Add header | `None` |
| `add_footer(canvas, text, page_num)` | Add footer | `None` |

## Testing

```bash
# Run tests
pytest backend/tests/test_pdf_bytes.py -v

# Test specific functionality
pytest backend/tests/test_pdf_bytes.py::TestPDFByteMixin -v
```

## Error Handling

```python
from core.pdf_bytes import REPORTLAB_AVAILABLE

if not REPORTLAB_AVAILABLE:
    print("reportlab not installed")
else:
    # Safe to use PDF generation
    pdf_bytes = model.to_pdf_bytes()
```

## Tips

1. ✅ Always use `format_german_number()` for numbers
2. ✅ Set metadata for professional documents
3. ✅ Use tables for structured data
4. ✅ Test with various data types
5. ✅ Handle reportlab import errors gracefully

## Common Issues

**PDF is empty**: Ensure you're adding elements to `story` in `_render_to_pdf`

**Numbers wrong format**: Use `self._pdf_engine.format_german_number(value)`

**Import error**: Install reportlab: `pip install reportlab`

## Examples

See `backend/examples/pdf_byte_examples.py` for complete examples.
