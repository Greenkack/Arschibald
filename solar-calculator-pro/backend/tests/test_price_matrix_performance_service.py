"""
Tests for Price Matrix Performance Service

Tests all optimization strategies:
- Multi-level caching
- Index structures
- Lazy loading
- Precomputation
- Performance monitoring
"""

import pytest
import time
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.price_matrix_performance_service import (
    LRUCache,
    TieredCache,
    MatrixIndex,
    LazyMatrixLoader,
    QueryPrecomputer,
    PriceMatrixPerformanceService,
    get_performance_service,
    track_performance,
    CacheEntry,
    IndexEntry
)


# ============================================================================
# Test Data
# ============================================================================

@pytest.fixture
def sample_matrix_data():
    """Sample matrix data for testing"""
    return {
        'rows': [10, 15, 20, 25, 30],
        'columns': ['5kWh', '10kWh', '15kWh', 'kein Speicher'],
        'cells': {
            '0_0': 15000.00,
            '0_1': 18000.00,
            '0_2': 21000.00,
            '0_3': 12000.00,
            '1_0': 18000.00,
            '1_1': 21000.00,
            '1_2': 24000.00,
            '1_3': 15000.00,
            '2_0': 21000.00,
            '2_1': 24000.00,
            '2_2': 27000.00,
            '2_3': 18000.00,
            '3_0': 24000.00,
            '3_1': 27000.00,
            '3_2': 30000.00,
            '3_3': 21000.00,
            '4_0': 27000.00,
            '4_1': 30000.00,
            '4_2': 33000.00,
            '4_3': 24000.00
        }
    }


# ============================================================================
# LRU Cache Tests
# ============================================================================

class TestLRUCache:
    """Test LRU Cache implementation"""
    
    def test_basic_operations(self):
        """Test basic get/set operations"""
        cache = LRUCache(max_size=3)
        
        # Set values
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Get values
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'
        assert cache.get('key4') is None
    
    def test_lru_eviction(self):
        """Test LRU eviction policy"""
        cache = LRUCache(max_size=2)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        # Access key1 to make it most recently used
        cache.get('key1')
        
        # Add key3, should evict key2
        cache.set('key3', 'value3')
        
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') is None  # Evicted
        assert cache.get('key3') == 'value3'
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        cache = LRUCache(max_size=10, default_ttl=1)  # 1 second TTL
        
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('key1') is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = LRUCache(max_size=10)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        cache.get('key1')  # Hit
        cache.get('key3')  # Miss
        
        stats = cache.get_stats()
        assert stats['size'] == 2
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0


# ============================================================================
# Tiered Cache Tests
# ============================================================================

class TestTieredCache:
    """Test tiered cache system"""
    
    def test_tier_promotion(self):
        """Test promotion from L2 to L1"""
        cache = TieredCache(l1_size=2, l2_size=5)
        
        # Set in both tiers
        cache.set('key1', 'value1')
        
        # Clear L1
        cache.l1_cache.clear()
        
        # Get should promote from L2 to L1
        value = cache.get('key1')
        assert value == 'value1'
        assert cache.l1_cache.get('key1') == 'value1'
    
    def test_tier_stats(self):
        """Test statistics for all tiers"""
        cache = TieredCache()
        
        cache.set('key1', 'value1')
        cache.get('key1')
        
        stats = cache.get_stats()
        assert 'l1' in stats
        assert 'l2' in stats
        assert stats['l1']['size'] == 1
        assert stats['l2']['size'] == 1


# ============================================================================
# Matrix Index Tests
# ============================================================================

class TestMatrixIndex:
    """Test matrix index structure"""
    
    def test_build_index(self, sample_matrix_data):
        """Test index building"""
        index = MatrixIndex()
        index.build_index(sample_matrix_data)
        
        stats = index.get_stats()
        assert stats['total_entries'] == 20
        assert stats['unique_module_counts'] == 5
        assert stats['unique_storage_models'] == 4
    
    def test_fast_lookup(self, sample_matrix_data):
        """Test O(1) lookup"""
        index = MatrixIndex()
        index.build_index(sample_matrix_data)
        
        entry = index.lookup(20, '15kWh')
        assert entry is not None
        assert entry.price == 27000.00
        assert entry.module_count == 20
        assert entry.storage_model == '15kWh'
    
    def test_range_query(self, sample_matrix_data):
        """Test module count range query"""
        index = MatrixIndex()
        index.build_index(sample_matrix_data)
        
        entries = index.find_by_module_count_range(15, 25)
        assert len(entries) == 12  # 3 module counts × 4 storage models
    
    def test_prefix_search(self, sample_matrix_data):
        """Test storage model prefix search"""
        index = MatrixIndex()
        index.build_index(sample_matrix_data)
        
        entries = index.find_by_storage_model_prefix('1')
        assert len(entries) == 10  # '10kWh' and '15kWh'


