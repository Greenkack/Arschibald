"""
Demo script for backend performance optimization features

This script demonstrates all the performance optimization features:
- Database query optimization
- Caching with Redis/In-memory
- Async operations and background tasks
- Performance monitoring
"""

import time
import asyncio
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import performance modules
from core.database_optimization import (
    QueryOptimizer,
    IndexManager,
    ConnectionPoolManager,
    create_common_indexes,
    monitor_query_performance
)
from core.caching import (
    init_cache,
    cache,
    get_cache_manager
)
from core.async_operations import (
    get_task_manager,
    background_task,
    ProgressTracker
)
from core.performance_monitoring import (
    init_performance_monitoring,
    get_performance_monitor,
    monitor_performance,
    ResourceMonitor
)

# Setup test database
Base = declarative_base()


class DemoUser(Base):
    __tablename__ = 'demo_users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)


def setup_database():
    """Setup demo database"""
    print("\n=== Setting up database ===")
    
    # Create engine with connection pooling
    pool_config = ConnectionPoolManager.get_pool_config(
        pool_size=5,
        max_overflow=10
    )
    engine = create_engine('sqlite:///demo.db', **pool_config)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add sample data
    if session.query(DemoUser).count() == 0:
        users = [
            DemoUser(email=f'user{i}@example.com', name=f'User {i}')
            for i in range(1, 11)
        ]
        session.add_all(users)
        session.commit()
        print(f"Added {len(users)} demo users")
    
    return engine, session


def demo_database_optimization(engine, session):
    """Demonstrate database optimization features"""
    print("\n=== Database Optimization Demo ===")
    
    # 1. Query Optimizer
    print("\n1. Query Optimizer")
    optimizer = QueryOptimizer(session)
    
    query = session.query(DemoUser)
    optimized_query = optimizer.optimize_query(query)
    paginated_query = optimizer.add_pagination(optimized_query, page=1, page_size=5)
    
    results = paginated_query.all()
    print(f"   Retrieved {len(results)} users (paginated)")
    
    # 2. Index Manager
    print("\n2. Index Manager")
    index_manager = IndexManager(engine)
    
    try:
        index_manager.create_index('demo_users', ['email'], unique=True)
        print("   Created index on email column")
    except Exception as e:
        print(f"   Index already exists: {e}")
    
    indexes = index_manager.list_indexes('demo_users')
    print(f"   Total indexes: {len(indexes)}")
    
    # 3. Connection Pool Status
    print("\n3. Connection Pool Status")
    status = ConnectionPoolManager.get_pool_status(engine)
    print(f"   Pool size: {status['size']}")
    print(f"   Checked out: {status['checked_out']}")
    print(f"   Checked in: {status['checked_in']}")
    
    # 4. Query Performance Monitoring
    print("\n4. Query Performance Monitoring")
    
    @optimizer.track_query_performance("get_all_users")
    def get_all_users():
        time.sleep(0.1)  # Simulate slow query
        return session.query(DemoUser).all()
    
    users = get_all_users()
    print(f"   Retrieved {len(users)} users")
    
    stats = optimizer.get_query_stats()
    if "get_all_users" in stats:
        print(f"   Query stats: {stats['get_all_users']}")


def demo_caching():
    """Demonstrate caching features"""
    print("\n=== Caching Demo ===")
    
    # Initialize cache
    print("\n1. Initialize Cache")
    init_cache(use_redis=False, default_expire=60)
    print("   Initialized in-memory cache")
    
    # Cache decorator
    print("\n2. Cache Decorator")
    call_count = 0
    
    @cache(expire=30, key_prefix='demo')
    def expensive_calculation(x, y):
        nonlocal call_count
        call_count += 1
        time.sleep(0.5)  # Simulate expensive operation
        return x + y
    
    print("   First call (cache miss)...")
    result1 = expensive_calculation(5, 10)
    print(f"   Result: {result1}, Calls: {call_count}")
    
    print("   Second call (cache hit)...")
    result2 = expensive_calculation(5, 10)
    print(f"   Result: {result2}, Calls: {call_count}")
    
    # Cache statistics
    print("\n3. Cache Statistics")
    cache_manager = get_cache_manager()
    stats = cache_manager.get_stats()
    print(f"   Cache stats: {stats}")
    
    # Manual caching
    print("\n4. Manual Caching")
    key = cache_manager.cache_key(param1='value1', param2='value2')
    cache_manager.backend.set(key, {'data': 'cached_value'}, expire=60)
    cached_value = cache_manager.backend.get(key)
    print(f"   Cached value: {cached_value}")


def demo_async_operations():
    """Demonstrate async operations and background tasks"""
    print("\n=== Async Operations Demo ===")
    
    # Get task manager
    task_manager = get_task_manager()
    
    # 1. Simple background task
    print("\n1. Simple Background Task")
    
    def simple_task(x):
        time.sleep(1)
        return x * 2
    
    task = task_manager.create_task(simple_task, 5, name="Simple calculation")
    print(f"   Created task: {task.id}")
    print(f"   Status: {task.status}")
    
    # Wait for completion
    time.sleep(1.5)
    print(f"   Status: {task.status}")
    print(f"   Result: {task.result}")
    
    # 2. Background task with progress
    print("\n2. Background Task with Progress")
    
    def task_with_progress(items, task):
        tracker = ProgressTracker(total=len(items), task=task)
        for i, item in enumerate(items):
            time.sleep(0.2)
            tracker.update()
            print(f"   Progress: {task.progress:.1f}%")
        tracker.complete()
        return "Completed"
    
    task2 = task_manager.create_task(
        task_with_progress,
        [1, 2, 3, 4, 5],
        task=None,
        name="Process items"
    )
    
    # Wait for completion
    time.sleep(1.5)
    print(f"   Final status: {task2.status}")
    
    # 3. Background task decorator
    print("\n3. Background Task Decorator")
    
    @background_task(name="Decorated task")
    def decorated_task(x, y):
        time.sleep(0.5)
        return x + y
    
    task3 = decorated_task(10, 20)
    print(f"   Created task: {task3.id}")
    
    time.sleep(0.7)
    print(f"   Result: {task3.result}")
    
    # 4. Task management
    print("\n4. Task Management")
    active_tasks = task_manager.get_active_tasks()
    print(f"   Active tasks: {len(active_tasks)}")
    
    all_tasks = task_manager.get_all_tasks()
    print(f"   Total tasks: {len(all_tasks)}")
    
    # Cleanup
    task_manager.cleanup_old_tasks(max_age_hours=0)
    print("   Cleaned up old tasks")


