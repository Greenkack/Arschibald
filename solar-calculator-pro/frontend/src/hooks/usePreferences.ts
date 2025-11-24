// frontend/src/hooks/usePreferences.ts

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface Preference {
  value: any;
  data_type: string;
  is_default: boolean;
  updated_at?: string;
}

export interface PreferenceCategory {
  [key: string]: Preference;
}

export interface AllPreferences {
  [category: string]: PreferenceCategory;
}

export interface UsePreferencesReturn {
  preferences: AllPreferences;
  loading: boolean;
  error: string | null;
  getPreference: (category: string, key: string, defaultValue?: any) => any;
  setPreference: (category: string, key: string, value: any) => Promise<void>;
  bulkUpdate: (updates: Array<{ category: string; key: string; value: any }>) => Promise<void>;
  resetPreference: (category: string, key: string) => Promise<void>;
  resetCategory: (category: string) => Promise<void>;
  resetAll: () => Promise<void>;
  exportPreferences: () => Promise<string>;
  importPreferences: (data: string, overwrite?: boolean) => Promise<void>;
  syncPreferences: (deviceId: string, deviceName?: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export const usePreferences = (): UsePreferencesReturn => {
  const [preferences, setPreferences] = useState<AllPreferences>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadPreferences = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/v1/preferences/');
      setPreferences(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load preferences');
      console.error('Error loading preferences:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const getPreference = useCallback(
    (category: string, key: string, defaultValue: any = null): any => {
      return preferences[category]?.[key]?.value ?? defaultValue;
    },
    [preferences]
  );

  const setPreference = useCallback(
    async (category: string, key: string, value: any): Promise<void> => {
      try {
        await api.put(`/api/v1/preferences/${category}/${key}`, { value });
        
        // Update local state
        setPreferences((prev) => ({
          ...prev,
          [category]: {
            ...prev[category],
            [key]: {
              value,
              data_type: prev[category]?.[key]?.data_type || 'string',
              is_default: false,
              updated_at: new Date().toISOString(),
            },
          },
        }));
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to update preference');
        throw err;
      }
    },
    []
  );

  const bulkUpdate = useCallback(
    async (updates: Array<{ category: string; key: string; value: any }>): Promise<void> => {
      try {
        await api.put('/api/v1/preferences/bulk', { preferences: updates });
        await loadPreferences();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to bulk update preferences');
        throw err;
      }
    },
    [loadPreferences]
  );

  const resetPreference = useCallback(
    async (category: string, key: string): Promise<void> => {
      try {
        await api.delete(`/api/v1/preferences/${category}/${key}`);
        await loadPreferences();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to reset preference');
        throw err;
      }
    },
    [loadPreferences]
  );

  const resetCategory = useCallback(
    async (category: string): Promise<void> => {
      try {
        await api.post('/api/v1/preferences/reset', { category });
        await loadPreferences();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to reset category');
        throw err;
      }
    },
    [loadPreferences]
  );

  const resetAll = useCallback(async (): Promise<void> => {
    try {
      await api.post('/api/v1/preferences/reset', {});
      await loadPreferences();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset all preferences');
      throw err;
    }
  }, [loadPreferences]);

  const exportPreferences = useCallback(async (): Promise<string> => {
    try {
      const response = await api.get('/api/v1/preferences/export/all');
      return JSON.stringify(response.data, null, 2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export preferences');
      throw err;
    }
  }, []);

  const importPreferences = useCallback(
    async (data: string, overwrite: boolean = false): Promise<void> => {
      try {
        const importData = JSON.parse(data);
        await api.post('/api/v1/preferences/import', {
          ...importData,
          overwrite_existing: overwrite,
        });
        await loadPreferences();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to import preferences');
        throw err;
      }
    },
    [loadPreferences]
  );

  const syncPreferences = useCallback(
    async (deviceId: string, deviceName?: string): Promise<void> => {
      try {
        await api.post('/api/v1/preferences/sync', {
          device_id: deviceId,
          device_name: deviceName,
          preferences,
        });
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to sync preferences');
        throw err;
      }
    },
    [preferences]
  );

  const refresh = useCallback(async (): Promise<void> => {
    await loadPreferences();
  }, [loadPreferences]);

  return {
    preferences,
    loading,
    error,
    getPreference,
    setPreference,
    bulkUpdate,
    resetPreference,
    resetCategory,
    resetAll,
    exportPreferences,
    importPreferences,
    syncPreferences,
    refresh,
  };
};
