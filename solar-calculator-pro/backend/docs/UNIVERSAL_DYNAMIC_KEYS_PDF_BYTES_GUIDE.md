# Universal Dynamic Keys & PDF Bytes System

**Task 124 Implementation Guide**

## Overview

The Universal Dynamic Keys & PDF Bytes System provides a comprehensive solution for managing dynamic keys and generating PDF bytes for **ALL** data types in the application, not just PV-specific data.

## Key Features

### 1. Universal Dynamic Key Management
- **Import keys from diverse files**: calculations.py, database.py, product_db.py, price_matrix_*.py, pv3d.py, etc.
- **Support for all data types**: Text, Numbers, Currency, Percentage, kWh, Years, Images, Charts, Documents
- **German formatting**: 16.999,00 €, 85,5%, 12.500 kWh
- **Fast lookup**: O(1) key-based retrieval
- **Source tracking**: Know where each key came from

### 2. Universal PDF Bytes Generation
- **All data types**: Text, numbers, currency, percentage, kWh, years
- **All chart types**: CIRCLE, DONUT, BAR, COLUMN, LINE, AREA, PIE, POLAR, RADAR, WATERFALL
- **Images and photos**: With descriptions and metadata
- **Documents**: Multi-section documents with formatting
- **3D visualizations**: With screenshots and data tables
- **German formatting**: All numbers formatted according to German conventions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Universal Dynamic Keys & PDF Bytes System            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      UniversalDynamicKeyManager                       │  │
│  │  - Import from calculations.py                        │  │
│  │  - Import from database.py                            │  │
│  │  - Import from product_db.py                          │  │
│  │  - Import from price_matrix_*.py                      │  │
│  │  - Import from pv3d.py                                │  │
│  │  - Import from charts                                 │  │
│  │  - German formatting                                  │  │
│  │  - Fast lookup (O(1))                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      UniversalPDFBytesGenerator                       │  │
│  │  - Data PDF (all types)                               │  │
│  │  - Chart PDF (10 types)                               │  │
│  │  - Image PDF                                          │  │
│  │  - Document PDF                                       │  │
│  │  - 3D Visualization PDF                               │  │
│  │  - German formatting                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Import Keys from Calculations

```python
from solar-calculator-pro.backend.services.universal_dynamic_key_manager import (
    UniversalDynamicKeyManager
)

# Initialize manager
manager = UniversalDynamicKeyManager()

# Import from calculations.py
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

calc_keys = manager.import_from_calculations(calculation_data)

# Get formatted value
key = calc_keys['total_cost']
formatted = manager.get_formatted_value(key)
print(formatted)  # "16.999,00 €"
```

### Example 2: Import Keys from Database

```python
# Import from database.py
database_records = [
    {
        'id': 1,
        'customer_name': 'Max Mustermann',
        'project_name': 'PV-Anlage Mustermann'
    },
    {
        'id': 2,
        'customer_name': 'Erika Musterfrau',
        'project_name': 'PV-Anlage Musterfrau'
    }
]

db_keys = manager.import_from_database(database_records)
```

### Example 3: Import Keys from Products

```python
# Import from product_db.py
product_data = {
    'product_name': 'Trina Solar TSM-400W',
    'manufacturer': 'Trina Solar',
    'power': 400.0,
    'price': 250.00
}

prod_keys = manager.import_from_products(product_data)

# Get formatted price
key = prod_keys['price']
formatted = manager.get_formatted_value(key)
print(formatted)  # "250,00 €"
```

### Example 4: Import Keys from Price Matrix

```python
# Import from price_matrix_lookup.py
pricing_data = {
    'base_price': 15000.00,
    'total_price': 16999.00,
    'discount': 500.00
}

price_keys = manager.import_from_price_matrix(pricing_data)
```

### Example 5: Import Keys from 3D Visualization

```python
# Import from pv3d.py
visualization_data = {
    'module_placement': {...},
    'roof_model': {...}
}

vis_keys = manager.import_from_3d_visualization(visualization_data)
```

### Example 6: Import Keys from Charts

```python
# Import from chart data
chart_data = {
    'labels': ['Januar', 'Februar', 'März'],
    'values': [1200, 1350, 1500]
}

chart_keys = manager.import_from_charts(chart_data, 'BAR')
```

### Example 7: Generate PDF for Data

```python
from solar-calculator-pro.backend.services.universal_pdf_bytes_generator import (
    UniversalPDFBytesGenerator
)

# Initialize generator
generator = UniversalPDFBytesGenerator()

# Data with mixed types
data = {
    'Gesamtkosten': 16999.00,
    'Anlagengröße': 10.5,
    'Eigenverbrauchsquote': 85.5,
    'Jahresproduktion': 12500.0,
    'Amortisationszeit': 12.5
}

# Specify data types for formatting
data_types = {
    'Gesamtkosten': 'currency',
    'Anlagengröße': 'number',
    'Eigenverbrauchsquote': 'percentage',
    'Jahresproduktion': 'kwh',
    'Amortisationszeit': 'years'
}

# Generate PDF
pdf_bytes = generator.generate_data_pdf(data, "Systemdaten", data_types)

# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Example 8: Generate PDF for Chart

```python
# Chart data
chart_data = {
    'labels': ['Januar', 'Februar', 'März', 'April'],
    'values': [1200.50, 1350.75, 1500.00, 1650.25]
}

# Generate PDF for BAR chart
pdf_bytes = generator.generate_chart_pdf('BAR', chart_data, "Monatliche Produktion")

