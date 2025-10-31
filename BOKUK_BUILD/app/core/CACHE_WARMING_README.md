# Cache Warming System

The Cache Warming System provides proactive cache population for critical data, user-specific preloading, and intelligent warming based on usage patterns.

## Features

### 1. Proactive Cache Population
- **Critical Data Warming**: Automatically warm high-priority cache keys
- **Scheduled Warming**: Configure warming schedules for different data types
- **Priority-Based Execution**: Higher priority tasks are warmed first

### 2. Usage Pattern-Based Warming
- **Access Tracking**: Monitor cache key access patterns
- **Frequency Analysis**: Identify frequently accessed keys
- **Predictive Warming**: Warm cache before predicted access times
- **Adaptive Scheduling**: Adjust warming intervals based on usage

### 3. User-Specific Preloading
- **Session Preloading**: Warm user session data on login
- **Form Data Preloading**: Load user's recent forms
- **Navigation Preloading**: Prepare navigation history
- **Intelligent Caching**: Skip recently warmed data to save resources

### 4. Performance Optimization
- **Performance Tracking**: Monitor warming duration and efficiency
- **Schedule Optimization**: Automatically adjust warming schedules
- **Resource Management**: Prevent excessive warming operations
- **Efficiency Scoring**: Track warming system effectiveness

## Core Components

### WarmingTask
Defines a cache warming task with scheduling and priority:

```python
from core.cache_warming import WarmingTask

task = WarmingTask(
    task_id="user_prefs",
    name="User Preferences",
    cache_key="prefs:default",
    compute_fn=load_preferences,
    ttl=3600,
    priority=50,  # Higher = more important
    tags={"user", "preferences"}
)
```

### CacheWarmingEngine
Main engine for managing and executing warming tasks:

```python
from core.cache_warming import get_warming_engine

engine = get_warming_engine()

# Register tasks
engine.register_task(task, is_critical=True)

# Warm critical data
results = engine.warm_critical_data()

# Warm user data
user_results = engine.warm_user_data("user_123")

# Get statistics
stats = engine.get_stats()
```

### UsagePatternTracker
Tracks cache access patterns for intelligent warming:

```python
# Access patterns are tracked automatically
# Get hot keys
hot_keys = tracker.get_hot_keys(top_n=10)

# Get access frequency
frequency = tracker.get_access_frequency("key", window_minutes=60)

# Predict next access
next_access = tracker.predict_next_access("key")
```

## Usage Examples

### Basic Cache Warming

```python
from core.cache_warming import warm_cache

def load_expensive_data():
    # Expensive computation
    return {"data": "result"}

# Warm a specific key
success = warm_cache(
    key="expensive_data",
    compute_fn=load_expensive_data,
    ttl=3600,
    tags={"expensive", "critical"}
)
```

### Register Warming Tasks

```python
from core.cache_warming import register_warming_task, register_critical_task

# Regular task
task = WarmingTask(
    task_id="analytics",
    name="Analytics Data",
    cache_key="analytics:dashboard",
    compute_fn=load_analytics,
    priority=30
)
register_warming_task(task)

# Critical task (high priority)
critical_task = WarmingTask(
    task_id="catalog",
    name="Product Catalog",
    cache_key="catalog:products",
    compute_fn=load_catalog,
    priority=100
)
register_critical_task(critical_task)
```

### Warm Critical Data

```python
from core.cache_warming import warm_critical_data

# Warm all critical data
results = warm_critical_data()

print(f"Succeeded: {results['succeeded']}")
print(f"Failed: {results['failed']}")
print(f"Duration: {results['total_duration_ms']}ms")
```

### Warm User-Specific Data

```python
from core.cache_warming import warm_user_data_optimized

# Warm user data with optimization
results = warm_user_data_optimized(
    user_id="user_123",
    force=False,  # Skip if recently warmed
    preload_forms=True  # Also preload recent forms
)

if not results.get("skipped"):
    print(f"Keys warmed: {len(results['keys_warmed'])}")
    print(f"Duration: {results['duration_ms']}ms")
```

### Background Warming

```python
from core.cache_warming import (
    start_cache_warming,
    stop_cache_warming,
    get_warming_stats
)

# Start background warming
start_cache_warming(
    interval_minutes=60,  # Warm every hour
    enable_pattern_warming=True,  # Use usage patterns
    enable_critical_warming=True  # Warm critical data
)

# Get statistics
stats = get_warming_stats()
print(f"Active tasks: {stats['tasks']}")
print(f"Running: {stats['running']}")

# Stop when done
stop_cache_warming()
```

### Performance Monitoring

```python
from core.cache_warming import get_warming_performance

# Get performance statistics
perf = get_warming_performance()

print(f"Total warmings: {perf['total_warmings']}")
print(f"Average duration: {perf['avg_duration_ms']:.2f}ms")
print(f"Fastest: {perf['fastest_ms']:.2f}ms")
print(f"Slowest: {perf['slowest_ms']:.2f}ms")
print(f"Efficiency score: {perf['efficiency_score']:.1f}%")
```

### Schedule Optimization

```python
from core.cache_warming import optimize_warming_schedules

# Optimize schedules based on usage patterns
results = optimize_warming_schedules()

print(f"Tasks optimized: {results['tasks_optimized']}")

for adjustment in results['schedules_adjusted']:
    print(f"{adjustment['task_id']}:")
    print(f"  Frequency: {adjustment['frequency']} accesses/min")
    print(f"  New interval: {adjustment['interval_minutes']} minutes")
```

