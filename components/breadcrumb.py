"""
shadcn/ui Breadcrumb-Komponente für Streamlit

Diese Komponente bietet eine moderne Breadcrumb-Navigation.
"""

from typing import Optional, List, Dict, Any, Callable
import streamlit as st
from .shadcn_base import ShadcnComponent


class Breadcrumb(ShadcnComponent):
    """
    shadcn/ui Breadcrumb-Komponente
    
    Eine Breadcrumb-Navigation für hierarchische Pfade.
    
    Features:
    - Klickbare Links
    - Custom Separator
    - Icons für Items
    - Responsive Design
    
    Example:
        ```python
        from components import Breadcrumb
        
        breadcrumb = Breadcrumb()
        breadcrumb.render(
            items=[
                {"label": "Home", "icon": "🏠"},
                {"label": "Projekte", "icon": "📁"},
                {"label": "Solar-Anlage"}
            ],
            separator="/"
        )
        ```
    """
    
    def render(
        self,
        items: List[Dict[str, Any]],
        separator: str = "/",
        on_click: Optional[Callable[[int], None]] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> Optional[int]:
        """
        Rendert eine Breadcrumb-Navigation
        
        Args:
            items: Liste von Dicts mit 'label', optional 'icon', 'href'
            separator: Trennzeichen zwischen Items
            on_click: Callback mit Item-Index bei Klick
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        
        Returns:
            Index des geklickten Items oder None
        """
        breadcrumb_id = key or self._generate_unique_id("breadcrumb")
        
        # Theme-Tokens
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        primary = self.get_token('colors.primary', '#18181b')
        transition = self.get_token('animations.transition_fast', '150ms')
        
        # CSS
        css = f"""
        <style>
        .shadcn-breadcrumb-{breadcrumb_id} {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
            font-size: 0.875rem;
        }}
        
        .shadcn-breadcrumb-item-{breadcrumb_id} {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
            color: {muted_fg};
            transition: color {transition};
        }}
        
        .shadcn-breadcrumb-item-{breadcrumb_id}:hover {{
            color: {primary};
        }}
        
        .shadcn-breadcrumb-item-active-{breadcrumb_id} {{
            color: {fg_color};
            font-weight: 500;
        }}
        
        .shadcn-breadcrumb-separator-{breadcrumb_id} {{
            color: {muted_fg};
            user-select: none;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Breadcrumb
        clicked_idx = None
        
        cols = st.columns(len(items) * 2 - 1)
        
        for idx, item in enumerate(items):
            label = item.get('label', f'Item {idx + 1}')
            item_icon = item.get('icon', '')
            is_last = idx == len(items) - 1
            
            # Item
            with cols[idx * 2]:
                active_class = "shadcn-breadcrumb-item-active" if is_last else ""
                
                if not is_last and on_click:
                    if st.button(
                        f"{item_icon} {label}" if item_icon else label,
                        key=f"breadcrumb_item_{breadcrumb_id}_{idx}",
                        help=f"Gehe zu {label}"
                    ):
                        clicked_idx = idx
                        on_click(idx)
                else:
                    st.markdown(
                        f'<span class="shadcn-breadcrumb-item-{breadcrumb_id} {active_class}">'
                        f'{item_icon} {label if not item_icon else label}'
                        f'</span>',
                        unsafe_allow_html=True
                    )
            
            # Separator
            if not is_last:
                with cols[idx * 2 + 1]:
                    st.markdown(
                        f'<span class="shadcn-breadcrumb-separator-{breadcrumb_id}">{separator}</span>',
                        unsafe_allow_html=True
                    )
        
        return clicked_idx


def breadcrumb(
    items: List[Dict[str, Any]],
    separator: str = "/",
    on_click: Optional[Callable[[int], None]] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> Optional[int]:
    """Convenience-Funktion zum Rendern einer Breadcrumb"""
    bc = Breadcrumb(theme_manager=theme_manager)
    return bc.render(items, separator, on_click, custom_css, key)
