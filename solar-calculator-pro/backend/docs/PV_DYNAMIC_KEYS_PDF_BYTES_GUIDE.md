# PV Dynamic Keys & PDF Bytes System Guide

## Overview

This guide documents the PV-specific dynamic key management and PDF bytes generation system implemented for Task 115. The system provides comprehensive support for:

- Dynamic key generation for all PV data types
- PDF bytes generation with German formatting
- Integration with existing infrastructure
- Support for calculations, products, charts, and 3D visualizations

## Requirements

- **Task**: 115 - Standard PV PDF Dynamic Keys & PDF Bytes
- **Requirements**: 1.3, 4.5, 14.1, 14.2

## Architecture

### Components

1. **PVDynamicKeyManager**: Manages dynamic keys for PV data
2. **PVPDFBytesGenerator**: Generates PDF bytes for all data types
3. **GermanNumberFormatter**: Formats numbers in German format
4. **PVDataModel**: Base model combining dynamic keys and PDF generation

### Key Prefixes

The system uses specific prefixes for different PV data types:

```python
# Calculation results
PV_SYS_SIZE      # System size
PV_MOD_CNT       # Module count
PV_ANN_PROD      # Annual production
PV_SELF_CONS     # Self consumption
PV_PAYBACK       # Payback period
PV_COST          # Total cost
PV_SAV_25Y       # 25-year savings
PV_CO2_SAV       # CO2 savings

# Product data
PV_MOD_TYPE      # Module type
PV_MOD_PWR       # Module power
PV_INV_TYPE      # Inverter type
PV_BAT_TYPE      # Battery type
PV_BAT_CAP       # Battery capacity

# Pricing data
PV_PRICE_BASE    # Base price
PV_PRICE_TOT     # Total price
PV_PRICE_MOD     # Module price
PV_PRICE_INV     # Inverter price
PV_PRICE_BAT     # Battery price
```

## Usage

### 1. Dynamic Key Management

#### Import Calculation Keys

```python
from backend.services.pv_dynamic_key_manager import PVDynamicKeyManager

# Initialize manager
manager = PVDynamicKeyManager()

# Sample calculation data
calculation_data = {
    'system_size': 10.5,
    'module_count': 30,
    'annual_production': 12500.0,
    'self_consumption_rate': 85.5,
    'payback_period': 12.5,
    'total_cost': 16999.00,
    'savings_25_years': 45000.00,
    'co2_savings': 125000.0
}

# Import keys
keys = manager.import_calculation_keys(calculation_data)

# Result: {'system_size': 'PV_SYS_SIZE_20250122_143052_a1b2c3', ...}
```

#### Import Product Keys

```python
# Sample product data
product_data = {
    'module_type': 'Trina Solar TSM-400W',
    'module_power': 400,
    'module_efficiency': 20.5,
    'inverter_type': 'SMA Sunny Tripower 10.0',
    'battery_type': 'BYD Battery-Box Premium HVS 10.2',
    'battery_capacity': 10.2
}

# Import keys
product_keys = manager.import_product_keys(product_data)
```

#### Import Pricing Keys (with German Formatting)

```python
# Sample pricing data
pricing_data = {
    'base_price': 15000.00,
    'total_price': 16999.00,
    'module_price': 8000.00,
    'inverter_price': 3000.00,
    'battery_price': 5000.00
}

# Import keys - values are automatically formatted in German
pricing_keys = manager.import_pricing_keys(pricing_data)

# Retrieve formatted value
total_price_key = pricing_keys['total_price']
formatted_value = manager.get_formatted_value(total_price_key)
# Result: "16.999,00 €"
```

#### Retrieve Values

```python
# Get value by dynamic key
value = manager.get_value_by_key(dynamic_key)

# Get formatted value
formatted = manager.get_formatted_value(dynamic_key)

# Export all keys
all_keys = manager.export_all_keys()
```

### 2. German Number Formatting

