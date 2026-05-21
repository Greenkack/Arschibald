# Electron Performance Quick Reference

## Performance Targets

| Metric | Target | Requirement |
|--------|--------|-------------|
| Startup Time | < 3 seconds | 8.1 |
| Memory Usage (Idle) | < 500MB | 8.7 |
| IPC Response Time | < 100ms | 8.1 |

## Quick Commands

### Get Performance Metrics

```typescript
const metrics = await window.electronAPI.performance.getMetrics();
```

### Check Startup Time

```typescript
const { startup } = await window.electronAPI.performance.getMetrics();
console.log(`Startup: ${startup.time}ms (target: ${startup.target}ms)`);
console.log(`Within target: ${startup.withinTarget ? 'YES' : 'NO'}`);
```

### Check Memory Usage

```typescript
const { memory } = await window.electronAPI.performance.getMetrics();
console.log(`Memory: ${memory.current.rss}MB / ${memory.limit}MB`);
console.log(`Within limit: ${memory.withinLimit ? 'YES' : 'NO'}`);
```

### Force Cleanup

```typescript
// Normal cleanup
await window.electronAPI.cleanup.performCleanup();

// Aggressive cleanup (high memory)
await window.electronAPI.cleanup.performAggressiveCleanup();
```

### Force Garbage Collection

```typescript
await window.electronAPI.performance.forceGC();
```

### Register Temp File

```typescript
await window.electronAPI.cleanup.registerTempFile(filePath);
```

### Export Metrics

```typescript
const export = await window.electronAPI.performance.exportMetrics();
// Save or analyze export data
```

## Performance Monitoring

### Real-time Monitoring

```typescript
// Poll metrics every 5 seconds
setInterval(async () => {
  const metrics = await window.electronAPI.performance.getMetrics();
  
  // Check memory
  if (!metrics.memory.withinLimit) {
    console.warn('Memory limit exceeded!');
    await window.electronAPI.cleanup.performAggressiveCleanup();
  }
  
  // Check IPC performance
  if (metrics.ipc.slowCalls > 10) {
    console.warn('Many slow IPC calls detected');
  }
}, 5000);
```

### Memory Monitoring

```typescript
const { memory } = await window.electronAPI.performance.getMetrics();

// Current usage
console.log('Heap:', memory.current.heapUsed, 'MB');
console.log('RSS:', memory.current.rss, 'MB');
console.log('External:', memory.current.external, 'MB');

// History (last 10 measurements)
memory.history.forEach(m => {
  console.log(`${new Date(m.timestamp).toISOString()}: ${m.rss}MB`);
});
```

### IPC Monitoring

```typescript
const { ipc } = await window.electronAPI.performance.getMetrics();

console.log('Total calls:', ipc.totalCalls);
console.log('Average latency:', ipc.averageLatency, 'ms');
console.log('Slow calls (>100ms):', ipc.slowCalls);
console.log('Errors:', ipc.errors);
```

## Cleanup Operations

### Get Cleanup Statistics

```typescript
const stats = await window.electronAPI.cleanup.getStatistics();

console.log('Temp files:', stats.tempFiles);
console.log('Timers:', stats.timers);
console.log('Intervals:', stats.intervals);
console.log('Event listeners:', stats.eventListeners);
console.log('Cleanup tasks:', stats.cleanupTasks);
```

### Manual Cleanup Trigger

```typescript
// Trigger periodic cleanup manually
await window.electronAPI.cleanup.performCleanup();

// Check memory after cleanup
const metrics = await window.electronAPI.performance.getMetrics();
console.log('Memory after cleanup:', metrics.memory.current.rss, 'MB');
```

## Configuration

### Performance Manager

```javascript
// In electron/performance-manager.js
config: {
  maxMemoryMB: 500,              // Memory limit
  memoryCheckInterval: 30000,    // Check interval
  gcInterval: 60000,             // GC interval
  ipcTimeout: 100,               // IPC timeout
  preloadCriticalResources: true,
  enableHardwareAcceleration: true,
  enableBackgroundThrottling: true
}
```

### Cleanup Manager

```javascript
// In electron/resource-cleanup.js
config: {
  tempFileMaxAge: 24 * 60 * 60 * 1000,  // 24 hours
  cacheMaxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  cleanupInterval: 60 * 60 * 1000,      // 1 hour
  aggressiveCleanupOnLowMemory: true
}
```

## Troubleshooting

### High Memory Usage

