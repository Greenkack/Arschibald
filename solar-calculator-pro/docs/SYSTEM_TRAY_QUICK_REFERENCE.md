# System Tray Quick Reference

## Quick Start

```typescript
// Show notification
await window.electronAPI.tray.showNotification(
  'Title',
  'Message body',
  'success' // info, success, warning, error
);

// Add recent project
await window.electronAPI.tray.addRecentProject({
  id: 'project-id',
  name: 'Project Name'
});

// Update icon state
await window.electronAPI.tray.updateIcon('busy'); // normal, busy, error, warning

// Flash icon
await window.electronAPI.tray.flash(3000); // duration in ms
```

## Tray Menu Structure

```
Solar Calculator Pro
├── Show/Hide Window
├── Dashboard
├── New Calculation
├── Quick Actions
│   ├── Solar Calculator
│   ├── Heat Pump
│   ├── CRM
│   ├── Products
│   └── PDF Generation
├── Recent Projects
│   ├── Project 1
│   ├── Project 2
│   └── Clear Recent Projects
├── Tools
│   ├── Import Excel
│   ├── Export PDF
│   ├── Generate Report
│   └── Database Backup
├── Settings
├── Tray Preferences
│   ├── Minimize to Tray
│   ├── Close to Tray
│   ├── Show Notifications
│   ├── Notification Sound
│   └── Configure Quick Actions
├── Help
├── About
└── Quit
```

## API Methods

### Notifications
```typescript
// Basic notification
tray.showNotification(title, body, type);

// With actions (future)
tray.showNotification(title, body, type, actions);
```

### Icon Management
```typescript
// Update icon state
tray.updateIcon('normal' | 'busy' | 'error' | 'warning');

// Flash icon
tray.flash(duration);

// Update tooltip
tray.updateTooltip(text);
```

### Recent Projects
```typescript
// Add project
tray.addRecentProject({ id, name, date });

// Projects are automatically managed (max 10)
```

### Preferences
```typescript
// Get preferences
const prefs = await tray.getPreferences();

// Update preferences
await tray.updatePreferences({
  minimizeToTray: boolean,
  closeToTray: boolean,
  showNotifications: boolean,
  notificationSound: boolean
});
```

### Quick Actions
```typescript
// Update quick actions
await tray.updateQuickActions([
  { id: 'solar', label: 'Solar Calculator', route: '/solar', enabled: true },
  { id: 'crm', label: 'CRM', route: '/crm', enabled: true }
]);
```

### Utility
```typescript
// Check if tray is available
const available = await tray.isAvailable();
```

## Notification Types

| Type | Color | Use Case | Icon Flash |
|------|-------|----------|------------|
| `info` | Blue | General information | No |
| `success` | Green | Successful operations | No |
| `warning` | Yellow | Warnings | Yes |
| `error` | Red | Errors | Yes |

## Icon States

| State | Use Case |
|-------|----------|
| `normal` | Default state |
| `busy` | Long-running operations |
| `error` | Error occurred |
| `warning` | Warning condition |

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Show/Hide Window | Ctrl+Shift+H | Cmd+Shift+H |
| Dashboard | Ctrl+Shift+D | Cmd+Shift+D |
| New Calculation | Ctrl+Shift+N | Cmd+Shift+N |
| Quit | Ctrl+Q | Cmd+Q |

## User Preferences

### Minimize to Tray
- **Default**: Enabled
- **Behavior**: Minimizing hides to tray instead of taskbar
- **Access**: Tray menu → Tray Preferences

### Close to Tray
- **Default**: Disabled
- **Behavior**: Closing hides to tray instead of quitting
- **Access**: Tray menu → Tray Preferences

### Show Notifications
- **Default**: Enabled
- **Behavior**: Show desktop notifications
- **Access**: Tray menu → Tray Preferences

### Notification Sound
- **Default**: Enabled
- **Behavior**: Play sound with notifications
- **Access**: Tray menu → Tray Preferences

## Common Patterns

### Long Operation
```typescript
// Start
await tray.updateIcon('busy');
await tray.updateTooltip('Calculating...');

// Complete
await tray.updateIcon('normal');
await tray.updateTooltip('Solar Calculator Pro');
await tray.showNotification('Complete', 'Calculation finished', 'success');
```

### Error Handling
```typescript
try {
  // Operation
} catch (error) {
  await tray.updateIcon('error');
  await tray.showNotification('Error', error.message, 'error');
  await tray.flash(5000);
}
```

### Project Management
```typescript
// When project is opened/saved
await tray.addRecentProject({
  id: project.id,
  name: project.name,
  date: new Date().toISOString()
});
```

## Platform Differences

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Icon Size | 16x16 | 22x22 | 22x22 |
| Icon Flash | ✓ | ✗ | ✓ |
| Template Image | ✗ | ✓ | ✗ |
| Balloon Notifications | ✓ | ✗ | ✗ |
| Notification Center | ✗ | ✓ | Varies |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tray icon not visible | Check `tray.isAvailable()` |
| Notifications not showing | Check preferences and system settings |
| Window not restoring | Click tray icon or use "Show Window" |
| Menu not updating | Preferences update automatically |

## Best Practices

1. ✓ Use notifications sparingly
2. ✓ Update icon state during operations
3. ✓ Keep notification messages concise
4. ✓ Add projects to recent list when opened
5. ✓ Return icon to normal state after operations
6. ✗ Don't spam notifications
7. ✗ Don't flash icon unnecessarily
8. ✗ Don't show notifications for every action

## Example: Complete Workflow

```typescript
async function performCalculation() {
  try {
    // Start
    await window.electronAPI.tray.updateIcon('busy');
    await window.electronAPI.tray.updateTooltip('Calculating solar system...');
    
    // Perform calculation
    const result = await calculateSolarSystem(inputs);
    
    // Save project
    const project = await saveProject(result);
    await window.electronAPI.tray.addRecentProject({
      id: project.id,
      name: project.name
    });
    
    // Complete
    await window.electronAPI.tray.updateIcon('normal');
    await window.electronAPI.tray.updateTooltip('Solar Calculator Pro');
    await window.electronAPI.tray.showNotification(
      'Calculation Complete',
      `System size: ${result.systemSize} kWp`,
      'success'
    );
    
  } catch (error) {
    // Error
    await window.electronAPI.tray.updateIcon('error');
    await window.electronAPI.tray.showNotification(
      'Calculation Failed',
      error.message,
      'error'
    );
    await window.electronAPI.tray.flash(5000);
    
    // Reset after delay
    setTimeout(async () => {
      await window.electronAPI.tray.updateIcon('normal');
    }, 10000);
  }
}
```

## Related Documentation

- [System Tray Guide](./SYSTEM_TRAY_GUIDE.md) - Complete documentation
- [Native Menu Guide](./NATIVE_MENU_GUIDE.md) - Application menu
- [Notifications](./NOTIFICATIONS.md) - Notification system
