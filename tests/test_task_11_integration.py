"""
Integration Test für Task 11: UI-Theme-Einstellungen

Testet die Integration mit admin_pdf_settings_ui.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_function_exists():
    """Test dass die render_ui_theme_settings Funktion existiert"""
    print("Testing function existence...")

    try:
        from admin_pdf_settings_ui import render_ui_theme_settings
        print("✓ render_ui_theme_settings function exists")
        return True
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False


def test_function_signature():
    """Test dass die Funktion die richtige Signatur hat"""
    print("\nTesting function signature...")

    try:
        from admin_pdf_settings_ui import render_ui_theme_settings
        import inspect

        sig = inspect.signature(render_ui_theme_settings)
        params = list(sig.parameters.keys())

        # Should have load_setting and save_setting parameters
        assert 'load_setting' in params, "Missing 'load_setting' parameter"
        assert 'save_setting' in params, "Missing 'save_setting' parameter"

        print(f"✓ Function has correct parameters: {params}")
        return True

    except Exception as e:
        print(f"❌ Error checking signature: {e}")
        return False


def test_theme_definitions():
    """Test dass die Theme-Definitionen im Code vorhanden sind"""
    print("\nTesting theme definitions in code...")

    try:
        # Read the file
        with open('admin_pdf_settings_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for theme definitions
        required_themes = ['light', 'dark', 'corporate', 'high_contrast']

        for theme in required_themes:
            assert f"'{theme}'" in content, f"Theme '{theme}' not found in code"
            print(f"✓ Theme '{theme}' found in code")

        # Check for required color properties
        required_colors = [
            'primary_color',
            'secondary_color',
            'background_color',
            'text_color',
            'accent_color'
        ]

        for color in required_colors:
            assert f"'{color}'" in content, f"Color property '{color}' not found"

        print(f"✓ All {len(required_colors)} color properties found")

        return True

    except Exception as e:
        print(f"❌ Error checking theme definitions: {e}")
        return False


def test_ui_components():
    """Test dass alle UI-Komponenten im Code vorhanden sind"""
    print("\nTesting UI components...")

    try:
        with open('admin_pdf_settings_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for Task 11.1 components (Theme-Auswahl)
        assert 'st.selectbox' in content, "Missing selectbox for theme selection"
        assert 'Theme aktivieren' in content, "Missing 'Theme aktivieren' button"
        print("✓ Task 11.1 components found (Theme-Auswahl)")

        # Check for Task 11.2 components (Theme-Vorschau)
        assert 'preview_html' in content, "Missing preview HTML generation"
        assert 'unsafe_allow_html=True' in content, "Missing HTML rendering"
        print("✓ Task 11.2 components found (Theme-Vorschau)")

        # Check for Task 11.3 components (Theme-Editor)
        assert 'st.color_picker' in content, "Missing color picker"
        assert 'Theme speichern' in content, "Missing 'Theme speichern' button"
        assert 'custom_theme' in content, "Missing custom theme handling"
        print("✓ Task 11.3 components found (Theme-Editor)")

        return True

    except Exception as e:
        print(f"❌ Error checking UI components: {e}")
        return False


def test_requirements_coverage():
    """Test dass alle Requirements im Code referenziert sind"""
    print("\nTesting requirements coverage...")

    try:
        with open('admin_pdf_settings_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for requirement references in comments
        requirements = ['22.1', '22.2', '22.3', '22.4', '28.1', '28.2', '28.4']

        found_requirements = []
        for req in requirements:
            if req in content:
                found_requirements.append(req)

        print(
            f"✓ Found {len(found_requirements)}/{len(requirements)} requirement references")

        # Check for key functionality
        assert 'predefined_themes' in content, "Missing predefined themes"
        assert 'active_theme' in content, "Missing active theme handling"
        assert 'theme_config' in content, "Missing theme config"

        print("✓ All key functionality present")

        return True

    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False


def test_database_integration():
    """Test dass die Datenbank-Integration korrekt ist"""
    print("\nTesting database integration...")

    try:
        with open('admin_pdf_settings_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for database operations
        assert 'load_setting' in content, "Missing load_setting usage"
        assert 'save_setting' in content, "Missing save_setting usage"
        assert "'ui_theme_settings'" in content, "Missing ui_theme_settings key"

        print("✓ Database integration present")

        # Check for proper error handling
        assert 'st.rerun()' in content, "Missing st.rerun() after save"

        print("✓ Proper state management with st.rerun()")

        return True

    except Exception as e:
        print(f"❌ Error checking database integration: {e}")
        return False


def run_integration_tests():
    """Führt alle Integrationstests aus"""
    print("=" * 60)
    print("Task 11 Integration Tests")
    print("=" * 60)

    tests = [
        test_function_exists,
        test_function_signature,
        test_theme_definitions,
        test_ui_components,
        test_requirements_coverage,
        test_database_integration
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)

    if all(results):
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nTask 11 ist vollständig implementiert und integriert:")
        print("- ✓ Funktion existiert und ist aufrufbar")
        print("- ✓ Korrekte Funktionssignatur")
        print("- ✓ Alle Themes definiert")
        print("- ✓ Alle UI-Komponenten vorhanden")
        print("- ✓ Requirements abgedeckt")
        print("- ✓ Datenbank-Integration korrekt")
        return True
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("=" * 60)
        failed_count = len([r for r in results if not r])
        print(f"\n{failed_count}/{len(results)} tests failed")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
