#!/usr/bin/env node

/**
 * Upload to Distribution Channels
 * Handles uploading releases to various distribution platforms
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class DistributionUploader {
  constructor() {
    this.version = require('../package.json').version;
    this.releaseDir = path.join(__dirname, '..', 'release', 'production');
    this.channels = {
      github: process.env.GITHUB_TOKEN,
      website: process.env.WEBSITE_DEPLOY_KEY,
      updateServer: process.env.UPDATE_SERVER_URL
    };
  }

  async upload() {
    console.log('📤 Starting Distribution Upload');
    console.log(`📦 Version: ${this.version}`);
    
    try {
      await this.validateChannels();
      await this.uploadToGitHub();
      await this.uploadToWebsite();
      await this.uploadToUpdateServer();
      await this.notifyChannels();
      
      console.log('✅ Distribution upload complete!');
    } catch (error) {
      console.error('❌ Upload failed:', error.message);
      process.exit(1);
    }
  }

  async validateChannels() {
    console.log('\n🔍 Validating Distribution Channels...');
    
    if (!this.channels.github) {
      console.warn('⚠️  GitHub token not found. Skipping GitHub release.');
    }
    
    if (!this.channels.website) {
      console.warn('⚠️  Website deploy key not found. Skipping website upload.');
    }
    
    if (!this.channels.updateServer) {
      console.warn('⚠️  Update server URL not found. Skipping update server.');
    }
    
    console.log('✅ Channels validated');
  }

  async uploadToGitHub() {
    if (!this.channels.github) return;
    
    console.log('\n🐙 Uploading to GitHub Releases...');
    
    try {
      // Create git tag
      execSync(`git tag -a v${this.version} -m "Release v${this.version}"`);
      execSync('git push --tags');
      
      // Create GitHub release using gh CLI
      const releaseNotes = fs.readFileSync(
        path.join(this.releaseDir, 'RELEASE_NOTES.md'),
        'utf8'
      );
      
      execSync(`gh release create v${this.version} --title "v${this.version}" --notes "${releaseNotes}"`);
      
      // Upload assets
      const files = fs.readdirSync(this.releaseDir);
      for (const file of files) {
        if (file.endsWith('.exe') || file.endsWith('.dmg') || file.endsWith('.AppImage')) {
          const filePath = path.join(this.releaseDir, file);
          execSync(`gh release upload v${this.version} "${filePath}"`);
          console.log(`  ✅ Uploaded ${file}`);
        }
      }
      
      // Upload checksums
      execSync(`gh release upload v${this.version} "${path.join(this.releaseDir, 'SHA256SUMS.txt')}"`);
      
      console.log('✅ GitHub release complete');
    } catch (error) {
      console.error('❌ GitHub upload failed:', error.message);
    }
  }

  async uploadToWebsite() {
    if (!this.channels.website) return;
    
    console.log('\n🌐 Uploading to Website...');
    
    try {
      // This would typically use SCP, SFTP, or cloud storage API
      // Example using rsync:
      const websiteDir = process.env.WEBSITE_DEPLOY_PATH || '/var/www/downloads';
      
      execSync(`rsync -avz ${this.releaseDir}/ ${websiteDir}/v${this.version}/`, {
        stdio: 'inherit'
      });
      
      // Update latest version pointer
      const latestInfo = {
        version: this.version,
        releaseDate: new Date().toISOString(),
        downloadUrls: {
          windows: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-Setup-${this.version}.exe`,
          macos: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.dmg`,
          linux: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.AppImage`
        }
      };
      
      fs.writeFileSync(
        path.join(this.releaseDir, 'latest.json'),
        JSON.stringify(latestInfo, null, 2)
      );
      
      console.log('✅ Website upload complete');
    } catch (error) {
      console.error('❌ Website upload failed:', error.message);
    }
  }

  async uploadToUpdateServer() {
    if (!this.channels.updateServer) return;
    
    console.log('\n🔄 Uploading to Update Server...');
    
    try {
      const updateManifest = {
        version: this.version,
        releaseDate: new Date().toISOString(),
        files: {
          windows: {
            url: `${this.channels.updateServer}/v${this.version}/Solar-Calculator-Pro-Setup-${this.version}.exe`,
            sha256: this.getChecksum(`Solar-Calculator-Pro-Setup-${this.version}.exe`)
          },
          macos: {
            url: `${this.channels.updateServer}/v${this.version}/Solar-Calculator-Pro-${this.version}.dmg`,
            sha256: this.getChecksum(`Solar-Calculator-Pro-${this.version}.dmg`)
          },
          linux: {
            url: `${this.channels.updateServer}/v${this.version}/Solar-Calculator-Pro-${this.version}.AppImage`,
            sha256: this.getChecksum(`Solar-Calculator-Pro-${this.version}.AppImage`)
          }
        },
        releaseNotes: fs.readFileSync(
          path.join(this.releaseDir, 'RELEASE_NOTES.md'),
          'utf8'
        )
      };
      
      // Upload manifest
      fs.writeFileSync(
        path.join(this.releaseDir, 'update-manifest.json'),
        JSON.stringify(updateManifest, null, 2)
      );
      
      console.log('✅ Update server upload complete');
    } catch (error) {
      console.error('❌ Update server upload failed:', error.message);
    }
  }

  getChecksum(filename) {
    const checksumsPath = path.join(this.releaseDir, 'SHA256SUMS.txt');
    const checksums = fs.readFileSync(checksumsPath, 'utf8');
    const line = checksums.split('\n').find(l => l.includes(filename));
    return line ? line.split(' ')[0] : '';
  }

  async notifyChannels() {
    console.log('\n📢 Sending Release Notifications...');
    
    // This would typically send notifications via:
    // - Email to subscribers
    // - Slack/Discord webhooks
    // - Social media APIs
    // - RSS feed update
    
    console.log('  ℹ️  Manual notification required');
    console.log('  - Update website announcement');
    console.log('  - Send email to users');
    console.log('  - Post on social media');
    console.log('  - Update documentation site');
  }
}

// Run if called directly
if (require.main === module) {
  const uploader = new DistributionUploader();
  uploader.upload().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = DistributionUploader;
