# PDF Archiving & CRM Integration Guide

## Overview

The PDF Archiving Service provides automatic PDF archiving to CRM customer records with comprehensive metadata management, versioning, search capabilities, and export functionality.

## Features

### 1. Auto-Save to CRM
- Automatically save PDFs to customer documents
- No manual upload required
- Seamless integration with CRM system

### 2. PDF Versioning
- Automatic version numbering (v1, v2, v3, ...)
- Version history tracking
- Prevents overwriting previous versions

### 3. PDF History per Customer
- Complete PDF history for each customer
- Filter by project, type, date range
- Formatted display with metadata

### 4. PDF Metadata
- **Creation Date**: When the PDF was created
- **Company**: Company/customer information
- **Products**: List of products in the offer
- **Price**: Total price of the offer
- **PDF Type**: offer_pdf, invoice_pdf, contract_pdf, report_pdf
- **Project Type**: pv, heatpump, combined
- **Version**: Version number
- **File Size**: Size in bytes
- **Checksum**: SHA-256 checksum for integrity

### 5. PDF Search
- Search by customer, filename, type
- Filter by date range, price range
- Full-text search in metadata
- Company name search

### 6. PDF Export
- Export single PDF
- Export multiple PDFs
- Save to file system
- Return as bytes for download

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# The service uses existing CRM database
# No additional setup required
```

## Usage

### Basic Usage

```python
from services.pdf_archiving_service import PDFArchivingService

# Initialize service
service = PDFArchivingService()

# Archive a PDF
doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot_Mustermann.pdf",
    customer_id=1,
    project_id=10,
    company_name="Mustermann GmbH",
    products=[
        {"name": "PV Module", "quantity": 20},
        {"name": "Wechselrichter", "quantity": 1}
    ],
    total_price=16999.00
)

print(f"PDF archived with ID: {doc_id}")
```

### With Offer Data

```python
# Archive PDF with complete offer data
offer_data = {
    'customer_id': 1,
    'customer': {'name': 'Mustermann GmbH'},
    'project_type': 'pv',
    'products': [...],
    'total_cost': 16999.00,
    'offer_id': 'OFF-2025-001'
}

doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot.pdf",
    customer_id=1,
    offer_data=offer_data
)
```

### Get PDF History

```python
# Get all PDFs for a customer
history = service.get_pdf_history(customer_id=1)

# Filter by type
history = service.get_pdf_history(
    customer_id=1,
    pdf_type='offer_pdf'
)

# Filter by date range
from datetime import datetime, timedelta

history = service.get_pdf_history(
    customer_id=1,
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)
```

### Search PDFs

```python
# Search by term
results = service.search_pdfs(
    search_term='Angebot',
    pdf_type='offer_pdf'
)

# Search with filters
results = service.search_pdfs(
    customer_id=1,
    search_term='PV',
    min_price=10000.00,
    max_price=20000.00,
    start_date=datetime(2025, 1, 1),
    company_name='Mustermann'
)
```

### Export PDFs

```python
# Export single PDF
pdf_bytes = service.export_pdf(document_id=1)

# Export to file
pdf_bytes = service.export_pdf(
    document_id=1,
    output_path='/path/to/output.pdf'
)

# Export multiple PDFs
results = service.export_multiple_pdfs(
    document_ids=[1, 2, 3],
    output_dir='/path/to/output'
)
```

### Get Statistics

```python
# Get overall statistics
stats = service.get_pdf_statistics()

# Get customer-specific statistics
stats = service.get_pdf_statistics(customer_id=1)

# Get statistics for date range
stats = service.get_pdf_statistics(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31)
)
```

## API Endpoints

### POST /api/v1/pdf-archiving/archive
Archive a PDF to customer documents.

**Request:**
```json
{
  "customer_id": 1,
  "project_id": 10,
  "company_name": "Mustermann GmbH",
  "products": [
    {"name": "PV Module", "quantity": 20}
  ],
  "total_price": 16999.00,
  "offer_data": {...}
}
```

**Response:**
```json
{
  "document_id": 123,
  "metadata": {
    "creation_date": "2025-01-15T10:30:00",
    "company_id": 1,
    "company_name": "Mustermann GmbH",
    "total_price": 16999.00,
    "pdf_type": "offer_pdf",
    "version": 1,
    "file_size": 1024,
    "checksum": "abc123..."
  },
  "message": "PDF archived successfully"
}
```

### GET /api/v1/pdf-archiving/history/{customer_id}
Get PDF history for a customer.

**Query Parameters:**
- `project_id` (optional): Filter by project
- `pdf_type` (optional): Filter by PDF type
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "display_name": "Angebot_v1_2025-01-15.pdf",
      "doc_type": "offer_pdf",
      "uploaded_at": "2025-01-15T10:30:00",
      "version": 1
    }
  ],
  "total_count": 1
}
```

### POST /api/v1/pdf-archiving/search
Search PDFs in archive.

**Request:**
```json
{
  "customer_id": 1,
  "search_term": "Angebot",
  "pdf_type": "offer_pdf",
  "min_price": 10000.00,
  "max_price": 20000.00,
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "company_name": "Mustermann"
}
```

**Response:**
```json
{
  "documents": [...],
  "total_count": 5
}
```

### GET /api/v1/pdf-archiving/export/{document_id}
Export a PDF from archive.

**Response:** PDF file (application/pdf)

### POST /api/v1/pdf-archiving/export-multiple
Export multiple PDFs from archive.

**Request:**
```json
{
  "document_ids": [1, 2, 3],
  "output_dir": "/path/to/output"
}
```

