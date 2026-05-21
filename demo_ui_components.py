"""
Demo-Seite für shadcn/ui Komponenten
Zeigt alle verfügbaren Komponenten mit interaktiven Beispielen
"""

import streamlit as st
from components.shadcn_ui_integration import (
    button, badge, card, alert, tabs, switch, slider,
    input, textarea, select, checkbox, radio_group, date_picker,
    link, metric, table, element,
    carousel, drawer, skeleton, progress, tooltip, popover, accordion,
    get_available_components, show_availability_status, is_available
)

st.set_page_config(
    page_title="Component Demo - ARSCHIBALD",
    page_icon="🎨",
    layout="wide"
)

st.title("shadcn/ui Komponenten Demo")
st.caption("Interaktive Übersicht aller verfügbaren UI-Komponenten")

# Status der shadcn/ui Library
show_availability_status()

st.divider()

# Tabs für Kategorien
tab1, tab2, tab3, tab4 = st.tabs([
    "Basis Komponenten",
    "Neue Komponenten",
    "Navigation & Layout",
    "Erweiterte Beispiele"
])

# ==================== TAB 1: BASIS KOMPONENTEN ====================
with tab1:
    st.header("Basis Komponenten")
    
    # Buttons
    st.subheader("Buttons")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if button("Primary", variant="default", key="btn_primary"):
            st.success("Primary Button geklickt!")
    
    with col2:
        if button("Secondary", variant="secondary", key="btn_secondary"):
            st.info("Secondary Button geklickt!")
    
    with col3:
        if button("Destructive", variant="destructive", key="btn_destructive"):
            st.error("Destructive Button geklickt!")
    
    with col4:
        if button("Ghost", variant="ghost", key="btn_ghost"):
            st.info("Ghost Button geklickt!")
    
    st.divider()
    
    # Badges
    st.subheader("Badges")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        badge("Default", variant="default")
    
    with col2:
        badge("Secondary", variant="secondary")
    
    with col3:
        badge("Destructive", variant="destructive")
    
    with col4:
        badge("Outline", variant="outline")
    
    st.divider()
    
    # Cards
    st.subheader("Cards")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        card(
            title="Photovoltaik",
            description="PV-Anlagen Kalkulation mit 3D-Visualisierung",
            key="card_pv"
        )
    
    with col2:
        card(
            title="Wärmepumpe",
            description="Effiziente Heizungsplanung",
            key="card_wp"
        )
    
    with col3:
        card(
            title="CRM",
            description="Kundenmanagement & Projekte",
            key="card_crm"
        )
    
    st.divider()
    
    # Alerts
    st.subheader("Alerts")
    
    alert(
        title="Info",
        description="Dies ist eine Info-Nachricht mit Kontext",
        variant="default",
        key="alert_info"
    )
    
    alert(
        title="Warnung",
        description="Bitte beachten Sie diese wichtige Information",
        variant="warning",
        key="alert_warning"
    )
    
    alert(
        title="Fehler",
        description="Ein kritischer Fehler ist aufgetreten",
        variant="destructive",
        key="alert_error"
    )
    
    st.divider()
    
    # Form Inputs
    st.subheader("Form Inputs")
    col1, col2 = st.columns(2)
    
    with col1:
        input(
            label="Name",
            placeholder="Ihr vollständiger Name",
            key="demo_input_name"
        )
        
        textarea(
            label="Beschreibung",
            placeholder="Beschreiben Sie Ihr Projekt...",
            key="demo_textarea"
        )
        
        select(
            label="Bundesland",
            options=["Bayern", "Baden-Württemberg", "Nordrhein-Westfalen", "Hessen"],
            key="demo_select"
        )
    
    with col2:
        checkbox(
            label="Newsletter abonnieren",
            key="demo_checkbox"
        )
        
        radio_group(
            label="Anlagentyp",
            options=["Photovoltaik", "Wärmepumpe", "Kombination"],
            key="demo_radio"
        )
        
        date_picker(
            label="Installationsdatum",
            key="demo_date"
        )

