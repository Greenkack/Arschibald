# PDF Archiving - Quick Reference

## Quick Start

```python
from services.pdf_archiving_service import PDFArchivingService

service = PDFArchivingService()

# Archive PDF
doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot.pdf",
    customer_id=1,
    total_price=16999.00
)
```

## Common Operations

### Archive PDF
```python
doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot_Mustermann.pdf",
    customer_id=1,
    project_id=10,
    company_name="Mustermann GmbH",
    products=[{"name": "PV Module", "quantity": 20}],
    total_price=16999.00
)
```

### Get PDF History
```python
# All PDFs for customer
history = service.get_pdf_history(customer_id=1)

# Filter by type
history = service.get_pdf_history(
    customer_id=1,
    pdf_type='offer_pdf'
)

# Filter by date
from datetime import datetime, timedelta
history = service.get_pdf_history(
    customer_id=1,
    start_date=datetime.now() - timedelta(days=30)
)
```

### Search PDFs
```python
results = service.search_pdfs(
    search_term='Angebot',
    pdf_type='offer_pdf',
    customer_id=1
)
```

### Export PDF
```python
# Get bytes
pdf_bytes = service.export_pdf(document_id=1)

# Save to file
pdf_bytes = service.export_pdf(
    document_id=1,
    output_path='/path/to/output.pdf'
)

# Export multiple
results = service.export_multiple_pdfs(
    document_ids=[1, 2, 3],
    output_dir='/path/to/output'
)
```

### Get Statistics
```python
stats = service.get_pdf_statistics()
# Returns: {total_pdfs, total_customers, by_type}

stats = service.get_pdf_statistics(customer_id=1)
```

## API Endpoints

### Archive PDF
```bash
POST /api/v1/pdf-archiving/archive
Content-Type: multipart/form-data

file: <PDF file>
customer_id: 1
project_id: 10
total_price: 16999.00
```

### Get History
```bash
GET /api/v1/pdf-archiving/history/1?pdf_type=offer_pdf
```

### Search
```bash
POST /api/v1/pdf-archiving/search
Content-Type: application/json

{
  "search_term": "Angebot",
  "pdf_type": "offer_pdf",
  "customer_id": 1
}
```

### Export
```bash
GET /api/v1/pdf-archiving/export/1
```

### Statistics
```bash
GET /api/v1/pdf-archiving/statistics?customer_id=1
```

## PDF Types

- `offer_pdf` - Offer/quote documents
- `invoice_pdf` - Invoice documents
- `contract_pdf` - Contract documents
- `report_pdf` - Report documents
- `other_pdf` - Other documents

## Metadata Fields

```python
{
    'creation_date': datetime,
    'company_id': int,
    'company_name': str,
    'products': List[Dict],
    'total_price': float,
    'pdf_type': str,
    'project_type': str,
    'version': int,
    'file_size': int,
    'checksum': str
}
```

## Versioning

- First PDF: v1
- Updated PDF: v2
- Another update: v3
- Automatic version numbering
- No overwriting of previous versions

## Error Handling

```python
try:
    doc_id = service.auto_save_to_crm(...)
    if doc_id:
        print(f"Success: {doc_id}")
    else:
        print("Failed to archive")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Always provide metadata**
   ```python
   doc_id = service.auto_save_to_crm(
       pdf_bytes=pdf_bytes,
       filename="Angebot.pdf",
       customer_id=1,
       company_name="Mustermann GmbH",  # ✓
       products=[...],                   # ✓
       total_price=16999.00             # ✓
   )
   ```

2. **Use descriptive filenames**
   ```python
   # Good
   filename = "Angebot_Mustermann_PV_2025-01-15.pdf"
   
   # Avoid
   filename = "document.pdf"
   ```

3. **Include offer data**
   ```python
   offer_data = {
       'customer_id': 1,
       'customer': {'name': 'Mustermann GmbH'},
       'products': [...],
       'total_cost': 16999.00
   }
   
   doc_id = service.auto_save_to_crm(
       pdf_bytes=pdf_bytes,
       filename="Angebot.pdf",
       customer_id=1,
       offer_data=offer_data  # ✓
   )
   ```

4. **Filter searches**
   ```python
   # Good: Specific filters
   results = service.search_pdfs(
       customer_id=1,
       pdf_type='offer_pdf',
       start_date=datetime(2025, 1, 1)
   )
   
   # Avoid: No filters (slow)
   results = service.search_pdfs()
   ```

## Common Issues

### PDF Not Archived
- Check customer_id exists
- Verify PDF bytes are valid
- Check database connection

### Wrong Version Number
- Check previous PDFs for customer
- Verify PDF type matches
- Check project_id if used

### Search Returns Nothing
- Verify search criteria
- Check date range
- Try broader search terms

## Testing

```bash
# Run tests
pytest tests/test_pdf_archiving_service.py -v

# Run demo
python demo_pdf_archiving.py
```

## Requirements

- Python 3.10+
- FastAPI
- Existing CRM database

## Related Docs

- [Full Guide](./PDF_ARCHIVING_GUIDE.md)
- [API Docs](./API_DOCUMENTATION.md)
- [CRM Integration](./CRM_INTEGRATION_GUIDE.md)
