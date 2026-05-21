"""
Demo: shadcn/ui Sidebar

Demonstriert die Verwendung der modernen Sidebar-Komponente mit shadcn/ui-Design.
"""

import streamlit as st
from utils.shadcn_sidebar import (
    ShadcnSidebar,
    MenuGroup,
    MenuItem,
    create_sidebar_menu,
    get_default_menu,
    get_solar_calculator_menu
)
from theming import ThemeManager


def main():
    st.set_page_config(
        page_title="shadcn/ui Sidebar Demo",
        page_
        layout="wide"
    )

    # Initialisiere ThemeManager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')

    # Injiziere Theme CSS
    theme_css = st.session_state.theme_manager.generate_css()
    st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

    st.title(" shadcn/ui Sidebar Demo")
    st.markdown("---")

    # Demo-Auswahl
    demo_type = st.radio(
        "Wähle Demo:",
        [
            "Basis-Sidebar",
            "Mit Callbacks",
            "Kollabierbare Gruppen",
            "Mit Footer",
            "Deaktivierte Einträge",
            "Vordefinierte Menüs",
            "Solar-Rechner-Menü",
            "Convenience-Funktion"
        ],
        horizontal=True
    )

    st.markdown("---")

    # Sidebar-Container
    with st.sidebar:
        st.markdown("### Sidebar Demo")
        st.markdown("---")

        if demo_type == "Basis-Sidebar":
            demo_basic_sidebar()
        elif demo_type == "Mit Callbacks":
            demo_with_callbacks()
        elif demo_type == "Kollabierbare Gruppen":
            demo_collapsible_groups()
        elif demo_type == "Mit Footer":
            demo_with_footer()
        elif demo_type == "Deaktivierte Einträge":
            demo_disabled_items()
        elif demo_type == "Vordefinierte Menüs":
            demo_predefined_menus()
        elif demo_type == "Solar-Rechner-Menü":
            demo_solar_menu()
        elif demo_type == "Convenience-Funktion":
            demo_convenience_function()

    # Hauptbereich
    show_main_content(demo_type)


def demo_basic_sidebar():
    """Demo: Basis-Sidebar"""
    st.markdown("#### Basis-Sidebar")
    st.caption("Einfache Sidebar mit Menü-Gruppen und Icons")

    sidebar = ShadcnSidebar()

    groups = [
        MenuGroup(
            title="Navigation",
            items=[
                MenuItem(label="Home", key="home"),
                MenuItem(label="About", icon="ℹ", key="about"),
                MenuItem(label="Contact", key="contact"),
            ]
        ),
        MenuGroup(
            title="Features",
            items=[
                MenuItem(label="Dashboard", key="dashboard"),
                MenuItem(label="Analytics", key="analytics"),
                MenuItem(label="Reports", key="reports"),
            ]
        )
    ]

    selected = sidebar.render(groups)

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_with_callbacks():
    """Demo: Mit Callbacks"""
    st.markdown("#### Mit Callbacks")
    st.caption("Menü-Einträge mit Callback-Funktionen")

    def on_dashboard_click():
        st.session_state.callback_message = "Dashboard wurde geöffnet!"

    def on_settings_click():
        st.session_state.callback_message = "Einstellungen wurden geöffnet!"

    sidebar = ShadcnSidebar()

    groups = [
        MenuGroup(
            title="Hauptmenü",
            items=[
                MenuItem(
                    label="Dashboard",
                    key="dashboard_cb",
                    callback=on_dashboard_click
                ),
                MenuItem(
                    label="Einstellungen",
                    key="settings_cb",
                    callback=on_settings_click
                ),
            ]
        )
    ]

    sidebar.render(groups)

    if 'callback_message' in st.session_state:
        st.info(st.session_state.callback_message)


