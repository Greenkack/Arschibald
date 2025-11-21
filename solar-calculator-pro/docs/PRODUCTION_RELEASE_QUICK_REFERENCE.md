# Production Release Quick Reference

Quick reference guide for releasing Solar Calculator Pro to production.

## Prerequisites

- [ ] All tests passing
- [ ] Beta testing complete
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Git working directory clean
- [ ] Code signing certificates valid

## Environment Setup

```bash
# Required environment variables
export GITHUB_TOKEN="your-github-token"
export WEBSITE_DEPLOY_KEY="your-deploy-key"
export UPDATE_SERVER_URL="https://updates.solarcalculatorpro.com"
export WINDOWS_CERT_PATH="/path/to/cert.pfx"
export APPLE_ID="your-apple-id"
```

## Quick Release Commands

### Full Automated Release
```bash
./scripts/release-production.sh
```

### Step-by-Step Release

```bash
# 1. Build production releases
node scripts/production-release.js

# 2. Upload to distribution
node scripts/upload-to-distribution.js

# 3. Update website
node scripts/update-website.js
```

## Manual Steps Checklist

After automated release:

- [ ] Send release announcement email
- [ ] Post on social media (Twitter, LinkedIn, Facebook)
- [ ] Update app store listings (if applicable)
- [ ] Announce in community forum
- [ ] Notify beta testers
- [ ] Monitor analytics and error reports
- [ ] Ensure support team is ready

## Distribution Channels

| Channel | URL | Status |
|---------|-----|--------|
| GitHub Releases | https://github.com/yourorg/solar-calculator-pro/releases | Automated |
| Website Downloads | https://solarcalculatorpro.com/download | Automated |
| Update Server | Configured in app | Automated |

## Support Channels

| Channel | Contact | Response Time |
|---------|---------|---------------|
| Email | support@solarcalculatorpro.com | 4-72 hours |
| Documentation | https://docs.solarcalculatorpro.com | 24/7 |
| Issue Tracker | GitHub Issues | 24-48 hours |
| Live Chat | Website | < 5 min (business hours) |
| Social Media | Twitter/LinkedIn | < 2 hours |

## Monitoring

### Key Metrics to Watch

- Download statistics
- Error rates
- Support ticket volume
- Auto-update adoption
- User feedback

### Monitoring Tools

- Sentry (error tracking)
- Google Analytics (usage)
- GitHub Insights (downloads)
- Support ticketing system
- Status page

## Rollback Procedure

If critical issues arise:

```bash
# 1. Disable auto-updates
# Edit update-manifest.json to point to previous version

# 2. Remove from GitHub releases
gh release delete v1.0.0

# 3. Update website
# Revert download links to previous version

# 4. Communicate with users
# Send email and post on all channels
```

## Common Issues

### Build Fails
- Check code signing certificates
- Verify all dependencies installed
- Check disk space
- Review build logs

### Upload Fails
- Verify credentials/tokens
- Check network connectivity
- Verify file permissions
- Check server capacity

### Auto-Update Not Working
- Verify update manifest
- Check update server URL
- Verify file checksums
- Check electron-updater config

## Emergency Contacts

- **Release Manager**: [Name] - [Email] - [Phone]
- **Development Lead**: [Name] - [Email] - [Phone]
- **Support Lead**: [Name] - [Email] - [Phone]
- **On-Call Engineer**: [PagerDuty/OpsGenie]

## Post-Release Timeline

### First Hour
- Monitor error rates
- Check download links
- Verify auto-updates
- Monitor support channels

### First Day
- Review download statistics
- Check error reports
- Respond to support requests
- Monitor social media

### First Week
- Analyze metrics
- Review user feedback
- Plan hotfix if needed
- Update documentation

### First Month
- Monthly report
- User survey
- Feature analysis
- Plan next release

## Quick Links

- [Full Release Checklist](PRODUCTION_RELEASE_CHECKLIST.md)
- [Support Setup Guide](SUPPORT_CHANNELS_SETUP.md)
- [Release Announcement Template](RELEASE_ANNOUNCEMENT_TEMPLATE.md)
- [Task 90 Complete](../TASK_90_COMPLETE.md)

## Version History

| Version | Release Date | Notes |
|---------|--------------|-------|
| 1.0.0 | YYYY-MM-DD | Initial production release |

---

**Last Updated**: [Date]
**Maintained By**: Release Team
