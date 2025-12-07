"""
Demo: Price Matrix Performance Optimization

Demonstrates all optimization strategies:
- Multi-level caching
- Index structures
- Lazy loading
- Precomputation
- Performance monitoring
"""

import time
import random
from solar-calculator-pro.backend.services.price_matrix_performance_service import (
    get_performance_service,
    LRUCache,
    TieredCache,
    MatrixIndex,
    LazyMatrixLoader,
    QueryPrecomputer,
    track_performance
)


# ============================================================================
# Sample Data
# ============================================================================

def generate_sample_matrix(rows=50, cols=4):
    """Generate sample matrix data"""
    module_counts = list(range(10, 10 + rows))
    storage_models = ['5kWh', '10kWh', '15kWh', 'kein Speicher']
    
    cells = {}
    for row_idx, module_count in enumerate(module_counts):
        for col_idx, storage_model in enumerate(storage_models):
            # Generate realistic prices
            base_price = module_count * 800  # €800 per module
            storage_price = col_idx * 3000  # Storage adds cost
            price = base_price + storage_price
            
            cells[f"{row_idx}_{col_idx}"] = float(price)
    
    return {
        'rows': module_counts,
        'columns': storage_models,
        'cells': cells
    }


# ============================================================================
# Demo Functions
# ============================================================================

