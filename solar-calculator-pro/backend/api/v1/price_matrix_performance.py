"""
API Endpoints for Price Matrix Performance Optimization

Provides endpoints for:
- Performance monitoring
- Cache management
- Index operations
- Optimization recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from solar-calculator-pro.backend.services.price_matrix_performance_service import (
    get_performance_service,
    PriceMatrixPerformanceService
)

router = APIRouter(prefix="/price-matrix-performance", tags=["Price Matrix Performance"])


# ============================================================================
# Request/Response Models
# ============================================================================

class PerformanceStatsResponse(BaseModel):
    """Performance statistics response"""
    cache_stats: Dict[str, Any]
    index_stats: Dict[str, Any]
    precomputed_queries: int
    total_operations: int
    avg_duration_ms: float
    cache_hit_rate: float
    top_queries: List[tuple]


class OptimizationRecommendationsResponse(BaseModel):
    """Optimization recommendations response"""
    recommendations: List[str]
    timestamp: str


class CacheWarmRequest(BaseModel):
    """Request to warm cache"""
    matrix_data: Dict[str, Any] = Field(..., description="Matrix data to cache")


class PrecomputeRequest(BaseModel):
    """Request to precompute queries"""
    matrix_data: Dict[str, Any] = Field(..., description="Matrix data")
    common_module_counts: List[int] = Field(..., description="Common module counts")
    common_storage_models: List[str] = Field(..., description="Common storage models")


class LookupRequest(BaseModel):
    """Request for optimized lookup"""
    module_count: int = Field(..., ge=1, description="Number of PV modules")
    storage_model: str = Field(..., description="Battery storage model")
    matrix_data: Optional[Dict[str, Any]] = Field(None, description="Optional matrix data")


class LookupResponse(BaseModel):
    """Response for optimized lookup"""
    price: Optional[float]
    cache_hit: bool
    duration_ms: float


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/stats", response_model=PerformanceStatsResponse)
async def get_performance_stats():
    """
    Get comprehensive performance statistics
    
    Returns:
        Performance statistics including cache, index, and operation metrics
    """
    try:
        service = get_performance_service()
        stats = service.get_performance_stats()
        
        return PerformanceStatsResponse(
            cache_stats=stats['cache_stats'],
            index_stats=stats['index_stats'],
            precomputed_queries=stats['precomputed_queries'],
            total_operations=stats['total_operations'],
            avg_duration_ms=stats['avg_duration_ms'],
            cache_hit_rate=stats['cache_hit_rate'],
            top_queries=stats['top_queries']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=OptimizationRecommendationsResponse)
async def get_optimization_recommendations():
    """
    Get optimization recommendations based on current metrics
    
    Returns:
        List of optimization recommendations
    """
    try:
        service = get_performance_service()
        recommendations = service.get_optimization_recommendations()
        
        from datetime import datetime
        return OptimizationRecommendationsResponse(
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/warm")
async def warm_cache(request: CacheWarmRequest):
    """
    Warm up cache with matrix data
    
    Args:
        request: Cache warm request with matrix data
    
    Returns:
        Success message
    """
    try:
        service = get_performance_service()
        service.warm_cache(request.matrix_data)
        
        return {
            "success": True,
            "message": "Cache warmed successfully",
            "entries_cached": len(request.matrix_data.get('cells', {}))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/invalidate")
async def invalidate_cache(matrix_id: Optional[str] = Query(None)):
    """
    Invalidate cache
    
    Args:
        matrix_id: Optional matrix ID to invalidate specific matrix
    
    Returns:
        Success message
    """
    try:
        service = get_performance_service()
        service.invalidate_cache(matrix_id)
        
        return {
            "success": True,
            "message": f"Cache invalidated{' for matrix ' + matrix_id if matrix_id else ' (all)'}",
            "matrix_id": matrix_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/precompute")
async def precompute_queries(request: PrecomputeRequest):
    """
    Precompute results for common queries
    
    Args:
        request: Precompute request with matrix data and common queries
    
    Returns:
        Success message with precomputed count
    """
    try:
        service = get_performance_service()
        service.precompute_common_queries(
            request.matrix_data,
            request.common_module_counts,
            request.common_storage_models
        )
        
        total_precomputed = (
            len(request.common_module_counts) *
            len(request.common_storage_models)
        )
        
        return {
            "success": True,
            "message": "Queries precomputed successfully",
            "precomputed_count": total_precomputed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup", response_model=LookupResponse)
async def optimized_lookup(request: LookupRequest):
    """
    Perform optimized price lookup
    
    Args:
        request: Lookup request with module count and storage model
    
    Returns:
        Price and performance metrics
    """
    try:
        import time
        service = get_performance_service()
        
        start_time = time.time()
        
        # Check cache first
        cache_key = f"price_{request.module_count}_{request.storage_model}"
        cached_price = service.cache.get(cache_key)
        cache_hit = cached_price is not None
        
        if cache_hit:
            price = cached_price
        else:
            price = service.optimize_lookup(
                request.module_count,
                request.storage_model,
                request.matrix_data
            )
        
        duration_ms = (time.time() - start_time) * 1000
        
        return LookupResponse(
            price=price,
            cache_hit=cache_hit,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/build")
async def build_index(matrix_data: Dict[str, Any]):
    """
    Build index for matrix data
    
    Args:
        matrix_data: Matrix data to index
    
    Returns:
        Index statistics
    """
    try:
        service = get_performance_service()
        service.index.build_index(matrix_data)
        
        stats = service.index.get_stats()
        
        return {
            "success": True,
            "message": "Index built successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/stats")
async def get_index_stats():
    """
    Get index statistics
    
    Returns:
        Index statistics
    """
    try:
        service = get_performance_service()
        stats = service.index.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics for all tiers
    
    Returns:
        Cache statistics
    """
    try:
        service = get_performance_service()
        stats = service.cache.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark")