```typescript
// 1. Check current usage
const metrics = await window.electronAPI.performance.getMetrics();
console.log('Memory:', metrics.memory.current.rss, 'MB');

// 2. Trigger aggressive cleanup
await window.electronAPI.cleanup.performAggressiveCleanup();

// 3. Force GC
await window.electronAPI.performance.forceGC();

// 4. Check again
const after = await window.electronAPI.performance.getMetrics();
console.log('Memory after cleanup:', after.memory.current.rss, 'MB');
```

### Slow Startup

```typescript
// Check startup time
const { startup } = await window.electronAPI.performance.getMetrics();

if (!startup.withinTarget) {
  console.warn(`Startup took ${startup.time}ms (target: ${startup.target}ms)`);
  // Review initialization sequence
  // Check for blocking operations
  // Consider disabling hardware acceleration
}
```

### Slow IPC Calls

```typescript
// Monitor IPC performance
const { ipc } = await window.electronAPI.performance.getMetrics();

if (ipc.averageLatency > 100) {
  console.warn(`Average IPC latency: ${ipc.averageLatency}ms`);
  // Optimize handlers
  // Reduce data transfer
  // Use async operations
}

if (ipc.slowCalls > 0) {
  console.warn(`${ipc.slowCalls} slow IPC calls detected`);
  // Check specific channels
  // Profile slow operations
}
```

## Best Practices

### Resource Management

```typescript
// Always register temp files
const tempFile = '/path/to/temp.tmp';
await window.electronAPI.cleanup.registerTempFile(tempFile);

// Clean up after use
// File will be automatically cleaned after 24 hours
```

### Memory Management

```typescript
// Monitor memory in long-running operations
async function longOperation() {
  const before = await window.electronAPI.performance.getMetrics();
  
  // Perform operation
  await doWork();
  
  const after = await window.electronAPI.performance.getMetrics();
  const increase = after.memory.current.rss - before.memory.current.rss;
  
  if (increase > 50) {
    console.warn(`Operation increased memory by ${increase}MB`);
    await window.electronAPI.cleanup.performCleanup();
  }
}
```

### IPC Optimization

```typescript
// Keep IPC handlers fast
ipcMain.handle('fast-operation', async () => {
  // Should complete in < 100ms
  return quickResult();
});

// Use async for slow operations
ipcMain.handle('slow-operation', async () => {
  // Long-running operation
  return await slowOperation();
});

// Batch operations
ipcMain.handle('batch-operation', async (event, items) => {
  // Process multiple items at once
  return await Promise.all(items.map(processItem));
});
```

## Metrics Export Format

```typescript
{
  timestamp: "2024-01-01T12:00:00.000Z",
  metrics: {
    startup: { time: 2500, target: 3000, withinTarget: true },
    memory: {
      current: { heapUsed: 150, rss: 350, external: 10 },
      limit: 500,
      withinLimit: true,
      history: [...]
    },
    cpu: { user: 1000, system: 500 },
    ipc: {
      totalCalls: 1000,
      averageLatency: 50,
      slowCalls: 5,
      errors: 0
    },
    processes: {
      main: 12345,
      renders: [{ windowId: 1, pid: 12346, age: 60000 }]
    },
    v8: { heapStatistics: {...} }
  },
  config: {
    maxMemoryMB: 500,
    memoryCheckInterval: 30000,
    ...
  }
}
```

## Common Issues

### Issue: Memory keeps growing

**Solution:**
```typescript
// 1. Check for memory leaks
const metrics = await window.electronAPI.performance.getMetrics();
console.log('Memory history:', metrics.memory.history);

// 2. Trigger cleanup
await window.electronAPI.cleanup.performAggressiveCleanup();

// 3. Force GC
await window.electronAPI.performance.forceGC();

// 4. Check cleanup stats
const stats = await window.electronAPI.cleanup.getStatistics();
console.log('Resources:', stats);
```

### Issue: Slow startup

**Solution:**
```typescript
// Check startup metrics
const { startup } = await window.electronAPI.performance.getMetrics();

// If slow, try:
// 1. Disable hardware acceleration (in config)
// 2. Reduce preload operations
// 3. Lazy load non-critical features
// 4. Check for blocking operations
```

### Issue: IPC calls timing out

**Solution:**
```typescript
// Monitor IPC performance
const { ipc } = await window.electronAPI.performance.getMetrics();

// Optimize slow handlers:
// 1. Use async operations
// 2. Reduce data transfer
// 3. Batch operations
// 4. Cache results
```

## Performance Checklist

- [ ] Startup time < 3 seconds
- [ ] Memory usage < 500MB in idle
- [ ] IPC calls < 100ms average
- [ ] No memory leaks
- [ ] Temp files cleaned up
- [ ] Caches managed
- [ ] Resources released
- [ ] Metrics monitored
- [ ] Cleanup scheduled
- [ ] GC running when needed
