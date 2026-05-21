# Document Management System - Complete Guide

## Overview

The Document Management System provides comprehensive functionality for storing, versioning, templating, generating, sharing, and searching documents within the Solar Calculator Pro application.

## Features

### 1. Document Storage
- **Upload Documents**: Store any file type (PDF, Word, Excel, images, etc.)
- **Metadata Management**: Add names, descriptions, tags, and custom metadata
- **File Organization**: Automatic organization by date and unique identifiers
- **Status Tracking**: Draft, Active, Archived, and Deleted states

### 2. Document Versioning
- **Version Control**: Create multiple versions of the same document
- **Version History**: Track all versions with timestamps and creators
- **Latest Version Tracking**: Automatically mark the most recent version
- **Version Comparison**: Compare different versions side-by-side

### 3. Document Templates
- **Template Library**: Store reusable document templates
- **Variable Support**: Define placeholders for dynamic content
- **Category Organization**: Organize templates by category
- **Template Management**: Create, update, and deactivate templates

### 4. Document Generation
- **Template-Based Generation**: Create documents from templates
- **Variable Substitution**: Replace template variables with actual data
- **Automated Creation**: Generate documents programmatically
- **Batch Generation**: Create multiple documents at once

### 5. Document Sharing
- **User Sharing**: Share documents with specific users
- **Email Sharing**: Share via email with access tokens
- **Permission Control**: Set view, edit, delete, and share permissions
- **Expiration Dates**: Set time-limited access
- **Access Tracking**: Monitor when shared documents are accessed

### 6. Document Search
- **Full-Text Search**: Search by name and description
- **Filter by Type**: Filter by document type (PDF, Word, etc.)
- **Filter by Status**: Filter by document status
- **Tag-Based Search**: Search by tags
- **Date Range Search**: Filter by creation date
- **Creator Filter**: Filter by document creator

## API Endpoints

### Document CRUD

#### Create Document
```http
POST /api/v1/documents/
Content-Type: multipart/form-data

file: <file>
name: "My Document"
description: "Document description"
type: "pdf"
```

**Response:**
```json
{
  "id": 1,
  "name": "My Document",
  "description": "Document description",
  "type": "pdf",
  "status": "draft",
  "file_name": "document.pdf",
  "file_path": "2024/01/15/abc123_document.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "version": 1,
  "is_latest_version": true,
  "parent_document_id": null,
  "tags": [],
  "metadata": {},
  "created_by": 1,
  "updated_by": null,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### Get Document
```http
GET /api/v1/documents/{document_id}
```

#### Update Document
```http
PUT /api/v1/documents/{document_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "active",
  "tags": ["important", "project-a"]
}
```

#### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

#### Download Document
```http
GET /api/v1/documents/{document_id}/download
```

### Document Versioning

#### Create New Version
```http
POST /api/v1/documents/{document_id}/versions
Content-Type: multipart/form-data

file: <new_file>
```

#### Get All Versions
```http
GET /api/v1/documents/{document_id}/versions
```

**Response:**
```json
[
  {
    "id": 2,
    "version": 2,
    "created_at": "2024-01-16T10:00:00Z",
    "created_by": 1,
    "file_size": 1050000,
    "is_latest_version": true
  },
  {
    "id": 1,
    "version": 1,
    "created_at": "2024-01-15T10:00:00Z",
    "created_by": 1,
    "file_size": 1024000,
    "is_latest_version": false
  }
]
```

### Document Templates

#### Create Template
```http
POST /api/v1/documents/templates
Content-Type: application/json

{
  "name": "Invoice Template",
  "description": "Standard invoice template",
  "type": "pdf",
  "template_path": "templates/invoice.pdf",
  "template_variables": ["customer_name", "invoice_number", "total_amount"],
  "category": "financial",
  "tags": ["invoice", "billing"]
}
```

#### List Templates
```http
GET /api/v1/documents/templates?type=pdf&category=financial
```

#### Get Template
```http
GET /api/v1/documents/templates/{template_id}
```

#### Update Template
```http
PUT /api/v1/documents/templates/{template_id}
Content-Type: application/json

{
  "name": "Updated Template Name",
  "is_active": true
}
```

### Document Generation

#### Generate from Template
```http
POST /api/v1/documents/generate
Content-Type: application/json

{
  "template_id": 1,
  "output_name": "Invoice_2024_001.pdf",
  "variables": {
    "customer_name": "John Doe",
    "invoice_number": "INV-2024-001",
    "total_amount": "1,234.56 €"
  },
  "tags": ["invoice", "2024", "customer-123"]
}
```

### Document Sharing

#### Share Document
```http
POST /api/v1/documents/share
Content-Type: application/json

{
  "document_id": 1,
  "shared_with_user_id": 2,
  "can_view": true,
  "can_edit": false,
  "can_delete": false,
  "can_share": false,
  "expires_at": "2024-12-31T23:59:59Z",
  "message": "Please review this document"
}
```

**Response:**
```json
{
  "id": 1,
  "document_id": 1,
  "shared_with_user_id": 2,
  "shared_with_email": null,
  "can_view": true,
  "can_edit": false,
  "can_delete": false,
  "can_share": false,
  "access_token": "abc123def456...",
  "expires_at": "2024-12-31T23:59:59Z",
  "shared_by": 1,
  "message": "Please review this document",
  "created_at": "2024-01-15T10:00:00Z",
  "accessed_at": null
}
```

#### Get Shared Documents
```http
GET /api/v1/documents/shared
```

#### Revoke Share
```http
DELETE /api/v1/documents/share/{share_id}
```

### Document Search

#### Search Documents
```http
POST /api/v1/documents/search
Content-Type: application/json

