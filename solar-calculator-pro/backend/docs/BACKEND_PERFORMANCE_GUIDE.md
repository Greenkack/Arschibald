# Backend Performance Optimization Guide

This guide covers the backend performance optimization features implemented in Task 68.

## Overview

The backend performance optimization system provides:

1. **Database Query Optimization** - Optimize queries, manage indexes, and monitor performance
2. **Response Caching with Redis** - Cache API responses and expensive calculations
3. **Connection Pooling** - Efficient database connection management
4. **Async Operations** - Background tasks and async database operations
5. **Performance Monitoring** - Track and analyze application performance

## Components

### 1. Database Optimization (`core/database_optimization.py`)

#### Query Optimizer

Optimize database queries for better performance:

```python
from core.database_optimization import QueryOptimizer

# Initialize optimizer
optimizer = QueryOptimizer(session)

# Optimize a query
query = session.query(User)
optimized_query = optimizer.optimize_query(query)

# Add eager loading to avoid N+1 queries
query = optimizer.add_eager_loading(query, User.projects, User.settings)

# Add pagination
query = optimizer.add_pagination(query, page=1, page_size=50)

# Track query performance
@optimizer.track_query_performance("get_users")
def get_users():
    return session.query(User).all()

# Get performance statistics
stats = optimizer.get_query_stats()
```

#### Index Manager

Manage database indexes:

```python
from core.database_optimization import IndexManager

# Initialize manager
index_manager = IndexManager(engine)

# Create an index
index_manager.create_index(
    table_name='users',
    column_names=['email'],
    unique=True
)

# List indexes for a table
indexes = index_manager.list_indexes('users')

# Analyze missing indexes
suggestions = index_manager.analyze_missing_indexes(User)

# Create common indexes
from core.database_optimization import create_common_indexes
create_common_indexes(engine)
```

#### Connection Pool Manager

Configure connection pooling:

```python
from core.database_optimization import ConnectionPoolManager
from sqlalchemy import create_engine

# Get pool configuration
pool_config = ConnectionPoolManager.get_pool_config(
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)

# Create engine with pooling
engine = create_engine(
    'sqlite:///database.db',
    **pool_config
)

# Get pool status
status = ConnectionPoolManager.get_pool_status(engine)
print(f"Active connections: {status['checked_out']}")
```

### 2. Caching System (`core/caching.py`)

#### Cache Manager

Unified caching interface:

```python
from core.caching import CacheManager, InMemoryCache, RedisCache

# Initialize with in-memory cache
cache_manager = CacheManager(backend=InMemoryCache())

# Or with Redis
cache_manager = CacheManager(backend=RedisCache(
    host='localhost',
    port=6379
))

# Cache decorator
@cache_manager.cached(expire=3600, key_prefix='solar')
def calculate_solar_production(location, modules):
    # Expensive calculation
    return result

# Manual caching
key = cache_manager.cache_key(location='Berlin', modules=30)
result = cache_manager.backend.get(key)
if result is None:
    result = expensive_calculation()
    cache_manager.backend.set(key, result, expire=3600)

# Get cache statistics
stats = cache_manager.get_stats()
```

#### Global Cache Initialization

```python
from core.caching import init_cache, cache

# Initialize cache (call once at startup)
init_cache(
    use_redis=True,
    redis_host='localhost',
    redis_port=6379,
    default_expire=3600
)

# Use simple decorator
@cache(expire=1800, key_prefix='products')
def get_products():
    return db.query(Product).all()
```

#### Cache Backends

**In-Memory Cache:**
- Fast, no external dependencies
- Limited to single process
- Good for development and small deployments

**Redis Cache:**
- Distributed caching
- Persistent across restarts
- Supports multiple processes/servers
- Recommended for production

### 3. Async Operations (`core/async_operations.py`)

#### Background Task Manager

Execute long-running tasks in the background:

