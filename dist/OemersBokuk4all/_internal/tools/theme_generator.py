"""
Theme Generator Tool

Generiert automatisch vollständige shadcn/ui Themes aus einer Basis-Farbe.
Berechnet Komplementär- und Akzentfarben, generiert alle notwendigen Tokens
und exportiert das Theme als JSON.

Usage:
    python tools/theme_generator.py --base-color "#3b82f6" --name "my-theme"
    python tools/theme_generator.py --interactive
"""

import json
import colorsys
import argparse
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ColorPalette:
    """Generierte Farbpalette"""
    primary: str
    primary_light: str
    primary_dark: str
    secondary: str
    accent: str
    success: str
    warning: str
    error: str
    info: str


class ColorGenerator:
    """Generiert Farben aus einer Basis-Farbe"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Konvertiert Hex zu RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Konvertiert RGB zu Hex"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Konvertiert RGB zu HSL"""
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    @staticmethod
    def hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Konvertiert HSL zu RGB"""
        h, s, l = hsl
        h, s, l = h / 360, s / 100, l / 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @classmethod
    def lighten(cls, hex_color: str, amount: float) -> str:
        """Hellt eine Farbe auf (amount: 0-100)"""
        rgb = cls.hex_to_rgb(hex_color)
        h, s, l = cls.rgb_to_hsl(rgb)
        l = min(100, l + amount)
        new_rgb = cls.hsl_to_rgb((h, s, l))
        return cls.rgb_to_hex(new_rgb)
    
    @classmethod
    def darken(cls, hex_color: str, amount: float) -> str:
        """Dunkelt eine Farbe ab (amount: 0-100)"""
        rgb = cls.hex_to_rgb(hex_color)
        h, s, l = cls.rgb_to_hsl(rgb)
        l = max(0, l - amount)
        new_rgb = cls.hsl_to_rgb((h, s, l))
        return cls.rgb_to_hex(new_rgb)
    
    @classmethod
    def saturate(cls, hex_color: str, amount: float) -> str:
        """Erhöht die Sättigung (amount: 0-100)"""
        rgb = cls.hex_to_rgb(hex_color)
        h, s, l = cls.rgb_to_hsl(rgb)
        s = min(100, s + amount)
        new_rgb = cls.hsl_to_rgb((h, s, l))
        return cls.rgb_to_hex(new_rgb)
    
    @classmethod
    def desaturate(cls, hex_color: str, amount: float) -> str:
        """Verringert die Sättigung (amount: 0-100)"""
        rgb = cls.hex_to_rgb(hex_color)
        h, s, l = cls.rgb_to_hsl(rgb)
        s = max(0, s - amount)
        new_rgb = cls.hsl_to_rgb((h, s, l))
        return cls.rgb_to_hex(new_rgb)
    
    @classmethod
    def rotate_hue(cls, hex_color: str, degrees: float) -> str:
        """Rotiert den Farbton (degrees: 0-360)"""
        rgb = cls.hex_to_rgb(hex_color)
        h, s, l = cls.rgb_to_hsl(rgb)
        h = (h + degrees) % 360
        new_rgb = cls.hsl_to_rgb((h, s, l))
        return cls.rgb_to_hex(new_rgb)
    
    @classmethod
    def get_complementary(cls, hex_color: str) -> str:
        """Berechnet Komplementärfarbe (180° Rotation)"""
        return cls.rotate_hue(hex_color, 180)
    
    @classmethod
    def get_triadic(cls, hex_color: str) -> Tuple[str, str]:
        """Berechnet triadische Farben (120° und 240° Rotation)"""
        return (
            cls.rotate_hue(hex_color, 120),
            cls.rotate_hue(hex_color, 240)
        )
    
    @classmethod
    def get_analogous(cls, hex_color: str) -> Tuple[str, str]:
        """Berechnet analoge Farben (±30° Rotation)"""
        return (
            cls.rotate_hue(hex_color, -30),
            cls.rotate_hue(hex_color, 30)
        )
    
    @classmethod
    def get_split_complementary(cls, hex_color: str) -> Tuple[str, str]:
        """Berechnet split-komplementäre Farben"""
        return (
            cls.rotate_hue(hex_color, 150),
            cls.rotate_hue(hex_color, 210)
        )


class ThemeGenerator:
    """Generiert vollständige Themes aus einer Basis-Farbe"""
    
    def __init__(self, base_color: str, theme_name: str, is_dark: bool = False):
        self.base_color = base_color
        self.theme_name = theme_name
        self.is_dark = is_dark
        self.color_gen = ColorGenerator()
    
    def generate_color_palette(self) -> ColorPalette:
        """Generiert vollständige Farbpalette"""
        # Primary colors
        primary = self.base_color
        primary_light = self.color_gen.lighten(primary, 20)
        primary_dark = self.color_gen.darken(primary, 20)
        
        # Secondary (analogous color)
        analogous = self.color_gen.get_analogous(primary)
        secondary = analogous[0]
        
        # Accent (complementary color)
        accent = self.color_gen.get_complementary(primary)
        
        # Semantic colors (fixed, professional colors)
        success = "#22c55e"  # Green
        warning = "#f59e0b"  # Amber
        error = "#ef4444"    # Red
        info = self.base_color  # Use base color for info
        
        return ColorPalette(
            primary=primary,
            primary_light=primary_light,
            primary_dark=primary_dark,
            secondary=secondary,
            accent=accent,
            success=success,
            warning=warning,
            error=error,
            info=info
        )
    
    def generate_chart_colors(self, palette: ColorPalette) -> List[str]:
        """Generiert Chart-Farben basierend auf der Palette"""
        # Verwende triadische Farben für Vielfalt
        triadic = self.color_gen.get_triadic(palette.primary)
        
        return [
            palette.primary,
            palette.accent,
            triadic[0],
            triadic[1],
            palette.secondary
        ]
    
    def generate_theme(self) -> Dict:
        """Generiert vollständiges Theme"""
        palette = self.generate_color_palette()
        chart_colors = self.generate_chart_colors(palette)
        
        # Base colors (light or dark mode)
        if self.is_dark:
            background = "#0a0a0a"
            foreground = "#fafafa"
            muted = "#27272a"
            muted_foreground = "#a1a1aa"
            border = "#27272a"
            input_bg = "#27272a"
        else:
            background = "#ffffff"
            foreground = "#0a0a0a"
            muted = "#f4f4f5"
            muted_foreground = "#71717a"
            border = "#e4e4e7"
            input_bg = "#e4e4e7"
        
        # Determine foreground colors for primary/secondary/accent
        primary_fg = self._get_contrasting_color(palette.primary)
        secondary_fg = self._get_contrasting_color(palette.secondary)
        accent_fg = self._get_contrasting_color(palette.accent)
        
        theme = {
            "name": self.theme_name,
            "display_name": self.theme_name.replace('-', ' ').title(),
            "colors": {
                "background": background,
                "foreground": foreground,
                "primary": palette.primary,
                "primary_foreground": primary_fg,
                "secondary": palette.secondary,
                "secondary_foreground": secondary_fg,
                "accent": palette.accent,
                "accent_foreground": accent_fg,
                "success": palette.success,
                "warning": palette.warning,
                "error": palette.error,
                "info": palette.info,
                "muted": muted,
                "muted_foreground": muted_foreground,
                "border": border,
                "input": input_bg,
                "ring": palette.primary,
                "chart_1": chart_colors[0],
                "chart_2": chart_colors[1],
                "chart_3": chart_colors[2],
                "chart_4": chart_colors[3],
                "chart_5": chart_colors[4]
            },
            "typography": {
                "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                "font_family_mono": "'Fira Code', 'Courier New', monospace",
                "font_size_xs": "0.75rem",
                "font_size_sm": "0.875rem",
                "font_size_base": "1rem",
                "font_size_lg": "1.125rem",
                "font_size_xl": "1.25rem",
                "font_size_2xl": "1.5rem",
                "font_weight_normal": 400,
                "font_weight_medium": 500,
                "font_weight_semibold": 600,
                "font_weight_bold": 700,
                "line_height_tight": 1.25,
                "line_height_normal": 1.5,
                "line_height_relaxed": 1.75
            },
            "spacing": {
                "spacing_0": "0",
                "spacing_1": "0.25rem",
                "spacing_2": "0.5rem",
                "spacing_3": "0.75rem",
                "spacing_4": "1rem",
                "spacing_6": "1.5rem",
                "spacing_8": "2rem",
                "spacing_12": "3rem",
                "spacing_16": "4rem"
            },
            "shadows": {
                "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
            },
            "borders": {
                "border_width": "1px",
                "border_radius_sm": "0.25rem",
                "border_radius_md": "0.375rem",
                "border_radius_lg": "0.5rem",
                "border_radius_full": "9999px"
            },
            "animations": {
                "transition_fast": "150ms cubic-bezier(0.4, 0, 0.2, 1)",
                "transition_base": "200ms cubic-bezier(0.4, 0, 0.2, 1)",
                "transition_slow": "300ms cubic-bezier(0.4, 0, 0.2, 1)",
                "easing_default": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
        }
        
        return theme
    
    def _get_contrasting_color(self, hex_color: str) -> str:
        """Bestimmt kontrastierende Vordergrundfarbe (hell oder dunkel)"""
        rgb = self.color_gen.hex_to_rgb(hex_color)
        # Berechne relative Luminanz
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        # Wenn Farbe hell ist, verwende dunklen Text, sonst hellen Text
        return "#0a0a0a" if luminance > 0.5 else "#fafafa"
    
    def export_to_json(self, output_dir: str = "theming/themes") -> str:
        """Exportiert Theme als JSON-Datei"""
        theme = self.generate_theme()
        
        # Erstelle Output-Verzeichnis falls nicht vorhanden
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Schreibe JSON-Datei
        filename = f"{self.theme_name}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(theme, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def preview_theme(self) -> str:
        """Generiert eine Vorschau des Themes als formatierter String"""
        theme = self.generate_theme()
        palette = self.generate_color_palette()
        
        preview = f"""

                    THEME PREVIEW                             

 Name: {theme['display_name']:<52} 
 Mode: {'Dark' if self.is_dark else 'Light':<52} 

                    COLOR PALETTE                             

 Primary:     {palette.primary:<45} 
 Secondary:   {palette.secondary:<45} 
 Accent:      {palette.accent:<45} 
 Success:     {palette.success:<45} 
 Warning:     {palette.warning:<45} 
 Error:       {palette.error:<45} 
 Info:        {palette.info:<45} 

                    CHART COLORS                              

