# Extended WP PDF Service - Complete Guide

## Overview

The Extended WP (Heat Pump) PDF Service extends the standard 8-page WP PDF with optional additional pages (9+) that can be dynamically activated based on user selection.

## Architecture

```
Extended WP PDF Service
├── Standard 8 Pages (1-8)
│   └── Uses StandardWPPDFService
└── Optional Additional Pages (9+)
    ├── Detailed WP Calculations
    ├── Additional WP Diagrams
    ├── WP Product Datasheets
    ├── WP Documents from Database
    ├── WP Images from Database
    └── Extended WP Visualizations
```

## Key Features

### 1. Standard 8-Page Base
- Uses the same logic as StandardWPPDFService
- Templates: `hp_nt_01.pdf` to `hp_nt_08.pdf`
- Coordinates: `coords_wp/wp_seite1.yml` to `wp_seite8.yml`
- WP-specific content: COP, JAZ, heating costs, efficiency

### 2. Optional Additional Pages
- **Page 9+**: Dynamically activated based on user selection
- **Component Types**:
  - Detailed WP calculations (COP, JAZ, heating costs)
  - Additional WP diagrams (monthly COP, cost comparison)
  - WP product datasheets from database
  - WP documents from database (individual per product)
  - WP images from database (dynamic)
  - Extended WP visualizations

### 3. WP Component Selection System
- User can select which components to include
- Each component type can be enabled/disabled
- Specific items can be selected (e.g., which diagrams, which products)

### 4. Database Integration
- **WP Datasheets**: Retrieved from product database
- **WP Documents**: Individual per product, stored in database
- **WP Images**: Dynamic images from database, converted to PDF

## Usage

### Basic Usage

```python
from services.extended_wp_pdf_service import (
    ExtendedWPPDFService,
    WPComponentSelection
)

# Initialize service
service = ExtendedWPPDFService()

# Prepare WP data
wp_data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_jahresarbeitszahl': 4.2,
    'wp_heizkosten_jahr': 1250.00,
    # ... more WP data
}

# Select components
selection = WPComponentSelection(
    include_detailed_wp_calculations=True,
    include_additional_wp_diagrams=True,
    selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison']
)

# Generate PDF
pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)

# Save to file
with open('extended_wp_offer.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Get Available Components

```python
# Get available WP components
components = service.get_available_wp_components()

print("Available WP Calculations:")
for calc in components['wp_calculations']:
    print(f"  - {calc['name']}")

print("Available WP Diagrams:")
for diagram in components['wp_diagrams']:
    print(f"  - {diagram['name']}")
```

### With Product-Specific Components

```python
# Get components for specific WP products
product_ids = ['wp_product_1', 'wp_product_2']
components = service.get_available_wp_components(product_ids)

# Select product datasheets
selection = WPComponentSelection(
    include_wp_product_datasheets=True,
    selected_wp_product_ids=product_ids
)

pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)
```

## WP Component Types

### 1. Detailed WP Calculations
- **COP Analysis**: Detailed Coefficient of Performance calculations
- **JAZ Analysis**: Jahresarbeitszahl (Annual Performance Factor) breakdown
- **Heating Cost Analysis**: Detailed heating cost calculations
- **Efficiency Analysis**: Comprehensive efficiency analysis

### 2. Additional WP Diagrams
- **Monthly COP**: COP values throughout the year
- **Heating Cost Comparison**: Compare with other heating systems
- **Efficiency Analysis**: Visual efficiency breakdown
- **Savings Projection**: Long-term savings projection

### 3. WP Product Datasheets
- Retrieved from product database
- PDF format
- Product-specific technical specifications

### 4. WP Documents
- Individual per product
- Stored in database
- Can include: installation guides, warranties, certifications

### 5. WP Images
- Dynamic images from database
- Automatically converted to PDF
- Can include: product photos, installation diagrams

### 6. Extended WP Visualizations
- Advanced WP system visualizations
- Integration with visualization service

## API Endpoints

### Generate Extended WP PDF

```http
POST /api/v1/extended-wp-pdf/generate
Content-Type: application/json

