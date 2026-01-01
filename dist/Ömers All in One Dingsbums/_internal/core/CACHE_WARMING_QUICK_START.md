# Cache Warming System - Quick Start Guide

## What is Cache Warming?

Cache warming proactively populates the cache with frequently accessed data before users request it, ensuring fast response times (<10ms) and optimal performance.

## Quick Setup (3 Steps)

### 1. Register Warming Tasks

```python
from core.cache_warming import register_critical_task, WarmingTask

# Define your data loading function
def load_product_catalog():
    # Your expensive data loading logic
    return fetch_products_from_db()

# Create and register a warming task
task = WarmingTask(
    task_id="product_catalog",
    name="Product Catalog",
    cache_key="catalog:products",
    compute_fn=load_product_catalog,
    ttl=3600,  # Cache for 1 hour
    priority=100  # High priority
)

register_critical_task(task)  # Mark as critical for priority warming
```

### 2. Start Background Warming

```python
from core.cache_warming import start_cache_warming

# Start automatic warming every hour
start_cache_warming(
    interval_minutes=60,
    enable_pattern_warming=True,  # Warm based on usage patterns
    enable_critical_warming=True  # Warm critical data
)
```

### 3. Warm User Data on Login

```python
from core.cache_warming import warm_user_data_optimized

def user_login(user_id: str):
    # Warm user-specific data
    warm_user_data_optimized(
        user_id=user_id,
        preload_forms=True  # Also preload recent forms
    )
```

## Common Use Cases

### Warm Specific Data Immediately

```python
from core.cache_warming import warm_cache

success = warm_cache(
    key="expensive_data",
    compute_fn=load_expensive_data,
    ttl=3600,
    tags={"critical"}
)
```

### Monitor Performance

```python
from core.cache_warming import get_warming_performance

perf = get_warming_performance()
print(f"Efficiency: {perf['efficiency_score']:.1f}%")
print(f"Average duration: {perf['avg_duration_ms']:.2f}ms")
```

### Optimize Schedules

```python
from core.cache_warming import optimize_warming_schedules

# Run this periodically (e.g., daily)
results = optimize_warming_schedules()
print(f"Optimized {results['tasks_optimized']} task schedules")
```

## Key Features

- ✅ **Proactive Warming**: Populate cache before users request data
- ✅ **Priority-Based**: Critical data warmed first
- ✅ **Usage Patterns**: Automatically adjust based on access frequency
- ✅ **User Preloading**: Warm user-specific data on login
- ✅ **Performance Tracking**: Monitor warming efficiency
- ✅ **Background Processing**: Automatic warming in background thread

## Performance Targets

- **Cache Hit**: <10ms (after warming)
- **Warming Duration**: <100ms per key (target)
- **Efficiency Score**: >80% (good), >90% (excellent)

## Best Practices

1. **Register critical tasks early** during app initialization
2. **Use appropriate priorities**: 100+ for critical, 50+ for important
3. **Set reasonable TTLs**: Balance freshness vs. performance
4. **Monitor performance** regularly with `get_warming_performance()`
5. **Optimize schedules** periodically with `optimize_warming_schedules()`

## Complete Example

```python
from core.cache_warming import (
    WarmingTask,
    register_critical_task,
    start_cache_warming,
    warm_user_data_optimized,
    get_warming_stats
)

# 1. Register tasks during app initialization
def init_cache_warming():
    # Critical system data
    catalog_task = WarmingTask(
        task_id="catalog",
        name="Product Catalog",
        cache_key="catalog:products",
        compute_fn=load_catalog,
        priority=100
    )
    register_critical_task(catalog_task)
    
    # Start background warming
    start_cache_warming(interval_minutes=60)

# 2. Warm user data on login
def handle_user_login(user_id: str):
    warm_user_data_optimized(user_id, preload_forms=True)

# 3. Monitor performance
def check_warming_health():
    stats = get_warming_stats()
    print(f"Active tasks: {stats['tasks']}")
    print(f"Critical keys: {stats['critical_keys']}")
    print(f"Running: {stats['running']}")
```

## Need More Details?

- See `CACHE_WARMING_README.md` for complete documentation
- See `example_cache_warming_usage.py` for detailed examples
- Run `verify_cache_warming.py` to test the system

## Troubleshooting

**Warming too slow?**
```python
perf = get_warming_performance()
if perf['avg_duration_ms'] > 100:
    # Check slow tasks
    stats = get_warming_stats()
    for task in stats['task_details']:
        if task['avg_duration_ms'] > 100:
            print(f"Slow: {task['name']}")
```

**Tasks not running?**
```python
stats = get_warming_stats()
if not stats['running']:
    start_cache_warming()
```

## Summary

The Cache Warming System ensures your application responds instantly by proactively populating the cache with frequently accessed data. Set it up once, and it automatically optimizes based on usage patterns.

**Result**: <10ms cache hits, happy users! 🚀
