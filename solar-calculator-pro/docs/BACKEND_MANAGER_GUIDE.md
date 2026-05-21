# Backend Process Manager Guide

## Overview

The Backend Process Manager is a robust system for managing the Python FastAPI backend process lifecycle within the Electron application. It provides automatic startup, health monitoring, error recovery, and graceful shutdown capabilities.

## Features

### 1. Auto-Start on App Launch
- Automatically starts the Python backend when the Electron app launches
- Detects development vs production environment
- Configures appropriate Python executable path
- Handles environment variables and working directory

### 2. Health Check Polling
- Periodic health checks every 10 seconds (configurable)
- Monitors backend availability
- Tracks last successful health check timestamp
- Emits events on health status changes

### 3. Graceful Shutdown Handling
- Attempts graceful shutdown via API endpoint
- Falls back to SIGTERM signal
- Force kills with SIGKILL if necessary
- Cleans up resources properly

### 4. Error Recovery and Restart Logic
- Automatic restart on unexpected crashes
- Configurable maximum restart attempts (default: 3)
- Exponential backoff between restart attempts
- Detailed error logging and event emission

### 5. Port Configuration
- Configurable backend port (default: 8000)
- Environment variable support
- Runtime port validation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Electron Main Process                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │           Backend Manager (EventEmitter)           │ │
│  │                                                    │ │
│  │  • Process Lifecycle Management                   │ │
│  │  • Health Check Polling                           │ │
│  │  • Error Recovery                                 │ │
│  │  • Logging & Events                               │ │
│  └────────────────────────────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Python Backend Process (FastAPI)           │ │
│  │                                                    │ │
│  │  • HTTP Server (Port 8000)                        │ │
│  │  • Health Endpoint (/health)                      │ │
│  │  • Shutdown Endpoint (/shutdown)                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Basic Usage

```javascript
const BackendManager = require('./electron/backend-manager');

// Create instance with default options
const backendManager = new BackendManager();

// Start backend
await backendManager.start();

// Check health
const isHealthy = await backendManager.checkHealth();

// Get status
const status = backendManager.getStatus();
console.log(status);
// {
//   isRunning: true,
//   port: 8000,
//   url: 'http://localhost:8000',
//   uptime: 45000,
//   lastHealthCheck: 1234567890,
//   restartAttempts: 0,
//   pid: 12345
// }

// Stop backend
await backendManager.stop();
```

### Advanced Configuration

```javascript
const backendManager = new BackendManager({
  port: 8080,                    // Custom port
  maxRetries: 40,                // Max startup retries
  retryDelay: 1500,              // Delay between retries (ms)
  healthCheckInterval: 15000,    // Health check interval (ms)
  maxRestartAttempts: 5,         // Max automatic restart attempts
  restartDelay: 3000,            // Delay before restart (ms)
});
```

### Event Handling

The Backend Manager extends EventEmitter and emits the following events:

```javascript
// Backend is starting
backendManager.on('starting', () => {
  console.log('Backend is starting...');
});

// Backend started successfully
backendManager.on('started', () => {
  console.log('Backend is ready!');
});

// Backend is stopping
backendManager.on('stopping', () => {
  console.log('Backend is shutting down...');
});

// Backend stopped
backendManager.on('stopped', ({ code, signal }) => {
  console.log(`Backend stopped with code ${code}, signal ${signal}`);
});

// Backend is restarting
backendManager.on('restarting', () => {
  console.log('Backend is restarting...');
});

// Health check failed
backendManager.on('unhealthy', () => {
  console.log('Backend health check failed!');
});

// Backend failed to start/restart
backendManager.on('failed', (error) => {
  console.error('Backend failed:', error);
});

// Process stdout
backendManager.on('stdout', (message) => {
  console.log('Backend output:', message);
});

// Process stderr
backendManager.on('stderr', (message) => {
  console.error('Backend error:', message);
});

// Log entry
backendManager.on('log', ({ timestamp, level, message }) => {
  console.log(`[${timestamp}] [${level}] ${message}`);
});

// Process error
backendManager.on('error', (error) => {
  console.error('Backend error:', error);
});
```

