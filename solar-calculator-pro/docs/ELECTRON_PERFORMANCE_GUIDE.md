# Electron Performance Optimization Guide

This guide covers the performance optimization features implemented in the Solar Calculator Pro Electron application.

## Overview

The application implements comprehensive performance optimization to meet the following requirements:
- **Requirement 8.1**: Application startup time < 3 seconds
- **Requirement 8.7**: Memory usage < 500MB in idle state

## Performance Manager

The Performance Manager (`electron/performance-manager.js`) provides:

### Startup Optimization

The application optimizes startup time through:

1. **Hardware Acceleration Control**
   - Configurable hardware acceleration
   - Automatic detection of optimal settings

2. **Background Throttling**
   - Reduces resource usage for background processes
   - Improves foreground performance

3. **V8 Optimization**
   - Code caching for faster subsequent starts
   - Optimized memory limits
   - Efficient garbage collection

4. **Process Priority**
   - Appropriate process priority settings
   - Platform-specific optimizations

### Memory Management

Memory is actively monitored and managed:

1. **Continuous Monitoring**
   - Memory usage checked every 30 seconds
   - Automatic alerts when limits are approached
   - Historical tracking of memory patterns

2. **Automatic Cleanup**
   - Garbage collection triggered when needed
   - Cache clearing on high memory usage
   - Process cleanup on window close

3. **Memory Limits**
   - Target: < 500MB in idle state
   - Warning threshold: 400MB
   - Critical threshold: 750MB (1.5x limit)

### IPC Optimization

Inter-Process Communication is optimized for performance:

1. **Latency Tracking**
   - All IPC calls are measured
   - Target response time: < 100ms
   - Automatic warnings for slow calls

2. **Performance Metrics**
   - Average latency calculation
   - Slow call identification
   - Error tracking

### Performance Monitoring

Real-time monitoring provides:

1. **Startup Metrics**
   - Actual startup time
   - Comparison to 3-second target
   - Success/failure indication

2. **Memory Metrics**
   - Current heap usage
   - RSS (Resident Set Size)
   - External memory
   - Historical data

3. **CPU Metrics**
   - User time
   - System time
   - Process utilization

4. **IPC Metrics**
   - Total calls
   - Average latency
   - Slow calls count
   - Error count

5. **Process Metrics**
   - Main process PID
   - Render process information
   - Process age tracking

## Resource Cleanup Manager

The Resource Cleanup Manager (`electron/resource-cleanup.js`) handles:

### Automatic Cleanup

1. **Periodic Cleanup**
   - Runs every hour by default
   - Cleans temp files, caches, and logs
   - Removes orphaned resources

2. **Lifecycle Cleanup**
   - Before app quit
   - On window close
   - On web contents destroyed

3. **Memory Pressure Cleanup**
   - Triggered when memory > 400MB
   - Aggressive cache clearing
   - Forced garbage collection

### Resource Tracking

The cleanup manager tracks:

1. **Temp Files**
   - Automatic registration
   - Age-based cleanup (24 hours default)
   - Manual cleanup on demand

2. **Timers and Intervals**
   - Automatic registration
   - Cleanup on app quit
   - Prevents memory leaks

3. **Event Listeners**
   - Tracked for cleanup
   - Removed on shutdown
   - Prevents memory leaks

4. **Caches**
   - Session caches
   - Storage data
   - Service workers

### Cleanup Tasks

Default cleanup tasks include:

1. **Temp Files**
   - Removes files older than 24 hours
   - Cleans registered temp files
   - Validates file existence

2. **Caches**
   - Clears old cache data
   - Removes storage data
   - Cleans service workers

3. **Logs**
   - Removes logs older than 7 days
   - Maintains recent logs
   - Prevents disk space issues

4. **Orphaned Resources**
   - Identifies unused resources
   - Cleans up destroyed windows
   - Removes stale references

## Usage

### Accessing Performance Metrics

From the renderer process:

```typescript
// Get current performance metrics
const metrics = await window.electronAPI.performance.getMetrics();

console.log('Startup time:', metrics.startup.time, 'ms');
console.log('Memory usage:', metrics.memory.current.rss, 'MB');
console.log('Within limits:', metrics.memory.withinLimit);
console.log('Average IPC latency:', metrics.ipc.averageLatency, 'ms');
```

### Exporting Metrics

```typescript
// Export metrics for analysis
const export = await window.electronAPI.performance.exportMetrics();

// Save to file or send to analytics
console.log('Metrics export:', export);
```

### Manual Cleanup

```typescript
// Trigger manual cleanup
await window.electronAPI.cleanup.performCleanup();

// Aggressive cleanup (when memory is high)
await window.electronAPI.cleanup.performAggressiveCleanup();

// Get cleanup statistics
const stats = await window.electronAPI.cleanup.getStatistics();
console.log('Temp files:', stats.tempFiles);
console.log('Timers:', stats.timers);
```

