# Frontend Performance Optimization Guide

This guide covers all the performance optimizations implemented in the Solar Calculator Pro frontend application.

## Table of Contents

1. [Code Splitting](#code-splitting)
2. [Lazy Loading](#lazy-loading)
3. [Bundle Optimization](#bundle-optimization)
4. [Virtual Scrolling](#virtual-scrolling)
5. [Image Lazy Loading](#image-lazy-loading)
6. [Performance Monitoring](#performance-monitoring)
7. [Best Practices](#best-practices)

## Code Splitting

### Route-Based Code Splitting

All routes are automatically code-split using React's `lazy()` function. This means each page is loaded only when needed.

```typescript
import { lazyWithRetry } from '@utils/lazyLoad';

const Dashboard = lazyWithRetry(() => import('@pages/Dashboard'));
```

### Component-Based Code Splitting

Large components can be lazy-loaded:

```typescript
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));

function MyComponent() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyChart />
    </Suspense>
  );
}
```

### Manual Chunk Splitting

The Vite configuration splits vendor libraries into separate chunks for better caching:

- `react-vendor`: React core libraries
- `primereact-vendor`: PrimeReact UI components
- `chart-vendor`: Recharts and D3 libraries
- `3d-vendor`: Three.js and React Three Fiber
- `form-vendor`: Form handling libraries
- `utils-vendor`: Utility libraries

## Lazy Loading

### Lazy Loading with Retry

Use `lazyWithRetry` for more reliable lazy loading with automatic retry on failure:

```typescript
import { lazyWithRetry } from '@utils/lazyLoad';

const MyComponent = lazyWithRetry(() => import('./MyComponent'), 3); // 3 retries
```

### Prefetching

Prefetch components before they're needed:

```typescript
import { prefetchOnHover, prefetchOnIdle } from '@utils/lazyLoad';

// Prefetch on hover
<Link 
  to="/dashboard" 
  onMouseEnter={prefetchOnHover(() => import('./Dashboard'))}
>
  Dashboard
</Link>

// Prefetch on idle
prefetchOnIdle([
  () => import('./Dashboard'),
  () => import('./Settings'),
]);
```

### Lazy Loading with Timeout

Set a timeout for lazy loading to prevent indefinite loading:

```typescript
import { lazyWithTimeout } from '@utils/lazyLoad';

const MyComponent = lazyWithTimeout(() => import('./MyComponent'), 5000);
```

## Bundle Optimization

### Build Configuration

The Vite configuration includes several optimizations:

1. **Minification**: Uses Terser for aggressive minification
2. **Tree Shaking**: Removes unused code automatically
3. **Console Removal**: Removes console.log in production
4. **Chunk Size Optimization**: Warns about large chunks (>1000KB)

### Analyzing Bundle Size

Run the build with analysis:

```bash
npm run build
```

Check the `dist` folder for chunk sizes.

### Reducing Bundle Size

1. **Use named imports**: `import { Button } from 'primereact/button'` instead of `import * as PrimeReact from 'primereact'`
2. **Avoid large dependencies**: Check bundle size before adding new dependencies
3. **Use dynamic imports**: Load heavy features only when needed
4. **Enable compression**: Use gzip or brotli compression on the server

## Virtual Scrolling

### VirtualList Component

For large lists, use the `VirtualList` component to render only visible items:

```typescript
import { VirtualList } from '@components/common/VirtualList';

function MyList({ items }) {
  return (
    <VirtualList
      items={items}
      itemHeight={50}
      containerHeight={600}
      renderItem={(item, index) => (
        <div key={index}>{item.name}</div>
      )}
      overscan={3}
    />
  );
}
```

### VirtualGrid Component

For grid layouts:

```typescript
import { VirtualGrid } from '@components/common/VirtualList';

function MyGrid({ items }) {
  return (
    <VirtualGrid
      items={items}
      itemWidth={200}
      itemHeight={200}
      containerWidth={1000}
      containerHeight={600}
      renderItem={(item, index) => (
        <div key={index}>{item.name}</div>
      )}
      gap={10}
    />
  );
}
```

### When to Use Virtual Scrolling

- Lists with more than 100 items
- Grids with more than 50 items
- Any scrollable content with performance issues

## Image Lazy Loading

### LazyImage Component

Lazy load images when they enter the viewport:

```typescript
import { LazyImage } from '@components/common/LazyImage';

function MyComponent() {
  return (
    <LazyImage
      src="/path/to/image.jpg"
      alt="Description"
      placeholder="/path/to/placeholder.jpg"
      threshold={0.1}
      rootMargin="50px"
    />
  );
}
```

### LazyBackground Component

Lazy load background images:

```typescript
import { LazyBackground } from '@components/common/LazyImage';

function MyComponent() {
  return (
    <LazyBackground
      src="/path/to/background.jpg"
      placeholder="/path/to/placeholder.jpg"
    >
      <div>Content</div>
    </LazyBackground>
  );
}
```

### ProgressiveImage Component

Load low-quality placeholder first, then full-quality image:

```typescript
import { ProgressiveImage } from '@components/common/LazyImage';

function MyComponent() {
  return (
    <ProgressiveImage
      src="/path/to/full-quality.jpg"
      placeholderSrc="/path/to/low-quality.jpg"
      alt="Description"
    />
  );
}
```

## Performance Monitoring

### Render Time Monitoring

Monitor component render time:

```typescript
import { useRenderTime } from '@hooks/usePerformance';

function MyComponent() {
  useRenderTime('MyComponent');
  
  return <div>Content</div>;
}
```

### Effect Time Monitoring

Monitor effect execution time:

```typescript
import { useEffectTime } from '@hooks/usePerformance';

function MyComponent() {
  useEffectTime('DataFetch', [userId], () => {
    fetchUserData(userId);
  });
  
  return <div>Content</div>;
}
```

### Function Execution Time

Measure function execution time:

```typescript
import { useMeasure } from '@hooks/usePerformance';

function MyComponent() {
  const expensiveCalculation = useMeasure('expensiveCalculation', (data) => {
    // ... expensive operation
    return result;
  });
  
  return <button onClick={() => expensiveCalculation(data)}>Calculate</button>;
}
```

### Why Did You Update

Track why a component re-rendered:

```typescript
import { useWhyDidYouUpdate } from '@hooks/usePerformance';

function MyComponent(props) {
  useWhyDidYouUpdate('MyComponent', props);
  
  return <div>Content</div>;
}
```

### Performance Metrics

Get detailed performance metrics:

```typescript
import { getPerformanceMetrics, logPerformanceMetrics } from '@utils/bundleAnalyzer';

// Get metrics
const metrics = getPerformanceMetrics();
console.log(metrics);

// Log metrics to console
logPerformanceMetrics();
```

### Memory Usage

Monitor memory usage (Chrome only):

```typescript
import { getMemoryUsage, logMemoryUsage } from '@utils/bundleAnalyzer';

// Get memory usage
const memory = getMemoryUsage();
console.log(memory);

// Log memory usage
logMemoryUsage();
```

### Initialize Monitoring

Initialize all performance monitoring:

```typescript
import { initPerformanceMonitoring } from '@utils/bundleAnalyzer';

// In your main.tsx or App.tsx
if (process.env.NODE_ENV === 'development') {
  initPerformanceMonitoring();
}
```

## Best Practices

### 1. Optimize Re-renders

Use `React.memo` for expensive components:

```typescript
import React from 'react';

const ExpensiveComponent = React.memo(({ data }) => {
  // ... expensive rendering
  return <div>{data}</div>;
});
```

### 2. Use Debouncing and Throttling

For expensive operations triggered by user input:

```typescript
import { useDebounce, useThrottle } from '@hooks/usePerformance';

function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  
  useEffect(() => {
    // This only runs 500ms after the user stops typing
    searchAPI(debouncedSearchTerm);
  }, [debouncedSearchTerm]);
  
  return <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />;
}
```

### 3. Avoid Inline Functions

Don't create new functions on every render:

```typescript
// Bad
<button onClick={() => handleClick(id)}>Click</button>

// Good
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<button onClick={handleButtonClick}>Click</button>
```

### 4. Use Keys Properly

Always use stable, unique keys for lists:

```typescript
// Bad
{items.map((item, index) => <div key={index}>{item.name}</div>)}

// Good
{items.map((item) => <div key={item.id}>{item.name}</div>)}
```

### 5. Optimize Images

- Use appropriate image formats (WebP for photos, SVG for icons)
- Compress images before uploading
- Use responsive images with `srcset`
- Lazy load images below the fold

### 6. Code Splitting Strategy

- Split by route (already implemented)
- Split large features
- Split vendor libraries
- Don't over-split (too many chunks can hurt performance)

### 7. Avoid Large Dependencies

Before adding a new dependency:

1. Check its bundle size on [Bundlephobia](https://bundlephobia.com/)
2. Look for lighter alternatives
3. Consider if you can implement it yourself

### 8. Use Production Builds

Always test with production builds:

```bash
npm run build
npm run preview
```

Development builds are much slower and larger.

### 9. Monitor Performance

Regularly check:

- Lighthouse scores
- Bundle sizes
- Load times
- Memory usage
- Network requests

### 10. Progressive Enhancement

Build for the slowest devices first:

- Test on slow 3G networks
- Test on low-end devices
- Use performance budgets
- Implement loading states

## Performance Checklist

- [ ] All routes are code-split
- [ ] Large components are lazy-loaded
- [ ] Images are lazy-loaded
- [ ] Virtual scrolling is used for large lists
- [ ] Bundle size is optimized
- [ ] Console logs are removed in production
- [ ] Performance monitoring is enabled in development
- [ ] Expensive operations are debounced/throttled
- [ ] Components are memoized where appropriate
- [ ] Production build is tested

## Troubleshooting

### Slow Initial Load

1. Check bundle sizes
2. Reduce vendor chunk sizes
3. Implement more aggressive code splitting
4. Enable compression on server

### Slow Navigation

1. Prefetch routes on hover
2. Reduce component complexity
3. Optimize state management
4. Check for unnecessary re-renders

### Memory Leaks

1. Clean up effects properly
2. Remove event listeners
3. Cancel pending requests
4. Clear intervals/timeouts

### Large Bundle Size

1. Analyze bundle with build tools
2. Remove unused dependencies
3. Use tree-shaking
4. Split large features

## Resources

- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
