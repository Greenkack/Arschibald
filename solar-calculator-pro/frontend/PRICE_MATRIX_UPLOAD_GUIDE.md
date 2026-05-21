# Price Matrix Upload Interface - User Guide

## Overview

The Price Matrix Upload Interface provides a modern, user-friendly way to upload and manage price matrices for PV systems and battery storage. It features drag-and-drop functionality, real-time validation, progress tracking, and comprehensive error handling.

## Features

### ✅ Implemented Features

1. **Drag-and-Drop Upload**
   - Intuitive drag-and-drop interface
   - Click to select file alternative
   - Visual feedback during drag operations

2. **File Validation**
   - Supported formats: Excel (.xlsx, .xls), CSV, JSON
   - Maximum file size: 10MB
   - File type and extension validation
   - Real-time validation feedback

3. **Upload Progress Tracking**
   - Real-time progress bar
   - Percentage indicator
   - File name display
   - Animated loading states

4. **Success/Error Feedback**
   - Toast notifications for all operations
   - Inline success messages
   - Detailed error messages
   - Visual animations for feedback

5. **Format Help**
   - Expected file format documentation
   - Example template download
   - Clear instructions for users

## Usage

### Basic Upload Flow

1. **Navigate to Price Matrix Page**
   ```
   Dashboard → Price Matrix → Upload Tab
   ```

2. **Select File**
   - Drag and drop a file onto the upload area, OR
   - Click "Datei auswählen" to browse for a file

3. **Validation**
   - File is automatically validated
   - Invalid files are rejected with clear error messages

4. **Upload**
   - Click "Hochladen" button
   - Watch progress bar for upload status
   - Receive success confirmation

5. **View Results**
   - Automatically switches to Management tab on success
   - View uploaded matrix details

### Supported File Formats

#### Excel Files (.xlsx, .xls)
```
Expected Structure:
- Column A (A2:A200): PV Module Count (10, 15, 20, ...)
- Row 1 (B1:XX1): Battery Storage Models
- Last Column: "kein Speicher" (No Storage)
- Cells: Turnkey system prices in Euro
```

#### CSV Files (.csv)
```
Same structure as Excel, comma-separated values
First row: headers
First column: module counts
```

#### JSON Files (.json)
```json
{
  "matrix_type": "price_matrix",
  "rows": [...],
  "columns": [...],
  "data": [[...]]
}
```

## Component API

### MatrixUpload Component

```typescript
interface MatrixUploadProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: string) => void;
}
```

#### Props

- **onUploadSuccess** (optional)
  - Callback function called when upload succeeds
  - Receives uploaded data as parameter
  - Use to update parent component state

- **onUploadError** (optional)
  - Callback function called when upload fails
  - Receives error message as parameter
  - Use for custom error handling

#### Example Usage

```typescript
import MatrixUpload from '../components/pricing/MatrixUpload';

const MyComponent = () => {
  const handleSuccess = (data) => {
    console.log('Upload successful:', data);
    // Update state, navigate, etc.
  };

  const handleError = (error) => {
    console.error('Upload failed:', error);
    // Show custom error UI
  };

  return (
    <MatrixUpload 
      onUploadSuccess={handleSuccess}
      onUploadError={handleError}
    />
  );
};
```

## Validation Rules

### File Type Validation

✅ **Allowed Types:**
- `application/vnd.ms-excel` (Excel .xls)
- `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel .xlsx)
- `text/csv` (CSV)
- `application/json` (JSON)

❌ **Rejected Types:**
- All other file types

### File Size Validation

- **Maximum Size:** 10MB (10,485,760 bytes)
- Files larger than 10MB are rejected

### File Extension Validation

✅ **Allowed Extensions:**
- `.xlsx`
- `.xls`
- `.csv`
- `.json`

❌ **Rejected Extensions:**
- All other extensions

## Error Messages

### German Error Messages

| Error Type | Message |
|------------|---------|
| Invalid Type | "Ungültiger Dateityp. Bitte laden Sie eine Excel (.xlsx, .xls), CSV oder JSON Datei hoch." |
| File Too Large | "Datei ist zu groß. Maximale Größe: 10MB" |
| Invalid Extension | "Ungültige Dateierweiterung. Erlaubt: .xlsx, .xls, .csv, .json" |
| Upload Failed | "Upload fehlgeschlagen" (+ server error details) |
| Validation Error | "Validierungsfehler" (+ specific validation issue) |

## API Integration

### Upload Endpoint

```
POST /api/v1/pricing/matrix/upload
```

#### Request

```typescript
FormData {
  file: File,
  matrix_type: 'price_matrix'
}
```

#### Response (Success)

```json
{
  "success": true,
  "data": {
    "id": 123,
    "fileName": "price_matrix.xlsx",
    "uploadedAt": "2024-01-15T10:30:00Z",
    "rows": 200,
    "columns": 50,
    "matrixType": "price_matrix"
  }
}
```

#### Response (Error)

```json
{
  "error": {
    "message": "Invalid matrix structure",
    "details": {
      "missingColumns": ["kein Speicher"],
      "invalidRows": [5, 10, 15]
    }
  }
}
```

### Template Download Endpoint

```
GET /api/v1/pricing/matrix/template
```

Returns an Excel template file with the correct structure.

## Styling

### CSS Classes

- `.matrix-upload` - Main container
- `.upload-card` - Card wrapper
- `.upload-area` - File upload area
- `.empty-template` - Drag-and-drop zone
- `.upload-progress` - Progress indicator
- `.upload-message` - Success/error messages
- `.format-help` - Help section

### Customization

Override styles in your own CSS:

```css
.matrix-upload .upload-card {
  /* Custom card styles */
}

