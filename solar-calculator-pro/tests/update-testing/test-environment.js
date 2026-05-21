#!/usr/bin/env node

/**
 * Update Testing Environment Setup
 * 
 * This script sets up the testing environment for update testing.
 * It creates necessary directories, installs dependencies, and configures the test environment.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const TEST_DIR = __dirname;
const TEST_DATA_DIR = path.join(TEST_DIR, 'test-data');
const VERSIONS_DIR = path.join(TEST_DATA_DIR, 'versions');
const MANIFESTS_DIR = path.join(TEST_DATA_DIR, 'manifests');
const RELEASES_DIR = path.join(TEST_DATA_DIR, 'releases');
const BACKUPS_DIR = path.join(TEST_DATA_DIR, 'backups');
const RESULTS_DIR = path.join(TEST_DIR, 'results');

class TestEnvironment {
  constructor() {
    this.config = {
      testVersions: ['1.0.0', '1.0.1', '1.0.2', '2.0.0'],
      mockServerPort: 3000,
      testTimeout: 300000, // 5 minutes
      platforms: ['win', 'mac', 'linux'],
      channels: ['latest', 'beta', 'alpha']
    };
  }

  /**
   * Setup the test environment
   */
  async setup() {
    console.log('🔧 Setting up update testing environment...\n');

    try {
      // Create directories
      this.createDirectories();

      // Check dependencies
      this.checkDependencies();

      // Create configuration files
      this.createConfigFiles();

      // Create test data
      this.createTestData();

      console.log('\n✅ Test environment setup complete!');
      console.log('\nNext steps:');
      console.log('1. Build test versions: node version-builder.js --version 1.0.0');
      console.log('2. Start mock server: node mock-update-server.js');
      console.log('3. Run tests: npm test');
    } catch (error) {
      console.error('\n❌ Setup failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Create necessary directories
   */
  createDirectories() {
    console.log('📁 Creating directories...');

    const dirs = [
      TEST_DATA_DIR,
      VERSIONS_DIR,
      MANIFESTS_DIR,
      RELEASES_DIR,
      BACKUPS_DIR,
      RESULTS_DIR
    ];

    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`  ✓ Created ${path.relative(TEST_DIR, dir)}`);
      } else {
        console.log(`  ⊙ ${path.relative(TEST_DIR, dir)} already exists`);
      }
    });
  }

  /**
   * Check required dependencies
   */
  checkDependencies() {
    console.log('\n📦 Checking dependencies...');

    const requiredPackages = [
      'electron',
      'electron-builder',
      'electron-updater',
      'express',
      'axios',
      'chalk',
      'ora'
    ];

    const packageJsonPath = path.join(__dirname, '../../package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      console.log('  ⚠ package.json not found, skipping dependency check');
      return;
    }

    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const allDeps = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies
    };

    const missing = requiredPackages.filter(pkg => !allDeps[pkg]);

    if (missing.length > 0) {
      console.log('  ⚠ Missing dependencies:', missing.join(', '));
      console.log('  Run: npm install ' + missing.join(' '));
    } else {
      console.log('  ✓ All required dependencies installed');
    }
  }

  /**
   * Create configuration files
   */
  createConfigFiles() {
    console.log('\n⚙️  Creating configuration files...');

    // Test configuration
    const testConfig = {
      environment: 'test',
      mockServer: {
        port: this.config.mockServerPort,
        host: 'localhost',
        protocol: 'http'
      },
      versions: this.config.testVersions,
      platforms: this.config.platforms,
      channels: this.config.channels,
      timeout: this.config.testTimeout,
      retries: 3,
      logging: {
        level: 'debug',
        file: path.join(RESULTS_DIR, 'test.log')
      }
    };

    const configPath = path.join(TEST_DIR, 'test-config.json');
    fs.writeFileSync(configPath, JSON.stringify(testConfig, null, 2));
    console.log('  ✓ Created test-config.json');

    // Environment variables
    const envContent = `# Update Testing Environment Variables
NODE_ENV=test
UPDATE_SERVER_URL=http://localhost:${this.config.mockServerPort}
UPDATE_CHANNEL=latest
AUTO_DOWNLOAD=false
AUTO_INSTALL=false
TEST_TIMEOUT=${this.config.testTimeout}
LOG_LEVEL=debug
`;

    const envPath = path.join(TEST_DIR, '.env.test');
    fs.writeFileSync(envPath, envContent);
    console.log('  ✓ Created .env.test');
  }

  /**
   * Create test data
   */
  createTestData() {
    console.log('\n📝 Creating test data...');

    // Create sample release notes
    this.config.testVersions.forEach(version => {
      const releaseNotes = this.generateReleaseNotes(version);
      const notesPath = path.join(MANIFESTS_DIR, `release-notes-${version}.md`);
      fs.writeFileSync(notesPath, releaseNotes);
      console.log(`  ✓ Created release notes for v${version}`);
    });

    // Create test scenarios
    const scenarios = this.generateTestScenarios();
    const scenariosPath = path.join(TEST_DIR, 'test-scenarios.json');
    fs.writeFileSync(scenariosPath, JSON.stringify(scenarios, null, 2));
    console.log('  ✓ Created test scenarios');
  }

  /**
   * Generate release notes for a version
   */
  generateReleaseNotes(version) {
    const notes = {
      '1.0.0': `# Version 1.0.0 - Initial Release

## Features
- Solar calculator with 3D visualization
- Heat pump calculator
- Price matrix management
- PDF generation
- CRM system
- Product database

## Known Issues
- None

## Installation
Download and install the application.
`,
      '1.0.1': `# Version 1.0.1 - Bug Fixes

## Bug Fixes
- Fixed calculation errors in solar calculator
- Improved 3D rendering performance
- Fixed PDF generation issues
- Updated price matrix validation

## Improvements
- Better error messages
- Faster startup time
- Improved UI responsiveness

## Known Issues
- None
`,
      '1.0.2': `# Version 1.0.2 - Feature Update

## New Features
- Advanced solar calculations
- Battery storage optimization
- Enhanced 3D visualization
- New PDF templates

## Bug Fixes
- Fixed memory leaks
- Improved database performance
- Fixed update notification issues

## Database Changes
- Added new tables for battery storage
- Updated schema for better performance

## Known Issues
- None
`,
      '2.0.0': `# Version 2.0.0 - Major Update

## Breaking Changes
- New database schema (automatic migration)
- Updated API endpoints
- Changed configuration format

## New Features
- Complete UI redesign
- Advanced analytics
- Multi-language support
- Cloud synchronization
- Mobile app integration

## Improvements
- 50% faster calculations
- 30% smaller file size
- Better error handling
- Enhanced security

## Migration
Your data will be automatically migrated. Please backup before updating.

## Known Issues
- None
`
    };

    return notes[version] || `# Version ${version}\n\nRelease notes for version ${version}.`;
  }

  /**
   * Generate test scenarios
   */
  generateTestScenarios() {
    return {
      scenarios: [
        {
          id: 'basic-update',
          name: 'Basic Update Flow',
          description: 'Test basic update from v1.0.0 to v1.0.1',
          steps: [
            'Install v1.0.0',
            'Check for updates',
            'Download v1.0.1',
            'Install update',
            'Verify v1.0.1 is running'
          ],
          expectedResult: 'App successfully updated to v1.0.1',
          priority: 'high'
        },
        {
          id: 'skip-version',
          name: 'Skip Version',
          description: 'Test skipping a version',
          steps: [
            'Install v1.0.0',
            'Check for updates (v1.0.1 available)',
            'Skip v1.0.1',
            'Check for updates again',
            'Verify v1.0.1 is skipped',
            'Check for v1.0.2',
            'Download and install v1.0.2'
          ],
          expectedResult: 'App updated to v1.0.2, skipping v1.0.1',
          priority: 'medium'
        },
        {
          id: 'cancel-download',
          name: 'Cancel Download',
          description: 'Test cancelling an update download',
          steps: [
            'Install v1.0.0',
            'Start downloading v1.0.1',
            'Cancel download',
            'Verify download cancelled',
            'Restart download',
            'Complete installation'
          ],
          expectedResult: 'Download can be cancelled and restarted',
          priority: 'medium'
        },
        {
          id: 'network-failure',
          name: 'Network Failure',
          description: 'Test update with network failure',
          steps: [
            'Install v1.0.0',
            'Start downloading v1.0.1',
            'Simulate network failure',
            'Verify error handling',
            'Restore network',
            'Retry download',
            'Complete installation'
          ],
          expectedResult: 'Update recovers from network failure',
          priority: 'high'
        },
        {
          id: 'rollback',
          name: 'Rollback',
          description: 'Test rolling back to previous version',
          steps: [
            'Install v1.0.1',
            'Detect critical bug',
            'Rollback to v1.0.0',
            'Verify v1.0.0 is running',
            'Verify data integrity'
          ],
          expectedResult: 'Successfully rolled back to v1.0.0',
          priority: 'high'
        },
        {
          id: 'channel-switch',
          name: 'Channel Switching',
          description: 'Test switching update channels',
          steps: [
            'Install v1.0.0 (stable)',
            'Switch to beta channel',
            'Check for updates',
            'Download beta version',
            'Install and verify'
          ],
          expectedResult: 'Successfully switched to beta channel',
          priority: 'low'
        },
        {
          id: 'auto-download',
          name: 'Auto-Download',
          description: 'Test automatic download',
          steps: [
            'Enable auto-download',
            'Check for updates',
            'Verify automatic download',
            'Verify installation prompt'
          ],
          expectedResult: 'Update downloads automatically',
          priority: 'medium'
        },
        {
          id: 'auto-install',
          name: 'Auto-Install on Quit',
          description: 'Test automatic installation on quit',
          steps: [
            'Enable auto-install on quit',
            'Download update',
            'Quit application',
            'Verify update installs',
            'Verify app restarts'
          ],
          expectedResult: 'Update installs automatically on quit',
          priority: 'medium'
        },
        {
          id: 'major-version',
          name: 'Major Version Update',
          description: 'Test major version update with breaking changes',
          steps: [
            'Install v1.0.2',
            'Check for updates (v2.0.0 available)',
            'Review breaking changes',
            'Download v2.0.0',
            'Install update',
            'Verify database migration',
            'Verify app functions correctly'
          ],
          expectedResult: 'Successfully updated to v2.0.0 with data migration',
          priority: 'high'
        },
        {
          id: 'corrupted-download',
          name: 'Corrupted Download',
          description: 'Test handling of corrupted download',
          steps: [
            'Install v1.0.0',
            'Start downloading v1.0.1',
            'Corrupt download file',
            'Verify SHA512 check fails',
            'Verify error message',
            'Retry download',
            'Complete installation'
          ],
          expectedResult: 'Corrupted download detected and handled',
          priority: 'high'
        }
      ]
    };
  }

  /**
   * Clean up test environment
   */
  async cleanup() {
    console.log('🧹 Cleaning up test environment...\n');

    try {
      // Remove test data (keep backups)
      const dirsToClean = [VERSIONS_DIR, RELEASES_DIR, RESULTS_DIR];

      dirsToClean.forEach(dir => {
        if (fs.existsSync(dir)) {
          fs.rmSync(dir, { recursive: true, force: true });
          console.log(`  ✓ Cleaned ${path.relative(TEST_DIR, dir)}`);
        }
      });

      console.log('\n✅ Cleanup complete!');
    } catch (error) {
      console.error('\n❌ Cleanup failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Verify test environment
   */
  async verify() {
    console.log('🔍 Verifying test environment...\n');

    const checks = [
      {
        name: 'Directories exist',
        check: () => {
          const dirs = [TEST_DATA_DIR, VERSIONS_DIR, MANIFESTS_DIR, RELEASES_DIR];
          return dirs.every(dir => fs.existsSync(dir));
        }
      },
      {
        name: 'Configuration files exist',
        check: () => {
          const files = [
            path.join(TEST_DIR, 'test-config.json'),
            path.join(TEST_DIR, '.env.test')
          ];
          return files.every(file => fs.existsSync(file));
        }
      },
      {
        name: 'Test data exists',
        check: () => {
          const files = [
            path.join(TEST_DIR, 'test-scenarios.json'),
            path.join(MANIFESTS_DIR, 'release-notes-1.0.0.md')
          ];
          return files.every(file => fs.existsSync(file));
        }
      }
    ];

    let allPassed = true;

    checks.forEach(({ name, check }) => {
      const passed = check();
      console.log(`  ${passed ? '✓' : '✗'} ${name}`);
      if (!passed) allPassed = false;
    });

    if (allPassed) {
      console.log('\n✅ Test environment is ready!');
    } else {
      console.log('\n❌ Test environment has issues. Run setup again.');
      process.exit(1);
    }
  }
}

// CLI
if (require.main === module) {
  const command = process.argv[2] || 'setup';
  const env = new TestEnvironment();

  switch (command) {
    case 'setup':
      env.setup();
      break;
    case 'cleanup':
      env.cleanup();
      break;
    case 'verify':
      env.verify();
      break;
    default:
      console.log('Usage: node test-environment.js [setup|cleanup|verify]');
      process.exit(1);
  }
}

module.exports = TestEnvironment;
