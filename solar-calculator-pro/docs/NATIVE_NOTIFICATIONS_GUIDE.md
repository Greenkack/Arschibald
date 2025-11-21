# Native Notifications System Guide

## Overview

The Solar Calculator Pro application includes a comprehensive native notification system that provides desktop notifications for various events and actions. This system is built on Electron's native notification API and provides a rich set of features for managing and customizing notifications.

## Features

### Notification Types

The system supports the following notification types:

1. **Calculation Complete** - Shown when a solar or heat pump calculation finishes
2. **Update Available** - Notifies users when a new version is available
3. **Error Notifications** - Critical errors that require user attention
4. **Warning Notifications** - Important warnings
5. **Info Notifications** - General information messages
6. **PDF Complete** - Shown when PDF generation finishes
7. **Export Complete** - Notifies when data export completes
8. **Backup Complete** - Confirms successful backup creation
9. **Sync Complete** - Notifies when data synchronization finishes
10. **Custom Notifications** - User-defined notifications

### User Preferences

Users can customize their notification experience through:

- **Enable/Disable** - Turn all notifications on or off
- **Notification Types** - Enable/disable specific notification types
- **Sound** - Toggle notification sounds
- **Do Not Disturb** - Temporarily disable all notifications
- **Quiet Hours** - Set time periods when notifications are suppressed

### Notification History

The system maintains a history of recent notifications, allowing users to:

- View past notifications
- Search and filter by type
- Clear history

## Architecture

### Backend (Electron Main Process)

**File:** `electron/notifications.js`

The `NotificationManager` class handles all notification logic:

```javascript
const NotificationManager = require('./notifications');
const notificationManager = new NotificationManager();

// Show a calculation complete notification
notificationManager.showCalculationComplete('My Project', 'Solar');

// Show an error notification
notificationManager.showError('Calculation failed', { details: '...' });

// Get user preferences
const preferences = notificationManager.getPreferences();

// Update preferences
notificationManager.updatePreferences({
  sound: false,
  doNotDisturb: true
});
```

### Frontend (React)

**Hook:** `hooks/useNotifications.ts`

The `useNotifications` hook provides React integration:

```typescript
import { useNotifications } from '../hooks/useNotifications';

function MyComponent() {
  const {
    showCalculationComplete,
    showError,
    preferences,
    updatePreferences
  } = useNotifications();

  const handleCalculation = async () => {
    // ... perform calculation ...
    await showCalculationComplete('Project Name', 'Solar');
  };

  return (
    // ... component JSX ...
  );
}
```

## Usage Examples

### Showing Notifications

#### Calculation Complete

```typescript
await showCalculationComplete('Mein Projekt', 'Solar');
```

#### Update Available

```typescript
await showUpdateAvailable('2.0.0', 'New features and bug fixes');
```

#### Error

```typescript
await showError('Berechnung fehlgeschlagen', {
  code: 'CALC_ERROR',
  details: 'Invalid input parameters'
});
```

#### Warning

```typescript
await showWarning('Unvollständige Daten', {
  missingFields: ['roofArea', 'location']
});
```

#### Custom Notification

```typescript
await showCustom(
  'Benutzerdefinierte Nachricht',
  'Dies ist eine benutzerdefinierte Benachrichtigung',
  {
    urgency: 'normal',
    icon: 'custom-icon.png'
  }
);
```

### Managing Preferences

#### Get Current Preferences

```typescript
const preferences = await getPreferences();
console.log(preferences);
// {
//   enabled: true,
//   calculationComplete: true,
//   updateAvailable: true,
//   errors: true,
//   warnings: true,
//   info: false,
//   sound: true,
//   doNotDisturb: false,
//   quietHours: {
//     enabled: false,
//     start: '22:00',
//     end: '08:00'
//   }
// }
```

#### Update Preferences

```typescript
await updatePreferences({
  sound: false,
  info: true
});
```

#### Enable/Disable All Notifications

```typescript
await setEnabled(false); // Disable all
await setEnabled(true);  // Enable all
```

#### Set Do Not Disturb

```typescript
await setDoNotDisturb(true);  // Enable DND
await setDoNotDisturb(false); // Disable DND
```

#### Configure Quiet Hours

