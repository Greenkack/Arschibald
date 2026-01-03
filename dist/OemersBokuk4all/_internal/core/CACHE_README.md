# Intelligent Caching System

A comprehensive multi-layer caching system with smart invalidation, performance monitoring, and proactive cache warming.

## Features

### 1. Multi-Layer Caching
- **Memory Cache**: Fast in-memory cache with LRU eviction
- **Streamlit Cache**: Integration with Streamlit's caching decorators
- **Database Cache**: Persistent caching for expensive query results
- **Automatic Fallback**: Seamlessly falls back through cache layers

### 2. Smart Cache Invalidation
- **Tagged Invalidation**: Invalidate related cache entries by tags
- **Dependency Tracking**: Automatically invalidate dependent caches
- **Invalidation Rules**: Define custom rules for automatic invalidation
- **Batch Invalidation**: Optimize performance with batched invalidation

### 3. Performance Monitoring
- **Hit Rate Tracking**: Monitor cache effectiveness
- **Trend Analysis**: Detect performance degradation
- **Automatic Alerts**: Get notified of performance issues
- **Comprehensive Reports**: Detailed performance analytics

### 4. Proactive Cache Warming
- **Critical Data Warming**: Pre-populate important caches
- **Usage Pattern Learning**: Warm based on access patterns
- **User-Specific Warming**: Pre-load user data
- **Background Warming**: Automatic periodic warming

## Quick Start

### Basic Usage

```python
from core.cache import get_cache, get_or_compute, CacheKeys

# Simple caching
cache = get_cache()
cache.set("my_key", "my_value", ttl=3600)
value = cache.get("my_key")

# Compute and cache pattern
def expensive_function():
    # ... expensive computation ...
    return result

key = CacheKeys.computed("my_function", arg1, arg2)
result = get_or_compute(key, expensive_function, ttl=300)
```

### Tagged Invalidation

```python
from core.cache import get_cache, invalidate_cache

cache = get_cache()

# Set with tags
cache.set("user_data", data, tags={"user", "user:123"})
cache.set("user_prefs", prefs, tags={"user", "user:123"})

# Invalidate all user:123 caches
invalidate_cache(tags={"user:123"})
```

### Cache Dependencies

```python
from core.cache_invalidation import add_cache_dependency, invalidate_with_dependencies

# Define dependency
add_cache_dependency("derived_key", {"source_key1", "source_key2"})

# Invalidate source and all dependents
invalidate_with_dependencies("source_key1")
```

### Cache Warming

```python
from core.cache_warming import WarmingTask, register_warming_task, start_cache_warming

# Define warming task
task = WarmingTask(
    task_id="critical_data",
    name="Critical Configuration",
    cache_key="app_config",
    compute_fn=load_config,
    priority=100,
    ttl=3600
)

register_warming_task(task)

# Start background warming
start_cache_warming(interval_minutes=60)
```

### Performance Monitoring

```python
from core.cache_monitoring import start_cache_monitoring, get_cache_performance_report

# Start monitoring
start_cache_monitoring(interval_seconds=60)

# Get performance report
report = get_cache_performance_report()
print(f"Hit Rate: {report['layers']['memory']['hit_rate']['hit_rate']:.1%}")
```

## Architecture

### Cache Layers

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (get_or_compute, invalidate_cache)    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Multi-Layer Cache Manager         │
└─────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Memory     │ │  Streamlit   │ │   Database   │
│   Cache      │ │   Cache      │ │    Cache     │
│  (LRU+TTL)   │ │ (Decorators) │ │ (Persistent) │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Invalidation Flow

```
Database Write
      │
      ▼
Invalidation Engine
      │
      ├─→ Check Rules
      │   (trigger_tags → invalidate_tags)
      │
      ├─→ Check Dependencies
      │   (source → derived keys)
      │
      └─→ Batch Invalidation
          (optimize performance)
```

## API Reference

### Core Functions

#### `get_cache() -> MultiLayerCache`
Get the global cache instance.

#### `get_or_compute(key, fn, ttl=None, tags=None, force_refresh=False) -> Any`
Get value from cache or compute and cache it.

**Parameters:**
- `key`: Cache key
- `fn`: Function to compute value if not cached
- `ttl`: Time to live in seconds
- `tags`: Tags for invalidation
- `force_refresh`: Bypass cache and recompute

#### `invalidate_cache(tags=None, keys=None) -> int`
Invalidate cache entries by tags or keys.

**Returns:** Number of entries invalidated

### CacheKeys Class

Provides namespaced cache key generation:

```python
CacheKeys.user_session(user_id)
CacheKeys.form_data(form_id, user_id)
CacheKeys.computed(function_name, *args, **kwargs)
CacheKeys.query_result(query, params)
CacheKeys.custom(namespace, *parts)
```

### Invalidation Functions

#### `invalidate_by_write(resource_type, resource_id=None, context=None) -> int`
Invalidate cache after database write.

#### `add_cache_dependency(key, depends_on) -> None`
Add cache dependency relationship.

#### `invalidate_with_dependencies(key, recursive=True) -> int`
Invalidate key and all its dependents.

