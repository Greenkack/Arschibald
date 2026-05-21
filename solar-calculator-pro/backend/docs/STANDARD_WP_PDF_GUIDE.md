# Standard WP PDF System - Complete Guide

## Overview

The Standard WP (Heat Pump) PDF System generates professional 8-page PDF documents for heat pump installations. It uses a template-based approach with YML coordinate files for precise positioning of dynamic content.

## Architecture

### Components

1. **WPYMLCoordinateParser**: Parses YML coordinate files
2. **WPTemplateLoader**: Loads PDF templates
3. **WPPlaceholderSystem**: Manages static and dynamic placeholders
4. **WPPositioningEngine**: Positions text elements on PDF pages
5. **StandardWPPDFService**: Main orchestration service

### File Structure

```
pdf_templates_static/notext/
├── hp_nt_01.pdf  # Page 1: Cover page
├── hp_nt_02.pdf  # Page 2: Introduction
├── hp_nt_03.pdf  # Page 3: Technical specifications
├── hp_nt_04.pdf  # Page 4: Cost analysis
├── hp_nt_05.pdf  # Page 5: Efficiency calculations
├── hp_nt_06.pdf  # Page 6: Comparison charts
├── hp_nt_07.pdf  # Page 7: Environmental impact
└── hp_nt_08.pdf  # Page 8: Summary

coords_wp/
├── wp_seite1.yml  # Coordinates for page 1
├── wp_seite2.yml  # Coordinates for page 2
├── wp_seite3.yml  # Coordinates for page 3
├── wp_seite4.yml  # Coordinates for page 4
├── wp_seite5.yml  # Coordinates for page 5
├── wp_seite6.yml  # Coordinates for page 6
├── wp_seite7.yml  # Coordinates for page 7
└── wp_seite8.yml  # Coordinates for page 8
```

## YML Coordinate Format

Each YML file contains text elements with positioning information:

```yaml
----------------------------------------
Text: wp_modell_name
Position: (100.0, 200.0, 300.0, 250.0)
Schriftart: Helvetica
Schriftgröße: 12
Farbe: 0
----------------------------------------
Text: wp_cop_wert
Position: (100.0, 300.0, 300.0, 350.0)
Schriftart: Helvetica-Bold
Schriftgröße: 14
Farbe: 16711680
```

### Field Descriptions

- **Text**: Placeholder name or static text
- **Position**: (x1, y1, x2, y2) coordinates in points
- **Schriftart**: Font name (e.g., Helvetica, Helvetica-Bold)
- **Schriftgröße**: Font size in points
- **Farbe**: Color as integer (RGB encoded)

## Placeholders

### Static Placeholders

Static text that appears in templates:

- `ERSTELLT FÜR:`
- `aus`
- `WÄRMEPUMPE`
- `ANGEBOT`
- `erstellt am:`
- `Angebotsnummer:`
- `COP-Wert:`
- `Heizkosten:`
- `Effizienz:`
- `Vergleich:`

### Dynamic Placeholders

Values that get replaced with actual data:

#### Customer Information
- `anrede_kunde` - Customer salutation (Herr/Frau)
- `kunde_vorname_und_nachname` - Customer full name
- `kunde_wohnort` - Customer city

#### Heat Pump Specifications
- `wp_leistung_kw` - Heat pump power in kW
- `wp_cop_wert` - COP (Coefficient of Performance) value
- `wp_jahresarbeitszahl` - Annual performance factor (JAZ)
- `wp_modell_name` - Heat pump model name
- `wp_hersteller` - Manufacturer name
- `wp_effizienzklasse` - Efficiency class (e.g., A+++)
- `wp_vorlauftemperatur` - Flow temperature
- `wp_heizlast_kw` - Heating load in kW
- `wp_warmwasser_liter` - Hot water capacity in liters

#### Cost and Savings
- `wp_heizkosten_jahr` - Annual heating costs
- `wp_heizkosten_monat` - Monthly heating costs
- `wp_einsparung_jahr` - Annual savings
- `wp_einsparung_prozent` - Savings percentage
- `wp_amortisationszeit` - Payback period

#### Environmental Impact
- `wp_co2_einsparung` - CO2 savings

#### Other
- `langes_datum_heute` - Date in German format
- `total_price` - Total price

## Usage Examples

### Basic PDF Generation

