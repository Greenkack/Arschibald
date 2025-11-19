/**
 * TypeScript type definitions for Electron API
 * 
 * These types provide IntelliSense and type safety when using
 * the Electron API exposed through the preload script.
 */

interface UpdateInfo {
  version: string;
  releaseDate?: string;
  releaseNotes?: string;
}

interface UpdateProgress {
  percent: number;
  transferred: number;
  total: number;
  bytesPerSecond: number;
}

interface UpdateError {
  message: string;
}

interface FileDialogOptions {
  defaultPath?: string;
  filters?: Array<{
    name: string;
    extensions: string[];
  }>;
}

interface ElectronAPI {
  // File operations
  selectFile: () => Promise<string | undefined>;
  saveFile: (options: FileDialogOptions) => Promise<string | undefined>;
  selectDirectory: () => Promise<string | undefined>;

  // Backend communication
  getBackendUrl: () => Promise<string | null>;
  checkBackendHealth: () => Promise<boolean>;

  // Window operations
  minimize: () => void;
  maximize: () => void;
  close: () => void;

  // App operations
  getAppVersion: () => Promise<string>;
  getPlatform: () => string;
  getArch: () => string;

  // Updates
  checkForUpdates: () => Promise<{
    success: boolean;
    updateInfo?: any;
    error?: string;
  }>;
  downloadUpdate: () => Promise<{
    success: boolean;
    error?: string;
  }>;
  installUpdate: () => void;
  getCurrentVersion: () => Promise<string>;

  // Update event listeners (return cleanup function)
  onUpdateAvailable: (callback: (data: UpdateInfo) => void) => () => void;
  onUpdateDownloaded: (callback: (data: UpdateInfo) => void) => () => void;
  onUpdateProgress: (callback: (data: UpdateProgress) => void) => () => void;
  onUpdateError: (callback: (data: UpdateError) => void) => () => void;
  onUpdateChecking: (callback: () => void) => () => void;

  // Navigation events (from menu)
  onNavigate: (callback: (route: string) => void) => () => void;

  // Action events (from menu/tray)
  onAction: (callback: (action: string, data?: any) => void) => () => void;

  // Notifications
  showNotification: (title: string, body: string) => void;

  // System info
  isOnline: () => boolean;
  isElectron: () => boolean;

  // Deep linking (for future use)
  onDeepLink: (callback: (url: string) => void) => () => void;
}

interface NodeAPI {
  // Path operations (safe subset)
  pathJoin: (...args: string[]) => string;
  pathBasename: (path: string) => string;
  pathDirname: (path: string) => string;
  pathExtname: (path: string) => string;

  // Environment info (read-only)
  env: {
    NODE_ENV?: string;
    PLATFORM: string;
    ARCH: string;
  };
}

// Extend Window interface
declare global {
  interface Window {
    electronAPI: ElectronAPI;
    nodeAPI: NodeAPI;
  }
}

export {};
