/**
 * Native Notifications Manager for Electron
 * 
 * Provides native desktop notifications for:
 * - Calculation completion
 * - Update availability
 * - Error notifications
 * - Custom notifications
 * 
 * Features:
 * - User preferences for notification types
 * - Sound support
 * - Action buttons
 * - Notification history
 * - Do Not Disturb mode
 */

const { Notification, nativeImage } = require('electron');
const path = require('path');
const Store = require('electron-store');

class NotificationManager {
  constructor() {
    this.store = new Store({
      name: 'notification-preferences',
      defaults: {
        enabled: true,
        calculationComplete: true,
        updateAvailable: true,
        errors: true,
        warnings: true,
        info: false,
        sound: true,
        doNotDisturb: false,
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        },
        history: []
      }
    });

    this.notificationHistory = [];
    this.maxHistorySize = 50;
  }

  /**
   * Check if notifications are currently allowed
   */
  canShowNotification() {
    if (!this.store.get('enabled')) {
      return false;
    }

    if (this.store.get('doNotDisturb')) {
      return false;
    }

    // Check quiet hours
    const quietHours = this.store.get('quietHours');
    if (quietHours.enabled) {
      const now = new Date();
      const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
      
      if (currentTime >= quietHours.start || currentTime <= quietHours.end) {
        return false;
      }
    }

    return true;
  }

  /**
   * Show calculation complete notification
   */
  showCalculationComplete(projectName, calculationType) {
    if (!this.store.get('calculationComplete')) {
      return null;
    }

    const title = 'Berechnung abgeschlossen';
    const body = `${calculationType}-Berechnung für "${projectName}" wurde erfolgreich abgeschlossen.`;
    
    return this.show({
      title,
      body,
      type: 'calculation',
      icon: this.getIcon('success'),
      urgency: 'normal',
      actions: [
        {
          type: 'button',
          text: 'Ergebnisse anzeigen'
        }
      ],
      data: {
        projectName,
        calculationType
      }
    });
  }

  /**
   * Show update available notification
   */
  showUpdateAvailable(version, releaseNotes) {
    if (!this.store.get('updateAvailable')) {
      return null;
    }

    const title = 'Update verfügbar';
    const body = `Version ${version} ist verfügbar. Klicken Sie hier, um mehr zu erfahren.`;
    
    return this.show({
      title,
      body,
      type: 'update',
      icon: this.getIcon('update'),
      urgency: 'normal',
      actions: [
        {
          type: 'button',
          text: 'Jetzt aktualisieren'
        },
        {
          type: 'button',
          text: 'Später erinnern'
        }
      ],
      data: {
        version,
        releaseNotes
      }
    });
  }

  /**
   * Show error notification
   */
  showError(errorMessage, errorDetails = null) {
    if (!this.store.get('errors')) {
      return null;
    }

    const title = 'Fehler aufgetreten';
    const body = errorMessage;
    
    return this.show({
      title,
      body,
      type: 'error',
      icon: this.getIcon('error'),
      urgency: 'critical',
      sound: 'error',
      actions: [
        {
          type: 'button',
          text: 'Details anzeigen'
        }
      ],
      data: {
        errorMessage,
        errorDetails
      }
    });
  }

  /**
   * Show warning notification
   */
  showWarning(warningMessage, details = null) {
    if (!this.store.get('warnings')) {
      return null;
    }

    const title = 'Warnung';
    const body = warningMessage;
    
    return this.show({
      title,
      body,
      type: 'warning',
      icon: this.getIcon('warning'),
      urgency: 'normal',
      sound: 'warning',
      data: {
        warningMessage,
        details
      }
    });
  }

  /**
   * Show info notification
   */
  showInfo(infoMessage, details = null) {
    if (!this.store.get('info')) {
      return null;
    }

    const title = 'Information';
    const body = infoMessage;
    
    return this.show({
      title,
      body,
      type: 'info',
      icon: this.getIcon('info'),
      urgency: 'low',
      data: {
        infoMessage,
        details
      }
    });
  }

  /**
   * Show PDF generation complete notification
   */
  showPDFComplete(fileName) {
    const title = 'PDF erstellt';
    const body = `Die PDF-Datei "${fileName}" wurde erfolgreich erstellt.`;
    
    return this.show({
      title,
      body,
      type: 'pdf',
      icon: this.getIcon('success'),
      urgency: 'normal',
      actions: [
        {
          type: 'button',
          text: 'PDF öffnen'
        }
      ],
      data: {
        fileName
      }
    });
  }

  /**
   * Show export complete notification
   */
  showExportComplete(exportType, fileName) {
    const title = 'Export abgeschlossen';
    const body = `${exportType}-Export "${fileName}" wurde erfolgreich abgeschlossen.`;
    
    return this.show({
      title,
      body,
      type: 'export',
      icon: this.getIcon('success'),
      urgency: 'normal',
      actions: [
        {
          type: 'button',
          text: 'Datei öffnen'
        }
      ],
      data: {
        exportType,
        fileName
      }
    });
  }

  /**
   * Show backup complete notification
   */
  showBackupComplete(backupName) {
    const title = 'Backup erstellt';
    const body = `Backup "${backupName}" wurde erfolgreich erstellt.`;
    
    return this.show({
      title,
      body,
      type: 'backup',
      icon: this.getIcon('success'),
      urgency: 'low'
    });
  }

  /**
   * Show sync complete notification
   */
  showSyncComplete(itemCount) {
    const title = 'Synchronisierung abgeschlossen';
    const body = `${itemCount} Elemente wurden erfolgreich synchronisiert.`;
    
    return this.show({
      title,
      body,
      type: 'sync',
      icon: this.getIcon('success'),
      urgency: 'low'
    });
  }

  /**
   * Show custom notification
   */
  showCustom(title, body, options = {}) {
    return this.show({
      title,
      body,
      type: 'custom',
      icon: options.icon || this.getIcon('info'),
      urgency: options.urgency || 'normal',
      sound: options.sound,
      actions: options.actions || [],
      data: options.data || {}
    });
  }

  /**
   * Core notification display method
   */
  show(options) {
    if (!this.canShowNotification()) {
      console.log('Notification suppressed:', options.title);
      return null;
    }

    try {
      const notification = new Notification({
        title: options.title,
        body: options.body,
        icon: options.icon,
        urgency: options.urgency || 'normal',
        silent: !this.store.get('sound'),
        timeoutType: 'default',
        actions: options.actions || []
      });

      // Store notification data for click handling
      notification.notificationData = options.data || {};
      notification.notificationType = options.type;

      // Add to history
      this.addToHistory({
        title: options.title,
        body: options.body,
        type: options.type,
        timestamp: new Date().toISOString(),
        data: options.data
      });

      // Show notification
      notification.show();

      return notification;
    } catch (error) {
      console.error('Failed to show notification:', error);
      return null;
    }
  }

  /**
   * Get icon for notification type
   */
  getIcon(type) {
    const iconMap = {
      success: 'success.png',
      error: 'error.png',
      warning: 'warning.png',
      info: 'info.png',
      update: 'update.png'
    };

    const iconFile = iconMap[type] || 'info.png';
    const iconPath = path.join(__dirname, '../assets/icons', iconFile);

    try {
      return nativeImage.createFromPath(iconPath);
    } catch (error) {
      console.warn('Icon not found:', iconPath);
      return null;
    }
  }

  /**
   * Add notification to history
   */
  addToHistory(notification) {
    this.notificationHistory.unshift(notification);

    // Limit history size
    if (this.notificationHistory.length > this.maxHistorySize) {
      this.notificationHistory = this.notificationHistory.slice(0, this.maxHistorySize);
    }

    // Persist to store
    this.store.set('history', this.notificationHistory);
  }

  /**
   * Get notification history
   */
  getHistory(limit = 20) {
    return this.notificationHistory.slice(0, limit);
  }

  /**
   * Clear notification history
   */
  clearHistory() {
    this.notificationHistory = [];
    this.store.set('history', []);
  }

  /**
   * Get notification preferences
   */
  getPreferences() {
    return {
      enabled: this.store.get('enabled'),
      calculationComplete: this.store.get('calculationComplete'),
      updateAvailable: this.store.get('updateAvailable'),
      errors: this.store.get('errors'),
      warnings: this.store.get('warnings'),
      info: this.store.get('info'),
      sound: this.store.get('sound'),
      doNotDisturb: this.store.get('doNotDisturb'),
      quietHours: this.store.get('quietHours')
    };
  }

  /**
   * Update notification preferences
   */
  updatePreferences(preferences) {
    Object.keys(preferences).forEach(key => {
      if (this.store.has(key)) {
        this.store.set(key, preferences[key]);
      }
    });
  }

  /**
   * Enable/disable all notifications
   */
  setEnabled(enabled) {
    this.store.set('enabled', enabled);
  }

  /**
   * Enable/disable Do Not Disturb mode
   */
  setDoNotDisturb(enabled) {
    this.store.set('doNotDisturb', enabled);
  }

  /**
   * Set quiet hours
   */
  setQuietHours(enabled, start, end) {
    this.store.set('quietHours', {
      enabled,
      start,
      end
    });
  }

  /**
   * Test notification system
   */
  test() {
    return this.showCustom(
      'Test-Benachrichtigung',
      'Dies ist eine Test-Benachrichtigung. Wenn Sie diese sehen, funktioniert das Benachrichtigungssystem korrekt.',
      {
        urgency: 'normal',
        icon: this.getIcon('info')
      }
    );
  }
}

module.exports = NotificationManager;
