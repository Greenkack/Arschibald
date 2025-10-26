"""Test Native Carousel"""
import streamlit as st

from carousel_ui_utils_native import render_vertical_carousel_with_confirmation

st.title("Native Carousel Test")

# Page Options
page_options = [
    ("input", "Projektkonfigurator"),
    ("solar", "Solar Calculator"),
    ("heat", "Wärmepumpe"),
    ("analysis", "Analyse"),
    ("crm", "CRM System"),
    ("settings", "Einstellungen"),
    ("admin", "Administration"),
    ("doc", "Dokumente"),
    ("calc", "Quick-Kalkulator"),
    ("info", "Info & Hilfe"),
]

page_icons = {
    "input": "DATA",
    "solar": "SUN",
    "heat": "HEAT",
    "analysis": "GRAF",
    "crm": "CRM",
    "settings": "SET",
    "admin": "ADM",
    "doc": "DOC",
    "calc": "CALC",
    "info": "INFO",
}

# Sidebar mit Carousel
with st.sidebar:
    st.title("NAVIGATION")

    selected = render_vertical_carousel_with_confirmation(
        state_key="test_page",
        options=page_options,
        icons=page_icons,
        visible_count=5,
        theme="sidebar",
        help_text="Wählen Sie einen Bereich und bestätigen Sie",
    )

    st.write(f"Aktuelle Seite: **{selected}**")

# Main Content
st.write(f"## Aktuelle Seite: {selected}")
st.write("Das Carousel sollte jetzt in der Sidebar funktionieren!")