# ============================================================================
# Lazy Loader Tests
# ============================================================================

class TestLazyMatrixLoader:
    """Test lazy loading system"""
    
    def test_chunk_loading(self):
        """Test chunk loading"""
        loader = LazyMatrixLoader(chunk_size=100)
        
        def mock_loader(matrix_id, chunk_id):
            return {'data': f'{matrix_id}_{chunk_id}'}
        
        chunk = loader.load_chunk('matrix1', 'chunk1', mock_loader)
        assert chunk['data'] == 'matrix1_chunk1'
        
        # Second load should use cache
        chunk2 = loader.load_chunk('matrix1', 'chunk1', mock_loader)
        assert chunk2 == chunk
    
    def test_chunk_clearing(self):
        """Test chunk clearing"""
        loader = LazyMatrixLoader()
        
        def mock_loader(matrix_id, chunk_id):
            return {'data': f'{matrix_id}_{chunk_id}'}
        
        loader.load_chunk('matrix1', 'chunk1', mock_loader)
        loader.load_chunk('matrix2', 'chunk1', mock_loader)
        
        # Clear specific matrix
        loader.clear_chunks('matrix1')
        assert 'matrix1_chunk1' not in loader.loaded_chunks
        assert 'matrix2_chunk1' in loader.loaded_chunks


# ============================================================================
# Precomputer Tests
# ============================================================================

class TestQueryPrecomputer:
    """Test query precomputation"""
    
    def test_frequency_tracking(self):
        """Test query frequency tracking"""
        precomputer = QueryPrecomputer()
        precomputer.threshold = 3
        
        precomputer.record_query('query1')
        precomputer.record_query('query1')
        assert not precomputer.should_precompute('query1')
        
        precomputer.record_query('query1')
        assert precomputer.should_precompute('query1')
    
    def test_precomputation(self):
        """Test result precomputation"""
        precomputer = QueryPrecomputer()
        
        def compute_func():
            return 42
        
        result = precomputer.precompute('query1', compute_func)
        assert result == 42
        
        # Should use cached result
        cached = precomputer.get_precomputed('query1')
        assert cached == 42
    
    def test_invalidation(self):
        """Test cache invalidation"""
        precomputer = QueryPrecomputer()
        
        precomputer.precomputed['query1'] = 42
        precomputer.precomputed['query2'] = 43
        
        # Invalidate specific query
        precomputer.invalidate('query1')
        assert 'query1' not in precomputer.precomputed
        assert 'query2' in precomputer.precomputed
        
        # Invalidate all
        precomputer.invalidate()
        assert len(precomputer.precomputed) == 0
    
    def test_top_queries(self):
        """Test top queries retrieval"""
        precomputer = QueryPrecomputer()
        
        precomputer.record_query('query1')
        precomputer.record_query('query1')
        precomputer.record_query('query2')
        precomputer.record_query('query3')
        precomputer.record_query('query3')
        precomputer.record_query('query3')
        
        top = precomputer.get_top_queries(limit=2)
        assert len(top) == 2
        assert top[0][0] == 'query3'  # Most frequent
        assert top[0][1] == 3


# ============================================================================
# Performance Service Tests
# ============================================================================

