# Backend Packaging Guide

This guide explains how to package the Solar Calculator Pro backend into a standalone executable using PyInstaller.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Build Process](#build-process)
5. [Optimization](#optimization)
6. [Testing](#testing)
7. [Distribution](#distribution)
8. [Troubleshooting](#troubleshooting)
9. [Platform-Specific Notes](#platform-specific-notes)

## Overview

The backend packaging process converts the Python FastAPI application into a standalone executable that can be bundled with the Electron application. This eliminates the need for users to have Python installed on their systems.

### What Gets Packaged

- FastAPI application and all routes
- Database models and migrations
- All services and business logic
- Dependencies (FastAPI, SQLAlchemy, etc.)
- Configuration files
- Static files and templates

### Output

- **Windows**: `backend.exe` (~50-100 MB)
- **macOS**: `backend` (~50-100 MB)
- **Linux**: `backend` (~50-100 MB)

## Prerequisites

### Required Software

- Python 3.10 or higher
- pip (Python package manager)
- PyInstaller (will be installed automatically)

### Required Python Packages

All packages from `requirements.txt` must be installed:

```bash
pip install -r requirements.txt
```

### System Requirements

- **Windows**: Windows 10 or higher
- **macOS**: macOS 10.14 or higher
- **Linux**: Ubuntu 20.04 or equivalent
- **RAM**: Minimum 4 GB (8 GB recommended for building)
- **Disk Space**: Minimum 500 MB free space

## Quick Start

### Basic Build

```bash
# Navigate to backend directory
cd solar-calculator-pro/backend

# Run the build script
python build_backend.py
```

### Build with All Options

```bash
# Clean, optimize, test, and package
python build_backend.py --clean --optimize --test --package
```

### Manual Build with PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller backend.spec
```

## Build Process

### Step-by-Step Process

#### 1. Preparation

The build script performs the following preparation steps:

- Checks Python version compatibility
- Verifies all dependencies are installed
- Installs PyInstaller if not present
- Creates runtime hooks

#### 2. Analysis

PyInstaller analyzes the application to determine:

- All Python modules used
- Required data files
- Binary dependencies
- Hidden imports

#### 3. Bundling

PyInstaller bundles everything into a single directory:

```
dist/backend/
├── backend.exe (or backend on Unix)
├── _internal/
│   ├── Python DLLs
│   ├── Dependencies
│   └── Data files
```

#### 4. Optimization (Optional)

The optimization step:

- Removes unnecessary files (tests, docs, etc.)
- Compresses binaries with UPX
- Strips debug symbols
- Reduces overall bundle size by 20-40%

#### 5. Testing (Optional)

Automated tests verify:

- Executable runs without errors
- All imports work correctly
- API endpoints are accessible
- Database connections work

#### 6. Packaging (Optional)

Creates a distribution package with:

- Executable and dependencies
- Startup scripts
- Configuration examples
- Documentation

## Optimization

### Bundle Size Optimization

#### Exclude Unnecessary Modules

The spec file already excludes common large modules:

```python
excludes=[
    'pytest',
    'matplotlib',
    'numpy',
    'pandas',
    'tkinter',
]
```

#### Use UPX Compression

UPX (Ultimate Packer for eXecutables) is enabled by default:

```python
upx=True,
upx_exclude=[],
```

To disable UPX:

```python
upx=False,
```

#### Remove Development Dependencies

Before building, create a production requirements file:

```bash
# Create production requirements (no dev dependencies)
pip freeze | grep -v "pytest\|black\|flake8\|mypy" > requirements-prod.txt

# Install only production dependencies
pip install -r requirements-prod.txt
```

### Performance Optimization

#### Precompile Python Files

```bash
python -m compileall .
```

#### Use --onefile (Not Recommended)

Creates a single executable file but slower startup:

```bash
pyinstaller --onefile main.py
```

**Note**: We use `--onedir` (default) for faster startup times.

## Testing

### Automated Testing

The build script includes automated tests:

```bash
python build_backend.py --test
```

### Manual Testing

#### Test 1: Basic Execution

```bash
cd dist/backend
./backend --help
```

Expected output: Uvicorn help message or server startup

#### Test 2: API Server

```bash
# Start the server
./backend

# In another terminal, test the API
curl http://localhost:8000/health
```

Expected output: `{"status": "healthy"}`

#### Test 3: Database Operations

```bash
# Check if database can be created
./backend

# Verify database file exists
ls *.db
```

#### Test 4: Import Verification

Create a test script `test_imports.py`:

```python
import sys
sys.path.insert(0, 'dist/backend')

# Test critical imports
try:
    import fastapi
    import sqlalchemy
    import uvicorn
    print("✓ All critical imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
```

### Performance Testing

#### Startup Time

```bash
time ./dist/backend/backend --help
```

Target: < 2 seconds

#### Memory Usage

```bash
# Start server
./dist/backend/backend &

# Check memory usage
ps aux | grep backend
```

Target: < 200 MB idle

## Distribution

### Creating Distribution Package

```bash
python build_backend.py --package
```

This creates `dist/backend-package/` with:

```
backend-package/
├── backend/           # Executable and dependencies
├── start-backend.bat  # Windows startup script
├── start-backend.sh   # Unix startup script
├── .env.example       # Configuration template
└── README.md          # User documentation
```

### Packaging for Electron

The backend executable should be placed in the Electron app:

```
electron-app/
├── resources/
│   └── backend/
│       ├── backend.exe (Windows)
│       ├── backend (macOS/Linux)
│       └── _internal/
```

### Creating Installers

#### Windows (NSIS)

```nsis
; Include backend in installer
Section "Backend"
  SetOutPath "$INSTDIR\resources\backend"
  File /r "dist\backend\*.*"
SectionEnd
```

#### macOS (DMG)

```bash
# Copy backend to app bundle
cp -r dist/backend MyApp.app/Contents/Resources/backend
```

#### Linux (AppImage)

```bash
# Include backend in AppDir
cp -r dist/backend AppDir/usr/bin/backend
```

## Troubleshooting

### Common Issues

#### Issue: "Module not found" Error

**Cause**: PyInstaller missed a hidden import

**Solution**: Add to `hiddenimports` in `backend.spec`:

```python
hiddenimports = [
    'your.missing.module',
]
```

#### Issue: Large Bundle Size (>200 MB)

**Cause**: Unnecessary dependencies included

**Solution**: 
1. Check what's included: `pyinstaller --log-level=DEBUG backend.spec`
2. Add exclusions to spec file
3. Use `--optimize` flag

#### Issue: Slow Startup Time (>5 seconds)

**Cause**: Too many files in bundle

**Solution**:
1. Use `--onedir` instead of `--onefile`
2. Reduce number of dependencies
3. Precompile Python files

#### Issue: "Permission Denied" on Linux/macOS

**Cause**: Executable doesn't have execute permission

**Solution**:

```bash
chmod +x dist/backend/backend
```

#### Issue: Database Connection Fails

**Cause**: Database path not correctly resolved in bundled app

**Solution**: Use absolute paths or environment variables:

```python
import sys
import os

if getattr(sys, 'frozen', False):
    # Running in bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python
    base_path = os.path.dirname(__file__)

db_path = os.path.join(base_path, 'database.db')
```

#### Issue: Static Files Not Found

**Cause**: Static files not included in bundle

**Solution**: Add to `datas` in spec file:

```python
datas = [
    ('static', 'static'),
    ('templates', 'templates'),
]
```

### Debug Mode

Build with debug mode for troubleshooting:

```python
# In backend.spec
exe = EXE(
    ...
    debug=True,  # Enable debug mode
    console=True,  # Show console output
)
```

### Logging

Enable detailed logging:

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Platform-Specific Notes

### Windows

#### Code Signing

For production, sign the executable:

```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.server backend.exe
```

#### Antivirus False Positives

PyInstaller executables may trigger antivirus warnings. Solutions:

1. Sign the executable with a valid certificate
2. Submit to antivirus vendors for whitelisting
3. Use `--noupx` to avoid UPX compression

#### DLL Dependencies

Check DLL dependencies:

```bash
dumpbin /dependents backend.exe
```

### macOS

#### Code Signing and Notarization

Required for distribution:

```bash
# Sign the executable
codesign --force --sign "Developer ID Application: Your Name" backend

# Notarize with Apple
xcrun altool --notarize-app --file backend.zip
```

#### Gatekeeper

Users may need to allow the app:

```bash
xattr -cr backend
```

### Linux

#### Library Dependencies

Check library dependencies:

```bash
ldd backend
```

#### AppImage Creation

```bash
# Create AppImage
appimagetool AppDir backend.AppImage
```

## Advanced Topics

### Custom Hooks

Create custom PyInstaller hooks for complex dependencies:

```python
# hook-mymodule.py
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mymodule')
```

### Multi-Platform Builds

Use CI/CD to build for all platforms:

```yaml
# .github/workflows/build.yml
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - name: Build
        run: python build_backend.py --clean --optimize --package
```

### Incremental Builds

Speed up development builds:

```bash
# Skip clean for faster builds
python build_backend.py --optimize
```

### Bundle Analysis

Analyze what's in your bundle:

```bash
# Generate analysis report
pyinstaller --log-level=DEBUG backend.spec 2>&1 | tee build.log

# Check bundle contents
ls -lh dist/backend/_internal/
```

## Best Practices

1. **Always test the executable** before distribution
2. **Keep dependencies minimal** to reduce bundle size
3. **Use virtual environments** for clean builds
4. **Version your builds** for tracking
5. **Document any platform-specific requirements**
6. **Test on clean systems** without Python installed
7. **Monitor bundle size** and optimize regularly
8. **Keep PyInstaller updated** for bug fixes
9. **Use CI/CD** for consistent builds
10. **Sign executables** for production releases

## Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Electron Builder](https://www.electron.build/)
- [UPX Compressor](https://upx.github.io/)

## Support

For issues specific to backend packaging:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review PyInstaller logs in `build/backend/`
3. Test with `--debug` flag enabled
4. Consult the main project documentation

## Changelog

### Version 1.0.0
- Initial packaging setup
- PyInstaller spec file
- Build automation script
- Comprehensive documentation
- Multi-platform support