"""
        chart_colors = self.generate_chart_colors(palette)
        for i, color in enumerate(chart_colors, 1):
            preview += f" Chart {i}:     {color:<45} \n"
        
        preview += ""
        
        return preview


def interactive_mode():
    """Interaktiver Modus für Theme-Generierung"""
    print("\n" + "="*60)
    print("  SHADCN/UI THEME GENERATOR - Interactive Mode")
    print("="*60 + "\n")
    
    # Basis-Farbe eingeben
    print("Enter base color (hex format, e.g., #3b82f6):")
    base_color = input("> ").strip()
    
    if not base_color.startswith('#'):
        base_color = '#' + base_color
    
    # Theme-Name eingeben
    print("\nEnter theme name (e.g., my-custom-theme):")
    theme_name = input("> ").strip().lower().replace(' ', '-')
    
    # Dark Mode?
    print("\nIs this a dark theme? (y/n):")
    is_dark = input("> ").strip().lower() == 'y'
    
    # Theme generieren
    print("\n" + "-"*60)
    print("Generating theme...")
    print("-"*60 + "\n")
    
    generator = ThemeGenerator(base_color, theme_name, is_dark)
    
    # Vorschau anzeigen
    print(generator.preview_theme())
    
    # Exportieren?
    print("\n\nExport theme to JSON? (y/n):")
    if input("> ").strip().lower() == 'y':
        filepath = generator.export_to_json()
        print(f"\n Theme exported to: {filepath}")
    else:
        print("\n Theme not exported.")
    
    print("\n" + "="*60 + "\n")


def batch_generate_themes():
    """Generiert mehrere vordefinierte Themes"""
    themes_config = [
        {"base_color": "#3b82f6", "theme_name": "shadcn-blue", "is_dark": False},
        {"base_color": "#3b82f6", "theme_name": "shadcn-blue-dark", "is_dark": True},
        {"base_color": "#8b5cf6", "theme_name": "shadcn-purple", "is_dark": False},
        {"base_color": "#8b5cf6", "theme_name": "shadcn-purple-dark", "is_dark": True},
        {"base_color": "#10b981", "theme_name": "shadcn-green", "is_dark": False},
        {"base_color": "#f59e0b", "theme_name": "shadcn-amber", "is_dark": False},
        {"base_color": "#ef4444", "theme_name": "shadcn-red", "is_dark": False},
        {"base_color": "#06b6d4", "theme_name": "shadcn-cyan", "is_dark": False},
    ]
    
    print("\n" + "="*60)
    print("  Batch Generating Themes...")
    print("="*60 + "\n")
    
    for config in themes_config:
        generator = ThemeGenerator(**config)
        filepath = generator.export_to_json()
        print(f" Generated: {config['theme_name']}")
    
    print(f"\n Successfully generated {len(themes_config)} themes!")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate shadcn/ui themes from a base color",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python theme_generator.py --interactive
  
  # Generate single theme
  python theme_generator.py --base-color "#3b82f6" --name "my-theme"
  
  # Generate dark theme
  python theme_generator.py --base-color "#8b5cf6" --name "purple-dark" --dark
  
  # Batch generate multiple themes
  python theme_generator.py --batch
  
  # Preview only (no export)
  python theme_generator.py --base-color "#10b981" --name "green" --preview-only
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--base-color', '-c',
        type=str,
        help='Base color in hex format (e.g., #3b82f6)'
    )
    
    parser.add_argument(
        '--name', '-n',
        type=str,
        help='Theme name (e.g., my-custom-theme)'
    )
    
    parser.add_argument(
        '--dark', '-d',
        action='store_true',
        help='Generate dark theme variant'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='theming/themes',
        help='Output directory for theme files (default: theming/themes)'
    )
    
    parser.add_argument(
        '--preview-only', '-p',
        action='store_true',
        help='Only show preview, do not export'
    )
    
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Generate multiple predefined themes'
    )
    
    args = parser.parse_args()
    
    # Batch mode
    if args.batch:
        batch_generate_themes()
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Command-line mode
    if not args.base_color or not args.name:
        parser.print_help()
        print("\n Error: --base-color and --name are required (or use --interactive)")
        return
    
    # Generiere Theme
    generator = ThemeGenerator(args.base_color, args.name, args.dark)
    
    # Zeige Vorschau
    print(generator.preview_theme())
    
    # Exportiere (falls nicht preview-only)
    if not args.preview_only:
        filepath = generator.export_to_json(args.output)
        print(f"\n Theme exported to: {filepath}")
    else:
        print("\n(Preview only - not exported)")


if __name__ == "__main__":
    main()
