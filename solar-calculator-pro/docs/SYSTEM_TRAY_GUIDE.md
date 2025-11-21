# System Tray Integration Guide

## Overview

The Solar Calculator Pro application includes comprehensive system tray integration that allows the application to run in the background and provides quick access to common features without opening the main window.

## Features

### 1. System Tray Icon

The application displays an icon in the system tray (Windows notification area, macOS menu bar, or Linux system tray) that provides:

- **Visual Status Indicators**: Different icon states for normal, busy, error, and warning conditions
- **Tooltip**: Hover over the icon to see the application name and version
- **Click Actions**: 
  - Single click: Toggle window visibility
  - Double click: Show window
  - Right click: Open context menu

### 2. Tray Context Menu

Right-clicking the tray icon opens a comprehensive menu with:

#### Quick Access
- **Dashboard**: Navigate directly to the dashboard
- **New Calculation**: Start a new project
- **Show/Hide Window**: Toggle main window visibility

#### Quick Actions Submenu
Configurable shortcuts to frequently used features:
- Solar Calculator
- Heat Pump Calculator
- CRM
- Products
- PDF Generation

#### Recent Projects Submenu
- Access up to 10 most recently opened projects
- Shows project name and last accessed date
- Clear recent projects option

#### Tools Submenu
- Import Excel
- Export PDF
- Generate Report
- Database Backup

#### Settings & Preferences
- Application Settings
- Tray Preferences (see below)

#### Help & About
- Help documentation
- About dialog

#### Quit
- Exit the application completely

### 3. Minimize to Tray

When enabled, minimizing the main window will hide it to the tray instead of the taskbar.

**Configuration**: Right-click tray icon → Tray Preferences → Minimize to Tray

**Behavior**:
- Window is hidden from taskbar
- Application continues running in background
- First-time notification explains the feature
- Click tray icon to restore window

### 4. Close to Tray

When enabled, closing the main window will hide it to the tray instead of quitting the application.

**Configuration**: Right-click tray icon → Tray Preferences → Close to Tray

**Behavior**:
- Clicking X button hides window instead of quitting
- Notification reminds user app is still running
- Use "Quit" from tray menu to exit completely

### 5. Tray Notifications

The system tray can display desktop notifications for important events:

**Notification Types**:
- **Info**: General information (blue)
- **Success**: Successful operations (green)
- **Warning**: Warnings that need attention (yellow)
- **Error**: Critical errors (red)

**Features**:
- Queue management (prevents notification spam)
- 2-second delay between notifications
- Click notification to show main window
- Optional notification sound
- Icon flashing for important notifications

**Configuration**:
- Show Notifications: Enable/disable all notifications
- Notification Sound: Enable/disable sound alerts

### 6. Quick Actions

Customizable shortcuts in the tray menu for frequently used features.

**Default Quick Actions**:
- Solar Calculator
- Heat Pump Calculator
- CRM
- Products
- PDF Generation

**Customization**:
- Enable/disable individual actions
- Reorder actions
- Add custom actions (future feature)

Access configuration: Tray Preferences → Configure Quick Actions

## API Reference

### Frontend Integration

The tray API is exposed to the frontend through the `window.electronAPI.tray` object:

```typescript
// Add a recent project to tray menu
await window.electronAPI.tray.addRecentProject({
  id: 'project-123',
  name: 'Solar Installation - Smith Residence',
  date: new Date().toISOString()
});

// Show a tray notification
await window.electronAPI.tray.showNotification(
  'Calculation Complete',
  'Your solar system calculation is ready to view.',
  'success'
);

// Flash tray icon to get attention
await window.electronAPI.tray.flash(3000); // Flash for 3 seconds

// Update tray icon state
await window.electronAPI.tray.updateIcon('busy'); // normal, busy, error, warning

// Update tooltip
await window.electronAPI.tray.updateTooltip('Solar Calculator Pro - Calculating...');

// Get tray preferences
const preferences = await window.electronAPI.tray.getPreferences();

// Update tray preferences
await window.electronAPI.tray.updatePreferences({
  minimizeToTray: true,
  showNotifications: true
});

// Update quick actions
await window.electronAPI.tray.updateQuickActions([
  { id: 'solar', label: 'Solar Calculator', route: '/solar', enabled: true },
  { id: 'crm', label: 'CRM', route: '/crm', enabled: true }
]);

// Check if tray is available
const isAvailable = await window.electronAPI.tray.isAvailable();
```

### Notification Examples

```typescript
// Simple notification
await window.electronAPI.tray.showNotification(
  'Export Complete',
  'Your PDF has been exported successfully.',
  'success'
);

// Notification with actions (future feature)
await window.electronAPI.tray.showNotification(
  'New Message',
  'You have a new message from John Doe',
  'info',
  [
    { text: 'View', callback: () => navigateTo('/messages') },
    { text: 'Dismiss', callback: () => {} }
  ]
);

// Error notification with icon flash
await window.electronAPI.tray.showNotification(
  'Calculation Error',
  'Failed to calculate solar system. Please check your inputs.',
  'error'
);
await window.electronAPI.tray.flash(5000);
```

### React Hook Example

