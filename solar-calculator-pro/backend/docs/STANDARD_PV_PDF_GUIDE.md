# Standard PV PDF Template System - Complete Guide

## Overview

The Standard PV PDF Template System generates professional 8-page solar photovoltaic offer documents using a template-based approach with YML coordinate positioning.

## Architecture

### Components

1. **YMLCoordinateParser**: Parses YML files containing text positioning data
2. **TemplateLoader**: Loads PDF templates from the template directory
3. **PlaceholderSystem**: Manages static and dynamic placeholders
4. **PositioningEngine**: Positions text elements on PDF pages
5. **StandardPVPDFService**: Main orchestration service

### Directory Structure

```
pdf_templates_static/
└── notext/
    ├── nt_nt_01.pdf  # Page 1: Cover page
    ├── nt_nt_02.pdf  # Page 2: Cover letter
    ├── nt_nt_03.pdf  # Page 3: Offer positions
    ├── nt_nt_04.pdf  # Page 4: Price breakdown
    ├── nt_nt_05.pdf  # Page 5: Economic analysis
    ├── nt_nt_06.pdf  # Page 6: Technical data
    ├── nt_nt_07.pdf  # Page 7: 3D visualization
    └── nt_nt_08.pdf  # Page 8: Summary

coords/
├── seite1.yml  # Coordinates for page 1
├── seite2.yml  # Coordinates for page 2
├── seite3.yml  # Coordinates for page 3
├── seite4.yml  # Coordinates for page 4
├── seite5.yml  # Coordinates for page 5
├── seite6.yml  # Coordinates for page 6
├── seite7.yml  # Coordinates for page 7
└── seite8.yml  # Coordinates for page 8
```

## YML Coordinate Format

Each YML file contains text elements with positioning information:

```yaml
Text: ERSTELLT FÜR:
Position: (48.0, 70.0, 220.0, 87.0)
Schriftart: Helvetica-Bold
Schriftgröße: 20.0
Farbe: 30920
----------------------------------------
Text: kunde_vorname_und_nachname
Position: (90.0, 87.0, 220.0, 105.0)
Schriftart: Helvetica-Bold
Schriftgröße: 14.0
Farbe: 3487029
----------------------------------------
```

### Field Descriptions

- **Text**: The text content or placeholder name
- **Position**: (x1, y1, x2, y2) coordinates in points
- **Schriftart**: Font name (e.g., Helvetica-Bold, Helvetica-Regular)
- **Schriftgröße**: Font size in points
- **Farbe**: Color as integer (converted to RGB)

## Placeholder System

### Static Placeholders

Static text that appears as-is in the PDF:

- `ERSTELLT FÜR:`
- `aus`
- `PHOTOVOLTAIK`
- `ANGEBOT`
- `erstellt am:`
- `Angebotsnummer:`

### Dynamic Placeholders

Placeholders that get replaced with actual data:

- `anrede_kunde` - Customer salutation (Herr/Frau)
- `kunde_vorname_und_nachname` - Customer full name
- `kunde_wohnort` - Customer city/location
- `kWp_anlage_anlage` - System size in kWp
- `langes_datum_heute` - Current date in long format

## German Number Formatting

All numbers are formatted according to German standards:

- **Decimal separator**: Comma (,)
- **Thousands separator**: Dot (.)
- **Currency**: Euro symbol (€)

Examples:
- `16999.00` → `16.999,00 €`
- `1234.56` → `1.234,56 €`
- `10.5` → `10,5 kWp`

## API Usage

### Generate Complete PDF

```python
POST /api/v1/standard-pv-pdf/generate
```

**Request Body:**

```json
{
  "customer": {
    "anrede": "Herr",
    "vorname": "Max",
    "nachname": "Mustermann",
    "wohnort": "Berlin",
    "strasse": "Hauptstraße 123",
    "plz": "10115"
  },
  "calculation": {
    "kwp_anlage": 10.5,
    "module_count": 30,
    "annual_production": 12000,
    "self_consumption_rate": 65.5,
    "payback_period": 12.5,
    "co2_savings": 8500
  },
  "pricing": {
    "total_price": 16999.00,
    "module_price": 8000.00,
    "inverter_price": 3000.00,
    "battery_price": 4000.00,
    "installation_price": 1999.00
  },
  "include_pages": [1, 2, 3, 4, 5, 6, 7, 8],
  "offer_number": "ANG-2025/001"
}
```

**Response:**

Binary PDF file with appropriate headers.

### Get PDF Generation Info

```python
POST /api/v1/standard-pv-pdf/generate-info
```

Returns information about the generated PDF without returning the file itself.

**Response:**

```json
{
  "success": true,
  "message": "PDF generated successfully",
  "pdf_size_bytes": 245678,
  "pages_generated": 8
}
```

### Get Available Templates

```python
GET /api/v1/standard-pv-pdf/templates/available
```

**Response:**

```json
{
  "success": true,
  "templates": [1, 2, 3, 4, 5, 6, 7, 8],
  "total_pages": 8
}
```

### Get Page Coordinates

```python
GET /api/v1/standard-pv-pdf/coordinates/page/1
```

**Response:**