def demo_collapsible_groups():
    """Demo: Kollabierbare Gruppen"""
    st.markdown("#### Kollabierbare Gruppen")
    st.caption("Gruppen können ein-/ausgeklappt werden")

    sidebar = ShadcnSidebar()

    groups = [
        MenuGroup(
            title="Immer sichtbar",
            items=[
                MenuItem(label="Home", key="home_coll"),
                MenuItem(label="Dashboard", key="dash_coll"),
            ]
        ),
        MenuGroup(
            title="Erweiterte Optionen",
            items=[
                MenuItem(label="Option 1", icon="1⃣", key="opt1"),
                MenuItem(label="Option 2", icon="2⃣", key="opt2"),
                MenuItem(label="Option 3", icon="3⃣", key="opt3"),
            ],
            collapsible=True,
            collapsed=True
        ),
        MenuGroup(
            title="Admin-Bereich",
            items=[
                MenuItem(label="Benutzer", key="users_coll"),
                MenuItem(label="Logs", key="logs_coll"),
            ],
            collapsible=True,
            collapsed=False
        )
    ]

    selected = sidebar.render(groups)

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_with_footer():
    """Demo: Mit Footer"""
    st.markdown("#### Mit Footer")
    st.caption("Sidebar mit Footer-Bereich")

    def render_footer():
        st.markdown("---")
        st.caption(" Version 1.0.0")
        st.caption("© 2024 Firma GmbH")
        st.caption(" www.example.com")

    sidebar = ShadcnSidebar()

    groups = [
        MenuGroup(
            title="Navigation",
            items=[
                MenuItem(label="Home", key="home_footer"),
                MenuItem(label="About", icon="ℹ", key="about_footer"),
            ]
        )
    ]

    selected = sidebar.render(groups, footer_content=render_footer)

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_disabled_items():
    """Demo: Deaktivierte Einträge"""
    st.markdown("#### Deaktivierte Einträge")
    st.caption("Einige Menü-Einträge sind deaktiviert")

    sidebar = ShadcnSidebar()

    groups = [
        MenuGroup(
            title="Features",
            items=[
                MenuItem(
                    label="Verfügbar",
                    key="available"
                ),
                MenuItem(
                    label="In Entwicklung",
                    key="dev",
                    disabled=True
                ),
                MenuItem(
                    label="Bald verfügbar",
                    key="soon",
                    disabled=True
                ),
                MenuItem(
                    label="Beta",
                    key="beta"
                ),
            ]
        )
    ]

    selected = sidebar.render(groups)

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_predefined_menus():
    """Demo: Vordefinierte Menüs"""
    st.markdown("#### Vordefinierte Menüs")
    st.caption("Standard-Menü-Konfiguration")

    sidebar = ShadcnSidebar()
    selected = sidebar.render(get_default_menu())

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_solar_menu():
    """Demo: Solar-Rechner-Menü"""
    st.markdown("#### Solar-Rechner-Menü")
    st.caption("Menü für Solar-Kalkulations-App")

    sidebar = ShadcnSidebar()
    selected = sidebar.render(get_solar_calculator_menu())

    if selected:
        st.success(f" Ausgewählt: {selected}")


def demo_convenience_function():
    """Demo: Convenience-Funktion"""
    st.markdown("#### Convenience-Funktion")
    st.caption("Vereinfachte API mit create_sidebar_menu()")

    groups = [
        MenuGroup(
            title="Quick Menu",
            items=[
                MenuItem("Item 1", icon="1⃣", key="item1_conv"),
                MenuItem("Item 2", icon="2⃣", key="item2_conv"),
                MenuItem("Item 3", icon="3⃣", key="item3_conv"),
            ]
        )
    ]

    selected = create_sidebar_menu(
        groups,
        theme_manager=st.session_state.theme_manager
    )

    if selected:
        st.success(f" Ausgewählt: {selected}")


