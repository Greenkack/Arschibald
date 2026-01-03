"""
shadcn/ui Skeleton-Loader-Komponente für Streamlit

Diese Komponente bietet moderne Skeleton-Loader für Lade-Zustände.
"""

from typing import Optional, Literal, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Skeleton(ShadcnComponent):
    """
    shadcn/ui Skeleton-Loader-Komponente
    
    Ein Skeleton-Loader für Lade-Zustände.
    
    Features:
    - Verschiedene Formen (text, circle, rectangle)
    - Animierte Pulse-Effekte
    - Verschiedene Größen
    - Kombinierbare Layouts
    
    Example:
        ```python
        from components import Skeleton
        
        skeleton = Skeleton()
        skeleton.render(
            variant="text",
            lines=3,
            animated=True
        )
        ```
    """
    
    def render(
        self,
        variant: Literal["text", "circle", "rectangle"] = "text",
        width: Optional[str] = None,
        height: Optional[str] = None,
        lines: int = 1,
        animated: bool = True,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert einen Skeleton-Loader
        
        Args:
            variant: Form ('text', 'circle', 'rectangle')
            width: Breite (CSS-Wert, z.B. '100%', '200px')
            height: Höhe (CSS-Wert)
            lines: Anzahl Zeilen (nur bei variant='text')
            animated: Ob Pulse-Animation gezeigt werden soll
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        """
        skeleton_id = key or self._generate_unique_id("skeleton")
        
        # Theme-Tokens
        muted_bg = self.get_token('colors.muted', '#f4f4f5')
        border_radius = self.get_token('borders.border_radius_md', '0.375rem')
        
        # Default-Größen
        if variant == "text":
            default_width = "100%"
            default_height = "1rem"
        elif variant == "circle":
            default_width = "3rem"
            default_height = "3rem"
        else:  # rectangle
            default_width = "100%"
            default_height = "8rem"
        
        width = width or default_width
        height = height or default_height
        
        # Border-Radius basierend auf Variante
        if variant == "circle":
            radius = "50%"
        elif variant == "text":
            radius = "0.25rem"
        else:
            radius = border_radius
        
        # Animation
        animation = """
        @keyframes skeleton-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        """ if animated else ""
        
        animated_style = "animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;" if animated else ""
        
        # CSS
        css = f"""
        <style>
        {animation}
        
        .shadcn-skeleton-{skeleton_id} {{
            background: {muted_bg};
            border-radius: {radius};
            {animated_style}
        }}
        
        .shadcn-skeleton-line-{skeleton_id} {{
            width: {width};
            height: {height};
            margin-bottom: 0.5rem;
        }}
        
        .shadcn-skeleton-line-{skeleton_id}:last-child {{
            margin-bottom: 0;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Skeleton
        if variant == "text" and lines > 1:
            for i in range(lines):
                # Letzte Zeile etwas kürzer
                line_width = width if i < lines - 1 else "80%"
                st.markdown(
                    f'<div class="shadcn-skeleton-{skeleton_id} shadcn-skeleton-line-{skeleton_id}" '
                    f'style="width: {line_width}; height: {height};"></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f'<div class="shadcn-skeleton-{skeleton_id}" '
                f'style="width: {width}; height: {height};"></div>',
                unsafe_allow_html=True
            )


class SkeletonCard(ShadcnComponent):
    """
    Vordefiniertes Skeleton-Layout für Card
    
    Example:
        ```python
        from components import SkeletonCard
        
        skeleton = SkeletonCard()
        skeleton.render()
        ```
    """
    
    def render(
        self,
        show_avatar: bool = True,
        show_footer: bool = True,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert ein Card-Skeleton
        
        Args:
            show_avatar: Ob Avatar-Skeleton gezeigt werden soll
            show_footer: Ob Footer-Skeleton gezeigt werden soll
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        """
        skeleton_id = key or self._generate_unique_id("skeleton_card")
        
        # Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        border_color = self.get_token('colors.border', '#e4e4e7')
        border_radius = self.get_token('borders.border_radius_lg', '0.5rem')
        spacing_6 = self.get_token('spacing.spacing_6', '1.5rem')
        
        # CSS
        css = f"""
        <style>
        .shadcn-skeleton-card-{skeleton_id} {{
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            padding: {spacing_6};
        }}
        
        .shadcn-skeleton-card-header-{skeleton_id} {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Card Skeleton
        st.markdown(
            f'<div class="shadcn-skeleton-card-{skeleton_id}">',
            unsafe_allow_html=True
        )
        
        # Header mit Avatar
        if show_avatar:
            st.markdown(
                f'<div class="shadcn-skeleton-card-header-{skeleton_id}">',
                unsafe_allow_html=True
            )
            
            # Avatar
            skeleton = Skeleton(theme_manager=self.theme_manager)
            skeleton.render(variant="circle", width="3rem", height="3rem", key=f"{skeleton_id}_avatar")
            
            # Title und Subtitle
            skeleton.render(variant="text", width="60%", height="1rem", key=f"{skeleton_id}_title")
            skeleton.render(variant="text", width="40%", height="0.75rem", key=f"{skeleton_id}_subtitle")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Content
        skeleton = Skeleton(theme_manager=self.theme_manager)
        skeleton.render(variant="text", lines=3, key=f"{skeleton_id}_content")
        
        # Footer
        if show_footer:
            st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
            skeleton.render(variant="rectangle", height="2.5rem", key=f"{skeleton_id}_footer")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def skeleton(
    variant: Literal["text", "circle", "rectangle"] = "text",
    width: Optional[str] = None,
    height: Optional[str] = None,
    lines: int = 1,
    animated: bool = True,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """Convenience-Funktion zum Rendern eines Skeleton-Loaders"""
    skel = Skeleton(theme_manager=theme_manager)
    skel.render(variant, width, height, lines, animated, custom_css, key)


def skeleton_card(
    show_avatar: bool = True,
    show_footer: bool = True,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """Convenience-Funktion zum Rendern eines Card-Skeletons"""
    skel = SkeletonCard(theme_manager=theme_manager)
    skel.render(show_avatar, show_footer, custom_css, key)
