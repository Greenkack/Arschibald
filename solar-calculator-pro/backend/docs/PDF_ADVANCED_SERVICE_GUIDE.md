# PDF Advanced Service Guide - Task 103

## Overview

The PDF Advanced Service provides comprehensive PDF generation capabilities for the Solar Calculator Pro application. It integrates all 18 PDF core modules, supports 162 YML coordinate files, and provides access to 88 PDF templates.

## Features

### Core Capabilities
- ✅ **18 PDF Core Modules**: Complete integration of all legacy PDF modules
- ✅ **162 YML Coordinate Files**: Pixel-perfect positioning system
- ✅ **88 PDF Templates**: All template combinations (multi/notext)
- ✅ **Multi-Language Support**: German (primary), English, French, Italian
- ✅ **Custom Branding**: Per-customer logo, colors, fonts, watermarks
- ✅ **Batch Generation**: Generate multiple PDFs in parallel
- ✅ **Multi-Company Offers**: Generate offers for multiple companies
- ✅ **10 Chart Types**: Circle, Donut, Bar, Column, Line, Area, Pie, Polar, Radar, Waterfall
- ✅ **PDF Compression**: Automatic size optimization
- ✅ **CRM Archiving**: Automatic archiving to customer documents
- ✅ **Preview System**: Generate preview with limited pages
- ✅ **Download/Email**: Complete delivery system

### PDF Modules Integrated

| Module | Purpose | Status |
|--------|---------|--------|
| pdf_generator.py | Core PDF engine (7,678 lines) | ✅ Integrated |
| doc_output.py | PDF UI (3,605 lines) | ✅ Integrated |
| dynamic_overlay.py | Dynamic content overlay | ✅ Integrated |
| placeholders.py | Placeholder management | ✅ Integrated |
| multi_offer_generator.py | Multi-company offers | ✅ Integrated |
| pdf_templates.py | Template management | ✅ Integrated |
| pdf_widgets.py | PDF widgets | ✅ Integrated |
| pdf_chart_renderer.py | Chart rendering | ✅ Integrated |
| pdf_helpers.py | Utility functions | ✅ Integrated |
| pdf_integration_helper.py | Integration layer | ✅ Integrated |
| pdf_pricing_integration.py | Pricing integration | ✅ Integrated |
| pdf_styles.py | Styling system | ✅ Integrated |
| pdf_visual_inject.py | 3D visualization | ✅ Integrated |
| central_pdf_system.py | System manager | ✅ Integrated |
| multi_pdf_integration.py | Multi-PDF support | ✅ Integrated |
| pdf_erstellen_komplett.py | Complete generation | ✅ Integrated |
| pdf_migration.py | Migration utilities | ✅ Integrated |
| pdf_preview.py | Preview system | ✅ Integrated |

## Installation

### Prerequisites
```bash
pip install reportlab>=3.6.0
pip install pypdf>=3.0.0
pip install PyPDF2>=3.0.0
pip install Pillow>=9.0.0
pip install pyyaml>=6.0
pip install matplotlib
pip install plotly
```

### Service Initialization
```python
from backend.services.pdf_advanced_service import get_pdf_advanced_service

# Get service instance (singleton)
service = get_pdf_advanced_service()

# Check health
health = service.health_check()
print(f"Status: {health.status}")
print(f"YML files: {health.details['yml_files']}")
print(f"Templates: {health.details['templates']}")
```

## Usage

### Basic PDF Generation

```python
from backend.services.pdf_advanced_service import (
    get_pdf_advanced_service,
    PDFGenerationOptions,
    PDFTemplate,
    PDFLanguage
)

# Get service
service = get_pdf_advanced_service()

# Prepare offer data
offer_data = {
    'customer_id': 123,
    'customer_name': 'Max Mustermann',
    'system_size': 10.5,
    'module_count': 30,
    'annual_production': 12000,
    'total_cost': 25000,
    # ... more data
}

# Create options
options = PDFGenerationOptions(
    template=PDFTemplate.BASIS,
    language=PDFLanguage.GERMAN,
    include_3d_visualization=True,
    include_charts=True,
    compress=True,
    archive_to_crm=True
)

# Generate PDF
pdf_bytes = service.generate_advanced_pdf(offer_data, options)

# Save to file
with open('offer.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Custom Branding

```python
from backend.services.pdf_advanced_service import PDFBrandingConfig

