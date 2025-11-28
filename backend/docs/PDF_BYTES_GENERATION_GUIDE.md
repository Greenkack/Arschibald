# PDF Bytes Generation Guide

## Overview

The PDF Bytes system generates binary PDF content for various data types including numbers, text, tables, charts, and images. This enables dynamic PDF generation with German formatting.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Bytes Generator                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Numbers   │  │    Text     │  │   Tables    │         │
│  │  Generator  │  │  Generator  │  │  Generator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Charts    │  │   Images    │  │  Documents  │         │
│  │  Generator  │  │  Generator  │  │  Generator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                  German Formatter Integration                │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Generate PDF Bytes for Number

```http
POST /api/v1/pdf-bytes/number
Content-Type: application/json

{
    "value": 1234.56,
    "format": "currency",
    "decimal_places": 2
}
```

Response:
```json
{
    "pdf_bytes": "base64_encoded_pdf_content",
    "formatted_value": "1.234,56 €",
    "size_bytes": 1024
}
```

### Generate PDF Bytes for Text

```http
POST /api/v1/pdf-bytes/text
Content-Type: application/json

{
    "text": "Solaranlage 10 kWp",
    "font_size": 12,
    "font_family": "Arial"
}
```

### Generate PDF Bytes for Table

```http
POST /api/v1/pdf-bytes/table
Content-Type: application/json

{
    "headers": ["Position", "Beschreibung", "Preis"],
    "rows": [
        ["1", "PV-Module", "5.000,00 €"],
        ["2", "Wechselrichter", "2.000,00 €"],
        ["3", "Montage", "3.000,00 €"]
    ],
    "style": {
        "header_bg": "#f0f0f0",
        "border_color": "#cccccc"
    }
}
```

### Generate PDF Bytes for Chart

```http
POST /api/v1/pdf-bytes/chart
Content-Type: application/json

{
    "type": "bar",
    "title": "Energieproduktion",
    "data": {
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "values": [100, 150, 200, 180]
    },
    "width": 400,
    "height": 300
}
```

## Python Usage

### Number to PDF Bytes

```python
from backend.core.pdf_bytes import generate_pdf_bytes_for_number

# Generate PDF bytes for a formatted number
pdf_bytes = generate_pdf_bytes_for_number(
    value=1234.56,
    format_type="currency",
    decimal_places=2
)

# Save to file
with open("number.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Text to PDF Bytes

```python
from backend.core.pdf_bytes import generate_pdf_bytes_for_text

pdf_bytes = generate_pdf_bytes_for_text(
    text="Angebot für Solaranlage",
    font_size=14,
    font_family="Arial",
    bold=True
)
```

### Table to PDF Bytes

```python
from backend.core.pdf_bytes import generate_pdf_bytes_for_table

table_data = [
    ["Position", "Beschreibung", "Preis"],
    ["1", "PV-Module 10 kWp", "5.000,00 €"],
    ["2", "Wechselrichter", "2.000,00 €"],
    ["3", "Montagesystem", "1.500,00 €"],
    ["", "Gesamt", "8.500,00 €"]
]

pdf_bytes = generate_pdf_bytes_for_table(
    data=table_data,
    header_row=True,
    column_widths=[50, 200, 100]
)
```

### Chart to PDF Bytes

```python
from backend.core.pdf_bytes import generate_pdf_bytes_for_chart

pdf_bytes = generate_pdf_bytes_for_chart(
    chart_type="line",
    title="Jahresproduktion",
    labels=["Jan", "Feb", "Mar", "Apr", "Mai", "Jun"],
    values=[800, 1000, 1200, 1400, 1500, 1600],
    unit="kWh"
)
```

## Integration with Dynamic Keys

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix
from backend.core.pdf_bytes import generate_pdf_bytes_for_number

# Generate unique key for PDF element
element_key = generate_hash_key("price_total", KeyPrefix.PDF_DOCUMENT)

# Generate PDF bytes
pdf_bytes = generate_pdf_bytes_for_number(1234.56, "currency")

# Store with key
pdf_elements[element_key] = pdf_bytes
```

## German Formatting Integration

All PDF bytes generators automatically use German formatting:

```python
# Numbers are formatted as German
generate_pdf_bytes_for_number(1234.56)
# Renders as "1.234,56" in PDF

# Currency uses Euro symbol
generate_pdf_bytes_for_number(1234.56, "currency")
# Renders as "1.234,56 €" in PDF

# Percentages use German format
generate_pdf_bytes_for_number(0.15, "percent")
# Renders as "15,00 %" in PDF
```

## Supported Content Types

| Type | Description | German Formatting |
|------|-------------|-------------------|
| Number | Numeric values | ✅ 1.234,56 |
| Currency | Money amounts | ✅ 1.234,56 € |
| Percentage | Percent values | ✅ 15,00 % |
| Text | Plain text | ✅ Umlauts supported |
| Table | Data tables | ✅ All cells formatted |
| Chart | Visualizations | ✅ Axis labels formatted |
| Image | Pictures | N/A |
| Document | Full documents | ✅ All content formatted |

## Error Handling

```python
from backend.core.pdf_bytes import PDFBytesError

try:
    pdf_bytes = generate_pdf_bytes_for_number("invalid")
except PDFBytesError as e:
    print(f"PDF generation failed: {e}")
```

## Performance Considerations

- PDF bytes are generated on-demand
- Cache frequently used elements
- Use batch generation for multiple elements
- Compress large PDF content

## Best Practices

1. **Use appropriate content type** for each element
2. **Apply German formatting** consistently
3. **Cache generated bytes** for repeated use
4. **Validate input** before generation
5. **Handle errors** gracefully
6. **Use dynamic keys** for element tracking
