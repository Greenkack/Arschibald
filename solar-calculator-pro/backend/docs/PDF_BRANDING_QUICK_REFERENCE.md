# PDF Branding & Multi-Logo System - Quick Reference

## Quick Start

### 1. Create Company Branding
```python
from backend.services.branding_service import BrandingService
from backend.models.branding_schemas import CompanyBrandingCreate

service = BrandingService(db)
branding = service.create_branding(CompanyBrandingCreate(
    company_id=1,
    primary_color="#0066CC",
    font_family="Helvetica",
    header_enabled=True,
    footer_enabled=True
))
```

### 2. Upload Logo
```python
with open("logo.png", "rb") as f:
    asset = service.upload_logo(1, f.read(), "logo.png")
```

### 3. Apply to PDF
```python
from reportlab.pdfgen import canvas

pdf = canvas.Canvas("output.pdf")
service.apply_header(pdf, branding.id, 1)
service.apply_footer(pdf, branding.id, 1, 8)
service.apply_logo_positioning(pdf, branding.id, 1, "header")
pdf.save()
```

## API Endpoints Cheat Sheet

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/branding/` | POST | Create branding |
| `/api/v1/branding/{id}` | GET | Get branding |
| `/api/v1/branding/company/{id}` | GET | Get by company |
| `/api/v1/branding/{id}` | PUT | Update branding |
| `/api/v1/branding/{id}` | DELETE | Delete branding |
| `/api/v1/branding/{id}/logo-positions` | POST | Add logo position |
| `/api/v1/branding/{id}/logo-positions` | GET | Get positions |
| `/api/v1/branding/{company_id}/upload-logo` | POST | Upload logo |
| `/api/v1/branding/{id}/yml-coordinates/{page}` | GET | Get YML coords |
| `/api/v1/branding/{id}/colors` | GET | Get color scheme |
| `/api/v1/branding/templates` | POST | Create template |
| `/api/v1/branding/templates` | GET | List templates |
| `/api/v1/branding/{id}/apply-template/{tid}` | POST | Apply template |

## Configuration Options

### Logo Configuration
```python
{
    "logo_width": 120.0,          # Width in points
    "logo_height": 60.0,          # Height in points
    "logo_position_x": 50.0,      # X coordinate
    "logo_position_y": 750.0,     # Y coordinate
    "logo_page": "all"            # all|first|header|footer
}
```

### Color Scheme
```python
{
    "primary_color": "#0066CC",
    "secondary_color": "#003366",
    "accent_color": "#FF6600",
    "text_color": "#333333",
    "background_color": "#FFFFFF",
    "header_color": "#0066CC",
    "footer_color": "#666666"
}
```

### Typography
```python
{
    "font_family": "Helvetica",
    "font_size_base": 10,
    "font_size_heading": 16,
    "font_size_subheading": 12,
    "font_weight": "normal"       # normal|bold
}
```

### Header
```python
{
    "header_enabled": True,
    "header_text": "Company Name",
    "header_height": 80.0,
    "header_background_color": "#0066CC",
    "header_text_color": "#FFFFFF",
    "header_logo_enabled": True
}
```

### Footer
```python
{
    "footer_enabled": True,
    "footer_text": "Contact Info",
    "footer_height": 60.0,
    "footer_background_color": "#F0F0F0",
    "footer_text_color": "#333333",
    "footer_logo_enabled": False,
    "footer_page_numbers": True
}
```

### Watermark
```python
{
    "watermark_enabled": True,
    "watermark_text": "CONFIDENTIAL",
    "watermark_opacity": 0.1,     # 0.0 to 1.0
    "watermark_rotation": 45.0,   # Degrees
    "watermark_font_size": 60,
    "watermark_color": "#CCCCCC"
}
```

## Service Methods

### Branding CRUD
```python
service.create_branding(data)
service.get_branding(id)
service.get_branding_by_company(company_id)
service.update_branding(id, data)
service.delete_branding(id)
service.list_brandings(skip, limit, active_only)
```

### Logo Operations
```python
service.add_logo_position(branding_id, position_data)
service.get_logo_positions(branding_id, page_number, context)
service.delete_logo_position(position_id)
service.upload_logo(company_id, logo_bytes, filename)
service.get_logo_image(branding_id)
```

### PDF Application
```python
service.apply_logo_positioning(pdf_canvas, branding_id, page_number, context)
service.apply_color_scheme(pdf_canvas, branding_id)
service.apply_font_settings(pdf_canvas, branding_id, font_type)
service.apply_header(pdf_canvas, branding_id, page_number)
service.apply_footer(pdf_canvas, branding_id, page_number, total_pages)
service.apply_watermark(pdf_canvas, branding_id)
```

### YML & Templates
```python
service.load_yml_coordinates(branding_id, page_number)
service.create_template(template_data, user_id)
service.get_template(template_id)
service.list_templates(public_only)
service.apply_template(branding_id, template_id)
```

### Utilities
```python
service.get_color(branding_id, color_type)  # Returns hex color
```

## Logo Position Contexts

| Context | Description | Typical Position |
|---------|-------------|------------------|
| `header` | Header area | Top of page |
| `footer` | Footer area | Bottom of page |
| `body` | Main content area | Anywhere in content |
| `watermark` | Background watermark | Center, rotated |

## Common Patterns

### Multi-Company PDF Generation
```python
for company_id in [1, 2, 3, 4, 5]:
    branding = service.get_branding_by_company(company_id)
    pdf = canvas.Canvas(f"offer_{company_id}.pdf")
    
    for page in range(1, 9):
        pdf.showPage()
        service.apply_header(pdf, branding.id, page)
        service.apply_footer(pdf, branding.id, page, 8)
        service.apply_logo_positioning(pdf, branding.id, page, "header")
        # Add content...
    
    pdf.save()