# Save to file
with open('chart.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Example 9: Generate PDF for Image

```python
# Generate PDF for image
pdf_bytes = generator.generate_image_pdf(
    image_path='path/to/image.png',
    title='PV-Anlage Visualisierung',
    description='3D-Visualisierung der geplanten PV-Anlage'
)

# Save to file
with open('image.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Example 10: Generate PDF for 3D Visualization

```python
# 3D visualization data
visualization_data = {
    'description': '3D-Modell der PV-Anlage',
    'module_count': 30,
    'roof_area': 50.0,
    'orientation': 'Süd'
}

# Generate PDF
pdf_bytes = generator.generate_3d_visualization_pdf(
    visualization_data,
    image_path='path/to/screenshot.png',
    title='3D-Visualisierung'
)

# Save to file
with open('3d_vis.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

## Data Types

### Supported Data Types

| Data Type | German Format | Example |
|-----------|---------------|---------|
| `currency` | 16.999,00 € | 16999.00 → "16.999,00 €" |
| `percentage` | 85,5 % | 85.5 → "85,5 %" |
| `kwh` | 12.500 kWh | 12500.0 → "12.500 kWh" |
| `years` | 12,5 Jahre | 12.5 → "12,5 Jahre" |
| `number` | 1.234,56 | 1234.56 → "1.234,56" |
| `integer` | 30 | 30 → "30" |
| `text` | Text | "Hello" → "Hello" |
| `date` | 16.11.2023 | datetime → "16.11.2023" |
| `datetime` | 16.11.2023 14:30:52 | datetime → "16.11.2023 14:30:52" |
| `boolean` | Ja/Nein | True → "Ja", False → "Nein" |

### Chart Types

All 10 chart types are supported:

1. **CIRCLE** - Circle chart
2. **DONUT** - Donut chart (pie with hole)
3. **BAR** - Horizontal bar chart
4. **COLUMN** - Vertical bar chart
5. **LINE** - Line chart
6. **AREA** - Area chart (filled line)
7. **PIE** - Pie chart
8. **POLAR** - Polar chart
9. **RADAR** - Radar chart
10. **WATERFALL** - Waterfall chart

## API Reference

### UniversalDynamicKeyManager

#### Methods

- `import_from_calculations(calculation_data, source)` - Import keys from calculations
- `import_from_database(database_records, source)` - Import keys from database
- `import_from_products(product_data, source)` - Import keys from products
- `import_from_price_matrix(pricing_data, source)` - Import keys from price matrix
- `import_from_3d_visualization(visualization_data, source)` - Import keys from 3D viz
- `import_from_charts(chart_data, chart_type, source)` - Import keys from charts
- `get_value_by_key(key)` - Get value by dynamic key
- `get_formatted_value(key, data_type)` - Get formatted value (German format)
- `get_all_keys_by_source(source)` - Get all keys from a specific source
- `get_all_keys_by_type(data_type)` - Get all keys of a specific type
- `export_all_keys()` - Export all keys with metadata

### UniversalPDFBytesGenerator

#### Methods

- `generate_data_pdf(data, title, data_types, metadata)` - Generate PDF for data
- `generate_chart_pdf(chart_type, chart_data, title, metadata)` - Generate PDF for chart
- `generate_image_pdf(image_path, title, description, metadata)` - Generate PDF for image
- `generate_document_pdf(document_data, title, metadata)` - Generate PDF for document
- `generate_3d_visualization_pdf(visualization_data, image_path, title, metadata)` - Generate PDF for 3D viz

## Integration with Existing Code

### Import from calculations.py

```python
# In your calculation code
from solar-calculator-pro.backend.services.universal_dynamic_key_manager import (
    UniversalDynamicKeyManager
)

manager = UniversalDynamicKeyManager()

# After calculation
results = calculate_solar_system(...)
keys = manager.import_from_calculations(results, source="calculations.py")
```

### Import from database.py

```python
# In your database code
from solar-calculator-pro.backend.services.universal_dynamic_key_manager import (
    UniversalDynamicKeyManager
)

manager = UniversalDynamicKeyManager()

# After database query
records = db.query(Customer).all()
keys = manager.import_from_database(records, source="database.py")
```

### Import from product_db.py

```python
# In your product code
from solar-calculator-pro.backend.services.universal_dynamic_key_manager import (
    UniversalDynamicKeyManager
)

manager = UniversalDynamicKeyManager()

# After product query
product = get_product_by_id(product_id)
keys = manager.import_from_products(product, source="product_db.py")
```

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 1.3**: Backend Service integration
- **Requirement 14.1**: Dynamic keys for all data types
- **Requirement 14.2**: German number formatting (16.999,00 €, 85,5%, 12.500 kWh)

## Task 124 Completion

This implementation completes Task 124: PDF Dynamic Keys & PDF Bytes Universal System

✅ Universal DynamicKeyManager implemented
✅ PDF-Bytes-Generator for all data types implemented
✅ Key-Import-System from existing files implemented
✅ PDF-Bytes for calculations implemented
✅ PDF-Bytes for diagrams (all 10 types) implemented
✅ PDF-Bytes for images and documents implemented
✅ PDF-Bytes for product data implemented
✅ PDF-Bytes for 3D visualizations implemented
✅ German formatting (16.999,00 €, 85,5%, 12.500 kWh) implemented

## Next Steps

1. **Integration**: Integrate with existing modules (calculations.py, database.py, etc.)
2. **Testing**: Write comprehensive tests for all functionality
3. **Documentation**: Update API documentation
4. **Deployment**: Deploy to production environment

## Support

For questions or issues, please refer to:
- Task 124 in tasks.md
- Requirements 1.3, 14.1, 14.2 in requirements.md
- Design document for architecture details