```python
from core.async_operations import BackgroundTaskManager, get_task_manager

# Get global task manager
task_manager = get_task_manager()

# Create a background task
def generate_pdf(project_id):
    # Long-running PDF generation
    return pdf_bytes

task = task_manager.create_task(
    generate_pdf,
    project_id=123,
    name="Generate PDF for project 123"
)

# Check task status
task = task_manager.get_task(task.id)
print(f"Status: {task.status}, Progress: {task.progress}%")

# Get all active tasks
active_tasks = task_manager.get_active_tasks()

# Cancel a task
task_manager.cancel_task(task.id)

# Cleanup old tasks
task_manager.cleanup_old_tasks(max_age_hours=24)
```

#### Background Task Decorator

```python
from core.async_operations import background_task

@background_task(name="Process large dataset")
def process_dataset(data):
    # Long-running processing
    return results

# Call returns Task object immediately
task = process_dataset(large_data)
print(f"Task ID: {task.id}")
```

#### Progress Tracking

```python
from core.async_operations import ProgressTracker

def process_items(items, task):
    tracker = ProgressTracker(total=len(items), task=task)
    
    for item in items:
        process_item(item)
        tracker.update()
    
    tracker.complete()
```

#### Async Database Operations

```python
from core.async_operations import AsyncDatabaseOperations

# Bulk insert asynchronously
await AsyncDatabaseOperations.bulk_insert(
    session,
    Product,
    [
        {'name': 'Product 1', 'price': 100},
        {'name': 'Product 2', 'price': 200},
    ]
)

# Bulk update asynchronously
await AsyncDatabaseOperations.bulk_update(
    session,
    Product,
    [
        {'id': 1, 'price': 150},
        {'id': 2, 'price': 250},
    ]
)
```

### 4. Performance Monitoring (`core/performance_monitoring.py`)

#### Performance Monitor

Track application performance:

```python
from core.performance_monitoring import get_performance_monitor

# Get global monitor
monitor = get_performance_monitor()

# Record custom metric
monitor.record_metric(
    name='calculation_time',
    value=1.5,
    unit='seconds',
    metadata={'type': 'solar'}
)

# Record request time
monitor.record_request_time('/api/v1/solar/calculate', 0.5)

# Get endpoint statistics
stats = monitor.get_endpoint_stats('/api/v1/solar/calculate')
print(f"Average time: {stats['avg_time']:.3f}s")
print(f"P95: {stats['p95']:.3f}s")

# Get all endpoint stats
all_stats = monitor.get_all_endpoint_stats()

# Get slow queries
slow_queries = monitor.get_slow_queries(limit=10)

# Get system metrics
system_metrics = monitor.get_system_metrics()
print(f"CPU: {system_metrics['cpu_percent']}%")
print(f"Memory: {system_metrics['memory_percent']}%")

# Get complete summary
summary = monitor.get_metrics_summary()
```

#### Performance Decorators

```python
from core.performance_monitoring import monitor_performance, monitor_endpoint

# Monitor function performance
@monitor_performance(name='solar_calculation')
def calculate_solar(params):
    return result

# Monitor API endpoint
@monitor_endpoint('/api/v1/solar/calculate')
async def calculate_solar_endpoint(request):
    return response
```

#### Resource Monitor

Monitor system resources over time:

```python
from core.performance_monitoring import ResourceMonitor

# Initialize monitor
resource_monitor = ResourceMonitor(interval=60)

# Collect metrics
metrics = resource_monitor.collect_metrics()

# Get history
history = resource_monitor.get_history(hours=1)

# Get averages
averages = resource_monitor.get_average_metrics(hours=24)
print(f"Average CPU: {averages['avg_cpu_percent']:.1f}%")
```

## Integration with FastAPI

### Startup Configuration

```python
# main.py
from fastapi import FastAPI
from core.caching import init_cache
from core.performance_monitoring import init_performance_monitoring
from core.database_optimization import create_common_indexes

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize caching
    init_cache(
        use_redis=True,
        redis_host='localhost',
        redis_port=6379,
        default_expire=3600
    )
    
    # Initialize performance monitoring
    init_performance_monitoring(slow_threshold=1.0)
    
    # Create database indexes
    create_common_indexes(engine)
```

### Middleware Integration

```python
from fastapi import Request
import time

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record request time
    from core.performance_monitoring import get_performance_monitor
    monitor = get_performance_monitor()
    monitor.record_request_time(request.url.path, duration)
    
    # Add timing header
    response.headers["X-Process-Time"] = f"{duration:.3f}"
    
    return response
```

