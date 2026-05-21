# Linux Build Guide for Solar Calculator Pro

This guide provides comprehensive instructions for building Solar Calculator Pro on Linux systems.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Process](#build-process)
3. [Package Types](#package-types)
4. [Build Configuration](#build-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Distribution](#distribution)

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 18.04+, Debian 10+, Fedora 30+, or compatible Linux distribution
- **Architecture**: x64 (AMD64) or ARM64
- **RAM**: Minimum 4GB, recommended 8GB
- **Disk Space**: Minimum 2GB free space

### Required Software

#### Node.js and npm

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Fedora
sudo dnf install nodejs npm

# Verify installation
node --version  # Should be v18.x or higher
npm --version   # Should be v9.x or higher
```

#### Python 3

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Verify installation
python3 --version  # Should be 3.8 or higher
pip3 --version
```

#### PyInstaller

```bash
pip3 install pyinstaller
```

#### System Libraries

```bash
# Ubuntu/Debian
sudo apt-get install -y \
  libgtk-3-0 \
  libnotify4 \
  libnss3 \
  libxss1 \
  libxtst6 \
  xdg-utils \
  libatspi2.0-0 \
  libuuid1 \
  libsecret-1-0 \
  libappindicator3-1

# Fedora
sudo dnf install -y \
  gtk3 \
  libnotify \
  nss \
  libXScrnSaver \
  libXtst \
  xdg-utils
```

#### Build Tools (Optional)

For advanced packaging:

```bash
# Ubuntu/Debian
sudo apt-get install -y build-essential fakeroot dpkg-dev rpm

# Fedora
sudo dnf install -y @development-tools rpm-build

# fpm (for advanced DEB/RPM packaging)
sudo gem install fpm
```

## Build Process

### Quick Build

```bash
# Clone the repository
git clone https://github.com/your-org/solar-calculator-pro.git
cd solar-calculator-pro

# Install dependencies
npm install

# Build for Linux
npm run electron:build:linux
```

### Step-by-Step Build

#### 1. Install Dependencies

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
pip3 install -r requirements.txt
cd ..
```

#### 2. Build Frontend

```bash
cd frontend
npm run build
cd ..
```

#### 3. Build Backend

```bash
cd backend
pyinstaller main-linux.spec --clean --noconfirm
cd ..
```

#### 4. Build Electron Application

```bash
npm run electron:build:linux
```

### Using the Build Script

The automated build script handles all steps:

```bash
node build/build-linux.js
```

This script will:
- Check prerequisites
- Clean previous builds
- Create desktop entry files
- Build frontend
- Build backend with PyInstaller
- Package with electron-builder
- Create AppImage and DEB packages
- Verify build artifacts
- Generate build report

## Package Types

### AppImage

**Advantages:**
- Universal Linux package
- No installation required
- Runs on most distributions
- Self-contained

**Usage:**
```bash
chmod +x Solar\ Calculator\ Pro-1.0.0.AppImage
./Solar\ Calculator\ Pro-1.0.0.AppImage
```

**Integration:**
```bash
# Optional: Integrate with system
./Solar\ Calculator\ Pro-1.0.0.AppImage --appimage-extract
sudo mv squashfs-root /opt/solar-calculator-pro
sudo ln -s /opt/solar-calculator-pro/AppRun /usr/local/bin/solar-calculator-pro
```

### DEB Package (Debian/Ubuntu)

**Installation:**
```bash
# Method 1: Using dpkg
sudo dpkg -i solar-calculator-pro_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Method 2: Using apt (recommended)
sudo apt install ./solar-calculator-pro_1.0.0_amd64.deb
```

**Uninstallation:**
```bash
sudo apt remove solar-calculator-pro
```

**Package Contents:**
- `/usr/lib/solar-calculator-pro/` - Application files
- `/usr/share/applications/solar-calculator-pro.desktop` - Desktop entry
- `/usr/share/icons/hicolor/*/apps/solar-calculator-pro.png` - Application icons
- `/usr/bin/solar-calculator-pro` - Executable symlink

### RPM Package (Fedora/RHEL/CentOS)

**Installation:**
```bash
# Method 1: Using rpm
sudo rpm -i solar-calculator-pro-1.0.0.x86_64.rpm

# Method 2: Using dnf (recommended)
sudo dnf install solar-calculator-pro-1.0.0.x86_64.rpm
```

**Uninstallation:**
```bash
sudo dnf remove solar-calculator-pro
```

### Snap Package

**Installation:**
```bash
sudo snap install solar-calculator-pro_1.0.0_amd64.snap --dangerous
```

**Note:** The `--dangerous` flag is needed for locally built snaps. For Snap Store distribution, this is not required.

## Build Configuration

### electron-builder Configuration

The build configuration is in `package.json`:

```json
{
  "build": {
    "linux": {
      "target": ["AppImage", "deb", "rpm", "snap"],
      "icon": "assets/icon.png",
      "category": "Office",
      "maintainer": "Your Company <support@yourcompany.com>",
      "desktop": {
        "Name": "Solar Calculator Pro",
        "Comment": "Professional Solar Calculator",
        "Categories": "Office;Finance;Engineering;"
      }
    }
  }
}
```

### Desktop Entry

The desktop entry file (`solar-calculator-pro.desktop`) defines:
- Application name and description
- Icon and executable paths
- MIME type associations
- Application categories
- Quick actions

### File Associations

The application registers handlers for:
- `.scp` files (Solar Calculator Project)
- `solarcalc://` URL scheme

### Custom Icons

Place custom icons in the `assets/` directory:
- `icon.png` - Main application icon (512x512 recommended)
- `file-icon.png` - File type icon (256x256 recommended)

Multiple sizes for better integration:
```
assets/icons/
  16x16/solar-calculator-pro.png
  32x32/solar-calculator-pro.png
  48x48/solar-calculator-pro.png
  128x128/solar-calculator-pro.png
  256x256/solar-calculator-pro.png
  512x512/solar-calculator-pro.png
```

## Troubleshooting

### Build Fails with "PyInstaller not found"

```bash
pip3 install --user pyinstaller
# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Missing System Libraries

```bash
# Check for missing libraries
ldd release/linux-unpacked/solar-calculator-pro

# Install missing libraries
sudo apt-get install <library-name>
```

### AppImage Won't Run

```bash
# Make executable
chmod +x Solar\ Calculator\ Pro-1.0.0.AppImage

# Check for FUSE
sudo apt-get install fuse libfuse2

# Extract and run manually
./Solar\ Calculator\ Pro-1.0.0.AppImage --appimage-extract
./squashfs-root/AppRun
```

### DEB Package Installation Fails

```bash
# Check dependencies
dpkg -I solar-calculator-pro_1.0.0_amd64.deb

# Fix broken dependencies
sudo apt-get install -f
```

### Backend Binary Not Executable

```bash
chmod +x backend/dist/main
```

### Build Runs Out of Memory

```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run electron:build:linux
```

### Python Module Import Errors

```bash
# Ensure all dependencies are installed
cd backend
pip3 install -r requirements.txt

# Check for missing hidden imports in PyInstaller spec
# Edit backend/main-linux.spec and add to hiddenimports list
```

## Distribution

### GitHub Releases

1. Create a new release on GitHub
2. Upload build artifacts:
   - `Solar Calculator Pro-1.0.0.AppImage`
   - `solar-calculator-pro_1.0.0_amd64.deb`
   - `solar-calculator-pro-1.0.0.x86_64.rpm`
   - `solar-calculator-pro_1.0.0_amd64.snap`

### Snap Store

```bash
# Login to Snap Store
snapcraft login

# Upload snap
snapcraft upload solar-calculator-pro_1.0.0_amd64.snap --release=stable
```

### Flatpak (Alternative)

Create a Flatpak manifest and submit to Flathub:
```bash
flatpak-builder build-dir com.yourcompany.SolarCalculatorPro.yml
flatpak-builder --repo=repo build-dir com.yourcompany.SolarCalculatorPro.yml
```

### PPA (Ubuntu/Debian)

1. Create source package
2. Upload to Launchpad PPA
3. Users can install via:
```bash
sudo add-apt-repository ppa:yourname/solar-calculator-pro
sudo apt-get update
sudo apt-get install solar-calculator-pro
```

### AUR (Arch Linux)

Create a PKGBUILD file and submit to AUR:
```bash
# Example PKGBUILD structure
pkgname=solar-calculator-pro
pkgver=1.0.0
pkgrel=1
arch=('x86_64')
# ... rest of PKGBUILD
```

## Build Optimization

### Reduce Package Size

1. **Strip debug symbols:**
```bash
strip backend/dist/main
```

2. **Optimize frontend build:**
```bash
cd frontend
npm run build -- --mode production
```

3. **Use UPX compression:**
```bash
# Install UPX
sudo apt-get install upx

# Compress binary
upx --best backend/dist/main
```

### Faster Builds

1. **Use build cache:**
```bash
# electron-builder uses cache by default
# Cache location: ~/.cache/electron-builder
```

2. **Parallel builds:**
```bash
# Build multiple targets in parallel
npm run electron:build:linux -- --parallel
```

3. **Skip unnecessary steps:**
```bash
# Skip frontend rebuild if unchanged
npm run electron:build:linux -- --dir
```

## Security Considerations

### Code Signing

Linux doesn't require code signing like Windows/macOS, but you can:

1. **Sign DEB packages:**
```bash
dpkg-sig --sign builder solar-calculator-pro_1.0.0_amd64.deb
```

2. **Sign RPM packages:**
```bash
rpm --addsign solar-calculator-pro-1.0.0.x86_64.rpm
```

3. **GPG signatures:**
```bash
gpg --detach-sign --armor Solar\ Calculator\ Pro-1.0.0.AppImage
```

### Sandboxing

Consider using:
- **Snap confinement:** Strict confinement for better security
- **Flatpak sandbox:** Isolated runtime environment
- **AppArmor profiles:** Additional security layer

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Linux

on:
  push:
    tags:
      - 'v*'

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6
          npm install
          pip3 install pyinstaller
      
      - name: Build
        run: node build/build-linux.js
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-builds
          path: release/*
```

## Support

For build issues:
- Check the [Troubleshooting](#troubleshooting) section
- Review build logs in `release/build-report-linux.json`
- Open an issue on GitHub with build logs

For distribution questions:
- Consult distribution-specific documentation
- Check electron-builder documentation
- Review Linux packaging best practices
