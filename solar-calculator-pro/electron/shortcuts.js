/**
 * Electron Keyboard Shortcuts
 * 
 * Handles native keyboard shortcuts at the Electron level
 */

const { globalShortcut, BrowserWindow } = require('electron');

class ShortcutManager {
  constructor() {
    this.registeredShortcuts = new Map();
  }

  /**
   * Register all global shortcuts
   */
  registerAll(mainWindow) {
    this.mainWindow = mainWindow;

    // Application shortcuts
    this.register('CommandOrControl+Q', () => {
      if (process.platform !== 'darwin') {
        this.mainWindow.close();
      }
    });

    this.register('CommandOrControl+W', () => {
      this.mainWindow.close();
    });

    this.register('CommandOrControl+M', () => {
      this.mainWindow.minimize();
    });

    this.register('F11', () => {
      const isFullScreen = this.mainWindow.isFullScreen();
      this.mainWindow.setFullScreen(!isFullScreen);
    });

    // Developer tools
    this.register('CommandOrControl+Shift+I', () => {
      this.mainWindow.webContents.toggleDevTools();
    });

    this.register('F12', () => {
      this.mainWindow.webContents.toggleDevTools();
    });

    // Reload
    this.register('CommandOrControl+R', () => {
      this.mainWindow.webContents.reload();
    });

    this.register('CommandOrControl+Shift+R', () => {
      this.mainWindow.webContents.reloadIgnoringCache();
    });

    // Zoom
    this.register('CommandOrControl+Plus', () => {
      const currentZoom = this.mainWindow.webContents.getZoomLevel();
      this.mainWindow.webContents.setZoomLevel(currentZoom + 1);
    });

    this.register('CommandOrControl+=', () => {
      const currentZoom = this.mainWindow.webContents.getZoomLevel();
      this.mainWindow.webContents.setZoomLevel(currentZoom + 1);
    });

    this.register('CommandOrControl+-', () => {
      const currentZoom = this.mainWindow.webContents.getZoomLevel();
      this.mainWindow.webContents.setZoomLevel(currentZoom - 1);
    });

    this.register('CommandOrControl+0', () => {
      this.mainWindow.webContents.setZoomLevel(0);
    });

    // Print
    this.register('CommandOrControl+P', () => {
      this.mainWindow.webContents.print();
    });

    // Find
    this.register('CommandOrControl+F', () => {
      this.mainWindow.webContents.send('open-find');
    });

    // Help
    this.register('F1', () => {
      this.mainWindow.webContents.send('open-help');
    });

    // Shortcut help
    this.register('CommandOrControl+Shift+/', () => {
      this.mainWindow.webContents.send('open-shortcut-help');
    });

    console.log(`Registered ${this.registeredShortcuts.size} global shortcuts`);
  }

  /**
   * Register a single shortcut
   */
  register(accelerator, callback) {
    try {
      const success = globalShortcut.register(accelerator, callback);
      
      if (success) {
        this.registeredShortcuts.set(accelerator, callback);
        console.log(`Registered shortcut: ${accelerator}`);
      } else {
        console.warn(`Failed to register shortcut: ${accelerator}`);
      }
    } catch (error) {
      console.error(`Error registering shortcut ${accelerator}:`, error);
    }
  }

  /**
   * Unregister a single shortcut
   */
  unregister(accelerator) {
    globalShortcut.unregister(accelerator);
    this.registeredShortcuts.delete(accelerator);
    console.log(`Unregistered shortcut: ${accelerator}`);
  }

  /**
   * Unregister all shortcuts
   */
  unregisterAll() {
    globalShortcut.unregisterAll();
    this.registeredShortcuts.clear();
    console.log('Unregistered all shortcuts');
  }

  /**
   * Check if a shortcut is registered
   */
  isRegistered(accelerator) {
    return globalShortcut.isRegistered(accelerator);
  }

  /**
   * Get all registered shortcuts
   */
  getAll() {
    return Array.from(this.registeredShortcuts.keys());
  }

  /**
   * Update shortcuts from renderer process
   */
  updateFromRenderer(shortcuts) {
    // Unregister all current shortcuts
    this.unregisterAll();

    // Register new shortcuts
    shortcuts.forEach(shortcut => {
      const accelerator = this.formatAccelerator(shortcut);
      this.register(accelerator, () => {
        this.mainWindow.webContents.send('shortcut-triggered', shortcut.id);
      });
    });
  }

  /**
   * Format shortcut config to Electron accelerator format
   */
  formatAccelerator(shortcut) {
    const parts = [];
    
    if (shortcut.ctrl) parts.push('CommandOrControl');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.meta) parts.push('Command');
    
    parts.push(shortcut.key.toUpperCase());
    
    return parts.join('+');
  }
}

module.exports = ShortcutManager;
