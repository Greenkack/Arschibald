const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  
  // Single file selection
  selectFile: (options) => ipcRenderer.invoke('dialog:openFile', options),
  
  // Multiple file selection
  selectFiles: (options) => ipcRenderer.invoke('dialog:openFiles', options),
  
  // Save file dialog
  saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),
  
  // Directory selection
  selectDirectory: (options) => ipcRenderer.invoke('dialog:openDirectory', options),
  
  // Specialized file type dialogs
  selectExcelFile: (options) => ipcRenderer.invoke('dialog:openExcelFile', options),
  selectPDFFile: (options) => ipcRenderer.invoke('dialog:openPDFFile', options),
  selectImageFile: (options) => ipcRenderer.invoke('dialog:openImageFile', options),
  selectImageFiles: (options) => ipcRenderer.invoke('dialog:openImageFiles', options),
  
  // Specialized save dialogs
  saveExcelFile: (options) => ipcRenderer.invoke('dialog:saveExcelFile', options),
  savePDFFile: (options) => ipcRenderer.invoke('dialog:savePDFFile', options),
  saveImageFile: (options) => ipcRenderer.invoke('dialog:saveImageFile', options),

  // Backend communication
  getBackendUrl: () => ipcRenderer.invoke('backend:getUrl'),
  checkBackendHealth: () => ipcRenderer.invoke('backend:checkHealth'),
  getBackendStatus: () => ipcRenderer.invoke('backend:getStatus'),
  getBackendLogs: (count) => ipcRenderer.invoke('backend:getLogs', count),
  restartBackend: () => ipcRenderer.invoke('backend:restart'),

  // Backend event listeners
  onBackendStarted: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('backend:started', subscription);
    return () => ipcRenderer.removeListener('backend:started', subscription);
  },
  onBackendStopped: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('backend:stopped', subscription);
    return () => ipcRenderer.removeListener('backend:stopped', subscription);
  },
  onBackendUnhealthy: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('backend:unhealthy', subscription);
    return () => ipcRenderer.removeListener('backend:unhealthy', subscription);
  },
  onBackendRestarting: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('backend:restarting', subscription);
    return () => ipcRenderer.removeListener('backend:restarting', subscription);
  },

  // Window operations
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // App operations
  getAppVersion: () => ipcRenderer.invoke('app:getVersion'),
  getPlatform: () => process.platform,
  getArch: () => process.arch,

  // Updates
  checkForUpdates: () => ipcRenderer.invoke('updater:check'),
  downloadUpdate: () => ipcRenderer.invoke('updater:download'),
  installUpdate: () => ipcRenderer.invoke('updater:install'),
  getCurrentVersion: () => ipcRenderer.invoke('updater:version'),
  getUpdateInfo: () => ipcRenderer.invoke('updater:info'),
  setUpdatePreferences: (preferences) => ipcRenderer.invoke('updater:setPreferences', preferences),
  clearSkipVersion: () => ipcRenderer.invoke('updater:clearSkipVersion'),
  getReleaseNotes: (version) => ipcRenderer.invoke('updater:releaseNotes', version),

  // Update event listeners
  onUpdateAvailable: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('updater:available', subscription);
    return () => ipcRenderer.removeListener('updater:available', subscription);
  },
  onUpdateDownloaded: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('updater:downloaded', subscription);
    return () => ipcRenderer.removeListener('updater:downloaded', subscription);
  },
  onUpdateProgress: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('updater:progress', subscription);
    return () => ipcRenderer.removeListener('updater:progress', subscription);
  },
  onUpdateError: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('updater:error', subscription);
    return () => ipcRenderer.removeListener('updater:error', subscription);
  },
  onUpdateChecking: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('updater:checking', subscription);
    return () => ipcRenderer.removeListener('updater:checking', subscription);
  },
  onUpdateNotAvailable: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('updater:not-available', subscription);
    return () => ipcRenderer.removeListener('updater:not-available', subscription);
  },
  onUpdateDownloading: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('updater:downloading', subscription);
    return () => ipcRenderer.removeListener('updater:downloading', subscription);
  },
  onUpdateCancelled: (callback) => {
    const subscription = () => callback();
    ipcRenderer.on('updater:cancelled', subscription);
    return () => ipcRenderer.removeListener('updater:cancelled', subscription);
  },

  // Navigation events (from menu)
  onNavigate: (callback) => {
    const subscription = (event, route) => callback(route);
    ipcRenderer.on('navigate', subscription);
    return () => ipcRenderer.removeListener('navigate', subscription);
  },

  // Action events (from menu/tray)
  onAction: (callback) => {
    const subscription = (event, action, data) => callback(action, data);
    ipcRenderer.on('action', subscription);
    return () => ipcRenderer.removeListener('action', subscription);
  },

  // Notifications (basic)
  showNotification: (title, body) => ipcRenderer.send('notification:show', { title, body }),

  // Native notification system
  notifications: {
    showCalculationComplete: (projectName, calculationType) => 
      ipcRenderer.invoke('notification:showCalculationComplete', { projectName, calculationType }),
    showUpdateAvailable: (version, releaseNotes) => 
      ipcRenderer.invoke('notification:showUpdateAvailable', { version, releaseNotes }),
    showError: (errorMessage, errorDetails) => 
      ipcRenderer.invoke('notification:showError', { errorMessage, errorDetails }),
    showWarning: (warningMessage, details) => 
      ipcRenderer.invoke('notification:showWarning', { warningMessage, details }),
    showInfo: (infoMessage, details) => 
      ipcRenderer.invoke('notification:showInfo', { infoMessage, details }),
    showPDFComplete: (fileName) => 
      ipcRenderer.invoke('notification:showPDFComplete', { fileName }),
    showExportComplete: (exportType, fileName) => 
      ipcRenderer.invoke('notification:showExportComplete', { exportType, fileName }),
    showBackupComplete: (backupName) => 
      ipcRenderer.invoke('notification:showBackupComplete', { backupName }),
    showSyncComplete: (itemCount) => 
      ipcRenderer.invoke('notification:showSyncComplete', { itemCount }),
    showCustom: (title, body, options) => 
      ipcRenderer.invoke('notification:showCustom', { title, body, options }),
    getPreferences: () => 
      ipcRenderer.invoke('notification:getPreferences'),
    updatePreferences: (preferences) => 
      ipcRenderer.invoke('notification:updatePreferences', preferences),
    setEnabled: (enabled) => 
      ipcRenderer.invoke('notification:setEnabled', enabled),
    setDoNotDisturb: (enabled) => 
      ipcRenderer.invoke('notification:setDoNotDisturb', enabled),
    setQuietHours: (enabled, start, end) => 
      ipcRenderer.invoke('notification:setQuietHours', { enabled, start, end }),
    getHistory: (limit) => 
      ipcRenderer.invoke('notification:getHistory', limit),
    clearHistory: () => 
      ipcRenderer.invoke('notification:clearHistory'),
    test: () => 
      ipcRenderer.invoke('notification:test')
  },

  // Menu operations
  addRecentProject: (projectPath, projectName) => ipcRenderer.invoke('menu:addRecentProject', projectPath, projectName),
  addRecentFile: (filePath, fileName) => ipcRenderer.invoke('menu:addRecentFile', filePath, fileName),
  getKeyboardShortcuts: () => ipcRenderer.invoke('menu:getKeyboardShortcuts'),
  clearRecentProjects: () => ipcRenderer.invoke('menu:clearRecentProjects'),
  clearRecentFiles: () => ipcRenderer.invoke('menu:clearRecentFiles'),

  // Tray operations
  tray: {
    addRecentProject: (project) => ipcRenderer.invoke('tray:addRecentProject', project),
    updateQuickActions: (quickActions) => ipcRenderer.invoke('tray:updateQuickActions', quickActions),
    getPreferences: () => ipcRenderer.invoke('tray:getPreferences'),
    updatePreferences: (preferences) => ipcRenderer.invoke('tray:updatePreferences', preferences),
    showNotification: (title, body, type, actions) => ipcRenderer.invoke('tray:showNotification', { title, body, type, actions }),
    flash: (duration) => ipcRenderer.invoke('tray:flash', { duration }),
    updateTooltip: (tooltip) => ipcRenderer.invoke('tray:updateTooltip', tooltip),
    updateIcon: (state) => ipcRenderer.invoke('tray:updateIcon', state),
    isAvailable: () => ipcRenderer.invoke('tray:isAvailable')
  },

  // Window Management operations
  window: {
    create: (options) => ipcRenderer.invoke('window:create', options),
    focus: (windowId) => ipcRenderer.invoke('window:focus', windowId),
    toggleFullscreen: (windowId) => ipcRenderer.invoke('window:toggleFullscreen', windowId),
    setFullscreen: (windowId, fullscreen) => ipcRenderer.invoke('window:setFullscreen', { windowId, fullscreen }),
    toggleAlwaysOnTop: (windowId) => ipcRenderer.invoke('window:toggleAlwaysOnTop', windowId),
    setAlwaysOnTop: (windowId, alwaysOnTop) => ipcRenderer.invoke('window:setAlwaysOnTop', { windowId, alwaysOnTop }),
    minimize: (windowId) => ipcRenderer.invoke('window:minimize', windowId),
    maximize: (windowId) => ipcRenderer.invoke('window:maximize', windowId),
    restore: (windowId) => ipcRenderer.invoke('window:restore', windowId),
    close: (windowId) => ipcRenderer.invoke('window:close', windowId),
    getInfo: (windowId) => ipcRenderer.invoke('window:getInfo', windowId),
    getAllInfo: () => ipcRenderer.invoke('window:getAllInfo'),
    getPreferences: () => ipcRenderer.invoke('window:getPreferences'),
    updatePreferences: (preferences) => ipcRenderer.invoke('window:updatePreferences', preferences),
    clearState: (windowId) => ipcRenderer.invoke('window:clearState', windowId),
    clearAllStates: () => ipcRenderer.invoke('window:clearAllStates')
  },

  // System info
  isOnline: () => navigator.onLine,
  
  // Security: Validate that we're in the correct context
  isElectron: () => true,
  
  // Deep linking
  deepLink: {
    generate: (options) => ipcRenderer.invoke('deepLink:generate', options),
    copyToClipboard: (options) => ipcRenderer.invoke('deepLink:copyToClipboard', options),
    test: (urlString) => ipcRenderer.invoke('deepLink:test', urlString),
    getHandlers: () => ipcRenderer.invoke('deepLink:getHandlers'),
    isRegistered: () => ipcRenderer.invoke('deepLink:isRegistered'),
    registerHandler: (action, handlerName) => ipcRenderer.invoke('deepLink:registerHandler', { action, handlerName })
  },

  // Generic event listener for deep link events
  on: (channel, callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on(channel, subscription);
    return () => ipcRenderer.removeListener(channel, subscription);
  }
});

// Expose a limited Node.js API for specific use cases
contextBridge.exposeInMainWorld('nodeAPI', {
  // Path operations (safe subset)
  pathJoin: (...args) => require('path').join(...args),
  pathBasename: (path) => require('path').basename(path),
  pathDirname: (path) => require('path').dirname(path),
  pathExtname: (path) => require('path').extname(path),
  
  // Environment info (read-only)
  env: {
    NODE_ENV: process.env.NODE_ENV,
    PLATFORM: process.platform,
    ARCH: process.arch
  }
});

// Log that preload script has loaded
console.log('Preload script loaded successfully');
console.log('Context isolation:', process.contextIsolated);
console.log('Node integration:', process.env.ELECTRON_RUN_AS_NODE ? 'enabled' : 'disabled');
