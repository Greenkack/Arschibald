"""
Test script for Task 3: Geometrie-Primitives und Dachformen
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import (
    make_box,
    make_roof_flat,
    make_roof_gable,
    make_roof_hip,
    make_roof_pent,
    make_roof_pyramid,
    make_panel
)


def test_make_box():
    """Test make_box function with various dimensions"""
    print("Testing make_box()...")
    
    # Test 1: Basic box
    box1 = make_box(10.0, 6.0, 3.0)
    assert box1 is not None
    assert box1.n_points > 0
    print("  ✓ Basic box created")
    
    # Test 2: Box with custom center
    box2 = make_box(5.0, 5.0, 5.0, center=(10.0, 10.0, 0.0))
    assert box2 is not None
    print("  ✓ Box with custom center created")
    
    # Test 3: Box with origin at center
    box3 = make_box(8.0, 4.0, 2.0, origin_at_bottom=False)
    assert box3 is not None
    print("  ✓ Box with centered origin created")
    
    print("✅ make_box() tests passed\n")


def test_roof_shapes():
    """Test all roof shape functions"""
    print("Testing roof shape functions...")
    
    length = 10.0
    width = 6.0
    base_height = 6.0
    inclination = 35.0
    
    # Test flat roof
    roof_flat = make_roof_flat(length, width, base_height)
    assert roof_flat is not None
    assert roof_flat.n_points > 0
    print("  ✓ Flat roof created")
    
    # Test gable roof
    roof_gable = make_roof_gable(length, width, base_height, inclination)
    assert roof_gable is not None
    assert roof_gable.n_points >= 6  # Should have at least 6 points
    print("  ✓ Gable roof created")
    
    # Test hip roof
    roof_hip = make_roof_hip(length, width, base_height, inclination)
    assert roof_hip is not None
    assert roof_hip.n_points >= 4
    print("  ✓ Hip roof created")
    
    # Test pent roof
    roof_pent = make_roof_pent(length, width, base_height, inclination)
    assert roof_pent is not None
    assert roof_pent.n_points == 4
    print("  ✓ Pent roof created")
    
    # Test pyramid roof
    roof_pyramid = make_roof_pyramid(length, width, base_height, inclination)
    assert roof_pyramid is not None
    assert roof_pyramid.n_points == 5  # 4 corners + 1 peak
    print("  ✓ Pyramid roof created")
    
    print("✅ All roof shape tests passed\n")


def test_make_panel():
    """Test PV panel creation with various rotations"""
    print("Testing make_panel()...")
    
    # Test 1: Horizontal panel
    panel1 = make_panel((0.0, 0.0, 0.0), yaw_deg=0.0, tilt_deg=0.0)
    assert panel1 is not None
    assert panel1.n_points > 0
    print("  ✓ Horizontal panel created")
    
    # Test 2: Panel with tilt (15° south-facing)
    panel2 = make_panel((5.0, 5.0, 1.0), yaw_deg=0.0, tilt_deg=15.0)
    assert panel2 is not None
    print("  ✓ Tilted panel (15°) created")
    
    # Test 3: Panel with yaw rotation (90° west-facing)
    panel3 = make_panel((0.0, 0.0, 2.0), yaw_deg=90.0, tilt_deg=0.0)
    assert panel3 is not None
    print("  ✓ Rotated panel (90° yaw) created")
    
    # Test 4: Panel with both tilt and yaw
    panel4 = make_panel((10.0, 10.0, 3.0), yaw_deg=45.0, tilt_deg=30.0)
    assert panel4 is not None
    print("  ✓ Panel with tilt and yaw created")
    
    # Test 5: Vertical panel (facade)
    panel5 = make_panel((0.0, 0.0, 5.0), yaw_deg=0.0, tilt_deg=90.0)
    assert panel5 is not None
    print("  ✓ Vertical panel (90° tilt) created")
    
    print("✅ make_panel() tests passed\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Task 3: Geometrie-Primitives und Dachformen - Tests")
    print("=" * 60)
    print()
    
    try:
        test_make_box()
        test_roof_shapes()
        test_make_panel()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  • make_box() - Working correctly")
        print("  • All 5 roof shapes - Working correctly")
        print("  • make_panel() with rotations - Working correctly")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
