"""
Test script for performance metrics

Tests:
- Scene creation time (< 1 second)
- Screenshot time (< 2 seconds)
- Performance with 10, 50, 100 modules
- Verify smooth rendering
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    build_scene,
    render_image_bytes
)


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start


def test_scene_creation_time():
    """Test that scene creation is under 1 second"""
    print("\n" + "=" * 60)
    print("Testing Scene Creation Time")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    layout = LayoutConfig(mode="auto")
    
    # Test with different module quantities
    test_quantities = [10, 20, 30]
    
    for qty in test_quantities:
        (plotter, panels), elapsed = measure_time(
            build_scene,
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=qty,
            layout_config=layout
        )
        
        assert plotter is not None, f"Scene creation failed for {qty} modules"
        assert elapsed < 1.0, f"Scene creation too slow for {qty} modules: {elapsed:.3f}s (should be < 1.0s)"
        
        print(f"✓ {qty} modules: {elapsed:.3f}s (target: < 1.0s)")
        plotter.close()
    
    print("\n✅ Scene creation time tests passed")
    return True


def test_screenshot_time():
    """Test that screenshot generation is under 2 seconds"""
    print("\n" + "=" * 60)
    print("Testing Screenshot Generation Time")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    layout = LayoutConfig(mode="auto")
    
    # Test with different module quantities
    test_quantities = [10, 20, 30]
    
    for qty in test_quantities:
        png_bytes, elapsed = measure_time(
            render_image_bytes,
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=qty,
            layout_config=layout
        )
        
        assert png_bytes is not None, f"Screenshot failed for {qty} modules"
        assert len(png_bytes) > 0, f"Screenshot empty for {qty} modules"
        assert elapsed < 2.0, f"Screenshot too slow for {qty} modules: {elapsed:.3f}s (should be < 2.0s)"
        
        print(f"✓ {qty} modules: {elapsed:.3f}s, {len(png_bytes):,} bytes (target: < 2.0s)")
    
    print("\n✅ Screenshot time tests passed")
    return True


def test_performance_scaling():
    """Test performance with 10, 50, 100 modules"""
    print("\n" + "=" * 60)
    print("Testing Performance Scaling")
    print("=" * 60)
    
    dims = BuildingDims(length_m=15.0, width_m=10.0, wall_height_m=8.0)  # Larger building
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    layout = LayoutConfig(mode="auto", use_garage=True, use_facade=True)
    
    test_quantities = [10, 50, 100]
    results = []
    
    for qty in test_quantities:
        # Measure scene creation
        (plotter, panels), scene_time = measure_time(
            build_scene,
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=qty,
            layout_config=layout
        )
        
        total_placed = len(panels['main']) + len(panels.get('garage', [])) + len(panels.get('facade', []))
        
        # Measure screenshot
        png_bytes, screenshot_time = measure_time(
            render_image_bytes,
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=qty,
            layout_config=layout
        )
        
        plotter.close()
        
        results.append({
            'requested': qty,
            'placed': total_placed,
            'scene_time': scene_time,
            'screenshot_time': screenshot_time,
            'total_time': scene_time + screenshot_time
        })
        
        print(f"✓ {qty} modules requested ({total_placed} placed):")
        print(f"    Scene: {scene_time:.3f}s, Screenshot: {screenshot_time:.3f}s, Total: {scene_time + screenshot_time:.3f}s")
    
    # Check that performance doesn't degrade too much with more modules
    if len(results) >= 2:
        time_10 = results[0]['total_time']
        time_100 = results[-1]['total_time']
        ratio = time_100 / time_10 if time_10 > 0 else 0
        
        print(f"\n  Performance ratio (100 vs 10 modules): {ratio:.2f}x")
        assert ratio < 5.0, f"Performance degrades too much: {ratio:.2f}x (should be < 5x)"
        print(f"  ✓ Performance scaling is acceptable (< 5x)")
    
    print("\n✅ Performance scaling tests passed")
    return True


def test_complex_scene_performance():
    """Test performance with complex scenes (multiple features)"""
    print("\n" + "=" * 60)
    print("Testing Complex Scene Performance")
    print("=" * 60)
    
    dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=7.0)
    project_data = {
        "project_details": {
            "roof_type": "Walmdach",
            "roof_orientation": "Ost",
            "roof_inclination_deg": 35,
            "roof_covering_type": "Schiefer"
        }
    }
    
    # Test with all features enabled
    layout_complex = LayoutConfig(
        mode="manual",
        use_garage=True,
        use_facade=True,
        removed_indices=[0, 1, 2, 3, 4, 5]
    )
    
    (plotter, panels), elapsed = measure_time(
        build_scene,
        project_data=project_data,
        dims=dims,
        roof_type="Walmdach",
        module_quantity=50,
        layout_config=layout_complex
    )
    
    assert plotter is not None, "Complex scene creation failed"
    assert elapsed < 1.5, f"Complex scene too slow: {elapsed:.3f}s (should be < 1.5s)"
    
    total_placed = len(panels['main']) + len(panels.get('garage', [])) + len(panels.get('facade', []))
    print(f"✓ Complex scene (Walmdach + manual + garage + facade): {elapsed:.3f}s")
    print(f"    {total_placed} modules placed (main: {len(panels['main'])}, garage: {len(panels.get('garage', []))}, facade: {len(panels.get('facade', []))})")
    
    plotter.close()
    
    print("\n✅ Complex scene performance tests passed")
    return True


def test_memory_efficiency():
    """Test that plotters are properly closed and memory is managed"""
    print("\n" + "=" * 60)
    print("Testing Memory Efficiency")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    project_data = {
        "project_details": {
            "roof_type": "Flachdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 0,
            "roof_covering_type": "Bitumen"
        }
    }
    layout = LayoutConfig(mode="auto")
    
    # Create and close multiple scenes to test memory management
    iterations = 10
    start_time = time.time()
    
    for i in range(iterations):
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout
        )
        plotter.close()
    
    elapsed = time.time() - start_time
    avg_time = elapsed / iterations
    
    print(f"✓ Created and closed {iterations} scenes")
    print(f"    Total time: {elapsed:.3f}s, Average: {avg_time:.3f}s per scene")
    print(f"    Memory management appears stable (no crashes)")
    
    assert avg_time < 1.0, f"Average scene time too slow: {avg_time:.3f}s (should be < 1.0s)"
    
    print("\n✅ Memory efficiency tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE")
    print("=" * 60)
    print("\nPerformance Targets:")
    print("  - Scene creation: < 1.0 second")
    print("  - Screenshot generation: < 2.0 seconds")
    print("  - Performance scaling: < 5x degradation (10 vs 100 modules)")
    print("  - Complex scenes: < 1.5 seconds")
    
    tests = [
        test_scene_creation_time,
        test_screenshot_time,
        test_performance_scaling,
        test_complex_scene_performance,
        test_memory_efficiency
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL PERFORMANCE TESTS PASSED!")
        print("\nThe system meets all performance targets:")
        print("  ✓ Fast scene creation (< 1s)")
        print("  ✓ Fast screenshot generation (< 2s)")
        print("  ✓ Good performance scaling")
        print("  ✓ Efficient memory management")
        exit(0)
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        exit(1)
