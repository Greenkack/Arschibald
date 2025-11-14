"""
Test Task 4: Manuelle Belegung reparieren

This test verifies the implementation of manual module placement features:
- Task 4.1: Modul-Auswahl implementieren
- Task 4.2: Modul-Manipulation implementieren
- Task 4.3: Drag & Drop implementieren (Quick Move)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_placement_handler_imports():
    """Test that all handler functions can be imported."""
    print("Test 1: Import placement handler functions...")
    
    try:
        from utils.pv3d_placement_handler import (
            handle_auto_placement,
            handle_reset_placement,
            handle_manual_add,
            handle_remove_selected,
            handle_move_selected,  # TASK 4.2
            handle_rotate_selected,  # TASK 4.2
            check_module_collision,
            calculate_z_position,
            calculate_tilt_angle
        )
        print("[OK] All handler functions imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False


def test_ui_component_imports():
    """Test that UI components can be imported."""
    print("\nTest 2: Import UI components...")
    
    try:
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        print("[OK] UI components imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False


def test_move_handler_signature():
    """Test that move handler has correct signature."""
    print("\nTest 3: Verify move handler signature...")
    
    try:
        from utils.pv3d_placement_handler import handle_move_selected
        import inspect
        
        sig = inspect.signature(handle_move_selected)
        params = list(sig.parameters.keys())
        
        expected_params = [
            'selected_indices',
            'offset_x',
            'offset_y',
            'roof_length',
            'roof_width',
            'roof_type',
            'roof_pitch'
        ]
        
        for param in expected_params:
            if param not in params:
                print(f"[ERROR] Missing parameter: {param}")
                return False
        
        print(f"[OK] Move handler has correct signature: {params}")
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_rotate_handler_signature():
    """Test that rotate handler has correct signature."""
    print("\nTest 4: Verify rotate handler signature...")
    
    try:
        from utils.pv3d_placement_handler import handle_rotate_selected
        import inspect
        
        sig = inspect.signature(handle_rotate_selected)
        params = list(sig.parameters.keys())
        
        expected_params = ['selected_indices', 'rotation_degrees']
        
        for param in expected_params:
            if param not in params:
                print(f"[ERROR] Missing parameter: {param}")
                return False
        
        print(f"[OK] Rotate handler has correct signature: {params}")
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_collision_detection():
    """Test collision detection function."""
    print("\nTest 5: Test collision detection...")
    
    try:
        from utils.pv3d_placement_handler import check_module_collision
        
        # Test case 1: No collision (modules far apart)
        new_position = (0.0, 0.0, 1.0)
        existing_positions = [(5.0, 5.0, 1.0)]
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=10.0,
            roof_width=8.0,
            margin=0.3,
            orientation="portrait"
        )
        
        if result["collision"]:
            print(f"[ERROR] False positive collision detected: {result['message']}")
            return False
        
        print("[OK] No collision detected (correct)")
        
        # Test case 2: Collision (modules overlapping)
        new_position = (0.0, 0.0, 1.0)
        existing_positions = [(0.5, 0.5, 1.0)]  # Very close
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=10.0,
            roof_width=8.0,
            margin=0.3,
            orientation="portrait"
        )
        
        if not result["collision"]:
            print("[ERROR] Collision not detected (should have detected)")
            return False
        
        print(f"[OK] Collision detected (correct): {result['type']}")
        
        # Test case 3: Boundary violation
        new_position = (10.0, 0.0, 1.0)  # Outside roof
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=10.0,
            roof_width=8.0,
            margin=0.3,
            orientation="portrait"
        )
        
        if not result["collision"] or result["type"] != "boundary":
            print("[ERROR] Boundary violation not detected")
            return False
        
        print(f"[OK] Boundary violation detected (correct)")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_z_position_calculation():
    """Test Z-position calculation for different roof types."""
    print("\nTest 6: Test Z-position calculation...")
    
    try:
        from utils.pv3d_placement_handler import calculate_z_position
        
        # Test flat roof
        z_flat = calculate_z_position("Flachdach", 0.0, 10.0)
        if z_flat != 0.30:  # 30cm elevation
            print(f"[ERROR] Flat roof Z-position incorrect: {z_flat} (expected 0.30)")
            return False
        print(f"[OK] Flat roof Z-position: {z_flat}m (correct)")
        
        # Test pitched roof
        z_pitched = calculate_z_position("Satteldach", 35.0, 10.0)
        if z_pitched != 0.15:  # 15cm clearance
            print(f"[ERROR] Pitched roof Z-position incorrect: {z_pitched} (expected 0.15)")
            return False
        print(f"[OK] Pitched roof Z-position: {z_pitched}m (correct)")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tilt_angle_calculation():
    """Test tilt angle calculation for different roof types."""
    print("\nTest 7: Test tilt angle calculation...")
    
    try:
        from utils.pv3d_placement_handler import calculate_tilt_angle
        
        # Test flat roof (should be 30° for optimal solar exposure)
        tilt_flat = calculate_tilt_angle("Flachdach", 0.0)
        if tilt_flat != 30.0:
            print(f"[ERROR] Flat roof tilt incorrect: {tilt_flat} (expected 30.0)")
            return False
        print(f"[OK] Flat roof tilt: {tilt_flat}° (correct)")
        
        # Test pitched roof (should follow roof pitch)
        tilt_pitched = calculate_tilt_angle("Satteldach", 35.0)
        if tilt_pitched != 35.0:
            print(f"[ERROR] Pitched roof tilt incorrect: {tilt_pitched} (expected 35.0)")
            return False
        print(f"[OK] Pitched roof tilt: {tilt_pitched}° (correct)")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Task 4: Manuelle Belegung reparieren - Test Suite")
    print("=" * 60)
    
    tests = [
        test_placement_handler_imports,
        test_ui_component_imports,
        test_move_handler_signature,
        test_rotate_handler_signature,
        test_collision_detection,
        test_z_position_calculation,
        test_tilt_angle_calculation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[ERROR] {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
