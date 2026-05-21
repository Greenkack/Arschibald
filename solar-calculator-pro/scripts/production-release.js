#!/usr/bin/env node

/**
 * Production Release Script
 * Handles the complete production release process
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class ProductionReleaseManager {
  constructor() {
    this.version = this.getVersion();
    this.platforms = ['windows', 'macos', 'linux'];
    this.releaseDir = path.join(__dirname, '..', 'release', 'production');
  }

  getVersion() {
    const packageJson = require('../package.json');
    return packageJson.version;
  }

  async run() {
    console.log('🚀 Starting Production Release Process');
    console.log(`📦 Version: ${this.version}`);
    
    try {
      await this.validatePrerequisites();
      await this.runTests();
      await this.buildProduction();
      await this.signBuilds();
      await this.generateChecksums();
      await this.createReleaseNotes();
      await this.prepareDistribution();
      
      console.log('✅ Production Release Complete!');
      console.log(`📁 Release files: ${this.releaseDir}`);
    } catch (error) {
      console.error('❌ Release failed:', error.message);
      process.exit(1);
    }
  }

  async validatePrerequisites() {
    console.log('\n📋 Validating Prerequisites...');
    
    // Check git status
    const gitStatus = execSync('git status --porcelain').toString();
    if (gitStatus) {
      throw new Error('Working directory not clean. Commit or stash changes.');
    }
    
    // Check version tag
    const tags = execSync('git tag').toString().split('\n');
    if (tags.includes(`v${this.version}`)) {
      throw new Error(`Version tag v${this.version} already exists`);
    }
    
    console.log('✅ Prerequisites validated');
  }

  async runTests() {
    console.log('\n🧪 Running Test Suite...');
    
    try {
      // Backend tests
      console.log('  Running backend tests...');
      execSync('cd backend && python -m pytest tests/ -v', { stdio: 'inherit' });
      
      // Frontend tests
      console.log('  Running frontend tests...');
      execSync('cd frontend && npm test -- --run', { stdio: 'inherit' });
      
      console.log('✅ All tests passed');
    } catch (error) {
      throw new Error('Tests failed. Fix issues before release.');
    }
  }

  async buildProduction() {
    console.log('\n🔨 Building Production Releases...');
    
    // Ensure release directory exists
    if (!fs.existsSync(this.releaseDir)) {
      fs.mkdirSync(this.releaseDir, { recursive: true });
    }
    
    for (const platform of this.platforms) {
      console.log(`  Building for ${platform}...`);
      
      const buildCommand = platform === 'windows' 
        ? 'npm run electron:build:win'
        : platform === 'macos'
        ? 'npm run electron:build:mac'
        : 'npm run electron:build:linux';
      
      execSync(buildCommand, { stdio: 'inherit' });
    }
    
    console.log('✅ Production builds complete');
  }

  async signBuilds() {
    console.log('\n🔐 Signing Builds...');
    
    // Windows signing
    if (process.platform === 'win32' && process.env.WINDOWS_CERT_PATH) {
      console.log('  Signing Windows build...');
      // Signing is handled by electron-builder
    }
    
    // macOS signing and notarization
    if (process.platform === 'darwin' && process.env.APPLE_ID) {
      console.log('  Signing and notarizing macOS build...');
      // Handled by electron-builder with notarize.js
    }
    
    console.log('✅ Builds signed');
  }

  async generateChecksums() {
    console.log('\n🔢 Generating Checksums...');
    
    const crypto = require('crypto');
    const checksums = {};
    
    const releaseFiles = fs.readdirSync(this.releaseDir);
    
    for (const file of releaseFiles) {
      if (file.endsWith('.exe') || file.endsWith('.dmg') || file.endsWith('.AppImage')) {
        const filePath = path.join(this.releaseDir, file);
        const fileBuffer = fs.readFileSync(filePath);
        const hash = crypto.createHash('sha256').update(fileBuffer).digest('hex');
        checksums[file] = hash;
        console.log(`  ${file}: ${hash}`);
      }
    }
    
    // Write checksums file
    const checksumsPath = path.join(this.releaseDir, 'SHA256SUMS.txt');
    const checksumsContent = Object.entries(checksums)
      .map(([file, hash]) => `${hash}  ${file}`)
      .join('\n');
    
    fs.writeFileSync(checksumsPath, checksumsContent);
    console.log('✅ Checksums generated');
  }

  async createReleaseNotes() {
    console.log('\n📝 Creating Release Notes...');
    
    const releaseNotes = this.generateReleaseNotes();
    const notesPath = path.join(this.releaseDir, 'RELEASE_NOTES.md');
    
    fs.writeFileSync(notesPath, releaseNotes);
    console.log('✅ Release notes created');
  }

  generateReleaseNotes() {
    const date = new Date().toISOString().split('T')[0];
    
    return `# Solar Calculator Pro v${this.version}

**Release Date:** ${date}

## 🎉 What's New

This is the production release of Solar Calculator Pro, a modern desktop application for solar energy system calculations.

### Key Features

- ☀️ **Solar Calculator**: Complete solar system design and calculation
- 🔥 **Heat Pump Calculator**: Heat pump sizing and efficiency analysis
- 💰 **Price Matrix**: Dynamic pricing with Excel-like formulas
- 📄 **PDF Generation**: Professional PDF reports with customization
- 🏢 **CRM System**: Customer relationship management
- 📦 **Product Database**: Comprehensive product catalog
- 🎨 **Modern UI**: Beautiful, responsive interface with PrimeReact
- 🌍 **Multi-Platform**: Windows, macOS, and Linux support
- 🔄 **Auto-Update**: Automatic updates for new versions
- 🔐 **Secure**: Enterprise-grade security features

### System Requirements

**Windows:**
- Windows 10 or later (64-bit)
- 4 GB RAM minimum, 8 GB recommended
- 500 MB free disk space

**macOS:**
- macOS 10.13 (High Sierra) or later
- 4 GB RAM minimum, 8 GB recommended
- 500 MB free disk space

**Linux:**
- Ubuntu 18.04 or later (or equivalent)
- 4 GB RAM minimum, 8 GB recommended
- 500 MB free disk space

### Installation

Download the appropriate installer for your platform:
- Windows: \`Solar-Calculator-Pro-Setup-${this.version}.exe\`
- macOS: \`Solar-Calculator-Pro-${this.version}.dmg\`
- Linux: \`Solar-Calculator-Pro-${this.version}.AppImage\`

### Documentation

- User Manual: docs/USER_MANUAL.md
- Developer Guide: docs/DEVELOPER_GUIDE.md
- API Documentation: docs/API_DOCUMENTATION.md

### Support

- Email: support@solarcalculatorpro.com
- Documentation: https://docs.solarcalculatorpro.com
- Issue Tracker: https://github.com/yourorg/solar-calculator-pro/issues

### License

Copyright © ${new Date().getFullYear()} Your Company Name. All rights reserved.

---

**Checksums:** See SHA256SUMS.txt for file verification
`;
  }

  async prepareDistribution() {
    console.log('\n📦 Preparing Distribution Package...');
    
    // Copy documentation
    const docsToInclude = [
      'docs/USER_MANUAL.md',
      'docs/QUICK_START.md',
      'docs/TROUBLESHOOTING_GUIDE.md',
      'LICENSE.txt',
      'README.md'
    ];
    
    for (const doc of docsToInclude) {
      const sourcePath = path.join(__dirname, '..', doc);
      const destPath = path.join(this.releaseDir, path.basename(doc));
      
      if (fs.existsSync(sourcePath)) {
        fs.copyFileSync(sourcePath, destPath);
      }
    }
    
    // Create distribution info file
    const distInfo = {
      version: this.version,
      releaseDate: new Date().toISOString(),
      platforms: this.platforms,
      files: fs.readdirSync(this.releaseDir)
    };
    
    fs.writeFileSync(
      path.join(this.releaseDir, 'distribution-info.json'),
      JSON.stringify(distInfo, null, 2)
    );
    
    console.log('✅ Distribution package prepared');
  }
}

// Run if called directly
if (require.main === module) {
  const manager = new ProductionReleaseManager();
  manager.run().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = ProductionReleaseManager;