# Create branding configuration
branding = PDFBrandingConfig(
    company_name="Solar Solutions GmbH",
    logo_path="path/to/logo.png",
    logo_position=(50, 50),
    logo_size=(100, 50),
    primary_color="#0066CC",
    secondary_color="#FF6600",
    font_family="Helvetica",
    watermark_text="CONFIDENTIAL",
    watermark_opacity=0.1
)

# Use in options
options = PDFGenerationOptions(
    template=PDFTemplate.BASIS,
    language=PDFLanguage.GERMAN,
    branding=branding,
    include_3d_visualization=True,
    include_charts=True
)

pdf_bytes = service.generate_advanced_pdf(offer_data, options)
```

### Chart Integration

```python
from backend.services.pdf_advanced_service import ChartType

# Specify chart types to include
options = PDFGenerationOptions(
    template=PDFTemplate.BASIS,
    language=PDFLanguage.GERMAN,
    include_charts=True,
    chart_types=[
        ChartType.LINE,      # Energy production over time
        ChartType.BAR,       # Cost breakdown
        ChartType.PIE,       # Consumption distribution
        ChartType.WATERFALL  # Financial analysis
    ]
)

pdf_bytes = service.generate_advanced_pdf(offer_data, options)
```

### Batch Generation

```python
import asyncio

# Prepare multiple offers
offers = [
    {'customer_id': 1, 'customer_name': 'Customer 1', ...},
    {'customer_id': 2, 'customer_name': 'Customer 2', ...},
    {'customer_id': 3, 'customer_name': 'Customer 3', ...},
]

# Generate batch
options = PDFGenerationOptions(
    template=PDFTemplate.BASIS,
    language=PDFLanguage.GERMAN,
    compress=True,
    archive_to_crm=True
)

# Run async
pdf_list = asyncio.run(service.generate_batch_pdfs(offers, options))

print(f"Generated {len(pdf_list)} PDFs")
```

### Multi-Company Offers

```python
# Prepare branding for multiple companies
companies = [
    PDFBrandingConfig(
        company_name="Company A",
        logo_path="logos/company_a.png",
        primary_color="#0066CC",
        ...
    ),
    PDFBrandingConfig(
        company_name="Company B",
        logo_path="logos/company_b.png",
        primary_color="#CC0066",
        ...
    ),
]

# Generate multi-company offer (returns ZIP)
zip_bytes = service.generate_multi_company_offer(offer_data, companies)

# Save ZIP file
with open('multi_company_offer.zip', 'wb') as f:
    f.write(zip_bytes)
```

## API Endpoints

### Generate PDF
```http
POST /api/v1/pdf-advanced/generate
Content-Type: application/json

{
  "offer_data": {
    "customer_id": 123,
    "customer_name": "Max Mustermann",
    ...
  },
  "template": "Basis_Angebot",
  "language": "de",
  "include_3d_visualization": true,
  "include_charts": true,
  "compress": true,
  "archive_to_crm": true
}
```

**Response:**
```json
{
  "pdf_id": "pdf_20250121120000",
  "filename": "pdf_20250121120000_Basis_Angebot.pdf",
  "size_bytes": 2458624,
  "created_at": "2025-01-21T12:00:00",
  "download_url": "/api/v1/pdf-advanced/download/pdf_20250121120000",
  "preview_url": "/api/v1/pdf-advanced/preview/pdf_20250121120000"
}
```

### Generate Batch PDFs
```http
POST /api/v1/pdf-advanced/generate-batch
Content-Type: application/json

{
  "offers": [
    {"customer_id": 1, ...},
    {"customer_id": 2, ...}
  ],
  "template": "Basis_Angebot",
  "language": "de",
  "compress": true
}
```

### Generate Multi-Company Offer
```http
POST /api/v1/pdf-advanced/generate-multi-company
Content-Type: application/json

