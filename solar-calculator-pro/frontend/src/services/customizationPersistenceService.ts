/**
 * Task 209: Customization Persistence
 * ====================================
 * Handles persistence, synchronization, and versioning of customization settings.
 */

import { PresetConfig, UIPreset } from './presetService';

// ============================================================================
// Types
// ============================================================================

export interface CustomizationData {
  version: string;
  lastUpdated: string;
  deviceId: string;
  activePresetId: string;
  customPresets: UIPreset[];
  settings: CustomizationSettings;
}

export interface CustomizationSettings {
  theme: string;
  emojis: {
    enabled: boolean;
    style: 'native' | 'twemoji' | 'noto';
    animateOnHover: boolean;
  };
  effects: {
    preset: string;
    animationSpeed: number;
    shadowIntensity: number;
    enableTransitions: boolean;
    enableAnimations: boolean;
  };
  accessibility: {
    reducedMotion: boolean;
    highContrast: boolean;
    largeText: boolean;
  };
}

export interface SyncStatus {
  lastSyncTime: string | null;
  isSyncing: boolean;
  syncError: string | null;
  pendingChanges: boolean;
}

export interface MigrationResult {
  success: boolean;
  fromVersion: string;
  toVersion: string;
  migratedFields: string[];
  errors: string[];
}

// ============================================================================
// Constants
// ============================================================================

const CURRENT_VERSION = '2.0.0';
const STORAGE_KEY = 'solar-calculator-customization';
const SYNC_ENDPOINT = '/api/v1/customization/sync';

// ============================================================================
// Default Settings
// ============================================================================

const DEFAULT_SETTINGS: CustomizationSettings = {
  theme: 'light',
  emojis: {
    enabled: true,
    style: 'native',
    animateOnHover: false,
  },
  effects: {
    preset: 'standard',
    animationSpeed: 1.0,
    shadowIntensity: 50,
    enableTransitions: true,
    enableAnimations: true,
  },
  accessibility: {
    reducedMotion: false,
    highContrast: false,
    largeText: false,
  },
};

// ============================================================================
// Migration Functions
// ============================================================================

type MigrationFn = (data: any) => any;

const MIGRATIONS: Record<string, MigrationFn> = {
  '1.0.0_to_1.1.0': (data) => {
    // Add emoji style field
    if (data.settings?.emojis && !data.settings.emojis.style) {
      data.settings.emojis.style = 'native';
    }
    return data;
  },
  '1.1.0_to_1.2.0': (data) => {
    // Add accessibility settings
    if (!data.settings?.accessibility) {
      data.settings.accessibility = {
        reducedMotion: false,
        highContrast: false,
        largeText: false,
      };
    }
    return data;
  },
  '1.2.0_to_2.0.0': (data) => {
    // Add animation speed and shadow intensity
    if (data.settings?.effects) {
      if (data.settings.effects.animationSpeed === undefined) {
        data.settings.effects.animationSpeed = 1.0;
      }
      if (data.settings.effects.shadowIntensity === undefined) {
        data.settings.effects.shadowIntensity = 50;
      }
    }
    return data;
  },
};

const VERSION_ORDER = ['1.0.0', '1.1.0', '1.2.0', '2.0.0'];

// ============================================================================
// Customization Persistence Service
// ============================================================================

class CustomizationPersistenceService {
  private deviceId: string;
  private syncStatus: SyncStatus = {
    lastSyncTime: null,
    isSyncing: false,
    syncError: null,
    pendingChanges: false,
  };
  private listeners: Set<(data: CustomizationData) => void> = new Set();
  private syncListeners: Set<(status: SyncStatus) => void> = new Set();

  constructor() {
    this.deviceId = this.getOrCreateDeviceId();
  }

  // --------------------------------------------------------------------------
  // Device ID Management
  // --------------------------------------------------------------------------

  private getOrCreateDeviceId(): string {
    if (typeof localStorage === 'undefined') return 'unknown';

    let deviceId = localStorage.getItem('solar-calculator-device-id');
    if (!deviceId) {
      deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('solar-calculator-device-id', deviceId);
    }
    return deviceId;
  }

  // --------------------------------------------------------------------------
  // Local Storage Operations
  // --------------------------------------------------------------------------

  load(): CustomizationData {
    if (typeof localStorage === 'undefined') {
      return this.createDefaultData();
    }

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return this.createDefaultData();
      }

