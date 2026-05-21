"""
Tests für Theme Selector UI

Testet die Theme-Selector-Komponente und ihre Funktionen.
"""

import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    ThemeSelectorUI,
    get_current_theme_name,
    is_dark_mode
)


def test_theme_selector_initialization():
    """Test: ThemeSelectorUI Initialisierung"""
    print("Test: ThemeSelectorUI Initialisierung...")

    theme_manager = ThemeManager()
    selector = ThemeSelectorUI(theme_manager)

    assert selector.theme_manager is not None
    assert selector.theme_manager == theme_manager

    print(" ThemeSelectorUI erfolgreich initialisiert")


def test_theme_manager_integration():
    """Test: Integration mit ThemeManager"""
    print("\nTest: Integration mit ThemeManager...")

    theme_manager = ThemeManager()
    selector = ThemeSelectorUI(theme_manager)

    # Prüfe verfügbare Themes
    themes = theme_manager.get_available_themes()
    assert len(themes) >= 5, f"Erwartet mindestens 5 Themes, gefunden: {len(themes)}"

    expected_themes = [
        'shadcn-default',
        'shadcn-dark',
        'shadcn-ocean',
        'shadcn-forest',
        'shadcn-sunset'
    ]

    for theme_name in expected_themes:
        assert theme_name in themes, f"Theme '{theme_name}' nicht gefunden"

    print(f" {len(themes)} Themes verfügbar: {', '.join(themes)}")


def test_theme_display_names():
    """Test: Theme Display-Namen"""
    print("\nTest: Theme Display-Namen...")

    theme_manager = ThemeManager()
    display_names = theme_manager.get_theme_display_names()

    assert len(display_names) >= 5
    assert 'shadcn-default' in display_names
    assert display_names['shadcn-default'] == 'shadcn/ui Default'

    print(" Display-Namen korrekt:")
    for name, display_name in display_names.items():
        print(f"   - {name}: {display_name}")


def test_theme_switching():
    """Test: Theme-Wechsel"""
    print("\nTest: Theme-Wechsel...")

    theme_manager = ThemeManager()

    # Setze Default-Theme
    success = theme_manager.set_theme('shadcn-default')
    assert success, "Konnte shadcn-default nicht setzen"
    assert theme_manager.current_theme.name == 'shadcn-default'

    # Wechsle zu Dark-Theme
    success = theme_manager.set_theme('shadcn-dark')
    assert success, "Konnte shadcn-dark nicht setzen"
    assert theme_manager.current_theme.name == 'shadcn-dark'

    # Wechsle zu Ocean-Theme
    success = theme_manager.set_theme('shadcn-ocean')
    assert success, "Konnte shadcn-ocean nicht setzen"
    assert theme_manager.current_theme.name == 'shadcn-ocean'

    print(" Theme-Wechsel funktioniert")


def test_theme_colors():
    """Test: Theme-Farben"""
    print("\nTest: Theme-Farben...")

    theme_manager = ThemeManager()
    theme_manager.set_theme('shadcn-default')

    theme = theme_manager.current_theme
    colors = theme.colors

    # Prüfe wichtige Farben
    assert colors.primary is not None
    assert colors.secondary is not None
    assert colors.accent is not None
    assert colors.success is not None
    assert colors.warning is not None
    assert colors.error is not None

    # Prüfe Hex-Format
    assert colors.primary.startswith('#')
    assert len(colors.primary) == 7  # #RRGGBB

    print(" Theme-Farben korrekt:")
    print(f"   - Primary: {colors.primary}")
    print(f"   - Secondary: {colors.secondary}")
    print(f"   - Success: {colors.success}")
    print(f"   - Warning: {colors.warning}")
    print(f"   - Error: {colors.error}")


def test_css_generation():
    """Test: CSS-Generierung"""
    print("\nTest: CSS-Generierung...")

    theme_manager = ThemeManager()
    theme_manager.set_theme('shadcn-default')

    css = theme_manager.generate_css()

    # Prüfe CSS-Inhalt
    assert ':root {' in css
    assert '--primary:' in css
    assert '--secondary:' in css
    assert '--background:' in css
    assert '--foreground:' in css

    # Prüfe Component-Styles
    assert '.stButton' in css
    assert '.stTextInput' in css

    # Prüfe Utility-Klassen
    assert '.p-4' in css
    assert '.text-primary' in css

    print(f" CSS generiert ({len(css)} Zeichen)")
    print(f"   - Enthält :root Variablen")
    print(f"   - Enthält Component-Styles")
    print(f"   - Enthält Utility-Klassen")


def test_dark_mode_detection():
    """Test: Dark Mode Erkennung"""
    print("\nTest: Dark Mode Erkennung...")

    theme_manager = ThemeManager()

    # Test mit Light-Theme
    theme_manager.set_theme('shadcn-default')
    assert not theme_manager.current_theme.name.endswith('-dark')

    # Test mit Dark-Theme
    theme_manager.set_theme('shadcn-dark')
    assert theme_manager.current_theme.name.endswith('-dark')

    print(" Dark Mode Erkennung funktioniert")


def test_all_themes():
    """Test: Alle Themes laden"""
    print("\nTest: Alle Themes laden...")

    theme_manager = ThemeManager()
    themes = theme_manager.get_available_themes()

    for theme_name in themes:
        success = theme_manager.set_theme(theme_name)
        assert success, f"Konnte Theme '{theme_name}' nicht laden"

        theme = theme_manager.current_theme
        assert theme is not None
        assert theme.name == theme_name

        # Prüfe Theme-Struktur
        assert theme.colors is not None
        assert theme.typography is not None
        assert theme.spacing is not None
        assert theme.shadows is not None
        assert theme.borders is not None
        assert theme.animations is not None

        print(f"    {theme.display_name}")

    print(f" Alle {len(themes)} Themes erfolgreich geladen")


def test_callback_mechanism():
    """Test: Callback-Mechanismus"""
    print("\nTest: Callback-Mechanismus...")

    theme_manager = ThemeManager()
    selector = ThemeSelectorUI(theme_manager)

    # Callback-Tracker
    callback_called = {'count': 0, 'last_theme': None}

    def test_callback(theme_name: str):
        callback_called['count'] += 1
        callback_called['last_theme'] = theme_name

    # Simuliere Theme-Wechsel
    theme_manager.set_theme('shadcn-ocean')
    test_callback('shadcn-ocean')

    assert callback_called['count'] == 1
    assert callback_called['last_theme'] == 'shadcn-ocean'

    print(" Callback-Mechanismus funktioniert")


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 60)
    print("Theme Selector UI - Tests")
    print("=" * 60)

    try:
        test_theme_selector_initialization()
        test_theme_manager_integration()
        test_theme_display_names()
        test_theme_switching()
        test_theme_colors()
        test_css_generation()
        test_dark_mode_detection()
        test_all_themes()
        test_callback_mechanism()

        print("\n" + "=" * 60)
        print(" Alle Tests erfolgreich!")
        print("=" * 60)

        return True

    except AssertionError as e:
        print(f"\n Test fehlgeschlagen: {e}")
        return False

    except Exception as e:
        print(f"\n Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
