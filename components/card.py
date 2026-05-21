"""
shadcn/ui Card-Komponente für Streamlit

Diese Komponente bietet eine moderne Card mit Header, Body und Footer.
"""

from typing import Optional, Literal, Callable, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Card(ShadcnComponent):
    """
    shadcn/ui Card-Komponente
    
    Eine flexible Card-Komponente mit Header, Body und Footer.
    Unterstützt verschiedene Varianten und Hover-Effekte.
    
    Features:
    - Header mit optionalem Titel, Beschreibung, Icon und Badge
    - Body für Hauptinhalt
    - Footer für Aktionen oder zusätzliche Informationen
    - Varianten: default, outlined, elevated
    - Hover-Effekte mit sanften Transitions
    - Responsive Design
    
    Example:
        ```python
        from components import Card
        
        card = Card()
        card.render(
            title="Meine Card",
            description="Eine Beschreibung",
            content="Hauptinhalt hier",
            footer="Footer-Text",
            variant="elevated"
        )
        ```
    """
    
    def render(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        footer: Optional[str] = None,
        variant: Literal["default", "outlined", "elevated"] = "default",
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        badge_variant: Literal["default", "success", "warning", "error", "info"] = "default",
        hover_effect: bool = True,
        clickable: bool = False,
        on_click: Optional[Callable] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine Card-Komponente
        
        Args:
            title: Titel der Card (optional)
            description: Beschreibung unter dem Titel (optional)
            content: Hauptinhalt der Card (optional)
            footer: Footer-Inhalt (optional)
            variant: Card-Variante ('default', 'outlined', 'elevated')
            icon: Icon für den Header (optional, z.B. Emoji oder Unicode)
            badge: Badge-Text für den Header (optional)
            badge_variant: Badge-Farbe ('default', 'success', 'warning', 'error', 'info')
            hover_effect: Ob Hover-Effekt angezeigt werden soll
            clickable: Ob Card klickbar sein soll
            on_click: Callback-Funktion bei Klick (nur wenn clickable=True)
            custom_css: Zusätzliches Custom-CSS (optional)
            key: Eindeutiger Key für die Komponente (optional)
        
        Example:
            ```python
            card = Card()
            card.render(
                title="Solar-Analyse",
                description="Aktuelle Daten",
                content="Hier steht der Inhalt",
                variant="elevated",
                badge="Neu",
                badge_variant="success"
            )
            ```
        """
        # Generiere eindeutige ID
        card_id = key or self._generate_unique_id("card")
        
        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_color = self.get_token('colors.muted', '#f4f4f5')
        muted_fg_color = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token('borders.border_radius_lg', '0.5rem')
        spacing_4 = self.get_token('spacing.spacing_4', '1rem')
        spacing_6 = self.get_token('spacing.spacing_6', '1.5rem')
        shadow_sm = self.get_token('shadows.shadow_sm', '0 1px 2px 0 rgba(0, 0, 0, 0.05)')
        shadow_md = self.get_token('shadows.shadow_md', '0 4px 6px -1px rgba(0, 0, 0, 0.1)')
        shadow_lg = self.get_token('shadows.shadow_lg', '0 10px 15px -3px rgba(0, 0, 0, 0.1)')
        transition = self.get_token('animations.transition_base', '200ms cubic-bezier(0.4, 0, 0.2, 1)')
        
        # Badge-Farben
        badge_colors = {
            'default': (muted_color, fg_color),
            'success': (self.get_token('colors.success', '#22c55e'), '#ffffff'),
            'warning': (self.get_token('colors.warning', '#f59e0b'), '#ffffff'),
            'error': (self.get_token('colors.error', '#ef4444'), '#ffffff'),
            'info': (self.get_token('colors.info', '#3b82f6'), '#ffffff'),
        }
        badge_bg, badge_fg = badge_colors.get(badge_variant, badge_colors['default'])
        
        # Varianten-spezifische Styles
        variant_styles = {
            'default': f"""
                background: {bg_color};
                border: 1px solid {border_color};
                box-shadow: {shadow_sm};
            """,
            'outlined': f"""
                background: {bg_color};
                border: 2px solid {border_color};
                box-shadow: none;
            """,
            'elevated': f"""
                background: {bg_color};
                border: 1px solid {border_color};
                box-shadow: {shadow_md};
            """
        }
        
        # Hover-Effekt
        hover_style = ""
        if hover_effect:
            if variant == 'elevated':
                hover_style = f"""
                    box-shadow: {shadow_lg};
                    transform: translateY(-2px);
                """
            else:
                hover_style = f"""
                    box-shadow: {shadow_md};
                    border-color: {self.get_token('colors.primary', '#18181b')};
                """
        
        # Clickable-Style
        cursor_style = "cursor: pointer;" if clickable else ""
        
        # CSS für Card
        card_css_content = f"""
        .shadcn-card-{card_id} {{
            {variant_styles[variant]}
            border-radius: {border_radius};
            padding: {spacing_6};
            transition: all {transition};
            color: {fg_color};
            {cursor_style}
            overflow: hidden;
        }}
        
        .shadcn-card-{card_id}:hover {{
            {hover_style}
        }}
        
        .shadcn-card-header-{card_id} {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: {spacing_4};
        }}
        
        .shadcn-card-header-left-{card_id} {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            flex: 1;
        }}
        
        .shadcn-card-icon-{card_id} {{
            font-size: 1.5rem;
            line-height: 1;
            flex-shrink: 0;
        }}
        
        .shadcn-card-title-wrapper-{card_id} {{
            flex: 1;
        }}
        
        .shadcn-card-title-{card_id} {{
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1.4;
            margin: 0;
            color: {fg_color};
        }}
        
        .shadcn-card-description-{card_id} {{
            font-size: 0.875rem;
            color: {muted_fg_color};
            margin: 0.25rem 0 0 0;
            line-height: 1.5;
        }}
        
        .shadcn-card-badge-{card_id} {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            background: {badge_bg};
            color: {badge_fg};
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .shadcn-card-body-{card_id} {{
            font-size: 0.875rem;
            line-height: 1.6;
            color: {fg_color};
        }}
        
        .shadcn-card-footer-{card_id} {{
            margin-top: {spacing_4};
            padding-top: {spacing_4};
            border-top: 1px solid {border_color};
            font-size: 0.875rem;
            color: {muted_fg_color};
        }}
        
        {custom_css or ''}
        """
        
        # Injiziere CSS
        card_css = f"<style>{card_css_content}</style>"
        st.markdown(card_css, unsafe_allow_html=True)
        
        # Baue HTML
        html_parts = [f'<div class="shadcn-card-{card_id}">']
        
        # Header
        if title or icon or badge:
            html_parts.append(f'<div class="shadcn-card-header-{card_id}">')
            html_parts.append(f'<div class="shadcn-card-header-left-{card_id}">')
            
            if icon:
                html_parts.append(f'<div class="shadcn-card-icon-{card_id}">{icon}</div>')
            
            if title:
                html_parts.append(f'<div class="shadcn-card-title-wrapper-{card_id}">')
                html_parts.append(f'<h3 class="shadcn-card-title-{card_id}">{title}</h3>')
                if description:
                    html_parts.append(f'<p class="shadcn-card-description-{card_id}">{description}</p>')
                html_parts.append('</div>')
            
            html_parts.append('</div>')  # header-left
            
            if badge:
                html_parts.append(f'<div class="shadcn-card-badge-{card_id}">{badge}</div>')
            
            html_parts.append('</div>')  # header
        
        # Body
        if content:
            html_parts.append(f'<div class="shadcn-card-body-{card_id}">')
            html_parts.append(content)
            html_parts.append('</div>')
        
        # Footer
        if footer:
            html_parts.append(f'<div class="shadcn-card-footer-{card_id}">')
            html_parts.append(footer)
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Rendere HTML
        html = ''.join(html_parts)
        st.markdown(html, unsafe_allow_html=True)
        
        # Handle Click-Event
        if clickable and on_click:
            # Verwende einen unsichtbaren Button für Click-Handling
            if st.button("", key=f"card_click_{card_id}", help="Click to interact"):
                on_click()


def card(
    title: Optional[str] = None,
    description: Optional[str] = None,
    content: Optional[str] = None,
    footer: Optional[str] = None,
    variant: Literal["default", "outlined", "elevated"] = "default",
    icon: Optional[str] = None,
    badge: Optional[str] = None,
    badge_variant: Literal["default", "success", "warning", "error", "info"] = "default",
    hover_effect: bool = True,
    clickable: bool = False,
    on_click: Optional[Callable] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern einer Card
    
    Dies ist eine Shortcut-Funktion, die eine Card-Instanz erstellt und rendert.
    
    Args:
        Siehe Card.render() für Parameter-Dokumentation
    
    Example:
        ```python
        from components.card import card
        
        card(
            title="Meine Card",
            content="Inhalt",
            variant="elevated"
        )
        ```
    """
    card_component = Card(theme_manager=theme_manager)
    card_component.render(
        title=title,
        description=description,
        content=content,
        footer=footer,
        variant=variant,
        icon=icon,
        badge=badge,
        badge_variant=badge_variant,
        hover_effect=hover_effect,
        clickable=clickable,
        on_click=on_click,
        custom_css=custom_css,
        key=key
    )
