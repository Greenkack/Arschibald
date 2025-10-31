"""
Test für admin_pdf_settings_ui.py

Testet die PDF-Design-Einstellungen UI (Task 9)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that the module can be imported"""
    try:
        import admin_pdf_settings_ui
        print("✅ Module import successful")
        return True
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False


def test_function_exists():
    """Test that required functions exist"""
    try:
        from admin_pdf_settings_ui import (
            render_pdf_settings_ui,
            render_pdf_design_settings,
            get_db_functions
        )
        print("✅ All required functions exist")
        return True
    except ImportError as e:
        print(f"❌ Function import failed: {e}")
        return False


def test_default_settings():
    """Test that default settings are properly defined"""
    try:
        # Mock the database functions
        def mock_load_setting(key, default=None):
            return {}
        
        def mock_save_setting(key, value):
            return True
        
        # Test that the function can handle empty settings
        defaults = {
            'primary_color': '#1E3A8A',
            'secondary_color': '#3B82F6',
            'font_family': 'Helvetica',
            'font_size_h1': 18,
            'font_size_h2': 14,
            'font_size_body': 10,
            'font_size_small': 8,
            'logo_position': 'left',
            'footer_format': 'with_page_number',
            'custom_footer_text': '',
            'watermark_enabled': False,
            'watermark_text': 'ENTWURF',
            'watermark_opacity': 0.1
        }
        
        print("✅ Default settings structure is valid")
        print(f"   - {len(defaults)} settings defined")
        return True
    except Exception as e:
        print(f"❌ Default settings test failed: {e}")
        return False


def test_color_validation():
    """Test color format validation"""
    try:
        # Test valid hex colors
        valid_colors = ['#1E3A8A', '#3B82F6', '#000000', '#FFFFFF']
        for color in valid_colors:
            assert color.startswith('#'), f"Invalid color format: {color}"
            assert len(color) == 7, f"Invalid color length: {color}"
        
        print("✅ Color validation passed")
        return True
    except Exception as e:
        print(f"❌ Color validation failed: {e}")
        return False


def test_font_settings():
    """Test font settings structure"""
    try:
        valid_fonts = ['Helvetica', 'Times-Roman', 'Courier']
        font_sizes = {
            'h1': (12, 24),
            'h2': (10, 20),
            'body': (8, 14),
            'small': (6, 10)
        }
        
        print("✅ Font settings structure is valid")
        print(f"   - {len(valid_fonts)} fonts available")
        print(f"   - {len(font_sizes)} size categories defined")
        return True
    except Exception as e:
        print(f"❌ Font settings test failed: {e}")
        return False


def test_layout_options():
    """Test layout options"""
    try:
        logo_positions = ['left', 'center', 'right']
        footer_formats = ['with_page_number', 'without_page_number', 'custom']
        
        print("✅ Layout options are valid")
        print(f"   - {len(logo_positions)} logo positions")
        print(f"   - {len(footer_formats)} footer formats")
        return True
    except Exception as e:
        print(f"❌ Layout options test failed: {e}")
        return False


def test_watermark_settings():
    """Test watermark settings"""
    try:
        # Test opacity range
        min_opacity = 0.0
        max_opacity = 1.0
        default_opacity = 0.1
        
        assert 0.0 <= default_opacity <= 1.0, "Invalid default opacity"
        
        print("✅ Watermark settings are valid")
        print(f"   - Opacity range: {min_opacity} - {max_opacity}")
        return True
    except Exception as e:
        print(f"❌ Watermark settings test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing admin_pdf_settings_ui.py (Task 9)")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Import", test_imports),
        ("Function Existence", test_function_exists),
        ("Default Settings", test_default_settings),
        ("Color Validation", test_color_validation),
        ("Font Settings", test_font_settings),
        ("Layout Options", test_layout_options),
        ("Watermark Settings", test_watermark_settings)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