**Response:**
```json
{
  "exported_count": 3,
  "results": {
    "1": "/path/to/output/doc1.pdf",
    "2": "/path/to/output/doc2.pdf",
    "3": "/path/to/output/doc3.pdf"
  }
}
```

### GET /api/v1/pdf-archiving/statistics
Get PDF archive statistics.

**Query Parameters:**
- `customer_id` (optional): Filter by customer
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)

**Response:**
```json
{
  "total_pdfs": 150,
  "total_customers": 25,
  "by_type": {
    "offer_pdf": 100,
    "invoice_pdf": 30,
    "contract_pdf": 20
  }
}
```

### GET /api/v1/pdf-archiving/next-version/{customer_id}
Get the next version number for a PDF type.

**Query Parameters:**
- `pdf_type` (required): PDF type
- `project_id` (optional): Project ID

**Response:**
```json
{
  "next_version": 3
}
```

## PDF Metadata Structure

```python
class PDFMetadata:
    creation_date: datetime      # When PDF was created
    company_id: int             # Customer/company ID
    company_name: str           # Customer/company name
    products: List[Dict]        # List of products
    total_price: float          # Total price
    pdf_type: str              # Type: offer_pdf, invoice_pdf, etc.
    project_type: str          # Project type: pv, heatpump, combined
    version: int               # Version number
    file_size: int             # File size in bytes
    checksum: str              # SHA-256 checksum
    additional_data: Dict      # Additional custom data
```

## PDF Types

- **offer_pdf**: Offer/quote documents
- **invoice_pdf**: Invoice documents
- **contract_pdf**: Contract documents
- **report_pdf**: Report documents
- **other_pdf**: Other PDF documents

## Versioning

The service automatically manages PDF versions:

1. **First PDF**: Version 1
2. **Updated PDF**: Version 2
3. **Another Update**: Version 3
4. And so on...

Versions are tracked per customer and PDF type. Each version is preserved in the archive.

## Integration with CRM

The PDF archiving service integrates seamlessly with the CRM system:

### Automatic Offer Status Update

When an offer PDF is archived, the service automatically:
1. Updates offer status to "sent"
2. Creates a follow-up reminder for 7 days
3. Records the offer version
4. Stores the offer value

### Customer Documents

All PDFs are stored in the `customer_documents` table with:
- Customer ID linkage
- Project ID linkage (optional)
- Document type classification
- Upload timestamp
- File bytes (BLOB)

## Best Practices

### 1. Always Provide Metadata

```python
# Good: Comprehensive metadata
doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot.pdf",
    customer_id=1,
    company_name="Mustermann GmbH",
    products=[...],
    total_price=16999.00
)

# Avoid: Minimal metadata
doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot.pdf",
    customer_id=1
)
```

### 2. Use Descriptive Filenames

```python
# Good: Descriptive filename
filename = "Angebot_Mustermann_PV_2025-01-15.pdf"

# Avoid: Generic filename
filename = "document.pdf"
```

### 3. Include Offer Data

```python
# Good: Complete offer data
offer_data = {
    'customer_id': 1,
    'customer': {'name': 'Mustermann GmbH'},
    'project_type': 'pv',
    'products': [...],
    'total_cost': 16999.00,
    'offer_id': 'OFF-2025-001'
}

doc_id = service.auto_save_to_crm(
    pdf_bytes=pdf_bytes,
    filename="Angebot.pdf",
    customer_id=1,
    offer_data=offer_data
)
```

### 4. Handle Errors Gracefully

```python
try:
    doc_id = service.auto_save_to_crm(...)
    if doc_id:
        print(f"Success: {doc_id}")
    else:
        print("Failed to archive PDF")
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### PDF Not Archived

**Problem:** `auto_save_to_crm` returns `None`

**Solutions:**
1. Check if customer_id exists in database
2. Verify PDF bytes are valid
3. Check database connection
4. Review logs for error messages

### Version Number Incorrect

**Problem:** Version number doesn't increment

**Solutions:**
1. Check if previous PDFs exist for customer
2. Verify PDF type matches
3. Check project_id if using project-specific versioning

### Search Returns No Results

**Problem:** `search_pdfs` returns empty list

**Solutions:**
1. Verify search criteria
2. Check date range filters
3. Ensure PDFs exist in database
4. Try broader search terms

## Performance Considerations

### Large PDF Files

For PDFs larger than 10MB:
- Consider compression before archiving
- Use streaming for export
- Implement pagination for history

### Many PDFs

For customers with 100+ PDFs:
- Use pagination in history retrieval
- Implement caching for frequently accessed PDFs
- Use date range filters to limit results

### Search Performance

For fast search:
- Use specific filters (customer_id, pdf_type)
- Limit date ranges
- Use indexed fields in queries

## Security

### Access Control

Implement access control in your application:
```python
# Check user permissions before archiving
if user.has_permission('archive_pdf'):
    doc_id = service.auto_save_to_crm(...)
```

### Data Integrity

The service ensures data integrity through:
- SHA-256 checksums
- Version tracking
- Immutable archives (no overwriting)

### Audit Trail

All PDF operations are logged:
- Archive timestamp
- User (if tracked)
- Customer ID
- Document type
- Version number

## Requirements

- Python 3.10+
- FastAPI
- SQLite (or compatible database)
- Existing CRM database schema

## Related Documentation

- [CRM Integration Guide](./CRM_INTEGRATION_GUIDE.md)
- [PDF Generation Guide](./PDF_GENERATION_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the demo script: `demo_pdf_archiving.py`
3. Run the tests: `pytest tests/test_pdf_archiving_service.py`
4. Check the logs for error messages
