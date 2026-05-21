# PDF Export & Download - Quick Reference

## Quick Start

### Download Single PDF
```typescript
<PDFExportManager pdfId={123} />
```

### Download Multiple PDFs
```typescript
<PDFExportManager pdfIds={[123, 124, 125]} />
```

### View History
```typescript
<PDFHistoryViewer userId={currentUser.id} />
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/pdf-export/download/single` | POST | Download single PDF |
| `/api/v1/pdf-export/download/batch` | POST | Download multiple PDFs as ZIP |
| `/api/v1/pdf-export/email/single` | POST | Send single PDF via email |
| `/api/v1/pdf-export/email/batch` | POST | Send multiple PDFs via email |
| `/api/v1/pdf-export/preview` | POST | Get PDF preview data |
| `/api/v1/pdf-export/history` | GET | Get PDF history |
| `/api/v1/pdf-export/history/search` | POST | Search PDF history |
| `/api/v1/pdf-export/history/statistics` | GET | Get statistics |
| `/api/v1/pdf-export/history/{id}` | DELETE | Delete history record |
| `/api/v1/pdf-export/cleanup` | POST | Clean up old files |

## Service Methods

### PDFExportService

```python
# Export single PDF
export_single_pdf(pdf_bytes, filename, metadata)

# Export batch PDFs
export_batch_pdfs(pdfs, zip_filename)

# Send email
send_pdf_email(pdf_bytes, filename, recipient, subject, body, smtp_config)

# Send batch email
send_batch_pdf_email(pdfs, recipient, subject, body, smtp_config, as_zip)

# Get preview
get_pdf_for_preview(pdf_bytes)

# Get for download
get_pdf_for_download(file_path)

# Cleanup
cleanup_old_exports(days)
```

### PDFHistoryService

```python
# Record generation
record_pdf_generation(user_id, pdf_type, filename, file_path, file_size, metadata)

# Get history
get_user_history(user_id, limit, offset, pdf_type)

# Get recent
get_recent_pdfs(user_id, count)

# Search
search_history(user_id, search_term, pdf_type, date_from, date_to)

# Statistics
get_statistics(user_id, date_from, date_to)

# Delete
delete_history_record(user_id, record_id)

# Bulk delete
bulk_delete_history(user_id, record_ids)
```

## Component Props

### PDFExportManager

| Prop | Type | Description |
|------|------|-------------|
| `pdfId` | number | Single PDF ID |
| `pdfIds` | number[] | Multiple PDF IDs |
| `onExportComplete` | function | Callback on export complete |

### PDFHistoryViewer

| Prop | Type | Description |
|------|------|-------------|
| `userId` | number | User ID for history |
| `onPDFSelect` | function | Callback on PDF selection |

## Common Patterns

### Download with Progress
```typescript
const [progress, setProgress] = useState(0);

const download = async () => {
  setProgress(0);
  // Download logic
  setProgress(100);
};
```

### Email with Validation
```typescript
const sendEmail = async (email: string) => {
  if (!isValidEmail(email)) {
    showError('Invalid email');
    return;
  }
  // Send logic
};
```

### Batch Operations
```typescript
const downloadMultiple = async (ids: number[]) => {
  const response = await fetch('/api/v1/pdf-export/download/batch', {
    method: 'POST',
    body: JSON.stringify({ pdf_ids: ids })
  });
  // Handle response
};
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

## Configuration

### Environment Variables
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_password
SMTP_USE_TLS=true
PDF_STORAGE_PATH=pdf_exports
PDF_CLEANUP_DAYS=7
```

## Best Practices

1. ✅ Always validate email addresses
2. ✅ Use background tasks for email sending
3. ✅ Implement progress tracking for large files
4. ✅ Clean up old exports regularly
5. ✅ Cache frequently accessed PDFs
6. ✅ Use pagination for history
7. ✅ Implement proper error handling
8. ✅ Log all export operations
9. ✅ Validate file sizes
10. ✅ Use secure storage paths

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Download fails | Check file permissions |
| Email not sending | Verify SMTP config |
| Preview not working | Check base64 encoding |
| History not loading | Verify database connection |
| Slow downloads | Enable compression |

## Performance Tips

1. Use ZIP for batch downloads
2. Implement caching
3. Use background tasks
4. Enable compression
5. Paginate history queries
6. Clean up old files
7. Optimize database queries
8. Use CDN for static files

## Security Checklist

- [ ] JWT authentication enabled
- [ ] User authorization implemented
- [ ] File validation in place
- [ ] Rate limiting configured
- [ ] Email validation active
- [ ] Secure storage configured
- [ ] HTTPS enforced
- [ ] Input sanitization enabled

## Quick Commands

```bash
# Start backend
cd backend && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev

# Run tests
pytest tests/test_pdf_export_service.py

# Clean up old exports
curl -X POST http://localhost:8000/api/v1/pdf-export/cleanup?days=7
```

## Support

- 📖 Full Documentation: `PDF_EXPORT_DOWNLOAD_GUIDE.md`
- 🐛 Report Issues: GitHub Issues
- 💬 Get Help: Support Team
- 📧 Email: support@solarcalculator.pro