def show_main_content(demo_type: str):
    """Zeigt Hauptbereich-Content"""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(" Code-Beispiel")

        if demo_type == "Basis-Sidebar":
            st.code("""
from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem

sidebar = ShadcnSidebar()

groups = [
    MenuGroup(
        title="Navigation",
        items=[
            MenuItem(label="Home", key="home"),
            MenuItem(label="About", icon="ℹ", key="about"),
        ]
    )
]

selected = sidebar.render(groups)
            """, language="python")

        elif demo_type == "Mit Callbacks":
            st.code("""
def on_click():
    st.success("Geklickt!")

groups = [
    MenuGroup(
        title="Menü",
        items=[
            MenuItem(
                label="Button",
                key="btn",
                callback=on_click
            ),
        ]
    )
]

sidebar.render(groups)
            """, language="python")

        elif demo_type == "Kollabierbare Gruppen":
            st.code("""
groups = [
    MenuGroup(
        title="Erweitert",
        items=[...],
        collapsible=True,
        collapsed=True  # Initial kollabiert
    )
]

sidebar.render(groups)
            """, language="python")

        elif demo_type == "Mit Footer":
            st.code("""
def render_footer():
    st.caption("Version 1.0.0")

sidebar.render(groups, footer_content=render_footer)
            """, language="python")

        elif demo_type == "Deaktivierte Einträge":
            st.code("""
MenuItem(
    label="Bald verfügbar",
    key="soon",
    disabled=True
)
            """, language="python")

        elif demo_type == "Vordefinierte Menüs":
            st.code("""
from utils.shadcn_sidebar import get_default_menu

sidebar.render(get_default_menu())
            """, language="python")

        elif demo_type == "Solar-Rechner-Menü":
            st.code("""
from utils.shadcn_sidebar import get_solar_calculator_menu

sidebar.render(get_solar_calculator_menu())
            """, language="python")

        elif demo_type == "Convenience-Funktion":
            st.code("""
from utils.shadcn_sidebar import create_sidebar_menu

selected = create_sidebar_menu(groups)
            """, language="python")

    with col2:
        st.subheader("ℹ Info")

        if demo_type == "Basis-Sidebar":
            st.info("""
**Features:**
- Menü-Gruppen mit Titeln
- Icons für Einträge
- Aktive Hervorhebung
- Hover-Effekte
            """)

        elif demo_type == "Mit Callbacks":
            st.info("""
**Callbacks:**
- Werden beim Klick ausgeführt
- Können State ändern
- Sollten leichtgewichtig sein
            """)

        elif demo_type == "Kollabierbare Gruppen":
            st.info("""
**Kollabierbar:**
- Ein-/Ausklappen per Klick
- Initial-Zustand konfigurierbar
- State wird gespeichert
            """)

        elif demo_type == "Mit Footer":
            st.info("""
**Footer:**
- Am Ende der Sidebar
- Für Versions-Info, Links, etc.
- Callback-Funktion
            """)

        elif demo_type == "Deaktivierte Einträge":
            st.info("""
**Deaktiviert:**
- Nicht klickbar
- Visuell abgeschwächt
- Für "Coming Soon" Features
            """)

        elif demo_type == "Vordefinierte Menüs":
            st.info("""
**Vordefiniert:**
- Standard-Menü-Layouts
- Schneller Start
- Anpassbar
            """)

        elif demo_type == "Solar-Rechner-Menü":
            st.info("""
**Solar-Menü:**
- Speziell für Solar-App
- Alle Hauptbereiche
- Sofort einsatzbereit
            """)

        elif demo_type == "Convenience-Funktion":
            st.info("""
**Convenience:**
- Vereinfachte API
- Weniger Code
- Gleiche Features
            """)

    # Session State Info
    st.markdown("---")
    st.subheader(" Session State")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Aktiver Menü-Eintrag:**")
        active = st.session_state.get('active_menu_item', 'Keiner')
        st.code(active)

    with col2:
        st.write("**Kollabierte Gruppen:**")
        collapsed = st.session_state.get('collapsed_groups', set())
        st.code(str(collapsed) if collapsed else "Keine")


if __name__ == "__main__":
    main()
