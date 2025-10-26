"""
Test-Skript für CSS-Template-Integration
"""
import streamlit as st

from css_template_manager import get_css_manager

st.set_page_config(page_title="CSS Test", layout="wide")

st.title("🎨 CSS Template Test")

# CSS laden
css_manager = get_css_manager()
template_count = css_manager.inject_into_streamlit(
    load_intro=False,  # Kein Intro für Test
    load_context_menu=False,  # Kein Context Menu für Test
    app_name="Test App"
)

st.success(f"✅ {template_count} CSS-Templates geladen")

# Test-Komponenten
st.write("## Test-Komponenten")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="glass" style="padding:20px;">',
        unsafe_allow_html=True)
    st.subheader("Glass Effect")
    st.write("Dieser Container hat Glasmorphism-Effekt")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(
        '<div class="neu" style="padding:20px;">',
        unsafe_allow_html=True)
    st.subheader("Neumorphism")
    st.write("Dieser Container hat Neumorphism-Effekt")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown(
        '<div class="neu-inset" style="padding:20px;">',
        unsafe_allow_html=True)
    st.subheader("Neu Inset")
    st.write("Dieser Container hat eingelassenen Neumorph-Effekt")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# Buttons
st.write("## Buttons")
c1, c2, c3 = st.columns(3)
with c1:
    st.button("Primär Button", key="btn1", type="primary")
with c2:
    st.button("Sekundär Button", key="btn2")
with c3:
    st.button("Info Button", key="btn3")

st.write("---")

# Inputs
st.write("## Input-Felder")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Name", placeholder="Ihr Name...")
    st.text_area("Nachricht", placeholder="Ihre Nachricht...")
with col2:
    st.selectbox("Auswahl", ["Option 1", "Option 2", "Option 3"])
    st.slider("Wert", 0, 100, 50)

st.write("---")

# Tabs
st.write("## Tabs")
tab1, tab2, tab3 = st.tabs(["🏠 Tab 1", "📊 Tab 2", "⚙️ Tab 3"])

with tab1:
    st.write("Inhalt von Tab 1")
    st.info("Dies ist eine Info-Box")

with tab2:
    st.write("Inhalt von Tab 2")
    st.success("Dies ist eine Success-Box")

with tab3:
    st.write("Inhalt von Tab 3")
    st.warning("Dies ist eine Warning-Box")

st.write("---")

# Expander
with st.expander("🔽 Erweiterte Optionen"):
    st.write("Dieser Expander hat Glasmorphism-Effekt")
    st.checkbox("Option 1")
    st.checkbox("Option 2")
    st.checkbox("Option 3")

st.write("---")

# Progress
st.write("## Progress Bar")
st.markdown('<div class="progress-glow"></div>', unsafe_allow_html=True)
st.progress(0.75, text="75% abgeschlossen")

st.write("---")

# Metrics
st.write("## Metrics")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Temperatur", "24°C", "+2°C")
with c2:
    st.metric("Luftfeuchtigkeit", "65%", "-5%")
with c3:
    st.metric("Luftdruck", "1013 hPa", "0 hPa")
