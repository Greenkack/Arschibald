"""
Tests for Backend Performance Optimization

Tests for database optimization, caching, async operations, and performance monitoring.
"""

import pytest
import time
from unittest.mock import Mock, patch
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Import modules to test
from core.database_optimization import (
    QueryOptimizer,
    IndexManager,
    ConnectionPoolManager,
    monitor_query_performance
)
from core.caching import (
    InMemoryCache,
    CacheManager,
    get_cache_manager,
    init_cache,
    cache
)
from core.async_operations import (
    BackgroundTaskManager,
    Task,
    TaskStatus,
    ProgressTracker,
    background_task
)
from core.performance_monitoring import (
    PerformanceMonitor,
    get_performance_monitor,
    monitor_performance,
    ResourceMonitor
)

# Test database setup
Base = declarative_base()


class TestUser(Base):
    __tablename__ = 'test_users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    projects = relationship('TestProject', back_populates='user')


class TestProject(Base):
    __tablename__ = 'test_projects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('test_users.id'))
    user = relationship('TestUser', back_populates='projects')


@pytest.fixture
def engine():
    """Create test database engine"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create test database session"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# Database Optimization Tests

class TestQueryOptimizer:
    """Test QueryOptimizer class"""
    
    def test_optimize_query(self, session):
        """Test query optimization"""
        optimizer = QueryOptimizer(session)
        query = session.query(TestUser)
        
        optimized = optimizer.optimize_query(query)
        assert optimized is not None
    
    def test_add_eager_loading(self, session):
        """Test eager loading"""
        optimizer = QueryOptimizer(session)
        query = session.query(TestUser)
        
        query_with_loading = optimizer.add_eager_loading(query, TestUser.projects)
        assert query_with_loading is not None
    
    def test_add_pagination(self, session):
        """Test pagination"""
        optimizer = QueryOptimizer(session)
        query = session.query(TestUser)
        
        paginated = optimizer.add_pagination(query, page=1, page_size=10)
        assert paginated is not None
    
    def test_track_query_performance(self, session):
        """Test query performance tracking"""
        optimizer = QueryOptimizer(session)
        
        @optimizer.track_query_performance("test_query")
        def test_query():
            time.sleep(0.1)
            return "result"
        
        result = test_query()
        assert result == "result"
        
        stats = optimizer.get_query_stats()
        assert "test_query" in stats
        assert stats["test_query"]["count"] == 1


class TestIndexManager:
    """Test IndexManager class"""
    
    def test_create_index(self, engine):
        """Test index creation"""
        manager = IndexManager(engine)
        
        # Create index
        manager.create_index('test_users', ['email'], unique=True)
        
        # Verify index exists
        indexes = manager.list_indexes('test_users')
        assert any('email' in idx['column_names'] for idx in indexes)
    
    def test_list_indexes(self, engine):
        """Test listing indexes"""
        manager = IndexManager(engine)
        indexes = manager.list_indexes('test_users')
        assert isinstance(indexes, list)


class TestConnectionPoolManager:
    """Test ConnectionPoolManager class"""
    
    def test_get_pool_config(self):
        """Test pool configuration"""
        config = ConnectionPoolManager.get_pool_config(
            pool_size=10,
            max_overflow=20
        )
        
        assert config['pool_size'] == 10
        assert config['max_overflow'] == 20
        assert config['pool_pre_ping'] is True
    
    def test_get_pool_status(self, engine):
        """Test pool status"""
        status = ConnectionPoolManager.get_pool_status(engine)
        
        assert 'size' in status
        assert 'checked_in' in status
        assert 'checked_out' in status


# Caching Tests

class TestInMemoryCache:
    """Test InMemoryCache class"""
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
    
    def test_expiration(self):
        """Test cache expiration"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1', expire=1)
        assert cache.get('key1') == 'value1'
        
        time.sleep(1.1)
        assert cache.get('key1') is None
    
    def test_delete(self):
        """Test deleting values"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        cache.delete('key1')
        assert cache.get('key1') is None
    
    def test_clear(self):
        """Test clearing cache"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
    
    def test_exists(self):
        """Test checking existence"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        assert cache.exists('key1') is True
        assert cache.exists('key2') is False
    
    def test_stats(self):
        """Test cache statistics"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        cache.get('key1')  # Hit
        cache.get('key2')  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1


