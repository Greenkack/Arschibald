"""
Sidebar Styling mit shadcn/ui-Design

Dieses Modul bietet moderne Sidebar-Styling-Funktionen mit shadcn/ui-Design,
einschließlich Menü-Gruppen, Icons, aktiver Hervorhebung und Hover-Effekten.
"""

from typing import Optional, List, Dict, Any, Callable
import streamlit as st
from dataclasses import dataclass


@dataclass
class MenuItem:
    """
    Repräsentiert einen Menü-Eintrag in der Sidebar

    Attributes:
        label: Anzeigetext des Menü-Eintrags
        icon: Optional Icon (Emoji oder HTML)
        key: Eindeutiger Schlüssel für den Menü-Eintrag
        callback: Optional Callback-Funktion beim Klick
        disabled: Ob der Eintrag deaktiviert ist
    """
    label: str
    icon: Optional[str] = None
    key: Optional[str] = None
    callback: Optional[Callable] = None
    disabled: bool = False


@dataclass
class MenuGroup:
    """
    Repräsentiert eine Menü-Gruppe in der Sidebar

    Attributes:
        title: Titel der Menü-Gruppe
        items: Liste von MenuItem-Objekten
        collapsible: Ob die Gruppe kollabierbar ist
        collapsed: Initial-Zustand (nur wenn collapsible=True)
    """
    title: str
    items: List[MenuItem]
    collapsible: bool = False
    collapsed: bool = False


