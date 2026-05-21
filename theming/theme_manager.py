"""
Theme Manager

Zentrale Verwaltung von Themes und Design-Tokens.
Lädt Themes aus JSON-Dateien und bietet API für Token-Zugriff.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from theming.theme_tokens import Theme


class ThemeManager:
    """Verwaltet Themes und Design-Tokens"""
    
    def __init__(self, themes_dir: Optional[str] = None):
        """
        Initialisiert ThemeManager
        
        Args:
            themes_dir: Pfad zum Themes-Verzeichnis (optional)
        """
        if themes_dir is None:
            # Standard: theming/themes/ Verzeichnis
            themes_dir = Path(__file__).parent / "themes"
        
        self.themes_dir = Path(themes_dir)
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        
        # Lade alle verfügbaren Themes
        self.load_themes()
    
    def load_themes(self) -> None:
        """Lädt alle verfügbaren Themes aus dem themes/ Verzeichnis"""
        if not self.themes_dir.exists():
            raise FileNotFoundError(f"Themes-Verzeichnis nicht gefunden: {self.themes_dir}")
        
        # Lade alle JSON-Dateien im Themes-Verzeichnis
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                theme = Theme.from_dict(theme_data)
                self.themes[theme.name] = theme
                
            except Exception as e:
                print(f"Warnung: Konnte Theme '{theme_file.name}' nicht laden: {e}")
                continue
        
        if not self.themes:
            raise ValueError("Keine Themes gefunden")
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """
        Gibt ein Theme nach Namen zurück
        
        Args:
            theme_name: Name des Themes
            
        Returns:
            Theme-Objekt oder None wenn nicht gefunden
        """
        return self.themes.get(theme_name)
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Setzt das aktuelle Theme
        
        Args:
            theme_name: Name des zu aktivierenden Themes
            
        Returns:
            True wenn erfolgreich, False wenn Theme nicht gefunden
        """
        theme = self.get_theme(theme_name)
        if theme:
            self.current_theme = theme
            return True
        return False
    
    def get_current_theme(self) -> str:
        """
        Gibt den Namen des aktuellen Themes zurück
        
        Returns:
            Name des aktuellen Themes oder 'shadcn-default' als Fallback
        """
        if self.current_theme:
            return self.current_theme.name
        
        # Fallback: Setze und gib shadcn-default zurück
        if 'shadcn-default' in self.themes:
            self.current_theme = self.themes['shadcn-default']
            return 'shadcn-default'
        
        # Wenn shadcn-default nicht existiert, nimm erstes verfügbares
        if self.themes:
            first_theme = list(self.themes.keys())[0]
            self.current_theme = self.themes[first_theme]
            return first_theme
        
        return 'none'
    
    def get_token(self, token_path: str) -> Optional[str]:
        """
        Gibt einen Design-Token-Wert zurück
        
        Args:
            token_path: Pfad zum Token (z.B. 'colors.primary', 'typography.font_family')
            
        Returns:
            Token-Wert als String oder None wenn nicht gefunden
        """
        if not self.current_theme:
            return None
        
        # Parse token path (z.B. "colors.primary")
        parts = token_path.split('.')
        if len(parts) != 2:
            return None
        
        category, token_name = parts
        
        # Hole entsprechende Token-Kategorie
        if category == 'colors':
            tokens = self.current_theme.colors
        elif category == 'typography':
            tokens = self.current_theme.typography
        elif category == 'spacing':
            tokens = self.current_theme.spacing
        elif category == 'shadows':
            tokens = self.current_theme.shadows
        elif category == 'borders':
            tokens = self.current_theme.borders
        elif category == 'animations':
            tokens = self.current_theme.animations
        else:
            return None
        
        # Hole Token-Wert
        return getattr(tokens, token_name, None)
    
    def get_available_themes(self) -> List[str]:
        """
        Gibt Liste aller verfügbaren Theme-Namen zurück
        
        Returns:
            Liste von Theme-Namen
        """
        return list(self.themes.keys())
    
    def get_theme_display_names(self) -> Dict[str, str]:
        """
        Gibt Dictionary mit Theme-Namen und Display-Namen zurück
        
        Returns:
            Dictionary {theme_name: display_name}
        """
        return {name: theme.display_name for name, theme in self.themes.items()}
    
    def reload_theme(self, theme_name: str) -> bool:
        """
        Lädt ein Theme neu aus der Datei
        
        Args:
            theme_name: Name des neu zu ladenden Themes
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        theme_file = self.themes_dir / f"{theme_name}.json"
        
        if not theme_file.exists():
            return False
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = Theme.from_dict(theme_data)
            self.themes[theme.name] = theme
            
            # Wenn dies das aktuelle Theme ist, aktualisiere es
            if self.current_theme and self.current_theme.name == theme_name:
                self.current_theme = theme
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Neuladen von Theme '{theme_name}': {e}")
            return False
    
    def get_fallback_theme(self) -> Theme:
        """
        Gibt ein Fallback-Theme zurück (shadcn-default oder erstes verfügbares)
        
        Returns:
            Fallback-Theme
        """
        # Versuche shadcn-default
        if 'shadcn-default' in self.themes:
            return self.themes['shadcn-default']
        
        # Sonst erstes verfügbares Theme
        if self.themes:
            return list(self.themes.values())[0]
        
        # Wenn gar keine Themes verfügbar, erstelle minimales Fallback
        return self._create_minimal_fallback()
    
    def _create_minimal_fallback(self) -> Theme:
        """Erstellt ein minimales Fallback-Theme"""
        from theming.theme_tokens import (
            ColorTokens, TypographyTokens, SpacingTokens,
            ShadowTokens, BorderTokens, AnimationTokens
        )

        return Theme(
            name='fallback',
            display_name='Fallback Theme',
            colors=ColorTokens(
                background='#ffffff',
                foreground='#0a0a0a',
                primary='#18181b',
                primary_foreground='#fafafa',
                secondary='#f4f4f5',
                secondary_foreground='#18181b',
                accent='#f4f4f5',
                accent_foreground='#18181b',
                success='#22c55e',
                warning='#f59e0b',
                error='#ef4444',
                info='#3b82f6',
                muted='#f4f4f5',
                muted_foreground='#71717a',
                border='#e4e4e7',
                input='#e4e4e7',
                ring='#18181b',
                chart_1='#38bdf8',
                chart_2='#34d399',
                chart_3='#f87171',
                chart_4='#fbbf24',
                chart_5='#a78bfa'
            ),
            typography=TypographyTokens(
                font_family='Inter, sans-serif',
                font_family_mono='monospace',
                font_size_xs='0.75rem',
                font_size_sm='0.875rem',
                font_size_base='1rem',
                font_size_lg='1.125rem',
                font_size_xl='1.25rem',
                font_size_2xl='1.5rem',
                font_weight_normal=400,
                font_weight_medium=500,
                font_weight_semibold=600,
                font_weight_bold=700,
                line_height_tight=1.25,
                line_height_normal=1.5,
                line_height_relaxed=1.75
            ),
            spacing=SpacingTokens(
                spacing_0='0',
                spacing_1='0.25rem',
                spacing_2='0.5rem',
                spacing_3='0.75rem',
                spacing_4='1rem',
                spacing_6='1.5rem',
                spacing_8='2rem',
                spacing_12='3rem',
                spacing_16='4rem'
            ),
            shadows=ShadowTokens(
                shadow_sm='0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                shadow_md='0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                shadow_lg='0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                shadow_xl='0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            ),
            borders=BorderTokens(
                border_width='1px',
                border_radius_sm='0.25rem',
                border_radius_md='0.375rem',
                border_radius_lg='0.5rem',
                border_radius_full='9999px'
            ),
            animations=AnimationTokens(
                transition_fast='150ms cubic-bezier(0.4, 0, 0.2, 1)',
                transition_base='200ms cubic-bezier(0.4, 0, 0.2, 1)',
                transition_slow='300ms cubic-bezier(0.4, 0, 0.2, 1)',
                easing_default='cubic-bezier(0.4, 0, 0.2, 1)'
            )
        )

    def generate_css(self, minified: bool = True, use_cache: bool = True) -> str:
        """
        Generiert CSS aus dem aktuellen Theme mit Performance-Optimierung

        Args:
            minified: Ob CSS minifiziert werden soll (Standard: True)
            use_cache: Ob Cache verwendet werden soll (Standard: True)

        Returns:
            Vollständiger CSS-String (minifiziert wenn aktiviert)

        Raises:
            ValueError: Wenn kein Theme aktiv ist
        """
        if not self.current_theme:
            raise ValueError("Kein Theme aktiv. Bitte setze ein Theme.")

        from theming.css_generator import CSSGenerator
        from theming.performance_optimizer import get_optimizer
        
        # Wenn Caching deaktiviert, generiere direkt
        if not use_cache:
            css_generator = CSSGenerator(self.current_theme)
            css = css_generator.generate_full_css()
            
            if minified:
                from theming.performance_optimizer import CSSMinifier
                return CSSMinifier.minify(css)
            return css
        
        # Verwende Performance-Optimizer mit Caching
        optimizer = get_optimizer()
        theme_data = self.current_theme.to_dict()
        
        def generate_func():
            css_generator = CSSGenerator(self.current_theme)
            return css_generator.generate_full_css()
        
        return optimizer.generate_optimized_css(
            self.current_theme.name,
            theme_data,
            generate_func,
            minified=minified
        )
    
    def get_contrast_text_color(self, background_color: Optional[str] = None) -> str:
        """
        Gibt optimale Textfarbe für Hintergrund zurück
        
        Args:
            background_color: Hintergrundfarbe (Hex). 
                            Falls None, wird theme.colors.background verwendet
        
        Returns:
            WCAG AA konforme Textfarbe (Hex)
        """
        if background_color is None:
            if self.current_theme:
                background_color = self.current_theme.colors.background
            else:
                background_color = '#FFFFFF'
        
        return get_accessible_text_color(background_color)
    
    def get_theme_colors_dict(self) -> dict:
        """
        Gibt alle Theme-Farben als Dictionary zurück
        
        Returns:
            Dictionary mit allen Farben des aktuellen Themes
        """
        if not self.current_theme:
            return {}
        
        return {
            'background': self.current_theme.colors.background,
            'foreground': self.current_theme.colors.foreground,
            'primary': self.current_theme.colors.primary,
            'primary_foreground': self.current_theme.colors.primary_foreground,
            'secondary': self.current_theme.colors.secondary,
            'secondary_foreground': self.current_theme.colors.secondary_foreground,
            'accent': self.current_theme.colors.accent,
            'accent_foreground': self.current_theme.colors.accent_foreground,
            'muted': self.current_theme.colors.muted,
            'muted_foreground': self.current_theme.colors.muted_foreground,
            'border': self.current_theme.colors.border,
            'success': self.current_theme.colors.success,
            'warning': self.current_theme.colors.warning,
            'error': self.current_theme.colors.error,
            'info': self.current_theme.colors.info,
        }
    
    def inject_auto_contrast(self) -> None:
        """
        Injiziert Auto-Contrast CSS in die App
        
        Sorgt dafür, dass Text immer lesbar ist auf jedem Hintergrund
        """
        theme_colors = self.get_theme_colors_dict()
        inject_auto_contrast_css(theme_colors)
    
    def is_dark_theme(self) -> bool:
        """
        Prüft ob aktuelles Theme dunkel ist
        
        Returns:
            True wenn dunkel, False wenn hell
        """
        if not self.current_theme:
            return False
        
        bg = self.current_theme.colors.background
        return not is_light_color(bg)
    
    def validate_contrast(self, bg_color: str, text_color: str) -> bool:
        """
        Validiert ob Farbkombination WCAG AA konform ist
        
        Args:
            bg_color: Hintergrundfarbe (Hex)
            text_color: Textfarbe (Hex)
        
        Returns:
            True wenn WCAG AA konform
        """
        return meets_wcag_aa(bg_color, text_color)

