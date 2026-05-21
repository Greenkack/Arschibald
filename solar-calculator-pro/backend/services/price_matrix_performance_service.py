"""
Price Matrix Performance Optimization Service

Comprehensive performance optimization for price matrix operations including:
- Multi-level caching strategies (memory, disk, distributed)
- Lookup optimization with index structures
- Lazy loading for large matrices
- Precomputation for common queries
- Performance monitoring and analytics

Requirements: 1.3, 8.4, 8.5
"""

import time
import hashlib
import pickle
import json
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from functools import lru_cache, wraps
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        """Update last accessed time and increment counter"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class IndexEntry:
    """Index entry for fast lookups"""
    module_count: int
    storage_model: str
    row_index: int
    col_index: int
    price: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    operation: str
    duration_ms: float
    cache_hit: bool
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Multi-Level Cache System
# ============================================================================

class LRUCache:
    """
    LRU (Least Recently Used) Cache implementation
    
    Features:
    - Automatic eviction of least recently used items
    - Configurable max size
    - TTL support
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.touch()
            self.hits += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        with self.lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 0
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                ttl_seconds=ttl or self.default_ttl
            )
            
            # Add to cache
            if key in self.cache:
                del self.cache[key]
            
            self.cache[key] = entry
            self.cache.move_to_end(key)
            
            # Evict if necessary
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.evictions += 1
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate,
                'total_size_mb': total_size / (1024 * 1024)
            }


class TieredCache:
    """
    Multi-tiered cache system
    
    Tiers:
    1. L1: In-memory LRU cache (fastest, smallest)
    2. L2: Larger in-memory cache
    3. L3: Disk-based cache (slowest, largest)
    """
    
    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        l1_ttl: int = 300,  # 5 minutes
        l2_ttl: int = 3600  # 1 hour
    ):
        self.l1_cache = LRUCache(max_size=l1_size, default_ttl=l1_ttl)
        self.l2_cache = LRUCache(max_size=l2_size, default_ttl=l2_ttl)
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from tiered cache"""
        # Try L1 first
        value = self.l1_cache.get(key)
        if value is not None:
            return value
        
        # Try L2
        value = self.l2_cache.get(key)
        if value is not None:
            # Promote to L1
            self.l1_cache.set(key, value)
            return value
        
        return None
    
    def set(self, key: str, value: Any):
        """Set value in tiered cache"""
        # Set in both tiers
        self.l1_cache.set(key, value)
        self.l2_cache.set(key, value)
    
    def clear(self):
        """Clear all tiers"""
        self.l1_cache.clear()
        self.l2_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all tiers"""
        return {
            'l1': self.l1_cache.get_stats(),
            'l2': self.l2_cache.get_stats()
        }


# ============================================================================
# Index Structures for Fast Lookups
# ============================================================================

