const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');
const { EventEmitter } = require('events');

/**
 * Backend Process Manager for Electron
 * 
 * Manages the Python FastAPI backend process lifecycle:
 * - Auto-start on app launch
 * - Health check polling
 * - Graceful shutdown handling
 * - Error recovery and restart logic
 * - Port configuration
 * 
 * Requirements: 3.2, 3.5
 */
class BackendManager extends EventEmitter {
  constructor(options = {}) {
    super();
    
    // Configuration
    this.port = options.port || process.env.BACKEND_PORT || 8000;
    this.maxRetries = options.maxRetries || 30;
    this.retryDelay = options.retryDelay || 1000;
    this.healthCheckInterval = options.healthCheckInterval || 10000; // 10 seconds
    this.maxRestartAttempts = options.maxRestartAttempts || 3;
    this.restartDelay = options.restartDelay || 5000; // 5 seconds
    
    // State
    this.process = null;
    this.isRunning = false;
    this.isShuttingDown = false;
    this.restartAttempts = 0;
    this.healthCheckTimer = null;
    this.lastHealthCheck = null;
    this.startTime = null;
    
    // Logging
    this.logs = [];
    this.maxLogSize = 1000;
  }

  /**
   * Get Python executable path based on environment
   */
  getPythonPath() {
    // In development, use system Python
    if (process.env.NODE_ENV === 'development') {
      return process.platform === 'win32' ? 'python' : 'python3';
    }

    // In production, use bundled Python executable
    const backendPath = path.join(process.resourcesPath, 'backend');
    return path.join(backendPath, process.platform === 'win32' ? 'main.exe' : 'main');
  }

  /**
   * Get backend directory path
   */
  getBackendPath() {
    if (process.env.NODE_ENV === 'development') {
      return path.join(__dirname, '../../backend');
    }
    return path.join(process.resourcesPath, 'backend');
  }

  /**
   * Start the backend process
   */
  async start() {
    if (this.isRunning) {
      this.log('warn', 'Backend is already running');
      return;
    }

    if (this.isShuttingDown) {
      this.log('warn', 'Backend is shutting down, cannot start');
      return;
    }

    this.log('info', 'Starting Python backend...');
    this.emit('starting');

    try {
      const pythonPath = this.getPythonPath();
      const backendPath = this.getBackendPath();

      // Spawn backend process
      if (process.env.NODE_ENV === 'development') {
        // Development: Run with uvicorn
        this.process = spawn(
          pythonPath,
          ['-m', 'uvicorn', 'main:app', '--port', this.port.toString(), '--host', '127.0.0.1'],
          {
            cwd: backendPath,
            env: { 
              ...process.env, 
              PYTHONUNBUFFERED: '1',
              PORT: this.port.toString()
            },
          }
        );
      } else {
        // Production: Run bundled executable
        this.process = spawn(pythonPath, [], {
          cwd: backendPath,
          env: { 
            ...process.env, 
            PORT: this.port.toString() 
          },
        });
      }

      // Setup process event handlers
      this.setupProcessHandlers();

      // Wait for backend to be ready
      await this.waitForBackend();

      this.isRunning = true;
      this.startTime = Date.now();
      this.restartAttempts = 0;
      
      this.log('info', 'Backend started successfully');
      this.emit('started');

      // Start health check polling
      this.startHealthCheckPolling();

    } catch (error) {
      this.log('error', `Failed to start backend: ${error.message}`);
      this.emit('error', error);
      
      // Attempt restart if within retry limit
      await this.handleStartupFailure(error);
    }
  }

  /**
   * Setup process event handlers
   */
  setupProcessHandlers() {
    if (!this.process) return;

    // Capture stdout
    this.process.stdout.on('data', (data) => {
      const message = data.toString().trim();
      this.log('info', `Backend: ${message}`);
      this.emit('stdout', message);
    });

    // Capture stderr
    this.process.stderr.on('data', (data) => {
      const message = data.toString().trim();
      this.log('error', `Backend Error: ${message}`);
      this.emit('stderr', message);
    });

    // Handle process exit
    this.process.on('close', (code, signal) => {
      this.log('info', `Backend process exited with code ${code}, signal ${signal}`);
      this.isRunning = false;
      this.process = null;
      
      this.emit('stopped', { code, signal });

      // Attempt restart if not intentional shutdown
      if (!this.isShuttingDown && code !== 0) {
        this.handleUnexpectedExit(code, signal);
      }
    });

    // Handle process errors
    this.process.on('error', (error) => {
      this.log('error', `Backend process error: ${error.message}`);
      this.emit('error', error);
    });
  }

  /**
   * Wait for backend to be ready by polling health endpoint
   */
  async waitForBackend() {
    this.log('info', 'Waiting for backend to be ready...');

    for (let i = 0; i < this.maxRetries; i++) {
      try {
        const response = await axios.get(`http://localhost:${this.port}/health`, {
          timeout: 2000,
        });

        if (response.status === 200) {
          this.log('info', 'Backend is ready!');
          this.lastHealthCheck = Date.now();
          return;
        }
      } catch (error) {
        // Backend not ready yet, wait and retry
        this.log('debug', `Health check attempt ${i + 1}/${this.maxRetries} failed, retrying...`);
        await new Promise((resolve) => setTimeout(resolve, this.retryDelay));
      }
    }

    throw new Error('Backend failed to start within timeout period');
  }

