"""
Demo: Theme Generator Tool

Demonstriert die Verwendung des Theme Generators.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.theme_generator import ThemeGenerator, ColorGenerator


def demo_color_operations():
    """Demonstriert Farb-Operationen"""
    print("\n" + "="*70)
    print("  COLOR OPERATIONS DEMO")
    print("="*70 + "\n")
    
    base_color = "#3b82f6"  # Blue
    print(f"Base Color: {base_color}")
    print("-" * 70)
    
    # Lighten/Darken
    print(f"Lighten 20%:  {ColorGenerator.lighten(base_color, 20)}")
    print(f"Darken 20%:   {ColorGenerator.darken(base_color, 20)}")
    
    # Saturate/Desaturate
    print(f"Saturate 20%: {ColorGenerator.saturate(base_color, 20)}")
    print(f"Desaturate 20%: {ColorGenerator.desaturate(base_color, 20)}")
    
    # Color harmonies
    print(f"\nComplementary: {ColorGenerator.get_complementary(base_color)}")
    
    triadic = ColorGenerator.get_triadic(base_color)
    print(f"Triadic 1:     {triadic[0]}")
    print(f"Triadic 2:     {triadic[1]}")
    
    analogous = ColorGenerator.get_analogous(base_color)
    print(f"Analogous 1:   {analogous[0]}")
    print(f"Analogous 2:   {analogous[1]}")
    
    split = ColorGenerator.get_split_complementary(base_color)
    print(f"Split Comp 1:  {split[0]}")
    print(f"Split Comp 2:  {split[1]}")


def demo_theme_generation():
    """Demonstriert Theme-Generierung"""
    print("\n" + "="*70)
    print("  THEME GENERATION DEMO")
    print("="*70 + "\n")
    
    # Generiere verschiedene Themes
    themes = [
        {"base_color": "#3b82f6", "theme_name": "demo-blue", "is_dark": False},
        {"base_color": "#8b5cf6", "theme_name": "demo-purple", "is_dark": False},
        {"base_color": "#10b981", "theme_name": "demo-green", "is_dark": False},
        {"base_color": "#3b82f6", "theme_name": "demo-blue-dark", "is_dark": True},
    ]
    
    for config in themes:
        print(f"\nGenerating: {config['theme_name']}")
        print("-" * 70)
        
        generator = ThemeGenerator(**config)
        
        # Zeige Vorschau
        print(generator.preview_theme())
        
        # Exportiere Theme
        filepath = generator.export_to_json("theming/themes")
        print(f"\n✅ Exported to: {filepath}\n")


def demo_color_palette():
    """Demonstriert Farbpaletten-Generierung"""
    print("\n" + "="*70)
    print("  COLOR PALETTE DEMO")
    print("="*70 + "\n")
    
    base_colors = [
        ("#3b82f6", "Blue"),
        ("#8b5cf6", "Purple"),
        ("#10b981", "Green"),
        ("#f59e0b", "Amber"),
        ("#ef4444", "Red"),
    ]
    
    for base_color, name in base_colors:
        print(f"\n{name} Palette (Base: {base_color})")
        print("-" * 70)
        
        generator = ThemeGenerator(base_color, f"demo-{name.lower()}", False)
        palette = generator.generate_color_palette()
        
        print(f"Primary:       {palette.primary}")
        print(f"Primary Light: {palette.primary_light}")
        print(f"Primary Dark:  {palette.primary_dark}")
        print(f"Secondary:     {palette.secondary}")
        print(f"Accent:        {palette.accent}")
        print(f"Success:       {palette.success}")
        print(f"Warning:       {palette.warning}")
        print(f"Error:         {palette.error}")
        print(f"Info:          {palette.info}")


def demo_chart_colors():
    """Demonstriert Chart-Farben-Generierung"""
    print("\n" + "="*70)
    print("  CHART COLORS DEMO")
    print("="*70 + "\n")
    
    base_color = "#3b82f6"
    generator = ThemeGenerator(base_color, "demo-charts", False)
    palette = generator.generate_color_palette()
    chart_colors = generator.generate_chart_colors(palette)
    
    print(f"Base Color: {base_color}")
    print("-" * 70)
    print("\nGenerated Chart Colors:")
    for i, color in enumerate(chart_colors, 1):
        print(f"Chart {i}: {color}")


def demo_usage_examples():
    """Zeigt Verwendungsbeispiele"""
    print("\n" + "="*70)
    print("  USAGE EXAMPLES")
    print("="*70 + "\n")
    
    examples = """
1. Interactive Mode:
   python tools/theme_generator.py --interactive

2. Generate Single Theme:
   python tools/theme_generator.py --base-color "#3b82f6" --name "my-theme"

3. Generate Dark Theme:
   python tools/theme_generator.py --base-color "#8b5cf6" --name "purple-dark" --dark

4. Preview Only (No Export):
   python tools/theme_generator.py --base-color "#10b981" --name "green" --preview-only

5. Batch Generate Multiple Themes:
   python tools/theme_generator.py --batch

6. Custom Output Directory:
   python tools/theme_generator.py --base-color "#ef4444" --name "red" --output "my_themes"

7. Programmatic Usage:
   from tools.theme_generator import ThemeGenerator
   
   generator = ThemeGenerator("#3b82f6", "my-theme", is_dark=False)
   theme = generator.generate_theme()
   filepath = generator.export_to_json()
   preview = generator.preview_theme()
    """
    
    print(examples)


def main():
    """Hauptfunktion"""
    print("\n" + "="*70)
    print("  THEME GENERATOR TOOL - DEMO")
    print("="*70)
    
    # Demonstriere verschiedene Features
    demo_color_operations()
    demo_color_palette()
    demo_chart_colors()
    demo_theme_generation()
    demo_usage_examples()
    
    print("\n" + "="*70)
    print("  DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
