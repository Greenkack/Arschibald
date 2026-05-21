# Update Testing Environment

This directory contains comprehensive testing tools for the auto-update system.

## Overview

The update testing environment allows you to:
- Test update downloads
- Verify update installation
- Test rollback functionality
- Validate update flows
- Test different update scenarios

## Directory Structure

```
tests/update-testing/
├── README.md                    # This file
├── test-environment.js          # Test environment setup
├── test-update-flow.js          # Update flow tests
├── test-rollback.js             # Rollback tests
├── mock-update-server.js        # Mock update server
├── version-builder.js           # Build multiple versions
├── test-scenarios.js            # Test scenarios
└── test-data/                   # Test data and fixtures
    ├── versions/                # Different app versions
    ├── manifests/               # Update manifests
    └── releases/                # Release files
```

## Quick Start

### 1. Setup Test Environment

```bash
cd solar-calculator-pro/tests/update-testing
npm install
node test-environment.js setup
```

### 2. Build Test Versions

```bash
# Build version 1.0.0
node version-builder.js --version 1.0.0

# Build version 1.0.1
node version-builder.js --version 1.0.1

# Build version 1.0.2
node version-builder.js --version 1.0.2
```

### 3. Start Mock Update Server

```bash
node mock-update-server.js --port 3000
```

### 4. Run Tests

```bash
# Test update download
node test-update-flow.js --test download

# Test update installation
node test-update-flow.js --test install

# Test rollback
node test-rollback.js

# Run all tests
npm test
```

## Test Scenarios

### Scenario 1: Basic Update Flow
- Install v1.0.0
- Check for updates
- Download v1.0.1
- Install update
- Verify v1.0.1 is running

### Scenario 2: Skip Version
- Install v1.0.0
- Check for updates (v1.0.1 available)
- Skip v1.0.1
- Check for updates again
- Verify v1.0.1 is skipped
- Check for v1.0.2
- Download and install v1.0.2

### Scenario 3: Cancel Download
- Install v1.0.0
- Start downloading v1.0.1
- Cancel download
- Verify download cancelled
- Restart download
- Complete installation

### Scenario 4: Update Failure
- Install v1.0.0
- Simulate network failure during download
- Verify error handling
- Retry download
- Complete installation

### Scenario 5: Rollback
- Install v1.0.1
- Detect critical bug
- Rollback to v1.0.0
- Verify v1.0.0 is running
- Verify data integrity

### Scenario 6: Channel Switching
- Install v1.0.0 (stable)
- Switch to beta channel
- Check for updates
- Download beta version
- Install and verify

### Scenario 7: Auto-Download
- Enable auto-download
- Check for updates
- Verify automatic download
- Verify installation prompt

### Scenario 8: Auto-Install on Quit
- Enable auto-install on quit
- Download update
- Quit application
- Verify update installs
- Verify app restarts

## Testing Checklist

### Pre-Testing
- [ ] Build multiple test versions
- [ ] Setup mock update server
- [ ] Configure test environment
- [ ] Backup test data

### Update Download Tests
- [ ] Download starts correctly
- [ ] Progress updates work
- [ ] Download completes successfully
- [ ] Downloaded file is valid
- [ ] SHA512 verification works
- [ ] Cancel download works
- [ ] Resume download works (if supported)
- [ ] Network error handling works

### Update Installation Tests
- [ ] Installation starts correctly
- [ ] App closes gracefully
- [ ] Update installs successfully
- [ ] App restarts with new version
- [ ] User data preserved
- [ ] Settings preserved
- [ ] Database migrated correctly
- [ ] No data loss

### Rollback Tests
- [ ] Rollback detection works
- [ ] Previous version restored
- [ ] Data integrity maintained
- [ ] Settings restored
- [ ] App functions correctly
- [ ] Rollback logged correctly

### UI Tests
- [ ] Update notification displays
- [ ] Progress bar updates
- [ ] Ready dialog shows
- [ ] Preferences save correctly
- [ ] Release notes display
- [ ] All buttons work
- [ ] Dark mode works
- [ ] Responsive design works

### Edge Cases
- [ ] No internet connection
- [ ] Slow internet connection
- [ ] Server unavailable
- [ ] Corrupted download
- [ ] Insufficient disk space
- [ ] Permission errors
- [ ] Multiple update checks
- [ ] Rapid version changes

### Security Tests
- [ ] SHA512 verification
- [ ] Code signature verification
- [ ] HTTPS enforcement
- [ ] Man-in-the-middle protection
- [ ] Tampered file detection

### Performance Tests
- [ ] Update check speed
- [ ] Download speed
- [ ] Installation speed
- [ ] Memory usage
- [ ] CPU usage
- [ ] Disk usage

## Test Data

### Version Differences

**v1.0.0 → v1.0.1**
- Bug fixes
- Minor UI improvements
- Small file size (~5MB)

**v1.0.1 → v1.0.2**
- New features
- Database schema changes
- Medium file size (~15MB)

**v1.0.2 → v2.0.0**
- Major version upgrade
- Breaking changes
- Large file size (~50MB)

## Troubleshooting

### Test Fails to Start
- Check Node.js version (>=16)
- Install dependencies: `npm install`
- Check port availability
- Verify file permissions

### Update Download Fails
- Check mock server is running
- Verify network connectivity
- Check firewall settings
- Verify manifest files

### Installation Fails
- Check disk space
- Verify file permissions
- Check antivirus settings
- Review error logs

### Rollback Fails
- Verify backup exists
- Check file integrity
- Review rollback logs
- Verify database state

## Continuous Integration

### GitHub Actions

```yaml
name: Update Tests

on: [push, pull_request]

jobs:
  test-updates:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build test versions
        run: |
          node tests/update-testing/version-builder.js --version 1.0.0
          node tests/update-testing/version-builder.js --version 1.0.1
      
      - name: Run update tests
        run: npm run test:updates
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.os }}
          path: tests/update-testing/results/
```

## Best Practices

1. **Always test on clean installations**
2. **Test all platforms (Windows, macOS, Linux)**
3. **Test with different network conditions**
4. **Verify data integrity after updates**
5. **Test rollback scenarios**
6. **Monitor resource usage**
7. **Check logs for errors**
8. **Test with real users (beta testing)**

## Resources

- [electron-updater Documentation](https://www.electron.build/auto-update)
- [Testing Electron Apps](https://www.electronjs.org/docs/latest/tutorial/automated-testing)
- [Update Testing Best Practices](https://www.electron.build/auto-update#testing)

## Support

For issues or questions:
- Check the troubleshooting section
- Review test logs
- Check GitHub issues
- Contact development team
