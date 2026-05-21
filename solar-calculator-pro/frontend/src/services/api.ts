/**
 * Axios API Client Configuration
 * 
 * This file configures Axios for API communication with the FastAPI backend.
 * It includes request/response interceptors for authentication, error handling,
 * logging, automatic token refresh, and retry logic.
 * 
 * Features:
 * - Request/Response logging
 * - Automatic token refresh
 * - Retry logic for failed requests
 * - Error handling with toast notifications
 * - Request/Response timing
 * - Request cancellation support
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, CancelTokenSource } from 'axios';

/**
 * API Error interface
 */
export interface APIError {
  message: string;
  details?: Record<string, any>;
  path?: string;
  status?: number;
}

/**
 * Request metadata for logging
 */
interface RequestMetadata {
  startTime: number;
  url: string;
  method: string;
}

/**
 * Retry configuration
 */
interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryableStatuses: number[];
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
};

/**
 * Store for request metadata
 */
const requestMetadataStore = new Map<string, RequestMetadata>();

/**
 * Flag to prevent multiple token refresh attempts
 */
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

/**
 * Subscribe to token refresh
 */
const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

/**
 * Notify all subscribers when token is refreshed
 */
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
};

/**
 * Create Axios instance with base configuration
 */
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * - Adds authentication token to requests
 * - Logs requests with timing information
 * - Tracks request metadata
 */
api.interceptors.request.use(
  (config) => {
    // Generate unique request ID
    const requestId = `${config.method}-${config.url}-${Date.now()}`;
    
    // Store request metadata for timing
    requestMetadataStore.set(requestId, {
      startTime: Date.now(),
      url: config.url || '',
      method: config.method?.toUpperCase() || 'UNKNOWN',
    });
    
    // Attach request ID to config for later retrieval
    (config as any).requestId = requestId;

    // Add authentication token if available
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp
    if (config.headers) {
      config.headers['X-Request-Time'] = new Date().toISOString();
    }

    // Log requests in development
    if (import.meta.env.DEV) {
      console.group(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
      console.log('Headers:', config.headers);
      console.log('Data:', config.data);
      console.log('Params:', config.params);
      console.groupEnd();
    }

    return config;
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * - Handles authentication errors with automatic token refresh
 * - Provides consistent error handling
 * - Logs responses with timing information
 * - Implements retry logic for failed requests
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Retrieve request metadata
    const requestId = (response.config as any).requestId;
    const metadata = requestMetadataStore.get(requestId);
    
    if (metadata) {
      const duration = Date.now() - metadata.startTime;
      
      // Log responses in development with timing
      if (import.meta.env.DEV) {
        console.group(`[API Response] ${metadata.method} ${metadata.url} (${duration}ms)`);
        console.log('Status:', response.status);
        console.log('Data:', response.data);
        console.log('Headers:', response.headers);
        console.groupEnd();
      }
      
      // Add timing header to response
      response.headers['x-response-time'] = `${duration}ms`;
      
      // Clean up metadata
      requestMetadataStore.delete(requestId);
    }

    return response;
  },
  async (error: AxiosError<{ error: APIError }>) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean; _retryCount?: number };
    const apiError = error.response?.data?.error;
    const status = error.response?.status;

    // Calculate request duration if metadata exists
    const requestId = (originalRequest as any)?.requestId;
    const metadata = requestMetadataStore.get(requestId);
    let duration = 0;
    
    if (metadata) {
      duration = Date.now() - metadata.startTime;
      requestMetadataStore.delete(requestId);
    }

    // Log errors with timing
    console.error('[API Response Error]', {
      status,
      message: apiError?.message || error.message,
      details: apiError?.details,
      path: apiError?.path,
      duration: `${duration}ms`,
      url: originalRequest?.url,
      method: originalRequest?.method,
    });

    // Handle 401 Unauthorized - Attempt token refresh
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        
        try {
          // Attempt to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          const response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token, refresh_token: newRefreshToken } = response.data;
          
          // Store new tokens
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }

          // Notify all subscribers
          onTokenRefreshed(access_token);
          isRefreshing = false;

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          isRefreshing = false;
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/auth/login';
          return Promise.reject(refreshError);
        }
      } else {
        // Token refresh in progress - wait for it
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(api(originalRequest));
          });
        });
      }
    }

    // Implement retry logic for retryable errors
    if (status && DEFAULT_RETRY_CONFIG.retryableStatuses.includes(status)) {
      const retryCount = originalRequest._retryCount || 0;
      
      if (retryCount < DEFAULT_RETRY_CONFIG.maxRetries) {
        originalRequest._retryCount = retryCount + 1;
        
        // Calculate exponential backoff delay
        const delay = DEFAULT_RETRY_CONFIG.retryDelay * Math.pow(2, retryCount);
        
        console.warn(`[API Retry] Attempt ${retryCount + 1}/${DEFAULT_RETRY_CONFIG.maxRetries} after ${delay}ms`);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay));
        
        // Retry request
        return api(originalRequest);
      }
    }

    // Return structured error
    return Promise.reject({
      status,
      message: apiError?.message || error.message || 'Network error. Please check your connection.',
      details: apiError?.details,
      path: apiError?.path,
    } as APIError);
  }
);

