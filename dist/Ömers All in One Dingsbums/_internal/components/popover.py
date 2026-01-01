"""
shadcn/ui Popover-Komponente für Streamlit

Diese Komponente bietet ein modernes Popover für zusätzliche Informationen.
"""

from typing import Optional, Literal, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Popover(ShadcnComponent):
    """
    shadcn/ui Popover-Komponente
    
    Ein Popover für zusätzliche Informationen und Inhalte.
    
    Features:
    - Verschiedene Positionen (top, bottom, left, right)
    - Trigger on hover oder click
    - Arrow/Pointer
    - Responsive Design
    
    Example:
        ```python
        from components import Popover
        
        popover = Popover()
        popover.render(
            trigger_label="Info",
            content="Zusätzliche Informationen hier",
            position="top"
        )
        ```
    """
    
    def render(
        self,
        trigger_label: str,
        content: str,
        title: Optional[str] = None,
        position: Literal["top", "bottom", "left", "right"] = "top",
        trigger_type: Literal["click", "hover"] = "click",
        trigger_icon: Optional[str] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert ein Popover
        
        Args:
            trigger_label: Label für Trigger-Element
            content: Popover-Inhalt
            title: Optionaler Titel
            position: Position des Popovers ('top', 'bottom', 'left', 'right')
            trigger_type: Trigger-Art ('click' oder 'hover')
            trigger_icon: Icon für Trigger
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        """
        popover_id = key or self._generate_unique_id("popover")
        
        # Session State für Popover-Status (nur bei click)
        if trigger_type == "click":
            state_key = f"popover_open_{popover_id}"
            if state_key not in st.session_state:
                st.session_state[state_key] = False
        
        # Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token('borders.border_radius_md', '0.375rem')
        spacing_3 = self.get_token('spacing.spacing_3', '0.75rem')
        spacing_4 = self.get_token('spacing.spacing_4', '1rem')
        shadow_lg = self.get_token('shadows.shadow_lg', '0 10px 15px -3px rgba(0, 0, 0, 0.1)')
        transition = self.get_token('animations.transition_base', '200ms')
        
        # Position-spezifische Styles
        position_styles = {
            'top': 'bottom: 100%; left: 50%; transform: translateX(-50%); margin-bottom: 0.5rem;',
            'bottom': 'top: 100%; left: 50%; transform: translateX(-50%); margin-top: 0.5rem;',
            'left': 'right: 100%; top: 50%; transform: translateY(-50%); margin-right: 0.5rem;',
            'right': 'left: 100%; top: 50%; transform: translateY(-50%); margin-left: 0.5rem;',
        }
        
        # CSS
        css = f"""
        <style>
        .shadcn-popover-{popover_id} {{
            position: relative;
            display: inline-block;
        }}
        
        .shadcn-popover-content-{popover_id} {{
            position: absolute;
            {position_styles[position]}
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            box-shadow: {shadow_lg};
            padding: {spacing_4};
            min-width: 200px;
            max-width: 300px;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: opacity {transition}, visibility {transition};
        }}
        
        .shadcn-popover-{popover_id}:hover .shadcn-popover-content-{popover_id} {{
            opacity: 1;
            visibility: visible;
        }}
        
        .shadcn-popover-content-open-{popover_id} {{
            opacity: 1 !important;
            visibility: visible !important;
        }}
        
        .shadcn-popover-title-{popover_id} {{
            font-size: 0.875rem;
            font-weight: 600;
            color: {fg_color};
            margin: 0 0 {spacing_3} 0;
        }}
        
        .shadcn-popover-text-{popover_id} {{
            font-size: 0.875rem;
            color: {muted_fg};
            line-height: 1.5;
            margin: 0;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Popover
        st.markdown(f'<div class="shadcn-popover-{popover_id}">', unsafe_allow_html=True)
        
        # Trigger
        trigger_text = f"{trigger_icon} {trigger_label}" if trigger_icon else trigger_label
        
        if trigger_type == "click":
            if st.button(
                trigger_text,
                key=f"popover_trigger_{popover_id}",
                help="Klicken für mehr Info"
            ):
                st.session_state[state_key] = not st.session_state[state_key]
                st.rerun()
            
            is_open = st.session_state.get(state_key, False)
            open_class = "shadcn-popover-content-open" if is_open else ""
        else:
            # Hover: zeige Trigger als Text
            st.markdown(
                f'<span style="cursor: help; text-decoration: underline dotted;">{trigger_text}</span>',
                unsafe_allow_html=True
            )
            open_class = ""
        
        # Content
        st.markdown(
            f'<div class="shadcn-popover-content-{popover_id} {open_class}">',
            unsafe_allow_html=True
        )
        
        if title:
            st.markdown(
                f'<div class="shadcn-popover-title-{popover_id}">{title}</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div class="shadcn-popover-text-{popover_id}">{content}</div>',
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def popover(
    trigger_label: str,
    content: str,
    title: Optional[str] = None,
    position: Literal["top", "bottom", "left", "right"] = "top",
    trigger_type: Literal["click", "hover"] = "click",
    trigger_icon: Optional[str] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """Convenience-Funktion zum Rendern eines Popovers"""
    pop = Popover(theme_manager=theme_manager)
    pop.render(trigger_label, content, title, position, trigger_type, trigger_icon, custom_css, key)
