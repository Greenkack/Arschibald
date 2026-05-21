# Multi-PDF Template & Koordinaten System - Complete Guide

## Overview

The Multi-PDF Template & Koordinaten System is a comprehensive solution for generating multiple company-specific PDF offers with different templates and positioning. This system allows you to create customized PDFs for multiple companies in a single batch operation.

## Architecture

### Directory Structure

```
project_root/
├── pdf_templates_static/
│   └── multi/
│       ├── multi_nt_01_f1.pdf    # Company 1, Page 1
│       ├── multi_nt_02_f1.pdf    # Company 1, Page 2
│       ├── ...
│       ├── multi_nt_08_f1.pdf    # Company 1, Page 8
│       ├── multi_nt_01_f2.pdf    # Company 2, Page 1
│       ├── multi_nt_02_f2.pdf    # Company 2, Page 2
│       ├── ...
│       └── multi_nt_08_f2.pdf    # Company 2, Page 8
│
└── coords_multi/
    ├── seite1_f1.yml             # Company 1, Page 1 coordinates
    ├── seite2_f1.yml             # Company 1, Page 2 coordinates
    ├── ...
    ├── seite8_f1.yml             # Company 1, Page 8 coordinates
    ├── seite1_f2.yml             # Company 2, Page 1 coordinates
    ├── seite2_f2.yml             # Company 2, Page 2 coordinates
    ├── ...
    └── seite8_f2.yml             # Company 2, Page 8 coordinates
```

### Naming Conventions

**Template Files:**
- Pattern: `multi_nt_{XX}_f{Y}.pdf`
- `XX`: Page number (01-08)
- `Y`: Company number (1, 2, 3, ...)
- Example: `multi_nt_03_f5.pdf` = Company 5, Page 3

**Coordinate Files:**
- Pattern: `seite{X}_f{Y}.yml`
- `X`: Page number (1-8)
- `Y`: Company number (1, 2, 3, ...)
- Example: `seite3_f5.yml` = Company 5, Page 3

## Core Components

### 1. MultiPDFTemplateService

The main service class that handles all template and coordinate operations.

```python
from services.multi_pdf_template_service import MultiPDFTemplateService

# Initialize service
service = MultiPDFTemplateService(
    template_base_dir="pdf_templates_static/multi",
    coordinate_base_dir="coords_multi"
)
```

### 2. Data Models

**TemplateInfo:**
```python
@dataclass
class TemplateInfo:
    company_id: int
    page_number: int
    file_path: Path
    exists: bool
    file_size: Optional[int] = None
```

**CoordinateInfo:**
```python
@dataclass
class CoordinateInfo:
    company_id: int
    page_number: int
    file_path: Path
    exists: bool
    coordinates: Optional[Dict[str, Any]] = None
```

## Usage Examples

### Discover Available Companies

```python
# Discover all companies by scanning template files
companies = service.discover_companies()
print(f"Found companies: {companies}")
# Output: Found companies: [1, 2, 3, 4, 5]
```

### Load Templates

```python
# Load a specific template
template_bytes = service.load_template(company_id=1, page_number=3)
if template_bytes:
    print(f"Loaded {len(template_bytes)} bytes")

# Load all templates for a company
templates = service.get_all_templates_for_company(company_id=1, pages=8)
for template in templates:
    print(f"Page {template.page_number}: {template.exists}")
```

### Load Coordinates

```python
# Load specific coordinates
coordinates = service.load_coordinates(company_id=1, page_number=3)
if coordinates:
    print(f"Title position: x={coordinates['title']['x']}, y={coordinates['title']['y']}")

# Load all coordinates for a company
coords = service.get_all_coordinates_for_company(company_id=1, pages=8)
for coord in coords:
    print(f"Page {coord.page_number}: {len(coord.coordinates) if coord.coordinates else 0} elements")
```

### Validate Company Data

```python
# Validate templates
templates_valid, missing_templates = service.validate_company_templates(
    company_id=1,
    pages=8
)
print(f"Templates valid: {templates_valid}")
if not templates_valid:
    print(f"Missing: {missing_templates}")

# Validate coordinates
coords_valid, missing_coords = service.validate_company_coordinates(
    company_id=1,
    pages=8
)
print(f"Coordinates valid: {coords_valid}")
if not coords_valid:
    print(f"Missing: {missing_coords}")
```

### Get Company Summary

