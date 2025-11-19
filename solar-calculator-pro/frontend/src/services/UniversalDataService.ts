/**
 * Universal Data Service - Frontend
 * 
 * Frontend service for managing universal data operations including:
 * - Fetching data with PDF bytes
 * - Formatting all numbers recursively
 * - Downloading PDFs
 * - Data caching with dynamic keys
 * - Real-time data synchronization
 * 
 * Requirements: 14.3, 14.10
 */

import axios, { AxiosInstance } from 'axios';
import { germanFormatter } from '../utils/germanNumberFormatter';

/**
 * Configuration for the Universal Data Service
 */
interface UniversalDataServiceConfig {
  baseURL?: string;
  timeout?: number;
  enableCaching?: boolean;
  cacheExpiration?: number; // milliseconds
}

/**
 * Data with PDF bytes response
 */
interface DataWithPDFBytes<T = any> {
  data: T;
  dynamic_key: string;
  pdf_bytes?: string; // base64 encoded
  pdf_url?: string;
  key_metadata?: {
    prefix: string;
    created_at: string;
    has_timestamp: boolean;
    has_uuid: boolean;
  };
}

/**
 * Cache entry structure
 */
interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  key: string;
}

/**
 * Download options for PDF
 */
interface DownloadOptions {
  filename?: string;
  openInNewTab?: boolean;
}

/**
 * Universal Data Service Class
 * 
 * Provides comprehensive data management with German formatting,
 * PDF generation, and dynamic key support.
 */
export class UniversalDataService {
  private api: AxiosInstance;
  private cache: Map<string, CacheEntry>;
  private config: Required<UniversalDataServiceConfig>;
  private syncCallbacks: Map<string, Set<(data: any) => void>>;

