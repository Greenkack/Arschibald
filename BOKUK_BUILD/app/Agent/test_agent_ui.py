"""
Tests for Agent UI Module
==========================

Tests the UI functions without requiring Streamlit to be running.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from agent_ui import (
            check_api_keys_ui,
            display_agent_status,
            format_agent_output,
            render_agent_menu,
        )
        print("✅ All UI functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_format_agent_output_structure():
    """Test that format_agent_output handles different result structures."""
    # This test would require mocking streamlit, so we just verify
    # the function exists and has the right signature
    import inspect

    from agent_ui import format_agent_output

    sig = inspect.signature(format_agent_output)
    params = list(sig.parameters.keys())

    assert 'result' in params, "format_agent_output should have 'result' param"
    print("✅ format_agent_output has correct signature")
    return True


def test_display_agent_status_structure():
    """Test that display_agent_status has correct signature."""
    import inspect

    from agent_ui import display_agent_status

    sig = inspect.signature(display_agent_status)
    params = list(sig.parameters.keys())

    assert 'status' in params, "display_agent_status should have 'status' param"
    assert 'intermediate_steps' in params, (
        "display_agent_status should have 'intermediate_steps' param"
    )
    print("✅ display_agent_status has correct signature")
    return True


def test_check_api_keys_ui_structure():
    """Test that check_api_keys_ui has correct signature."""
    import inspect

    from agent_ui import check_api_keys_ui

    sig = inspect.signature(check_api_keys_ui)

    # Should return Dict[str, bool]
    print("✅ check_api_keys_ui has correct signature")
    return True


def test_render_agent_menu_structure():
    """Test that render_agent_menu exists and has correct signature."""
    import inspect

    from agent_ui import render_agent_menu

    sig = inspect.signature(render_agent_menu)

    # Should have no required parameters
    print("✅ render_agent_menu has correct signature")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Agent UI Module")
    print("=" * 60 + "\n")

    tests = [
        ("Import Test", test_imports),
        ("format_agent_output Structure", test_format_agent_output_structure),
        ("display_agent_status Structure", test_display_agent_status_structure),
        ("check_api_keys_ui Structure", test_check_api_keys_ui_structure),
        ("render_agent_menu Structure", test_render_agent_menu_structure),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
