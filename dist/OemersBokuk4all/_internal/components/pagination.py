"""
shadcn/ui Pagination-Komponente für Streamlit

Diese Komponente bietet eine moderne Pagination.
"""

from typing import Optional, Callable, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Pagination(ShadcnComponent):
    """
    shadcn/ui Pagination-Komponente
    
    Eine Pagination für seitenweise Navigation.
    
    Features:
    - Erste/Letzte Seite
    - Vorherige/Nächste Seite
    - Seitenzahlen mit Ellipsis
    - Responsive Design
    
    Example:
        ```python
        from components import Pagination
        
        pagination = Pagination()
        current_page = pagination.render(
            total_pages=10,
            current_page=1,
            on_page_change=lambda page: st.write(f"Seite {page}")
        )
        ```
    """
    
    def render(
        self,
        total_pages: int,
        current_page: int = 1,
        max_visible_pages: int = 5,
        show_first_last: bool = True,
        show_prev_next: bool = True,
        on_page_change: Optional[Callable[[int], None]] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> int:
        """
        Rendert eine Pagination
        
        Args:
            total_pages: Gesamtanzahl Seiten
            current_page: Aktuelle Seite (1-basiert)
            max_visible_pages: Maximale Anzahl sichtbarer Seitenzahlen
            show_first_last: Ob Erste/Letzte-Buttons gezeigt werden sollen
            show_prev_next: Ob Vorherige/Nächste-Buttons gezeigt werden sollen
            on_page_change: Callback mit neuer Seitenzahl
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key
        
        Returns:
            Aktuelle Seitenzahl
        """
        pagination_id = key or self._generate_unique_id("pagination")
        
        # Session State für aktuelle Seite
        state_key = f"pagination_page_{pagination_id}"
        if state_key not in st.session_state:
            st.session_state[state_key] = current_page
        
        current = st.session_state[state_key]
        
        # Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        primary = self.get_token('colors.primary', '#18181b')
        primary_fg = self.get_token('colors.primary_foreground', '#fafafa')
        muted_bg = self.get_token('colors.muted', '#f4f4f5')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token('borders.border_radius_md', '0.375rem')
        spacing_2 = self.get_token('spacing.spacing_2', '0.5rem')
        transition = self.get_token('animations.transition_base', '200ms')
        
        # CSS
        css = f"""
        <style>
        .shadcn-pagination-{pagination_id} {{
            display: flex;
            align-items: center;
            gap: {spacing_2};
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .shadcn-pagination-item-{pagination_id} {{
            min-width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid {border_color};
            border-radius: {border_radius};
            background: {bg_color};
            color: {fg_color};
            font-size: 0.875rem;
            cursor: pointer;
            transition: all {transition};
            user-select: none;
        }}
        
        .shadcn-pagination-item-{pagination_id}:hover {{
            background: {muted_bg};
            border-color: {primary};
        }}
        
        .shadcn-pagination-item-active-{pagination_id} {{
            background: {primary};
            color: {primary_fg};
            border-color: {primary};
        }}
        
        .shadcn-pagination-item-active-{pagination_id}:hover {{
            background: {primary};
        }}
        
        .shadcn-pagination-item-disabled-{pagination_id} {{
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }}
        
        .shadcn-pagination-ellipsis-{pagination_id} {{
            min-width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {muted_fg};
            font-size: 0.875rem;
        }}
        
        {custom_css or ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Berechne sichtbare Seiten
        def get_visible_pages():
            if total_pages <= max_visible_pages:
                return list(range(1, total_pages + 1))
            
            half = max_visible_pages // 2
            
            if current <= half + 1:
                return list(range(1, max_visible_pages + 1))
            elif current >= total_pages - half:
                return list(range(total_pages - max_visible_pages + 1, total_pages + 1))
            else:
                return list(range(current - half, current + half + 1))
        
        visible_pages = get_visible_pages()
        
        # Render Pagination
        st.markdown(f'<div class="shadcn-pagination-{pagination_id}">', unsafe_allow_html=True)
        
        # Buttons in Columns
        num_buttons = 0
        if show_first_last:
            num_buttons += 2
        if show_prev_next:
            num_buttons += 2
        num_buttons += len(visible_pages)
        if visible_pages[0] > 1:
            num_buttons += 1  # Ellipsis
        if visible_pages[-1] < total_pages:
            num_buttons += 1  # Ellipsis
        
        cols = st.columns(num_buttons)
        col_idx = 0
        
        # Erste Seite
        if show_first_last:
            with cols[col_idx]:
                disabled = current == 1
                if st.button(
                    "",
                    key=f"pagination_first_{pagination_id}",
                    disabled=disabled,
                    help="Erste Seite"
                ):
                    st.session_state[state_key] = 1
                    if on_page_change:
                        on_page_change(1)
                    st.rerun()
            col_idx += 1
        
        # Vorherige Seite
        if show_prev_next:
            with cols[col_idx]:
                disabled = current == 1
                if st.button(
                    "‹",
                    key=f"pagination_prev_{pagination_id}",
                    disabled=disabled,
                    help="Vorherige Seite"
                ):
                    st.session_state[state_key] = current - 1
                    if on_page_change:
                        on_page_change(current - 1)
                    st.rerun()
            col_idx += 1
        
        # Ellipsis am Anfang
        if visible_pages[0] > 1:
            with cols[col_idx]:
                st.markdown(
                    f'<div class="shadcn-pagination-ellipsis-{pagination_id}">...</div>',
                    unsafe_allow_html=True
                )
            col_idx += 1
        
        # Seitenzahlen
        for page in visible_pages:
            with cols[col_idx]:
                is_current = page == current
                if st.button(
                    str(page),
                    key=f"pagination_page_{pagination_id}_{page}",
                    type="primary" if is_current else "secondary",
                    disabled=is_current,
                    help=f"Seite {page}"
                ):
                    st.session_state[state_key] = page
                    if on_page_change:
                        on_page_change(page)
                    st.rerun()
            col_idx += 1
        
        # Ellipsis am Ende
        if visible_pages[-1] < total_pages:
            with cols[col_idx]:
                st.markdown(
                    f'<div class="shadcn-pagination-ellipsis-{pagination_id}">...</div>',
                    unsafe_allow_html=True
                )
            col_idx += 1
        
        # Nächste Seite
        if show_prev_next:
            with cols[col_idx]:
                disabled = current == total_pages
                if st.button(
                    "›",
                    key=f"pagination_next_{pagination_id}",
                    disabled=disabled,
                    help="Nächste Seite"
                ):
                    st.session_state[state_key] = current + 1
                    if on_page_change:
                        on_page_change(current + 1)
                    st.rerun()
            col_idx += 1
        
        # Letzte Seite
        if show_first_last:
            with cols[col_idx]:
                disabled = current == total_pages
                if st.button(
                    "",
                    key=f"pagination_last_{pagination_id}",
                    disabled=disabled,
                    help="Letzte Seite"
                ):
                    st.session_state[state_key] = total_pages
                    if on_page_change:
                        on_page_change(total_pages)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return st.session_state[state_key]


def pagination(
    total_pages: int,
    current_page: int = 1,
    max_visible_pages: int = 5,
    show_first_last: bool = True,
    show_prev_next: bool = True,
    on_page_change: Optional[Callable[[int], None]] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> int:
    """Convenience-Funktion zum Rendern einer Pagination"""
    pag = Pagination(theme_manager=theme_manager)
    return pag.render(
        total_pages, current_page, max_visible_pages,
        show_first_last, show_prev_next, on_page_change,
        custom_css, key
    )
