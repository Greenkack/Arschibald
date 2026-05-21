# Update Scripts

This directory contains utility scripts for managing the auto-update system.

## Scripts

### generate-update-manifest.js

Generates update manifest files (latest.yml) that electron-updater uses to check for updates.

**Usage:**
```bash
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release \
  --releaseNotes "Bug fixes and improvements" \
  --releaseNotesUrl "https://github.com/owner/repo/releases/tag/v1.0.0"
```

**Options:**
- `--version`: Version number (required)
- `--platform`: Platform (win, mac, linux) (required)
- `--output`: Output directory (default: ./release)
- `--releaseNotes`: Release notes text (optional)
- `--releaseNotesUrl`: URL to release notes (optional)

**Output:**
- `latest.yml` (Windows)
- `latest-mac.yml` (macOS)
- `latest-linux.yml` (Linux)
- `*.json` (Debug version)

**Example:**
```bash
# Generate manifest for Windows
node scripts/generate-update-manifest.js \
  --version 1.0.1 \
  --platform win \
  --output ./release

# Generate manifest for macOS
node scripts/generate-update-manifest.js \
  --version 1.0.1 \
  --platform mac \
  --output ./release

# Generate manifest for Linux
node scripts/generate-update-manifest.js \
  --version 1.0.1 \
  --platform linux \
  --output ./release
```

### update-server.js

Simple HTTP server for testing updates locally during development.

**Usage:**
```bash
node scripts/update-server.js \
  --port 3000 \
  --dir ./release \
  --host localhost
```

**Options:**
- `--port`: Server port (default: 3000)
- `--dir`: Directory to serve (default: ./release)
- `--host`: Host to bind to (default: localhost)

**Features:**
- Serves update files with proper MIME types
- Directory listing with web interface
- CORS support for local development
- Range request support
- File size and transfer info

**Example:**
```bash
# Start server on default port
node scripts/update-server.js

# Start server on custom port
node scripts/update-server.js --port 8080

# Serve from custom directory
node scripts/update-server.js --dir ./dist

# Bind to all interfaces
node scripts/update-server.js --host 0.0.0.0
```

**Access:**
- Open browser: http://localhost:3000
- View files and download installers
- Test update process

## Workflow

### 1. Build Application

```bash
# Build for current platform
npm run electron:build

# Build for specific platform
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux
```

### 2. Generate Manifests

```bash
# Generate for all platforms
node scripts/generate-update-manifest.js --version 1.0.0 --platform win --output ./release
node scripts/generate-update-manifest.js --version 1.0.0 --platform mac --output ./release
node scripts/generate-update-manifest.js --version 1.0.0 --platform linux --output ./release
```

### 3. Test Locally

```bash
# Start local update server
node scripts/update-server.js --port 3000 --dir ./release

# Configure app to use local server (in electron/main.js)
if (isDevelopment) {
  updater.setUpdateFeed('http://localhost:3000', 'generic');
}

# Install old version and test update
```

### 4. Publish

```bash
# Publish to GitHub Releases
npx electron-builder --publish always

# Or manually upload to your server
scp release/* user@server:/path/to/updates/
```

## Testing Updates

### Local Testing Setup

1. **Build Version 1.0.0:**
   ```bash
   # Set version in package.json
   "version": "1.0.0"
   
   # Build
   npm run electron:build
   ```

2. **Install Version 1.0.0:**
   - Install the built application
   - Run it to verify it works

3. **Build Version 1.0.1:**
   ```bash
   # Update version in package.json
   "version": "1.0.1"
   
   # Make some visible changes
   # Build
   npm run electron:build
   ```

4. **Generate Manifest:**
   ```bash
   node scripts/generate-update-manifest.js \
     --version 1.0.1 \
     --platform win \
     --output ./release \
     --releaseNotes "Test update"
   ```

5. **Start Update Server:**
   ```bash
   node scripts/update-server.js --port 3000 --dir ./release
   ```

6. **Test Update:**
   - Open the installed v1.0.0 app
   - Go to Help → Check for Updates
   - Verify update notification appears
   - Download and install update
   - Verify app restarts with v1.0.1

### Testing Checklist

- [ ] Update check works
- [ ] Update notification appears
- [ ] Release notes display correctly
- [ ] Download progress shows
- [ ] Download completes successfully
- [ ] Install prompt appears
- [ ] App restarts after install
- [ ] New version is running
- [ ] User data is preserved
- [ ] Preferences are maintained

## Troubleshooting

### Manifest Generation Fails

**Problem:** Script can't find installer files

**Solution:**
```bash
# Check if files exist
ls -la ./release

# Verify file extensions
# Windows: .exe
# macOS: .dmg
# Linux: .AppImage or .deb

# Rebuild if necessary
npm run electron:build
```

### Update Server Won't Start

**Problem:** Port already in use

**Solution:**
```bash
# Use different port
node scripts/update-server.js --port 8080

# Or kill process using port
# Windows:
netstat -ano | findstr :3000
taskkill /PID <pid> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

### Update Check Fails

**Problem:** App can't connect to update server

**Solution:**
```bash
# Verify server is running
curl http://localhost:3000/latest.yml

# Check firewall settings
# Verify update URL in app configuration

# Check logs
# Windows: %APPDATA%\solar-calculator-pro\logs\
# macOS: ~/Library/Logs/solar-calculator-pro/
# Linux: ~/.config/solar-calculator-pro/logs/
```

## Advanced Usage

### Custom Release Notes

```bash
# From file
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release \
  --releaseNotes "$(cat CHANGELOG.md)"

# With URL
node scripts/generate-update-manifest.js \
  --version 1.0.0 \
  --platform win \
  --output ./release \
  --releaseNotesUrl "https://github.com/owner/repo/releases/tag/v1.0.0"
```

### Automated Build Script

```bash
#!/bin/bash
# build-and-publish.sh

VERSION=$1
PLATFORM=$2

if [ -z "$VERSION" ] || [ -z "$PLATFORM" ]; then
  echo "Usage: ./build-and-publish.sh <version> <platform>"
  exit 1
fi

# Update version in package.json
npm version $VERSION --no-git-tag-version

# Build
npm run electron:build:$PLATFORM

# Generate manifest
node scripts/generate-update-manifest.js \
  --version $VERSION \
  --platform $PLATFORM \
  --output ./release

# Upload to server (customize as needed)
# scp release/* user@server:/path/to/updates/$PLATFORM/

echo "Build complete for version $VERSION on $PLATFORM"
```

### CI/CD Integration

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        run: npm run electron:build
      
      - name: Generate manifest
        run: |
          node scripts/generate-update-manifest.js \
            --version ${GITHUB_REF#refs/tags/v} \
            --platform ${{ matrix.os }} \
            --output ./release
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: release/*
```

## Resources

- [electron-updater Documentation](https://www.electron.build/auto-update)
- [electron-builder Documentation](https://www.electron.build/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

## Support

For issues or questions:
- Check logs in application data directory
- Review documentation in `docs/AUTO_UPDATE_GUIDE.md`
- Open issue on GitHub
- Contact support team
