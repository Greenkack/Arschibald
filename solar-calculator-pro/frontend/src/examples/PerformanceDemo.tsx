/**
 * Performance Optimization Demo
 * 
 * This file demonstrates all the performance optimization features
 * available in the application.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { VirtualList, VirtualGrid } from '@components/common/VirtualList';
import { LazyImage, LazyBackground, ProgressiveImage } from '@components/common/LazyImage';
import {
  useRenderTime,
  useWhyDidYouUpdate,
  useMeasure,
  useDebounce,
  useThrottle,
} from '@hooks/usePerformance';
import {
  getPerformanceMetrics,
  logPerformanceMetrics,
  getMemoryUsage,
  logMemoryUsage,
} from '@utils/bundleAnalyzer';

/**
 * Virtual List Demo
 */
const VirtualListDemo: React.FC = () => {
  // Generate large dataset
  const items = useMemo(
    () => Array.from({ length: 10000 }, (_, i) => ({ id: i, name: `Item ${i}` })),
    []
  );

  return (
    <Card title="Virtual List Demo" className="mb-4">
      <p className="mb-3">
        Rendering 10,000 items efficiently using virtual scrolling.
        Only visible items are rendered.
      </p>
      <VirtualList
        items={items}
        itemHeight={50}
        containerHeight={400}
        renderItem={(item) => (
          <div
            style={{
              padding: '10px',
              borderBottom: '1px solid #e0e0e0',
            }}
          >
            {item.name}
          </div>
        )}
      />
    </Card>
  );
};

/**
 * Virtual Grid Demo
 */
const VirtualGridDemo: React.FC = () => {
  const items = useMemo(
    () => Array.from({ length: 1000 }, (_, i) => ({ id: i, name: `Item ${i}` })),
    []
  );

  return (
    <Card title="Virtual Grid Demo" className="mb-4">
      <p className="mb-3">
        Rendering 1,000 items in a grid layout using virtual scrolling.
      </p>
      <VirtualGrid
        items={items}
        itemWidth={150}
        itemHeight={150}
        containerWidth={800}
        containerHeight={400}
        gap={10}
        renderItem={(item) => (
          <div
            style={{
              padding: '20px',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
              textAlign: 'center',
            }}
          >
            {item.name}
          </div>
        )}
      />
    </Card>
  );
};

/**
 * Lazy Image Demo
 */
const LazyImageDemo: React.FC = () => {
  return (
    <Card title="Lazy Image Loading Demo" className="mb-4">
      <p className="mb-3">
        Images are loaded only when they enter the viewport.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        {Array.from({ length: 9 }, (_, i) => (
          <LazyImage
            key={i}
            src={`https://picsum.photos/300/200?random=${i}`}
            alt={`Demo image ${i}`}
            style={{ width: '100%', height: 'auto', borderRadius: '4px' }}
          />
        ))}
      </div>
    </Card>
  );
};

/**
 * Progressive Image Demo
 */
const ProgressiveImageDemo: React.FC = () => {
  return (
    <Card title="Progressive Image Loading Demo" className="mb-4">
      <p className="mb-3">
        Low-quality placeholder loads first, then full-quality image.
      </p>
      <ProgressiveImage
        src="https://picsum.photos/800/400"
        placeholderSrc="https://picsum.photos/80/40"
        alt="Progressive demo"
        style={{ width: '100%', height: 'auto', borderRadius: '4px' }}
      />
    </Card>
  );
};

/**
 * Lazy Background Demo
 */
const LazyBackgroundDemo: React.FC = () => {
  return (
    <Card title="Lazy Background Image Demo" className="mb-4">
      <LazyBackground
        src="https://picsum.photos/800/300"
        style={{
          height: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '24px',
          fontWeight: 'bold',
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
          borderRadius: '4px',
        }}
      >
        Background Image Loaded Lazily
      </LazyBackground>
    </Card>
  );
};

/**
 * Performance Monitoring Demo
 */
const PerformanceMonitoringDemo: React.FC = () => {
  useRenderTime('PerformanceMonitoringDemo');

  const handleGetMetrics = () => {
    const metrics = getPerformanceMetrics();
    console.log('Performance Metrics:', metrics);
    logPerformanceMetrics();
  };

  const handleGetMemory = () => {
    const memory = getMemoryUsage();
    console.log('Memory Usage:', memory);
    logMemoryUsage();
  };

  return (
    <Card title="Performance Monitoring Demo" className="mb-4">
      <p className="mb-3">
        Monitor application performance and memory usage.
        Check the browser console for detailed metrics.
      </p>
      <div style={{ display: 'flex', gap: '10px' }}>
        <Button label="Get Performance Metrics" onClick={handleGetMetrics} />
        <Button label="Get Memory Usage" onClick={handleGetMemory} />
      </div>
    </Card>
  );
};

/**
 * Debounce Demo
 */
