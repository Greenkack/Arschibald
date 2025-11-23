# Multi-PDF Batch Generation - Quick Reference

## Quick Start

```python
from backend.services.batch_pdf_service import BatchPDFService, BatchPDFRequest

# Create request
request = BatchPDFRequest(
    company_ids=[1, 2, 3],
    analysis_data={"base_price": 16999.00},
    template_type="standard_pv",
    options={"price_increase_percentage": 7.0}
)

# Generate
result = await service.generate_batch(request)

# Download ZIP
zip_bytes = await service.download_zip(result.batch_id)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/batch-pdf/generate` | POST | Generate batch (sync) |
| `/batch-pdf/generate-async` | POST | Generate batch (async) |
| `/batch-pdf/progress/{batch_id}` | GET | Get progress |
| `/batch-pdf/download/zip/{batch_id}` | GET | Download ZIP |
| `/batch-pdf/download/single/{batch_id}/{company_id}` | GET | Download single PDF |
| `/batch-pdf/cleanup/{batch_id}` | DELETE | Cleanup batch |

## Request Format

```json
{
  "company_ids": [1, 2, 3, 4, 5],
  "analysis_data": {
    "roof_area": 50.0,
    "module_count": 30,
    "base_price": 16999.00,
    "products": {
      "pv_module": "Trina Solar 400W",
      "inverter": "Fronius Symo",
      "battery": "BYD Battery-Box"
    }
  },
  "template_type": "standard_pv",
  "options": {
    "price_increase_percentage": 7.0
  }
}
```

## Response Format

```json
{
  "batch_id": "batch_20240115_143022",
  "total_companies": 5,
  "successful": 5,
  "failed": 0,
  "results": [
    {
      "company_id": 1,
      "company_name": "Solar Solutions GmbH",
      "success": true,
      "pdf_path": "/output/...",
      "generation_time": 1.23,
      "file_size": 245678
    }
  ],
  "total_time": 3.45,
  "zip_path": "/output/...",
  "zip_size": 1234567
}
```

## Progress Tracking

```python
# Get progress
progress = service.get_progress(batch_id)

# Progress fields
progress.batch_id          # Batch identifier
progress.total             # Total companies
progress.completed         # Completed count
progress.current_company   # Current company name
progress.percentage        # Completion percentage
progress.status            # 'queued', 'processing', 'completed', 'failed'
```

## Product Rotation

```python
# Automatic rotation per offer
# Offer 1: Trina Solar, Fronius, BYD
# Offer 2: JA Solar, SMA, Tesla
# Offer 3: Longi, Huawei, Sonnen
# Offer 4: Canadian Solar, SolarEdge, LG Chem
```

## Price Increase

```python
# Formula: price = base_price × (1 + (percentage / 100) × index)

# Example with 7% increase:
# Offer 1: 16.999,00 € (base)
# Offer 2: 18.188,93 € (+7%)
# Offer 3: 19.462,15 € (+14.5%)
# Offer 4: 20.824,50 € (+22.5%)
```

## Configuration

```python
service = BatchPDFService(
    pdf_service=pdf_service,
    company_service=company_service,
    product_rotation_service=rotation_service,
    price_increase_service=price_service,
    max_workers=4  # Parallel workers
)
```

## Error Handling

```python
result = await service.generate_batch(request)

if result.failed > 0:
    for r in result.results:
        if not r.success:
            print(f"Failed: {r.company_name}")
            print(f"Error: {r.error_message}")
```

## Cleanup

```python
# Keep ZIP, delete PDFs
service.cleanup_batch(batch_id, keep_zip=True)

# Delete everything
service.cleanup_batch(batch_id, keep_zip=False)
```

## Performance Tips

1. **Parallel Workers**: Increase `max_workers` for faster generation
2. **Batch Size**: Optimal 5-10 companies, max 50
3. **Caching**: Cache company and product data
4. **Cleanup**: Remove old batches regularly

## Common Patterns

### Synchronous Generation

```python
result = await service.generate_batch(request)
# Wait for completion, get result immediately
```

### Asynchronous Generation

```python
# Start generation
batch_id = service._generate_batch_id()
service._init_progress(batch_id, len(company_ids))
asyncio.create_task(service.generate_batch(request))

# Poll progress
while True:
    progress = service.get_progress(batch_id)
    if progress.status == "completed":
        break
    await asyncio.sleep(1)
```

### Download All PDFs

```python
# Download ZIP with all PDFs
zip_bytes = await service.download_zip(batch_id)

# Save to file
with open("all_offers.zip", "wb") as f:
    f.write(zip_bytes)
```

### Download Single PDF

```python
# Download specific company PDF
pdf_bytes = await service.download_single_pdf(batch_id, company_id)

# Save to file
with open(f"offer_company_{company_id}.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## Frontend Integration

```typescript
// Generate batch
const response = await fetch('/api/v1/batch-pdf/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
});

const result = await response.json();

// Download ZIP
window.location.href = `/api/v1/batch-pdf/download/zip/${result.batch_id}`;
```

## Limits

- **Maximum Companies**: 50 per batch
- **Maximum Workers**: 8 (recommended)
- **Batch Retention**: 24 hours (configurable)
- **File Size**: No limit (depends on disk space)

## Status Codes

| Status | Description |
|--------|-------------|
| `queued` | Batch queued for processing |
| `processing` | PDFs being generated |
| `completed` | All PDFs generated successfully |
| `failed` | Batch generation failed |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow generation | Increase `max_workers` |
| High memory | Reduce `max_workers` or batch size |
| Failed PDFs | Check error messages in results |
| Missing ZIP | Verify batch completed successfully |
| Disk space | Clean up old batches |

## Examples

```bash
# Run demo
python backend/demo_batch_pdf.py

# Run tests
pytest backend/tests/test_batch_pdf_service.py -v
```

## Related Docs

- [Full Guide](BATCH_PDF_GUIDE.md)
- [Product Rotation](PRODUCT_ROTATION_GUIDE.md)
- [Price Increase](PRICE_INCREASE_GUIDE.md)
