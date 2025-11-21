# Native Menu Quick Reference

## Keyboard Shortcuts

### File Operations
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| New Project | `Ctrl+N` | `Cmd+N` |
| Open Project | `Ctrl+O` | `Cmd+O` |
| Save Project | `Ctrl+S` | `Cmd+S` |
| Save As | `Ctrl+Shift+S` | `Cmd+Shift+S` |
| Save All | `Ctrl+Alt+S` | `Cmd+Alt+S` |
| Close Project | `Ctrl+W` | `Cmd+W` |
| Import Excel | `Ctrl+Shift+I` | `Cmd+Shift+I` |
| Export PDF | `Ctrl+P` | `Cmd+P` |
| Export Excel | `Ctrl+E` | `Cmd+E` |
| Print | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Quit | `Ctrl+Q` | `Cmd+Q` |

### Edit Operations
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Undo | `Ctrl+Z` | `Cmd+Z` |
| Redo | `Ctrl+Y` | `Cmd+Shift+Z` |
| Cut | `Ctrl+X` | `Cmd+X` |
| Copy | `Ctrl+C` | `Cmd+C` |
| Paste | `Ctrl+V` | `Cmd+V` |
| Select All | `Ctrl+A` | `Cmd+A` |
| Find | `Ctrl+F` | `Cmd+F` |
| Find Next | `F3` | `Cmd+G` |
| Find Previous | `Shift+F3` | `Cmd+Shift+G` |
| Replace | `Ctrl+H` | `Cmd+H` |
| Preferences | `Ctrl+,` | `Cmd+,` |

### Navigation
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Dashboard | `Ctrl+1` | `Cmd+1` |
| Solar Calculator | `Ctrl+2` | `Cmd+2` |
| Heat Pump | `Ctrl+3` | `Cmd+3` |
| Combined System | `Ctrl+4` | `Cmd+4` |
| CRM | `Ctrl+5` | `Cmd+5` |
| Products | `Ctrl+6` | `Cmd+6` |
| Price Matrix | `Ctrl+7` | `Cmd+7` |
| PDF Generation | `Ctrl+8` | `Cmd+8` |
| 3D Visualization | `Ctrl+9` | `Cmd+9` |
| Go Back | `Ctrl+[` | `Cmd+[` |
| Go Forward | `Ctrl+]` | `Cmd+]` |

### View Operations
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Reload | `Ctrl+R` | `Cmd+R` |
| Force Reload | `Ctrl+Shift+R` | `Cmd+Shift+R` |
| Toggle DevTools | `Ctrl+Shift+I` | `Alt+Cmd+I` |
| Actual Size | `Ctrl+0` | `Cmd+0` |
| Zoom In | `Ctrl+Plus` | `Cmd+Plus` |
| Zoom Out | `Ctrl+-` | `Cmd+-` |
| Toggle Full Screen | `F11` | `Ctrl+Cmd+F` |
| Toggle Sidebar | `Ctrl+B` | `Cmd+B` |
| Toggle Theme | `Ctrl+T` | `Cmd+T` |

### Window Operations
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Minimize | `Ctrl+M` | `Cmd+M` |
| Close | `Alt+F4` | `Cmd+W` |

### Help
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Documentation | `F1` | `F1` |
| Keyboard Shortcuts | `Ctrl+/` | `Cmd+/` |
| Search Help | `Ctrl+Shift+H` | `Cmd+Shift+H` |

## Recent Items Shortcuts

### Recent Projects
| Project | Windows/Linux | macOS |
|---------|--------------|-------|
| Project 1 | `Ctrl+Alt+1` | `Cmd+Alt+1` |
| Project 2 | `Ctrl+Alt+2` | `Cmd+Alt+2` |
| ... | ... | ... |
| Project 9 | `Ctrl+Alt+9` | `Cmd+Alt+9` |

## API Quick Reference

### Frontend (React/TypeScript)

