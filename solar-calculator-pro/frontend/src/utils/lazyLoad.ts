/**
 * Lazy Loading Utilities
 * 
 * Utilities for lazy loading components with retry logic and error handling.
 */

import { lazy, ComponentType } from 'react';

/**
 * Retry function for failed lazy loads
 */
const retry = <T extends ComponentType<any>>(
  fn: () => Promise<{ default: T }>,
  retriesLeft = 3,
  interval = 1000
): Promise<{ default: T }> => {
  return new Promise((resolve, reject) => {
    fn()
      .then(resolve)
      .catch((error) => {
        setTimeout(() => {
          if (retriesLeft === 1) {
            reject(error);
            return;
          }

          // Retry with exponential backoff
          retry(fn, retriesLeft - 1, interval * 2).then(resolve, reject);
        }, interval);
      });
  });
};

/**
 * Lazy load a component with retry logic
 * 
 * @param importFn - Function that returns a dynamic import
 * @param retries - Number of retries (default: 3)
 * @returns Lazy loaded component
 * 
 * @example
 * const Dashboard = lazyWithRetry(() => import('./pages/Dashboard'));
 */
export const lazyWithRetry = <T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  retries = 3
) => {
  return lazy(() => retry(importFn, retries));
};

/**
 * Preload a lazy component
 * 
 * @param importFn - Function that returns a dynamic import
 * 
 * @example
 * const Dashboard = lazy(() => import('./pages/Dashboard'));
 * preloadComponent(() => import('./pages/Dashboard'));
 */
export const preloadComponent = (importFn: () => Promise<any>) => {
  importFn();
};

/**
 * Lazy load multiple components
 * 
 * @param imports - Object with component names as keys and import functions as values
 * @returns Object with lazy loaded components
 * 
 * @example
 * const { Dashboard, Settings } = lazyLoadMultiple({
 *   Dashboard: () => import('./pages/Dashboard'),
 *   Settings: () => import('./pages/Settings'),
 * });
 */
export const lazyLoadMultiple = <T extends Record<string, () => Promise<any>>>(
  imports: T
): { [K in keyof T]: ReturnType<typeof lazy> } => {
  const result: any = {};
  
  for (const [key, importFn] of Object.entries(imports)) {
    result[key] = lazyWithRetry(importFn);
  }
  
  return result;
};

/**
 * Prefetch components on hover
 * 
 * @param importFn - Function that returns a dynamic import
 * @returns Event handler for onMouseEnter
 * 
 * @example
 * <Link to="/dashboard" onMouseEnter={prefetchOnHover(() => import('./pages/Dashboard'))}>
 *   Dashboard
 * </Link>
 */
export const prefetchOnHover = (importFn: () => Promise<any>) => {
  let prefetched = false;
  
  return () => {
    if (!prefetched) {
      prefetched = true;
      importFn();
    }
  };
};

/**
 * Prefetch components on idle
 * 
 * Uses requestIdleCallback to prefetch components when the browser is idle.
 * 
 * @param imports - Array of import functions
 * 
 * @example
 * prefetchOnIdle([
 *   () => import('./pages/Dashboard'),
 *   () => import('./pages/Settings'),
 * ]);
 */
export const prefetchOnIdle = (imports: Array<() => Promise<any>>) => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      imports.forEach((importFn) => importFn());
    });
  } else {
    // Fallback for browsers that don't support requestIdleCallback
    setTimeout(() => {
      imports.forEach((importFn) => importFn());
    }, 1);
  }
};

/**
 * Lazy load with timeout
 * 
 * @param importFn - Function that returns a dynamic import
 * @param timeout - Timeout in milliseconds (default: 10000)
 * @returns Lazy loaded component
 * 
 * @example
 * const Dashboard = lazyWithTimeout(() => import('./pages/Dashboard'), 5000);
 */
export const lazyWithTimeout = <T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  timeout = 10000
) => {
  return lazy(() => {
    return Promise.race([
      importFn(),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Component load timeout')), timeout)
      ),
    ]);
  });
};

/**
 * Create a lazy component with custom loading and error boundaries
 * 
 * @param importFn - Function that returns a dynamic import
 * @param options - Options for loading and error handling
 * @returns Lazy loaded component with boundaries
 */
export interface LazyComponentOptions {
  retries?: number;
  timeout?: number;
  onError?: (error: Error) => void;
}

export const createLazyComponent = <T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  options: LazyComponentOptions = {}
) => {
  const { retries = 3, timeout = 10000, onError } = options;

  return lazy(() => {
    const loadPromise = retry(importFn, retries);
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Component load timeout')), timeout)
    );

    return Promise.race([loadPromise, timeoutPromise]).catch((error) => {
      onError?.(error);
      throw error;
    });
  });
};
