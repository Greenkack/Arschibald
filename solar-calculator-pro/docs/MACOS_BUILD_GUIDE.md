# macOS Build Guide for Solar Calculator Pro

This guide provides comprehensive instructions for building Solar Calculator Pro for macOS, including code signing and notarization.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Code Signing Setup](#code-signing-setup)
4. [Notarization Setup](#notarization-setup)
5. [Building the Application](#building-the-application)
6. [Build Artifacts](#build-artifacts)
7. [Troubleshooting](#troubleshooting)
8. [Distribution](#distribution)

## Prerequisites

### System Requirements

- **macOS**: 10.15 (Catalina) or later
- **Xcode Command Line Tools**: Required for code signing
- **Node.js**: 18.x or later
- **Python**: 3.10 or later
- **npm**: 9.x or later

### Install Xcode Command Line Tools

```bash
xcode-select --install
```

Verify installation:

```bash
xcode-select -p
# Should output: /Library/Developer/CommandLineTools
```

### Install Node.js and npm

Using Homebrew:

```bash
brew install node
```

Verify installation:

```bash
node --version  # Should be 18.x or later
npm --version   # Should be 9.x or later
```

### Install Python

Using Homebrew:

```bash
brew install python@3.10
```

Verify installation:

```bash
python3 --version  # Should be 3.10 or later
```

### Install PyInstaller

```bash
pip3 install pyinstaller
```

Verify installation:

```bash
pyinstaller --version
```

## Environment Setup

### Clone the Repository

```bash
git clone https://github.com/your-org/solar-calculator-pro.git
cd solar-calculator-pro
```

### Install Dependencies

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

## Code Signing Setup

Code signing is required for macOS applications to run without security warnings.

### 1. Join Apple Developer Program

- Go to https://developer.apple.com
- Enroll in the Apple Developer Program ($99/year)
- Wait for approval (usually 24-48 hours)

### 2. Create Certificates

1. Open **Keychain Access** on your Mac
2. Go to **Keychain Access > Certificate Assistant > Request a Certificate from a Certificate Authority**
3. Enter your email and name
4. Select "Saved to disk"
5. Save the certificate request file

6. Go to https://developer.apple.com/account/resources/certificates
7. Click the "+" button to create a new certificate
8. Select **"Developer ID Application"** (for distribution outside the Mac App Store)
9. Upload your certificate request file
10. Download the certificate
11. Double-click to install it in Keychain Access

### 3. Find Your Signing Identity

```bash
security find-identity -v -p codesigning
```

Look for an identity like:
```
1) XXXXXXXXXX "Developer ID Application: Your Name (TEAM_ID)"
```

Copy the full identity string (including quotes).

### 4. Set Environment Variable

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export MACOS_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
```

Reload your shell:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

## Notarization Setup

Notarization is required for macOS 10.15+ to prevent Gatekeeper warnings.

### 1. Create App-Specific Password

1. Go to https://appleid.apple.com
2. Sign in with your Apple ID
3. Go to **Security** section
4. Under **App-Specific Passwords**, click **Generate Password**
5. Enter a label (e.g., "Solar Calculator Notarization")
6. Copy the generated password (format: xxxx-xxxx-xxxx-xxxx)

### 2. Find Your Team ID

1. Go to https://developer.apple.com/account
2. Click **Membership** in the sidebar
3. Your Team ID is listed (10 characters, e.g., ABCDE12345)

### 3. Set Environment Variables

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export APPLE_ID="your-apple-id@example.com"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # App-specific password
export APPLE_TEAM_ID="ABCDE12345"
```

Reload your shell:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

### 4. Store Credentials in Keychain (Optional but Recommended)

```bash
xcrun notarytool store-credentials "solar-calculator-notarization" \
  --apple-id "your-apple-id@example.com" \
  --team-id "ABCDE12345" \
  --password "xxxx-xxxx-xxxx-xxxx"
```

## Building the Application

### Quick Build

```bash
npm run electron:build:mac
```

This will:
1. Build the frontend (React)
2. Package the backend (Python with PyInstaller)
3. Create the Electron app
4. Sign the app (if credentials are configured)
5. Create a DMG installer
6. Notarize the app (if credentials are configured)

### Custom Build Script

For more control, use the custom build script:

```bash
node build/build-macos.js
```

This script provides:
- Detailed logging
- Prerequisite checks
- Build verification
- Code signing verification
- Notarization status
- Build report generation

### Build for Specific Architecture

Build for Intel (x64):
```bash
npm run electron:build:mac -- --x64
```

Build for Apple Silicon (arm64):
```bash
npm run electron:build:mac -- --arm64
```

Build for both (universal):
```bash
npm run electron:build:mac -- --universal
```

## Build Artifacts

After a successful build, you'll find the following in the `release/` directory:

### DMG Installer

```
Solar Calculator Pro-1.0.0-x64.dmg
Solar Calculator Pro-1.0.0-arm64.dmg
```

The DMG file is the primary distribution format for macOS. Users can:
1. Double-click to mount the DMG
2. Drag the app to the Applications folder
3. Eject the DMG

### ZIP Archive

```
Solar Calculator Pro-1.0.0-x64-mac.zip
Solar Calculator Pro-1.0.0-arm64-mac.zip
```

The ZIP archive contains the `.app` bundle and can be used for:
- Direct distribution
- Automated deployment
- Testing

### App Bundle

```
release/mac/Solar Calculator Pro.app
```

The `.app` bundle is the actual application. It can be:
- Copied directly to Applications
- Distributed via ZIP
- Used for testing

### Build Report

```
release/build-report-macos.json
```

Contains detailed information about the build:
- Build date and version
- Environment details
- Artifacts list
- Signing status
- Notarization status

## Troubleshooting

### Code Signing Issues

#### "No identity found"

**Problem**: Code signing identity not found.

**Solution**:
1. Verify certificate is installed: `security find-identity -v -p codesigning`
2. Check environment variable: `echo $MACOS_SIGNING_IDENTITY`
3. Ensure certificate is valid and not expired

#### "User interaction is not allowed"

**Problem**: Keychain access denied during automated build.

**Solution**:
```bash
# Unlock keychain
security unlock-keychain -p "your-password" ~/Library/Keychains/login.keychain-db

# Or allow codesign to access keychain
security set-key-partition-list -S apple-tool:,apple: -s -k "your-password" ~/Library/Keychains/login.keychain-db
```

### Notarization Issues

#### "Invalid credentials"

**Problem**: Apple ID or password incorrect.

**Solution**:
1. Verify Apple ID: `echo $APPLE_ID`
2. Verify you're using an **app-specific password**, not your Apple ID password
3. Regenerate app-specific password if needed

#### "Notarization failed"

**Problem**: App doesn't meet notarization requirements.

**Solution**:
1. Check notarization log:
   ```bash
   xcrun notarytool log <submission-id> --apple-id $APPLE_ID --team-id $APPLE_TEAM_ID --password $APPLE_ID_PASSWORD
   ```
2. Common issues:
   - Missing hardened runtime
   - Missing entitlements
   - Unsigned binaries
   - Invalid bundle structure

#### "Notarization timeout"

**Problem**: Notarization taking too long.

**Solution**:
- Notarization can take 5-30 minutes
- Check status manually:
  ```bash
  xcrun notarytool history --apple-id $APPLE_ID --team-id $APPLE_TEAM_ID --password $APPLE_ID_PASSWORD
  ```

### Build Issues

#### "PyInstaller not found"

**Problem**: PyInstaller not installed.

**Solution**:
```bash
pip3 install pyinstaller
```

#### "Frontend build failed"

**Problem**: Frontend dependencies or build errors.

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
cd ..
```

#### "Backend build failed"

**Problem**: Python dependencies or PyInstaller errors.

**Solution**:
```bash
cd backend
pip3 install -r requirements.txt --upgrade
pyinstaller main-macos.spec --clean --noconfirm
cd ..
```

### Runtime Issues

#### "App is damaged and can't be opened"

**Problem**: Gatekeeper blocking unsigned or unnotarized app.

**Solution**:
1. For development: Remove quarantine attribute
   ```bash
   xattr -cr "/Applications/Solar Calculator Pro.app"
   ```
2. For distribution: Ensure app is signed and notarized

#### "App can't be opened because Apple cannot check it for malicious software"

**Problem**: App not notarized.

**Solution**:
1. Right-click the app and select "Open"
2. Click "Open" in the dialog
3. Or: System Preferences > Security & Privacy > Click "Open Anyway"

## Distribution

### Direct Download

1. Upload DMG to your website or file hosting
2. Provide download link to users
3. Users download and install normally

### GitHub Releases

1. Create a new release on GitHub
2. Upload DMG and ZIP files as release assets
3. electron-updater will automatically detect new versions

### Mac App Store

For Mac App Store distribution:
1. Create a "Mac App Distribution" certificate (not "Developer ID")
2. Create an App Store provisioning profile
3. Update `package.json` to use `mas` target
4. Build with: `npm run electron:build:mac -- --mac mas`
5. Submit to App Store Connect

### Auto-Update

The app includes electron-updater for automatic updates:

1. Configure update server in `electron/updater.js`
2. Upload new releases to GitHub or your server
3. App will check for updates on launch
4. Users will be notified of available updates

## Best Practices

### Security

1. **Never commit credentials**: Keep signing identities and passwords in environment variables
2. **Use app-specific passwords**: Never use your main Apple ID password
3. **Rotate passwords**: Change app-specific passwords periodically
4. **Secure CI/CD**: Use encrypted secrets in CI/CD pipelines

### Testing

1. **Test on clean system**: Test installation on a Mac without Xcode
2. **Test both architectures**: Test on Intel and Apple Silicon Macs
3. **Test Gatekeeper**: Test with a fresh download (not from build directory)
4. **Test updates**: Test the auto-update mechanism

### Versioning

1. **Semantic versioning**: Use MAJOR.MINOR.PATCH format
2. **Update package.json**: Increment version before building
3. **Tag releases**: Create Git tags for each release
4. **Changelog**: Maintain a changelog for users

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build macOS

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        env:
          MACOS_SIGNING_IDENTITY: ${{ secrets.MACOS_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_ID_PASSWORD: ${{ secrets.APPLE_ID_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: node build/build-macos.js
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: macos-build
          path: release/*.dmg
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: release/*.dmg
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Additional Resources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [electron-builder macOS Documentation](https://www.electron.build/configuration/mac)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-org/solar-calculator-pro/issues
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