```python
from services.standard_wp_pdf_service import StandardWPPDFService

# Initialize service
service = StandardWPPDFService()

# Prepare data
data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_modell_name': 'Viessmann Vitocal 200-S',
    'wp_hersteller': 'Viessmann',
    'langes_datum_heute': '22. Januar 2025'
}

# Generate PDF
pdf_bytes = service.generate_complete_pdf(data)

# Save to file
with open('wp_angebot.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### PDF with German Formatting

```python
# Calculation data
calculation_data = {
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_jahresarbeitszahl': 4.2,
    'wp_heizkosten_jahr': 1250.00,
    'wp_heizkosten_monat': 104.17,
    'wp_einsparung_jahr': 2500.00,
    'wp_modell_name': 'Viessmann Vitocal 200-S',
    'wp_hersteller': 'Viessmann'
}

# Customer data
customer_data = {
    'anrede_kunde': 'Frau',
    'kunde_vorname_und_nachname': 'Anna Schmidt',
    'kunde_wohnort': 'München',
    'langes_datum_heute': '22. Januar 2025'
}

# Pricing data
pricing_data = {
    'total_price': 18999.00
}

# Generate with German formatting
pdf_bytes = service.generate_pdf_with_german_formatting(
    calculation_data=calculation_data,
    customer_data=customer_data,
    pricing_data=pricing_data
)
```

### Partial Page Generation

```python
# Generate only pages 1-3
pdf_bytes = service.generate_complete_pdf(
    data,
    include_pages=[1, 2, 3]
)
```

## German Number Formatting

The service automatically formats numbers in German format:

### Currency Formatting

```python
service._format_german_currency(16999.00)
# Output: "16.999,00 €"

service._format_german_currency(1250.50)
# Output: "1.250,50 €"
```

### Decimal Formatting

```python
service._format_german_decimal(4.5, 1)
# Output: "4,5"

service._format_german_decimal(4.25, 2)
# Output: "4,25"
```

## API Endpoints

### Generate WP PDF

**POST** `/api/v1/standard-wp-pdf/generate`

Generate a complete 8-page WP PDF.

**Request Body:**
```json
{
  "customer_data": {
    "anrede_kunde": "Herr",
    "kunde_vorname_und_nachname": "Max Mustermann",
    "kunde_wohnort": "Berlin"
  },
  "calculation_data": {
    "wp_leistung_kw": 12.5,
    "wp_cop_wert": 4.5,
    "wp_jahresarbeitszahl": 4.2,
    "wp_heizkosten_jahr": 1250.00,
    "wp_heizkosten_monat": 104.17,
    "wp_einsparung_jahr": 2500.00,
    "wp_einsparung_prozent": "66,7%",
    "wp_amortisationszeit": "8 Jahre",
    "wp_co2_einsparung": "4.500 kg/Jahr",
    "wp_effizienzklasse": "A+++",
    "wp_vorlauftemperatur": "35°C",
    "wp_heizlast_kw": 10.0,
    "wp_warmwasser_liter": 300,
    "wp_modell_name": "Viessmann Vitocal 200-S",
    "wp_hersteller": "Viessmann"
  },
  "pricing_data": {
    "total_price": 18999.00
  },
  "langes_datum_heute": "22. Januar 2025"
}
```

**Response:**
- Content-Type: `application/pdf`
- Binary PDF data

### Generate Custom WP PDF

**POST** `/api/v1/standard-wp-pdf/generate-custom`

Generate a WP PDF with custom data structure.

**Request Body:**
```json
{
  "data": {
    "wp_modell_name": "Viessmann Vitocal 200-S",
    "wp_cop_wert": "4,5",
    "kunde_vorname_und_nachname": "Max Mustermann"
  },
  "include_pages": [1, 2, 3]
}
```

### Get Available Templates

**GET** `/api/v1/standard-wp-pdf/templates`

Get information about available WP templates.

**Response:**
```json
{
  "success": true,
  "total_pages": 8,
  "available_templates": [1, 2, 3, 4, 5, 6, 7, 8],
  "template_directory": "pdf_templates_static/notext",
  "coordinates_directory": "coords_wp",
  "template_files": [
    "hp_nt_01.pdf",
    "hp_nt_02.pdf",
    "hp_nt_03.pdf",
    "hp_nt_04.pdf",
    "hp_nt_05.pdf",
    "hp_nt_06.pdf",
    "hp_nt_07.pdf",
    "hp_nt_08.pdf"
  ],
  "coordinate_files": [
    "wp_seite1.yml",
    "wp_seite2.yml",
    "wp_seite3.yml",
    "wp_seite4.yml",
    "wp_seite5.yml",
    "wp_seite6.yml",
    "wp_seite7.yml",
    "wp_seite8.yml"
  ]
}
```

### Get Available Placeholders

**GET** `/api/v1/standard-wp-pdf/placeholders`

Get list of available placeholders.

**Response:**
```json
{
  "success": true,
  "static_placeholders": [
    "WÄRMEPUMPE",
    "COP-Wert:",
    "Heizkosten:",
    "..."
  ],
  "dynamic_placeholders": [
    "wp_modell_name",
    "wp_cop_wert",
    "wp_leistung_kw",
    "..."
  ],
  "description": {
    "static": "Static text that appears in templates",
    "dynamic": "Placeholders that get replaced with actual data"
  }
}
```

### Validate WP Data

**POST** `/api/v1/standard-wp-pdf/validate-data`

Validate data before PDF generation.

**Request Body:**
```json
{
  "wp_modell_name": "Viessmann Vitocal 200-S",
  "wp_cop_wert": 4.5,
  "kunde_vorname_und_nachname": "Max Mustermann"
}
```

**Response:**
```json
{
  "valid": true,
  "missing_fields": [],
  "warnings": [],
  "message": "Data is valid"
}
```

### Health Check

**GET** `/api/v1/standard-wp-pdf/health`

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "template_directory_exists": true,
  "coordinates_directory_exists": true,
  "available_templates": 8,
  "service": "Standard WP PDF Service"
}
```