async def run_benchmark(
    module_counts: List[int] = Query(..., description="Module counts to test"),
    storage_models: List[str] = Query(..., description="Storage models to test"),
    iterations: int = Query(100, ge=1, le=1000, description="Number of iterations")
):
    """
    Run performance benchmark
    
    Args:
        module_counts: List of module counts to test
        storage_models: List of storage models to test
        iterations: Number of iterations per combination
    
    Returns:
        Benchmark results
    """
    try:
        import time
        service = get_performance_service()
        
        results = {
            'total_lookups': 0,
            'successful_lookups': 0,
            'failed_lookups': 0,
            'total_time_ms': 0.0,
            'avg_time_ms': 0.0,
            'min_time_ms': float('inf'),
            'max_time_ms': 0.0,
            'lookups_per_second': 0.0
        }
        
        start_time = time.time()
        
        for _ in range(iterations):
            for module_count in module_counts:
                for storage_model in storage_models:
                    lookup_start = time.time()
                    
                    price = service.optimize_lookup(module_count, storage_model)
                    
                    lookup_time_ms = (time.time() - lookup_start) * 1000
                    
                    results['total_lookups'] += 1
                    results['total_time_ms'] += lookup_time_ms
                    results['min_time_ms'] = min(results['min_time_ms'], lookup_time_ms)
                    results['max_time_ms'] = max(results['max_time_ms'], lookup_time_ms)
                    
                    if price is not None:
                        results['successful_lookups'] += 1
                    else:
                        results['failed_lookups'] += 1
        
        total_time_s = time.time() - start_time
        
        if results['total_lookups'] > 0:
            results['avg_time_ms'] = results['total_time_ms'] / results['total_lookups']
            results['lookups_per_second'] = results['total_lookups'] / total_time_s
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/metrics")
async def clear_metrics():
    """
    Clear all performance metrics
    
    Returns:
        Success message
    """
    try:
        service = get_performance_service()
        service.metrics.clear()
        
        return {
            "success": True,
            "message": "Metrics cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
