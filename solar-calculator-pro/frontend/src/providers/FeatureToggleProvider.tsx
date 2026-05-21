/**
 * Feature Toggle Provider
 * 
 * Global context provider for feature toggle state management
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

interface FeatureToggleContextType {
  features: Record<string, boolean>;
  isLoading: boolean;
  error: string | null;
  isFeatureEnabled: (key: string) => boolean;
  refreshFeatures: () => Promise<void>;
  preloadFeatures: (keys: string[]) => Promise<void>;
}

const FeatureToggleContext = createContext<FeatureToggleContextType | undefined>(
  undefined
);

interface FeatureToggleProviderProps {
  children: React.ReactNode;
  userId?: number;
  preloadKeys?: string[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const FeatureToggleProvider: React.FC<FeatureToggleProviderProps> = ({
  children,
  userId,
  preloadKeys = [],
  autoRefresh = false,
  refreshInterval = 300000, // 5 minutes
}) => {
  const [features, setFeatures] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadFeatures = useCallback(
    async (keys: string[]) => {
      if (keys.length === 0) return;

      try {
        setIsLoading(true);
        setError(null);

        const response = await api.post('/api/v1/feature-flags/check-bulk', {
          keys,
          user_id: userId,
        });

        setFeatures((prev) => ({
          ...prev,
          ...response.data.flags,
        }));
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load feature flags');
        console.error('Failed to load feature flags:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  const refreshFeatures = useCallback(async () => {
    const keys = Object.keys(features);
    if (keys.length > 0) {
      await loadFeatures(keys);
    }
  }, [features, loadFeatures]);

  const preloadFeatures = useCallback(
    async (keys: string[]) => {
      await loadFeatures(keys);
    },
    [loadFeatures]
  );

  const isFeatureEnabled = useCallback(
    (key: string): boolean => {
      return features[key] || false;
    },
    [features]
  );

  // Preload features on mount
  useEffect(() => {
    if (preloadKeys.length > 0) {
      loadFeatures(preloadKeys);
    }
  }, [preloadKeys, loadFeatures]);

  // Auto-refresh features
  useEffect(() => {
    if (autoRefresh && Object.keys(features).length > 0) {
      const interval = setInterval(refreshFeatures, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, features, refreshFeatures]);

  const value: FeatureToggleContextType = {
    features,
    isLoading,
    error,
    isFeatureEnabled,
    refreshFeatures,
    preloadFeatures,
  };

  return (
    <FeatureToggleContext.Provider value={value}>
      {children}
    </FeatureToggleContext.Provider>
  );
};

export const useFeatureToggleContext = (): FeatureToggleContextType => {
  const context = useContext(FeatureToggleContext);
  if (!context) {
    throw new Error(
      'useFeatureToggleContext must be used within a FeatureToggleProvider'
    );
  }
  return context;
};

/**
 * Feature Gate Component
 * 
 * Conditionally renders children based on feature flag status
 */
interface FeatureGateProps {
  featureKey: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  loadingFallback?: React.ReactNode;
}

export const FeatureGate: React.FC<FeatureGateProps> = ({
  featureKey,
  children,
  fallback = null,
  loadingFallback = null,
}) => {
  const { isFeatureEnabled, isLoading, preloadFeatures } = useFeatureToggleContext();

  useEffect(() => {
    // Ensure the feature is loaded
    if (!isFeatureEnabled(featureKey)) {
      preloadFeatures([featureKey]);
    }
  }, [featureKey, isFeatureEnabled, preloadFeatures]);

  if (isLoading && loadingFallback) {
    return <>{loadingFallback}</>;
  }

  if (!isFeatureEnabled(featureKey)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
