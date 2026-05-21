# PV Dynamic Keys & PDF Bytes - Quick Reference

## Quick Start

```python
from backend.services.pv_dynamic_key_manager import PVDynamicKeyManager
from backend.services.pv_pdf_bytes_generator import PVPDFBytesGenerator

# Initialize
manager = PVDynamicKeyManager()
generator = PVPDFBytesGenerator()

# Import keys
keys = manager.import_calculation_keys(calculation_data)

# Generate PDF
pdf_bytes = generator.generate_calculation_pdf(calculation_data)
```

## German Number Formatting

```python
from backend.services.pv_dynamic_key_manager import GermanNumberFormatter

formatter = GermanNumberFormatter()

formatter.format(1234.56, 2)           # "1.234,56"
formatter.format_currency(16999.00)    # "16.999,00 €"
formatter.format_kwh(12500.50)         # "12.500,50 kWh"
formatter.format_percentage(85.5)      # "85,50 %"
formatter.format_years(12.5)           # "12,5 Jahre"
```

## Key Prefixes

| Prefix | Description |
|--------|-------------|
| `PV_SYS_SIZE` | System size (kWp) |
| `PV_MOD_CNT` | Module count |
| `PV_ANN_PROD` | Annual production (kWh) |
| `PV_PRICE_TOT` | Total price (€) |
| `PV_MOD_TYPE` | Module type |
| `PV_INV_TYPE` | Inverter type |
| `PV_BAT_TYPE` | Battery type |

## Import Data

```python
# Calculation data
calc_keys = manager.import_calculation_keys({
    'system_size': 10.5,
    'module_count': 30,
    'annual_production': 12500.0,
    'total_cost': 16999.00
})

# Product data
prod_keys = manager.import_product_keys({
    'module_type': 'Trina Solar TSM-400W',
    'inverter_type': 'SMA Sunny Tripower 10.0'
})

# Pricing data (auto-formatted)
price_keys = manager.import_pricing_keys({
    'total_price': 16999.00,
    'module_price': 8000.00
})
```

## Retrieve Values

```python
# Get raw value
value = manager.get_value_by_key(dynamic_key)

# Get formatted value
formatted = manager.get_formatted_value(dynamic_key)

# Export all
all_keys = manager.export_all_keys()
```

## Generate PDFs

```python
# Calculation results
pdf = generator.generate_calculation_pdf(calculation_data)

# Product datasheet
pdf = generator.generate_product_pdf(product_data)

# Chart
pdf = generator.generate_chart_pdf('PIE', chart_data, 'Title')

# 3D visualization
pdf = generator.generate_3d_visualization_pdf(viz_data, image_path)
```

## Save PDF

```python
# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)

# Or use PVDataModel
model = PVDataModel(data)
model.save_pdf('output.pdf')
```

## Common Patterns

### Complete Workflow

```python
# 1. Initialize
manager = PVDynamicKeyManager()
generator = PVPDFBytesGenerator()

# 2. Import all data
calc_keys = manager.import_calculation_keys(calculation_data)
prod_keys = manager.import_product_keys(product_data)
price_keys = manager.import_pricing_keys(pricing_data)

# 3. Generate PDF
pdf_bytes = generator.generate_calculation_pdf(calculation_data)

# 4. Save
with open('pv_report.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Retrieve and Format

```python
# Get all keys for a category
calc_keys = manager.get_all_keys_by_category('calculation')

# Format each value
for key in calc_keys:
    formatted = manager.get_formatted_value(key)
    print(f"{key}: {formatted}")
```

## Error Handling

```python
try:
    keys = manager.import_calculation_keys(data)
except ValueError as e:
    print(f"Invalid data: {e}")

try:
    pdf = generator.generate_calculation_pdf(data)
except ImportError:
    print("reportlab not installed")
except Exception as e:
    print(f"PDF generation failed: {e}")
```

## Testing

```bash
# Run tests
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py -v

# Run specific test
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py::TestGermanNumberFormatter -v

# With coverage
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py --cov -v
```

## Key Methods

### PVDynamicKeyManager

| Method | Description |
|--------|-------------|
| `import_calculation_keys(data)` | Import calculation keys |
| `import_product_keys(data)` | Import product keys |
| `import_pricing_keys(data)` | Import pricing keys (formatted) |
| `get_value_by_key(key)` | Get raw value |
| `get_formatted_value(key)` | Get formatted value |
| `export_all_keys()` | Export all keys and values |

### PVPDFBytesGenerator

| Method | Description |
|--------|-------------|
| `generate_calculation_pdf(data)` | Generate calculation PDF |
| `generate_product_pdf(data)` | Generate product PDF |
| `generate_chart_pdf(type, data, title)` | Generate chart PDF |
| `generate_3d_visualization_pdf(data, img)` | Generate 3D viz PDF |

### GermanNumberFormatter

| Method | Description |
|--------|-------------|
| `format(value, decimals)` | Format number |
| `format_currency(value)` | Format as currency (€) |
| `format_kwh(value)` | Format as kWh |
| `format_percentage(value)` | Format as percentage (%) |
| `format_years(value)` | Format as years |

## Data Structures

### Calculation Data

```python
{
    'system_size': float,          # kWp
    'module_count': int,           # pieces
    'annual_production': float,    # kWh
    'self_consumption_rate': float,# %
    'payback_period': float,       # years
    'total_cost': float,           # €
    'savings_25_years': float,     # €
    'co2_savings': float           # kg
}
```

### Product Data

```python
{
    'module_type': str,
    'module_power': float,         # Wp
    'module_efficiency': float,    # %
    'inverter_type': str,
    'inverter_power': float,       # kW
    'battery_type': str,
    'battery_capacity': float      # kWh
}
```

### Pricing Data

```python
{
    'base_price': float,           # €
    'total_price': float,          # €
    'module_price': float,         # €
    'inverter_price': float,       # €
    'battery_price': float         # €
}
```

## Tips

1. **Always import keys before retrieval**
2. **Use formatter methods for German format**
3. **Check metadata for units and types**
4. **Cache formatted values in index**
5. **Handle None values gracefully**

## Requirements

- Python 3.10+
- reportlab (for PDF generation)
- pytest (for testing)

## Installation

```bash
pip install reportlab pytest
```

---

**Task**: 115 - Standard PV PDF Dynamic Keys & PDF Bytes  
**Requirements**: 1.3, 4.5, 14.1, 14.2  
**Version**: 1.0.0
