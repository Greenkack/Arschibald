"""
Demo für die shadcn/ui Card-Komponente

Dieses Skript demonstriert alle Features der Card-Komponente.
"""

import streamlit as st
from components import Card
from components.card import card
from theming import ThemeManager

# Seiten-Konfiguration
st.set_page_config(
    page_title="Card Component Demo",
    page_icon="",
    layout="wide"
)

# Theme Manager initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# CSS injizieren
from theming import CSSGenerator
css_gen = CSSGenerator(theme_manager.current_theme)
css = css_gen.generate_full_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Titel
st.title(" Card Component Demo")
st.markdown("Demonstration aller Features der shadcn/ui Card-Komponente")

# Sidebar für Optionen
with st.sidebar:
    st.header("Optionen")
    
    demo_variant = st.selectbox(
        "Card-Variante",
        ["default", "outlined", "elevated"],
        index=0
    )
    
    demo_badge_variant = st.selectbox(
        "Badge-Variante",
        ["default", "success", "warning", "error", "info"],
        index=0
    )
    
    show_icon = st.checkbox("Icon anzeigen", value=True)
    show_badge = st.checkbox("Badge anzeigen", value=True)
    show_description = st.checkbox("Beschreibung anzeigen", value=True)
    show_footer = st.checkbox("Footer anzeigen", value=True)
    hover_effect = st.checkbox("Hover-Effekt", value=True)

st.divider()

