const { autoUpdater } = require('electron-updater');
const { dialog, ipcMain } = require('electron');
const log = require('electron-log');

// Configure logging
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';

let mainWindow = null;
let updateCheckInProgress = false;

function setupAutoUpdater(window) {
  mainWindow = window;

  // Configure auto-updater
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;

  // Check for updates on startup (after 10 seconds)
  setTimeout(() => {
    checkForUpdates(false);
  }, 10000);

  // Setup event handlers
  setupUpdateHandlers();

  // Setup IPC handlers
  setupIpcHandlers();
}

function setupUpdateHandlers() {
  // Update available
  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info);
    
    if (mainWindow) {
      mainWindow.webContents.send('updater:available', {
        version: info.version,
        releaseDate: info.releaseDate,
        releaseNotes: info.releaseNotes
      });
    }

    // Show dialog
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `A new version (${info.version}) is available!`,
      detail: 'Would you like to download it now? The update will be installed when you close the application.',
      buttons: ['Download', 'Later'],
      defaultId: 0,
      cancelId: 1
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.downloadUpdate();
        
        // Show download progress
        if (mainWindow) {
          mainWindow.webContents.send('updater:downloading');
        }
      }
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
    return require('electron').app.getVersion();
  });
}

async function checkForUpdates(manual = false) {
  if (manual) {
    updateCheckInProgress = true;
  }

  try {
    const result = await autoUpdater.checkForUpdates();
    return {
      success: true,
      updateInfo: result.updateInfo
    };
  } catch (error) {
    log.error('Check for updates error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

function setUpdateFeed(url) {
  autoUpdater.setFeedURL({
    provider: 'generic',
    url: url
  });
}

module.exports = {
  setupAutoUpdater,
  checkForUpdates,
  setUpdateFeed
};
