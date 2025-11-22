/**
 * useFeatureToggle Hook
 * 
 * Custom hook for checking feature flag status in components
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

interface FeatureFlagCheckResponse {
  key: string;
  enabled: boolean;
  reason: string;
}

interface UseFeatureToggleOptions {
  userId?: number;
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
}

export const useFeatureToggle = (
  featureKey: string,
  options: UseFeatureToggleOptions = {}
) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [reason, setReason] = useState<string>('');

  const { userId, autoRefresh = false, refreshInterval = 60000 } = options;

  const checkFeature = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.post<FeatureFlagCheckResponse>(
        '/api/v1/feature-flags/check',
        {
          key: featureKey,
          user_id: userId,
        }
      );

      setIsEnabled(response.data.enabled);
      setReason(response.data.reason);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check feature flag');
      setIsEnabled(false);
    } finally {
      setIsLoading(false);
    }
  }, [featureKey, userId]);

  useEffect(() => {
    checkFeature();

    if (autoRefresh) {
      const interval = setInterval(checkFeature, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [checkFeature, autoRefresh, refreshInterval]);

  return {
    isEnabled,
    isLoading,
    error,
    reason,
    refresh: checkFeature,
  };
};

/**
 * Hook for checking multiple feature flags at once
 */
export const useFeatureToggles = (
  featureKeys: string[],
  options: UseFeatureToggleOptions = {}
) => {
  const [features, setFeatures] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const { userId, autoRefresh = false, refreshInterval = 60000 } = options;

  const checkFeatures = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.post('/api/v1/feature-flags/check-bulk', {
        keys: featureKeys,
        user_id: userId,
      });

      setFeatures(response.data.flags);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check feature flags');
      setFeatures({});
    } finally {
      setIsLoading(false);
    }
  }, [featureKeys, userId]);

  useEffect(() => {
    if (featureKeys.length > 0) {
      checkFeatures();

      if (autoRefresh) {
        const interval = setInterval(checkFeatures, refreshInterval);
        return () => clearInterval(interval);
      }
    }
  }, [checkFeatures, autoRefresh, refreshInterval, featureKeys.length]);

  return {
    features,
    isLoading,
    error,
    refresh: checkFeatures,
    isFeatureEnabled: (key: string) => features[key] || false,
  };
};

/**
 * Higher-order component for feature-gated components
 */
export const withFeatureToggle = <P extends object>(
  Component: React.ComponentType<P>,
  featureKey: string,
  fallback?: React.ReactNode
) => {
  return (props: P) => {
    const { isEnabled, isLoading } = useFeatureToggle(featureKey);

    if (isLoading) {
      return <div>Loading...</div>;
    }

    if (!isEnabled) {
      return fallback ? <>{fallback}</> : null;
    }

    return <Component {...props} />;
  };
};