{
  "customer_data": {
    "anrede_kunde": "Herr",
    "kunde_vorname_und_nachname": "Max Mustermann",
    "kunde_wohnort": "Berlin"
  },
  "calculation_data": {
    "wp_leistung_kw": 12.5,
    "wp_cop_wert": 4.5,
    "wp_jahresarbeitszahl": 4.2
  },
  "pricing_data": {
    "total_price": 18999.00
  },
  "component_selection": {
    "include_detailed_wp_calculations": true,
    "include_additional_wp_diagrams": true,
    "selected_wp_diagram_types": ["cop_monthly", "heating_cost_comparison"]
  }
}
```

### Get Available Components

```http
GET /api/v1/extended-wp-pdf/available-components?product_ids=wp_product_1,wp_product_2
```

## WP Data Structure

### Required WP Fields
```python
{
    'anrede_kunde': str,  # Customer salutation
    'kunde_vorname_und_nachname': str,  # Customer name
    'kunde_wohnort': str,  # Customer location
    'wp_leistung_kw': float,  # Heat pump power in kW
    'wp_cop_wert': float,  # COP value
    'wp_jahresarbeitszahl': float,  # Annual performance factor
    'wp_heizkosten_jahr': float,  # Annual heating costs
    'wp_heizkosten_monat': float,  # Monthly heating costs
    'wp_einsparung_jahr': float,  # Annual savings
    'wp_einsparung_prozent': str,  # Savings percentage
    'wp_amortisationszeit': str,  # Payback period
    'wp_co2_einsparung': str,  # CO2 savings
    'wp_effizienzklasse': str,  # Efficiency class
    'wp_vorlauftemperatur': str,  # Flow temperature
    'wp_heizlast_kw': float,  # Heating load in kW
    'wp_warmwasser_liter': int,  # Hot water capacity in liters
    'langes_datum_heute': str,  # Date
    'wp_modell_name': str,  # Heat pump model name
    'wp_hersteller': str,  # Manufacturer
    'total_price': float  # Total price
}
```

## Configuration

### Template Directory
Default: `pdf_templates_static/notext`
- Standard templates: `hp_nt_01.pdf` to `hp_nt_08.pdf`
- Extended templates: `hp_nt_09.pdf`, `hp_nt_10.pdf`, etc.
- Generic extended template: `hp_nt_extended.pdf`

### Coordinates Directory
Default: `coords_wp`
- Standard coordinates: `wp_seite1.yml` to `wp_seite8.yml`
- Extended coordinates: `wp_seite9.yml`, `wp_seite10.yml`, etc.

### Database Service
Optional database service for:
- WP product datasheets
- WP documents
- WP images

## Error Handling

```python
try:
    pdf_bytes = service.generate_extended_wp_pdf(data, selection)
    if not pdf_bytes:
        print("Failed to generate PDF")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Always include standard 8 pages**: The extended service automatically includes them
2. **Select components wisely**: Only include necessary components to keep PDF size manageable
3. **Validate WP data**: Ensure all required WP fields are present
4. **Handle missing templates gracefully**: Service returns None for missing templates
5. **Use German formatting**: All prices and values should use German formatting

## Comparison with Extended PV PDF

| Feature | Extended WP PDF | Extended PV PDF |
|---------|----------------|-----------------|
| Standard Pages | 8 (WP-specific) | 8 (PV-specific) |
| Template Prefix | `hp_nt_` | `nt_nt_` |
| Coordinates Dir | `coords_wp/` | `coords/` |
| Content Focus | Heat pumps, COP, JAZ | Solar, kWp, production |
| Calculations | Heating costs, efficiency | Energy production, ROI |
| Diagrams | COP, cost comparison | Production, savings |

## Troubleshooting

### PDF Generation Fails
- Check if PyPDF/PyPDF2 is installed
- Verify template files exist
- Ensure coordinate files are valid
- Check WP data completeness

### Missing Components
- Verify database service is configured
- Check product IDs are valid
- Ensure documents/images exist in database

### Empty Additional Pages
- Check if templates exist for pages 9+
- Verify coordinate files for extended pages
- Ensure component selection is correct

## See Also

- [Standard WP PDF Guide](STANDARD_WP_PDF_GUIDE.md)
- [Extended PV PDF Guide](EXTENDED_PV_PDF_GUIDE.md)
- [WP PDF Quick Reference](EXTENDED_WP_PDF_QUICK_REFERENCE.md)
