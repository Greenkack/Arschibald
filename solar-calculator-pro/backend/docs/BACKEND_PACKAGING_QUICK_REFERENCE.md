# Backend Packaging Quick Reference

Quick commands and tips for packaging the Solar Calculator Pro backend.

## Quick Commands

### Basic Build
```bash
python build_backend.py
```

### Full Build (Recommended)
```bash
python build_backend.py --clean --optimize --test --package
```

### Manual PyInstaller
```bash
pyinstaller backend.spec
```

## Common Options

| Option | Description |
|--------|-------------|
| `--clean` | Remove old build files before building |
| `--optimize` | Apply size optimizations (removes ~20-40% size) |
| `--test` | Run automated tests on built executable |
| `--package` | Create distribution package with docs |
| `--keep-spec` | Don't regenerate spec file |

## File Locations

| Item | Location |
|------|----------|
| Spec File | `backend.spec` |
| Build Script | `build_backend.py` |
| Output Executable | `dist/backend/backend(.exe)` |
| Build Artifacts | `build/` |
| Distribution Package | `dist/backend-package/` |

## Quick Checks

### Check if Executable Works
```bash
cd dist/backend
./backend --help
```

### Check Bundle Size
```bash
du -sh dist/backend/
```

### Check Dependencies
```bash
ldd dist/backend/backend  # Linux
otool -L dist/backend/backend  # macOS
dumpbin /dependents dist/backend/backend.exe  # Windows
```

## Troubleshooting Quick Fixes

### Module Not Found
Add to `hiddenimports` in `backend.spec`:
```python
hiddenimports = [
    'missing.module.name',
]
```

### File Not Found
Add to `datas` in `backend.spec`:
```python
datas = [
    ('path/to/file', 'destination'),
]
```

### Permission Denied (Unix)
```bash
chmod +x dist/backend/backend
```

### Large Bundle Size
```bash
python build_backend.py --optimize
```

## Size Optimization Tips

1. **Remove dev dependencies** before building
2. **Use `--optimize` flag**
3. **Exclude unnecessary modules** in spec file
4. **Enable UPX compression** (default)
5. **Remove test files** from bundle

## Testing Checklist

- [ ] Executable runs without errors
- [ ] API server starts successfully
- [ ] Database operations work
- [ ] All imports resolve correctly
- [ ] Bundle size is reasonable (<200 MB)
- [ ] Startup time is acceptable (<3 seconds)
- [ ] Memory usage is normal (<200 MB idle)

## Platform-Specific Notes

### Windows
- Output: `backend.exe`
- Sign with: `signtool`
- May trigger antivirus (false positive)

### macOS
- Output: `backend`
- Sign with: `codesign`
- Notarize with: `xcrun altool`
- May need: `xattr -cr backend`

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

Start backend from Electron:
```javascript
const backendPath = path.join(
  process.resourcesPath,
  'backend',
  process.platform === 'win32' ? 'backend.exe' : 'backend'
);

const backend = spawn(backendPath);
```

## Environment Variables

Set in `.env` file:
```bash
PORT=8000
HOST=localhost
DEBUG=false
DATABASE_URL=sqlite:///./database.db
```

## Build Performance

| Action | Time (approx) |
|--------|---------------|
| Clean build | 2-5 minutes |
| Incremental build | 30-60 seconds |
| With optimization | +30 seconds |
| With testing | +15 seconds |

## Bundle Size Targets

| Platform | Target Size | Maximum |
|----------|-------------|---------|
| Windows | 80 MB | 150 MB |
| macOS | 70 MB | 140 MB |
| Linux | 60 MB | 130 MB |

## Common Errors

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Add to `hiddenimports` |
| `FileNotFoundError` | Add to `datas` |
| `Permission denied` | Run `chmod +x` |
| `DLL not found` (Windows) | Include in `binaries` |
| `Library not found` (Unix) | Check with `ldd`/`otool` |

## Resources

- Full Guide: `docs/BACKEND_PACKAGING_GUIDE.md`
- PyInstaller Docs: https://pyinstaller.readthedocs.io/
- Spec File: `backend.spec`
- Build Script: `build_backend.py`

## Support

1. Check full documentation
2. Review build logs in `build/`
3. Enable debug mode in spec file
4. Test with `--test` flag

## Version Info

- PyInstaller: 6.0+
- Python: 3.10+
- FastAPI: 0.104+
- Platform: Windows/macOS/Linux