  /**
   * Start periodic health check polling
   */
  startHealthCheckPolling() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }

    this.healthCheckTimer = setInterval(async () => {
      const isHealthy = await this.checkHealth();
      
      if (!isHealthy && this.isRunning) {
        this.log('warn', 'Backend health check failed');
        this.emit('unhealthy');
        
        // Attempt restart
        await this.restart();
      }
    }, this.healthCheckInterval);
  }

  /**
   * Stop health check polling
   */
  stopHealthCheckPolling() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }
  }

  /**
   * Check backend health
   */
  async checkHealth() {
    try {
      const response = await axios.get(`${this.getUrl()}/health`, { 
        timeout: 2000 
      });
      
      if (response.status === 200) {
        this.lastHealthCheck = Date.now();
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  }

  /**
   * Gracefully stop the backend process
   */
  async stop() {
    if (!this.isRunning && !this.process) {
      this.log('info', 'Backend is not running');
      return;
    }

    this.isShuttingDown = true;
    this.log('info', 'Stopping backend gracefully...');
    this.emit('stopping');

    // Stop health check polling
    this.stopHealthCheckPolling();

    if (this.process) {
      // Try graceful shutdown first
      try {
        await axios.post(`${this.getUrl()}/shutdown`, {}, { timeout: 2000 });
        this.log('info', 'Sent graceful shutdown signal to backend');
      } catch (error) {
        this.log('warn', 'Could not send graceful shutdown signal, forcing termination');
      }

      // Wait a bit for graceful shutdown
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Force kill if still running
      if (this.process) {
        this.log('info', 'Force killing backend process');
        this.process.kill('SIGTERM');
        
        // Wait for process to exit
        await new Promise((resolve) => setTimeout(resolve, 1000));
        
        // Force kill if still alive
        if (this.process) {
          this.process.kill('SIGKILL');
        }
      }
    }

    this.process = null;
    this.isRunning = false;
    this.isShuttingDown = false;
    
    this.log('info', 'Backend stopped');
    this.emit('stopped', { code: 0, signal: 'SIGTERM' });
  }

  /**
   * Restart the backend process
   */
  async restart() {
    this.log('info', 'Restarting backend...');
    this.emit('restarting');

    await this.stop();
    await new Promise((resolve) => setTimeout(resolve, this.restartDelay));
    await this.start();
  }

  /**
   * Handle startup failure with retry logic
   */
  async handleStartupFailure(error) {
    this.restartAttempts++;

    if (this.restartAttempts < this.maxRestartAttempts) {
      this.log('warn', `Startup failed, attempting restart ${this.restartAttempts}/${this.maxRestartAttempts}`);
      await new Promise((resolve) => setTimeout(resolve, this.restartDelay));
      await this.start();
    } else {
      this.log('error', 'Max restart attempts reached, giving up');
      this.emit('failed', error);
    }
  }

  /**
   * Handle unexpected process exit
   */
  async handleUnexpectedExit(code, signal) {
    this.log('warn', `Backend exited unexpectedly (code: ${code}, signal: ${signal})`);
    
    this.restartAttempts++;

    if (this.restartAttempts < this.maxRestartAttempts) {
      this.log('info', `Attempting automatic restart ${this.restartAttempts}/${this.maxRestartAttempts}`);
      await new Promise((resolve) => setTimeout(resolve, this.restartDelay));
      await this.start();
    } else {
      this.log('error', 'Max restart attempts reached after unexpected exit');
      this.emit('failed', new Error('Backend crashed and could not be restarted'));
    }
  }

  /**
   * Get backend URL
   */
  getUrl() {
    return `http://localhost:${this.port}`;
  }

  /**
   * Get backend status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      isShuttingDown: this.isShuttingDown,
      port: this.port,
      url: this.getUrl(),
      uptime: this.startTime ? Date.now() - this.startTime : 0,
      lastHealthCheck: this.lastHealthCheck,
      restartAttempts: this.restartAttempts,
      pid: this.process ? this.process.pid : null,
    };
  }

  /**
   * Get recent logs
   */
  getLogs(count = 100) {
    return this.logs.slice(-count);
  }

  /**
   * Log message with timestamp
   */
  log(level, message) {
    const timestamp = new Date().toISOString();
    const logEntry = { timestamp, level, message };
    
    this.logs.push(logEntry);
    
    // Trim logs if too large
    if (this.logs.length > this.maxLogSize) {
      this.logs = this.logs.slice(-this.maxLogSize);
    }

    // Console output
    const consoleMethod = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'log';
    console[consoleMethod](`[BackendManager] [${level.toUpperCase()}] ${message}`);
    
    this.emit('log', logEntry);
  }

  /**
   * Configure backend port
   */
  setPort(port) {
    if (this.isRunning) {
      throw new Error('Cannot change port while backend is running');
    }
    this.port = port;
    this.log('info', `Backend port configured to ${port}`);
  }

  /**
   * Clean up resources
   */
  async cleanup() {
    this.log('info', 'Cleaning up backend manager...');
    this.stopHealthCheckPolling();
    await this.stop();
    this.removeAllListeners();
  }
}

module.exports = BackendManager;
