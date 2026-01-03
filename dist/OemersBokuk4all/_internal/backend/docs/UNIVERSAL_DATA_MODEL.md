# Universal Data Model

## Overview

The Universal Data Model is a comprehensive base class that provides a unified interface for all data models in the application. It integrates three powerful capabilities:

1. **Dynamic Key Generation** - Unique, traceable keys for all data
2. **PDF Byte Generation** - Convert any data to PDF format
3. **German Number Formatting** - Locale-aware formatting with German standards

## Features

### 1. Dynamic Keys

Every data model can generate unique dynamic keys for identification and tracking:

```python
from backend.core.universal_data import SimpleDataModel
from backend.core.dynamic_keys import KeyPrefix

model = SimpleDataModel(title="Solar Calculation", cost=15000.0)
key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
# Result: "SOL_20231116_143052_a1b2c3d4"
```

### 2. PDF Generation

Convert any data model to PDF bytes:

```python
# Generate PDF bytes
pdf_bytes = model.to_pdf_bytes()

# Generate base64-encoded PDF
pdf_base64 = model.to_pdf_base64()

# Save to file
model.save_pdf("report.pdf")
```

### 3. German Number Formatting

Format numbers according to German standards (1.234,56):

```python
# Format a single value
formatted = model.get_formatted_value('cost', locale='de-DE')
# Result: "15.000,00"

# Format as currency
formatted = model.get_formatted_value('cost', format_type='currency')
# Result: "15.000,00 €"

# Format as percentage
formatted = model.get_formatted_value('efficiency', format_type='percent')
# Result: "95,50 %"
```

### 4. Locale Support

Support for multiple locales:

```python
# German format
model.get_formatted_value('price', locale='de-DE')
# Result: "1.234,56"

# English format
model.get_formatted_value('price', locale='en-US')
# Result: "1,234.56"
```

### 5. Data Serialization

Convert models to dictionaries with optional formatting:

```python
# Standard dictionary
data = model.to_dict(formatted=False)

# Formatted dictionary (German numbers)
data = model.to_dict(formatted=True, locale='de-DE')

# JSON-serializable dictionary
data = model.to_json_serializable()
```

## Usage

### Creating a Custom Model

```python
from backend.core.universal_data import UniversalDataModel
from backend.core.dynamic_keys import KeyPrefix

class SolarCalculation(UniversalDataModel):
    def __init__(self, system_size: float, cost: float):
        super().__init__()
        self.system_size = system_size
        self.cost = cost
    
    def _get_default_title(self) -> str:
        return "Solar Calculation Report"
    
    def _render_to_pdf(self, story, doc):
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, Spacer
        
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph(self._get_default_title(), styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add data
        story.append(Paragraph(
            f"System Size: {self.get_formatted_value('system_size')} kWp",
            styles['BodyText']
        ))
        story.append(Paragraph(
            f"Cost: {self.get_formatted_value('cost', format_type='currency')}",
            styles['BodyText']
        ))

# Usage
calc = SolarCalculation(system_size=10.5, cost=15000.0)
calc.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
pdf_bytes = calc.to_pdf_bytes()
```

### Using SimpleDataModel

For quick prototyping or simple use cases:

```python
from backend.core.universal_data import SimpleDataModel

model = SimpleDataModel(
    title="Quick Report",
    cost=15000.0,
    size=10.5,
    efficiency=95.5
)

# Generate key
model.generate_dynamic_key(KeyPrefix.DATA)

# Get formatted values
formatted_cost = model.get_formatted_value('cost', format_type='currency')
# Result: "15.000,00 €"

# Generate PDF
pdf_bytes = model.to_pdf_bytes()
```

### Using Utility Functions

```python
from backend.core.universal_data import (
    create_universal_model,
    format_dict_german
)
from backend.core.dynamic_keys import KeyPrefix

# Create model from dictionary
data = {'cost': 15000.0, 'size': 10.5}
model = create_universal_model(
    data,
    title="Solar System",
    key_prefix=KeyPrefix.SOLAR_CALCULATION
)

# Format dictionary values
formatted_data = format_dict_german(data)
# Result: {'cost': '15.000,00', 'size': '10,50'}
```