def demo_performance_monitoring():
    """Demonstrate performance monitoring features"""
    print("\n=== Performance Monitoring Demo ===")
    
    # Initialize monitoring
    print("\n1. Initialize Monitoring")
    init_performance_monitoring(slow_threshold=0.5)
    print("   Initialized performance monitoring")
    
    # Get monitor
    monitor = get_performance_monitor()
    
    # 2. Monitor function performance
    print("\n2. Monitor Function Performance")
    
    @monitor_performance(name='demo_calculation')
    def demo_calculation(x):
        time.sleep(0.3)
        return x ** 2
    
    result = demo_calculation(5)
    print(f"   Result: {result}")
    
    # 3. Record custom metrics
    print("\n3. Record Custom Metrics")
    monitor.record_metric('custom_metric', 1.5, 'seconds', {'type': 'demo'})
    print("   Recorded custom metric")
    
    # 4. Simulate API requests
    print("\n4. Simulate API Requests")
    monitor.record_request_time('/api/v1/calculate', 0.2)
    monitor.record_request_time('/api/v1/calculate', 0.3)
    monitor.record_request_time('/api/v1/calculate', 0.8)  # Slow request
    
    stats = monitor.get_endpoint_stats('/api/v1/calculate')
    print(f"   Endpoint stats:")
    print(f"     Count: {stats['count']}")
    print(f"     Avg time: {stats['avg_time']:.3f}s")
    print(f"     Max time: {stats['max_time']:.3f}s")
    
    # 5. Slow queries
    print("\n5. Slow Queries")
    slow_queries = monitor.get_slow_queries()
    print(f"   Slow queries detected: {len(slow_queries)}")
    for sq in slow_queries:
        print(f"     {sq['endpoint']}: {sq['duration']:.3f}s")
    
    # 6. System metrics
    print("\n6. System Metrics")
    system_metrics = monitor.get_system_metrics()
    print(f"   CPU: {system_metrics['cpu_percent']:.1f}%")
    print(f"   Memory: {system_metrics['memory_percent']:.1f}%")
    print(f"   Disk: {system_metrics['disk_percent']:.1f}%")
    
    # 7. Complete summary
    print("\n7. Complete Summary")
    summary = monitor.get_metrics_summary()
    print(f"   Total metrics: {summary['total_metrics']}")
    print(f"   Total requests: {summary['total_requests']}")
    print(f"   Total endpoints: {summary['total_endpoints']}")
    
    # 8. Resource monitoring
    print("\n8. Resource Monitoring")
    resource_monitor = ResourceMonitor()
    
    for i in range(3):
        metrics = resource_monitor.collect_metrics()
        print(f"   Sample {i+1}: CPU {metrics['cpu_percent']:.1f}%, "
              f"Memory {metrics['memory_percent']:.1f}%")
        time.sleep(0.5)
    
    averages = resource_monitor.get_average_metrics(hours=1)
    print(f"   Average CPU: {averages['avg_cpu_percent']:.1f}%")
    print(f"   Average Memory: {averages['avg_memory_percent']:.1f}%")


def demo_integration():
    """Demonstrate integrated usage of all features"""
    print("\n=== Integration Demo ===")
    
    print("\n1. Cached Query with Monitoring")
    
    @cache(expire=60, key_prefix='integration')
    @monitor_performance(name='cached_query')
    def get_data(param):
        time.sleep(0.5)
        return f"Data for {param}"
    
    # First call - cache miss
    print("   First call (cache miss)...")
    result1 = get_data('test')
    print(f"   Result: {result1}")
    
    # Second call - cache hit
    print("   Second call (cache hit)...")
    result2 = get_data('test')
    print(f"   Result: {result2}")
    
    print("\n2. Background Task with Caching and Monitoring")
    
    @background_task(name="Cached background task")
    @cache(expire=60)
    @monitor_performance(name='bg_task')
    def background_cached_task(x):
        time.sleep(0.5)
        return x * 3
    
    task = background_cached_task(10)
    print(f"   Created task: {task.id}")
    
    time.sleep(0.7)
    print(f"   Result: {task.result}")
    
    # Show final statistics
    print("\n3. Final Statistics")
    monitor = get_performance_monitor()
    cache_manager = get_cache_manager()
    
    print(f"   Performance metrics: {len(monitor.metrics)}")
    print(f"   Cache stats: {cache_manager.get_stats()}")


def main():
    """Run all demos"""
    print("=" * 60)
    print("Backend Performance Optimization Demo")
    print("=" * 60)
    
    # Setup
    engine, session = setup_database()
    
    # Run demos
    demo_database_optimization(engine, session)
    demo_caching()
    demo_async_operations()
    demo_performance_monitoring()
    demo_integration()
    
    # Cleanup
    session.close()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