# ==================== TAB 2: NEUE KOMPONENTEN ====================
with tab2:
    st.header("Neue Komponenten (Phase 2)")
    
    # Carousel
    st.subheader("1. Carousel")
    st.caption("Feature Showcase mit Auto-Advance")
    
    carousel_items = [
        {
            "title": "Photovoltaik-Kalkulator",
            "content": "Professionelle PV-Anlagen Planung mit 3D-Visualisierung und Wirtschaftlichkeitsberechnung"
        },
        {
            "title": "Wärmepumpen-Planung",
            "content": "Effiziente Heizungsplanung mit dynamischen Tarifen und Verbrauchsprognose"
        },
        {
            "title": "CRM-System",
            "content": "Integriertes Kundenmanagement mit Projektverfolgung und Dokumentenverwaltung"
        },
        {
            "title": "Controlling & Analytics",
            "content": "Mitarbeiter-Performance Tracking mit Dashboards und automatischen Berichten"
        }
    ]
    
    active_slide = carousel(
        items=carousel_items,
        auto_advance=st.checkbox("Auto-Advance aktivieren", value=False, key="carousel_auto"),
        interval=3000,
        show_dots=True,
        key="demo_carousel"
    )
    
    st.info(f"Aktueller Slide: {active_slide + 1} von {len(carousel_items)}")
    
    st.divider()
    
    # Drawer
    st.subheader("2. Drawer")
    st.caption("Side Panel für Filter, Menüs, etc.")
    
    def drawer_content():
        st.write("Filter & Einstellungen")
        st.selectbox("Status", ["Alle", "Aktiv", "Inaktiv"], key="drawer_status")
        st.slider("Preis", 0, 10000, (0, 5000), key="drawer_price")
        st.multiselect("Tags", ["Solar", "Wärmepumpe", "CRM"], key="drawer_tags")
        
        if st.button("Filter anwenden", key="drawer_apply"):
            st.success("Filter angewendet!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        drawer(
            trigger_label="Drawer Links",
            content=drawer_content,
            side="left",
            size="default",
            key="demo_drawer_left"
        )
    
    with col2:
        drawer(
            trigger_label="Drawer Rechts",
            content=drawer_content,
            side="right",
            size="default",
            key="demo_drawer_right"
        )
    
    with col3:
        drawer(
            trigger_label="Drawer Oben",
            content=drawer_content,
            side="top",
            size="default",
            key="demo_drawer_top"
        )
    
    with col4:
        drawer(
            trigger_label="Drawer Unten",
            content=drawer_content,
            side="bottom",
            size="default",
            key="demo_drawer_bottom"
        )
    
    st.divider()
    
    # Skeleton
    st.subheader("3. Skeleton Loader")
    st.caption("Loading States mit Shimmer-Effekt")
    
    show_skeleton = st.checkbox("Loading State anzeigen", value=True, key="skeleton_toggle")
    
    if show_skeleton:
        skeleton(width="100%", height="20px", count=1, key="skeleton_1")
        skeleton(width="80%", height="20px", count=1, key="skeleton_2")
        skeleton(width="90%", height="20px", count=1, key="skeleton_3")
    else:
        st.success("Daten geladen!")
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        st.write("Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
        st.write("Ut enim ad minim veniam, quis nostrud exercitation ullamco.")
    
    st.divider()
    
    # Progress
    st.subheader("4. Progress Indicators")
    st.caption("Linear und Circular Progress Bars")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Linear Progress:")
        progress_value = st.slider("Progress Wert", 0, 100, 65, key="progress_linear_value")
        progress(
            value=progress_value,
            max_value=100,
            label=f"Export läuft... {progress_value}%",
            variant="default",
            key="demo_progress_linear"
        )
    
    with col2:
        st.write("Circular Progress:")
        circular_value = st.slider("Autarkiegrad", 0, 100, 87, key="progress_circular_value")
        progress(
            value=circular_value,
            max_value=100,
            label="Autarkiegrad",
            variant="circular",
            key="demo_progress_circular"
        )
    
    st.divider()
    
    # Tooltip
    st.subheader("5. Tooltip")
    st.caption("Hover-Texte für zusätzliche Informationen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tooltip(
            content="PV",
            tooltip_text="Photovoltaik - Umwandlung von Sonnenenergie in elektrische Energie",
            key="tooltip_pv"
        )
    
    with col2:
        tooltip(
            content="kWh",
            tooltip_text="Kilowattstunde - Einheit für Energie (1000 Wattstunden)",
            key="tooltip_kwh"
        )
    
    with col3:
        tooltip(
            content="kWp",
            tooltip_text="Kilowatt Peak - Spitzenleistung einer PV-Anlage unter Standardbedingungen",
            key="tooltip_kwp"
        )
    
    st.divider()
    
    # Popover
    st.subheader("6. Popover")
    st.caption("Click-to-Show Content Boxes")
    
    def popover_content_1():
        st.write("Weitere Informationen:")
        st.markdown("- Photovoltaik-Module")
        st.markdown("- Wechselrichter")
        st.markdown("- Montagesystem")
    
    def popover_content_2():
        st.write("Einstellungen:")
        st.checkbox("Dark Mode", key="popover_dark")
        st.checkbox("Notifications", key="popover_notif")
    
    col1, col2 = st.columns(2)
    
    with col1:
        popover(
            trigger_label="Info anzeigen",
            content=popover_content_1,
            key="demo_popover_1"
        )
    
    with col2:
        popover(
            trigger_label="Einstellungen",
            content=popover_content_2,
            key="demo_popover_2"
        )
    
    st.divider()
    
    # Accordion
    st.subheader("7. Accordion")
    st.caption("Collapsible Sections für Formulare und FAQs")
    
    accordion_items = [
        {
            "title": "1. Kundendaten",
            "content": "Name, Adresse, PLZ, Kontaktdaten, E-Mail, Telefon"
        },
        {
            "title": "2. Standortdaten",
            "content": "GPS-Koordinaten, Adresse, Bundesland, Netzbetreiber"
        },
        {
            "title": "3. Dachparameter",
            "content": "Neigung, Ausrichtung, Fläche, Dachtyp, Material"
        },
        {
            "title": "4. Verbrauchsdaten",
            "content": "Jahresverbrauch in kWh, Verbrauchsprofil, Lastgang"
        },
        {
            "title": "5. Erweiterte Optionen",
            "content": "Batteriespeicher, Monitoring, Smart Home Integration"
        }
    ]
    
    allow_multiple = st.checkbox("Mehrere Sections gleichzeitig öffnen", value=False, key="accordion_multiple")
    
    open_indices = accordion(
        items=accordion_items,
        default_open=0,
        allow_multiple=allow_multiple,
        key="demo_accordion"
    )
    
    st.info(f"Geöffnete Sections: {open_indices}")

# ==================== TAB 3: NAVIGATION & LAYOUT ====================
with tab3:
    st.header("Navigation & Layout Komponenten")
    
    # Tabs Component
    st.subheader("Tabs")
    
    tab_items = [
        {"key": "overview", "label": "Übersicht"},
        {"key": "details", "label": "Details"},
        {"key": "settings", "label": "Einstellungen"}
    ]
    
    active_tab = tabs(items=tab_items, default_value="overview", key="demo_tabs")
    
    if active_tab == "overview":
        st.write("Übersicht über alle Daten")
        metric(label="Gesamtertrag", value="45.678 kWh", delta="12%", key="metric_ertrag")
    
    elif active_tab == "details":
        st.write("Detaillierte Ansicht")
        table(
            data={
                "Monat": ["Januar", "Februar", "März"],
                "Ertrag (kWh)": [3500, 4200, 5100],
                "Verbrauch (kWh)": [4000, 3800, 3900]
            },
            key="demo_table"
        )
    
    elif active_tab == "settings":
        st.write("Einstellungen")
        switch(label="Dark Mode", default=False, key="demo_switch_dark")
        switch(label="Notifications", default=True, key="demo_switch_notif")
        slider(label="Font Size", min_value=12, max_value=24, default_value=16, key="demo_slider_font")
    
    st.divider()
    
    # Metrics
    st.subheader("Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric(label="Ertrag", value="45.678 kWh", delta="12%", key="demo_metric_1")
    
    with col2:
        metric(label="Autarkie", value="87,5%", delta="5%", key="demo_metric_2")
    
    with col3:
        metric(label="ROI", value="8,5 Jahre", delta="-0,5 Jahre", key="demo_metric_3")
    
    with col4:
        metric(label="CO2", value="12,3 t", delta="15%", key="demo_metric_4")
    
    st.divider()
    
    # Links
    st.subheader("Links")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        link(text="Dokumentation", url="https://docs.example.com", key="demo_link_1")
    
    with col2:
        link(text="Support", url="https://support.example.com", key="demo_link_2")
    
    with col3:
        link(text="GitHub", url="https://github.com", key="demo_link_3")

# ==================== TAB 4: ERWEITERTE BEISPIELE ====================
with tab4:
    st.header("Erweiterte Beispiele")
    
    # Dashboard mit KPI Cards + Progress Rings
    st.subheader("Dashboard Layout")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        card(title="Gesamtertrag", content="45.678 kWh", key="ex_card_1")
        badge("Heute: 123 kWh", variant="default")
    
    with col2:
        card(title="Autarkie", key="ex_card_2")
        progress(value=87.5, max_value=100, variant="circular", key="ex_progress_1")
    
    with col3:
        card(title="ROI", content="8,5 Jahre", key="ex_card_3")
        badge("Sehr gut", variant="default")
    
    with col4:
        card(title="CO2-Einsparung", content="12,3 Tonnen", key="ex_card_4")
        badge("Exzellent", variant="default")
    
    st.divider()
    
    # Multi-Step Form
    st.subheader("Multi-Step Form mit Progress")
    
    if 'form_step' not in st.session_state:
        st.session_state.form_step = 0
    
    # Progress Indicator
    progress(
        value=st.session_state.form_step * 20,
        max_value=100,
        label=f"Schritt {st.session_state.form_step + 1} von 5",
        variant="default",
        key="form_progress_indicator"
    )
    
    # Accordion für Steps
    form_steps = [
        {"title": "1. Kundendaten", "content": "Name, Adresse, Kontakt"},
        {"title": "2. Standortdaten", "content": "GPS, PLZ, Bundesland"},
        {"title": "3. Dachparameter", "content": "Neigung, Ausrichtung, Fläche"},
        {"title": "4. Verbrauchsdaten", "content": "kWh/Jahr, Verbrauchsprofil"},
        {"title": "5. Optionen", "content": "Speicher, Monitoring"}
    ]
    
    accordion(
        items=form_steps,
        default_open=st.session_state.form_step,
        allow_multiple=False,
        key="form_accordion"
    )
    
    # Navigation Buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if button("Zurück", variant="secondary", key="form_back"):
            if st.session_state.form_step > 0:
                st.session_state.form_step -= 1
                st.rerun()
    
    with col2:
        if button("Weiter", variant="default", key="form_next"):
            if st.session_state.form_step < 4:
                st.session_state.form_step += 1
                st.rerun()
    
    with col3:
        if st.session_state.form_step == 4:
            if button("Absenden", variant="default", key="form_submit"):
                st.success("Formular erfolgreich abgeschickt!")
                st.session_state.form_step = 0
    
    st.divider()
    
    # Loading State Simulation
    st.subheader("Loading State Simulation")
    
    if button("Daten laden", variant="default", key="load_data"):
        st.session_state.loading = True
        st.rerun()
    
    if st.session_state.get('loading', False):
        skeleton(width="100%", height="120px", count=3, key="loading_skeleton")
        
        import time
        time.sleep(2)  # Simulate loading
        st.session_state.loading = False
        st.rerun()
    else:
        card(
            title="Kundendaten",
            description="Max Mustermann, Musterstraße 123, 12345 Musterstadt",
            key="loaded_card_1"
        )
        card(
            title="Projektdaten",
            description="PV-Anlage 10 kWp, Süd-Ausrichtung, 30 Grad Neigung",
            key="loaded_card_2"
        )
        card(
            title="Wirtschaftlichkeit",
            description="ROI 8,5 Jahre, Autarkie 87,5%, CO2-Einsparung 12,3 t",
            key="loaded_card_3"
        )

# Footer
st.divider()
st.caption("shadcn/ui Integration - ARSCHIBALD UI Modernization - Phase 2")
st.caption("Alle Komponenten mit nativen Streamlit Fallbacks")
