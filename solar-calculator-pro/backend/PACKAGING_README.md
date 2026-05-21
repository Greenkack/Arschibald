# Backend Packaging

This directory contains everything needed to package the Solar Calculator Pro backend into a standalone executable.

## Quick Start

```bash
# Install PyInstaller
pip install pyinstaller

# Build the backend
python build_backend.py --clean --optimize --test --package
```

## Files

| File | Description |
|------|-------------|
| `backend.spec` | PyInstaller specification file |
| `build_backend.py` | Automated build script |
| `test_packaging.py` | Test suite for packaged executable |
| `runtime_hook.py` | Runtime hook for PyInstaller (auto-generated) |
| `PACKAGING_README.md` | This file |

## Documentation

- **Full Guide**: `docs/BACKEND_PACKAGING_GUIDE.md`
- **Quick Reference**: `docs/BACKEND_PACKAGING_QUICK_REFERENCE.md`

## Build Options

### Basic Build
```bash
python build_backend.py
```

### Clean Build
```bash
python build_backend.py --clean
```

### Optimized Build
```bash
python build_backend.py --optimize
```

### Build with Testing
```bash
python build_backend.py --test
```

### Create Distribution Package
```bash
python build_backend.py --package
```

### All Options
```bash
python build_backend.py --clean --optimize --test --package
```

## Output

After building, you'll find:

```
dist/
├── backend/              # Executable and dependencies
│   ├── backend(.exe)     # Main executable
│   └── _internal/        # Dependencies and data files
└── backend-package/      # Distribution package (if --package used)
    ├── backend/          # Executable directory
    ├── start-backend.*   # Startup script
    ├── .env.example      # Configuration template
    └── README.md         # User documentation
```

## Testing

### Automated Testing
```bash
python test_packaging.py
```

### Manual Testing
```bash
# Navigate to output directory
cd dist/backend

# Run the executable
./backend  # Unix
backend.exe  # Windows

# Test API
curl http://localhost:8000/health
```

## Platform-Specific Notes

### Windows
- Output: `backend.exe`
- May trigger antivirus warnings (false positive)
- Consider code signing for production

### macOS
- Output: `backend`
- Requires code signing and notarization for distribution
- May need: `xattr -cr backend`

### Linux
- Output: `backend`
- Check dependencies: `ldd backend`
- Set permissions: `chmod +x backend`

## Integration with Electron

The packaged backend should be placed in the Electron app's resources:

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

## Troubleshooting

### Common Issues

**Module not found**
- Add to `hiddenimports` in `backend.spec`

**File not found**
- Add to `datas` in `backend.spec`

**Large bundle size**
- Use `--optimize` flag
- Exclude unnecessary modules in spec file

**Permission denied (Unix)**
```bash
chmod +x dist/backend/backend
```

**Slow startup**
- Use `--onedir` (default) instead of `--onefile`
- Reduce number of dependencies

## Size Optimization

Current bundle sizes (approximate):
- Windows: 80-100 MB
- macOS: 70-90 MB
- Linux: 60-80 MB

To reduce size:
1. Use `--optimize` flag
2. Exclude dev dependencies
3. Remove unnecessary modules
4. Enable UPX compression (default)

## Requirements

- Python 3.10+
- PyInstaller 6.0+
- All dependencies from `requirements.txt`
- 500 MB free disk space
- 4 GB RAM (8 GB recommended)

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build Backend

on: [push]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build backend
        run: python build_backend.py --clean --optimize --package
      
      - name: Test backend
        run: python test_packaging.py
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: backend-${{ matrix.os }}
          path: dist/backend-package/
```

## Support

For issues:
1. Check `docs/BACKEND_PACKAGING_GUIDE.md`
2. Review build logs in `build/`
3. Enable debug mode in `backend.spec`
4. Run tests with `python test_packaging.py`

## Version History

### 1.0.0 (Current)
- Initial packaging setup
- PyInstaller spec file
- Automated build script
- Comprehensive testing
- Multi-platform support
- Documentation

## License

Same as main project license.

## Contributing

When modifying the packaging:
1. Update `backend.spec` for new dependencies
2. Test on all platforms
3. Update documentation
4. Run full test suite
5. Check bundle size

## Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Electron Builder](https://www.electron.build/)
