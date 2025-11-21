const { Tray, Menu, app, nativeImage, Notification } = require('electron');
const path = require('path');
const Store = require('electron-store');

let tray = null;
let mainWindow = null;
let trayIconPath = null;
let notificationQueue = [];
let isProcessingNotifications = false;

// Store for tray preferences
const trayStore = new Store({
  name: 'tray-preferences',
  defaults: {
    minimizeToTray: true,
    closeToTray: false,
    showNotifications: true,
    notificationSound: true,
    startMinimized: false,
    recentProjects: [],
    quickActions: [
      { id: 'solar', label: 'Solar Calculator', route: '/solar', enabled: true },
      { id: 'heatpump', label: 'Heat Pump', route: '/heatpump', enabled: true },
      { id: 'crm', label: 'CRM', route: '/crm', enabled: true },
      { id: 'products', label: 'Products', route: '/products', enabled: true },
      { id: 'pdf', label: 'PDF Generation', route: '/pdf', enabled: true }
    ]
  }
});

/**
 * Create system tray icon with full functionality
 * @param {BrowserWindow} window - Main application window
 * @returns {Tray} Tray instance
 */
function createTray(window) {
  mainWindow = window;
  
  // Create tray icon
  trayIconPath = path.join(__dirname, '../assets/tray-icon.png');
  let icon;
  
  try {
    icon = createTrayIcon(trayIconPath);
  } catch (error) {
    console.warn('Tray icon not found, creating fallback icon');
    icon = createFallbackIcon();
  }

  tray = new Tray(icon);

  // Set tooltip with app version
  const appVersion = app.getVersion();
  tray.setToolTip(`Solar Calculator Pro v${appVersion}`);

  // Build and set context menu
  updateTrayMenu();

  // Handle tray click (single click)
  tray.on('click', () => {
    handleTrayClick();
  });

  // Handle double click (Windows/Linux)
  tray.on('double-click', () => {
    showWindow();
  });

  // Handle right-click (show context menu explicitly on some platforms)
  tray.on('right-click', () => {
    tray.popUpContextMenu();
  });

  // Setup window event handlers for minimize to tray
  setupWindowHandlers();

  // Setup IPC handlers for tray operations
  setupTrayIpcHandlers();

  console.log('System tray created successfully');
  return tray;
}

/**
 * Create properly sized tray icon for the platform
 * @param {string} iconPath - Path to icon file
 * @returns {NativeImage} Resized icon
 */
function createTrayIcon(iconPath) {
  let icon = nativeImage.createFromPath(iconPath);
  
  // Platform-specific sizing
  if (process.platform === 'darwin') {
    // macOS: 22x22 with @2x support
    icon = icon.resize({ width: 22, height: 22 });
    icon.setTemplateImage(true); // Use template image for dark mode support
  } else if (process.platform === 'win32') {
    // Windows: 16x16
    icon = icon.resize({ width: 16, height: 16 });
  } else {
    // Linux: 22x22
    icon = icon.resize({ width: 22, height: 22 });
  }
  
  return icon;
}

/**
 * Create fallback icon when icon file is not found
 * @returns {NativeImage} Fallback icon
 */
function createFallbackIcon() {
  // Create a simple colored square as fallback
  const size = process.platform === 'darwin' ? 22 : 16;
  const canvas = require('canvas').createCanvas(size, size);
  const ctx = canvas.getContext('2d');
  
  // Draw a simple sun icon
  ctx.fillStyle = '#FFA500';
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, size / 3, 0, 2 * Math.PI);
  ctx.fill();
  
  const buffer = canvas.toBuffer('image/png');
  return nativeImage.createFromBuffer(buffer);
}

/**
 * Build and update the tray context menu
 */
