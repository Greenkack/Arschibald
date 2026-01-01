"""
Database Performance Monitoring System

Tracks query performance, connection pool metrics, and transaction analytics.
Provides real-time insights for database optimization.

Author: ARSCHIBALD Development Team
Date: 2025-12-14
"""

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from contextlib import contextmanager

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class QueryMetric:
    """Single query execution metric"""
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        self.__dict__.update(state)
    
    query_id: str
    sql: str
    duration_ms: float
    rows_affected: int
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionPoolMetric:
    """Connection pool status metric"""
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        self.__dict__.update(state)
    
    active_connections: int
    idle_connections: int
    total_connections: int
    max_connections: int
    wait_time_ms: float
    timestamp: datetime


class QueryTracker:
    """Context manager for tracking query execution"""
    
    def __init__(self, monitor: 'DBPerformanceMonitor', sql: str):
        self.monitor = monitor
        self.sql = sql
        self.start_time: Optional[float] = None
        self.rows_affected: int = 0
        self.success: bool = False
        self.error: Optional[str] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is not None:
            self.success = False
            self.error = str(exc_val)
        else:
            self.success = True
        
        self.monitor._record_query(
            sql=self.sql,
            duration_ms=duration_ms,
            rows_affected=self.rows_affected,
            success=self.success,
            error=self.error
        )
    
    def record_rows(self, count: int):
        """Record number of rows affected"""
        self.rows_affected = count