class TestCacheManager:
    """Test CacheManager class"""
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        manager = CacheManager()
        
        key1 = manager.cache_key('arg1', 'arg2', param='value')
        key2 = manager.cache_key('arg1', 'arg2', param='value')
        key3 = manager.cache_key('arg1', 'arg3', param='value')
        
        assert key1 == key2
        assert key1 != key3
    
    def test_cached_decorator(self):
        """Test cached decorator"""
        manager = CacheManager()
        call_count = 0
        
        @manager.cached(expire=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Only called once due to caching
    
    def test_cache_decorator(self):
        """Test simple cache decorator"""
        init_cache(use_redis=False)
        call_count = 0
        
        @cache(expire=60)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3
        
        result1 = test_function(5)
        result2 = test_function(5)
        
        assert result1 == 15
        assert result2 == 15
        assert call_count == 1


# Async Operations Tests

class TestBackgroundTaskManager:
    """Test BackgroundTaskManager class"""
    
    def test_create_task(self):
        """Test task creation"""
        manager = BackgroundTaskManager(max_workers=2)
        
        def test_func():
            time.sleep(0.1)
            return "result"
        
        task = manager.create_task(test_func, name="test_task")
        
        assert task.id is not None
        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING or task.status == TaskStatus.RUNNING
        
        # Wait for completion
        time.sleep(0.2)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "result"
        
        manager.shutdown()
    
    def test_get_task(self):
        """Test getting task by ID"""
        manager = BackgroundTaskManager()
        
        def test_func():
            return "result"
        
        task = manager.create_task(test_func)
        retrieved = manager.get_task(task.id)
        
        assert retrieved is not None
        assert retrieved.id == task.id
        
        manager.shutdown()
    
    def test_get_active_tasks(self):
        """Test getting active tasks"""
        manager = BackgroundTaskManager()
        
        def slow_func():
            time.sleep(0.5)
        
        task = manager.create_task(slow_func)
        active = manager.get_active_tasks()
        
        assert len(active) > 0
        assert task.id in [t.id for t in active]
        
        manager.shutdown()
    
    def test_cancel_task(self):
        """Test task cancellation"""
        manager = BackgroundTaskManager()
        
        def slow_func():
            time.sleep(1.0)
        
        task = manager.create_task(slow_func)
        cancelled = manager.cancel_task(task.id)
        
        assert cancelled is True
        assert task.status == TaskStatus.CANCELLED
        
        manager.shutdown()


class TestTask:
    """Test Task class"""
    
    def test_task_creation(self):
        """Test task creation"""
        task = Task(name="test_task")
        
        assert task.id is not None
        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0
    
    def test_task_to_dict(self):
        """Test task serialization"""
        task = Task(name="test_task")
        task_dict = task.to_dict()
        
        assert task_dict['id'] == task.id
        assert task_dict['name'] == "test_task"
        assert task_dict['status'] == TaskStatus.PENDING.value


class TestProgressTracker:
    """Test ProgressTracker class"""
    
    def test_progress_tracking(self):
        """Test progress tracking"""
        task = Task(name="test")
        tracker = ProgressTracker(total=10, task=task)
        
        for i in range(10):
            tracker.update()
        
        assert task.progress == 100.0
    
    def test_complete(self):
        """Test completion"""
        task = Task(name="test")
        tracker = ProgressTracker(total=10, task=task)
        
        tracker.complete()
        assert task.progress == 100.0


class TestBackgroundTaskDecorator:
    """Test background_task decorator"""
    
    def test_decorator(self):
        """Test background task decorator"""
        @background_task(name="test_bg_task")
        def test_func(x):
            return x * 2
        
        task = test_func(5)
        
        assert isinstance(task, Task)
        assert task.name == "test_bg_task"
        
        # Wait for completion
        time.sleep(0.1)
        assert task.result == 10


# Performance Monitoring Tests

class TestPerformanceMonitor:
    """Test PerformanceMonitor class"""
    
    def test_record_metric(self):
        """Test recording metrics"""
        monitor = PerformanceMonitor()
        
        monitor.record_metric('test_metric', 1.5, 'seconds')
        
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].name == 'test_metric'
        assert monitor.metrics[0].value == 1.5
    
    def test_record_request_time(self):
        """Test recording request times"""
        monitor = PerformanceMonitor()
        
        monitor.record_request_time('/api/test', 0.5)
        monitor.record_request_time('/api/test', 0.7)
        
        stats = monitor.get_endpoint_stats('/api/test')
        
        assert stats['count'] == 2
        assert stats['avg_time'] == 0.6
        assert stats['min_time'] == 0.5
        assert stats['max_time'] == 0.7
    
    def test_slow_query_detection(self):
        """Test slow query detection"""
        monitor = PerformanceMonitor()
        monitor.slow_threshold = 0.5
        
        monitor.record_request_time('/api/slow', 1.0)
        
        slow_queries = monitor.get_slow_queries()
        assert len(slow_queries) == 1
        assert slow_queries[0]['endpoint'] == '/api/slow'
    
    def test_get_system_metrics(self):
        """Test getting system metrics"""
        monitor = PerformanceMonitor()
        
        metrics = monitor.get_system_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'disk_percent' in metrics
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary"""
        monitor = PerformanceMonitor()
        
        monitor.record_request_time('/api/test', 0.5)
        
        summary = monitor.get_metrics_summary()
        
        assert 'total_requests' in summary
        assert 'system_metrics' in summary
        assert 'endpoint_stats' in summary


class TestMonitorPerformanceDecorator:
    """Test monitor_performance decorator"""
    
    def test_decorator(self):
        """Test performance monitoring decorator"""
        @monitor_performance(name='test_function')
        def test_func():
            time.sleep(0.1)
            return "result"
        
        result = test_func()
        
        assert result == "result"
        
        monitor = get_performance_monitor()
        # Check that metric was recorded
        assert len(monitor.metrics) > 0


class TestResourceMonitor:
    """Test ResourceMonitor class"""
    
    def test_collect_metrics(self):
        """Test collecting metrics"""
        monitor = ResourceMonitor()
        
        metrics = monitor.collect_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'timestamp' in metrics
    
    def test_get_history(self):
        """Test getting history"""
        monitor = ResourceMonitor()
        
        monitor.collect_metrics()
        time.sleep(0.1)
        monitor.collect_metrics()
        
        history = monitor.get_history(hours=1)
        assert len(history) == 2
    
    def test_get_average_metrics(self):
        """Test getting average metrics"""
        monitor = ResourceMonitor()
        
        monitor.collect_metrics()
        monitor.collect_metrics()
        
        averages = monitor.get_average_metrics(hours=1)
        
        assert 'avg_cpu_percent' in averages
        assert 'avg_memory_percent' in averages


# Integration Tests

class TestPerformanceIntegration:
    """Integration tests for performance features"""
    
    def test_cached_query_with_monitoring(self, session):
        """Test cached query with performance monitoring"""
        init_cache(use_redis=False)
        call_count = 0
        
        @cache(expire=60)
        @monitor_performance(name='cached_query')
        def get_users():
            nonlocal call_count
            call_count += 1
            return session.query(TestUser).all()
        
        # First call - cache miss
        result1 = get_users()
        
        # Second call - cache hit
        result2 = get_users()
        
        assert call_count == 1  # Only called once
        
        monitor = get_performance_monitor()
        assert len(monitor.metrics) > 0
    
    def test_background_task_with_progress(self):
        """Test background task with progress tracking"""
        manager = BackgroundTaskManager()
        
        def process_items(items):
            time.sleep(0.1)
            return "done"
        
        task = manager.create_task(
            process_items,
            [1, 2, 3, 4, 5],
            name="process_items"
        )
        
        # Wait for completion
        time.sleep(0.3)
        
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "done"
        
        manager.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
