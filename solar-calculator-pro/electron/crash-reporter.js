/**
 * Crash Reporter
 * 
 * Integrates Sentry for crash reporting in beta builds
 */

const { app } = require('electron');
const Sentry = require('@sentry/electron');
const betaConfig = require('../build/beta-config');
const log = require('electron-log');

class CrashReporter {
  constructor() {
    this.initialized = false;
  }

  /**
   * Initialize crash reporting
   */
  initialize() {
    if (!betaConfig.crashReporting.enabled) {
      log.info('Crash reporting is disabled');
      return;
    }

    if (!betaConfig.crashReporting.dsn) {
      log.warn('Crash reporting DSN not configured');
      return;
    }

    try {
      // Initialize Sentry
      Sentry.init({
        dsn: betaConfig.crashReporting.dsn,
        environment: betaConfig.crashReporting.environment,
        release: this.getRelease(),
        
        // Performance monitoring
        tracesSampleRate: betaConfig.crashReporting.tracesSampleRate,
        
        // Error sampling
        sampleRate: betaConfig.crashReporting.sampleRate,
        
        // Breadcrumbs
        maxBreadcrumbs: 50,
        
        // Attach stack traces
        attachStacktrace: true,
        
        // Before send hook
        beforeSend: (event, hint) => {
          return this.beforeSend(event, hint);
        },
        
        // Before breadcrumb hook
        beforeBreadcrumb: (breadcrumb, hint) => {
          return this.beforeBreadcrumb(breadcrumb, hint);
        },
      });

      // Set user context
      this.setUserContext();

      // Set tags
      this.setTags();

      this.initialized = true;
      log.info('Crash reporting initialized');
    } catch (error) {
      log.error('Failed to initialize crash reporting:', error);
    }
  }

  /**
   * Get release version
   */
  getRelease() {
    const packageJson = require('../package.json');
    return `${packageJson.name}@${packageJson.version}`;
  }

  /**
   * Set user context
   */
  setUserContext() {
    // Get user info from settings
    const userSettings = this.getUserSettings();
    
    if (userSettings) {
      Sentry.setUser({
        id: userSettings.userId || 'anonymous',
        email: userSettings.email,
        username: userSettings.username,
      });
    }
  }

  /**
   * Set tags
   */
  setTags() {
    Sentry.setTags({
      'app.version': app.getVersion(),
      'app.name': app.getName(),
      'electron.version': process.versions.electron,
      'chrome.version': process.versions.chrome,
      'node.version': process.versions.node,
      'platform': process.platform,
      'arch': process.arch,
      'beta': 'true',
    });
  }

  /**
   * Before send hook
   */
  beforeSend(event, hint) {
    // Add additional context
    event.contexts = event.contexts || {};
    
    // Add system info
    event.contexts.system = {
      platform: process.platform,
      arch: process.arch,
      memory: process.memoryUsage(),
      uptime: process.uptime(),
    };
    
    // Add app info
    event.contexts.app = {
      version: app.getVersion(),
      name: app.getName(),
      path: app.getAppPath(),
    };
    
    // Filter sensitive data
    event = this.filterSensitiveData(event);
    
    // Log crash
    log.error('Crash reported to Sentry:', {
      eventId: event.event_id,
      message: event.message,
      level: event.level,
    });
    
    return event;
  }

  /**
   * Before breadcrumb hook
   */
  beforeBreadcrumb(breadcrumb, hint) {
    // Filter sensitive breadcrumbs
    if (breadcrumb.category === 'console' && breadcrumb.level === 'log') {
      // Don't send all console.log breadcrumbs
      return null;
    }
    
    return breadcrumb;
  }

  /**
   * Filter sensitive data from events
   */
  filterSensitiveData(event) {
    // Remove sensitive keys from extra data
    const sensitiveKeys = [
      'password',
      'token',
      'apiKey',
      'secret',
      'authorization',
      'cookie',
    ];
    
    if (event.extra) {
      for (const key of sensitiveKeys) {
        if (event.extra[key]) {
          event.extra[key] = '[Filtered]';
        }
      }
    }
    
    // Filter request data
    if (event.request && event.request.headers) {
      for (const key of sensitiveKeys) {
        if (event.request.headers[key]) {
          event.request.headers[key] = '[Filtered]';
        }
      }
    }
    
    return event;
  }

  /**
   * Get user settings
   */
  getUserSettings() {
    try {
      const Store = require('electron-store');
      const store = new Store();
      return store.get('user', {});
    } catch (error) {
      log.error('Failed to get user settings:', error);
      return null;
    }
  }

  /**
   * Capture exception
   */
  captureException(error, context = {}) {
    if (!this.initialized) {
      log.error('Crash reporter not initialized');
      return;
    }

    Sentry.withScope((scope) => {
      // Add context
      if (context.tags) {
        for (const [key, value] of Object.entries(context.tags)) {
          scope.setTag(key, value);
        }
      }
      
      if (context.extra) {
        for (const [key, value] of Object.entries(context.extra)) {
          scope.setExtra(key, value);
        }
      }
      
      if (context.level) {
        scope.setLevel(context.level);
      }
      
      // Capture exception
      Sentry.captureException(error);
    });
  }

  /**
   * Capture message
   */
  captureMessage(message, level = 'info', context = {}) {
    if (!this.initialized) {
      log.error('Crash reporter not initialized');
      return;
    }

    Sentry.withScope((scope) => {
      // Add context
      if (context.tags) {
        for (const [key, value] of Object.entries(context.tags)) {
          scope.setTag(key, value);
        }
      }
      
      if (context.extra) {
        for (const [key, value] of Object.entries(context.extra)) {
          scope.setExtra(key, value);
        }
      }
      
      scope.setLevel(level);
      
      // Capture message
      Sentry.captureMessage(message);
    });
  }

  /**
   * Add breadcrumb
   */
  addBreadcrumb(breadcrumb) {
    if (!this.initialized) {
      return;
    }

    Sentry.addBreadcrumb(breadcrumb);
  }

  /**
   * Set user
   */
  setUser(user) {
    if (!this.initialized) {
      return;
    }

    Sentry.setUser(user);
  }

  /**
   * Clear user
   */
  clearUser() {
    if (!this.initialized) {
      return;
    }

    Sentry.setUser(null);
  }

  /**
   * Flush events
   */
  async flush(timeout = 2000) {
    if (!this.initialized) {
      return;
    }

    try {
      await Sentry.flush(timeout);
      log.info('Crash reports flushed');
    } catch (error) {
      log.error('Failed to flush crash reports:', error);
    }
  }

  /**
   * Close crash reporter
   */
  async close() {
    if (!this.initialized) {
      return;
    }

    try {
      await Sentry.close(2000);
      log.info('Crash reporter closed');
    } catch (error) {
      log.error('Failed to close crash reporter:', error);
    }
  }
}

// Create singleton instance
const crashReporter = new CrashReporter();

module.exports = crashReporter;