# === SECTION 1: Basis-Verwendung ===
st.header("1. Basis-Verwendung")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Einfache Card")
    st.code("""
card(
    title="Einfache Card",
    content="Minimale Card mit nur Titel und Inhalt"
)
    """)
    
    card(
        title="Einfache Card",
        content="Minimale Card mit nur Titel und Inhalt",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Card mit allen Features")
    st.code("""
card(
    title="Vollständige Card",
    description="Mit allen Features",
    content="Hauptinhalt hier",
    footer="Footer-Text",
    icon="",
    badge="Neu",
    badge_variant="success"
)
    """)
    
    card(
        title="Vollständige Card",
        description="Mit allen Features",
        content="Hauptinhalt hier",
        footer="Footer-Text",
        icon="",
        badge="Neu",
        badge_variant="success",
        theme_manager=theme_manager
    )

st.divider()

# === SECTION 2: Varianten ===
st.header("2. Card-Varianten")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Default")
    card(
        title="Default Card",
        content="Standard-Variante mit leichtem Schatten und Border",
        variant="default",
        icon="",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("Outlined")
    card(
        title="Outlined Card",
        content="Variante mit stärkerem Border, ohne Schatten",
        variant="outlined",
        icon="",
        theme_manager=theme_manager
    )

with col3:
    st.subheader("Elevated")
    card(
        title="Elevated Card",
        content="Variante mit starkem Schatten für Hervorhebung",
        variant="elevated",
        icon="",
        theme_manager=theme_manager
    )

st.divider()

# === SECTION 3: Badge-Varianten ===
st.header("3. Badge-Varianten")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    card(
        title="Default",
        content="Standard Badge",
        badge="Default",
        badge_variant="default",
        variant="outlined",
        theme_manager=theme_manager
    )

with col2:
    card(
        title="Success",
        content="Erfolgs-Badge",
        badge="Aktiv",
        badge_variant="success",
        variant="outlined",
        theme_manager=theme_manager
    )

with col3:
    card(
        title="Warning",
        content="Warnungs-Badge",
        badge="Achtung",
        badge_variant="warning",
        variant="outlined",
        theme_manager=theme_manager
    )

with col4:
    card(
        title="Error",
        content="Fehler-Badge",
        badge="Offline",
        badge_variant="error",
        variant="outlined",
        theme_manager=theme_manager
    )

with col5:
    card(
        title="Info",
        content="Info-Badge",
        badge="Beta",
        badge_variant="info",
        variant="outlined",
        theme_manager=theme_manager
    )

st.divider()

# === SECTION 4: Praktische Beispiele ===
st.header("4. Praktische Beispiele")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Dashboard-Metrik")
    card(
        title="Gesamtertrag",
        description="Heute",
        content="<h1 style='margin:0; font-size: 3rem; text-align: center;'>28.5 kWh</h1>",
        footer="↑ 12% vs. gestern",
        variant="elevated",
        icon="",
        badge="+12%",
        badge_variant="success",
        theme_manager=theme_manager
    )

with col2:
    st.subheader("System-Status")
    card(
        title="System-Status",
        description="Alle Systeme betriebsbereit",
        content="""
            <div style='display: flex; flex-direction: column; gap: 0.5rem;'>
                <div> Wechselrichter</div>
                <div> Speicher</div>
                <div> Monitoring</div>
            </div>
        """,
        footer="Letzte Prüfung: vor 2 Minuten",
        variant="outlined",
        icon="",
        badge="Online",
        badge_variant="success",
        theme_manager=theme_manager
    )

with col3:
    st.subheader("Wartungs-Hinweis")
    card(
        title="Wartung erforderlich",
        description="Nächste Wartung überfällig",
        content="Bitte kontaktieren Sie den Service für eine Wartung der Solaranlage.",
        footer="Fällig seit: 10.11.2025",
        variant="default",
        icon="",
        badge="Dringend",
        badge_variant="warning",
        theme_manager=theme_manager
    )

st.divider()

# === SECTION 5: Interaktive Demo ===
st.header("5. Interaktive Demo")
st.markdown("Passen Sie die Card-Eigenschaften in der Sidebar an:")

card(
    title="Interaktive Demo-Card",
    description="Beschreibung der Card" if show_description else None,
    content="""
        <p>Dies ist eine interaktive Demo-Card.</p>
        <p>Ändern Sie die Optionen in der Sidebar, um verschiedene Konfigurationen zu testen.</p>
    """,
    footer="Footer-Bereich" if show_footer else None,
    variant=demo_variant,
    icon="" if show_icon else None,
    badge="Demo" if show_badge else None,
    badge_variant=demo_badge_variant,
    hover_effect=hover_effect,
    theme_manager=theme_manager
)

st.divider()

# === SECTION 6: Grid-Layout ===
st.header("6. Grid-Layout mit Cards")

col1, col2, col3, col4 = st.columns(4)

metrics = [
    ("Leistung", "4.5 kW", "", "success"),
    ("Ertrag", "28 kWh", "", "info"),
    ("Effizienz", "94%", "", "success"),
    ("Temperatur", "45°C", "", "warning"),
]

for col, (title, value, icon, badge_var) in zip([col1, col2, col3, col4], metrics):
    with col:
        card(
            title=title,
            content=f"<h2 style='margin:0; text-align: center;'>{value}</h2>",
            variant="elevated",
            icon=icon,
            badge="Live",
            badge_variant=badge_var,
            theme_manager=theme_manager
        )

st.divider()

# === SECTION 7: Mit Streamlit-Komponenten ===
st.header("7. Cards mit Streamlit-Komponenten")

col1, col2 = st.columns(2)

with col1:
    card(
        title="Einstellungen",
        description="Passen Sie die Parameter an",
        content="",
        variant="outlined",
        icon="",
        theme_manager=theme_manager
    )
    
    # Streamlit-Komponenten nach der Card
    st.slider("Leistung (kW)", 0.0, 10.0, 5.0)
    st.selectbox("Modus", ["Auto", "Manuell", "Eco"])
    st.button("Speichern")

with col2:
    card(
        title="Daten-Export",
        description="Exportieren Sie Ihre Daten",
        content="",
        variant="outlined",
        icon="",
        theme_manager=theme_manager
    )
    
    # Streamlit-Komponenten nach der Card
    st.radio("Format", ["CSV", "Excel", "JSON"])
    st.date_input("Zeitraum von")
    st.button("Exportieren")

st.divider()

# === SECTION 8: Custom CSS ===
st.header("8. Custom CSS")

card(
    title="Card mit Custom CSS",
    content="Diese Card hat zusätzliches Custom-Styling",
    variant="elevated",
    icon="",
    custom_css="""
        .shadcn-card-body-* {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 0.5rem;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
    """,
    theme_manager=theme_manager
)

st.divider()

# === SECTION 9: Code-Beispiele ===
st.header("9. Code-Beispiele")

with st.expander("Basis-Verwendung"):
    st.code("""
from components.card import card

card(
    title="Meine Card",
    content="Inhalt hier",
    variant="elevated"
)
    """, language="python")

with st.expander("Mit Theme-Manager"):
    st.code("""
from components import Card
from theming import ThemeManager

theme_manager = st.session_state.theme_manager
card = Card(theme_manager=theme_manager)

card.render(
    title="Themed Card",
    content="Diese Card verwendet den Theme-Manager",
    variant="elevated"
)
    """, language="python")

with st.expander("Mehrere Cards in Schleife"):
    st.code("""
for i in range(5):
    card(
        title=f"Card {i+1}",
        content=f"Inhalt für Card {i+1}",
        key=f"card_{i}",
        variant="outlined"
    )
    """, language="python")

st.divider()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #71717a;'>
    <p>shadcn/ui Card Component Demo</p>
    <p>Erstellt mit  für Streamlit</p>
</div>
""", unsafe_allow_html=True)
