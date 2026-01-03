"""
Standalone test for Task 7.2: Snap-to-Grid (Magnet-Funktion)
"""

import sys
import os
sys.path.insert(0, '.')

from utils.pv3d_placement_handler import snap_to_grid, handle_manual_move_with_snap
import streamlit as st

# Mock streamlit session_state for testing
class MockSessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

st.session_state = MockSessionState()


def test_snap_to_grid_half_meter():
    """Test snap to 0.5m grid"""
    print("Testing snap to 0.5m grid...")
    
    # Test verschiedene Positionen
    test_cases = [
        ((1.23, 2.67), (1.0, 2.5)),
        ((0.24, 0.26), (0.0, 0.5)),
        ((0.75, 0.76), (1.0, 1.0)),
        ((-1.23, -2.67), (-1.0, -2.5)),
    ]
    
    for (x, y), (expected_x, expected_y) in test_cases:
        result_x, result_y = snap_to_grid(x, y, grid_spacing=0.5)
        assert abs(result_x - expected_x) < 0.01, f"X: {result_x} != {expected_x}"
        assert abs(result_y - expected_y) < 0.01, f"Y: {result_y} != {expected_y}"
    
    print("✓ Snap to 0.5m grid test passed")


def test_snap_to_grid_tenth_meter():
    """Test snap to 0.1m grid"""
    print("Testing snap to 0.1m grid...")
    
    test_cases = [
        ((1.23, 2.67), (1.2, 2.7)),
        ((0.24, 0.26), (0.2, 0.3)),
        ((0.75, 0.76), (0.8, 0.8)),
    ]
    
    for (x, y), (expected_x, expected_y) in test_cases:
        result_x, result_y = snap_to_grid(x, y, grid_spacing=0.1)
        assert abs(result_x - expected_x) < 0.01, f"X: {result_x} != {expected_x}"
        assert abs(result_y - expected_y) < 0.01, f"Y: {result_y} != {expected_y}"
    
    print("✓ Snap to 0.1m grid test passed")


def test_snap_to_grid_one_meter():
    """Test snap to 1.0m grid"""
    print("Testing snap to 1.0m grid...")
    
    test_cases = [
        ((1.23, 2.67), (1.0, 3.0)),
        ((0.49, 0.51), (0.0, 1.0)),
        ((1.5, 2.5), (2.0, 2.0)),
    ]
    
    for (x, y), (expected_x, expected_y) in test_cases:
        result_x, result_y = snap_to_grid(x, y, grid_spacing=1.0)
        assert abs(result_x - expected_x) < 0.01, f"X: {result_x} != {expected_x}"
        assert abs(result_y - expected_y) < 0.01, f"Y: {result_y} != {expected_y}"
    
    print("✓ Snap to 1.0m grid test passed")


def test_snap_to_grid_zero_position():
    """Test snap at origin"""
    print("Testing snap at origin...")
    
    result_x, result_y = snap_to_grid(0.0, 0.0, grid_spacing=0.5)
    assert result_x == 0.0, f"X should be 0.0, got {result_x}"
    assert result_y == 0.0, f"Y should be 0.0, got {result_y}"
    
    print("✓ Snap at origin test passed")


def test_snap_to_grid_negative_positions():
    """Test snap with negative coordinates"""
    print("Testing snap with negative coordinates...")
    
    test_cases = [
        ((-1.23, -2.67), (-1.0, -2.5)),
        ((-0.24, -0.26), (0.0, -0.5)),  # -0.24 -> 0.0, -0.26 -> -0.5
        ((-0.75, -0.76), (-1.0, -1.0)),
    ]
    
    for (x, y), (expected_x, expected_y) in test_cases:
        result_x, result_y = snap_to_grid(x, y, grid_spacing=0.5)
        assert abs(result_x - expected_x) < 0.01, f"X: {result_x} != {expected_x}"
        assert abs(result_y - expected_y) < 0.01, f"Y: {result_y} != {expected_y}"
    
    print("✓ Snap with negative coordinates test passed")


def test_handle_manual_move_with_snap_enabled():
    """Test module move with snap enabled"""
    print("Testing module move with snap enabled...")
    
    # Setup: Platziere ein Modul
    st.session_state["placed_module_positions"] = [(0.0, 0.0, 1.0)]
    st.session_state["placed_module_count"] = 1
    
    # Verschiebe mit Snap
    result = handle_manual_move_with_snap(
        module_index=0,
        new_x=1.23,
        new_y=2.67,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0,
        enable_snap=True,
        grid_spacing=0.5
    )
    
    assert result["success"], f"Move should succeed: {result['message']}"
    assert result["new_position"][0] == 1.0, "X should be snapped to 1.0"
    assert result["new_position"][1] == 2.5, "Y should be snapped to 2.5"
    
    print("✓ Module move with snap enabled test passed")


def test_handle_manual_move_with_snap_disabled():
    """Test module move with snap disabled"""
    print("Testing module move with snap disabled...")
    
    # Setup
    st.session_state["placed_module_positions"] = [(0.0, 0.0, 1.0)]
    st.session_state["placed_module_count"] = 1
    
    # Verschiebe ohne Snap
    result = handle_manual_move_with_snap(
        module_index=0,
        new_x=1.23,
        new_y=2.67,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0,
        enable_snap=False,
        grid_spacing=0.5
    )
    
    assert result["success"], f"Move should succeed: {result['message']}"
    assert abs(result["new_position"][0] - 1.23) < 0.01, "X should not be snapped"
    assert abs(result["new_position"][1] - 2.67) < 0.01, "Y should not be snapped"
    
    print("✓ Module move with snap disabled test passed")


def test_handle_manual_move_collision_detection():
    """Test collision detection during move"""
    print("Testing collision detection during move...")
    
    # Setup: Platziere zwei Module
    st.session_state["placed_module_positions"] = [
        (0.0, 0.0, 1.0),
        (2.0, 0.0, 1.0)
    ]
    st.session_state["placed_module_count"] = 2
    
    # Versuche Modul 0 auf Position von Modul 1 zu verschieben
    result = handle_manual_move_with_snap(
        module_index=0,
        new_x=2.0,
        new_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0,
        enable_snap=True,
        grid_spacing=0.5
    )
    
    assert not result["success"], "Move should fail due to collision"
    assert "Kollision" in result["message"], "Error message should mention collision"
    
    print("✓ Collision detection test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TASK 7.2: SNAP-TO-GRID TESTS")
    print("="*60 + "\n")
    
    try:
        test_snap_to_grid_half_meter()
        test_snap_to_grid_tenth_meter()
        test_snap_to_grid_one_meter()
        test_snap_to_grid_zero_position()
        test_snap_to_grid_negative_positions()
        test_handle_manual_move_with_snap_enabled()
        test_handle_manual_move_with_snap_disabled()
        test_handle_manual_move_collision_detection()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED (8/8)")
        print("="*60 + "\n")
        print("Task 7.2 implementation is complete and working!")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
