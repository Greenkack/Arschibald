# Windows Build Configuration Guide

This guide provides comprehensive instructions for building Solar Calculator Pro for Windows.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Configuration](#build-configuration)
3. [Code Signing](#code-signing)
4. [Building the Application](#building-the-application)
5. [Installer Customization](#installer-customization)
6. [Troubleshooting](#troubleshooting)
7. [Distribution](#distribution)

## Prerequisites

### Required Software

1. **Node.js** (v18 or later)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Python** (v3.10 or later)
   - Download from: https://www.python.org/
   - Verify installation: `python --version`
   - Ensure Python is added to PATH

3. **Git** (for version control)
   - Download from: https://git-scm.com/
   - Verify installation: `git --version`

4. **Visual Studio Build Tools** (for native modules)
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++" workload

### Optional Software

1. **Code Signing Certificate**
   - Required for production releases
   - Can be obtained from certificate authorities like DigiCert, Sectigo, etc.

2. **NSIS** (Nullsoft Scriptable Install System)
   - Automatically installed by electron-builder
   - Manual installation: https://nsis.sourceforge.io/

## Build Configuration

### Package.json Configuration

The Windows build configuration is defined in `package.json`:

```json
{
  "build": {
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64", "ia32"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        },
        {
          "target": "zip",
          "arch": ["x64"]
        }
      ],
      "icon": "assets/icon.ico",
      "publisherName": "Your Company Name",
      "certificateFile": "build/cert.pfx",
      "certificatePassword": "${env.WINDOWS_CERT_PASSWORD}",
      "fileAssociations": [
        {
          "ext": "scp",
          "name": "Solar Calculator Project",
          "description": "Solar Calculator Project File",
          "icon": "assets/file-icon.ico"
        }
      ]
    }
  }
}
```

### Build Targets

The configuration creates three types of Windows builds:

1. **NSIS Installer** (`.exe`)
   - Full-featured installer with customization options
   - Supports both x64 and x86 (ia32) architectures
   - Includes uninstaller

2. **Portable Version** (`.exe`)
   - Standalone executable that doesn't require installation
   - x64 architecture only
   - Useful for USB drives or temporary installations

3. **ZIP Archive** (`.zip`)
   - Compressed archive of application files
   - x64 architecture only
   - For manual deployment or advanced users

### Application Icon

The application icon must be in `.ico` format with multiple resolutions:

- 16x16
- 32x32
- 48x48
- 64x64
- 128x128
- 256x256

Place the icon at: `assets/icon.ico`

You can create an `.ico` file from a PNG using online tools or software like:
- GIMP (free)
- IcoFX
- Online converters

### File Associations

The build is configured to associate `.scp` files (Solar Calculator Project) with the application:

```json
"fileAssociations": [
  {
    "ext": "scp",
    "name": "Solar Calculator Project",
    "description": "Solar Calculator Project File",
    "icon": "assets/file-icon.ico",
    "role": "Editor"
  }
]
```

When users double-click a `.scp` file, it will open in Solar Calculator Pro.

## Code Signing

### Why Code Signing?

Code signing provides:
- **Trust**: Users know the software comes from you
- **Security**: Windows SmartScreen won't show warnings
- **Integrity**: Ensures the software hasn't been tampered with

### Obtaining a Certificate

1. **Purchase a code signing certificate** from a trusted CA:
   - DigiCert
   - Sectigo (formerly Comodo)
   - GlobalSign
   - Entrust

2. **Certificate types**:
   - Standard Code Signing Certificate
   - EV (Extended Validation) Code Signing Certificate (recommended)

3. **Cost**: Typically $100-$500 per year

### Setting Up Code Signing

1. **Export your certificate** to a `.pfx` file (PKCS#12 format)

2. **Place the certificate** in the `build` directory:
   ```
   solar-calculator-pro/build/cert.pfx
   ```

3. **Set the certificate password** as an environment variable:
   ```powershell
   $env:WINDOWS_CERT_PASSWORD = "your-certificate-password"
   ```

4. **For CI/CD**, store the password as a secret:
   - GitHub Actions: Repository Settings → Secrets
   - Azure DevOps: Pipeline → Variables
   - GitLab CI: Settings → CI/CD → Variables

### Signing Configuration

The signing configuration in `package.json`:

```json
{
  "win": {
    "certificateFile": "build/cert.pfx",
    "certificatePassword": "${env.WINDOWS_CERT_PASSWORD}",
    "signingHashAlgorithms": ["sha256"],
    "rfc3161TimeStampServer": "http://timestamp.digicert.com"
  }
}
```

**Important**: Never commit your certificate or password to version control!

Add to `.gitignore`:
```
build/cert.pfx
build/*.pfx
```

## Building the Application

### Method 1: Using npm Scripts

#### Build for Windows (all targets):
```bash
npm run electron:build:win
```

This will create:
- NSIS installer (x64 and ia32)
- Portable executable (x64)
- ZIP archive (x64)

#### Build specific target:
```bash
# NSIS installer only
npx electron-builder --win nsis

# Portable only
npx electron-builder --win portable

# ZIP only
npx electron-builder --win zip
```

### Method 2: Using PowerShell Script

The PowerShell script provides additional options:

```powershell
# Basic build
.\build\build-windows.ps1

# Clean build (removes previous builds)
.\build\build-windows.ps1 -Clean

# Skip tests
.\build\build-windows.ps1 -SkipTests

# Enable code signing
.\build\build-windows.ps1 -Sign -CertPassword "your-password"

# Combine options
.\build\build-windows.ps1 -Clean -Sign -CertPassword "your-password"
```

### Method 3: Using Node.js Script

```bash
node build/build-windows.js
```

This script:
1. Checks prerequisites
2. Cleans build directories
3. Builds frontend (React)
4. Builds backend (Python with PyInstaller)
5. Packages Electron application
6. Verifies build artifacts
7. Generates build report

### Build Output

Build artifacts are created in the `release` directory:

```
release/
├── Solar Calculator Pro-Setup-1.0.0-x64.exe    # NSIS installer (64-bit)
├── Solar Calculator Pro-Setup-1.0.0-ia32.exe   # NSIS installer (32-bit)
├── Solar Calculator Pro-1.0.0-x64.exe          # Portable (64-bit)
├── Solar Calculator Pro-1.0.0-x64.zip          # ZIP archive (64-bit)
├── latest.yml                                   # Auto-update metadata
└── build-report.json                            # Build information
```

## Installer Customization

### NSIS Configuration

The NSIS installer is configured in `package.json`:

```json
{
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "allowElevation": true,
    "installerIcon": "assets/icon.ico",
    "uninstallerIcon": "assets/icon.ico",
    "installerHeader": "assets/installer-header.bmp",
    "installerSidebar": "assets/installer-sidebar.bmp",
    "createDesktopShortcut": "always",
    "createStartMenuShortcut": true,
    "shortcutName": "Solar Calculator Pro",
    "menuCategory": true,
    "runAfterFinish": true,
    "perMachine": false,
    "multiLanguageInstaller": true,
    "installerLanguages": ["en_US", "de_DE"]
  }
}
```

### Custom Installer Graphics

#### Installer Header (150x57 pixels)
- File: `assets/installer-header.bmp`
- Format: 24-bit BMP
- Displayed at the top of installer pages

#### Installer Sidebar (164x314 pixels)
- File: `assets/installer-sidebar.bmp`
- Format: 24-bit BMP
- Displayed on the left side of welcome and finish pages

### Custom NSIS Script

Advanced customization is available in `build/installer.nsh`:

```nsis
!macro customInstall
  ; Custom installation steps
  CreateDirectory "$APPDATA\Solar Calculator Pro"
  CreateDirectory "$APPDATA\Solar Calculator Pro\logs"
  
  ; Set file associations
  WriteRegStr HKCR ".scp" "" "SolarCalculatorProject"
  WriteRegStr HKCR "SolarCalculatorProject\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}" "%1"'
!macroend
```

### Installation Options

Users can customize the installation:

1. **Installation Directory**
   - Default: `C:\Users\<Username>\AppData\Local\Programs\Solar Calculator Pro`
   - Can be changed during installation

2. **Shortcuts**
   - Desktop shortcut (always created)
   - Start Menu shortcut (always created)
   - Start Menu folder (optional)

3. **Installation Type**
   - Per-user installation (default)
   - Per-machine installation (requires admin rights)

## Troubleshooting

### Common Issues

#### 1. "Python not found" Error

**Problem**: Build script can't find Python

**Solution**:
```powershell
# Add Python to PATH
$env:Path += ";C:\Python310;C:\Python310\Scripts"

# Or use py launcher
py --version
```

#### 2. "PyInstaller not found" Error

**Problem**: PyInstaller is not installed

**Solution**:
```bash
pip install pyinstaller
```

#### 3. "node-gyp" Build Errors

**Problem**: Native modules fail to build

**Solution**:
```bash
# Install Visual Studio Build Tools
# Then install windows-build-tools
npm install --global windows-build-tools

# Or install specific version of node-gyp
npm install --global node-gyp@latest
```

#### 4. Code Signing Fails

**Problem**: Certificate or password issues

**Solution**:
```powershell
# Verify certificate
certutil -dump build\cert.pfx

# Check password
$env:WINDOWS_CERT_PASSWORD = "your-password"
echo $env:WINDOWS_CERT_PASSWORD

# Test signing manually
signtool sign /f build\cert.pfx /p "password" /tr http://timestamp.digicert.com /td sha256 /fd sha256 test.exe
```

#### 5. "ENOENT: no such file or directory" Error

**Problem**: Missing files or directories

**Solution**:
```bash
# Clean and rebuild
npm run electron:build:win -- --clean

# Or use PowerShell script
.\build\build-windows.ps1 -Clean
```

#### 6. Installer Size Too Large

**Problem**: Installer exceeds expected size

**Solution**:
- Check for unnecessary files in `files` configuration
- Exclude development dependencies
- Optimize frontend bundle size
- Compress backend with UPX

```json
{
  "build": {
    "files": [
      "!**/*.map",
      "!**/node_modules/*/{CHANGELOG.md,README.md,README,readme.md,readme}",
      "!**/node_modules/*/{test,__tests__,tests,powered-test,example,examples}",
      "!**/node_modules/*.d.ts",
      "!**/node_modules/.bin"
    ]
  }
}
```

### Build Logs

Build logs are saved to:
- Console output (stdout/stderr)
- `release/build-report.json` (build metadata)
- electron-builder logs in `%LOCALAPPDATA%\electron-builder\`

### Debugging

Enable verbose logging:

```bash
# electron-builder verbose mode
DEBUG=electron-builder npm run electron:build:win

# Or set environment variable
$env:DEBUG = "electron-builder"
npm run electron:build:win
```

## Distribution

### Testing the Installer

Before distributing:

1. **Test on clean Windows installation**
   - Use a virtual machine (VirtualBox, VMware, Hyper-V)
   - Test both x64 and ia32 versions

2. **Test installation scenarios**:
   - Fresh installation
   - Upgrade from previous version
   - Uninstallation
   - Reinstallation

3. **Test application functionality**:
   - All features work correctly
   - File associations work
   - Auto-update works (if configured)

### Distribution Channels

#### 1. Direct Download

Host the installer on your website:
```
https://yourcompany.com/downloads/solar-calculator-pro-setup.exe
```

#### 2. GitHub Releases

Upload to GitHub Releases:
```bash
# Create a release
gh release create v1.0.0 \
  release/Solar-Calculator-Pro-Setup-1.0.0-x64.exe \
  release/Solar-Calculator-Pro-Setup-1.0.0-ia32.exe \
  --title "Solar Calculator Pro v1.0.0" \
  --notes "Release notes here"
```

#### 3. Microsoft Store

Submit to Microsoft Store:
- Convert to MSIX format
- Follow Microsoft Store submission guidelines
- Requires Microsoft Partner Center account

#### 4. Chocolatey

Create a Chocolatey package:
```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Create package
choco new solar-calculator-pro
# Edit nuspec file
choco pack
choco push
```

### Auto-Update Configuration

Configure auto-update in `package.json`:

```json
{
  "build": {
    "publish": [
      {
        "provider": "github",
        "owner": "your-github-username",
        "repo": "solar-calculator-pro",
        "releaseType": "release"
      }
    ]
  }
}
```

The application will automatically check for updates on startup.

### System Requirements

Document system requirements for users:

**Minimum Requirements:**
- Windows 10 (64-bit) or later
- 4 GB RAM
- 500 MB free disk space
- 1280x720 screen resolution

**Recommended Requirements:**
- Windows 11 (64-bit)
- 8 GB RAM
- 1 GB free disk space
- 1920x1080 screen resolution

### License and Legal

Include in your installer:
- End User License Agreement (EULA)
- Privacy Policy
- Third-party licenses

Add to NSIS configuration:
```json
{
  "nsis": {
    "license": "LICENSE.txt",
    "warningsAsErrors": false
  }
}
```

## Best Practices

1. **Version Numbering**
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Update version in `package.json` before building

2. **Code Signing**
   - Always sign production releases
   - Use EV certificates for immediate SmartScreen reputation

3. **Testing**
   - Test on multiple Windows versions
   - Test both installation and upgrade scenarios
   - Verify all features work after installation

4. **Documentation**
   - Include user manual
   - Provide installation instructions
   - Document system requirements

5. **Support**
   - Provide clear contact information
   - Include troubleshooting guide
   - Set up crash reporting

## Additional Resources

- [electron-builder Documentation](https://www.electron.build/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [Windows Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [Microsoft Store Submission](https://docs.microsoft.com/en-us/windows/uwp/publish/)

## Support

For build issues or questions:
- GitHub Issues: https://github.com/your-repo/issues
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com

---

**Last Updated**: 2024
**Version**: 1.0.0
