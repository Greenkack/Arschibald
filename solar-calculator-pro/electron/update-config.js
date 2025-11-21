/**
 * Update Server Configuration
 * 
 * This file contains configuration for the auto-update system.
 * You can configure different update servers for different environments.
 */

const { app } = require('electron');
const path = require('path');

// Environment detection
const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

/**
 * Update server configurations
 */
const updateServers = {
  // GitHub Releases (recommended for open source projects)
  github: {
    provider: 'github',
    owner: 'your-github-username',
    repo: 'solar-calculator-pro',
    releaseType: 'release', // 'release' or 'prerelease'
    private: false, // Set to true if using private repository
    token: process.env.GH_TOKEN // Required for private repos
  },

  // Generic HTTP Server (for self-hosted updates)
  generic: {
    provider: 'generic',
    url: 'https://your-update-server.com/updates',
    channel: 'latest', // 'latest', 'beta', 'alpha'
    useMultipleRangeRequest: true
  },

  // AWS S3 (for cloud-hosted updates)
  s3: {
    provider: 's3',
    bucket: 'your-s3-bucket',
    region: 'us-east-1',
    channel: 'latest',
    path: 'updates'
  },

  // Azure Blob Storage
  azure: {
    provider: 'generic',
    url: 'https://your-storage-account.blob.core.windows.net/updates'
  },

  // Custom server
  custom: {
    provider: 'generic',
    url: process.env.UPDATE_SERVER_URL || 'http://localhost:3000/updates'
  }
};

/**
 * Get active update server configuration
 * @returns {Object} Update server configuration
 */
function getUpdateServerConfig() {
  // In development, you might want to use a local server
  if (isDevelopment) {
    return {
      ...updateServers.custom,
      url: 'http://localhost:3000/updates'
    };
  }

  // In production, use the configured server
  // Default to GitHub releases
  const serverType = process.env.UPDATE_SERVER_TYPE || 'github';
  return updateServers[serverType] || updateServers.github;
}

/**
 * Update channels configuration
 */
const updateChannels = {
  latest: {
    name: 'Stable',
    description: 'Stable releases with full testing',
    checkInterval: 3600000, // 1 hour
    autoDownload: false
  },
  beta: {
    name: 'Beta',
    description: 'Pre-release versions for testing',
    checkInterval: 1800000, // 30 minutes
    autoDownload: false
  },
  alpha: {
    name: 'Alpha',
    description: 'Early development versions',
    checkInterval: 900000, // 15 minutes
    autoDownload: false
  }
};

/**
 * Update manifest structure
 * This is the structure of the latest.yml file that electron-updater expects
 */
const manifestStructure = {
  version: '1.0.0',
  releaseDate: '2024-01-01T00:00:00.000Z',
  files: [
    {
      url: 'Solar-Calculator-Pro-Setup-1.0.0.exe',
      sha512: 'base64-encoded-sha512-hash',
      size: 123456789
    }
  ],
  path: 'Solar-Calculator-Pro-Setup-1.0.0.exe',
  sha512: 'base64-encoded-sha512-hash',
  releaseNotes: 'Release notes in markdown format',
  releaseNotesUrl: 'https://github.com/owner/repo/releases/tag/v1.0.0'
};

/**
 * Code signing configuration
 */
const codeSigningConfig = {
  windows: {
    certificateFile: process.env.WIN_CSC_LINK,
    certificatePassword: process.env.WIN_CSC_KEY_PASSWORD,
    signingHashAlgorithms: ['sha256'],
    rfc3161TimeStampServer: 'http://timestamp.digicert.com'
  },
  mac: {
    identity: process.env.APPLE_ID,
    identityValidation: true,
    provisioningProfile: process.env.PROVISIONING_PROFILE,
    hardenedRuntime: true,
    gatekeeperAssess: false,
    entitlements: path.join(__dirname, '../build/entitlements.mac.plist'),
    entitlementsInherit: path.join(__dirname, '../build/entitlements.mac.plist')
  }
};

/**
 * Update preferences defaults
 */
const defaultPreferences = {
  autoDownload: false,
  autoInstallOnAppQuit: true,
  checkOnStartup: true,
  checkInterval: 3600000, // 1 hour
  updateChannel: 'latest',
  skipVersion: null,
  notifyOnNoUpdate: false
};

/**
 * Validate update server configuration
 * @param {Object} config - Update server configuration
 * @returns {boolean} True if valid
 */
function validateConfig(config) {
  if (!config || !config.provider) {
    return false;
  }

  switch (config.provider) {
    case 'github':
      return !!(config.owner && config.repo);
    case 'generic':
      return !!config.url;
    case 's3':
      return !!(config.bucket && config.region);
    default:
      return false;
  }
}

/**
 * Get update URL for current platform
 * @param {Object} config - Update server configuration
 * @returns {string} Update URL
 */
function getUpdateUrl(config) {
  const platform = process.platform;
  const arch = process.arch;
  const version = app.getVersion();

  if (config.provider === 'github') {
    return `https://github.com/${config.owner}/${config.repo}/releases`;
  }

  if (config.provider === 'generic') {
    return `${config.url}/${platform}/${arch}`;
  }

  if (config.provider === 's3') {
    return `https://${config.bucket}.s3.${config.region}.amazonaws.com/${config.path || 'updates'}`;
  }

  return config.url;
}

module.exports = {
  getUpdateServerConfig,
  updateChannels,
  manifestStructure,
  codeSigningConfig,
  defaultPreferences,
  validateConfig,
  getUpdateUrl,
  isDevelopment,
  isProduction
};