```typescript
await setQuietHours(true, '22:00', '08:00');
```

### Working with History

#### Load History

```typescript
await loadHistory(50); // Load last 50 notifications
```

#### Clear History

```typescript
await clearHistory();
```

## UI Components

### Notification Preferences Component

Located at: `frontend/src/components/settings/NotificationPreferences.tsx`

This component provides a complete UI for managing notification settings:

```typescript
import { NotificationPreferences } from './components/settings/NotificationPreferences';

function SettingsPage() {
  return (
    <div>
      <h1>Einstellungen</h1>
      <NotificationPreferences />
    </div>
  );
}
```

### Notification History Component

Located at: `frontend/src/components/settings/NotificationHistory.tsx`

This component displays the notification history with search and filtering:

```typescript
import { NotificationHistory } from './components/settings/NotificationHistory';

function HistoryPage() {
  return (
    <div>
      <h1>Benachrichtigungsverlauf</h1>
      <NotificationHistory />
    </div>
  );
}
```

## Integration with Application Features

### Solar Calculator

```typescript
// In solar calculator component
const { showCalculationComplete, showError } = useNotifications();

const handleCalculate = async () => {
  try {
    const result = await calculateSolar(params);
    await showCalculationComplete(projectName, 'Solar');
  } catch (error) {
    await showError('Berechnung fehlgeschlagen', error);
  }
};
```

### PDF Generation

```typescript
// In PDF generation component
const { showPDFComplete, showError } = useNotifications();

const handleGeneratePDF = async () => {
  try {
    const pdfPath = await generatePDF(data);
    await showPDFComplete(pdfPath);
  } catch (error) {
    await showError('PDF-Erstellung fehlgeschlagen', error);
  }
};
```

### Auto-Updater Integration

```typescript
// In updater component
const { showUpdateAvailable } = useNotifications();

useEffect(() => {
  const unsubscribe = window.electronAPI.onUpdateAvailable((info) => {
    showUpdateAvailable(info.version, info.releaseNotes);
  });

  return unsubscribe;
}, [showUpdateAvailable]);
```

## Best Practices

### 1. Use Appropriate Notification Types

Choose the correct notification type for the context:
- Use `showError` for critical errors
- Use `showWarning` for important but non-critical issues
- Use `showInfo` for general information
- Use specific types (`showCalculationComplete`, `showPDFComplete`) for domain-specific events

### 2. Provide Meaningful Messages

```typescript
// Good
await showError('Berechnung fehlgeschlagen: Ungültige Dacheingabe', {
  field: 'roofArea',
  value: -10
});

// Bad
await showError('Error');
```

### 3. Respect User Preferences

Always check if notifications are enabled before showing them:

```typescript
const { preferences } = useNotifications();

if (preferences?.enabled && preferences?.info) {
  await showInfo('Information message');
}
```

### 4. Don't Spam Notifications

Avoid showing too many notifications in quick succession:

```typescript
// Bad - shows 10 notifications
for (let i = 0; i < 10; i++) {
  await showInfo(`Processing item ${i}`);
}

// Good - show one summary notification
await showInfo(`Processed 10 items successfully`);
```

### 5. Test Notifications

Use the test function to verify notifications are working:

```typescript
const { test } = useNotifications();

// Show a test notification
await test();
```

## Troubleshooting

### Notifications Not Showing

1. Check if notifications are enabled in preferences
2. Verify Do Not Disturb mode is off
3. Check if quiet hours are active
4. Ensure the notification type is enabled

### No Sound

1. Check if sound is enabled in preferences
2. Verify system sound settings
3. Check if system is muted

### Notifications Appearing at Wrong Times

1. Review quiet hours configuration
2. Check system time zone settings
3. Verify quiet hours start/end times

## API Reference

### NotificationManager Methods

#### `showCalculationComplete(projectName, calculationType)`
Shows a calculation complete notification.

**Parameters:**
- `projectName` (string): Name of the project
- `calculationType` (string): Type of calculation (e.g., 'Solar', 'Heat Pump')

**Returns:** Notification object or null

#### `showUpdateAvailable(version, releaseNotes)`
Shows an update available notification.

**Parameters:**
- `version` (string): New version number
- `releaseNotes` (string, optional): Release notes

