const { app, BrowserWindow, ipcMain, dialog, session } = require('electron');
const path = require('path');
const BackendManager = require('./backend-manager');
const { createApplicationMenu, setupContextMenu, updateMenu, getKeyboardShortcuts, menuState } = require('./menu');
const { 
  createTray, 
  updateTrayMenu, 
  showTrayNotification, 
  flashTrayIcon, 
  updateTrayIcon,
  addRecentProject: addTrayRecentProject,
  clearRecentProjects: clearTrayRecentProjects,
  getTrayPreferences,
  updateTrayPreferences
} = require('./tray');
const { setupAutoUpdater } = require('./updater');
const NotificationManager = require('./notifications');
const windowManager = require('./window-manager');
const deepLinkManager = require('./deep-link');
const { getPerformanceManager } = require('./performance-manager');
const { getCleanupManager } = require('./resource-cleanup');

let mainWindow;
let backendManager;
let tray;
let notificationManager;
let performanceManager;
let cleanupManager;

function createWindow() {
  // Create main window using window manager
  mainWindow = windowManager.createWindow({
    id: 'main',
    type: 'main',
    rememberState: true,
    browserWindowOptions: {
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      icon: path.join(__dirname, '../assets/icon.png'),
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        sandbox: true,
        webSecurity: true,
      }
    },
    url: process.env.NODE_ENV === 'development' 
      ? 'http://localhost:3000' 
      : `file://${path.join(__dirname, '../frontend/dist/index.html')}`
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

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Handle window state
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle minimize to tray
  mainWindow.on('minimize', (event) => {
    // Handled by tray.js
  });

  // Handle close to tray
  mainWindow.on('close', (event) => {
    // Handled by tray.js
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
  
  // Single file selection
  ipcMain.handle('dialog:openFile', async (event, options = {}) => {
    const dialogOptions = {
      properties: ['openFile'],
      title: options.title || 'Select File',
      buttonLabel: options.buttonLabel || 'Select',
      filters: options.filters || [
        { name: 'All Files', extensions: ['*'] },
        { name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] },
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'] },
        { name: 'Documents', extensions: ['doc', 'docx', 'txt', 'rtf'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'XML Files', extensions: ['xml'] }
      ]
    };

    if (options.defaultPath) {
      dialogOptions.defaultPath = options.defaultPath;
    }

    const result = await dialog.showOpenDialog(mainWindow, dialogOptions);
    
    if (result.canceled) {
      return { canceled: true, filePath: null };
    }
    
    return { 
      canceled: false, 
      filePath: result.filePaths[0],
      fileName: path.basename(result.filePaths[0])
    };
  });

  // Multiple file selection
  ipcMain.handle('dialog:openFiles', async (event, options = {}) => {
    const dialogOptions = {
      properties: ['openFile', 'multiSelections'],
      title: options.title || 'Select Files',
      buttonLabel: options.buttonLabel || 'Select',
      filters: options.filters || [
        { name: 'All Files', extensions: ['*'] },
        { name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] },
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'] },
        { name: 'Documents', extensions: ['doc', 'docx', 'txt', 'rtf'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'XML Files', extensions: ['xml'] }
      ]
    };

    if (options.defaultPath) {
      dialogOptions.defaultPath = options.defaultPath;
    }

    const result = await dialog.showOpenDialog(mainWindow, dialogOptions);
    
    if (result.canceled) {
      return { canceled: true, filePaths: [] };
    }
    
    return { 
      canceled: false, 
      filePaths: result.filePaths,
      fileNames: result.filePaths.map(fp => path.basename(fp)),
      count: result.filePaths.length
    };
  });

  // Save file dialog
  ipcMain.handle('dialog:saveFile', async (event, options = {}) => {
    const dialogOptions = {
      title: options.title || 'Save File',
      buttonLabel: options.buttonLabel || 'Save',
      defaultPath: options.defaultPath || 'untitled',
      filters: options.filters || [
        { name: 'All Files', extensions: ['*'] }
      ]
    };

    if (options.properties) {
      dialogOptions.properties = options.properties;
    }

    const result = await dialog.showSaveDialog(mainWindow, dialogOptions);
    
    if (result.canceled) {
      return { canceled: true, filePath: null };
    }
    
    return { 
      canceled: false, 
      filePath: result.filePath,
      fileName: path.basename(result.filePath)
    };
  });

  // Directory selection
  ipcMain.handle('dialog:openDirectory', async (event, options = {}) => {
    const dialogOptions = {
      properties: ['openDirectory'],
      title: options.title || 'Select Directory',
      buttonLabel: options.buttonLabel || 'Select'
    };

    if (options.defaultPath) {
      dialogOptions.defaultPath = options.defaultPath;
    }

    if (options.createDirectory !== false) {
      dialogOptions.properties.push('createDirectory');
    }

    const result = await dialog.showOpenDialog(mainWindow, dialogOptions);
    
    if (result.canceled) {
      return { canceled: true, directoryPath: null };
    }
    
    return { 
      canceled: false, 
      directoryPath: result.filePaths[0],
      directoryName: path.basename(result.filePaths[0])
    };
  });

  // Specialized file type dialogs
  ipcMain.handle('dialog:openExcelFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:openFile', event, {
      ...options,
      title: options.title || 'Select Excel File',
      filters: [
        { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:openPDFFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:openFile', event, {
      ...options,
      title: options.title || 'Select PDF File',
      filters: [
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:openImageFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:openFile', event, {
      ...options,
      title: options.title || 'Select Image File',
      filters: [
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'] },
        { name: 'PNG Images', extensions: ['png'] },
        { name: 'JPEG Images', extensions: ['jpg', 'jpeg'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:openImageFiles', async (event, options = {}) => {
    return ipcMain.invoke('dialog:openFiles', event, {
      ...options,
      title: options.title || 'Select Image Files',
      filters: [
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'] },
        { name: 'PNG Images', extensions: ['png'] },
        { name: 'JPEG Images', extensions: ['jpg', 'jpeg'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:saveExcelFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:saveFile', event, {
      ...options,
      title: options.title || 'Save Excel File',
      defaultPath: options.defaultPath || 'export.xlsx',
      filters: [
        { name: 'Excel Files', extensions: ['xlsx'] },
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:savePDFFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:saveFile', event, {
      ...options,
      title: options.title || 'Save PDF File',
      defaultPath: options.defaultPath || 'document.pdf',
      filters: [
        { name: 'PDF Files', extensions: ['pdf'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
  });

  ipcMain.handle('dialog:saveImageFile', async (event, options = {}) => {
    return ipcMain.invoke('dialog:saveFile', event, {
      ...options,
      title: options.title || 'Save Image File',
      defaultPath: options.defaultPath || 'image.png',
      filters: [
        { name: 'PNG Images', extensions: ['png'] },
        { name: 'JPEG Images', extensions: ['jpg', 'jpeg'] },
        { name: 'All Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
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

  // Native notification system
  ipcMain.handle('notification:showCalculationComplete', (event, { projectName, calculationType }) => {
    if (notificationManager) {
      const notification = notificationManager.showCalculationComplete(projectName, calculationType);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showUpdateAvailable', (event, { version, releaseNotes }) => {
    if (notificationManager) {
      const notification = notificationManager.showUpdateAvailable(version, releaseNotes);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showError', (event, { errorMessage, errorDetails }) => {
    if (notificationManager) {
      const notification = notificationManager.showError(errorMessage, errorDetails);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showWarning', (event, { warningMessage, details }) => {
    if (notificationManager) {
      const notification = notificationManager.showWarning(warningMessage, details);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showInfo', (event, { infoMessage, details }) => {
    if (notificationManager) {
      const notification = notificationManager.showInfo(infoMessage, details);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showPDFComplete', (event, { fileName }) => {
    if (notificationManager) {
      const notification = notificationManager.showPDFComplete(fileName);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showExportComplete', (event, { exportType, fileName }) => {
    if (notificationManager) {
      const notification = notificationManager.showExportComplete(exportType, fileName);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showBackupComplete', (event, { backupName }) => {
    if (notificationManager) {
      const notification = notificationManager.showBackupComplete(backupName);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showSyncComplete', (event, { itemCount }) => {
    if (notificationManager) {
      const notification = notificationManager.showSyncComplete(itemCount);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:showCustom', (event, { title, body, options }) => {
    if (notificationManager) {
      const notification = notificationManager.showCustom(title, body, options);
      return { success: notification !== null };
    }
    return { success: false };
  });

  ipcMain.handle('notification:getPreferences', () => {
    if (notificationManager) {
      return notificationManager.getPreferences();
    }
    return null;
  });

  ipcMain.handle('notification:updatePreferences', (event, preferences) => {
    if (notificationManager) {
      notificationManager.updatePreferences(preferences);
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('notification:setEnabled', (event, enabled) => {
    if (notificationManager) {
      notificationManager.setEnabled(enabled);
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('notification:setDoNotDisturb', (event, enabled) => {
    if (notificationManager) {
      notificationManager.setDoNotDisturb(enabled);
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('notification:setQuietHours', (event, { enabled, start, end }) => {
    if (notificationManager) {
      notificationManager.setQuietHours(enabled, start, end);
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('notification:getHistory', (event, limit) => {
    if (notificationManager) {
      return notificationManager.getHistory(limit);
    }
    return [];
  });

  ipcMain.handle('notification:clearHistory', () => {
    if (notificationManager) {
      notificationManager.clearHistory();
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('notification:test', () => {
    if (notificationManager) {
      const notification = notificationManager.test();
      return { success: notification !== null };
    }
    return { success: false };
  });

  // Menu operations
  ipcMain.handle('menu:addRecentProject', (event, projectPath, projectName) => {
    menuState.addRecentProject(projectPath, projectName);
    updateMenu(mainWindow);
    return { success: true };
  });

  ipcMain.handle('menu:addRecentFile', (event, filePath, fileName) => {
    menuState.addRecentFile(filePath, fileName);
    updateMenu(mainWindow);
    return { success: true };
  });

  ipcMain.handle('menu:getKeyboardShortcuts', () => {
    return getKeyboardShortcuts();
  });

  ipcMain.handle('menu:clearRecentProjects', () => {
    menuState.clearRecentProjects();
    updateMenu(mainWindow);
    return { success: true };
  });

  ipcMain.handle('menu:clearRecentFiles', () => {
    menuState.clearRecentFiles();
    updateMenu(mainWindow);
    return { success: true };
  });

  // Tray operations (additional handlers beyond those in tray.js)
  ipcMain.handle('tray:updateIcon', (event, state) => {
    updateTrayIcon(state);
    return { success: true };
  });

  ipcMain.handle('tray:isAvailable', () => {
    return tray !== null;
  });

  // Window Management operations
  ipcMain.handle('window:create', (event, options) => {
    try {
      const window = windowManager.createWindow(options);
      return { success: true, windowId: options.id };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('window:focus', (event, windowId) => {
    const success = windowManager.focusWindow(windowId);
    return { success };
  });

  ipcMain.handle('window:toggleFullscreen', (event, windowId) => {
    const isFullScreen = windowManager.toggleFullscreen(windowId || 'main');
    return { success: true, isFullScreen };
  });

  ipcMain.handle('window:setFullscreen', (event, { windowId, fullscreen }) => {
    const success = windowManager.setFullscreen(windowId || 'main', fullscreen);
    return { success };
  });

  ipcMain.handle('window:toggleAlwaysOnTop', (event, windowId) => {
    const isAlwaysOnTop = windowManager.toggleAlwaysOnTop(windowId || 'main');
    return { success: true, isAlwaysOnTop };
  });

  ipcMain.handle('window:setAlwaysOnTop', (event, { windowId, alwaysOnTop }) => {
    const success = windowManager.setAlwaysOnTop(windowId || 'main', alwaysOnTop);
    return { success };
  });

  ipcMain.handle('window:minimize', (event, windowId) => {
    const success = windowManager.minimizeWindow(windowId || 'main');
    return { success };
  });

  ipcMain.handle('window:maximize', (event, windowId) => {
    const isMaximized = windowManager.maximizeWindow(windowId || 'main');
    return { success: true, isMaximized };
  });

  ipcMain.handle('window:restore', (event, windowId) => {
    const success = windowManager.restoreWindow(windowId || 'main');
    return { success };
  });

  ipcMain.handle('window:close', (event, windowId) => {
    const success = windowManager.closeWindow(windowId || 'main');
    return { success };
  });

  ipcMain.handle('window:getInfo', (event, windowId) => {
    const info = windowManager.getWindowInfo(windowId || 'main');
    return info;
  });

  ipcMain.handle('window:getAllInfo', () => {
    const info = windowManager.getAllWindowInfo();
    return info;
  });

  ipcMain.handle('window:getPreferences', () => {
    return windowManager.getPreferences();
  });

  ipcMain.handle('window:updatePreferences', (event, preferences) => {
    windowManager.updatePreferences(preferences);
    return { success: true };
  });

  ipcMain.handle('window:clearState', (event, windowId) => {
    windowManager.clearWindowState(windowId);
    return { success: true };
  });

  ipcMain.handle('window:clearAllStates', () => {
    windowManager.clearAllWindowStates();
    return { success: true };
  });

  // Deep Link operations
  ipcMain.handle('deepLink:generate', (event, { action, params, pathSegments }) => {
    try {
      const deepLink = deepLinkManager.generateDeepLink(action, params, pathSegments);
      return { success: true, deepLink };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('deepLink:copyToClipboard', (event, { action, params, pathSegments }) => {
    try {
      const deepLink = deepLinkManager.copyDeepLinkToClipboard(action, params, pathSegments);
      return { success: true, deepLink };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('deepLink:test', (event, urlString) => {
    try {
      deepLinkManager.testDeepLink(urlString);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('deepLink:getHandlers', () => {
    const handlers = deepLinkManager.getRegisteredHandlers();
    return { success: true, handlers };
  });

  ipcMain.handle('deepLink:isRegistered', () => {
    const isRegistered = deepLinkManager.isProtocolRegistered();
    return { success: true, isRegistered };
  });

  ipcMain.handle('deepLink:registerHandler', (event, { action, handlerName }) => {
    // Custom handlers can be registered from renderer
    // This is a placeholder for future extensibility
    return { success: true, message: 'Custom handler registration not yet implemented' };
  });

  // Performance monitoring operations
  ipcMain.handle('performance:getMetrics', () => {
    if (performanceManager) {
      return performanceManager.getMetrics();
    }
    return null;
  });

  ipcMain.handle('performance:exportMetrics', () => {
    if (performanceManager) {
      return performanceManager.exportMetrics();
    }
    return null;
  });

  ipcMain.handle('performance:logMetrics', () => {
    if (performanceManager) {
      performanceManager.logPerformanceMetrics();
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('performance:forceGC', () => {
    if (performanceManager) {
      performanceManager.performGarbageCollection();
      return { success: true };
    }
    return { success: false };
  });

  // Resource cleanup operations
  ipcMain.handle('cleanup:getStatistics', () => {
    if (cleanupManager) {
      return cleanupManager.getStatistics();
    }
    return null;
  });

  ipcMain.handle('cleanup:performCleanup', async () => {
    if (cleanupManager) {
      await cleanupManager.performPeriodicCleanup();
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('cleanup:performAggressiveCleanup', async () => {
    if (cleanupManager) {
      await cleanupManager.performAggressiveCleanup();
      return { success: true };
    }
    return { success: false };
  });

  ipcMain.handle('cleanup:registerTempFile', (event, filePath) => {
    if (cleanupManager) {
      cleanupManager.registerTempFile(filePath);
      return { success: true };
    }
    return { success: false };
  });
}

// Initialize performance manager before app is ready
performanceManager = getPerformanceManager();
performanceManager.initializeBeforeReady();

// Register deep link protocol before app is ready
deepLinkManager.registerProtocol();

// Handle deep links on macOS
app.on('open-url', (event, url) => {
  event.preventDefault();
  console.log('Received open-url event:', url);
  deepLinkManager.handleDeepLink(url);
});

// Handle deep links on Windows/Linux (second instance)
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  // Another instance is already running, quit this one
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, focus our window instead
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }

    // Handle deep link from command line (Windows/Linux)
    const url = commandLine.find(arg => arg.startsWith('solarcalc://'));
    if (url) {
      console.log('Received deep link from second instance:', url);
      deepLinkManager.handleDeepLink(url);
    }
  });
}

app.whenReady().then(async () => {
  // Initialize performance manager after app is ready
  performanceManager.initializeAfterReady();
  
  // Initialize cleanup manager
  cleanupManager = getCleanupManager();
  cleanupManager.initialize();
  
  // Initialize notification manager
  notificationManager = new NotificationManager();

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
  
  // Optimize window performance
  performanceManager.optimizeWindow(mainWindow);

  // Initialize deep link manager with main window
  deepLinkManager.initialize(mainWindow);

  // Handle deep link from command line on first launch (Windows/Linux)
  if (process.platform === 'win32' || process.platform === 'linux') {
    const url = process.argv.find(arg => arg.startsWith('solarcalc://'));
    if (url) {
      console.log('Received deep link from command line:', url);
      deepLinkManager.handleDeepLink(url);
    }
  }

  // Create application menu
  createApplicationMenu(mainWindow);

  // Setup context menu
  setupContextMenu(mainWindow);

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
  // Set flag to prevent close-to-tray behavior
  app.isQuitting = true;
  
  // Save window states
  console.log('Saving window states...');
  windowManager.cleanup();
  
  // Cleanup performance manager
  if (performanceManager) {
    console.log('Cleaning up performance manager...');
    performanceManager.cleanup();
  }
  
  // Cleanup resource manager
  if (cleanupManager) {
    console.log('Performing final resource cleanup...');
    await cleanupManager.performFullCleanup();
  }
  
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
