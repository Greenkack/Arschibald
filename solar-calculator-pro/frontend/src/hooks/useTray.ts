/**
 * React hook for system tray integration
 * Provides easy access to tray functionality from React components
 */

import { useCallback, useEffect, useState } from 'react';

export interface TrayNotificationOptions {
  title: string;
  body: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  actions?: Array<{
    text: string;
    callback: () => void;
  }>;
}

export interface TrayProject {
  id: string;
  name: string;
  date?: string;
}

export interface TrayQuickAction {
  id: string;
  label: string;
  route: string;
  enabled: boolean;
}

export interface TrayPreferences {
  minimizeToTray: boolean;
  closeToTray: boolean;
  showNotifications: boolean;
  notificationSound: boolean;
  startMinimized: boolean;
  recentProjects: TrayProject[];
  quickActions: TrayQuickAction[];
}

export type TrayIconState = 'normal' | 'busy' | 'error' | 'warning';

/**
 * Hook for system tray operations
 */
export function useTray() {
  const [isAvailable, setIsAvailable] = useState<boolean>(false);
  const [preferences, setPreferences] = useState<TrayPreferences | null>(null);

  // Check if tray is available
  useEffect(() => {
    const checkAvailability = async () => {
      if (window.electronAPI?.tray) {
        const available = await window.electronAPI.tray.isAvailable();
        setIsAvailable(available);
      }
    };
    checkAvailability();
  }, []);

  // Load preferences
  useEffect(() => {
    const loadPreferences = async () => {
      if (window.electronAPI?.tray) {
        const prefs = await window.electronAPI.tray.getPreferences();
        setPreferences(prefs);
      }
    };
    loadPreferences();
  }, []);

  /**
   * Show a tray notification
   */
  const showNotification = useCallback(
    async (options: TrayNotificationOptions) => {
      if (!window.electronAPI?.tray) {
        console.warn('Tray API not available');
        return;
      }

      const { title, body, type = 'info', actions } = options;
      await window.electronAPI.tray.showNotification(title, body, type, actions);
    },
    []
  );

  /**
   * Show a success notification
   */
  const showSuccess = useCallback(
    async (title: string, body: string) => {
      await showNotification({ title, body, type: 'success' });
    },
    [showNotification]
  );

  /**
   * Show an error notification
   */
  const showError = useCallback(
    async (title: string, body: string) => {
      await showNotification({ title, body, type: 'error' });
    },
    [showNotification]
  );

  /**
   * Show a warning notification
   */
  const showWarning = useCallback(
    async (title: string, body: string) => {
      await showNotification({ title, body, type: 'warning' });
    },
    [showNotification]
  );

  /**
   * Show an info notification
   */
  const showInfo = useCallback(
    async (title: string, body: string) => {
      await showNotification({ title, body, type: 'info' });
    },
    [showNotification]
  );

  /**
   * Update tray icon state
   */
  const updateIcon = useCallback(async (state: TrayIconState) => {
    if (!window.electronAPI?.tray) {
      console.warn('Tray API not available');
      return;
    }

    await window.electronAPI.tray.updateIcon(state);
  }, []);

  /**
   * Flash tray icon to get attention
   */
  const flash = useCallback(async (duration: number = 3000) => {
    if (!window.electronAPI?.tray) {
      console.warn('Tray API not available');
      return;
    }

    await window.electronAPI.tray.flash(duration);
  }, []);

  /**
   * Update tray tooltip
   */
  const updateTooltip = useCallback(async (tooltip: string) => {
    if (!window.electronAPI?.tray) {
      console.warn('Tray API not available');
      return;
    }

    await window.electronAPI.tray.updateTooltip(tooltip);
  }, []);

  /**
   * Add a recent project to tray menu
   */
  const addRecentProject = useCallback(async (project: TrayProject) => {
    if (!window.electronAPI?.tray) {
      console.warn('Tray API not available');
      return;
    }

    await window.electronAPI.tray.addRecentProject(project);
    
    // Reload preferences to get updated recent projects
    const prefs = await window.electronAPI.tray.getPreferences();
    setPreferences(prefs);
  }, []);

  /**
   * Update quick actions
   */
  const updateQuickActions = useCallback(
    async (quickActions: TrayQuickAction[]) => {
      if (!window.electronAPI?.tray) {
        console.warn('Tray API not available');
        return;
      }

      await window.electronAPI.tray.updateQuickActions(quickActions);
      
      // Reload preferences
      const prefs = await window.electronAPI.tray.getPreferences();
      setPreferences(prefs);
    },
    []
  );

  /**
   * Update tray preferences
   */
  const updatePreferences = useCallback(
    async (newPreferences: Partial<TrayPreferences>) => {
      if (!window.electronAPI?.tray) {
        console.warn('Tray API not available');
        return;
      }

      await window.electronAPI.tray.updatePreferences(newPreferences);
      
      // Reload preferences
      const prefs = await window.electronAPI.tray.getPreferences();
      setPreferences(prefs);
    },
    []
  );

  /**
   * Reload preferences from tray
   */
  const reloadPreferences = useCallback(async () => {
    if (!window.electronAPI?.tray) {
      console.warn('Tray API not available');
      return;
    }

    const prefs = await window.electronAPI.tray.getPreferences();
    setPreferences(prefs);
  }, []);

  return {
    // State
    isAvailable,
    preferences,

    // Notifications
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // Icon management
    updateIcon,
    flash,
    updateTooltip,

    // Recent projects
    addRecentProject,

    // Quick actions
    updateQuickActions,

    // Preferences
    updatePreferences,
    reloadPreferences,
  };
}

