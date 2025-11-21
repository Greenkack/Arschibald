/**
 * React Hook for Native Notifications
 * 
 * Provides easy access to Electron's native notification system
 * with TypeScript support and React integration.
 */

import { useCallback, useEffect, useState } from 'react';

interface NotificationPreferences {
  enabled: boolean;
  calculationComplete: boolean;
  updateAvailable: boolean;
  errors: boolean;
  warnings: boolean;
  info: boolean;
  sound: boolean;
  doNotDisturb: boolean;
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
}

interface NotificationHistory {
  title: string;
  body: string;
  type: string;
  timestamp: string;
  data?: any;
}

interface NotificationResult {
  success: boolean;
}

export const useNotifications = () => {
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [history, setHistory] = useState<NotificationHistory[]>([]);
  const [isSupported, setIsSupported] = useState(false);

  // Check if notifications are supported
  useEffect(() => {
    setIsSupported(typeof window !== 'undefined' && 'electronAPI' in window && 'notifications' in (window as any).electronAPI);
  }, []);

  // Load preferences on mount
  useEffect(() => {
    if (isSupported) {
      loadPreferences();
      loadHistory();
    }
  }, [isSupported]);

  const loadPreferences = useCallback(async () => {
    if (!isSupported) return;
    
    try {
      const prefs = await (window as any).electronAPI.notifications.getPreferences();
      setPreferences(prefs);
    } catch (error) {
      console.error('Failed to load notification preferences:', error);
    }
  }, [isSupported]);

  const loadHistory = useCallback(async (limit: number = 20) => {
    if (!isSupported) return;
    
    try {
      const hist = await (window as any).electronAPI.notifications.getHistory(limit);
      setHistory(hist);
    } catch (error) {
      console.error('Failed to load notification history:', error);
    }
  }, [isSupported]);

  const showCalculationComplete = useCallback(async (
    projectName: string,
    calculationType: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showCalculationComplete(
        projectName,
        calculationType
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show calculation complete notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showUpdateAvailable = useCallback(async (
    version: string,
    releaseNotes?: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showUpdateAvailable(
        version,
        releaseNotes
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show update available notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showError = useCallback(async (
    errorMessage: string,
    errorDetails?: any
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showError(
        errorMessage,
        errorDetails
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show error notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showWarning = useCallback(async (
    warningMessage: string,
    details?: any
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showWarning(
        warningMessage,
        details
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show warning notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showInfo = useCallback(async (
    infoMessage: string,
    details?: any
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showInfo(
        infoMessage,
        details
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show info notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showPDFComplete = useCallback(async (
    fileName: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showPDFComplete(fileName);
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show PDF complete notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showExportComplete = useCallback(async (
    exportType: string,
    fileName: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showExportComplete(
        exportType,
        fileName
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show export complete notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showBackupComplete = useCallback(async (
    backupName: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showBackupComplete(backupName);
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show backup complete notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showSyncComplete = useCallback(async (
    itemCount: number
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showSyncComplete(itemCount);
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show sync complete notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const showCustom = useCallback(async (
    title: string,
    body: string,
    options?: any
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.showCustom(
        title,
        body,
        options
      );
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to show custom notification:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  const updatePreferences = useCallback(async (
    newPreferences: Partial<NotificationPreferences>
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.updatePreferences(newPreferences);
      await loadPreferences();
      return result;
    } catch (error) {
      console.error('Failed to update notification preferences:', error);
      return { success: false };
    }
  }, [isSupported, loadPreferences]);

  const setEnabled = useCallback(async (enabled: boolean): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.setEnabled(enabled);
      await loadPreferences();
      return result;
    } catch (error) {
      console.error('Failed to set notification enabled state:', error);
      return { success: false };
    }
  }, [isSupported, loadPreferences]);

  const setDoNotDisturb = useCallback(async (enabled: boolean): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.setDoNotDisturb(enabled);
      await loadPreferences();
      return result;
    } catch (error) {
      console.error('Failed to set Do Not Disturb:', error);
      return { success: false };
    }
  }, [isSupported, loadPreferences]);

  const setQuietHours = useCallback(async (
    enabled: boolean,
    start: string,
    end: string
  ): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.setQuietHours(
        enabled,
        start,
        end
      );
      await loadPreferences();
      return result;
    } catch (error) {
      console.error('Failed to set quiet hours:', error);
      return { success: false };
    }
  }, [isSupported, loadPreferences]);

  const clearHistory = useCallback(async (): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.clearHistory();
      setHistory([]);
      return result;
    } catch (error) {
      console.error('Failed to clear notification history:', error);
      return { success: false };
    }
  }, [isSupported]);

  const test = useCallback(async (): Promise<NotificationResult> => {
    if (!isSupported) return { success: false };
    
    try {
      const result = await (window as any).electronAPI.notifications.test();
      await loadHistory();
      return result;
    } catch (error) {
      console.error('Failed to test notifications:', error);
      return { success: false };
    }
  }, [isSupported, loadHistory]);

  return {
    isSupported,
    preferences,
    history,
    showCalculationComplete,
    showUpdateAvailable,
    showError,
    showWarning,
    showInfo,
    showPDFComplete,
    showExportComplete,
    showBackupComplete,
    showSyncComplete,
    showCustom,
    updatePreferences,
    setEnabled,
    setDoNotDisturb,
    setQuietHours,
    clearHistory,
    loadHistory,
    test
  };
};