**Returns:** Notification object or null

#### `showError(errorMessage, errorDetails)`
Shows an error notification.

**Parameters:**
- `errorMessage` (string): Error message
- `errorDetails` (any, optional): Additional error details

**Returns:** Notification object or null

#### `showWarning(warningMessage, details)`
Shows a warning notification.

**Parameters:**
- `warningMessage` (string): Warning message
- `details` (any, optional): Additional details

**Returns:** Notification object or null

#### `showInfo(infoMessage, details)`
Shows an info notification.

**Parameters:**
- `infoMessage` (string): Info message
- `details` (any, optional): Additional details

**Returns:** Notification object or null

#### `showPDFComplete(fileName)`
Shows a PDF generation complete notification.

**Parameters:**
- `fileName` (string): Name of the generated PDF file

**Returns:** Notification object or null

#### `showExportComplete(exportType, fileName)`
Shows an export complete notification.

**Parameters:**
- `exportType` (string): Type of export (e.g., 'Excel', 'CSV')
- `fileName` (string): Name of the exported file

**Returns:** Notification object or null

#### `showBackupComplete(backupName)`
Shows a backup complete notification.

**Parameters:**
- `backupName` (string): Name of the backup

**Returns:** Notification object or null

#### `showSyncComplete(itemCount)`
Shows a sync complete notification.

**Parameters:**
- `itemCount` (number): Number of items synchronized

**Returns:** Notification object or null

#### `showCustom(title, body, options)`
Shows a custom notification.

**Parameters:**
- `title` (string): Notification title
- `body` (string): Notification body
- `options` (object, optional): Additional options

**Returns:** Notification object or null

#### `getPreferences()`
Gets current notification preferences.

**Returns:** Preferences object

#### `updatePreferences(preferences)`
Updates notification preferences.

**Parameters:**
- `preferences` (object): Partial preferences object

**Returns:** void

#### `setEnabled(enabled)`
Enables or disables all notifications.

**Parameters:**
- `enabled` (boolean): Enable state

**Returns:** void

#### `setDoNotDisturb(enabled)`
Enables or disables Do Not Disturb mode.

**Parameters:**
- `enabled` (boolean): DND state

**Returns:** void

#### `setQuietHours(enabled, start, end)`
Configures quiet hours.

**Parameters:**
- `enabled` (boolean): Enable quiet hours
- `start` (string): Start time (HH:MM format)
- `end` (string): End time (HH:MM format)

**Returns:** void

#### `getHistory(limit)`
Gets notification history.

**Parameters:**
- `limit` (number, optional): Maximum number of notifications to return (default: 20)

**Returns:** Array of notification history items

#### `clearHistory()`
Clears notification history.

**Returns:** void

#### `test()`
Shows a test notification.

**Returns:** Notification object or null

## Security Considerations

1. **No Sensitive Data**: Never include sensitive information (passwords, tokens) in notifications
2. **User Control**: Always respect user preferences and provide opt-out options
3. **Rate Limiting**: Implement rate limiting to prevent notification spam
4. **Validation**: Validate all notification content before display

## Performance Considerations

1. **Async Operations**: All notification operations are asynchronous
2. **History Limit**: History is limited to 50 items to prevent memory issues
3. **Persistence**: Preferences are persisted to disk using electron-store
4. **Cleanup**: Old notifications are automatically cleaned up

## Future Enhancements

Potential future improvements:

1. **Action Buttons**: Add clickable action buttons to notifications
2. **Rich Content**: Support for images and formatted text
3. **Notification Groups**: Group related notifications
4. **Priority Levels**: Different priority levels for notifications
5. **Custom Sounds**: User-selectable notification sounds
6. **Notification Templates**: Predefined templates for common scenarios
7. **Analytics**: Track notification engagement metrics
8. **Cross-Device Sync**: Sync notification preferences across devices

## Support

For issues or questions about the notification system:

1. Check this documentation
2. Review the code examples
3. Test with the built-in test function
4. Check the console for error messages
5. Contact the development team

## Changelog

### Version 1.0.0
- Initial implementation
- Basic notification types
- User preferences
- Notification history
- Do Not Disturb mode
- Quiet hours
- React integration
- UI components
