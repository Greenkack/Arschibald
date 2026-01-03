"""
shadcn/ui Badge-Komponente für Streamlit

Diese Komponente bietet moderne Badges für Labels und Status-Anzeigen.
"""

from typing import Optional, Literal, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Badge(ShadcnComponent):
    """
    shadcn/ui Badge-Komponente

    Eine flexible Badge-Komponente für Labels, Status und Tags.
    Unterstützt verschiedene Varianten und Größen.

    Features:
    - Verschiedene Varianten (default, success, warning, error, info, outline)
    - Verschiedene Größen (sm, md, lg)
    - Optionale Icons
    - Dot-Indikator
    - Anpassbare Farben

    Example:
        ```python
        from components import Badge

        badge = Badge()
        badge.render(
            text="Neu",
            variant="success"
        )
        ```
    """

    def render(
        self,
        text: str,
        variant: Literal[
            "default", "success", "warning", "error",
            "info", "outline", "secondary"
        ] = "default",
        size: Literal["sm", "md", "lg"] = "md",
        icon: Optional[str] = None,
        dot: bool = False,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine Badge-Komponente

        Args:
            text: Badge-Text
            variant: Badge-Variante
            size: Badge-Größe ('sm', 'md', 'lg')
            icon: Optionales Icon vor dem Text
            dot: Zeigt einen Dot-Indikator an
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key für die Komponente

        Example:
            ```python
            badge = Badge()
            badge.render(
                text="Premium",
                variant="success",
                size="lg"
            )
            ```
        """
        # Generiere eindeutige ID
        badge_id = key or self._generate_unique_id("badge")

        # Hole Theme-Tokens
        border_radius = self.get_token(
            'borders.border_radius_full', '9999px'
        )
        transition = self.get_token(
            'animations.transition_base',
            '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        )

        # Varianten-spezifische Farben
        variant_colors = {
            'default': {
                'bg': self.get_token('colors.primary', '#18181b'),
                'fg': self.get_token('colors.primary_foreground', '#fafafa'),
                'border': self.get_token('colors.primary', '#18181b'),
            },
            'secondary': {
                'bg': self.get_token('colors.secondary', '#f4f4f5'),
                'fg': self.get_token('colors.secondary_foreground', '#18181b'),
                'border': self.get_token('colors.secondary', '#f4f4f5'),
            },
            'success': {
                'bg': self.get_token('colors.success', '#22c55e'),
                'fg': '#ffffff',
                'border': self.get_token('colors.success', '#22c55e'),
            },
            'warning': {
                'bg': self.get_token('colors.warning', '#f59e0b'),
                'fg': '#ffffff',
                'border': self.get_token('colors.warning', '#f59e0b'),
            },
            'error': {
                'bg': self.get_token('colors.error', '#ef4444'),
                'fg': '#ffffff',
                'border': self.get_token('colors.error', '#ef4444'),
            },
            'info': {
                'bg': self.get_token('colors.info', '#3b82f6'),
                'fg': '#ffffff',
                'border': self.get_token('colors.info', '#3b82f6'),
            },
            'outline': {
                'bg': 'transparent',
                'fg': self.get_token('colors.foreground', '#0a0a0a'),
                'border': self.get_token('colors.border', '#e4e4e7'),
            }
        }

        colors = variant_colors.get(variant, variant_colors['default'])

        # Größen-spezifische Styles
        size_styles = {
            'sm': {
                'padding': '0.125rem 0.5rem',
                'font_size': '0.75rem',
                'height': '1.25rem',
                'icon_size': '0.75rem',
                'dot_size': '0.375rem',
            },
            'md': {
                'padding': '0.25rem 0.75rem',
                'font_size': '0.875rem',
                'height': '1.5rem',
                'icon_size': '0.875rem',
                'dot_size': '0.5rem',
            },
            'lg': {
                'padding': '0.375rem 1rem',
                'font_size': '1rem',
                'height': '2rem',
                'icon_size': '1rem',
                'dot_size': '0.625rem',
            }
        }

        size_config = size_styles.get(size, size_styles['md'])

        # CSS für Badge
        badge_css = f"""
        <style>
        .shadcn-badge-{badge_id} {{
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: {size_config['padding']};
            border-radius: {border_radius};
            background: {colors['bg']};
            color: {colors['fg']};
            border: 1px solid {colors['border']};
            font-size: {size_config['font_size']};
            font-weight: 500;
            line-height: 1;
            white-space: nowrap;
            transition: all {transition};
            height: {size_config['height']};
            vertical-align: middle;
        }}

        .shadcn-badge-icon-{badge_id} {{
            font-size: {size_config['icon_size']};
            line-height: 1;
            display: flex;
            align-items: center;
        }}

        .shadcn-badge-dot-{badge_id} {{
            width: {size_config['dot_size']};
            height: {size_config['dot_size']};
            border-radius: 50%;
            background: currentColor;
            flex-shrink: 0;
        }}

        .shadcn-badge-text-{badge_id} {{
            line-height: 1;
        }}

        {custom_css or ''}
        </style>
        """  # noqa: E501

        # Injiziere CSS
        st.markdown(badge_css, unsafe_allow_html=True)

        # Baue HTML
        html_parts = [f'<span class="shadcn-badge-{badge_id}">']

        # Dot
        if dot:
            html_parts.append(
                f'<span class="shadcn-badge-dot-{badge_id}"></span>'
            )

        # Icon
        if icon:
            html_parts.append(
                f'<span class="shadcn-badge-icon-{badge_id}">{icon}</span>'
            )

        # Text
        html_parts.append(
            f'<span class="shadcn-badge-text-{badge_id}">{text}</span>'
        )

        html_parts.append('</span>')

        # Rendere HTML
        html = ''.join(html_parts)
        st.markdown(html, unsafe_allow_html=True)


class BadgeGroup(ShadcnComponent):
    """
    Badge-Gruppe für mehrere Badges

    Zeigt mehrere Badges in einer Gruppe an.

    Example:
        ```python
        from components import BadgeGroup

        group = BadgeGroup()
        group.render(
            badges=[
                {"text": "Python", "variant": "info"},
                {"text": "React", "variant": "success"},
                {"text": "TypeScript", "variant": "warning"}
            ]
        )
        ```
    """

    def render(
        self,
        badges: list[dict],
        spacing: Literal["sm", "md", "lg"] = "md",
        wrap: bool = True,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine Badge-Gruppe

        Args:
            badges: Liste von Badge-Konfigurationen
                (Dicts mit Badge-Parametern)
            spacing: Abstand zwischen Badges
            wrap: Ob Badges umbrechen sollen
            key: Eindeutiger Key

        Example:
            ```python
            group = BadgeGroup()
            group.render(
                badges=[
                    {"text": "Tag 1", "variant": "default"},
                    {"text": "Tag 2", "variant": "success", "icon": ""}
                ],
                spacing="md"
            )
            ```
        """
        # Generiere eindeutige ID
        group_id = key or self._generate_unique_id("badge-group")

        # Spacing-Werte
        spacing_values = {
            'sm': '0.25rem',
            'md': '0.5rem',
            'lg': '0.75rem'
        }

        gap = spacing_values.get(spacing, spacing_values['md'])

        # CSS für Badge-Gruppe
        group_css = f"""
        <style>
        .shadcn-badge-group-{group_id} {{
            display: flex;
            align-items: center;
            gap: {gap};
            flex-wrap: {'wrap' if wrap else 'nowrap'};
        }}
        </style>
        """

        st.markdown(group_css, unsafe_allow_html=True)

        # Baue HTML
        st.markdown(
            f'<div class="shadcn-badge-group-{group_id}">',
            unsafe_allow_html=True
        )

        # Rendere alle Badges
        badge_component = Badge(theme_manager=self.theme_manager)
        for i, badge_config in enumerate(badges):
            badge_key = badge_config.get('key', f"{group_id}_badge_{i}")
            badge_component.render(
                text=badge_config.get('text', ''),
                variant=badge_config.get('variant', 'default'),
                size=badge_config.get('size', 'md'),
                icon=badge_config.get('icon'),
                dot=badge_config.get('dot', False),
                custom_css=badge_config.get('custom_css'),
                key=badge_key
            )

        st.markdown('</div>', unsafe_allow_html=True)  # noqa: E501


def badge(
    text: str,
    variant: Literal[
        "default", "success", "warning", "error",
        "info", "outline", "secondary"
    ] = "default",
    size: Literal["sm", "md", "lg"] = "md",
    icon: Optional[str] = None,
    dot: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern eines Badges

    Args:
        Siehe Badge.render() für Parameter-Dokumentation

    Example:
        ```python
        from components.badge import badge

        badge(
            text="Neu",
            variant="success"
        )
        ```
    """
    badge_component = Badge(theme_manager=theme_manager)
    badge_component.render(
        text=text,
        variant=variant,
        size=size,
        icon=icon,
        dot=dot,
        custom_css=custom_css,
        key=key
    )


def badge_group(
    badges: list[dict],
    spacing: Literal["sm", "md", "lg"] = "md",
    wrap: bool = True,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern einer Badge-Gruppe

    Args:
        Siehe BadgeGroup.render() für Parameter-Dokumentation

    Example:
        ```python
        from components.badge import badge_group

        badge_group(
            badges=[
                {"text": "Python", "variant": "info"},
                {"text": "React", "variant": "success"}
            ]
        )
        ```
    """
    group_component = BadgeGroup(theme_manager=theme_manager)
    group_component.render(
        badges=badges,
        spacing=spacing,
        wrap=wrap,
        key=key
    )