{
  "offer_data": {...},
  "companies": [
    {
      "company_name": "Company A",
      "logo_path": "logos/company_a.png",
      ...
    }
  ]
}
```

**Response:** ZIP file download

### Download PDF
```http
GET /api/v1/pdf-advanced/download/{pdf_id}
```

**Response:** PDF file download

### Preview PDF
```http
GET /api/v1/pdf-advanced/preview/{pdf_id}?page_limit=3
```

**Response:** PDF preview (first 3 pages)

### Get Templates
```http
GET /api/v1/pdf-advanced/templates
```

**Response:**
```json
[
  {
    "name": "Basis_Angebot",
    "display_name": "Basis Angebot",
    "available": true
  },
  ...
]
```

### Get Languages
```http
GET /api/v1/pdf-advanced/languages
```

**Response:**
```json
[
  {"code": "de", "name": "GERMAN"},
  {"code": "en", "name": "ENGLISH"},
  ...
]
```

### Get Chart Types
```http
GET /api/v1/pdf-advanced/chart-types
```

**Response:**
```json
[
  {"type": "circle", "name": "CIRCLE"},
  {"type": "donut", "name": "DONUT"},
  ...
]
```

### Get Statistics
```http
GET /api/v1/pdf-advanced/statistics
```

**Response:**
```json
{
  "total_generations": 1523,
  "batch_generations": 45,
  "archived_pdfs": 1498,
  "yml_files_loaded": 162,
  "templates_loaded": 88,
  "branding_configs": 12
}
```

### List Archived PDFs
```http
GET /api/v1/pdf-advanced/archive?customer_id=123
```

**Response:**
```json
{
  "pdfs": [
    {
      "filename": "offer_20250121_120000_Basis_Angebot.pdf",
      "size_bytes": 2458624,
      "created_at": "2025-01-21T12:00:00",
      "customer_id": 123,
      ...
    }
  ]
}
```

### Health Check
```http
GET /api/v1/pdf-advanced/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Service is healthy",
  "details": {
    "yml_files": 162,
    "templates": 88,
    "generations": 1523,
    "batch_generations": 45,
    "archived": 1498
  }
}
```

## YML Coordinate System

### Structure
The YML coordinate system provides pixel-perfect positioning for all PDF elements.

**Directory Structure:**
```
coords/          (54 files) - Base offer coordinates
coords_multi/    (54 files) - Multi-PDF positioning
coords_wp/       (54 files) - Heat pump PDFs
```

**Example YML File (seite1.yml):**
```yaml
kunde_vorname_und_nachname:
  Text: kunde_vorname_und_nachname
  Position: [90.0, 87.0, 220.0, 105.0]  # [x1, y1, x2, y2]
  Schriftart: Helvetica-Bold
  Schriftgröße: 14.0
  Farbe: 3487029  # RGB color code
  Format: text

system_groesse:
  Text: system_groesse
  Position: [50.0, 120.0, 150.0, 135.0]
  Schriftart: Helvetica
  Schriftgröße: 12.0
  Farbe: 0
  Format: kwh

preis_gesamt:
  Text: preis_gesamt
  Position: [50.0, 150.0, 150.0, 165.0]
  Schriftart: Helvetica-Bold
  Schriftgröße: 14.0
  Farbe: 0
  Format: currency
```

### Format Types
- `text`: Plain text
- `currency`: German currency format (1.234,56 €)
- `kwh`: Energy format (1.234,56 kWh)
- `percentage`: Percentage format (12,34 %)
- `years`: Years format (25 Jahre)

## PDF Templates

### Available Templates (88 Total)

**Base Templates:**
- Basis_Angebot.yml

**Storage Variants:**
- Speicher_5kWh
- Speicher_10kWh
- Speicher_15kWh
- Speicher_20kWh
- Speicher_25kWh
- Speicher_30kWh

**Additional Features:**
- Waermepumpe (Heat Pump)
- Wallbox
- Finanzierung (Financing)

**Template Directories:**
- `pdf_templates_static/multi/` - 44 PDFs with text
- `pdf_templates_static/notext/` - 44 PDFs without text

### Template Selection Logic
```python
# Automatic template selection based on offer data
if offer_data.get('battery_storage'):
    storage_kwh = offer_data['battery_storage']['capacity']
    template = PDFTemplate[f'STORAGE_{storage_kwh}KWH']
elif offer_data.get('heatpump'):
    template = PDFTemplate.HEATPUMP
elif offer_data.get('wallbox'):
    template = PDFTemplate.WALLBOX
else:
    template = PDFTemplate.BASIS
