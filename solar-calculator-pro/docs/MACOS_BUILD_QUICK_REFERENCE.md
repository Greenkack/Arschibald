# macOS Build Quick Reference

Quick commands and checklists for building Solar Calculator Pro on macOS.

## Prerequisites Checklist

- [ ] macOS 10.15 or later
- [ ] Xcode Command Line Tools installed
- [ ] Node.js 18+ installed
- [ ] Python 3.10+ installed
- [ ] npm 9+ installed
- [ ] PyInstaller installed
- [ ] Apple Developer account (for signing/notarization)

## Quick Setup

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install dependencies
npm install
cd frontend && npm install && cd ..
cd backend && pip3 install -r requirements.txt && cd ..

# Install PyInstaller
pip3 install pyinstaller
```

## Environment Variables

### Required for Code Signing

```bash
export MACOS_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
```

### Required for Notarization

```bash
export APPLE_ID="your-apple-id@example.com"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # App-specific password
export APPLE_TEAM_ID="ABCDE12345"
```

### Add to Shell Profile

```bash
# Add to ~/.zshrc or ~/.bash_profile
echo 'export MACOS_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"' >> ~/.zshrc
echo 'export APPLE_ID="your-apple-id@example.com"' >> ~/.zshrc
echo 'export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"' >> ~/.zshrc
echo 'export APPLE_TEAM_ID="ABCDE12345"' >> ~/.zshrc
source ~/.zshrc
```

## Build Commands

### Standard Build

```bash
# Build for current architecture
npm run electron:build:mac

# Or use custom build script
node build/build-macos.js
```

### Architecture-Specific Builds

```bash
# Intel (x64)
npm run electron:build:mac -- --x64

# Apple Silicon (arm64)
npm run electron:build:mac -- --arm64

# Universal (both)
npm run electron:build:mac -- --universal
```

### Development Build (No Signing)

```bash
# Unset signing variables temporarily
unset MACOS_SIGNING_IDENTITY
unset APPLE_ID
unset APPLE_ID_PASSWORD
unset APPLE_TEAM_ID

# Build
npm run electron:build:mac
```

## Verification Commands

### Check Signing Identity

```bash
security find-identity -v -p codesigning
```

### Verify Code Signature

```bash
# Verify .app bundle
codesign -vvv --deep --strict "release/mac/Solar Calculator Pro.app"

# Verify DMG
codesign -vvv "release/Solar Calculator Pro-1.0.0-x64.dmg"
```

### Check Notarization Status

```bash
# Check if app is notarized
spctl -a -vvv -t install "release/Solar Calculator Pro-1.0.0-x64.dmg"

# View notarization history
xcrun notarytool history --apple-id $APPLE_ID --team-id $APPLE_TEAM_ID --password $APPLE_ID_PASSWORD
```

### Check Entitlements

```bash
codesign -d --entitlements - "release/mac/Solar Calculator Pro.app"
```

## Common Issues & Quick Fixes

### "No identity found"

```bash
# Check if certificate is installed
security find-identity -v -p codesigning

# If not found, install certificate from Apple Developer portal
```

### "User interaction is not allowed"

```bash
# Unlock keychain
security unlock-keychain -p "your-password" ~/Library/Keychains/login.keychain-db

# Allow codesign access
security set-key-partition-list -S apple-tool:,apple: -s -k "your-password" ~/Library/Keychains/login.keychain-db
```

### "App is damaged"

```bash
# Remove quarantine attribute (development only)
xattr -cr "/Applications/Solar Calculator Pro.app"
```

### "Notarization failed"

```bash
# Get notarization log
xcrun notarytool log <submission-id> --apple-id $APPLE_ID --team-id $APPLE_TEAM_ID --password $APPLE_ID_PASSWORD
```

### Clean Build

```bash
# Clean all build artifacts
rm -rf release/
rm -rf frontend/dist/
rm -rf backend/dist/
rm -rf backend/build/

