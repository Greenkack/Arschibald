# CI/CD Pipeline Quick Reference

## Quick Start

### Running Workflows Manually

```bash
# Using GitHub CLI
gh workflow run ci.yml
gh workflow run build.yml --ref main
gh workflow run release.yml --ref v1.0.0
```

### Viewing Workflow Status

```bash
# List recent runs
gh run list --workflow=ci.yml --limit 5

# View specific run
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>
```

### Re-running Workflows

```bash
# Re-run failed jobs only
gh run rerun <run-id> --failed

# Re-run entire workflow
gh run rerun <run-id>
```

## Workflow Cheat Sheet

### CI Workflow

**File**: `.github/workflows/ci.yml`

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Jobs**:
- `backend-tests`: Python tests with pytest
- `frontend-tests`: React tests with Jest
- `e2e-tests`: Playwright E2E tests
- `security-scan`: Trivy, npm audit, pip audit
- `code-quality`: Linters and formatters

**Duration**: ~10-15 minutes

### Build Workflow

**File**: `.github/workflows/build.yml`

**Triggers**:
- Push to `main`
- Tags `v*`
- Manual dispatch

**Jobs**:
- `build-windows`: Windows .exe and .msi
- `build-macos`: macOS .dmg and .zip
- `build-linux`: Linux .AppImage and .deb

**Duration**: ~30-45 minutes

### Release Workflow

**File**: `.github/workflows/release.yml`

**Triggers**:
- Tags `v*.*.*`

**Jobs**:
- `create-release`: Create GitHub release
- `build-and-upload-windows`: Build and upload Windows
- `build-and-upload-macos`: Build and upload macOS
- `build-and-upload-linux`: Build and upload Linux
- `update-manifest`: Update auto-update manifest

**Duration**: ~45-60 minutes

### Performance Workflow

**File**: `.github/workflows/performance.yml`

**Triggers**:
- Push to `main`
- Pull requests to `main`
- Daily at 2 AM UTC
- Manual dispatch

**Jobs**:
- `backend-performance`: Load tests and benchmarks
- `frontend-performance`: Bundle size and Lighthouse
- `e2e-performance`: Performance E2E tests
- `database-performance`: Database benchmarks

**Duration**: ~20-30 minutes

### Security Workflow

**File**: `.github/workflows/security.yml`

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Weekly on Monday at 3 AM UTC
- Manual dispatch

**Jobs**:
- `dependency-scan`: Snyk, npm audit, pip audit
- `code-scanning`: CodeQL analysis
- `container-scan`: Trivy scanner
- `secret-scan`: Gitleaks and TruffleHog
- `sast-scan`: Bandit and ESLint security
- `license-scan`: License compliance

**Duration**: ~15-25 minutes

## Common Commands

### Creating a Release

```bash
# 1. Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. Release workflow runs automatically

# 3. Monitor release
gh run list --workflow=release.yml
gh run watch <run-id>
```

### Checking Build Status

```bash
# Check status of latest CI run
gh run list --workflow=ci.yml --limit 1

# Check all workflows
gh run list --limit 10

# View failed runs only
gh run list --status=failure
```

### Downloading Artifacts

```bash
# List artifacts for a run
gh run view <run-id> --log

# Download all artifacts
gh run download <run-id>

# Download specific artifact
gh run download <run-id> --name windows-build
```

### Managing Cache

```bash
# List caches
gh cache list

# Delete specific cache
gh cache delete <cache-key>

# Delete all caches (use with caution)
gh cache delete --all
```

## Required Secrets

### Code Signing

```
APPLE_ID                    # macOS: Apple Developer ID
APPLE_ID_PASSWORD           # macOS: App-specific password
APPLE_TEAM_ID               # macOS: Team ID
WINDOWS_CERTIFICATE         # Windows: Base64 certificate
WINDOWS_CERTIFICATE_PASSWORD # Windows: Certificate password
```

### Security Scanning

```
SNYK_TOKEN                  # Snyk API token
```

### Optional

```
CODECOV_TOKEN               # Code coverage reporting
SENTRY_DSN                  # Error tracking
AWS_ACCESS_KEY_ID           # S3 uploads
AWS_SECRET_ACCESS_KEY       # S3 uploads
```

## Troubleshooting Quick Fixes

### Build Fails

```bash
# Clear cache and retry
gh cache delete --all
gh run rerun <run-id>
```

### Tests Timeout

```yaml
# Increase timeout in workflow
timeout-minutes: 30  # Default is 360
```

### macOS Signing Fails

```bash
# Verify secrets are set
gh secret list

# Check certificate validity
security find-identity -v -p codesigning
```

### Dependency Issues

```bash
# Update dependencies locally first
cd backend && pip install --upgrade -r requirements.txt
cd frontend && npm update

# Commit and push
git add .
git commit -m "Update dependencies"
git push
```

## Workflow Status Badges

Add to README.md:

```markdown
![CI](https://github.com/username/repo/workflows/CI/badge.svg)
![Build](https://github.com/username/repo/workflows/Build/badge.svg)
![Security](https://github.com/username/repo/workflows/Security/badge.svg)
```

## Performance Metrics

### Target Metrics

- **CI Workflow**: < 15 minutes
- **Build Workflow**: < 45 minutes
- **Test Coverage**: > 80%
- **Bundle Size**: < 5MB (frontend)
- **Backend Response**: < 200ms (p95)

### Monitoring

```bash
# Check workflow duration
gh run list --workflow=ci.yml --json durationMs

# View test coverage
# Check Codecov dashboard or artifacts
```

## Release Checklist

- [ ] All tests passing on `main`
- [ ] Version bumped in `package.json`
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Create and push tag
- [ ] Monitor release workflow
- [ ] Verify artifacts uploaded
- [ ] Test installers on each platform
- [ ] Announce release

## Emergency Procedures

### Cancel Running Workflow

```bash
# Cancel specific run
gh run cancel <run-id>

# Cancel all runs for a workflow
gh run list --workflow=ci.yml --json databaseId --jq '.[].databaseId' | xargs -I {} gh run cancel {}
```

### Rollback Release

```bash
# Delete release and tag
gh release delete v1.0.0 --yes
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### Disable Workflow

```yaml
# Add to workflow file
on:
  workflow_dispatch:  # Only manual triggers
```

## Useful Links

- **Actions Dashboard**: `https://github.com/username/repo/actions`
- **Secrets Settings**: `https://github.com/username/repo/settings/secrets/actions`
- **Branch Protection**: `https://github.com/username/repo/settings/branches`
- **Releases**: `https://github.com/username/repo/releases`

## Support

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Status Page**: https://www.githubstatus.com/

---

**Quick Reference Version**: 1.0.0
