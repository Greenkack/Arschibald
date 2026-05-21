# Import/Export System - Quick Reference

## Quick Start

### Import Data
```bash
POST /api/v1/import-export/import
{
  "file_content": "base64_encoded_content",
  "config": {
    "format": "csv",
    "mappings": [...],
    "validation_rules": [...]
  }
}
```

### Export Data
```bash
POST /api/v1/import-export/export
{
  "data_source": "projects",
  "config": {
    "format": "excel",
    "fields": ["id", "name", "customer_name"]
  }
}
```

## Supported Formats

| Format | Import | Export | Extension |
|--------|--------|--------|-----------|
| CSV    | ✅     | ✅     | .csv      |
| Excel  | ✅     | ✅     | .xlsx     |
| JSON   | ✅     | ✅     | .json     |
| XML    | ✅     | ✅     | .xml      |
| PDF    | ❌     | ✅     | .pdf      |

## Transformations

| Name      | Description           | Example                |
|-----------|-----------------------|------------------------|
| uppercase | Convert to uppercase  | 'hello' → 'HELLO'      |
| lowercase | Convert to lowercase  | 'HELLO' → 'hello'      |
| trim      | Remove whitespace     | '  text  ' → 'text'    |
| to_int    | Convert to integer    | '123' → 123            |
| to_float  | Convert to float      | '123.45' → 123.45      |
| to_bool   | Convert to boolean    | 'true' → True          |
| to_date   | Convert to date       | '2024-01-01' → date    |

## Validation Rules

| Type    | Description              | Parameters           |
|---------|--------------------------|----------------------|
| required| Field must have value    | -                    |
| type    | Field must be type       | type: str/int/float  |
| range   | Field must be in range   | min, max             |
| pattern | Field must match pattern | pattern: regex       |
| custom  | Custom validator         | validator: name      |

## Common Validators

| Name     | Description              |
|----------|--------------------------|
| required | Value must exist         |
| email    | Valid email format       |
| numeric  | Must be numeric          |
| positive | Must be positive number  |

## API Endpoints

| Endpoint                          | Method | Description              |
|-----------------------------------|--------|--------------------------|
| `/import-export/import`           | POST   | Import data from file    |
| `/import-export/export`           | POST   | Export data to file      |
| `/import-export/template`         | POST   | Create import template   |
| `/import-export/validate`         | POST   | Validate import file     |
| `/import-export/batch-import`     | POST   | Import multiple files    |
| `/import-export/data-sources`     | GET    | List data sources        |
| `/import-export/transformations`  | GET    | List transformations     |
| `/import-export/validators`       | GET    | List validators          |

## Configuration Options

### Import Config
```json
{
  "format": "csv|excel|json|xml",
  "mappings": [
    {
      "source_field": "Name",
      "target_field": "name",
      "transformation": "trim",
      "default_value": null
    }
  ],
  "validation_rules": [
    {
      "field": "name",
      "rule_type": "required",
      "parameters": {},
      "error_message": "Name is required"
    }
  ],
  "skip_errors": false,
  "batch_size": 100
}
```

### Export Config
```json
{
  "format": "csv|excel|json|xml|pdf",
  "fields": ["id", "name", "email"],
  "include_headers": true,
  "custom_headers": {
    "id": "ID",
    "name": "Name",
    "email": "Email Address"
  }
}
```

## Quick Examples

### Import CSV with Validation
```python
config = {
    "format": "csv",
    "mappings": [
        {"source_field": "Name", "target_field": "name", "transformation": "trim"}
    ],
    "validation_rules": [
        {"field": "name", "rule_type": "required", "error_message": "Name required"}
    ]
}
```

### Export to Excel with Custom Headers
```python
config = {
    "format": "excel",
    "fields": ["id", "name", "email"],
    "custom_headers": {
        "id": "Customer ID",
        "name": "Full Name",
        "email": "Email Address"
    }
}
```

### Batch Import Multiple Files
```python
files = [
    {"name": "file1.csv", "content": "base64..."},
    {"name": "file2.csv", "content": "base64..."}
]
config = {"format": "csv", "mappings": [...]}
```

## Error Handling

### Import Result
```json
{
  "success": true,
  "total_records": 100,
  "imported_records": 98,
  "failed_records": 2,
  "errors": [
    {"record_index": 5, "errors": ["Name required"]}
  ]
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid format, validation error)
- `401`: Unauthorized
- `500`: Server error

## Best Practices

✅ **DO:**
- Validate files before importing
- Use batch processing for large datasets
- Apply transformations to normalize data
- Enable skip_errors for bulk imports
- Use custom headers for exports

❌ **DON'T:**
- Import without validation
- Use very large batch sizes (>1000)
- Ignore error messages
- Skip data transformation
- Export sensitive data without filtering

## Performance Tips

1. **Batch Size**: 100-500 for complex data, 500-1000 for simple data
2. **Skip Errors**: Enable for faster bulk imports
3. **Parallel Processing**: Use batch import for multiple files
4. **Field Selection**: Export only needed fields
5. **Caching**: Transformations and validations are cached

## Troubleshooting

| Issue                    | Solution                              |
|--------------------------|---------------------------------------|
| Invalid format error     | Check file format and encoding        |
| Validation errors        | Review validation rules               |
| Transformation errors    | Verify data type compatibility        |
| Performance issues       | Reduce batch size                     |
| Memory errors            | Process in smaller batches            |

## Support Resources

- Full Guide: `/docs/IMPORT_EXPORT_GUIDE.md`
- API Docs: `/docs` (Swagger UI)
- Examples: `/examples/import_export_examples.py`
