"""
Performance Monitoring Module

This module provides performance monitoring utilities including:
- Request/response time tracking
- Resource usage monitoring
- Performance metrics collection
- Slow query detection
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import psutil
import logging
from functools import wraps
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.request_times: Dict[str, List[float]] = defaultdict(list)
        self.slow_queries: List[Dict[str, Any]] = []
        self.slow_threshold = 1.0  # seconds
    
    def record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            metadata=metadata or {}
        )
        self.metrics.append(metric)
        
        # Keep only recent metrics (last 1000)
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def record_request_time(self, endpoint: str, duration: float):
        """
        Record request processing time
        
        Args:
            endpoint: API endpoint
            duration: Processing time in seconds
        """
        self.request_times[endpoint].append(duration)
        
        # Keep only recent times (last 100 per endpoint)
        if len(self.request_times[endpoint]) > 100:
            self.request_times[endpoint] = self.request_times[endpoint][-100:]
        
        # Record as metric
        self.record_metric(
            name=f"request_time_{endpoint}",
            value=duration,
            unit="seconds",
            metadata={'endpoint': endpoint}
        )
        
        # Check for slow requests
        if duration > self.slow_threshold:
            self.slow_queries.append({
                'endpoint': endpoint,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            logger.warning(f"Slow request detected: {endpoint} took {duration:.2f}s")
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """
        Get statistics for an endpoint
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Statistics dictionary
        """
        times = self.request_times.get(endpoint, [])
        
        if not times:
            return {
                'endpoint': endpoint,
                'count': 0,
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        sorted_times = sorted(times)
        count = len(times)
        
        return {
            'endpoint': endpoint,
            'count': count,
            'avg_time': sum(times) / count,
            'min_time': min(times),
            'max_time': max(times),
            'p50': sorted_times[int(count * 0.5)],
            'p95': sorted_times[int(count * 0.95)] if count > 20 else max(times),
            'p99': sorted_times[int(count * 0.99)] if count > 100 else max(times)
        }
    
    def get_all_endpoint_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all endpoints"""
        return [
            self.get_endpoint_stats(endpoint)
            for endpoint in self.request_times.keys()
        ]
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent slow queries
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of slow query information
        """
        return self.slow_queries[-limit:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system resource metrics
        
        Returns:
            System metrics dictionary
        """
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_used_gb': psutil.disk_usage('/').used / (1024 * 1024 * 1024),
            'disk_free_gb': psutil.disk_usage('/').free / (1024 * 1024 * 1024),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics
        
        Returns:
            Metrics summary
        """
        return {
            'total_metrics': len(self.metrics),
            'total_requests': sum(len(times) for times in self.request_times.values()),
            'total_endpoints': len(self.request_times),
            'slow_queries_count': len(self.slow_queries),
            'system_metrics': self.get_system_metrics(),
            'endpoint_stats': self.get_all_endpoint_stats()
        }
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.request_times.clear()
        self.slow_queries.clear()
        logger.info("Cleared all performance metrics")


def monitor_performance(name: str = ""):
    """
    Decorator to monitor function performance
    
    Args:
        name: Name for the metric
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metric_name = name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record metric
                monitor = get_performance_monitor()
                monitor.record_metric(
                    name=f"function_{metric_name}",
                    value=duration,
                    unit="seconds"
                )
                
                # Log if slow
                if duration > 1.0:
                    logger.warning(
                        f"Slow function: {metric_name} took {duration:.2f}s"
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {metric_name} failed after {duration:.2f}s: {e}"
                )
                raise
        
        return wrapper
    return decorator


def monitor_endpoint(endpoint: str):
    """
    Decorator to monitor API endpoint performance
    
    Args:
        endpoint: Endpoint path
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record request time
                monitor = get_performance_monitor()
                monitor.record_request_time(endpoint, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Endpoint {endpoint} failed after {duration:.2f}s: {e}"
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record request time
                monitor = get_performance_monitor()
                monitor.record_request_time(endpoint, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Endpoint {endpoint} failed after {duration:.2f}s: {e}"
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ResourceMonitor:
    """Monitor system resource usage"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.history: List[Dict[str, Any]] = []
        self.max_history = 1440  # 24 hours at 1-minute intervals
    
    def collect_metrics(self):
        """Collect current resource metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            'disk_percent': psutil.disk_usage('/').percent,
            'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024 * 1024),
            'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024 * 1024),
        }
        
        self.history.append(metrics)
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return metrics
    
    def get_history(
        self,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get resource history
        
        Args:
            hours: Number of hours of history
            
        Returns:
            List of metrics
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.history
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """
        Get average metrics over time period
        
        Args:
            hours: Number of hours
            
        Returns:
            Average metrics
        """
        history = self.get_history(hours)
        
        if not history:
            return {}
        
        return {
            'avg_cpu_percent': sum(m['cpu_percent'] for m in history) / len(history),
            'avg_memory_percent': sum(m['memory_percent'] for m in history) / len(history),
            'avg_memory_used_mb': sum(m['memory_used_mb'] for m in history) / len(history),
            'avg_disk_percent': sum(m['disk_percent'] for m in history) / len(history),
        }


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def init_performance_monitoring(slow_threshold: float = 1.0):
    """
    Initialize performance monitoring
    
    Args:
        slow_threshold: Threshold for slow query detection in seconds
    """
    global _performance_monitor
    _performance_monitor = PerformanceMonitor()
    _performance_monitor.slow_threshold = slow_threshold
    logger.info(f"Performance monitoring initialized (slow threshold: {slow_threshold}s)")
