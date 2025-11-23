# Company Database System - Complete Guide

## Overview

The Company Database System is the foundation of the Multi-PDF generation feature. It allows managing multiple companies, each with their own branding, pricing rules, documents, and images. With one click, the system can generate customized PDF offers for multiple companies simultaneously.

## Key Concepts

### Multi-Company Architecture

- **One Click → Multiple PDFs**: Generate offers for 8+ companies simultaneously
- **Individual Branding**: Each company has unique logos, colors, and templates
- **Dynamic Pricing**: Company-specific pricing rules and markups
- **Custom Content**: Company-specific documents, images, and datasheets
- **Template System**: Each company can have custom PDF templates

### Database Schema

The system consists of 4 main tables:

1. **companies** - Core company information
2. **company_documents** - Documents (datasheets, certificates, etc.)
3. **company_images** - Images (product photos, facility images, etc.)
4. **company_pricing_rules** - Custom pricing rules per company

## Company Model

### Core Fields

```python
class Company:
    # Basic Information
    id: int
    name: str  # Unique identifier (e.g., "solar-gmbh")
    display_name: str  # Display name (e.g., "Solar GmbH")
    
    # Contact Information
    email: str
    phone: str
    website: str
    address_street: str
    address_city: str
    address_postal_code: str
    address_country: str
    
    # Tax and Legal
    tax_id: str
    vat_number: str
    registration_number: str
    
    # Branding
    logo_path: str
    logo_position_x: float  # X position in PDF (mm)
    logo_position_y: float  # Y position in PDF (mm)
    logo_width: float  # Logo width (mm)
    logo_height: float  # Logo height (mm)
    primary_color: str  # Hex color (e.g., "#0066CC")
    secondary_color: str
    accent_color: str
    
    # Pricing Rules
    base_markup_percentage: float  # Base markup for all products
    price_increase_percentage: float  # Increase for multi-PDF (default: 7%)
    
    # Template Configuration
    template_prefix: str  # e.g., "f1", "f2" for template files
    template_folder: str  # Custom template folder path
    
    # Status
    is_active: bool
    is_default: bool
    sort_order: int
```

### Example Company

```json
{
  "name": "solar-gmbh",
  "display_name": "Solar GmbH",
  "email": "info@solar-gmbh.de",
  "phone": "+49 123 456789",
  "website": "https://www.solar-gmbh.de",
  "address_street": "Sonnenstraße 1",
  "address_city": "München",
  "address_postal_code": "80331",
  "primary_color": "#0066CC",
  "secondary_color": "#FF6600",
  "accent_color": "#00CC66",
  "base_markup_percentage": 0.0,
  "price_increase_percentage": 7.0,
  "template_prefix": "f1",
  "is_active": true,
  "is_default": true
}
```

## Company Documents

Documents are files associated with a company that can be included in PDFs.

### Document Types

- **datasheet** - Product datasheets
- **certificate** - Certificates (TÜV, ISO, etc.)
- **brochure** - Marketing brochures
- **contract** - Contract templates
- **warranty** - Warranty documents
- **manual** - Installation manuals

### Document Model

```python
class CompanyDocument:
    id: int
    company_id: int
    title: str
    description: str
    document_type: str
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    
    # PDF Integration
    include_in_pdf: bool
    pdf_page_number: int  # Which page to include on
    pdf_position_x: float
    pdf_position_y: float
    
    # Metadata
    tags: List[str]
    sort_order: int
    is_active: bool
```

### Example Document

```json
{
  "company_id": 1,
  "title": "Produktdatenblatt PV-Module",
  "description": "Technische Daten der PV-Module",
  "document_type": "datasheet",
  "file_path": "/uploads/documents/pv_module_datasheet.pdf",
  "file_name": "pv_module_datasheet.pdf",
  "include_in_pdf": true,
  "pdf_page_number": 7,
  "is_active": true
}
```

## Company Images

Images are visual assets associated with a company.

### Image Types

- **product** - Product photos
- **facility** - Facility/office images
- **team** - Team photos
- **logo** - Company logos
- **reference** - Reference project images

### Image Model

```python
class CompanyImage:
    id: int
    company_id: int
    title: str
    description: str
    image_type: str
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    width: int  # Original width in pixels
    height: int  # Original height in pixels
    
    # PDF Integration
    include_in_pdf: bool
    pdf_page_number: int
    pdf_position_x: float
    pdf_position_y: float
    pdf_width: float  # Width in PDF (mm)
    pdf_height: float  # Height in PDF (mm)
    
    # Metadata
    tags: List[str]
    sort_order: int
    is_active: bool
```

