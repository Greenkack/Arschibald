# Price Matrix Performance - Quick Reference

Fast reference for price matrix performance optimization.

## Quick Start

```python
from solar-calculator-pro.backend.services.price_matrix_performance_service import (
    get_performance_service
)

# Get service
service = get_performance_service()

# Warm cache
service.warm_cache(matrix_data)

# Optimized lookup
price = service.optimize_lookup(20, '15kWh')

# Get stats
stats = service.get_performance_stats()
print(f"Hit rate: {stats['cache_hit_rate']}%")
```

## Common Operations

### Cache Management

```python
# Warm cache
service.warm_cache(matrix_data)

# Invalidate cache
service.invalidate_cache()  # All
service.invalidate_cache('matrix1')  # Specific

# Get cache stats
stats = service.cache.get_stats()
```

### Index Operations

```python
# Build index
service.index.build_index(matrix_data)

# Fast lookup
entry = service.index.lookup(20, '15kWh')

# Range query
entries = service.index.find_by_module_count_range(15, 25)

# Get stats
stats = service.index.get_stats()
```

### Precomputation

```python
# Precompute common queries
service.precompute_common_queries(
    matrix_data,
    common_module_counts=[20, 25, 30],
    common_storage_models=['10kWh', '15kWh']
)

# Get precomputed
result = service.precomputer.get_precomputed('query_key')
```

### Performance Monitoring

```python
# Get comprehensive stats
stats = service.get_performance_stats()

# Get recommendations
recommendations = service.get_optimization_recommendations()

# Track operation
@track_performance('my_operation')
def my_function():
    pass
```

## API Endpoints

### Get Stats
```http
GET /api/v1/price-matrix-performance/stats
```

### Get Recommendations
```http
GET /api/v1/price-matrix-performance/recommendations
```

### Warm Cache
```http
POST /api/v1/price-matrix-performance/cache/warm
{
  "matrix_data": { ... }
}
```

### Invalidate Cache
```http
POST /api/v1/price-matrix-performance/cache/invalidate?matrix_id=matrix1
```

### Precompute
```http
POST /api/v1/price-matrix-performance/precompute
{
  "matrix_data": { ... },
  "common_module_counts": [20, 25, 30],
  "common_storage_models": ["10kWh", "15kWh"]
}
```

### Optimized Lookup
```http
POST /api/v1/price-matrix-performance/lookup
{
  "module_count": 20,
  "storage_model": "15kWh"
}
```

### Run Benchmark
```http
POST /api/v1/price-matrix-performance/benchmark?module_counts=20,25&storage_models=10kWh,15kWh&iterations=100
```

## Performance Targets

| Metric | Target | Excellent |
|--------|--------|-----------|
| Cache Hit Rate | >70% | >90% |
| Avg Lookup Time | <10ms | <1ms |
| Memory Usage | <100MB | <50MB |

## Troubleshooting

### Low Hit Rate (<50%)
- Increase cache size
- Precompute common queries
- Warm cache on startup

### Slow Lookups (>10ms)
- Build indexes
- Warm cache
- Precompute queries

### High Memory (>100MB)
- Reduce cache size
- Use lazy loading
- Reduce TTL

## Best Practices

1. **Warm cache on startup**
   ```python
   service.warm_cache(matrix_data)
   ```

2. **Build indexes early**
   ```python
   service.index.build_index(matrix_data)
   ```

3. **Precompute common queries**
   ```python
   service.precompute_common_queries(...)
   ```

4. **Monitor regularly**
   ```python
   stats = service.get_performance_stats()
   ```

5. **Invalidate on updates**
   ```python
   service.invalidate_cache(matrix_id)
   ```

## Configuration

### Cache Sizes
```python
cache = TieredCache(
    l1_size=100,    # Fast cache
    l2_size=1000,   # Larger cache
    l1_ttl=300,     # 5 minutes
    l2_ttl=3600     # 1 hour
)
```

### Index Settings
```python
index = MatrixIndex()
index.build_index(matrix_data)
```

### Lazy Loading
```python
loader = LazyMatrixLoader(chunk_size=1000)
```

### Precomputation
```python
precomputer = QueryPrecomputer()
precomputer.threshold = 10  # Precompute after 10 hits
```

## Performance Metrics

### Cache Statistics
- `size`: Current entries
- `hits`: Cache hits
- `misses`: Cache misses
- `hit_rate`: Hit percentage
- `evictions`: Evicted entries

### Index Statistics
- `total_entries`: Total indexed entries
- `unique_module_counts`: Unique module counts
- `unique_storage_models`: Unique storage models

### Operation Metrics
- `total_operations`: Total operations
- `avg_duration_ms`: Average duration
- `cache_hit_rate`: Overall hit rate

## Examples

### Complete Optimization Workflow

```python
# 1. Get service
service = get_performance_service()

# 2. Build index
service.index.build_index(matrix_data)

# 3. Precompute common queries
service.precompute_common_queries(
    matrix_data,
    [20, 25, 30],
    ['10kWh', '15kWh']
)

# 4. Warm cache
service.warm_cache(matrix_data)

# 5. Perform lookups
price = service.optimize_lookup(20, '15kWh')

# 6. Monitor performance
stats = service.get_performance_stats()
recommendations = service.get_optimization_recommendations()
```

### Benchmark Performance

```python
import time

# Without optimization
start = time.time()
for _ in range(1000):
    price = calculate_price_from_matrix(20, '15kWh')
duration_without = time.time() - start

# With optimization
service.warm_cache(matrix_data)
start = time.time()
for _ in range(1000):
    price = service.optimize_lookup(20, '15kWh')
duration_with = time.time() - start

improvement = duration_without / duration_with
print(f"Performance improvement: {improvement}x")
```

## See Also

- [Complete Guide](./PRICE_MATRIX_PERFORMANCE_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Price Matrix Guide](./PRICE_MATRIX_GUIDE.md)
