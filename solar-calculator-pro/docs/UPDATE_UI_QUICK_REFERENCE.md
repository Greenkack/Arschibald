# Update UI Quick Reference

## Quick Start

### 1. Import Components

```tsx
import {
  UpdateNotification,
  UpdateProgress,
  UpdateReady,
  UpdatePreferences,
  ReleaseNotes
} from './components/update';
import { useUpdate } from './hooks/useUpdate';
```

### 2. Use the Hook

```tsx
const {
  updateAvailable,
  updateInfo,
  downloading,
  downloadProgress,
  updateReady,
  checkForUpdates,
  downloadUpdate,
  installUpdate
} = useUpdate();
```

### 3. Add Components

```tsx
<UpdateNotification
  visible={updateAvailable}
  updateInfo={updateInfo}
  onDownload={downloadUpdate}
  onSkipVersion={skipVersion}
  onRemindLater={() => {}}
  onClose={() => {}}
/>

<UpdateProgress
  visible={downloading}
  progress={downloadProgress}
  version={updateInfo?.version || ''}
  onCancel={() => {}}
/>

<UpdateReady
  visible={updateReady}
  version={updateInfo?.version || ''}
  onInstallNow={installUpdate}
  onInstallLater={() => {}}
/>
```

## Component Props

### UpdateNotification

| Prop | Type | Description |
|------|------|-------------|
| `visible` | `boolean` | Show/hide dialog |
| `updateInfo` | `UpdateInfo \| null` | Update information |
| `onDownload` | `() => void` | Download button handler |
| `onSkipVersion` | `() => void` | Skip version handler |
| `onRemindLater` | `() => void` | Remind later handler |
| `onClose` | `() => void` | Close dialog handler |

### UpdateProgress

| Prop | Type | Description |
|------|------|-------------|
| `visible` | `boolean` | Show/hide dialog |
| `progress` | `ProgressInfo \| null` | Download progress |
| `version` | `string` | Version being downloaded |
| `onCancel` | `() => void` | Cancel download handler |

### UpdateReady

| Prop | Type | Description |
|------|------|-------------|
| `visible` | `boolean` | Show/hide dialog |
| `version` | `string` | Version ready to install |
| `onInstallNow` | `() => void` | Install now handler |
| `onInstallLater` | `() => void` | Install later handler |

### UpdatePreferences

| Prop | Type | Description |
|------|------|-------------|
| `preferences` | `UpdatePreferencesData` | Current preferences |
| `currentVersion` | `string` | Current app version |
| `onSave` | `(prefs) => Promise<void>` | Save preferences handler |
| `onCheckNow` | `() => void` | Check for updates handler |
| `onClearSkipVersion` | `() => void` | Clear skip version handler |

### ReleaseNotes

| Prop | Type | Description |
|------|------|-------------|
| `version` | `string` | Version to show notes for |
| `onFetchNotes` | `(version) => Promise<ReleaseNote>` | Fetch notes function |

## Hook API

### useUpdate()

**State:**
- `updateAvailable: boolean` - Update is available
- `updateInfo: UpdateInfo | null` - Update information
- `downloading: boolean` - Download in progress
- `downloadProgress: ProgressInfo | null` - Download progress
- `updateReady: boolean` - Update ready to install
- `checking: boolean` - Checking for updates
- `error: string | null` - Error message
- `preferences: UpdatePreferences | null` - User preferences

**Actions:**
- `checkForUpdates()` - Check for updates
- `downloadUpdate()` - Download update
- `installUpdate()` - Install update
- `skipVersion()` - Skip current version
- `cancelDownload()` - Cancel download
- `setPreferences(prefs)` - Save preferences
- `clearSkipVersion()` - Clear skipped version

## Types

### UpdateInfo

```typescript
interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  releaseNotesUrl?: string;
  currentVersion: string;
  updateChannel?: string;
}
```

### ProgressInfo

```typescript
interface ProgressInfo {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}
```

### UpdatePreferences

```typescript
interface UpdatePreferences {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkOnStartup: boolean;
  checkInterval: number;
  updateChannel: string;
  skipVersion: string | null;
  notifyOnNoUpdate: boolean;
}
```

## Common Patterns

### Basic Integration

```tsx
function App() {
  const { updateAvailable, updateInfo, downloadUpdate } = useUpdate();
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    if (updateAvailable) setShowDialog(true);
  }, [updateAvailable]);

  return (
    <UpdateNotification
      visible={showDialog}
      updateInfo={updateInfo}
      onDownload={() => {
        downloadUpdate();
        setShowDialog(false);
      }}
      onSkipVersion={() => setShowDialog(false)}
      onRemindLater={() => setShowDialog(false)}
      onClose={() => setShowDialog(false)}
    />
  );
}
```

### With Toast Notifications

```tsx
function App() {
  const toast = useRef<Toast>(null);
  const { error, updateReady } = useUpdate();

  useEffect(() => {
    if (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Update Error',
        detail: error
      });
    }
  }, [error]);

  useEffect(() => {
    if (updateReady) {
      toast.current?.show({
        severity: 'success',
        summary: 'Update Ready',
        detail: 'Update is ready to install'
      });
    }
  }, [updateReady]);

  return <Toast ref={toast} />;
}
```