```

### Template-Based Setup
```python
# Create template
template = service.create_template(BrandingTemplateCreate(
    name="Modern Blue",
    config={
        "primary_color": "#0066CC",
        "font_family": "Helvetica",
        "header_enabled": True
    }
))

# Apply to multiple companies
for company_id in [1, 2, 3]:
    branding = service.get_branding_by_company(company_id)
    service.apply_template(branding.id, template.id)
```

### Custom Logo Positions
```python
# Different logo on each page
for page_num in range(1, 9):
    service.add_logo_position(branding.id, LogoPositionCreate(
        page_number=page_num,
        context="header",
        x=50.0 + (page_num * 10),  # Shift right on each page
        y=750.0,
        width=120.0,
        height=60.0
    ))
```

## Error Handling

```python
from backend.core.errors import NotFoundError, ValidationError

try:
    branding = service.create_branding(data)
except ValidationError as e:
    print(f"Validation error: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
```

## Testing

```python
# Test branding application
def test_branding():
    service = BrandingService(db)
    
    # Create test branding
    branding = service.create_branding(CompanyBrandingCreate(
        company_id=1,
        primary_color="#FF0000",
        header_text="TEST COMPANY"
    ))
    
    # Generate test PDF
    pdf = canvas.Canvas("test.pdf")
    service.apply_header(pdf, branding.id, 1)
    service.apply_footer(pdf, branding.id, 1, 1)
    pdf.save()
    
    # Verify
    assert branding.primary_color == "#FF0000"
    assert branding.header_text == "TEST COMPANY"
    
    # Cleanup
    service.delete_branding(branding.id)
```

## Performance Tips

1. **Cache branding objects**: Don't query for every page
2. **Reuse ImageReader**: Create once, use multiple times
3. **Batch operations**: Process multiple companies together
4. **Lazy load YML**: Only load when needed
5. **Optimize images**: Compress logos before upload

## Common Issues

| Issue | Solution |
|-------|----------|
| Logo not showing | Check `logo_base64` is set and `header_logo_enabled=True` |
| Wrong colors | Verify hex format `#RRGGBB` |
| Font errors | Use standard PDF fonts (Helvetica, Times, Courier) |
| Watermark invisible | Increase opacity to 0.1-0.2 |
| YML not loading | Check file exists in `coords/seite{N}.yml` |

## Database Schema Summary

```
company_branding (main table)
  ├── Logo config (path, base64, dimensions, position)
  ├── Colors (7 colors)
  ├── Fonts (family, sizes, weight)
  ├── Header (enabled, text, height, colors, logo)
  ├── Footer (enabled, text, height, colors, logo, page numbers)
  ├── Watermark (enabled, text, opacity, rotation, size, color)
  └── Template (path, type, yml_coordinates)

logo_positions (multiple logos per branding)
  ├── page_number (nullable)
  ├── context (header|footer|body|watermark)
  ├── x, y, width, height
  └── opacity, rotation, scale

branding_templates (reusable templates)
  ├── name, description
  ├── config (JSON)
  └── preview_image

branding_assets (logos, images, fonts)
  ├── asset_type (logo|image|font|icon)
  ├── file_base64
  └── dimensions, metadata
```

## Integration Points

### With Multi-PDF System
```python
# Task 120: Multi-PDF Template System
# Task 121: Product Rotation System
# Task 122: Price Increase System
# Task 123: Batch Generation

# Each company gets its own branding applied
```

### With YML Coordinates
```python
# Task 114-118: Standard/Extended PV/WP PDFs
# Coordinates loaded from coords/ folder
# Custom coordinates in branding.yml_coordinates
```

### With PDF Generation
```python
# Task 103: PDF Generation Advanced Service
# Task 126: PDF Chart Integration
# All PDF generation uses branding service
```

## Version Compatibility

- **Backend**: Python 3.10+
- **Database**: SQLAlchemy 2.0+
- **PDF**: ReportLab 4.0+
- **Images**: Pillow 10.0+

## Next Steps

1. ✅ Create company branding
2. ✅ Upload logo
3. ✅ Configure colors and fonts
4. ✅ Set up header/footer
5. ✅ Add logo positions
6. ✅ Test with PDF generation
7. ✅ Create templates for reuse
8. ✅ Integrate with multi-PDF system

## Resources

- Full Guide: `PDF_BRANDING_GUIDE.md`
- API Docs: `/docs` endpoint
- Demo Script: `demo_branding.py`
- Migration: `migrations/add_branding_tables.py`