### Monitoring Functions

#### `start_cache_monitoring(interval_seconds=60) -> None`
Start automatic cache monitoring.

#### `get_cache_performance_report() -> dict`
Get comprehensive performance report.

### Warming Functions

#### `warm_cache(key, compute_fn, ttl=None, tags=None) -> bool`
Warm specific cache key.

#### `warm_user_data(user_id) -> dict`
Warm user-specific cache data.

#### `start_cache_warming(interval_minutes=60) -> None`
Start background cache warming.

## Configuration

Cache behavior is configured via `AppConfig`:

```python
from core.config import get_config

config = get_config()

# Cache settings
config.cache.default_ttl = 3600  # Default TTL in seconds
config.cache.max_entries = 1000  # Max memory cache entries
config.cache.redis_url = "redis://localhost:6379"  # Optional Redis

# Performance settings
config.performance.cache_warming_enabled = True
config.performance.response_time_target_ms = 50
```

## Best Practices

### 1. Use Namespaced Keys

Always use `CacheKeys` for consistent key naming:

```python
# Good
key = CacheKeys.user_session(user_id)

# Avoid
key = f"user_session_{user_id}"
```

### 2. Tag Your Caches

Use tags for efficient invalidation:

```python
cache.set(
    key,
    value,
    tags={"user", f"user:{user_id}", "session"}
)
```

### 3. Set Appropriate TTLs

- Short TTL (60-300s): Frequently changing data
- Medium TTL (300-3600s): Moderately stable data
- Long TTL (3600-86400s): Rarely changing data

### 4. Invalidate After Writes

Always invalidate related caches after database writes:

```python
def update_user(user_id, data):
    # Update database
    repo.update(user_id, data)
    
    # Invalidate caches
    invalidate_by_write("user", user_id)
```

### 5. Monitor Performance

Enable monitoring in production:

```python
from core.cache_monitoring import start_cache_monitoring

start_cache_monitoring(interval_seconds=60)
```

### 6. Warm Critical Data

Pre-populate important caches:

```python
from core.cache_warming import register_warming_task, WarmingTask

task = WarmingTask(
    task_id="app_config",
    name="Application Config",
    cache_key="config",
    compute_fn=load_config,
    priority=100
)

register_warming_task(task)
```

## Performance Considerations

### Memory Usage

- Memory cache uses LRU eviction when full
- Monitor cache size with `get_cache_stats()`
- Adjust `max_entries` based on available memory

### Hit Rate Optimization

Target hit rates:
- **Excellent**: > 90%
- **Good**: 70-90%
- **Fair**: 50-70%
- **Poor**: < 50%

If hit rate is low:
1. Increase TTL
2. Increase max_entries
3. Review invalidation patterns
4. Enable cache warming

### Invalidation Performance

- Use batch invalidation for multiple keys
- Avoid invalidating too frequently
- Use specific tags instead of broad invalidation

## Troubleshooting

### Low Hit Rate

**Symptoms:** Cache hit rate < 70%

**Solutions:**
1. Check if TTL is too short
2. Verify invalidation isn't too aggressive
3. Enable cache warming for hot keys
4. Increase max_entries

### High Memory Usage

**Symptoms:** Cache using too much memory

**Solutions:**
1. Reduce max_entries
2. Reduce TTL for large objects
3. Enable more aggressive eviction
4. Use database cache for large data

### Stale Data

**Symptoms:** Cached data is outdated

**Solutions:**
1. Reduce TTL
2. Add proper invalidation after writes
3. Use tagged invalidation
4. Implement cache dependencies

## Examples

See `example_cache_usage.py` for comprehensive examples including:
- Basic caching operations
- Tagged invalidation
- Cache dependencies
- Custom invalidation rules
- Cache warming
- Performance monitoring
- Real-world scenarios

## Testing

Run the test suite:

```bash
pytest core/test_cache.py -v
```

Tests cover:
- Cache operations (get, set, delete)
- LRU eviction
- TTL expiration
- Tagged invalidation
- Multi-layer coordination
- Dependency tracking
- Performance monitoring
- Cache warming

## Integration with Streamlit

The caching system integrates seamlessly with Streamlit:

```python
import streamlit as st
from core.cache import get_cache, get_or_compute

# Use with Streamlit
@st.cache_data(ttl=3600)
def load_data():
    return expensive_query()

# Or use our system
def load_data_cached():
    return get_or_compute(
        "data_key",
        expensive_query,
        ttl=3600
    )
```

## Requirements

- Python 3.10+
- Optional: Redis (for distributed caching)
- Optional: Streamlit (for Streamlit integration)

## Related Components

- **Session Management** (`session.py`): Uses caching for session persistence
- **Form Manager** (`form_manager.py`): Caches form states
- **Database** (`database.py`): Database-level caching
- **Configuration** (`config.py`): Cache configuration

## Support

For issues or questions:
1. Check the examples in `example_cache_usage.py`
2. Review the test suite in `test_cache.py`
3. Check performance reports with `get_cache_performance_report()`
4. Enable debug logging for detailed information