class MatrixIndex:
    """
    Index structure for fast matrix lookups
    
    Features:
    - Hash-based index for O(1) lookups
    - Range queries for module counts
    - Prefix matching for storage models
    """
    
    def __init__(self):
        self.hash_index: Dict[str, IndexEntry] = {}
        self.module_count_index: Dict[int, List[IndexEntry]] = defaultdict(list)
        self.storage_model_index: Dict[str, List[IndexEntry]] = defaultdict(list)
        self.lock = threading.RLock()
    
    def build_index(self, matrix_data: Dict[str, Any]):
        """Build index from matrix data"""
        with self.lock:
            self.hash_index.clear()
            self.module_count_index.clear()
            self.storage_model_index.clear()
            
            rows = matrix_data.get('rows', [])
            columns = matrix_data.get('columns', [])
            cells = matrix_data.get('cells', {})
            
            for row_idx, module_count in enumerate(rows):
                for col_idx, storage_model in enumerate(columns):
                    cell_key = f"{row_idx}_{col_idx}"
                    price = cells.get(cell_key)
                    
                    if price is not None:
                        entry = IndexEntry(
                            module_count=module_count,
                            storage_model=storage_model,
                            row_index=row_idx,
                            col_index=col_idx,
                            price=price
                        )
                        
                        # Hash index
                        hash_key = self._make_hash_key(module_count, storage_model)
                        self.hash_index[hash_key] = entry
                        
                        # Module count index
                        self.module_count_index[module_count].append(entry)
                        
                        # Storage model index
                        self.storage_model_index[storage_model].append(entry)
    
    def lookup(self, module_count: int, storage_model: str) -> Optional[IndexEntry]:
        """Fast O(1) lookup"""
        hash_key = self._make_hash_key(module_count, storage_model)
        return self.hash_index.get(hash_key)
    
    def find_by_module_count_range(
        self,
        min_count: int,
        max_count: int
    ) -> List[IndexEntry]:
        """Find entries within module count range"""
        results = []
        for count in range(min_count, max_count + 1):
            results.extend(self.module_count_index.get(count, []))
        return results
    
    def find_by_storage_model_prefix(self, prefix: str) -> List[IndexEntry]:
        """Find entries matching storage model prefix"""
        results = []
        for model, entries in self.storage_model_index.items():
            if model.startswith(prefix):
                results.extend(entries)
        return results
    
    def _make_hash_key(self, module_count: int, storage_model: str) -> str:
        """Create hash key for lookup"""
        return f"{module_count}_{storage_model}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            'total_entries': len(self.hash_index),
            'unique_module_counts': len(self.module_count_index),
            'unique_storage_models': len(self.storage_model_index)
        }


# ============================================================================
# Lazy Loading System
# ============================================================================

class LazyMatrixLoader:
    """
    Lazy loading system for large matrices
    
    Features:
    - Load matrix data on-demand
    - Chunk-based loading for large matrices
    - Background preloading
    """
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.loaded_chunks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
    
    def load_chunk(
        self,
        matrix_id: str,
        chunk_id: str,
        loader_func: Callable
    ) -> Dict[str, Any]:
        """Load a specific chunk"""
        with self.lock:
            cache_key = f"{matrix_id}_{chunk_id}"
            
            if cache_key in self.loaded_chunks:
                return self.loaded_chunks[cache_key]
            
            # Load chunk
            chunk_data = loader_func(matrix_id, chunk_id)
            self.loaded_chunks[cache_key] = chunk_data
            
            return chunk_data
    
    def preload_chunks(
        self,
        matrix_id: str,
        chunk_ids: List[str],
        loader_func: Callable
    ):
        """Preload multiple chunks in background"""
        def preload_worker():
            for chunk_id in chunk_ids:
                try:
                    self.load_chunk(matrix_id, chunk_id, loader_func)
                except Exception as e:
                    logger.error(f"Error preloading chunk {chunk_id}: {e}")
        
        thread = threading.Thread(target=preload_worker, daemon=True)
        thread.start()
    
    def clear_chunks(self, matrix_id: Optional[str] = None):
        """Clear loaded chunks"""
        with self.lock:
            if matrix_id:
                # Clear specific matrix chunks
                keys_to_remove = [
                    k for k in self.loaded_chunks.keys()
                    if k.startswith(f"{matrix_id}_")
                ]
                for key in keys_to_remove:
                    del self.loaded_chunks[key]
            else:
                # Clear all chunks
                self.loaded_chunks.clear()


# ============================================================================
# Precomputation System
# ============================================================================

