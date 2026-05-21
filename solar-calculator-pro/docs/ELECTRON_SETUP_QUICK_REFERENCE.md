# Electron Setup Quick Reference

## Overview
This document provides a quick reference for the Electron application setup, including security configuration, IPC communication, menu structure, and auto-updates.

## Security Configuration

### BrowserWindow Security Settings
```javascript
new BrowserWindow({
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    nodeIntegration: false,        // Disable Node.js in renderer
    contextIsolation: true,         // Isolate renderer context
    enableRemoteModule: false,      // Disable remote module
    sandbox: true,                  // Enable sandbox
    webSecurity: true,              // Enable web security
  }
});
```

### Content Security Policy
```javascript
'Content-Security-Policy': [
  "default-src 'self'; " +
  "script-src 'self'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: https:; " +
  "font-src 'self' data:; " +
  "connect-src 'self' http://localhost:8000"
]
```

## IPC Communication

### From Renderer to Main (Invoke)
```typescript
// Renderer
const result = await window.electronAPI.selectFile();
const url = await window.electronAPI.getBackendUrl();
const version = await window.electronAPI.getAppVersion();
```

### From Renderer to Main (Send)
```typescript
// Renderer
window.electronAPI.minimize();
window.electronAPI.maximize();
window.electronAPI.close();
window.electronAPI.showNotification('Title', 'Body');
```

### From Main to Renderer (Send)
```javascript
// Main process
mainWindow.webContents.send('navigate', '/dashboard');
mainWindow.webContents.send('action', 'new-project');
mainWindow.webContents.send('updater:available', updateInfo);
```

### Event Listeners with Cleanup
```typescript
// Renderer
const unsubscribe = window.electronAPI.onUpdateAvailable((data) => {
  console.log('Update:', data.version);
});

// Cleanup when component unmounts
useEffect(() => {
  return () => unsubscribe();
}, []);
```

## Application Menu

### Keyboard Shortcuts
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| New Project | Ctrl+N | Cmd+N |
| Open Project | Ctrl+O | Cmd+O |
| Save Project | Ctrl+S | Cmd+S |
| Save As | Ctrl+Shift+S | Cmd+Shift+S |
| Export PDF | Ctrl+P | Cmd+P |
| Find | Ctrl+F | Cmd+F |
| Preferences | Ctrl+, | Cmd+, |
| Dashboard | Ctrl+1 | Cmd+1 |
| Solar Calculator | Ctrl+2 | Cmd+2 |
| Heat Pump | Ctrl+3 | Cmd+3 |
| CRM | Ctrl+4 | Cmd+4 |
| Products | Ctrl+5 | Cmd+5 |
| Shortcuts Help | Ctrl+/ | Cmd+/ |

### Menu Actions
```typescript
// Listen for menu actions
window.electronAPI.onAction((action, data) => {
  switch(action) {
    case 'new-project':
      createNewProject();
      break;
    case 'save-project':
      saveCurrentProject();
      break;
    case 'export-pdf':
      exportToPDF();
      break;
    case 'import-excel':
      importExcelFile();
      break;
  }
});
```

### Navigation from Menu
```typescript
// Listen for navigation
window.electronAPI.onNavigate((route) => {
  router.push(route);
});
```

## System Tray

### Tray Features
- Click to show/hide window
- Double-click to show window
- Context menu with quick actions
- Recent projects menu
- Notifications

### Update Tray Menu
```javascript
// Main process
const { updateTrayMenu } = require('./electron/tray');

updateTrayMenu(mainWindow, [
  { id: 1, name: 'Project A' },
  { id: 2, name: 'Project B' }
]);
```

### Show Tray Notification
```javascript
// Main process
const { showNotification } = require('./electron/tray');
showNotification('Title', 'Message body');
```

## Auto-Updater

### Check for Updates
```typescript
// Renderer
const result = await window.electronAPI.checkForUpdates();
if (result.success) {
  console.log('Update info:', result.updateInfo);
}
```

### Download Update
```typescript
const result = await window.electronAPI.downloadUpdate();
if (result.success) {
  console.log('Download started');
}
```

### Install Update
```typescript
// This will quit and install
window.electronAPI.installUpdate();
```

### Update Events
```typescript
// Update available
window.electronAPI.onUpdateAvailable((data) => {
  console.log('Version:', data.version);
  console.log('Release notes:', data.releaseNotes);
});

// Download progress
window.electronAPI.onUpdateProgress((data) => {
  console.log('Progress:', data.percent + '%');
  console.log('Speed:', data.bytesPerSecond);
});

// Update downloaded
window.electronAPI.onUpdateDownloaded((data) => {
  console.log('Ready to install:', data.version);
});

// Update error
window.electronAPI.onUpdateError((data) => {
  console.error('Update error:', data.message);
});

// Checking for update
window.electronAPI.onUpdateChecking(() => {
  console.log('Checking for updates...');
});
```

## File Operations

### Open File Dialog
```typescript
const filePath = await window.electronAPI.selectFile();
if (filePath) {
  // Load file
}
```

### Save File Dialog
```typescript
const filePath = await window.electronAPI.saveFile({
  defaultPath: 'project.json',
  filters: [
    { name: 'JSON Files', extensions: ['json'] },
    { name: 'All Files', extensions: ['*'] }
  ]
});
```

### Select Directory
```typescript
const dirPath = await window.electronAPI.selectDirectory();
if (dirPath) {
  // Use directory
}
```

## Backend Communication

