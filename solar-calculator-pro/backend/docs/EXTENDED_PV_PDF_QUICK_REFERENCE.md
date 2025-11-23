# Extended PV PDF Service - Quick Reference

## Quick Start

```python
from services.extended_pv_pdf_service import ExtendedPVPDFService, ComponentSelection

# Initialize
service = ExtendedPVPDFService()

# Prepare data
data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'kWp_anlage_anlage': '10,5 kWp',
    'langes_datum_heute': '22. Januar 2025',
    'total_price': 16999.00
}

# Select components
selection = ComponentSelection(
    include_detailed_calculations=True,
    include_additional_diagrams=True,
    selected_diagram_types=['production_monthly']
)

# Generate PDF
pdf_bytes = service.generate_extended_pdf(data, selection)

# Save
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

## Component Types

| Component | Description | Page Count |
|-----------|-------------|------------|
| `include_detailed_calculations` | Extended calculation details | +1 |
| `include_additional_diagrams` | Extra charts and visualizations | +N (per diagram) |
| `include_product_datasheets` | Product technical specs | +N (per product) |
| `include_documents` | Product documents | +N (per document) |
| `include_images` | Dynamic images | +N (per image) |
| `include_extended_visualizations` | 3D and advanced visuals | +1 |

## Available Diagram Types

- `production_monthly` - Monthly production chart
- `consumption_analysis` - Consumption breakdown
- `savings_projection` - Long-term savings forecast
- `roi_analysis` - ROI visualization
- `environmental_impact` - CO2 savings chart

## API Endpoints

### Generate Extended PDF

```http
POST /api/v1/extended-pv-pdf/generate
Content-Type: application/json

{
  "customer_data": {...},
  "calculation_data": {...},
  "pricing_data": {...},
  "component_selection": {
    "include_detailed_calculations": true,
    "include_additional_diagrams": true,
    "selected_diagram_types": ["production_monthly"]
  }
}
```

**Response**: PDF file (application/pdf)

### Get Available Components

```http
POST /api/v1/extended-pv-pdf/available-components
Content-Type: application/json

{
  "product_ids": ["module_123", "inverter_456"]
}
```

**Response**:
```json
{
  "calculations": [...],
  "diagrams": [...],
  "datasheets": [...],
  "documents": [...],
  "images": [...]
}
```

### Preview PDF Configuration

```http
POST /api/v1/extended-pv-pdf/preview
Content-Type: application/json

{
  "include_detailed_calculations": true,
  "include_additional_diagrams": true,
  "selected_diagram_types": ["production_monthly", "savings_projection"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "PDF will have 11 pages (3 additional)",
  "total_pages": 11,
  "standard_pages": 8,
  "additional_pages": 3
}
```

## Common Patterns

### Pattern 1: Standard Pages Only

```python
selection = ComponentSelection()  # All False
pdf_bytes = service.generate_extended_pdf(data, selection)
```

**Result**: 8 pages

### Pattern 2: With Calculations

```python
selection = ComponentSelection(
    include_detailed_calculations=True
)
pdf_bytes = service.generate_extended_pdf(data, selection)
```

**Result**: 9 pages (8 + 1)

### Pattern 3: With Multiple Diagrams

```python
selection = ComponentSelection(
    include_additional_diagrams=True,
    selected_diagram_types=[
        'production_monthly',
        'consumption_analysis',
        'savings_projection'
    ]
)
pdf_bytes = service.generate_extended_pdf(data, selection)
```

**Result**: 11 pages (8 + 3)

### Pattern 4: With Product Components

```python
selection = ComponentSelection(
    include_product_datasheets=True,
    include_documents=True,
    selected_product_ids=['module_123', 'inverter_456'],
    selected_document_ids=['doc_123', 'doc_456']
)
pdf_bytes = service.generate_extended_pdf(data, selection)
```

**Result**: 12 pages (8 + 2 datasheets + 2 documents)

### Pattern 5: Complete Extended PDF

```python
selection = ComponentSelection(
    include_detailed_calculations=True,
    include_additional_diagrams=True,
    include_product_datasheets=True,
    include_documents=True,
    include_images=True,
    include_extended_visualizations=True,
    selected_diagram_types=['production_monthly', 'savings_projection'],
    selected_product_ids=['module_123'],
    selected_document_ids=['doc_123'],
    selected_image_ids=['img_123']
)
pdf_bytes = service.generate_extended_pdf(data, selection)
```

**Result**: 15 pages (8 + 1 calc + 2 diagrams + 1 datasheet + 1 doc + 1 image + 1 viz)

## Data Requirements

### Minimum Required Data

```python
{
    'anrede_kunde': str,              # Customer salutation
    'kunde_vorname_und_nachname': str, # Customer name
    'kunde_wohnort': str,             # Customer city
    'kWp_anlage_anlage': str,         # System size
    'langes_datum_heute': str,        # Date
    'total_price': float              # Total price
}
```

### Extended Calculation Data

```python
{
    'detailed_roi': float,            # ROI percentage
    'payback_period': float,          # Years
    'annual_production': float,       # kWh
    'annual_savings': float,          # EUR
    'co2_savings': float              # kg CO2
}
```

## Error Handling

```python
try:
    pdf_bytes = service.generate_extended_pdf(data, selection)
    if not pdf_bytes:
        print("PDF generation failed")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Use Async for Large PDFs**
   ```python
   # Use async endpoint for PDFs with many components
   POST /api/v1/extended-pv-pdf/generate-async
   ```

2. **Cache Templates**
   ```python
   # Templates are cached automatically
   # Reuse service instance for multiple PDFs
   ```

3. **Batch Generation**
   ```python
   # Generate multiple PDFs in parallel
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       futures = [
           executor.submit(service.generate_extended_pdf, data, selection)
           for data, selection in pdf_requests
       ]
       results = [f.result() for f in futures]
   ```

## Testing

```bash
# Run tests
pytest tests/test_extended_pv_pdf_service.py -v

# Run demo
python demo_extended_pv_pdf.py

# Check output
ls demo_output/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty PDF | Check template files exist |
| Missing components | Verify database connectivity |
| Wrong formatting | Use German number formatter |
| Slow generation | Reduce components or use async |
| Memory issues | Process PDFs in batches |

## Configuration

### Template Directory

```python
service = ExtendedPVPDFService(
    template_dir="custom/templates",
    coords_dir="custom/coords"
)
```

### Database Service

```python
from services.database_service import DatabaseService

db_service = DatabaseService()
service = ExtendedPVPDFService(database_service=db_service)
```

## German Number Formatting

```python
# Currency
16999.00 → "16.999,00 €"

# Percentage
85.5 → "85,5%"

# kWh
12500 → "12.500 kWh"

# Years
11.8 → "11,8 Jahre"
```

## Component Selection Validation

```python
# Get available components first
components = service.get_available_components(
    product_ids=['module_123']
)

# Validate selection
valid_diagram_types = [d['id'] for d in components['diagrams']]
selected_diagrams = [
    d for d in selection.selected_diagram_types
    if d in valid_diagram_types
]
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Service will log:
# - Template loading
# - Component generation
# - Database queries
# - PDF assembly
# - Errors and warnings
```

## Version

Current Version: **1.0.0**

Last Updated: **2025-01-22**

## Support

- Documentation: `docs/EXTENDED_PV_PDF_GUIDE.md`
- Demo: `demo_extended_pv_pdf.py`
- Tests: `tests/test_extended_pv_pdf_service.py`
- API: `api/v1/extended_pv_pdf.py`