# Rebuild
npm run electron:build:mac
```

## File Locations

### Build Artifacts

```
release/
├── Solar Calculator Pro-1.0.0-x64.dmg          # DMG installer (Intel)
├── Solar Calculator Pro-1.0.0-arm64.dmg        # DMG installer (Apple Silicon)
├── Solar Calculator Pro-1.0.0-x64-mac.zip      # ZIP archive (Intel)
├── Solar Calculator Pro-1.0.0-arm64-mac.zip    # ZIP archive (Apple Silicon)
├── build-report-macos.json                      # Build report
└── mac/
    └── Solar Calculator Pro.app                 # App bundle
```

### Configuration Files

```
build/
├── build-macos.js                    # Build script
├── entitlements.mac.plist            # Main entitlements
├── entitlements.mac.inherit.plist    # Inherited entitlements
└── notarize.js                       # Notarization script
```

## Testing Checklist

- [ ] Build completes without errors
- [ ] DMG mounts correctly
- [ ] App installs to Applications
- [ ] App launches without errors
- [ ] Backend starts automatically
- [ ] Frontend loads correctly
- [ ] All features work as expected
- [ ] No Gatekeeper warnings (if signed)
- [ ] Auto-update works (if configured)

## Distribution Checklist

- [ ] Version number updated in package.json
- [ ] Changelog updated
- [ ] Git tag created
- [ ] Build is signed
- [ ] Build is notarized
- [ ] DMG tested on clean system
- [ ] Release notes prepared
- [ ] GitHub release created
- [ ] Download links updated

## Quick Reference: Apple Developer Portal

### Certificates

1. Go to: https://developer.apple.com/account/resources/certificates
2. Create: "Developer ID Application" certificate
3. Download and install in Keychain Access

### App-Specific Password

1. Go to: https://appleid.apple.com
2. Security > App-Specific Passwords
3. Generate new password
4. Copy and save securely

### Team ID

1. Go to: https://developer.apple.com/account
2. Membership section
3. Copy Team ID (10 characters)

## Useful Commands

### Check macOS Version

```bash
sw_vers -productVersion
```

### Check Architecture

```bash
uname -m
# x86_64 = Intel
# arm64 = Apple Silicon
```

### Check App Info

```bash
# Get app version
defaults read "release/mac/Solar Calculator Pro.app/Contents/Info.plist" CFBundleShortVersionString

# Get bundle identifier
defaults read "release/mac/Solar Calculator Pro.app/Contents/Info.plist" CFBundleIdentifier
```

### Monitor Build

```bash
# Watch build directory
watch -n 1 'ls -lh release/'

# Monitor notarization
watch -n 10 'xcrun notarytool history --apple-id $APPLE_ID --team-id $APPLE_TEAM_ID --password $APPLE_ID_PASSWORD | head -n 5'
```

## Performance Tips

### Faster Builds

1. Use `--x64` or `--arm64` instead of universal
2. Skip notarization for development builds
3. Use local caching for dependencies
4. Build on SSD (not network drive)

### Smaller DMG

1. Optimize images in assets/
2. Remove unused dependencies
3. Enable compression in DMG settings
4. Use `UDZO` format (default)

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate app-specific passwords** regularly
4. **Use separate certificates** for development and distribution
5. **Enable 2FA** on Apple ID
6. **Secure CI/CD secrets** with encryption

## Support Resources

- **Full Guide**: `docs/MACOS_BUILD_GUIDE.md`
- **Package Config**: `package.json` (build section)
- **Build Script**: `build/build-macos.js`
- **Entitlements**: `build/entitlements.mac.plist`
- **Notarization**: `build/notarize.js`

## Emergency Contacts

- Apple Developer Support: https://developer.apple.com/support/
- electron-builder Issues: https://github.com/electron-userland/electron-builder/issues
- Project Issues: https://github.com/your-org/solar-calculator-pro/issues
