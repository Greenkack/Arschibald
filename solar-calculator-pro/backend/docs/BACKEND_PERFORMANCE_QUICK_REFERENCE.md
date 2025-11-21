# Backend Performance Quick Reference

Quick reference for backend performance optimization features.

## Database Optimization

### Query Optimization
```python
from core.database_optimization import QueryOptimizer

optimizer = QueryOptimizer(session)
query = optimizer.optimize_query(query)
query = optimizer.add_eager_loading(query, User.projects)
query = optimizer.add_pagination(query, page=1, page_size=50)
```

### Index Management
```python
from core.database_optimization import IndexManager, create_common_indexes

index_manager = IndexManager(engine)
index_manager.create_index('users', ['email'], unique=True)
create_common_indexes(engine)  # Create all common indexes
```

### Connection Pooling
```python
from core.database_optimization import ConnectionPoolManager

pool_config = ConnectionPoolManager.get_pool_config(
    pool_size=10,
    max_overflow=20
)
engine = create_engine('sqlite:///db.db', **pool_config)
```

## Caching

### Initialize Cache
```python
from core.caching import init_cache

# In-memory (development)
init_cache(use_redis=False)

# Redis (production)
init_cache(
    use_redis=True,
    redis_host='localhost',
    redis_port=6379
)
```

### Cache Decorator
```python
from core.caching import cache

@cache(expire=3600, key_prefix='products')
def get_products():
    return db.query(Product).all()
```

### Manual Caching
```python
from core.caching import get_cache_manager

cache_manager = get_cache_manager()
key = cache_manager.cache_key(param1='value1')
result = cache_manager.backend.get(key)
if result is None:
    result = expensive_operation()
    cache_manager.backend.set(key, result, expire=3600)
```

## Async Operations

### Background Tasks
```python
from core.async_operations import get_task_manager, background_task

# Using task manager
task_manager = get_task_manager()
task = task_manager.create_task(long_function, arg1, arg2)

# Using decorator
@background_task(name="Process data")
def process_data(data):
    return results

task = process_data(large_dataset)
```

### Check Task Status
```python
task = task_manager.get_task(task_id)
print(f"Status: {task.status}, Progress: {task.progress}%")
```

### Progress Tracking
```python
from core.async_operations import ProgressTracker

tracker = ProgressTracker(total=100, task=task)
for item in items:
    process(item)
    tracker.update()
tracker.complete()
```

## Performance Monitoring

### Initialize Monitoring
```python
from core.performance_monitoring import init_performance_monitoring

init_performance_monitoring(slow_threshold=1.0)
```

### Monitor Functions
```python
from core.performance_monitoring import monitor_performance

@monitor_performance(name='calculation')
def calculate():
    return result
```

### Monitor Endpoints
```python
from core.performance_monitoring import monitor_endpoint

@monitor_endpoint('/api/v1/calculate')
async def calculate_endpoint():
    return response
```

### Get Metrics
```python
from core.performance_monitoring import get_performance_monitor

monitor = get_performance_monitor()

# Endpoint stats
stats = monitor.get_endpoint_stats('/api/v1/calculate')

# System metrics
system = monitor.get_system_metrics()

# Complete summary
summary = monitor.get_metrics_summary()
```

## FastAPI Integration

### Startup Configuration
```python
@app.on_event("startup")
async def startup():
    init_cache(use_redis=True)
    init_performance_monitoring()
    create_common_indexes(engine)
```

### Performance Middleware
```python
@app.middleware("http")
async def perf_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    monitor = get_performance_monitor()
    monitor.record_request_time(request.url.path, duration)
    response.headers["X-Process-Time"] = f"{duration:.3f}"
    
    return response
```

### API Endpoints
```python
# Cached endpoint
@router.get("/products")
@cache(expire=3600)
async def get_products():
    return products

# Background task endpoint
@router.post("/process")
async def start_processing():
    task = task_manager.create_task(process_data, data)
    return {"task_id": task.id}

# Metrics endpoint
@router.get("/metrics")
async def metrics():
    return get_performance_monitor().get_metrics_summary()
```

## Common Patterns

### Expensive Calculation with Caching
```python
@cache(expire=1800, key_prefix='solar')
def calculate_solar_production(location, modules):
    # Expensive calculation
    return result
```

### Long-Running Task with Progress
```python
@background_task(name="Generate report")
def generate_report(project_id, task):
    tracker = ProgressTracker(total=100, task=task)
    
    # Step 1
    fetch_data()
    tracker.update(20)
    
    # Step 2
    process_data()
    tracker.update(50)
    
    # Step 3
    generate_pdf()
    tracker.update(30)
    
    tracker.complete()
    return pdf_bytes
```

### Optimized Database Query
```python
@monitor_performance(name='get_projects')
def get_projects(user_id, page=1):
    optimizer = QueryOptimizer(session)
    
    query = session.query(Project).filter(Project.user_id == user_id)
    query = optimizer.add_eager_loading(query, Project.calculations)
    query = optimizer.add_pagination(query, page=page, page_size=50)
    
    return query.all()
```

## Performance Targets

- **Simple queries**: < 100ms
- **API responses**: < 200ms (cached), < 1s (uncached)
- **Cache hit rate**: > 80%
- **Slow query threshold**: 1 second
- **Background tasks**: Non-blocking, async

## Monitoring Checklist

- [ ] All endpoints monitored
- [ ] Slow queries logged
- [ ] Cache hit rate tracked
- [ ] System resources monitored
- [ ] Indexes created on foreign keys
- [ ] Connection pool configured
- [ ] Background tasks for long operations
- [ ] Performance metrics exposed via API

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow queries | Add indexes, optimize query, enable caching |
| High memory | Clear cache, check connection pool, review tasks |
| Cache misses | Verify TTL, check key generation, review eviction |
| Pool exhaustion | Increase pool size, check for leaks |
| High CPU | Review query patterns, optimize calculations |

## Configuration Examples

### Development
```python
# In-memory cache, small pool
init_cache(use_redis=False)
pool_config = ConnectionPoolManager.get_pool_config(pool_size=5)
```

### Production
```python
# Redis cache, larger pool
init_cache(use_redis=True, redis_host='redis-server')
pool_config = ConnectionPoolManager.get_pool_config(
    pool_size=20,
    max_overflow=40
)
```

## API Endpoints for Monitoring

```
GET /api/v1/metrics              # Performance metrics
GET /api/v1/metrics/endpoints    # Endpoint statistics
GET /api/v1/metrics/system       # System resources
GET /api/v1/tasks                # Active tasks
GET /api/v1/tasks/{id}           # Task status
GET /api/v1/cache/stats          # Cache statistics
POST /api/v1/cache/clear         # Clear cache
```