class TestPriceMatrixPerformanceService:
    """Test main performance service"""
    
    def test_optimized_lookup(self, sample_matrix_data):
        """Test optimized lookup with all strategies"""
        service = PriceMatrixPerformanceService()
        
        # First lookup (cache miss, builds index)
        price1 = service.optimize_lookup(20, '15kWh', sample_matrix_data)
        assert price1 == 27000.00
        
        # Second lookup (cache hit)
        price2 = service.optimize_lookup(20, '15kWh')
        assert price2 == 27000.00
        
        stats = service.get_performance_stats()
        assert stats['total_operations'] == 2
        assert stats['cache_hit_rate'] == 50.0  # 1 hit, 1 miss
    
    def test_cache_warming(self, sample_matrix_data):
        """Test cache warming"""
        service = PriceMatrixPerformanceService()
        
        service.warm_cache(sample_matrix_data)
        
        # All lookups should be cache hits
        price1 = service.optimize_lookup(20, '15kWh')
        price2 = service.optimize_lookup(25, '10kWh')
        
        assert price1 == 27000.00
        assert price2 == 27000.00
        
        stats = service.get_performance_stats()
        assert stats['cache_hit_rate'] == 100.0
    
    def test_precompute_common_queries(self, sample_matrix_data):
        """Test precomputation of common queries"""
        service = PriceMatrixPerformanceService()
        
        common_counts = [20, 25]
        common_models = ['10kWh', '15kWh']
        
        service.precompute_common_queries(
            sample_matrix_data,
            common_counts,
            common_models
        )
        
        # All precomputed queries should be cache hits
        price1 = service.optimize_lookup(20, '10kWh')
        price2 = service.optimize_lookup(25, '15kWh')
        
        assert price1 == 24000.00
        assert price2 == 30000.00
        
        stats = service.get_performance_stats()
        assert stats['cache_hit_rate'] == 100.0
        assert stats['precomputed_queries'] >= 4
    
    def test_cache_invalidation(self, sample_matrix_data):
        """Test cache invalidation"""
        service = PriceMatrixPerformanceService()
        
        service.warm_cache(sample_matrix_data)
        
        # Invalidate cache
        service.invalidate_cache()
        
        stats = service.get_performance_stats()
        cache_stats = stats['cache_stats']
        assert cache_stats['l1']['size'] == 0
        assert cache_stats['l2']['size'] == 0
    
    def test_performance_stats(self, sample_matrix_data):
        """Test performance statistics"""
        service = PriceMatrixPerformanceService()
        
        # Perform some lookups
        service.optimize_lookup(20, '15kWh', sample_matrix_data)
        service.optimize_lookup(20, '15kWh')  # Cache hit
        service.optimize_lookup(25, '10kWh', sample_matrix_data)
        
        stats = service.get_performance_stats()
        
        assert 'cache_stats' in stats
        assert 'index_stats' in stats
        assert 'total_operations' in stats
        assert 'avg_duration_ms' in stats
        assert 'cache_hit_rate' in stats
        assert stats['total_operations'] == 3
    
    def test_optimization_recommendations(self, sample_matrix_data):
        """Test optimization recommendations"""
        service = PriceMatrixPerformanceService()
        
        # Perform lookups without optimization
        for _ in range(10):
            service.optimize_lookup(20, '15kWh', sample_matrix_data)
        
        recommendations = service.get_optimization_recommendations()
        assert len(recommendations) > 0
        assert isinstance(recommendations[0], str)


# ============================================================================
# Decorator Tests
# ============================================================================

class TestPerformanceDecorator:
    """Test performance tracking decorator"""
    
    def test_decorator(self):
        """Test performance tracking decorator"""
        service = get_performance_service()
        initial_count = len(service.metrics)
        
        @track_performance('test_operation')
        def test_function():
            time.sleep(0.01)
            return 42
        
        result = test_function()
        assert result == 42
        assert len(service.metrics) > initial_count


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_complete_optimization_workflow(self, sample_matrix_data):
        """Test complete optimization workflow"""
        service = PriceMatrixPerformanceService()
        
        # Step 1: Build index
        service.index.build_index(sample_matrix_data)
        
        # Step 2: Precompute common queries
        service.precompute_common_queries(
            sample_matrix_data,
            [20, 25],
            ['10kWh', '15kWh']
        )
        
        # Step 3: Warm cache
        service.warm_cache(sample_matrix_data)
        
        # Step 4: Perform lookups
        prices = []
        for module_count in [20, 25, 30]:
            for storage_model in ['10kWh', '15kWh']:
                price = service.optimize_lookup(module_count, storage_model)
                if price:
                    prices.append(price)
        
        # Verify results
        assert len(prices) == 6
        assert all(price > 0 for price in prices)
        
        # Check performance
        stats = service.get_performance_stats()
        assert stats['cache_hit_rate'] == 100.0  # All should be cache hits
        assert stats['avg_duration_ms'] < 1.0  # Should be very fast
        
        # Get recommendations
        recommendations = service.get_optimization_recommendations()
        assert any('Excellent' in r or 'well optimized' in r for r in recommendations)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