```python
# Get detailed summary for a company
summary = service.get_company_summary(company_id=1)
print(f"Company {summary['company_id']}:")
print(f"  Templates: {summary['templates']['existing']}/{summary['templates']['total']}")
print(f"  Coordinates: {summary['coordinates']['existing']}/{summary['coordinates']['total']}")
print(f"  Ready: {summary['ready_for_generation']}")
```

### Batch Operations

```python
# Batch load templates for multiple companies
templates = service.batch_load_templates(
    company_ids=[1, 2, 3],
    pages=8
)
# Result: {1: {1: bytes, 2: bytes, ...}, 2: {1: bytes, ...}, ...}

# Batch load coordinates for multiple companies
coordinates = service.batch_load_coordinates(
    company_ids=[1, 2, 3],
    pages=8
)
# Result: {1: {1: dict, 2: dict, ...}, 2: {1: dict, ...}, ...}
```

### Get All Companies Summary

```python
# Get summary for all discovered companies
summary = service.get_all_companies_summary()
print(f"Total companies: {summary['total_companies']}")
print(f"Ready for generation: {summary['companies_ready']}")
print(f"With issues: {summary['companies_with_issues']}")

for company_id, details in summary['details'].items():
    print(f"\nCompany {company_id}:")
    print(f"  Ready: {details['ready_for_generation']}")
```

## API Endpoints

### GET /api/v1/multi-pdf-template/companies

Discover all available companies.

**Response:**
```json
[1, 2, 3, 4, 5]
```

### GET /api/v1/multi-pdf-template/companies/summary

Get summary for all companies.

**Response:**
```json
{
  "total_companies": 5,
  "companies_ready": 3,
  "companies_with_issues": 2,
  "company_ids": [1, 2, 3, 4, 5],
  "details": {
    "1": {
      "company_id": 1,
      "templates": {
        "total": 8,
        "existing": 8,
        "missing": 0,
        "valid": true
      },
      "coordinates": {
        "total": 8,
        "existing": 8,
        "missing": 0,
        "valid": true
      },
      "ready_for_generation": true
    }
  }
}
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/summary

Get summary for a specific company.

**Parameters:**
- `company_id` (path): Company number

**Response:**
```json
{
  "company_id": 1,
  "templates": {
    "total": 8,
    "existing": 8,
    "missing": 0,
    "missing_files": [],
    "valid": true,
    "total_size_bytes": 524288
  },
  "coordinates": {
    "total": 8,
    "existing": 8,
    "missing": 0,
    "missing_files": [],
    "valid": true
  },
  "ready_for_generation": true
}
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/templates

Get all templates for a company.

**Parameters:**
- `company_id` (path): Company number
- `pages` (query, optional): Number of pages (default: 8)

**Response:**
```json
[
  {
    "company_id": 1,
    "page_number": 1,
    "file_path": "pdf_templates_static/multi/multi_nt_01_f1.pdf",
    "exists": true,
    "file_size": 65536
  },
  ...
]
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/coordinates

Get all coordinates for a company.

**Parameters:**
- `company_id` (path): Company number
- `pages` (query, optional): Number of pages (default: 8)

**Response:**
```json
[
  {
    "company_id": 1,
    "page_number": 1,
    "file_path": "coords_multi/seite1_f1.yml",
    "exists": true,
    "has_coordinates": true
  },
  ...
]
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/coordinates/{page_number}

Load coordinate data for a specific page.

**Parameters:**
- `company_id` (path): Company number
- `page_number` (path): Page number (1-8)

