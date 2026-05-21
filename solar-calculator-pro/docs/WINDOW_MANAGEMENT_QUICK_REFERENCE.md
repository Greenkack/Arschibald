# Window Management Quick Reference

## Quick Start

```typescript
import { useWindowManager } from '../hooks/useWindowManager';

const { toggleFullscreen, toggleAlwaysOnTop, windowInfo } = useWindowManager();
```

## Common Operations

### Toggle Fullscreen
```typescript
await window.electronAPI.window.toggleFullscreen();
```

### Toggle Always-on-Top
```typescript
await window.electronAPI.window.toggleAlwaysOnTop();
```

### Create New Window
```typescript
await window.electronAPI.window.create({
  id: 'my-window',
  type: 'secondary',
  browserWindowOptions: { width: 800, height: 600 },
  url: 'http://localhost:3000/page'
});
```

### Focus Window
```typescript
await window.electronAPI.window.focus('my-window');
```

### Close Window
```typescript
await window.electronAPI.window.close('my-window');
```

### Get Window Info
```typescript
const info = await window.electronAPI.window.getInfo('main');
```

### Update Preferences
```typescript
await window.electronAPI.window.updatePreferences({
  rememberWindowState: true,
  restoreWindowsOnStartup: true
});
```

## React Hook

```typescript
const {
  windowInfo,           // Current window information
  preferences,          // Window preferences
  allWindows,          // All windows list
  toggleFullscreen,    // Toggle fullscreen mode
  toggleAlwaysOnTop,   // Toggle always-on-top
  createWindow,        // Create new window
  focusWindow,         // Focus window
  closeWindow,         // Close window
  minimizeWindow,      // Minimize window
  maximizeWindow,      // Maximize window
  restoreWindow        // Restore window
} = useWindowManager();
```

## Window Info Structure

```typescript
{
  id: string;
  bounds: { x: number; y: number; width: number; height: number };
  isMaximized: boolean;
  isMinimized: boolean;
  isFullScreen: boolean;
  isAlwaysOnTop: boolean;
  isFocused: boolean;
  isVisible: boolean;
  title: string;
}
```

## Preferences Structure

```typescript
{
  rememberWindowState: boolean;
  restoreWindowsOnStartup: boolean;
  defaultWidth: number;
  defaultHeight: number;
  defaultMinWidth: number;
  defaultMinHeight: number;
}
```

## Keyboard Shortcuts

- **F11**: Toggle fullscreen
- **Ctrl/Cmd + M**: Minimize
- **Ctrl/Cmd + W**: Close window
- **Alt + F4** (Windows/Linux): Close window
- **Cmd + Q** (macOS): Quit app

## Best Practices

✅ **DO:**
- Use descriptive window IDs
- Enable state persistence for main windows
- Handle errors from window operations
- Clean up windows when done

❌ **DON'T:**
- Use generic IDs like 'window1'
- Enable persistence for temporary windows
- Ignore operation errors
- Leave windows open unnecessarily

## Common Patterns

### Modal Window
```typescript
await window.electronAPI.window.create({
  id: 'modal',
  browserWindowOptions: {
    modal: true,
    parent: mainWindow,
    width: 600,
    height: 400
  },
  rememberState: false
});
```

### Persistent Secondary Window
```typescript
await window.electronAPI.window.create({
  id: 'project-details',
  type: 'secondary',
  browserWindowOptions: {
    width: 1000,
    height: 700
  },
  rememberState: true
});
```

### Temporary Window
```typescript
await window.electronAPI.window.create({
  id: 'temp-preview',
  browserWindowOptions: {
    width: 800,
    height: 600,
    show: true
  },
  rememberState: false
});
```

## Troubleshooting

**Window not restoring?**
```typescript
// Clear state and restart
await window.electronAPI.window.clearState('window-id');
```

**Window off-screen?**
```typescript
// System auto-centers if invalid bounds
// Or manually clear state
await window.electronAPI.window.clearState('window-id');
```

**Can't create window?**
- Check unique ID
- Verify options are valid
- Check console for errors

## See Also

- [Complete Guide](./WINDOW_MANAGEMENT_GUIDE.md)
- [API Reference](./WINDOW_MANAGEMENT_API.md)
- [Example Component](../frontend/src/components/settings/WindowManagement.tsx)
