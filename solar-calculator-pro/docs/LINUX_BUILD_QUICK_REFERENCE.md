# Linux Build Quick Reference

Quick reference guide for building Solar Calculator Pro on Linux.

## Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nodejs npm python3 python3-pip \
  libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils

# Fedora
sudo dnf install -y nodejs npm python3 python3-pip \
  gtk3 libnotify nss libXScrnSaver libXtst xdg-utils

# Install PyInstaller
pip3 install pyinstaller
```

## Quick Build Commands

```bash
# Full build (all package types)
npm run electron:build:linux

# Build specific package type
npm run electron:build:linux -- --linux AppImage
npm run electron:build:linux -- --linux deb
npm run electron:build:linux -- --linux rpm
npm run electron:build:linux -- --linux snap

# Using build script
node build/build-linux.js
```

## Package Installation

### AppImage
```bash
chmod +x Solar\ Calculator\ Pro-1.0.0.AppImage
./Solar\ Calculator\ Pro-1.0.0.AppImage
```

### DEB (Ubuntu/Debian)
```bash
sudo apt install ./solar-calculator-pro_1.0.0_amd64.deb
```

### RPM (Fedora/RHEL)
```bash
sudo dnf install solar-calculator-pro-1.0.0.x86_64.rpm
```

### Snap
```bash
sudo snap install solar-calculator-pro_1.0.0_amd64.snap --dangerous
```

## Build Targets

| Target | Command | Output |
|--------|---------|--------|
| AppImage | `--linux AppImage` | Universal Linux package |
| DEB | `--linux deb` | Debian/Ubuntu package |
| RPM | `--linux rpm` | Fedora/RHEL package |
| Snap | `--linux snap` | Snap package |
| All | `--linux` | All package types |

## Common Issues

### Missing Libraries
```bash
# Check missing libraries
ldd release/linux-unpacked/solar-calculator-pro

# Install missing
sudo apt-get install <library-name>
```

### PyInstaller Not Found
```bash
pip3 install --user pyinstaller
export PATH="$HOME/.local/bin:$PATH"
```

### AppImage Won't Run
```bash
# Install FUSE
sudo apt-get install fuse libfuse2

# Make executable
chmod +x Solar\ Calculator\ Pro-1.0.0.AppImage
```

### Build Out of Memory
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run electron:build:linux
```

## Build Configuration

### package.json
```json
{
  "build": {
    "linux": {
      "target": ["AppImage", "deb", "rpm"],
      "icon": "assets/icon.png",
      "category": "Office"
    }
  }
}
```

### Desktop Entry
Location: `build/linux/solar-calculator-pro.desktop`

### Post-Install Scripts
- `build/linux/postinst.sh` - Run after installation
- `build/linux/postrm.sh` - Run after removal

## Build Artifacts

After successful build, find artifacts in `release/`:
- `Solar Calculator Pro-1.0.0.AppImage`
- `solar-calculator-pro_1.0.0_amd64.deb`
- `solar-calculator-pro-1.0.0.x86_64.rpm`
- `solar-calculator-pro_1.0.0_amd64.snap`
- `build-report-linux.json`

## Environment Variables

```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=4096"

# Skip code signing
export CSC_IDENTITY_AUTO_DISCOVERY=false

# Custom build directory
export BUILD_DIR="./custom-build"
```

## Verification

```bash
# Verify AppImage
file Solar\ Calculator\ Pro-1.0.0.AppImage
chmod +x Solar\ Calculator\ Pro-1.0.0.AppImage

# Verify DEB package
dpkg-deb -I solar-calculator-pro_1.0.0_amd64.deb
dpkg-deb -c solar-calculator-pro_1.0.0_amd64.deb

# Verify RPM package
rpm -qip solar-calculator-pro-1.0.0.x86_64.rpm
rpm -qlp solar-calculator-pro-1.0.0.x86_64.rpm
```

## Distribution

### GitHub Release
```bash
# Create release and upload artifacts
gh release create v1.0.0 \
  release/Solar\ Calculator\ Pro-1.0.0.AppImage \
  release/solar-calculator-pro_1.0.0_amd64.deb \
  release/solar-calculator-pro-1.0.0.x86_64.rpm
```

### Snap Store
```bash
snapcraft login
snapcraft upload solar-calculator-pro_1.0.0_amd64.snap --release=stable
```

## CI/CD Example

```yaml
# .github/workflows/build-linux.yml
name: Build Linux
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Build
        run: node build/build-linux.js
      - name: Upload
        uses: actions/upload-artifact@v3
        with:
          name: linux-builds
          path: release/*
```

## Optimization Tips

1. **Reduce size:**
   ```bash
   strip backend/dist/main
   upx --best backend/dist/main
   ```

2. **Faster builds:**
   ```bash
   npm run electron:build:linux -- --dir  # Skip packaging
   ```

3. **Parallel builds:**
   ```bash
   npm run electron:build:linux -- --parallel
   ```

## Support

- Full guide: `docs/LINUX_BUILD_GUIDE.md`
- Build logs: `release/build-report-linux.json`
- Issues: GitHub Issues

## Useful Links

- [electron-builder Linux docs](https://www.electron.build/configuration/linux)
- [AppImage documentation](https://docs.appimage.org/)
- [Debian packaging guide](https://www.debian.org/doc/manuals/maint-guide/)
- [RPM packaging guide](https://rpm-packaging-guide.github.io/)
- [Snap documentation](https://snapcraft.io/docs)
