# CI/CD Pipeline Guide

## Overview

This document describes the complete CI/CD pipeline setup for Solar Calculator Pro, including continuous integration, automated builds, releases, performance testing, and security scanning.

## Table of Contents

1. [Pipeline Architecture](#pipeline-architecture)
2. [Workflows](#workflows)
3. [Setup Instructions](#setup-instructions)
4. [Secrets Configuration](#secrets-configuration)
5. [Workflow Triggers](#workflow-triggers)
6. [Artifacts and Reports](#artifacts-and-reports)
7. [Troubleshooting](#troubleshooting)

## Pipeline Architecture

The CI/CD pipeline consists of five main workflows:

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflows                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CI Tests   │  │    Build     │  │   Release    │      │
│  │              │  │              │  │              │      │
│  │ • Backend    │  │ • Windows    │  │ • Create     │      │
│  │ • Frontend   │  │ • macOS      │  │ • Upload     │      │
│  │ • E2E        │  │ • Linux      │  │ • Manifest   │      │
│  │ • Security   │  │              │  │              │      │
│  │ • Quality    │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Performance  │  │   Security   │                        │
│  │              │  │              │                        │
│  │ • Load Tests │  │ • Dependency │                        │
│  │ • Benchmarks │  │ • CodeQL     │                        │
│  │ • Lighthouse │  │ • Container  │                        │
│  │ • Bundle     │  │ • Secrets    │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Workflows

### 1. CI Workflow (`ci.yml`)

**Purpose**: Continuous integration testing on every push and pull request

**Jobs**:
- **Backend Tests**: Runs Python tests with pytest, generates coverage reports
- **Frontend Tests**: Runs TypeScript/React tests with Jest, linting, type checking
- **E2E Tests**: Runs end-to-end tests with Playwright
- **Security Scan**: Runs Trivy, npm audit, pip audit
- **Code Quality**: Runs Black, Flake8, MyPy, ESLint, Prettier

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Matrix Testing**:
- Python: 3.10, 3.11
- Node.js: 18.x, 20.x

### 2. Build Workflow (`build.yml`)

**Purpose**: Multi-platform application builds

**Jobs**:
- **Build Windows**: Creates Windows installer (.exe, .msi)
- **Build macOS**: Creates macOS DMG and ZIP
- **Build Linux**: Creates AppImage, DEB, and RPM packages

**Triggers**:
- Push to `main` branch
- Tags matching `v*`
- Manual workflow dispatch

**Artifacts**:
- Windows: `.exe`, `.msi`
- macOS: `.dmg`, `.zip`
- Linux: `.AppImage`, `.deb`, `.rpm`

### 3. Release Workflow (`release.yml`)

**Purpose**: Automated release creation and distribution

**Jobs**:
- **Create Release**: Creates GitHub release with changelog
- **Build and Upload Windows**: Builds and uploads Windows artifacts
- **Build and Upload macOS**: Builds and uploads macOS artifacts
- **Build and Upload Linux**: Builds and uploads Linux artifacts
- **Update Manifest**: Generates and uploads auto-update manifest

**Triggers**:
- Tags matching `v*.*.*` (semantic versioning)

**Features**:
- Automatic changelog generation
- Checksum calculation for all artifacts
- Auto-update manifest generation
- Code signing (Windows and macOS)

### 4. Performance Workflow (`performance.yml`)

**Purpose**: Performance testing and monitoring

**Jobs**:
- **Backend Performance**: Load tests with Locust, benchmarks with pytest-benchmark
- **Frontend Performance**: Bundle size analysis, Lighthouse CI
- **E2E Performance**: Performance-focused E2E tests
- **Database Performance**: Database query benchmarks
- **Compare Performance**: Compares with baseline metrics

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch
- Daily schedule (2 AM UTC)
- Manual workflow dispatch

**Reports**:
- Load test HTML reports
- Benchmark JSON results
- Lighthouse performance scores
- Bundle size analysis

### 5. Security Workflow (`security.yml`)

**Purpose**: Security scanning and vulnerability detection

**Jobs**:
- **Dependency Scan**: Snyk, npm audit, pip audit
- **Code Scanning**: CodeQL analysis for JavaScript and Python
- **Container Scan**: Trivy vulnerability scanner
- **Secret Scan**: Gitleaks and TruffleHog
- **SAST Scan**: Bandit for Python, ESLint security for JavaScript
- **License Scan**: License compliance checking
- **Security Report**: Consolidated security report generation

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly schedule (Monday 3 AM UTC)
- Manual workflow dispatch

## Setup Instructions

### 1. Repository Setup

1. **Enable GitHub Actions**:
   ```bash
   # Actions are enabled by default for new repositories
   # Check: Settings > Actions > General
   ```

2. **Create workflow directory**:
   ```bash
   mkdir -p .github/workflows
   ```

3. **Copy workflow files**:
   ```bash
   cp workflows/*.yml .github/workflows/
   ```

### 2. Branch Protection

Configure branch protection rules for `main` and `develop`:

1. Go to **Settings > Branches > Add rule**
2. Branch name pattern: `main` or `develop`
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Status checks: All CI jobs
   - ✅ Require pull request reviews before merging
   - ✅ Dismiss stale pull request approvals when new commits are pushed

### 3. Caching Configuration

Workflows use GitHub Actions cache to speed up builds:

- **Node modules**: Cached by `package-lock.json` hash
- **Python packages**: Cached by `requirements.txt` hash
- **Build artifacts**: Cached between jobs

Cache is automatically managed by GitHub Actions.

## Secrets Configuration

### Required Secrets

Configure these secrets in **Settings > Secrets and variables > Actions**:

#### Code Signing (macOS)

```
APPLE_ID=your-apple-id@example.com
APPLE_ID_PASSWORD=app-specific-password
APPLE_TEAM_ID=XXXXXXXXXX
```

**How to get**:
1. Apple ID: Your Apple Developer account email
2. App-specific password: Generate at appleid.apple.com
3. Team ID: Found in Apple Developer account

#### Code Signing (Windows)

```
WINDOWS_CERTIFICATE=base64-encoded-certificate
WINDOWS_CERTIFICATE_PASSWORD=certificate-password
```

**How to get**:
1. Purchase code signing certificate
2. Convert to base64: `base64 -i certificate.pfx`
3. Store password securely

#### Security Scanning

```
SNYK_TOKEN=your-snyk-api-token
```

**How to get**:
1. Sign up at snyk.io
2. Go to Account Settings > API Token
3. Copy token

#### Optional Secrets

```
CODECOV_TOKEN=your-codecov-token
SENTRY_DSN=your-sentry-dsn
AWS_ACCESS_KEY_ID=for-s3-uploads
AWS_SECRET_ACCESS_KEY=for-s3-uploads
```

## Workflow Triggers

### Automatic Triggers

| Workflow | Push (main) | Push (develop) | PR | Tag | Schedule |
|----------|-------------|----------------|-----|-----|----------|
| CI | ✅ | ✅ | ✅ | ❌ | ❌ |
| Build | ✅ | ❌ | ❌ | ✅ | ❌ |
| Release | ❌ | ❌ | ❌ | ✅ | ❌ |
| Performance | ✅ | ❌ | ✅ | ❌ | Daily |
| Security | ✅ | ✅ | ✅ | ❌ | Weekly |

### Manual Triggers

All workflows support manual triggering via `workflow_dispatch`:

```bash
# Using GitHub CLI
gh workflow run ci.yml
gh workflow run build.yml
gh workflow run performance.yml
gh workflow run security.yml
```

Or via GitHub UI: **Actions > Select workflow > Run workflow**

## Artifacts and Reports

### CI Artifacts

- **Test Coverage Reports**: HTML and XML coverage reports
- **Playwright Reports**: E2E test results with screenshots
- **Lint Reports**: ESLint and Flake8 results

**Retention**: 30 days

### Build Artifacts

- **Windows Build**: `.exe` and `.msi` installers
- **macOS Build**: `.dmg` and `.zip` packages
- **Linux Build**: `.AppImage`, `.deb`, `.rpm` packages

**Retention**: 30 days (90 days for releases)

### Performance Artifacts

- **Load Test Reports**: HTML reports from Locust
- **Benchmark Results**: JSON benchmark data
- **Lighthouse Reports**: Performance scores and metrics
- **Bundle Analysis**: Webpack bundle analyzer reports

**Retention**: 30 days

### Security Artifacts

- **Dependency Audit**: npm and pip audit results
- **SAST Results**: Bandit and ESLint security findings
- **License Reports**: License compliance reports
- **Security Report**: Consolidated security summary

**Retention**: 90 days

## Troubleshooting

### Common Issues

#### 1. Build Fails on Windows

**Symptom**: PyInstaller fails to create executable

**Solution**:
```yaml
# Ensure Python and dependencies are correctly installed
- name: Install backend dependencies
  run: |
    cd backend
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
```

#### 2. macOS Code Signing Fails

**Symptom**: Notarization fails or certificate not found

**Solution**:
- Verify Apple ID credentials are correct
- Ensure app-specific password is used (not regular password)
- Check Team ID matches your Apple Developer account
- Verify certificate is valid and not expired

#### 3. Tests Timeout

**Symptom**: E2E tests timeout waiting for server

**Solution**:
```yaml
# Increase wait time for server startup
- name: Start backend server
  run: |
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    sleep 15  # Increase from 10 to 15 seconds
```

#### 4. Cache Not Working

**Symptom**: Dependencies reinstalled every time

**Solution**:
- Verify cache key includes correct hash file
- Check cache size limits (10GB per repository)
- Clear cache manually if corrupted:
  ```bash
  gh cache delete <cache-key>
  ```

#### 5. Security Scan False Positives

**Symptom**: Security workflow fails on known safe dependencies

**Solution**:
```yaml
# Add continue-on-error for non-critical scans
- name: Run npm audit
  run: npm audit --audit-level=moderate
  continue-on-error: true
```

### Debugging Workflows

#### Enable Debug Logging

1. Go to **Settings > Secrets and variables > Actions**
2. Add repository variable:
   - Name: `ACTIONS_STEP_DEBUG`
   - Value: `true`

#### View Workflow Logs

```bash
# Using GitHub CLI
gh run list --workflow=ci.yml
gh run view <run-id> --log
```

#### Re-run Failed Jobs

```bash
# Re-run failed jobs only
gh run rerun <run-id> --failed

# Re-run entire workflow
gh run rerun <run-id>
```

### Performance Optimization

#### 1. Parallel Jobs

Jobs run in parallel by default. Ensure dependencies are correctly specified:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
  
  build:
    needs: test  # Only run after test succeeds
    runs-on: ubuntu-latest
```

#### 2. Matrix Strategy

Use matrix for testing multiple versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']
    node-version: ['18.x', '20.x']
```

#### 3. Caching

Always cache dependencies:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Best Practices

### 1. Workflow Organization

- Keep workflows focused on single responsibilities
- Use reusable workflows for common tasks
- Document all custom actions

### 2. Security

- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly
- Limit secret access to necessary workflows

### 3. Testing

- Run fast tests first (unit tests before E2E)
- Use matrix testing for multiple environments
- Keep test suites fast (<10 minutes)
- Generate and upload test reports

### 4. Releases

- Use semantic versioning (v1.2.3)
- Generate changelogs automatically
- Include checksums for all artifacts
- Test releases in staging before production

### 5. Monitoring

- Set up notifications for failed workflows
- Monitor workflow execution times
- Track artifact sizes
- Review security scan results regularly

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Electron Builder Documentation](https://www.electron.build/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Locust Documentation](https://locust.io/)

## Support

For issues with the CI/CD pipeline:

1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Check GitHub Actions status page
4. Contact DevOps team

---

**Last Updated**: 2024
**Version**: 1.0.0
