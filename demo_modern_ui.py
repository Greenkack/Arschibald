"""
DEMO: Modernes UI Design
Zeigt das neue Glasmorphism + Neumorphism Design
"""
import numpy as np
import pandas as pd
import streamlit as st

from css_template_manager import get_css_manager

# Page Config
st.set_page_config(page_title="🎨 Modernes UI Demo", layout="wide")

# CSS laden
css_manager = get_css_manager()
css_manager.inject_into_streamlit(load_intro=False, load_context_menu=False)

# Header
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(0,188,212,0.08));
    border: 2px solid #00E5FF;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 0 40px rgba(0,229,255,0.4);
    backdrop-filter: blur(12px);
    text-align: center;
">
    <h1 style="color: #00E5FF; margin: 0; font-family: Nunito, sans-serif; font-size: 3rem;">
        🎨 Modernes UI Design Demo
    </h1>
    <p style="color: #E6F7FF; margin: 15px 0 0 0; font-size: 1.2rem;">
        Glasmorphism • Neumorphism • Cyan Accents • Dark Theme
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎨 Effekte", "🔘 Buttons", "📝 Inputs", "📊 Charts"])

with tab1:
    st.header("UI-Effekte")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="glass" style="padding:25px; min-height:200px;">',
            unsafe_allow_html=True)
        st.subheader("🔮 Glasmorphism")
        st.write("Transparenter Blur-Effekt")
        st.write("Mit sanften Schatten")
        st.write("Und Glas-Optik")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="neu" style="padding:25px; min-height:200px;">',
            unsafe_allow_html=True)
        st.subheader("⚪ Neumorphism")
        st.write("3D-Schatten-Effekt")
        st.write("Soft-UI Design")
        st.write("Erhabene Optik")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(
            '<div class="neu-inset" style="padding:25px; min-height:200px;">',
            unsafe_allow_html=True)
        st.subheader("🔵 Neu Inset")
        st.write("Eingelassener Effekt")
        st.write("Innen-Schatten")
        st.write("Vertiefte Optik")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("Buttons")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("✨ Primär Button", type="primary", use_container_width=True)
    with col2:
        st.button("📌 Sekundär Button", use_container_width=True)
    with col3:
        st.button("🔔 Info Button", use_container_width=True)
    with col4:
        st.button("⚙️ Settings", use_container_width=True)

    st.write("---")

    # Button Grid
    for i in range(3):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            col.button(f"Button {i * 5 + j + 1}", key=f"btn_{i}_{j}")

with tab3:
    st.header("Input-Felder")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("🏷️ Name", placeholder="Ihr Name...")
        st.text_input("📧 E-Mail", placeholder="ihre@email.de")
        st.text_area(
            "💬 Nachricht",
            placeholder="Ihre Nachricht...",
            height=150)

    with col2:
        st.selectbox(
            "🎯 Kategorie", [
                "Option 1", "Option 2", "Option 3", "Option 4"])
        st.multiselect(
            "🏷️ Tags", [
                "Python", "JavaScript", "CSS", "HTML", "SQL"])
        st.slider("📊 Wert", 0, 100, 50)
        st.slider("📏 Bereich", 0, 100, (20, 80))

with tab4:
    st.header("Charts & Visualisierungen")

    # Dummy Data
    np.random.seed(42)
    df = pd.DataFrame({
        'Monat': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun'],
        'Umsatz': np.random.randint(40, 120, 6),
        'Kosten': np.random.randint(20, 80, 6)
    })

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(df.set_index('Monat'))

    with col2:
        st.bar_chart(df.set_index('Monat'))

# Footer
st.write("---")
st.markdown("""
<div style="
    background: rgba(17, 23, 32, .55);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
">
    <p style="color: #9AB3BF; margin: 0;">
        Modernes UI Design mit Glasmorphism + Neumorphism + Türkis-Akzenten
    </p>
</div>
""", unsafe_allow_html=True)
