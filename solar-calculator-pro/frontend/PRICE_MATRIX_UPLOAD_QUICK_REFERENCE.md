# Price Matrix Upload - Quick Reference

## 🚀 Quick Start

```typescript
import MatrixUpload from '../components/pricing/MatrixUpload';

<MatrixUpload 
  onUploadSuccess={(data) => console.log(data)}
  onUploadError={(error) => console.error(error)}
/>
```

## 📁 Supported Formats

| Format | Extension | MIME Type |
|--------|-----------|-----------|
| Excel | `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| Excel (Legacy) | `.xls` | `application/vnd.ms-excel` |
| CSV | `.csv` | `text/csv` |
| JSON | `.json` | `application/json` |

**Max Size:** 10MB

## 📊 Expected File Structure

```
     A          B           C           D        ...    XX
1  [empty]  Battery1    Battery2    Battery3   ...  kein Speicher
2    10      5.000€      6.500€      7.200€    ...    4.500€
3    15      6.200€      7.800€      8.500€    ...    5.800€
4    20      7.400€      9.100€      9.800€    ...    7.100€
...
200  500     45.000€     52.000€     58.000€   ...    42.000€
```

- **Column A:** PV Module Count (10, 15, 20, ...)
- **Row 1:** Battery Storage Models
- **Last Column:** "kein Speicher" (No Storage)
- **Cells:** Turnkey system prices in Euro

## 🔌 API Endpoints

### Upload
```
POST /api/v1/pricing/matrix/upload
Content-Type: multipart/form-data

FormData:
  - file: File
  - matrix_type: 'price_matrix'
```

### Download Template
```
GET /api/v1/pricing/matrix/template
```

## ✅ Validation Rules

```typescript
// File Type
allowedTypes = [
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/csv',
  'application/json'
];

// File Size
maxFileSize = 10 * 1024 * 1024; // 10MB

// Extensions
validExtensions = ['xlsx', 'xls', 'csv', 'json'];
```

## 🎨 CSS Classes

```css
.matrix-upload              /* Main container */
.upload-card                /* Card wrapper */
.upload-area                /* Upload zone */
.empty-template             /* Drag-drop area */
.upload-progress            /* Progress bar */
.upload-message             /* Feedback messages */
.format-help                /* Help section */
```

## 🌐 Internationalization

### German Messages

```typescript
const messages = {
  invalidType: 'Ungültiger Dateityp. Bitte laden Sie eine Excel (.xlsx, .xls), CSV oder JSON Datei hoch.',
  fileTooLarge: 'Datei ist zu groß. Maximale Größe: 10MB',
  invalidExtension: 'Ungültige Dateierweiterung. Erlaubt: .xlsx, .xls, .csv, .json',
  uploadFailed: 'Upload fehlgeschlagen',
  uploadSuccess: 'Datei wurde erfolgreich hochgeladen',
  validationError: 'Validierungsfehler'
};
```

## 🎯 Component Props

```typescript
interface MatrixUploadProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: string) => void;
}
```

## 📱 Responsive Breakpoints

```css
/* Desktop */
@media (min-width: 769px) { }

/* Mobile */
@media (max-width: 768px) { }
```

## 🌙 Dark Mode

```css
@media (prefers-color-scheme: dark) {
  /* Automatic dark mode styles */
}
```

## ⚡ Performance Tips

1. **Validate client-side first** - Prevents unnecessary uploads
2. **Show progress** - Better UX for large files
3. **Handle errors gracefully** - Clear error messages
4. **Use FormData** - Efficient file upload

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Upload rejected | Check file type and size |
| No progress | Check network connection |
| Server error | Check backend logs |
| Validation fails | Download template and compare |

## 🧪 Testing

```typescript
// Validate file
const validation = validateFile(file);
expect(validation.valid).toBe(true);

// Mock upload
const mockFile = new File(['content'], 'test.xlsx', {
  type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
});
```

## 📦 Dependencies

```json
{
  "primereact": "^10.0.0",
  "primeicons": "^6.0.0",
  "axios": "^1.6.0"
}
```

## 🔗 Related Components

- `PriceMatrix` - Main page
- `MatrixPreview` - Preview uploaded matrix
- `MatrixManagement` - Manage matrices
- `PriceCalculation` - Calculate prices

## 📚 Documentation

- [Full User Guide](./PRICE_MATRIX_UPLOAD_GUIDE.md)
- [API Documentation](../../backend/docs/PRICING_SERVICE_GUIDE.md)
- [Design Specification](../../.kiro/specs/streamlit-to-electron-migration/design.md)

## 🎓 Examples

### Basic Usage
```typescript
<MatrixUpload />
```

### With Callbacks
```typescript
<MatrixUpload 
  onUploadSuccess={(data) => {
    console.log('Success:', data);
    navigate('/price-matrix/management');
  }}
  onUploadError={(error) => {
    console.error('Error:', error);
    showErrorDialog(error);
  }}
/>
```

### In Tab View
```typescript
<TabView>
  <TabPanel header="Upload">
    <MatrixUpload onUploadSuccess={handleSuccess} />
  </TabPanel>
</TabView>
```

## 🔐 Security

- ✅ File type validation
- ✅ File size limits
- ✅ Extension validation
- ✅ Server-side validation
- ✅ CSRF protection
- ✅ Secure file storage

## ♿ Accessibility

- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ ARIA labels
- ✅ Focus management
- ✅ Error announcements

## 📊 Metrics

- Upload success rate
- Average upload time
- File size distribution
- Error frequency
- User engagement

## 🚦 Status Indicators

| State | Icon | Color |
|-------|------|-------|
| Idle | 📤 | Blue |
| Uploading | ⏳ | Purple |
| Success | ✅ | Green |
| Error | ❌ | Red |
| Warning | ⚠️ | Yellow |

## 🎨 Theme Colors

```css
--primary: #6366f1;
--success: #10b981;
--error: #ef4444;
--warning: #f59e0b;
--info: #3b82f6;
```

## 📞 Support

- 📧 Email: support@solarcalculator.pro
- 📖 Docs: /docs/price-matrix-upload
- 🐛 Issues: /issues/new
- 💬 Chat: /support/chat
