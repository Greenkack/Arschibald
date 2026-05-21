const { autoUpdater } = require('electron-updater');
const { dialog, ipcMain, app } = require('electron');
const log = require('electron-log');
const Store = require('electron-store');

// Configure logging
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';
log.transports.file.level = 'info';

// Store for update preferences
const store = new Store({
  name: 'update-preferences',
  defaults: {
    autoDownload: false,
    autoInstallOnAppQuit: true,
    checkOnStartup: true,
    checkInterval: 3600000, // 1 hour in milliseconds
    lastCheckTime: null,
    updateChannel: 'latest', // 'latest', 'beta', 'alpha'
    skipVersion: null
  }
});

let mainWindow = null;
let updateCheckInProgress = false;
let updateCheckInterval = null;

/**
 * Setup auto-updater with configuration
 * @param {BrowserWindow} window - Main window instance
 * @param {Object} config - Optional configuration override
 */
function setupAutoUpdater(window, config = {}) {
  mainWindow = window;

  // Load preferences
  const prefs = {
    autoDownload: store.get('autoDownload'),
    autoInstallOnAppQuit: store.get('autoInstallOnAppQuit'),
    checkOnStartup: store.get('checkOnStartup'),
    checkInterval: store.get('checkInterval'),
    updateChannel: store.get('updateChannel'),
    ...config
  };

  // Configure auto-updater
  autoUpdater.autoDownload = prefs.autoDownload;
  autoUpdater.autoInstallOnAppQuit = prefs.autoInstallOnAppQuit;
  autoUpdater.allowPrerelease = prefs.updateChannel !== 'latest';
  autoUpdater.allowDowngrade = false;

  // Set update channel
  if (prefs.updateChannel === 'beta') {
    autoUpdater.channel = 'beta';
  } else if (prefs.updateChannel === 'alpha') {
    autoUpdater.channel = 'alpha';
  }

  log.info('Auto-updater configured:', {
    version: app.getVersion(),
    channel: prefs.updateChannel,
    autoDownload: prefs.autoDownload,
    autoInstallOnAppQuit: prefs.autoInstallOnAppQuit
  });

  // Check for updates on startup (after 10 seconds)
  if (prefs.checkOnStartup) {
    setTimeout(() => {
      checkForUpdates(false);
    }, 10000);
  }

  // Setup periodic update checks
  if (prefs.checkInterval > 0) {
    updateCheckInterval = setInterval(() => {
      checkForUpdates(false);
    }, prefs.checkInterval);
  }

  // Setup event handlers
  setupUpdateHandlers();

  // Setup IPC handlers
  setupIpcHandlers();
}