const DebounceDemo: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Simulate API call
  React.useEffect(() => {
    if (debouncedSearchTerm) {
      // This only runs 500ms after the user stops typing
      const results = Array.from(
        { length: 5 },
        (_, i) => `Result ${i + 1} for "${debouncedSearchTerm}"`
      );
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [debouncedSearchTerm]);

  return (
    <Card title="Debounce Demo" className="mb-4">
      <p className="mb-3">
        Search is debounced by 500ms. API call only happens after you stop typing.
      </p>
      <InputText
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Type to search..."
        className="w-full mb-3"
      />
      {searchResults.length > 0 && (
        <ul>
          {searchResults.map((result, i) => (
            <li key={i}>{result}</li>
          ))}
        </ul>
      )}
    </Card>
  );
};

/**
 * Throttle Demo
 */
const ThrottleDemo: React.FC = () => {
  const [scrollCount, setScrollCount] = useState(0);
  const [throttledScrollCount, setThrottledScrollCount] = useState(0);

  const handleScroll = useCallback(() => {
    setScrollCount((prev) => prev + 1);
  }, []);

  const handleThrottledScroll = useThrottle(() => {
    setThrottledScrollCount((prev) => prev + 1);
  }, 1000);

  return (
    <Card title="Throttle Demo" className="mb-4">
      <p className="mb-3">
        Scroll the box below. Normal handler fires on every scroll event,
        throttled handler fires at most once per second.
      </p>
      <div
        style={{
          height: '200px',
          overflow: 'auto',
          border: '1px solid #e0e0e0',
          padding: '10px',
          marginBottom: '10px',
        }}
        onScroll={(e) => {
          handleScroll();
          handleThrottledScroll();
        }}
      >
        <div style={{ height: '1000px' }}>
          <p>Normal scroll count: {scrollCount}</p>
          <p>Throttled scroll count: {throttledScrollCount}</p>
          <p>Scroll down to see the difference...</p>
        </div>
      </div>
    </Card>
  );
};

/**
 * Memoization Demo
 */
const MemoizationDemo: React.FC = () => {
  const [count, setCount] = useState(0);
  const [input, setInput] = useState('');

  // Expensive calculation (simulated)
  const expensiveCalculation = useMeasure('expensiveCalculation', (num: number) => {
    let result = 0;
    for (let i = 0; i < 1000000; i++) {
      result += num;
    }
    return result;
  });

  // Memoized value - only recalculates when count changes
  const memoizedValue = useMemo(() => expensiveCalculation(count), [count, expensiveCalculation]);

  return (
    <Card title="Memoization Demo" className="mb-4">
      <p className="mb-3">
        The expensive calculation is memoized and only runs when count changes.
        Typing in the input doesn't trigger recalculation.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div>
          <Button label="Increment Count" onClick={() => setCount(count + 1)} />
          <span style={{ marginLeft: '10px' }}>Count: {count}</span>
        </div>
        <div>
          <InputText
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type here (doesn't trigger calculation)"
            className="w-full"
          />
        </div>
        <div>Memoized Result: {memoizedValue}</div>
      </div>
    </Card>
  );
};

/**
 * Why Did You Update Demo
 */
const WhyDidYouUpdateDemo: React.FC<{ value: string; count: number }> = ({ value, count }) => {
  useWhyDidYouUpdate('WhyDidYouUpdateDemo', { value, count });

  return (
    <div style={{ padding: '10px', border: '1px solid #e0e0e0', borderRadius: '4px' }}>
      <p>Value: {value}</p>
      <p>Count: {count}</p>
      <p style={{ fontSize: '12px', color: '#666' }}>
        Check console to see which props changed
      </p>
    </div>
  );
};

const WhyDidYouUpdateDemoContainer: React.FC = () => {
  const [value, setValue] = useState('');
  const [count, setCount] = useState(0);

  return (
    <Card title="Why Did You Update Demo" className="mb-4">
      <p className="mb-3">
        Track which props changed and caused a re-render.
        Check the browser console for details.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '10px' }}>
        <InputText
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Change value"
        />
        <Button label="Increment Count" onClick={() => setCount(count + 1)} />
      </div>
      <WhyDidYouUpdateDemo value={value} count={count} />
    </Card>
  );
};

/**
 * Main Performance Demo Component
 */
export const PerformanceDemo: React.FC = () => {
  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Performance Optimization Demo</h1>
      <p className="mb-4">
        This page demonstrates all the performance optimization features available in the application.
      </p>

      <VirtualListDemo />
      <VirtualGridDemo />
      <LazyImageDemo />
      <ProgressiveImageDemo />
      <LazyBackgroundDemo />
      <PerformanceMonitoringDemo />
      <DebounceDemo />
      <ThrottleDemo />
      <MemoizationDemo />
      <WhyDidYouUpdateDemoContainer />
    </div>
  );
};

export default PerformanceDemo;