The system provides comprehensive German number formatting:

```python
from backend.services.pv_dynamic_key_manager import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Basic number
formatter.format(1234.56, 2)  # "1.234,56"

# Currency
formatter.format_currency(16999.00)  # "16.999,00 €"

# kWh
formatter.format_kwh(12500.50)  # "12.500,50 kWh"

# Percentage
formatter.format_percentage(85.5)  # "85,50 %"

# Years
formatter.format_years(12.5)  # "12,5 Jahre"
```

### 3. PDF Bytes Generation

#### Generate Calculation PDF

```python
from backend.services.pv_pdf_bytes_generator import PVPDFBytesGenerator

# Initialize generator
generator = PVPDFBytesGenerator()

# Generate PDF bytes
pdf_bytes = generator.generate_calculation_pdf(calculation_data)

# Save to file
with open('calculation_results.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

#### Generate Product PDF

```python
# Generate product datasheet PDF
pdf_bytes = generator.generate_product_pdf(product_data)

# Save to file
with open('product_datasheet.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

#### Generate Chart PDF

```python
# Sample chart data
chart_data = {
    'labels': ['Januar', 'Februar', 'März', 'April'],
    'values': [1000, 1200, 1500, 1800]
}

# Generate chart PDF
pdf_bytes = generator.generate_chart_pdf(
    chart_type='PIE',
    chart_data=chart_data,
    title='Monatliche Produktion'
)
```

#### Generate 3D Visualization PDF

```python
# Sample visualization data
viz_data = {
    'description': '3D-Visualisierung der PV-Anlage',
    'module_count': 30,
    'roof_area': 50.0,
    'orientation': 'Süd'
}

# Generate PDF
pdf_bytes = generator.generate_3d_visualization_pdf(
    visualization_data=viz_data,
    image_path='path/to/3d_render.png'  # Optional
)
```

### 4. Using PVDataModel

The `PVDataModel` class combines dynamic keys and PDF generation:

```python
from backend.services.pv_dynamic_key_manager import PVDataModel, PVKeyPrefix

# Create model
data = {
    'system_size': 10.5,
    'module_count': 30,
    'annual_production': 12500.0
}
model = PVDataModel(data)

# Generate dynamic key
key = model.generate_dynamic_key(prefix=PVKeyPrefix.SYSTEM_SIZE)

# Generate PDF bytes
pdf_bytes = model.to_pdf_bytes()

# Generate base64-encoded PDF
base64_pdf = model.to_pdf_base64()

# Save PDF to file
model.save_pdf('output.pdf')
```

## German Formatting Specifications

### Number Format

- **Thousands separator**: Dot (.)
- **Decimal separator**: Comma (,)
- **Decimal places**: 2 (for currency and most values)

### Examples

| Value | Format | Output |
|-------|--------|--------|
| 16999.00 | Currency | 16.999,00 € |
| 12500.50 | kWh | 12.500,50 kWh |
| 85.5 | Percentage | 85,50 % |
| 12.5 | Years | 12,5 Jahre |
| 1234567.89 | Number | 1.234.567,89 |

## Data Types Supported

### 1. Text Data
- Customer names
- Addresses
- Product descriptions
- All formatted as UTF-8 strings

### 2. Numeric Data
- System sizes (kWp)
- Module counts
- Production values (kWh)
- Prices (€)
- Percentages (%)
- Years
- All formatted in German format

### 3. Charts and Diagrams
- Pie charts
- Bar charts
- Line charts
- All 10 chart types supported
- German-formatted axis labels and values

### 4. Images
- Product images
- 3D visualizations
- Embedded in PDF with proper sizing

### 5. Product Data
- Module specifications
- Inverter specifications
- Battery specifications
- All from database

## Integration with Standard PV PDF Service

The dynamic keys and PDF bytes system integrates seamlessly with the existing Standard PV PDF Service:

```python
from solar_calculator_pro.backend.services.standard_pv_pdf_service import StandardPVPDFService
from backend.services.pv_dynamic_key_manager import PVDynamicKeyManager
from backend.services.pv_pdf_bytes_generator import PVPDFBytesGenerator

# Initialize services
pdf_service = StandardPVPDFService()
key_manager = PVDynamicKeyManager()
pdf_generator = PVPDFBytesGenerator()

# Import keys
calculation_keys = key_manager.import_calculation_keys(calculation_data)
pricing_keys = key_manager.import_pricing_keys(pricing_data)

# Generate PDF with dynamic keys
pdf_bytes = pdf_service.generate_pdf_with_german_formatting(
    calculation_data=calculation_data,
    customer_data=customer_data,
    pricing_data=pricing_data
)
```

## Performance Considerations

### Key Generation
- Keys are generated with timestamps and hashes for uniqueness
- O(1) lookup performance through indexing
- Minimal memory overhead

### PDF Generation
- Lazy loading of templates
- Efficient memory usage with BytesIO
- Streaming for large documents

### Caching
- Formatted values are cached in the index
- Metadata is stored alongside keys
- Fast retrieval without re-formatting

## Error Handling

The system includes comprehensive error handling:

```python
try:
    keys = manager.import_calculation_keys(calculation_data)
except ValueError as e:
    print(f"Invalid data: {e}")

try:
    pdf_bytes = generator.generate_calculation_pdf(calculation_data)
except ImportError as e:
    print(f"Missing dependency: {e}")
except Exception as e:
    print(f"PDF generation failed: {e}")
```

## Testing

Comprehensive tests are provided in `test_pv_dynamic_keys_pdf_bytes.py`:

```bash
# Run all tests
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py -v

# Run specific test class
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py::TestGermanNumberFormatter -v

# Run with coverage
pytest solar-calculator-pro/backend/tests/test_pv_dynamic_keys_pdf_bytes.py --cov=backend.services -v
```

## Best Practices

1. **Always use the manager for key generation**
   - Don't create keys manually
   - Use the appropriate prefix for each data type

2. **Format numbers before display**
   - Use GermanNumberFormatter for all numeric values
   - Apply correct unit formatting

3. **Cache formatted values**
   - The index stores formatted values
   - Retrieve using `get_formatted_value()`

4. **Handle missing data gracefully**
   - Check for None values
   - Provide defaults where appropriate

5. **Use metadata**
   - Store units and types in metadata
   - Use for validation and formatting

## Troubleshooting

### Issue: Keys not found in index
**Solution**: Ensure keys are imported before retrieval
```python
keys = manager.import_calculation_keys(data)
value = manager.get_value_by_key(keys['system_size'])
```

### Issue: PDF generation fails
**Solution**: Check that reportlab is installed
```bash
pip install reportlab
```

### Issue: Incorrect German formatting
**Solution**: Use the formatter methods, not manual formatting
```python
# Wrong
formatted = f"{value:,.2f} €"

# Correct
formatted = formatter.format_currency(value)
```

## Future Enhancements

Planned improvements for future versions:

1. **Additional chart types**
   - DONUT, POLAR, RADAR, WATERFALL
   - 3D effects for charts

2. **Enhanced metadata**
   - Validation rules
   - Conversion factors
   - Historical tracking

3. **Batch operations**
   - Import multiple datasets at once
   - Generate multiple PDFs in parallel

4. **Advanced caching**
   - Redis integration
   - Distributed caching

## References

- Task 115: Standard PV PDF Dynamic Keys & PDF Bytes
- Requirements: 1.3, 4.5, 14.1, 14.2
- Related: Task 114 (Standard PV PDF Template System)
- Related: Task 219 (Dynamic Key System Infrastructure)
- Related: Task 220 (PDF Byte Generation Core)

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the inline documentation
3. Consult the main design document
4. Contact the development team

---

**Last Updated**: 2025-01-22
**Version**: 1.0.0
**Status**: Complete
