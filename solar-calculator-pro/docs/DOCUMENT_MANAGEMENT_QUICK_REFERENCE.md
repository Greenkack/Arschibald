# Document Management - Quick Reference

## Quick Start

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "name=My Document" \
  -F "type=pdf"
```

### Search Documents
```bash
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "invoice", "type": "pdf", "limit": 10}'
```

### Download Document
```bash
curl -X GET "http://localhost:8000/api/v1/documents/1/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -O
```

## Key Features

| Feature | Endpoint | Method |
|---------|----------|--------|
| Upload Document | `/documents/` | POST |
| Get Document | `/documents/{id}` | GET |
| Update Document | `/documents/{id}` | PUT |
| Delete Document | `/documents/{id}` | DELETE |
| Download Document | `/documents/{id}/download` | GET |
| Create Version | `/documents/{id}/versions` | POST |
| List Versions | `/documents/{id}/versions` | GET |
| Create Template | `/documents/templates` | POST |
| List Templates | `/documents/templates` | GET |
| Generate Document | `/documents/generate` | POST |
| Share Document | `/documents/share` | POST |
| Get Shared Docs | `/documents/shared` | GET |
| Search Documents | `/documents/search` | POST |

## Document Types

- `pdf` - PDF documents
- `word` - Word documents
- `excel` - Excel spreadsheets
- `image` - Image files
- `text` - Text files
- `other` - Other file types

## Document Status

- `draft` - Draft document
- `active` - Active document
- `archived` - Archived document
- `deleted` - Deleted document (soft delete)

## Permissions

- `can_view` - View document
- `can_edit` - Edit document metadata
- `can_delete` - Delete document
- `can_share` - Share document with others

## Common Operations

### Create Document with Tags
```python
document_data = DocumentCreate(
    name="Invoice 2024-001",
    type="pdf",
    tags=["invoice", "2024", "important"]
)
```

### Search by Multiple Criteria
```python
search = DocumentSearchRequest(
    query="invoice",
    type="pdf",
    status="active",
    tags=["important"],
    created_after=datetime(2024, 1, 1),
    limit=50
)
```

### Share with Expiration
```python
share = DocumentShareCreate(
    document_id=1,
    shared_with_user_id=2,
    can_view=True,
    expires_at=datetime(2024, 12, 31)
)
```

### Generate from Template
```python
generate = DocumentGenerateRequest(
    template_id=1,
    output_name="Invoice_2024_001.pdf",
    variables={
        "customer_name": "John Doe",
        "amount": "1,234.56 €"
    }
)
```

## Storage Structure

```
storage/documents/
├── 2024/
│   ├── 01/
│   │   ├── 15/
│   │   │   ├── abc123_document.pdf
│   │   │   └── def456_invoice.pdf
│   │   └── 16/
│   │       └── ghi789_report.docx
│   └── 02/
│       └── ...
└── templates/
    ├── invoice.pdf
    └── report.docx
```

## Error Codes

| Code | Description |
|------|-------------|
| 201 | Document created successfully |
| 200 | Operation successful |
| 204 | Document deleted successfully |
| 404 | Document not found |
| 500 | Server error during operation |

## Tips

1. **Use Tags**: Tag documents for easy searching
2. **Version Control**: Create versions instead of overwriting
3. **Set Expiration**: Use expiration dates for temporary shares
4. **Regular Cleanup**: Archive old documents periodically
5. **Use Templates**: Create templates for recurring documents
6. **Metadata**: Add custom metadata for additional context
7. **Search Filters**: Combine multiple filters for precise results

## Integration Example

```python
from backend.services.document_service import DocumentService

# Initialize
service = DocumentService(db)

# Upload
with open('file.pdf', 'rb') as f:
    doc = service.create_document(doc_data, f, user_id=1)

# Search
docs, total = service.search_documents(search_request, user_id=1)

# Share
share = service.share_document(share_data, user_id=1)

# Download
file_path = service.get_file_path(doc)
```

## Requirements

- **Storage**: Sufficient disk space for documents
- **Permissions**: Write access to storage directory
- **Database**: PostgreSQL or SQLite with JSON support
- **Authentication**: Valid JWT token for API access