### Integration with Electron Main Process

```javascript
// electron/main.js
const { app, BrowserWindow } = require('electron');
const BackendManager = require('./backend-manager');

let mainWindow;
let backendManager;

async function createWindow() {
  // Create backend manager
  backendManager = new BackendManager({
    port: 8000,
    maxRestartAttempts: 3,
  });

  // Setup event handlers
  backendManager.on('started', () => {
    console.log('Backend ready, creating window...');
    
    // Create browser window
    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
        preload: path.join(__dirname, 'preload.js'),
      },
    });

    // Load frontend
    if (process.env.NODE_ENV === 'development') {
      mainWindow.loadURL('http://localhost:3000');
    } else {
      mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
    }
  });

  backendManager.on('failed', (error) => {
    console.error('Backend failed to start:', error);
    app.quit();
  });

  // Start backend
  await backendManager.start();
}

app.whenReady().then(createWindow);

app.on('before-quit', async (event) => {
  if (backendManager && backendManager.isRunning) {
    event.preventDefault();
    await backendManager.cleanup();
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

### Exposing Backend Status to Renderer

```javascript
// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend operations
  getBackendStatus: () => ipcRenderer.invoke('backend:getStatus'),
  getBackendLogs: (count) => ipcRenderer.invoke('backend:getLogs', count),
  restartBackend: () => ipcRenderer.invoke('backend:restart'),
  
  // Backend events
  onBackendStarted: (callback) => 
    ipcRenderer.on('backend:started', callback),
  onBackendStopped: (callback) => 
    ipcRenderer.on('backend:stopped', callback),
  onBackendUnhealthy: (callback) => 
    ipcRenderer.on('backend:unhealthy', callback),
});
```

```javascript
// electron/main.js - IPC handlers
const { ipcMain } = require('electron');

ipcMain.handle('backend:getStatus', () => {
  return backendManager.getStatus();
});

ipcMain.handle('backend:getLogs', (event, count) => {
  return backendManager.getLogs(count);
});

ipcMain.handle('backend:restart', async () => {
  await backendManager.restart();
  return { success: true };
});

// Forward backend events to renderer
backendManager.on('started', () => {
  mainWindow?.webContents.send('backend:started');
});

backendManager.on('stopped', (data) => {
  mainWindow?.webContents.send('backend:stopped', data);
});

backendManager.on('unhealthy', () => {
  mainWindow?.webContents.send('backend:unhealthy');
});
```

### Using in React Frontend

```typescript
// frontend/src/hooks/useBackendStatus.ts
import { useState, useEffect } from 'react';

interface BackendStatus {
  isRunning: boolean;
  port: number;
  url: string;
  uptime: number;
  lastHealthCheck: number | null;
  restartAttempts: number;
  pid: number | null;
}

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    // Get initial status
    window.electronAPI?.getBackendStatus().then(setStatus);

    // Poll for status updates
    const interval = setInterval(async () => {
      const newStatus = await window.electronAPI?.getBackendStatus();
      setStatus(newStatus);
    }, 5000);

    // Listen for backend events
    window.electronAPI?.onBackendStarted(() => {
      setIsHealthy(true);
    });

    window.electronAPI?.onBackendUnhealthy(() => {
      setIsHealthy(false);
    });

    return () => {
      clearInterval(interval);
    };
  }, []);

  const restart = async () => {
    await window.electronAPI?.restartBackend();
  };

  return { status, isHealthy, restart };
}
```

```tsx
// frontend/src/components/BackendStatusIndicator.tsx
import React from 'react';
import { useBackendStatus } from '../hooks/useBackendStatus';