class DBPerformanceMonitor:
    """Monitor database performance metrics"""
    
    def __getstate__(self):
        return {
            'history_size': self.history_size,
            'slow_query_threshold_ms': self.slow_query_threshold_ms,
            'sampling_rate': self._sampling_rate
        }
    
    def __setstate__(self, state):
        self.__init__(
            history_size=state.get('history_size', 1000),
            slow_query_threshold_ms=state.get('slow_query_threshold_ms', 1000)
        )
        self._sampling_rate = state.get('sampling_rate', 1.0)
    
    def __init__(
        self,
        history_size: int = 1000,
        slow_query_threshold_ms: float = 1000
    ):
        self.history_size = history_size
        self.slow_query_threshold_ms = slow_query_threshold_ms
        
        self._query_metrics: deque[QueryMetric] = deque(maxlen=history_size)
        self._pool_metrics: deque[ConnectionPoolMetric] = deque(maxlen=100)
        self._slow_queries: deque[QueryMetric] = deque(maxlen=100)
        
        self._lock = threading.RLock()
        self._total_queries = 0
        self._total_slow_queries = 0
        self._total_errors = 0
        self._sampling_rate = 1.0
        
        self._query_id_counter = 0
    
    @contextmanager
    def track_query(self, sql: str):
        """
        Context manager to track query execution
        
        Usage:
            with monitor.track_query("SELECT * FROM users") as tracker:
                result = execute_query(...)
                tracker.record_rows(len(result))
        """
        tracker = QueryTracker(self, sql)
        try:
            yield tracker
        finally:
            pass
    
    def _record_query(
        self,
        sql: str,
        duration_ms: float,
        rows_affected: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Internal method to record query metric"""
        # Sampling
        import random
        if random.random() > self._sampling_rate:
            return
        
        with self._lock:
            self._query_id_counter += 1
            query_id = f"q_{self._query_id_counter}"
            
            metric = QueryMetric(
                query_id=query_id,
                sql=sql[:200],  # Truncate long queries
                duration_ms=duration_ms,
                rows_affected=rows_affected,
                timestamp=datetime.now(),
                success=success,
                error=error
            )
            
            self._query_metrics.append(metric)
            self._total_queries += 1
            
            if not success:
                self._total_errors += 1
            
            # Slow query detection
            if duration_ms > self.slow_query_threshold_ms:
                self._slow_queries.append(metric)
                self._total_slow_queries += 1
                logger.warning(
                    "slow_query_detected",
                    duration_ms=duration_ms,
                    sql=sql[:100]
                )
    
    def record_connection_pool_status(
        self,
        active: int,
        idle: int,
        total: int,
        max_connections: int,
        wait_time_ms: float = 0.0
    ):
        """Record connection pool status"""
        metric = ConnectionPoolMetric(
            active_connections=active,
            idle_connections=idle,
            total_connections=total,
            max_connections=max_connections,
            wait_time_ms=wait_time_ms,
            timestamp=datetime.now()
        )
        
        with self._lock:
            self._pool_metrics.append(metric)
    
    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._lock:
            recent_queries = list(self._query_metrics)
            
            if not recent_queries:
                return {
                    'total_queries': self._total_queries,
                    'total_slow_queries': self._total_slow_queries,
                    'total_errors': self._total_errors,
                    'avg_duration_ms': 0.0,
                    'recent_queries': 0,
                    'slow_query_percentage': 0.0,
                    'error_rate': 0.0,
                    'active_connections': 0,
                    'status': 'no_data'
                }
            
            durations = [q.duration_ms for q in recent_queries]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            successful = [q for q in recent_queries if q.success]
            success_rate = len(successful) / len(recent_queries)
            
            # Connection pool
            latest_pool = self._pool_metrics[-1] if self._pool_metrics else None
            
            return {
                'total_queries': self._total_queries,
                'total_slow_queries': self._total_slow_queries,
                'total_errors': self._total_errors,
                'recent_queries': len(recent_queries),
                'avg_duration_ms': round(avg_duration, 2),
                'max_duration_ms': round(max_duration, 2),
                'min_duration_ms': round(min_duration, 2),
                'slow_query_percentage': round(
                    (self._total_slow_queries / self._total_queries * 100)
                    if self._total_queries > 0 else 0, 2
                ),
                'success_rate': round(success_rate * 100, 2),
                'error_rate': round((1 - success_rate) * 100, 2),
                'active_connections': latest_pool.active_connections if latest_pool else 0,
                'idle_connections': latest_pool.idle_connections if latest_pool else 0,
                'total_connections': latest_pool.total_connections if latest_pool else 0,
                'status': self._get_status(avg_duration, success_rate)
            }
    
    def _get_status(self, avg_duration: float, success_rate: float) -> str:
        """Determine overall status"""
        if success_rate < 0.95:
            return 'critical'
        if avg_duration > self.slow_query_threshold_ms * 2:
            return 'warning'
        if avg_duration > self.slow_query_threshold_ms:
            return 'degraded'
        return 'ok'
    
    def get_slow_queries(self, limit: int = 10) -> list[QueryMetric]:
        """Get recent slow queries"""
        with self._lock:
            return list(self._slow_queries)[-limit:]
    
    def get_recent_queries(self, limit: int = 20) -> list[QueryMetric]:
        """Get recent queries"""
        with self._lock:
            return list(self._query_metrics)[-limit:]
    
    def set_slow_query_threshold(self, threshold_ms: float):
        """Set slow query threshold"""
        self.slow_query_threshold_ms = threshold_ms
        logger.info("slow_query_threshold_updated", threshold_ms=threshold_ms)
    
    def set_sampling_rate(self, rate: float):
        """Set sampling rate (0.0-1.0)"""
        if not 0.0 <= rate <= 1.0:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")
        self._sampling_rate = rate
        logger.info("sampling_rate_updated", rate=rate)
    
    def clear(self):
        """Clear all metrics"""
        with self._lock:
            self._query_metrics.clear()
            self._pool_metrics.clear()
            self._slow_queries.clear()
            self._total_queries = 0
            self._total_slow_queries = 0
            self._total_errors = 0


# Global instance
_db_performance_monitor: Optional[DBPerformanceMonitor] = None
_monitor_lock = threading.Lock()


def get_db_performance_monitor() -> DBPerformanceMonitor:
    """Get global DB performance monitor instance"""
    global _db_performance_monitor
    
    if _db_performance_monitor is None:
        with _monitor_lock:
            if _db_performance_monitor is None:
                _db_performance_monitor = DBPerformanceMonitor()
    
    return _db_performance_monitor


def get_slow_queries(limit: int = 10) -> list[QueryMetric]:
    """Get recent slow queries"""
    monitor = get_db_performance_monitor()
    return monitor.get_slow_queries(limit)


def get_db_stats() -> dict[str, Any]:
    """Get database performance statistics"""
    monitor = get_db_performance_monitor()
    return monitor.get_stats()
