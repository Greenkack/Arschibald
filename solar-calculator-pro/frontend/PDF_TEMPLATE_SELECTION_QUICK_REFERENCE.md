# PDF Template Selection - Quick Reference Guide

## Overview

The PDF Template Selection system provides a comprehensive interface for managing and selecting PDF templates for document generation.

## Components

### 1. TemplateGallery

**Purpose:** Display available templates in a grid layout

**Usage:**
```tsx
import { TemplateGallery } from '../components/pdf/TemplateGallery';

<TemplateGallery
  onSelectTemplate={(template) => setSelectedTemplate(template)}
  selectedTemplate={selectedTemplate}
  onPreviewTemplate={(template) => handlePreview(template)}
/>
```

**Props:**
- `onSelectTemplate`: Callback when template is selected
- `selectedTemplate`: Currently selected template (optional)
- `onPreviewTemplate`: Callback for preview action (optional)

### 2. TemplatePreview

**Purpose:** Preview PDF templates with zoom and navigation

**Usage:**
```tsx
import { TemplatePreview } from '../components/pdf/TemplatePreview';

<TemplatePreview
  template={previewTemplate}
  visible={previewVisible}
  onHide={() => setPreviewVisible(false)}
  projectData={projectData}
/>
```

**Props:**
- `template`: Template to preview
- `visible`: Dialog visibility state
- `onHide`: Callback to close dialog
- `projectData`: Optional project data for preview (optional)

### 3. TemplateUpload

**Purpose:** Upload custom PDF templates

**Usage:**
```tsx
import { TemplateUpload } from '../components/pdf/TemplateUpload';

<TemplateUpload
  visible={uploadVisible}
  onHide={() => setUploadVisible(false)}
  onUploadSuccess={() => refreshTemplates()}
/>
```

**Props:**
- `visible`: Dialog visibility state
- `onHide`: Callback to close dialog
- `onUploadSuccess`: Callback after successful upload

### 4. TemplateManagement

**Purpose:** Manage templates (edit, delete, set default)

**Usage:**
```tsx
import { TemplateManagement } from '../components/pdf/TemplateManagement';

<TemplateManagement
  onTemplateChange={() => refreshTemplates()}
/>
```

**Props:**
- `onTemplateChange`: Callback when templates are modified (optional)

### 5. PDFGeneration Page

**Purpose:** Main page integrating all PDF template features

**Usage:**
```tsx
import { PDFGeneration } from '../pages/PDFGeneration';

// In your router
<Route path="/pdf" element={<PDFGeneration />} />
```

## API Endpoints

### Get All Templates
```typescript
GET /api/v1/pdf/templates

Response:
[
  {
    name: "main",
    display_name: "Main Template",
    description: "Full-featured PDF",
    is_custom: false,
    created_at: "2025-01-19T10:00:00",
    file_size: 1024000
  }
]
```

### Upload Template
```typescript
POST /api/v1/pdf/templates/upload

FormData:
- file: File (PDF, HTML, or JSON)
- name: string
- description: string

Response:
{
  message: "Template uploaded successfully",
  template: { ... }
}
```

### Update Template
```typescript
PUT /api/v1/pdf/templates/{template_name}

Body:
{
  display_name: "Updated Name",
  description: "Updated description"
}

Response:
{
  message: "Template updated successfully"
}
```

### Delete Template
```typescript
DELETE /api/v1/pdf/templates/{template_name}

Response:
{
  message: "Template deleted successfully"
}
```

### Set Default Template
```typescript
POST /api/v1/pdf/templates/{template_name}/set-default

Response:
{
  message: "Template 'main' set as default"
}
```

### Get Default Template
```typescript
GET /api/v1/pdf/templates/default

Response:
{
  name: "main",
  display_name: "Main Template",
  ...
}
```

## Common Workflows

### 1. Browse and Select Template

```tsx
const [selectedTemplate, setSelectedTemplate] = useState<PDFTemplate | null>(null);

<TemplateGallery
  onSelectTemplate={setSelectedTemplate}
  selectedTemplate={selectedTemplate}
/>

{selectedTemplate && (
  <div>
    Selected: {selectedTemplate.display_name}
    <Button onClick={() => generatePDF(selectedTemplate)}>
      Generate PDF
    </Button>
  </div>
)}
```

### 2. Preview Template Before Selection

```tsx
const [previewTemplate, setPreviewTemplate] = useState<PDFTemplate | null>(null);
const [previewVisible, setPreviewVisible] = useState(false);

<TemplateGallery
  onPreviewTemplate={(template) => {
    setPreviewTemplate(template);
    setPreviewVisible(true);
  }}
/>

<TemplatePreview
  template={previewTemplate}
  visible={previewVisible}
  onHide={() => setPreviewVisible(false)}
/>
```

