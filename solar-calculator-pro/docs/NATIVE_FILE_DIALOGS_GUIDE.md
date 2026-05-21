# Native File Dialogs Guide

Complete guide for using native file dialogs in the Solar Calculator Pro desktop application.

## Overview

The application provides native file dialog integration through Electron, allowing users to select files, save files, and choose directories using the operating system's native dialogs. This provides a familiar and consistent user experience across Windows, macOS, and Linux.

## Features

### Core Capabilities

1. **Single File Selection** - Select one file at a time
2. **Multiple File Selection** - Select multiple files simultaneously
3. **Save File Dialog** - Choose location and name for saving files
4. **Directory Selection** - Select folders/directories
5. **File Type Filters** - Filter by file extensions
6. **Specialized Dialogs** - Pre-configured dialogs for common file types

### Supported File Types

- **Excel Files**: `.xlsx`, `.xls`, `.csv`
- **PDF Files**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`
- **Documents**: `.doc`, `.docx`, `.txt`, `.rtf`
- **Data Files**: `.json`, `.xml`
- **All Files**: `*` (no filter)

## Usage

### Using the React Hook

The `useFileDialog` hook provides the easiest way to work with file dialogs in React components.

```typescript
import { useFileDialog } from '../hooks/useFileDialog';

function MyComponent() {
  const fileDialog = useFileDialog();

  const handleSelectFile = async () => {
    const result = await fileDialog.openFile({
      title: 'Select a File',
      buttonLabel: 'Open',
    });

    if (!result.canceled) {
      console.log('Selected file:', result.filePath);
      console.log('File name:', result.fileName);
    }
  };

  return (
    <button onClick={handleSelectFile} disabled={fileDialog.isOpen}>
      Select File
    </button>
  );
}
```

### Hook API

#### State Properties

- `isOpen: boolean` - Whether a dialog is currently open
- `error: string | null` - Last error message, if any

#### Methods

##### openFile(options?)
Opens a single file selection dialog.

```typescript
const result = await fileDialog.openFile({
  title: 'Select File',
  buttonLabel: 'Open',
  defaultPath: '/path/to/default',
  filters: [
    { name: 'Text Files', extensions: ['txt'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});

// Result: { canceled: boolean, filePath: string | null, fileName?: string }
```

##### openFiles(options?)
Opens a multiple file selection dialog.

```typescript
const result = await fileDialog.openFiles({
  title: 'Select Files',
  buttonLabel: 'Open All',
});

// Result: { canceled: boolean, filePaths: string[], fileNames?: string[], count?: number }
```

##### saveFile(options?)
Opens a save file dialog.

```typescript
const result = await fileDialog.saveFile({
  title: 'Save File',
  buttonLabel: 'Save',
  defaultPath: 'document.txt',
  filters: [
    { name: 'Text Files', extensions: ['txt'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});

// Result: { canceled: boolean, filePath: string | null, fileName?: string }
```

##### openDirectory(options?)
Opens a directory selection dialog.

```typescript
const result = await fileDialog.openDirectory({
  title: 'Select Directory',
  buttonLabel: 'Select',
});

// Result: { canceled: boolean, directoryPath: string | null, directoryName?: string }
```

##### Specialized Methods

Pre-configured dialogs for common file types:

- `openExcelFile(options?)` - Excel file selection
- `openPDFFile(options?)` - PDF file selection
- `openImageFile(options?)` - Single image selection
- `openImageFiles(options?)` - Multiple image selection
- `saveExcelFile(options?)` - Save Excel file
- `savePDFFile(options?)` - Save PDF file
- `saveImageFile(options?)` - Save image file

### Direct Electron API Usage

You can also use the Electron API directly without the React hook:

```typescript
// Single file
const result = await window.electronAPI.selectFile({
  title: 'Select File',
  filters: [
    { name: 'Images', extensions: ['png', 'jpg'] }
  ]
});

// Multiple files
const result = await window.electronAPI.selectFiles({
  title: 'Select Multiple Files'
});

// Save file
const result = await window.electronAPI.saveFile({
  defaultPath: 'export.xlsx',
  filters: [
    { name: 'Excel Files', extensions: ['xlsx'] }
  ]
});

// Directory
const result = await window.electronAPI.selectDirectory({
  title: 'Select Output Directory'
});
```

## Options Reference

### FileDialogOptions

All dialog methods accept an optional `options` object:

```typescript
interface FileDialogOptions {
  title?: string;           // Dialog window title
  buttonLabel?: string;     // Label for the action button
  defaultPath?: string;     // Default path to open
  filters?: FileFilter[];   // File type filters
  properties?: string[];    // Additional properties (advanced)
}

interface FileFilter {
  name: string;             // Filter name (e.g., "Images")
  extensions: string[];     // File extensions (e.g., ["png", "jpg"])
}
```

### Common Options Examples

#### Custom File Filters

```typescript
const result = await fileDialog.openFile({
  title: 'Select Project File',
  filters: [
    { name: 'Project Files', extensions: ['proj', 'project'] },
    { name: 'JSON Files', extensions: ['json'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});
```

#### Default Path

```typescript
const result = await fileDialog.saveFile({
  title: 'Export Data',
  defaultPath: '/Users/username/Documents/export.csv',
  filters: [
    { name: 'CSV Files', extensions: ['csv'] }
  ]
});
```

#### Custom Button Label

```typescript
const result = await fileDialog.openFile({
  title: 'Import Configuration',
  buttonLabel: 'Import',
  filters: [
    { name: 'Config Files', extensions: ['json', 'yaml'] }
  ]
});
```

## Result Objects

### Single File Result

```typescript
interface FileResult {
  canceled: boolean;        // true if user canceled
  filePath: string | null;  // Selected file path
  fileName?: string;        // File name only
}
```

### Multiple Files Result

```typescript
interface FilesResult {
  canceled: boolean;        // true if user canceled
  filePaths: string[];      // Array of selected file paths
  fileNames?: string[];     // Array of file names
  count?: number;           // Number of files selected
}
```

### Directory Result

```typescript
interface DirectoryResult {
  canceled: boolean;            // true if user canceled
  directoryPath: string | null; // Selected directory path
  directoryName?: string;       // Directory name only
}
```

## Examples

### Example 1: Import Excel File

```typescript
const ImportButton = () => {
  const fileDialog = useFileDialog();
  const [data, setData] = useState(null);

  const handleImport = async () => {
    const result = await fileDialog.openExcelFile({
      title: 'Import Price Matrix',
      buttonLabel: 'Import'
    });

    if (!result.canceled && result.filePath) {
      // Read and process the file
      const fileData = await readExcelFile(result.filePath);
      setData(fileData);
    }
  };

  return (
    <button onClick={handleImport} disabled={fileDialog.isOpen}>
      Import Excel
    </button>
  );
};
```

### Example 2: Export PDF

```typescript
const ExportButton = () => {
  const fileDialog = useFileDialog();

  const handleExport = async () => {
    const result = await fileDialog.savePDFFile({
      title: 'Export Report',
      defaultPath: `report-${new Date().toISOString().split('T')[0]}.pdf`,
      buttonLabel: 'Export'
    });

    if (!result.canceled && result.filePath) {
      // Generate and save PDF
      await generatePDF(result.filePath);
      alert(`PDF saved to ${result.fileName}`);
    }
  };

  return <button onClick={handleExport}>Export PDF</button>;
};
```

### Example 3: Select Multiple Images

```typescript
const ImageGallery = () => {
  const fileDialog = useFileDialog();
  const [images, setImages] = useState<string[]>([]);

  const handleSelectImages = async () => {
    const result = await fileDialog.openImageFiles({
      title: 'Select Images for Gallery'
    });

    if (!result.canceled && result.filePaths.length > 0) {
      setImages(result.filePaths);
    }
  };

  return (
    <div>
      <button onClick={handleSelectImages}>
        Add Images ({images.length} selected)
      </button>
      {/* Display images */}
    </div>
  );
};
```

### Example 4: Select Output Directory

```typescript
const ExportSettings = () => {
  const fileDialog = useFileDialog();
  const [outputDir, setOutputDir] = useState<string>('');

  const handleSelectDirectory = async () => {
    const result = await fileDialog.openDirectory({
      title: 'Select Export Directory',
      buttonLabel: 'Select Folder'
    });

    if (!result.canceled && result.directoryPath) {
      setOutputDir(result.directoryPath);
    }
  };

  return (
    <div>
      <label>Export Directory:</label>
      <input type="text" value={outputDir} readOnly />
      <button onClick={handleSelectDirectory}>Browse...</button>
    </div>
  );
};
```

### Example 5: Custom File Type Filter

```typescript
const ProjectLoader = () => {
  const fileDialog = useFileDialog();

  const handleLoadProject = async () => {
    const result = await fileDialog.openFile({
      title: 'Open Solar Project',
      buttonLabel: 'Open Project',
      filters: [
        { name: 'Solar Projects', extensions: ['solar', 'solarproj'] },
        { name: 'JSON Projects', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled && result.filePath) {
      // Load project
      await loadProject(result.filePath);
    }
  };

  return <button onClick={handleLoadProject}>Open Project</button>;
};
```

## Error Handling

The hook automatically handles errors and provides error state:

```typescript
const MyComponent = () => {
  const fileDialog = useFileDialog();

  useEffect(() => {
    if (fileDialog.error) {
      console.error('File dialog error:', fileDialog.error);
      // Show error to user
      alert(`Error: ${fileDialog.error}`);
    }
  }, [fileDialog.error]);

  // ... rest of component
};
```

## Best Practices

### 1. Disable UI During Dialog

Always disable buttons while a dialog is open:

```typescript
<button onClick={handleOpen} disabled={fileDialog.isOpen}>
  Select File
</button>
```

### 2. Check for Cancellation

Always check if the user canceled before processing:

```typescript
const result = await fileDialog.openFile();
if (!result.canceled && result.filePath) {
  // Process file
}
```

### 3. Provide Clear Titles

Use descriptive titles that explain what the user is selecting:

```typescript
await fileDialog.openFile({
  title: 'Select Price Matrix Excel File',
  buttonLabel: 'Import Matrix'
});
```

### 4. Use Appropriate Filters

Limit file types to what your feature actually supports:

```typescript
await fileDialog.openFile({
  filters: [
    { name: 'Supported Files', extensions: ['xlsx', 'csv'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});
```

### 5. Set Sensible Defaults

Provide default paths and filenames when appropriate:

```typescript
await fileDialog.saveFile({
  defaultPath: `export-${Date.now()}.xlsx`,
  filters: [{ name: 'Excel Files', extensions: ['xlsx'] }]
});
```

## Platform Differences

### Windows
- Uses standard Windows file dialogs
- Supports all features
- File paths use backslashes (`\`)

### macOS
- Uses native macOS file panels
- Supports all features
- File paths use forward slashes (`/`)
- May show additional macOS-specific options

### Linux
- Uses GTK file chooser dialogs
- Supports all features
- File paths use forward slashes (`/`)
- Appearance depends on desktop environment

## Troubleshooting

### Dialog Not Opening

If dialogs don't open:
1. Check that you're running in Electron (not browser)
2. Verify `window.electronAPI` is available
3. Check browser console for errors

### File Path Issues

If file paths aren't working:
1. Use `path.normalize()` for cross-platform compatibility
2. Check file permissions
3. Verify the path exists before reading

### Multiple Dialogs

Only one dialog can be open at a time. The hook's `isOpen` state helps manage this.

## See Also

- [Electron Dialog Documentation](https://www.electronjs.org/docs/latest/api/dialog)
- [File System Integration Guide](./FILE_SYSTEM_GUIDE.md)
- [Backend Manager Guide](./BACKEND_MANAGER_GUIDE.md)

## Support

For issues or questions:
- Check the demo component: `frontend/src/examples/FileDialogDemo.tsx`
- Review the hook implementation: `frontend/src/hooks/useFileDialog.ts`
- See Electron main process: `electron/main.js`
