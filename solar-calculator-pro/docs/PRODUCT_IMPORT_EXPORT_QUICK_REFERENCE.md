# Product Import/Export Quick Reference

Quick reference for product data import/export operations.

## Import Endpoints

### Excel Import
```http
POST /api/v1/product-import-export/import/excel
Content-Type: multipart/form-data

file: products.xlsx
mapping: {...}
validate_only: false
```

### CSV Import
```http
POST /api/v1/product-import-export/import/csv?delimiter=,&encoding=utf-8
Content-Type: multipart/form-data

file: products.csv
```

### XML Import
```http
POST /api/v1/product-import-export/import/xml
Content-Type: multipart/form-data

file: products.xml
```

### API Import
```http
POST /api/v1/product-import-export/import/api
Content-Type: application/json

{
  "api_url": "https://api.supplier.com/products",
  "api_key": "your-key",
  "params": {"category": "solar"}
}
```

## Export Endpoints

### Excel Export
```http
POST /api/v1/product-import-export/export/excel
Content-Type: application/json

{
  "format": "excel",
  "filters": {"category": "Solar Modules"},
  "columns": ["name", "sku", "price"],
  "include_metadata": true
}
```

### CSV Export
```http
POST /api/v1/product-import-export/export/csv
Content-Type: application/json

{
  "format": "csv",
  "filters": {"manufacturer": "SolarTech"}
}
```

### XML Export
```http
POST /api/v1/product-import-export/export/xml
Content-Type: application/json

{
  "format": "xml",
  "columns": ["name", "sku", "price"]
}
```

### JSON Export
```http
POST /api/v1/product-import-export/export/json?pretty=true
Content-Type: application/json

{
  "format": "json"
}
```

## Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Product name |
| sku | string | Yes | Stock Keeping Unit (unique) |
| category | string | No | Product category |
| manufacturer | string | No | Manufacturer name |
| price | number | No | Product price (≥ 0) |
| description | string | No | Product description |

## Column Mapping

```json
{
  "mapping": {
    "name_column": "Product Name",
    "sku_column": "Article Number",
    "category_column": "Category",
    "manufacturer_column": "Brand",
    "price_column": "Unit Price",
    "description_column": "Description"
  }
}
```

## Validation

### Validate Only
```http
POST /api/v1/product-import-export/import/excel?validate_only=true
```

### Validation Endpoint
```http
POST /api/v1/product-import-export/validate/excel
Content-Type: multipart/form-data

file: products.xlsx
```

## Templates

### Get Template Info
```http
GET /api/v1/product-import-export/template/excel
```

### Download Template
```http
GET /api/v1/product-import-export/template/download/excel
GET /api/v1/product-import-export/template/download/csv
GET /api/v1/product-import-export/template/download/json
```

## Bulk Operations

### Bulk Update
```http
POST /api/v1/product-import-export/bulk/update
Content-Type: application/json

{
  "product_ids": [1, 2, 3],
  "updates": {
    "category": "Premium",
    "price": 399.99
  }
}
```

### Bulk Delete
```http
POST /api/v1/product-import-export/bulk/delete
Content-Type: application/json

{
  "product_ids": [10, 11, 12],
  "confirm": true
}
```

## Response Format

### Success Response
```json
{
  "success": true,
  "total_rows": 100,
  "imported_count": 98,
  "failed_count": 2,
  "errors": [
    {"row": 5, "error": "Duplicate SKU"},
    {"row": 23, "error": "Invalid price"}
  ]
}
```

### Error Response
```json
{
  "detail": "Import failed: Invalid file format"
}
```

## File Formats

### Excel (.xlsx, .xls)
- Multiple sheets supported
- Automatic type detection
- Formatted output

### CSV (.csv)
- Customizable delimiter
- UTF-8 encoding recommended
- Header row required

### XML (.xml)
- Customizable structure
- Nested elements supported
- UTF-8 encoding

### JSON (.json)
- Array or object format
- Pretty printing option
- UTF-8 encoding

## Common Filters

```json
{
  "filters": {
    "category": "Solar Modules",
    "manufacturer": "SolarTech",
    "min_price": 100,
    "max_price": 1000,
    "in_stock": true,
    "updated_after": "2024-01-01"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request (invalid format, validation error) |
| 404 | Not Found (product not found) |
| 422 | Unprocessable Entity (validation failed) |
| 500 | Internal Server Error |

## Best Practices

1. **Always validate first** with `validate_only=true`
2. **Use column mapping** for custom column names
3. **Filter exports** to reduce file size
4. **Backup before import** large datasets
5. **Test with samples** before full import
6. **Monitor results** and handle errors
7. **Use templates** for consistent format

## Quick Examples

### Python
```python
import requests

# Import from Excel
files = {'file': open('products.xlsx', 'rb')}
response = requests.post(
    'http://localhost:8000/api/v1/product-import-export/import/excel',
    files=files
)

# Export to CSV
response = requests.post(
    'http://localhost:8000/api/v1/product-import-export/export/csv',
    json={'format': 'csv', 'filters': {'category': 'Solar Modules'}}
)
```

### cURL
```bash
# Import from CSV
curl -X POST "http://localhost:8000/api/v1/product-import-export/import/csv" \
  -F "file=@products.csv"

# Export to Excel
curl -X POST "http://localhost:8000/api/v1/product-import-export/export/excel" \
  -H "Content-Type: application/json" \
  -d '{"format":"excel","filters":{"category":"Solar Modules"}}' \
  --output products.xlsx
```

### JavaScript
```javascript
// Import from Excel
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/v1/product-import-export/import/excel', {
  method: 'POST',
  body: formData
});

// Export to JSON
const response = await fetch('/api/v1/product-import-export/export/json', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({format: 'json'})
});
```

## Support

- 📚 Full Documentation: `docs/PRODUCT_IMPORT_EXPORT_GUIDE.md`
- 🔗 API Docs: `/docs`
- 💻 Demo: `backend/demo_product_import_export.py`
