"""
Demo: Auto-Contrast System

Zeigt wie das Auto-Contrast-System automatisch Textfarben anpasst,
damit diese immer lesbar sind - egal ob heller oder dunkler Hintergrund.
"""

import streamlit as st
from theming.theme_manager import ThemeManager
from utils.contrast_utils import (
    get_accessible_text_color,
    get_contrast_ratio,
    is_light_color,
    meets_wcag_aa,
    meets_wcag_aaa
)

st.set_page_config(
    page_title="Auto-Contrast Demo",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Auto-Contrast System Demo")
st.markdown("---")

# Initialisiere Theme Manager
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')
    st.session_state.theme_manager.inject_auto_contrast()

tm = st.session_state.theme_manager

# Demo-Sektion 1: Theme-Informationen
st.header("1. Aktuelles Theme")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Theme-Name", tm.get_current_theme())
    
with col2:
    is_dark = tm.is_dark_theme()
    st.metric("Theme-Typ", "Dunkel" if is_dark else "Hell")
    
with col3:
    colors = tm.get_theme_colors_dict()
    st.metric("Verfügbare Farben", len(colors))

st.markdown("---")

# Demo-Sektion 2: Farbbeispiele
st.header("2. Auto-Contrast in Aktion")
st.write("Der Text passt sich automatisch dem Hintergrund an:")

# Beispiel-Farben (verschiedene Helligkeiten)
test_colors = [
    ("#000000", "Schwarz"),
    ("#1E1E1E", "Dunkelgrau"),
    ("#3B82F6", "Blau"),
    ("#EF4444", "Rot"),
    ("#10B981", "Grün"),
    ("#F59E0B", "Orange"),
    ("#FFFFFF", "Weiß"),
    ("#F5F5F5", "Hellgrau"),
]

cols = st.columns(4)
for i, (bg_color, name) in enumerate(test_colors):
    col = cols[i % 4]
    
    # Berechne optimale Textfarbe
    text_color = get_accessible_text_color(bg_color)
    
    # Zeige Beispiel
    with col:
        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                color: {text_color};
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 10px;
            ">
                <strong>{name}</strong><br>
                BG: {bg_color}<br>
                Text: {text_color}
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# Demo-Sektion 3: Kontrast-Checker
st.header("3. Kontrast-Checker")
st.write("Prüfe beliebige Farbkombinationen:")

col1, col2 = st.columns(2)

with col1:
    bg_input = st.color_picker("Hintergrundfarbe", "#1E1E1E")
    
with col2:
    text_input = st.color_picker("Textfarbe (oder Auto)", "#FFFFFF")

# Berechne Kontrast
ratio = get_contrast_ratio(bg_input, text_input)
wcag_aa = meets_wcag_aa(bg_input, text_input)
wcag_aaa = meets_wcag_aaa(bg_input, text_input)
suggested = get_accessible_text_color(bg_input)

# Zeige Ergebnisse
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Kontrastverhältnis", f"{ratio:.2f}:1")
    
with col2:
    st.metric("WCAG AA", "✅ Bestanden" if wcag_aa else "❌ Nicht bestanden")
    
with col3:
    st.metric("WCAG AAA", "✅ Bestanden" if wcag_aaa else "❌ Nicht bestanden")
    
with col4:
    st.metric("Empfohlene Textfarbe", suggested)

# Zeige Vorschau
st.subheader("Vorschau")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Deine Kombination:**")
    st.markdown(
        f"""
        <div style="
            background-color: {bg_input};
            color: {text_input};
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        ">
            <h3>Beispieltext</h3>
            <p>Dies ist ein Beispieltext mit deiner gewählten Farbkombination.</p>
            <p>Ratio: {ratio:.2f}:1</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("**Empfohlene Kombination:**")
    st.markdown(
        f"""
        <div style="
            background-color: {bg_input};
            color: {suggested};
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        ">
            <h3>Beispieltext</h3>
            <p>Dies ist ein Beispieltext mit der empfohlenen Farbkombination.</p>
            <p>Ratio: {get_contrast_ratio(bg_input, suggested):.2f}:1</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Demo-Sektion 4: Theme-Farben-Test
st.header("4. Theme-Farben Auto-Contrast")
st.write("Alle Theme-Farben mit automatischer Textfarbe:")

theme_colors = tm.get_theme_colors_dict()

cols = st.columns(3)
for i, (name, color) in enumerate(theme_colors.items()):
    col = cols[i % 3]
    
    text_color = get_accessible_text_color(color)
    ratio = get_contrast_ratio(color, text_color)
    
    with col:
        st.markdown(
            f"""
            <div style="
                background-color: {color};
                color: {text_color};
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            ">
                <strong>{name.replace('_', ' ').title()}</strong><br>
                {color}<br>
                Ratio: {ratio:.2f}:1
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# Demo-Sektion 5: Informationen
st.header("5. WCAG-Standards")

col1, col2 = st.columns(2)

with col1:
    st.subheader("WCAG 2.1 AA")
    st.write("""
    **Mindest-Kontrastverhältnisse:**
    - Normaler Text: **4.5:1**
    - Großer Text (≥18pt oder ≥14pt bold): **3:1**
    
    Dies ist der empfohlene Standard für Barrierefreiheit.
    """)

with col2:
    st.subheader("WCAG 2.1 AAA")
    st.write("""
    **Mindest-Kontrastverhältnisse:**
    - Normaler Text: **7:1**
    - Großer Text (≥18pt oder ≥14pt bold): **4.5:1**
    
    Dies ist der erweiterte Standard für erhöhte Barrierefreiheit.
    """)

st.markdown("---")

# Demo-Sektion 6: Vorher/Nachher
st.header("6. Vorher/Nachher Vergleich")
st.write("Sehe den Unterschied mit und ohne Auto-Contrast:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**❌ OHNE Auto-Contrast (schlecht lesbar)**")
    st.markdown(
        """
        <div style="
            background-color: #1E1E1E;
            color: #1E1E1E;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        ">
            <h3>Dieser Text ist fast unsichtbar!</h3>
            <p>Dunkle Schrift auf dunklem Hintergrund = ❌</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("**✅ MIT Auto-Contrast (gut lesbar)**")
    dark_bg = "#1E1E1E"
    auto_text = get_accessible_text_color(dark_bg)
    st.markdown(
        f"""
        <div style="
            background-color: {dark_bg};
            color: {auto_text};
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        ">
            <h3>Dieser Text ist perfekt lesbar!</h3>
            <p>Auto-Contrast wählt automatisch helle Schrift = ✅</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Footer
st.info("""
**💡 Zusammenfassung:**

Das Auto-Contrast-System stellt sicher, dass:
- ✅ Text **immer lesbar** ist, egal welcher Hintergrund
- ✅ **WCAG 2.1 AA Standards** eingehalten werden (4.5:1 Mindestkontrast)
- ✅ Die Anpassung **automatisch** erfolgt
- ✅ Sowohl **helle als auch dunkle Themes** unterstützt werden
- ✅ **Alle Menüs, Buttons, Cards** etc. korrekte Textfarben haben

Das System wird automatisch in der gesamten App aktiviert!
""")

st.success("✅ Auto-Contrast ist aktiv und schützt vor unlesbaren Texten!")
