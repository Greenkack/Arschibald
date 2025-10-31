"""
Test script for all roof forms in the 3D visualization

Tests:
- Flachdach with Süd and Ost-West mounting
- Satteldach with various inclinations
- Walmdach, Pultdach, Zeltdach
- Correct geometry and colors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    build_scene,
    make_roof_flat,
    make_roof_gable,
    make_roof_hip,
    make_roof_pent,
    make_roof_pyramid,
    _roof_color_from_covering,
    ROOF_COLORS
)


def test_roof_colors():
    """Test that all roof covering types have correct colors"""
    print("\n" + "=" * 60)
    print("Testing Roof Colors")
    print("=" * 60)
    
    test_cases = [
        ("Ziegel", "#c96a2d"),
        ("Beton", "#9ea3a8"),
        ("Schiefer", "#3b3f44"),
        ("Eternit", "#7e8388"),
        ("Trapezblech", "#8e8f93"),
        ("Bitumen", "#4a4d52"),
        ("Unknown", "#b0b5ba"),  # Default
    ]
    
    for covering, expected_color in test_cases:
        color = _roof_color_from_covering(covering)
        assert color == expected_color, f"Color mismatch for {covering}: got {color}, expected {expected_color}"
        print(f"✓ {covering}: {color}")
    
    print("\n✅ All roof colors correct")
    return True


def test_flat_roof():
    """Test flat roof geometry"""
    print("\n" + "=" * 60)
    print("Testing Flat Roof (Flachdach)")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Test flat roof creation
    roof = make_roof_flat(dims.length_m, dims.width_m, dims.wall_height_m)
    assert roof is not None, "Flat roof creation failed"
    assert roof.n_points > 0, "Flat roof has no points"
    
    print(f"✓ Flat roof created with {roof.n_points} points and {roof.n_cells} cells")
    
    # Test with scene (default mounting is Süd)
    project_data = {
        "project_details": {
            "roof_type": "Flachdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 0,
            "roof_covering_type": "Bitumen"
        }
    }
    
    layout = LayoutConfig(mode="auto")
    plotter, panels = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Flachdach",
        module_quantity=20,
        layout_config=layout
    )
    
    assert plotter is not None, "Plotter creation failed for flat roof"
    assert len(panels["main"]) > 0, "No panels placed on flat roof"
    print(f"✓ Flat roof scene: {len(panels['main'])} panels placed")
    
    plotter.close()
    
    # Test place_panels_flat_roof directly for both mounting types
    from utils.pv3d import place_panels_flat_roof
    
    panels_south = place_panels_flat_roof(
        roof_length=dims.length_m,
        roof_width=dims.width_m,
        module_quantity=20,
        mounting_type="south",
        base_z=dims.wall_height_m
    )
    assert len(panels_south) > 0, "No panels with south mounting"
    print(f"✓ Süd mounting: {len(panels_south)} panels placed")
    
    panels_ew = place_panels_flat_roof(
        roof_length=dims.length_m,
        roof_width=dims.width_m,
        module_quantity=20,
        mounting_type="east-west",
        base_z=dims.wall_height_m
    )
    assert len(panels_ew) > 0, "No panels with east-west mounting"
    print(f"✓ Ost-West mounting: {len(panels_ew)} panels placed")
    
    print("\n✅ Flat roof tests passed")
    return True


def test_gable_roof():
    """Test gable roof (Satteldach) with various inclinations"""
    print("\n" + "=" * 60)
    print("Testing Gable Roof (Satteldach)")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    inclinations = [15, 30, 45, 60]
    
    for incl in inclinations:
        roof = make_roof_gable(dims.length_m, dims.width_m, dims.wall_height_m, incl)
        assert roof is not None, f"Gable roof creation failed for {incl}°"
        assert roof.n_points > 0, f"Gable roof has no points for {incl}°"
        print(f"✓ Gable roof {incl}°: {roof.n_points} points, {roof.n_cells} cells")
    
    # Test with scene
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    
    layout = LayoutConfig(mode="auto")
    plotter, panels = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=20,
        layout_config=layout
    )
    
    assert plotter is not None, "Plotter creation failed for gable roof"
    assert len(panels["main"]) > 0, "No panels placed on gable roof"
    print(f"✓ Gable roof scene: {len(panels['main'])} panels placed")
    
    plotter.close()
    
    print("\n✅ Gable roof tests passed")
    return True


def test_hip_roof():
    """Test hip roof (Walmdach)"""
    print("\n" + "=" * 60)
    print("Testing Hip Roof (Walmdach)")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    roof = make_roof_hip(dims.length_m, dims.width_m, dims.wall_height_m, 30)
    assert roof is not None, "Hip roof creation failed"
    assert roof.n_points > 0, "Hip roof has no points"
    print(f"✓ Hip roof created with {roof.n_points} points and {roof.n_cells} cells")
    
    # Test with scene
    project_data = {
        "project_details": {
            "roof_type": "Walmdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Beton"
        }
    }
    
    layout = LayoutConfig(mode="auto")
    plotter, panels = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Walmdach",
        module_quantity=20,
        layout_config=layout
    )
    
    assert plotter is not None, "Plotter creation failed for hip roof"
    assert len(panels["main"]) > 0, "No panels placed on hip roof"
    print(f"✓ Hip roof scene: {len(panels['main'])} panels placed")
    
    plotter.close()
    
    print("\n✅ Hip roof tests passed")
    return True


def test_pent_roof():
    """Test pent roof (Pultdach)"""
    print("\n" + "=" * 60)
    print("Testing Pent Roof (Pultdach)")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    roof = make_roof_pent(dims.length_m, dims.width_m, dims.wall_height_m, 15)
    assert roof is not None, "Pent roof creation failed"
    assert roof.n_points > 0, "Pent roof has no points"
    print(f"✓ Pent roof created with {roof.n_points} points and {roof.n_cells} cells")
    
    # Test with scene
    project_data = {
        "project_details": {
            "roof_type": "Pultdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 15,
            "roof_covering_type": "Schiefer"
        }
    }
    
    layout = LayoutConfig(mode="auto")
    plotter, panels = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Pultdach",
        module_quantity=20,
        layout_config=layout
    )
    
    assert plotter is not None, "Plotter creation failed for pent roof"
    assert len(panels["main"]) > 0, "No panels placed on pent roof"
    print(f"✓ Pent roof scene: {len(panels['main'])} panels placed")
    
    plotter.close()
    
    print("\n✅ Pent roof tests passed")
    return True


def test_pyramid_roof():
    """Test pyramid roof (Zeltdach)"""
    print("\n" + "=" * 60)
    print("Testing Pyramid Roof (Zeltdach)")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    roof = make_roof_pyramid(dims.length_m, dims.width_m, dims.wall_height_m, 30)
    assert roof is not None, "Pyramid roof creation failed"
    assert roof.n_points > 0, "Pyramid roof has no points"
    print(f"✓ Pyramid roof created with {roof.n_points} points and {roof.n_cells} cells")
    
    # Test with scene
    project_data = {
        "project_details": {
            "roof_type": "Zeltdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Eternit"
        }
    }
    
    layout = LayoutConfig(mode="auto")
    plotter, panels = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Zeltdach",
        module_quantity=20,
        layout_config=layout
    )
    
    assert plotter is not None, "Plotter creation failed for pyramid roof"
    assert len(panels["main"]) > 0, "No panels placed on pyramid roof"
    print(f"✓ Pyramid roof scene: {len(panels['main'])} panels placed")
    
    plotter.close()
    
    print("\n✅ Pyramid roof tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING ALL ROOF FORMS")
    print("=" * 60)
    
    tests = [
        test_roof_colors,
        test_flat_roof,
        test_gable_roof,
        test_hip_roof,
        test_pent_roof,
        test_pyramid_roof
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
        print("\n✅ ALL ROOF FORM TESTS PASSED!")
        exit(0)
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        exit(1)
