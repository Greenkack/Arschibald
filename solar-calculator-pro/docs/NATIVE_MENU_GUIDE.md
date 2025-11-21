# Native Menu Implementation Guide

## Overview

The Solar Calculator Pro application features a comprehensive native menu system that provides full keyboard shortcut support, context menus, recent files management, and dynamic menu state management.

## Features

### 1. Application Menu

The application menu provides access to all major features through a hierarchical menu structure:

#### File Menu
- **New Project** (`Ctrl/Cmd+N`): Create a new project
- **Open Project** (`Ctrl/Cmd+O`): Open an existing project with file dialog
- **Save Project** (`Ctrl/Cmd+S`): Save the current project
- **Save As** (`Ctrl/Cmd+Shift+S`): Save project with a new name
- **Save All** (`Ctrl/Cmd+Alt+S`): Save all open projects
- **Close Project** (`Ctrl/Cmd+W`): Close the current project
- **Import**: Submenu for importing various file types
  - Import Excel (`Ctrl/Cmd+Shift+I`)
  - Import CSV
  - Import Price Matrix
  - Import Product Database
- **Export**: Submenu for exporting data
  - Export PDF (`Ctrl/Cmd+P`)
  - Export Excel (`Ctrl/Cmd+E`)
  - Export 3D Model (STL, OBJ, GLTF)
  - Export Report
- **Recent Projects**: Dynamic list of recently opened projects (up to 10)
- **Recent Files**: Dynamic list of recently opened files (up to 10)
- **Page Setup**: Configure page settings for printing
- **Print** (`Ctrl/Cmd+Shift+P`): Print current view

#### Edit Menu
- **Undo** (`Ctrl/Cmd+Z`): Undo last action
- **Redo** (`Ctrl/Cmd+Shift+Z` or `Ctrl+Y`): Redo last undone action
- **Cut** (`Ctrl/Cmd+X`): Cut selected text
- **Copy** (`Ctrl/Cmd+C`): Copy selected text
- **Paste** (`Ctrl/Cmd+V`): Paste from clipboard
- **Delete**: Delete selected content
- **Select All** (`Ctrl/Cmd+A`): Select all content
- **Find** (`Ctrl/Cmd+F`): Open find dialog
- **Find Next** (`Cmd+G` or `F3`): Find next occurrence
- **Find Previous** (`Cmd+Shift+G` or `Shift+F3`): Find previous occurrence
- **Replace** (`Ctrl/Cmd+H`): Open find and replace dialog
- **Preferences** (`Ctrl/Cmd+,`): Open application preferences

#### View Menu
- **Dashboard** (`Ctrl/Cmd+1`): Navigate to dashboard
- **Solar Calculator** (`Ctrl/Cmd+2`): Navigate to solar calculator
- **Heat Pump** (`Ctrl/Cmd+3`): Navigate to heat pump calculator
- **Combined System** (`Ctrl/Cmd+4`): Navigate to combined system
- **CRM** (`Ctrl/Cmd+5`): Navigate to CRM
- **Products** (`Ctrl/Cmd+6`): Navigate to products
- **Price Matrix** (`Ctrl/Cmd+7`): Navigate to price matrix
- **PDF Generation** (`Ctrl/Cmd+8`): Navigate to PDF generation
- **3D Visualization** (`Ctrl/Cmd+9`): Navigate to 3D visualization
- **Go Back** (`Ctrl/Cmd+[`): Navigate back in history
- **Go Forward** (`Ctrl/Cmd+]`): Navigate forward in history
- **Reload** (`Ctrl/Cmd+R`): Reload current page
- **Force Reload** (`Ctrl/Cmd+Shift+R`): Force reload bypassing cache
- **Toggle Developer Tools** (`Alt+Cmd+I` or `Ctrl+Shift+I`): Open DevTools
- **Actual Size** (`Ctrl/Cmd+0`): Reset zoom to 100%
- **Zoom In** (`Ctrl/Cmd+Plus`): Increase zoom level
- **Zoom Out** (`Ctrl/Cmd+-`): Decrease zoom level
- **Toggle Full Screen** (`Ctrl+Cmd+F` or `F11`): Toggle fullscreen mode
- **Toggle Sidebar** (`Ctrl/Cmd+B`): Show/hide sidebar
- **Toggle Theme** (`Ctrl/Cmd+T`): Switch between light/dark theme

