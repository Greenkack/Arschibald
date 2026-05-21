# Auto-Update System Guide

## Overview

The Solar Calculator Pro application includes a comprehensive auto-update system that allows users to receive updates automatically without manual downloads. The system is built on `electron-updater` and supports multiple update distribution methods.

## Table of Contents

1. [Features](#features)
2. [Update Channels](#update-channels)
3. [Configuration](#configuration)
4. [Update Servers](#update-servers)
5. [Building and Publishing](#building-and-publishing)
6. [Testing Updates](#testing-updates)
7. [User Experience](#user-experience)
8. [Troubleshooting](#troubleshooting)

## Features

### Core Features

- **Automatic Update Checking**: Checks for updates on startup and at configurable intervals
- **Multiple Update Channels**: Support for stable, beta, and alpha releases
- **Smart Download Management**: Optional automatic downloads with progress tracking
- **Version Skipping**: Users can skip specific versions
- **Background Updates**: Downloads happen in the background without interrupting work
- **Rollback Protection**: Prevents downgrades to older versions
- **Code Signing**: Ensures update authenticity and security
- **Cross-Platform**: Works on Windows, macOS, and Linux

### User Preferences

Users can configure:
- Auto-download updates
- Auto-install on quit
- Check for updates on startup
- Update check interval
- Update channel (stable/beta/alpha)
- Skip specific versions

## Update Channels

### Stable (Latest)

- **Purpose**: Production-ready releases
- **Frequency**: Monthly or as needed
- **Testing**: Full QA testing
- **Recommended for**: All users
- **Check Interval**: 1 hour (default)

### Beta

- **Purpose**: Pre-release testing
- **Frequency**: Weekly
- **Testing**: Internal testing
- **Recommended for**: Early adopters, testers
- **Check Interval**: 30 minutes (default)

### Alpha

- **Purpose**: Development builds
- **Frequency**: Daily or per-commit
- **Testing**: Minimal testing
- **Recommended for**: Developers only
- **Check Interval**: 15 minutes (default)

## Configuration

### Environment Variables

```bash
# Update server type (github, generic, s3, custom)
UPDATE_SERVER_TYPE=github

# GitHub configuration
GH_TOKEN=your_github_token

# Generic server configuration
UPDATE_SERVER_URL=https://your-server.com/updates

# Code signing (Windows)
WIN_CSC_LINK=path/to/certificate.pfx
WIN_CSC_KEY_PASSWORD=certificate_password

# Code signing (macOS)
APPLE_ID=your_apple_id
APPLE_ID_PASSWORD=app_specific_password
CSC_LINK=path/to/certificate.p12
CSC_KEY_PASSWORD=certificate_password
```

### Update Configuration File

Edit `electron/update-config.js` to configure update servers:

```javascript
const updateServers = {
  github: {
    provider: 'github',
    owner: 'your-username',
    repo: 'solar-calculator-pro',
    releaseType: 'release'
  },
  generic: {
    provider: 'generic',
    url: 'https://your-server.com/updates'
  },
  s3: {
    provider: 's3',
    bucket: 'your-bucket',
    region: 'us-east-1'
  }
};
```

## Update Servers

### GitHub Releases (Recommended)

**Pros:**
- Free for public repositories
- Automatic hosting
- Built-in release management
- Version control integration

**Cons:**
- Requires GitHub account
- Public releases are visible to all

**Setup:**

1. Create a GitHub repository
2. Configure `package.json`:
   ```json
   {
     "build": {
       "publish": [{
         "provider": "github",
         "owner": "your-username",
         "repo": "solar-calculator-pro"
       }]
     }
   }
   ```
3. Set `GH_TOKEN` environment variable
4. Build and publish:
   ```bash
   npm run electron:build
   npx electron-builder --publish always
   ```

### Generic HTTP Server

**Pros:**
- Full control over hosting
- Can be self-hosted
- Private updates

**Cons:**
- Requires server setup
- Manual upload process

**Setup:**

1. Setup HTTP server (nginx, Apache, etc.)
2. Create update directory structure:
   ```
   /updates
     /win
       latest.yml
       Solar-Calculator-Pro-Setup-1.0.0.exe
     /mac
       latest-mac.yml
       Solar-Calculator-Pro-1.0.0.dmg
     /linux
       latest-linux.yml
       Solar-Calculator-Pro-1.0.0.AppImage
   ```
3. Configure `package.json`:
   ```json
   {
     "build": {
       "publish": [{
         "provider": "generic",
         "url": "https://your-server.com/updates"
       }]
     }
   }
   ```

### AWS S3

**Pros:**
- Scalable
- Reliable
- Global CDN

**Cons:**
- Costs money
- Requires AWS account

**Setup:**

1. Create S3 bucket
2. Configure bucket policy for public read
3. Configure `package.json`:
   ```json
   {
     "build": {
       "publish": [{
         "provider": "s3",
         "bucket": "your-bucket",
         "region": "us-east-1"
       }]
     }
   }
   ```
4. Set AWS credentials:
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

## Building and Publishing

### Build for All Platforms

```bash
# Build for current platform
npm run electron:build

# Build for Windows
npm run electron:build:win

# Build for macOS
npm run electron:build:mac

# Build for Linux
npm run electron:build:linux
```

### Publish Updates

#### GitHub Releases

```bash
# Build and publish
npx electron-builder --publish always

# Or with specific platform
npx electron-builder --win --publish always
```

#### Generic Server

```bash
# Build
npm run electron:build

# Generate manifest
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release

# Upload to server
scp release/* user@server:/path/to/updates/win/
```

### Version Numbering

Follow semantic versioning (semver):

- **Major**: Breaking changes (1.0.0 → 2.0.0)
- **Minor**: New features (1.0.0 → 1.1.0)
- **Patch**: Bug fixes (1.0.0 → 1.0.1)

Update version in `package.json`:

```json
{
  "version": "1.0.0"
}
```

## Testing Updates

### Local Testing

1. Start local update server:
   ```bash
   node scripts/update-server.js --port 3000 --dir ./release
   ```

2. Configure app to use local server:
   ```javascript
   // In electron/main.js
   if (isDevelopment) {
     updater.setUpdateFeed('http://localhost:3000/updates', 'generic');
   }
   ```

3. Build two versions:
   ```bash
   # Version 1.0.0
   npm run electron:build
   
   # Update version to 1.0.1
   # Make some changes
   npm run electron:build
   ```

4. Generate manifest for new version:
   ```bash
   node scripts/generate-update-manifest.js \
     --version 1.0.1 \
     --platform win \
     --output ./release
   ```

5. Install version 1.0.0 and test update to 1.0.1

### Testing Checklist

- [ ] Update check works
- [ ] Download progress is shown
- [ ] Update installs correctly
- [ ] App restarts with new version
- [ ] User preferences are preserved
- [ ] Data is not lost
- [ ] Update can be skipped
- [ ] Auto-download works (if enabled)
- [ ] Update notifications appear
- [ ] Release notes are displayed

## User Experience

### Update Flow

1. **Check for Updates**
   - Automatic on startup (configurable)
   - Manual via Help → Check for Updates
   - Periodic background checks

2. **Update Available**
   - Notification appears
   - Release notes displayed
   - Options: Download, Skip Version, Remind Later

3. **Downloading**
   - Progress bar shown
   - Can continue working
   - Can cancel download

4. **Ready to Install**
   - Notification appears
   - Options: Restart Now, Install on Quit
   - Update installs when app closes

5. **Installation**
   - App closes
   - Update installs
   - App restarts automatically

### User Settings

Users can access update settings via:
- Settings → Updates
- Help → Update Preferences

Available settings:
- Enable/disable automatic updates
- Choose update channel
- Set check frequency
- Configure download behavior
- View update history

## Troubleshooting

### Common Issues

#### Update Check Fails

**Symptoms**: "Failed to check for updates" error

**Solutions**:
1. Check internet connection
2. Verify update server is accessible
3. Check firewall settings
4. Review logs in `~/.config/solar-calculator-pro/logs/`

#### Download Fails

**Symptoms**: Download starts but fails partway

**Solutions**:
1. Check available disk space
2. Verify file permissions
3. Try manual download
4. Check antivirus software

#### Installation Fails

**Symptoms**: Update downloads but won't install

**Solutions**:
1. Close all app instances
2. Run as administrator (Windows)
3. Check file permissions
4. Manually install from download location

#### Wrong Version Installed

**Symptoms**: Update installs but version doesn't change

**Solutions**:
1. Clear update cache
2. Manually uninstall and reinstall
3. Check for multiple installations

### Debug Mode

Enable debug logging:

```bash
# Windows
set DEBUG=electron-updater
Solar-Calculator-Pro.exe

# macOS/Linux
DEBUG=electron-updater ./Solar-Calculator-Pro
```

View logs:
- Windows: `%APPDATA%\solar-calculator-pro\logs\`
- macOS: `~/Library/Logs/solar-calculator-pro/`
- Linux: `~/.config/solar-calculator-pro/logs/`

### Manual Update

If auto-update fails, users can manually update:

1. Download latest version from website
2. Close running application
3. Run installer
4. Installer will upgrade existing installation

## Security

### Code Signing

**Windows:**
- Requires code signing certificate
- Prevents "Unknown Publisher" warnings
- Required for auto-update

**macOS:**
- Requires Apple Developer account
- App must be notarized
- Required for Gatekeeper

**Linux:**
- Optional but recommended
- GPG signing supported

### Update Verification

- All updates are verified via SHA512 hash
- Code signature is checked before installation
- HTTPS required for update server
- Man-in-the-middle protection

### Best Practices

1. Always use HTTPS for update server
2. Sign all releases
3. Test updates before publishing
4. Keep update server secure
5. Monitor update logs
6. Have rollback plan

## API Reference

### IPC Channels

```javascript
// Check for updates
window.electronAPI.checkForUpdates()

// Download update
window.electronAPI.downloadUpdate()

// Install update
window.electronAPI.installUpdate()

// Get current version
window.electronAPI.getVersion()

// Get update info
window.electronAPI.getUpdateInfo()

// Set preferences
window.electronAPI.setUpdatePreferences({
  autoDownload: true,
  checkInterval: 3600000
})
```

### Events

```javascript
// Update available
window.electronAPI.onUpdateAvailable((info) => {
  console.log('Update available:', info.version);
});

// Download progress
window.electronAPI.onUpdateProgress((progress) => {
  console.log('Download progress:', progress.percent);
});

// Update downloaded
window.electronAPI.onUpdateDownloaded((info) => {
  console.log('Update ready:', info.version);
});

// Update error
window.electronAPI.onUpdateError((error) => {
  console.error('Update error:', error);
});
```

## Resources

- [electron-updater Documentation](https://www.electron.build/auto-update)
- [Code Signing Guide](https://www.electron.build/code-signing)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-username/solar-calculator-pro/issues
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
