# Extended PV PDF Service - Complete Guide

## Overview

The Extended PV PDF Service provides a flexible system for generating PV (Photovoltaic) PDF documents with optional additional pages beyond the standard 8-page format. This service builds on top of the Standard PV PDF Service and adds dynamic content selection capabilities.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [Component Types](#component-types)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Database Integration](#database-integration)
7. [Customization](#customization)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                Extended PV PDF Service                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Standard PV PDF Service (Base)               │  │
│  │  • 8 standard pages (always included)                │  │
│  │  • YML coordinate system                             │  │
│  │  • Template loading                                  │  │
│  │  • Placeholder replacement                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Extended Components (Optional)               │  │
│  │  • Detailed calculations                             │  │
│  │  • Additional diagrams                               │  │
│  │  • Product datasheets                                │  │
│  │  • Documents from database                           │  │
│  │  • Images from database                              │  │
│  │  • Extended visualizations                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Database Integrations                        │  │
│  │  • DatasheetIntegration                              │  │
│  │  • DocumentIntegration                               │  │
│  │  • ImageIntegration                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Selection → Component Selection → Service → PDF Generation
     │                    │                │            │
     │                    │                │            ▼
     │                    │                │      Standard Pages (1-8)
     │                    │                │            │
     │                    │                ▼            ▼
     │                    │         Database Queries   Additional Pages (9+)
     │                    │                │            │
     │                    ▼                ▼            ▼
     │              Validation      Content Assembly   Final PDF
     │                    │                │            │
     └────────────────────┴────────────────┴────────────┘
```

## Features

### Core Features

1. **Standard 8-Page Base**
   - Always included
   - Uses existing template system
   - YML coordinate-based positioning
   - German number formatting

2. **Optional Additional Pages**
   - Dynamically activated based on user selection
   - Flexible page ordering
   - Database-driven content
   - Full PDF-bytes integration

3. **Component Selection System**
   - Granular control over included content
   - Preview before generation
   - Validation of selections
   - Dependency management

4. **Database Integration**
   - Product datasheets
   - Product-specific documents
   - Dynamic images
   - Flexible content retrieval

### Advanced Features

1. **Dynamic Content**
   - All documents and datasheets from database
   - Not always the same - full flexibility
   - Product-specific variations
   - Real-time content updates

2. **PDF Bytes System**
   - All additional content with PDF bytes
   - Optimized for performance
   - Consistent formatting
   - Quality preservation

3. **German Formatting**
   - Currency: 16.999,00 €
   - Percentages: 85,5%
   - Numbers: 12.500 kWh
   - Dates: 22. Januar 2025

## Component Types

### 1. Detailed Calculations

**Purpose**: Extended calculation details beyond standard pages

**Content**:
- Detailed ROI calculations
- Payback period analysis
- Production forecasts
- Savings projections
- Environmental impact

**Usage**:
```python
selection = ComponentSelection(
    include_detailed_calculations=True
)
```

### 2. Additional Diagrams

**Purpose**: Extra visualizations and charts

**Available Types**:
- `production_monthly`: Monthly production chart
- `consumption_analysis`: Consumption breakdown
- `savings_projection`: Long-term savings forecast
- `roi_analysis`: ROI visualization
- `environmental_impact`: CO2 savings chart

**Usage**:
```python
selection = ComponentSelection(
    include_additional_diagrams=True,
    selected_diagram_types=[
        'production_monthly',
        'savings_projection'
    ]
)
```

### 3. Product Datasheets

**Purpose**: Technical specifications from product database

**Content**:
- Module specifications
- Inverter datasheets
- Battery specifications
- Mounting system details

**Usage**:
```python
selection = ComponentSelection(
    include_product_datasheets=True,
    selected_product_ids=['module_123', 'inverter_456']
)
```

### 4. Documents

**Purpose**: Product-specific documents from database

**Content**:
- Installation guides
- Warranty information
- Certificates
- Compliance documents

**Usage**:
```python
selection = ComponentSelection(
    include_documents=True,
    selected_document_ids=['doc_123', 'doc_456']
)
```

### 5. Images

**Purpose**: Dynamic images from database

**Content**:
- Product photos
- Installation examples
- Reference projects
- Technical drawings

**Usage**:
```python
selection = ComponentSelection(
    include_images=True,
    selected_image_ids=['img_123', 'img_456']
)
```

### 6. Extended Visualizations

**Purpose**: Advanced 3D and technical visualizations

**Content**:
- 3D roof models
- Module placement diagrams
- Shading analysis
- System overview

**Usage**:
```python
selection = ComponentSelection(
    include_extended_visualizations=True
)
```

## Usage Examples

### Example 1: Standard Pages Only

```python
from services.extended_pv_pdf_service import (
    ExtendedPVPDFService,
    ComponentSelection
)

# Initialize service
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

# No additional components
selection = ComponentSelection()

# Generate PDF
pdf_bytes = service.generate_extended_pdf(data, selection)

# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Example 2: With Detailed Calculations

```python
# Enable detailed calculations
selection = ComponentSelection(
    include_detailed_calculations=True
)

# Add calculation data
data = {
    **data,  # Previous data
    'detailed_roi': 8.5,
    'payback_period': 11.8,
    'annual_production': 14000,
    'annual_savings': 2400
}

pdf_bytes = service.generate_extended_pdf(data, selection)
```

### Example 3: With Multiple Components

```python
# Enable multiple components
selection = ComponentSelection(
    include_detailed_calculations=True,
    include_additional_diagrams=True,
    include_product_datasheets=True,
    selected_diagram_types=[
        'production_monthly',
        'savings_projection'
    ],
    selected_product_ids=['module_123', 'inverter_456']
)

pdf_bytes = service.generate_extended_pdf(data, selection)
```

### Example 4: Get Available Components

```python
# Get all available components
components = service.get_available_components()

print("Available Calculations:")
for calc in components['calculations']:
    print(f"  - {calc['name']} (ID: {calc['id']})")

print("\nAvailable Diagrams:")
for diagram in components['diagrams']:
    print(f"  - {diagram['name']} (ID: {diagram['id']})")

# Get product-specific components
product_components = service.get_available_components(
    product_ids=['module_123', 'inverter_456']
)

print("\nProduct Datasheets:")
for datasheet in product_components['datasheets']:
    print(f"  - {datasheet['name']}")
```

## API Reference

### ExtendedPVPDFService

Main service class for extended PDF generation.

#### Constructor

```python
ExtendedPVPDFService(
    template_dir: str = "pdf_templates_static/notext",
    coords_dir: str = "coords",
    database_service = None
)
```

**Parameters**:
- `template_dir`: Directory containing PDF templates
- `coords_dir`: Directory containing YML coordinate files
- `database_service`: Database service instance for content retrieval

#### Methods

##### generate_extended_pdf()

```python
def generate_extended_pdf(
    data: Dict[str, Any],
    component_selection: ComponentSelection
) -> bytes
```

Generate extended PDF with selected components.

**Parameters**:
- `data`: Dictionary containing all placeholder values
- `component_selection`: ComponentSelection instance

**Returns**: PDF bytes

**Example**:
```python
pdf_bytes = service.generate_extended_pdf(data, selection)
```

##### get_available_components()

```python
def get_available_components(
    product_ids: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]
```

Get available components that can be added to PDF.

**Parameters**:
- `product_ids`: Optional list of product IDs for product-specific components

**Returns**: Dictionary of available components by type

**Example**:
```python
components = service.get_available_components(
    product_ids=['module_123']
)
```

### ComponentSelection

Configuration class for component selection.

#### Constructor

```python
ComponentSelection(
    include_detailed_calculations: bool = False,
    include_additional_diagrams: bool = False,
    include_product_datasheets: bool = False,
    include_documents: bool = False,
    include_images: bool = False,
    include_extended_visualizations: bool = False,
    selected_diagram_types: List[str] = None,
    selected_product_ids: List[str] = None,
    selected_document_ids: List[str] = None,
    selected_image_ids: List[str] = None
)
```

**Example**:
```python
selection = ComponentSelection(
    include_detailed_calculations=True,
    include_additional_diagrams=True,
    selected_diagram_types=['production_monthly']
)
```

## Database Integration

### DatasheetIntegration

Retrieves product datasheets from database.

**Required Database Schema**:
```sql
CREATE TABLE product_datasheets (
    id VARCHAR PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    pdf_bytes BLOB NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Methods**:
- `get_product_datasheet(product_id: str) -> Optional[bytes]`
- `get_all_product_datasheets(product_ids: List[str]) -> Dict[str, bytes]`

### DocumentIntegration

Retrieves documents from database.

**Required Database Schema**:
```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    product_id VARCHAR,
    pdf_bytes BLOB NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Methods**:
- `get_document(document_id: str) -> Optional[bytes]`
- `get_product_documents(product_id: str) -> List[Dict[str, Any]]`

### ImageIntegration

Retrieves and converts images to PDF.

**Required Database Schema**:
```sql
CREATE TABLE images (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    image_bytes BLOB NOT NULL,
    mime_type VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Methods**:
- `get_image(image_id: str) -> Optional[bytes]`

## Customization

### Custom Component Types

To add new component types:

1. Define new ComponentType enum value
2. Create generator class
3. Implement generation logic
4. Add to service workflow

**Example**:
```python
class ComponentType(Enum):
    CUSTOM_REPORT = "custom_report"

class CustomReportGenerator:
    def generate_report_page(self, data, template):
        # Implementation
        pass
```

### Custom Templates

To use custom templates:

1. Create template PDF in `pdf_templates_static/notext/`
2. Create coordinate YML in `coords/`
3. Reference in service

**Template Naming**:
- Standard: `nt_nt_01.pdf` to `nt_nt_08.pdf`
- Extended: `nt_nt_09.pdf`, `nt_nt_10.pdf`, etc.
- Generic: `nt_nt_extended.pdf`

## Best Practices

### 1. Component Selection

- **Start Simple**: Begin with standard pages, add components as needed
- **Preview First**: Use preview endpoint to check page count
- **Validate Selection**: Ensure selected IDs exist in database
- **Consider Performance**: More components = longer generation time

### 2. Data Preparation

- **Complete Data**: Provide all required fields
- **German Formatting**: Use German number format for display
- **Validation**: Validate data before PDF generation
- **Defaults**: Provide sensible defaults for optional fields

### 3. Error Handling

- **Graceful Degradation**: Missing components should not fail entire PDF
- **Logging**: Log all errors and warnings
- **User Feedback**: Provide clear error messages
- **Retry Logic**: Implement retry for transient failures

### 4. Performance

- **Caching**: Cache frequently used templates and coordinates
- **Async Generation**: Use async for large PDFs
- **Batch Processing**: Generate multiple PDFs in parallel
- **Resource Cleanup**: Clean up temporary files

## Troubleshooting

### Common Issues

#### 1. PDF Generation Fails

**Symptoms**: Empty PDF or exception during generation

**Solutions**:
- Check template files exist
- Verify coordinate files are valid
- Ensure all required data fields are provided
- Check database connectivity

#### 2. Missing Components

**Symptoms**: Selected components not appearing in PDF

**Solutions**:
- Verify component IDs exist in database
- Check database service is configured
- Ensure component selection is correct
- Review logs for errors

#### 3. Formatting Issues

**Symptoms**: Numbers not in German format

**Solutions**:
- Use GermanNumberFormatter
- Verify locale settings
- Check data types (should be float/int)
- Review formatting configuration

#### 4. Performance Issues

**Symptoms**: Slow PDF generation

**Solutions**:
- Reduce number of components
- Use async generation
- Enable caching
- Optimize database queries
- Check template file sizes

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Testing

Run tests:

```bash
# Run all tests
pytest tests/test_extended_pv_pdf_service.py -v

# Run specific test
pytest tests/test_extended_pv_pdf_service.py::TestExtendedPVPDFService::test_generate_extended_pdf_standard_only -v

# Run with coverage
pytest tests/test_extended_pv_pdf_service.py --cov=services.extended_pv_pdf_service
```

## Support

For issues or questions:
- Check logs for error messages
- Review this documentation
- Run demo script: `python demo_extended_pv_pdf.py`
- Check test suite for examples

## Version History

- **1.0.0** (2025-01-22): Initial release
  - Standard 8-page PDF generation
  - Optional additional pages
  - Component selection system
  - Database integration
  - German number formatting
