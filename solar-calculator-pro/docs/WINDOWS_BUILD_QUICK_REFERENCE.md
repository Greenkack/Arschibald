# Windows Build Quick Reference

Quick commands and configurations for building Solar Calculator Pro on Windows.

## Quick Start

```powershell
# Clone and setup
git clone <repository-url>
cd solar-calculator-pro
npm install

# Build for Windows
npm run electron:build:win
```

## Build Commands

### npm Scripts

```bash
# Build all Windows targets (NSIS, Portable, ZIP)
npm run electron:build:win

# Build frontend only
npm run frontend:build

# Build backend only (requires Python)
cd backend && pyinstaller main.spec

# Run tests before building
npm test

# Lint code
npm run lint
```

### PowerShell Script

```powershell
# Basic build
.\build\build-windows.ps1

# Clean build
.\build\build-windows.ps1 -Clean

# Skip tests
.\build\build-windows.ps1 -SkipTests

# With code signing
.\build\build-windows.ps1 -Sign -CertPassword "your-password"

# All options
.\build\build-windows.ps1 -Clean -Sign -CertPassword "your-password"
```

### Node.js Script

```bash
# Run build script directly
node build/build-windows.js
```

## Build Targets

| Target | Command | Output | Architecture |
|--------|---------|--------|--------------|
| NSIS Installer | `npx electron-builder --win nsis` | `.exe` installer | x64, ia32 |
| Portable | `npx electron-builder --win portable` | `.exe` standalone | x64 |
| ZIP Archive | `npx electron-builder --win zip` | `.zip` archive | x64 |

## Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Main build configuration |
| `build/installer.nsh` | Custom NSIS installer script |
| `build/build-windows.js` | Node.js build automation |
| `build/build-windows.ps1` | PowerShell build script |
| `backend/main.spec` | PyInstaller configuration |

## Required Assets

| Asset | Path | Size | Format |
|-------|------|------|--------|
| App Icon | `assets/icon.ico` | Multiple | ICO |
| File Icon | `assets/file-icon.ico` | Multiple | ICO |
| Installer Header | `assets/installer-header.bmp` | 150x57 | BMP 24-bit |
| Installer Sidebar | `assets/installer-sidebar.bmp` | 164x314 | BMP 24-bit |

## Code Signing

### Setup

```powershell
# Set certificate password
$env:WINDOWS_CERT_PASSWORD = "your-password"

# Place certificate
# Location: build/cert.pfx
```

### Configuration

```json
{
  "win": {
    "certificateFile": "build/cert.pfx",
    "certificatePassword": "${env.WINDOWS_CERT_PASSWORD}",
    "signingHashAlgorithms": ["sha256"]
  }
}
```

## Environment Variables

```powershell
# Certificate password
$env:WINDOWS_CERT_PASSWORD = "password"

# Debug mode
$env:DEBUG = "electron-builder"

# Python path (if needed)
$env:Path += ";C:\Python310;C:\Python310\Scripts"
```

## Build Output

```
release/
├── Solar Calculator Pro-Setup-1.0.0-x64.exe    # NSIS (64-bit)
├── Solar Calculator Pro-Setup-1.0.0-ia32.exe   # NSIS (32-bit)
├── Solar Calculator Pro-1.0.0-x64.exe          # Portable
├── Solar Calculator Pro-1.0.0-x64.zip          # ZIP
├── latest.yml                                   # Update metadata
└── build-report.json                            # Build info
```

## Common Issues

### Python not found
```powershell
$env:Path += ";C:\Python310;C:\Python310\Scripts"
```

### PyInstaller not installed
```bash
pip install pyinstaller
```

### node-gyp errors
```bash
npm install --global windows-build-tools
```

### Clean build
```bash
npm run electron:build:win -- --clean
```

## Testing

```bash
# Run all tests
npm test

# Frontend tests only
npm run frontend:test

# Backend tests only
npm run backend:test

# Lint code
npm run lint
```

## Version Management

```json
// package.json
{
  "version": "1.0.0"  // Update before building
}
```

## File Associations

```json
{
  "fileAssociations": [
    {
      "ext": "scp",
      "name": "Solar Calculator Project",
      "icon": "assets/file-icon.ico"
    }
  ]
}
```

## Installer Options

| Option | Default | Description |
|--------|---------|-------------|
| `oneClick` | `false` | One-click installation |
| `allowToChangeInstallationDirectory` | `true` | User can choose directory |
| `createDesktopShortcut` | `always` | Create desktop shortcut |
| `createStartMenuShortcut` | `true` | Create start menu shortcut |
| `perMachine` | `false` | Install for all users |
| `runAfterFinish` | `true` | Run app after install |

## Debugging

```bash
# Verbose logging
DEBUG=electron-builder npm run electron:build:win

# Check build logs
cat %LOCALAPPDATA%\electron-builder\builder-debug.log
```

## Distribution

### GitHub Release

```bash
gh release create v1.0.0 \
  release/*.exe \
  --title "v1.0.0" \
  --notes "Release notes"
```

### Direct Download

```
https://yourcompany.com/downloads/solar-calculator-pro-setup.exe
```

## System Requirements

**Minimum:**
- Windows 10 (64-bit)
- 4 GB RAM
- 500 MB disk space

**Recommended:**
- Windows 11 (64-bit)
- 8 GB RAM
- 1 GB disk space

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Run with `-Clean` flag |
| Python errors | Check Python in PATH |
| Signing fails | Verify certificate password |
| Large installer | Optimize bundle size |
| Missing files | Check `files` configuration |

## Resources

- [Full Build Guide](./WINDOWS_BUILD_GUIDE.md)
- [electron-builder Docs](https://www.electron.build/)
- [NSIS Docs](https://nsis.sourceforge.io/Docs/)

## Support

- Issues: https://github.com/your-repo/issues
- Email: support@yourcompany.com
- Docs: https://docs.yourcompany.com

---

**Quick Reference Version**: 1.0.0
