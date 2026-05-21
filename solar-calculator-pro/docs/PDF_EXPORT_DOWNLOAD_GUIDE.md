# PDF Export & Download System - Complete Guide

## Overview

The PDF Export & Download system provides comprehensive functionality for exporting, downloading, emailing, previewing, printing, and managing PDF documents in the Solar Calculator Pro application.

## Features

### 1. Single PDF Download
- Download individual PDF files
- Automatic filename generation
- Progress tracking
- Error handling and retry logic

### 2. Batch PDF Download
- Download multiple PDFs as a ZIP file
- Configurable ZIP filename
- Compression optimization
- Bulk export management

### 3. Email Sending
- Send single PDF via email
- Send multiple PDFs (as ZIP or separate attachments)
- Customizable email subject and body
- Background email processing
- SMTP configuration support

### 4. PDF Preview
- Browser-based PDF preview
- Base64 encoding for web display
- Zoom and navigation controls
- Full-screen mode

### 5. PDF Printing
- Direct print from browser
- Print dialog integration
- Page setup options
- Print preview

### 6. PDF History
- Complete generation history
- Search and filter capabilities
- Statistics and analytics
- Bulk operations

## Architecture

### Backend Services

#### PDFExportService
```python
from backend.services.pdf_export_service import PDFExportService

service = PDFExportService(pdf_storage_path="pdf_exports")

# Export single PDF
result = service.export_single_pdf(
    pdf_bytes=pdf_content,
    filename="solar_offer.pdf",
    metadata={'customer': 'John Doe'}
)

# Export batch PDFs
result = service.export_batch_pdfs(
    pdfs=[
        {'bytes': pdf1, 'filename': 'offer1.pdf'},
        {'bytes': pdf2, 'filename': 'offer2.pdf'}
    ],
    zip_filename="batch_offers.zip"
)

# Send email
result = service.send_pdf_email(
    pdf_bytes=pdf_content,
    filename="offer.pdf",
    recipient_email="customer@example.com",
    subject="Your Solar Offer",
    body="Please find attached...",
    smtp_config={
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'your@email.com',
        'password': 'password',
        'use_tls': True
    }
)
```

#### PDFHistoryService
```python
from backend.services.pdf_history_service import PDFHistoryService

service = PDFHistoryService(db_session)

# Record PDF generation
record = service.record_pdf_generation(
    user_id=1,
    pdf_type='standard_pv',
    filename='offer.pdf',
    file_path='/path/to/offer.pdf',
    file_size=1024000,
    metadata={'customer_id': 123}
)

# Get user history
history = service.get_user_history(
    user_id=1,
    limit=50,
    offset=0,
    pdf_type='standard_pv'
)

# Search history
results = service.search_history(
    user_id=1,
    search_term='solar',
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 12, 31)
)

# Get statistics
stats = service.get_statistics(user_id=1)
```

### API Endpoints

#### Download Endpoints

**Single PDF Download**
```http
POST /api/v1/pdf-export/download/single
Content-Type: application/json
Authorization: Bearer <token>

{
  "pdf_id": 123,
  "filename": "solar_offer.pdf"
}

Response: PDF file (application/pdf)
```

**Batch PDF Download**
```http
POST /api/v1/pdf-export/download/batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "pdf_ids": [123, 124, 125],
  "zip_filename": "solar_offers.zip"
}

Response: ZIP file (application/zip)
```

#### Email Endpoints

**Single PDF Email**
```http
POST /api/v1/pdf-export/email/single
Content-Type: application/json
Authorization: Bearer <token>

{
  "pdf_id": 123,
  "recipient_email": "customer@example.com",
  "subject": "Your Solar Offer",
  "body": "Please find attached your solar offer.",
  "filename": "solar_offer.pdf"
}

Response:
{
  "message": "Email is being sent",
  "recipient": "customer@example.com",
  "filename": "solar_offer.pdf",
  "queued_at": "2024-01-15T10:30:00Z"
}
```

