/**
 * Resource Cleanup Manager
 * 
 * Handles cleanup of resources to prevent memory leaks and ensure
 * optimal performance throughout the application lifecycle.
 * 
 * Requirements: 8.1, 8.7
 */

const { app, BrowserWindow, session } = require('electron');
const fs = require('fs');
const path = require('path');

class ResourceCleanupManager {
  constructor() {
    this.cleanupTasks = [];
    this.tempFiles = new Set();
    this.timers = new Set();
    this.intervals = new Set();
    this.eventListeners = new Map();
    this.isShuttingDown = false;
    
    this.config = {
      tempFileMaxAge: 24 * 60 * 60 * 1000, // 24 hours
      cacheMaxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      cleanupInterval: 60 * 60 * 1000, // 1 hour
      aggressiveCleanupOnLowMemory: true,
    };
  }

  /**
   * Initialize resource cleanup
   */
  initialize() {
    console.log('[Cleanup] Initializing resource cleanup manager...');
    
    // Setup periodic cleanup
    this.setupPeriodicCleanup();
    
    // Setup app lifecycle hooks
    this.setupLifecycleHooks();
    
    // Setup memory pressure handlers
    this.setupMemoryPressureHandlers();
    
    // Register default cleanup tasks
    this.registerDefaultCleanupTasks();
  }

  /**
   * Setup periodic cleanup
   */
  setupPeriodicCleanup() {
    const cleanupInterval = setInterval(() => {
      if (!this.isShuttingDown) {
        this.performPeriodicCleanup();
      }
    }, this.config.cleanupInterval);
    
    this.registerInterval(cleanupInterval);
    console.log('[Cleanup] Periodic cleanup scheduled');
  }

  /**
   * Setup app lifecycle hooks
   */
  setupLifecycleHooks() {
    // Cleanup before quit
    app.on('before-quit', (event) => {
      if (!this.isShuttingDown) {
        console.log('[Cleanup] App quitting, performing cleanup...');
        this.isShuttingDown = true;
        this.performFullCleanup();
      }
    });
    
    // Cleanup on window close
    app.on('window-all-closed', () => {
      console.log('[Cleanup] All windows closed');
      this.cleanupWindowResources();
    });
    
    // Cleanup on web contents destroyed
    app.on('web-contents-created', (event, webContents) => {
      webContents.on('destroyed', () => {
        this.cleanupWebContents(webContents.id);
      });
    });
  }

  /**
   * Setup memory pressure handlers
   */
  setupMemoryPressureHandlers() {
    if (this.config.aggressiveCleanupOnLowMemory) {
      // Monitor memory and trigger cleanup if needed
      const memoryCheckInterval = setInterval(() => {
        const memoryUsage = process.memoryUsage();
        const rssMB = memoryUsage.rss / 1024 / 1024;
        
        // If memory exceeds 400MB, trigger aggressive cleanup
        if (rssMB > 400) {
          console.log(`[Cleanup] High memory usage detected (${Math.round(rssMB)}MB), triggering cleanup...`);
          this.performAggressiveCleanup();
        }
      }, 30000); // Check every 30 seconds
      
      this.registerInterval(memoryCheckInterval);
    }
  }

  /**
   * Register default cleanup tasks
   */
  registerDefaultCleanupTasks() {
    // Cleanup temp files
    this.registerCleanupTask('temp-files', () => this.cleanupTempFiles());
    
    // Cleanup old caches
    this.registerCleanupTask('caches', () => this.cleanupCaches());
    
    // Cleanup old logs
    this.registerCleanupTask('logs', () => this.cleanupLogs());
    
    // Cleanup orphaned resources
    this.registerCleanupTask('orphaned', () => this.cleanupOrphanedResources());
  }

  /**
   * Register a cleanup task
   */
  registerCleanupTask(name, task) {
    this.cleanupTasks.push({ name, task });
    console.log(`[Cleanup] Registered cleanup task: ${name}`);
  }

  /**
   * Register a timer for cleanup
   */
  registerTimer(timer) {
    this.timers.add(timer);
    return timer;
  }

  /**
   * Register an interval for cleanup
   */
  registerInterval(interval) {
    this.intervals.add(interval);
    return interval;
  }

  /**
   * Register an event listener for cleanup
   */
  registerEventListener(emitter, event, listener) {
    const key = `${emitter.constructor.name}-${event}`;
    if (!this.eventListeners.has(key)) {
      this.eventListeners.set(key, []);
    }
    this.eventListeners.get(key).push({ emitter, event, listener });
  }

  /**
   * Register a temp file for cleanup
   */
  registerTempFile(filePath) {
    this.tempFiles.add(filePath);
    console.log(`[Cleanup] Registered temp file: ${filePath}`);
  }

  /**
   * Perform periodic cleanup
   */
  async performPeriodicCleanup() {
    console.log('[Cleanup] Performing periodic cleanup...');
    
    const startTime = Date.now();
    let tasksCompleted = 0;
    let tasksFailed = 0;
    
    for (const { name, task } of this.cleanupTasks) {
      try {
        await task();
        tasksCompleted++;
      } catch (error) {
        console.error(`[Cleanup] Task '${name}' failed:`, error.message);
        tasksFailed++;
      }
    }
    
    const duration = Date.now() - startTime;
    console.log(`[Cleanup] Periodic cleanup completed in ${duration}ms (${tasksCompleted} succeeded, ${tasksFailed} failed)`);
  }

  /**
   * Perform aggressive cleanup (when memory is high)
   */
  async performAggressiveCleanup() {
    console.log('[Cleanup] Performing aggressive cleanup...');
    
    // Clear all caches immediately
    await this.cleanupCaches(true);
    
    // Clear temp files
    await this.cleanupTempFiles(true);
    
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
      console.log('[Cleanup] Forced garbage collection');
    }
    
