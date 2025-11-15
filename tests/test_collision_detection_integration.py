"""
Test Suite for Task 7: Collision Detection Integration

This test verifies that collision detection is properly integrated into
the manual placement workflow and that warnings are displayed correctly.

Requirements tested: 7.1, 7.2, 7.3, 7.4
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockSessionState(dict):
    """Mock Streamlit session state."""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value

# Create mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from utils.pv3d_placement_handler import (
    check_module_collision,
    handle_manual_add,
    handle_move_selected,
    initialize_session_state
)


def test_collision_detection_prevents_overlap():
    """
    Test 7.1: Module-to-Module collision detection prevents overlapping placement.
    
    Requirements:
        - 7.1: Erkenne Überlappungen
        - 7.3: Zeige Warnung
        - 7.4: Verhindere Platzierung bei Kollision
    """
    print("\n=== Test 7.1: Module-to-Module Collision Prevention ===")
    
    # Initialize session state
    initialize_session_state()
    
    # Place first module at origin
    st.session_state["placed_module_positions"] = [(0.0, 0.0, 0.3)]
    st.session_state["placed_module_count"] = 1
    
    # Try to place second module too close (should fail)
    result = handle_manual_add(
        x=0.5,  # Only 0.5m away (less than module width 1.05m)
        y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_length=10.0,
        roof_width=8.0,
        orientation="portrait"
    )
    
    print(f"Placement result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify collision was detected
    assert result["success"] is False, "Should prevent overlapping placement"
    assert "überlappt" in result["message"].lower(), "Should show overlap warning"
    
    # Verify module was NOT added
    assert len(st.session_state["placed_module_positions"]) == 1, \
        "Should not add overlapping module"
    
    print("Test passed: Overlapping placement prevented with warning")
    return True


def test_collision_detection_allows_valid_placement():
    """
    Test 7.1: Collision detection allows valid placement when no collision.
    
    Requirements:
        - 7.1: Erkenne Überlappungen (keine Überlappung = erlaubt)
        - 7.4: Verhindere Platzierung NUR bei Kollision
    """
    print("\n=== Test 7.1: Valid Placement Allowed ===")
    
    # Initialize session state
    initialize_session_state()
    
    # Place first module at origin
    st.session_state["placed_module_positions"] = [(0.0, 0.0, 0.3)]
    st.session_state["placed_module_count"] = 1
    
    # Try to place second module far enough away (should succeed)
    result = handle_manual_add(
        x=3.0,  # 3m away (more than module width 1.05m)
        y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_length=10.0,
        roof_width=8.0,
        orientation="portrait"
    )
    
    print(f"Placement result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify placement was allowed
    assert result["success"] is True, "Should allow valid placement"
    assert "hinzugefügt" in result["message"].lower(), "Should show success message"
    
    # Verify module was added
    assert len(st.session_state["placed_module_positions"]) == 2, \
        "Should add module when no collision"
    
    print("Test passed: Valid placement allowed")
    return True


def test_boundary_collision_prevents_placement():
    """
    Test 7.2: Boundary collision detection prevents placement outside roof.
    
    Requirements:
        - 7.2: Erkenne wenn Modul über Dachrand hinausragt
        - 7.3: Zeige Warnung
        - 7.4: Verhindere ungültige Platzierung
    """
    print("\n=== Test 7.2: Boundary Collision Prevention ===")
    
    # Initialize session state
    initialize_session_state()
    st.session_state["placed_module_positions"] = []
    st.session_state["placed_module_count"] = 0
    
    # Try to place module beyond roof boundary
    result = handle_manual_add(
        x=6.0,  # Far beyond roof edge (roof_length=10.0, so max x ≈ 4.5m)
        y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_length=10.0,
        roof_width=8.0,
        orientation="portrait"
    )
    
    print(f"Placement result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify boundary violation was detected
    assert result["success"] is False, "Should prevent out-of-bounds placement"
    assert "dachkante" in result["message"].lower(), "Should show boundary warning"
    
    # Verify module was NOT added
    assert len(st.session_state["placed_module_positions"]) == 0, \
        "Should not add out-of-bounds module"
    
    print("Test passed: Out-of-bounds placement prevented with warning")
    return True


def test_move_collision_detection():
    """
    Test 7.1 + 7.2: Collision detection during module move operation.
    
    Requirements:
        - 7.1: Erkenne Überlappungen beim Verschieben
        - 7.2: Erkenne Grenzüberschreitungen beim Verschieben
        - 7.3: Zeige Warnung
        - 7.4: Verhindere ungültige Verschiebung
    """
    print("\n=== Test 7.1 + 7.2: Move Collision Detection ===")
    
    # Initialize session state
    initialize_session_state()
    
    # Place two modules
    st.session_state["placed_module_positions"] = [
        (0.0, 0.0, 0.3),  # Module 0
        (3.0, 0.0, 0.3),  # Module 1
    ]
    st.session_state["placed_module_count"] = 2
    
    # Try to move module 1 onto module 0 (should fail)
    result = handle_move_selected(
        selected_indices=[1],
        offset_x=-2.5,  # Move left by 2.5m (would overlap with module 0)
        offset_y=0.0,
        roof_length=10.0,
        roof_width=8.0,
        roof_type="Flachdach",
        roof_pitch=0.0
    )
    
    print(f"Move result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify collision was detected
    assert result["success"] is False, "Should prevent overlapping move"
    assert "kollision" in result["message"].lower() or \
           "überlappt" in result["message"].lower(), \
           "Should show collision warning"
    
    # Verify module was NOT moved
    assert st.session_state["placed_module_positions"][1] == (3.0, 0.0, 0.3), \
        "Module should not move when collision detected"
    
    print("Test passed: Overlapping move prevented with warning")
    
    # Now try to move module 1 to a valid position (should succeed)
    result = handle_move_selected(
        selected_indices=[1],
        offset_x=1.0,  # Move right by 1m (no collision)
        offset_y=0.0,
        roof_length=10.0,
        roof_width=8.0,
        roof_type="Flachdach",
        roof_pitch=0.0
    )
    
    print(f"\nValid move result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify move was allowed
    assert result["success"] is True, "Should allow valid move"
    assert "verschoben" in result["message"].lower(), "Should show success message"
    
    # Verify module was moved
    assert st.session_state["placed_module_positions"][1][0] == 4.0, \
        "Module should move when no collision"
    
    print("Test passed: Valid move allowed")
    return True


def test_collision_warning_messages():
    """
    Test 7.3: Verify that collision warnings contain meaningful information.
    
    Requirements:
        - 7.3: Zeige Warnung mit Details
    """
    print("\n=== Test 7.3: Collision Warning Messages ===")
    
    # Test module-to-module collision message
    result = check_module_collision(
        new_position=(0.0, 0.0, 0.3),
        existing_positions=[(0.5, 0.0, 0.3)],
        roof_length=10.0,
        roof_width=8.0
    )
    
    print(f"\nModule collision message: {result['message']}")
    
    # Verify message contains useful information
    assert "modul" in result["message"].lower(), "Should mention module"
    assert "überlappt" in result["message"].lower(), "Should mention overlap"
    assert "#" in result["message"], "Should show module number"
    
    print("Module collision message is informative")
    
    # Test boundary collision message
    result = check_module_collision(
        new_position=(6.0, 0.0, 0.3),
        existing_positions=[],
        roof_length=10.0,
        roof_width=8.0
    )
    
    print(f"\nBoundary collision message: {result['message']}")
    
    # Verify message contains useful information
    assert "dachkante" in result["message"].lower(), "Should mention roof edge"
    assert "überschreitet" in result["message"].lower(), "Should mention exceeding"
    assert "m" in result["message"], "Should show measurements"
    
    print("Boundary collision message is informative")
    
    return True


def test_collision_detection_with_different_orientations():
    """
    Test 7.1: Collision detection works with different module orientations.
    
    Requirements:
        - 7.1: Erkenne Überlappungen (auch bei verschiedenen Orientierungen)
    """
    print("\n=== Test 7.1: Collision Detection with Orientations ===")
    
    # Test portrait orientation
    result_portrait = check_module_collision(
        new_position=(0.0, 0.0, 0.3),
        existing_positions=[(0.5, 0.0, 0.3)],
        roof_length=10.0,
        roof_width=8.0,
        orientation="portrait"
    )
    
    print(f"Portrait collision: {result_portrait['collision']}")
    assert result_portrait["collision"] is True, \
        "Should detect collision in portrait"
    
    # Test landscape orientation
    result_landscape = check_module_collision(
        new_position=(0.0, 0.0, 0.3),
        existing_positions=[(0.0, 0.8, 0.3)],
        roof_length=10.0,
        roof_width=8.0,
        orientation="landscape"
    )
    
    print(f"Landscape collision: {result_landscape['collision']}")
    assert result_landscape["collision"] is True, \
        "Should detect collision in landscape"
    
    print("Test passed: Collision detection works with both orientations")
    return True


def run_all_tests():
    """Run all collision detection integration tests."""
    print("=" * 70)
    print("COLLISION DETECTION INTEGRATION TEST SUITE - TASK 7")
    print("=" * 70)
    
    tests = [
        ("7.1 - Module Overlap Prevention", test_collision_detection_prevents_overlap),
        ("7.1 - Valid Placement Allowed", test_collision_detection_allows_valid_placement),
        ("7.2 - Boundary Violation Prevention", test_boundary_collision_prevents_placement),
        ("7.1 + 7.2 - Move Collision Detection", test_move_collision_detection),
        ("7.3 - Warning Messages", test_collision_warning_messages),
        ("7.1 - Orientation Support", test_collision_detection_with_different_orientations),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'=' * 70}")
            print(f"Running: {test_name}")
            print('=' * 70)
            test_func()
            passed += 1
            print(f"\n{test_name} PASSED")
        except AssertionError as e:
            print(f"\n{test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n{test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\nALL TESTS PASSED - Task 7 Complete!")
        print("\nCollision Detection Summary:")
        print("  7.1: Module-to-module overlap detection working")
        print("  7.2: Roof boundary violation detection working")
        print("  7.3: Meaningful warning messages displayed")
        print("  7.4: Invalid placements prevented")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