/**
 * Manual retry logic for failed requests
 * Use this for custom retry scenarios outside of automatic retry
 */
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        // Exponential backoff
        const backoffDelay = delay * Math.pow(2, i);
        console.warn(`[Manual Retry] Attempt ${i + 1}/${maxRetries} failed, retrying in ${backoffDelay}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoffDelay));
      }
    }
  }

  console.error(`[Manual Retry] All ${maxRetries} attempts failed`);
  throw lastError;
};

/**
 * Create a cancel token source for request cancellation
 */
export const createCancelToken = (): CancelTokenSource => {
  return axios.CancelToken.source();
};

/**
 * Check if error is a cancellation error
 */
export const isCancelError = (error: any): boolean => {
  return axios.isCancel(error);
};

/**
 * Configure retry settings for specific requests
 */
export const configureRetry = (config: Partial<RetryConfig>): RetryConfig => {
  return {
    ...DEFAULT_RETRY_CONFIG,
    ...config,
  };
};

/**
 * API request with custom retry configuration
 */
export const requestWithRetry = async <T>(
  requestFn: () => Promise<AxiosResponse<T>>,
  retryConfig?: Partial<RetryConfig>
): Promise<T> => {
  const config = configureRetry(retryConfig || {});
  let lastError: any;

  for (let i = 0; i < config.maxRetries; i++) {
    try {
      const response = await requestFn();
      return response.data;
    } catch (error: any) {
      lastError = error;
      
      // Check if error is retryable
      const status = error.status || error.response?.status;
      if (status && config.retryableStatuses.includes(status) && i < config.maxRetries - 1) {
        const delay = config.retryDelay * Math.pow(2, i);
        console.warn(`[Custom Retry] Attempt ${i + 1}/${config.maxRetries} failed, retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        break;
      }
    }
  }

  throw lastError;
};

/**
 * Helper function to handle file uploads
 */
export const uploadFile = async (
  endpoint: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  return api.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
};

/**
 * Helper function to download files
 */
export const downloadFile = async (
  endpoint: string,
  filename: string
): Promise<void> => {
  const response = await api.get(endpoint, {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Batch request helper - execute multiple requests in parallel
 */
export const batchRequest = async <T>(
  requests: (() => Promise<AxiosResponse<T>>)[]
): Promise<T[]> => {
  try {
    const responses = await Promise.all(requests.map(req => req()));
    return responses.map(res => res.data);
  } catch (error) {
    console.error('[Batch Request Error]', error);
    throw error;
  }
};

/**
 * Sequential request helper - execute requests one after another
 */
export const sequentialRequest = async <T>(
  requests: (() => Promise<AxiosResponse<T>>)[]
): Promise<T[]> => {
  const results: T[] = [];
  
  for (const request of requests) {
    try {
      const response = await request();
      results.push(response.data);
    } catch (error) {
      console.error('[Sequential Request Error]', error);
      throw error;
    }
  }
  
  return results;
};

/**
 * Polling helper - repeatedly call an endpoint until condition is met
 */
export const pollEndpoint = async <T>(
  requestFn: () => Promise<AxiosResponse<T>>,
  conditionFn: (data: T) => boolean,
  options: {
    interval?: number;
    maxAttempts?: number;
    timeout?: number;
  } = {}
): Promise<T> => {
  const interval = options.interval || 2000;
  const maxAttempts = options.maxAttempts || 30;
  const timeout = options.timeout || 60000;
  
  const startTime = Date.now();
  let attempts = 0;

  while (attempts < maxAttempts) {
    // Check timeout
    if (Date.now() - startTime > timeout) {
      throw new Error('Polling timeout exceeded');
    }

    try {
      const response = await requestFn();
      
      if (conditionFn(response.data)) {
        return response.data;
      }
    } catch (error) {
      console.warn(`[Polling] Attempt ${attempts + 1} failed:`, error);
    }

    attempts++;
    await new Promise(resolve => setTimeout(resolve, interval));
  }

  throw new Error('Polling max attempts exceeded');
};

/**
 * Request queue for rate limiting
 */
class RequestQueue {
  private queue: (() => Promise<any>)[] = [];
  private processing = false;
  private requestsPerSecond: number;
  private lastRequestTime = 0;

  constructor(requestsPerSecond: number = 10) {
    this.requestsPerSecond = requestsPerSecond;
  }

  async add<T>(requestFn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await requestFn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });

      if (!this.processing) {
        this.process();
      }
    });
  }

  private async process() {
    this.processing = true;

    while (this.queue.length > 0) {
      const now = Date.now();
      const timeSinceLastRequest = now - this.lastRequestTime;
      const minInterval = 1000 / this.requestsPerSecond;

      if (timeSinceLastRequest < minInterval) {
        await new Promise(resolve => setTimeout(resolve, minInterval - timeSinceLastRequest));
      }

      const request = this.queue.shift();
      if (request) {
        this.lastRequestTime = Date.now();
        await request();
      }
    }

    this.processing = false;
  }
}

/**
 * Global request queue instance
 */
export const requestQueue = new RequestQueue(10);

/**
 * Clear all stored tokens (useful for logout)
 */
export const clearTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};

/**
 * Get current access token
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * Set access token
 */
export const setAccessToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

/**
 * Set refresh token
 */
export const setRefreshToken = (token: string): void => {
  localStorage.setItem('refresh_token', token);
};

/**
 * API service object with utility methods
 */
export const apiService = {
  // Core instance
  instance: api,
  
  // Token management
  clearTokens,
  isAuthenticated,
  getAccessToken,
  setAccessToken,
  setRefreshToken,
  
  // Request utilities
  retry: retryRequest,
  requestWithRetry,
  batch: batchRequest,
  sequential: sequentialRequest,
  poll: pollEndpoint,
  queue: requestQueue,
  
  // File operations
  upload: uploadFile,
  download: downloadFile,
  
  // Cancellation
  createCancelToken,
  isCancelError,
  
  // Configuration
  configureRetry,
};

export default api;
