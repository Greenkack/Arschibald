# Window Management Guide

## Overview

The Window Management system provides comprehensive control over application windows, including state persistence, fullscreen mode, always-on-top functionality, multi-window support, and focus management.

## Features

### 1. Window State Persistence

Automatically saves and restores window state across application restarts:

- **Position**: Window location on screen
- **Size**: Window dimensions (width and height)
- **Maximized State**: Whether window is maximized
- **Fullscreen State**: Whether window is in fullscreen mode
- **Always-on-Top State**: Whether window stays on top of other windows
- **Focus State**: Which window was last focused

### 2. Fullscreen Mode

Toggle fullscreen mode for immersive experience:

```typescript
// Toggle fullscreen
const { isFullScreen } = await window.electronAPI.window.toggleFullscreen();

// Set fullscreen explicitly
await window.electronAPI.window.setFullscreen('main', true);
```

**Keyboard Shortcut**: F11 (default)

### 3. Always-on-Top

Keep window above other applications:

```typescript
// Toggle always-on-top
const { isAlwaysOnTop } = await window.electronAPI.window.toggleAlwaysOnTop();

// Set always-on-top explicitly
await window.electronAPI.window.setAlwaysOnTop('main', true);
```

### 4. Multi-Window Support

Create and manage multiple windows:

```typescript
// Create a new window
const result = await window.electronAPI.window.create({
  id: 'secondary-1',
  type: 'secondary',
  browserWindowOptions: {
    width: 800,
    height: 600,
    title: 'Secondary Window'
  },
  url: 'http://localhost:3000/secondary',
  rememberState: true
});

// Get all windows
const windows = await window.electronAPI.window.getAllInfo();

// Focus a specific window
await window.electronAPI.window.focus('secondary-1');

// Close a window
await window.electronAPI.window.close('secondary-1');
```

### 5. Window Focus Management

Control which window has focus:

```typescript
// Focus main window
await window.electronAPI.window.focus('main');

// Get window info including focus state
const info = await window.electronAPI.window.getInfo('main');
console.log('Is focused:', info.isFocused);
```

## Using the React Hook

The `useWindowManager` hook provides easy access to window management features:

```typescript
import { useWindowManager } from '../hooks/useWindowManager';

function MyComponent() {
  const {
    windowInfo,
    preferences,
    allWindows,
    toggleFullscreen,
    toggleAlwaysOnTop,
    createWindow,
    focusWindow
  } = useWindowManager();

  return (
    <div>
      <h2>Window: {windowInfo?.title}</h2>
      <p>Size: {windowInfo?.bounds.width} × {windowInfo?.bounds.height}</p>
      <p>Fullscreen: {windowInfo?.isFullScreen ? 'Yes' : 'No'}</p>
      
      <button onClick={() => toggleFullscreen()}>
        Toggle Fullscreen
      </button>
      <button onClick={() => toggleAlwaysOnTop()}>
        Toggle Always on Top
      </button>
    </div>
  );
}
```

## Window Preferences

Configure window behavior through preferences:

```typescript
const preferences = {
  rememberWindowState: true,        // Save window state
  restoreWindowsOnStartup: true,    // Restore windows on app start
  defaultWidth: 1200,                // Default window width
  defaultHeight: 800,                // Default window height
  defaultMinWidth: 800,              // Minimum window width
  defaultMinHeight: 600              // Minimum window height
};

await window.electronAPI.window.updatePreferences(preferences);
```

## Window Operations

### Minimize

```typescript
await window.electronAPI.window.minimize('main');
```

### Maximize/Restore

```typescript
// Toggle maximize
const { isMaximized } = await window.electronAPI.window.maximize('main');

// Restore from minimized/maximized
await window.electronAPI.window.restore('main');
```

### Get Window Information

