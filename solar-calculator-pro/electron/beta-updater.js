/**
 * Beta Update Manager
 * 
 * Manages updates for beta builds with beta-specific behavior
 */

const { autoUpdater } = require('electron-updater');
const { dialog, BrowserWindow } = require('electron');
const log = require('electron-log');
const betaConfig = require('../build/beta-config');

class BetaUpdateManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.updateCheckTimer = null;
    this.setupAutoUpdater();
    this.setupEventHandlers();
  }

  /**
   * Setup auto-updater configuration
   */
  setupAutoUpdater() {
    // Configure logger
    autoUpdater.logger = log;
    autoUpdater.logger.transports.file.level = 'info';
    
    // Beta-specific configuration
    autoUpdater.channel = betaConfig.betaChannel;
    autoUpdater.autoDownload = betaConfig.autoDownload;
    autoUpdater.autoInstallOnAppQuit = betaConfig.autoInstallOnAppQuit;
    
    // Allow pre-release versions
    autoUpdater.allowPrerelease = true;
    
    // Set update server
    if (betaConfig.updateServer) {
      autoUpdater.setFeedURL({
        provider: 'generic',
        url: betaConfig.updateServer,
        channel: betaConfig.betaChannel,
      });
    }
    
    log.info('Beta updater configured:', {
      channel: autoUpdater.channel,
      feedURL: betaConfig.updateServer,
    });
  }

  /**
   * Setup event handlers
   */
  setupEventHandlers() {
    // Checking for update
    autoUpdater.on('checking-for-update', () => {
      log.info('Checking for beta updates...');
      this.sendStatusToWindow('checking-for-update');
    });

    // Update available
    autoUpdater.on('update-available', (info) => {
      log.info('Beta update available:', info);
      this.sendStatusToWindow('update-available', info);
      
      // Show notification
      this.showUpdateAvailableDialog(info);
    });

    // Update not available
    autoUpdater.on('update-not-available', (info) => {
      log.info('Beta update not available:', info);
      this.sendStatusToWindow('update-not-available', info);
    });

    // Download progress
    autoUpdater.on('download-progress', (progressObj) => {
      const message = `Download speed: ${progressObj.bytesPerSecond} - Downloaded ${progressObj.percent}% (${progressObj.transferred}/${progressObj.total})`;
      log.info(message);
      this.sendStatusToWindow('download-progress', progressObj);
    });

    // Update downloaded
    autoUpdater.on('update-downloaded', (info) => {
      log.info('Beta update downloaded:', info);
      this.sendStatusToWindow('update-downloaded', info);
      
      // Show install dialog
      this.showUpdateReadyDialog(info);
    });

    // Error
    autoUpdater.on('error', (err) => {
      log.error('Beta update error:', err);
      this.sendStatusToWindow('update-error', { message: err.message });
      
      // Show error dialog
      this.showUpdateErrorDialog(err);
    });
  }

  /**
   * Send status to renderer window
   */
  sendStatusToWindow(event, data = {}) {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('beta-update-status', {
        event,
        data,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * Show update available dialog
   */
  showUpdateAvailableDialog(info) {
    const version = info.version;
    const releaseNotes = info.releaseNotes || 'No release notes available';
    
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Beta Update Available',
      message: `A new beta version ${version} is available!`,
      detail: `Current version: ${require('../package.json').version}\n\nRelease Notes:\n${releaseNotes}\n\nThe update will be downloaded automatically.`,
      buttons: ['OK', 'View Release Notes'],
      defaultId: 0,
    }).then((result) => {
      if (result.response === 1) {
        // Open release notes in browser
        require('electron').shell.openExternal(
          `https://docs.yourcompany.com/beta/releases/${version}`
        );
      }
    });
  }

  /**
   * Show update ready dialog
   */
  showUpdateReadyDialog(info) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Beta Update Ready',
      message: `Beta version ${info.version} has been downloaded and is ready to install.`,
      detail: 'The application will restart to install the update.',
      buttons: ['Restart Now', 'Later'],
      defaultId: 0,
    }).then((result) => {
      if (result.response === 0) {
        // Quit and install
        setImmediate(() => autoUpdater.quitAndInstall());
      }
    });
  }

  /**
   * Show update error dialog
   */
  showUpdateErrorDialog(err) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'error',
      title: 'Beta Update Error',
      message: 'Failed to check for updates',
      detail: `Error: ${err.message}\n\nPlease try again later or contact support if the problem persists.`,
      buttons: ['OK'],
    });
  }

  /**
   * Check for updates manually
   */
  checkForUpdates() {
    log.info('Manual beta update check triggered');
    autoUpdater.checkForUpdates();
  }

  /**
   * Start automatic update checks
   */
  startAutoUpdateChecks() {
    // Check immediately
    this.checkForUpdates();
    
    // Schedule periodic checks
    this.updateCheckTimer = setInterval(() => {
      this.checkForUpdates();
    }, betaConfig.updateCheckInterval);
    
    log.info('Automatic beta update checks started');
  }

  /**
   * Stop automatic update checks
   */
  stopAutoUpdateChecks() {
    if (this.updateCheckTimer) {
      clearInterval(this.updateCheckTimer);
      this.updateCheckTimer = null;
      log.info('Automatic beta update checks stopped');
    }
  }

  /**
   * Download update manually
   */
  downloadUpdate() {
    log.info('Manual beta update download triggered');
    autoUpdater.downloadUpdate();
  }

  /**
   * Quit and install update
   */
  quitAndInstall() {
    log.info('Quitting and installing beta update');
    autoUpdater.quitAndInstall();
  }

  /**
   * Get current version
   */
  getCurrentVersion() {
    return require('../package.json').version;
  }

  /**
   * Check if beta has expired
   */
  checkBetaExpiration() {
    if (!betaConfig.expiration.enabled) {
      return { expired: false };
    }
    
    const expiryDate = betaConfig.expiration.expiryDate;
    if (!expiryDate) {
      return { expired: false };
    }
    
    const now = new Date();
    const expiry = new Date(expiryDate);
    const daysUntilExpiry = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiry < 0) {
      // Beta has expired
      return {
        expired: true,
        daysOverdue: Math.abs(daysUntilExpiry),
      };
    } else if (daysUntilExpiry <= betaConfig.expiration.warningDays) {
      // Show warning
      return {
        expired: false,
        warning: true,
        daysRemaining: daysUntilExpiry,
      };
    }
    
    return {
      expired: false,
      daysRemaining: daysUntilExpiry,
    };
  }

  /**
   * Show beta expiration warning
   */
  showBetaExpirationWarning(daysRemaining) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'warning',
      title: 'Beta Version Expiring Soon',
      message: `This beta version will expire in ${daysRemaining} day(s).`,
      detail: 'Please check for updates to continue using the application.',
      buttons: ['Check for Updates', 'Remind Me Later'],
      defaultId: 0,
    }).then((result) => {
      if (result.response === 0) {
        this.checkForUpdates();
      }
    });
  }

  /**
   * Show beta expired dialog
   */
  showBetaExpiredDialog(daysOverdue) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'error',
      title: 'Beta Version Expired',
      message: 'This beta version has expired.',
      detail: `This beta expired ${daysOverdue} day(s) ago. Please update to the latest version to continue using the application.`,
      buttons: ['Check for Updates', 'Exit'],
      defaultId: 0,
    }).then((result) => {
      if (result.response === 0) {
        this.checkForUpdates();
      } else {
        require('electron').app.quit();
      }
    });
  }
}

module.exports = BetaUpdateManager;
