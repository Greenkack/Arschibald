#!/usr/bin/env node

/**
 * Website Update Script
 * Updates website with new release information
 */

const fs = require('fs');
const path = require('path');

class WebsiteUpdater {
  constructor() {
    this.version = require('../package.json').version;
    this.releaseDir = path.join(__dirname, '..', 'release', 'production');
    this.websiteDir = process.env.WEBSITE_DIR || path.join(__dirname, '..', 'website');
  }

  async update() {
    console.log('🌐 Updating Website for Production Release');
    console.log(`📦 Version: ${this.version}`);
    
    try {
      await this.updateHomepage();
      await this.updateDownloadPage();
      await this.updateChangelog();
      await this.updateDocumentation();
      await this.generateSitemap();
      
      console.log('✅ Website updated successfully!');
    } catch (error) {
      console.error('❌ Website update failed:', error.message);
      process.exit(1);
    }
  }

  async updateHomepage() {
    console.log('\n📄 Updating Homepage...');
    
    const homepageData = {
      latestVersion: this.version,
      releaseDate: new Date().toISOString().split('T')[0],
      downloadLinks: {
        windows: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-Setup-${this.version}.exe`,
        macos: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.dmg`,
        linux: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.AppImage`
      },
      features: [
        'Solar System Design & Calculation',
        'Heat Pump Analysis',
        'Dynamic Price Matrix',
        'Professional PDF Reports',
        'CRM Integration',
        'Product Catalog',
        '3D Visualization',
        'Auto-Updates'
      ]
    };
    
    // Write homepage data
    const dataPath = path.join(this.websiteDir, 'data', 'homepage.json');
    fs.mkdirSync(path.dirname(dataPath), { recursive: true });
    fs.writeFileSync(dataPath, JSON.stringify(homepageData, null, 2));
    
    console.log('✅ Homepage updated');
  }

  async updateDownloadPage() {
    console.log('\n💾 Updating Download Page...');
    
    const checksums = this.loadChecksums();
    
    const downloadData = {
      version: this.version,
      releaseDate: new Date().toISOString().split('T')[0],
      platforms: {
        windows: {
          name: 'Windows',
          filename: `Solar-Calculator-Pro-Setup-${this.version}.exe`,
          url: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-Setup-${this.version}.exe`,
          size: this.getFileSize(`Solar-Calculator-Pro-Setup-${this.version}.exe`),
          sha256: checksums[`Solar-Calculator-Pro-Setup-${this.version}.exe`],
          requirements: 'Windows 10 or later (64-bit)',
          icon: 'windows'
        },
        macos: {
          name: 'macOS',
          filename: `Solar-Calculator-Pro-${this.version}.dmg`,
          url: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.dmg`,
          size: this.getFileSize(`Solar-Calculator-Pro-${this.version}.dmg`),
          sha256: checksums[`Solar-Calculator-Pro-${this.version}.dmg`],
          requirements: 'macOS 10.13 (High Sierra) or later',
          icon: 'apple'
        },
        linux: {
          name: 'Linux',
          filename: `Solar-Calculator-Pro-${this.version}.AppImage`,
          url: `https://downloads.solarcalculatorpro.com/v${this.version}/Solar-Calculator-Pro-${this.version}.AppImage`,
          size: this.getFileSize(`Solar-Calculator-Pro-${this.version}.AppImage`),
          sha256: checksums[`Solar-Calculator-Pro-${this.version}.AppImage`],
          requirements: 'Ubuntu 18.04 or later (or equivalent)',
          icon: 'linux'
        }
      },
      releaseNotes: this.loadReleaseNotes()
    };
    
    const dataPath = path.join(this.websiteDir, 'data', 'downloads.json');
    fs.writeFileSync(dataPath, JSON.stringify(downloadData, null, 2));
    
