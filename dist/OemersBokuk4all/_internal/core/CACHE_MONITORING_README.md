# Cache Performance Monitoring System

Comprehensive cache performance monitoring with detailed metrics tracking, trend analysis, automatic cleanup, and performance degradation alerts.

## Overview

The Cache Performance Monitoring system provides real-time insights into cache behavior, helping identify performance issues and optimize cache configuration. It includes:

- **Detailed Hit Rate Tracking**: Track cache hit rates with historical data and statistics
- **Performance Analytics**: Analyze trends and detect performance degradation
- **Automatic Cleanup**: Monitor cache size and trigger cleanup when needed
- **Performance Alerts**: Get notified when performance degrades below thresholds

## Quick Start

### Basic Monitoring

```python
from core.cache_monitoring import (
    start_cache_monitoring,
    get_cache_performance_report
)

# Start monitoring with 60-second intervals
start_cache_monitoring(interval_seconds=60)

# Get performance report
report = get_cache_performance_report()
print(f"Hit Rate: {report['layers']['memory']['hit_rate']['hit_rate']:.2%}")
```

### Detailed Metrics

```python
from core.cache_monitoring import get_detailed_metrics

# Get detailed metrics for last hour
metrics = get_detailed_metrics("memory", window_minutes=60)

for metric_type, stats in metrics["metrics"].items():
    print(f"{metric_type}:")
    print(f"  Current: {stats['current']:.4f}")
    print(f"  Average: {stats['average']:.4f}")
    print(f"  Trend: {stats['trend']}")
```

### Automatic Cleanup

```python
from core.cache_monitoring import (
    enable_automatic_cleanup,
    register_cleanup_callback
)

# Enable automatic cleanup at 90% utilization
enable_automatic_cleanup(threshold=0.9)

# Register custom cleanup callback
def my_cleanup():
    print("Performing custom cleanup...")
    # Your cleanup logic here

register_cleanup_callback(my_cleanup)
```

### Performance Alerts

```python
from core.cache_monitoring import detect_performance_issues

# Check for performance issues
issues = detect_performance_issues()

if issues["degradation"]:
    print(f"Performance degraded by {issues['degradation']['degradation_percent']:.1f}%")

for alert in issues["alerts"]:
    print(f"[{alert['severity']}] {alert['message']}")

for recommendation in issues["recommendations"]:
    print(f"Recommendation: {recommendation}")
```

## Core Components

### CacheMetricsCollector

Collects and stores cache performance metrics over time.

```python
from core.cache_monitoring import CacheMetricsCollector

collector = CacheMetricsCollector(history_size=1000)

# Record metric
collector.record_metric("memory", "hit_rate", 0.85)

# Get metrics with filters
metrics = collector.get_metrics(
    layer="memory",
    metric_type="hit_rate",
    since=datetime.now() - timedelta(minutes=5)
)

# Calculate average
avg = collector.calculate_average("memory", "hit_rate", window_minutes=5)

# Calculate trend
trend = collector.calculate_trend("memory", "hit_rate", window_minutes=5)
# Returns: "improving", "degrading", or "stable"
```

### CachePerformanceAnalyzer

Analyzes cache performance and generates insights.

```python
from core.cache_monitoring import CachePerformanceAnalyzer

analyzer = CachePerformanceAnalyzer(metrics_collector)

# Analyze hit rate
hit_rate_report = analyzer.analyze_hit_rate("memory")
print(f"Hit Rate: {hit_rate_report['hit_rate']:.2%}")
print(f"Status: {hit_rate_report['status']}")
print(f"Trend: {hit_rate_report['trend']}")

# Analyze cache size
size_report = analyzer.analyze_cache_size("memory")
print(f"Utilization: {size_report['utilization']:.2%}")
print(f"Entries: {size_report['entries']}/{size_report['max_entries']}")

# Detect performance degradation
degradation = analyzer.detect_performance_degradation("memory")
if degradation:
    print(f"Degradation: {degradation['degradation_percent']:.1f}%")

# Get comprehensive report
report = analyzer.get_comprehensive_report()
```

### CacheMonitor

Automated monitoring with periodic metric collection.

```python
from core.cache_monitoring import CacheMonitor

# Create monitor with custom settings
monitor = CacheMonitor(
    collection_interval_seconds=60,
    enable_auto_cleanup=True,
    cleanup_threshold=0.9
)

# Start monitoring
monitor.start()

# Get report
report = monitor.get_report()

# Get detailed report with historical data
detailed_report = monitor.get_detailed_report(window_minutes=60)

# Stop monitoring
monitor.stop()
```

## API Reference

### Starting and Stopping Monitoring

```python
# Start monitoring
start_cache_monitoring(interval_seconds=60)

# Stop monitoring
stop_cache_monitoring()

# Get monitor instance
monitor = get_cache_monitor()
```

### Getting Reports

