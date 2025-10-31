# === AUTO-GENERATED INSERT PATCH ===
# target_module: admin_logo_positions_ui.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import json

import streamlit as st


# --- DEF BLOCK START: func render_logo_position_settings ---
def render_logo_position_settings(
        load_admin_setting_func,
        save_admin_setting_func):
    """Rendert die Logo-Positions-Einstellungen"""
    st.subheader("📍 Logo-Positionen auf PDF Seite 4")
    st.markdown("---")

    # Aktuelle Einstellungen laden
    try:
        current_positions = load_admin_setting_func(
            "pdf_logo_positions", DEFAULT_POSITIONS.copy())
        if not isinstance(current_positions, dict):
            current_positions = DEFAULT_POSITIONS.copy()
    except Exception as e:
        st.error(f"Fehler beim Laden der Logo-Positionen: {e}")
        current_positions = DEFAULT_POSITIONS.copy()

    # Info-Box
    with st.expander("ℹ️ Hilfe zu Logo-Positionen"):
        st.markdown("""
        **Koordinatensystem:**
        - **X**: Horizontale Position (0 = links, 595 = rechts für A4)
        - **Y**: Vertikale Position (0 = unten, 842 = oben für A4)
        - **Breite/Höhe**: Größe des Logo-Bereichs in Punkten

        **Standard PDF Seite 4 Layout:**
        - PV-Module: Rechts neben dem Modul-Text-Bereich
        - Wechselrichter: Rechts neben dem WR-Text-Bereich
        - Batteriespeicher: Rechts neben dem Speicher-Text-Bereich

        **Tipps:**
        - Logos werden proportional skaliert
        - Empfohlene Logo-Größe: 60x30 Punkte
        - Testen Sie die Position mit der PDF-Vorschau
        """)

    # Bearbeitungs-Interface
    edited_positions = {}

    for category, default_pos in DEFAULT_POSITIONS.items():
        current_pos = current_positions.get(category, default_pos.copy())

        st.subheader(f"🔧 {default_pos['label']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            x = st.number_input(
                "X-Position:",
                min_value=0.0,
                max_value=595.0,
                value=float(current_pos.get('x', default_pos['x'])),
                step=1.0,
                key=f"logo_pos_x_{category}"
            )

        with col2:
            y = st.number_input(
                "Y-Position:",
                min_value=0.0,
                max_value=842.0,
                value=float(current_pos.get('y', default_pos['y'])),
                step=1.0,
                key=f"logo_pos_y_{category}"
            )

        with col3:
            width = st.number_input(
                "Breite:",
                min_value=10.0,
                max_value=200.0,
                value=float(current_pos.get('width', default_pos['width'])),
                step=1.0,
                key=f"logo_pos_width_{category}"
            )

        with col4:
            height = st.number_input(
                "Höhe:",
                min_value=10.0,
                max_value=100.0,
                value=float(current_pos.get('height', default_pos['height'])),
                step=1.0,
                key=f"logo_pos_height_{category}"
            )

        # Aktualisierte Position speichern
        edited_positions[category] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "label": default_pos['label']
        }

        # Vorschau der Koordinaten
        st.caption(
            f"📐 Bereich: ({
                x:.0f}, {
                y:.0f}) bis ({
                x +
                width:.0f}, {
                    y +
                height:.0f})")

        st.markdown("---")

    # Speicher- und Reset-Buttons
    col_save, col_reset, col_preview = st.columns(3)

    with col_save:
        if st.button("💾 Positionen speichern", type="primary"):
            try:
                success = save_admin_setting_func(
                    "pdf_logo_positions", edited_positions)
                if success:
                    st.success("✅ Logo-Positionen erfolgreich gespeichert!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Speichern der Positionen!")
            except Exception as e:
                st.error(f"❌ Speicher-Fehler: {e}")

    with col_reset:
        if st.button("🔄 Auf Standard zurücksetzen"):
            try:
                success = save_admin_setting_func(
                    "pdf_logo_positions", DEFAULT_POSITIONS.copy())
                if success:
                    st.success("✅ Positionen auf Standard zurückgesetzt!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Zurücksetzen!")
            except Exception as e:
                st.error(f"❌ Reset-Fehler: {e}")

    with col_preview:
        if st.button("👁️ Koordinaten-Übersicht"):
            st.session_state['show_logo_coords_preview'] = True

    # Koordinaten-Übersicht
    if st.session_state.get('show_logo_coords_preview', False):
        st.subheader("📊 Koordinaten-Übersicht")

        # Tabelle mit allen Positionen
        import pandas as pd

        table_data = []
        for category, pos in edited_positions.items():
            table_data.append({
                'Kategorie': pos['label'],
                'X': f"{pos['x']:.0f}",
                'Y': f"{pos['y']:.0f}",
                'Breite': f"{pos['width']:.0f}",
                'Höhe': f"{pos['height']:.0f}",
                'X-Ende': f"{pos['x'] + pos['width']:.0f}",
                'Y-Ende': f"{pos['y'] + pos['height']:.0f}"
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

        # JSON-Export
        with st.expander("📄 JSON-Export"):
            st.code(json.dumps(edited_positions, indent=2))

        if st.button("❌ Übersicht schließen"):
            st.session_state['show_logo_coords_preview'] = False
            st.rerun()
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_position_test ---
def render_logo_position_test():
    """Test-Funktion für Logo-Positionen"""
    st.subheader("🧪 Logo-Position Test")

    st.info("""
    **Test der Logo-Positionen:**
    1. Speichern Sie die gewünschten Positionen
    2. Erstellen Sie eine Test-PDF über die normale App
    3. Prüfen Sie, ob die Logos korrekt positioniert sind
    4. Passen Sie die Koordinaten bei Bedarf an
    """)

    # Aktuelle Positionen anzeigen
    try:
        from database import load_admin_setting
        positions = load_admin_setting("pdf_logo_positions", DEFAULT_POSITIONS)

        st.write("**Aktuell gespeicherte Positionen:**")
        for category, pos in positions.items():
            st.write(
                f"- **{
                    pos.get(
                        'label',
                        category)}**: X={
                    pos.get('x')}, Y={
                    pos.get('y')}, {
                        pos.get('width')}x{
                            pos.get('height')}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Test-Daten: {e}")
# --- DEF BLOCK END ---
