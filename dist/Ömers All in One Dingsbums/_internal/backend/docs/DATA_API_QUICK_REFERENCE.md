# Data API Quick Reference

Quick reference for Data API endpoints with dynamic keys and PDF generation.

**Task:** 231 - API Endpoints for Dynamic Keys and PDF  
**Requirements:** 14.4, 14.5, 14.10

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/data/pdf/{dynamic_key}` | Get PDF by dynamic key |
| POST | `/api/v1/data/generate-pdf` | Generate PDF for record |
| GET | `/api/v1/data/by-key/{key}` | Get data by dynamic key |
| POST | `/api/v1/data/bulk-pdf` | Bulk generate PDFs |
| GET | `/api/v1/data/keys/search` | Search dynamic keys |
| GET | `/api/v1/data/keys/statistics` | Get key statistics |
| GET | `/api/v1/data/pdf/statistics` | Get PDF statistics |
| DELETE | `/api/v1/data/pdf/{dynamic_key}` | Delete PDF |
| POST | `/api/v1/data/pdf/{dynamic_key}/regenerate` | Regenerate PDF |

## Quick Examples

### Get PDF
```bash
curl -X GET "http://localhost:8000/api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4" \
  --output report.pdf
```

### Generate PDF
```bash
curl -X POST "http://localhost:8000/api/v1/data/generate-pdf?record_id=123" \
  -H "Content-Type: application/json" \
  -d '{"title": "Report", "include_base64": true}'
```

### Get Data by Key
```bash
curl -X GET "http://localhost:8000/api/v1/data/by-key/SOL_20231116_143052_a1b2c3d4?include_pdf=true"
```

### Bulk Generate
```bash
curl -X POST "http://localhost:8000/api/v1/data/bulk-pdf" \
  -H "Content-Type: application/json" \
  -d '{"record_ids": [1,2,3], "batch_size": 100}'
```

### Search Keys
```bash
curl -X GET "http://localhost:8000/api/v1/data/keys/search?prefix=SOL&limit=50"
```

### Get Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/data/keys/statistics"
curl -X GET "http://localhost:8000/api/v1/data/pdf/statistics"
```

## Key Prefixes

| Prefix | Type |
|--------|------|
| SOL | Solar Calculation |
| PRJ | Project |
| CUS | Customer |
| HP | Heat Pump |
| PDF | PDF Document |
| PRD | Product |
| OFF | Offer |

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

## TypeScript Integration

```typescript
// Get PDF
const pdf = await axios.get(`/api/v1/data/pdf/${key}`, {
  responseType: 'blob'
});

// Generate PDF
const result = await axios.post(`/api/v1/data/generate-pdf?record_id=${id}`, {
  title: "Report",
  include_base64: true
});

// Get data
const data = await axios.get(`/api/v1/data/by-key/${key}`, {
  params: { include_pdf: true, formatted: true }
});

// Search
const keys = await axios.get('/api/v1/data/keys/search', {
  params: { prefix: 'SOL', limit: 100 }
});
```

## Common Patterns

### Download PDF
```typescript
async function downloadPDF(key: string, filename: string) {
  const response = await axios.get(`/api/v1/data/pdf/${key}`, {
    responseType: 'blob'
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
}
```

### Generate and Download
```typescript
async function generateAndDownload(recordId: number) {
  // Generate PDF
  const result = await axios.post(
    `/api/v1/data/generate-pdf?record_id=${recordId}`,
    { title: "Report", include_base64: false }
  );
  
  // Get the record to find its key
  const data = await axios.get(`/api/v1/data/by-key/${result.dynamic_key}`);
  
  // Download PDF
  await downloadPDF(data.dynamic_key, 'report.pdf');
}
```

### Bulk Process with Progress
```typescript
async function bulkGenerateWithProgress(recordIds: number[]) {
  const batchSize = 100;
  const result = await axios.post('/api/v1/data/bulk-pdf', {
    record_ids: recordIds,
    batch_size: batchSize
  });
  
  console.log(`Generated: ${result.generated}/${result.total_records}`);
  console.log(`Success rate: ${result.success_rate}%`);
  
  return result;
}
```

## See Also

- [Full API Documentation](DATA_API_ENDPOINTS.md)
- [Dynamic Key System](DYNAMIC_KEY_SYSTEM.md)
- [PDF Byte Generation](PDF_BYTE_GENERATION.md)
