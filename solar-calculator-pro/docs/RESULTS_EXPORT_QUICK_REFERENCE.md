# Results Export - Quick Reference

## Quick Start

```bash
# Create PDF export
curl -X POST http://localhost:8000/api/v1/exports/ \
  -H "Content-Type: application/json" \
  -d '{"result_id": 123, "format": "pdf", "options": {}}'

# Download export
curl -O http://localhost:8000/api/v1/exports/{export_id}/download
```

## Supported Formats

| Format | Extension | Use Case | German Formatting |
|--------|-----------|----------|-------------------|
| PDF | .pdf | Reports, presentations | ✅ |
| Excel | .xlsx | Data analysis | ✅ |
| CSV | .csv | Simple data export | ✅ |
| JSON | .json | API integration | ✅ |
| XML | .xml | Legacy systems | ✅ |

## Common Options

### PDF
```json
{
  "include_charts": true,
  "include_tables": true,
  "page_size": "A4",
  "orientation": "portrait"
}
```

### Excel
```json
{
  "include_charts": true,
  "freeze_panes": true,
  "auto_filter": true
}
```

### CSV
```json
{
  "delimiter": ",",
  "decimal_separator": ",",
  "thousands_separator": "."
}
```

### JSON
```json
{
  "pretty_print": true,
  "include_metadata": true,
  "date_format": "iso"
}
```

### XML
```json
{
  "root_element": "result",
  "pretty_print": true
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/exports/` | Create export |
| POST | `/api/v1/exports/batch` | Batch export |
| GET | `/api/v1/exports/{id}/download` | Download file |
| GET | `/api/v1/exports/history` | Export history |
| DELETE | `/api/v1/exports/{id}` | Delete export |
| GET | `/api/v1/exports/formats` | List formats |

## German Number Formatting

| Input | Output |
|-------|--------|
| 16999.00 | 16.999,00 € |
| 12500 | 12.500 kWh |
| 0.085 | 8,50% |
| 8.5 | 8,50 years |

## Response Structure

```json
{
  "export_id": "uuid",
  "format": "pdf",
  "file_name": "result_123_20240115.pdf",
  "file_size": 245678,
  "download_url": "/api/v1/exports/{id}/download",
  "expires_at": "2024-01-16T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 404 | Result or export not found |
| 400 | Invalid format or options |
| 500 | Export generation failed |

## File Retention

- Exports expire after **24 hours**
- Automatic cleanup of expired files
- Manual deletion available via API

## Best Practices

1. ✅ Use PDF for reports
2. ✅ Use Excel for data analysis
3. ✅ Use CSV for simple exports
4. ✅ Enable German formatting for all formats
5. ✅ Set appropriate page size for PDF
6. ✅ Use batch export for multiple results
7. ✅ Handle expired exports gracefully

## TypeScript Example

```typescript
const response = await fetch('/api/v1/exports/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    result_id: 123,
    format: 'pdf',
    options: { include_charts: true }
  })
});

const { download_url } = await response.json();
window.open(download_url, '_blank');
```

## Python Example

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/exports/',
    json={'result_id': 123, 'format': 'excel', 'options': {}}
)

export_id = response.json()['export_id']
file = requests.get(f'http://localhost:8000/api/v1/exports/{export_id}/download')

with open('result.xlsx', 'wb') as f:
    f.write(file.content)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 on download | Check if export expired (24h limit) |
| Large file size | Disable charts, use CSV |
| Wrong formatting | Verify German options set |
| Slow export | Use batch export, reduce data |

## Support

- API Docs: `/api/v1/docs`
- Full Guide: `RESULTS_EXPORT_GUIDE.md`