### 3. Upload Custom Template

```tsx
const [uploadVisible, setUploadVisible] = useState(false);

<Button onClick={() => setUploadVisible(true)}>
  Upload Template
</Button>

<TemplateUpload
  visible={uploadVisible}
  onHide={() => setUploadVisible(false)}
  onUploadSuccess={() => {
    // Refresh template list
    loadTemplates();
  }}
/>
```

### 4. Manage Templates

```tsx
<TemplateManagement
  onTemplateChange={() => {
    // Refresh template list
    loadTemplates();
  }}
/>
```

## Styling Customization

### Override Template Card Styles

```css
.template-card {
  /* Custom card styling */
}

.template-card-selected {
  /* Selected state styling */
}

.template-preview-image {
  /* Preview image styling */
}
```

### Override Gallery Grid

```css
.template-gallery-grid {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
```

## Error Handling

### Handle API Errors

```tsx
try {
  const response = await api.get('/api/v1/pdf/templates');
  setTemplates(response.data);
} catch (err: any) {
  const errorMessage = err.response?.data?.error?.message || 'Failed to load templates';
  toast.current?.show({
    severity: 'error',
    summary: 'Error',
    detail: errorMessage,
    life: 5000
  });
}
```

### Handle Upload Errors

```tsx
// File type validation
const validTypes = ['application/pdf', 'text/html', 'application/json'];
if (!validTypes.includes(file.type)) {
  setError('Invalid file type');
  return;
}

// File size validation
const maxSize = 10 * 1024 * 1024; // 10MB
if (file.size > maxSize) {
  setError('File size exceeds 10MB limit');
  return;
}
```

## Best Practices

### 1. Template Selection
- Always provide visual feedback for selected template
- Show preview before final selection
- Display template metadata (size, date, type)

### 2. Template Upload
- Validate file type and size before upload
- Provide clear upload guidelines
- Show upload progress
- Handle errors gracefully

### 3. Template Management
- Require confirmation for destructive actions
- Provide search and filter capabilities
- Support bulk operations
- Track template usage

### 4. Performance
- Lazy load templates
- Cache template metadata
- Use pagination for large lists
- Optimize preview generation

### 5. User Experience
- Provide clear navigation
- Show loading states
- Display helpful error messages
- Include contextual help

## Troubleshooting

### Templates Not Loading
```tsx
// Check API connection
const response = await api.get('/health');
console.log('Backend status:', response.data);

// Check authentication
const user = await api.get('/api/v1/auth/me');
console.log('User authenticated:', user.data);
```

### Upload Failing
```tsx
// Check file size
console.log('File size:', file.size / 1024 / 1024, 'MB');

// Check file type
console.log('File type:', file.type);

// Check backend logs
// Look for upload errors in backend console
```

### Preview Not Working
```tsx
// Check if PDF service is available
const response = await api.get('/api/v1/pdf/templates');
console.log('Templates available:', response.data);

// Check if preview endpoint is accessible
const preview = await api.post('/api/v1/pdf/preview', {
  template: 'main',
  project_data: {}
});
```

## Integration Examples

### With Project Management

```tsx
// Generate PDF for specific project
const handleGeneratePDF = async (project: Project, template: PDFTemplate) => {
  try {
    const response = await api.post('/api/v1/pdf/generate', {
      template: template.name,
      project_data: project
    }, {
      responseType: 'blob'
    });
    
    // Download PDF
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${project.name}_${template.name}.pdf`;
    link.click();
  } catch (err) {
    console.error('PDF generation failed:', err);
  }
};
```

### With User Preferences

```tsx
// Save user's preferred template
const savePreferredTemplate = async (template: PDFTemplate) => {
  await api.post('/api/v1/user/preferences', {
    preferred_pdf_template: template.name
  });
};

// Load user's preferred template
const loadPreferredTemplate = async () => {
  const response = await api.get('/api/v1/user/preferences');
  const templateName = response.data.preferred_pdf_template;
  
  if (templateName) {
    const templates = await api.get('/api/v1/pdf/templates');
    const preferred = templates.data.find(t => t.name === templateName);
    setSelectedTemplate(preferred);
  }
};
```

## Additional Resources

- **PrimeReact Documentation:** https://primereact.org/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **PDF Generation Guide:** See Task 41 documentation
- **Template Configuration:** See Task 40 documentation

---

**Last Updated:** 2025-01-19
**Version:** 1.0.0
