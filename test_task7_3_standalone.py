"""
Standalone test for Task 7.3: Kopieren & Einfügen (Copy & Paste)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d_placement_handler import (
    copy_module_group,
    paste_module_group
)
import streamlit as st


# Mock streamlit session_state for testing
class MockSessionState(dict):
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


st.session_state = MockSessionState()


def test_copy_single_module():
    """Test copying a single module"""
    print("Testing copy single module...")

    # Setup: Place one module
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1

    # Copy module 0
    result = copy_module_group([0])

    assert result["success"], f"Copy should succeed: {result['message']}"
    assert result["count"] == 1, "Should copy 1 module"
    assert "module_clipboard" in st.session_state
    assert len(st.session_state["module_clipboard"]) == 1

    clipboard = st.session_state["module_clipboard"][0]
    assert clipboard["x"] == 1.0
    assert clipboard["y"] == 2.0
    assert clipboard["z"] == 0.3

    print("✓ Copy single module test passed")


def test_copy_multiple_modules():
    """Test copying multiple modules"""
    print("Testing copy multiple modules...")

    # Setup: Place three modules
    st.session_state["placed_module_positions"] = [
        (1.0, 2.0, 0.3),
        (3.0, 4.0, 0.3),
        (5.0, 6.0, 0.3)
    ]
    st.session_state["placed_module_count"] = 3

    # Copy modules 0, 1, 2
    result = copy_module_group([0, 1, 2])

    assert result["success"], f"Copy should succeed: {result['message']}"
    assert result["count"] == 3, "Should copy 3 modules"
    assert len(st.session_state["module_clipboard"]) == 3

    print("✓ Copy multiple modules test passed")


def test_copy_empty_selection():
    """Test copying with empty selection"""
    print("Testing copy with empty selection...")

    # Setup
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1

    # Try to copy empty selection
    result = copy_module_group([])

    assert not result["success"], "Copy should fail with empty selection"
    assert "Keine Module ausgewählt" in result["message"]
    assert result["count"] == 0

    print("✓ Copy empty selection test passed")


def test_copy_invalid_indices():
    """Test copying with invalid indices"""
    print("Testing copy with invalid indices...")

    # Setup
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1

    # Try to copy invalid indices
    result = copy_module_group([999, -1, 100])

    assert not result["success"], "Copy should fail with invalid indices"
    assert result["count"] == 0

    print("✓ Copy invalid indices test passed")


def test_paste_single_module():
    """Test pasting a single module"""
    print("Testing paste single module...")

    # Setup: Copy one module
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1
    st.session_state["module_clipboard"] = [
        {"x": 1.0, "y": 2.0, "z": 0.3, "original_index": 0}
    ]

    # Paste with offset
    result = paste_module_group(
        offset_x=2.0,
        offset_y=1.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0
    )

    assert result["success"], f"Paste should succeed: {result['message']}"
    assert result["pasted_count"] == 1, "Should paste 1 module"
    assert result["skipped_count"] == 0, "No modules should be skipped"

    # Check new position
    positions = st.session_state["placed_module_positions"]
    assert len(positions) == 2, "Should have 2 modules now"
    assert positions[1][0] == 3.0, "X should be 1.0 + 2.0 = 3.0"
    assert positions[1][1] == 3.0, "Y should be 2.0 + 1.0 = 3.0"

    print("✓ Paste single module test passed")


def test_paste_multiple_modules():
    """Test pasting multiple modules"""
    print("Testing paste multiple modules...")

    # Setup: Copy three modules
    st.session_state["placed_module_positions"] = [
        (1.0, 2.0, 0.3),
        (3.0, 4.0, 0.3),
        (5.0, 6.0, 0.3)
    ]
    st.session_state["placed_module_count"] = 3
    st.session_state["module_clipboard"] = [
        {"x": 1.0, "y": 2.0, "z": 0.3, "original_index": 0},
        {"x": 3.0, "y": 4.0, "z": 0.3, "original_index": 1},
        {"x": 5.0, "y": 6.0, "z": 0.3, "original_index": 2}
    ]

    # Paste with offset (use larger roof to avoid boundary collision)
    result = paste_module_group(
        offset_x=2.0,
        offset_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=20.0,
        roof_length=20.0
    )

    assert result["success"], f"Paste should succeed: {result['message']}"
    assert result["pasted_count"] == 3, "Should paste 3 modules"

    # Check we have 6 modules now
    positions = st.session_state["placed_module_positions"]
    assert len(positions) == 6, "Should have 6 modules now"

    print("✓ Paste multiple modules test passed")


def test_paste_empty_clipboard():
    """Test pasting with empty clipboard"""
    print("Testing paste with empty clipboard...")

    # Setup: No clipboard
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1
    st.session_state["module_clipboard"] = []

    # Try to paste
    result = paste_module_group(
        offset_x=1.0,
        offset_y=1.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0
    )

    assert not result["success"], "Paste should fail with empty clipboard"
    assert "Zwischenablage leer" in result["message"]
    assert result["pasted_count"] == 0

    print("✓ Paste empty clipboard test passed")


def test_paste_with_collision_detection():
    """Test paste with collision detection"""
    print("Testing paste with collision detection...")

    # Setup: Place module at (1, 2)
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1

    # Copy it
    st.session_state["module_clipboard"] = [
        {"x": 1.0, "y": 2.0, "z": 0.3, "original_index": 0}
    ]

    # Try to paste at same location (offset 0, 0)
    result = paste_module_group(
        offset_x=0.0,
        offset_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0,
        check_collisions=True
    )

    # Should fail due to collision
    assert not result["success"], "Paste should fail due to collision"
    assert result["pasted_count"] == 0
    assert result["skipped_count"] == 1

    print("✓ Paste with collision detection test passed")


def test_paste_without_collision_detection():
    """Test paste without collision detection"""
    print("Testing paste without collision detection...")

    # Setup
    st.session_state["placed_module_positions"] = [(1.0, 2.0, 0.3)]
    st.session_state["placed_module_count"] = 1
    st.session_state["module_clipboard"] = [
        {"x": 1.0, "y": 2.0, "z": 0.3, "original_index": 0}
    ]

    # Paste at same location with collision check disabled
    result = paste_module_group(
        offset_x=0.0,
        offset_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=10.0,
        roof_length=10.0,
        check_collisions=False
    )

    # Should succeed (no collision check)
    assert result["success"], f"Paste should succeed: {result['message']}"
    assert result["pasted_count"] == 1
    assert result["skipped_count"] == 0

    print("✓ Paste without collision detection test passed")


def test_copy_paste_workflow():
    """Test complete copy-paste workflow"""
    print("Testing complete copy-paste workflow...")

    # Setup: Place 2 modules
    st.session_state["placed_module_positions"] = [
        (1.0, 2.0, 0.3),
        (3.0, 4.0, 0.3)
    ]
    st.session_state["placed_module_count"] = 2

    # Step 1: Copy both modules
    copy_result = copy_module_group([0, 1])
    assert copy_result["success"], "Copy should succeed"
    assert copy_result["count"] == 2

    # Step 2: Paste with offset
    paste_result = paste_module_group(
        offset_x=5.0,
        offset_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0.0,
        roof_width=20.0,
        roof_length=20.0
    )
    assert paste_result["success"], "Paste should succeed"
    assert paste_result["pasted_count"] == 2

    # Verify we have 4 modules now
    positions = st.session_state["placed_module_positions"]
    assert len(positions) == 4, "Should have 4 modules"

    # Verify positions
    assert positions[2][0] == 6.0, "New module X should be 1.0 + 5.0"
    assert positions[3][0] == 8.0, "New module X should be 3.0 + 5.0"

    print("✓ Complete copy-paste workflow test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TASK 7.3: KOPIEREN & EINFÜGEN TESTS")
    print("="*60 + "\n")

    try:
        test_copy_single_module()
        test_copy_multiple_modules()
        test_copy_empty_selection()
        test_copy_invalid_indices()
        test_paste_single_module()
        test_paste_multiple_modules()
        test_paste_empty_clipboard()
        test_paste_with_collision_detection()
        test_paste_without_collision_detection()
        test_copy_paste_workflow()

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED (10/10)")
        print("="*60 + "\n")
        print("Task 7.3 implementation is complete and working!")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