**Batch PDF Email**
```http
POST /api/v1/pdf-export/email/batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "pdf_ids": [123, 124, 125],
  "recipient_email": "customer@example.com",
  "subject": "Your Solar Offers",
  "body": "Please find attached your solar offers.",
  "as_zip": true,
  "zip_filename": "solar_offers.zip"
}

Response:
{
  "message": "Email is being sent",
  "recipient": "customer@example.com",
  "pdf_count": 3,
  "as_zip": true,
  "queued_at": "2024-01-15T10:30:00Z"
}
```

#### Preview & Print Endpoints

**PDF Preview**
```http
POST /api/v1/pdf-export/preview
Content-Type: application/json
Authorization: Bearer <token>

{
  "pdf_id": 123
}

Response:
{
  "pdf_id": 123,
  "preview_data": "base64_encoded_pdf_data",
  "content_type": "application/pdf",
  "size": 1024000
}
```

#### History Endpoints

**Get History**
```http
GET /api/v1/pdf-export/history?limit=50&offset=0&pdf_type=standard_pv
Authorization: Bearer <token>

Response:
{
  "history": [
    {
      "id": 1,
      "pdf_type": "standard_pv",
      "filename": "offer.pdf",
      "file_size_mb": 1.5,
      "generated_at": "2024-01-15T10:30:00Z",
      "metadata": {},
      "status": "completed"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

**Search History**
```http
POST /api/v1/pdf-export/history/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "search_term": "solar",
  "pdf_type": "standard_pv",
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-12-31T23:59:59Z",
  "limit": 50,
  "offset": 0
}

Response:
{
  "results": [...],
  "count": 25,
  "query": {...}
}
```

**Get Statistics**
```http
GET /api/v1/pdf-export/history/statistics
Authorization: Bearer <token>

Response:
{
  "total_pdfs": 150,
  "total_size_mb": 225.5,
  "by_type": {
    "standard_pv": 80,
    "extended_pv": 40,
    "multi_pdf": 30
  },
  "by_month": {
    "2024-01": 50,
    "2024-02": 60,
    "2024-03": 40
  },
  "average_size_mb": 1.5,
  "most_common_type": "standard_pv"
}
```

**Delete History Record**
```http
DELETE /api/v1/pdf-export/history/{record_id}
Authorization: Bearer <token>

Response:
{
  "record_id": 123,
  "deleted": true,
  "deleted_at": "2024-01-15T10:30:00Z"
}
```

### Frontend Components

#### PDFExportManager

```tsx
import { PDFExportManager } from '@/components/pdf/PDFExportManager';

// Single PDF export
<PDFExportManager
  pdfId={123}
  onExportComplete={(result) => {
    console.log('Export complete:', result);
  }}
/>

// Batch PDF export
<PDFExportManager
  pdfIds={[123, 124, 125]}
  onExportComplete={(result) => {
    console.log('Batch export complete:', result);
  }}
/>
```

**Features:**
- Download button (single or batch)
- Email dialog with customization
- Print button (single only)
- Progress tracking
- Error handling
- Toast notifications

#### PDFHistoryViewer

```tsx
import { PDFHistoryViewer } from '@/components/pdf/PDFHistoryViewer';

<PDFHistoryViewer
  userId={currentUser.id}
  onPDFSelect={(record) => {
    console.log('PDF selected:', record);
    // Open preview or perform action
  }}