  constructor(config: UniversalDataServiceConfig = {}) {
    this.config = {
      baseURL: config.baseURL || 'http://localhost:8000/api/v1',
      timeout: config.timeout || 30000,
      enableCaching: config.enableCaching !== false,
      cacheExpiration: config.cacheExpiration || 5 * 60 * 1000, // 5 minutes default
    };

    this.api = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.cache = new Map();
    this.syncCallbacks = new Map();

    // Setup request interceptor for auth token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Setup response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        throw error;
      }
    );
  }

  /**
   * Fetch data with PDF bytes from backend
   * 
   * @param endpoint - API endpoint to fetch from
   * @param params - Optional query parameters
   * @returns Promise with data and PDF bytes
   */
  async fetchWithPDFBytes<T = any>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<DataWithPDFBytes<T>> {
    // Check cache first
    const cacheKey = this.getCacheKey(endpoint, params);
    if (this.config.enableCaching) {
      const cached = this.getFromCache<DataWithPDFBytes<T>>(cacheKey);
      if (cached) {
        return cached;
      }
    }

    // Fetch from API
    const response = await this.api.get<DataWithPDFBytes<T>>(endpoint, { params });
    const data = response.data;

    // Cache the result
    if (this.config.enableCaching) {
      this.addToCache(cacheKey, data);
    }

    // Trigger sync callbacks
    if (data.dynamic_key) {
      this.triggerSyncCallbacks(data.dynamic_key, data);
    }

    return data;
  }

  /**
   * Fetch data by dynamic key
   * 
   * @param key - Dynamic key to fetch
   * @returns Promise with data and PDF bytes
   */
  async fetchByKey<T = any>(key: string): Promise<DataWithPDFBytes<T>> {
    return this.fetchWithPDFBytes<T>(`/data/by-key/${key}`);
  }

  /**
   * Format all numbers in an object recursively to German format
   * 
   * This function traverses the entire object tree and formats all
   * numeric values to German format (1.234,56)
   * 
   * @param data - Data object to format
   * @param decimals - Number of decimal places (default: 2)
   * @returns Formatted data object
   */
  formatAllNumbers(data: any, decimals: number = 2): any {
    // Handle null/undefined
    if (data === null || data === undefined) {
      return data;
    }

    // Handle numbers
    if (typeof data === 'number') {
      return germanFormatter.format(data, decimals);
    }

    // Handle arrays
    if (Array.isArray(data)) {
      return data.map((item) => this.formatAllNumbers(item, decimals));
    }

    // Handle objects
    if (typeof data === 'object') {
      const formatted: Record<string, any> = {};
      for (const [key, value] of Object.entries(data)) {
        formatted[key] = this.formatAllNumbers(value, decimals);
      }
      return formatted;
    }

    // Return other types as-is
    return data;
  }

  /**
   * Download PDF from data
   * 
   * @param data - Data with PDF bytes or URL
   * @param options - Download options
   */
  async downloadPDF(
    data: DataWithPDFBytes | string,
    options: DownloadOptions = {}
  ): Promise<void> {
    let pdfBlob: Blob;
    let filename = options.filename || 'document.pdf';

    // Handle different input types
    if (typeof data === 'string') {
      // Assume it's a dynamic key
      const fetchedData = await this.fetchByKey(data);
      return this.downloadPDF(fetchedData, options);
    }

    // Get PDF data
    if (data.pdf_bytes) {
      // Convert base64 to blob
      const binaryString = atob(data.pdf_bytes);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      pdfBlob = new Blob([bytes], { type: 'application/pdf' });
    } else if (data.pdf_url) {
      // Fetch from URL
      const response = await fetch(data.pdf_url);
      pdfBlob = await response.blob();
    } else {
      throw new Error('No PDF data available');
    }

    // Generate filename from dynamic key if not provided
    if (!options.filename && data.dynamic_key) {
      filename = `${data.dynamic_key}.pdf`;
    }

    // Download or open
    if (options.openInNewTab) {
      const url = URL.createObjectURL(pdfBlob);
      window.open(url, '_blank');
      // Clean up after a delay
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } else {
      // Trigger download
      const url = URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  }

  /**
   * Generate PDF for data
   * 
   * @param endpoint - API endpoint to generate PDF
   * @param data - Data to generate PDF from
   * @returns Promise with PDF bytes
   */
  async generatePDF(
    endpoint: string,
    data: Record<string, any>
  ): Promise<DataWithPDFBytes> {
    const response = await this.api.post<DataWithPDFBytes>(endpoint, data);
    return response.data;
  }

  /**
   * Bulk generate PDFs
   * 
   * @param endpoint - API endpoint for bulk generation
   * @param dataList - Array of data objects
   * @returns Promise with array of PDF results
   */
  async bulkGeneratePDF(
    endpoint: string,
    dataList: Record<string, any>[]
  ): Promise<DataWithPDFBytes[]> {
    const response = await this.api.post<DataWithPDFBytes[]>(endpoint, {
      data_list: dataList,
    });
    return response.data;
  }

  /**
   * Search data by key pattern
   * 
   * @param pattern - Search pattern (supports wildcards)
   * @returns Promise with matching data
   */
  async searchByKey(pattern: string): Promise<DataWithPDFBytes[]> {
    const response = await this.api.get<DataWithPDFBytes[]>('/data/keys/search', {
      params: { pattern },
    });
    return response.data;
  }

  /**
   * Get data by prefix
   * 
   * @param prefix - Key prefix to filter by
   * @returns Promise with matching data
   */
  async getByPrefix(prefix: string): Promise<DataWithPDFBytes[]> {
    const response = await this.api.get<DataWithPDFBytes[]>('/data/by-prefix', {
      params: { prefix },
    });
    return response.data;
  }

  /**
   * Subscribe to real-time data updates for a key
   * 
   * @param key - Dynamic key to watch
   * @param callback - Callback function when data changes
   * @returns Unsubscribe function
   */
  subscribeToKey(key: string, callback: (data: any) => void): () => void {
    if (!this.syncCallbacks.has(key)) {
      this.syncCallbacks.set(key, new Set());
    }
    this.syncCallbacks.get(key)!.add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.syncCallbacks.get(key);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.syncCallbacks.delete(key);
        }
      }
    };
  }

  /**
   * Trigger sync callbacks for a key
   * 
   * @param key - Dynamic key
   * @param data - Updated data
   */
  private triggerSyncCallbacks(key: string, data: any): void {
    const callbacks = this.syncCallbacks.get(key);
    if (callbacks) {
      callbacks.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in sync callback:', error);
        }
      });
    }
  }

  /**
   * Clear cache for a specific key or all cache
   * 
   * @param key - Optional cache key to clear
   */
  clearCache(key?: string): void {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Get cache statistics
   * 
   * @returns Cache statistics
   */
  getCacheStats(): {
    size: number;
    keys: string[];
    oldestEntry: number | null;
    newestEntry: number | null;
  } {
    const entries = Array.from(this.cache.values());
    const timestamps = entries.map((e) => e.timestamp);

    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      oldestEntry: timestamps.length > 0 ? Math.min(...timestamps) : null,
      newestEntry: timestamps.length > 0 ? Math.max(...timestamps) : null,
    };
  }

  /**
   * Generate cache key from endpoint and params
   * 
   * @param endpoint - API endpoint
   * @param params - Query parameters
   * @returns Cache key string
   */
  private getCacheKey(endpoint: string, params?: Record<string, any>): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${endpoint}:${paramString}`;
  }

  /**
   * Get data from cache
   * 
   * @param key - Cache key
   * @returns Cached data or null
   */
  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) {
      return null;
    }

    // Check if expired
    const now = Date.now();
    if (now - entry.timestamp > this.config.cacheExpiration) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Add data to cache
   * 
   * @param key - Cache key
   * @param data - Data to cache
   */
  private addToCache(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      key,
    });

    // Clean up old entries if cache is too large
    if (this.cache.size > 1000) {
      this.cleanupCache();
    }
  }

  /**
   * Clean up old cache entries
   */
  private cleanupCache(): void {
    const now = Date.now();
    const entries = Array.from(this.cache.entries());

    // Sort by timestamp
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);

    // Remove oldest 20%
    const toRemove = Math.floor(entries.length * 0.2);
    for (let i = 0; i < toRemove; i++) {
      this.cache.delete(entries[i][0]);
    }
  }

  /**
   * Prefetch data for a list of keys
   * 
   * @param keys - Array of dynamic keys to prefetch
   */
  async prefetchKeys(keys: string[]): Promise<void> {
    const promises = keys.map((key) =>
      this.fetchByKey(key).catch((error) => {
        console.warn(`Failed to prefetch key ${key}:`, error);
        return null;
      })
    );

    await Promise.all(promises);
  }

  /**
   * Export data with formatted numbers
   * 
   * @param data - Data to export
   * @param format - Export format ('json' | 'csv')
   * @param filename - Output filename
   */
  async exportData(
    data: any,
    format: 'json' | 'csv' = 'json',
    filename?: string
  ): Promise<void> {
    const formatted = this.formatAllNumbers(data);

    if (format === 'json') {
      const json = JSON.stringify(formatted, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      this.downloadBlob(blob, filename || 'data.json');
    } else if (format === 'csv') {
      const csv = this.convertToCSV(formatted);
      const blob = new Blob([csv], { type: 'text/csv' });
      this.downloadBlob(blob, filename || 'data.csv');
    }
  }

  /**
   * Convert data to CSV format
   * 
   * @param data - Data to convert
   * @returns CSV string
   */
  private convertToCSV(data: any): string {
    if (Array.isArray(data)) {
      if (data.length === 0) return '';

      // Get headers from first object
      const headers = Object.keys(data[0]);
      const rows = data.map((item) =>
        headers.map((header) => {
          const value = item[header];
          // Escape quotes and wrap in quotes if contains comma
          const stringValue = String(value);
          if (stringValue.includes(',') || stringValue.includes('"')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
          }
          return stringValue;
        }).join(',')
      );

      return [headers.join(','), ...rows].join('\n');
    } else if (typeof data === 'object') {
      // Convert single object to CSV
      const headers = Object.keys(data);
      const values = headers.map((header) => String(data[header]));
      return [headers.join(','), values.join(',')].join('\n');
    }

    return String(data);
  }

  /**
   * Download blob as file
   * 
   * @param blob - Blob to download
   * @param filename - Filename
   */
  private downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// Create singleton instance
export const universalDataService = new UniversalDataService();

// Export default
export default universalDataService;
