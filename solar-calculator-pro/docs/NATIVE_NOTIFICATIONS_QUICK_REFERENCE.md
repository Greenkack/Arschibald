# Native Notifications Quick Reference

## Quick Start

### Basic Usage

```typescript
import { useNotifications } from '../hooks/useNotifications';

function MyComponent() {
  const { showCalculationComplete, showError } = useNotifications();

  const handleAction = async () => {
    try {
      // Your code here
      await showCalculationComplete('Project', 'Solar');
    } catch (error) {
      await showError('Action failed', error);
    }
  };
}
```

## Common Notification Types

### Calculation Complete
```typescript
await showCalculationComplete('Project Name', 'Solar');
```

### Update Available
```typescript
await showUpdateAvailable('2.0.0', 'Release notes');
```

### Error
```typescript
await showError('Error message', { details: '...' });
```

### Warning
```typescript
await showWarning('Warning message', { details: '...' });
```

### Info
```typescript
await showInfo('Info message', { details: '...' });
```

### PDF Complete
```typescript
await showPDFComplete('document.pdf');
```

### Export Complete
```typescript
await showExportComplete('Excel', 'export.xlsx');
```

### Custom
```typescript
await showCustom('Title', 'Body', { urgency: 'normal' });
```

## Preferences Management

### Get Preferences
```typescript
const preferences = await getPreferences();
```

### Update Preferences
```typescript
await updatePreferences({ sound: false, info: true });
```

### Enable/Disable All
```typescript
await setEnabled(false); // Disable
await setEnabled(true);  // Enable
```

### Do Not Disturb
```typescript
await setDoNotDisturb(true);  // Enable
await setDoNotDisturb(false); // Disable
```

### Quiet Hours
```typescript
await setQuietHours(true, '22:00', '08:00');
```

## History Management

### Load History
```typescript
await loadHistory(50);
```

### Clear History
```typescript
await clearHistory();
```

## UI Components

### Preferences Component
```typescript
import { NotificationPreferences } from './components/settings/NotificationPreferences';

<NotificationPreferences />
```

### History Component
```typescript
import { NotificationHistory } from './components/settings/NotificationHistory';

<NotificationHistory />
```

## Testing

### Test Notification
```typescript
await test();
```

## Preference Structure

```typescript
{
  enabled: boolean;
  calculationComplete: boolean;
  updateAvailable: boolean;
  errors: boolean;
  warnings: boolean;
  info: boolean;
  sound: boolean;
  doNotDisturb: boolean;
  quietHours: {
    enabled: boolean;
    start: string; // 'HH:MM'
    end: string;   // 'HH:MM'
  };
}
```

## Best Practices

✅ **DO:**
- Use appropriate notification types
- Provide meaningful messages
- Respect user preferences
- Test notifications
- Handle errors gracefully

❌ **DON'T:**
- Spam notifications
- Include sensitive data
- Ignore user preferences
- Show generic error messages
- Block UI with notifications

## Common Patterns

### With Error Handling
```typescript
try {
  const result = await performAction();
  await showInfo('Action completed');
} catch (error) {
  await showError('Action failed', error);
}
```

### With Loading State
```typescript
const [loading, setLoading] = useState(false);

const handleAction = async () => {
  setLoading(true);
  try {
    await performAction();
    await showInfo('Success');
  } catch (error) {
    await showError('Failed', error);
  } finally {
    setLoading(false);
  }
};
```

### Conditional Notifications
```typescript
const { preferences } = useNotifications();

if (preferences?.enabled && preferences?.info) {
  await showInfo('Message');
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Notifications not showing | Check preferences, DND mode, quiet hours |
| No sound | Check sound preference and system settings |
| Wrong timing | Review quiet hours configuration |
| History not loading | Call `loadHistory()` explicitly |

## File Locations

- **Backend:** `electron/notifications.js`
- **Hook:** `frontend/src/hooks/useNotifications.ts`
- **Preferences UI:** `frontend/src/components/settings/NotificationPreferences.tsx`
- **History UI:** `frontend/src/components/settings/NotificationHistory.tsx`
- **Documentation:** `docs/NATIVE_NOTIFICATIONS_GUIDE.md`

## API Summary

| Method | Purpose |
|--------|---------|
| `showCalculationComplete()` | Calculation finished |
| `showUpdateAvailable()` | Update ready |
| `showError()` | Error occurred |
| `showWarning()` | Warning issued |
| `showInfo()` | Information |
| `showPDFComplete()` | PDF generated |
| `showExportComplete()` | Export finished |
| `showBackupComplete()` | Backup created |
| `showSyncComplete()` | Sync finished |
| `showCustom()` | Custom notification |
| `getPreferences()` | Get settings |
| `updatePreferences()` | Update settings |
| `setEnabled()` | Enable/disable all |
| `setDoNotDisturb()` | DND mode |
| `setQuietHours()` | Quiet hours |
| `getHistory()` | Get history |
| `clearHistory()` | Clear history |
| `test()` | Test notification |

## Support

For detailed information, see: `docs/NATIVE_NOTIFICATIONS_GUIDE.md`
