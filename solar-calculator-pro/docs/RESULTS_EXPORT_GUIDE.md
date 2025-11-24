# Results Export System - Complete Guide

## Overview

The Results Export System provides comprehensive functionality to export calculation results in multiple formats: PDF, Excel, CSV, JSON, XML, and via API. All exports support German number formatting (16.999,00 €) and can be customized with various options.

## Supported Export Formats

### 1. PDF Export

Professional PDF reports with charts, tables, and formatted data.

**Features:**
- Multiple page sizes (A4, Letter, Legal)
- Portrait or landscape orientation
- Include/exclude charts, tables, and summary
- Custom templates support
- German number formatting

**Example Request:**
```json
{
  "result_id": 123,
  "format": "pdf",
  "options": {
    "include_charts": true,
    "include_tables": true,
    "include_summary": true,
    "page_size": "A4",
    "orientation": "portrait",
    "template": "professional"
  }
}
```

### 2. Excel Export

Multi-sheet Excel workbooks with charts and formatted data.

**Features:**
- Multiple sheets for different data sections
- Embedded charts
- Auto-filter and freeze panes
- Custom sheet names
- Excel formulas (optional)
- German number formatting

**Example Request:**
```json
{
  "result_id": 123,
  "format": "excel",
  "options": {
    "include_charts": true,
    "include_formulas": false,
    "sheet_names": ["Summary", "Monthly Data", "Financial Analysis"],
    "freeze_panes": true,
    "auto_filter": true
  }
}
```

### 3. CSV Export

Comma-separated values with German number formatting.

**Features:**
- Custom delimiter
- German decimal separator (,) and thousands separator (.)
- Multiple encoding options
- Header row control

**Example Request:**
```json
{
  "result_id": 123,
  "format": "csv",
  "options": {
    "delimiter": ",",
    "encoding": "utf-8",
    "include_headers": true,
    "decimal_separator": ",",
    "thousands_separator": "."
  }
}
```

**Example Output:**
```csv
Metric,Value
System Size,10,50 kWp
Annual Production,12.500 kWh
Total Cost,16.999,00 €
Payback Period,8,50 years
```

### 4. JSON Export

Structured JSON data export.

**Features:**
- Pretty printing
- Metadata inclusion
- Multiple date formats (ISO, Unix timestamp, custom)
- Full data structure preservation

**Example Request:**
```json
{
  "result_id": 123,
  "format": "json",
  "options": {
    "pretty_print": true,
    "include_metadata": true,
    "date_format": "iso"
  }
}
```

**Example Output:**
```json
{
  "id": 123,
  "title": "Solar Calculation Result #123",
  "summary": {
    "System Size": "10.5 kWp",
    "Annual Production": "12,500 kWh",
    "Total Cost": "16.999,00 €"
  },
  "_metadata": {
    "exported_at": "2024-01-15T10:30:00Z",
    "format": "json",
    "version": "1.0"
  }
}
```

### 5. XML Export

XML-formatted data export.

**Features:**
- Custom root element
- Pretty printing
- Optional XML schema
- Hierarchical data structure

**Example Request:**
```json
{
  "result_id": 123,
  "format": "xml",
  "options": {
    "root_element": "calculation_result",
    "include_schema": false,
    "pretty_print": true
  }
}
```

**Example Output:**
```xml
<?xml version="1.0" ?>
<calculation_result exported_at="2024-01-15T10:30:00Z" format="xml">
  <id>123</id>
  <title>Solar Calculation Result #123</title>
  <summary>
    <System_Size>10.5 kWp</System_Size>
    <Annual_Production>12,500 kWh</Annual_Production>
    <Total_Cost>16.999,00 €</Total_Cost>
  </summary>
</calculation_result>
```

### 6. API Export

Direct API access to result data.

**Features:**
- Webhook support for async exports
- API key authentication
- JSON or XML response format
- Raw data inclusion option

**Example Request:**
```json
{
  "result_id": 123,
  "format": "json",
  "options": {
    "webhook_url": "https://example.com/webhook",
    "api_key": "your-api-key",
    "format": "json",
    "include_raw_data": false
  }
}
```

## API Endpoints

### Create Export

```http
POST /api/v1/exports/
Content-Type: application/json

{
  "result_id": 123,
  "format": "pdf",
  "options": {}
}
```

**Response:**
```json
{
  "export_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "pdf",
  "file_name": "result_123_20240115_103000.pdf",
  "file_size": 245678,
  "download_url": "/api/v1/exports/550e8400-e29b-41d4-a716-446655440000/download",
  "expires_at": "2024-01-16T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Batch Export

```http
POST /api/v1/exports/batch
Content-Type: application/json