## Company Pricing Rules

Pricing rules allow customizing prices per company.

### Rule Types

- **global** - Applies to all products
- **product** - Applies to specific product
- **category** - Applies to product category
- **brand** - Applies to specific brand

### Pricing Rule Model

```python
class CompanyPricingRule:
    id: int
    company_id: int
    rule_name: str
    rule_type: str
    
    # Target
    target_id: int  # Product ID, Category ID, etc.
    target_name: str
    
    # Pricing Adjustments
    markup_percentage: float
    markup_fixed: float
    discount_percentage: float
    discount_fixed: float
    
    # Conditions
    min_quantity: int
    max_quantity: int
    valid_from: datetime
    valid_until: datetime
    
    # Priority
    priority: int  # Higher priority rules apply first
    is_active: bool
```

### Example Pricing Rule

```json
{
  "company_id": 1,
  "rule_name": "Mengenrabatt ab 20 Module",
  "rule_type": "global",
  "discount_percentage": 5.0,
  "min_quantity": 20,
  "priority": 10,
  "is_active": true
}
```

## API Endpoints

### Company Management

```
POST   /api/v1/companies/                    # Create company
GET    /api/v1/companies/                    # List companies
GET    /api/v1/companies/selection           # Get companies for UI selection
GET    /api/v1/companies/{id}                # Get company by ID
PUT    /api/v1/companies/{id}                # Update company
DELETE /api/v1/companies/{id}                # Delete company (soft delete)
GET    /api/v1/companies/{id}/data           # Get complete company data
```

### Logo Management

```
POST   /api/v1/companies/{id}/logo           # Upload company logo
GET    /api/v1/companies/{id}/logo/config    # Get logo configuration
```

### Document Management

```
POST   /api/v1/companies/{id}/documents      # Create document
GET    /api/v1/companies/{id}/documents      # List documents
PUT    /api/v1/companies/documents/{doc_id}  # Update document
DELETE /api/v1/companies/documents/{doc_id}  # Delete document
```

### Image Management

```
POST   /api/v1/companies/{id}/images         # Create image
GET    /api/v1/companies/{id}/images         # List images
PUT    /api/v1/companies/images/{img_id}     # Update image
DELETE /api/v1/companies/images/{img_id}     # Delete image
```

### Pricing Rule Management

```
POST   /api/v1/companies/{id}/pricing-rules  # Create pricing rule
GET    /api/v1/companies/{id}/pricing-rules  # List pricing rules
PUT    /api/v1/companies/pricing-rules/{id}  # Update pricing rule
DELETE /api/v1/companies/pricing-rules/{id}  # Delete pricing rule
```

## Usage Examples

### Creating a Company

```python
import requests

company_data = {
    "name": "solar-gmbh",
    "display_name": "Solar GmbH",
    "email": "info@solar-gmbh.de",
    "phone": "+49 123 456789",
    "primary_color": "#0066CC",
    "secondary_color": "#FF6600",
    "base_markup_percentage": 0.0,
    "price_increase_percentage": 7.0,
    "template_prefix": "f1",
    "is_active": True,
    "is_default": True
}

response = requests.post(
    "http://localhost:8000/api/v1/companies/",
    json=company_data
)

company = response.json()
print(f"Created company: {company['id']}")
```

### Uploading a Logo

```python
import requests

files = {'file': open('logo.png', 'rb')}
params = {
    'position_x': 50.0,
    'position_y': 20.0,
    'width': 50.0,
    'height': 30.0
}

response = requests.post(
    f"http://localhost:8000/api/v1/companies/{company_id}/logo",
    files=files,
    params=params
)

print(response.json())
```

### Loading Company Data

```python
import requests

response = requests.get(
    f"http://localhost:8000/api/v1/companies/{company_id}/data"
)

company_data = response.json()

# Access company information
print(f"Company: {company_data['company']['display_name']}")
print(f"Documents: {len(company_data['documents'])}")
print(f"Images: {len(company_data['images'])}")
print(f"Pricing Rules: {len(company_data['pricing_rules'])}")

# Access branding
branding = company_data['branding']
print(f"Logo: {branding['logo_path']}")
print(f"Primary Color: {branding['colors']['primary']}")

# Access pricing
pricing = company_data['pricing']
print(f"Base Markup: {pricing['base_markup']}%")
print(f"Price Increase: {pricing['price_increase']}%")
```

