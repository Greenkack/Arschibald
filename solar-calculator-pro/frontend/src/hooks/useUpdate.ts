/**
 * useUpdate Hook
 * 
 * Custom hook for managing application updates
 */

import { useState, useEffect, useCallback } from 'react';

interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  releaseNotesUrl?: string;
  currentVersion: string;
  updateChannel?: string;
}

interface ProgressInfo {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}

interface UpdatePreferences {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkOnStartup: boolean;
  checkInterval: number;
  updateChannel: string;
  skipVersion: string | null;
  notifyOnNoUpdate: boolean;
}

interface UseUpdateReturn {
  // State
  updateAvailable: boolean;
  updateInfo: UpdateInfo | null;
  downloading: boolean;
  downloadProgress: ProgressInfo | null;
  updateReady: boolean;
  checking: boolean;
  error: string | null;
  preferences: UpdatePreferences | null;

  // Actions
  checkForUpdates: () => Promise<void>;
  downloadUpdate: () => Promise<void>;
  installUpdate: () => Promise<void>;
  skipVersion: () => Promise<void>;
  cancelDownload: () => Promise<void>;
  setPreferences: (prefs: UpdatePreferences) => Promise<void>;
  clearSkipVersion: () => Promise<void>;
}

export const useUpdate = (): UseUpdateReturn => {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<ProgressInfo | null>(null);
  const [updateReady, setUpdateReady] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferencesState] = useState<UpdatePreferences | null>(null);

  // Load initial preferences
  useEffect(() => {
    loadPreferences();
    setupEventListeners();

    return () => {
      removeEventListeners();
    };
  }, []);

  const loadPreferences = async () => {
    try {
      if (window.electronAPI?.getUpdateInfo) {
        const info = await window.electronAPI.getUpdateInfo();
        setPreferencesState(info.preferences);
      }
    } catch (err) {
      console.error('Failed to load update preferences:', err);
    }
  };

  const setupEventListeners = () => {
    if (!window.electronAPI) return;

    // Update available
    window.electronAPI.onUpdateAvailable?.((info: UpdateInfo) => {
      setUpdateAvailable(true);
      setUpdateInfo(info);
      setChecking(false);
      setError(null);
    });

    // Update not available
    window.electronAPI.onUpdateNotAvailable?.(() => {
      setUpdateAvailable(false);
      setUpdateInfo(null);
      setChecking(false);
      setError(null);
    });

    // Download progress
    window.electronAPI.onUpdateProgress?.((progress: ProgressInfo) => {
      setDownloading(true);
      setDownloadProgress(progress);
      setError(null);
    });

    // Update downloaded
    window.electronAPI.onUpdateDownloaded?.((info: UpdateInfo) => {
      setDownloading(false);
      setDownloadProgress(null);
      setUpdateReady(true);
      setUpdateInfo(info);
      setError(null);
    });

    // Update error
    window.electronAPI.onUpdateError?.((err: Error) => {
      setError(err.message || 'An error occurred during update');
      setChecking(false);
      setDownloading(false);
      setDownloadProgress(null);
    });

    // Download cancelled
    window.electronAPI.onUpdateCancelled?.(() => {
      setDownloading(false);
      setDownloadProgress(null);
      setError(null);
    });
  };

  const removeEventListeners = () => {
    // Cleanup if needed
  };

  const checkForUpdates = useCallback(async () => {
    if (!window.electronAPI?.checkForUpdates) {
      setError('Update functionality not available');
      return;
    }

    setChecking(true);
    setError(null);

    try {
      await window.electronAPI.checkForUpdates();
    } catch (err: any) {
      setError(err.message || 'Failed to check for updates');
      setChecking(false);
    }
  }, []);

  const downloadUpdate = useCallback(async () => {
    if (!window.electronAPI?.downloadUpdate) {
      setError('Download functionality not available');
      return;
    }

    setError(null);

    try {
      await window.electronAPI.downloadUpdate();
    } catch (err: any) {
      setError(err.message || 'Failed to download update');
    }
  }, []);

  const installUpdate = useCallback(async () => {
    if (!window.electronAPI?.installUpdate) {
      setError('Install functionality not available');
      return;
    }

    try {
      await window.electronAPI.installUpdate();
    } catch (err: any) {
      setError(err.message || 'Failed to install update');
    }
  }, []);

  const skipVersion = useCallback(async () => {
    if (!window.electronAPI?.setUpdatePreferences || !updateInfo) {
      return;
    }

    try {
      await window.electronAPI.setUpdatePreferences({
        skipVersion: updateInfo.version
      });
      setUpdateAvailable(false);
      setUpdateInfo(null);
      await loadPreferences();
    } catch (err: any) {
      setError(err.message || 'Failed to skip version');
    }
  }, [updateInfo]);

  const cancelDownload = useCallback(async () => {
    if (!window.electronAPI?.cancelDownload) {
      return;
    }

    try {
      await window.electronAPI.cancelDownload();
      setDownloading(false);
      setDownloadProgress(null);
    } catch (err: any) {
      setError(err.message || 'Failed to cancel download');
    }
  }, []);

  const setPreferences = useCallback(async (prefs: UpdatePreferences) => {
    if (!window.electronAPI?.setUpdatePreferences) {
      setError('Preferences functionality not available');
      return;
    }

    try {
      await window.electronAPI.setUpdatePreferences(prefs);
      setPreferencesState(prefs);
    } catch (err: any) {
      setError(err.message || 'Failed to save preferences');
      throw err;
    }
  }, []);

  const clearSkipVersion = useCallback(async () => {
    if (!window.electronAPI?.clearSkipVersion) {
      return;
    }

    try {
      await window.electronAPI.clearSkipVersion();
      await loadPreferences();
    } catch (err: any) {
      setError(err.message || 'Failed to clear skip version');
    }
  }, []);

  return {
    // State
    updateAvailable,
    updateInfo,
    downloading,
    downloadProgress,
    updateReady,
    checking,
    error,
    preferences,

    // Actions
    checkForUpdates,
    downloadUpdate,
    installUpdate,
    skipVersion,
    cancelDownload,
    setPreferences,
    clearSkipVersion
  };
};
