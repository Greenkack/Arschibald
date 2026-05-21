# PDF Branding & Multi-Logo System - Complete Guide

## Overview

The PDF Branding & Multi-Logo System provides comprehensive company-specific branding for PDF generation. Each company can have its own logos, color schemes, fonts, headers, footers, and watermarks applied to all generated PDFs.

## Key Features

### 1. Multi-Logo Support
- Upload multiple logos per company
- Different logos for different contexts (header, footer, body, watermark)
- Logo positioning from YML coordinates
- Support for PNG, JPG, and SVG formats
- Automatic base64 encoding and storage

### 2. Logo Positioning Engine
- YML coordinate integration
- Page-specific positioning
- Context-based positioning (header, footer, body, watermark)
- Transformation support (rotation, scale, opacity)
- Multiple logos per page

### 3. Color Scheme Application
- Primary, secondary, and accent colors
- Text and background colors
- Header and footer colors
- Hex color format (#RRGGBB)
- Real-time color application to PDF elements

### 4. Font Application
- Custom font family selection
- Font size configuration (base, heading, subheading)
- Font weight (normal, bold)
- Consistent typography across all PDFs

### 5. Header/Footer Templates
- Customizable header and footer
- Background colors and text colors
- Logo integration in headers/footers
- Page numbering in German format
- Configurable heights

### 6. Watermark Support
- Custom watermark text
- Opacity control (0.0 to 1.0)
- Rotation angle
- Font size and color
- Centered diagonal placement

### 7. Branding Database Integration
- Complete CRUD operations
- Company-specific branding
- Template system for quick setup
- Asset management (logos, images, fonts)
- Version control and history

## Architecture

### Database Schema

```
company_branding
├── id (PK)
├── company_id (FK → companies.id)
├── Logo Configuration
│   ├── logo_path
│   ├── logo_base64
│   ├── logo_width, logo_height
│   ├── logo_position_x, logo_position_y
│   └── logo_page
├── Color Scheme
│   ├── primary_color, secondary_color, accent_color
│   ├── text_color, background_color
│   └── header_color, footer_color
├── Typography
│   ├── font_family
│   ├── font_size_base, font_size_heading, font_size_subheading
│   └── font_weight
├── Header Configuration
│   ├── header_enabled, header_text, header_height
│   ├── header_background_color, header_text_color
│   └── header_logo_enabled
├── Footer Configuration
│   ├── footer_enabled, footer_text, footer_height
│   ├── footer_background_color, footer_text_color
│   ├── footer_logo_enabled
│   └── footer_page_numbers
├── Watermark Configuration
│   ├── watermark_enabled, watermark_text
│   ├── watermark_opacity, watermark_rotation
│   ├── watermark_font_size
│   └── watermark_color
├── Template Configuration
│   ├── template_path
│   ├── template_type
│   └── yml_coordinates (JSON)
└── Metadata
    ├── is_active
    ├── created_at
    └── updated_at

logo_positions
├── id (PK)
├── branding_id (FK → company_branding.id)
├── page_number (nullable for all pages)
├── context (header|footer|body|watermark)
├── x, y (position coordinates)
├── width, height (dimensions)
├── opacity, rotation, scale (transformations)
└── created_at

branding_templates
├── id (PK)
├── name (unique)
├── description
├── config (JSON - complete branding configuration)
├── preview_image (base64)
├── is_public
├── created_by (FK → users.id)
├── created_at
└── updated_at

branding_assets
├── id (PK)
├── company_id (FK → companies.id)
├── asset_type (logo|image|font|icon)
├── name, description
├── file_path, file_base64
├── file_size, mime_type
├── width, height (for images)
├── is_primary
├── tags (JSON array)
├── created_at
└── updated_at
```

## API Endpoints

### Company Branding

#### Create Branding
```http
POST /api/v1/branding/
Content-Type: application/json

{
  "company_id": 1,
  "logo_width": 120.0,
  "logo_height": 60.0,
  "primary_color": "#0066CC",
  "secondary_color": "#003366",
  "font_family": "Helvetica",
  "header_enabled": true,
  "header_text": "Solar Solutions GmbH",
  "footer_enabled": true,
  "footer_page_numbers": true,
  "watermark_enabled": false
}
```

#### Get Branding
```http
GET /api/v1/branding/{branding_id}
GET /api/v1/branding/company/{company_id}
```

#### Update Branding (Partial)
```http
PUT /api/v1/branding/{branding_id}
Content-Type: application/json

{
  "primary_color": "#FF6600",
  "header_text": "Updated Company Name"
}
```

#### Delete Branding
```http
DELETE /api/v1/branding/{branding_id}
```

#### List Brandings
```http
GET /api/v1/branding/?skip=0&limit=100&active_only=true
```

### Logo Positions

#### Add Logo Position
```http
POST /api/v1/branding/{branding_id}/logo-positions
Content-Type: application/json

{
  "page_number": 1,
  "context": "header",
  "x": 50.0,
  "y": 750.0,
  "width": 120.0,
  "height": 60.0,
  "opacity": 1.0,
  "rotation": 0.0,
  "scale": 1.0
}
```

#### Get Logo Positions
```http
GET /api/v1/branding/{branding_id}/logo-positions
GET /api/v1/branding/{branding_id}/logo-positions?page_number=1
GET /api/v1/branding/{branding_id}/logo-positions?context=header
```

#### Delete Logo Position
```http
DELETE /api/v1/branding/logo-positions/{position_id}
```

### Logo Upload

#### Upload Logo
```http
POST /api/v1/branding/{company_id}/upload-logo
Content-Type: multipart/form-data

file: [logo.png]
```

### YML Coordinates

#### Get YML Coordinates
```http
GET /api/v1/branding/{branding_id}/yml-coordinates/{page_number}
```

Returns coordinates from custom YML or default YML file.

### Color Scheme

#### Get Color Scheme
```http
GET /api/v1/branding/{branding_id}/colors
```

Returns:
```json
{
  "primary": "#0066CC",
  "secondary": "#003366",
  "accent": "#FF6600",
  "text": "#333333",
  "background": "#FFFFFF",
  "header": "#0066CC",
  "footer": "#666666"
}
```

### Branding Templates

#### Create Template
```http
POST /api/v1/branding/templates
Content-Type: application/json

{
  "name": "Modern Blue Theme",
  "description": "Professional blue color scheme with modern fonts",
  "config": {
    "primary_color": "#0066CC",
    "secondary_color": "#003366",
    "font_family": "Helvetica",
    "font_size_base": 10,
    "header_enabled": true,
    "footer_enabled": true
  },
  "is_public": true
}
```

#### Get Template
```http
GET /api/v1/branding/templates/{template_id}
```

#### List Templates
```http
GET /api/v1/branding/templates?public_only=true
```

#### Apply Template
```http
POST /api/v1/branding/{branding_id}/apply-template/{template_id}
```

### Preview

#### Generate Preview
```http
POST /api/v1/branding/preview
Content-Type: application/json

{
  "branding_id": 1,
  "page_type": "standard",
  "include_watermark": true,
  "include_header": true,
  "include_footer": true
}
```

## Usage Examples

### Python Service Usage

```python
from backend.services.branding_service import BrandingService
from backend.models.branding_schemas import CompanyBrandingCreate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Initialize service
service = BrandingService(db)

# Create branding
branding_data = CompanyBrandingCreate(
    company_id=1,
    logo_width=120.0,
    logo_height=60.0,
    primary_color="#0066CC",
    font_family="Helvetica",
    header_enabled=True,
    header_text="My Company",
    footer_enabled=True,
    watermark_enabled=True,
    watermark_text="CONFIDENTIAL"
)
branding = service.create_branding(branding_data)

# Generate PDF with branding
pdf_canvas = canvas.Canvas("output.pdf", pagesize=A4)

# Apply branding
service.apply_color_scheme(pdf_canvas, branding.id)
service.apply_font_settings(pdf_canvas, branding.id, "heading")
service.apply_header(pdf_canvas, branding.id, page_number=1)
service.apply_footer(pdf_canvas, branding.id, page_number=1, total_pages=8)
service.apply_watermark(pdf_canvas, branding.id)
service.apply_logo_positioning(pdf_canvas, branding.id, page_number=1, context="header")

# Add content
pdf_canvas.drawString(100, 700, "My PDF Content")

# Save
pdf_canvas.save()
```

### Upload Logo

```python
# Upload logo
with open("company_logo.png", "rb") as f:
    logo_bytes = f.read()

asset = service.upload_logo(
    company_id=1,
    logo_file=logo_bytes,
    filename="company_logo.png"
)

print(f"Logo uploaded: {asset.id}")
print(f"Dimensions: {asset.width}x{asset.height}")
```

### Add Multiple Logo Positions

```python
from backend.models.branding_schemas import LogoPositionCreate

# Header logo
header_position = LogoPositionCreate(
    page_number=None,  # All pages
    context="header",
    x=50.0,
    y=750.0,
    width=120.0,
    height=60.0,
    opacity=1.0
)
service.add_logo_position(branding.id, header_position)

# Footer logo (smaller)
footer_position = LogoPositionCreate(
    page_number=None,
    context="footer",
    x=50.0,
    y=30.0,
    width=80.0,
    height=40.0,
    opacity=0.7
)
service.add_logo_position(branding.id, footer_position)

# Watermark logo (rotated)
watermark_position = LogoPositionCreate(
    page_number=None,
    context="watermark",
    x=200.0,
    y=400.0,
    width=200.0,
    height=100.0,
    opacity=0.1,
    rotation=45.0
)
service.add_logo_position(branding.id, watermark_position)
```

### Apply Template

```python
# Create template
from backend.models.branding_schemas import BrandingTemplateCreate

template_data = BrandingTemplateCreate(
    name="Corporate Blue",
    description="Professional corporate theme",
    config={
        "primary_color": "#003366",
        "secondary_color": "#0066CC",
        "accent_color": "#FF6600",
        "font_family": "Helvetica",
        "font_size_base": 10,
        "font_size_heading": 16,
        "header_enabled": True,
        "header_height": 80.0,
        "footer_enabled": True,
        "footer_page_numbers": True
    },
    is_public=True
)
template = service.create_template(template_data)

# Apply to branding
updated_branding = service.apply_template(branding.id, template.id)
```

### Load YML Coordinates

```python
# Load coordinates for page 1
coordinates = service.load_yml_coordinates(branding.id, page_number=1)

# Access specific elements
if "logo" in coordinates:
    logo_x = coordinates["logo"]["x"]
    logo_y = coordinates["logo"]["y"]
    print(f"Logo position: ({logo_x}, {logo_y})")

if "title" in coordinates:
    title_x = coordinates["title"]["x"]
    title_y = coordinates["title"]["y"]
    title_font_size = coordinates["title"]["font_size"]
    print(f"Title: ({title_x}, {title_y}), size: {title_font_size}")
```

## Integration with Multi-PDF System

The branding system integrates seamlessly with the Multi-PDF generation system:

```python
# Generate PDFs for multiple companies with their branding
companies = [1, 2, 3, 4, 5]  # Company IDs

for company_id in companies:
    # Get company branding
    branding = service.get_branding_by_company(company_id)
    
    if not branding:
        print(f"No branding for company {company_id}, using default")
        continue
    
    # Generate PDF with company-specific branding
    pdf_canvas = canvas.Canvas(f"offer_company_{company_id}.pdf", pagesize=A4)
    
    # Apply all branding elements
    service.apply_color_scheme(pdf_canvas, branding.id)
    service.apply_font_settings(pdf_canvas, branding.id)
    
    for page_num in range(1, 9):  # 8 pages
        pdf_canvas.showPage()
        service.apply_header(pdf_canvas, branding.id, page_num)
        service.apply_footer(pdf_canvas, branding.id, page_num, 8)
        service.apply_watermark(pdf_canvas, branding.id)
        service.apply_logo_positioning(pdf_canvas, branding.id, page_num, "header")
        
        # Add page content here
        # ...
    
    pdf_canvas.save()
    print(f"✅ Generated PDF for company {company_id}")
```

## Best Practices

### 1. Logo Guidelines
- Use high-resolution logos (minimum 300 DPI)
- Prefer PNG with transparency
- Keep file size under 1MB
- Use square or landscape orientation

### 2. Color Scheme
- Use hex colors (#RRGGBB format)
- Ensure sufficient contrast (text vs background)
- Test colors in print preview
- Consider color blindness accessibility

### 3. Typography
- Use standard PDF fonts (Helvetica, Times, Courier)
- Keep base font size between 8-12pt
- Use consistent font weights
- Test readability at different sizes

### 4. Headers/Footers
- Keep header height between 60-100pt
- Keep footer height between 40-80pt
- Include essential information only
- Test with different page counts

### 5. Watermarks
- Use low opacity (0.05-0.15)
- Keep text short and clear
- Use diagonal rotation (30-60 degrees)
- Test visibility on different backgrounds

### 6. Performance
- Cache branding configurations
- Reuse logo ImageReader objects
- Minimize database queries
- Use batch operations for multiple PDFs

## Troubleshooting

### Logo Not Appearing
- Check logo_base64 is not null
- Verify logo dimensions are positive
- Ensure context matches (header/footer/body)
- Check page_number filter

### Colors Not Applied
- Verify hex color format (#RRGGBB)
- Check color scheme is loaded
- Ensure PDF canvas is using correct colors
- Test with simple shapes first

### Fonts Not Working
- Verify font family is available
- Check font size is reasonable (6-48pt)
- Ensure font weight is valid
- Use standard PDF fonts

### Watermark Too Visible/Invisible
- Adjust opacity (0.05-0.20 range)
- Check watermark_enabled is true
- Verify watermark_text is not empty
- Test rotation angle

### YML Coordinates Not Loading
- Check YML file exists in coords/ folder
- Verify YML syntax is valid
- Ensure page_number is correct
- Check custom yml_coordinates in branding

## Migration Guide

### From Legacy System

```python
# Migrate existing branding data
def migrate_legacy_branding(legacy_data, company_id):
    service = BrandingService(db)
    
    branding_data = CompanyBrandingCreate(
        company_id=company_id,
        logo_path=legacy_data.get("logo_path"),
        primary_color=legacy_data.get("primary_color", "#0066CC"),
        font_family=legacy_data.get("font", "Helvetica"),
        header_enabled=legacy_data.get("show_header", True),
        footer_enabled=legacy_data.get("show_footer", True),
        watermark_enabled=legacy_data.get("show_watermark", False),
        watermark_text=legacy_data.get("watermark_text")
    )
    
    return service.create_branding(branding_data)
```

## Future Enhancements

- [ ] Custom font upload support
- [ ] Advanced watermark patterns
- [ ] Multi-language header/footer templates
- [ ] Branding preview in browser
- [ ] Branding marketplace/sharing
- [ ] A/B testing for branding effectiveness
- [ ] Analytics on branding usage
- [ ] Automated branding suggestions based on industry

## Support

For issues or questions:
- Check API documentation: `/docs`
- Review error logs in `logs/app.log`
- Contact development team
- Submit bug reports with examples

## Version History

- **v1.0.0** (2024-01-20): Initial release
  - Multi-logo support
  - Color scheme application
  - Font customization
  - Header/footer templates
  - Watermark support
  - YML coordinate integration
  - Template system
  - Asset management