**Response:**
```json
{
  "title": {
    "x": 100,
    "y": 200,
    "font_size": 24,
    "font_color": "#000000"
  },
  "subtitle": {
    "x": 100,
    "y": 250,
    "font_size": 16,
    "font_color": "#666666"
  }
}
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/validate/templates

Validate templates for a company.

**Parameters:**
- `company_id` (path): Company number
- `pages` (query, optional): Number of pages to validate (default: 8)

**Response:**
```json
{
  "is_valid": true,
  "missing_files": [],
  "message": "All 8 templates are valid for company 1"
}
```

### GET /api/v1/multi-pdf-template/companies/{company_id}/validate/coordinates

Validate coordinates for a company.

**Parameters:**
- `company_id` (path): Company number
- `pages` (query, optional): Number of pages to validate (default: 8)

**Response:**
```json
{
  "is_valid": false,
  "missing_files": [
    "coords_multi/seite7_f1.yml",
    "coords_multi/seite8_f1.yml"
  ],
  "message": "Missing 2 coordinate files for company 1"
}
```

### POST /api/v1/multi-pdf-template/batch/validate

Validate multiple companies at once.

**Request Body:**
```json
{
  "company_ids": [1, 2, 3],
  "pages": 8
}
```

**Response:**
```json
{
  "total_companies": 3,
  "companies_ready": 2,
  "results": {
    "1": {
      "templates": {
        "valid": true,
        "missing": []
      },
      "coordinates": {
        "valid": true,
        "missing": []
      },
      "ready": true
    },
    "2": {
      "templates": {
        "valid": true,
        "missing": []
      },
      "coordinates": {
        "valid": false,
        "missing": ["coords_multi/seite8_f2.yml"]
      },
      "ready": false
    }
  }
}
```

### GET /api/v1/multi-pdf-template/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "template_directory": "pdf_templates_static/multi",
  "template_directory_exists": true,
  "coordinate_directory": "coords_multi",
  "coordinate_directory_exists": true,
  "companies_discovered": 5,
  "company_ids": [1, 2, 3, 4, 5]
}
```

## Coordinate File Format

Coordinate files are YAML files that define the positioning of elements on each page.

### Example Coordinate File (seite1_f1.yml)

```yaml
# Page title
title:
  x: 100
  y: 200
  font_size: 24
  font_color: "#000000"
  format: "text"

# Subtitle
subtitle:
  x: 100
  y: 250
  font_size: 16
  font_color: "#666666"
  format: "text"

# Company logo
logo:
  x: 450
  y: 50
  width: 100
  height: 50

# Price field
price:
  x: 400
  y: 500
  font_size: 20
  font_color: "#FF0000"
  format: "currency"

# Date field
date:
  x: 100
  y: 750
  font_size: 12
  font_color: "#999999"
  format: "date"
```

### Supported Formats

- `text`: Plain text
- `currency`: Currency formatting (e.g., "16.999,00 €")
- `percentage`: Percentage formatting (e.g., "85,5%")
- `number`: Number formatting (e.g., "1.234,56")
- `date`: Date formatting
- `kwh`: Energy formatting (e.g., "12.500 kWh")
- `years`: Years formatting

## Error Handling

The service includes comprehensive error handling:

```python
try:
    template = service.load_template(company_id=1, page_number=1)
    if template is None:
        print("Template not found")
except Exception as e:
    print(f"Error loading template: {e}")
```

All methods return `None` or empty results instead of raising exceptions for missing files, making it easy to handle incomplete data sets.

## Best Practices

1. **Always validate before generation:**
   ```python
   templates_valid, _ = service.validate_company_templates(company_id, pages=8)
   coords_valid, _ = service.validate_company_coordinates(company_id, pages=8)
   
   if templates_valid and coords_valid:
       # Proceed with PDF generation
       pass
   ```

2. **Use batch operations for multiple companies:**
   ```python
   # More efficient than loading individually
   templates = service.batch_load_templates(company_ids=[1, 2, 3], pages=8)
   ```

3. **Check company summary before processing:**
   ```python
   summary = service.get_company_summary(company_id)
   if summary['ready_for_generation']:
       # Company is ready
       pass
   ```

4. **Handle missing files gracefully:**
   ```python
   coordinates = service.load_coordinates(company_id, page_number)
   if coordinates:
       # Use coordinates
       pass
   else:
       # Use default positioning or skip
       pass
   ```

## Testing

Run the test suite:

```bash
cd solar-calculator-pro/backend
pytest tests/test_multi_pdf_template_service.py -v
```

Run the demo script:

```bash
cd solar-calculator-pro/backend
python demo_multi_pdf_template.py
```

## Requirements

- Python 3.10+
- PyYAML
- FastAPI
- Pydantic

## Related Documentation

- [Standard PV PDF Guide](STANDARD_PV_PDF_GUIDE.md)
- [Extended PV PDF Guide](EXTENDED_PV_PDF_GUIDE.md)
- [PDF Advanced Service Guide](PDF_ADVANCED_SERVICE_GUIDE.md)
- [Company Database Guide](COMPANY_DATABASE_GUIDE.md)

## Support

For issues or questions, please refer to:
- API Documentation: `/docs` endpoint
- Test Suite: `tests/test_multi_pdf_template_service.py`
- Demo Script: `demo_multi_pdf_template.py`