```python
# Basic report
report = get_cache_performance_report()

# Detailed report with historical data
detailed_report = get_cache_performance_report(detailed=True)

# Get specific metrics
metrics = get_detailed_metrics("memory", window_minutes=60)
```

### Automatic Cleanup

```python
# Enable automatic cleanup
enable_automatic_cleanup(threshold=0.9)

# Disable automatic cleanup
disable_automatic_cleanup()

# Register cleanup callback
def my_cleanup():
    # Custom cleanup logic
    pass

register_cleanup_callback(my_cleanup)

# Trigger manual cleanup
results = trigger_manual_cleanup(reason="manual")
print(f"Freed {results['space_freed_bytes']} bytes")
```

### Performance Issue Detection

```python
# Detect all performance issues
issues = detect_performance_issues()

# Check degradation
if issues["degradation"]:
    deg = issues["degradation"]
    print(f"Current: {deg['current_hit_rate']:.2%}")
    print(f"Historical: {deg['historical_avg']:.2%}")
    print(f"Degradation: {deg['degradation_percent']:.1f}%")

# Check alerts
for alert in issues["alerts"]:
    print(f"[{alert['severity']}] {alert['message']}")

# Get recommendations
for rec in issues["recommendations"]:
    print(f"Recommendation: {rec}")
```

## Metrics and Thresholds

### Default Alert Thresholds

```python
{
    "hit_rate_low": 0.7,           # Alert if hit rate < 70%
    "miss_rate_high": 0.3,         # Alert if miss rate > 30%
    "size_high": 0.9,              # Alert if cache > 90% full
    "eviction_rate_high": 100,     # Alert if > 100 evictions/min
    "degradation_threshold": 0.15  # Alert if 15% degradation
}
```

### Metric Types

- **hit_rate**: Cache hit rate (0.0 to 1.0)
- **utilization**: Cache capacity utilization (0.0 to 1.0)
- **evictions**: Number of cache evictions
- **expirations**: Number of expired entries
- **performance**: Overall performance score

### Status Levels

- **excellent**: Hit rate >= 90%
- **good**: Hit rate >= 70%
- **fair**: Hit rate >= 50%
- **poor**: Hit rate < 50%
- **critical**: Utilization > 90%

## Advanced Usage

### Custom Cleanup Logic

```python
from core.cache_monitoring import register_cleanup_callback
from core.cache import get_cache

def aggressive_cleanup():
    """Remove all entries older than 1 hour"""
    cache = get_cache()
    cutoff = datetime.now() - timedelta(hours=1)
    
    for key in cache.memory_cache.get_all_keys():
        entry = cache.memory_cache.get_entry(key)
        if entry and entry.created_at < cutoff:
            cache.delete(key)

register_cleanup_callback(aggressive_cleanup)
```

### Performance Monitoring Dashboard

```python
from core.cache_monitoring import get_cache_monitor

def print_dashboard():
    monitor = get_cache_monitor()
    report = monitor.get_detailed_report(window_minutes=60)
    
    print("=" * 60)
    print("Cache Performance Dashboard")
    print("=" * 60)
    
    # Memory layer stats
    memory = report["layers"]["memory"]
    hit_rate = memory["hit_rate"]
    size = memory["size"]
    
    print(f"\nHit Rate: {hit_rate['hit_rate']:.2%} ({hit_rate['status']})")
    print(f"Trend: {hit_rate['trend']}")
    print(f"Hits: {hit_rate['hits']}, Misses: {hit_rate['misses']}")
    
    print(f"\nCache Size: {size['entries']}/{size['max_entries']}")
    print(f"Utilization: {size['utilization']:.2%}")
    print(f"Total Size: {size['total_size_mb']:.2f} MB")
    
    # Alerts
    if report["alerts"]:
        print(f"\nActive Alerts: {len(report['alerts'])}")
        for alert in report["alerts"]:
            print(f"  [{alert['severity']}] {alert['message']}")
    
    # Recommendations
    if report["recommendations"]:
        print(f"\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

# Run dashboard every minute
import time
while True:
    print_dashboard()
    time.sleep(60)
```

### Trend Analysis

```python
from core.cache_monitoring import get_cache_monitor

monitor = get_cache_monitor()

# Analyze trend over different windows
for window in [5, 15, 30, 60]:
    trend = monitor.metrics_collector.calculate_trend(
        "memory",
        "hit_rate",
        window_minutes=window
    )
    print(f"{window}min trend: {trend}")

# Get detailed trend data
detailed = monitor.analyzer.get_detailed_metrics("memory", window_minutes=60)
for metric_type, stats in detailed["metrics"].items():
    print(f"{metric_type}: {stats['trend']}")
    print(f"  Min: {stats['min']:.4f}")
    print(f"  Max: {stats['max']:.4f}")
    print(f"  Avg: {stats['average']:.4f}")
```

## Integration Examples

### With Streamlit