export const BackendStatusIndicator: React.FC = () => {
  const { status, isHealthy, restart } = useBackendStatus();

  if (!status) return null;

  return (
    <div className="backend-status">
      <div className={`status-indicator ${isHealthy ? 'healthy' : 'unhealthy'}`}>
        {isHealthy ? '🟢' : '🔴'} Backend: {status.isRunning ? 'Running' : 'Stopped'}
      </div>
      
      {status.isRunning && (
        <div className="status-details">
          <span>Port: {status.port}</span>
          <span>Uptime: {Math.floor(status.uptime / 1000)}s</span>
          <span>PID: {status.pid}</span>
        </div>
      )}
      
      {!isHealthy && (
        <button onClick={restart}>Restart Backend</button>
      )}
    </div>
  );
};
```

## Configuration

### Environment Variables

```bash
# Backend port
BACKEND_PORT=8000

# Node environment
NODE_ENV=development  # or 'production'
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `port` | number | 8000 | Backend server port |
| `maxRetries` | number | 30 | Maximum startup retry attempts |
| `retryDelay` | number | 1000 | Delay between retries (ms) |
| `healthCheckInterval` | number | 10000 | Health check interval (ms) |
| `maxRestartAttempts` | number | 3 | Maximum automatic restart attempts |
| `restartDelay` | number | 5000 | Delay before restart (ms) |

## Error Handling

### Startup Failures

If the backend fails to start, the manager will:
1. Log the error
2. Emit 'error' event
3. Attempt restart up to `maxRestartAttempts` times
4. Emit 'failed' event if all attempts fail

### Unexpected Exits

If the backend crashes unexpectedly:
1. Log the exit code and signal
2. Emit 'stopped' event
3. Automatically attempt restart
4. Emit 'failed' event if restart limit reached

### Health Check Failures

If health checks fail:
1. Log warning
2. Emit 'unhealthy' event
3. Attempt automatic restart
4. Continue monitoring after restart

## Logging

The Backend Manager maintains an internal log buffer with the following levels:
- `debug`: Detailed diagnostic information
- `info`: General informational messages
- `warn`: Warning messages
- `error`: Error messages

### Accessing Logs

```javascript
// Get last 100 log entries
const logs = backendManager.getLogs(100);

logs.forEach(({ timestamp, level, message }) => {
  console.log(`[${timestamp}] [${level}] ${message}`);
});
```

### Log Events

```javascript
backendManager.on('log', ({ timestamp, level, message }) => {
  // Send to external logging service
  logService.log(level, message, { timestamp });
});
```

## Best Practices

1. **Always cleanup on app quit**
   ```javascript
   app.on('before-quit', async (event) => {
     event.preventDefault();
     await backendManager.cleanup();
     app.quit();
   });
   ```

2. **Handle startup failures gracefully**
   ```javascript
   backendManager.on('failed', (error) => {
     dialog.showErrorBox('Backend Error', 
       'Failed to start backend. Please check logs.');
     app.quit();
   });
   ```

3. **Monitor health in production**
   ```javascript
   backendManager.on('unhealthy', () => {
     // Notify user
     mainWindow.webContents.send('show-notification', {
       type: 'warning',
       message: 'Backend connection lost. Attempting to reconnect...'
     });
   });
   ```

4. **Provide user feedback**
   ```javascript
   backendManager.on('starting', () => {
     mainWindow.webContents.send('show-loading', 'Starting backend...');
   });

   backendManager.on('started', () => {
     mainWindow.webContents.send('hide-loading');
   });
   ```

## Troubleshooting

### Backend Won't Start

1. Check Python installation
2. Verify backend files exist
3. Check port availability
4. Review logs for errors

### Frequent Restarts

1. Check backend logs for crashes
2. Verify system resources
3. Increase restart delay
4. Check for port conflicts

### Health Checks Failing

1. Verify health endpoint exists
2. Check network connectivity
3. Increase health check timeout
4. Review backend logs

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 3.2**: THE Desktop Application SHALL den Python-Backend-Prozess automatisch starten und verwalten
- **Requirement 3.5**: WHEN die Desktop Application startet, THEN THE Desktop Application SHALL prüfen, ob das Backend erreichbar ist

## Related Documentation

- [Electron Setup Guide](./ELECTRON_SETUP_GUIDE.md)
- [Backend API Documentation](../../backend/docs/API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
