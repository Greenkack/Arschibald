/**
 * Window Manager
 * 
 * Manages window state persistence, fullscreen mode, always-on-top,
 * multi-window support, and window focus management.
 * 
 * Features:
 * - Window state persistence (position, size, maximized state)
 * - Fullscreen mode management
 * - Always-on-top functionality
 * - Multi-window support with window registry
 * - Window focus management
 * - Window restoration on app restart
 */

const { BrowserWindow, screen } = require('electron');
const Store = require('electron-store');
const path = require('path');

// Window state store
const windowStateStore = new Store({
  name: 'window-state',
  defaults: {
    windows: {},
    lastActiveWindow: null,
    preferences: {
      rememberWindowState: true,
      restoreWindowsOnStartup: true,
      defaultWidth: 1200,
      defaultHeight: 800,
      defaultMinWidth: 800,
      defaultMinHeight: 600
    }
  }
});

// Window registry
const windowRegistry = new Map();

class WindowManager {
  constructor() {
    this.windows = windowRegistry;
    this.store = windowStateStore;
    this.nextWindowId = 1;
  }

  /**
   * Create a new window with state management
   * @param {Object} options - Window creation options
   * @param {string} options.id - Unique window identifier
   * @param {string} options.type - Window type (main, secondary, modal, etc.)
   * @param {Object} options.browserWindowOptions - BrowserWindow options
   * @param {string} options.url - URL to load
   * @param {boolean} options.rememberState - Whether to remember window state
   * @returns {BrowserWindow} Created window
   */
  createWindow(options = {}) {
    const {
      id = `window-${this.nextWindowId++}`,
      type = 'secondary',
      browserWindowOptions = {},
      url = null,
      rememberState = true
    } = options;

    // Get saved state or defaults
    const savedState = this.getWindowState(id);
    const preferences = this.store.get('preferences');

    // Determine window bounds
    const bounds = this.calculateWindowBounds(savedState, browserWindowOptions, preferences);

    // Create window options
    const windowOptions = {
      ...bounds,
      minWidth: browserWindowOptions.minWidth || preferences.defaultMinWidth,
      minHeight: browserWindowOptions.minHeight || preferences.defaultMinHeight,
      show: false, // Don't show until ready
      ...browserWindowOptions,
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        sandbox: true,
        webSecurity: true,
        ...browserWindowOptions.webPreferences
      }
    };

    // Create the window
    const window = new BrowserWindow(windowOptions);

    // Register window
    this.registerWindow(id, window, type, rememberState);

    // Restore window state
    if (savedState && rememberState) {
      if (savedState.isMaximized) {
        window.maximize();
      }
      if (savedState.isFullScreen) {
        window.setFullScreen(true);
      }
      if (savedState.isAlwaysOnTop) {
        window.setAlwaysOnTop(true);
      }
    }

    // Setup window event handlers
    this.setupWindowHandlers(id, window, rememberState);

    // Load URL
    if (url) {
      window.loadURL(url);
    }

    // Show window when ready
    window.once('ready-to-show', () => {
      window.show();
      if (savedState && savedState.isFocused) {
        window.focus();
      }
    });

