# Backend Manager Quick Reference

## Quick Start

```javascript
const BackendManager = require('./electron/backend-manager');

const backendManager = new BackendManager();
await backendManager.start();
```

## Configuration

```javascript
new BackendManager({
  port: 8000,                    // Backend port
  maxRetries: 30,                // Startup retries
  retryDelay: 1000,              // Retry delay (ms)
  healthCheckInterval: 10000,    // Health check interval (ms)
  maxRestartAttempts: 3,         // Max auto-restart attempts
  restartDelay: 5000,            // Restart delay (ms)
});
```

## Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `start()` | Start backend process | `Promise<void>` |
| `stop()` | Stop backend gracefully | `Promise<void>` |
| `restart()` | Restart backend | `Promise<void>` |
| `checkHealth()` | Check backend health | `Promise<boolean>` |
| `getStatus()` | Get backend status | `Object` |
| `getLogs(count)` | Get recent logs | `Array` |
| `getUrl()` | Get backend URL | `string` |
| `setPort(port)` | Set backend port | `void` |
| `cleanup()` | Clean up resources | `Promise<void>` |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `starting` | - | Backend is starting |
| `started` | - | Backend started successfully |
| `stopping` | - | Backend is stopping |
| `stopped` | `{ code, signal }` | Backend stopped |
| `restarting` | - | Backend is restarting |
| `unhealthy` | - | Health check failed |
| `failed` | `Error` | Backend failed to start/restart |
| `stdout` | `string` | Process stdout |
| `stderr` | `string` | Process stderr |
| `log` | `{ timestamp, level, message }` | Log entry |
| `error` | `Error` | Process error |

## Status Object

```javascript
{
  isRunning: boolean,
  isShuttingDown: boolean,
  port: number,
  url: string,
  uptime: number,              // milliseconds
  lastHealthCheck: number,     // timestamp
  restartAttempts: number,
  pid: number | null,
}
```

## Common Patterns

### Basic Setup

```javascript
const backendManager = new BackendManager();

backendManager.on('started', () => {
  console.log('Backend ready!');
});

backendManager.on('failed', (error) => {
  console.error('Backend failed:', error);
  app.quit();
});

await backendManager.start();
```

### Graceful Shutdown

```javascript
app.on('before-quit', async (event) => {
  event.preventDefault();
  await backendManager.cleanup();
  app.quit();
});
```

### Health Monitoring

```javascript
backendManager.on('unhealthy', () => {
  console.warn('Backend unhealthy, restarting...');
});

backendManager.on('restarting', () => {
  console.log('Backend restarting...');
});
```

### IPC Integration

```javascript
// Main process
ipcMain.handle('backend:status', () => {
  return backendManager.getStatus();
});

ipcMain.handle('backend:restart', async () => {
  await backendManager.restart();
});

// Preload
contextBridge.exposeInMainWorld('electronAPI', {
  getBackendStatus: () => ipcRenderer.invoke('backend:status'),
  restartBackend: () => ipcRenderer.invoke('backend:restart'),
});

// Renderer
const status = await window.electronAPI.getBackendStatus();
await window.electronAPI.restartBackend();
```

## Environment Variables

```bash
BACKEND_PORT=8000
NODE_ENV=development
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python installation and port availability |
| Frequent restarts | Review backend logs, check system resources |
| Health checks failing | Verify health endpoint, check network |
| Port conflicts | Change port configuration |

## Requirements

- **3.2**: Auto-start and manage Python backend process
- **3.5**: Check backend availability on startup

## See Also

- [Backend Manager Guide](./BACKEND_MANAGER_GUIDE.md)
- [Electron Setup Guide](./ELECTRON_SETUP_QUICK_REFERENCE.md)