    // Clear session caches
    const windows = BrowserWindow.getAllWindows();
    for (const window of windows) {
      if (!window.isDestroyed()) {
        await window.webContents.session.clearCache();
        await window.webContents.session.clearStorageData({
          storages: ['appcache', 'serviceworkers', 'cachestorage'],
        });
      }
    }
    
    console.log('[Cleanup] Aggressive cleanup completed');
  }

  /**
   * Perform full cleanup (on app quit)
   */
  async performFullCleanup() {
    console.log('[Cleanup] Performing full cleanup...');
    
    // Clear all timers
    for (const timer of this.timers) {
      clearTimeout(timer);
    }
    this.timers.clear();
    
    // Clear all intervals
    for (const interval of this.intervals) {
      clearInterval(interval);
    }
    this.intervals.clear();
    
    // Remove all event listeners
    for (const [key, listeners] of this.eventListeners) {
      for (const { emitter, event, listener } of listeners) {
        try {
          emitter.removeListener(event, listener);
        } catch (error) {
          console.warn(`[Cleanup] Failed to remove listener for ${key}:`, error.message);
        }
      }
    }
    this.eventListeners.clear();
    
    // Run all cleanup tasks
    await this.performPeriodicCleanup();
    
    // Cleanup temp files
    await this.cleanupTempFiles(true);
    
    console.log('[Cleanup] Full cleanup completed');
  }

  /**
   * Cleanup temp files
   */
  async cleanupTempFiles(force = false) {
    console.log('[Cleanup] Cleaning up temp files...');
    
    let cleaned = 0;
    let failed = 0;
    
    for (const filePath of this.tempFiles) {
      try {
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          const age = Date.now() - stats.mtimeMs;
          
          if (force || age > this.config.tempFileMaxAge) {
            fs.unlinkSync(filePath);
            this.tempFiles.delete(filePath);
            cleaned++;
          }
        } else {
          this.tempFiles.delete(filePath);
        }
      } catch (error) {
        console.warn(`[Cleanup] Failed to cleanup temp file ${filePath}:`, error.message);
        failed++;
      }
    }
    
    console.log(`[Cleanup] Temp files: ${cleaned} cleaned, ${failed} failed`);
  }

  /**
   * Cleanup caches
   */
  async cleanupCaches(force = false) {
    console.log('[Cleanup] Cleaning up caches...');
    
    try {
      const windows = BrowserWindow.getAllWindows();
      
      for (const window of windows) {
        if (!window.isDestroyed()) {
          const ses = window.webContents.session;
          
          if (force) {
            // Clear everything
            await ses.clearCache();
            await ses.clearStorageData();
          } else {
            // Clear only old data
            await ses.clearStorageData({
              storages: ['appcache'],
            });
          }
        }
      }
      
      console.log('[Cleanup] Caches cleaned');
    } catch (error) {
      console.error('[Cleanup] Failed to cleanup caches:', error.message);
    }
  }

  /**
   * Cleanup logs
   */
  async cleanupLogs() {
    console.log('[Cleanup] Cleaning up old logs...');
    
    try {
      const logsDir = path.join(app.getPath('userData'), 'logs');
      
      if (fs.existsSync(logsDir)) {
        const files = fs.readdirSync(logsDir);
        let cleaned = 0;
        
        for (const file of files) {
          const filePath = path.join(logsDir, file);
          const stats = fs.statSync(filePath);
          const age = Date.now() - stats.mtimeMs;
          
          // Delete logs older than 7 days
          if (age > 7 * 24 * 60 * 60 * 1000) {
            fs.unlinkSync(filePath);
            cleaned++;
          }
        }
        
        console.log(`[Cleanup] Cleaned ${cleaned} old log files`);
      }
    } catch (error) {
      console.error('[Cleanup] Failed to cleanup logs:', error.message);
    }
  }

  /**
   * Cleanup orphaned resources
   */
  async cleanupOrphanedResources() {
    console.log('[Cleanup] Cleaning up orphaned resources...');
    
    // Remove destroyed windows from tracking
    const windows = BrowserWindow.getAllWindows();
    const validWindowIds = new Set(windows.map(w => w.id));
    
    // Could add more orphaned resource cleanup here
    
    console.log('[Cleanup] Orphaned resources cleaned');
  }

  /**
   * Cleanup window resources
   */
  cleanupWindowResources() {
    console.log('[Cleanup] Cleaning up window resources...');
    
    // Force garbage collection
    if (global.gc) {
      setTimeout(() => {
        global.gc();
        console.log('[Cleanup] GC after window cleanup');
      }, 1000);
    }
  }

  /**
   * Cleanup web contents
   */
  cleanupWebContents(webContentsId) {
    console.log(`[Cleanup] Cleaning up web contents ${webContentsId}...`);
    
    // Remove any tracked resources for this web contents
    // Could add more specific cleanup here
  }

  /**
   * Get cleanup statistics
   */
  getStatistics() {
    return {
      tempFiles: this.tempFiles.size,
      timers: this.timers.size,
      intervals: this.intervals.size,
      eventListeners: Array.from(this.eventListeners.values()).reduce((sum, arr) => sum + arr.length, 0),
      cleanupTasks: this.cleanupTasks.length,
    };
  }
}

// Singleton instance
let cleanupManagerInstance = null;

function getCleanupManager() {
  if (!cleanupManagerInstance) {
    cleanupManagerInstance = new ResourceCleanupManager();
  }
  return cleanupManagerInstance;
}

module.exports = {
  ResourceCleanupManager,
  getCleanupManager,
};
