"""
Demo für erweiterte shadcn/ui-Komponenten

Dieses Skript demonstriert alle erweiterten UI-Komponenten:
- Accordion
- Breadcrumb
- Dropdown Menu
- Popover
- Progress
- Skeleton Loader
- Pagination
"""

import streamlit as st
import time

# Importiere Theme Manager
from theming import ThemeManager

# Importiere Komponenten
from components import (
    Accordion, accordion,
    Breadcrumb, breadcrumb,
    DropdownMenu, dropdown_menu,
    Popover, popover,
    Progress, progress,
    Skeleton, SkeletonCard, skeleton, skeleton_card,
    Pagination, pagination
)


def main():
    st.set_page_config(
        page_title="Erweiterte shadcn/ui Komponenten Demo",
        page_
        layout="wide"
    )
    
    st.title(" Erweiterte shadcn/ui Komponenten Demo")
    st.markdown("---")
    
    # Initialisiere Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    # Sidebar für Theme-Auswahl
    with st.sidebar:
        st.header("Theme-Einstellungen")
        theme_names = list(st.session_state.theme_manager.themes.keys())
        current_theme = st.selectbox(
            "Theme wählen",
            theme_names,
            index=theme_names.index(
                st.session_state.theme_manager.current_theme.name
            )
        )
        
        if current_theme != st.session_state.theme_manager.current_theme.name:
            st.session_state.theme_manager.set_theme(current_theme)
            st.rerun()
    
    # Injiziere Theme CSS
    css = st.session_state.theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Tabs für verschiedene Komponenten
    tabs = st.tabs([
        "Accordion",
        "Breadcrumb",
        "Dropdown Menu",
        "Popover",
        "Progress",
        "Skeleton Loader",
        "Pagination"
    ])
    
    # Tab 1: Accordion
    with tabs[0]:
        st.header("Accordion-Komponente")
        st.markdown("Ein Accordion für zusammenklappbare Inhalte.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Single Mode")
            st.markdown("Nur ein Item kann gleichzeitig geöffnet sein.")
            
            acc = Accordion(theme_manager=st.session_state.theme_manager)
            acc.render(
                items=[
                    {
                        "title": "Was ist Solar-Energie?",
                        "content": "Solar-Energie ist die Energie der Sonne, "
                                 "die durch Photovoltaik-Module in "
                                 "elektrischen Strom umgewandelt wird.",
                        "icon": ""
                    },
                    {
                        "title": "Wie funktioniert eine PV-Anlage?",
                        "content": "PV-Module wandeln Sonnenlicht direkt in "
                                 "Gleichstrom um. Ein Wechselrichter "
                                 "konvertiert diesen in Wechselstrom.",
                        "icon": ""
                    },
                    {
                        "title": "Welche Förderungen gibt es?",
                        "content": "Es gibt verschiedene staatliche "
                                 "Förderungen und Einspeisevergütungen "
                                 "für Solaranlagen.",
                        "icon": ""
                    }
                ],
                type="single",
                default_open=[0],
                key="accordion_single"
            )
        
        with col2:
            st.subheader("Multiple Mode")
            st.markdown("Mehrere Items können gleichzeitig geöffnet sein.")
            
            acc2 = Accordion(theme_manager=st.session_state.theme_manager)
            acc2.render(
                items=[
                    {
                        "title": "Technische Details",
                        "content": "Leistung: 10 kWp, Module: 25x 400W, "
                                 "Wechselrichter: 10 kW"
                    },
                    {
                        "title": "Kosten",
                        "content": "Gesamtkosten: 15.000€, "
                                 "Förderung: 3.000€, Eigenanteil: 12.000€"
                    },
                    {
                        "title": "Ertrag",
                        "content": "Jährlicher Ertrag: 10.000 kWh, "
                                 "Eigenverbrauch: 60%, Einspeisung: 40%"
                    }
                ],
                type="multiple",
                default_open=[0, 1],
                key="accordion_multiple"
            )
    
    # Tab 2: Breadcrumb
    with tabs[1]:
        st.header("Breadcrumb-Komponente")
        st.markdown("Eine Breadcrumb-Navigation für hierarchische Pfade.")
        
        st.subheader("Beispiel 1: Einfache Navigation")
        bc = Breadcrumb(theme_manager=st.session_state.theme_manager)
        clicked = bc.render(
            items=[
                {"label": "Home", "icon": ""},
                {"label": "Projekte", "icon": ""},
                {"label": "Solar-Anlage", "icon": ""},
                {"label": "Konfiguration"}
            ],
            separator="/",
            on_click=lambda idx: st.info(f"Navigiere zu Item {idx}"),
            key="breadcrumb_1"
        )
        
        if clicked is not None:
            st.success(f"Item {clicked} wurde geklickt!")
        
        st.markdown("---")
        
        st.subheader("Beispiel 2: Mit Custom Separator")
        bc2 = Breadcrumb(theme_manager=st.session_state.theme_manager)
        bc2.render(
            items=[
                {"label": "Dashboard"},
                {"label": "Kunden"},
                {"label": "Max Mustermann"},
                {"label": "Angebote"}
            ],
            separator="›",
            key="breadcrumb_2"
        )
    
    # Tab 3: Dropdown Menu
    with tabs[2]:
        st.header("Dropdown-Menu-Komponente")
        st.markdown("Ein Dropdown-Menü für Aktionen und Navigation.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Aktions-Menü")
            dd = DropdownMenu(theme_manager=st.session_state.theme_manager)
            selected = dd.render(
                trigger_label="Aktionen",
                trigger_
                items=[
                    {"label": "Bearbeiten", "icon": "", "value": "edit"},
                    {"label": "Duplizieren", "icon": "", "value": "duplicate"},
                    {"separator": True},
                    {
                        "label": "Löschen",
                        "icon": "",
                        "value": "delete",
                        "disabled": False
                    }
                ],
                on_select=lambda val: st.success(f"Aktion: {val}"),
                key="dropdown_actions"
            )
            
            if selected:
                st.info(f"Ausgewählt: {selected}")
        
        with col2:
            st.subheader("Export-Menü")
            dd2 = DropdownMenu(theme_manager=st.session_state.theme_manager)
            selected2 = dd2.render(
                trigger_label="Exportieren",
                trigger_
                items=[
                    {"label": "Als PDF", "icon": "", "value": "pdf"},
                    {"label": "Als Excel", "icon": "", "value": "excel"},
                    {"label": "Als CSV", "icon": "", "value": "csv"},
                    {"separator": True},
                    {"label": "Drucken", "icon": "", "value": "print"}
                ],
                align="right",
                key="dropdown_export"
            )
    
    # Tab 4: Popover
    with tabs[3]:
        st.header("Popover-Komponente")
        st.markdown("Ein Popover für zusätzliche Informationen.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Click Popover")
            st.markdown("Klicken Sie auf den Trigger:")
            
            pop = Popover(theme_manager=st.session_state.theme_manager)
            pop.render(
                trigger_label="Info anzeigen",
                trigger_icon="ℹ",
                title="Wichtige Information",
                content="Dies ist ein Popover mit zusätzlichen "
                       "Informationen. Es kann durch Klicken "
                       "geöffnet und geschlossen werden.",
                position="top",
                trigger_type="click",
                key="popover_click"
            )
        
        with col2:
            st.subheader("Hover Popover")
            st.markdown("Bewegen Sie die Maus über den Text:")
            
            pop2 = Popover(theme_manager=st.session_state.theme_manager)
            pop2.render(
                trigger_label="Hover für Details",
                trigger_
                title="Tipp",
                content="Dieser Popover erscheint beim Hovern über "
                       "dem Trigger-Element.",
                position="bottom",
                trigger_type="hover",
                key="popover_hover"
            )
    
    # Tab 5: Progress
    with tabs[4]:
        st.header("Progress-Komponente")
        st.markdown("Eine Progress-Bar für Fortschrittsanzeigen.")
        
        st.subheader("Verschiedene Varianten")
        
        prog1 = Progress(theme_manager=st.session_state.theme_manager)
        prog1.render(
            value=75,
            label="Upload",
            show_percentage=True,
            variant="default",
            size="md",
            animated=True,
            key="progress_1"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        prog2 = Progress(theme_manager=st.session_state.theme_manager)
        prog2.render(
            value=100,
            label="Abgeschlossen",
            show_percentage=True,
            variant="success",
            size="md",
            animated=False,
            key="progress_2"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        prog3 = Progress(theme_manager=st.session_state.theme_manager)
        prog3.render(
            value=45,
            label="Warnung",
            show_percentage=True,
            variant="warning",
            size="lg",
            animated=True,
            key="progress_3"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        prog4 = Progress(theme_manager=st.session_state.theme_manager)
        prog4.render(
            value=20,
            label="Fehler",
            show_percentage=True,
            variant="error",
            size="sm",
            animated=True,
            key="progress_4"
        )
        
        st.markdown("---")
        
        st.subheader("Interaktive Progress-Bar")
        progress_value = st.slider("Fortschritt", 0, 100, 50)
        
        prog5 = Progress(theme_manager=st.session_state.theme_manager)
        prog5.render(
            value=progress_value,
            label="Dynamischer Fortschritt",
            show_percentage=True,
            variant="default",
            animated=True,
            key="progress_interactive"
        )
    
    # Tab 6: Skeleton Loader
    with tabs[5]:
        st.header("Skeleton-Loader-Komponente")
        st.markdown("Skeleton-Loader für Lade-Zustände.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Text Skeleton")
            skel = Skeleton(theme_manager=st.session_state.theme_manager)
            skel.render(
                variant="text",
                lines=3,
                animated=True,
                key="skeleton_text"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("Circle Skeleton")
            skel2 = Skeleton(theme_manager=st.session_state.theme_manager)
            skel2.render(
                variant="circle",
                width="5rem",
                height="5rem",
                animated=True,
                key="skeleton_circle"
            )
        
        with col2:
            st.subheader("Rectangle Skeleton")
            skel3 = Skeleton(theme_manager=st.session_state.theme_manager)
            skel3.render(
                variant="rectangle",
                width="100%",
                height="10rem",
                animated=True,
                key="skeleton_rectangle"
            )
        
        st.markdown("---")
        
        st.subheader("Card Skeleton")
        skel_card = SkeletonCard(theme_manager=st.session_state.theme_manager)
        skel_card.render(
            show_avatar=True,
            show_footer=True,
            key="skeleton_card"
        )
        
        st.markdown("---")
        
        st.subheader("Lade-Simulation")
        if st.button("Daten laden", key="load_data_btn"):
            with st.spinner("Lade Daten..."):
                # Zeige Skeleton während des Ladens
                skel_loading = SkeletonCard(
                    theme_manager=st.session_state.theme_manager
                )
                skel_loading.render(key="skeleton_loading")
                
                time.sleep(2)
                st.success("Daten geladen!")
    
    # Tab 7: Pagination
    with tabs[6]:
        st.header("Pagination-Komponente")
        st.markdown("Eine Pagination für seitenweise Navigation.")
        
        st.subheader("Beispiel 1: Standard Pagination")
        pag = Pagination(theme_manager=st.session_state.theme_manager)
        current_page = pag.render(
            total_pages=10,
            current_page=1,
            max_visible_pages=5,
            show_first_last=True,
            show_prev_next=True,
            on_page_change=lambda page: st.info(f"Seite {page} geladen"),
            key="pagination_1"
        )
        
        st.write(f"Aktuelle Seite: {current_page}")
        
        st.markdown("---")
        
        st.subheader("Beispiel 2: Viele Seiten")
        pag2 = Pagination(theme_manager=st.session_state.theme_manager)
        current_page2 = pag2.render(
            total_pages=50,
            current_page=1,
            max_visible_pages=7,
            show_first_last=True,
            show_prev_next=True,
            key="pagination_2"
        )
        
        st.write(f"Aktuelle Seite: {current_page2} von 50")
        
        st.markdown("---")
        
        st.subheader("Beispiel 3: Wenige Seiten")
        pag3 = Pagination(theme_manager=st.session_state.theme_manager)
        current_page3 = pag3.render(
            total_pages=3,
            current_page=1,
            show_first_last=False,
            show_prev_next=True,
            key="pagination_3"
        )


if __name__ == "__main__":
    main()
