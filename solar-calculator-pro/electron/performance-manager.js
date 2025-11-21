/**
 * Electron Performance Manager
 * 
 * Optimizes Electron application performance including:
 * - Startup time optimization
 * - Memory management
 * - Resource cleanup
 * - Performance monitoring
 * - IPC communication optimization
 * 
 * Requirements: 8.1, 8.7
 */

const { app, BrowserWindow } = require('electron');
const os = require('os');
const v8 = require('v8');

class PerformanceManager {
  constructor() {
    this.metrics = {
      startupTime: null,
      memoryUsage: [],
      ipcLatency: [],
      renderProcesses: new Map(),
    };
    
    this.config = {
      maxMemoryMB: 500, // Requirement 8.7: Keep memory under 500MB in idle
      memoryCheckInterval: 30000, // Check every 30 seconds
      gcInterval: 60000, // Force GC every 60 seconds if needed
      ipcTimeout: 100, // IPC should respond within 100ms
      preloadCriticalResources: true,
      enableHardwareAcceleration: true,
      enableBackgroundThrottling: true,
    };
    
    this.startTime = Date.now();
    this.isMonitoring = false;
  }

  /**
   * Initialize performance optimizations
   * Must be called before app is ready
   */
  initializeBeforeReady() {
    console.log('[Performance] Initializing pre-ready optimizations...');
    
    // Optimize startup time
    this.optimizeStartup();
    
    // Configure app-level performance settings
    this.configureAppPerformance();
    
    // Setup early event listeners
    this.setupEarlyListeners();
  }

  /**
   * Initialize performance monitoring after app is ready
   */
  initializeAfterReady() {
    console.log('[Performance] Initializing post-ready optimizations...');
    
    // Calculate startup time (Requirement 8.1: < 3 seconds)
    this.metrics.startupTime = Date.now() - this.startTime;
    console.log(`[Performance] Startup time: ${this.metrics.startupTime}ms`);
    
    if (this.metrics.startupTime > 3000) {
      console.warn('[Performance] WARNING: Startup time exceeds 3 second target!');
    }
    
    // Start monitoring
    this.startMonitoring();
    
    // Setup memory management
    this.setupMemoryManagement();
    
    // Setup IPC optimization
    this.setupIPCOptimization();
  }

  /**
   * Optimize application startup time
   */
  optimizeStartup() {
    // Disable hardware acceleration if not needed (can speed up startup)
    if (!this.config.enableHardwareAcceleration) {
      app.disableHardwareAcceleration();
      console.log('[Performance] Hardware acceleration disabled');
    }
    
    // Enable background throttling to save resources
    if (this.config.enableBackgroundThrottling) {
      app.commandLine.appendSwitch('enable-features', 'BackgroundResourceFetch');
      console.log('[Performance] Background throttling enabled');
    }
    
    // Optimize renderer process
    app.commandLine.appendSwitch('disable-renderer-backgrounding');
    app.commandLine.appendSwitch('disable-background-timer-throttling');
    
    // Reduce memory footprint
    app.commandLine.appendSwitch('js-flags', '--max-old-space-size=512');
    
    // Enable V8 code caching for faster subsequent starts
    app.commandLine.appendSwitch('enable-features', 'V8CodeCache');
    
    console.log('[Performance] Startup optimizations applied');
  }

  /**
   * Configure app-level performance settings
   */
  configureAppPerformance() {
    // Set app user model ID for better Windows performance
    if (process.platform === 'win32') {
      app.setAppUserModelId('com.solarcalculator.app');
    }
    
    // Optimize process priority
    if (process.platform !== 'darwin') {
      try {
        app.setAppUserModelId(process.pid, os.constants.priority.PRIORITY_NORMAL);
      } catch (error) {
        console.warn('[Performance] Could not set process priority:', error.message);
      }
    }
  }

