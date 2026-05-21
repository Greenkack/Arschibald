"""
shadcn/ui Progress-Komponente für Streamlit

Diese Komponente bietet eine moderne Progress-Bar.
"""

from typing import Optional, Literal, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Progress(ShadcnComponent):
    """
    shadcn/ui Progress-Komponente
    
    Eine Progress-Bar für Fortschrittsanzeigen.
    
    Features:
    - Verschiedene Varianten (default, success, warning, error)
    - Animierte Transitions
    - Label und Prozentanzeige
    - Verschiedene Größen
    
    Example:
        ```python
        from components import Progress
        
        progress = Progress()
        progress.render(
            value=75,
            label="Upload",
            show_percentage=True,
            variant="success"
        )
        ```
    """
    
    def render(
        self,
        value: float,
        max_value: float = 100,
        label: Optional[str] = None,
        show_percentage: bool = True,
        variant: Literal["default", "success", "warning", "error"] = "default",
        size: Literal["sm", "md", "lg"] = "md",
        animated: bool = True,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine Progress-Bar
        
        Args:
            value: Aktueller Wert
            max_value: Maximalwert
            label: Optionales Label
            show_percentage: Ob Prozentanzeige gezeigt werden soll
            variant: Farb-Variante ('default', 'success', 'warning', 'error')
            size: Größe ('sm', 'md', 'lg')
            animated: Ob animiert werden soll
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        """
        progress_id = key or self._generate_unique_id("progress")
        
        # Berechne Prozent
        percentage = min(100, max(0, (value / max_value) * 100))
        
        # Theme-Tokens
        bg_color = self.get_token('colors.muted', '#f4f4f5')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_radius = self.get_token('borders.border_radius_full', '9999px')
        transition = self.get_token('animations.transition_base', '200ms')
        
        # Varianten-Farben
        variant_colors = {
            'default': self.get_token('colors.primary', '#18181b'),
            'success': self.get_token('colors.success', '#22c55e'),
            'warning': self.get_token('colors.warning', '#f59e0b'),
            'error': self.get_token('colors.error', '#ef4444'),
        }
        bar_color = variant_colors.get(variant, variant_colors['default'])
        
        # Größen
        sizes = {
            'sm': '0.5rem',
            'md': '0.75rem',
            'lg': '1rem',
        }
        height = sizes.get(size, sizes['md'])
        
        # Animation
        animation = """
        @keyframes progress-animation {
            0% { background-position: 0 0; }
            100% { background-position: 40px 0; }
        }
        """ if animated else ""
        
        animated_style = """
        background-image: linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.15) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255, 255, 255, 0.15) 50%,
            rgba(255, 255, 255, 0.15) 75%,
            transparent 75%,
            transparent
        );
        background-size: 40px 40px;
        animation: progress-animation 1s linear infinite;
        """ if animated else ""
        
        # CSS
        css = f"""
        <style>
        {animation}
        
        .shadcn-progress-wrapper-{progress_id} {{
            width: 100%;
        }}
        
        .shadcn-progress-header-{progress_id} {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }}
        
        .shadcn-progress-label-{progress_id} {{
            color: {fg_color};
            font-weight: 500;
        }}
        
        .shadcn-progress-percentage-{progress_id} {{
            color: {self.get_token('colors.muted_foreground', '#71717a')};
            font-size: 0.75rem;
        }}
        
        .shadcn-progress-{progress_id} {{
            width: 100%;
            height: {height};
            background: {bg_color};
            border-radius: {border_radius};
            overflow: hidden;
            position: relative;
        }}
        
        .shadcn-progress-bar-{progress_id} {{
            height: 100%;
            background: {bar_color};
            border-radius: {border_radius};
            transition: width {transition};
            {animated_style}
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Progress
        st.markdown(
            f'<div class="shadcn-progress-wrapper-{progress_id}">',
            unsafe_allow_html=True
        )
        
        # Header (Label und Prozent)
        if label or show_percentage:
            st.markdown(
                f'<div class="shadcn-progress-header-{progress_id}">',
                unsafe_allow_html=True
            )
            
            if label:
                st.markdown(
                    f'<div class="shadcn-progress-label-{progress_id}">{label}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div></div>', unsafe_allow_html=True)
            
            if show_percentage:
                st.markdown(
                    f'<div class="shadcn-progress-percentage-{progress_id}">{percentage:.0f}%</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Progress Bar
        st.markdown(
            f'<div class="shadcn-progress-{progress_id}">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="shadcn-progress-bar-{progress_id}" style="width: {percentage}%"></div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def progress(
    value: float,
    max_value: float = 100,
    label: Optional[str] = None,
    show_percentage: bool = True,
    variant: Literal["default", "success", "warning", "error"] = "default",
    size: Literal["sm", "md", "lg"] = "md",
    animated: bool = True,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """Convenience-Funktion zum Rendern einer Progress-Bar"""
    prog = Progress(theme_manager=theme_manager)
    prog.render(value, max_value, label, show_percentage, variant, size, animated, custom_css, key)
