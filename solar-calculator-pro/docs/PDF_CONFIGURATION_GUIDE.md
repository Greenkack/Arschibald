# PDF Configuration System - Complete Guide

## Overview

The PDF Configuration System provides a comprehensive UI for configuring all aspects of PDF generation. Everything is individually configurable and optionally activatable, giving users complete control over PDF output.

## Features

### 1. PDF Type Selection

Choose from 5 different PDF types:

- **Standard PV PDF (8 Seiten)**: Standard photovoltaic offer with 8 pages
- **Erweiterte PV PDF (8+ Seiten)**: Extended PV offer with optional additional pages
- **Standard WP PDF (8 Seiten)**: Standard heat pump offer with 8 pages
- **Erweiterte WP PDF (8+ Seiten)**: Extended heat pump offer with optional pages
- **Multi-PDF**: Generate multiple offers for different companies with one click

### 2. Page Configuration

- **Enable/Disable Pages**: Turn individual pages on or off
- **Custom Headers/Footers**: Set custom text for each page
- **Component Assignment**: Assign components to specific pages
- **Preview**: Generate preview images for any page

### 3. Component Selection

Control which components appear in the PDF:

- **Diagrams**: Include various diagram types
- **Calculations**: Show detailed calculation results
- **Documents**: Embed additional documents from database
- **Images**: Include images and photos
- **Datasheets**: Add product datasheets
- **Tables**: Include data tables
- **Charts**: Add 10 different chart types
- **Text**: Include custom text sections

### 4. Styling Options

#### Color Schemes
- Default
- Blue
- Green
- Orange
- Purple
- Custom (define your own colors)

#### Font Options
- **Font Family**: Helvetica, Times Roman, Courier, Arial, Verdana
- **Font Size**: Adjustable base font size (6-20pt)

### 5. Logo Configuration

- **Per-Page Positioning**: Set logo position for each page
- **Size Control**: Adjust logo width and height
- **Multi-Company Support**: Different logos for different companies

### 6. Watermark Configuration

- **Enable/Disable**: Turn watermark on or off
- **Custom Text**: Set watermark text
- **Opacity**: Adjust transparency (0-100%)
- **Rotation**: Set rotation angle
- **Font Size**: Adjust watermark font size
- **Color**: Choose watermark color

### 7. Multi-PDF Features

#### Company Selection
- Select multiple companies from database
- Each company gets its own PDF
- Company-specific branding (logos, colors, fonts)

#### Product Rotation
- **Automatic Product Rotation**: Each offer gets different products
- **Avoid Duplicate Brands**: No brand repetition across offers
- **Avoid Duplicate Products**: No product repetition across offers
- **Rotation Strategies**: Sequential, random, or optimized

#### Price Increase Rules
- **Automatic Price Increase**: Each subsequent offer is more expensive
- **Configurable Percentage**: Set increase rate (0-50%)
- **Compound Increases**: Apply increases cumulatively
- **Min/Max Thresholds**: Set price boundaries

### 8. Advanced Options

- **3D Visualization**: Include/exclude 3D roof visualization
- **Charts**: Include/exclude all charts
- **Detailed Calculations**: Show/hide calculation details
- **Product Datasheets**: Include/exclude datasheets
- **Additional Documents**: Include/exclude extra documents
- **PDF Compression**: Enable/disable compression
- **PDF Version**: Select PDF version (1.4, 1.7, etc.)
- **Encryption**: Optional PDF encryption

## API Endpoints

### Create Configuration
```http
POST /api/v1/pdf-configuration/
Content-Type: application/json

{
  "pdf_type": "standard_pv",
  "pages": [...],
  "components": [...],
  "color_scheme": "blue",
  "font_family": "Helvetica",
  "font_size_base": 10,
  ...
}
```

**Response:**
```json
{
  "config_id": "uuid",
  "pdf_type": "standard_pv",
  "total_pages": 8,
  "enabled_pages": 8,
  "total_components": 15,
  "enabled_components": 12,
  "estimated_size_mb": 2.5,
  "validation_errors": [],
  "validation_warnings": []
}
```