```typescript
// hooks/useTray.ts
import { useEffect, useCallback } from 'react';

export function useTray() {
  const showNotification = useCallback(
    async (title: string, body: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
      if (window.electronAPI?.tray) {
        await window.electronAPI.tray.showNotification(title, body, type);
      }
    },
    []
  );

  const addRecentProject = useCallback(async (project: { id: string; name: string }) => {
    if (window.electronAPI?.tray) {
      await window.electronAPI.tray.addRecentProject(project);
    }
  }, []);

  const updateIcon = useCallback(async (state: 'normal' | 'busy' | 'error' | 'warning') => {
    if (window.electronAPI?.tray) {
      await window.electronAPI.tray.updateIcon(state);
    }
  }, []);

  return {
    showNotification,
    addRecentProject,
    updateIcon
  };
}

// Usage in component
function SolarCalculator() {
  const { showNotification, updateIcon } = useTray();

  const handleCalculate = async () => {
    try {
      updateIcon('busy');
      const result = await calculateSolarSystem(inputs);
      updateIcon('normal');
      showNotification(
        'Calculation Complete',
        `System size: ${result.systemSize} kWp`,
        'success'
      );
    } catch (error) {
      updateIcon('error');
      showNotification(
        'Calculation Failed',
        error.message,
        'error'
      );
    }
  };

  return (
    <button onClick={handleCalculate}>Calculate</button>
  );
}
```

## Tray Preferences

### Available Preferences

```typescript
interface TrayPreferences {
  // Minimize to tray instead of taskbar
  minimizeToTray: boolean;
  
  // Close to tray instead of quitting
  closeToTray: boolean;
  
  // Show desktop notifications
  showNotifications: boolean;
  
  // Play sound with notifications
  notificationSound: boolean;
  
  // Start application minimized to tray
  startMinimized: boolean;
  
  // Recent projects (managed automatically)
  recentProjects: Array<{
    id: string;
    name: string;
    date: string;
  }>;
  
  // Quick actions configuration
  quickActions: Array<{
    id: string;
    label: string;
    route: string;
    enabled: boolean;
  }>;
}
```

### Accessing Preferences

```typescript
// Get all preferences
const prefs = await window.electronAPI.tray.getPreferences();

// Update specific preferences
await window.electronAPI.tray.updatePreferences({
  minimizeToTray: true,
  showNotifications: false
});
```

## Platform-Specific Behavior

### Windows
- Tray icon appears in notification area (system tray)
- Icon size: 16x16 pixels
- Supports icon flashing for attention
- Balloon notifications supported

### macOS
- Tray icon appears in menu bar
- Icon size: 22x22 pixels (with @2x support)
- Template image mode for dark mode support
- No icon flashing (not supported by macOS)
- Native notification center integration

### Linux
- Tray icon appears in system tray
- Icon size: 22x22 pixels
- Behavior varies by desktop environment
- libnotify for notifications

## Best Practices

### 1. Use Notifications Sparingly
- Only notify for important events
- Don't spam users with notifications
- Use appropriate notification types
- Keep messages concise and actionable

### 2. Update Icon State
- Show busy state during long operations
- Show error state when issues occur
- Return to normal state when complete

### 3. Manage Recent Projects
- Add projects when they're opened or saved
- Limit to 10 most recent
- Include meaningful project names

### 4. Configure Quick Actions
- Enable only frequently used features
- Keep the list short (5-7 items max)
- Use clear, descriptive labels

### 5. Respect User Preferences
- Check if notifications are enabled before showing
- Honor minimize/close to tray settings
- Provide clear way to disable features

## Troubleshooting

### Tray Icon Not Appearing
1. Check if tray is supported: `await window.electronAPI.tray.isAvailable()`
2. Verify icon file exists at `assets/tray-icon.png`
3. Check console for errors
4. Try restarting the application

### Notifications Not Showing
1. Check if notifications are enabled in preferences
2. Verify system notification permissions
3. Check if Do Not Disturb is enabled (macOS)
4. Verify notification support: `Notification.isSupported()`

### Window Not Restoring from Tray
1. Click tray icon to toggle visibility
2. Use "Show Window" from context menu
3. Check if window is minimized vs hidden
4. Try double-clicking tray icon

### Tray Menu Not Updating
1. Recent projects should update automatically
2. Preferences changes update menu immediately
3. Try right-clicking to refresh menu
4. Check console for errors

## Future Enhancements

Planned features for future releases:

1. **Custom Quick Actions**: Allow users to create custom shortcuts
2. **Notification Actions**: Clickable buttons in notifications
3. **Tray Icon Badges**: Show unread count or status
4. **Multiple Tray Icons**: Different icons for different states
5. **Tray Popover**: Quick view without opening main window
6. **Keyboard Shortcuts**: Global shortcuts for tray actions
7. **Notification History**: View past notifications
8. **Smart Notifications**: AI-powered notification timing

## Related Documentation

- [Native Menu Guide](./NATIVE_MENU_GUIDE.md)
- [Window Management](./WINDOW_MANAGEMENT.md)
- [Notifications System](./NOTIFICATIONS.md)
- [Electron Setup Guide](./ELECTRON_SETUP_QUICK_REFERENCE.md)

## Support

For issues or questions about system tray integration:
- Check the troubleshooting section above
- Review the API reference
- Check the example code
- Contact support team