### Getting Companies for Selection UI

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/companies/selection"
)

selection_data = response.json()

print(f"Total Companies: {selection_data['total']}")
print(f"Active Companies: {selection_data['active_count']}")
print(f"Default Company ID: {selection_data['default_company_id']}")

for company in selection_data['companies']:
    print(f"- {company['display_name']} ({company['name']})")
    print(f"  Documents: {company['document_count']}")
    print(f"  Images: {company['image_count']}")
    print(f"  Pricing Rules: {company['pricing_rule_count']}")
```

## Database Migration

### Running the Migration

```bash
# Create tables
python -m backend.migrations.add_company_tables upgrade

# Seed sample data
python -m backend.migrations.add_company_tables seed

# Drop tables (if needed)
python -m backend.migrations.add_company_tables downgrade
```

### Sample Data

The migration includes sample data for 3 companies:

1. **Solar GmbH** (Default)
   - Template prefix: f1
   - Primary color: #0066CC
   - Base markup: 0%
   - Price increase: 7%

2. **Energie Plus AG**
   - Template prefix: f2
   - Primary color: #FF6600
   - Base markup: 5%
   - Price increase: 7%

3. **Grüne Energie GmbH**
   - Template prefix: f3
   - Primary color: #00CC66
   - Base markup: 3%
   - Price increase: 7%

## Integration with Multi-PDF System

The company database integrates with the multi-PDF generation system:

1. **Company Selection**: User selects multiple companies from the UI
2. **Data Loading**: System loads complete data for each company
3. **Template Assignment**: Each company gets its template (based on prefix)
4. **Branding Application**: Logos, colors applied to each PDF
5. **Pricing Calculation**: Company-specific pricing rules applied
6. **Content Inclusion**: Company documents and images included
7. **PDF Generation**: One PDF per company with customized content
8. **Batch Download**: All PDFs packaged in ZIP file

## Best Practices

### Company Management

1. **Unique Names**: Use lowercase, hyphenated names (e.g., "solar-gmbh")
2. **Display Names**: Use proper capitalization (e.g., "Solar GmbH")
3. **Default Company**: Always have one default company
4. **Sort Order**: Use sort_order for consistent ordering in UI
5. **Active Status**: Use is_active for soft deletes

### Document Management

1. **File Organization**: Store files in organized folder structure
2. **File Naming**: Use descriptive, consistent file names
3. **PDF Integration**: Set pdf_page_number for automatic inclusion
4. **Tags**: Use tags for easy filtering and search
5. **Active Status**: Deactivate instead of deleting

### Image Management

1. **Image Optimization**: Compress images before upload
2. **Dimensions**: Store original dimensions for reference
3. **PDF Sizing**: Set appropriate pdf_width and pdf_height
4. **Image Types**: Use consistent image_type values
5. **Sort Order**: Use sort_order for consistent display

### Pricing Rules

1. **Priority System**: Use priority to control rule application order
2. **Rule Naming**: Use descriptive names for easy identification
3. **Date Ranges**: Set valid_from and valid_until for time-limited rules
4. **Quantity Conditions**: Use min_quantity and max_quantity for volume discounts
5. **Testing**: Test pricing rules thoroughly before activation

## Troubleshooting

### Common Issues

**Issue**: Company name already exists
- **Solution**: Use unique company names or update existing company

**Issue**: Logo not displaying in PDF
- **Solution**: Check logo_path exists and file is accessible

**Issue**: Pricing rules not applying
- **Solution**: Check is_active=True and priority is set correctly

**Issue**: Documents not included in PDF
- **Solution**: Verify include_in_pdf=True and pdf_page_number is set

**Issue**: Template not found
- **Solution**: Verify template_prefix matches template file names

## Next Steps

After setting up the company database:

1. **Create Companies**: Add your companies via API or admin UI
2. **Upload Logos**: Upload company logos and configure positioning
3. **Add Documents**: Upload datasheets, certificates, etc.
4. **Add Images**: Upload product photos and facility images
5. **Configure Pricing**: Set up pricing rules per company
6. **Test Multi-PDF**: Generate test PDFs for multiple companies
7. **Refine Templates**: Adjust templates based on results

## Related Documentation

- [Multi-PDF Generation Guide](./MULTI_PDF_GENERATION_GUIDE.md)
- [Template System Guide](./TEMPLATE_SYSTEM_GUIDE.md)
- [Pricing System Guide](./PRICING_SYSTEM_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