```python
import streamlit as st
from core.cache_monitoring import get_cache_performance_report

# Display cache metrics in Streamlit
st.title("Cache Performance")

report = get_cache_performance_report(detailed=True)
memory = report["layers"]["memory"]

col1, col2, col3 = st.columns(3)

with col1:
    hit_rate = memory["hit_rate"]["hit_rate"]
    st.metric("Hit Rate", f"{hit_rate:.1%}")

with col2:
    utilization = memory["size"]["utilization"]
    st.metric("Utilization", f"{utilization:.1%}")

with col3:
    entries = memory["size"]["entries"]
    st.metric("Entries", entries)

# Show alerts
if report["alerts"]:
    st.warning(f"{len(report['alerts'])} active alerts")
    for alert in report["alerts"]:
        st.error(f"[{alert['severity']}] {alert['message']}")
```

### With Logging

```python
import logging
from core.cache_monitoring import get_cache_monitor

logger = logging.getLogger(__name__)

def log_cache_metrics():
    monitor = get_cache_monitor()
    report = monitor.get_report()
    
    memory = report["layers"]["memory"]
    hit_rate = memory["hit_rate"]["hit_rate"]
    utilization = memory["size"]["utilization"]
    
    logger.info(
        "Cache metrics",
        extra={
            "hit_rate": hit_rate,
            "utilization": utilization,
            "alerts": len(report["alerts"])
        }
    )

# Log metrics periodically
import time
while True:
    log_cache_metrics()
    time.sleep(300)  # Every 5 minutes
```

## Best Practices

### 1. Set Appropriate Collection Intervals

```python
# For production: 60-300 seconds
start_cache_monitoring(interval_seconds=60)

# For development: 10-30 seconds
start_cache_monitoring(interval_seconds=10)
```

### 2. Configure Cleanup Thresholds

```python
# Conservative (more cleanup)
enable_automatic_cleanup(threshold=0.8)

# Aggressive (less cleanup)
enable_automatic_cleanup(threshold=0.95)
```

### 3. Monitor Trends

```python
# Check trends regularly
issues = detect_performance_issues()

if issues["degradation"]:
    # Investigate and take action
    logger.warning("Cache performance degrading", extra=issues["degradation"])
```

### 4. Use Custom Cleanup

```python
# Implement domain-specific cleanup
def cleanup_old_sessions():
    cache = get_cache()
    # Remove old session data
    for key in cache.memory_cache.get_all_keys():
        if key.startswith("user_session:"):
            entry = cache.memory_cache.get_entry(key)
            if entry and entry.created_at < cutoff:
                cache.delete(key)

register_cleanup_callback(cleanup_old_sessions)
```

### 5. Alert on Critical Issues

```python
def check_and_alert():
    issues = detect_performance_issues()
    
    for alert in issues["alerts"]:
        if alert["severity"] == "critical":
            # Send notification (email, Slack, etc.)
            send_alert(alert["message"])
```

## Troubleshooting

### High Miss Rate

```python
# Check hit rate
report = get_cache_performance_report()
hit_rate = report["layers"]["memory"]["hit_rate"]["hit_rate"]

if hit_rate < 0.5:
    # Possible causes:
    # 1. TTL too short
    # 2. Cache size too small
    # 3. Excessive invalidation
    # 4. Poor cache key design
    
    # Get recommendations
    issues = detect_performance_issues()
    for rec in issues["recommendations"]:
        print(rec)
```

### High Eviction Rate

```python
# Check evictions
report = get_cache_performance_report()
evictions = report["layers"]["memory"]["evictions"]["evictions"]

if evictions > 1000:
    # Increase cache size
    # Or implement better eviction strategy
    pass
```

### Performance Degradation

```python
# Detect degradation
monitor = get_cache_monitor()
degradation = monitor.analyzer.detect_performance_degradation("memory")

if degradation:
    print(f"Degradation: {degradation['degradation_percent']:.1f}%")
    print(f"Current: {degradation['current_hit_rate']:.2%}")
    print(f"Historical: {degradation['historical_avg']:.2%}")
    
    # Investigate recent changes
    # Check for increased load
    # Review invalidation patterns
```

## Requirements Satisfied

This implementation satisfies the following requirements from Task 6.3:

✓ **Cache hit rate tracking with detailed metrics**
  - Historical data collection
  - Statistical analysis (min, max, average)
  - Real-time tracking

✓ **Performance analytics with trend analysis**
  - Trend detection (improving, degrading, stable)
  - Performance degradation detection
  - Comprehensive reporting

✓ **Cache size monitoring with automatic cleanup**
  - Utilization tracking
  - Automatic cleanup triggers
  - Custom cleanup callbacks
  - Manual cleanup support

✓ **Performance degradation detection**
  - Threshold-based alerts
  - Historical comparison
  - Alert management
  - Recommendations generation

## Related Documentation

- [Cache System README](./CACHE_README.md)
- [Cache Invalidation README](./CACHE_INVALIDATION_README.md)
- [Cache Warming README](./CACHE_WARMING_README.md)
