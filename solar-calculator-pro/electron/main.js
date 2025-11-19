const { app, BrowserWindow, ipcMain, dialog, session } = require('electron');
const path = require('path');
const BackendManager = require('./backend-manager');
const { createApplicationMenu } = require('./menu');
const { createTray } = require('./tray');
const { setupAutoUpdater } = require('./updater');

let mainWindow;
let backendManager;
let tray;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true,
      webSecurity: true,
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    show: false, // Don't show until ready
  });

  // Set Content Security Policy
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          process.env.NODE_ENV === 'development'
            ? "default-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* ws://localhost:*"
            : "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' http://localhost:8000"
        ]
      }
    });
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window state
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Prevent navigation to external URLs
  mainWindow.webContents.on('will-navigate', (event, url) => {
    const allowedOrigins = ['http://localhost:3000', 'http://localhost:8000'];
    const urlObj = new URL(url);
    if (!allowedOrigins.some(origin => url.startsWith(origin))) {
      event.preventDefault();
    }
  });

  // Prevent opening new windows
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Open external links in default browser
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });

  return mainWindow;
}

// IPC Handlers
function setupIpcHandlers() {
  // File dialogs
  ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'All Files', extensions: ['*'] },
        { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif'] }
      ]
    });
    return result.filePaths[0];
  });

  ipcMain.handle('dialog:saveFile', async (event, data) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: data.defaultPath || 'untitled',
      filters: data.filters || [{ name: 'All Files', extensions: ['*'] }]
    });
    return result.filePath;
  });

  ipcMain.handle('dialog:openDirectory', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    return result.filePaths[0];
  });

  // Backend communication
  ipcMain.handle('backend:getUrl', () => {
    return backendManager ? backendManager.getUrl() : null;
  });

  ipcMain.handle('backend:checkHealth', async () => {
    return backendManager ? await backendManager.checkHealth() : false;
  });

  ipcMain.handle('backend:getStatus', () => {
    return backendManager ? backendManager.getStatus() : null;
  });

  ipcMain.handle('backend:getLogs', (event, count = 100) => {
    return backendManager ? backendManager.getLogs(count) : [];
  });

  ipcMain.handle('backend:restart', async () => {
    if (backendManager) {
      try {
        await backendManager.restart();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
    return { success: false, error: 'Backend manager not initialized' };
  });

  // Window operations
  ipcMain.on('window:minimize', () => {
    if (mainWindow) mainWindow.minimize();
  });

  ipcMain.on('window:maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  ipcMain.on('window:close', () => {
    if (mainWindow) mainWindow.close();
  });

  // App info
  ipcMain.handle('app:getVersion', () => {
    return app.getVersion();
  });

  // Notifications
  ipcMain.on('notification:show', (event, { title, body }) => {
    const { Notification } = require('electron');
    if (Notification.isSupported()) {
      new Notification({ title, body }).show();
    }
  });
}

app.whenReady().then(async () => {
  // Setup IPC handlers
  setupIpcHandlers();

  // Start backend
  backendManager = new BackendManager({
    port: process.env.BACKEND_PORT || 8000,
    maxRetries: 30,
    retryDelay: 1000,
    healthCheckInterval: 10000,
    maxRestartAttempts: 3,
    restartDelay: 5000,
  });

  // Setup backend event handlers
  backendManager.on('started', () => {
    console.log('Backend started successfully');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:started');
    }
  });

  backendManager.on('stopped', ({ code, signal }) => {
    console.log(`Backend stopped (code: ${code}, signal: ${signal})`);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:stopped', { code, signal });
    }
  });

  backendManager.on('unhealthy', () => {
    console.warn('Backend health check failed');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:unhealthy');
    }
  });

  backendManager.on('restarting', () => {
    console.log('Backend is restarting...');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:restarting');
    }
  });

  backendManager.on('failed', (error) => {
    console.error('Backend failed:', error);
    dialog.showErrorBox(
      'Backend Error',
      `The backend server has failed:\n\n${error.message}\n\nPlease restart the application.`
    );
  });

  try {
    await backendManager.start();
  } catch (error) {
    console.error('Failed to start backend:', error);
    dialog.showErrorBox(
      'Backend Startup Failed',
      `Failed to start the application backend:\n\n${error.message}\n\nThe application will now exit.`
    );
    app.quit();
    return;
  }

  // Create window
  createWindow();

  // Create application menu
  createApplicationMenu(mainWindow);

  // Create system tray
  tray = createTray(mainWindow);

  // Setup auto-updater
  setupAutoUpdater(mainWindow);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', async (event) => {
  if (backendManager && backendManager.isRunning) {
    console.log('Cleaning up backend before quit...');
    event.preventDefault();
    
    try {
      await backendManager.cleanup();
      console.log('Backend cleanup completed');
    } catch (error) {
      console.error('Error during backend cleanup:', error);
    }
    
    // Now quit for real
    app.quit();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  dialog.showErrorBox('Application Error', error.message);
});

// Export for testing
module.exports = { createWindow, setupIpcHandlers };