### Get Backend URL
```typescript
const backendUrl = await window.electronAPI.getBackendUrl();
// Use for API calls: http://localhost:8000
```

### Check Backend Health
```typescript
const isHealthy = await window.electronAPI.checkBackendHealth();
if (!isHealthy) {
  // Show error message
}
```

## Window Operations

### Minimize Window
```typescript
window.electronAPI.minimize();
```

### Maximize/Restore Window
```typescript
window.electronAPI.maximize();
```

### Close Window
```typescript
window.electronAPI.close();
```

## Notifications

### Show Native Notification
```typescript
window.electronAPI.showNotification(
  'Success',
  'Your project has been saved!'
);
```

## System Information

### Get App Version
```typescript
const version = await window.electronAPI.getAppVersion();
console.log('App version:', version);
```

### Get Platform
```typescript
const platform = window.electronAPI.getPlatform();
// 'win32', 'darwin', 'linux'
```

### Check Online Status
```typescript
const isOnline = window.electronAPI.isOnline();
```

## Path Operations

### Join Paths
```typescript
const fullPath = window.nodeAPI.pathJoin('folder', 'file.txt');
```

### Get Basename
```typescript
const filename = window.nodeAPI.pathBasename('/path/to/file.txt');
// 'file.txt'
```

### Get Directory Name
```typescript
const dirname = window.nodeAPI.pathDirname('/path/to/file.txt');
// '/path/to'
```

### Get Extension
```typescript
const ext = window.nodeAPI.pathExtname('file.txt');
// '.txt'
```

## Environment Info

### Access Environment Variables
```typescript
const env = window.nodeAPI.env;
console.log('Environment:', env.NODE_ENV);
console.log('Platform:', env.PLATFORM);
console.log('Architecture:', env.ARCH);
```

## React Integration Example

### Update Notification Component
```typescript
import { useEffect, useState } from 'react';

export const UpdateNotification: React.FC = () => {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState<any>(null);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Listen for update available
    const unsubAvailable = window.electronAPI.onUpdateAvailable((data) => {
      setUpdateAvailable(true);
      setUpdateInfo(data);
    });

    // Listen for download progress
    const unsubProgress = window.electronAPI.onUpdateProgress((data) => {
      setDownloading(true);
      setProgress(data.percent);
    });

    // Listen for update downloaded
    const unsubDownloaded = window.electronAPI.onUpdateDownloaded(() => {
      setDownloading(false);
      // Show install prompt
    });

    return () => {
      unsubAvailable();
      unsubProgress();
      unsubDownloaded();
    };
  }, []);

  const handleDownload = async () => {
    await window.electronAPI.downloadUpdate();
  };

  if (!updateAvailable) return null;

  return (
    <div className="update-notification">
      <h3>Update Available: {updateInfo?.version}</h3>
      {downloading ? (
        <div>Downloading: {progress.toFixed(0)}%</div>
      ) : (
        <button onClick={handleDownload}>Download Update</button>
      )}
    </div>
  );
};
```

### Menu Action Handler
```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const useMenuActions = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Handle navigation from menu
    const unsubNav = window.electronAPI.onNavigate((route) => {
      navigate(route);
    });

    // Handle actions from menu
    const unsubAction = window.electronAPI.onAction((action, data) => {
      switch(action) {
        case 'new-project':
          // Handle new project
          break;
        case 'save-project':
          // Handle save
          break;
        case 'export-pdf':
          // Handle PDF export
          break;
      }
    });

    return () => {
      unsubNav();
      unsubAction();
    };
  }, [navigate]);
};
```

## Troubleshooting

### Context Isolation Issues
If you get errors about `window.electronAPI` being undefined:
1. Check that preload script is loaded
2. Verify `contextIsolation: true` in BrowserWindow
3. Check browser console for preload script logs

### IPC Communication Errors
If IPC calls fail:
1. Check that handler is registered in main process
2. Verify channel name matches exactly
3. Check for typos in method names
4. Look at main process console for errors

### Update Not Working
If auto-update doesn't work:
1. Check that `electron-updater` is installed
2. Verify update feed URL is configured
3. Check logs in `~/.config/solar-calculator-pro/logs/`
4. Ensure app is code-signed (required for macOS)

### Menu Not Showing
If application menu doesn't appear:
1. Check that `createApplicationMenu()` is called
2. Verify menu.js is imported correctly
3. On macOS, menu appears in system menu bar
4. On Windows/Linux, menu appears in window

## Best Practices

### Security
- ✅ Always use `contextIsolation: true`
- ✅ Always set `nodeIntegration: false`
- ✅ Use preload script for IPC bridge
- ✅ Validate all IPC inputs
- ✅ Never expose full Node.js API
- ✅ Use CSP headers

### Performance
- ✅ Use `show: false` and show window when ready
- ✅ Lazy load heavy operations
- ✅ Use background processes for long tasks
- ✅ Implement proper cleanup in event listeners

### User Experience
- ✅ Provide keyboard shortcuts
- ✅ Show loading states
- ✅ Handle errors gracefully
- ✅ Persist window state
- ✅ Support system tray
- ✅ Implement auto-updates

## Additional Resources

- [Electron Security](https://www.electronjs.org/docs/latest/tutorial/security)
- [IPC Communication](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [Context Isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation)
- [Auto Updates](https://www.electronjs.org/docs/latest/api/auto-updater)
- [Menu](https://www.electronjs.org/docs/latest/api/menu)
- [Tray](https://www.electronjs.org/docs/latest/api/tray)