    return window;
  }

  /**
   * Register a window in the registry
   */
  registerWindow(id, window, type, rememberState) {
    this.windows.set(id, {
      window,
      type,
      rememberState,
      id,
      createdAt: Date.now()
    });

    console.log(`Window registered: ${id} (type: ${type})`);
  }

  /**
   * Setup window event handlers for state management
   */
  setupWindowHandlers(id, window, rememberState) {
    if (!rememberState) return;

    // Track window state changes
    const saveState = () => {
      if (!window.isDestroyed()) {
        this.saveWindowState(id, window);
      }
    };

    // Save state on various events
    window.on('resize', saveState);
    window.on('move', saveState);
    window.on('maximize', saveState);
    window.on('unmaximize', saveState);
    window.on('enter-full-screen', saveState);
    window.on('leave-full-screen', saveState);
    window.on('always-on-top-changed', saveState);

    // Track focus
    window.on('focus', () => {
      this.store.set('lastActiveWindow', id);
      if (rememberState) {
        this.updateWindowState(id, { isFocused: true });
      }
    });

    window.on('blur', () => {
      if (rememberState) {
        this.updateWindowState(id, { isFocused: false });
      }
    });

    // Cleanup on close
    window.on('closed', () => {
      this.unregisterWindow(id);
    });
  }

  /**
   * Calculate window bounds from saved state or defaults
   */
  calculateWindowBounds(savedState, options, preferences) {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { workArea } = primaryDisplay;

    let bounds = {
      width: options.width || preferences.defaultWidth,
      height: options.height || preferences.defaultHeight
    };

    // Use saved state if available and valid
    if (savedState && this.isValidBounds(savedState, workArea)) {
      bounds = {
        x: savedState.x,
        y: savedState.y,
        width: savedState.width,
        height: savedState.height
      };
    } else {
      // Center window on screen
      bounds.x = Math.round(workArea.x + (workArea.width - bounds.width) / 2);
      bounds.y = Math.round(workArea.y + (workArea.height - bounds.height) / 2);
    }

    return bounds;
  }

  /**
   * Check if saved bounds are valid for current screen configuration
   */
  isValidBounds(bounds, workArea) {
    return (
      bounds.x >= workArea.x &&
      bounds.y >= workArea.y &&
      bounds.x + bounds.width <= workArea.x + workArea.width &&
      bounds.y + bounds.height <= workArea.y + workArea.height
    );
  }

  /**
   * Save window state to store
   */
  saveWindowState(id, window) {
    if (window.isDestroyed()) return;

    const bounds = window.getBounds();
    const state = {
      x: bounds.x,
      y: bounds.y,
      width: bounds.width,
      height: bounds.height,
      isMaximized: window.isMaximized(),
      isFullScreen: window.isFullScreen(),
      isAlwaysOnTop: window.isAlwaysOnTop(),
      isFocused: window.isFocused(),
      lastSaved: Date.now()
    };

    const windows = this.store.get('windows', {});
    windows[id] = state;
    this.store.set('windows', windows);
  }

  /**
   * Update specific window state properties
   */
  updateWindowState(id, updates) {
    const windows = this.store.get('windows', {});
    if (windows[id]) {
      windows[id] = { ...windows[id], ...updates, lastSaved: Date.now() };
      this.store.set('windows', windows);
    }
  }

  /**
   * Get saved window state
   */
  getWindowState(id) {
    const windows = this.store.get('windows', {});
    return windows[id] || null;
  }

  /**
   * Clear saved window state
   */
  clearWindowState(id) {
    const windows = this.store.get('windows', {});
    delete windows[id];
    this.store.set('windows', windows);
  }

  /**
   * Unregister window from registry
   */
  unregisterWindow(id) {
    this.windows.delete(id);
    console.log(`Window unregistered: ${id}`);
  }

  /**
   * Get window by ID
   */
  getWindow(id) {
    const entry = this.windows.get(id);
    return entry ? entry.window : null;
  }

  /**
   * Get all windows
   */
  getAllWindows() {
    return Array.from(this.windows.values()).map(entry => ({
      id: entry.id,
      type: entry.type,
      window: entry.window
    }));
  }

  /**
   * Get windows by type
   */
  getWindowsByType(type) {
    return Array.from(this.windows.values())
      .filter(entry => entry.type === type)
      .map(entry => ({
        id: entry.id,
        window: entry.window
      }));
  }

  /**
   * Focus window by ID
   */
  focusWindow(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      if (window.isMinimized()) {
        window.restore();
      }
      window.focus();
      return true;
    }
    return false;
  }

  /**
   * Toggle fullscreen for window
   */
  toggleFullscreen(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      const isFullScreen = window.isFullScreen();
      window.setFullScreen(!isFullScreen);
      return !isFullScreen;
    }
    return false;
  }

  /**
   * Set fullscreen state for window
   */
  setFullscreen(id, fullscreen) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      window.setFullScreen(fullscreen);
      return true;
    }
    return false;
  }

  /**
   * Toggle always-on-top for window
   */
  toggleAlwaysOnTop(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      const isAlwaysOnTop = window.isAlwaysOnTop();
      window.setAlwaysOnTop(!isAlwaysOnTop);
      return !isAlwaysOnTop;
    }
    return false;
  }

  /**
   * Set always-on-top state for window
   */
  setAlwaysOnTop(id, alwaysOnTop) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      window.setAlwaysOnTop(alwaysOnTop);
      return true;
    }
    return false;
  }

  /**
   * Minimize window
   */
  minimizeWindow(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      window.minimize();
      return true;
    }
    return false;
  }

  /**
   * Maximize window
   */
  maximizeWindow(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      if (window.isMaximized()) {
        window.unmaximize();
        return false;
      } else {
        window.maximize();
        return true;
      }
    }
    return false;
  }

  /**
   * Restore window from minimized/maximized state
   */
  restoreWindow(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      if (window.isMinimized()) {
        window.restore();
      } else if (window.isMaximized()) {
        window.unmaximize();
      }
      return true;
    }
    return false;
  }

  /**
   * Close window
   */
  closeWindow(id) {
    const window = this.getWindow(id);
    if (window && !window.isDestroyed()) {
      window.close();
      return true;
    }
    return false;
  }

  /**
   * Close all windows of a specific type
   */
  closeWindowsByType(type) {
    const windows = this.getWindowsByType(type);
    windows.forEach(({ window }) => {
      if (!window.isDestroyed()) {
        window.close();
      }
    });
  }

  /**
   * Get window state info
   */
  getWindowInfo(id) {
    const window = this.getWindow(id);
    if (!window || window.isDestroyed()) {
      return null;
    }

    const bounds = window.getBounds();
    return {
      id,
      bounds,
      isMaximized: window.isMaximized(),
      isMinimized: window.isMinimized(),
      isFullScreen: window.isFullScreen(),
      isAlwaysOnTop: window.isAlwaysOnTop(),
      isFocused: window.isFocused(),
      isVisible: window.isVisible(),
      title: window.getTitle()
    };
  }

  /**
   * Get all window info
   */
  getAllWindowInfo() {
    return Array.from(this.windows.keys()).map(id => this.getWindowInfo(id)).filter(Boolean);
  }

  /**
   * Update preferences
   */
  updatePreferences(preferences) {
    const current = this.store.get('preferences');
    this.store.set('preferences', { ...current, ...preferences });
  }

  /**
   * Get preferences
   */
  getPreferences() {
    return this.store.get('preferences');
  }

  /**
   * Clear all saved window states
   */
  clearAllWindowStates() {
    this.store.set('windows', {});
    this.store.set('lastActiveWindow', null);
  }

  /**
   * Restore windows from previous session
   */
  restoreWindows(createWindowCallback) {
    const preferences = this.getPreferences();
    if (!preferences.restoreWindowsOnStartup) {
      return [];
    }

    const savedWindows = this.store.get('windows', {});
    const restoredWindows = [];

    Object.keys(savedWindows).forEach(id => {
      try {
        const window = createWindowCallback(id, savedWindows[id]);
        if (window) {
          restoredWindows.push({ id, window });
        }
      } catch (error) {
        console.error(`Failed to restore window ${id}:`, error);
      }
    });

    return restoredWindows;
  }

  /**
   * Get last active window ID
   */
  getLastActiveWindowId() {
    return this.store.get('lastActiveWindow');
  }

  /**
   * Cleanup - save all window states before quit
   */
  cleanup() {
    this.windows.forEach((entry, id) => {
      if (entry.rememberState && !entry.window.isDestroyed()) {
        this.saveWindowState(id, entry.window);
      }
    });
  }
}

// Export singleton instance
const windowManager = new WindowManager();

module.exports = windowManager;