function updateTrayMenu() {
  if (!tray) return;

  const preferences = trayStore.store;
  const recentProjects = preferences.recentProjects || [];
  const quickActions = preferences.quickActions || [];

  const contextMenu = Menu.buildFromTemplate([
    // Header with app name
    {
      label: 'Solar Calculator Pro',
      enabled: false,
      icon: createSmallIcon()
    },
    { type: 'separator' },
    
    // Quick window toggle
    {
      label: mainWindow && mainWindow.isVisible() ? 'Hide Window' : 'Show Window',
      click: () => {
        if (mainWindow && mainWindow.isVisible()) {
          mainWindow.hide();
        } else {
          showWindow();
        }
      },
      accelerator: 'CmdOrCtrl+Shift+H'
    },
    
    // Dashboard
    {
      label: '📊 Dashboard',
      click: () => {
        showWindow();
        mainWindow.webContents.send('navigate', '/dashboard');
      },
      accelerator: 'CmdOrCtrl+Shift+D'
    },
    
    { type: 'separator' },
    
    // New calculation
    {
      label: '➕ New Calculation',
      click: () => {
        showWindow();
        mainWindow.webContents.send('action', 'new-project');
      },
      accelerator: 'CmdOrCtrl+Shift+N'
    },
    
    { type: 'separator' },
    
    // Quick Actions submenu
    {
      label: '⚡ Quick Actions',
      submenu: buildQuickActionsMenu(quickActions)
    },
    
    // Recent Projects submenu
    {
      label: '📁 Recent Projects',
      submenu: buildRecentProjectsMenu(recentProjects)
    },
    
    { type: 'separator' },
    
    // Tools submenu
    {
      label: '🔧 Tools',
      submenu: [
        {
          label: 'Import Excel',
          click: () => {
            showWindow();
            mainWindow.webContents.send('action', 'import-excel');
          }
        },
        {
          label: 'Export PDF',
          click: () => {
            showWindow();
            mainWindow.webContents.send('action', 'export-pdf');
          }
        },
        {
          label: 'Generate Report',
          click: () => {
            showWindow();
            mainWindow.webContents.send('action', 'generate-report');
          }
        },
        { type: 'separator' },
        {
          label: 'Database Backup',
          click: () => {
            showWindow();
            mainWindow.webContents.send('action', 'database-backup');
          }
        }
      ]
    },
    
    { type: 'separator' },
    
    // Settings
    {
      label: '⚙️ Settings',
      click: () => {
        showWindow();
        mainWindow.webContents.send('navigate', '/settings');
      }
    },
    
    // Tray preferences
    {
      label: '🎛️ Tray Preferences',
      submenu: [
        {
          label: 'Minimize to Tray',
          type: 'checkbox',
          checked: preferences.minimizeToTray,
          click: (menuItem) => {
            trayStore.set('minimizeToTray', menuItem.checked);
          }
        },
        {
          label: 'Close to Tray',
          type: 'checkbox',
          checked: preferences.closeToTray,
          click: (menuItem) => {
            trayStore.set('closeToTray', menuItem.checked);
          }
        },
        {
          label: 'Show Notifications',
          type: 'checkbox',
          checked: preferences.showNotifications,
          click: (menuItem) => {
            trayStore.set('showNotifications', menuItem.checked);
          }
        },
        {
          label: 'Notification Sound',
          type: 'checkbox',
          checked: preferences.notificationSound,
          click: (menuItem) => {
            trayStore.set('notificationSound', menuItem.checked);
          }
        },
        { type: 'separator' },
        {
          label: 'Configure Quick Actions',
          click: () => {
            showWindow();
            mainWindow.webContents.send('action', 'configure-tray-quick-actions');
          }
        }
      ]
    },
    
    { type: 'separator' },
    
    // Help
    {
      label: '❓ Help',
      click: () => {
        showWindow();
        mainWindow.webContents.send('action', 'show-help');
      }
    },
    
    // About
    {
      label: 'ℹ️ About',
      click: () => {
        showWindow();
        mainWindow.webContents.send('action', 'show-about');
      }
    },
    
    { type: 'separator' },
    
    // Quit
    {
      label: '🚪 Quit',
      click: () => {
        // Force quit, bypassing close to tray
        trayStore.set('closeToTray', false);
        app.quit();
      },
      accelerator: 'CmdOrCtrl+Q'
    }
  ]);

  tray.setContextMenu(contextMenu);
}

/**
 * Build quick actions submenu
 * @param {Array} quickActions - Array of quick action configurations
 * @returns {Array} Menu items
 */
function buildQuickActionsMenu(quickActions) {
  const enabledActions = quickActions.filter(action => action.enabled);
  
  if (enabledActions.length === 0) {
    return [
      { label: 'No quick actions configured', enabled: false }
    ];
  }

  return enabledActions.map(action => ({
    label: action.label,
    click: () => {
      showWindow();
      mainWindow.webContents.send('navigate', action.route);
    }
  }));
}

/**
 * Build recent projects submenu
 * @param {Array} recentProjects - Array of recent project objects
 * @returns {Array} Menu items
 */
function buildRecentProjectsMenu(recentProjects) {
  if (recentProjects.length === 0) {
    return [
      { label: 'No recent projects', enabled: false }
    ];
  }

  const projectItems = recentProjects.slice(0, 10).map((project, index) => ({
    label: `${index + 1}. ${project.name}`,
    click: () => {
      showWindow();
      mainWindow.webContents.send('action', 'open-project', project.id);
    },
    sublabel: project.date ? new Date(project.date).toLocaleDateString() : ''
  }));

  return [
    ...projectItems,
    { type: 'separator' },
    {
      label: 'Clear Recent Projects',
      click: () => {
        trayStore.set('recentProjects', []);
        updateTrayMenu();
      }
    }
  ];
}