### Settings Page

```tsx
function SettingsPage() {
  const {
    preferences,
    setPreferences,
    checkForUpdates,
    clearSkipVersion
  } = useUpdate();

  return (
    <UpdatePreferences
      preferences={preferences}
      currentVersion="1.0.0"
      onSave={setPreferences}
      onCheckNow={checkForUpdates}
      onClearSkipVersion={clearSkipVersion}
    />
  );
}
```

### Release Notes Page

```tsx
function ReleaseNotesPage() {
  const fetchNotes = async (version: string) => {
    const response = await fetch(`/api/releases/${version}`);
    return response.json();
  };

  return (
    <ReleaseNotes
      version="1.1.0"
      onFetchNotes={fetchNotes}
    />
  );
}
```

## Styling

### CSS Variables

```css
:root {
  --update-notification-gradient-start: #667eea;
  --update-notification-gradient-end: #764ba2;
  --update-progress-gradient-start: #4299e1;
  --update-progress-gradient-end: #667eea;
  --update-ready-gradient-start: #48bb78;
  --update-ready-gradient-end: #38a169;
}
```

### Custom Styles

```css
.update-notification-dialog {
  /* Override dialog styles */
}

.update-progress-bar .p-progressbar-value {
  /* Override progress bar */
}

.update-ready-dialog .option-card:hover {
  /* Override hover effect */
}
```

## Event Handling

### Update Available

```tsx
useEffect(() => {
  if (updateAvailable && updateInfo) {
    console.log('Update available:', updateInfo.version);
    // Show notification
  }
}, [updateAvailable, updateInfo]);
```

### Download Progress

```tsx
useEffect(() => {
  if (downloading && downloadProgress) {
    console.log('Progress:', downloadProgress.percent);
    // Update UI
  }
}, [downloading, downloadProgress]);
```

### Update Ready

```tsx
useEffect(() => {
  if (updateReady) {
    console.log('Update ready to install');
    // Show ready dialog
  }
}, [updateReady]);
```

### Errors

```tsx
useEffect(() => {
  if (error) {
    console.error('Update error:', error);
    // Show error message
  }
}, [error]);
```

## Testing

### Mock Update Available

```tsx
const mockUpdateInfo = {
  version: '1.1.0',
  releaseDate: new Date().toISOString(),
  currentVersion: '1.0.0',
  releaseNotes: '# What\'s New\n- Feature 1\n- Feature 2'
};

// Trigger update available
window.electronAPI.onUpdateAvailable(mockUpdateInfo);
```

### Mock Download Progress

```tsx
const mockProgress = {
  percent: 50,
  bytesPerSecond: 1024000,
  transferred: 5242880,
  total: 10485760
};

// Trigger progress update
window.electronAPI.onUpdateProgress(mockProgress);
```

### Mock Update Ready

```tsx
const mockUpdateInfo = {
  version: '1.1.0',
  releaseDate: new Date().toISOString(),
  currentVersion: '1.0.0'
};

// Trigger update ready
window.electronAPI.onUpdateDownloaded(mockUpdateInfo);
```

## Troubleshooting

### Dialog Not Showing

```tsx
// Check visibility state
console.log('Update available:', updateAvailable);
console.log('Show dialog:', showDialog);

// Ensure state is updated
useEffect(() => {
  if (updateAvailable) {
    setShowDialog(true);
  }
}, [updateAvailable]);
```

### Progress Not Updating

```tsx
// Check progress object
console.log('Progress:', downloadProgress);

// Ensure component is visible
console.log('Downloading:', downloading);
```

### Preferences Not Saving

```tsx
// Check save function
const handleSave = async (prefs) => {
  try {
    await setPreferences(prefs);
    console.log('Saved successfully');
  } catch (error) {
    console.error('Save failed:', error);
  }
};
```

## File Structure

```
frontend/src/
├── components/
│   └── update/
│       ├── UpdateNotification.tsx
│       ├── UpdateNotification.css
│       ├── UpdateProgress.tsx
│       ├── UpdateProgress.css
│       ├── UpdateReady.tsx
│       ├── UpdateReady.css
│       ├── UpdatePreferences.tsx
│       ├── UpdatePreferences.css
│       ├── ReleaseNotes.tsx
│       ├── ReleaseNotes.css
│       └── index.ts
├── hooks/
│   └── useUpdate.ts
└── examples/
    ├── UpdateSystemDemo.tsx
    └── UpdateSystemDemo.css
```

## Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "primereact": "^10.0.0",
    "primeicons": "^6.0.0"
  }
}
```

## Resources

- Full Guide: `docs/UPDATE_UI_GUIDE.md`
- Auto-Update Guide: `docs/AUTO_UPDATE_GUIDE.md`
- PrimeReact: https://primereact.org/
- Electron: https://www.electronjs.org/

## Support

- GitHub: https://github.com/your-username/solar-calculator-pro
- Docs: https://docs.yourcompany.com
- Email: support@yourcompany.com