## API Reference

### UniversalDataModel

#### Methods

##### `set_locale(locale: str)`
Set the locale for formatting.

```python
model.set_locale('de-DE')  # German
model.set_locale('en-US')  # English
```

##### `get_locale() -> str`
Get the current locale.

##### `set_decimal_places(places: int)`
Set the number of decimal places for formatting.

```python
model.set_decimal_places(3)  # Use 3 decimal places
```

##### `get_formatted_value(key: str, locale: Optional[str] = None, format_type: Optional[str] = None) -> str`
Get a formatted value.

**Parameters:**
- `key`: Key of the value to retrieve
- `locale`: Locale to use (defaults to instance locale)
- `format_type`: Format type ('currency', 'percent', 'number')

**Returns:** Formatted string value

```python
# Number
model.get_formatted_value('cost')
# Result: "15.000,00"

# Currency
model.get_formatted_value('cost', format_type='currency')
# Result: "15.000,00 €"

# Percentage
model.get_formatted_value('efficiency', format_type='percent')
# Result: "95,50 %"
```

##### `get_all_formatted_values(locale: Optional[str] = None) -> Dict[str, str]`
Get all values formatted according to locale.

```python
formatted = model.get_all_formatted_values(locale='de-DE')
```

##### `to_dict(include_keys: bool = True, include_metadata: bool = True, formatted: bool = False, locale: Optional[str] = None) -> Dict[str, Any]`
Convert model to dictionary.

**Parameters:**
- `include_keys`: Include dynamic key information
- `include_metadata`: Include metadata
- `formatted`: Return formatted values (German format for numbers)
- `locale`: Locale for formatting (if formatted=True)

```python
# Standard dictionary
data = model.to_dict()

# Formatted dictionary
data = model.to_dict(formatted=True, locale='de-DE')
```

##### `to_json_serializable() -> Dict[str, Any]`
Convert model to JSON-serializable dictionary.

```python
data = model.to_json_serializable()
```

##### `set_data(key: str, value: Any)`
Set a data value.

```python
model.set_data('custom_field', 'custom_value')
```

##### `get_data(key: str, default: Any = None) -> Any`
Get a data value.

```python
value = model.get_data('custom_field', default='default_value')
```

##### `set_metadata(key: str, value: Any)`
Set a metadata value.

```python
model.set_metadata('version', '1.0')
```

##### `get_metadata(key: str, default: Any = None) -> Any`
Get a metadata value.

```python
version = model.get_metadata('version', default='1.0')
```

##### `format_all_numbers_german() -> Dict[str, str]`
Get all numeric values formatted in German format.

```python
formatted = model.format_all_numbers_german()
# Result: {'cost': '15.000,00', 'size': '10,50'}
```

### Inherited from DynamicKeyMixin

##### `generate_dynamic_key(prefix: KeyPrefix, ...) -> str`
Generate a unique dynamic key.

```python
key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
```

##### `get_dynamic_key() -> Optional[str]`
Get the current dynamic key.

##### `get_key_metadata() -> Dict[str, Any]`
Get metadata about the dynamic key.

### Inherited from PDFByteMixin

##### `to_pdf_bytes(metadata: Optional[PDFMetadata] = None) -> bytes`
Convert data to PDF bytes.

```python
pdf_bytes = model.to_pdf_bytes()
```

##### `to_pdf_base64(metadata: Optional[PDFMetadata] = None) -> str`
Convert data to base64-encoded PDF bytes.

```python
pdf_base64 = model.to_pdf_base64()
```

##### `save_pdf(filepath: str, metadata: Optional[PDFMetadata] = None)`
Save PDF to file.

```python
model.save_pdf("report.pdf")
```

## Examples

### Example 1: Solar Calculation

```python
from backend.core.universal_data import SimpleDataModel
from backend.core.dynamic_keys import KeyPrefix

# Create calculation
calc = SimpleDataModel(
    title="Solar System Calculation",
    system_size=10.5,
    module_count=30,
    cost=15000.0,
    efficiency=95.5,
    annual_production=12000.0
)

# Generate key
key = calc.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
print(f"Key: {key}")

# Get formatted values
print(f"Cost: {calc.get_formatted_value('cost', format_type='currency')}")
print(f"Efficiency: {calc.get_formatted_value('efficiency', format_type='percent')}")
print(f"System Size: {calc.get_formatted_value('system_size')} kWp")

# Generate PDF
pdf_bytes = calc.to_pdf_bytes()
calc.save_pdf("solar_calculation.pdf")
```