function setupUpdateHandlers() {
  // Update available
  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info);
    
    // Check if this version should be skipped
    const skipVersion = store.get('skipVersion');
    if (skipVersion === info.version) {
      log.info(`Skipping version ${info.version} as per user preference`);
      return;
    }

    // Update last check time
    store.set('lastCheckTime', new Date().toISOString());
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:available', {
        version: info.version,
        releaseDate: info.releaseDate,
        releaseNotes: info.releaseNotes,
        currentVersion: app.getVersion(),
        files: info.files,
        path: info.path,
        sha512: info.sha512,
        releaseNotesUrl: info.releaseNotesUrl
      });
    }

    // Auto-download if enabled
    if (autoUpdater.autoDownload) {
      log.info('Auto-downloading update...');
      autoUpdater.downloadUpdate();
      
      if (mainWindow) {
        mainWindow.webContents.send('updater:downloading');
      }
      return;
    }

    // Show dialog for manual download
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `A new version (${info.version}) is available!`,
      detail: `Current version: ${app.getVersion()}\nNew version: ${info.version}\n\nWould you like to download it now? The update will be installed when you close the application.`,
      buttons: ['Download', 'Skip This Version', 'Remind Me Later'],
      defaultId: 0,
      cancelId: 2,
      checkboxLabel: 'Automatically download future updates',
      checkboxChecked: false
    }).then((result) => {
      // Save auto-download preference if checkbox was checked
      if (result.checkboxChecked) {
        store.set('autoDownload', true);
        autoUpdater.autoDownload = true;
      }

      if (result.response === 0) {
        // Download
        autoUpdater.downloadUpdate();
        
        if (mainWindow) {
          mainWindow.webContents.send('updater:downloading');
        }
      } else if (result.response === 1) {
        // Skip this version
        store.set('skipVersion', info.version);
        log.info(`User chose to skip version ${info.version}`);
      }
      // Response 2 is "Remind Me Later" - do nothing
    });
  });

  // No update available
  autoUpdater.on('update-not-available', (info) => {
    log.info('Update not available:', info);
    
    if (updateCheckInProgress) {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'No Updates',
        message: 'You are running the latest version.',
        buttons: ['OK']
      });
      updateCheckInProgress = false;
    }
  });

  // Download progress
  autoUpdater.on('download-progress', (progressObj) => {
    const message = `Download speed: ${progressObj.bytesPerSecond} - Downloaded ${progressObj.percent}%`;
    log.info(message);
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:progress', {
        percent: progressObj.percent,
        transferred: progressObj.transferred,
        total: progressObj.total,
        bytesPerSecond: progressObj.bytesPerSecond
      });
    }
  });

  // Update downloaded
  autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info);
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:downloaded', {
        version: info.version,
        releaseNotes: info.releaseNotes
      });
    }

    // Show dialog
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update downloaded successfully!',
      detail: 'The application will restart to install the update.',
      buttons: ['Restart Now', 'Later'],
      defaultId: 0,
      cancelId: 1
    }).then((result) => {
      if (result.response === 0) {
        // Quit and install
        setImmediate(() => autoUpdater.quitAndInstall());
      }
    });
  });

  // Error handling
  autoUpdater.on('error', (error) => {
    log.error('Update error:', error);
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:error', {
        message: error.message
      });
    }

    if (updateCheckInProgress) {
      dialog.showErrorBox(
        'Update Error',
        'An error occurred while checking for updates. Please try again later.'
      );
      updateCheckInProgress = false;
    }
  });

  // Checking for update
  autoUpdater.on('checking-for-update', () => {
    log.info('Checking for updates...');
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:checking');
    }
  });
}

function setupIpcHandlers() {
  // Manual update check
  ipcMain.handle('updater:check', async () => {
    return checkForUpdates(true);
  });

  // Download update
  ipcMain.handle('updater:download', async () => {
    try {
      await autoUpdater.downloadUpdate();
      return { success: true };
    } catch (error) {
      log.error('Download error:', error);
      return { success: false, error: error.message };
    }
  });

  // Install update
  ipcMain.handle('updater:install', () => {
    autoUpdater.quitAndInstall();
  });

  // Get current version
  ipcMain.handle('updater:version', () => {
    return app.getVersion();
  });

  // Get update info
  ipcMain.handle('updater:info', () => {
    return {
      currentVersion: app.getVersion(),
      channel: store.get('updateChannel'),
      autoDownload: store.get('autoDownload'),
      autoInstallOnAppQuit: store.get('autoInstallOnAppQuit'),
      checkOnStartup: store.get('checkOnStartup'),
      checkInterval: store.get('checkInterval'),
      lastCheckTime: store.get('lastCheckTime'),
      skipVersion: store.get('skipVersion')
    };
  });

  // Update preferences
  ipcMain.handle('updater:setPreferences', (event, preferences) => {
    try {
      if (preferences.autoDownload !== undefined) {
        store.set('autoDownload', preferences.autoDownload);
        autoUpdater.autoDownload = preferences.autoDownload;
      }
      
      if (preferences.autoInstallOnAppQuit !== undefined) {
        store.set('autoInstallOnAppQuit', preferences.autoInstallOnAppQuit);
        autoUpdater.autoInstallOnAppQuit = preferences.autoInstallOnAppQuit;
      }
      
      if (preferences.checkOnStartup !== undefined) {
        store.set('checkOnStartup', preferences.checkOnStartup);
      }
      
      if (preferences.checkInterval !== undefined) {
        store.set('checkInterval', preferences.checkInterval);
        
        // Restart interval timer
        if (updateCheckInterval) {
          clearInterval(updateCheckInterval);
        }
        
        if (preferences.checkInterval > 0) {
          updateCheckInterval = setInterval(() => {
            checkForUpdates(false);
          }, preferences.checkInterval);
        }
      }
      
      if (preferences.updateChannel !== undefined) {
        store.set('updateChannel', preferences.updateChannel);
        autoUpdater.allowPrerelease = preferences.updateChannel !== 'latest';
        
        if (preferences.updateChannel === 'beta') {
          autoUpdater.channel = 'beta';
        } else if (preferences.updateChannel === 'alpha') {
          autoUpdater.channel = 'alpha';
        } else {
          autoUpdater.channel = 'latest';
        }
      }
      
      if (preferences.skipVersion !== undefined) {
        store.set('skipVersion', preferences.skipVersion);
      }
      
      log.info('Update preferences saved:', preferences);
      return { success: true };
    } catch (error) {
      log.error('Error saving preferences:', error);
      return { success: false, error: error.message };
    }
  });

  // Clear skip version
  ipcMain.handle('updater:clearSkipVersion', () => {
    store.set('skipVersion', null);
    return { success: true };
  });

  // Get release notes
  ipcMain.handle('updater:releaseNotes', async (event, version) => {
    try {
      // This would fetch release notes from GitHub or your update server
      // For now, return a placeholder
      return {
        success: true,
        notes: `Release notes for version ${version} would be fetched from the update server.`
      };
    } catch (error) {
      log.error('Error fetching release notes:', error);
      return { success: false, error: error.message };
    }
  });
}