      const data = JSON.parse(stored) as CustomizationData;
      
      // Check if migration is needed
      if (data.version !== CURRENT_VERSION) {
        const migrated = this.migrate(data);
        this.save(migrated);
        return migrated;
      }

      return data;
    } catch (error) {
      console.error('Failed to load customization data:', error);
      return this.createDefaultData();
    }
  }

  save(data: CustomizationData): void {
    if (typeof localStorage === 'undefined') return;

    try {
      data.lastUpdated = new Date().toISOString();
      data.version = CURRENT_VERSION;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      this.syncStatus.pendingChanges = true;
      this.notifyListeners(data);
    } catch (error) {
      console.error('Failed to save customization data:', error);
    }
  }

  saveSettings(settings: Partial<CustomizationSettings>): void {
    const data = this.load();
    data.settings = { ...data.settings, ...settings };
    this.save(data);
  }

  saveActivePreset(presetId: string): void {
    const data = this.load();
    data.activePresetId = presetId;
    this.save(data);
  }

  saveCustomPresets(presets: UIPreset[]): void {
    const data = this.load();
    data.customPresets = presets;
    this.save(data);
  }

  private createDefaultData(): CustomizationData {
    return {
      version: CURRENT_VERSION,
      lastUpdated: new Date().toISOString(),
      deviceId: this.deviceId,
      activePresetId: 'standard',
      customPresets: [],
      settings: { ...DEFAULT_SETTINGS },
    };
  }

  // --------------------------------------------------------------------------
  // Migration
  // --------------------------------------------------------------------------

  migrate(data: CustomizationData): CustomizationData {
    const fromVersion = data.version || '1.0.0';
    const fromIndex = VERSION_ORDER.indexOf(fromVersion);
    const toIndex = VERSION_ORDER.indexOf(CURRENT_VERSION);

    if (fromIndex === -1 || fromIndex >= toIndex) {
      return data;
    }

    let migratedData = { ...data };
    const migratedFields: string[] = [];
    const errors: string[] = [];

    for (let i = fromIndex; i < toIndex; i++) {
      const fromVer = VERSION_ORDER[i];
      const toVer = VERSION_ORDER[i + 1];
      const migrationKey = `${fromVer}_to_${toVer}`;
      const migrationFn = MIGRATIONS[migrationKey];

      if (migrationFn) {
        try {
          migratedData = migrationFn(migratedData);
          migratedFields.push(migrationKey);
        } catch (error) {
          errors.push(`Migration ${migrationKey} failed: ${error}`);
        }
      }
    }

    migratedData.version = CURRENT_VERSION;
    
    console.log('Migration result:', {
      fromVersion,
      toVersion: CURRENT_VERSION,
      migratedFields,
      errors,
    });

    return migratedData;
  }

  getMigrationInfo(): { currentVersion: string; supportedVersions: string[] } {
    return {
      currentVersion: CURRENT_VERSION,
      supportedVersions: VERSION_ORDER,
    };
  }

  // --------------------------------------------------------------------------
  // Backend Sync
  // --------------------------------------------------------------------------

  async syncWithBackend(authToken?: string): Promise<boolean> {
    if (this.syncStatus.isSyncing) {
      return false;
    }

    this.updateSyncStatus({ isSyncing: true, syncError: null });

    try {
      const localData = this.load();
      
      const response = await fetch(SYNC_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify({
          deviceId: this.deviceId,
          data: localData,
        }),
      });

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.statusText}`);
      }

      const serverData = await response.json();
      
      // Merge server data with local data
      const mergedData = this.mergeData(localData, serverData.data);
      this.save(mergedData);

      this.updateSyncStatus({
        isSyncing: false,
        lastSyncTime: new Date().toISOString(),
        pendingChanges: false,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateSyncStatus({
        isSyncing: false,
        syncError: errorMessage,
      });
      console.error('Sync failed:', error);
      return false;
    }
  }

  private mergeData(local: CustomizationData, server: CustomizationData): CustomizationData {
    // Use the most recently updated data
    const localTime = new Date(local.lastUpdated).getTime();
    const serverTime = new Date(server.lastUpdated).getTime();

    if (serverTime > localTime) {
      // Server is newer, use server data but keep local custom presets
      return {
        ...server,
        customPresets: this.mergePresets(local.customPresets, server.customPresets),
      };
    }

    return local;
  }

  private mergePresets(local: UIPreset[], server: UIPreset[]): UIPreset[] {
    const merged = new Map<string, UIPreset>();

    // Add server presets first
    server.forEach(preset => merged.set(preset.id, preset));

    // Override with local presets (local takes precedence for same ID)
    local.forEach(preset => {
      const existing = merged.get(preset.id);
      if (!existing || new Date(preset.updatedAt || 0) > new Date(existing.updatedAt || 0)) {
        merged.set(preset.id, preset);
      }
    });

    return Array.from(merged.values());
  }

  getSyncStatus(): SyncStatus {
    return { ...this.syncStatus };
  }

  private updateSyncStatus(updates: Partial<SyncStatus>): void {
    this.syncStatus = { ...this.syncStatus, ...updates };
    this.notifySyncListeners();
  }

  // --------------------------------------------------------------------------
  // Cross-Device Sync
  // --------------------------------------------------------------------------

  async fetchFromDevice(deviceId: string, authToken?: string): Promise<CustomizationData | null> {
    try {
      const response = await fetch(`${SYNC_ENDPOINT}/device/${deviceId}`, {
        headers: {
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch from device: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch from device:', error);
      return null;
    }
  }

  async pushToDevice(deviceId: string, authToken?: string): Promise<boolean> {
    try {
      const localData = this.load();
      
      const response = await fetch(`${SYNC_ENDPOINT}/device/${deviceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify(localData),
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to push to device:', error);
      return false;
    }
  }

  // --------------------------------------------------------------------------
  // Export/Import
  // --------------------------------------------------------------------------

  exportToFile(): string {
    const data = this.load();
    return JSON.stringify({
      exportVersion: '1.0',
      exportDate: new Date().toISOString(),
      data,
    }, null, 2);
  }

  importFromFile(jsonString: string): boolean {
    try {
      const imported = JSON.parse(jsonString);
      
      if (!imported.data) {
        throw new Error('Invalid export format');
      }

      const migratedData = this.migrate(imported.data);
      this.save(migratedData);
      return true;
    } catch (error) {
      console.error('Failed to import customization data:', error);
      return false;
    }
  }

  // --------------------------------------------------------------------------
  // Reset
  // --------------------------------------------------------------------------

  reset(): void {
    const defaultData = this.createDefaultData();
    this.save(defaultData);
  }

  // --------------------------------------------------------------------------
  // Listeners
  // --------------------------------------------------------------------------

  subscribe(listener: (data: CustomizationData) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  subscribeToSync(listener: (status: SyncStatus) => void): () => void {
    this.syncListeners.add(listener);
    return () => this.syncListeners.delete(listener);
  }

  private notifyListeners(data: CustomizationData): void {
    this.listeners.forEach(listener => listener(data));
  }

  private notifySyncListeners(): void {
    this.syncListeners.forEach(listener => listener(this.syncStatus));
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const customizationPersistenceService = new CustomizationPersistenceService();

// ============================================================================
// React Hooks
// ============================================================================

import { useState, useEffect, useCallback } from 'react';

export function useCustomizationPersistence() {
  const [data, setData] = useState<CustomizationData>(customizationPersistenceService.load());
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(customizationPersistenceService.getSyncStatus());

  useEffect(() => {
    const unsubData = customizationPersistenceService.subscribe(setData);
    const unsubSync = customizationPersistenceService.subscribeToSync(setSyncStatus);
    return () => {
      unsubData();
      unsubSync();
    };
  }, []);

  const saveSettings = useCallback((settings: Partial<CustomizationSettings>) => {
    customizationPersistenceService.saveSettings(settings);
  }, []);

  const sync = useCallback(async (authToken?: string) => {
    return customizationPersistenceService.syncWithBackend(authToken);
  }, []);

  const exportData = useCallback(() => {
    return customizationPersistenceService.exportToFile();
  }, []);

  const importData = useCallback((jsonString: string) => {
    return customizationPersistenceService.importFromFile(jsonString);
  }, []);

  const reset = useCallback(() => {
    customizationPersistenceService.reset();
  }, []);

  return {
    data,
    syncStatus,
    saveSettings,
    saveActivePreset: customizationPersistenceService.saveActivePreset.bind(customizationPersistenceService),
    saveCustomPresets: customizationPersistenceService.saveCustomPresets.bind(customizationPersistenceService),
    sync,
    exportData,
    importData,
    reset,
  };
}

export default customizationPersistenceService;
