/**
 * Performance Manager Demo
 * 
 * This demo shows how to use the performance manager and cleanup manager
 * to monitor and optimize Electron application performance.
 * 
 * Run with: node demo-performance.js
 */

const { app, BrowserWindow } = require('electron');
const { getPerformanceManager } = require('./performance-manager');
const { getCleanupManager } = require('./resource-cleanup');

let mainWindow;
let performanceManager;
let cleanupManager;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  mainWindow.loadURL('data:text/html,<h1>Performance Demo</h1>');
}

async function runDemo() {
  console.log('=== Performance Manager Demo ===\n');

  // Initialize performance manager
  console.log('1. Initializing Performance Manager...');
  performanceManager = getPerformanceManager();
  performanceManager.initializeBeforeReady();

  // Wait for app ready
  await app.whenReady();
  
  performanceManager.initializeAfterReady();
  console.log('   ✓ Performance manager initialized\n');

  // Initialize cleanup manager
  console.log('2. Initializing Cleanup Manager...');
  cleanupManager = getCleanupManager();
  cleanupManager.initialize();
  console.log('   ✓ Cleanup manager initialized\n');

  // Create window
  console.log('3. Creating Window...');
  createWindow();
  performanceManager.optimizeWindow(mainWindow);
  console.log('   ✓ Window created and optimized\n');

  // Wait a bit for metrics to accumulate
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Display performance metrics
  console.log('4. Performance Metrics:');
  console.log('   ─────────────────────────────────────');
  performanceManager.logPerformanceMetrics();
  console.log('   ─────────────────────────────────────\n');

  // Get detailed metrics
  console.log('5. Detailed Metrics:');
  const metrics = performanceManager.getMetrics();
  
  console.log('   Startup:');
  console.log(`     Time: ${metrics.startup.time}ms`);
  console.log(`     Target: ${metrics.startup.target}ms`);
  console.log(`     Status: ${metrics.startup.withinTarget ? '✓ PASS' : '✗ FAIL'}\n`);
  
  console.log('   Memory:');
  console.log(`     Heap Used: ${metrics.memory.current.heapUsed}MB`);
  console.log(`     RSS: ${metrics.memory.current.rss}MB`);
  console.log(`     External: ${metrics.memory.current.external}MB`);
  console.log(`     Limit: ${metrics.memory.limit}MB`);
  console.log(`     Status: ${metrics.memory.withinLimit ? '✓ PASS' : '✗ FAIL'}\n`);
  
  console.log('   CPU:');
  console.log(`     User: ${metrics.cpu.user}ms`);
  console.log(`     System: ${metrics.cpu.system}ms\n`);
  
  console.log('   IPC:');
  console.log(`     Total Calls: ${metrics.ipc.totalCalls}`);
  console.log(`     Average Latency: ${metrics.ipc.averageLatency}ms`);
  console.log(`     Slow Calls: ${metrics.ipc.slowCalls}`);
  console.log(`     Errors: ${metrics.ipc.errors}\n`);

  // Display cleanup statistics
  console.log('6. Cleanup Statistics:');
  const stats = cleanupManager.getStatistics();
  console.log(`     Temp Files: ${stats.tempFiles}`);
  console.log(`     Timers: ${stats.timers}`);
  console.log(`     Intervals: ${stats.intervals}`);
  console.log(`     Event Listeners: ${stats.eventListeners}`);
  console.log(`     Cleanup Tasks: ${stats.cleanupTasks}\n`);

  // Simulate some operations
  console.log('7. Simulating Operations...');
  
  // Register some temp files
  console.log('   Registering temp files...');
  cleanupManager.registerTempFile('/tmp/test1.tmp');
  cleanupManager.registerTempFile('/tmp/test2.tmp');
  cleanupManager.registerTempFile('/tmp/test3.tmp');
  console.log('   ✓ 3 temp files registered\n');

  // Simulate memory usage
  console.log('   Simulating memory usage...');
  const largeArray = new Array(1000000).fill('data');
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log('   ✓ Memory allocated\n');

  // Check memory after allocation
  console.log('8. Memory After Allocation:');
  const afterMetrics = performanceManager.getMetrics();
  console.log(`     Heap Used: ${afterMetrics.memory.current.heapUsed}MB`);
  console.log(`     RSS: ${afterMetrics.memory.current.rss}MB`);
  console.log(`     Status: ${afterMetrics.memory.withinLimit ? '✓ PASS' : '✗ FAIL'}\n`);

  // Perform cleanup
  console.log('9. Performing Cleanup...');
  await cleanupManager.performPeriodicCleanup();
  console.log('   ✓ Cleanup completed\n');

  // Force garbage collection
  console.log('10. Forcing Garbage Collection...');
  performanceManager.performGarbageCollection();
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log('    ✓ GC completed\n');

  // Check memory after cleanup
  console.log('11. Memory After Cleanup:');
  const finalMetrics = performanceManager.getMetrics();
  console.log(`     Heap Used: ${finalMetrics.memory.current.heapUsed}MB`);
  console.log(`     RSS: ${finalMetrics.memory.current.rss}MB`);
  console.log(`     Status: ${finalMetrics.memory.withinLimit ? '✓ PASS' : '✗ FAIL'}\n`);

  // Export metrics
  console.log('12. Exporting Metrics...');
  const exportData = performanceManager.exportMetrics();
  console.log('    ✓ Metrics exported');
  console.log(`    Timestamp: ${exportData.timestamp}`);
  console.log(`    Data size: ${JSON.stringify(exportData).length} bytes\n`);

  // Summary
  console.log('=== Demo Summary ===');
  console.log(`Startup Time: ${metrics.startup.time}ms (target: ${metrics.startup.target}ms) ${metrics.startup.withinTarget ? '✓' : '✗'}`);
  console.log(`Memory Usage: ${finalMetrics.memory.current.rss}MB (limit: ${finalMetrics.memory.limit}MB) ${finalMetrics.memory.withinLimit ? '✓' : '✗'}`);
  console.log(`IPC Performance: ${metrics.ipc.averageLatency}ms average latency`);
  console.log(`Cleanup: ${stats.cleanupTasks} tasks registered`);
  console.log('\nDemo completed successfully!\n');

  // Keep app running for a bit
  console.log('Keeping app running for 5 seconds...');
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Cleanup and quit
  console.log('Cleaning up and quitting...');
  performanceManager.cleanup();
  await cleanupManager.performFullCleanup();
  app.quit();
}

// Run demo
runDemo().catch(error => {
  console.error('Demo failed:', error);
  app.quit();
});

// Handle app events
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
