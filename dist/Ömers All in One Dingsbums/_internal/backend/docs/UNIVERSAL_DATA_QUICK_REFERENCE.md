# Universal Data Model - Quick Reference

## Quick Start

```python
from backend.core.universal_data import SimpleDataModel
from backend.core.dynamic_keys import KeyPrefix

# Create model
model = SimpleDataModel(
    title="My Data",
    cost=15000.0,
    size=10.5
)

# Generate key
model.generate_dynamic_key(KeyPrefix.DATA)

# Get formatted value
formatted = model.get_formatted_value('cost', format_type='currency')
# Result: "15.000,00 €"

# Generate PDF
pdf_bytes = model.to_pdf_bytes()
```

## Common Operations

### Create Model

```python
# Simple model
model = SimpleDataModel(title="Report", value=1234.56)

# From dictionary
from backend.core.universal_data import create_universal_model
model = create_universal_model(
    {'cost': 15000.0, 'size': 10.5},
    title="Solar System",
    key_prefix=KeyPrefix.SOLAR_CALCULATION
)
```

### Generate Dynamic Key

```python
key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
# Result: "SOL_20231116_143052_a1b2c3d4"
```

### Format Numbers

```python
# German format (default)
model.get_formatted_value('cost')
# Result: "15.000,00"

# Currency
model.get_formatted_value('cost', format_type='currency')
# Result: "15.000,00 €"

# Percentage
model.get_formatted_value('efficiency', format_type='percent')
# Result: "95,50 %"
```

### Generate PDF

```python
# Get bytes
pdf_bytes = model.to_pdf_bytes()

# Get base64
pdf_base64 = model.to_pdf_base64()

# Save to file
model.save_pdf("report.pdf")
```

### Export Data

```python
# Standard dictionary
data = model.to_dict()

# Formatted dictionary (German numbers)
data = model.to_dict(formatted=True, locale='de-DE')

# JSON-serializable
data = model.to_json_serializable()
```

## Format Types

| Format Type | Example Input | German Output | English Output |
|-------------|---------------|---------------|----------------|
| `number` | 1234.56 | "1.234,56" | "1,234.56" |
| `currency` | 1234.56 | "1.234,56 €" | "$1,234.56" |
| `percent` | 95.5 | "95,50 %" | "95.50%" |

## Locales

| Locale | Number | Currency | Boolean |
|--------|--------|----------|---------|
| `de-DE` | "1.234,56" | "1.234,56 €" | "Ja" / "Nein" |
| `en-US` | "1,234.56" | "$1,234.56" | "Yes" / "No" |

## Key Prefixes

```python
from backend.core.dynamic_keys import KeyPrefix

KeyPrefix.SOLAR_CALCULATION  # "SOL"
KeyPrefix.PRICE_CALCULATION  # "PRC"
KeyPrefix.PDF_DOCUMENT       # "PDF"
KeyPrefix.CUSTOMER           # "CUS"
KeyPrefix.PROJECT            # "PRJ"
KeyPrefix.DATA               # "DAT"
```

## Metadata

```python
# Set metadata
model.set_metadata('version', '1.0')
model.set_metadata('author', 'System')

# Get metadata
version = model.get_metadata('version')

# Include in export
data = model.to_dict(include_metadata=True)
```

## Custom Data

```python
# Set custom data
model.set_data('custom_field', 'custom_value')

# Get custom data
value = model.get_data('custom_field', default='default')
```

## Utility Functions

```python
from backend.core.universal_data import format_dict_german

# Format dictionary
data = {'cost': 15000.0, 'size': 10.5}
formatted = format_dict_german(data)
# Result: {'cost': '15.000,00', 'size': '10,50'}
```

## Common Patterns

### Pattern 1: Create, Format, Export

```python
model = SimpleDataModel(title="Report", cost=15000.0)
model.generate_dynamic_key(KeyPrefix.DATA)
formatted = model.get_formatted_value('cost', format_type='currency')
data = model.to_dict(formatted=True)
```

### Pattern 2: Multi-Locale Display

```python
model = SimpleDataModel(title="Data", price=1234.56)

# German
de_price = model.get_formatted_value('price', locale='de-DE')

# English
en_price = model.get_formatted_value('price', locale='en-US')
```

### Pattern 3: PDF Generation with Metadata

```python
from backend.core.pdf_bytes import PDFMetadata

model = SimpleDataModel(title="Report", cost=15000.0)

metadata = PDFMetadata(
    title="Solar Calculation Report",
    author="System",
    subject="Solar System Analysis"
)

pdf_bytes = model.to_pdf_bytes(metadata)
```

## Error Handling

```python
try:
    pdf_bytes = model.to_pdf_bytes()
except ImportError:
    print("reportlab not installed")
    print("Install with: pip install reportlab")
```

## Testing

```python
# Run tests
pytest backend/tests/test_universal_data.py -v

# Run demo
python backend/demo_universal_data.py
```

## Requirements

```bash
pip install reportlab
```

## See Also

- [Full Documentation](UNIVERSAL_DATA_MODEL.md)
- [Dynamic Keys](DYNAMIC_KEY_SYSTEM.md)
- [PDF Bytes](PDF_BYTE_GENERATION.md)
- [German Formatter](GERMAN_FORMATTER.md)
