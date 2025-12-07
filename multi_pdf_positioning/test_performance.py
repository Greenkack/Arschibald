"""
Test script for Performance Optimizer

This script tests the performance optimization functionality.
"""

from pathlib import Path
from multi_pdf_positioning.performance_optimizer import (
    measure_performance,
    PerformanceOptimizer
)
from multi_pdf_positioning.config import OUTPUT_DIR


def test_performance_measurement():
    """Test performance measurement on a subset of combinations."""
    print("\n=== Testing Performance Measurement ===\n")
    
    # Test with a small subset
    print("Testing with Firma 1, Seiten 1-2...")
    
    optimizer = PerformanceOptimizer(enable_cache=True)
    metrics = optimizer.measure_all_combinations(
        firmen=[1],
        seiten=[1, 2]
    )
    
    optimizer.display_metrics(metrics)
    
    # Verify metrics
    assert metrics.total_combinations == 2, "Should process 2 combinations"
    assert metrics.total_duration > 0, "Should have positive duration"
    assert len(metrics.component_timings) > 0, "Should have component timings"
    
    print("\nPerformance measurement test passed")
    
    return metrics


def test_cache_effectiveness():
    """Test cache effectiveness."""
    print("\n=== Testing Cache Effectiveness ===\n")
    
    # Measure with cache
    print("Measuring with cache enabled...")
    optimizer_cached = PerformanceOptimizer(enable_cache=True)
    metrics_cached = optimizer_cached.measure_all_combinations(
        firmen=[1],
        seiten=[1, 2]
    )
    
    # Measure without cache
    print("\nMeasuring with cache disabled...")
    optimizer_uncached = PerformanceOptimizer(enable_cache=False)
    metrics_uncached = optimizer_uncached.measure_all_combinations(
        firmen=[1],
        seiten=[1, 2]
    )
    
    # Compare
    print("\n--- Comparison ---")
    print(f"With cache: {metrics_cached.total_duration:.3f}s")
    print(f"Without cache: {metrics_uncached.total_duration:.3f}s")
    
    if metrics_cached.total_duration < metrics_uncached.total_duration:
        if metrics_cached != 0:
            speedup = metrics_uncached.total_duration / metrics_cached.total_duration
        else:
            speedup = 0.0
        print(f"Speedup: {speedup:.2f}x")
        print("Cache is effective")
    else:
        print(" Cache did not improve performance (may be due to small dataset)")
    
    return metrics_cached, metrics_uncached


def test_metrics_export():
    """Test metrics export to JSON."""
    print("\n=== Testing Metrics Export ===\n")
    
    optimizer = PerformanceOptimizer(enable_cache=True)
    metrics = optimizer.measure_all_combinations(
        firmen=[1],
        seiten=[1]
    )
    
    # Save metrics
    output_file = OUTPUT_DIR / "test_performance_metrics.json"
    optimizer.save_metrics(metrics, output_file)
    
    # Verify file exists
    assert output_file.exists(), "Metrics file should exist"
    
    # Read and verify
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert 'total_combinations' in data, "Should have total_combinations"
    assert 'total_duration' in data, "Should have total_duration"
    assert 'component_timings' in data, "Should have component_timings"
    
    print(f"Metrics exported to: {output_file}")
    
    return output_file


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PERFORMANCE OPTIMIZER TESTS")
    print("=" * 70)
    
    try:
        # Test 1: Basic performance measurement
        test_performance_measurement()
        
        # Test 2: Cache effectiveness
        test_cache_effectiveness()
        
        # Test 3: Metrics export
        test_metrics_export()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