## Configuration

### Task Priority Levels
- **100+**: Critical system data (always warmed first)
- **50-99**: Important user data
- **10-49**: Nice-to-have data
- **<10**: Low priority background data

### Warming Intervals
The system automatically adjusts intervals based on access frequency:
- **High frequency (>1 access/min)**: 15 minutes
- **Medium frequency (>0.5 access/min)**: 30 minutes
- **Normal frequency (>0.1 access/min)**: 60 minutes
- **Low frequency (<0.1 access/min)**: 120 minutes

### Performance Targets
- **Warming duration**: <100ms per key (target)
- **Efficiency score**: >80% (good), >90% (excellent)
- **User preload**: Skip if warmed within 5 minutes

## Best Practices

### 1. Register Critical Tasks Early
```python
# Register critical tasks during application initialization
def init_app():
    register_critical_task(catalog_task)
    register_critical_task(user_prefs_task)
    # ... other critical tasks
```

### 2. Use Appropriate Priorities
```python
# Critical system data
priority=100

# Important user data
priority=50

# Background data
priority=10
```

### 3. Set Reasonable TTLs
```python
# Frequently changing data
ttl=300  # 5 minutes

# Stable data
ttl=3600  # 1 hour

# Rarely changing data
ttl=86400  # 24 hours
```

### 4. Tag Your Cache Keys
```python
tags={"user", "critical", "session"}  # For targeted invalidation
```

### 5. Monitor Performance
```python
# Regularly check warming performance
perf = get_warming_performance()
if perf['avg_duration_ms'] > 100:
    logger.warning("Warming performance degraded")
```

### 6. Optimize Schedules Periodically
```python
# Run optimization daily or weekly
optimize_warming_schedules()
```

## Integration with Other Systems

### With Session Management
```python
from core.session import bootstrap_session
from core.cache_warming import warm_user_data_optimized

def user_login(user_id: str):
    # Bootstrap session
    session = bootstrap_session(user_id)
    
    # Warm user data
    warm_user_data_optimized(user_id, preload_forms=True)
    
    return session
```

### With Form Manager
```python
from core.form_manager import FormManager
from core.cache_warming import warm_cache

def save_form(form_id: str, data: dict):
    # Save form
    manager = FormManager()
    manager.save_form(form_id, data)
    
    # Warm the cache
    warm_cache(
        key=f"form:{form_id}",
        compute_fn=lambda: manager.load_form(form_id),
        ttl=3600
    )
```

### With Cache Invalidation
```python
from core.cache_invalidation import invalidate_by_tags
from core.cache_warming import warm_critical_data

def update_product_catalog():
    # Update catalog
    update_catalog_in_db()
    
    # Invalidate old cache
    invalidate_by_tags({"catalog"})
    
    # Warm new data
    warm_critical_data()
```

## Performance Considerations

### Memory Usage
- Warming tasks are lightweight (metadata only)
- Usage tracker maintains limited history (default: 1000 entries)
- User preload cache tracks only timestamps

### CPU Usage
- Background warming runs in separate thread
- Warming operations are throttled by interval
- Pattern analysis is optimized for speed

### Network/Database
- Warming may trigger database queries
- Use appropriate TTLs to reduce load
- Consider off-peak warming for expensive operations

## Troubleshooting

### Warming Takes Too Long
```python
# Check performance stats
perf = get_warming_performance()
print(f"Avg duration: {perf['avg_duration_ms']}ms")

# Identify slow tasks
stats = get_warming_stats()
for task in stats['task_details']:
    if task['avg_duration_ms'] > 100:
        print(f"Slow task: {task['name']} ({task['avg_duration_ms']}ms)")
```

### Tasks Not Running
```python
# Check if background warming is running
stats = get_warming_stats()
if not stats['running']:
    start_cache_warming()

# Check task schedules
for task in stats['task_details']:
    print(f"{task['name']}: next_run={task['next_run']}")
```

### High Memory Usage
```python
# Clear usage history
from core.cache_warming import get_warming_engine
engine = get_warming_engine()
engine._usage_tracker.clear()

# Reduce history size
tracker = UsagePatternTracker(history_size=500)
```

## API Reference

See `example_cache_warming_usage.py` for complete examples.

### Main Functions
- `warm_cache(key, compute_fn, ttl, tags)` - Warm specific key
- `warm_critical_data()` - Warm all critical data
- `warm_user_data_optimized(user_id, force, preload_forms)` - Warm user data
- `start_cache_warming(interval_minutes, ...)` - Start background warming
- `stop_cache_warming()` - Stop background warming
- `get_warming_stats()` - Get warming statistics
- `get_warming_performance()` - Get performance metrics
- `optimize_warming_schedules()` - Optimize schedules

### Classes
- `WarmingTask` - Cache warming task definition
- `CacheWarmingEngine` - Main warming engine
- `UsagePatternTracker` - Usage pattern tracking

## Requirements Satisfied

This implementation satisfies the following requirements:

- **4.1**: Proactive cache population for critical data
- **4.6**: Cache performance optimization with <10ms cache hits

The system ensures fast cache access by proactively warming frequently accessed data and optimizing warming schedules based on usage patterns.
