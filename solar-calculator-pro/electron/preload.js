const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data) => ipcRenderer.invoke('dialog:saveFile', data),
  selectDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),

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

  // Notifications
  showNotification: (title, body) => ipcRenderer.send('notification:show', { title, body }),

  // System info
  isOnline: () => navigator.onLine,
  
  // Security: Validate that we're in the correct context
  isElectron: () => true,
  
  // Deep linking (for future use)
  onDeepLink: (callback) => {
    const subscription = (event, url) => callback(url);
    ipcRenderer.on('deep-link', subscription);
    return () => ipcRenderer.removeListener('deep-link', subscription);
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