{
  "query": "invoice",
  "type": "pdf",
  "status": "active",
  "tags": ["important"],
  "created_after": "2024-01-01T00:00:00Z",
  "created_before": "2024-12-31T23:59:59Z",
  "created_by": 1,
  "limit": 50,
  "offset": 0
}
```

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "name": "Invoice 2024-001",
      "description": "Customer invoice",
      "type": "pdf",
      "status": "active",
      "file_name": "invoice.pdf",
      "file_path": "2024/01/15/abc123_invoice.pdf",
      "file_size": 1024000,
      "mime_type": "application/pdf",
      "version": 1,
      "is_latest_version": true,
      "parent_document_id": null,
      "tags": ["invoice", "important"],
      "metadata": {},
      "created_by": 1,
      "updated_by": null,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

## Database Schema

### Documents Table
- `id`: Primary key
- `name`: Document name
- `description`: Document description
- `type`: Document type (PDF, Word, Excel, Image, Text, Other)
- `status`: Document status (Draft, Active, Archived, Deleted)
- `file_name`: Original filename
- `file_path`: Storage path
- `file_size`: File size in bytes
- `mime_type`: MIME type
- `version`: Version number
- `is_latest_version`: Boolean flag for latest version
- `parent_document_id`: Reference to parent document for versions
- `tags`: JSON array of tags
- `metadata`: JSON object for custom metadata
- `created_by`: User ID of creator
- `updated_by`: User ID of last updater
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Document Templates Table
- `id`: Primary key
- `name`: Template name
- `description`: Template description
- `type`: Document type
- `template_path`: Path to template file
- `template_variables`: JSON array of variable names
- `category`: Template category
- `tags`: JSON array of tags
- `is_active`: Boolean flag for active status
- `created_by`: User ID of creator
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Document Shares Table
- `id`: Primary key
- `document_id`: Reference to document
- `shared_with_user_id`: User ID (if sharing with user)
- `shared_with_email`: Email address (if sharing via email)
- `can_view`: View permission
- `can_edit`: Edit permission
- `can_delete`: Delete permission
- `can_share`: Share permission
- `access_token`: Unique access token
- `expires_at`: Expiration timestamp
- `shared_by`: User ID of sharer
- `message`: Optional message
- `created_at`: Creation timestamp
- `accessed_at`: Last access timestamp

## Usage Examples

### Python Service Usage

```python
from backend.services.document_service import DocumentService
from backend.models.document_schemas import DocumentCreate, DocumentSearchRequest

# Initialize service
service = DocumentService(db_session)

# Create document
with open('document.pdf', 'rb') as f:
    document_data = DocumentCreate(
        name="My Document",
        description="Important document",
        type="pdf",
        file_name="document.pdf",
        file_path="",
        file_size=0,
        mime_type="application/pdf",
        tags=["important", "project-a"]
    )
    document = service.create_document(document_data, f, user_id=1)

# Search documents
search_request = DocumentSearchRequest(
    query="invoice",
    type="pdf",
    tags=["important"],
    limit=10
)
documents, total = service.search_documents(search_request, user_id=1)

# Create version
with open('document_v2.pdf', 'rb') as f:
    new_version = service.create_version(document.id, f, user_id=1)

# Share document
from backend.models.document_schemas import DocumentShareCreate

share_data = DocumentShareCreate(
    document_id=document.id,
    shared_with_user_id=2,
    can_view=True,
    can_edit=False
)
share = service.share_document(share_data, user_id=1)
```

## Best Practices

1. **File Organization**: Use descriptive names and tags for easy searching
2. **Version Control**: Create new versions instead of overwriting documents
3. **Access Control**: Use sharing permissions to control document access
4. **Regular Cleanup**: Archive or delete old documents to save storage
5. **Template Reuse**: Create templates for frequently generated documents
6. **Metadata**: Use metadata for additional context and filtering
7. **Security**: Always validate file types and sizes before upload
8. **Backup**: Regularly backup the document storage directory

## Security Considerations

1. **File Validation**: Validate file types and sizes
2. **Access Control**: Enforce permission checks on all operations
3. **Secure Storage**: Store files outside web root
4. **Token Security**: Use secure random tokens for sharing
5. **Expiration**: Set expiration dates on shared documents
6. **Audit Trail**: Log all document access and modifications
7. **Encryption**: Consider encrypting sensitive documents at rest

## Performance Optimization

1. **Indexing**: Database indexes on frequently queried fields
2. **Caching**: Cache frequently accessed documents
3. **Lazy Loading**: Load document content only when needed
4. **Pagination**: Use pagination for large result sets
5. **Compression**: Compress large files before storage
6. **CDN**: Use CDN for frequently accessed documents
7. **Cleanup**: Regularly clean up deleted documents

## Troubleshooting

### Common Issues

1. **Upload Fails**
   - Check file size limits
   - Verify storage directory permissions
   - Check available disk space

2. **Document Not Found**
   - Verify document ID
   - Check document status (not deleted)
   - Verify user permissions

3. **Version Creation Fails**
   - Verify parent document exists
   - Check storage space
   - Verify file format compatibility

4. **Search Returns No Results**
   - Check search criteria
   - Verify user has access to documents
   - Check document status filters

## Requirements Mapping

This implementation satisfies the following requirements:
- **1.3**: Document management as part of core functionality
- **6.1**: Modular service architecture for document operations