```typescript
const info = await window.electronAPI.window.getInfo('main');
console.log({
  position: `${info.bounds.x}, ${info.bounds.y}`,
  size: `${info.bounds.width} × ${info.bounds.height}`,
  isMaximized: info.isMaximized,
  isMinimized: info.isMinimized,
  isFullScreen: info.isFullScreen,
  isAlwaysOnTop: info.isAlwaysOnTop,
  isFocused: info.isFocused,
  isVisible: info.isVisible
});
```

## Window State Management

### Clear Window State

Remove saved state for a specific window:

```typescript
await window.electronAPI.window.clearState('main');
```

### Clear All Window States

Remove all saved window states:

```typescript
await window.electronAPI.window.clearAllStates();
```

## Multi-Window Patterns

### Creating Secondary Windows

```typescript
// Create a project details window
const createProjectWindow = async (projectId: string) => {
  return await window.electronAPI.window.create({
    id: `project-${projectId}`,
    type: 'project-details',
    browserWindowOptions: {
      width: 1000,
      height: 700,
      title: `Project ${projectId}`,
      parent: mainWindow, // Optional: make it a child window
      modal: false
    },
    url: `http://localhost:3000/projects/${projectId}`,
    rememberState: true
  });
};

// Create a settings window
const createSettingsWindow = async () => {
  return await window.electronAPI.window.create({
    id: 'settings',
    type: 'settings',
    browserWindowOptions: {
      width: 800,
      height: 600,
      title: 'Settings',
      resizable: false
    },
    url: 'http://localhost:3000/settings',
    rememberState: false // Don't remember state for settings
  });
};
```

### Managing Multiple Windows

```typescript
// Get all project windows
const allWindows = await window.electronAPI.window.getAllInfo();
const projectWindows = allWindows.filter(w => w.id.startsWith('project-'));

// Close all project windows
for (const window of projectWindows) {
  await window.electronAPI.window.close(window.id);
}

// Focus the most recently created project window
if (projectWindows.length > 0) {
  const lastProject = projectWindows[projectWindows.length - 1];
  await window.electronAPI.window.focus(lastProject.id);
}
```

## Best Practices

### 1. Window IDs

Use descriptive, unique IDs for windows:

```typescript
// Good
'main'
'project-123'
'settings'
'pdf-preview-456'

// Avoid
'window1'
'w2'
'temp'
```

### 2. State Persistence

Only enable state persistence for windows that benefit from it:

```typescript
// Enable for main application windows
rememberState: true

// Disable for temporary/modal windows
rememberState: false
```

### 3. Window Cleanup

Always clean up windows when they're no longer needed:

```typescript
// Close window when component unmounts
useEffect(() => {
  return () => {
    window.electronAPI.window.close('secondary-window');
  };
}, []);
```

### 4. Error Handling

Always handle window operation errors:

```typescript
const result = await window.electronAPI.window.create(options);
if (!result.success) {
  console.error('Failed to create window:', result.error);
  // Show user-friendly error message
}
```

## Keyboard Shortcuts

Default keyboard shortcuts for window operations:

- **F11**: Toggle fullscreen
- **Ctrl/Cmd + M**: Minimize window
- **Ctrl/Cmd + W**: Close window
- **Alt + F4** (Windows/Linux): Close window
- **Cmd + Q** (macOS): Quit application

## Troubleshooting

### Window Not Restoring Position

If window position isn't being restored:

1. Check that `rememberWindowState` preference is enabled
2. Verify window ID is consistent across sessions
3. Clear window state and restart: `clearWindowState(windowId)`

### Window Opens Off-Screen

If window opens outside visible screen area:

1. The system automatically validates bounds against current screen
2. If invalid, window is centered on primary display
3. To force reset: `clearWindowState(windowId)`

### Multiple Windows Not Working

If you can't create multiple windows:

1. Ensure each window has a unique ID
2. Check that window type is appropriate
3. Verify browser window options are valid

## API Reference

See [WINDOW_MANAGEMENT_API.md](./WINDOW_MANAGEMENT_API.md) for complete API documentation.

## Examples

See [WindowManagement.tsx](../frontend/src/components/settings/WindowManagement.tsx) for a complete implementation example.
