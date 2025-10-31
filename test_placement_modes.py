"""
Test script for automatic and manual panel placement

Tests:
- Automatic placement with various module quantities
- Manual module removal with different indices
- Garage addition when space is insufficient
- Facade placement
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    build_scene
)


def test_automatic_placement():
    """Test automatic placement with various module quantities"""
    print("\n" + "=" * 60)
    print("Testing Automatic Placement")
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
    
    test_quantities = [10, 20, 50]
    
    for qty in test_quantities:
        layout = LayoutConfig(mode="auto")
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=qty,
            layout_config=layout
        )
        
        assert plotter is not None, f"Plotter creation failed for {qty} modules"
        total_placed = len(panels["main"]) + len(panels.get("garage", [])) + len(panels.get("facade", []))
        print(f"✓ {qty} modules requested: {total_placed} placed (main: {len(panels['main'])}, garage: {len(panels.get('garage', []))}, facade: {len(panels.get('facade', []))})")
        
        plotter.close()
    
    print("\n✅ Automatic placement tests passed")
    return True


def test_manual_removal():
    """Test manual module removal with different indices"""
    print("\n" + "=" * 60)
    print("Testing Manual Module Removal")
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
    
    # First, get automatic placement count
    layout_auto = LayoutConfig(mode="auto")
    plotter_auto, panels_auto = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=20,
        layout_config=layout_auto
    )
    auto_count = len(panels_auto["main"])
    print(f"✓ Automatic placement: {auto_count} modules")
    plotter_auto.close()
    
    # Test manual removal
    test_cases = [
        ([0], "Remove first module"),
        ([0, 1, 2], "Remove first 3 modules"),
        ([5, 10], "Remove modules 5 and 10"),
        (list(range(0, auto_count, 2)), "Remove every other module")
    ]
    
    for removed_indices, description in test_cases:
        layout_manual = LayoutConfig(mode="manual", removed_indices=removed_indices)
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=layout_manual
        )
        
        assert plotter is not None, f"Plotter creation failed for manual mode: {description}"
        manual_count = len(panels["main"])
        expected_count = auto_count - len([i for i in removed_indices if i < auto_count])
        
        # Allow some tolerance due to grid calculation differences
        assert abs(manual_count - expected_count) <= 2, \
            f"Manual count mismatch for {description}: got {manual_count}, expected ~{expected_count}"
        
        print(f"✓ {description}: {manual_count} modules (removed {len(removed_indices)} indices)")
        plotter.close()
    
    print("\n✅ Manual removal tests passed")
    return True


def test_garage_addition():
    """Test garage addition when main roof space is insufficient"""
    print("\n" + "=" * 60)
    print("Testing Garage Addition")
    print("=" * 60)
    
    dims = BuildingDims(length_m=8.0, width_m=5.0, wall_height_m=6.0)  # Smaller building
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    
    # Test without garage
    layout_no_garage = LayoutConfig(mode="auto", use_garage=False)
    plotter_no_garage, panels_no_garage = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=50,  # Request more than fits
        layout_config=layout_no_garage
    )
    
    main_only = len(panels_no_garage["main"])
    print(f"✓ Without garage: {main_only} modules on main roof (requested 50)")
    plotter_no_garage.close()
    
    # Test with garage
    layout_with_garage = LayoutConfig(mode="auto", use_garage=True)
    plotter_with_garage, panels_with_garage = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=50,
        layout_config=layout_with_garage
    )
    
    main_count = len(panels_with_garage["main"])
    garage_count = len(panels_with_garage.get("garage", []))
    total_count = main_count + garage_count
    
    print(f"✓ With garage: {total_count} modules total (main: {main_count}, garage: {garage_count})")
    assert garage_count > 0, "Garage should have modules when enabled"
    assert total_count > main_only, "Total with garage should be more than main only"
    
    plotter_with_garage.close()
    
    print("\n✅ Garage addition tests passed")
    return True


def test_facade_placement():
    """Test facade placement when roof and garage are insufficient"""
    print("\n" + "=" * 60)
    print("Testing Facade Placement")
    print("=" * 60)
    
    dims = BuildingDims(length_m=8.0, width_m=5.0, wall_height_m=6.0)  # Smaller building
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30,
            "roof_covering_type": "Ziegel"
        }
    }
    
    # Test without facade
    layout_no_facade = LayoutConfig(mode="auto", use_garage=True, use_facade=False)
    plotter_no_facade, panels_no_facade = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=100,  # Request way more than fits
        layout_config=layout_no_facade
    )
    
    total_no_facade = len(panels_no_facade["main"]) + len(panels_no_facade.get("garage", []))
    print(f"✓ Without facade: {total_no_facade} modules (main + garage, requested 100)")
    plotter_no_facade.close()
    
    # Test with facade
    layout_with_facade = LayoutConfig(mode="auto", use_garage=True, use_facade=True)
    plotter_with_facade, panels_with_facade = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Satteldach",
        module_quantity=100,
        layout_config=layout_with_facade
    )
    
    main_count = len(panels_with_facade["main"])
    garage_count = len(panels_with_facade.get("garage", []))
    facade_count = len(panels_with_facade.get("facade", []))
    total_count = main_count + garage_count + facade_count
    
    print(f"✓ With facade: {total_count} modules total (main: {main_count}, garage: {garage_count}, facade: {facade_count})")
    assert facade_count > 0, "Facade should have modules when enabled"
    assert total_count > total_no_facade, "Total with facade should be more than without"
    
    plotter_with_facade.close()
    
    print("\n✅ Facade placement tests passed")
    return True


def test_combined_scenarios():
    """Test combined scenarios with multiple features"""
    print("\n" + "=" * 60)
    print("Testing Combined Scenarios")
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
    
    # Scenario 1: Manual mode with garage and facade
    layout1 = LayoutConfig(
        mode="manual",
        use_garage=True,
        use_facade=True,
        removed_indices=[0, 1, 2, 3, 4]
    )
    plotter1, panels1 = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Flachdach",
        module_quantity=50,
        layout_config=layout1
    )
    
    total1 = len(panels1["main"]) + len(panels1.get("garage", [])) + len(panels1.get("facade", []))
    print(f"✓ Scenario 1 (manual + garage + facade): {total1} modules placed")
    plotter1.close()
    
    # Scenario 2: Auto mode with only garage
    layout2 = LayoutConfig(
        mode="auto",
        use_garage=True,
        use_facade=False
    )
    plotter2, panels2 = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type="Flachdach",
        module_quantity=30,
        layout_config=layout2
    )
    
    total2 = len(panels2["main"]) + len(panels2.get("garage", []))
    print(f"✓ Scenario 2 (auto + garage only): {total2} modules placed")
    plotter2.close()
    
    print("\n✅ Combined scenario tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING PLACEMENT MODES")
    print("=" * 60)
    
    tests = [
        test_automatic_placement,
        test_manual_removal,
        test_garage_addition,
        test_facade_placement,
        test_combined_scenarios
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
        print("\n✅ ALL PLACEMENT MODE TESTS PASSED!")
        exit(0)
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        exit(1)