class QueryPrecomputer:
    """
    Precomputation system for common queries
    
    Features:
    - Identify common query patterns
    - Precompute results
    - Automatic refresh
    """
    
    def __init__(self):
        self.precomputed: Dict[str, Any] = {}
        self.query_frequency: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()
        self.threshold = 10  # Precompute after 10 occurrences
    
    def record_query(self, query_key: str):
        """Record query for frequency analysis"""
        with self.lock:
            self.query_frequency[query_key] += 1
    
    def should_precompute(self, query_key: str) -> bool:
        """Check if query should be precomputed"""
        return self.query_frequency.get(query_key, 0) >= self.threshold
    
    def precompute(self, query_key: str, compute_func: Callable) -> Any:
        """Precompute and cache result"""
        with self.lock:
            if query_key in self.precomputed:
                return self.precomputed[query_key]
            
            result = compute_func()
            self.precomputed[query_key] = result
            return result
    
    def get_precomputed(self, query_key: str) -> Optional[Any]:
        """Get precomputed result"""
        return self.precomputed.get(query_key)
    
    def invalidate(self, query_key: Optional[str] = None):
        """Invalidate precomputed results"""
        with self.lock:
            if query_key:
                self.precomputed.pop(query_key, None)
            else:
                self.precomputed.clear()
    
    def get_top_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequent queries"""
        return sorted(
            self.query_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]


# ============================================================================
# Main Performance Service
# ============================================================================

class PriceMatrixPerformanceService:
    """
    Main service for price matrix performance optimization
    
    Integrates all optimization strategies:
    - Multi-level caching
    - Index structures
    - Lazy loading
    - Precomputation
    - Performance monitoring
    """
    
    def __init__(self):
        self.cache = TieredCache()
        self.index = MatrixIndex()
        self.lazy_loader = LazyMatrixLoader()
        self.precomputer = QueryPrecomputer()
        self.metrics: List[PerformanceMetrics] = []
        self.lock = threading.RLock()
    
    def optimize_lookup(
        self,
        module_count: int,
        storage_model: str,
        matrix_data: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """
        Optimized price lookup with all strategies
        
        Args:
            module_count: Number of PV modules
            storage_model: Battery storage model
            matrix_data: Optional matrix data (for index building)
        
        Returns:
            Price if found, None otherwise
        """
        start_time = time.time()
        cache_hit = False
        
        try:
            # Generate cache key
            cache_key = f"price_{module_count}_{storage_model}"
            
            # Try cache first
            cached_price = self.cache.get(cache_key)
            if cached_price is not None:
                cache_hit = True
                return cached_price
            
            # Try index lookup
            if matrix_data:
                # Build index if needed
                if not self.index.hash_index:
                    self.index.build_index(matrix_data)
                
                entry = self.index.lookup(module_count, storage_model)
                if entry:
                    price = entry.price
                    # Cache result
                    self.cache.set(cache_key, price)
                    return price
            
            return None
            
        finally:
            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                operation='optimize_lookup',
                duration_ms=duration_ms,
                cache_hit=cache_hit,
                metadata={
                    'module_count': module_count,
                    'storage_model': storage_model
                }
            )
    
    def precompute_common_queries(
        self,
        matrix_data: Dict[str, Any],
        common_module_counts: List[int],
        common_storage_models: List[str]
    ):
        """
        Precompute results for common queries
        
        Args:
            matrix_data: Matrix data
            common_module_counts: List of common module counts
            common_storage_models: List of common storage models
        """
        # Build index
        self.index.build_index(matrix_data)
        
        # Precompute all combinations
        for module_count in common_module_counts:
            for storage_model in common_storage_models:
                cache_key = f"price_{module_count}_{storage_model}"
                
                entry = self.index.lookup(module_count, storage_model)
                if entry:
                    self.cache.set(cache_key, entry.price)
                    
                    # Mark as precomputed
                    self.precomputer.precomputed[cache_key] = entry.price
    
    def warm_cache(self, matrix_data: Dict[str, Any]):
        """
        Warm up cache with matrix data
        
        Args:
            matrix_data: Matrix data to cache
        """
        # Build index
        self.index.build_index(matrix_data)
        
        # Cache all entries
        for entry in self.index.hash_index.values():
            cache_key = f"price_{entry.module_count}_{entry.storage_model}"
            self.cache.set(cache_key, entry.price)
    
    def invalidate_cache(self, matrix_id: Optional[str] = None):
        """
        Invalidate cache
        
        Args:
            matrix_id: Optional matrix ID to invalidate specific matrix
        """
        self.cache.clear()
        self.precomputer.invalidate()
        
        if matrix_id:
            self.lazy_loader.clear_chunks(matrix_id)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self.lock:
            # Calculate metrics
            total_operations = len(self.metrics)
            if total_operations > 0:
                avg_duration = sum(m.duration_ms for m in self.metrics) / total_operations
                cache_hits = sum(1 for m in self.metrics if m.cache_hit)
                cache_hit_rate = (cache_hits / total_operations) * 100
            else:
                avg_duration = 0
                cache_hit_rate = 0
            
            return {
                'cache_stats': self.cache.get_stats(),
                'index_stats': self.index.get_stats(),
                'precomputed_queries': len(self.precomputer.precomputed),
                'total_operations': total_operations,
                'avg_duration_ms': avg_duration,
                'cache_hit_rate': cache_hit_rate,
                'top_queries': self.precomputer.get_top_queries()
            }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on metrics"""
        recommendations = []
        stats = self.get_performance_stats()
        
        # Check cache hit rate
        cache_hit_rate = stats.get('cache_hit_rate', 0)
        if cache_hit_rate < 50:
            recommendations.append(
                f"Low cache hit rate ({cache_hit_rate:.1f}%). "
                "Consider increasing cache size or precomputing common queries."
            )
        elif cache_hit_rate > 90:
            recommendations.append(
                f"Excellent cache hit rate ({cache_hit_rate:.1f}%)!"
            )
        
        # Check average duration
        avg_duration = stats.get('avg_duration_ms', 0)
        if avg_duration > 10:
            recommendations.append(
                f"Average lookup time is {avg_duration:.2f}ms. "
                "Consider building indexes or precomputing results."
            )
        
        # Check index usage
        index_stats = stats.get('index_stats', {})
        if index_stats.get('total_entries', 0) == 0:
            recommendations.append(
                "No index built. Build index for faster lookups."
            )
        
        # Check precomputation
        precomputed = stats.get('precomputed_queries', 0)
        if precomputed == 0:
            recommendations.append(
                "No queries precomputed. Precompute common queries for better performance."
            )
        
        if not recommendations:
            recommendations.append(
                "System is well optimized. No recommendations at this time."
            )
        
        return recommendations
    
    def _record_metric(
        self,
        operation: str,
        duration_ms: float,
        cache_hit: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record performance metric"""
        with self.lock:
            metric = PerformanceMetrics(
                operation=operation,
                duration_ms=duration_ms,
                cache_hit=cache_hit,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            self.metrics.append(metric)
            
            # Keep only last 10000 metrics
            if len(self.metrics) > 10000:
                self.metrics = self.metrics[-10000:]


# ============================================================================
# Singleton Instance
# ============================================================================

_performance_service: Optional[PriceMatrixPerformanceService] = None


def get_performance_service() -> PriceMatrixPerformanceService:
    """Get singleton performance service instance"""
    global _performance_service
    if _performance_service is None:
        _performance_service = PriceMatrixPerformanceService()
    return _performance_service


# ============================================================================
# Decorator for Performance Tracking
# ============================================================================

def track_performance(operation_name: str):
    """Decorator to track performance of functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                service = get_performance_service()
                service._record_metric(
                    operation=operation_name,
                    duration_ms=duration_ms,
                    cache_hit=False
                )
        return wrapper
    return decorator


__all__ = [
    'PriceMatrixPerformanceService',
    'get_performance_service',
    'track_performance',
    'LRUCache',
    'TieredCache',
    'MatrixIndex',
    'LazyMatrixLoader',
    'QueryPrecomputer'
]