async function checkForUpdates(manual = false) {
  if (manual) {
    updateCheckInProgress = true;
  }

  try {
    log.info('Checking for updates...', {
      manual,
      currentVersion: app.getVersion(),
      channel: store.get('updateChannel')
    });

    const result = await autoUpdater.checkForUpdates();
    
    // Update last check time
    store.set('lastCheckTime', new Date().toISOString());
    
    return {
      success: true,
      updateInfo: result ? result.updateInfo : null,
      currentVersion: app.getVersion()
    };
  } catch (error) {
    log.error('Check for updates error:', error);
    
    if (manual && mainWindow) {
      dialog.showErrorBox(
        'Update Check Failed',
        `Failed to check for updates: ${error.message}\n\nPlease check your internet connection and try again.`
      );
    }
    
    return {
      success: false,
      error: error.message
    };
  } finally {
    if (manual) {
      updateCheckInProgress = false;
    }
  }
}

/**
 * Set custom update feed URL
 * @param {string} url - Update server URL
 * @param {string} provider - Provider type ('github', 'generic', 's3', etc.)
 */
function setUpdateFeed(url, provider = 'generic') {
  try {
    if (provider === 'github') {
      // GitHub releases
      const [owner, repo] = url.split('/').slice(-2);
      autoUpdater.setFeedURL({
        provider: 'github',
        owner,
        repo,
        releaseType: store.get('updateChannel') === 'latest' ? 'release' : 'prerelease'
      });
    } else if (provider === 'generic') {
      // Generic HTTP server
      autoUpdater.setFeedURL({
        provider: 'generic',
        url: url,
        channel: store.get('updateChannel')
      });
    } else if (provider === 's3') {
      // AWS S3
      autoUpdater.setFeedURL({
        provider: 's3',
        bucket: url,
        region: 'us-east-1', // Can be configured
        channel: store.get('updateChannel')
      });
    }
    
    log.info('Update feed configured:', { url, provider });
    return { success: true };
  } catch (error) {
    log.error('Error setting update feed:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get update manifest from server
 * @returns {Promise<Object>} Update manifest
 */
async function getUpdateManifest() {
  try {
    const feedURL = autoUpdater.getFeedURL();
    log.info('Fetching update manifest from:', feedURL);
    
    // This would fetch the latest.yml or latest-mac.yml file
    // For now, return current configuration
    return {
      success: true,
      manifest: {
        version: app.getVersion(),
        releaseDate: new Date().toISOString(),
        channel: store.get('updateChannel'),
        feedURL
      }
    };
  } catch (error) {
    log.error('Error fetching update manifest:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Cancel ongoing download
 */
function cancelDownload() {
  try {
    // electron-updater doesn't have a direct cancel method
    // We can only prevent installation
    log.info('Download cancellation requested');
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:cancelled');
    }
    
    return { success: true };
  } catch (error) {
    log.error('Error cancelling download:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Cleanup on app quit
 */
function cleanup() {
  if (updateCheckInterval) {
    clearInterval(updateCheckInterval);
    updateCheckInterval = null;
  }
  log.info('Updater cleanup completed');
}

// Cleanup on app quit
app.on('before-quit', () => {
  cleanup();
});

module.exports = {
  setupAutoUpdater,
  checkForUpdates,
  setUpdateFeed,
  getUpdateManifest,
  cancelDownload,
  cleanup
};