{
  "result_ids": [123, 124, 125],
  "format": "excel",
  "options": {},
  "combine_files": false
}
```

### Download Export

```http
GET /api/v1/exports/{export_id}/download
```

Returns the file as a download.

### Get Export History

```http
GET /api/v1/exports/history?result_id=123&limit=50
```

### Delete Export

```http
DELETE /api/v1/exports/{export_id}
```

### Get Supported Formats

```http
GET /api/v1/exports/formats
```

Returns list of all supported formats and their options.

## German Number Formatting

All numeric values are automatically formatted according to German standards:

- **Decimal separator:** Comma (,)
- **Thousands separator:** Dot (.)
- **Currency:** Euro symbol (€) after the amount
- **Decimal places:** Always 2 for currency and percentages

**Examples:**
- `16999.00` → `16.999,00 €`
- `12500` → `12.500 kWh`
- `0.085` → `8,50%`
- `8.5` → `8,50 years`

## Usage Examples

### Python Client

```python
import requests

# Create export
response = requests.post(
    'http://localhost:8000/api/v1/exports/',
    json={
        'result_id': 123,
        'format': 'pdf',
        'options': {
            'include_charts': True,
            'page_size': 'A4'
        }
    }
)

export_data = response.json()
export_id = export_data['export_id']

# Download file
download_response = requests.get(
    f'http://localhost:8000/api/v1/exports/{export_id}/download'
)

with open('result.pdf', 'wb') as f:
    f.write(download_response.content)
```

### JavaScript/TypeScript Client

```typescript
// Create export
const response = await fetch('/api/v1/exports/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    result_id: 123,
    format: 'excel',
    options: {
      include_charts: true,
      freeze_panes: true
    }
  })
});

const exportData = await response.json();

// Download file
const downloadUrl = exportData.download_url;
window.open(downloadUrl, '_blank');
```

### cURL

```bash
# Create export
curl -X POST http://localhost:8000/api/v1/exports/ \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": 123,
    "format": "csv",
    "options": {
      "decimal_separator": ",",
      "thousands_separator": "."
    }
  }'

# Download file
curl -O http://localhost:8000/api/v1/exports/{export_id}/download
```

## Best Practices

### 1. Choose the Right Format

- **PDF:** For professional reports and presentations
- **Excel:** For data analysis and manipulation
- **CSV:** For simple data import/export
- **JSON:** For API integration and data exchange
- **XML:** For legacy system integration

### 2. Optimize Export Options

- Disable charts in CSV exports (not supported)
- Use pretty printing for human-readable JSON/XML
- Enable auto-filter in Excel for large datasets
- Use appropriate page size for PDF based on content

### 3. Handle Large Exports

- Use batch export for multiple results
- Consider pagination for very large datasets
- Monitor file sizes and adjust options accordingly

### 4. Security Considerations

- Exports expire after 24 hours
- Use HTTPS for all API calls
- Implement proper authentication
- Validate user permissions before export

### 5. Error Handling

```typescript
try {
  const response = await createExport(request);
  if (response.ok) {
    const exportData = await response.json();
    // Handle success
  } else {
    // Handle HTTP errors
    console.error('Export failed:', response.status);
  }
} catch (error) {
  // Handle network errors
  console.error('Network error:', error);
}
```

## Troubleshooting

### Export Not Found

**Problem:** 404 error when downloading export

**Solutions:**
- Check if export has expired (24 hour limit)
- Verify export_id is correct
- Ensure export was created successfully

### Large File Sizes

**Problem:** Export files are too large

**Solutions:**
- Disable charts in PDF/Excel
- Reduce data range
- Use CSV instead of Excel
- Compress files before download

### Formatting Issues

**Problem:** Numbers not formatted correctly

**Solutions:**
- Verify German formatting options are set
- Check decimal and thousands separators
- Ensure locale is set to 'de-DE'

### Performance Issues

**Problem:** Exports take too long

**Solutions:**
- Use batch export for multiple results
- Reduce included data (disable charts/tables)
- Implement caching for frequently exported results
- Use background tasks for large exports

## Advanced Features

### Custom Templates

Create custom PDF templates:

```python
# Register custom template
export_service.register_template(
    name='custom_template',
    template_path='/path/to/template.pdf',
    options={'header': True, 'footer': True}
)

# Use custom template
request = ExportRequest(
    result_id=123,
    format='pdf',
    options={'template': 'custom_template'}
)
```

### Webhooks for Async Exports

```python
# Configure webhook
request = ExportRequest(
    result_id=123,
    format='pdf',
    options={
        'webhook_url': 'https://example.com/webhook',
        'api_key': 'your-api-key'
    }
)

# Webhook will receive:
# POST https://example.com/webhook
# {
#   "export_id": "...",
#   "status": "completed",
#   "download_url": "..."
# }
```

### Scheduled Exports

```python
# Schedule daily export
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=export_daily_results,
    trigger='cron',
    hour=2,
    minute=0
)
scheduler.start()
```

## Support

For issues or questions:
- Check the API documentation: `/api/v1/docs`
- Review error logs
- Contact support team

## Version History

- **v1.0.0** (2024-01-15): Initial release
  - PDF, Excel, CSV, JSON, XML export
  - German number formatting
  - Batch export support
  - 24-hour file retention
