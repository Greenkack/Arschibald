/**
 * Deep Linking System for Solar Calculator Pro
 * 
 * Handles custom URL protocol (solarcalc://) for deep linking functionality
 * Enables opening projects, navigating to specific pages, and email link integration
 */

const { app, dialog } = require('electron');
const path = require('path');
const url = require('url');

class DeepLinkManager {
  constructor() {
    this.protocol = 'solarcalc';
    this.mainWindow = null;
    this.pendingUrl = null;
    this.isReady = false;
    this.handlers = new Map();
    
    // Register default handlers
    this.registerDefaultHandlers();
  }

  /**
   * Initialize deep linking system
   * @param {BrowserWindow} mainWindow - Main application window
   */
  initialize(mainWindow) {
    this.mainWindow = mainWindow;
    this.isReady = true;

    // Process any pending URL that was received before window was ready
    if (this.pendingUrl) {
      this.handleDeepLink(this.pendingUrl);
      this.pendingUrl = null;
    }
  }

  /**
   * Register the custom protocol with the OS
   * Must be called before app is ready
   */
  registerProtocol() {
    // Set as default protocol client
    if (process.defaultApp) {
      if (process.argv.length >= 2) {
        app.setAsDefaultProtocolClient(this.protocol, process.execPath, [
          path.resolve(process.argv[1])
        ]);
      }
    } else {
      app.setAsDefaultProtocolClient(this.protocol);
    }

    console.log(`Registered protocol: ${this.protocol}://`);
  }

  /**
   * Handle deep link URL
   * @param {string} urlString - The deep link URL to handle
   */
  handleDeepLink(urlString) {
    console.log('Handling deep link:', urlString);

    // If window is not ready, store URL for later processing
    if (!this.isReady || !this.mainWindow) {
      console.log('Window not ready, storing URL for later');
      this.pendingUrl = urlString;
      return;
    }

    try {
      // Parse the URL
      const parsedUrl = url.parse(urlString, true);
      
      // Extract action and parameters
      const action = parsedUrl.hostname || parsedUrl.pathname?.replace(/^\/+/, '');
      const params = parsedUrl.query || {};
      const pathSegments = parsedUrl.pathname?.split('/').filter(Boolean) || [];

      console.log('Parsed deep link:', { action, params, pathSegments });

      // Get handler for this action
      const handler = this.handlers.get(action);
      
      if (handler) {
        // Focus window
        if (this.mainWindow.isMinimized()) {
          this.mainWindow.restore();
        }
        this.mainWindow.focus();

        // Execute handler
        handler(params, pathSegments);
      } else {
        console.warn(`No handler registered for action: ${action}`);
        this.showUnknownActionDialog(action);
      }
    } catch (error) {
      console.error('Error handling deep link:', error);
      this.showErrorDialog(error.message);
    }
  }

  /**
   * Register a deep link handler
   * @param {string} action - The action name (e.g., 'open-project')
   * @param {Function} handler - Handler function (params, pathSegments) => void
   */
  registerHandler(action, handler) {
    this.handlers.set(action, handler);
    console.log(`Registered deep link handler: ${action}`);
  }

  /**
   * Unregister a deep link handler
   * @param {string} action - The action name to unregister
   */
  unregisterHandler(action) {
    this.handlers.delete(action);
    console.log(`Unregistered deep link handler: ${action}`);
  }

