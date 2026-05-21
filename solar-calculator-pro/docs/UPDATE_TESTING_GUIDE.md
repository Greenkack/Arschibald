# Update Testing Guide

Complete guide for testing the auto-update system in Solar Calculator Pro.

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Running Tests](#running-tests)
4. [Test Scenarios](#test-scenarios)
5. [Manual Testing](#manual-testing)
6. [Automated Testing](#automated-testing)
7. [Rollback Testing](#rollback-testing)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)
10. [Troubleshooting](#troubleshooting)

## Overview

The update testing system provides comprehensive tools for testing all aspects of the auto-update functionality:

- **Update Flow Testing**: Test the complete update process
- **Rollback Testing**: Verify rollback functionality
- **Mock Server**: Local update server for testing
- **Version Builder**: Build multiple test versions
- **Test Scenarios**: Pre-defined test cases

## Test Environment Setup

### Prerequisites

- Node.js 16+ installed
- npm or yarn
- Electron development environment
- At least 2GB free disk space

### Initial Setup

```bash
# Navigate to test directory
cd solar-calculator-pro/tests/update-testing

# Install dependencies
npm install

# Setup test environment
npm run setup
```

This will:
- Create necessary directories
- Generate test configuration
- Create sample release notes
- Setup test scenarios

### Verify Setup

```bash
npm run verify
```

Expected output:
```
✓ Directories exist
✓ Configuration files exist
✓ Test data exists
✅ Test environment is ready!
```

## Running Tests

### Quick Start

```bash
# Run all tests
npm test

# Run specific test suite
npm run test:flow      # Update flow tests
npm run test:rollback  # Rollback tests
```

### With Mock Server

```bash
# Terminal 1: Start mock server
npm run server

# Terminal 2: Run tests
npm test
```

### Custom Configuration

```bash
# Use custom port
npm run server:custom

# Run tests with custom config
node test-update-flow.js --server http://localhost:3001
```

## Test Scenarios

### Scenario 1: Basic Update Flow

**Objective**: Test standard update from v1.0.0 to v1.0.1

**Steps**:
1. Install v1.0.0
2. Check for updates
3. Download v1.0.1
4. Install update
5. Verify v1.0.1 is running

**Expected Result**: App successfully updated to v1.0.1

**Test Command**:
```bash
node test-update-flow.js --scenario basic-update
```

### Scenario 2: Skip Version

**Objective**: Test version skipping functionality

**Steps**:
1. Install v1.0.0
2. Check for updates (v1.0.1 available)
3. Skip v1.0.1
4. Check for updates again
5. Verify v1.0.1 is skipped
6. Check for v1.0.2
7. Download and install v1.0.2

**Expected Result**: App updated to v1.0.2, skipping v1.0.1

**Test Command**:
```bash
node test-update-flow.js --scenario skip-version
```

### Scenario 3: Cancel Download

**Objective**: Test download cancellation

**Steps**:
1. Install v1.0.0
2. Start downloading v1.0.1
3. Cancel download
4. Verify download cancelled
5. Restart download
6. Complete installation

**Expected Result**: Download can be cancelled and restarted

**Test Command**:
```bash
node test-update-flow.js --scenario cancel-download
```

### Scenario 4: Network Failure

**Objective**: Test update with network failure

**Steps**:
1. Install v1.0.0
2. Start downloading v1.0.1
3. Simulate network failure
4. Verify error handling
5. Restore network
6. Retry download
7. Complete installation

**Expected Result**: Update recovers from network failure

**Test Command**:
```bash
node test-update-flow.js --scenario network-failure
```

### Scenario 5: Rollback

**Objective**: Test rolling back to previous version

**Steps**:
1. Install v1.0.1
2. Detect critical bug
3. Rollback to v1.0.0
4. Verify v1.0.0 is running
5. Verify data integrity

**Expected Result**: Successfully rolled back to v1.0.0

**Test Command**:
```bash
node test-rollback.js --scenario rollback
```

### Scenario 6: Channel Switching

**Objective**: Test switching update channels

**Steps**:
1. Install v1.0.0 (stable)
2. Switch to beta channel
3. Check for updates
4. Download beta version
5. Install and verify

**Expected Result**: Successfully switched to beta channel

**Test Command**:
```bash
node test-update-flow.js --scenario channel-switch
```

### Scenario 7: Auto-Download

**Objective**: Test automatic download

**Steps**:
1. Enable auto-download
2. Check for updates
3. Verify automatic download
4. Verify installation prompt

**Expected Result**: Update downloads automatically

**Test Command**:
```bash
node test-update-flow.js --scenario auto-download
```

### Scenario 8: Auto-Install on Quit

**Objective**: Test automatic installation on quit

**Steps**:
1. Enable auto-install on quit
2. Download update
3. Quit application
4. Verify update installs
5. Verify app restarts

**Expected Result**: Update installs automatically on quit

**Test Command**:
```bash
node test-update-flow.js --scenario auto-install
```

### Scenario 9: Major Version Update

**Objective**: Test major version update with breaking changes

**Steps**:
1. Install v1.0.2
2. Check for updates (v2.0.0 available)
3. Review breaking changes
4. Download v2.0.0
5. Install update
6. Verify database migration
7. Verify app functions correctly

**Expected Result**: Successfully updated to v2.0.0 with data migration

**Test Command**:
```bash
node test-update-flow.js --scenario major-version
```

### Scenario 10: Corrupted Download

**Objective**: Test handling of corrupted download

**Steps**:
1. Install v1.0.0
2. Start downloading v1.0.1
3. Corrupt download file
4. Verify SHA512 check fails
5. Verify error message
6. Retry download
7. Complete installation

**Expected Result**: Corrupted download detected and handled

**Test Command**:
```bash
node test-update-flow.js --scenario corrupted-download
```

## Manual Testing

### Testing Checklist

#### Pre-Testing
- [ ] Build multiple test versions
- [ ] Setup mock update server
- [ ] Configure test environment
- [ ] Backup test data

#### Update Download Tests
- [ ] Download starts correctly
- [ ] Progress updates work
- [ ] Download completes successfully
- [ ] Downloaded file is valid
- [ ] SHA512 verification works
- [ ] Cancel download works
- [ ] Resume download works (if supported)
- [ ] Network error handling works

#### Update Installation Tests
- [ ] Installation starts correctly
- [ ] App closes gracefully
- [ ] Update installs successfully
- [ ] App restarts with new version
- [ ] User data preserved
- [ ] Settings preserved
- [ ] Database migrated correctly
- [ ] No data loss

#### Rollback Tests
- [ ] Rollback detection works
- [ ] Previous version restored
- [ ] Data integrity maintained
- [ ] Settings restored
- [ ] App functions correctly
- [ ] Rollback logged correctly

#### UI Tests
- [ ] Update notification displays
- [ ] Progress bar updates
- [ ] Ready dialog shows
- [ ] Preferences save correctly
- [ ] Release notes display
- [ ] All buttons work
- [ ] Dark mode works
- [ ] Responsive design works

### Manual Test Procedure

1. **Install Base Version**
   ```bash
   # Install v1.0.0
   npm run electron:build
   # Install the generated installer
   ```

2. **Start Mock Server**
   ```bash
   npm run server
   ```

3. **Configure Update Server**
   - Open app settings
   - Set update server URL to `http://localhost:3000`
   - Enable update checking

4. **Test Update Check**
   - Click "Check for Updates" in Help menu
   - Verify notification appears
   - Check release notes display

5. **Test Download**
   - Click "Download" button
   - Verify progress bar updates
   - Check download speed display
   - Verify cancel button works

6. **Test Installation**
   - Wait for download to complete
   - Click "Install Now" or "Install on Quit"
   - Verify app closes
   - Verify update installs
   - Verify app restarts

7. **Verify Update**
   - Check version in About dialog
   - Verify all features work
   - Check data integrity
   - Verify settings preserved

## Automated Testing

### Continuous Integration

#### GitHub Actions Example

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
        run: |
          cd solar-calculator-pro
          npm install
      
      - name: Setup test environment
        run: |
          cd solar-calculator-pro/tests/update-testing
          npm install
          npm run setup
      
      - name: Run update tests
        run: |
          cd solar-calculator-pro/tests/update-testing
          npm test
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.os }}
          path: solar-calculator-pro/tests/update-testing/results/
```

### Test Automation Script

```bash
#!/bin/bash

# Automated test script
echo "Starting automated update tests..."

# Setup
cd solar-calculator-pro/tests/update-testing
npm install
npm run setup

# Start mock server in background
npm run server &
SERVER_PID=$!
sleep 2

# Run tests
npm test

# Capture exit code
TEST_EXIT_CODE=$?

# Stop server
kill $SERVER_PID

# Exit with test result
exit $TEST_EXIT_CODE
```

## Rollback Testing

### Rollback Test Procedure

1. **Create Backup**
   ```bash
   node test-rollback.js --test create-backup
   ```

2. **Simulate Update**
   ```bash
   # Install newer version
   # Simulate critical bug
   ```

3. **Trigger Rollback**
   ```bash
   node test-rollback.js --test rollback
   ```

4. **Verify Rollback**
   ```bash
   node test-rollback.js --test verify
   ```

### Rollback Scenarios

#### Scenario 1: Critical Bug Detection
- Install v1.0.1
- Detect crash on startup
- Automatic rollback to v1.0.0
- Verify app works

#### Scenario 2: Database Corruption
- Install v1.0.2
- Detect database corruption
- Rollback to v1.0.1
- Verify data integrity

#### Scenario 3: Manual Rollback
- Install v2.0.0
- User requests rollback
- Manual rollback to v1.0.2
- Verify functionality

## Performance Testing

### Metrics to Measure

1. **Update Check Time**
   - Target: < 2 seconds
   - Measure: Time from check to result

2. **Download Speed**
   - Target: > 1 MB/s on good connection
   - Measure: Bytes per second

3. **Installation Time**
   - Target: < 30 seconds
   - Measure: Time from start to completion

4. **Memory Usage**
   - Target: < 200MB during update
   - Measure: Peak memory usage

5. **CPU Usage**
   - Target: < 50% during update
   - Measure: Average CPU usage

### Performance Test Script

```javascript
const { performance } = require('perf_hooks');

async function measureUpdatePerformance() {
  const metrics = {};

  // Measure update check
  const checkStart = performance.now();
  await checkForUpdates();
  metrics.checkTime = performance.now() - checkStart;

  // Measure download
  const downloadStart = performance.now();
  await downloadUpdate();
  metrics.downloadTime = performance.now() - downloadStart;

  // Measure installation
  const installStart = performance.now();
  await installUpdate();
  metrics.installTime = performance.now() - installStart;

  console.log('Performance Metrics:', metrics);
  return metrics;
}
```

## Security Testing

### Security Checklist

- [ ] SHA512 hash verification
- [ ] Code signature verification
- [ ] HTTPS enforcement
- [ ] Man-in-the-middle protection
- [ ] Tampered file detection
- [ ] Secure storage of credentials
- [ ] No sensitive data in logs

### Security Test Procedure

1. **Test Hash Verification**
   ```bash
   # Modify downloaded file
   # Verify installation fails
   # Check error message
   ```

2. **Test HTTPS Enforcement**
   ```bash
   # Try HTTP update server
   # Verify connection rejected
   ```

3. **Test Signature Verification**
   ```bash
   # Use unsigned installer
   # Verify installation blocked
   ```

## Troubleshooting

### Common Issues

#### Test Environment Setup Fails

**Problem**: Setup script fails with errors

**Solutions**:
- Check Node.js version (>=16)
- Install dependencies: `npm install`
- Check file permissions
- Verify disk space

#### Mock Server Won't Start

**Problem**: Port already in use

**Solutions**:
- Use different port: `npm run server:custom`
- Kill process using port: `lsof -ti:3000 | xargs kill`
- Check firewall settings

#### Tests Fail to Connect

**Problem**: Cannot connect to mock server

**Solutions**:
- Verify server is running
- Check URL in test config
- Verify firewall allows connections
- Check network connectivity

#### Update Download Fails

**Problem**: Download fails or times out

**Solutions**:
- Check mock server logs
- Verify manifest file exists
- Check file permissions
- Increase timeout in config

#### Installation Fails

**Problem**: Update won't install

**Solutions**:
- Check disk space
- Verify file permissions
- Check antivirus settings
- Review error logs

#### Rollback Fails

**Problem**: Cannot rollback to previous version

**Solutions**:
- Verify backup exists
- Check backup integrity
- Review rollback logs
- Verify database state

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export DEBUG=update-testing:*

# Run tests
npm test
```

### Log Files

Test logs are saved to:
- `results/test.log` - General test log
- `results/update-flow-results.json` - Update flow test results
- `results/rollback-results.json` - Rollback test results

## Best Practices

1. **Always test on clean installations**
2. **Test all platforms (Windows, macOS, Linux)**
3. **Test with different network conditions**
4. **Verify data integrity after updates**
5. **Test rollback scenarios**
6. **Monitor resource usage**
7. **Check logs for errors**
8. **Test with real users (beta testing)**
9. **Document all test results**
10. **Automate repetitive tests**

## Resources

- [electron-updater Documentation](https://www.electron.build/auto-update)
- [Testing Electron Apps](https://www.electronjs.org/docs/latest/tutorial/automated-testing)
- [Update Testing Best Practices](https://www.electron.build/auto-update#testing)
- [Auto-Update Guide](./AUTO_UPDATE_GUIDE.md)
- [Update UI Guide](./UPDATE_UI_GUIDE.md)

## Support

For issues or questions:
- Check the troubleshooting section
- Review test logs
- Check GitHub issues
- Contact development team

## Conclusion

This comprehensive testing guide ensures that the auto-update system works reliably across all platforms and scenarios. Regular testing helps catch issues early and ensures a smooth update experience for users.