/**
 * Create small icon for menu header
 * @returns {NativeImage} Small icon
 */
function createSmallIcon() {
  try {
    const icon = nativeImage.createFromPath(trayIconPath);
    return icon.resize({ width: 16, height: 16 });
  } catch {
    return null;
  }
}

/**
 * Show and focus the main window
 */
function showWindow() {
  if (!mainWindow) return;
  
  if (mainWindow.isMinimized()) {
    mainWindow.restore();
  }
  
  if (!mainWindow.isVisible()) {
    mainWindow.show();
  }
  
  mainWindow.focus();
  
  // Bring to front on macOS
  if (process.platform === 'darwin') {
    app.dock.show();
  }
}

/**
 * Handle tray icon click
 */
function handleTrayClick() {
  if (!mainWindow) return;
  
  // Toggle window visibility on click
  if (mainWindow.isVisible() && !mainWindow.isMinimized()) {
    mainWindow.hide();
  } else {
    showWindow();
  }
}

/**
 * Setup window event handlers for minimize/close to tray
 */
function setupWindowHandlers() {
  if (!mainWindow) return;

  // Handle minimize event
  mainWindow.on('minimize', (event) => {
    const preferences = trayStore.store;
    if (preferences.minimizeToTray) {
      event.preventDefault();
      mainWindow.hide();
      
      // Show notification on first minimize
      if (!trayStore.get('hasShownMinimizeNotification')) {
        showTrayNotification(
          'Minimized to Tray',
          'Solar Calculator Pro is still running in the background. Click the tray icon to restore.',
          'info'
        );
        trayStore.set('hasShownMinimizeNotification', true);
      }
    }
  });

  // Handle close event
  mainWindow.on('close', (event) => {
    const preferences = trayStore.store;
    if (preferences.closeToTray && !app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      
      // Show notification
      showTrayNotification(
        'Running in Background',
        'Solar Calculator Pro is still running. Right-click the tray icon and select Quit to exit.',
        'info'
      );
    }
  });

  // Handle show event
  mainWindow.on('show', () => {
    updateTrayMenu();
  });

  // Handle hide event
  mainWindow.on('hide', () => {
    updateTrayMenu();
  });
}

/**
 * Setup IPC handlers for tray operations
 */
function setupTrayIpcHandlers() {
  const { ipcMain } = require('electron');

  // Add recent project to tray menu
  ipcMain.handle('tray:addRecentProject', (event, project) => {
    const recentProjects = trayStore.get('recentProjects', []);
    
    // Remove if already exists
    const filtered = recentProjects.filter(p => p.id !== project.id);
    
    // Add to beginning
    filtered.unshift({
      id: project.id,
      name: project.name,
      date: new Date().toISOString()
    });
    
    // Keep only last 10
    trayStore.set('recentProjects', filtered.slice(0, 10));
    updateTrayMenu();
    
    return { success: true };
  });

  // Update quick actions
  ipcMain.handle('tray:updateQuickActions', (event, quickActions) => {
    trayStore.set('quickActions', quickActions);
    updateTrayMenu();
    return { success: true };
  });

  // Get tray preferences
  ipcMain.handle('tray:getPreferences', () => {
    return trayStore.store;
  });

  // Update tray preferences
  ipcMain.handle('tray:updatePreferences', (event, preferences) => {
    Object.keys(preferences).forEach(key => {
      trayStore.set(key, preferences[key]);
    });
    updateTrayMenu();
    return { success: true };
  });

  // Show tray notification
  ipcMain.handle('tray:showNotification', (event, { title, body, type, actions }) => {
    showTrayNotification(title, body, type, actions);
    return { success: true };
  });

  // Flash tray icon
  ipcMain.handle('tray:flash', (event, { duration = 3000 }) => {
    flashTrayIcon(duration);
    return { success: true };
  });

  // Update tray tooltip
  ipcMain.handle('tray:updateTooltip', (event, tooltip) => {
    if (tray) {
      tray.setToolTip(tooltip);
    }
    return { success: true };
  });
}

/**
 * Show tray notification with enhanced features
 * @param {string} title - Notification title
 * @param {string} body - Notification body
 * @param {string} type - Notification type (info, success, warning, error)
 * @param {Array} actions - Optional notification actions
 */
function showTrayNotification(title, body, type = 'info', actions = []) {
  const preferences = trayStore.store;
  
  if (!preferences.showNotifications) {
    return;
  }

  // Add to queue
  notificationQueue.push({ title, body, type, actions, timestamp: Date.now() });
  
  // Process queue
  processNotificationQueue();
}

/**
 * Process notification queue to avoid overwhelming the user
 */