### Get Configuration
```http
GET /api/v1/pdf-configuration/{config_id}
```

### Update Configuration
```http
PUT /api/v1/pdf-configuration/{config_id}
Content-Type: application/json

{
  "pdf_type": "extended_pv",
  ...
}
```

### Delete Configuration
```http
DELETE /api/v1/pdf-configuration/{config_id}
```

### List Configurations
```http
GET /api/v1/pdf-configuration/?page=1&page_size=20
```

### Generate Preview
```http
POST /api/v1/pdf-configuration/preview
Content-Type: application/json

{
  "config_id": "uuid",
  "page_number": 1,
  "resolution": 150
}
```

**Response:**
```json
{
  "config_id": "uuid",
  "page_number": 1,
  "preview_image_base64": "...",
  "width": 800,
  "height": 1131
}
```

### Generate PDF
```http
POST /api/v1/pdf-configuration/generate
Content-Type: application/json

{
  "config_id": "uuid",
  "output_format": "pdf",
  "filename": "angebot.pdf"
}
```

**Response:**
```json
{
  "config_id": "uuid",
  "pdf_url": "/api/v1/pdf/download/uuid",
  "filename": "angebot.pdf",
  "size_bytes": 2621440,
  "page_count": 8,
  "generation_time_ms": 1250
}
```

### Get Default Configuration
```http
GET /api/v1/pdf-configuration/defaults/{pdf_type}
```

### Validate Configuration
```http
POST /api/v1/pdf-configuration/{config_id}/validate
```

## Usage Examples

### Example 1: Standard PV PDF

```typescript
const config = {
  pdf_type: 'standard_pv',
  project_id: 123,
  pages: [
    { page_number: 1, enabled: true, components: [] },
    { page_number: 2, enabled: true, components: [] },
    // ... pages 3-8
  ],
  components: [],
  color_scheme: 'blue',
  font_family: 'Helvetica',
  font_size_base: 10,
  include_3d_visualization: true,
  include_charts: true,
  include_calculations: true,
  compress_pdf: true
};

const response = await fetch('/api/v1/pdf-configuration/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(config)
});

const result = await response.json();
console.log('Config ID:', result.config_id);
```

### Example 2: Multi-PDF with Product Rotation

```typescript
const config = {
  pdf_type: 'multi_pdf',
  project_id: 123,
  pages: [...],
  components: [],
  companies: [
    { company_id: 1, company_name: 'Firma A' },
    { company_id: 2, company_name: 'Firma B' },
    { company_id: 3, company_name: 'Firma C' }
  ],
  product_rotation: {
    enabled: true,
    avoid_duplicate_brands: true,
    avoid_duplicate_products: true,
    rotation_strategy: 'sequential',
    product_categories: ['pv_modules', 'inverters', 'batteries']
  },
  price_increase: {
    enabled: true,
    increase_percentage: 7.0,
    apply_to_base_price: true,
    compound_increases: true
  }
};

// This will generate 3 PDFs, one for each company
// Each PDF will have different products and increasing prices
```

### Example 3: Extended PV with Custom Pages

```typescript
const config = {
  pdf_type: 'extended_pv',
  project_id: 123,
  pages: [
    // Standard pages 1-8
    ...standardPages,
    // Additional custom pages
    { page_number: 9, enabled: true, components: ['datasheet_1'] },
    { page_number: 10, enabled: true, components: ['document_1', 'image_1'] },
    { page_number: 11, enabled: false, components: [] }  // Disabled
  ],
  components: [
    {
      component_id: 'datasheet_1',
      component_type: 'datasheet',
      enabled: true,
      page: 9,
      position: { x: 50, y: 100 },
      data_source: 'product_123'
    },
    {
      component_id: 'document_1',
      component_type: 'document',
      enabled: true,
      page: 10,
      position: { x: 50, y: 100 },
      data_source: 'doc_456'
    }
  ],
  include_datasheets: true,
  include_documents: true
};
```