.matrix-upload .empty-template {
  /* Custom drag-drop zone styles */
}
```

## Accessibility

### Keyboard Navigation

- **Tab:** Navigate between buttons
- **Enter/Space:** Activate buttons
- **Escape:** Cancel upload (when in progress)

### Screen Reader Support

- All buttons have descriptive labels
- Progress updates are announced
- Error messages are announced
- Success messages are announced

### ARIA Labels

```html
<FileUpload 
  aria-label="Preismatrix-Datei hochladen"
  aria-describedby="upload-instructions"
/>
```

## Responsive Design

### Breakpoints

- **Desktop:** > 768px
  - Full-width layout
  - Large drag-drop zone
  - Side-by-side buttons

- **Mobile:** ≤ 768px
  - Stacked layout
  - Compact drag-drop zone
  - Stacked buttons

### Mobile Optimizations

- Touch-friendly button sizes
- Simplified layout
- Reduced padding
- Optimized font sizes

## Dark Mode Support

The component automatically adapts to system dark mode preferences:

```css
@media (prefers-color-scheme: dark) {
  /* Dark mode styles */
}
```

### Dark Mode Colors

- Background: `#1e293b`
- Surface: `#0f172a`
- Text: `#e2e8f0`
- Border: `#334155`
- Primary: `#6366f1`

## Performance

### Optimizations

1. **File Validation**
   - Client-side validation before upload
   - Prevents unnecessary server requests

2. **Progress Tracking**
   - Real-time progress updates
   - Smooth animations

3. **Memory Management**
   - Files are not loaded into memory
   - Direct FormData upload

4. **Error Handling**
   - Graceful error recovery
   - Clear error messages

### Best Practices

- Validate files before upload
- Show progress for large files
- Provide clear feedback
- Handle errors gracefully

## Troubleshooting

### Common Issues

#### Upload Fails Immediately

**Problem:** File is rejected before upload starts

**Solution:**
1. Check file type (must be .xlsx, .xls, .csv, or .json)
2. Check file size (must be < 10MB)
3. Check file extension

#### Upload Stalls at 0%

**Problem:** Upload doesn't start

**Solution:**
1. Check network connection
2. Check backend server is running
3. Check API endpoint is correct

#### Upload Fails at 100%

**Problem:** Upload completes but server rejects file

**Solution:**
1. Check file structure matches expected format
2. Check server logs for validation errors
3. Download template and compare structure

#### No Progress Updates

**Problem:** Progress bar doesn't update

**Solution:**
1. Check browser supports progress events
2. Check network speed (very fast uploads may not show progress)
3. Check console for errors

## Testing

### Manual Testing Checklist

- [ ] Upload valid Excel file
- [ ] Upload valid CSV file
- [ ] Upload valid JSON file
- [ ] Upload invalid file type
- [ ] Upload file > 10MB
- [ ] Upload file with wrong extension
- [ ] Drag and drop file
- [ ] Click to select file
- [ ] Cancel upload mid-progress
- [ ] Upload multiple files sequentially
- [ ] Test on mobile device
- [ ] Test in dark mode
- [ ] Test with screen reader

### Automated Testing

```typescript
// Example test
describe('MatrixUpload', () => {
  it('should validate file type', () => {
    const invalidFile = new File(['content'], 'test.txt', { 
      type: 'text/plain' 
    });
    const validation = validateFile(invalidFile);
    expect(validation.valid).toBe(false);
    expect(validation.error).toContain('Ungültiger Dateityp');
  });
});
```

## Future Enhancements

### Planned Features

1. **Batch Upload**
   - Upload multiple matrices at once
   - Queue management
   - Parallel uploads

2. **Matrix Preview**
   - Preview matrix before upload
   - Edit matrix inline
   - Validate data before saving

3. **Version Control**
   - Track matrix versions
   - Compare versions
   - Rollback to previous versions

4. **Advanced Validation**
   - Custom validation rules
   - Business logic validation
   - Data consistency checks

5. **Import History**
   - View upload history
   - Re-upload previous files
   - Export audit logs

## Support

### Getting Help

- Check this documentation first
- Review error messages carefully
- Check browser console for errors
- Contact support with:
  - Error message
  - File type and size
  - Browser and OS version
  - Steps to reproduce

### Reporting Issues

Include:
1. Description of the problem
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Screenshots (if applicable)
6. Browser and OS information

## Changelog

### Version 1.0.0 (Current)

- ✅ Initial implementation
- ✅ Drag-and-drop upload
- ✅ File validation
- ✅ Progress tracking
- ✅ Success/error feedback
- ✅ Format help
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Accessibility features

## License

Copyright © 2024 Solar Calculator Pro
All rights reserved.
