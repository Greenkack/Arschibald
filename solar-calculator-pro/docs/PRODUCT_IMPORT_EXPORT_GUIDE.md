# Product Data Import/Export Guide

Complete guide for importing and exporting product data in the Solar Calculator Pro application.

## Table of Contents

1. [Overview](#overview)
2. [Supported Formats](#supported-formats)
3. [Import Operations](#import-operations)
4. [Export Operations](#export-operations)
5. [Data Mapping](#data-mapping)
6. [Validation](#validation)
7. [API Integration](#api-integration)
8. [Best Practices](#best-practices)

## Overview

The Product Import/Export system allows you to:
- Import products from Excel, CSV, XML, and external APIs
- Export products to Excel, CSV, XML, and JSON
- Validate data before importing
- Map custom column names to standard fields
- Handle bulk operations efficiently
- Track import/export results

## Supported Formats

### Import Formats
- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv` (UTF-8, customizable delimiter)
- **XML**: `.xml` (customizable structure)
- **JSON**: Via API integration

### Export Formats
- **Excel**: `.xlsx` with optional metadata sheet
- **CSV**: `.csv` with customizable delimiter and encoding
- **XML**: `.xml` with customizable structure
- **JSON**: `.json` with pretty printing option

## Import Operations

### Excel Import

```python
# Example: Import from Excel
POST /api/v1/product-import-export/import/excel

# With file upload
files = {'file': open('products.xlsx', 'rb')}
response = requests.post(url, files=files)
```

**Required Columns:**
- `name`: Product name (required)
- `sku`: Stock Keeping Unit (required, unique)

**Optional Columns:**
- `category`: Product category
- `manufacturer`: Manufacturer name
- `price`: Product price
- `description`: Product description
- `spec_*`: Custom specifications (e.g., `spec_power`, `spec_efficiency`)

### CSV Import

```python
# Example: Import from CSV
POST /api/v1/product-import-export/import/csv?delimiter=,&encoding=utf-8

# With custom delimiter
POST /api/v1/product-import-export/import/csv?delimiter=;&encoding=utf-8
```

**CSV Format Example:**
```csv
name,sku,category,manufacturer,price,description
Solar Module 400W,SM-400-001,Solar Modules,SolarTech,299.99,High-efficiency module
Inverter 5kW,INV-5K-001,Inverters,PowerTech,1499.99,Hybrid inverter
```

### XML Import

```python
# Example: Import from XML
POST /api/v1/product-import-export/import/xml?root_element=products&product_element=product
```

**XML Format Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product>
        <name>Solar Module 400W</name>
        <sku>SM-400-001</sku>
        <category>Solar Modules</category>
        <manufacturer>SolarTech</manufacturer>
        <price>299.99</price>
        <description>High-efficiency module</description>
    </product>
</products>
```

### API Integration

```python
# Example: Import from external API
POST /api/v1/product-import-export/import/api

{
    "api_url": "https://api.supplier.com/products",
    "api_key": "your-api-key",
    "headers": {
        "Accept": "application/json"
    },
    "params": {
        "category": "solar",
        "limit": 100
    }
}
```

## Export Operations

### Excel Export

```python
# Example: Export to Excel
POST /api/v1/product-import-export/export/excel

{
    "format": "excel",
    "filters": {
        "category": "Solar Modules",
        "min_price": 100,
        "max_price": 1000
    },
    "columns": ["name", "sku", "price", "manufacturer"],
    "include_metadata": true
}
```

**Features:**
- Multiple sheets (Products + Metadata)
- Formatted columns
- Automatic column width adjustment
- German number formatting

### CSV Export

```python
# Example: Export to CSV
POST /api/v1/product-import-export/export/csv?delimiter=,&encoding=utf-8

{
    "format": "csv",
    "filters": {
        "manufacturer": "SolarTech"
    },
    "columns": ["name", "sku", "price"]
}
```

### XML Export

```python
# Example: Export to XML
POST /api/v1/product-import-export/export/xml?root_element=products&product_element=product

{
    "format": "xml",
    "filters": {
        "category": "Inverters"
    }
}
```

### JSON Export

```python
# Example: Export to JSON
POST /api/v1/product-import-export/export/json?pretty=true

{
    "format": "json",
    "columns": ["name", "sku", "price", "specifications"]
}
```

## Data Mapping

### Column Mapping

Map custom column names to standard fields:

```python
{
    "mapping": {
        "name_column": "Product Name",
        "sku_column": "Article Number",
        "category_column": "Product Category",
        "manufacturer_column": "Brand",
        "price_column": "Unit Price",
        "description_column": "Product Description"
    }
}
```

### Custom Specifications

Add custom product specifications with `spec_` prefix:

```python
# In your import file:
spec_power: "400W"
spec_efficiency: "21.5%"
spec_warranty: "25 years"
spec_dimensions: "1956x992x40mm"
spec_weight: "22.5kg"
```

## Validation

### Validate Before Import

```python
# Example: Validate without importing
POST /api/v1/product-import-export/import/excel?validate_only=true

# Response:
{
    "success": true,
    "total_rows": 100,
    "imported_count": 0,
    "failed_count": 0,
    "message": "Validation successful"
}
```

### Validation Rules

1. **Required Fields:**
   - `name`: Must not be empty
   - `sku`: Must not be empty and must be unique

2. **Data Types:**
   - `price`: Must be numeric and non-negative
   - `specifications`: Must be valid JSON if provided

3. **Constraints:**
   - `sku`: Must be unique across all products
   - `name`: Maximum 255 characters
   - `sku`: Maximum 100 characters

### Validation Errors

```python
# Example validation error response:
{
    "success": false,
    "total_rows": 100,
    "imported_count": 0,
    "failed_count": 5,
    "errors": [
        {
            "row": 5,
            "errors": ["SKU is required", "Price must be non-negative"]
        },
        {
            "row": 23,
            "errors": ["Duplicate SKU"]
        }
    ]
}
```

## API Integration

### External API Import

Import products from external supplier APIs:

```python
# Example: Import from supplier API
POST /api/v1/product-import-export/import/api

{
    "api_url": "https://api.supplier.com/v1/products",
    "api_key": "your-api-key-here",
    "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    "params": {
        "category": "solar-modules",
        "in_stock": true,
        "limit": 500
    },
    "response_path": "data.products"
}
```

### Supported API Response Formats

1. **Array Format:**
```json
[
    {"name": "Product 1", "sku": "SKU-001", ...},
    {"name": "Product 2", "sku": "SKU-002", ...}
]
```

2. **Object Format:**
```json
{
    "products": [
        {"name": "Product 1", "sku": "SKU-001", ...},
        {"name": "Product 2", "sku": "SKU-002", ...}
    ]
}
```

3. **Nested Format:**
```json
{
    "data": {
        "products": [
            {"name": "Product 1", "sku": "SKU-001", ...}
        ]
    }
}
```

## Best Practices

### Import Best Practices

1. **Always Validate First:**
   ```python
   # Validate before importing
   result = import_from_excel(file, validate_only=True)
   if result.success:
       # Proceed with actual import
       import_from_excel(file, validate_only=False)
   ```

2. **Use Column Mapping:**
   - Map your custom column names to standard fields
   - Reduces data transformation errors
   - Makes imports more flexible

3. **Handle Large Files:**
   - Split large files into smaller batches
   - Import in chunks of 1000-5000 rows
   - Monitor memory usage

4. **Backup Before Import:**
   - Always backup your database before large imports
   - Keep original import files
   - Test with small sample first

### Export Best Practices

1. **Use Filters:**
   ```python
   # Export only what you need
   {
       "filters": {
           "category": "Solar Modules",
           "updated_after": "2024-01-01"
       }
   }
   ```

2. **Select Specific Columns:**
   ```python
   # Export only required columns
   {
       "columns": ["name", "sku", "price", "stock_quantity"]
   }
   ```

3. **Choose Appropriate Format:**
   - **Excel**: Best for manual editing and analysis
   - **CSV**: Best for data exchange and automation
   - **XML**: Best for system integration
   - **JSON**: Best for API consumption

### Error Handling

1. **Check Import Results:**
   ```python
   result = import_from_excel(file)
   
   if not result.success:
       print(f"Import failed: {result.failed_count} errors")
       for error in result.errors:
           print(f"Row {error['row']}: {error['error']}")
   ```

2. **Retry Failed Rows:**
   - Extract failed rows from error report
   - Fix issues in source file
   - Re-import only failed rows

3. **Monitor Performance:**
   - Track import/export times
   - Monitor memory usage
   - Set appropriate timeouts

## Templates

### Download Import Templates

```python
# Get template information
GET /api/v1/product-import-export/template/excel

# Download template file
GET /api/v1/product-import-export/template/download/excel
```

### Template Structure

Templates include:
- Required columns with descriptions
- Sample data rows
- Import instructions
- Validation rules

## Bulk Operations

### Bulk Update

```python
# Update multiple products at once
POST /api/v1/product-import-export/bulk/update

{
    "product_ids": [1, 2, 3, 4, 5],
    "updates": {
        "category": "Premium Solar Modules",
        "price": 349.99
    }
}
```

### Bulk Delete

```python
# Delete multiple products at once
POST /api/v1/product-import-export/bulk/delete

{
    "product_ids": [10, 11, 12],
    "confirm": true
}
```

## Troubleshooting

### Common Issues

1. **"Missing required columns" Error:**
   - Check column names match exactly
   - Use column mapping if names differ
   - Ensure header row is present

2. **"Duplicate SKU" Error:**
   - SKUs must be unique
   - Check for duplicates in import file
   - Check against existing products

3. **"Invalid price format" Error:**
   - Price must be numeric
   - Use dot (.) as decimal separator
   - Remove currency symbols

4. **"File encoding error":**
   - Use UTF-8 encoding
   - Specify encoding parameter
   - Convert file encoding if needed

### Support

For additional help:
- Check API documentation: `/docs`
- Review error messages carefully
- Test with small sample files first
- Contact support with error details