### Example 2: Price Calculation

```python
from backend.core.universal_data import SimpleDataModel
from backend.core.dynamic_keys import KeyPrefix

# Create price calculation
price = SimpleDataModel(
    title="Price Calculation",
    base_price=12000.0,
    tax=2280.0,
    discount=1200.0,
    total=13080.0
)

# Generate key
price.generate_dynamic_key(KeyPrefix.PRICE_CALCULATION)

# Get all formatted values
formatted = price.get_all_formatted_values(locale='de-DE')
for key, value in formatted.items():
    if not key.startswith('_'):
        print(f"{key}: {value}")

# Export to dictionary
data = price.to_dict(formatted=True, locale='de-DE')
```

### Example 3: Multi-Locale Support

```python
from backend.core.universal_data import SimpleDataModel

model = SimpleDataModel(
    title="Multi-Locale Data",
    price=1234.56,
    active=True
)

# German format
print("German:")
print(f"  Price: {model.get_formatted_value('price', locale='de-DE')}")
print(f"  Active: {model.get_formatted_value('active', locale='de-DE')}")

# English format
print("English:")
print(f"  Price: {model.get_formatted_value('price', locale='en-US')}")
print(f"  Active: {model.get_formatted_value('active', locale='en-US')}")
```

## Requirements

- Python 3.10+
- reportlab (for PDF generation)
- decimal (standard library)
- datetime (standard library)

## Installation

```bash
pip install reportlab
```

## Testing

Run the test suite:

```bash
pytest backend/tests/test_universal_data.py -v
```

Run the demonstration:

```bash
python backend/demo_universal_data.py
```

## Best Practices

1. **Always generate dynamic keys** for data that needs to be tracked or referenced
2. **Use formatted values** when displaying data to users
3. **Set appropriate metadata** for better data management
4. **Override `_render_to_pdf`** for custom PDF layouts
5. **Use locale-aware formatting** for international applications

## Integration with Other Systems

### Database Integration

```python
from sqlalchemy import Column, String, Float
from backend.core.universal_data import UniversalDataModel

class SolarCalculationDB(Base, UniversalDataModel):
    __tablename__ = 'solar_calculations'
    
    id = Column(Integer, primary_key=True)
    dynamic_key = Column(String, unique=True, index=True)
    system_size = Column(Float)
    cost = Column(Float)
    
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        UniversalDataModel.__init__(self)
        self.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
```

### API Integration

```python
from fastapi import APIRouter
from backend.core.universal_data import SimpleDataModel

router = APIRouter()

@router.get("/calculation/{key}")
async def get_calculation(key: str):
    # Retrieve model by key
    model = get_model_by_key(key)
    
    # Return formatted data
    return model.to_dict(formatted=True, locale='de-DE')

@router.get("/calculation/{key}/pdf")
async def get_calculation_pdf(key: str):
    # Retrieve model by key
    model = get_model_by_key(key)
    
    # Return PDF bytes
    return Response(
        content=model.to_pdf_bytes(),
        media_type="application/pdf"
    )
```

## Troubleshooting

### PDF Generation Fails

**Problem:** `ImportError: reportlab not installed`

**Solution:** Install reportlab:
```bash
pip install reportlab
```

### Formatting Issues

**Problem:** Numbers not formatting correctly

**Solution:** Check locale setting:
```python
model.set_locale('de-DE')  # For German format
```

### Key Generation Issues

**Problem:** Keys not unique

**Solution:** Ensure you're calling `generate_dynamic_key()` for each instance:
```python
model.generate_dynamic_key(KeyPrefix.DATA)
```

## See Also

- [Dynamic Keys Documentation](DYNAMIC_KEY_SYSTEM.md)
- [PDF Bytes Documentation](PDF_BYTE_GENERATION.md)
- [German Formatter Documentation](GERMAN_FORMATTER.md)
