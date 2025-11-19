# PDF Preview and Generation - Quick Reference

## 🚀 Quick Start

### Generate a PDF
```tsx
import { PDFGenerator } from './components/pdf/PDFGenerator';

<PDFGenerator
  projectData={myProjectData}
  template="main"
  onSuccess={(pdfData) => handleSuccess(pdfData)}
  onError={(error) => handleError(error)}
/>
```

### Preview a PDF
```tsx
import { PDFPreviewViewer } from './components/pdf/PDFPreviewViewer';

<PDFPreviewViewer
  pdfData={base64PDF}
  visible={true}
  onHide={() => setVisible(false)}
/>
```

### Download a PDF
```tsx
import { PDFDownloader } from './components/pdf/PDFDownloader';

<PDFDownloader
  pdfData={base64PDF}
  filename="document.pdf"
  buttonLabel="Download"
/>
```

### Email a PDF
```tsx
import { PDFEmailer } from './components/pdf/PDFEmailer';

<PDFEmailer
  pdfData={base64PDF}
  defaultRecipient="customer@example.com"
  defaultSubject="Your PDF"
/>
```

### View PDF History
```tsx
import { PDFHistory } from './components/pdf/PDFHistory';

<PDFHistory
  onPreview={(filename) => handlePreview(filename)}
/>
```

## 📋 Component Props

### PDFGenerator
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| projectData | any | Yes | Project data for PDF generation |
| template | string | Yes | Template name (main/simple/extended) |
| onSuccess | (pdfData: string) => void | No | Success callback with base64 PDF |
| onError | (error: string) => void | No | Error callback |
| className | string | No | Additional CSS class |

### PDFPreviewViewer
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| pdfData | string \| null | Yes | Base64 encoded PDF |
| visible | boolean | Yes | Dialog visibility |
| onHide | () => void | Yes | Hide callback |
| title | string | No | Dialog title |
| onDownload | () => void | No | Download callback |
| onEmail | () => void | No | Email callback |

### PDFDownloader
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| pdfData | string | No* | Base64 encoded PDF |
| storedFilename | string | No* | Server filename |
| filename | string | No | Download filename |
| buttonLabel | string | No | Button text |
| buttonIcon | string | No | Button icon |
| buttonClassName | string | No | Button CSS class |

*Either pdfData or storedFilename required

### PDFEmailer
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| pdfData | string | No* | Base64 encoded PDF |
| storedFilename | string | No* | Server filename |
| defaultRecipient | string | No | Default email address |
| defaultSubject | string | No | Default subject |
| buttonLabel | string | No | Button text |
| buttonIcon | string | No | Button icon |
| buttonClassName | string | No | Button CSS class |

*Either pdfData or storedFilename required

### PDFHistory
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| onPreview | (filename: string) => void | No | Preview callback |
| className | string | No | Additional CSS class |

## 🎯 Common Use Cases

### 1. Generate and Preview
```tsx
const [pdfData, setPdfData] = useState<string | null>(null);
const [showPreview, setShowPreview] = useState(false);

<PDFGenerator
  projectData={data}
  template="main"
  onSuccess={(pdf) => {
    setPdfData(pdf);
    setShowPreview(true);
  }}
/>

<PDFPreviewViewer
  pdfData={pdfData}
  visible={showPreview}
  onHide={() => setShowPreview(false)}
/>
```

### 2. Generate and Download
```tsx
const [pdfData, setPdfData] = useState<string | null>(null);

<PDFGenerator
  projectData={data}
  template="main"
  onSuccess={(pdf) => setPdfData(pdf)}
/>

{pdfData && (
  <PDFDownloader
    pdfData={pdfData}
    filename="my-document.pdf"
  />
)}
```

### 3. Generate and Email
```tsx
const [pdfData, setPdfData] = useState<string | null>(null);

<PDFGenerator
  projectData={data}
  template="main"
  onSuccess={(pdf) => setPdfData(pdf)}
/>

{pdfData && (
  <PDFEmailer
    pdfData={pdfData}
    defaultRecipient="customer@example.com"
    defaultSubject="Your Solar Project PDF"
  />
)}
```

