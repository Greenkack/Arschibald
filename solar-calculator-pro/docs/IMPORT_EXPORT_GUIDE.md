# Import/Export System Guide

## Overview

The Import/Export System provides comprehensive data import and export functionality with support for multiple formats, data transformation, validation, and batch processing.

## Features

### Supported Formats

**Import Formats:**
- CSV (Comma-Separated Values)
- Excel (XLSX)
- JSON (JavaScript Object Notation)
- XML (Extensible Markup Language)

**Export Formats:**
- CSV
- Excel (XLSX)
- JSON
- XML
- PDF (for reports)

### Core Capabilities

1. **Data Mapping**: Map source fields to target fields with custom transformations
2. **Validation**: Apply validation rules to ensure data quality
3. **Transformation**: Transform data during import (uppercase, lowercase, type conversion, etc.)
4. **Batch Processing**: Process large datasets in configurable batches
5. **Error Handling**: Skip errors or fail fast with detailed error reporting
6. **Template Generation**: Create import templates with predefined fields
7. **File Validation**: Validate files before importing

## API Endpoints

### Import Data

```http
POST /api/v1/import-export/import
```

Import data from a file with mapping and validation.

**Request Body:**
```json
{
  "file_content": "base64_encoded_file_content",
  "config": {
    "format": "csv",
    "mappings": [
      {
        "source_field": "Name",
        "target_field": "customer_name",
        "transformation": "trim"
      }
    ],
    "validation_rules": [
      {
        "field": "customer_name",
        "rule_type": "required",
        "parameters": {},
        "error_message": "Customer name is required"
      }
    ],
    "skip_errors": false,
    "batch_size": 100
  }
}
```

**Response:**
```json
{
  "success": true,
  "total_records": 100,
  "imported_records": 98,
  "failed_records": 2,
  "errors": [
    {
      "record_index": 5,
      "errors": ["Customer name is required"]
    }
  ],
  "warnings": []
}
```

### Export Data

```http
POST /api/v1/import-export/export
```

Export data to a file with field selection and custom headers.

**Request Body:**
```json
{
  "data_source": "projects",
  "filters": {
    "status": "active"
  },
  "config": {
    "format": "excel",
    "fields": ["id", "name", "customer_name", "system_size"],
    "include_headers": true,
    "custom_headers": {
      "id": "Project ID",
      "name": "Project Name",
      "customer_name": "Customer",
      "system_size": "System Size (kWp)"
    }
  }
}
```

