# Backend Packaging - Quick Start Guide

Get your backend packaged in 5 minutes! 🚀

## Prerequisites

- Python 3.10 or higher
- All dependencies installed (`pip install -r requirements.txt`)

## Step 1: Navigate to Backend Directory

```bash
cd solar-calculator-pro/backend
```

## Step 2: Run the Build Script

### Option A: Basic Build (Fastest)
```bash
python build_backend.py
```

### Option B: Production Build (Recommended)
```bash
python build_backend.py --clean --optimize --test --package
```

## Step 3: Find Your Executable

Your executable is ready at:
```
dist/backend/backend(.exe)
```

## Step 4: Test It

```bash
# Navigate to output directory
cd dist/backend

# Run the executable
./backend  # Unix (macOS/Linux)
backend.exe  # Windows

# Test the API
curl http://localhost:8000/health
```

## That's It! 🎉

Your backend is now packaged as a standalone executable.

## What Next?

### For Development
- Test all functionality
- Check bundle size: `du -sh dist/backend/`
- Run automated tests: `python test_packaging.py`

### For Production
- Sign the executable (see platform-specific guides)
- Create installer (NSIS/DMG/AppImage)
- Integrate with Electron app

### For Distribution
- Use the distribution package: `dist/backend-package/`
- Includes startup scripts and documentation
- Ready to ship to users

## Need Help?

- **Full Guide**: `docs/BACKEND_PACKAGING_GUIDE.md`
- **Quick Reference**: `docs/BACKEND_PACKAGING_QUICK_REFERENCE.md`
- **Troubleshooting**: Check the guides above

## Common Commands

```bash
# Clean build
python build_backend.py --clean

# Optimized build
python build_backend.py --optimize

# Build with tests
python build_backend.py --test

# Create distribution package
python build_backend.py --package

# All options
python build_backend.py --clean --optimize --test --package

# Test executable
python test_packaging.py

# Manual PyInstaller
pyinstaller backend.spec
```

## Build Options Explained

| Option | What It Does | When to Use |
|--------|--------------|-------------|
| `--clean` | Removes old build files | First build or after changes |
| `--optimize` | Reduces bundle size by 20-40% | Production builds |
| `--test` | Runs automated tests | Before distribution |
| `--package` | Creates distribution package | For end users |

## Expected Results

### Build Time
- First build: 2-5 minutes
- Subsequent builds: 30-60 seconds

### Bundle Size
- Windows: ~80-100 MB
- macOS: ~70-90 MB
- Linux: ~60-80 MB

### Performance
- Startup: ~2 seconds
- Memory: ~150 MB idle
- Response: ~50 ms

## Troubleshooting Quick Fixes

### "Module not found"
Add to `hiddenimports` in `backend.spec`

### "Permission denied" (Unix)
```bash
chmod +x dist/backend/backend
```

### Large bundle size
```bash
python build_backend.py --optimize
```

### Build fails
```bash
# Check dependencies
pip install -r requirements.txt

# Try clean build
python build_backend.py --clean
```

## Platform-Specific Notes

### Windows
- Output: `backend.exe`
- May trigger antivirus (false positive)
- Consider code signing

### macOS
- Output: `backend`
- May need: `xattr -cr backend`
- Consider code signing + notarization

### Linux
- Output: `backend`
- Check deps: `ldd backend`
- Set permissions: `chmod +x backend`

## Integration with Electron

Place backend in Electron app:
```
electron-app/
└── resources/
    └── backend/
        ├── backend(.exe)
        └── _internal/
```

Start from Electron:
```javascript
const backendPath = path.join(
  process.resourcesPath,
  'backend',
  process.platform === 'win32' ? 'backend.exe' : 'backend'
);

const backend = spawn(backendPath);
```

## Success Checklist

- [ ] Build completes without errors
- [ ] Executable runs
- [ ] Server starts successfully
- [ ] API responds to requests
- [ ] Bundle size is reasonable
- [ ] Performance is acceptable
- [ ] Tests pass (if run)

## Resources

- Full documentation in `docs/` directory
- Test suite: `test_packaging.py`
- Build script: `build_backend.py`
- Spec file: `backend.spec`

## Support

If you encounter issues:
1. Check the full guide: `docs/BACKEND_PACKAGING_GUIDE.md`
2. Review troubleshooting section
3. Enable debug mode in `backend.spec`
4. Run tests: `python test_packaging.py`

---

**Happy Packaging! 🎉**