#### Window Menu
- **Minimize** (`Ctrl/Cmd+M`): Minimize window
- **Zoom**: Zoom window (macOS)
- **Close** (`Alt+F4` on Windows): Close window
- **Always on Top**: Keep window always on top (checkbox)

#### Help Menu
- **Documentation** (`F1`): Open online documentation
- **Getting Started Guide**: Open getting started guide
- **Video Tutorials**: Open video tutorials
- **Keyboard Shortcuts** (`Ctrl/Cmd+/`): Show keyboard shortcuts dialog
- **Search Help** (`Ctrl/Cmd+Shift+H`): Search help content
- **FAQ**: Open frequently asked questions
- **Report Issue**: Open issue tracker
- **Send Feedback**: Send feedback to developers
- **Check for Updates**: Check for application updates
- **Release Notes**: View release notes
- **View License**: View software license
- **Privacy Policy**: View privacy policy
- **About**: Show about dialog

### 2. Context Menus

Context menus appear on right-click and adapt to the context:

#### Text Input Context Menu
- Undo (if available)
- Redo (if available)
- Cut (if text selected)
- Copy (if text selected)
- Paste (if clipboard has content)
- Delete (if text selected)
- Select All

#### Link Context Menu
- Open Link
- Copy Link Address

#### Image Context Menu
- Copy Image
- Copy Image Address
- Save Image As...
- Open Image in Browser

#### Default Context Menu
- Copy (if text selected)
- Select All
- Reload
- Toggle Developer Tools

### 3. Recent Files Management

The menu system maintains lists of recently opened projects and files:

- **Maximum Items**: 10 items per list (configurable)
- **Persistence**: Recent items are saved to disk using electron-store
- **Quick Access**: Recent projects have keyboard shortcuts (Ctrl/Cmd+Alt+1-9)
- **Clear Options**: Both lists can be cleared from their respective menus

### 4. Keyboard Shortcuts

All keyboard shortcuts are documented and accessible via the Help menu. The shortcuts are platform-aware (Cmd on macOS, Ctrl on Windows/Linux).

## Usage

### From Frontend (React)

#### Listen for Menu Actions

```typescript
import { useEffect } from 'react';

function MyComponent() {
  useEffect(() => {
    // Listen for navigation events from menu
    const unsubscribeNav = window.electronAPI.onNavigate((route) => {
      console.log('Navigate to:', route);
      // Handle navigation
    });

    // Listen for action events from menu
    const unsubscribeAction = window.electronAPI.onAction((action, data) => {
      console.log('Action:', action, data);
      
      switch (action) {
        case 'new-project':
          handleNewProject();
          break;
        case 'save-project':
          handleSaveProject();
          break;
        case 'export-pdf':
          handleExportPDF();
          break;
        // ... handle other actions
      }
    });

    return () => {
      unsubscribeNav();
      unsubscribeAction();
    };
  }, []);

  return <div>My Component</div>;
}
```

#### Add Recent Items

```typescript
// Add a recently opened project
await window.electronAPI.addRecentProject(
  '/path/to/project.json',
  'My Project'
);

// Add a recently opened file
await window.electronAPI.addRecentFile(
  '/path/to/file.xlsx',
  'data.xlsx'
);
```

#### Get Keyboard Shortcuts

```typescript
const shortcuts = await window.electronAPI.getKeyboardShortcuts();
console.log(shortcuts);
// Returns:
// {
//   'File Operations': [
//     { action: 'New Project', shortcut: 'Ctrl+N' },
//     ...
//   ],
//   'Edit Operations': [...],
//   ...
// }
```

#### Clear Recent Lists

```typescript
// Clear recent projects
await window.electronAPI.clearRecentProjects();

// Clear recent files
await window.electronAPI.clearRecentFiles();
```

### From Main Process

#### Update Menu State

```javascript
const { updateMenu, menuState } = require('./menu');

// Add recent project
menuState.addRecentProject('/path/to/project.json', 'My Project');
updateMenu(mainWindow);

// Add recent file
menuState.addRecentFile('/path/to/file.xlsx', 'data.xlsx');
updateMenu(mainWindow);
```