**Response:**
```json
{
  "file_content": "base64_encoded_file_content",
  "filename": "export_projects.xlsx",
  "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

### Create Import Template

```http
POST /api/v1/import-export/template
```

Generate an import template with specified fields.

**Request Body:**
```json
{
  "fields": ["customer_name", "email", "phone", "address"],
  "format": "csv"
}
```

**Response:**
```json
{
  "file_content": "base64_encoded_template",
  "filename": "import_template.csv",
  "content_type": "text/csv"
}
```

### Validate Import File

```http
POST /api/v1/import-export/validate
```

Validate an import file without actually importing the data.

**Request Body:**
```json
{
  "file_content": "base64_encoded_file_content",
  "config": {
    "format": "csv",
    "mappings": [...],
    "validation_rules": [...]
  }
}
```

**Response:**
```json
{
  "valid": true,
  "record_count": 100,
  "fields": ["Name", "Email", "Phone"],
  "error": null
}
```

### Batch Import

```http
POST /api/v1/import-export/batch-import
```

Import multiple files in a single request.

**Request Body:**
```json
{
  "files": [
    {
      "name": "file1.csv",
      "content": "base64_encoded_content"
    },
    {
      "name": "file2.csv",
      "content": "base64_encoded_content"
    }
  ],
  "config": {
    "format": "csv",
    "mappings": [...],
    "validation_rules": [...]
  }
}
```

**Response:**
```json
{
  "total_files": 2,
  "successful_files": 2,
  "failed_files": 0,
  "results": [
    {
      "success": true,
      "total_records": 50,
      "imported_records": 50,
      "failed_records": 0,
      "errors": []
    },
    {
      "success": true,
      "total_records": 75,
      "imported_records": 75,
      "failed_records": 0,
      "errors": []
    }
  ]
}
```

### Get Data Sources

```http
GET /api/v1/import-export/data-sources
```

Get list of available data sources for export.

**Response:**
```json
[
  {
    "name": "projects",
    "description": "Solar calculator projects",
    "available_fields": ["id", "name", "customer_name", "system_size"],
    "record_count": 150
  }
]
```

### Get Transformations

```http
GET /api/v1/import-export/transformations
```

Get list of available transformation functions.

**Response:**
```json
[
  {
    "name": "uppercase",
    "description": "Convert text to uppercase",
    "example": "'hello' -> 'HELLO'"
  }
]
```

### Get Validators

```http
GET /api/v1/import-export/validators
```

Get list of available validator functions.

**Response:**
```json
[
  {
    "name": "required",
    "description": "Field must have a value",
    "parameters": []
  }
]
```

## Data Mapping

### Field Mapping

Map source fields to target fields:

```json
{
  "source_field": "Customer Name",
  "target_field": "customer_name",
  "transformation": "trim",
  "default_value": "Unknown"
}
```

### Available Transformations

- **uppercase**: Convert to uppercase
- **lowercase**: Convert to lowercase
- **trim**: Remove whitespace
- **to_int**: Convert to integer
- **to_float**: Convert to float
- **to_bool**: Convert to boolean
- **to_date**: Convert to date

### Custom Transformations

Register custom transformation functions:

```python
service = ImportExportService()
service.register_transformation(
    'custom_transform',
    lambda x: x.replace('-', '_')
)
```

## Validation Rules

### Rule Types

1. **required**: Field must have a value
2. **type**: Field must be of specific type
3. **range**: Field must be within range
4. **pattern**: Field must match regex pattern
5. **custom**: Custom validator function

### Examples

**Required Field:**
```json
{
  "field": "email",
  "rule_type": "required",
  "parameters": {},
  "error_message": "Email is required"
}
```

**Type Validation:**
```json
{
  "field": "age",
  "rule_type": "type",
  "parameters": {"type": "int"},
  "error_message": "Age must be an integer"
}
```

**Range Validation:**
```json
{
  "field": "price",
  "rule_type": "range",
  "parameters": {"min": 0, "max": 100000},
  "error_message": "Price must be between 0 and 100000"
}
```

**Pattern Validation:**
```json
{
  "field": "phone",
  "rule_type": "pattern",
  "parameters": {"pattern": "^\\+?[0-9]{10,15}$"},
  "error_message": "Invalid phone number format"
}
```

**Custom Validation:**
```json
{
  "field": "email",
  "rule_type": "custom",
  "parameters": {"validator": "email"},
  "error_message": "Invalid email address"
}
```

## Usage Examples

### Example 1: Import Customers from CSV

```python
import base64
import requests

# Read CSV file
with open('customers.csv', 'rb') as f:
    file_content = base64.b64encode(f.read()).decode('utf-8')

# Configure import
config = {
    "format": "csv",
    "mappings": [
        {
            "source_field": "Name",
            "target_field": "name",
            "transformation": "trim"
        },
        {
            "source_field": "Email",
            "target_field": "email",
            "transformation": "lowercase"
        }
    ],
    "validation_rules": [
        {
            "field": "name",
            "rule_type": "required",
            "parameters": {},
            "error_message": "Name is required"
        },
        {
            "field": "email",
            "rule_type": "custom",
            "parameters": {"validator": "email"},
            "error_message": "Invalid email"
        }
    ],
    "skip_errors": True,
    "batch_size": 100
}

# Import data
response = requests.post(
    'http://localhost:8000/api/v1/import-export/import',
    json={
        "file_content": file_content,
        "config": config
    }
)

