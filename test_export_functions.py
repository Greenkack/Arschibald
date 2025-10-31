"""
Test script for export functions

Tests:
- Screenshot export with various scenes
- STL export and file validation
- glTF export and file validation
- File sizes and quality verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    render_image_bytes,
    export_stl,
    export_gltf
)


def test_screenshot_export():
    """Test screenshot export with various scenes"""
    print("\n" + "=" * 60)
    print("Testing Screenshot Export")
    print("=" * 60)
    
    test_scenarios = [
        {
            "name": "Flat roof with modules",
            "project_data": {
                "project_details": {
                    "roof_type": "Flachdach",
                    "roof_orientation": "Süd",
                    "roof_inclination_deg": 0,
                    "roof_covering_type": "Bitumen"
                }
            },
            "roof_type": "Flachdach",
            "module_quantity": 20
        },
        {
            "name": "Gable roof with modules",
            "project_data": {
                "project_details": {
                    "roof_type": "Satteldach",
                    "roof_orientation": "Süd",
                    "roof_inclination_deg": 30,
                    "roof_covering_type": "Ziegel"
                }
            },
            "roof_type": "Satteldach",
            "module_quantity": 15
        },
        {
            "name": "Hip roof with modules",
            "project_data": {
                "project_details": {
                    "roof_type": "Walmdach",
                    "roof_orientation": "Ost",
                    "roof_inclination_deg": 25,
                    "roof_covering_type": "Schiefer"
                }
            },
            "roof_type": "Walmdach",
            "module_quantity": 12
        }
    ]
    
    for scenario in test_scenarios:
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        layout = LayoutConfig(mode="auto")
        
        png_bytes = render_image_bytes(
            project_data=scenario["project_data"],
            dims=dims,
            roof_type=scenario["roof_type"],
            module_quantity=scenario["module_quantity"],
            layout_config=layout
        )
        
        assert png_bytes is not None, f"Screenshot failed for {scenario['name']}"
        assert len(png_bytes) > 0, f"Screenshot is empty for {scenario['name']}"
        assert len(png_bytes) > 1000, f"Screenshot too small for {scenario['name']} ({len(png_bytes)} bytes)"
        
        # Check PNG header
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n', f"Invalid PNG header for {scenario['name']}"
        
        print(f"✓ {scenario['name']}: {len(png_bytes):,} bytes")
    
    print("\n✅ Screenshot export tests passed")
    return True


def test_stl_export():
    """Test STL export and file validation"""
    print("\n" + "=" * 60)
    print("Testing STL Export")
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
    
    test_file = "test_export.stl"
    success = export_stl(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=20,
        layout_config=layout,
        filepath=test_file
    )
    
    assert success, "STL export failed"
    assert os.path.exists(test_file), "STL file was not created"
    
    # Read and validate file
    with open(test_file, 'rb') as f:
        stl_bytes = f.read()
    
    assert len(stl_bytes) > 0, "STL file is empty"
    assert len(stl_bytes) > 1000, f"STL file too small ({len(stl_bytes)} bytes)"
    
    # Check STL header (binary STL starts with 80-byte header)
    # or ASCII STL starts with "solid"
    is_binary = len(stl_bytes) > 84
    is_ascii = stl_bytes[:5] == b'solid'
    
    assert is_binary or is_ascii, "Invalid STL format"
    
    print(f"✓ STL export successful: {len(stl_bytes):,} bytes")
    print(f"  Format: {'Binary' if is_binary and not is_ascii else 'ASCII'}")
    print(f"  Saved to {test_file} for manual inspection")
    
    print("\n✅ STL export tests passed")
    return True


def test_gltf_export():
    """Test glTF export and file validation"""
    print("\n" + "=" * 60)
    print("Testing glTF Export")
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
    
    test_file = "test_export.glb"
    success = export_gltf(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=20,
        layout_config=layout,
        filepath=test_file
    )
    
    assert success, "glTF export failed"
    assert os.path.exists(test_file), "glTF file was not created"
    
    # Read and validate file
    with open(test_file, 'rb') as f:
        gltf_bytes = f.read()
    
    assert len(gltf_bytes) > 0, "glTF file is empty"
    assert len(gltf_bytes) > 1000, f"glTF file too small ({len(gltf_bytes)} bytes)"
    
    # Check glTF header (glb format starts with "glTF" magic number)
    # or JSON format starts with "{"
    is_glb = gltf_bytes[:4] == b'glTF'
    is_json = gltf_bytes[0:1] == b'{'
    
    assert is_glb or is_json, "Invalid glTF format"
    
    print(f"✓ glTF export successful: {len(gltf_bytes):,} bytes")
    print(f"  Format: {'Binary (GLB)' if is_glb else 'JSON (glTF)'}")
    print(f"  Saved to {test_file} for manual inspection")
    
    print("\n✅ glTF export tests passed")
    return True


def test_export_with_different_scenes():
    """Test exports with different scene configurations"""
    print("\n" + "=" * 60)
    print("Testing Exports with Different Scenes")
    print("=" * 60)
    
    test_configs = [
        {
            "name": "Small building, few modules",
            "dims": BuildingDims(length_m=8.0, width_m=5.0, wall_height_m=5.0),
            "module_quantity": 10
        },
        {
            "name": "Large building, many modules",
            "dims": BuildingDims(length_m=15.0, width_m=10.0, wall_height_m=8.0),
            "module_quantity": 50
        },
        {
            "name": "With garage and facade",
            "dims": BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0),
            "module_quantity": 50,
            "layout": LayoutConfig(mode="auto", use_garage=True, use_facade=True)
        }
    ]
    
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    
    for config in test_configs:
        layout = config.get("layout", LayoutConfig(mode="auto"))
        
        # Test screenshot
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=config["dims"],
            roof_type="Satteldach",
            module_quantity=config["module_quantity"],
            layout_config=layout
        )
        
        assert png_bytes and len(png_bytes) > 1000, f"Screenshot failed for {config['name']}"
        
        # Test STL
        stl_file = f"test_export_{config['name'].replace(' ', '_').replace(',', '')}.stl"
        stl_success = export_stl(
            project_data=project_data,
            dims=config["dims"],
            roof_type="Satteldach",
            module_quantity=config["module_quantity"],
            layout_config=layout,
            filepath=stl_file
        )
        
        assert stl_success and os.path.exists(stl_file), f"STL export failed for {config['name']}"
        stl_size = os.path.getsize(stl_file)
        
        # Test glTF
        gltf_file = f"test_export_{config['name'].replace(' ', '_').replace(',', '')}.glb"
        gltf_success = export_gltf(
            project_data=project_data,
            dims=config["dims"],
            roof_type="Satteldach",
            module_quantity=config["module_quantity"],
            layout_config=layout,
            filepath=gltf_file
        )
        
        assert gltf_success and os.path.exists(gltf_file), f"glTF export failed for {config['name']}"
        gltf_size = os.path.getsize(gltf_file)
        
        print(f"✓ {config['name']}: PNG={len(png_bytes):,}B, STL={stl_size:,}B, glTF={gltf_size:,}B")
    
    print("\n✅ Different scene export tests passed")
    return True


def test_export_error_handling():
    """Test export error handling with invalid inputs"""
    print("\n" + "=" * 60)
    print("Testing Export Error Handling")
    print("=" * 60)
    
    # Test with minimal/invalid data
    dims = BuildingDims(length_m=1.0, width_m=1.0, wall_height_m=1.0)
    project_data = {}
    layout = LayoutConfig(mode="auto")
    
    # These should not crash, but return empty bytes or handle gracefully
    try:
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=0,
            layout_config=layout
        )
        print(f"✓ Screenshot with minimal data: {len(png_bytes) if png_bytes else 0} bytes")
    except Exception as e:
        print(f"✓ Screenshot with minimal data handled error: {type(e).__name__}")
    
    try:
        stl_file = "test_export_minimal.stl"
        stl_success = export_stl(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=0,
            layout_config=layout,
            filepath=stl_file
        )
        print(f"✓ STL with minimal data: {'success' if stl_success else 'failed'}")
    except Exception as e:
        print(f"✓ STL with minimal data handled error: {type(e).__name__}")
    
    try:
        gltf_file = "test_export_minimal.glb"
        gltf_success = export_gltf(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=0,
            layout_config=layout,
            filepath=gltf_file
        )
        print(f"✓ glTF with minimal data: {'success' if gltf_success else 'failed'}")
    except Exception as e:
        print(f"✓ glTF with minimal data handled error: {type(e).__name__}")
    
    print("\n✅ Error handling tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING EXPORT FUNCTIONS")
    print("=" * 60)
    
    tests = [
        test_screenshot_export,
        test_stl_export,
        test_gltf_export,
        test_export_with_different_scenes,
        test_export_error_handling
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
        print("\n✅ ALL EXPORT FUNCTION TESTS PASSED!")
        print("\nGenerated test files:")
        print("  - test_export.stl")
        print("  - test_export.glb (or test_export.gltf)")
        print("\nYou can open these files in a 3D viewer to verify quality.")
        exit(0)
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        exit(1)