class ShadcnSidebar:
    """
    Moderne Sidebar mit shadcn/ui-Design

    Diese Klasse bietet:
    - Menü-Gruppen mit Überschriften
    - Icon-Support für Menü-Einträge
    - Aktive Menü-Hervorhebung
    - Hover-Effekte
    - Optionale Kollabier-Funktion

    Example:
        ```python
        from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem

        sidebar = ShadcnSidebar()

        # Definiere Menü-Gruppen
        main_group = MenuGroup(
            title="Hauptmenü",
            items=[
                MenuItem(label="Dashboard", icon="📊", key="dashboard"),
                MenuItem(label="Projekte", icon="📁", key="projects"),
            ]
        )

        # Rendere Sidebar
        selected = sidebar.render([main_group])
        ```
    """

    def __init__(self, theme_manager: Optional[Any] = None):
        """
        Initialisiert die Sidebar

        Args:
            theme_manager: Optional ThemeManager für Token-Zugriff
        """
        self.theme_manager = theme_manager or st.session_state.get(
            'theme_manager'
        )

        # Initialisiere Session State für aktiven Menü-Eintrag
        if 'active_menu_item' not in st.session_state:
            st.session_state.active_menu_item = None

        # Initialisiere Session State für kollabierte Gruppen
        if 'collapsed_groups' not in st.session_state:
            st.session_state.collapsed_groups = set()

    def get_token(self, path: str, default: str = "") -> str:
        """
        Holt Design-Token vom ThemeManager

        Args:
            path: Token-Pfad (z.B. 'colors.primary')
            default: Fallback-Wert

        Returns:
            Token-Wert als String
        """
        if self.theme_manager is None:
            return default

        try:
            return self.theme_manager.get_token(path) or default
        except (AttributeError, KeyError):
            return default

    def inject_sidebar_css(self) -> None:
        """Injiziert shadcn/ui CSS für Sidebar"""

        css = f"""
        <style>
        /* Sidebar Container */
        [data-testid="stSidebar"] {{
            background-color: {self.get_token('colors.background', '#ffffff')};
            border-right: {self.get_token('borders.border_width', '1px')} solid {self.get_token('colors.border', '#e4e4e7')};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background-color: {self.get_token('colors.background', '#ffffff')};
        }}

        /* Sidebar Content */
        [data-testid="stSidebar"] .element-container {{
            font-family: {self.get_token('typography.font_family', 'Inter, sans-serif')};
        }}

        /* Menu Group Title */
        .shadcn-menu-group-title {{
            font-family: {self.get_token('typography.font_family', 'Inter, sans-serif')};
            font-size: {self.get_token('typography.font_size_xs', '0.75rem')};
            font-weight: {self.get_token('typography.font_weight_semibold', '600')};
            color: {self.get_token('colors.muted_foreground', '#71717a')};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: {self.get_token('spacing.spacing_2', '0.5rem')} {self.get_token('spacing.spacing_3', '0.75rem')};
            margin-top: {self.get_token('spacing.spacing_4', '1rem')};
            margin-bottom: {self.get_token('spacing.spacing_2', '0.5rem')};
        }}

        .shadcn-menu-group-title:first-child {{
            margin-top: 0;
        }}

        /* Menu Item */
        .shadcn-menu-item {{
            display: flex;
            align-items: center;
            gap: {self.get_token('spacing.spacing_3', '0.75rem')};
            padding: {self.get_token('spacing.spacing_2', '0.5rem')} {self.get_token('spacing.spacing_3', '0.75rem')};
            margin: {self.get_token('spacing.spacing_1', '0.25rem')} 0;
            border-radius: {self.get_token('borders.border_radius_md', '0.375rem')};
            font-family: {self.get_token('typography.font_family', 'Inter, sans-serif')};
            font-size: {self.get_token('typography.font_size_sm', '0.875rem')};
            font-weight: {self.get_token('typography.font_weight_medium', '500')};
            color: {self.get_token('colors.foreground', '#0a0a0a')};
            background-color: transparent;
            border: none;
            cursor: pointer;
            transition: all {self.get_token('animations.transition_base', '200ms cubic-bezier(0.4, 0, 0.2, 1)')};
            text-align: left;
            width: 100%;
        }}

        .shadcn-menu-item:hover {{
            background-color: {self.get_token('colors.accent', '#f4f4f5')};
            color: {self.get_token('colors.accent_foreground', '#18181b')};
        }}

        .shadcn-menu-item:active {{
            transform: scale(0.98);
        }}

        /* Active Menu Item */
        .shadcn-menu-item.active {{
            background-color: {self.get_token('colors.primary', '#18181b')};
            color: {self.get_token('colors.primary_foreground', '#fafafa')};
            font-weight: {self.get_token('typography.font_weight_semibold', '600')};
        }}

        .shadcn-menu-item.active:hover {{
            background-color: {self.get_token('colors.primary', '#18181b')};
            opacity: 0.9;
        }}

        /* Disabled Menu Item */
        .shadcn-menu-item:disabled,
        .shadcn-menu-item.disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }}

        /* Menu Item Icon */
        .shadcn-menu-item-icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 1.25rem;
            height: 1.25rem;
            font-size: 1rem;
            flex-shrink: 0;
        }}

        /* Menu Item Label */
        .shadcn-menu-item-label {{
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Collapsible Group Header */
        .shadcn-group-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            user-select: none;
        }}

        .shadcn-group-header:hover {{
            opacity: 0.8;
        }}

        .shadcn-collapse-icon {{
            transition: transform {self.get_token('animations.transition_base', '200ms cubic-bezier(0.4, 0, 0.2, 1)')};
            font-size: 0.75rem;
        }}

        .shadcn-collapse-icon.collapsed {{
            transform: rotate(-90deg);
        }}

        /* Sidebar Divider */
        .shadcn-sidebar-divider {{
            height: {self.get_token('borders.border_width', '1px')};
            background-color: {self.get_token('colors.border', '#e4e4e7')};
            margin: {self.get_token('spacing.spacing_4', '1rem')} 0;
        }}

        /* Sidebar Footer */
        .shadcn-sidebar-footer {{
            margin-top: auto;
            padding-top: {self.get_token('spacing.spacing_4', '1rem')};
            border-top: {self.get_token('borders.border_width', '1px')} solid {self.get_token('colors.border', '#e4e4e7')};
        }}
        </style>
        """

        st.markdown(css, unsafe_allow_html=True)

    def render_menu_item(
        self,
        item: MenuItem,
        group_key: str = ""
    ) -> bool:
        """
        Rendert einen einzelnen Menü-Eintrag

        Args:
            item: MenuItem-Objekt
            group_key: Schlüssel der Menü-Gruppe (für eindeutige IDs)

        Returns:
            True wenn der Eintrag geklickt wurde
        """
        # Generiere eindeutigen Key
        item_key = item.key or f"{group_key}_{item.label}"

        # Prüfe ob dieser Eintrag aktiv ist
        is_active = st.session_state.active_menu_item == item_key

        # CSS-Klassen
        css_classes = "shadcn-menu-item"
        if is_active:
            css_classes += " active"
        if item.disabled:
            css_classes += " disabled"

        # Icon HTML
        icon_html = ""
        if item.icon:
            icon_html = (
                f'<span class="shadcn-menu-item-icon">{item.icon}</span>'
            )

        # Button HTML
        button_html = f"""
        <button
            class="{css_classes}"
            onclick="window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                key: '{item_key}',
                value: true
            }}, '*')"
            {'disabled' if item.disabled else ''}
        >
            {icon_html}
            <span class="shadcn-menu-item-label">{item.label}</span>
        </button>
        """

        # Rendere Button
        st.markdown(button_html, unsafe_allow_html=True)

        # Prüfe ob Button geklickt wurde
        clicked = st.button(
            item.label,
            key=f"btn_{item_key}",
            disabled=item.disabled,
            use_container_width=True,
            type="primary" if is_active else "secondary"
        )

        if clicked:
            st.session_state.active_menu_item = item_key
            if item.callback:
                item.callback()
            return True

        return False

    def render_menu_group(
        self,
        group: MenuGroup,
        group_index: int = 0
    ) -> Optional[str]:
        """
        Rendert eine Menü-Gruppe

        Args:
            group: MenuGroup-Objekt
            group_index: Index der Gruppe (für eindeutige IDs)

        Returns:
            Key des geklickten Menü-Eintrags oder None
        """
        group_key = f"group_{group_index}_{group.title}"

        # Prüfe ob Gruppe kollabiert ist
        is_collapsed = group_key in st.session_state.collapsed_groups

        # Rendere Gruppen-Header
        if group.collapsible:
            # Kollabier-Icon
            collapse_icon = "▼" if not is_collapsed else "▶"

            header_html = f"""
            <div class="shadcn-group-header shadcn-menu-group-title">
                <span>{group.title}</span>
                <span class="shadcn-collapse-icon {'collapsed' if is_collapsed else ''}">{collapse_icon}</span>
            </div>
            """

            st.markdown(header_html, unsafe_allow_html=True)

            # Toggle-Button (unsichtbar)
            if st.button(
                f"Toggle {group.title}",
                key=f"toggle_{group_key}",
                use_container_width=True
            ):
                if is_collapsed:
                    st.session_state.collapsed_groups.discard(group_key)
                else:
                    st.session_state.collapsed_groups.add(group_key)
                st.rerun()
        else:
            # Normaler Gruppen-Titel
            st.markdown(
                f'<div class="shadcn-menu-group-title">{group.title}</div>',
                unsafe_allow_html=True
            )

        # Rendere Menü-Einträge (wenn nicht kollabiert)
        if not is_collapsed:
            for item in group.items:
                if self.render_menu_item(item, group_key):
                    return item.key or f"{group_key}_{item.label}"

        return None

    def render(
        self,
        menu_groups: List[MenuGroup],
        show_dividers: bool = True,
        footer_content: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Rendert die komplette Sidebar

        Args:
            menu_groups: Liste von MenuGroup-Objekten
            show_dividers: Ob Trennlinien zwischen Gruppen angezeigt werden
            footer_content: Optional Callback für Footer-Content

        Returns:
            Key des geklickten Menü-Eintrags oder None

        Example:
            ```python
            sidebar = ShadcnSidebar()

            groups = [
                MenuGroup(
                    title="Hauptmenü",
                    items=[
                        MenuItem("Dashboard", icon="📊", key="dashboard"),
                        MenuItem("Projekte", icon="📁", key="projects"),
                    ]
                ),
                MenuGroup(
                    title="Einstellungen",
                    items=[
                        MenuItem("Profil", icon="👤", key="profile"),
                        MenuItem("Themes", icon="🎨", key="themes"),
                    ]
                )
            ]

            selected = sidebar.render(groups)
            if selected:
                st.write(f"Ausgewählt: {selected}")
            ```
        """
        # Injiziere CSS
        self.inject_sidebar_css()

        selected_item = None

        # Rendere Menü-Gruppen
        for i, group in enumerate(menu_groups):
            result = self.render_menu_group(group, i)
            if result:
                selected_item = result

            # Trennlinie nach Gruppe (außer nach letzter)
            if show_dividers and i < len(menu_groups) - 1:
                st.markdown(
                    '<div class="shadcn-sidebar-divider"></div>',
                    unsafe_allow_html=True
                )

        # Footer-Content
        if footer_content:
            st.markdown(
                '<div class="shadcn-sidebar-footer"></div>',
                unsafe_allow_html=True
            )
            footer_content()

        return selected_item


def create_sidebar_menu(
    menu_groups: List[MenuGroup],
    theme_manager: Optional[Any] = None,
    **kwargs
) -> Optional[str]:
    """
    Convenience-Funktion zum Erstellen einer Sidebar

    Args:
        menu_groups: Liste von MenuGroup-Objekten
        theme_manager: Optional ThemeManager
        **kwargs: Zusätzliche Argumente für ShadcnSidebar.render()

    Returns:
        Key des geklickten Menü-Eintrags oder None

    Example:
        ```python
        from utils.shadcn_sidebar import create_sidebar_menu, MenuGroup, MenuItem

        groups = [
            MenuGroup(
                title="Navigation",
                items=[
                    MenuItem("Home", icon="🏠", key="home"),
                    MenuItem("About", icon="ℹ️", key="about"),
                ]
            )
        ]

        selected = create_sidebar_menu(groups)
        ```
    """
    sidebar = ShadcnSidebar(theme_manager)
    return sidebar.render(menu_groups, **kwargs)


# Beispiel-Menü-Konfigurationen
def get_default_menu() -> List[MenuGroup]:
    """
    Gibt eine Standard-Menü-Konfiguration zurück

    Returns:
        Liste von MenuGroup-Objekten
    """
    return [
        MenuGroup(
            title="Hauptmenü",
            items=[
                MenuItem(label="Dashboard", icon="📊", key="dashboard"),
                MenuItem(label="Projekte", icon="📁", key="projects"),
                MenuItem(label="Berichte", icon="📈", key="reports"),
            ]
        ),
        MenuGroup(
            title="Verwaltung",
            items=[
                MenuItem(label="Benutzer", icon="👥", key="users"),
                MenuItem(label="Einstellungen", icon="⚙️", key="settings"),
            ]
        ),
        MenuGroup(
            title="Hilfe",
            items=[
                MenuItem(label="Dokumentation", icon="📚", key="docs"),
                MenuItem(label="Support", icon="💬", key="support"),
            ]
        )
    ]


def get_solar_calculator_menu() -> List[MenuGroup]:
    """
    Gibt eine Menü-Konfiguration für Solar-Rechner zurück

    Returns:
        Liste von MenuGroup-Objekten
    """
    return [
        MenuGroup(
            title="Kalkulation",
            items=[
                MenuItem(
                    label="Solar-Rechner",
                    icon="☀️",
                    key="solar_calculator"
                ),
                MenuItem(
                    label="Wärmepumpe",
                    icon="🔥",
                    key="heatpump"
                ),
                MenuItem(
                    label="3D-Visualisierung",
                    icon="🏠",
                    key="3d_view"
                ),
            ]
        ),
        MenuGroup(
            title="Verwaltung",
            items=[
                MenuItem(label="CRM", icon="👥", key="crm"),
                MenuItem(label="Angebote", icon="📄", key="offers"),
                MenuItem(label="Produkte", icon="📦", key="products"),
            ]
        ),
        MenuGroup(
            title="Administration",
            items=[
                MenuItem(label="Admin-Panel", icon="⚙️", key="admin"),
                MenuItem(label="Preismatrix", icon="💰", key="pricing"),
                MenuItem(label="Themes", icon="🎨", key="themes"),
            ]
        )
    ]
