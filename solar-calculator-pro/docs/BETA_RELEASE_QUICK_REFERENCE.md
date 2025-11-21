# Beta Release Quick Reference

## Quick Commands

```bash
# Prepare for beta release
npm run prepare:beta

# Build beta version
npm run build:beta

# Build for specific platform
npm run build:beta -- win
npm run build:beta -- mac
npm run build:beta -- linux

# Generate release notes
npm run release-notes -- --version 1.0.0-beta.1 --beta

# Test beta build
npm run test:beta
```

## Beta Version Format

```
X.Y.Z-beta.N+HASH
```

- `X.Y.Z`: Semantic version
- `N`: Build number (git commit count)
- `HASH`: Git commit hash

Example: `1.0.0-beta.123+a1b2c3d`

## Beta Identification

### Visual Indicators
- "BETA" watermark (top-right)
- Beta badge in title bar
- Beta version in about dialog

### Programmatic Check
```javascript
// Electron main process
const isBeta = require('./build/beta-config').isBeta;

// Frontend
const isBeta = process.env.REACT_APP_BUILD_TYPE === 'beta';
```

## Crash Reporting

### Sentry Configuration
```javascript
// Environment variable
SENTRY_DSN_BETA=https://...@sentry.io/...

// Check status
const crashReporter = require('./electron/crash-reporter');
console.log(crashReporter.initialized);
```

### Manual Crash Report
```javascript
crashReporter.captureException(error, {
  tags: { feature: 'solar-calculator' },
  extra: { projectId: 123 },
  level: 'error',
});
```

## Feedback System

### Widget Position
```javascript
<FeedbackWidget
  position="bottom-right"
  showOnStartup={false}
  reminderInterval={604800000} // 7 days
/>
```

### Feedback Categories
- `bug`: Something is broken
- `feature`: New functionality request
- `improvement`: Enhancement
- `performance`: Speed/resource issues
- `ui-ux`: Interface issues

### Feedback Priorities
- `critical`: App crashes or data loss
- `high`: Major functionality broken
- `medium`: Minor issues
- `low`: Cosmetic issues

## Beta Tester Management

### Create Beta Tester
```bash
curl -X POST http://localhost:8000/api/v1/beta/testers \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tester@example.com",
    "name": "John Doe",
    "platform": "windows"
  }'
```

### Generate Invitation
```bash
curl -X POST http://localhost:8000/api/v1/beta/testers/1/invitations \
  -H "Content-Type: application/json" \
  -d '{
    "valid_days": 30,
    "max_uses": 1
  }'
```

### Validate Invitation
```bash
curl http://localhost:8000/api/v1/beta/invitations/XXXX-XXXX-XXXX-XXXX/validate
```

## Update System

### Check for Updates
```javascript
// Electron main process
const betaUpdater = require('./electron/beta-updater');
betaUpdater.checkForUpdates();
```

### Update Channels
- `beta`: Beta releases only
- `stable`: Stable releases only
- `all`: Both beta and stable

### Update Server
```
https://updates.yourcompany.com/beta
```

## File Locations

### Windows
```
%APPDATA%/solar-calculator-pro-beta/
├── config.json
├── database.db
├── logs/
└── temp/
```

### macOS
```
~/Library/Application Support/solar-calculator-pro-beta/
├── config.json
├── database.db
├── logs/
└── temp/
```

### Linux
```
~/.config/solar-calculator-pro-beta/
├── config.json
├── database.db
├── logs/
└── temp/
```

## Environment Variables

```bash
# Beta build
REACT_APP_BUILD_TYPE=beta
REACT_APP_ENABLE_BETA_FEATURES=true

# Crash reporting
SENTRY_DSN_BETA=https://...@sentry.io/...

# API endpoints
API_BASE_URL_BETA=http://localhost:8000

# Update server
UPDATE_SERVER_BETA=https://updates.yourcompany.com/beta
```

## Beta Expiration

### Check Expiration
```javascript
const betaUpdater = require('./electron/beta-updater');
const status = betaUpdater.checkBetaExpiration();

if (status.expired) {
  console.log(`Beta expired ${status.daysOverdue} days ago`);
} else if (status.warning) {
  console.log(`Beta expires in ${status.daysRemaining} days`);
}
```

### Set Expiration Date
```javascript
// In beta-config.js
expiration: {
  enabled: true,
  expiryDate: '2024-12-31',
  warningDays: 7,
  gracePeriodDays: 3,
}
```

## Monitoring

### Sentry Dashboard
```
https://sentry.io/organizations/yourcompany/projects/solar-calculator-beta/
```

### Key Metrics
- Crash rate
- Error frequency
- Performance metrics
- User sessions
- Feature usage

### Alerts
- Critical errors
- High crash rate
- Performance degradation
- Update failures

## Support

### Beta Support Email
```
beta@yourcompany.com
```

### Beta Forum
```
https://forum.yourcompany.com/beta
```

### Beta Discord
```
https://discord.gg/yourcompany-beta
```

## Release Process

### 1. Preparation
```bash
npm run prepare:beta
```

### 2. Build
```bash
npm run build:beta
```

### 3. Test
```bash
npm run test:beta
```

### 4. Upload
```bash
npm run upload:beta
```

### 5. Notify
```bash
npm run notify:beta-testers
```

## Troubleshooting

### Build Fails
1. Check git is clean
2. Verify dependencies installed
3. Check environment variables
4. Review build logs

### Crash Reporting Not Working
1. Verify SENTRY_DSN_BETA set
2. Check network connectivity
3. Review Sentry dashboard
4. Check crash reporter logs

### Updates Not Working
1. Verify update server accessible
2. Check update channel configuration
3. Review update logs
4. Test with manual update check

### Feedback Not Submitting
1. Check API endpoint
2. Verify authentication
3. Review network logs
4. Check feedback service status

## Common Issues

### Issue: Beta watermark not showing
**Solution**: Check beta-config.js `betaWatermark: true`

### Issue: Crash reports not sent
**Solution**: Verify Sentry DSN and network access

### Issue: Updates not detected
**Solution**: Check update server URL and channel

### Issue: Feedback widget not visible
**Solution**: Verify FeedbackWidget component mounted

## Resources

- [Beta Testing Guide](BETA_TESTING_GUIDE.md)
- [Beta Release Checklist](BETA_RELEASE_CHECKLIST.md)
- [Crash Reporting Guide](CRASH_REPORTING_GUIDE.md)
- [Feedback System Guide](FEEDBACK_SYSTEM_GUIDE.md)

---

*Last Updated: [Date]*
*Version: 1.0*
