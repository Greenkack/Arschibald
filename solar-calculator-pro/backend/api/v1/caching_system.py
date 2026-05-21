"""
Caching System
Task 188: Multi-level caching with invalidation and statistics
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import asyncio
from functools import wraps
import time


router = APIRouter(prefix="/cache", tags=["Caching System"])


class CacheLevel(str, Enum):
    L1_MEMORY = "l1_memory"
    L2_LOCAL = "l2_local"
    L3_DISTRIBUTED = "l3_distributed"


class CachePolicy(str, Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live


class CacheEntry(BaseModel):
    """Cache entry model"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime
    size_bytes: int = 0
    level: CacheLevel = CacheLevel.L1_MEMORY
    tags: List[str] = []


class CacheStats(BaseModel):
    """Cache statistics"""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    hit_rate: float
    eviction_count: int
    avg_access_time_ms: float


class CacheConfig(BaseModel):
    """Cache configuration"""
    level: CacheLevel
    max_entries: int = 1000
    max_size_bytes: int = 100 * 1024 * 1024  # 100MB
    default_ttl_seconds: int = 3600
    policy: CachePolicy = CachePolicy.LRU
    enabled: bool = True


class MultiLevelCache:
    """Multi-level cache implementation"""
    
    def __init__(self):
        self.caches: Dict[CacheLevel, Dict[str, CacheEntry]] = {
            CacheLevel.L1_MEMORY: {},
            CacheLevel.L2_LOCAL: {},
            CacheLevel.L3_DISTRIBUTED: {}
        }
        self.configs: Dict[CacheLevel, CacheConfig] = {
            CacheLevel.L1_MEMORY: CacheConfig(
                level=CacheLevel.L1_MEMORY,
                max_entries=500,
                max_size_bytes=50 * 1024 * 1024,
                default_ttl_seconds=300
            ),
            CacheLevel.L2_LOCAL: CacheConfig(
                level=CacheLevel.L2_LOCAL,
                max_entries=2000,
                max_size_bytes=200 * 1024 * 1024,
                default_ttl_seconds=1800
            ),
            CacheLevel.L3_DISTRIBUTED: CacheConfig(
                level=CacheLevel.L3_DISTRIBUTED,
                max_entries=10000,
                max_size_bytes=1024 * 1024 * 1024,
                default_ttl_seconds=3600
            )
        }
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "access_times": []
        }
        
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace"""
        return f"{namespace}:{key}"
        
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(json.dumps(value).encode())
        except:
            return 0
            
    def _should_evict(self, level: CacheLevel) -> bool:
        """Check if eviction is needed"""
        config = self.configs[level]
        cache = self.caches[level]
        
        if len(cache) >= config.max_entries:
            return True
            
        total_size = sum(e.size_bytes for e in cache.values())
        if total_size >= config.max_size_bytes:
            return True
            
        return False
        
    def _evict(self, level: CacheLevel):
        """Evict entries based on policy"""
        config = self.configs[level]
        cache = self.caches[level]
        
        if not cache:
            return
            
        if config.policy == CachePolicy.LRU:
            # Remove least recently used
            oldest = min(cache.values(), key=lambda x: x.last_accessed)
            del cache[oldest.key]
            
        elif config.policy == CachePolicy.LFU:
            # Remove least frequently used
            least_used = min(cache.values(), key=lambda x: x.access_count)
            del cache[least_used.key]
            
        elif config.policy == CachePolicy.FIFO:
            # Remove first added
            first = min(cache.values(), key=lambda x: x.created_at)
            del cache[first.key]
            
        elif config.policy == CachePolicy.TTL:
            # Remove expired entries
            now = datetime.now()
            expired = [k for k, v in cache.items() if v.expires_at and v.expires_at < now]
            for key in expired:
                del cache[key]
                
        self.stats["evictions"] += 1
        
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache (checks all levels)"""
        start_time = time.time()
        full_key = self._generate_key(key, namespace)
        
        # Check each level
        for level in CacheLevel:
            if not self.configs[level].enabled:
                continue
                
            cache = self.caches[level]
            if full_key in cache:
                entry = cache[full_key]
                
                # Check expiration
                if entry.expires_at and entry.expires_at < datetime.now():
                    del cache[full_key]
                    continue
                    
                # Update access stats
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                self.stats["hits"] += 1
                self.stats["access_times"].append((time.time() - start_time) * 1000)
                
                # Promote to higher level if found in lower level
                if level != CacheLevel.L1_MEMORY:
                    self.set(key, entry.value, namespace=namespace, level=CacheLevel.L1_MEMORY)
                    
                return entry.value
                
        self.stats["misses"] += 1
        self.stats["access_times"].append((time.time() - start_time) * 1000)
        return None
        
    def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl_seconds: Optional[int] = None,
        level: CacheLevel = CacheLevel.L1_MEMORY,
        tags: List[str] = []
    ):
        """Set value in cache"""
        if not self.configs[level].enabled:
            return
            
        full_key = self._generate_key(key, namespace)
        config = self.configs[level]
        
        # Evict if needed
        while self._should_evict(level):
            self._evict(level)
            
        # Calculate TTL
        ttl = ttl_seconds or config.default_ttl_seconds
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        # Create entry
        entry = CacheEntry(
            key=full_key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_accessed=datetime.now(),
            size_bytes=self._estimate_size(value),
            level=level,
            tags=tags
        )
        
        self.caches[level][full_key] = entry
        
    def delete(self, key: str, namespace: str = "default"):
        """Delete from all cache levels"""
        full_key = self._generate_key(key, namespace)
        
        for level in CacheLevel:
            if full_key in self.caches[level]:
                del self.caches[level][full_key]
                
    def invalidate_by_tag(self, tag: str):
        """Invalidate all entries with a specific tag"""
        for level in CacheLevel:
            keys_to_delete = [
                k for k, v in self.caches[level].items()
                if tag in v.tags
            ]
            for key in keys_to_delete:
                del self.caches[level][key]
                
    def invalidate_by_pattern(self, pattern: str):
        """Invalidate entries matching a pattern"""
        for level in CacheLevel:
            keys_to_delete = [
                k for k in self.caches[level].keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                del self.caches[level][key]
                
    def clear(self, level: Optional[CacheLevel] = None):
        """Clear cache (specific level or all)"""
        if level:
            self.caches[level].clear()
        else:
            for lvl in CacheLevel:
                self.caches[lvl].clear()
                
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        total_entries = sum(len(c) for c in self.caches.values())
        total_size = sum(
            sum(e.size_bytes for e in c.values())
            for c in self.caches.values()
        )
        
        total_accesses = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_accesses if total_accesses > 0 else 0
        
        avg_time = (
            sum(self.stats["access_times"][-100:]) / len(self.stats["access_times"][-100:])
            if self.stats["access_times"] else 0
        )
        
        return CacheStats(
            total_entries=total_entries,
            total_size_bytes=total_size,
            hit_count=self.stats["hits"],
            miss_count=self.stats["misses"],
            hit_rate=hit_rate,
            eviction_count=self.stats["evictions"],
            avg_access_time_ms=avg_time
        )
        
    def warm(self, data: Dict[str, Any], namespace: str = "default", level: CacheLevel = CacheLevel.L1_MEMORY):
        """Warm cache with pre-loaded data"""
        for key, value in data.items():
            self.set(key, value, namespace=namespace, level=level)


# Global cache instance
cache = MultiLevelCache()


# Cache decorator
def cached(
    namespace: str = "default",
    ttl_seconds: int = 300,
    level: CacheLevel = CacheLevel.L1_MEMORY,
    tags: List[str] = []
):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()[:32]
            
            # Try to get from cache
            cached_value = cache.get(cache_key, namespace)
            if cached_value is not None:
                return cached_value
                
            # Execute function and cache result
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            cache.set(cache_key, result, namespace=namespace, ttl_seconds=ttl_seconds, level=level, tags=tags)
            
            return result
        return wrapper
    return decorator


# API Endpoints

@router.get("/stats", response_model=CacheStats)
async def get_cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


@router.get("/stats/{level}")
async def get_level_stats(level: CacheLevel):
    """Get statistics for a specific cache level"""
    level_cache = cache.caches[level]
    config = cache.configs[level]
    
    return {
        "level": level.value,
        "entries": len(level_cache),
        "max_entries": config.max_entries,
        "size_bytes": sum(e.size_bytes for e in level_cache.values()),
        "max_size_bytes": config.max_size_bytes,
        "policy": config.policy.value,
        "default_ttl": config.default_ttl_seconds,
        "enabled": config.enabled
    }


@router.get("/entries")
async def list_cache_entries(
    level: Optional[CacheLevel] = None,
    namespace: Optional[str] = None,
    limit: int = 100
):
    """List cache entries"""
    entries = []
    
    levels = [level] if level else list(CacheLevel)
    
    for lvl in levels:
        for key, entry in cache.caches[lvl].items():
            if namespace and not key.startswith(f"{namespace}:"):
                continue
            entries.append({
                "key": key,
                "level": entry.level.value,
                "size_bytes": entry.size_bytes,
                "access_count": entry.access_count,
                "created_at": entry.created_at.isoformat(),
                "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                "tags": entry.tags
            })
            
    return sorted(entries, key=lambda x: x["access_count"], reverse=True)[:limit]


@router.post("/set")
async def set_cache_value(
    key: str,
    value: Any,
    namespace: str = "default",
    ttl_seconds: Optional[int] = None,
    level: CacheLevel = CacheLevel.L1_MEMORY,
    tags: List[str] = []
):
    """Set a cache value"""
    cache.set(key, value, namespace=namespace, ttl_seconds=ttl_seconds, level=level, tags=tags)
    return {"status": "cached", "key": key}


@router.get("/get/{key}")
async def get_cache_value(key: str, namespace: str = "default"):
    """Get a cache value"""
    value = cache.get(key, namespace)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found in cache")
    return {"key": key, "value": value}


@router.delete("/delete/{key}")
async def delete_cache_value(key: str, namespace: str = "default"):
    """Delete a cache value"""
    cache.delete(key, namespace)
    return {"status": "deleted", "key": key}


@router.post("/invalidate/tag/{tag}")
async def invalidate_by_tag(tag: str):
    """Invalidate all entries with a tag"""
    cache.invalidate_by_tag(tag)
    return {"status": "invalidated", "tag": tag}


@router.post("/invalidate/pattern")
async def invalidate_by_pattern(pattern: str):
    """Invalidate entries matching a pattern"""
    cache.invalidate_by_pattern(pattern)
    return {"status": "invalidated", "pattern": pattern}


@router.post("/clear")
async def clear_cache(level: Optional[CacheLevel] = None):
    """Clear cache"""
    cache.clear(level)
    return {"status": "cleared", "level": level.value if level else "all"}


@router.post("/warm")
async def warm_cache(
    data: Dict[str, Any],
    namespace: str = "default",
    level: CacheLevel = CacheLevel.L1_MEMORY
):
    """Warm cache with data"""
    cache.warm(data, namespace=namespace, level=level)
    return {"status": "warmed", "entries": len(data)}


@router.get("/config/{level}", response_model=CacheConfig)
async def get_cache_config(level: CacheLevel):
    """Get cache configuration"""
    return cache.configs[level]


@router.put("/config/{level}")
async def update_cache_config(level: CacheLevel, config: CacheConfig):
    """Update cache configuration"""
    config.level = level
    cache.configs[level] = config
    return {"status": "updated", "config": config}


@router.get("/health")
async def cache_health():
    """Get cache health status"""
    stats = cache.get_stats()
    
    health_status = "healthy"
    issues = []
    
    # Check hit rate
    if stats.hit_rate < 0.5 and stats.hit_count + stats.miss_count > 100:
        health_status = "degraded"
        issues.append("Low cache hit rate")
        
    # Check for high eviction rate
    if stats.eviction_count > stats.total_entries * 2:
        health_status = "degraded"
        issues.append("High eviction rate - consider increasing cache size")
        
    return {
        "status": health_status,
        "issues": issues,
        "stats": stats
    }
