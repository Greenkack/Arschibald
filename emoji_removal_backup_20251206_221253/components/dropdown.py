"""
shadcn/ui Dropdown-Menu-Komponente für Streamlit

Diese Komponente bietet ein modernes Dropdown-Menü.
"""

from typing import Optional, List, Dict, Any, Callable, Literal
import streamlit as st
from .shadcn_base import ShadcnComponent


class DropdownMenu(ShadcnComponent):
    """
    shadcn/ui Dropdown-Menu-Komponente
    
    Ein Dropdown-Menü für Aktionen und Navigation.
    
    Features:
    - Gruppierte Menu-Items
    - Icons und Shortcuts
    - Separatoren
    - Disabled Items
    
    Example:
        ```python
        from components import DropdownMenu
        
        dropdown = DropdownMenu()
        selected = dropdown.render(
            trigger_label="Aktionen",
            items=[
                {"label": "Bearbeiten", "icon": "✏️", "value": "edit"},
                {"label": "Löschen", "icon": "🗑️", "value": "delete"},
                {"separator": True},
                {"label": "Exportieren", "icon": "📤", "value": "export"}
            ]
        )
        ```
    """
    
    def render(
        self,
        trigger_label: str,
        items: List[Dict[str, Any]],
        trigger_icon: Optional[str] = None,
        align: Literal["left", "right"] = "left",
        on_select: Optional[Callable[[str], None]] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> Optional[str]:
        """
        Rendert ein Dropdown-Menu
        
        Args:
            trigger_label: Label für Trigger-Button
            items: Liste von Menu-Items (Dicts mit 'label', 'value', 'icon', 'disabled', 'separator')
            trigger_icon: Icon für Trigger-Button
            align: Ausrichtung des Menüs ('left' oder 'right')
            on_select: Callback mit Item-Value bei Auswahl
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        
        Returns:
            Value des ausgewählten Items oder None
        """
        dropdown_id = key or self._generate_unique_id("dropdown")
        
        # Session State für Menü-Status
        state_key = f"dropdown_open_{dropdown_id}"
        if state_key not in st.session_state:
            st.session_state[state_key] = False
        
        # Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        muted_bg = self.get_token('colors.muted', '#f4f4f5')
        border_radius = self.get_token('borders.border_radius_md', '0.375rem')
        spacing_2 = self.get_token('spacing.spacing_2', '0.5rem')
        shadow_md = self.get_token('shadows.shadow_md', '0 4px 6px -1px rgba(0, 0, 0, 0.1)')
        transition = self.get_token('animations.transition_base', '200ms')
        
        # CSS
        css = f"""
        <style>
        .shadcn-dropdown-{dropdown_id} {{
            position: relative;
            display: inline-block;
        }}
        
        .shadcn-dropdown-menu-{dropdown_id} {{
            position: absolute;
            top: 100%;
            {align}: 0;
            margin-top: {spacing_2};
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            box-shadow: {shadow_md};
            min-width: 200px;
            z-index: 1000;
            padding: {spacing_2};
        }}
        
        .shadcn-dropdown-item-{dropdown_id} {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: {spacing_2};
            border-radius: calc({border_radius} - 2px);
            font-size: 0.875rem;
            color: {fg_color};
            cursor: pointer;
            transition: background {transition};
            border: none;
            background: none;
            width: 100%;
            text-align: left;
        }}
        
        .shadcn-dropdown-item-{dropdown_id}:hover {{
            background: {muted_bg};
        }}
        
        .shadcn-dropdown-item-disabled-{dropdown_id} {{
            color: {muted_fg};
            cursor: not-allowed;
            opacity: 0.5;
        }}
        
        .shadcn-dropdown-item-disabled-{dropdown_id}:hover {{
            background: transparent;
        }}
        
        .shadcn-dropdown-separator-{dropdown_id} {{
            height: 1px;
            background: {border_color};
            margin: {spacing_2} 0;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Trigger Button
        trigger_text = f"{trigger_icon} {trigger_label}" if trigger_icon else trigger_label
        if st.button(
            trigger_text,
            key=f"dropdown_trigger_{dropdown_id}",
            help="Menü öffnen"
        ):
            st.session_state[state_key] = not st.session_state[state_key]
            st.rerun()
        
        # Menu (wenn offen)
        selected_value = None
        if st.session_state[state_key]:
            st.markdown(f'<div class="shadcn-dropdown-menu-{dropdown_id}">', unsafe_allow_html=True)
            
            for idx, item in enumerate(items):
                # Separator
                if item.get('separator'):
                    st.markdown(
                        f'<div class="shadcn-dropdown-separator-{dropdown_id}"></div>',
                        unsafe_allow_html=True
                    )
                    continue
                
                label = item.get('label', f'Item {idx}')
                value = item.get('value', label)
                item_icon = item.get('icon', '')
                disabled = item.get('disabled', False)
                
                if not disabled:
                    if st.button(
                        f"{item_icon} {label}" if item_icon else label,
                        key=f"dropdown_item_{dropdown_id}_{idx}",
                        use_container_width=True
                    ):
                        selected_value = value
                        st.session_state[state_key] = False
                        if on_select:
                            on_select(value)
                        st.rerun()
                else:
                    st.markdown(
                        f'<div class="shadcn-dropdown-item-{dropdown_id} '
                        f'shadcn-dropdown-item-disabled-{dropdown_id}">'
                        f'{item_icon} {label if not item_icon else label}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        return selected_value


def dropdown_menu(
    trigger_label: str,
    items: List[Dict[str, Any]],
    trigger_icon: Optional[str] = None,
    align: Literal["left", "right"] = "left",
    on_select: Optional[Callable[[str], None]] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> Optional[str]:
    """Convenience-Funktion zum Rendern eines Dropdown-Menüs"""
    dd = DropdownMenu(theme_manager=theme_manager)
    return dd.render(trigger_label, items, trigger_icon, align, on_select, custom_css, key)
