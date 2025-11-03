"""
Test script for error handling and robustness

Tests:
- Missing project_data
- Invalid dimensions
- Extreme values (very large/small)
- Error messages and fallbacks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    build_scene,
    render_image_bytes,
    _safe_get_orientation,
    _safe_get_roof_inclination_deg,
    _safe_get_roof_covering
)


def test_missing_project_data():
    """Test with missing or empty project_data"""
    print("\n" + "=" * 60)
    print("Testing Missing Project Data")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    layout = LayoutConfig(mode="auto")
    
    # Test with empty dict
    try:
        plotter, panels = build_scene(
            project_data={},
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout
        )
        assert plotter is not None, "Plotter should be created even with empty project_data"
        print("✓ Empty project_data handled gracefully")
        plotter.close()
    except Exception as e:
        print(f"✗ Empty project_data failed: {e}")
        raise
    
    # Test with None values
    try:
        plotter, panels = build_scene(
            project_data={"project_details": None},
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout
        )
        assert plotter is not None, "Plotter should be created with None project_details"
        print("✓ None project_details handled gracefully")
        plotter.close()
    except Exception as e:
        print(f"✗ None project_details failed: {e}")
        raise
    
    print("\n✅ Missing project_data tests passed")
    return True


def test_safe_get_functions():
    """Test the safe_get helper functions with various inputs"""
    print("\n" + "=" * 60)
    print("Testing Safe Get Functions")
    print("=" * 60)
    
    # Test _safe_get_orientation
    test_cases_orientation = [
        ({}, "Süd"),  # Empty dict
        ({"project_details": {}}, "Süd"),  # Empty project_details
        ({"project_details": {"roof_orientation": "Ost"}}, "Ost"),  # Valid
        ({"project_details": {"roof_orientation": None}}, "Süd"),  # None value
        ({"roof_orientation": "West"}, "West"),  # Direct key
    ]
    
    for project_data, expected in test_cases_orientation:
        result = _safe_get_orientation(project_data)
        assert result == expected, f"Orientation mismatch: got {result}, expected {expected}"
    print("✓ _safe_get_orientation handles all cases correctly")
    
    # Test _safe_get_roof_inclination_deg
    test_cases_inclination = [
        ({}, 35.0),  # Empty dict (default fallback)
        ({"project_details": {"roof_inclination_deg": 45}}, 45.0),  # Valid int
        ({"project_details": {"roof_inclination_deg": "25"}}, 25.0),  # String
        ({"project_details": {"roof_inclination_deg": None}}, 35.0),  # None (fallback)
        ({"roof_inclination_deg": 15.5}, 15.5),  # Direct key
    ]
    
    for project_data, expected in test_cases_inclination:
        result = _safe_get_roof_inclination_deg(project_data)
        assert result == expected, f"Inclination mismatch: got {result}, expected {expected}"
    print("✓ _safe_get_roof_inclination_deg handles all cases correctly")
    
    # Test _safe_get_roof_covering
    test_cases_covering = [
        ({}, "default"),  # Empty dict (default fallback)
        ({"project_details": {"roof_covering_type": "Beton"}}, "Beton"),  # Valid
        ({"project_details": {"roof_covering_type": None}}, "default"),  # None (fallback)
        ({"roof_covering_type": "Schiefer"}, "Schiefer"),  # Direct key
    ]
    
    for project_data, expected in test_cases_covering:
        result = _safe_get_roof_covering(project_data)
        assert result == expected, f"Covering mismatch: got {result}, expected {expected}"
    print("✓ _safe_get_roof_covering handles all cases correctly")
    
    print("\n✅ Safe get function tests passed")
    return True


def test_invalid_dimensions():
    """Test with invalid or edge-case dimensions"""
    print("\n" + "=" * 60)
    print("Testing Invalid Dimensions")
    print("=" * 60)
    
    project_data = {
        "project_details": {
            "roof_type": "Flachdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 0,
            "roof_covering_type": "Bitumen"
        }
    }
    layout = LayoutConfig(mode="auto")
    
    # Test with very small dimensions
    try:
        dims_small = BuildingDims(length_m=1.0, width_m=1.0, wall_height_m=1.0)
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims_small,
            roof_type="Flachdach",
            module_quantity=5,
            layout_config=layout
        )
        assert plotter is not None, "Should handle very small dimensions"
        print(f"✓ Very small dimensions (1x1x1m): {len(panels['main'])} panels placed")
        plotter.close()
    except Exception as e:
        print(f"✗ Very small dimensions failed: {e}")
        raise
    
    # Test with zero module quantity
    try:
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=0,
            layout_config=layout
        )
        assert plotter is not None, "Should handle zero modules"
        assert len(panels['main']) == 0, "Should have no panels with quantity 0"
        print("✓ Zero module quantity handled correctly")
        plotter.close()
    except Exception as e:
        print(f"✗ Zero module quantity failed: {e}")
        raise
    
    # Test with negative module quantity (should be handled gracefully)
    try:
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=-10,
            layout_config=layout
        )
        assert plotter is not None, "Should handle negative module quantity"
        assert len(panels['main']) == 0, "Should have no panels with negative quantity"
        print("✓ Negative module quantity handled correctly")
        plotter.close()
    except Exception as e:
        print(f"✗ Negative module quantity failed: {e}")
        raise
    
    print("\n✅ Invalid dimension tests passed")
    return True


def test_extreme_values():
    """Test with extreme values (very large/small)"""
    print("\n" + "=" * 60)
    print("Testing Extreme Values")
    print("=" * 60)
    
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    layout = LayoutConfig(mode="auto")
    
    # Test with very large building
    try:
        dims_large = BuildingDims(length_m=50.0, width_m=30.0, wall_height_m=15.0)
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims_large,
            roof_type="Satteldach",
            module_quantity=100,
            layout_config=layout
        )
        assert plotter is not None, "Should handle very large building"
        print(f"✓ Very large building (50x30x15m): {len(panels['main'])} panels placed")
        plotter.close()
    except Exception as e:
        print(f"✗ Very large building failed: {e}")
        raise
    
    # Test with extreme roof inclination
    try:
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        project_data_steep = {
            "project_details": {
                "roof_type": "Satteldach",
                "roof_orientation": "Süd",
                "roof_inclination_deg": 85,  # Very steep
                "roof_covering_type": "Ziegel"
            }
        }
        plotter, panels = build_scene(
            project_data=project_data_steep,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=layout
        )
        assert plotter is not None, "Should handle extreme roof inclination"
        print(f"✓ Extreme roof inclination (85°): {len(panels['main'])} panels placed")
        plotter.close()
    except Exception as e:
        print(f"✗ Extreme roof inclination failed: {e}")
        raise
    
    # Test with very many modules requested
    try:
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=1000,  # Way more than fits
            layout_config=layout
        )
        assert plotter is not None, "Should handle excessive module quantity"
        total = len(panels['main']) + len(panels.get('garage', [])) + len(panels.get('facade', []))
        assert total < 1000, "Should not place more modules than physically possible"
        print(f"✓ Excessive module quantity (1000 requested): {total} panels placed")
        plotter.close()
    except Exception as e:
        print(f"✗ Excessive module quantity failed: {e}")
        raise
    
    print("\n✅ Extreme value tests passed")
    return True


def test_render_error_handling():
    """Test error handling in render functions"""
    print("\n" + "=" * 60)
    print("Testing Render Error Handling")
    print("=" * 60)
    
    # Test render_image_bytes with minimal data
    try:
        dims = BuildingDims(length_m=5.0, width_m=3.0, wall_height_m=3.0)
        layout = LayoutConfig(mode="auto")
        
        png_bytes = render_image_bytes(
            project_data={},
            dims=dims,
            roof_type="Flachdach",
            module_quantity=0,
            layout_config=layout
        )
        
        assert png_bytes is not None, "render_image_bytes should not return None"
        assert len(png_bytes) > 0, "render_image_bytes should return valid PNG"
        print(f"✓ render_image_bytes with minimal data: {len(png_bytes)} bytes")
    except Exception as e:
        print(f"✗ render_image_bytes failed: {e}")
        raise
    
    # Test with invalid roof type (should use fallback)
    try:
        plotter, panels = build_scene(
            project_data={"project_details": {"roof_type": "InvalidType"}},
            dims=dims,
            roof_type="InvalidType",
            module_quantity=10,
            layout_config=layout
        )
        assert plotter is not None, "Should handle invalid roof type with fallback"
        print("✓ Invalid roof type handled with fallback")
        plotter.close()
    except Exception as e:
        print(f"✗ Invalid roof type failed: {e}")
        raise
    
    print("\n✅ Render error handling tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING AND ROBUSTNESS")
    print("=" * 60)
    
    tests = [
        test_missing_project_data,
        test_safe_get_functions,
        test_invalid_dimensions,
        test_extreme_values,
        test_render_error_handling
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
        print("\n✅ ALL ERROR HANDLING TESTS PASSED!")
        print("\nThe system is robust and handles:")
        print("  - Missing or invalid project data")
        print("  - Invalid dimensions and extreme values")
        print("  - Edge cases with zero or negative quantities")
        print("  - Graceful fallbacks for all error scenarios")
        exit(0)
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        exit(1)
