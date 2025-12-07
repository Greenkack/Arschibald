"""
Test: CSS Generator

Testet die CSS Generator Implementierung gegen die Requirements.
"""

from theming.theme_manager import ThemeManager
from theming.css_generator import CSSGenerator


def test_css_generator():
    """Testet CSS Generator Funktionalität"""
    print("=" * 70)
    print("CSS Generator Tests")
    print("=" * 70)

    # Setup
    theme_manager = ThemeManager()
    theme_manager.set_theme("shadcn-default")
    css_generator = CSSGenerator(theme_manager.current_theme)

    # Test 1: CSS-Variablen-Generierung
    print("\n Test 1: CSS-Variablen-Generierung")
    css_vars = css_generator.generate_css_variables()
    assert ":root {" in css_vars, "CSS sollte :root enthalten"
    assert "--background:" in css_vars, "Sollte background Variable haben"
    assert "--primary:" in css_vars, "Sollte primary Variable haben"
    assert "--font-family:" in css_vars, "Sollte font-family Variable haben"
    assert "--spacing-4:" in css_vars, "Sollte spacing Variable haben"
    assert "--shadow-md:" in css_vars, "Sollte shadow Variable haben"
    assert "--border-radius-md:" in css_vars, "Sollte border-radius haben"
    assert "--transition-base:" in css_vars, "Sollte transition Variable haben"
    print("   Alle CSS-Variablen vorhanden")

    # Test 2: Button-Styles (Requirement 3.1)
    print("\n Test 2: Button-Styles (Requirement 3.1)")
    component_styles = css_generator.generate_component_styles()
    assert ".stButton > button" in component_styles, "Button Styles fehlen"
    assert "background-color: var(--primary)" in component_styles
    assert ":hover" in component_styles, "Hover-States fehlen"
    assert ":focus" in component_styles, "Focus-States fehlen"
    assert ":active" in component_styles, "Active-States fehlen"
    print("   Button-Styles mit allen States vorhanden")

    # Test 3: Input-Styles (Requirement 3.2)
    print("\n Test 3: Input-Styles (Requirement 3.2)")
    assert ".stTextInput" in component_styles, "TextInput Styles fehlen"
    assert ".stNumberInput" in component_styles, "NumberInput Styles fehlen"
    assert ".stTextArea" in component_styles, "TextArea Styles fehlen"
    assert "border: var(--border-width)" in component_styles
    print("   Input-Styles für Text, Number, TextArea vorhanden")

    # Test 4: Select-Styles (Requirement 3.3)
    print("\n Test 4: Select-Styles (Requirement 3.3)")
    assert ".stSelectbox" in component_styles, "Selectbox Styles fehlen"
    assert ".stMultiSelect" in component_styles, "MultiSelect Styles fehlen"
    print("   Select-Styles vorhanden")

    # Test 5: Slider-Styles (Requirement 3.4)
    print("\n Test 5: Slider-Styles (Requirement 3.4)")
    assert ".stSlider" in component_styles, "Slider Styles fehlen"
    print("   Slider-Styles vorhanden")

    # Test 6: Checkbox/Radio-Styles (Requirement 3.5)
    print("\n Test 6: Checkbox/Radio-Styles (Requirement 3.5)")
    assert ".stCheckbox" in component_styles, "Checkbox Styles fehlen"
    assert ".stRadio" in component_styles, "Radio Styles fehlen"
    print("   Checkbox und Radio-Styles vorhanden")

    # Test 7: Tab-Styles (Requirement 3.6)
    print("\n Test 7: Tab-Styles (Requirement 3.6)")
    assert ".stTabs" in component_styles, "Tab Styles fehlen"
    assert '[data-baseweb="tab"]' in component_styles
    print("   Tab-Styles vorhanden")

    # Test 8: Hover/Focus/Active States (Requirement 3.7)
    print("\n Test 8: Hover/Focus/Active States (Requirement 3.7)")
    hover_count = component_styles.count(":hover")
    focus_count = component_styles.count(":focus")
    active_count = component_styles.count(":active")
    print(f"   {hover_count} Hover-States")
    print(f"   {focus_count} Focus-States")
    print(f"   {active_count} Active-States")
    assert hover_count > 5, "Sollte mehrere Hover-States haben"
    assert focus_count > 2, "Sollte mehrere Focus-States haben"

    # Test 9: Utility-Klassen
    print("\n Test 9: Utility-Klassen")
    utilities = css_generator.generate_utility_classes()
    assert ".p-0" in utilities, "Padding Utilities fehlen"
    assert ".px-4" in utilities, "Padding-X Utilities fehlen"
    assert ".py-2" in utilities, "Padding-Y Utilities fehlen"
    assert ".m-4" in utilities, "Margin Utilities fehlen"
    assert ".text-sm" in utilities, "Text-Size Utilities fehlen"
    assert ".font-bold" in utilities, "Font-Weight Utilities fehlen"
    assert ".text-primary" in utilities, "Text-Color Utilities fehlen"
    assert ".bg-muted" in utilities, "Background Utilities fehlen"
    assert ".border" in utilities, "Border Utilities fehlen"
    assert ".rounded-md" in utilities, "Border-Radius Utilities fehlen"
    assert ".shadow-lg" in utilities, "Shadow Utilities fehlen"
    assert ".transition-base" in utilities, "Transition Utilities fehlen"
    print("   Alle Utility-Klassen vorhanden")

    # Test 10: Vollständiges CSS (Requirement 1.5)
    print("\n Test 10: Vollständiges CSS (Requirement 1.5)")
    full_css = css_generator.generate_full_css()
    assert len(full_css) > 10000, "CSS sollte mindestens 10KB sein"
    assert ":root {" in full_css, "Sollte CSS-Variablen enthalten"
    assert ".stButton" in full_css, "Sollte Component-Styles enthalten"
    assert ".p-0" in full_css, "Sollte Utility-Klassen enthalten"
    print(f"   Vollständiges CSS: {len(full_css)} Zeichen")

    # Test 11: ThemeManager.generate_css()
    print("\n Test 11: ThemeManager.generate_css()")
    css_from_manager = theme_manager.generate_css()
    assert len(css_from_manager) > 10000, "CSS sollte generiert werden"
    assert css_from_manager == full_css, "CSS sollte identisch sein"
    print("   ThemeManager.generate_css() funktioniert")

    # Test 12: Verschiedene Themes
    print("\n Test 12: CSS für verschiedene Themes")
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        css = theme_manager.generate_css()
        assert len(css) > 10000, f"CSS für {theme_name} zu kurz"
        print(f"   {theme_name}: {len(css)} Zeichen")

    # Test 13: CSS-Variablen verwenden Theme-Tokens
    print("\n Test 13: CSS-Variablen verwenden Theme-Tokens")
    theme_manager.set_theme("shadcn-dark")
    dark_css = theme_manager.generate_css()
    assert "#0a0a0a" in dark_css, "Dark theme sollte dunkle Farben haben"
    theme_manager.set_theme("shadcn-ocean")
    ocean_css = theme_manager.generate_css()
    assert "#0ea5e9" in ocean_css, "Ocean theme sollte blaue Farben haben"
    print("   CSS verwendet korrekte Theme-Tokens")

    # Test 14: Transitions in allen interaktiven Elementen
    print("\n Test 14: Transitions in interaktiven Elementen")
    transition_count = component_styles.count("transition:")
    print(f"   {transition_count} Transition-Definitionen")
    assert transition_count >= 9, "Sollte Transitions haben"

    print("\n" + "=" * 70)
    print("Alle Tests bestanden! ")
    print("=" * 70)


if __name__ == "__main__":
    test_css_generator()
