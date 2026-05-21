# Update UI Guide

## Overview

The Update UI system provides a complete set of React components for managing application updates in the Solar Calculator Pro Electron application. It includes notification dialogs, progress tracking, preferences management, and release notes display.

## Table of Contents

1. [Components](#components)
2. [Custom Hook](#custom-hook)
3. [Integration](#integration)
4. [Styling](#styling)
5. [User Experience](#user-experience)
6. [Best Practices](#best-practices)

## Components

### UpdateNotification

Displays when a new update is available with version information and release notes.

**Props:**
```typescript
interface UpdateNotificationProps {
  visible: boolean;
  updateInfo: UpdateInfo | null;
  onDownload: () => void;
  onSkipVersion: () => void;
  onRemindLater: () => void;
  onClose: () => void;
}
```

**Features:**
- Version comparison (current vs. new)
- Release date display
- Formatted release notes with markdown support
- Channel indicator (stable/beta/alpha)
- Skip version checkbox
- External release notes link

**Usage:**
```tsx
<UpdateNotification
  visible={showNotification}
  updateInfo={updateInfo}
  onDownload={() => downloadUpdate()}
  onSkipVersion={() => skipVersion()}
  onRemindLater={() => setShowNotification(false)}
  onClose={() => setShowNotification(false)}
/>
```

### UpdateProgress

Shows download progress with real-time statistics.

**Props:**
```typescript
interface UpdateProgressProps {
  visible: boolean;
  progress: ProgressInfo | null;
  version: string;
  onCancel: () => void;
}
```

**Features:**
- Progress bar with percentage
- Download speed (bytes/second)
- Transferred/total size display
- Estimated time remaining
- Cancel download button
- Animated progress indicator

**Usage:**
```tsx
<UpdateProgress
  visible={downloading}
  progress={downloadProgress}
  version={updateInfo?.version || ''}
  onCancel={() => cancelDownload()}
/>
```

### UpdateReady

Displays when update is downloaded and ready to install.

**Props:**
```typescript
interface UpdateReadyProps {
  visible: boolean;
  version: string;
  onInstallNow: () => void;
  onInstallLater: () => void;
}
```

**Features:**
- Success indicator
- Version display
- Two installation options:
  - Restart and install now
  - Install on quit
- Clear option descriptions
- Data preservation message

**Usage:**
```tsx
<UpdateReady
  visible={updateReady}
  version={updateInfo?.version || ''}
  onInstallNow={() => installUpdate()}
  onInstallLater={() => setUpdateReady(false)}
/>
```

### UpdatePreferences

Allows users to configure update settings.

**Props:**
```typescript
interface UpdatePreferencesProps {
  preferences: UpdatePreferencesData;
  currentVersion: string;
  onSave: (preferences: UpdatePreferencesData) => Promise<void>;
  onCheckNow: () => void;
  onClearSkipVersion: () => void;
}
```

**Features:**
- Auto-download toggle
- Auto-install on quit toggle
- Check on startup toggle
- Notify on no update toggle
- Update channel selection (stable/beta/alpha)
- Check frequency dropdown
- Skip version management
- Current version display
- Check for updates button
- Save/reset buttons

**Usage:**
```tsx
<UpdatePreferences
  preferences={preferences}
  currentVersion="1.0.0"
  onSave={async (prefs) => await setPreferences(prefs)}
  onCheckNow={() => checkForUpdates()}
  onClearSkipVersion={() => clearSkipVersion()}
/>
```

### ReleaseNotes

Displays formatted release notes with markdown support.

**Props:**
```typescript
interface ReleaseNotesProps {
  version?: string;
  onFetchNotes?: (version: string) => Promise<ReleaseNote>;
}
```

**Features:**
- Markdown to HTML conversion
- Version and date display
- Channel indicator
- Loading skeleton
- Error handling with retry
- Formatted content (headers, lists, code, links)

**Usage:**
```tsx
<ReleaseNotes
  version="1.1.0"
  onFetchNotes={async (version) => {
    const response = await fetch(`/api/releases/${version}`);
    return response.json();
  }}
/>
```

## Custom Hook

### useUpdate

Custom React hook for managing update state and actions.

**Returns:**
```typescript
interface UseUpdateReturn {
  // State
  updateAvailable: boolean;
  updateInfo: UpdateInfo | null;
  downloading: boolean;
  downloadProgress: ProgressInfo | null;
  updateReady: boolean;
  checking: boolean;
  error: string | null;
  preferences: UpdatePreferences | null;

  // Actions
  checkForUpdates: () => Promise<void>;
  downloadUpdate: () => Promise<void>;
  installUpdate: () => Promise<void>;
  skipVersion: () => Promise<void>;
  cancelDownload: () => Promise<void>;
  setPreferences: (prefs: UpdatePreferences) => Promise<void>;
  clearSkipVersion: () => Promise<void>;
}
```

**Features:**
- Automatic event listener setup
- State management for all update phases
- Error handling
- Preference persistence
- IPC communication with Electron

**Usage:**
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

// Check for updates
await checkForUpdates();

// Download update
if (updateAvailable) {
  await downloadUpdate();
}

// Install update
if (updateReady) {
  await installUpdate();
}
```

## Integration

### Complete Integration Example

```tsx
import React, { useEffect } from 'react';
import { Toast } from 'primereact/toast';
import {
  UpdateNotification,
  UpdateProgress,
  UpdateReady
} from './components/update';
import { useUpdate } from './hooks/useUpdate';

export const App: React.FC = () => {
  const toast = React.useRef<Toast>(null);
  const {
    updateAvailable,
    updateInfo,
    downloading,
    downloadProgress,
    updateReady,
    error,
    checkForUpdates,
    downloadUpdate,
    installUpdate,
    skipVersion
  } = useUpdate();

  const [showNotification, setShowNotification] = React.useState(false);

  // Show notification when update is available
  useEffect(() => {
    if (updateAvailable) {
      setShowNotification(true);
    }
  }, [updateAvailable]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Update Error',
        detail: error,
        life: 5000
      });
    }
  }, [error]);

  // Check for updates on mount
  useEffect(() => {
    checkForUpdates();
  }, []);

  return (
    <div>
      <Toast ref={toast} />
      
      {/* Your app content */}
      
      <UpdateNotification
        visible={showNotification}
        updateInfo={updateInfo}
        onDownload={() => {
          downloadUpdate();
          setShowNotification(false);
        }}
        onSkipVersion={() => {
          skipVersion();
          setShowNotification(false);
        }}
        onRemindLater={() => setShowNotification(false)}
        onClose={() => setShowNotification(false)}
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
        onInstallNow={() => installUpdate()}
        onInstallLater={() => {}}
      />
    </div>
  );
};
```

### Settings Page Integration

```tsx
import React from 'react';
import { UpdatePreferences } from './components/update';
import { useUpdate } from './hooks/useUpdate';

export const SettingsPage: React.FC = () => {
  const {
    preferences,
    setPreferences,
    checkForUpdates,
    clearSkipVersion
  } = useUpdate();

  if (!preferences) return null;

  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <UpdatePreferences
        preferences={preferences}
        currentVersion="1.0.0"
        onSave={setPreferences}
        onCheckNow={checkForUpdates}
        onClearSkipVersion={clearSkipVersion}
      />
    </div>
  );
};
```

## Styling

### Theme Customization

All components support dark mode and can be customized via CSS variables:

```css
:root {
  /* Update notification colors */
  --update-notification-gradient-start: #667eea;
  --update-notification-gradient-end: #764ba2;
  
  /* Update progress colors */
  --update-progress-gradient-start: #4299e1;
  --update-progress-gradient-end: #667eea;
  
  /* Update ready colors */
  --update-ready-gradient-start: #48bb78;
  --update-ready-gradient-end: #38a169;
}
```

### Custom Styling

Override component styles:

```css
.update-notification-dialog {
  /* Custom styles */
}

.update-progress-bar .p-progressbar-value {
  background: linear-gradient(90deg, #your-color-1, #your-color-2);
}
```

## User Experience

### Update Flow

1. **Check for Updates**
   - Automatic on startup (if enabled)
   - Manual via menu or button
   - Periodic background checks

2. **Update Available**
   - Notification dialog appears
   - Shows version info and release notes
   - User can download, skip, or remind later

3. **Downloading**
   - Progress dialog shows download status
   - Real-time speed and time estimates
   - Can cancel download

4. **Ready to Install**
   - Success dialog appears
   - Options to install now or on quit
   - Data preservation message

5. **Installation**
   - App closes and updates
   - Automatic restart with new version

### User Preferences

Users can customize:
- **Auto-download**: Download updates automatically
- **Auto-install**: Install when closing app
- **Check on startup**: Check for updates at launch
- **Check frequency**: How often to check
- **Update channel**: Stable, beta, or alpha
- **Skip versions**: Skip specific versions

### Notifications

- **Update Available**: New version ready to download
- **Download Complete**: Update ready to install
- **No Updates**: Already on latest version (optional)
- **Error**: Update check or download failed

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```tsx
const { error } = useUpdate();

useEffect(() => {
  if (error) {
    // Show user-friendly error message
    toast.current?.show({
      severity: 'error',
      summary: 'Update Error',
      detail: error,
      life: 5000
    });
  }
}, [error]);
```

### 2. Loading States

Show loading indicators during operations:

```tsx
const { checking } = useUpdate();

{checking && (
  <ProgressSpinner />
)}
```

### 3. User Feedback

Provide clear feedback for all actions:

```tsx
const handleSavePreferences = async (prefs) => {
  try {
    await setPreferences(prefs);
    toast.current?.show({
      severity: 'success',
      summary: 'Saved',
      detail: 'Preferences updated successfully'
    });
  } catch (error) {
    toast.current?.show({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save preferences'
    });
  }
};
```

### 4. Accessibility

Ensure components are accessible:

```tsx
<Button
  label="Download Update"
  icon="pi pi-download"
  onClick={downloadUpdate}
  aria-label="Download the available update"
  autoFocus
/>
```

### 5. Responsive Design

Components are responsive by default, but test on different screen sizes:

```css
@media (max-width: 768px) {
  .update-notification-dialog {
    width: 95vw !important;
  }
}
```

### 6. Testing

Test all update scenarios:

```tsx
// Test update available
mockUpdateAvailable({
  version: '1.1.0',
  releaseDate: new Date().toISOString()
});

// Test download progress
mockDownloadProgress({
  percent: 50,
  bytesPerSecond: 1024000,
  transferred: 5242880,
  total: 10485760
});

// Test update ready
mockUpdateReady({
  version: '1.1.0'
});
```

## API Reference

### Types

```typescript
interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  releaseNotesUrl?: string;
  currentVersion: string;
  updateChannel?: string;
}

interface ProgressInfo {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}

interface UpdatePreferences {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkOnStartup: boolean;
  checkInterval: number;
  updateChannel: string;
  skipVersion: string | null;
  notifyOnNoUpdate: boolean;
}

interface ReleaseNote {
  version: string;
  releaseDate: string;
  notes: string;
  channel?: string;
}
```

## Resources

- [Electron Auto-Update](https://www.electron.build/auto-update)
- [PrimeReact Components](https://primereact.org/)
- [React Hooks](https://react.dev/reference/react)
- [TypeScript](https://www.typescriptlang.org/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-username/solar-calculator-pro/issues
- Documentation: https://docs.yourcompany.com
- Email: support@yourcompany.com