### Registering Temp Files

```typescript
// Register a temp file for automatic cleanup
await window.electronAPI.cleanup.registerTempFile('/path/to/temp/file.tmp');
```

### Force Garbage Collection

```typescript
// Force garbage collection (if available)
await window.electronAPI.performance.forceGC();
```

## Configuration

### Performance Manager Configuration

```javascript
{
  maxMemoryMB: 500,              // Memory limit (Requirement 8.7)
  memoryCheckInterval: 30000,    // Check every 30 seconds
  gcInterval: 60000,             // GC every 60 seconds if needed
  ipcTimeout: 100,               // IPC target response time
  preloadCriticalResources: true,
  enableHardwareAcceleration: true,
  enableBackgroundThrottling: true
}
```

### Cleanup Manager Configuration

```javascript
{
  tempFileMaxAge: 24 * 60 * 60 * 1000,  // 24 hours
  cacheMaxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  cleanupInterval: 60 * 60 * 1000,      // 1 hour
  aggressiveCleanupOnLowMemory: true
}
```

## Performance Targets

### Startup Time (Requirement 8.1)

- **Target**: < 3 seconds
- **Measured**: From app start to window ready
- **Optimization**: 
  - V8 code caching
  - Lazy loading
  - Preload optimization
  - Hardware acceleration

### Memory Usage (Requirement 8.7)

- **Target**: < 500MB in idle state
- **Measured**: RSS (Resident Set Size)
- **Optimization**:
  - Automatic garbage collection
  - Cache management
  - Resource cleanup
  - Memory monitoring

### IPC Performance

- **Target**: < 100ms response time
- **Measured**: All IPC calls
- **Optimization**:
  - Efficient handlers
  - Minimal data transfer
  - Async operations
  - Latency tracking

## Monitoring Dashboard

A performance monitoring dashboard can be accessed from the application:

1. Open Developer Tools (F12)
2. Navigate to Performance tab
3. View real-time metrics
4. Export data for analysis

## Troubleshooting

### High Memory Usage

If memory usage exceeds limits:

1. Check performance metrics
2. Review memory history
3. Trigger aggressive cleanup
4. Force garbage collection
5. Check for memory leaks

### Slow Startup

If startup time exceeds 3 seconds:

1. Check startup metrics
2. Review initialization sequence
3. Disable hardware acceleration if needed
4. Check for blocking operations
5. Review preload scripts

### Slow IPC Calls

If IPC calls are slow:

1. Check IPC metrics
2. Identify slow channels
3. Optimize handlers
4. Reduce data transfer
5. Use async operations

## Best Practices

### For Developers

1. **Register Resources**
   - Register all temp files
   - Track timers and intervals
   - Clean up event listeners

2. **Optimize IPC**
   - Keep handlers fast (< 100ms)
   - Use async operations
   - Minimize data transfer
   - Batch operations when possible

3. **Monitor Performance**
   - Check metrics regularly
   - Watch for memory leaks
   - Profile slow operations
   - Test on target hardware

4. **Clean Up Resources**
   - Remove event listeners
   - Clear timers/intervals
   - Close file handles
   - Release memory

### For Users

1. **Monitor Performance**
   - Check memory usage periodically
   - Watch for slow performance
   - Report issues with metrics

2. **Maintenance**
   - Allow periodic cleanup
   - Restart app if memory is high
   - Clear caches if needed
   - Update to latest version

## Performance Metrics Reference

### Startup Metrics

```typescript
{
  time: number,           // Actual startup time in ms
  target: 3000,          // Target startup time
  withinTarget: boolean  // Whether target was met
}
```

### Memory Metrics

```typescript
{
  current: {
    heapUsed: number,    // Heap memory in MB
    rss: number,         // Resident set size in MB
    external: number     // External memory in MB
  },
  limit: 500,           // Memory limit in MB
  withinLimit: boolean, // Whether within limit
  history: Array<{      // Recent measurements
    timestamp: number,
    heapUsed: number,
    rss: number,
    external: number
  }>
}
```

### CPU Metrics

```typescript
{
  user: number,    // User CPU time in ms
  system: number   // System CPU time in ms
}
```

### IPC Metrics

```typescript
{
  totalCalls: number,      // Total IPC calls
  averageLatency: number,  // Average latency in ms
  slowCalls: number,       // Calls > 100ms
  errors: number           // Failed calls
}
```

### Process Metrics

```typescript
{
  main: number,           // Main process PID
  renders: Array<{        // Render processes
    windowId: number,
    pid: number,
    age: number          // Process age in ms
  }>
}
```

## Conclusion

The performance optimization system ensures the application meets all performance requirements while providing comprehensive monitoring and management capabilities. Regular monitoring and maintenance will ensure optimal performance throughout the application lifecycle.