## Error Handling

The service handles various error scenarios:

1. **Missing Templates**: Returns None or logs error
2. **Missing Coordinates**: Uses template only without overlay
3. **Invalid Data**: Logs warning and continues
4. **Font Errors**: Falls back to Helvetica
5. **Color Errors**: Falls back to black (#000000)

## Best Practices

1. **Always provide required fields**: `anrede_kunde`, `kunde_vorname_und_nachname`, `kunde_wohnort`, `wp_leistung_kw`, `wp_cop_wert`, `wp_modell_name`

2. **Use German formatting**: The service automatically formats numbers, but you can also pre-format strings

3. **Validate data**: Use the `/validate-data` endpoint before generation

4. **Handle errors gracefully**: Check for None returns and catch exceptions

5. **Test with sample data**: Use the demo script to test your setup

## Troubleshooting

### PDF Generation Fails

**Problem**: `generate_complete_pdf()` returns empty bytes

**Solutions**:
- Check if template directory exists
- Verify template files are present (hp_nt_01.pdf to hp_nt_08.pdf)
- Check if PyPDF/pypdf is installed
- Check if ReportLab is installed

### Missing Content in PDF

**Problem**: Generated PDF is missing text

**Solutions**:
- Check if coordinate files exist (wp_seite1.yml to wp_seite8.yml)
- Verify placeholder names match exactly
- Check if data dictionary contains required keys

### Formatting Issues

**Problem**: Numbers not formatted correctly

**Solutions**:
- Use `generate_pdf_with_german_formatting()` instead of `generate_complete_pdf()`
- Ensure numeric values are float/int, not strings
- Check locale settings

## Performance Considerations

- **Template Caching**: Templates are loaded on demand, consider caching for high-volume scenarios
- **Coordinate Parsing**: YML files are parsed each time, consider caching parsed results
- **PDF Merging**: Uses in-memory operations, suitable for documents up to 50MB
- **Concurrent Generation**: Service is thread-safe for read operations

## Dependencies

- **pypdf** or **PyPDF2**: PDF manipulation
- **reportlab**: PDF generation and text rendering
- **pathlib**: File path handling
- **logging**: Error and info logging

## Related Documentation

- [Standard PV PDF Guide](STANDARD_PV_PDF_GUIDE.md)
- [Extended PV PDF Guide](EXTENDED_PV_PDF_GUIDE.md)
- [PDF System Architecture](PDF_SYSTEM_ANALYSIS_COMPLETE.md)
- [API Documentation](API_DOCUMENTATION.md)

## Support

For issues or questions:
1. Check the demo script: `demo_standard_wp_pdf.py`
2. Run tests: `pytest test_standard_wp_pdf_service.py`
3. Check logs for detailed error messages
4. Verify file structure and permissions
