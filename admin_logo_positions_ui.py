# admin_logo_positions_ui.py
"""
Admin-Interface für die Konfiguration der Logo-Positionen auf PDF Seite 4
"""

import json

import streamlit as st

try:
    import pandas as pd
except Exception:
    pd = None  # Fallback – Tabelle optional

# Default Logo-Positionen
DEFAULT_POSITIONS = {
    "modul": {
        "x": 520.0,
        "y": 180.0,
        "width": 60.0,
        "height": 30.0,
        "label": "PV-Modul Logo"
    },
    "wechselrichter": {
        "x": 520.0,
        "y": 370.0,
        "width": 60.0,
        "height": 30.0,
        "label": "Wechselrichter Logo"
    },
    "batteriespeicher": {
        "x": 520.0,
        "y": 560.0,
        "width": 60.0,
        "height": 30.0,
        "label": "Batteriespeicher Logo"
    }
}


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
    with st.expander("[INFO] Hilfe zu Logo-Positionen"):
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

        st.subheader(f"[TOOL] {default_pos['label']}")

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
            f"[DESIGN] Bereich: ({
                x:.0f}, {
                y:.0f}) bis ({
                x +
                width:.0f}, {
                    y +
                height:.0f})")

        st.markdown("---")

    # Speicher- und Reset-Buttons
    col_save, col_reset, col_preview, col_visual = st.columns(4)

    with col_save:
        if st.button("💾 Positionen speichern", type="primary"):
            try:
                success = save_admin_setting_func(
                    "pdf_logo_positions", edited_positions)
                if success:
                    st.success("[OK] Logo-Positionen erfolgreich gespeichert!")
                    st.rerun()
                else:
                    st.error("[ERROR] Fehler beim Speichern der Positionen!")
            except Exception as e:
                st.error(f"[ERROR] Speicher-Fehler: {e}")

    with col_reset:
        if st.button("🔄 Auf Standard zurücksetzen"):
            try:
                success = save_admin_setting_func(
                    "pdf_logo_positions", DEFAULT_POSITIONS.copy())
                if success:
                    st.success("[OK] Positionen auf Standard zurückgesetzt!")
                    st.rerun()
                else:
                    st.error("[ERROR] Fehler beim Zurücksetzen!")
            except Exception as e:
                st.error(f"[ERROR] Reset-Fehler: {e}")

    with col_preview:
        if st.button("👁️ Koordinaten-Übersicht"):
            st.session_state['show_logo_coords_preview'] = True

    with col_visual:
        if st.button("🖼️ Visuelle Vorschau"):
            st.session_state['show_logo_visual_preview'] = True

    # Koordinaten-Übersicht
    if st.session_state.get('show_logo_coords_preview', False):
        st.subheader("[CHART] Koordinaten-Übersicht")

        # Tabelle mit allen Positionen

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
        with st.expander("[FILE] JSON-Export"):
            st.code(json.dumps(edited_positions, indent=2))

        if st.button("[ERROR] Übersicht schließen"):
            st.session_state['show_logo_coords_preview'] = False
            st.rerun()

    # Visuelle Vorschau (vereinfachter A4-Canvas)
    if st.session_state.get('show_logo_visual_preview', False):
        st.subheader("🖼️ Visuelle Live-Vorschau (A4 S.4)")
        st.caption(
            "Hinweis: Maßstab vereinfacht – zeigt Bounding-Boxen und resultierende Positionen. Orientierung: (0,0) unten links.")

        # Einstellungen für Alignment
        try:
            align_with_titles_setting = load_admin_setting_func(
                "pdf_logo_align_with_titles", True)
            manual_mode = load_admin_setting_func(
                "pdf_logo_manual_mode", False)
            keep_alignment = load_admin_setting_func(
                "pdf_logo_keep_alignment_when_customized", False)
        except Exception:
            align_with_titles_setting = True
            manual_mode = False
            keep_alignment = False

        # Simulationsparameter
        a4_w, a4_h = 595.0, 842.0
        scale = 0.5  # Darstellung verkleinern
        canvas_w, canvas_h = int(a4_w * scale), int(a4_h * scale)

        # Headline Y-Zentren (hart kodiert approximation – kann optional aus YAML geladen werden)
        # Diese Werte müssten sonst analog im Backend gelesen werden.
        headline_centers = {
            'modul': 586.6,
            'wechselrichter': 394.9,
            'batteriespeicher': 203.9
        }

        # Prüfen ob Admin deutlich von Defaults abweicht
        admin_customized = False
        for cat, dfl in DEFAULT_POSITIONS.items():
            p = edited_positions.get(cat, dfl)
            if abs(p['x'] - dfl['x']) > 0.01 or abs(p['y'] - dfl['y']) > 0.01:
                admin_customized = True
                break

        effective_positions = {}
        align_effective = align_with_titles_setting and not manual_mode
        if admin_customized and align_effective and not keep_alignment:
            # würde im Code abgeschaltet
            align_effective = False

        if align_effective:
            # Repliziere vereinfachte Neu-Berechnung: Y durch headline center -
            # box_h/2
            for cat, pos in edited_positions.items():
                h_center = headline_centers.get(cat)
                if h_center:
                    new_pos = pos.copy()
                    new_pos['y'] = max(0.0, h_center - pos['height'] / 2.0)
                    effective_positions[cat] = new_pos
                else:
                    effective_positions[cat] = pos
        else:
            effective_positions = edited_positions

        # Zeichenfläche (SVG)
        import xml.etree.ElementTree as ET
        svg = ET.Element(
            'svg',
            attrib={
                'width': str(canvas_w),
                'height': str(canvas_h),
                'viewBox': f'0 0 {a4_w} {a4_h}',
                'style': 'border:1px solid #ccc; background:#fafafa'})

        # Hilfslinien für Headline-Zentren
        for cat, yc in headline_centers.items():
            line = ET.SubElement(
                svg,
                'line',
                attrib={
                    'x1': '0',
                    'x2': str(a4_w),
                    'y1': str(
                        a4_h - yc),
                    'y2': str(
                        a4_h - yc),
                    'stroke': '#ddd',
                    'stroke-width': '1',
                    'stroke-dasharray': '4 4'})
            ET.SubElement(
                svg,
                'text',
                attrib={
                    'x': '5',
                    'y': str(
                        a4_h -
                        yc -
                        4),
                    'font-size': '10',
                    'fill': '#888'}).text = f"{cat} center"

        # Boxen zeichnen
        colors_map = {
            'modul': '#1976d2',
            'wechselrichter': '#388e3c',
            'batteriespeicher': '#f57c00'
        }
        for cat, pos in edited_positions.items():
            eff = effective_positions.get(cat, pos)
            # Original (falls abweichend) gepunktete Box
            if eff is not pos:
                ET.SubElement(
                    svg,
                    'rect',
                    attrib={
                        'x': str(
                            pos['x']),
                        'y': str(
                            a4_h -
                            pos['y'] -
                            pos['height']),
                        'width': str(
                            pos['width']),
                        'height': str(
                            pos['height']),
                        'fill': 'none',
                        'stroke': colors_map.get(
                            cat,
                            '#555'),
                        'stroke-width': '1',
                        'stroke-dasharray': '3 2'})
            # Effektive Box
            ET.SubElement(
                svg,
                'rect',
                attrib={
                    'x': str(
                        eff['x']),
                    'y': str(
                        a4_h -
                        eff['y'] -
                        eff['height']),
                    'width': str(
                        eff['width']),
                    'height': str(
                        eff['height']),
                    'fill': colors_map.get(
                        cat,
                        '#555') +
                    '20',
                    'stroke': colors_map.get(
                        cat,
                        '#555'),
                    'stroke-width': '1'})
            ET.SubElement(
                svg,
                'text',
                attrib={
                    'x': str(
                        eff['x'] + 2),
                    'y': str(
                        a4_h - eff['y'] - 4),
                    'font-size': '10',
                    'fill': colors_map.get(
                        cat,
                        '#333')}).text = cat

        svg_code = ET.tostring(svg, encoding='unicode')
        st.components.v1.html(svg_code, height=canvas_h + 10, scrolling=True)

        # Legende
        st.markdown(
            "**Legende:** Vollfarbige Box = effektive Position, Gepunktet = ursprünglich eingegebene Admin-Box (wenn durch Alignment angepasst).")

        col_close, col_toggle = st.columns(2)
        with col_close:
            if st.button("[ERROR] Vorschau schließen"):
                st.session_state['show_logo_visual_preview'] = False
                st.rerun()
        with col_toggle:
            if st.button("🔁 Alignment umschalten (nur Vorschau)"):
                # Toggle Simulation
                st.session_state['show_logo_visual_preview'] = True
                # Temporär Setting toggeln (Simulation unabhängig vom
                # gespeicherten Wert)
                align_with_titles_setting = not align_with_titles_setting
                st.rerun()


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


if __name__ == "__main__":
    # Test der UI-Komponenten
    st.title("Logo-Positions-Konfiguration")

    # Mock-Funktionen für Tests
    def mock_load_setting(key, default):
        return default

    def mock_save_setting(key, value):
        return True

    render_logo_position_settings(mock_load_setting, mock_save_setting)
