"""
shadcn/ui Accordion-Komponente für Streamlit

Diese Komponente bietet ein modernes Accordion für zusammenklappbare Inhalte.
"""

from typing import Optional, List, Dict, Any, Literal
import streamlit as st
from .shadcn_base import ShadcnComponent


class Accordion(ShadcnComponent):
    """
    shadcn/ui Accordion-Komponente
    
    Ein Accordion für zusammenklappbare Content-Bereiche.
    Unterstützt Single- und Multi-Expand-Modi.
    
    Features:
    - Single oder Multiple Items gleichzeitig offen
    - Smooth Transitions
    - Icons für Expand/Collapse
    - Responsive Design
    
    Example:
        ```python
        from components import Accordion
        
        accordion = Accordion()
        accordion.render(
            items=[
                {
                    "title": "Abschnitt 1",
                    "content": "Inhalt 1",
                    "icon": ""
                },
                {
                    "title": "Abschnitt 2",
                    "content": "Inhalt 2"
                }
            ],
            type="single"
        )
        ```
    """
    
    def render(
        self,
        items: List[Dict[str, Any]],
        type: Literal["single", "multiple"] = "single",
        default_open: Optional[List[int]] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> List[int]:
        """
        Rendert ein Accordion
        
        Args:
            items: Liste von Dicts mit 'title', 'content', optional 'icon'
            type: 'single' (nur ein Item offen) oder 'multiple'
            default_open: Liste von Indizes die initial offen sein sollen
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        
        Returns:
            Liste der aktuell geöffneten Item-Indizes
        """
        accordion_id = key or self._generate_unique_id("accordion")
        
        # Session State für geöffnete Items
        state_key = f"accordion_open_{accordion_id}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default_open or []
        
        # Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token('borders.border_radius_md', '0.375rem')
        spacing_4 = self.get_token('spacing.spacing_4', '1rem')
        transition = self.get_token('animations.transition_base', '200ms')
        
        # CSS
        css = f"""
        <style>
        .shadcn-accordion-{accordion_id} {{
            border: 1px solid {border_color};
            border-radius: {border_radius};
            overflow: hidden;
        }}
        
        .shadcn-accordion-item-{accordion_id} {{
            border-bottom: 1px solid {border_color};
        }}
        
        .shadcn-accordion-item-{accordion_id}:last-child {{
            border-bottom: none;
        }}
        
        .shadcn-accordion-trigger-{accordion_id} {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: {spacing_4};
            background: {bg_color};
            border: none;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            color: {fg_color};
            transition: background {transition};
            text-align: left;
        }}
        
        .shadcn-accordion-trigger-{accordion_id}:hover {{
            background: {self.get_token('colors.muted', '#f4f4f5')};
        }}
        
        .shadcn-accordion-trigger-left-{accordion_id} {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .shadcn-accordion-icon-{accordion_id} {{
            transition: transform {transition};
        }}
        
        .shadcn-accordion-icon-open-{accordion_id} {{
            transform: rotate(180deg);
        }}
        
        .shadcn-accordion-content-{accordion_id} {{
            padding: 0 {spacing_4} {spacing_4} {spacing_4};
            font-size: 0.875rem;
            color: {muted_fg};
            line-height: 1.6;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Render Accordion
        st.markdown(f'<div class="shadcn-accordion-{accordion_id}">', unsafe_allow_html=True)
        
        for idx, item in enumerate(items):
            title = item.get('title', f'Item {idx + 1}')
            content = item.get('content', '')
            item_icon = item.get('icon', '')
            
            is_open = idx in st.session_state[state_key]
            
            # Trigger Button
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                if st.button(
                    f"{item_icon} {title}" if item_icon else title,
                    key=f"accordion_trigger_{accordion_id}_{idx}",
                    use_container_width=True
                ):
                    if type == "single":
                        # Single mode: nur ein Item offen
                        if is_open:
                            st.session_state[state_key] = []
                        else:
                            st.session_state[state_key] = [idx]
                    else:
                        # Multiple mode: toggle current item
                        if is_open:
                            st.session_state[state_key].remove(idx)
                        else:
                            st.session_state[state_key].append(idx)
                    st.rerun()
            
            with col2:
                icon_class = "shadcn-accordion-icon-open" if is_open else ""
                st.markdown(
                    f'<div class="shadcn-accordion-icon-{accordion_id} {icon_class}"></div>',
                    unsafe_allow_html=True
                )
            
            # Content (wenn offen)
            if is_open:
                st.markdown(
                    f'<div class="shadcn-accordion-content-{accordion_id}">{content}</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return st.session_state[state_key]


def accordion(
    items: List[Dict[str, Any]],
    type: Literal["single", "multiple"] = "single",
    default_open: Optional[List[int]] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> List[int]:
    """Convenience-Funktion zum Rendern eines Accordions"""
    acc = Accordion(theme_manager=theme_manager)
    return acc.render(items, type, default_open, custom_css, key)