### 4. Complete Workflow
```tsx
const [pdfData, setPdfData] = useState<string | null>(null);
const [showPreview, setShowPreview] = useState(false);

// Generate
<PDFGenerator
  projectData={data}
  template="main"
  onSuccess={(pdf) => setPdfData(pdf)}
/>

// Actions after generation
{pdfData && (
  <div className="pdf-actions">
    <Button
      label="Preview"
      onClick={() => setShowPreview(true)}
    />
    <PDFDownloader pdfData={pdfData} />
    <PDFEmailer pdfData={pdfData} />
  </div>
)}

// Preview dialog
<PDFPreviewViewer
  pdfData={pdfData}
  visible={showPreview}
  onHide={() => setShowPreview(false)}
/>
```

## 🔧 API Endpoints

### Generate PDF
```typescript
POST /api/v1/pdf/generate
{
  offer_data: {...},
  template: "main",
  use_cache: true,
  store_pdf: true,
  filename: "document.pdf",
  metadata: {...}
}
```

### Download PDF
```typescript
GET /api/v1/pdf/download/{filename}
```

### List PDFs
```typescript
GET /api/v1/pdf/list
```

### Delete PDF
```typescript
DELETE /api/v1/pdf/{filename}
```

### Email PDF
```typescript
POST /api/v1/email/send-pdf
{
  recipients: ["email@example.com"],
  subject: "...",
  message: "...",
  pdf_data: "...",
  cc: [],
  bcc: []
}
```

## 💡 Tips & Best Practices

### Performance
- ✅ Use caching for repeated generations
- ✅ Store PDFs for history access
- ✅ Use async generation for large documents
- ✅ Implement pagination in history

### User Experience
- ✅ Show progress during generation
- ✅ Provide clear error messages
- ✅ Confirm before deleting PDFs
- ✅ Validate email addresses
- ✅ Allow custom filenames

### Error Handling
```tsx
<PDFGenerator
  projectData={data}
  template="main"
  onSuccess={(pdf) => {
    toast.success('PDF generated successfully!');
    setPdfData(pdf);
  }}
  onError={(error) => {
    toast.error(`Failed to generate PDF: ${error}`);
    console.error(error);
  }}
/>
```

### Validation
```tsx
// Validate project data before generation
if (!projectData || Object.keys(projectData).length === 0) {
  toast.error('No project data available');
  return;
}

// Validate email before sending
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  toast.error('Invalid email address');
  return;
}
```

## 🎨 Styling

All components support custom styling:

```tsx
// Custom class
<PDFGenerator className="my-custom-generator" />

// Custom button style
<PDFDownloader buttonClassName="p-button-lg p-button-success" />

// Inline styles
<PDFPreviewViewer
  pdfData={pdf}
  visible={true}
  onHide={() => {}}
  style={{ width: '95vw', height: '95vh' }}
/>
```

## 🐛 Troubleshooting

### PDF not generating
- Check project data is valid
- Verify template name is correct
- Check API endpoint is accessible
- Review browser console for errors

### Preview not showing
- Ensure pdfData is base64 encoded
- Check browser PDF support
- Verify iframe is not blocked
- Try opening in new tab

### Download not working
- Check browser download settings
- Verify PDF data is valid
- Ensure filename has .pdf extension
- Check for popup blockers

### Email not sending
- Validate email addresses
- Check API endpoint configuration
- Verify email service is configured
- Review server logs for errors

## 📚 Related Documentation

- [PDF Service Guide](../backend/docs/PDF_SERVICE_GUIDE.md)
- [API Documentation](../backend/docs/API_DOCUMENTATION.md)
- [Component Library](./COMMON_COMPONENTS_GUIDE.md)
- [Task 41 Complete](../TASK_41_COMPLETE.md)

---

**Last Updated:** 2025-11-19
**Version:** 1.0.0