#### Setup Context Menu

```javascript
const { setupContextMenu } = require('./menu');

// Setup context menu for a window
setupContextMenu(mainWindow);
```

## Menu State Persistence

The menu state (recent projects and files) is automatically persisted using `electron-store`:

- **Storage Location**: 
  - Windows: `%APPDATA%\solar-calculator-pro\menu-state.json`
  - macOS: `~/Library/Application Support/solar-calculator-pro/menu-state.json`
  - Linux: `~/.config/solar-calculator-pro/menu-state.json`

- **Storage Format**:
```json
{
  "recentProjects": [
    {
      "path": "/path/to/project.json",
      "name": "My Project",
      "timestamp": 1234567890
    }
  ],
  "recentFiles": [
    {
      "path": "/path/to/file.xlsx",
      "name": "data.xlsx",
      "timestamp": 1234567890
    }
  ],
  "maxRecentItems": 10
}
```

## Customization

### Changing Maximum Recent Items

```javascript
const Store = require('electron-store');
const store = new Store({ name: 'menu-state' });

// Set maximum recent items
store.set('maxRecentItems', 15);
```

### Adding Custom Menu Items

To add custom menu items, modify the `createApplicationMenu` function in `electron/menu.js`:

```javascript
// Add to File menu
{
  label: 'My Custom Action',
  accelerator: 'CmdOrCtrl+Shift+X',
  click: () => {
    mainWindow.webContents.send('action', 'my-custom-action');
  }
}
```

### Adding Custom Context Menu Items

Modify the `setupContextMenu` function to add custom context menu items:

```javascript
mainWindow.webContents.on('context-menu', (event, params) => {
  // Add custom logic based on params
  if (params.myCustomCondition) {
    const customMenu = Menu.buildFromTemplate([
      {
        label: 'Custom Action',
        click: () => {
          // Handle custom action
        }
      }
    ]);
    customMenu.popup();
  }
});
```

## Platform Differences

### macOS
- Uses `Cmd` key instead of `Ctrl`
- Has an application menu (first menu with app name)
- Has "Services" submenu
- Has "Speech" submenu in Edit menu
- Uses `Cmd+Shift+Z` for Redo

### Windows/Linux
- Uses `Ctrl` key
- Uses `Ctrl+Y` for Redo
- Uses `Alt+F4` to close window
- No application menu or services menu

## Best Practices

1. **Always Update Menu After State Changes**: Call `updateMenu(mainWindow)` after modifying menu state
2. **Use Consistent Shortcuts**: Follow platform conventions for keyboard shortcuts
3. **Provide Visual Feedback**: Show loading states when menu actions trigger long operations
4. **Handle Errors Gracefully**: Show error dialogs when menu actions fail
5. **Keep Recent Lists Clean**: Validate that recent files still exist before opening
6. **Test on All Platforms**: Menu behavior can differ between platforms

## Troubleshooting

### Recent Items Not Persisting
- Check that electron-store is properly installed
- Verify write permissions to the config directory
- Check console for storage errors

### Keyboard Shortcuts Not Working
- Ensure shortcuts don't conflict with system shortcuts
- Check that the window has focus
- Verify accelerator syntax is correct

### Context Menu Not Appearing
- Ensure `setupContextMenu` is called after window creation
- Check that context-menu event is being fired
- Verify menu template is valid

## API Reference

### MenuStateManager

```javascript
class MenuStateManager {
  addRecentProject(projectPath, projectName)
  addRecentFile(filePath, fileName)
  clearRecentProjects()
  clearRecentFiles()
  getRecentProjects()
  getRecentFiles()
}
```

### Functions

```javascript
createApplicationMenu(mainWindow)
createContextMenu(params)
createLinkContextMenu(linkURL)
createImageContextMenu(params)
setupContextMenu(mainWindow)
updateMenu(mainWindow)
getKeyboardShortcuts()
```

## Related Documentation

- [Electron Menu Documentation](https://www.electronjs.org/docs/latest/api/menu)
- [Electron MenuItem Documentation](https://www.electronjs.org/docs/latest/api/menu-item)
- [Keyboard Shortcuts Guide](./KEYBOARD_SHORTCUTS.md)
- [Context Menu Guide](./CONTEXT_MENU_GUIDE.md)
