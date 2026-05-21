# Deployment Architecture

## Table of Contents

1. [Overview](#overview)
2. [Development Environment](#development-environment)
3. [Build Process](#build-process)
4. [Distribution Architecture](#distribution-architecture)
5. [Update Mechanism](#update-mechanism)
6. [Platform-Specific Considerations](#platform-specific-considerations)

## Overview

Solar Calculator Pro is deployed as a standalone desktop application for Windows, macOS, and Linux. The application bundles both the React frontend and Python backend into a single executable package.

## Development Environment

### Local Development Setup

```
┌─────────────────────────────────────────────────────────┐
│              Developer Machine                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Backend    │  │   Frontend   │  │   Electron   │ │
│  │  (Port 8000) │  │  (Port 3000) │  │   (Main)     │ │
│  │              │  │              │  │              │ │
│  │  uvicorn     │  │  vite dev    │  │  electron .  │ │
│  │  --reload    │  │  server      │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                    Hot Reload                            │
└─────────────────────────────────────────────────────────┘
```

### Development Commands

```bash
# Start backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start frontend
cd frontend
npm install
npm run dev

# Start Electron
npm run electron:dev
```

## Build Process

### Build Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    Build Process                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Backend Build                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  PyInstaller                                      │  │
│  │  • Bundle Python interpreter                      │  │
│  │  • Include all dependencies                       │  │
│  │  • Package legacy modules                         │  │
│  │  • Create standalone executable                   │  │
│  │  Output: backend/dist/main.exe                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Step 2: Frontend Build                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Vite Build                                       │  │
│  │  • Transpile TypeScript                           │  │
│  │  • Bundle React components                        │  │
│  │  • Optimize assets                                │  │
│  │  • Generate static files                          │  │
│  │  Output: frontend/dist/                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Step 3: Electron Packaging                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  electron-builder                                 │  │
│  │  • Package Electron app                           │  │
│  │  • Include frontend dist                          │  │
│  │  • Include backend executable                     │  │
│  │  • Create installers                              │  │
│  │  Output: release/                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Build Configuration

```json
// package.json
{
  "scripts": {
    "build:backend": "cd backend && python build_backend.py",
    "build:frontend": "cd frontend && npm run build",
    "build:electron": "electron-builder",
    "build": "npm run build:backend && npm run build:frontend && npm run build:electron"
  },
  "build": {
    "appId": "com.yourcompany.solarcalculator",
    "productName": "Solar Calculator Pro",
    "files": [
      "electron/**/*",
      "frontend/dist/**/*",
      "backend/dist/**/*"
    ],
    "extraResources": [
      {
        "from": "backend/dist/main${os === 'win' ? '.exe' : ''}",
        "to": "backend/main${os === 'win' ? '.exe' : ''}"
      }
    ]
  }
}
```

## Distribution Architecture

### Application Package Structure

```
solar-calculator-pro/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # IPC bridge
│   ├── backend-manager.js   # Python backend manager
│   ├── menu.js              # Application menu
│   ├── tray.js              # System tray
│   └── updater.js           # Auto-update logic
├── frontend/dist/           # Built React app
│   ├── index.html
│   ├── assets/
│   └── ...
├── backend/dist/            # Built Python backend
│   └── main.exe             # Standalone executable
└── resources/
    ├── icon.ico             # Windows icon
    ├── icon.icns            # macOS icon
    └── icon.png             # Linux icon
```

### Runtime Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Installed Application                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Electron Main Process                   │  │
│  │  • Manages application lifecycle                  │  │
│  │  • Creates browser windows                        │  │
│  │  • Handles IPC communication                      │  │
│  │  • Manages backend process                        │  │
│  └──────────────────────────────────────────────────┘  │
│         │                                    │           │
│         ▼                                    ▼           │
│  ┌──────────────┐                    ┌──────────────┐  │
│  │   Renderer   │                    │   Backend    │  │
│  │   Process    │◀──────HTTP────────▶│   Process    │  │
│  │  (Frontend)  │                    │  (FastAPI)   │  │
│  └──────────────┘                    └──────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Update Mechanism

### Auto-Update Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Update Process                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Check for Updates                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Application                                      │  │
│  │  • Checks update server on startup               │  │
│  │  • Compares current version with latest          │  │
│  │  • Notifies user if update available             │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  Step 2: Download Update                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  electron-updater                                 │  │
│  │  • Downloads update in background                │  │
│  │  • Shows progress to user                        │  │
│  │  • Verifies signature                            │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  Step 3: Install Update                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Application                                      │  │
│  │  • Prompts user to restart                       │  │
│  │  • Quits application                             │  │
│  │  • Installer runs                                │  │
│  │  • Application restarts with new version        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Update Server Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Update Server                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  GitHub Releases (or Custom Server)              │  │
│  │                                                   │  │
│  │  /releases/                                       │  │
│  │  ├── latest.yml                                  │  │
│  │  ├── solar-calculator-pro-1.0.0-win.exe         │  │
│  │  ├── solar-calculator-pro-1.0.0-mac.dmg         │  │
│  │  └── solar-calculator-pro-1.0.0-linux.AppImage  │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                 │
│                        ▼                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Client Applications                              │  │
│  │  • Check for updates                             │  │
│  │  • Download appropriate package                  │  │
│  │  • Verify and install                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Platform-Specific Considerations

### Windows Deployment

```
┌─────────────────────────────────────────────────────────┐
│                  Windows Package                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Installer: NSIS                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Custom installer UI                            │  │
│  │  • Installation directory selection               │  │
│  │  • Desktop shortcut creation                      │  │
│  │  • Start menu entry                               │  │
│  │  • Uninstaller                                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Code Signing                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Authenticode signature                         │  │
│  │  • Prevents SmartScreen warnings                 │  │
│  │  • Builds trust with users                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Installation Path                                      │
│  C:\Program Files\Solar Calculator Pro\                │
│  ├── Solar Calculator Pro.exe                          │
│  ├── resources\                                        │
│  └── ...                                               │
└─────────────────────────────────────────────────────────┘
```

### macOS Deployment

```
┌─────────────────────────────────────────────────────────┐
│                   macOS Package                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Installer: DMG                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Drag-and-drop installation                     │  │
│  │  • Custom background image                        │  │
│  │  • Application icon                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Code Signing & Notarization                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Apple Developer ID signature                   │  │
│  │  • Notarization by Apple                          │  │
│  │  • Gatekeeper approval                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Installation Path                                      │
│  /Applications/Solar Calculator Pro.app/               │
│  ├── Contents/                                         │
│  │   ├── MacOS/                                       │
│  │   ├── Resources/                                   │
│  │   └── Info.plist                                   │
│  └── ...                                               │
└─────────────────────────────────────────────────────────┘
```

### Linux Deployment

```
┌─────────────────────────────────────────────────────────┐
│                  Linux Package                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Formats                                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • AppImage (universal)                           │  │
│  │  • DEB (Debian/Ubuntu)                            │  │
│  │  • RPM (Fedora/RHEL)                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  AppImage Structure                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Self-contained executable                      │  │
│  │  • No installation required                       │  │
│  │  • Runs on most distributions                     │  │
│  │  • Desktop integration                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Installation Path (DEB/RPM)                            │
│  /opt/solar-calculator-pro/                            │
│  ├── solar-calculator-pro                             │
│  ├── resources/                                        │
│  └── ...                                               │
└─────────────────────────────────────────────────────────┘
```

## CI/CD Pipeline

### Automated Build and Release

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Trigger: Push to main or tag                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Job 1: Build Windows                             │  │
│  │  • Runs on: windows-latest                        │  │
│  │  • Build backend with PyInstaller                 │  │
│  │  • Build frontend with npm                        │  │
│  │  • Package with electron-builder                  │  │
│  │  • Upload artifacts                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Job 2: Build macOS                               │  │
│  │  • Runs on: macos-latest                          │  │
│  │  • Build backend with PyInstaller                 │  │
│  │  • Build frontend with npm                        │  │
│  │  • Package with electron-builder                  │  │
│  │  • Sign and notarize                              │  │
│  │  • Upload artifacts                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Job 3: Build Linux                               │  │
│  │  • Runs on: ubuntu-latest                         │  │
│  │  • Build backend with PyInstaller                 │  │
│  │  • Build frontend with npm                        │  │
│  │  • Package with electron-builder                  │  │
│  │  • Upload artifacts                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Job 4: Create Release                            │  │
│  │  • Create GitHub release                          │  │
│  │  • Upload all platform builds                     │  │
│  │  • Generate release notes                         │  │
│  │  • Publish to update server                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Deployment Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Code signing certificates valid
- [ ] Build scripts tested

### Release

- [ ] Create git tag
- [ ] Trigger CI/CD pipeline
- [ ] Verify builds for all platforms
- [ ] Test installers on clean systems
- [ ] Verify auto-update mechanism
- [ ] Update website/documentation

### Post-Release

- [ ] Monitor error reports
- [ ] Track update adoption
- [ ] Gather user feedback
- [ ] Plan next release

## Summary

The deployment architecture ensures:

- **Cross-Platform**: Single codebase, multiple platforms
- **Self-Contained**: All dependencies bundled
- **Auto-Update**: Seamless updates for users
- **Secure**: Code signing and verification
- **Automated**: CI/CD pipeline for consistent builds
- **Professional**: Native installers for each platform
