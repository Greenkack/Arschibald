# Auto-Update System - Quick Reference

## Quick Start

### For Developers

```bash
# 1. Build application
npm run electron:build

# 2. Generate update manifest
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release

# 3. Test locally
node scripts/update-server.js --port 3000 --dir ./release

# 4. Publish to GitHub
npx electron-builder --publish always
```

### For Users

1. **Check for Updates**: Help → Check for Updates
2. **Configure Updates**: Settings → Updates
3. **Install Update**: Click "Restart Now" when prompted

## Configuration

### Environment Variables

```bash
# GitHub
export GH_TOKEN=your_token

# Generic Server
export UPDATE_SERVER_URL=https://your-server.com/updates

# Code Signing (Windows)
export WIN_CSC_LINK=path/to/cert.pfx
export WIN_CSC_KEY_PASSWORD=password

# Code Signing (macOS)
export APPLE_ID=your_apple_id
export APPLE_ID_PASSWORD=app_password
```

### Update Channels

| Channel | Purpose | Check Interval | Stability |
|---------|---------|----------------|-----------|
| Stable | Production | 1 hour | High |
| Beta | Testing | 30 minutes | Medium |
| Alpha | Development | 15 minutes | Low |

## Commands

### Build Commands

```bash
# Build for current platform
npm run electron:build

# Build for specific platform
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux

# Build and publish
npx electron-builder --publish always
```

### Manifest Generation

```bash
# Windows
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release

# macOS
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform mac \
  --output ./release

# Linux
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform linux \
  --output ./release
```

### Local Testing

```bash
# Start update server
node scripts/update-server.js --port 3000 --dir ./release

# With custom host
node scripts/update-server.js --port 3000 --dir ./release --host 0.0.0.0
```

## File Structure

```
solar-calculator-pro/
├── electron/
│   ├── updater.js              # Main updater logic
│   ├── update-config.js        # Configuration
│   └── main.js                 # Electron main process
├── scripts/
│   ├── generate-update-manifest.js  # Manifest generator
│   └── update-server.js        # Local test server
├── release/                    # Build output
│   ├── latest.yml             # Windows manifest
│   ├── latest-mac.yml         # macOS manifest
│   ├── latest-linux.yml       # Linux manifest
│   └── *.exe, *.dmg, *.AppImage  # Installers
└── docs/
    ├── AUTO_UPDATE_GUIDE.md   # Full documentation
    └── AUTO_UPDATE_QUICK_REFERENCE.md  # This file
```

## Update Manifest Format

```yaml
version: 1.0.0
releaseDate: '2024-01-01T00:00:00.000Z'
files:
  - url: Solar-Calculator-Pro-Setup-1.0.0.exe
    sha512: base64-encoded-hash
    size: 123456789
path: Solar-Calculator-Pro-Setup-1.0.0.exe
sha512: base64-encoded-hash
releaseNotes: |
  ## What's New
  - Feature 1
  - Feature 2
  
  ## Bug Fixes
  - Fix 1
  - Fix 2
```

## API Usage

### Frontend (React)

```typescript
import { useEffect, useState } from 'react';

function UpdateChecker() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState(null);

  useEffect(() => {
    // Listen for updates
    window.electronAPI.onUpdateAvailable((info) => {
      setUpdateAvailable(true);
      setUpdateInfo(info);
    });

    // Check for updates
    window.electronAPI.checkForUpdates();
  }, []);

  const handleDownload = () => {
    window.electronAPI.downloadUpdate();
  };

  const handleInstall = () => {
    window.electronAPI.installUpdate();
  };

  if (!updateAvailable) return null;

  return (
    <div>
      <h3>Update Available: {updateInfo.version}</h3>
      <button onClick={handleDownload}>Download</button>
      <button onClick={handleInstall}>Install</button>
    </div>
  );
}
```

### Electron Main Process

```javascript
const { setupAutoUpdater } = require('./electron/updater');

app.whenReady().then(() => {
  const mainWindow = createWindow();
  
  // Setup auto-updater
  setupAutoUpdater(mainWindow, {
    autoDownload: false,
    checkOnStartup: true,
    updateChannel: 'latest'
  });
});
```

## IPC Channels

### From Renderer to Main

```javascript
// Check for updates
window.electronAPI.checkForUpdates()

// Download update
window.electronAPI.downloadUpdate()

// Install update
window.electronAPI.installUpdate()

// Get version
const version = await window.electronAPI.getVersion()

// Get update info
const info = await window.electronAPI.getUpdateInfo()

// Set preferences
await window.electronAPI.setUpdatePreferences({
  autoDownload: true,
  checkInterval: 3600000,
  updateChannel: 'beta'
})
```

### From Main to Renderer

```javascript
// Update available
window.electronAPI.onUpdateAvailable((info) => {
  // info: { version, releaseDate, releaseNotes, ... }
})

// Checking for update
window.electronAPI.onUpdateChecking(() => {
  // Show checking indicator
})

// No update available
window.electronAPI.onUpdateNotAvailable(() => {
  // Hide checking indicator
})

// Download progress
window.electronAPI.onUpdateProgress((progress) => {
  // progress: { percent, transferred, total, bytesPerSecond }
})

// Update downloaded
window.electronAPI.onUpdateDownloaded((info) => {
  // Show install prompt
})

// Update error
window.electronAPI.onUpdateError((error) => {
  // Show error message
})
```

## Troubleshooting

### Quick Fixes

| Problem | Solution |
|---------|----------|
| Update check fails | Check internet connection, verify server URL |
| Download fails | Check disk space, verify file permissions |
| Install fails | Close all app instances, run as admin |
| Wrong version | Clear cache, reinstall manually |

### Debug Commands

```bash
# Enable debug logging
DEBUG=electron-updater npm run electron:dev

# View logs
# Windows: %APPDATA%\solar-calculator-pro\logs\
# macOS: ~/Library/Logs/solar-calculator-pro/
# Linux: ~/.config/solar-calculator-pro/logs/
```

### Common Issues

```javascript
// Issue: Update server not found
// Fix: Check update-config.js
const config = require('./electron/update-config');
console.log('Update server:', config.getUpdateServerConfig());

// Issue: Code signing fails
// Fix: Verify certificates
console.log('CSC_LINK:', process.env.CSC_LINK);
console.log('WIN_CSC_LINK:', process.env.WIN_CSC_LINK);

// Issue: Manifest not found
// Fix: Generate manifest
node scripts/generate-update-manifest.js --version 1.0.0 --platform win --output ./release
```

## Version Management

### Semantic Versioning

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (Patch: Bug fixes)
1.0.0 → 1.1.0  (Minor: New features)
1.0.0 → 2.0.0  (Major: Breaking changes)
```

### Update package.json

```json
{
  "version": "1.0.1"
}
```

### Git Tags

```bash
# Create tag
git tag -a v1.0.1 -m "Version 1.0.1"

# Push tag
git push origin v1.0.1

# List tags
git tag -l
```

## Security Checklist

- [ ] Use HTTPS for update server
- [ ] Sign all releases
- [ ] Verify SHA512 hashes
- [ ] Test updates before publishing
- [ ] Keep certificates secure
- [ ] Monitor update logs
- [ ] Have rollback plan

## Resources

- **Documentation**: `docs/AUTO_UPDATE_GUIDE.md`
- **electron-updater**: https://www.electron.build/auto-update
- **Code Signing**: https://www.electron.build/code-signing
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github

## Support

- **Issues**: https://github.com/your-username/solar-calculator-pro/issues
- **Email**: support@yourcompany.com
- **Logs**: Check application logs directory
