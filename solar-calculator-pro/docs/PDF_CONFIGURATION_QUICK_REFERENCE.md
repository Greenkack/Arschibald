# PDF Configuration System - Quick Reference

## Quick Start

```typescript
// 1. Create configuration
const config = {
  pdf_type: 'standard_pv',
  project_id: 123,
  pages: [...],
  components: [],
  color_scheme: 'blue',
  font_family: 'Helvetica',
  font_size_base: 10
};

// 2. Validate
const response = await fetch('/api/v1/pdf-configuration/', {
  method: 'POST',
  body: JSON.stringify(config)
});
const result = await response.json();

// 3. Generate PDF
await fetch('/api/v1/pdf-configuration/generate', {
  method: 'POST',
  body: JSON.stringify({ config_id: result.config_id })
});
```

## PDF Types

| Type | Pages | Description |
|------|-------|-------------|
| `standard_pv` | 8 | Standard PV offer |
| `extended_pv` | 8-20 | Extended PV with optional pages |
| `standard_wp` | 8 | Standard heat pump offer |
| `extended_wp` | 8-20 | Extended heat pump with optional pages |
| `multi_pdf` | 8 per company | Multiple offers for different companies |

## Component Types

- `diagram` - Diagrams and flowcharts
- `calculation` - Calculation results
- `document` - Additional documents
- `image` - Images and photos
- `datasheet` - Product datasheets
- `table` - Data tables
- `chart` - Charts and graphs
- `text` - Text sections

## Color Schemes

- `default` - Standard colors
- `blue` - Blue theme
- `green` - Green theme
- `orange` - Orange theme
- `purple` - Purple theme
- `custom` - Custom colors

## Font Families

- `Helvetica` - Sans-serif, modern
- `Times-Roman` - Serif, traditional
- `Courier` - Monospace
- `Arial` - Sans-serif, clean
- `Verdana` - Sans-serif, readable

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pdf-configuration/` | Create configuration |
| GET | `/pdf-configuration/{id}` | Get configuration |
| PUT | `/pdf-configuration/{id}` | Update configuration |
| DELETE | `/pdf-configuration/{id}` | Delete configuration |
| GET | `/pdf-configuration/` | List configurations |
| POST | `/pdf-configuration/preview` | Generate preview |
| POST | `/pdf-configuration/generate` | Generate PDF |
| GET | `/pdf-configuration/defaults/{type}` | Get defaults |
| POST | `/pdf-configuration/{id}/validate` | Validate config |

## Configuration Options

### Basic Settings
```typescript
{
  pdf_type: 'standard_pv',
  color_scheme: 'blue',
  font_family: 'Helvetica',
  font_size_base: 10
}
```

### Page Configuration
```typescript
{
  pages: [
    {
      page_number: 1,
      enabled: true,
      components: [],
      custom_header: 'Optional header',
      custom_footer: 'Optional footer'
    }
  ]
}
```

### Component Configuration
```typescript
{
  components: [
    {
      component_id: 'chart_1',
      component_type: 'chart',
      enabled: true,
      page: 3,
      position: { x: 50, y: 100 },
      size: { width: 500, height: 300 },
      data_source: 'energy_production',
      options: {}
    }
  ]
}
```

### Logo Configuration
```typescript
{
  logo_positions: {
    1: {
      x: 50,
      y: 50,
      width: 150,
      height: 50,
      page: 1
    }
  }
}
```

### Watermark Configuration
```typescript
{
  watermark: {
    enabled: true,
    text: 'ENTWURF',
    opacity: 0.1,
    rotation: 45,
    font_size: 60,
    color: '#CCCCCC'
  }
}
```

### Multi-PDF Configuration
```typescript
{
  companies: [
    {
      company_id: 1,
      company_name: 'Firma A',
      logo_path: '/logos/firma_a.png',
      color_scheme: 'blue'
    }
  ],
  product_rotation: {
    enabled: true,
    avoid_duplicate_brands: true,
    avoid_duplicate_products: true,
    rotation_strategy: 'sequential'
  },
  price_increase: {
    enabled: true,
    increase_percentage: 7.0,
    apply_to_base_price: true,
    compound_increases: true
  }
}
```

## Validation Rules

### Errors (Block Generation)
- Missing required pages
- Too many pages
- Duplicate page numbers
- No companies (multi-PDF)
- Invalid positions
- Invalid percentages

### Warnings (Allow Generation)
- Missing recommended components
- Empty watermark text
- Low watermark opacity
- Extreme font sizes
- High price increases

## Common Patterns

### Standard PV PDF
```typescript
const config = {
  pdf_type: 'standard_pv',
  project_id: 123,
  include_3d_visualization: true,
  include_charts: true,
  include_calculations: true,
  compress_pdf: true
};
```

### Extended PV with Datasheets
```typescript
const config = {
  pdf_type: 'extended_pv',
  project_id: 123,
  include_datasheets: true,
  include_documents: true,
  // Add extra pages 9-11
  pages: [...standardPages, ...extraPages]
};
```

### Multi-PDF with Rotation
```typescript
const config = {
  pdf_type: 'multi_pdf',
  project_id: 123,
  companies: [
    { company_id: 1, company_name: 'Firma A' },
    { company_id: 2, company_name: 'Firma B' },
    { company_id: 3, company_name: 'Firma C' }
  ],
  product_rotation: {
    enabled: true,
    avoid_duplicate_brands: true
  },
  price_increase: {
    enabled: true,
    increase_percentage: 7.0
  }
};
```

## Response Examples

### Create Configuration Response
```json
{
  "config_id": "550e8400-e29b-41d4-a716-446655440000",
  "pdf_type": "standard_pv",
  "total_pages": 8,
  "enabled_pages": 8,
  "total_components": 15,
  "enabled_components": 12,
  "estimated_size_mb": 2.5,
  "validation_errors": [],
  "validation_warnings": [
    "Font size <8pt may be difficult to read"
  ]
}
```

### Preview Response
```json
{
  "config_id": "550e8400-e29b-41d4-a716-446655440000",
  "page_number": 1,
  "preview_image_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "width": 800,
  "height": 1131
}
```

### Generation Response
```json
{
  "config_id": "550e8400-e29b-41d4-a716-446655440000",
  "pdf_url": "/api/v1/pdf/download/550e8400-e29b-41d4-a716-446655440000",
  "filename": "angebot_1234567890.pdf",
  "size_bytes": 2621440,
  "page_count": 8,
  "generation_time_ms": 1250
}
```

## Performance Tips

1. **Enable Compression**: Always use `compress_pdf: true`
2. **Limit Components**: Only enable needed components
3. **Optimize Images**: Use appropriate image sizes
4. **Batch Multi-PDF**: Generate multiple PDFs in parallel
5. **Cache Configurations**: Reuse configurations when possible
6. **Monitor Size**: Check `estimated_size_mb` before generation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Validation errors | Check required fields and page numbers |
| Preview fails | Ensure configuration is saved first |
| Generation slow | Reduce components, enable compression |
| Large file size | Enable compression, optimize images |
| Multi-PDF fails | Verify company IDs and product availability |

## Support

- **Documentation**: `/docs/PDF_CONFIGURATION_GUIDE.md`
- **API Reference**: `/api/v1/docs`
- **Examples**: `/examples/pdf-configuration/`
- **Issues**: GitHub Issues

## Version

- **API Version**: v1
- **Last Updated**: 2024
- **Status**: Production Ready
