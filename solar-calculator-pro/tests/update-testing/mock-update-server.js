#!/usr/bin/env node

/**
 * Mock Update Server
 * 
 * A simple HTTP server for testing updates locally.
 * Serves update manifests and installer files.
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class MockUpdateServer {
  constructor(config = {}) {
    this.config = {
      port: config.port || 3000,
      host: config.host || 'localhost',
      releaseDir: config.releaseDir || path.join(__dirname, 'test-data', 'releases'),
      ...config
    };

    this.app = express();
    this.setupRoutes();
  }

  /**
   * Setup Express routes
   */
  setupRoutes() {
    // Enable CORS
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type');
      next();
    });

    // Logging middleware
    this.app.use((req, res, next) => {
      console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
      next();
    });

    // Serve static files from release directory
    this.app.use(express.static(this.config.releaseDir));

    // Windows update manifest
    this.app.get('/latest.yml', (req, res) => {
      this.serveManifest(req, res, 'win');
    });

    // macOS update manifest
    this.app.get('/latest-mac.yml', (req, res) => {
      this.serveManifest(req, res, 'mac');
    });

    // Linux update manifest
    this.app.get('/latest-linux.yml', (req, res) => {
      this.serveManifest(req, res, 'linux');
    });

    // Beta channel manifests
    this.app.get('/beta.yml', (req, res) => {
      this.serveManifest(req, res, 'win', 'beta');
    });

    this.app.get('/beta-mac.yml', (req, res) => {
      this.serveManifest(req, res, 'mac', 'beta');
    });

    this.app.get('/beta-linux.yml', (req, res) => {
      this.serveManifest(req, res, 'linux', 'beta');
    });

    // Alpha channel manifests
    this.app.get('/alpha.yml', (req, res) => {
      this.serveManifest(req, res, 'win', 'alpha');
    });

    this.app.get('/alpha-mac.yml', (req, res) => {
      this.serveManifest(req, res, 'mac', 'alpha');
    });

    this.app.get('/alpha-linux.yml', (req, res) => {
      this.serveManifest(req, res, 'linux', 'alpha');
    });

    // Release notes
    this.app.get('/release-notes/:version', (req, res) => {
      this.serveReleaseNotes(req, res);
    });

    // Download installer
    this.app.get('/download/:filename', (req, res) => {
      this.serveInstaller(req, res);
    });

    // Server info
    this.app.get('/info', (req, res) => {
      res.json({
        name: 'Mock Update Server',
        version: '1.0.0',
        releaseDir: this.config.releaseDir,
        availableVersions: this.getAvailableVersions()
      });
    });

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({ error: 'Not found' });
    });

    // Error handler
    this.app.use((err, req, res, next) => {
      console.error('Server error:', err);
      res.status(500).json({ error: 'Internal server error' });
    });
  }

  /**
   * Serve update manifest
   */
  serveManifest(req, res, platform, channel = 'latest') {
    try {
      const manifestFile = this.getManifestFilename(platform, channel);
      const manifestPath = path.join(this.config.releaseDir, manifestFile);

      if (!fs.existsSync(manifestPath)) {
        // Generate mock manifest
        const manifest = this.generateMockManifest(platform, channel);
        res.type('text/yaml').send(manifest);
        return;
      }

      const manifest = fs.readFileSync(manifestPath, 'utf8');
      res.type('text/yaml').send(manifest);
    } catch (error) {
      console.error('Error serving manifest:', error);
      res.status(500).json({ error: 'Failed to serve manifest' });
    }
  }

  /**
   * Serve release notes
   */
  serveReleaseNotes(req, res) {
    try {
      const { version } = req.params;
      const notesPath = path.join(
        __dirname,
        'test-data',
        'manifests',
        `release-notes-${version}.md`
      );

      if (!fs.existsSync(notesPath)) {
        res.status(404).json({ error: 'Release notes not found' });
        return;
      }

      const notes = fs.readFileSync(notesPath, 'utf8');
      res.type('text/markdown').send(notes);
    } catch (error) {
      console.error('Error serving release notes:', error);
      res.status(500).json({ error: 'Failed to serve release notes' });
    }
  }

  /**
   * Serve installer file
   */
  serveInstaller(req, res) {
    try {
      const { filename } = req.params;
      const filePath = path.join(this.config.releaseDir, filename);

      if (!fs.existsSync(filePath)) {
        res.status(404).json({ error: 'File not found' });
        return;
      }

      // Set appropriate headers
      const stat = fs.statSync(filePath);
      res.setHeader('Content-Length', stat.size);
      res.setHeader('Content-Type', 'application/octet-stream');
      res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);

      // Stream file
      const stream = fs.createReadStream(filePath);
      stream.pipe(res);
    } catch (error) {
      console.error('Error serving installer:', error);
      res.status(500).json({ error: 'Failed to serve installer' });
    }
  }

  /**
   * Generate mock manifest
   */
  generateMockManifest(platform, channel) {
    const version = channel === 'alpha' ? '1.0.3-alpha.1' :
                   channel === 'beta' ? '1.0.2-beta.1' : '1.0.1';

    const releaseDate = new Date().toISOString();
    const filename = this.getInstallerFilename(platform, version);

    return `version: ${version}
releaseDate: ${releaseDate}
files:
  - url: ${filename}
    sha512: ${this.generateMockHash()}
    size: ${this.getMockFileSize(platform)}
path: ${filename}
sha512: ${this.generateMockHash()}
releaseNotesUrl: http://${this.config.host}:${this.config.port}/release-notes/${version}
`;
  }

  /**
   * Get manifest filename
   */
  getManifestFilename(platform, channel) {
    if (channel === 'latest') {
      return platform === 'win' ? 'latest.yml' :
             platform === 'mac' ? 'latest-mac.yml' : 'latest-linux.yml';
    } else {
      return platform === 'win' ? `${channel}.yml` :
             platform === 'mac' ? `${channel}-mac.yml` : `${channel}-linux.yml`;
    }
  }

  /**
   * Get installer filename
   */
  getInstallerFilename(platform, version) {
    if (platform === 'win') {
      return `Solar-Calculator-Pro-Setup-${version}.exe`;
    } else if (platform === 'mac') {
      return `Solar-Calculator-Pro-${version}.dmg`;
    } else {
      return `Solar-Calculator-Pro-${version}.AppImage`;
    }
  }

  /**
   * Generate mock SHA512 hash
   */
  generateMockHash() {
    return crypto.randomBytes(64).toString('hex');
  }

  /**
   * Get mock file size
   */
  getMockFileSize(platform) {
    const sizes = {
      win: 50 * 1024 * 1024,  // 50MB
      mac: 60 * 1024 * 1024,  // 60MB
      linux: 55 * 1024 * 1024 // 55MB
    };
    return sizes[platform] || 50 * 1024 * 1024;
  }

  /**
   * Get available versions
   */
  getAvailableVersions() {
    try {
      if (!fs.existsSync(this.config.releaseDir)) {
        return [];
      }

      const files = fs.readdirSync(this.config.releaseDir);
      const versions = new Set();

      files.forEach(file => {
        const match = file.match(/(\d+\.\d+\.\d+(-[a-z]+\.\d+)?)/);
        if (match) {
          versions.add(match[1]);
        }
      });

      return Array.from(versions).sort();
    } catch (error) {
      console.error('Error getting versions:', error);
      return [];
    }
  }

  /**
   * Start the server
   */
  start() {
    return new Promise((resolve, reject) => {
      try {
        // Ensure release directory exists
        if (!fs.existsSync(this.config.releaseDir)) {
          fs.mkdirSync(this.config.releaseDir, { recursive: true });
        }

        this.server = this.app.listen(this.config.port, this.config.host, () => {
          console.log('\n🚀 Mock Update Server Started');
          console.log('='.repeat(50));
          console.log(`URL: http://${this.config.host}:${this.config.port}`);
          console.log(`Release Directory: ${this.config.releaseDir}`);
          console.log(`Available Versions: ${this.getAvailableVersions().join(', ') || 'None'}`);
          console.log('\nEndpoints:');
          console.log('  GET /latest.yml          - Windows manifest');
          console.log('  GET /latest-mac.yml      - macOS manifest');
          console.log('  GET /latest-linux.yml    - Linux manifest');
          console.log('  GET /beta.yml            - Windows beta manifest');
          console.log('  GET /release-notes/:ver  - Release notes');
          console.log('  GET /download/:file      - Download installer');
          console.log('  GET /info                - Server info');
          console.log('  GET /health              - Health check');
          console.log('\nPress Ctrl+C to stop');
          console.log('='.repeat(50) + '\n');

          resolve();
        });

        this.server.on('error', (error) => {
          if (error.code === 'EADDRINUSE') {
            console.error(`\n❌ Port ${this.config.port} is already in use`);
            console.error('Try a different port: node mock-update-server.js --port 3001\n');
          } else {
            console.error('\n❌ Server error:', error.message);
          }
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Stop the server
   */
  stop() {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          console.log('\n✅ Server stopped');
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  const config = {};

  // Parse command line arguments
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];

    if (key === 'port') {
      config.port = parseInt(value, 10);
    } else if (key === 'host') {
      config.host = value;
    } else if (key === 'dir') {
      config.releaseDir = value;
    }
  }

  const server = new MockUpdateServer(config);

  server.start().catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n\nShutting down...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await server.stop();
    process.exit(0);
  });
}

module.exports = MockUpdateServer;
