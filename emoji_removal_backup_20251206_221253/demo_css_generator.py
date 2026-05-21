"""
Demo: CSS Generator

Demonstriert die Verwendung des CSS Generators.
"""

from theming.theme_manager import ThemeManager
from theming.css_generator import CSSGenerator


def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("CSS Generator Demo")
    print("=" * 70)

    # Initialisiere ThemeManager
    print("\n1. Initialisiere ThemeManager...")
    theme_manager = ThemeManager()
    print(f"   ✓ {len(theme_manager.themes)} Themes geladen")

    # Setze Theme
    theme_name = "shadcn-default"
    print(f"\n2. Setze Theme: {theme_name}")
    theme_manager.set_theme(theme_name)
    print(f"   ✓ Theme '{theme_manager.current_theme.display_name}' aktiv")

    # Erstelle CSS Generator
    print("\n3. Erstelle CSS Generator...")
    css_generator = CSSGenerator(theme_manager.current_theme)
    print("   ✓ CSS Generator erstellt")

    # Generiere CSS-Variablen
    print("\n4. Generiere CSS-Variablen...")
    css_vars = css_generator.generate_css_variables()
    print(f"   ✓ {len(css_vars)} Zeichen generiert")
    print("\n   Vorschau (erste 500 Zeichen):")
    print("   " + "-" * 66)
    for line in css_vars[:500].split('\n'):
        print(f"   {line}")
    print("   ...")

    # Generiere Component-Styles
    print("\n5. Generiere Component-Styles...")
    component_styles = css_generator.generate_component_styles()
    print(f"   ✓ {len(component_styles)} Zeichen generiert")
    print(f"   ✓ Enthält Styles für:")
    print("     - Buttons")
    print("     - Inputs (Text, Number, TextArea)")
    print("     - Selects (Selectbox, MultiSelect)")
    print("     - Sliders")
    print("     - Checkboxes & Radios")
    print("     - Tabs")
    print("     - Containers & Expanders")

    # Generiere Utility-Klassen
    print("\n6. Generiere Utility-Klassen...")
    utilities = css_generator.generate_utility_classes()
    print(f"   ✓ {len(utilities)} Zeichen generiert")
    print(f"   ✓ Enthält Utilities für:")
    print("     - Spacing (padding, margin)")
    print("     - Typography (font-size, font-weight)")
    print("     - Colors (text, background)")
    print("     - Borders")
    print("     - Shadows")
    print("     - Transitions")

    # Generiere vollständiges CSS
    print("\n7. Generiere vollständiges CSS...")
    full_css = css_generator.generate_full_css()
    print(f"   ✓ {len(full_css)} Zeichen generiert")
    print(f"   ✓ {len(full_css.split(chr(10)))} Zeilen")

    # Speichere CSS in Datei (optional)
    output_file = "theming/generated_theme.css"
    print(f"\n8. Speichere CSS in Datei: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_css)
    print(f"   ✓ CSS gespeichert")

    # Teste mit verschiedenen Themes
    print("\n9. Teste mit verschiedenen Themes...")
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        css_gen = CSSGenerator(theme_manager.current_theme)
        css = css_gen.generate_full_css()
        print(f"   ✓ {theme_name}: {len(css)} Zeichen")

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
    print("=" * 70)


if __name__ == "__main__":
    main()
