"""
Basis-Klasse für alle shadcn/ui-Komponenten

Diese Klasse stellt gemeinsame Funktionalität für alle shadcn-Komponenten bereit.
"""

from typing import Optional, Any
import streamlit as st


def get_accessible_text_color(bg_color: str) -> str:
    """Gibt passende Textfarbe (schwarz/weiß) basierend auf Hintergrundfarbe zurück."""
    # Einfache Implementierung: dunkler Hintergrund = weiße Schrift, heller = schwarze Schrift
    if not bg_color or bg_color.startswith('#'):
        # Hex-Color: prüfe Helligkeit
        if len(bg_color) >= 7:
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            # Relative Luminanz berechnen
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return '#000000' if luminance > 0.5 else '#ffffff'
    return '#000000'  # Standard: schwarze Schrift


class ShadcnComponent:
    """
    Basis-Klasse für alle shadcn/ui-Komponenten
    
    Diese Klasse bietet:
    - Zugriff auf Theme-Manager und Design-Tokens
    - Gemeinsame Utility-Methoden
    - Konsistente Rendering-Schnittstelle
    
    Attributes:
        theme_manager: Referenz zum ThemeManager für Token-Zugriff
    
    Example:
        ```python
        class MyComponent(ShadcnComponent):
            def render(self, **kwargs):
                primary_color = self.get_token('colors.primary')
                st.markdown(f"<div style='color: {primary_color}'>Content</div>")
        ```
    """
    
    def __init__(self, theme_manager: Optional[Any] = None):
        """
        Initialisiert die Komponente
        
        Args:
            theme_manager: ThemeManager-Instanz für Token-Zugriff.
                          Falls None, wird versucht aus session_state zu laden.
        """
        if theme_manager is None:
            # Versuche ThemeManager aus Session State zu laden
            self.theme_manager = st.session_state.get('theme_manager')
        else:
            self.theme_manager = theme_manager
    
    def get_token(self, path: str, default: str = "") -> str:
        """
        Shortcut für Theme-Token-Zugriff
        
        Args:
            path: Pfad zum Token (z.B. 'colors.primary', 'spacing.spacing_4')
            default: Fallback-Wert falls Token nicht gefunden wird
        
        Returns:
            Token-Wert als String
        
        Example:
            ```python
            primary = self.get_token('colors.primary')
            spacing = self.get_token('spacing.spacing_4')
            ```
        """
        if self.theme_manager is None:
            return default
        
        try:
            return self.theme_manager.get_token(path)
        except (AttributeError, KeyError):
            return default
    
    def get_css_var(self, token_path: str) -> str:
        """
        Gibt CSS-Variable für Token zurück
        
        Args:
            token_path: Pfad zum Token (z.B. 'colors.primary')
        
        Returns:
            CSS-Variable als String (z.B. 'var(--color-primary)')
        
        Example:
            ```python
            css_var = self.get_css_var('colors.primary')
            # Returns: 'var(--color-primary)'
            ```
        """
        # Konvertiere Token-Pfad zu CSS-Variable-Name
        var_name = token_path.replace('.', '-')
        return f"var(--{var_name})"
    
    def inject_css(self, css: str) -> None:
        """
        Injiziert CSS in die Streamlit-App
        
        Args:
            css: CSS-Code als String
        
        Example:
            ```python
            self.inject_css('''
                .my-component {
                    color: red;
                }
            ''')
            ```
        """
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def render(self, **kwargs) -> None:
        """
        Rendert die Komponente (muss von Subklassen überschrieben werden)
        
        Args:
            **kwargs: Komponenten-spezifische Parameter
        
        Raises:
            NotImplementedError: Wenn Methode nicht überschrieben wurde
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} muss die render() Methode implementieren"
        )
    
    def _generate_unique_id(self, prefix: str = "shadcn") -> str:
        """
        Generiert eine eindeutige ID für die Komponente
        
        Args:
            prefix: Präfix für die ID
        
        Returns:
            Eindeutige ID als String
        """
        import uuid
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    
    def _sanitize_html(self, html: str) -> str:
        """
        Sanitized HTML-Content (Basis-Implementierung)
        
        Args:
            html: HTML-String
        
        Returns:
            Sanitized HTML-String
        """
        from html import escape
        return escape(html)
    
    def get_contrast_text_color(self, background_color: str) -> str:
        """
        Gibt optimale Textfarbe für Hintergrund zurück (WCAG AA konform)
        
        Args:
            background_color: Hintergrundfarbe (Hex)
        
        Returns:
            WCAG AA konforme Textfarbe (Hex)
        
        Example:
            ```python
            bg_color = self.get_token('colors.primary')
            text_color = self.get_contrast_text_color(bg_color)
            ```
        """
        return get_accessible_text_color(background_color)
