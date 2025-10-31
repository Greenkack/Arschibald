"""
Test script to verify 3D view navigation integration
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_solar_calculator_has_3d_link():
    """Test that solar_calculator.py contains the 3D view navigation link"""
    with open('solar_calculator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for 3D view button
    assert '3D-Visualisierung' in content, "3D-Visualisierung text not found in solar_calculator.py"
    assert 'btn_goto_3d_view' in content, "3D view button key not found"
    assert "selected_page_key'] = '3d_view'" in content, "3D view page key not set"
    
    print("✓ Solar Calculator has 3D view navigation link")
    return True


def test_gui_has_3d_menu_item():
    """Test that gui.py contains the 3D view menu item"""
    with open('gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for 3D view in menu
    assert '3D PV-Visualisierung' in content, "3D PV-Visualisierung not found in gui.py menu"
    assert '"key": "3d_view"' in content, "3d_view key not found in menu"
    assert 'selected_page_key == "3d_view"' in content, "3d_view page handler not found"
    
    print("✓ GUI has 3D view menu item and page handler")
    return True


def test_3d_view_page_exists():
    """Test that the 3D view page file exists"""
    page_path = os.path.join('pages', 'solar_3d_view.py')
    assert os.path.exists(page_path), f"3D view page not found at {page_path}"
    
    print("✓ 3D view page file exists")
    return True


def test_3d_view_imports():
    """Test that 3D view page has correct imports"""
    with open('pages/solar_3d_view.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required imports
    assert 'from utils.pv3d import' in content, "pv3d imports not found"
    assert 'BuildingDims' in content, "BuildingDims not imported"
    assert 'LayoutConfig' in content, "LayoutConfig not imported"
    assert 'build_scene' in content, "build_scene not imported"
    
    print("✓ 3D view page has correct imports")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing 3D View Navigation Integration")
    print("=" * 60)
    
    tests = [
        test_solar_calculator_has_3d_link,
        test_gui_has_3d_menu_item,
        test_3d_view_page_exists,
        test_3d_view_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All navigation integration tests passed!")
        exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed")
        exit(1)
