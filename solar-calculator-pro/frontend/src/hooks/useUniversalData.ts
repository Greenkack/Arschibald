/**
 * React Hook for Universal Data Service
 * 
 * Provides easy access to universal data operations with React state management
 * 
 * Requirements: 14.3, 14.10
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { universalDataService, DataWithPDFBytes } from '../services/UniversalDataService';

/**
 * Hook options
 */
interface UseUniversalDataOptions {
  autoFetch?: boolean;
  enableCaching?: boolean;
  formatNumbers?: boolean;
  decimals?: number;
}

/**
 * Hook return type
 */
interface UseUniversalDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  downloadPDF: (filename?: string) => Promise<void>;
  formattedData: any;
  dynamicKey: string | null;
}

/**
 * Hook for fetching data with PDF bytes
 * 
 * @param endpoint - API endpoint to fetch from
 * @param params - Optional query parameters
 * @param options - Hook options
 * @returns Hook state and methods
 */
export function useUniversalData<T = any>(
  endpoint: string,
  params?: Record<string, any>,
  options: UseUniversalDataOptions = {}
): UseUniversalDataReturn<T> {
  const {
    autoFetch = true,
    formatNumbers = true,
    decimals = 2,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [dynamicKey, setDynamicKey] = useState<string | null>(null);
  const [pdfData, setPdfData] = useState<DataWithPDFBytes<T> | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await universalDataService.fetchWithPDFBytes<T>(endpoint, params);
      setData(result.data);
      setDynamicKey(result.dynamic_key);
      setPdfData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [endpoint, params]);

  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [autoFetch, fetchData]);

  const downloadPDF = useCallback(async (filename?: string) => {
    if (!pdfData) {
      throw new Error('No PDF data available');
    }
    await universalDataService.downloadPDF(pdfData, { filename });
  }, [pdfData]);

  const formattedData = formatNumbers && data
    ? universalDataService.formatAllNumbers(data, decimals)
    : data;

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    downloadPDF,
    formattedData,
    dynamicKey,
  };
}

/**
 * Hook for fetching data by dynamic key
 * 
 * @param key - Dynamic key to fetch
 * @param options - Hook options
 * @returns Hook state and methods
 */
export function useDataByKey<T = any>(
  key: string | null,
  options: UseUniversalDataOptions = {}
): UseUniversalDataReturn<T> {
  const {
    autoFetch = true,
    formatNumbers = true,
    decimals = 2,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [dynamicKey, setDynamicKey] = useState<string | null>(key);
  const [pdfData, setPdfData] = useState<DataWithPDFBytes<T> | null>(null);

  const fetchData = useCallback(async () => {
    if (!key) return;

    setLoading(true);
    setError(null);

    try {
      const result = await universalDataService.fetchByKey<T>(key);
      setData(result.data);
      setDynamicKey(result.dynamic_key);
      setPdfData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [key]);

  useEffect(() => {
    if (autoFetch && key) {
      fetchData();
    }
  }, [autoFetch, key, fetchData]);

  const downloadPDF = useCallback(async (filename?: string) => {
    if (!pdfData) {
      throw new Error('No PDF data available');
    }
    await universalDataService.downloadPDF(pdfData, { filename });
  }, [pdfData]);

  const formattedData = formatNumbers && data
    ? universalDataService.formatAllNumbers(data, decimals)
    : data;

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    downloadPDF,
    formattedData,
    dynamicKey,
  };
}

/**
 * Hook for real-time data synchronization
 * 
 * @param key - Dynamic key to watch
 * @param callback - Callback when data changes
 */
export function useDataSync(
  key: string | null,
  callback: (data: any) => void
): void {
  const callbackRef = useRef(callback);

  // Update ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!key) return;

    const unsubscribe = universalDataService.subscribeToKey(key, (data) => {
      callbackRef.current(data);
    });

    return unsubscribe;
  }, [key]);
}

/**
 * Hook for bulk PDF generation
 * 
 * @returns Methods for bulk operations
 */
export function useBulkPDF() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [results, setResults] = useState<DataWithPDFBytes[]>([]);

  const generateBulk = useCallback(async (
    endpoint: string,
    dataList: Record<string, any>[]
  ) => {
    setLoading(true);
    setError(null);

    try {
      const result = await universalDataService.bulkGeneratePDF(endpoint, dataList);
      setResults(result);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadAll = useCallback(async () => {
    for (const result of results) {
      await universalDataService.downloadPDF(result);
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }, [results]);

  return {
    generateBulk,
    downloadAll,
    loading,
    error,
    results,
  };
}

/**
 * Hook for data export
 * 
 * @returns Export methods
 */
export function useDataExport() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const exportJSON = useCallback(async (
    data: any,
    filename?: string
  ) => {
    setLoading(true);
    setError(null);

    try {
      await universalDataService.exportData(data, 'json', filename);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const exportCSV = useCallback(async (
    data: any,
    filename?: string
  ) => {
    setLoading(true);
    setError(null);

    try {
      await universalDataService.exportData(data, 'csv', filename);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    exportJSON,
    exportCSV,
    loading,
    error,
  };
}

/**
 * Hook for cache management
 * 
 * @returns Cache methods and stats
 */
export function useDataCache() {
  const [stats, setStats] = useState(universalDataService.getCacheStats());

  const refresh = useCallback(() => {
    setStats(universalDataService.getCacheStats());
  }, []);

  const clear = useCallback((key?: string) => {
    universalDataService.clearCache(key);
    refresh();
  }, [refresh]);

  useEffect(() => {
    // Refresh stats every 5 seconds
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  return {
    stats,
    clear,
    refresh,
  };
}
