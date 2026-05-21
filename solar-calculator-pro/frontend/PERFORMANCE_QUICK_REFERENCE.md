# Performance Optimization Quick Reference

## Code Splitting

```typescript
// Lazy load with retry
import { lazyWithRetry } from '@utils/lazyLoad';
const Component = lazyWithRetry(() => import('./Component'));

// Prefetch on hover
import { prefetchOnHover } from '@utils/lazyLoad';
<Link onMouseEnter={prefetchOnHover(() => import('./Page'))}>Link</Link>

// Prefetch on idle
import { prefetchOnIdle } from '@utils/lazyLoad';
prefetchOnIdle([() => import('./Page1'), () => import('./Page2')]);
```

## Virtual Scrolling

```typescript
// Virtual list
import { VirtualList } from '@components/common/VirtualList';
<VirtualList
  items={items}
  itemHeight={50}
  containerHeight={600}
  renderItem={(item) => <div>{item.name}</div>}
/>

// Virtual grid
import { VirtualGrid } from '@components/common/VirtualList';
<VirtualGrid
  items={items}
  itemWidth={200}
  itemHeight={200}
  containerWidth={1000}
  containerHeight={600}
  renderItem={(item) => <div>{item.name}</div>}
/>
```

## Image Lazy Loading

```typescript
// Lazy image
import { LazyImage } from '@components/common/LazyImage';
<LazyImage src="/image.jpg" alt="Description" />

// Lazy background
import { LazyBackground } from '@components/common/LazyImage';
<LazyBackground src="/bg.jpg">Content</LazyBackground>

// Progressive image
import { ProgressiveImage } from '@components/common/LazyImage';
<ProgressiveImage src="/full.jpg" placeholderSrc="/thumb.jpg" alt="Description" />
```

## Performance Monitoring

```typescript
// Monitor render time
import { useRenderTime } from '@hooks/usePerformance';
useRenderTime('ComponentName');

// Monitor effect time
import { useEffectTime } from '@hooks/usePerformance';
useEffectTime('EffectName', [deps], () => { /* effect */ });

// Measure function execution
import { useMeasure } from '@hooks/usePerformance';
const fn = useMeasure('functionName', (arg) => { /* logic */ });

// Track re-renders
import { useWhyDidYouUpdate } from '@hooks/usePerformance';
useWhyDidYouUpdate('ComponentName', props);

// Debounce
import { useDebounce } from '@hooks/usePerformance';
const debouncedValue = useDebounce(value, 500);

// Throttle
import { useThrottle } from '@hooks/usePerformance';
const throttledFn = useThrottle(fn, 100);
```

## Performance Metrics

```typescript
// Get metrics
import { getPerformanceMetrics, logPerformanceMetrics } from '@utils/bundleAnalyzer';
const metrics = getPerformanceMetrics();
logPerformanceMetrics();

// Memory usage
import { getMemoryUsage, logMemoryUsage } from '@utils/bundleAnalyzer';
const memory = getMemoryUsage();
logMemoryUsage();

// Initialize monitoring
import { initPerformanceMonitoring } from '@utils/bundleAnalyzer';
initPerformanceMonitoring();
```

## Optimization Tips

### React.memo
```typescript
const Component = React.memo(({ data }) => <div>{data}</div>);
```

### useCallback
```typescript
const handleClick = useCallback(() => { /* logic */ }, [deps]);
```

### useMemo
```typescript
const expensiveValue = useMemo(() => computeExpensive(data), [data]);
```

### Avoid Inline Functions
```typescript
// Bad: <button onClick={() => handleClick(id)}>
// Good: <button onClick={handleClick}>
```

### Stable Keys
```typescript
// Bad: {items.map((item, i) => <div key={i}>)}
// Good: {items.map((item) => <div key={item.id}>)}
```

## Build Optimization

### Check Bundle Size
```bash
npm run build
```

### Analyze Bundle
Check `dist` folder for chunk sizes

### Production Build
```bash
npm run build
npm run preview
```

## Performance Checklist

- [ ] Routes are code-split
- [ ] Large components are lazy-loaded
- [ ] Images are lazy-loaded
- [ ] Virtual scrolling for large lists
- [ ] Bundle size optimized
- [ ] Console logs removed in production
- [ ] Performance monitoring enabled
- [ ] Expensive operations debounced/throttled
- [ ] Components memoized
- [ ] Production build tested

## Common Issues

### Slow Initial Load
- Check bundle sizes
- Reduce vendor chunks
- More code splitting
- Enable compression

### Slow Navigation
- Prefetch routes
- Reduce component complexity
- Optimize state management
- Check re-renders

### Memory Leaks
- Clean up effects
- Remove event listeners
- Cancel pending requests
- Clear intervals/timeouts

### Large Bundle
- Analyze bundle
- Remove unused dependencies
- Use tree-shaking
- Split large features
