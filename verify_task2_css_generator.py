"""
Verification Script: Task 2 - CSS Generator

Verifiziert dass alle Anforderungen von Task 2 erfüllt sind.
"""

from theming import ThemeManager, CSSGenerator


def verify_task2():
    """Verifiziert Task 2 Implementierung"""
    print("=" * 70)
    print("Task 2 Verification: CSS Generator")
    print("=" * 70)

    # Requirement 1.5: CSS-Generierung
    print("\n✓ Requirement 1.5: CSS-Generierung aus Theme-Tokens")
    theme_manager = ThemeManager()
    theme_manager.set_theme("shadcn-default")
    css_generator = CSSGenerator(theme_manager.current_theme)
    full_css = css_generator.generate_full_css()
    assert len(full_css) > 10000, "CSS sollte vollständig sein"
    print("  ✓ CSS wird aus Theme-Tokens generiert")
    print(f"  ✓ CSS-Größe: {len(full_css)} Zeichen")

    # Requirement 3.1: Button-Styles
    print("\n✓ Requirement 3.1: Button-Styles")
    component_styles = css_generator.generate_component_styles()
    assert ".stButton > button" in component_styles
    assert ":hover" in component_styles
    assert ":focus" in component_styles
    assert ":active" in component_styles
    print("  ✓ Button-Styles mit allen States implementiert")

    # Requirement 3.2: Input-Styles
    print("\n✓ Requirement 3.2: Input-Styles")
    assert ".stTextInput" in component_styles
    assert ".stNumberInput" in component_styles
    assert ".stTextArea" in component_styles
    print("  ✓ Input-Styles für Text, Number, TextArea implementiert")

    # Requirement 3.3: Select-Styles
    print("\n✓ Requirement 3.3: Select-Styles")
    assert ".stSelectbox" in component_styles
    assert ".stMultiSelect" in component_styles
    print("  ✓ Select-Styles implementiert")

    # Requirement 3.4: Slider-Styles
    print("\n✓ Requirement 3.4: Slider-Styles")
    assert ".stSlider" in component_styles
    print("  ✓ Slider-Styles implementiert")

    # Requirement 3.5: Checkbox/Radio-Styles
    print("\n✓ Requirement 3.5: Checkbox/Radio-Styles")
    assert ".stCheckbox" in component_styles
    assert ".stRadio" in component_styles
    print("  ✓ Checkbox und Radio-Styles implementiert")

    # Requirement 3.6: Tab-Styles
    print("\n✓ Requirement 3.6: Tab-Styles")
    assert ".stTabs" in component_styles
    print("  ✓ Tab-Styles implementiert")

    # Requirement 3.7: Hover/Focus/Active-States
    print("\n✓ Requirement 3.7: Hover/Focus/Active-States")
    hover_count = component_styles.count(":hover")
    focus_count = component_styles.count(":focus")
    active_count = component_styles.count(":active")
    print(f"  ✓ {hover_count} Hover-States")
    print(f"  ✓ {focus_count} Focus-States")
    print(f"  ✓ {active_count} Active-States")

    # Zusätzliche Verifikationen
    print("\n✓ Zusätzliche Features:")

    # CSS-Variablen
    css_vars = css_generator.generate_css_variables()
    assert ":root {" in css_vars
    print("  ✓ CSS-Variablen generiert")

    # Utility-Klassen
    utilities = css_generator.generate_utility_classes()
    assert ".p-4" in utilities
    assert ".text-lg" in utilities
    assert ".bg-primary" in utilities
    print("  ✓ Utility-Klassen generiert")

    # ThemeManager Integration
    css_from_manager = theme_manager.generate_css()
    assert css_from_manager == full_css
    print("  ✓ ThemeManager.generate_css() funktioniert")

    # Multi-Theme Support
    themes_tested = 0
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        css = theme_manager.generate_css()
        assert len(css) > 10000
        themes_tested += 1
    print(f"  ✓ {themes_tested} Themes getestet")

    print("\n" + "=" * 70)
    print("Task 2 Verification: ERFOLGREICH ✓")
    print("=" * 70)
    print("\nAlle Requirements erfüllt:")
    print("  ✓ Requirement 1.5: CSS-Generierung")
    print("  ✓ Requirement 3.1: Button-Styles")
    print("  ✓ Requirement 3.2: Input-Styles")
    print("  ✓ Requirement 3.3: Select-Styles")
    print("  ✓ Requirement 3.4: Slider-Styles")
    print("  ✓ Requirement 3.5: Checkbox/Radio-Styles")
    print("  ✓ Requirement 3.6: Tab-Styles")
    print("  ✓ Requirement 3.7: Hover/Focus/Active-States")
    print("\nTask 2 ist vollständig implementiert und getestet!")


if __name__ == "__main__":
    verify_task2()
