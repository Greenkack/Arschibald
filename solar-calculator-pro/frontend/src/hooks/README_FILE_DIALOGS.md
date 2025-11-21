# Native File Dialogs Hook

## Quick Start

```typescript
import { useFileDialog } from './useFileDialog';

function MyComponent() {
  const fileDialog = useFileDialog();

  const handleSelect = async () => {
    const result = await fileDialog.openFile();
    if (!result.canceled) {
      console.log('Selected:', result.filePath);
    }
  };

  return (
    <button onClick={handleSelect} disabled={fileDialog.isOpen}>
      Select File
    </button>
  );
}
```

## Available Methods

- `openFile(options?)` - Select single file
- `openFiles(options?)` - Select multiple files
- `saveFile(options?)` - Save file dialog
- `openDirectory(options?)` - Select directory
- `openExcelFile(options?)` - Select Excel file
- `openPDFFile(options?)` - Select PDF file
- `openImageFile(options?)` - Select image file
- `openImageFiles(options?)` - Select multiple images
- `saveExcelFile(options?)` - Save Excel file
- `savePDFFile(options?)` - Save PDF file
- `saveImageFile(options?)` - Save image file

## State

- `isOpen: boolean` - Dialog is currently open
- `error: string | null` - Last error message

## Documentation

See complete documentation:
- [Complete Guide](../../../docs/NATIVE_FILE_DIALOGS_GUIDE.md)
- [Quick Reference](../../../docs/NATIVE_FILE_DIALOGS_QUICK_REFERENCE.md)
- [Demo Component](../examples/FileDialogDemo.tsx)