    console.log('✅ Download page updated');
  }

  async updateChangelog() {
    console.log('\n📝 Updating Changelog...');
    
    const changelogPath = path.join(this.websiteDir, 'content', 'changelog.md');
    const releaseNotes = this.loadReleaseNotes();
    
    // Prepend new release to changelog
    let existingChangelog = '';
    if (fs.existsSync(changelogPath)) {
      existingChangelog = fs.readFileSync(changelogPath, 'utf8');
    }
    
    const newChangelog = `${releaseNotes}\n\n---\n\n${existingChangelog}`;
    
    fs.mkdirSync(path.dirname(changelogPath), { recursive: true });
    fs.writeFileSync(changelogPath, newChangelog);
    
    console.log('✅ Changelog updated');
  }

  async updateDocumentation() {
    console.log('\n📚 Updating Documentation...');
    
    // Copy documentation files to website
    const docsToUpdate = [
      { src: 'docs/USER_MANUAL.md', dest: 'content/docs/user-manual.md' },
      { src: 'docs/QUICK_START.md', dest: 'content/docs/quick-start.md' },
      { src: 'docs/TROUBLESHOOTING_GUIDE.md', dest: 'content/docs/troubleshooting.md' },
      { src: 'docs/API_DOCUMENTATION.md', dest: 'content/docs/api.md' },
      { src: 'docs/DEVELOPER_GUIDE.md', dest: 'content/docs/developer-guide.md' }
    ];
    
    for (const doc of docsToUpdate) {
      const sourcePath = path.join(__dirname, '..', doc.src);
      const destPath = path.join(this.websiteDir, doc.dest);
      
      if (fs.existsSync(sourcePath)) {
        fs.mkdirSync(path.dirname(destPath), { recursive: true });
        fs.copyFileSync(sourcePath, destPath);
        console.log(`  ✅ Updated ${doc.dest}`);
      }
    }
    
    console.log('✅ Documentation updated');
  }

  async generateSitemap() {
    console.log('\n🗺️  Generating Sitemap...');
    
    const baseUrl = 'https://solarcalculatorpro.com';
    const pages = [
      { url: '/', priority: 1.0, changefreq: 'weekly' },
      { url: '/download', priority: 0.9, changefreq: 'weekly' },
      { url: '/features', priority: 0.8, changefreq: 'monthly' },
      { url: '/pricing', priority: 0.8, changefreq: 'monthly' },
      { url: '/docs', priority: 0.7, changefreq: 'weekly' },
      { url: '/docs/user-manual', priority: 0.7, changefreq: 'weekly' },
      { url: '/docs/quick-start', priority: 0.7, changefreq: 'weekly' },
      { url: '/docs/api', priority: 0.6, changefreq: 'monthly' },
      { url: '/support', priority: 0.6, changefreq: 'monthly' },
      { url: '/about', priority: 0.5, changefreq: 'monthly' },
      { url: '/changelog', priority: 0.5, changefreq: 'weekly' }
    ];
    
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
    <loc>${baseUrl}${page.url}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;
    
    const sitemapPath = path.join(this.websiteDir, 'public', 'sitemap.xml');
    fs.mkdirSync(path.dirname(sitemapPath), { recursive: true });
    fs.writeFileSync(sitemapPath, sitemap);
    
    console.log('✅ Sitemap generated');
  }

  loadChecksums() {
    const checksumsPath = path.join(this.releaseDir, 'SHA256SUMS.txt');
    const checksums = {};
    
    if (fs.existsSync(checksumsPath)) {
      const content = fs.readFileSync(checksumsPath, 'utf8');
      content.split('\n').forEach(line => {
        const [hash, filename] = line.split('  ');
        if (hash && filename) {
          checksums[filename] = hash;
        }
      });
    }
    
    return checksums;
  }

  loadReleaseNotes() {
    const notesPath = path.join(this.releaseDir, 'RELEASE_NOTES.md');
    if (fs.existsSync(notesPath)) {
      return fs.readFileSync(notesPath, 'utf8');
    }
    return '';
  }

  getFileSize(filename) {
    const filePath = path.join(this.releaseDir, filename);
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
      return `${sizeInMB} MB`;
    }
    return 'N/A';
  }
}

// Run if called directly
if (require.main === module) {
  const updater = new WebsiteUpdater();
  updater.update().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = WebsiteUpdater;