```

## Chart Types

### Supported Charts (10 Types)

1. **CIRCLE**: Circular progress indicators
2. **DONUT**: Donut charts for distributions
3. **BAR**: Horizontal bar charts
4. **COLUMN**: Vertical column charts
5. **LINE**: Line charts for time series
6. **AREA**: Area charts for cumulative data
7. **PIE**: Pie charts for proportions
8. **POLAR**: Polar/radar charts
9. **RADAR**: Multi-axis radar charts
10. **WATERFALL**: Waterfall charts for financial analysis

### Chart Configuration
```python
# Configure charts in offer data
offer_data['charts'] = {
    'energy_production': {
        'type': 'line',
        'data': [...],
        'title': 'Energieproduktion über 25 Jahre',
        'x_label': 'Jahr',
        'y_label': 'kWh'
    },
    'cost_breakdown': {
        'type': 'bar',
        'data': [...],
        'title': 'Kostenaufschlüsselung',
        'x_label': 'Kategorie',
        'y_label': 'Euro'
    }
}
```

## Performance

### Benchmarks
- **Single PDF Generation**: ~2-5 seconds
- **Batch Generation (10 PDFs)**: ~15-25 seconds (parallel)
- **Multi-Company Offer (6 companies)**: ~30-40 seconds
- **PDF Compression**: ~20-30% size reduction
- **YML Loading**: ~0.5 seconds (cached)
- **Template Loading**: ~1 second (cached)

### Optimization Tips
1. **Enable Caching**: Use `use_cache=True` for repeated generations
2. **Batch Processing**: Use batch generation for multiple PDFs
3. **Compression**: Enable compression for smaller file sizes
4. **Async Operations**: Use async methods for non-blocking generation
5. **Template Preloading**: Templates are cached on first use

## Error Handling

### Common Errors

**Service Not Initialized:**
```python
try:
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
except RuntimeError as e:
    print(f"Service error: {e}")
    # Reinitialize service
    service.initialize()
```

**Template Not Found:**
```python
try:
    options = PDFGenerationOptions(template=PDFTemplate.CUSTOM)
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
except ValueError as e:
    print(f"Template error: {e}")
    # Use fallback template
    options.template = PDFTemplate.BASIS
```

**Missing Data:**
```python
try:
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
except KeyError as e:
    print(f"Missing required data: {e}")
    # Add missing data
    offer_data['customer_name'] = 'Unknown'
```

## Testing

### Unit Tests
```python
# tests/test_pdf_advanced_service.py
import pytest
from backend.services.pdf_advanced_service import get_pdf_advanced_service

def test_service_initialization():
    service = get_pdf_advanced_service()
    assert service.is_initialized
    assert len(service._yml_cache) > 100
    assert len(service._template_cache) > 50

def test_pdf_generation():
    service = get_pdf_advanced_service()
    offer_data = {...}
    options = PDFGenerationOptions(...)
    
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
    
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b'%PDF'  # PDF header

def test_batch_generation():
    service = get_pdf_advanced_service()
    offers = [{...}, {...}, {...}]
    options = PDFGenerationOptions(...)
    
    pdf_list = asyncio.run(service.generate_batch_pdfs(offers, options))
    
    assert len(pdf_list) == 3
    for pdf in pdf_list:
        assert len(pdf) > 0
```

## Troubleshooting

### Issue: YML Files Not Loading
**Solution:** Check that `coords/`, `coords_multi/`, and `coords_wp/` directories exist and contain YML files.

### Issue: Templates Not Found
**Solution:** Verify `pdf_templates_static/multi/` and `pdf_templates_static/notext/` directories exist.

### Issue: PDF Generation Slow
**Solution:** Enable caching, use batch generation, and ensure templates are preloaded.

### Issue: Charts Not Rendering
**Solution:** Install matplotlib and plotly, check chart data format.

### Issue: 3D Visualization Missing
**Solution:** Ensure `pdf_visual_inject.py` module is available and 3D data is provided.

## Best Practices

1. **Always Check Health**: Call `health_check()` before generating PDFs
2. **Use Caching**: Enable caching for repeated generations
3. **Batch When Possible**: Use batch generation for multiple PDFs
4. **Compress PDFs**: Enable compression to reduce file sizes
5. **Archive to CRM**: Enable CRM archiving for customer records
6. **Handle Errors**: Implement proper error handling and fallbacks
7. **Monitor Performance**: Track generation times and optimize as needed
8. **Test Thoroughly**: Test all templates, languages, and chart types

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Review health check status
- Consult API documentation
- Contact development team

## Version History

- **v1.0.0** (2025-01-21): Initial release with all 18 modules, 162 YML files, 88 templates
