# Universal Dynamic Keys & PDF Bytes - Quick Reference

**Task 124 Implementation**

## Quick Start

```python
# Import the universal system
from services.universal_dynamic_key_manager import UniversalDynamicKeyManager
from services.universal_pdf_bytes_generator import UniversalPDFBytesGenerator

# Initialize
key_manager = UniversalDynamicKeyManager()
pdf_generator = UniversalPDFBytesGenerator()
```

## Import Keys

### From Calculations
```python
calc_data = {'system_size': 10.5, 'total_cost': 16999.00}
keys = key_manager.import_from_calculations(calc_data)
```

### From Database
```python
records = [{'id': 1, 'customer_name': 'Max Mustermann'}]
keys = key_manager.import_from_database(records)
```

### From Products
```python
product = {'product_name': 'Trina Solar', 'price': 250.00}
keys = key_manager.import_from_products(product)
```

### From Price Matrix
```python
pricing = {'base_price': 15000.00, 'total_price': 16999.00}
keys = key_manager.import_from_price_matrix(pricing)
```

### From Charts
```python
chart = {'labels': ['A', 'B'], 'values': [10, 20]}
keys = key_manager.import_from_charts(chart, 'BAR')
```

## Get Formatted Values

```python
# Get formatted value (German format)
formatted = key_manager.get_formatted_value(key)
# Examples:
# 16999.00 → "16.999,00 €" (currency)
# 85.5 → "85,5 %" (percentage)
# 12500.0 → "12.500 kWh" (kwh)
# 12.5 → "12,5 Jahre" (years)
```

## Generate PDFs

### Data PDF
```python
data = {'Gesamtkosten': 16999.00, 'Größe': 10.5}
data_types = {'Gesamtkosten': 'currency', 'Größe': 'number'}
pdf_bytes = pdf_generator.generate_data_pdf(data, "Titel", data_types)
```

### Chart PDF
```python
chart_data = {'labels': ['A', 'B'], 'values': [10, 20]}
pdf_bytes = pdf_generator.generate_chart_pdf('BAR', chart_data, "Titel")
```

### Image PDF
```python
pdf_bytes = pdf_generator.generate_image_pdf('path/to/image.png', "Titel")
```

### Document PDF
```python
doc_data = {'sections': [{'title': 'Titel', 'content': 'Text'}]}
pdf_bytes = pdf_generator.generate_document_pdf(doc_data, "Titel")
```

### 3D Visualization PDF
```python
vis_data = {'module_count': 30, 'roof_area': 50.0}
pdf_bytes = pdf_generator.generate_3d_visualization_pdf(vis_data, title="Titel")
```

## Data Types

| Type | Format | Example |
|------|--------|---------|
| `currency` | 16.999,00 € | 16999.00 |
| `percentage` | 85,5 % | 85.5 |
| `kwh` | 12.500 kWh | 12500.0 |
| `years` | 12,5 Jahre | 12.5 |
| `number` | 1.234,56 | 1234.56 |
| `integer` | 30 | 30 |
| `text` | Text | "Hello" |
| `boolean` | Ja/Nein | True/False |

## Chart Types

All 10 types supported: `CIRCLE`, `DONUT`, `BAR`, `COLUMN`, `LINE`, `AREA`, `PIE`, `POLAR`, `RADAR`, `WATERFALL`

## Save PDF

```python
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

## Export All Keys

```python
all_keys = key_manager.export_all_keys()
# Returns: {original_key: {dynamic_key, value, formatted_value, metadata, source}}
```

## Get Keys by Source

```python
calc_keys = key_manager.get_all_keys_by_source('calculations.py')
```

## Get Keys by Type

```python
currency_keys = key_manager.get_all_keys_by_type('currency')
```

## Complete Example

```python
# 1. Import data
calc_data = {
    'system_size': 10.5,
    'total_cost': 16999.00,
    'annual_production': 12500.0
}
keys = key_manager.import_from_calculations(calc_data)

# 2. Create formatted data
formatted_data = {
    'Anlagengröße': calc_data['system_size'],
    'Gesamtkosten': calc_data['total_cost'],
    'Jahresproduktion': calc_data['annual_production']
}

data_types = {
    'Anlagengröße': 'number',
    'Gesamtkosten': 'currency',
    'Jahresproduktion': 'kwh'
}

# 3. Generate PDF
pdf_bytes = pdf_generator.generate_data_pdf(
    formatted_data,
    "PV-Anlagen Daten",
    data_types
)

# 4. Save
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

## Files

- `services/universal_dynamic_key_manager.py` - Key management
- `services/universal_pdf_bytes_generator.py` - PDF generation
- `docs/UNIVERSAL_DYNAMIC_KEYS_PDF_BYTES_GUIDE.md` - Full guide
- `demo_universal_system.py` - Demo script

## Requirements

- Task 124: PDF Dynamic Keys & PDF Bytes Universal System
- Requirement 1.3: Backend Service integration
- Requirement 14.1: Dynamic keys for all data types
- Requirement 14.2: German number formatting