def demo_lru_cache():
    """Demo LRU cache"""
    print("\n" + "="*70)
    print("DEMO: LRU Cache")
    print("="*70)
    
    cache = LRUCache(max_size=5, default_ttl=60)
    
    # Set values
    print("\n1. Setting values...")
    for i in range(7):
        cache.set(f'key{i}', f'value{i}')
        print(f"   Set key{i} = value{i}")
    
    # Get values (some will be evicted)
    print("\n2. Getting values...")
    for i in range(7):
        value = cache.get(f'key{i}')
        status = "✓ Found" if value else "✗ Evicted"
        print(f"   Get key{i}: {status}")
    
    # Show stats
    print("\n3. Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demo_tiered_cache():
    """Demo tiered cache"""
    print("\n" + "="*70)
    print("DEMO: Tiered Cache")
    print("="*70)
    
    cache = TieredCache(l1_size=3, l2_size=10)
    
    # Set values
    print("\n1. Setting values in both tiers...")
    for i in range(5):
        cache.set(f'key{i}', f'value{i}')
        print(f"   Set key{i} = value{i}")
    
    # Clear L1
    print("\n2. Clearing L1 cache...")
    cache.l1_cache.clear()
    
    # Get values (should promote from L2 to L1)
    print("\n3. Getting values (promotes from L2 to L1)...")
    for i in range(3):
        value = cache.get(f'key{i}')
        print(f"   Get key{i}: {value}")
    
    # Show stats
    print("\n4. Cache Statistics:")
    stats = cache.get_stats()
    print(f"   L1: {stats['l1']}")
    print(f"   L2: {stats['l2']}")


def demo_matrix_index():
    """Demo matrix index"""
    print("\n" + "="*70)
    print("DEMO: Matrix Index")
    print("="*70)
    
    # Generate sample data
    matrix_data = generate_sample_matrix(rows=20, cols=4)
    
    # Build index
    print("\n1. Building index...")
    index = MatrixIndex()
    start = time.time()
    index.build_index(matrix_data)
    build_time = (time.time() - start) * 1000
    print(f"   Index built in {build_time:.2f}ms")
    
    # Show stats
    stats = index.get_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Unique module counts: {stats['unique_module_counts']}")
    print(f"   Unique storage models: {stats['unique_storage_models']}")
    
    # Fast lookup
    print("\n2. Fast O(1) lookup...")
    module_count = 20
    storage_model = '15kWh'
    start = time.time()
    entry = index.lookup(module_count, storage_model)
    lookup_time = (time.time() - start) * 1000
    print(f"   Lookup({module_count}, '{storage_model}'): €{entry.price:.2f}")
    print(f"   Lookup time: {lookup_time:.4f}ms")
    
    # Range query
    print("\n3. Range query...")
    entries = index.find_by_module_count_range(15, 25)
    print(f"   Found {len(entries)} entries for module counts 15-25")
    
    # Prefix search
    print("\n4. Prefix search...")
    entries = index.find_by_storage_model_prefix('1')
    print(f"   Found {len(entries)} entries for storage models starting with '1'")


def demo_lazy_loading():
    """Demo lazy loading"""
    print("\n" + "="*70)
    print("DEMO: Lazy Loading")
    print("="*70)
    
    loader = LazyMatrixLoader(chunk_size=100)
    
    # Define loader function
    def mock_loader(matrix_id, chunk_id):
        print(f"   Loading {matrix_id}/{chunk_id} from database...")
        time.sleep(0.1)  # Simulate database load
        return {'data': f'{matrix_id}_{chunk_id}', 'size': 100}
    
    # Load chunks
    print("\n1. Loading chunks...")
    chunk1 = loader.load_chunk('matrix1', 'chunk1', mock_loader)
    print(f"   Loaded: {chunk1}")
    
    # Second load (cached)
    print("\n2. Loading same chunk (cached)...")
    chunk1_cached = loader.load_chunk('matrix1', 'chunk1', mock_loader)
    print(f"   Loaded from cache: {chunk1_cached}")
    
    # Preload in background
    print("\n3. Preloading chunks in background...")
    loader.preload_chunks('matrix1', ['chunk2', 'chunk3'], mock_loader)
    print("   Preloading started...")
    time.sleep(0.3)  # Wait for background loading
    print("   Preloading complete!")


def demo_precomputation():
    """Demo query precomputation"""
    print("\n" + "="*70)
    print("DEMO: Query Precomputation")
    print("="*70)
    
    precomputer = QueryPrecomputer()
    precomputer.threshold = 3
    
    # Record queries
    print("\n1. Recording query frequency...")
    queries = ['query1', 'query1', 'query2', 'query1', 'query3', 'query1']
    for query in queries:
        precomputer.record_query(query)
        print(f"   Recorded: {query}")
    
    # Check if should precompute
    print("\n2. Checking precomputation threshold...")
    for query in ['query1', 'query2', 'query3']:
        should = precomputer.should_precompute(query)
        freq = precomputer.query_frequency[query]
        status = "✓ Should precompute" if should else "✗ Below threshold"
        print(f"   {query} (frequency: {freq}): {status}")
    
    # Precompute
    print("\n3. Precomputing query1...")
    def expensive_calculation():
        time.sleep(0.1)
        return 42
    
    result = precomputer.precompute('query1', expensive_calculation)
    print(f"   Precomputed result: {result}")
    
    # Get precomputed
    print("\n4. Getting precomputed result (instant)...")
    cached = precomputer.get_precomputed('query1')
    print(f"   Cached result: {cached}")
    
    # Top queries
    print("\n5. Top queries:")
    top = precomputer.get_top_queries(limit=3)
    for query, freq in top:
        print(f"   {query}: {freq} times")


def demo_performance_service():
    """Demo complete performance service"""
    print("\n" + "="*70)
    print("DEMO: Complete Performance Service")
    print("="*70)
    
    # Generate sample data
    matrix_data = generate_sample_matrix(rows=30, cols=4)
    
    # Get service
    service = get_performance_service()
    
    # Build index
    print("\n1. Building index...")
    service.index.build_index(matrix_data)
    print("   ✓ Index built")
    
    # Precompute common queries
    print("\n2. Precomputing common queries...")
    service.precompute_common_queries(
        matrix_data,
        common_module_counts=[20, 25, 30],
        common_storage_models=['10kWh', '15kWh']
    )
    print("   ✓ Queries precomputed")
    
    # Warm cache
    print("\n3. Warming cache...")
    service.warm_cache(matrix_data)
    print("   ✓ Cache warmed")
    
    # Perform lookups
    print("\n4. Performing optimized lookups...")
    test_queries = [
        (20, '10kWh'),
        (25, '15kWh'),
        (30, '10kWh'),
        (20, '10kWh'),  # Duplicate (cache hit)
    ]
    
    for module_count, storage_model in test_queries:
        start = time.time()
        price = service.optimize_lookup(module_count, storage_model)
        duration = (time.time() - start) * 1000
        print(f"   Lookup({module_count}, '{storage_model}'): €{price:.2f} ({duration:.4f}ms)")
    
    # Get statistics
    print("\n5. Performance Statistics:")
    stats = service.get_performance_stats()
    print(f"   Total operations: {stats['total_operations']}")
    print(f"   Average duration: {stats['avg_duration_ms']:.4f}ms")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"   Precomputed queries: {stats['precomputed_queries']}")
    
    # Get recommendations
    print("\n6. Optimization Recommendations:")
    recommendations = service.get_optimization_recommendations()
    for rec in recommendations:
        print(f"   • {rec}")