/>
```

**Features:**
- Statistics cards (total PDFs, size, average)
- Search and filter controls
- Date range filtering
- Type filtering
- Bulk selection and deletion
- Download from history
- Preview from history
- Pagination

## Usage Examples

### Example 1: Download Single PDF

```typescript
// Frontend
const handleDownload = async (pdfId: number) => {
  const response = await fetch('/api/v1/pdf-export/download/single', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ pdf_id: pdfId })
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'solar_offer.pdf';
  a.click();
};
```

### Example 2: Send PDF via Email

```typescript
// Frontend
const handleEmailSend = async (pdfId: number, email: string) => {
  const response = await fetch('/api/v1/pdf-export/email/single', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      pdf_id: pdfId,
      recipient_email: email,
      subject: 'Your Solar Calculator Results',
      body: 'Please find attached your personalized solar calculator results.'
    })
  });

  const result = await response.json();
  console.log('Email queued:', result);
};
```

### Example 3: Batch Download with ZIP

```typescript
// Frontend
const handleBatchDownload = async (pdfIds: number[]) => {
  const response = await fetch('/api/v1/pdf-export/download/batch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      pdf_ids: pdfIds,
      zip_filename: 'solar_offers_batch.zip'
    })
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'solar_offers_batch.zip';
  a.click();
};
```

### Example 4: Preview PDF in Browser

```typescript
// Frontend
const handlePreview = async (pdfId: number) => {
  const response = await fetch('/api/v1/pdf-export/preview', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ pdf_id: pdfId })
  });

  const result = await response.json();
  
  // Convert base64 to blob
  const byteCharacters = atob(result.preview_data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  
  // Open in new window
  window.open(url, '_blank');
};
```

## Configuration

### SMTP Configuration

Configure SMTP settings for email sending:

```python
# backend/config.py
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD'),
    'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
}
```

### Storage Configuration

Configure PDF storage location:

```python
# backend/config.py
PDF_STORAGE_PATH = os.getenv('PDF_STORAGE_PATH', 'pdf_exports')
PDF_CLEANUP_DAYS = int(os.getenv('PDF_CLEANUP_DAYS', 7))
```

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own PDFs
3. **File Validation**: Validate PDF files before serving
4. **Rate Limiting**: Implement rate limiting on download endpoints
5. **Email Validation**: Validate email addresses before sending
6. **Storage Security**: Store PDFs in secure location with proper permissions

## Performance Optimization

1. **Caching**: Cache frequently accessed PDFs
2. **Compression**: Use ZIP compression for batch downloads
3. **Background Processing**: Send emails in background tasks
4. **Cleanup**: Regularly clean up old exported files
5. **Pagination**: Use pagination for history queries

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "status_code": 500
}
```

Common error codes:
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (missing or invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (PDF not found)
- 500: Internal Server Error

## Testing

### Backend Tests

```python
# tests/test_pdf_export_service.py
def test_export_single_pdf():
    service = PDFExportService()
    result = service.export_single_pdf(
        pdf_bytes=b"test content",
        filename="test.pdf"
    )
    assert result['success'] == True
    assert result['filename'] == 'test.pdf'

def test_export_batch_pdfs():
    service = PDFExportService()
    pdfs = [
        {'bytes': b"test1", 'filename': 'test1.pdf'},
        {'bytes': b"test2", 'filename': 'test2.pdf'}
    ]
    result = service.export_batch_pdfs(pdfs)
    assert result['success'] == True
    assert result['pdf_count'] == 2
```

### Frontend Tests

```typescript
// tests/PDFExportManager.test.tsx
describe('PDFExportManager', () => {
  it('downloads single PDF', async () => {
    render(<PDFExportManager pdfId={123} />);
    const downloadButton = screen.getByText('Download PDF');
    fireEvent.click(downloadButton);
    // Assert download initiated
  });

  it('sends email with PDF', async () => {
    render(<PDFExportManager pdfId={123} />);
    const emailButton = screen.getByText('Send Email');
    fireEvent.click(emailButton);
    // Assert email dialog opened
  });
});
```

## Troubleshooting

### Common Issues

1. **Download fails**: Check file permissions and storage path
2. **Email not sending**: Verify SMTP configuration
3. **Preview not working**: Check base64 encoding
4. **History not loading**: Verify database connection

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. Cloud storage integration (S3, Azure Blob)
2. PDF watermarking
3. Digital signatures
4. PDF encryption
5. Advanced search with full-text indexing
6. Export templates
7. Scheduled email sending
8. PDF versioning
9. Collaborative annotations
10. Mobile app integration

## Support

For issues or questions:
- Check the documentation
- Review error logs
- Contact support team
- Submit bug reports

## License

Copyright © 2024 Solar Calculator Pro. All rights reserved.
