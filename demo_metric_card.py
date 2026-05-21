"""
Demo für MetricCard-Komponente

Zeigt alle Features der MetricCard-Komponente.
"""

import streamlit as st
from components.metric_card import metric_card, metric_card_group, MetricCard
from theming import ThemeManager

# Seiten-Konfiguration
st.set_page_config(
    page_title="MetricCard Demo",
    page_
    layout="wide"
)

# Theme Manager initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# CSS injizieren
css = theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Titel
st.title(" MetricCard Komponente Demo")
st.markdown("---")

# Basis-Beispiele
st.header("1. Basis-Beispiele")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Einfache Metrik")
    metric_card(
        label="Umsatz",
        value="€45,231",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Mit positivem Trend")
    metric_card(
        label="Neue Kunden",
        value="1,234",
        trend=12.5,
        trend_label="+12.5% vs. letzter Monat",
        theme_manager=theme_manager
    )

with col3:
    st.subheader("Mit negativem Trend")
    metric_card(
        label="Absprungrate",
        value="23.4%",
        trend=-5.2,
        trend_label="-5.2% vs. letzter Monat",
        theme_manager=theme_manager
    )

st.markdown("---")

# Größen
st.header("2. Verschiedene Größen")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Small")
    metric_card(
        label="Besucher",
        value="12,345",
        trend=8.2,
        size="small",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Medium (Standard)")
    metric_card(
        label="Besucher",
        value="12,345",
        trend=8.2,
        size="medium",
        theme_manager=theme_manager
    )

with col3:
    st.subheader("Large")
    metric_card(
        label="Besucher",
        value="12,345",
        trend=8.2,
        size="large",
        theme_manager=theme_manager
    )

st.markdown("---")

# Varianten
st.header("3. Verschiedene Varianten")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Default")
    metric_card(
        label="Conversion Rate",
        value="3.24%",
        trend=1.2,
        variant="default",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Outlined")
    metric_card(
        label="Conversion Rate",
        value="3.24%",
        trend=1.2,
        variant="outlined",
        theme_manager=theme_manager
    )

with col3:
    st.subheader("Elevated")
    metric_card(
        label="Conversion Rate",
        value="3.24%",
        trend=1.2,
        variant="elevated",
        theme_manager=theme_manager
    )

st.markdown("---")

# Mit Beschreibung
st.header("4. Mit Beschreibung")

col1, col2 = st.columns(2)

with col1:
    metric_card(
        label="Durchschnittlicher Bestellwert",
        value="€127.50",
        description="Basierend auf 1,234 Bestellungen in diesem Monat",
        trend=5.3,
        size="large",
        theme_manager=theme_manager
    )

with col2:
    metric_card(
        label="Kundenzufriedenheit",
        value="4.8/5.0",
        description="Durchschnittliche Bewertung aus 567 Umfragen",
        trend=0.3,
        trend_label="+0.3 Punkte",
        size="large",
        theme_manager=theme_manager
    )

st.markdown("---")

# Ohne Trend-Pfeil
st.header("5. Ohne Trend-Pfeil")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Mit Pfeil (Standard)")
    metric_card(
        label="Wachstum",
        value="+15.2%",
        trend=15.2,
        show_trend_arrow=True,
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Ohne Pfeil")
    metric_card(
        label="Wachstum",
        value="+15.2%",
        trend=15.2,
        show_trend_arrow=False,
        theme_manager=theme_manager
    )

st.markdown("---")

# MetricCard-Gruppe
st.header("6. MetricCard-Gruppe")

st.subheader("Dashboard-Übersicht")

metric_card_group(
    metrics=[
        {
            "label": "Gesamtumsatz",
            "value": "€245,231",
            "trend": 12.5,
            "trend_label": "+12.5% vs. letzter Monat",
            "icon": ""
        },
        {
            "label": "Neue Kunden",
            "value": "1,234",
            "trend": 8.2,
            "trend_label": "+8.2% vs. letzter Monat",
            "icon": ""
        },
        {
            "label": "Bestellungen",
            "value": "3,456",
            "trend": -3.1,
            "trend_label": "-3.1% vs. letzter Monat",
            "icon": ""
        },
        {
            "label": "Conversion Rate",
            "value": "3.24%",
            "trend": 1.2,
            "trend_label": "+1.2% vs. letzter Monat",
            "icon": ""
        }
    ],
    columns=4,
    gap="md",
    variant="elevated",
    theme_manager=theme_manager
)

st.markdown("---")

# Verschiedene Spalten-Layouts
st.header("7. Verschiedene Spalten-Layouts")

st.subheader("2 Spalten")
metric_card_group(
    metrics=[
        {
            "label": "Umsatz",
            "value": "€45,231",
            "trend": 12.5,
            "icon": "",
            "size": "large"
        },
        {
            "label": "Kunden",
            "value": "1,234",
            "trend": -3.2,
            "icon": "",
            "size": "large"
        }
    ],
    columns=2,
    gap="lg",
    theme_manager=theme_manager
)

st.markdown("---")

st.subheader("3 Spalten")
metric_card_group(
    metrics=[
        {
            "label": "Umsatz",
            "value": "€45,231",
            "trend": 12.5,
            "icon": ""
        },
        {
            "label": "Kunden",
            "value": "1,234",
            "trend": -3.2,
            "icon": ""
        },
        {
            "label": "Bestellungen",
            "value": "3,456",
            "trend": 5.7,
            "icon": ""
        }
    ],
    columns=3,
    gap="md",
    theme_manager=theme_manager
)

st.markdown("---")

# Solar-spezifische Metriken
st.header("8. Solar-spezifische Metriken")

st.subheader("Solar-Anlage Dashboard")

metric_card_group(
    metrics=[
        {
            "label": "Aktuelle Leistung",
            "value": "8.5 kW",
            "description": "Von 10 kW Nennleistung",
            "trend": 15.2,
            "trend_label": "+15.2% vs. gestern",
            "icon": "",
            "size": "large"
        },
        {
            "label": "Heutige Erzeugung",
            "value": "42.3 kWh",
            "description": "Seit Sonnenaufgang",
            "trend": 8.5,
            "trend_label": "+8.5% vs. gestern",
            "icon": "",
            "size": "large"
        },
        {
            "label": "CO₂ Einsparung",
            "value": "18.2 kg",
            "description": "Heute eingespart",
            "trend": 8.5,
            "icon": "",
            "size": "large"
        },
        {
            "label": "Eigenverbrauch",
            "value": "68%",
            "description": "Selbst verbraucht",
            "trend": 3.2,
            "trend_label": "+3.2% vs. letzter Monat",
            "icon": "",
            "size": "large"
        }
    ],
    columns=2,
    gap="lg",
    variant="elevated",
    theme_manager=theme_manager
)

st.markdown("---")

# Animation Demo
st.header("9. Animation Demo")

st.info("Die Metriken haben Fade-In und Count-Up Animationen beim ersten Laden.")

if st.button("Metriken neu laden (Animation zeigen)"):
    st.rerun()

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        label="Animiert",
        value="€12,345",
        trend=10.5,
        animate=True,
        theme_manager=theme_manager
    )

with col2:
    metric_card(
        label="Nicht animiert",
        value="€12,345",
        trend=10.5,
        animate=False,
        theme_manager=theme_manager
    )

with col3:
    metric_card(
        label="Animiert",
        value="€12,345",
        trend=10.5,
        animate=True,
        theme_manager=theme_manager
    )

st.markdown("---")

# Code-Beispiele
st.header("10. Code-Beispiele")

with st.expander("Einfache MetricCard"):
    st.code("""
from components.metric_card import metric_card

metric_card(
    label="Umsatz",
    value="€45,231",
    trend=12.5,
    trend_label="+12.5% vs. letzter Monat"
)
    """, language="python")

with st.expander("MetricCard mit Beschreibung"):
    st.code("""
from components.metric_card import metric_card

metric_card(
    label="Durchschnittlicher Bestellwert",
    value="€127.50",
    description="Basierend auf 1,234 Bestellungen",
    trend=5.3,
    size="large"
)
    """, language="python")

with st.expander("MetricCard-Gruppe"):
    st.code("""
from components.metric_card import metric_card_group

metric_card_group(
    metrics=[
        {
            "label": "Umsatz",
            "value": "€45,231",
            "trend": 12.5,
            "icon": ""
        },
        {
            "label": "Kunden",
            "value": "1,234",
            "trend": -3.2,
            "icon": ""
        }
    ],
    columns=2,
    gap="lg",
    variant="elevated"
)
    """, language="python")

st.markdown("---")

# Footer
st.info("""
**Features:**
-  Verschiedene Größen (small, medium, large)
-  Trend-Indikatoren mit Pfeilen und Farben
-  Optionale Icons
-  Animierte Wert-Änderungen
-  Responsive Grid-Layout
-  Verschiedene Varianten (default, outlined, elevated)
-  Beschreibungen und Trend-Labels
""")