result = response.json()
print(f"Imported {result['imported_records']} of {result['total_records']} records")
```

### Example 2: Export Projects to Excel

```python
import base64
import requests

# Configure export
config = {
    "format": "excel",
    "fields": ["id", "name", "customer_name", "system_size", "created_at"],
    "include_headers": True,
    "custom_headers": {
        "id": "Project ID",
        "name": "Project Name",
        "customer_name": "Customer",
        "system_size": "System Size (kWp)",
        "created_at": "Created Date"
    }
}

# Export data
response = requests.post(
    'http://localhost:8000/api/v1/import-export/export',
    json={
        "data_source": "projects",
        "filters": {"status": "active"},
        "config": config
    }
)

result = response.json()

# Save file
file_data = base64.b64decode(result['file_content'])
with open(result['filename'], 'wb') as f:
    f.write(file_data)
```

### Example 3: Batch Import Multiple Files

```python
import base64
import requests
import glob

# Read all CSV files
files = []
for filepath in glob.glob('data/*.csv'):
    with open(filepath, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        files.append({
            "name": filepath,
            "content": content
        })

# Configure import
config = {
    "format": "csv",
    "mappings": [...],
    "validation_rules": [...],
    "skip_errors": True
}

# Batch import
response = requests.post(
    'http://localhost:8000/api/v1/import-export/batch-import',
    json={
        "files": files,
        "config": config
    }
)

result = response.json()
print(f"Processed {result['total_files']} files")
print(f"Successful: {result['successful_files']}")
print(f"Failed: {result['failed_files']}")
```

## Best Practices

1. **Always validate files before importing** using the `/validate` endpoint
2. **Use batch processing** for large datasets to avoid memory issues
3. **Enable skip_errors** for bulk imports to continue processing despite errors
4. **Apply transformations** to normalize data during import
5. **Use custom headers** in exports for user-friendly column names
6. **Create templates** to guide users on required fields and format
7. **Monitor import results** and handle errors appropriately
8. **Use appropriate batch sizes** (100-1000 records) based on data complexity

## Error Handling

### Common Errors

1. **Invalid Format**: Unsupported file format
2. **Missing Fields**: Required fields not found in source data
3. **Validation Errors**: Data doesn't meet validation rules
4. **Transformation Errors**: Transformation function failed
5. **Encoding Errors**: File encoding issues

### Error Response Format

```json
{
  "success": false,
  "total_records": 100,
  "imported_records": 85,
  "failed_records": 15,
  "errors": [
    {
      "record_index": 5,
      "errors": ["Email is required", "Invalid phone format"]
    },
    {
      "record_index": 12,
      "error": "Transformation 'to_int' failed: invalid literal"
    }
  ]
}
```

## Performance Considerations

1. **Batch Size**: Adjust based on record complexity (default: 100)
2. **Memory Usage**: Large files are processed in chunks
3. **Parallel Processing**: Batch imports can process files in parallel
4. **Caching**: Transformation and validation results are cached
5. **Streaming**: Large exports use streaming to avoid memory issues

## Security

1. **File Size Limits**: Maximum file size enforced
2. **Format Validation**: Only allowed formats accepted
3. **Input Sanitization**: All data sanitized before processing
4. **Access Control**: Import/export operations require authentication
5. **Audit Logging**: All operations logged for compliance

## Troubleshooting

### Import Fails with "Invalid Format"

- Verify file format matches config.format
- Check file encoding (UTF-8 recommended)
- Ensure file is not corrupted

### Validation Errors

- Review validation rules
- Check source data format
- Use `/validate` endpoint to test before importing

### Transformation Errors

- Verify transformation function exists
- Check data type compatibility
- Test transformation with sample data

### Performance Issues

- Reduce batch size
- Enable skip_errors for faster processing
- Use batch import for multiple files

## Support

For additional help:
- Check API documentation: `/docs`
- Review examples in `/examples`
- Contact support team
