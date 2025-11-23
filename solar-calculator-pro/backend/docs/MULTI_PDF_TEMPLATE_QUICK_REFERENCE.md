# Multi-PDF Template & Koordinaten System - Quick Reference

## Quick Start

```python
from services.multi_pdf_template_service import MultiPDFTemplateService

# Initialize
service = MultiPDFTemplateService()

# Discover companies
companies = service.discover_companies()

# Get summary
summary = service.get_company_summary(company_id=1)

# Load template
template = service.load_template(company_id=1, page_number=1)

# Load coordinates
coords = service.load_coordinates(company_id=1, page_number=1)
```

## File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Template | `multi_nt_{XX}_f{Y}.pdf` | `multi_nt_03_f5.pdf` |
| Coordinate | `seite{X}_f{Y}.yml` | `seite3_f5.yml` |

Where:
- `XX` / `X`: Page number (01-08 / 1-8)
- `Y`: Company number (1, 2, 3, ...)

## Common Operations

### Discover Companies
```python
companies = service.discover_companies()
# Returns: [1, 2, 3, 4, 5]
```

### Validate Company
```python
templates_valid, missing = service.validate_company_templates(company_id=1, pages=8)
coords_valid, missing = service.validate_company_coordinates(company_id=1, pages=8)
ready = templates_valid and coords_valid
```

### Load All Templates
```python
templates = service.get_all_templates_for_company(company_id=1, pages=8)
for t in templates:
    print(f"Page {t.page_number}: {t.exists}")
```

### Load All Coordinates
```python
coords = service.get_all_coordinates_for_company(company_id=1, pages=8)
for c in coords:
    print(f"Page {c.page_number}: {c.exists}")
```

### Batch Load
```python
# Load for multiple companies at once
templates = service.batch_load_templates(company_ids=[1, 2, 3], pages=8)
coords = service.batch_load_coordinates(company_ids=[1, 2, 3], pages=8)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/companies` | List all companies |
| GET | `/companies/summary` | Summary for all companies |
| GET | `/companies/{id}/summary` | Summary for one company |
| GET | `/companies/{id}/templates` | List templates |
| GET | `/companies/{id}/coordinates` | List coordinates |
| GET | `/companies/{id}/coordinates/{page}` | Get coordinate data |
| GET | `/companies/{id}/validate/templates` | Validate templates |
| GET | `/companies/{id}/validate/coordinates` | Validate coordinates |
| POST | `/batch/validate` | Validate multiple companies |
| GET | `/health` | Health check |

## Coordinate File Format

```yaml
title:
  x: 100
  y: 200
  font_size: 24
  font_color: "#000000"
  format: "text"

price:
  x: 400
  y: 500
  font_size: 20
  format: "currency"
```

### Supported Formats
- `text` - Plain text
- `currency` - Currency (16.999,00 €)
- `percentage` - Percentage (85,5%)
- `number` - Number (1.234,56)
- `date` - Date
- `kwh` - Energy (12.500 kWh)
- `years` - Years

## Error Handling

```python
# Methods return None for missing files
template = service.load_template(company_id=99, page_number=1)
if template is None:
    print("Template not found")

# Validation returns tuple
is_valid, missing_files = service.validate_company_templates(company_id=1)
if not is_valid:
    print(f"Missing: {missing_files}")
```

## Testing

```bash
# Run tests
pytest tests/test_multi_pdf_template_service.py -v

# Run demo
python demo_multi_pdf_template.py
```

## Directory Structure

```
pdf_templates_static/multi/
├── multi_nt_01_f1.pdf
├── multi_nt_02_f1.pdf
├── ...
└── multi_nt_08_f1.pdf

coords_multi/
├── seite1_f1.yml
├── seite2_f1.yml
├── ...
└── seite8_f1.yml
```

## Requirements

- Python 3.10+
- PyYAML
- FastAPI
- Pydantic

## See Also

- [Complete Guide](MULTI_PDF_TEMPLATE_GUIDE.md)
- [API Documentation](/docs)
- [Test Suite](../tests/test_multi_pdf_template_service.py)
