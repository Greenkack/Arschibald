# Update Testing Quick Reference

Quick reference for testing the auto-update system.

## Quick Start

```bash
# Setup
cd solar-calculator-pro/tests/update-testing
npm install
npm run setup

# Start mock server
npm run server

# Run tests (in another terminal)
npm test
```

## Commands

### Setup Commands

```bash
npm run setup      # Setup test environment
npm run cleanup    # Clean up test data
npm run verify     # Verify environment
```

### Server Commands

```bash
npm run server              # Start on port 3000
npm run server:custom       # Start on port 3001
node mock-update-server.js --port 3000 --dir ./releases
```

### Test Commands

```bash
npm test                    # Run all tests
npm run test:flow           # Update flow tests
npm run test:rollback       # Rollback tests
```

## Test Scenarios

| Scenario | Command | Duration |
|----------|---------|----------|
| Basic Update | `node test-update-flow.js --scenario basic-update` | ~2s |
| Skip Version | `node test-update-flow.js --scenario skip-version` | ~3s |
| Cancel Download | `node test-update-flow.js --scenario cancel-download` | ~2s |
| Network Failure | `node test-update-flow.js --scenario network-failure` | ~3s |
| Rollback | `node test-rollback.js --scenario rollback` | ~4s |
| Channel Switch | `node test-update-flow.js --scenario channel-switch` | ~2s |
| Auto-Download | `node test-update-flow.js --scenario auto-download` | ~2s |
| Auto-Install | `node test-update-flow.js --scenario auto-install` | ~3s |
| Major Version | `node test-update-flow.js --scenario major-version` | ~4s |
| Corrupted | `node test-update-flow.js --scenario corrupted-download` | ~2s |

## Mock Server Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /latest.yml` | Windows update manifest |
| `GET /latest-mac.yml` | macOS update manifest |
| `GET /latest-linux.yml` | Linux update manifest |
| `GET /beta.yml` | Beta channel manifest |
| `GET /alpha.yml` | Alpha channel manifest |
| `GET /release-notes/:version` | Release notes |
| `GET /download/:filename` | Download installer |
| `GET /info` | Server information |
| `GET /health` | Health check |

## Testing Checklist

### Quick Test (5 minutes)

- [ ] Setup environment
- [ ] Start mock server
- [ ] Run basic update test
- [ ] Verify results

### Standard Test (15 minutes)

- [ ] Setup environment
- [ ] Start mock server
- [ ] Run all update flow tests
- [ ] Run rollback tests
- [ ] Review test results
- [ ] Check logs

### Comprehensive Test (30 minutes)

- [ ] Setup environment
- [ ] Start mock server
- [ ] Run all automated tests
- [ ] Perform manual testing
- [ ] Test on multiple platforms
- [ ] Verify data integrity
- [ ] Check performance
- [ ] Review all logs

## Common Issues

### Port Already in Use

```bash
# Use different port
npm run server:custom

# Or kill process
lsof -ti:3000 | xargs kill  # macOS/Linux
netstat -ano | findstr :3000  # Windows
```

### Tests Fail to Connect

```bash
# Check server is running
curl http://localhost:3000/health

# Check firewall
# Allow connections on port 3000
```

### Environment Setup Fails

```bash
# Check Node.js version
node --version  # Should be >=16

# Reinstall dependencies
rm -rf node_modules
npm install
```

## File Locations

```
tests/update-testing/
├── test-config.json          # Test configuration
├── .env.test                 # Environment variables
├── test-scenarios.json       # Test scenarios
├── test-data/
│   ├── versions/             # Test versions
│   ├── manifests/            # Update manifests
│   ├── releases/             # Release files
│   └── backups/              # Backup files
└── results/
    ├── test.log              # Test log
    ├── update-flow-results.json
    └── rollback-results.json
```

## Test Results

### Success Output

```
✅ PASSED (245ms)
Total Tests: 10
✅ Passed: 10
❌ Failed: 0
```

### Failure Output

```
❌ FAILED: Download failed
Total Tests: 10
✅ Passed: 9
❌ Failed: 1

❌ Failed Tests:
  - Download Update: Network timeout
```

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Update Check | < 2s | < 5s |
| Download Speed | > 1 MB/s | > 500 KB/s |
| Installation | < 30s | < 60s |
| Memory Usage | < 200MB | < 500MB |
| CPU Usage | < 50% | < 80% |

## Debug Mode

```bash
# Enable debug logging
export DEBUG=update-testing:*

# Run tests with debug
npm test

# View logs
tail -f results/test.log
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run update tests
  run: |
    cd solar-calculator-pro/tests/update-testing
    npm install
    npm run setup
    npm test
```

### Jenkins

```groovy
stage('Update Tests') {
  steps {
    dir('solar-calculator-pro/tests/update-testing') {
      sh 'npm install'
      sh 'npm run setup'
      sh 'npm test'
    }
  }
}
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Use `--port 3001` |
| Tests timeout | Increase timeout in config |
| Server won't start | Check Node.js version |
| Download fails | Check mock server logs |
| Installation fails | Check disk space |
| Rollback fails | Verify backup exists |

## Resources

- Full Guide: `docs/UPDATE_TESTING_GUIDE.md`
- Test Overview: `tests/update-testing/README.md`
- Auto-Update Guide: `docs/AUTO_UPDATE_GUIDE.md`
- Update UI Guide: `docs/UPDATE_UI_GUIDE.md`

## Support

For issues:
1. Check troubleshooting section
2. Review test logs
3. Check GitHub issues
4. Contact development team

## Version History

- v1.0.0 - Initial release
- Complete test suite
- Mock server
- Documentation

---

**Last Updated**: 2024
**Status**: Production Ready ✅
