/**
 * React hook for Electron API
 * 
 * Provides easy access to Electron functionality with proper
 * TypeScript types and React lifecycle management.
 */

import { useEffect, useState, useCallback } from 'react';

/**
 * Check if running in Electron environment
 */
export function useIsElectron(): boolean {
  return typeof window !== 'undefined' && window.electronAPI?.isElectron();
}

/**
 * Hook for file operations
 */
export function useFileDialog() {
  const isElectron = useIsElectron();

  const selectFile = useCallback(async () => {
    if (!isElectron) return null;
    return await window.electronAPI.selectFile();
  }, [isElectron]);

  const saveFile = useCallback(async (options: any) => {
    if (!isElectron) return null;
    return await window.electronAPI.saveFile(options);
  }, [isElectron]);

  const selectDirectory = useCallback(async () => {
    if (!isElectron) return null;
    return await window.electronAPI.selectDirectory();
  }, [isElectron]);

  return {
    selectFile,
    saveFile,
    selectDirectory,
    isElectron
  };
}

/**
 * Hook for backend communication
 */
export function useBackend() {
  const isElectron = useIsElectron();
  const [backendUrl, setBackendUrl] = useState<string | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean>(false);

  useEffect(() => {
    if (!isElectron) return;

    const fetchBackendUrl = async () => {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url);
    };

    const checkHealth = async () => {
      const healthy = await window.electronAPI.checkBackendHealth();
      setIsHealthy(healthy);
    };

    fetchBackendUrl();
    checkHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, [isElectron]);

  return {
    backendUrl,
    isHealthy,
    isElectron
  };
}

/**
 * Hook for auto-updates
 */
export function useAutoUpdater() {
  const isElectron = useIsElectron();
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState<any>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [updateReady, setUpdateReady] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isElectron) return;

    const unsubAvailable = window.electronAPI.onUpdateAvailable((data) => {
      setUpdateAvailable(true);
      setUpdateInfo(data);
      setChecking(false);
    });

    const unsubProgress = window.electronAPI.onUpdateProgress((data) => {
      setDownloading(true);
      setDownloadProgress(data.percent);
    });

    const unsubDownloaded = window.electronAPI.onUpdateDownloaded((data) => {
      setDownloading(false);
      setUpdateReady(true);
      setUpdateInfo(data);
    });

    const unsubError = window.electronAPI.onUpdateError((data) => {
      setError(data.message);
      setChecking(false);
      setDownloading(false);
    });

    const unsubChecking = window.electronAPI.onUpdateChecking(() => {
      setChecking(true);
      setError(null);
    });

    return () => {
      unsubAvailable();
      unsubProgress();
      unsubDownloaded();
      unsubError();
      unsubChecking();
    };
  }, [isElectron]);

  const checkForUpdates = useCallback(async () => {
    if (!isElectron) return;
    setChecking(true);
    setError(null);
    await window.electronAPI.checkForUpdates();
  }, [isElectron]);

  const downloadUpdate = useCallback(async () => {
    if (!isElectron) return;
    setError(null);
    await window.electronAPI.downloadUpdate();
  }, [isElectron]);

  const installUpdate = useCallback(() => {
    if (!isElectron) return;
    window.electronAPI.installUpdate();
  }, [isElectron]);

  return {
    updateAvailable,
    updateInfo,
    downloading,
    downloadProgress,
    updateReady,
    checking,
    error,
    checkForUpdates,
    downloadUpdate,
    installUpdate,
    isElectron
  };
}

/**
 * Hook for menu/tray actions
 */
export function useMenuActions(
  onNavigate?: (route: string) => void,
  onAction?: (action: string, data?: any) => void
) {
  const isElectron = useIsElectron();

  useEffect(() => {
    if (!isElectron) return;

    const unsubNav = onNavigate
      ? window.electronAPI.onNavigate(onNavigate)
      : () => {};

    const unsubAction = onAction
      ? window.electronAPI.onAction(onAction)
      : () => {};

    return () => {
      unsubNav();
      unsubAction();
    };
  }, [isElectron, onNavigate, onAction]);
}

/**
 * Hook for window operations
 */
export function useWindow() {
  const isElectron = useIsElectron();

  const minimize = useCallback(() => {
    if (!isElectron) return;
    window.electronAPI.minimize();
  }, [isElectron]);

  const maximize = useCallback(() => {
    if (!isElectron) return;
    window.electronAPI.maximize();
  }, [isElectron]);

  const close = useCallback(() => {
    if (!isElectron) return;
    window.electronAPI.close();
  }, [isElectron]);

  return {
    minimize,
    maximize,
    close,
    isElectron
  };
}

/**
 * Hook for notifications
 */
export function useNotification() {
  const isElectron = useIsElectron();

  const showNotification = useCallback((title: string, body: string) => {
    if (!isElectron) {
      // Fallback to browser notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body });
      }
      return;
    }
    window.electronAPI.showNotification(title, body);
  }, [isElectron]);

  return {
    showNotification,
    isElectron
  };
}

/**
 * Hook for app info
 */
export function useAppInfo() {
  const isElectron = useIsElectron();
  const [version, setVersion] = useState<string>('');
  const [platform, setPlatform] = useState<string>('');
  const [arch, setArch] = useState<string>('');

  useEffect(() => {
    if (!isElectron) return;

    const fetchInfo = async () => {
      const ver = await window.electronAPI.getAppVersion();
      const plat = window.electronAPI.getPlatform();
      const architecture = window.electronAPI.getArch();

      setVersion(ver);
      setPlatform(plat);
      setArch(architecture);
    };

    fetchInfo();
  }, [isElectron]);

  return {
    version,
    platform,
    arch,
    isElectron
  };
}

/**
 * Hook for online status
 */
export function useOnlineStatus() {
  const isElectron = useIsElectron();
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    if (!isElectron) {
      setIsOnline(navigator.onLine);
      
      const handleOnline = () => setIsOnline(true);
      const handleOffline = () => setIsOnline(false);

      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }

    setIsOnline(window.electronAPI.isOnline());
  }, [isElectron]);

  return isOnline;
}
