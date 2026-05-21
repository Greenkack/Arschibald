/**
 * Performance Monitoring Hooks
 * 
 * Custom hooks for monitoring component and application performance.
 */

import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook to measure component render time
 * 
 * @param componentName - Name of the component for logging
 * @param enabled - Whether to enable performance monitoring (default: true in development)
 * 
 * @example
 * function MyComponent() {
 *   useRenderTime('MyComponent');
 *   return <div>Content</div>;
 * }
 */
export const useRenderTime = (componentName: string, enabled = process.env.NODE_ENV === 'development') => {
  const renderStartTime = useRef<number>(0);

  useEffect(() => {
    if (!enabled) return;

    renderStartTime.current = performance.now();

    return () => {
      const renderTime = performance.now() - renderStartTime.current;
      
      if (renderTime > 16) { // More than one frame at 60fps
        console.warn(
          `[Performance] ${componentName} render took ${renderTime.toFixed(2)}ms`
        );
      }
    };
  });
};

/**
 * Hook to measure effect execution time
 * 
 * @param effectName - Name of the effect for logging
 * @param dependencies - Effect dependencies
 * @param enabled - Whether to enable performance monitoring
 * 
 * @example
 * useEffectTime('DataFetch', [userId], () => {
 *   fetchUserData(userId);
 * });
 */
export const useEffectTime = (
  effectName: string,
  dependencies: any[],
  callback: () => void | (() => void),
  enabled = process.env.NODE_ENV === 'development'
) => {
  useEffect(() => {
    if (!enabled) {
      return callback();
    }

    const startTime = performance.now();
    const cleanup = callback();
    const executionTime = performance.now() - startTime;

    if (executionTime > 10) {
      console.warn(
        `[Performance] Effect "${effectName}" took ${executionTime.toFixed(2)}ms`
      );
    }

    return cleanup;
  }, dependencies);
};

/**
 * Hook to track component mount/unmount
 * 
 * @param componentName - Name of the component
 * @param enabled - Whether to enable tracking
 * 
 * @example
 * function MyComponent() {
 *   useComponentLifecycle('MyComponent');
 *   return <div>Content</div>;
 * }
 */
export const useComponentLifecycle = (
  componentName: string,
  enabled = process.env.NODE_ENV === 'development'
) => {
  const mountTime = useRef<number>(0);

  useEffect(() => {
    if (!enabled) return;

    mountTime.current = performance.now();
    console.log(`[Lifecycle] ${componentName} mounted`);

    return () => {
      const lifetime = performance.now() - mountTime.current;
      console.log(
        `[Lifecycle] ${componentName} unmounted after ${lifetime.toFixed(2)}ms`
      );
    };
  }, [componentName, enabled]);
};

/**
 * Hook to measure function execution time
 * 
 * @param functionName - Name of the function for logging
 * @param enabled - Whether to enable performance monitoring
 * @returns Wrapped function that measures execution time
 * 
 * @example
 * const expensiveCalculation = useMeasure('expensiveCalculation', (data) => {
 *   // ... expensive operation
 *   return result;
 * });
 */
export const useMeasure = <T extends (...args: any[]) => any>(
  functionName: string,
  fn: T,
  enabled = process.env.NODE_ENV === 'development'
): T => {
  return useCallback(
    ((...args: any[]) => {
      if (!enabled) {
        return fn(...args);
      }

      const startTime = performance.now();
      const result = fn(...args);
      const executionTime = performance.now() - startTime;

      if (executionTime > 10) {
        console.warn(
          `[Performance] Function "${functionName}" took ${executionTime.toFixed(2)}ms`
        );
      }

      return result;
    }) as T,
    [fn, functionName, enabled]
  );
};

/**
 * Hook to track re-renders
 * 
 * @param componentName - Name of the component
 * @param props - Component props to track
 * @param enabled - Whether to enable tracking
 * 
 * @example
 * function MyComponent(props) {
 *   useWhyDidYouUpdate('MyComponent', props);
 *   return <div>Content</div>;
 * }
 */
export const useWhyDidYouUpdate = (
  componentName: string,
  props: Record<string, any>,
  enabled = process.env.NODE_ENV === 'development'
) => {
  const previousProps = useRef<Record<string, any>>();

  useEffect(() => {
    if (!enabled) return;

    if (previousProps.current) {
      const allKeys = Object.keys({ ...previousProps.current, ...props });
      const changedProps: Record<string, { from: any; to: any }> = {};

      allKeys.forEach((key) => {
        if (previousProps.current![key] !== props[key]) {
          changedProps[key] = {
            from: previousProps.current![key],
            to: props[key],
          };
        }
      });

      if (Object.keys(changedProps).length > 0) {
        console.log(`[Why Update] ${componentName}`, changedProps);
      }
    }

    previousProps.current = props;
  });
};

/**
 * Hook to debounce expensive operations
 * 
 * @param value - Value to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced value
 * 
 * @example
 * const debouncedSearchTerm = useDebounce(searchTerm, 500);
 */
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Hook to throttle expensive operations
 * 
 * @param callback - Callback to throttle
 * @param delay - Delay in milliseconds
 * @returns Throttled callback
 * 
 * @example
 * const throttledScroll = useThrottle(handleScroll, 100);
 */
export const useThrottle = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const lastRun = useRef<number>(Date.now());

  return useCallback(
    ((...args: any[]) => {
      const now = Date.now();
      
      if (now - lastRun.current >= delay) {
        callback(...args);
        lastRun.current = now;
      }
    }) as T,
    [callback, delay]
  );
};

// Import useState for useDebounce
import { useState } from 'react';