```typescript
// Listen for menu navigation
window.electronAPI.onNavigate((route) => {
  // Handle navigation
});

// Listen for menu actions
window.electronAPI.onAction((action, data) => {
  // Handle action
});

// Add recent project
await window.electronAPI.addRecentProject(path, name);

// Add recent file
await window.electronAPI.addRecentFile(path, name);

// Get keyboard shortcuts
const shortcuts = await window.electronAPI.getKeyboardShortcuts();

// Clear recent lists
await window.electronAPI.clearRecentProjects();
await window.electronAPI.clearRecentFiles();
```

### Main Process (JavaScript)

```javascript
const { updateMenu, menuState } = require('./menu');

// Add recent items
menuState.addRecentProject(path, name);
menuState.addRecentFile(path, name);
updateMenu(mainWindow);

// Clear recent lists
menuState.clearRecentProjects();
menuState.clearRecentFiles();
updateMenu(mainWindow);

// Setup context menu
const { setupContextMenu } = require('./menu');
setupContextMenu(mainWindow);
```

## Menu Actions Reference

### File Actions
- `new-project` - Create new project
- `open-project` - Open project (with path parameter)
- `save-project` - Save current project
- `save-project-as` - Save project with new name (with path parameter)
- `save-all` - Save all open projects
- `close-project` - Close current project
- `import-excel` - Import Excel file (with path parameter)
- `import-csv` - Import CSV file (with path parameter)
- `import-price-matrix` - Import price matrix (with path parameter)
- `import-products` - Import product database (with path parameter)
- `export-pdf` - Export to PDF
- `export-excel` - Export to Excel
- `export-3d` - Export 3D model (with format parameter: 'stl', 'obj', 'gltf')
- `export-report` - Export report
- `page-setup` - Configure page setup

### Edit Actions
- `find` - Open find dialog
- `find-next` - Find next occurrence
- `find-previous` - Find previous occurrence
- `replace` - Open find and replace dialog

### View Actions
- `toggle-sidebar` - Show/hide sidebar
- `toggle-theme` - Switch theme

### Help Actions
- `show-getting-started` - Show getting started guide
- `show-shortcuts` - Show keyboard shortcuts dialog
- `search-help` - Open help search
- `show-faq` - Show FAQ
- `send-feedback` - Open feedback form
- `check-updates` - Check for updates
- `show-license` - Show license information
- `show-about` - Show about dialog

## Context Menu Types

### Text Input
- Undo, Redo, Cut, Copy, Paste, Delete, Select All

### Link
- Open Link, Copy Link Address

### Image
- Copy Image, Copy Image Address, Save Image As, Open Image in Browser

### Default
- Copy, Select All, Reload, Toggle DevTools

## Storage Locations

### Windows
```
%APPDATA%\solar-calculator-pro\menu-state.json
```

### macOS
```
~/Library/Application Support/solar-calculator-pro/menu-state.json
```

### Linux
```
~/.config/solar-calculator-pro/menu-state.json
```

## Common Tasks

### Add a Custom Menu Item

```javascript
// In electron/menu.js
{
  label: 'My Action',
  accelerator: 'CmdOrCtrl+Shift+X',
  click: () => {
    mainWindow.webContents.send('action', 'my-action');
  }
}
```

### Handle Menu Action in Frontend

```typescript
useEffect(() => {
  const unsubscribe = window.electronAPI.onAction((action, data) => {
    if (action === 'my-action') {
      // Handle your action
    }
  });
  return unsubscribe;
}, []);
```

### Update Recent Items

```typescript
// After opening a project
await window.electronAPI.addRecentProject(
  projectPath,
  projectName
);
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Shortcuts not working | Check window has focus, verify no conflicts |
| Recent items not saving | Check electron-store installation and permissions |
| Context menu not appearing | Ensure setupContextMenu() is called |
| Menu not updating | Call updateMenu(mainWindow) after state changes |

## See Also

- [Native Menu Guide](./NATIVE_MENU_GUIDE.md) - Complete documentation
- [Electron Menu API](https://www.electronjs.org/docs/latest/api/menu)
- [Keyboard Shortcuts](./KEYBOARD_SHORTCUTS.md)
