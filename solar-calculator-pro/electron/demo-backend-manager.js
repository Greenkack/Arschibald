/**
 * Demo: Backend Manager Integration
 * 
 * This demonstrates how to integrate the Backend Manager
 * into an Electron application's main process.
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const BackendManager = require('./backend-manager');

let mainWindow;
let backendManager;

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    show: false, // Don't show until backend is ready
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Load frontend
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Initialize backend manager with event handlers
 */
async function initializeBackend() {
  console.log('Initializing backend manager...');

  // Create backend manager
  backendManager = new BackendManager({
    port: process.env.BACKEND_PORT || 8000,
    maxRetries: 30,
    retryDelay: 1000,
    healthCheckInterval: 10000,
    maxRestartAttempts: 3,
    restartDelay: 5000,
  });

  // Setup event handlers
  setupBackendEventHandlers();

  // Start backend
  try {
    await backendManager.start();
  } catch (error) {
    console.error('Failed to start backend:', error);
    
    // Show error dialog
    dialog.showErrorBox(
      'Backend Startup Failed',
      `Failed to start the backend server:\n\n${error.message}\n\nThe application will now exit.`
    );
    
    app.quit();
  }
}

/**
 * Setup backend event handlers
 */
function setupBackendEventHandlers() {
  // Backend starting
  backendManager.on('starting', () => {
    console.log('Backend is starting...');
  });

  // Backend started successfully
  backendManager.on('started', () => {
    console.log('Backend started successfully!');
    
    // Show window now that backend is ready
    if (mainWindow) {
      mainWindow.show();
    }
    
    // Notify renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:started');
    }
  });

  // Backend stopping
  backendManager.on('stopping', () => {
    console.log('Backend is stopping...');
    
    // Notify renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:stopping');
    }
  });

  // Backend stopped
  backendManager.on('stopped', ({ code, signal }) => {
    console.log(`Backend stopped (code: ${code}, signal: ${signal})`);
    
    // Notify renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:stopped', { code, signal });
    }
  });

  // Backend restarting
  backendManager.on('restarting', () => {
    console.log('Backend is restarting...');
    
    // Show notification to user
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('show-notification', {
        type: 'info',
        title: 'Backend Restarting',
        message: 'The backend server is restarting. Please wait...',
      });
    }
  });

  // Backend unhealthy
  backendManager.on('unhealthy', () => {
    console.warn('Backend health check failed!');
    
    // Show warning to user
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('show-notification', {
        type: 'warning',
        title: 'Backend Connection Lost',
        message: 'Connection to backend lost. Attempting to reconnect...',
      });
      
      mainWindow.webContents.send('backend:unhealthy');
    }
  });

  // Backend failed
  backendManager.on('failed', (error) => {
    console.error('Backend failed:', error);
    
    // Show error dialog
    dialog.showErrorBox(
      'Backend Error',
      `The backend server has failed and could not be restarted:\n\n${error.message}\n\nPlease restart the application.`
    );
  });

  // Backend stdout
  backendManager.on('stdout', (message) => {
    // Log to console (could also send to renderer for debugging)
    console.log('[Backend]', message);
  });

  // Backend stderr
  backendManager.on('stderr', (message) => {
    // Log errors
    console.error('[Backend Error]', message);
  });

  // Backend errors
  backendManager.on('error', (error) => {
    console.error('Backend process error:', error);
  });

  // Log entries
  backendManager.on('log', ({ timestamp, level, message }) => {
    // Could send to external logging service
    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
  });
}

/**
 * Setup IPC handlers for backend operations
 */
function setupIPCHandlers() {
  // Get backend status
  ipcMain.handle('backend:getStatus', () => {
    return backendManager.getStatus();
  });

  // Get backend logs
  ipcMain.handle('backend:getLogs', (event, count = 100) => {
    return backendManager.getLogs(count);
  });

  // Restart backend
  ipcMain.handle('backend:restart', async () => {
    try {
      await backendManager.restart();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // Check backend health
  ipcMain.handle('backend:checkHealth', async () => {
    return await backendManager.checkHealth();
  });

  // Get backend URL
  ipcMain.handle('backend:getUrl', () => {
    return backendManager.getUrl();
  });
}

/**
 * App lifecycle handlers
 */

// App ready
app.whenReady().then(async () => {
  // Setup IPC handlers
  setupIPCHandlers();
  
  // Create window
  createWindow();
  
  // Initialize backend
  await initializeBackend();
});

// Before quit - cleanup backend
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

// All windows closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Activate (macOS)
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  
  dialog.showErrorBox(
    'Application Error',
    `An unexpected error occurred:\n\n${error.message}`
  );
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
});

console.log('Electron app initialized');