### API Endpoints

```python
from fastapi import APIRouter
from core.caching import cache
from core.async_operations import get_task_manager
from core.performance_monitoring import get_performance_monitor

router = APIRouter()

# Cached endpoint
@router.get("/products")
@cache(expire=3600, key_prefix='products')
async def get_products():
    return db.query(Product).all()

# Background task endpoint
@router.post("/generate-pdf/{project_id}")
async def generate_pdf(project_id: int):
    task_manager = get_task_manager()
    task = task_manager.create_task(
        pdf_service.generate,
        project_id,
        name=f"Generate PDF for project {project_id}"
    )
    return {"task_id": task.id}

# Task status endpoint
@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task_manager = get_task_manager()
    task = task_manager.get_task(task_id)
    if task:
        return task.to_dict()
    return {"error": "Task not found"}

# Performance metrics endpoint
@router.get("/metrics")
async def get_metrics():
    monitor = get_performance_monitor()
    return monitor.get_metrics_summary()
```

## Best Practices

### 1. Query Optimization

- **Use eager loading** for relationships to avoid N+1 queries
- **Add indexes** on frequently queried columns
- **Use pagination** for large result sets
- **Monitor slow queries** and optimize them

### 2. Caching Strategy

- **Cache expensive calculations** (solar production, pricing)
- **Cache frequently accessed data** (products, configurations)
- **Set appropriate TTL** based on data volatility
- **Invalidate cache** when data changes

### 3. Background Tasks

- **Use for long-running operations** (PDF generation, bulk imports)
- **Track progress** for user feedback
- **Handle errors gracefully** with retry logic
- **Clean up old tasks** regularly

### 4. Performance Monitoring

- **Monitor all endpoints** to identify bottlenecks
- **Set slow query thresholds** appropriately
- **Review metrics regularly** to spot trends
- **Alert on performance degradation**

## Performance Targets

Based on Requirements 8.4 and 8.5:

- **Simple queries**: < 100ms
- **Complex calculations**: < 500ms
- **API responses**: < 200ms (cached), < 1s (uncached)
- **Background tasks**: Async, non-blocking
- **Cache hit rate**: > 80% for frequently accessed data
- **Database connections**: Pool size 10-20, max overflow 20

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Response Times**
   - Average, P50, P95, P99
   - Per endpoint

2. **Cache Performance**
   - Hit rate
   - Miss rate
   - Cache size

3. **Database Performance**
   - Query execution time
   - Connection pool usage
   - Slow queries

4. **System Resources**
   - CPU usage
   - Memory usage
   - Disk I/O

### Setting Up Alerts

```python
# Example alert configuration
ALERT_THRESHOLDS = {
    'slow_query': 1.0,  # seconds
    'high_cpu': 80,  # percent
    'high_memory': 85,  # percent
    'low_cache_hit_rate': 70,  # percent
}

def check_alerts():
    monitor = get_performance_monitor()
    system_metrics = monitor.get_system_metrics()
    
    if system_metrics['cpu_percent'] > ALERT_THRESHOLDS['high_cpu']:
        send_alert('High CPU usage')
    
    if system_metrics['memory_percent'] > ALERT_THRESHOLDS['high_memory']:
        send_alert('High memory usage')
    
    cache_stats = get_cache_manager().get_stats()
    if cache_stats.get('hit_rate', 0) < ALERT_THRESHOLDS['low_cache_hit_rate']:
        send_alert('Low cache hit rate')
```

## Troubleshooting

### High Memory Usage

1. Check cache size and clear if needed
2. Review connection pool settings
3. Look for memory leaks in long-running tasks

### Slow Queries

1. Check query execution plans
2. Add missing indexes
3. Optimize query structure
4. Consider caching results

### Cache Misses

1. Verify cache configuration
2. Check TTL settings
3. Review cache key generation
4. Monitor cache eviction

### Connection Pool Exhaustion

1. Increase pool size
2. Reduce connection timeout
3. Check for connection leaks
4. Review query patterns

## Additional Resources

- [SQLAlchemy Performance Tips](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/performance/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