  /**
   * Setup early event listeners for performance tracking
   */
  setupEarlyListeners() {
    // Track when app becomes ready
    app.once('ready', () => {
      console.log('[Performance] App ready event fired');
    });
    
    // Track window creation
    app.on('browser-window-created', (event, window) => {
      const windowId = window.id;
      this.metrics.renderProcesses.set(windowId, {
        created: Date.now(),
        pid: window.webContents.getOSProcessId(),
      });
      
      console.log(`[Performance] Window ${windowId} created (PID: ${window.webContents.getOSProcessId()})`);
    });
  }

  /**
   * Start performance monitoring
   */
  startMonitoring() {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    console.log('[Performance] Starting performance monitoring...');
    
    // Monitor memory usage
    this.memoryMonitorInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, this.config.memoryCheckInterval);
    
    // Periodic garbage collection if needed
    this.gcInterval = setInterval(() => {
      this.performGarbageCollection();
    }, this.config.gcInterval);
    
    // Log initial metrics
    this.logPerformanceMetrics();
  }

  /**
   * Stop performance monitoring
   */
  stopMonitoring() {
    if (!this.isMonitoring) return;
    
    this.isMonitoring = false;
    console.log('[Performance] Stopping performance monitoring...');
    
    if (this.memoryMonitorInterval) {
      clearInterval(this.memoryMonitorInterval);
      this.memoryMonitorInterval = null;
    }
    
    if (this.gcInterval) {
      clearInterval(this.gcInterval);
      this.gcInterval = null;
    }
  }

  /**
   * Setup memory management
   */
  setupMemoryManagement() {
    console.log('[Performance] Setting up memory management...');
    
    // Monitor for memory pressure
    app.on('render-process-gone', (event, webContents, details) => {
      console.error('[Performance] Render process crashed:', details);
      this.handleProcessCrash(webContents, details);
    });
    
    // Handle low memory warnings
    if (process.platform === 'darwin') {
      app.on('child-process-gone', (event, details) => {
        console.warn('[Performance] Child process gone:', details);
      });
    }
  }

  /**
   * Check memory usage and enforce limits
   */
  checkMemoryUsage() {
    const memoryInfo = process.memoryUsage();
    const heapUsedMB = Math.round(memoryInfo.heapUsed / 1024 / 1024);
    const rssMB = Math.round(memoryInfo.rss / 1024 / 1024);
    
    // Store metrics
    this.metrics.memoryUsage.push({
      timestamp: Date.now(),
      heapUsed: heapUsedMB,
      rss: rssMB,
      external: Math.round(memoryInfo.external / 1024 / 1024),
    });
    
    // Keep only last 100 measurements
    if (this.metrics.memoryUsage.length > 100) {
      this.metrics.memoryUsage.shift();
    }
    
    // Check against limit (Requirement 8.7: < 500MB in idle)
    if (rssMB > this.config.maxMemoryMB) {
      console.warn(`[Performance] Memory usage (${rssMB}MB) exceeds limit (${this.config.maxMemoryMB}MB)`);
      this.handleHighMemoryUsage(rssMB);
    }
    
    // Log periodically
    if (this.metrics.memoryUsage.length % 10 === 0) {
      console.log(`[Performance] Memory: Heap ${heapUsedMB}MB, RSS ${rssMB}MB`);
    }
  }

  /**
   * Handle high memory usage
   */
  handleHighMemoryUsage(currentMB) {
    console.log('[Performance] Attempting to reduce memory usage...');
    
    // Force garbage collection
    if (global.gc) {
      global.gc();
      console.log('[Performance] Forced garbage collection');
    }
    
    // Clear caches in all windows
    const windows = BrowserWindow.getAllWindows();
    windows.forEach(window => {
      if (!window.isDestroyed()) {
        window.webContents.session.clearCache();
        console.log(`[Performance] Cleared cache for window ${window.id}`);
      }
    });
    
    // Notify user if memory is critically high
    if (currentMB > this.config.maxMemoryMB * 1.5) {
      console.error('[Performance] CRITICAL: Memory usage is critically high!');
      // Could show notification to user here
    }
  }

  /**
   * Perform garbage collection if available
   */
  performGarbageCollection() {
    if (global.gc) {
      const before = process.memoryUsage().heapUsed;
      global.gc();
      const after = process.memoryUsage().heapUsed;
      const freed = Math.round((before - after) / 1024 / 1024);
      
      if (freed > 10) {
        console.log(`[Performance] GC freed ${freed}MB`);
      }
    }
  }

  /**
   * Handle process crash
   */
  handleProcessCrash(webContents, details) {
    console.error('[Performance] Process crash details:', {
      reason: details.reason,
      exitCode: details.exitCode,
    });
    
    // Log memory state at crash
    this.logPerformanceMetrics();
    
    // Attempt recovery
    if (details.reason === 'oom') {
      console.error('[Performance] Out of memory crash detected!');
      // Could implement recovery strategy here
    }
  }

  /**
   * Setup IPC communication optimization
   */
  setupIPCOptimization() {
    console.log('[Performance] Setting up IPC optimization...');
    
    // Track IPC performance
    const { ipcMain } = require('electron');
    
    // Wrap IPC handlers to measure latency
    const originalHandle = ipcMain.handle.bind(ipcMain);
    ipcMain.handle = (channel, handler) => {
      return originalHandle(channel, async (event, ...args) => {
        const start = Date.now();
        try {
          const result = await handler(event, ...args);
          const latency = Date.now() - start;
          
          this.recordIPCLatency(channel, latency);
          
          if (latency > this.config.ipcTimeout) {
            console.warn(`[Performance] IPC '${channel}' took ${latency}ms (exceeds ${this.config.ipcTimeout}ms target)`);
          }
          
          return result;
        } catch (error) {
          const latency = Date.now() - start;
          this.recordIPCLatency(channel, latency, true);
          throw error;
        }
      });
    };
    
    console.log('[Performance] IPC monitoring enabled');
  }

  /**
   * Record IPC latency metrics
   */
  recordIPCLatency(channel, latency, isError = false) {
    this.metrics.ipcLatency.push({
      channel,
      latency,
      isError,
      timestamp: Date.now(),
    });
    
    // Keep only last 1000 measurements
    if (this.metrics.ipcLatency.length > 1000) {
      this.metrics.ipcLatency.shift();
    }
  }

  /**
   * Optimize window creation
   */
  optimizeWindow(window) {
    if (!window || window.isDestroyed()) return;
    
    console.log(`[Performance] Optimizing window ${window.id}...`);
    
    // Enable performance optimizations
    window.webContents.setBackgroundThrottling(this.config.enableBackgroundThrottling);
    
    // Setup resource cleanup on close
    window.on('closed', () => {
      this.cleanupWindow(window.id);
    });
    
    // Monitor page load performance
    window.webContents.on('did-finish-load', () => {
      const loadTime = Date.now() - (this.metrics.renderProcesses.get(window.id)?.created || Date.now());
      console.log(`[Performance] Window ${window.id} loaded in ${loadTime}ms`);
    });
    
    // Handle unresponsive renderer
    window.on('unresponsive', () => {
      console.warn(`[Performance] Window ${window.id} became unresponsive`);
    });
    
    window.on('responsive', () => {
      console.log(`[Performance] Window ${window.id} became responsive again`);
    });
  }

  /**
   * Cleanup resources for a window
   */
  cleanupWindow(windowId) {
    console.log(`[Performance] Cleaning up window ${windowId}...`);
    
    this.metrics.renderProcesses.delete(windowId);
    
    // Force garbage collection after window closes
    if (global.gc) {
      setTimeout(() => {
        global.gc();
        console.log(`[Performance] GC after window ${windowId} closed`);
      }, 1000);
    }
  }

  /**
   * Get current performance metrics
   */
  getMetrics() {
    const memoryInfo = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    return {
      startup: {
        time: this.metrics.startupTime,
        target: 3000,
        withinTarget: this.metrics.startupTime < 3000,
      },
      memory: {
        current: {
          heapUsed: Math.round(memoryInfo.heapUsed / 1024 / 1024),
          rss: Math.round(memoryInfo.rss / 1024 / 1024),
          external: Math.round(memoryInfo.external / 1024 / 1024),
        },
        limit: this.config.maxMemoryMB,
        withinLimit: Math.round(memoryInfo.rss / 1024 / 1024) < this.config.maxMemoryMB,
        history: this.metrics.memoryUsage.slice(-10),
      },
      cpu: {
        user: Math.round(cpuUsage.user / 1000),
        system: Math.round(cpuUsage.system / 1000),
      },
      ipc: {
        totalCalls: this.metrics.ipcLatency.length,
        averageLatency: this.calculateAverageIPCLatency(),
        slowCalls: this.metrics.ipcLatency.filter(m => m.latency > this.config.ipcTimeout).length,
        errors: this.metrics.ipcLatency.filter(m => m.isError).length,
      },
      processes: {
        main: process.pid,
        renders: Array.from(this.metrics.renderProcesses.entries()).map(([id, info]) => ({
          windowId: id,
          pid: info.pid,
          age: Date.now() - info.created,
        })),
      },
      v8: {
        heapStatistics: v8.getHeapStatistics(),
      },
    };
  }

  /**
   * Calculate average IPC latency
   */
  calculateAverageIPCLatency() {
    if (this.metrics.ipcLatency.length === 0) return 0;
    
    const sum = this.metrics.ipcLatency.reduce((acc, m) => acc + m.latency, 0);
    return Math.round(sum / this.metrics.ipcLatency.length);
  }

  /**
   * Log performance metrics
   */
  logPerformanceMetrics() {
    const metrics = this.getMetrics();
    
    console.log('[Performance] === Performance Metrics ===');
    console.log(`[Performance] Startup: ${metrics.startup.time}ms (target: ${metrics.startup.target}ms) ${metrics.startup.withinTarget ? '✓' : '✗'}`);
    console.log(`[Performance] Memory: ${metrics.memory.current.rss}MB / ${metrics.memory.limit}MB ${metrics.memory.withinLimit ? '✓' : '✗'}`);
    console.log(`[Performance] CPU: User ${metrics.cpu.user}ms, System ${metrics.cpu.system}ms`);
    console.log(`[Performance] IPC: ${metrics.ipc.totalCalls} calls, avg ${metrics.ipc.averageLatency}ms, ${metrics.ipc.slowCalls} slow, ${metrics.ipc.errors} errors`);
    console.log(`[Performance] Processes: Main ${metrics.processes.main}, ${metrics.processes.renders.length} render(s)`);
    console.log('[Performance] ========================');
  }

  /**
   * Export metrics for analysis
   */
  exportMetrics() {
    return {
      timestamp: new Date().toISOString(),
      metrics: this.getMetrics(),
      config: this.config,
    };
  }

  /**
   * Cleanup on app quit
   */
  cleanup() {
    console.log('[Performance] Cleaning up performance manager...');
    
    this.stopMonitoring();
    
    // Log final metrics
    this.logPerformanceMetrics();
    
    // Clear all metrics
    this.metrics.memoryUsage = [];
    this.metrics.ipcLatency = [];
    this.metrics.renderProcesses.clear();
  }
}

// Singleton instance
let performanceManagerInstance = null;

function getPerformanceManager() {
  if (!performanceManagerInstance) {
    performanceManagerInstance = new PerformanceManager();
  }
  return performanceManagerInstance;
}

module.exports = {
  PerformanceManager,
  getPerformanceManager,
};