```json
{
  "success": true,
  "page_number": 1,
  "elements_count": 25,
  "elements": [
    {
      "text": "ERSTELLT FÜR:",
      "position": {
        "x": 48.0,
        "y": 70.0,
        "x2": 220.0,
        "y2": 87.0
      },
      "font": "Helvetica-Bold",
      "font_size": 20.0,
      "color": 30920
    }
  ]
}
```

## Python Service Usage

### Basic Usage

```python
from services.standard_pv_pdf_service import StandardPVPDFService

# Initialize service
service = StandardPVPDFService()

# Prepare data
data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'kWp_anlage_anlage': '10,5 kWp',
    'langes_datum_heute': '22. Januar 2025',
    'total_price': 16999.00
}

# Generate complete PDF
pdf_bytes = service.generate_complete_pdf(data)

# Save to file
with open('angebot.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Generate Specific Pages Only

```python
# Generate only pages 1, 2, and 3
pdf_bytes = service.generate_complete_pdf(
    data,
    include_pages=[1, 2, 3]
)
```

### Generate with German Formatting

```python
customer_data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin'
}

calculation_data = {
    'kWp_anlage_anlage': '10,5 kWp',
    'annual_production': '12.000 kWh'
}

pricing_data = {
    'total_price': 16999.00
}

pdf_bytes = service.generate_pdf_with_german_formatting(
    calculation_data=calculation_data,
    customer_data=customer_data,
    pricing_data=pricing_data
)
```

## Page Content Description

### Page 1: Cover Page (Deckblatt)
- Customer information
- System size (kWp)
- Offer date
- Offer number
- Company branding

### Page 2: Cover Letter (Anschreiben)
- Personalized greeting
- Introduction text
- Project overview
- Contact information

### Page 3: Offer Positions (Angebotspositionen)
- Itemized list of components
- Quantities
- Individual prices
- Subtotals

### Page 4: Price Breakdown (Preisaufstellung)
- Detailed cost breakdown
- Module costs
- Inverter costs
- Battery costs
- Installation costs
- Total price with German formatting

### Page 5: Economic Analysis (Wirtschaftlichkeit)
- Annual production
- Self-consumption rate
- Savings calculations
- Payback period
- ROI analysis

### Page 6: Technical Data (Technische Daten)
- System specifications
- Module specifications
- Inverter specifications
- Battery specifications
- Technical diagrams

### Page 7: 3D Visualization (3D-Visualisierung)
- 3D rendering of the system
- Module placement
- Roof visualization
- Multiple views

### Page 8: Summary (Zusammenfassung)
- Key benefits
- Environmental impact
- CO2 savings
- Next steps
- Terms and conditions

## Chart Types Support

The system supports 10 different chart types for data visualization:

1. **CIRCLE** - Circular progress indicators
2. **DONUT** - Donut charts for proportions
3. **BAR** - Horizontal bar charts
4. **COLUMN** - Vertical column charts
5. **LINE** - Line charts for trends
6. **AREA** - Area charts for cumulative data
7. **PIE** - Pie charts for distributions
8. **POLAR** - Polar/radar charts
9. **RADAR** - Radar charts for multi-dimensional data
10. **WATERFALL** - Waterfall charts for sequential changes

## Error Handling

The service includes comprehensive error handling:

```python
try:
    pdf_bytes = service.generate_complete_pdf(data)
except Exception as e:
    logger.error(f"PDF generation failed: {e}")
    # Handle error appropriately
```

Common errors:
- Template file not found
- Coordinate file not found
- Invalid data format
- Font not available
- PDF merge failure

## Performance Considerations

- **Template Caching**: Templates are loaded once and reused
- **Coordinate Parsing**: YML files are parsed on-demand
- **Memory Management**: Large PDFs are handled with streaming
- **Parallel Processing**: Multiple pages can be generated in parallel

## Testing

Run the test suite:

```bash
pytest backend/tests/test_standard_pv_pdf_service.py -v
```

Test coverage includes:
- YML parsing
- Template loading
- Placeholder replacement
- Positioning engine
- German formatting
- Complete PDF generation
- Error handling

## Dependencies

Required packages:
- `reportlab` - PDF generation
- `pypdf` or `PyPDF2` - PDF manipulation
- `pyyaml` - YML parsing (optional, custom parser used)

## Troubleshooting

### Templates Not Found

Ensure templates exist in `pdf_templates_static/notext/`:
```bash
ls pdf_templates_static/notext/nt_nt_*.pdf
```

### Coordinates Not Found

Ensure coordinate files exist in `coords/`:
```bash
ls coords/seite*.yml
```

### Font Issues

If fonts are not rendering correctly:
1. Check font names in YML files
2. Ensure fonts are available on the system
3. Use fallback fonts (Helvetica, Times-Roman)

### Color Conversion Issues

If colors appear incorrect:
1. Verify color integer values in YML
2. Check color conversion function
3. Use hex colors directly if needed

## Future Enhancements

Planned improvements:
- [ ] Support for custom fonts
- [ ] Dynamic chart generation
- [ ] Multi-language support
- [ ] Template editor UI
- [ ] Coordinate visual editor
- [ ] Batch PDF generation
- [ ] PDF compression optimization
- [ ] Digital signature support

## Support

For issues or questions:
- Check the test suite for examples
- Review the API documentation
- Consult the source code comments
- Contact the development team

## License

Copyright © 2025 Solar Calculator Pro
All rights reserved.
