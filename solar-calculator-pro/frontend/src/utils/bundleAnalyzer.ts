/**
 * Bundle Size Analyzer
 * 
 * Utilities for analyzing and optimizing bundle size in development.
 */

/**
 * Log component render performance
 */
export const logComponentPerformance = (componentName: string) => {
  if (process.env.NODE_ENV === 'development') {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 16) { // More than one frame (60fps)
        console.warn(
          `[Performance] ${componentName} took ${renderTime.toFixed(2)}ms to render`
        );
      }
    };
  }
  
  return () => {};
};

/**
 * Measure bundle size impact
 */
export const measureBundleImpact = (moduleName: string, size: number) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Bundle] ${moduleName}: ${(size / 1024).toFixed(2)}KB`);
  }
};

/**
 * Check if a module should be lazy loaded
 */
export const shouldLazyLoad = (moduleSize: number, threshold = 50 * 1024) => {
  return moduleSize > threshold;
};

/**
 * Get performance metrics
 */
export const getPerformanceMetrics = () => {
  if (typeof window === 'undefined' || !window.performance) {
    return null;
  }

  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  if (!navigation) {
    return null;
  }

  return {
    // Page load metrics
    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
    
    // Network metrics
    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
    tcp: navigation.connectEnd - navigation.connectStart,
    request: navigation.responseStart - navigation.requestStart,
    response: navigation.responseEnd - navigation.responseStart,
    
    // Processing metrics
    domProcessing: navigation.domComplete - navigation.domInteractive,
    
    // Total time
    totalTime: navigation.loadEventEnd - navigation.fetchStart,
  };
};

/**
 * Log performance metrics to console
 */
export const logPerformanceMetrics = () => {
  if (process.env.NODE_ENV === 'development') {
    const metrics = getPerformanceMetrics();
    
    if (metrics) {
      console.group('[Performance Metrics]');
      console.log('DOM Content Loaded:', `${metrics.domContentLoaded.toFixed(2)}ms`);
      console.log('Load Complete:', `${metrics.loadComplete.toFixed(2)}ms`);
      console.log('DNS Lookup:', `${metrics.dns.toFixed(2)}ms`);
      console.log('TCP Connection:', `${metrics.tcp.toFixed(2)}ms`);
      console.log('Request Time:', `${metrics.request.toFixed(2)}ms`);
      console.log('Response Time:', `${metrics.response.toFixed(2)}ms`);
      console.log('DOM Processing:', `${metrics.domProcessing.toFixed(2)}ms`);
      console.log('Total Time:', `${metrics.totalTime.toFixed(2)}ms`);
      console.groupEnd();
    }
  }
};

/**
 * Monitor long tasks
 */
export const monitorLongTasks = () => {
  if (process.env.NODE_ENV === 'development' && 'PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.warn(
            `[Long Task] Duration: ${entry.duration.toFixed(2)}ms`,
            entry
          );
        }
      });
      
      observer.observe({ entryTypes: ['longtask'] });
      
      return () => observer.disconnect();
    } catch (e) {
      // PerformanceObserver might not support longtask
      console.log('[Performance] Long task monitoring not supported');
    }
  }
  
  return () => {};
};

/**
 * Get memory usage (Chrome only)
 */
export const getMemoryUsage = () => {
  if (
    process.env.NODE_ENV === 'development' &&
    'memory' in performance &&
    (performance as any).memory
  ) {
    const memory = (performance as any).memory;
    
    return {
      usedJSHeapSize: (memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
      totalJSHeapSize: (memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
      jsHeapSizeLimit: (memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB',
    };
  }
  
  return null;
};

/**
 * Log memory usage
 */
export const logMemoryUsage = () => {
  if (process.env.NODE_ENV === 'development') {
    const memory = getMemoryUsage();
    
    if (memory) {
      console.group('[Memory Usage]');
      console.log('Used JS Heap:', memory.usedJSHeapSize);
      console.log('Total JS Heap:', memory.totalJSHeapSize);
      console.log('JS Heap Limit:', memory.jsHeapSizeLimit);
      console.groupEnd();
    }
  }
};

/**
 * Initialize performance monitoring
 */
export const initPerformanceMonitoring = () => {
  if (process.env.NODE_ENV === 'development') {
    // Log metrics after page load
    window.addEventListener('load', () => {
      setTimeout(() => {
        logPerformanceMetrics();
        logMemoryUsage();
      }, 0);
    });
    
    // Monitor long tasks
    const cleanup = monitorLongTasks();
    
    // Log memory usage periodically
    const memoryInterval = setInterval(() => {
      logMemoryUsage();
    }, 30000); // Every 30 seconds
    
    return () => {
      cleanup();
      clearInterval(memoryInterval);
    };
  }
  
  return () => {};
};
