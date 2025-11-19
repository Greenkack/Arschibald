/**
 * useApi Hook
 * 
 * Custom hook for API calls with loading and error handling
 */

import { useState, useCallback } from 'react';
import { useUIStore } from '@store/uiStore';
import { APIError } from '@services/api';

interface UseApiOptions {
  showNotification?: boolean;
  successMessage?: string;
}

export const useApi = <T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<APIError | null>(null);
  const { addNotification } = useUIStore();

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setIsLoading(true);
        setError(null);

        const result = await apiFunction(...args);
        setData(result);

        if (options.showNotification && options.successMessage) {
          addNotification({
            type: 'success',
            title: 'Success',
            message: options.successMessage,
          });
        }

        return result;
      } catch (err: any) {
        const apiError: APIError = {
          message: err.message || 'An error occurred',
          details: err.details,
          path: err.path,
          status: err.status,
        };

        setError(apiError);

        if (options.showNotification) {
          addNotification({
            type: 'error',
            title: 'Error',
            message: apiError.message,
          });
        }

        throw apiError;
      } finally {
        setIsLoading(false);
      }
    },
    [apiFunction, options, addNotification]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    execute,
    reset,
  };
};