def demo_performance_comparison():
    """Demo performance comparison"""
    print("\n" + "="*70)
    print("DEMO: Performance Comparison")
    print("="*70)
    
    # Generate sample data
    matrix_data = generate_sample_matrix(rows=50, cols=4)
    
    # Simulate unoptimized lookup
    def unoptimized_lookup(module_count, storage_model):
        """Simulate slow database lookup"""
        time.sleep(0.01)  # Simulate 10ms database query
        rows = matrix_data['rows']
        columns = matrix_data['columns']
        cells = matrix_data['cells']
        
        try:
            row_idx = rows.index(module_count)
            col_idx = columns.index(storage_model)
            return cells.get(f"{row_idx}_{col_idx}")
        except ValueError:
            return None
    
    # Test unoptimized
    print("\n1. Testing UNOPTIMIZED lookups...")
    test_queries = [(20, '10kWh'), (25, '15kWh'), (30, '10kWh')] * 10
    
    start = time.time()
    for module_count, storage_model in test_queries:
        price = unoptimized_lookup(module_count, storage_model)
    unoptimized_time = time.time() - start
    
    print(f"   30 lookups: {unoptimized_time*1000:.2f}ms")
    print(f"   Average: {(unoptimized_time/30)*1000:.2f}ms per lookup")
    
    # Test optimized
    print("\n2. Testing OPTIMIZED lookups...")
    service = get_performance_service()
    service.warm_cache(matrix_data)
    
    start = time.time()
    for module_count, storage_model in test_queries:
        price = service.optimize_lookup(module_count, storage_model)
    optimized_time = time.time() - start
    
    print(f"   30 lookups: {optimized_time*1000:.2f}ms")
    print(f"   Average: {(optimized_time/30)*1000:.2f}ms per lookup")
    
    # Show improvement
    print("\n3. Performance Improvement:")
    improvement = unoptimized_time / optimized_time
    print(f"   Speedup: {improvement:.1f}x faster")
    print(f"   Time saved: {(unoptimized_time - optimized_time)*1000:.2f}ms")


def demo_decorator():
    """Demo performance tracking decorator"""
    print("\n" + "="*70)
    print("DEMO: Performance Tracking Decorator")
    print("="*70)
    
    @track_performance('expensive_operation')
    def expensive_operation(n):
        """Simulate expensive operation"""
        time.sleep(0.01 * n)
        return n * 2
    
    print("\n1. Calling tracked function...")
    for i in range(1, 4):
        result = expensive_operation(i)
        print(f"   expensive_operation({i}) = {result}")
    
    print("\n2. Viewing metrics...")
    service = get_performance_service()
    stats = service.get_performance_stats()
    
    # Find our operation
    for metric in service.metrics:
        if metric.operation == 'expensive_operation':
            print(f"   Duration: {metric.duration_ms:.2f}ms")


# ============================================================================
# Main Demo
# ============================================================================

def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("PRICE MATRIX PERFORMANCE OPTIMIZATION - COMPLETE DEMO")
    print("="*70)
    
    demos = [
        ("LRU Cache", demo_lru_cache),
        ("Tiered Cache", demo_tiered_cache),
        ("Matrix Index", demo_matrix_index),
        ("Lazy Loading", demo_lazy_loading),
        ("Query Precomputation", demo_precomputation),
        ("Performance Service", demo_performance_service),
        ("Performance Comparison", demo_performance_comparison),
        ("Performance Decorator", demo_decorator),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("• Multi-level caching provides 10-100x speedup")
    print("• Index structures enable O(1) lookups")
    print("• Lazy loading reduces memory usage")
    print("• Precomputation makes common queries instant")
    print("• Performance monitoring helps identify bottlenecks")
    print("\nFor more information, see:")
    print("• docs/PRICE_MATRIX_PERFORMANCE_GUIDE.md")
    print("• docs/PRICE_MATRIX_PERFORMANCE_QUICK_REFERENCE.md")


if __name__ == '__main__':
    main()