## Validation Rules

### Standard PV PDF
- **Required Pages**: 1-8
- **Max Pages**: 8
- **Required Components**: cover, calculations, pricing
- **Optional Components**: charts, 3d_viz, datasheets

### Extended PV PDF
- **Required Pages**: 1-8
- **Max Pages**: 20
- **Required Components**: cover, calculations, pricing
- **Optional Components**: charts, 3d_viz, datasheets, documents, images

### Multi-PDF
- **Required Pages**: 1-8
- **Max Pages**: 8 per company
- **Min Companies**: 1
- **Max Companies**: 20
- **Required**: At least one company selected

## Error Handling

### Validation Errors (Block Generation)
- Missing required pages
- Too many pages
- Duplicate page numbers
- No companies selected (for multi-PDF)
- Invalid logo positions
- Invalid price increase percentage

### Validation Warnings (Allow Generation)
- Missing recommended components
- Watermark enabled but no text
- Very low watermark opacity
- Font size too small or too large
- Price increase >50%
- Product rotation with <2 companies

## Performance Considerations

### Estimated PDF Size
The system estimates PDF size based on:
- Number of enabled pages (0.1 MB per page)
- Components (images: 0.5 MB, charts: 0.2 MB, etc.)
- 3D visualization (1.0 MB)
- Compression (reduces size by ~40%)
- Multi-PDF multiplier (size × number of companies)

### Generation Time
Typical generation times:
- Standard PV PDF: 1-2 seconds
- Extended PV PDF: 2-4 seconds
- Multi-PDF (3 companies): 3-6 seconds
- Multi-PDF (10 companies): 10-20 seconds

## Best Practices

1. **Start with Defaults**: Use the default configuration endpoint to get a valid starting point
2. **Validate Early**: Validate configuration before attempting generation
3. **Use Preview**: Generate previews to check layout before full generation
4. **Optimize Components**: Only enable components you need to reduce file size
5. **Compress PDFs**: Always enable compression for production use
6. **Test Multi-PDF**: Test with 2-3 companies before scaling to 10+
7. **Monitor Size**: Check estimated size before generation
8. **Handle Errors**: Always check validation_errors before proceeding

## Troubleshooting

### Configuration Not Saving
- Check validation_errors in response
- Ensure all required fields are present
- Verify page numbers are unique
- Check company IDs exist in database

### Preview Not Generating
- Ensure configuration is saved first
- Check page number is valid
- Verify page is enabled
- Check resolution is within limits (72-300 DPI)

### PDF Generation Fails
- Validate configuration first
- Check all data sources exist
- Verify project_id is valid
- Ensure sufficient disk space
- Check PDF service logs

### Multi-PDF Issues
- Verify all company IDs exist
- Check product rotation settings
- Ensure price increase percentage is valid
- Verify sufficient products for rotation

## Integration with Other Systems

### Solar Calculator Integration
```typescript
// Get project data from solar calculator
const projectData = await fetchProjectData(projectId);

// Create PDF configuration
const config = {
  pdf_type: 'standard_pv',
  project_id: projectId,
  // ... other settings
};

// Generate PDF
const pdf = await generatePDF(config);
```

### CRM Integration
```typescript
// Generate PDF for customer
const config = {
  pdf_type: 'multi_pdf',
  project_id: projectId,
  companies: await getCustomerPreferredCompanies(customerId),
  // ... other settings
};

// Save to CRM
await savePDFToCRM(customerId, pdf);
```

### Product Database Integration
```typescript
// Get products for rotation
const products = await getProductsForRotation(categories);

// Configure rotation
const config = {
  product_rotation: {
    enabled: true,
    product_categories: categories,
    // ... other settings
  }
};
```

## Future Enhancements

- Real-time collaborative editing
- Template marketplace
- AI-powered layout optimization
- Advanced analytics and reporting
- Batch processing for large-scale generation
- Custom scripting for advanced users
- Integration with external design tools
