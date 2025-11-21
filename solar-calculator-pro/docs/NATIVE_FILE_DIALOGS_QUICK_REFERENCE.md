# Native File Dialogs - Quick Reference

Quick reference for native file dialog operations.

## Import

```typescript
import { useFileDialog } from '../hooks/useFileDialog';
```

## Basic Usage

```typescript
const fileDialog = useFileDialog();

// Single file
const result = await fileDialog.openFile();

// Multiple files
const result = await fileDialog.openFiles();

// Save file
const result = await fileDialog.saveFile();

// Directory
const result = await fileDialog.openDirectory();
```

## Hook API

### State
- `isOpen: boolean` - Dialog is currently open
- `error: string | null` - Last error message

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `openFile(options?)` | Select single file | `FileResult` |
| `openFiles(options?)` | Select multiple files | `FilesResult` |
| `saveFile(options?)` | Save file dialog | `FileResult` |
| `openDirectory(options?)` | Select directory | `DirectoryResult` |
| `openExcelFile(options?)` | Select Excel file | `FileResult` |
| `openPDFFile(options?)` | Select PDF file | `FileResult` |
| `openImageFile(options?)` | Select image file | `FileResult` |
| `openImageFiles(options?)` | Select multiple images | `FilesResult` |
| `saveExcelFile(options?)` | Save Excel file | `FileResult` |
| `savePDFFile(options?)` | Save PDF file | `FileResult` |
| `saveImageFile(options?)` | Save image file | `FileResult` |

## Options

```typescript
interface FileDialogOptions {
  title?: string;           // Dialog title
  buttonLabel?: string;     // Button text
  defaultPath?: string;     // Default path
  filters?: FileFilter[];   // File type filters
}

interface FileFilter {
  name: string;             // Filter name
  extensions: string[];     // Extensions (without dots)
}
```

## Results

```typescript
// Single file
interface FileResult {
  canceled: boolean;
  filePath: string | null;
  fileName?: string;
}

// Multiple files
interface FilesResult {
  canceled: boolean;
  filePaths: string[];
  fileNames?: string[];
  count?: number;
}

// Directory
interface DirectoryResult {
  canceled: boolean;
  directoryPath: string | null;
  directoryName?: string;
}
```

## Common Patterns

### Select File with Custom Filter

```typescript
const result = await fileDialog.openFile({
  title: 'Select Configuration',
  filters: [
    { name: 'Config Files', extensions: ['json', 'yaml'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});

if (!result.canceled) {
  console.log('Selected:', result.filePath);
}
```

### Save File with Default Name

```typescript
const result = await fileDialog.saveFile({
  title: 'Export Data',
  defaultPath: 'export.csv',
  filters: [
    { name: 'CSV Files', extensions: ['csv'] }
  ]
});
```

### Select Multiple Images

```typescript
const result = await fileDialog.openImageFiles({
  title: 'Select Photos'
});

if (!result.canceled) {
  console.log(`Selected ${result.count} images`);
  result.filePaths.forEach(path => {
    // Process each image
  });
}
```

### Select Directory for Export

```typescript
const result = await fileDialog.openDirectory({
  title: 'Select Export Folder',
  buttonLabel: 'Export Here'
});

if (!result.canceled) {
  await exportToDirectory(result.directoryPath);
}
```

## File Type Filters

### Pre-defined Filters

```typescript
// Excel
{ name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] }

// PDF
{ name: 'PDF Files', extensions: ['pdf'] }

// Images
{ name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'] }

// Documents
{ name: 'Documents', extensions: ['doc', 'docx', 'txt', 'rtf'] }

// Data
{ name: 'JSON Files', extensions: ['json'] }
{ name: 'XML Files', extensions: ['xml'] }

// All files
{ name: 'All Files', extensions: ['*'] }
```

## Direct Electron API

```typescript
// Without React hook
const result = await window.electronAPI.selectFile(options);
const result = await window.electronAPI.selectFiles(options);
const result = await window.electronAPI.saveFile(options);
const result = await window.electronAPI.selectDirectory(options);

// Specialized
const result = await window.electronAPI.selectExcelFile(options);
const result = await window.electronAPI.selectPDFFile(options);
const result = await window.electronAPI.selectImageFile(options);
const result = await window.electronAPI.selectImageFiles(options);
const result = await window.electronAPI.saveExcelFile(options);
const result = await window.electronAPI.savePDFFile(options);
const result = await window.electronAPI.saveImageFile(options);
```

## Error Handling

```typescript
const fileDialog = useFileDialog();

// Check error state
if (fileDialog.error) {
  console.error('Error:', fileDialog.error);
}

// Check cancellation
const result = await fileDialog.openFile();
if (result.canceled) {
  console.log('User canceled');
  return;
}

// Process file
if (result.filePath) {
  await processFile(result.filePath);
}
```

## Best Practices

✅ **DO:**
- Disable UI while dialog is open
- Check for cancellation before processing
- Use descriptive titles and button labels
- Provide appropriate file filters
- Set sensible default paths

❌ **DON'T:**
- Open multiple dialogs simultaneously
- Assume user will select a file
- Use generic titles like "Select File"
- Allow all file types when specific types are needed
- Forget to handle errors

## Example Component

```typescript
import React from 'react';
import { useFileDialog } from '../hooks/useFileDialog';

export const FileSelector: React.FC = () => {
  const fileDialog = useFileDialog();
  const [selectedFile, setSelectedFile] = React.useState<string>('');

  const handleSelect = async () => {
    const result = await fileDialog.openFile({
      title: 'Select File',
      filters: [
        { name: 'Text Files', extensions: ['txt'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled && result.filePath) {
      setSelectedFile(result.filePath);
    }
  };

  return (
    <div>
      <button 
        onClick={handleSelect} 
        disabled={fileDialog.isOpen}
      >
        Select File
      </button>
      {selectedFile && <p>Selected: {selectedFile}</p>}
      {fileDialog.error && <p>Error: {fileDialog.error}</p>}
    </div>
  );
};
```

## See Also

- [Complete Guide](./NATIVE_FILE_DIALOGS_GUIDE.md)
- [Demo Component](../frontend/src/examples/FileDialogDemo.tsx)
- [Hook Implementation](../frontend/src/hooks/useFileDialog.ts)
