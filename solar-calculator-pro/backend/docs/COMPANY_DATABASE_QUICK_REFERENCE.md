# Company Database - Quick Reference

## Quick Start

```bash
# 1. Run migration
python -m backend.migrations.add_company_tables upgrade

# 2. Seed sample data
python -m backend.migrations.add_company_tables seed

# 3. Start server
uvicorn backend.main:app --reload
```

## API Endpoints Cheat Sheet

### Companies
```
POST   /api/v1/companies/                    Create company
GET    /api/v1/companies/                    List companies
GET    /api/v1/companies/selection           Get for UI selection
GET    /api/v1/companies/{id}                Get by ID
PUT    /api/v1/companies/{id}                Update
DELETE /api/v1/companies/{id}                Delete (soft)
GET    /api/v1/companies/{id}/data           Get complete data
```

### Logo
```
POST   /api/v1/companies/{id}/logo           Upload logo
GET    /api/v1/companies/{id}/logo/config    Get logo config
```

### Documents
```
POST   /api/v1/companies/{id}/documents      Create
GET    /api/v1/companies/{id}/documents      List
PUT    /api/v1/companies/documents/{id}      Update
DELETE /api/v1/companies/documents/{id}      Delete
```

### Images
```
POST   /api/v1/companies/{id}/images         Create
GET    /api/v1/companies/{id}/images         List
PUT    /api/v1/companies/images/{id}         Update
DELETE /api/v1/companies/images/{id}         Delete
```

### Pricing Rules
```
POST   /api/v1/companies/{id}/pricing-rules  Create
GET    /api/v1/companies/{id}/pricing-rules  List
PUT    /api/v1/companies/pricing-rules/{id}  Update
DELETE /api/v1/companies/pricing-rules/{id}  Delete
```

## Python Usage

### Create Company
```python
from backend.services.company_service import CompanyService
from backend.models.company_schemas import CompanyCreate

service = CompanyService(db)
company = service.create_company(CompanyCreate(
    name="solar-gmbh",
    display_name="Solar GmbH",
    email="info@solar-gmbh.de",
    primary_color="#0066CC",
    price_increase_percentage=7.0,
    template_prefix="f1",
    is_active=True,
    is_default=True
))
```

### Load Company Data
```python
data = service.load_company_data(company_id)

# Access data
company = data['company']
documents = data['documents']
images = data['images']
pricing_rules = data['pricing_rules']
branding = data['branding']
pricing = data['pricing']
```

### Upload Logo
```python
company = service.upload_company_logo(
    company_id=1,
    file_path="/uploads/logo.png",
    position_x=50.0,
    position_y=20.0,
    width=50.0,
    height=30.0
)
```

### Create Document
```python
from backend.models.company_schemas import CompanyDocumentCreate

document = service.create_company_document(CompanyDocumentCreate(
    company_id=1,
    title="Produktdatenblatt",
    document_type="datasheet",
    file_path="/uploads/datasheet.pdf",
    file_name="datasheet.pdf",
    include_in_pdf=True,
    pdf_page_number=7
))
```

### Create Pricing Rule
```python
from backend.models.company_schemas import CompanyPricingRuleCreate

rule = service.create_pricing_rule(CompanyPricingRuleCreate(
    company_id=1,
    rule_name="Mengenrabatt",
    rule_type="global",
    discount_percentage=5.0,
    min_quantity=20,
    priority=10
))
```

## Database Schema

### companies
```
id, name, display_name, email, phone, website,
address_street, address_city, address_postal_code, address_country,
tax_id, vat_number, registration_number,
logo_path, logo_position_x, logo_position_y, logo_width, logo_height,
primary_color, secondary_color, accent_color,
base_markup_percentage, price_increase_percentage,
template_prefix, template_folder,
is_active, is_default, sort_order, notes, custom_config,
created_at, updated_at
```

### company_documents
```
id, company_id, title, description, document_type,
file_path, file_name, file_size, mime_type,
include_in_pdf, pdf_page_number, pdf_position_x, pdf_position_y,
tags, sort_order, is_active,
created_at, updated_at
```

### company_images
```
id, company_id, title, description, image_type,
file_path, file_name, file_size, mime_type,
width, height,
include_in_pdf, pdf_page_number,
pdf_position_x, pdf_position_y, pdf_width, pdf_height,
tags, sort_order, is_active,
created_at, updated_at
```

### company_pricing_rules
```
id, company_id, rule_name, rule_type,
target_id, target_name,
markup_percentage, markup_fixed,
discount_percentage, discount_fixed,
min_quantity, max_quantity,
valid_from, valid_until,
priority, is_active,
created_at, updated_at
```

## Common Queries

### Get Active Companies
```python
companies = service.get_companies(active_only=True)
```

### Search Companies
```python
companies = service.get_companies(search="solar")
```

### Get Default Company
```python
default = service.get_default_company()
```

### Get Company Documents by Type
```python
datasheets = service.get_company_documents(
    company_id=1,
    document_type="datasheet",
    active_only=True
)
```

### Get Company Images by Type
```python
product_images = service.get_company_images(
    company_id=1,
    image_type="product",
    active_only=True
)
```

### Get Active Pricing Rules
```python
rules = service.get_company_pricing_rules(
    company_id=1,
    active_only=True
)
```

## Document Types
- `datasheet` - Product datasheets
- `certificate` - Certificates
- `brochure` - Marketing brochures
- `contract` - Contract templates
- `warranty` - Warranty documents
- `manual` - Installation manuals

## Image Types
- `product` - Product photos
- `facility` - Facility images
- `team` - Team photos
- `logo` - Company logos
- `reference` - Reference projects

## Pricing Rule Types
- `global` - All products
- `product` - Specific product
- `category` - Product category
- `brand` - Specific brand

## Color Format
All colors use hex format: `#RRGGBB`
- Example: `#0066CC` (blue)
- Example: `#FF6600` (orange)
- Example: `#00CC66` (green)

## Position Units
All positions and sizes in millimeters (mm):
- A4 page: 210mm × 297mm
- Logo position: (x, y) from top-left
- Logo size: (width, height)

## Default Values
- `base_markup_percentage`: 0.0
- `price_increase_percentage`: 7.0
- `logo_position_x`: 50.0
- `logo_position_y`: 20.0
- `logo_width`: 50.0
- `logo_height`: 30.0
- `primary_color`: #0066CC
- `secondary_color`: #FF6600
- `accent_color`: #00CC66
- `address_country`: Deutschland
- `sort_order`: 0
- `priority`: 0

## Status Flags
- `is_active`: Enable/disable company
- `is_default`: Mark as default company
- `include_in_pdf`: Include document/image in PDF

## Best Practices
1. ✓ Use unique company names (lowercase, hyphenated)
2. ✓ Always have one default company
3. ✓ Use sort_order for consistent ordering
4. ✓ Set priority for pricing rules
5. ✓ Use tags for easy filtering
6. ✓ Compress images before upload
7. ✓ Test pricing rules before activation
8. ✓ Use soft deletes (is_active=False)

## Troubleshooting
- **Logo not showing**: Check file_path exists
- **Pricing not applying**: Check is_active and priority
- **Document not in PDF**: Check include_in_pdf and pdf_page_number
- **Template not found**: Check template_prefix matches files

## Related Files
- Models: `backend/models/company_models.py`
- Schemas: `backend/models/company_schemas.py`
- Service: `backend/services/company_service.py`
- API: `backend/api/v1/companies.py`
- Migration: `backend/migrations/add_company_tables.py`
