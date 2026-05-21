/**
 * useWindowManager Hook
 * 
 * React hook for managing window state, fullscreen mode, always-on-top,
 * and multi-window functionality.
 */

import { useState, useEffect, useCallback } from 'react';

interface WindowInfo {
  id: string;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  isMaximized: boolean;
  isMinimized: boolean;
  isFullScreen: boolean;
  isAlwaysOnTop: boolean;
  isFocused: boolean;
  isVisible: boolean;
  title: string;
}

interface WindowPreferences {
  rememberWindowState: boolean;
  restoreWindowsOnStartup: boolean;
  defaultWidth: number;
  defaultHeight: number;
  defaultMinWidth: number;
  defaultMinHeight: number;
}

interface CreateWindowOptions {
  id?: string;
  type?: string;
  browserWindowOptions?: any;
  url?: string;
  rememberState?: boolean;
}

export const useWindowManager = (windowId: string = 'main') => {
  const [windowInfo, setWindowInfo] = useState<WindowInfo | null>(null);
  const [preferences, setPreferences] = useState<WindowPreferences | null>(null);
  const [allWindows, setAllWindows] = useState<WindowInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if running in Electron
  const isElectron = typeof window !== 'undefined' && window.electronAPI;

  // Fetch window info
  const fetchWindowInfo = useCallback(async () => {
    if (!isElectron) return;

    try {
      const info = await window.electronAPI.window.getInfo(windowId);
      setWindowInfo(info);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch window info');
    }
  }, [isElectron, windowId]);

  // Fetch all windows info
  const fetchAllWindows = useCallback(async () => {
    if (!isElectron) return;

    try {
      const windows = await window.electronAPI.window.getAllInfo();
      setAllWindows(windows);
    } catch (err) {
      console.error('Failed to fetch all windows:', err);
    }
  }, [isElectron]);

  // Fetch preferences
  const fetchPreferences = useCallback(async () => {
    if (!isElectron) return;

    try {
      const prefs = await window.electronAPI.window.getPreferences();
      setPreferences(prefs);
    } catch (err) {
      console.error('Failed to fetch preferences:', err);
    }
  }, [isElectron]);

  // Initialize
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([
        fetchWindowInfo(),
        fetchAllWindows(),
        fetchPreferences()
      ]);
      setLoading(false);
    };

    init();

    // Refresh window info periodically
    const interval = setInterval(() => {
      fetchWindowInfo();
      fetchAllWindows();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchWindowInfo, fetchAllWindows, fetchPreferences]);

  // Create new window
  const createWindow = useCallback(async (options: CreateWindowOptions) => {
    if (!isElectron) return { success: false, error: 'Not running in Electron' };

    try {
      const result = await window.electronAPI.window.create(options);
      if (result.success) {
        await fetchAllWindows();
      }
      return result;
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Failed to create window' };
    }
  }, [isElectron, fetchAllWindows]);

  // Focus window
  const focusWindow = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.focus(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Toggle fullscreen
  const toggleFullscreen = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false, isFullScreen: false };

    try {
      const result = await window.electronAPI.window.toggleFullscreen(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false, isFullScreen: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Set fullscreen
  const setFullscreen = useCallback(async (fullscreen: boolean, targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.setFullscreen(targetWindowId || windowId, fullscreen);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Toggle always on top
  const toggleAlwaysOnTop = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false, isAlwaysOnTop: false };

    try {
      const result = await window.electronAPI.window.toggleAlwaysOnTop(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false, isAlwaysOnTop: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Set always on top
  const setAlwaysOnTop = useCallback(async (alwaysOnTop: boolean, targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.setAlwaysOnTop(targetWindowId || windowId, alwaysOnTop);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Minimize window
  const minimizeWindow = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.minimize(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Maximize window
  const maximizeWindow = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false, isMaximized: false };

    try {
      const result = await window.electronAPI.window.maximize(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false, isMaximized: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Restore window
  const restoreWindow = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.restore(targetWindowId || windowId);
      if (result.success) {
        await fetchWindowInfo();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchWindowInfo]);

  // Close window
  const closeWindow = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.close(targetWindowId || windowId);
      if (result.success) {
        await fetchAllWindows();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId, fetchAllWindows]);

  // Update preferences
  const updatePreferences = useCallback(async (newPreferences: Partial<WindowPreferences>) => {
    if (!isElectron) return { success: false };

    try {
      const result = await window.electronAPI.window.updatePreferences(newPreferences);
      if (result.success) {
        await fetchPreferences();
      }
      return result;
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, fetchPreferences]);

  // Clear window state
  const clearWindowState = useCallback(async (targetWindowId?: string) => {
    if (!isElectron) return { success: false };

    try {
      return await window.electronAPI.window.clearState(targetWindowId || windowId);
    } catch (err) {
      return { success: false };
    }
  }, [isElectron, windowId]);

  // Clear all window states
  const clearAllWindowStates = useCallback(async () => {
    if (!isElectron) return { success: false };

    try {
      return await window.electronAPI.window.clearAllStates();
    } catch (err) {
      return { success: false };
    }
  }, [isElectron]);

  return {
    // State
    windowInfo,
    preferences,
    allWindows,
    loading,
    error,
    isElectron,

    // Actions
    createWindow,
    focusWindow,
    toggleFullscreen,
    setFullscreen,
    toggleAlwaysOnTop,
    setAlwaysOnTop,
    minimizeWindow,
    maximizeWindow,
    restoreWindow,
    closeWindow,
    updatePreferences,
    clearWindowState,
    clearAllWindowStates,

    // Refresh
    refresh: fetchWindowInfo,
    refreshAll: fetchAllWindows
  };
};

export default useWindowManager;