  /**
   * Register default handlers for common actions
   */
  registerDefaultHandlers() {
    // Open project by ID
    this.registerHandler('open-project', (params, pathSegments) => {
      const projectId = params.id || pathSegments[0];
      if (projectId) {
        this.sendToRenderer('deep-link:open-project', { projectId });
      } else {
        this.showErrorDialog('Project ID is required');
      }
    });

    // Open project by path
    this.registerHandler('open-project-path', (params) => {
      const projectPath = params.path;
      if (projectPath) {
        this.sendToRenderer('deep-link:open-project-path', { projectPath });
      } else {
        this.showErrorDialog('Project path is required');
      }
    });

    // Navigate to specific page
    this.registerHandler('navigate', (params, pathSegments) => {
      const page = params.page || pathSegments[0];
      if (page) {
        this.sendToRenderer('deep-link:navigate', { page, params });
      } else {
        this.showErrorDialog('Page parameter is required');
      }
    });

    // Open solar calculator with pre-filled data
    this.registerHandler('solar-calculator', (params) => {
      this.sendToRenderer('deep-link:solar-calculator', { params });
    });

    // Open heat pump calculator with pre-filled data
    this.registerHandler('heat-pump', (params) => {
      this.sendToRenderer('deep-link:heat-pump', { params });
    });

    // Open specific customer in CRM
    this.registerHandler('customer', (params, pathSegments) => {
      const customerId = params.id || pathSegments[0];
      if (customerId) {
        this.sendToRenderer('deep-link:customer', { customerId });
      } else {
        this.showErrorDialog('Customer ID is required');
      }
    });

    // Open specific offer
    this.registerHandler('offer', (params, pathSegments) => {
      const offerId = params.id || pathSegments[0];
      if (offerId) {
        this.sendToRenderer('deep-link:offer', { offerId });
      } else {
        this.showErrorDialog('Offer ID is required');
      }
    });

    // Generate PDF for project
    this.registerHandler('generate-pdf', (params, pathSegments) => {
      const projectId = params.project || pathSegments[0];
      const templateId = params.template;
      if (projectId) {
        this.sendToRenderer('deep-link:generate-pdf', { projectId, templateId });
      } else {
        this.showErrorDialog('Project ID is required');
      }
    });

    // Import data from file
    this.registerHandler('import', (params) => {
      const filePath = params.file;
      const importType = params.type;
      if (filePath) {
        this.sendToRenderer('deep-link:import', { filePath, importType });
      } else {
        this.showErrorDialog('File path is required');
      }
    });

    // Email integration - open compose with pre-filled data
    this.registerHandler('email', (params) => {
      const to = params.to;
      const subject = params.subject;
      const body = params.body;
      const attachmentId = params.attachment;
      
      this.sendToRenderer('deep-link:email', { to, subject, body, attachmentId });
    });

    // Share project via email
    this.registerHandler('share-project', (params, pathSegments) => {
      const projectId = params.id || pathSegments[0];
      const email = params.email;
      
      if (projectId) {
        this.sendToRenderer('deep-link:share-project', { projectId, email });
      } else {
        this.showErrorDialog('Project ID is required');
      }
    });

    // Open settings page
    this.registerHandler('settings', (params) => {
      const section = params.section;
      this.sendToRenderer('deep-link:settings', { section });
    });

    // Open dashboard
    this.registerHandler('dashboard', (params) => {
      this.sendToRenderer('deep-link:dashboard', { params });
    });

    // Create new project
    this.registerHandler('new-project', (params) => {
      const projectType = params.type;
      this.sendToRenderer('deep-link:new-project', { projectType, params });
    });

    // Open 3D visualization
    this.registerHandler('3d-view', (params, pathSegments) => {
      const projectId = params.project || pathSegments[0];
      if (projectId) {
        this.sendToRenderer('deep-link:3d-view', { projectId });
      } else {
        this.showErrorDialog('Project ID is required');
      }
    });

    // Open price matrix
    this.registerHandler('price-matrix', (params) => {
      const matrixId = params.id;
      this.sendToRenderer('deep-link:price-matrix', { matrixId });
    });

    // Open product catalog
    this.registerHandler('products', (params) => {
      const category = params.category;
      const search = params.search;
      this.sendToRenderer('deep-link:products', { category, search });
    });

    // Authentication/Login
    this.registerHandler('login', (params) => {
      const token = params.token;
      const redirect = params.redirect;
      this.sendToRenderer('deep-link:login', { token, redirect });
    });

    // Password reset
    this.registerHandler('reset-password', (params) => {
      const token = params.token;
      if (token) {
        this.sendToRenderer('deep-link:reset-password', { token });
      } else {
        this.showErrorDialog('Reset token is required');
      }
    });

    // Email verification
    this.registerHandler('verify-email', (params) => {
      const token = params.token;
      if (token) {
        this.sendToRenderer('deep-link:verify-email', { token });
      } else {
        this.showErrorDialog('Verification token is required');
      }
    });
  }

  /**
   * Send message to renderer process
   * @param {string} channel - IPC channel name
   * @param {Object} data - Data to send
   */
  sendToRenderer(channel, data) {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send(channel, data);
    }
  }

  /**
   * Show error dialog
   * @param {string} message - Error message
   */
  showErrorDialog(message) {
    dialog.showErrorBox(
      'Deep Link Error',
      `Failed to process deep link:\n\n${message}`
    );
  }

  /**
   * Show unknown action dialog
   * @param {string} action - Unknown action name
   */
  showUnknownActionDialog(action) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'warning',
      title: 'Unknown Deep Link Action',
      message: `Unknown action: ${action}`,
      detail: 'This deep link action is not recognized by the application.',
      buttons: ['OK']
    });
  }

  /**
   * Generate a deep link URL
   * @param {string} action - Action name
   * @param {Object} params - URL parameters
   * @param {Array} pathSegments - Additional path segments
   * @returns {string} Deep link URL
   */
  generateDeepLink(action, params = {}, pathSegments = []) {
    let urlString = `${this.protocol}://${action}`;
    
    // Add path segments
    if (pathSegments.length > 0) {
      urlString += '/' + pathSegments.join('/');
    }
    
    // Add query parameters
    const queryString = new URLSearchParams(params).toString();
    if (queryString) {
      urlString += '?' + queryString;
    }
    
    return urlString;
  }

  /**
   * Copy deep link to clipboard
   * @param {string} action - Action name
   * @param {Object} params - URL parameters
   * @param {Array} pathSegments - Additional path segments
   */
  copyDeepLinkToClipboard(action, params = {}, pathSegments = []) {
    const { clipboard } = require('electron');
    const deepLink = this.generateDeepLink(action, params, pathSegments);
    clipboard.writeText(deepLink);
    return deepLink;
  }

  /**
   * Test deep link functionality
   * @param {string} urlString - Deep link URL to test
   */
  testDeepLink(urlString) {
    console.log('Testing deep link:', urlString);
    this.handleDeepLink(urlString);
  }

  /**
   * Get all registered handlers
   * @returns {Array} List of registered action names
   */
  getRegisteredHandlers() {
    return Array.from(this.handlers.keys());
  }

  /**
   * Check if protocol is registered
   * @returns {boolean} True if protocol is registered
   */
  isProtocolRegistered() {
    return app.isDefaultProtocolClient(this.protocol);
  }

  /**
   * Unregister protocol
   */
  unregisterProtocol() {
    app.removeAsDefaultProtocolClient(this.protocol);
    console.log(`Unregistered protocol: ${this.protocol}://`);
  }
}

// Create singleton instance
const deepLinkManager = new DeepLinkManager();

module.exports = deepLinkManager;