async function processNotificationQueue() {
  if (isProcessingNotifications || notificationQueue.length === 0) {
    return;
  }

  isProcessingNotifications = true;

  while (notificationQueue.length > 0) {
    const notification = notificationQueue.shift();
    await displayNotification(notification);
    
    // Wait 2 seconds between notifications
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  isProcessingNotifications = false;
}

/**
 * Display a single notification
 * @param {Object} notificationData - Notification data
 */
async function displayNotification({ title, body, type, actions }) {
  const preferences = trayStore.store;

  if (!Notification.isSupported()) {
    console.warn('Notifications are not supported on this system');
    return;
  }

  // Create notification
  const notification = new Notification({
    title,
    body,
    icon: trayIconPath,
    silent: !preferences.notificationSound,
    urgency: type === 'error' ? 'critical' : type === 'warning' ? 'normal' : 'low',
    timeoutType: 'default'
  });

  // Add actions if provided
  if (actions && actions.length > 0) {
    notification.actions = actions;
  }

  // Handle notification click
  notification.on('click', () => {
    showWindow();
  });

  // Handle action clicks
  notification.on('action', (event, index) => {
    if (actions[index] && actions[index].callback) {
      actions[index].callback();
    }
  });

  // Show notification
  notification.show();

  // Flash tray icon for important notifications
  if (type === 'error' || type === 'warning') {
    flashTrayIcon(3000);
  }
}

/**
 * Flash tray icon to get user attention
 * @param {number} duration - Duration in milliseconds
 */
function flashTrayIcon(duration = 3000) {
  if (!tray || process.platform === 'darwin') {
    // macOS doesn't support flashing
    return;
  }

  let isHighlighted = false;
  const interval = 500;
  const iterations = Math.floor(duration / interval);
  let count = 0;

  const flashInterval = setInterval(() => {
    if (count >= iterations) {
      clearInterval(flashInterval);
      tray.setHighlightMode('never');
      return;
    }

    isHighlighted = !isHighlighted;
    tray.setHighlightMode(isHighlighted ? 'always' : 'never');
    count++;
  }, interval);
}

/**
 * Update tray icon based on application state
 * @param {string} state - Application state (normal, busy, error, warning)
 */
function updateTrayIcon(state = 'normal') {
  if (!tray) return;

  let icon;
  
  try {
    switch (state) {
      case 'busy':
        icon = createTrayIcon(path.join(__dirname, '../assets/tray-icon-busy.png'));
        break;
      case 'error':
        icon = createTrayIcon(path.join(__dirname, '../assets/tray-icon-error.png'));
        break;
      case 'warning':
        icon = createTrayIcon(path.join(__dirname, '../assets/tray-icon-warning.png'));
        break;
      default:
        icon = createTrayIcon(trayIconPath);
    }
    
    tray.setImage(icon);
  } catch (error) {
    console.warn('Failed to update tray icon:', error);
  }
}

/**
 * Add a recent project to the tray menu
 * @param {Object} project - Project object with id, name, and optional date
 */
function addRecentProject(project) {
  const recentProjects = trayStore.get('recentProjects', []);
  
  // Remove if already exists
  const filtered = recentProjects.filter(p => p.id !== project.id);
  
  // Add to beginning
  filtered.unshift({
    id: project.id,
    name: project.name,
    date: project.date || new Date().toISOString()
  });
  
  // Keep only last 10
  trayStore.set('recentProjects', filtered.slice(0, 10));
  updateTrayMenu();
}

/**
 * Clear all recent projects
 */
function clearRecentProjects() {
  trayStore.set('recentProjects', []);
  updateTrayMenu();
}

/**
 * Get tray preferences
 * @returns {Object} Tray preferences
 */
function getTrayPreferences() {
  return trayStore.store;
}

/**
 * Update tray preferences
 * @param {Object} preferences - Preferences to update
 */
function updateTrayPreferences(preferences) {
  Object.keys(preferences).forEach(key => {
    trayStore.set(key, preferences[key]);
  });
  updateTrayMenu();
}

/**
 * Destroy tray icon and cleanup
 */
function destroyTray() {
  if (tray) {
    tray.destroy();
    tray = null;
  }
  
  mainWindow = null;
  notificationQueue = [];
  isProcessingNotifications = false;
}

/**
 * Check if tray is available
 * @returns {boolean} True if tray is available
 */
function isTrayAvailable() {
  return tray !== null;
}

// Export functions
module.exports = {
  createTray,
  updateTrayMenu,
  showTrayNotification,
  flashTrayIcon,
  updateTrayIcon,
  addRecentProject,
  clearRecentProjects,
  getTrayPreferences,
  updateTrayPreferences,
  destroyTray,
  isTrayAvailable,
  showWindow
};