/**
 * Hook for tracking operation status with tray icon
 * Automatically updates icon state and shows notifications
 */
export function useTrayOperation() {
  const { updateIcon, updateTooltip, showSuccess, showError } = useTray();

  /**
   * Execute an operation with automatic tray status updates
   */
  const executeOperation = useCallback(
    async <T,>(
      operation: () => Promise<T>,
      options: {
        busyMessage?: string;
        successTitle?: string;
        successMessage?: string;
        errorTitle?: string;
        showSuccessNotification?: boolean;
        showErrorNotification?: boolean;
      } = {}
    ): Promise<T> => {
      const {
        busyMessage = 'Processing...',
        successTitle = 'Success',
        successMessage = 'Operation completed successfully',
        errorTitle = 'Error',
        showSuccessNotification = true,
        showErrorNotification = true,
      } = options;

      try {
        // Set busy state
        await updateIcon('busy');
        await updateTooltip(busyMessage);

        // Execute operation
        const result = await operation();

        // Set success state
        await updateIcon('normal');
        await updateTooltip('Solar Calculator Pro');

        if (showSuccessNotification) {
          await showSuccess(successTitle, successMessage);
        }

        return result;
      } catch (error) {
        // Set error state
        await updateIcon('error');

        if (showErrorNotification) {
          await showError(
            errorTitle,
            error instanceof Error ? error.message : 'An error occurred'
          );
        }

        // Reset icon after delay
        setTimeout(async () => {
          await updateIcon('normal');
          await updateTooltip('Solar Calculator Pro');
        }, 10000);

        throw error;
      }
    },
    [updateIcon, updateTooltip, showSuccess, showError]
  );

  return {
    executeOperation,
  };
}

/**
 * Hook for managing tray preferences UI
 */
export function useTrayPreferences() {
  const { preferences, updatePreferences, reloadPreferences } = useTray();
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Toggle a boolean preference
   */
  const togglePreference = useCallback(
    async (key: keyof TrayPreferences) => {
      if (!preferences) return;

      setIsLoading(true);
      try {
        await updatePreferences({
          [key]: !preferences[key],
        });
      } finally {
        setIsLoading(false);
      }
    },
    [preferences, updatePreferences]
  );

  /**
   * Update a preference value
   */
  const setPreference = useCallback(
    async <K extends keyof TrayPreferences>(
      key: K,
      value: TrayPreferences[K]
    ) => {
      setIsLoading(true);
      try {
        await updatePreferences({
          [key]: value,
        });
      } finally {
        setIsLoading(false);
      }
    },
    [updatePreferences]
  );

  return {
    preferences,
    isLoading,
    togglePreference,
    setPreference,
    reloadPreferences,
  };
}
