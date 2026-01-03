# crm/utils/import_export_ui.py
"""
Import/Export UI für Admin-Panel

Streamlit UI-Komponenten für Kunden-Import und -Export.

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
import tempfile
import os
from typing import Optional
from database import get_db_connection
from crm.utils.import_export_manager import (
    export_customers_to_csv,
    export_customers_to_excel,
    get_export_statistics,
    parse_csv_for_import,
    parse_excel_for_import,
    get_excel_sheet_names,
    map_import_fields,
    import_customers_batch,
    preview_import_data,
    get_available_db_fields,
    get_required_fields,
    format_import_statistics,
    CUSTOMER_FIELDS
)


def render_import_export_ui():
    """Hauptfunktion für Import/Export UI im Admin-Panel."""
    
    st.title(" Kunden Import/Export")
    
    # Tabs für Import und Export
    tab_export, tab_import = st.tabs([" Export", " Import"])
    
    with tab_export:
        render_export_ui()
    
    with tab_import:
        render_import_ui()


# ============================================================================
# EXPORT UI
# ============================================================================

def render_export_ui():
    """UI für Kunden-Export."""
    
    st.header("Kunden exportieren")
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        # Statistiken anzeigen
        stats = get_export_statistics(conn)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gesamt Kunden", stats.get('total_customers', 0))
        with col2:
            st.metric("Mit E-Mail", stats.get('customers_with_email', 0))
        with col3:
            st.metric("Mit Telefon", stats.get('customers_with_phone', 0))
        with col4:
            st.metric("Vollständigkeit", f"{stats.get('completeness_rate', 0)}%")
        
        st.divider()
        
        # Export-Optionen
        st.subheader("Export-Einstellungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.radio(
                "Format",
                ["CSV", "Excel"],
                horizontal=True
            )
        
        with col2:
            export_scope = st.radio(
                "Umfang",
                ["Alle Kunden", "Auswahl"],
                horizontal=True
            )
        
        # Feldauswahl
        st.subheader("Felder auswählen")
        
        all_fields = list(CUSTOMER_FIELDS.keys())
        default_fields = [f for f in all_fields if f not in ['id', 'creation_date', 'last_updated']]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_fields = st.multiselect(
                "Zu exportierende Felder",
                options=all_fields,
                default=default_fields,
                format_func=lambda x: CUSTOMER_FIELDS.get(x, x)
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Alle auswählen", use_container_width=True):
                st.session_state['export_fields'] = all_fields
                st.rerun()
            if st.button("Zurücksetzen", use_container_width=True):
                st.session_state['export_fields'] = default_fields
                st.rerun()
        
        # Kunden-Auswahl (wenn "Auswahl" gewählt)
        customer_ids = None
        if export_scope == "Auswahl":
            st.subheader("Kunden auswählen")
            
            # Lade alle Kunden
            cursor = conn.cursor()
            cursor.execute("SELECT id, first_name, last_name, email FROM customers ORDER BY last_name, first_name")
            customers = cursor.fetchall()
            
            customer_options = {
                f"{c[0]}: {c[1]} {c[2]} ({c[3] or 'keine E-Mail'})": c[0]
                for c in customers
            }
            
            selected_customers = st.multiselect(
                "Kunden",
                options=list(customer_options.keys()),
                help="Wählen Sie die zu exportierenden Kunden aus"
            )
            
            customer_ids = [customer_options[c] for c in selected_customers]
            
            if not customer_ids:
                st.warning("Bitte wählen Sie mindestens einen Kunden aus")
        
        st.divider()
        
        # Export-Button
        if not selected_fields:
            st.warning("Bitte wählen Sie mindestens ein Feld aus")
        elif export_scope == "Auswahl" and not customer_ids:
            pass  # Warnung bereits oben angezeigt
        else:
            if st.button("Export starten", type="primary", use_container_width=True):
                with st.spinner("Exportiere Daten..."):
                    if export_format == "CSV":
                        # CSV Export
                        csv_data = export_customers_to_csv(conn, selected_fields, customer_ids)
                        
                        if csv_data:
                            st.success("Export erfolgreich!")
                            
                            # Download-Button
                            st.download_button(
                                label=" CSV herunterladen",
                                data=csv_data,
                                file_name=f"kunden_export_{st.session_state.get('export_timestamp', 'data')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        else:
                            st.error("Export fehlgeschlagen")
                    
                    else:  # Excel
                        # Temporäre Datei erstellen
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_path = tmp_file.name
                        
                        success = export_customers_to_excel(conn, tmp_path, selected_fields, customer_ids)
                        
                        if success:
                            st.success("Export erfolgreich!")
                            
                            # Datei lesen und Download-Button anzeigen
                            with open(tmp_path, 'rb') as f:
                                excel_data = f.read()
                            
                            st.download_button(
                                label=" Excel herunterladen",
                                data=excel_data,
                                file_name=f"kunden_export_{st.session_state.get('export_timestamp', 'data')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            
                            # Temporäre Datei löschen
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                        else:
                            st.error("Export fehlgeschlagen")
    
    finally:
        conn.close()


# ============================================================================
# IMPORT UI
# ============================================================================

def render_import_ui():
    """UI für Kunden-Import."""
    
    st.header("Kunden importieren")
    
    # Anleitung
    with st.expander("Anleitung", expanded=False):
        st.markdown("""
        ### Import-Anleitung
        
        1. **Datei hochladen**: CSV oder Excel-Datei mit Kundendaten
        2. **Format prüfen**: Erste Zeile muss Spaltennamen enthalten
        3. **Felder zuordnen**: Automatische oder manuelle Zuordnung
        4. **Vorschau prüfen**: Kontrollieren Sie die ersten Zeilen
        5. **Duplikate behandeln**: Wählen Sie die gewünschte Aktion
        6. **Import starten**: Daten werden importiert
        
        ### Pflichtfelder
        - Vorname
        - Nachname
        
        ### Duplikatserkennung
        Duplikate werden erkannt über:
        - E-Mail-Adresse
        - Telefonnummer (Mobil oder Festnetz)
        - Name + PLZ
        """)
    
    # Datei-Upload
    st.subheader("1. Datei hochladen")
    
    upload_format = st.radio(
        "Dateiformat",
        ["CSV", "Excel"],
        horizontal=True
    )
    
    uploaded_file = None
    if upload_format == "CSV":
        uploaded_file = st.file_uploader(
            "CSV-Datei auswählen",
            type=['csv'],
            help="CSV-Datei mit Kundendaten (erste Zeile = Spaltennamen)"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                delimiter = st.selectbox("Trennzeichen", [',', ';', '\t'], index=0)
            with col2:
                encoding = st.selectbox("Zeichenkodierung", ['utf-8', 'latin-1', 'cp1252'], index=0)
    
    else:  # Excel
        uploaded_file = st.file_uploader(
            "Excel-Datei auswählen",
            type=['xlsx', 'xls'],
            help="Excel-Datei mit Kundendaten (erste Zeile = Spaltennamen)"
        )
    
    if not uploaded_file:
        st.info(" Bitte laden Sie eine Datei hoch, um fortzufahren")
        return
    
    # Datei parsen
    st.divider()
    st.subheader("2. Daten parsen")
    
    with st.spinner("Parse Datei..."):
        if upload_format == "CSV":
            # CSV parsen
            csv_content = uploaded_file.getvalue().decode(encoding)
            header, rows, errors = parse_csv_for_import(csv_content, delimiter, encoding)
        else:
            # Excel parsen
            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Sheet-Auswahl
            sheet_names = get_excel_sheet_names(tmp_path)
            if len(sheet_names) > 1:
                selected_sheet = st.selectbox("Sheet auswählen", sheet_names)
            else:
                selected_sheet = sheet_names[0] if sheet_names else None
            
            header, rows, errors = parse_excel_for_import(tmp_path, selected_sheet)
            
            # Temporäre Datei löschen
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    if errors:
        for error in errors:
            st.error(f"{error}")
        return
    
    if not header or not rows:
        st.error("Keine Daten gefunden")
        return
    
    st.success(f"{len(rows)} Zeilen gefunden")
    
    # Feld-Mapping
    st.divider()
    st.subheader("3. Felder zuordnen")
    
    # Automatisches Mapping
    auto_mapping = map_import_fields(header)
    
    st.info(f"{len(auto_mapping)} von {len(header)} Feldern automatisch zugeordnet")
    
    # Manuelle Anpassung
    with st.expander("Feld-Zuordnung anpassen", expanded=True):
        db_fields = get_available_db_fields()
        required_fields = get_required_fields()
        
        field_mapping = {}
        
        for import_col in header:
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.text(import_col)
            
            with col2:
                st.text("→")
            
            with col3:
                # Vorauswahl aus automatischem Mapping
                default_value = auto_mapping.get(import_col)
                default_index = 0
                
                options = ["(nicht importieren)"] + list(db_fields.keys())
                if default_value and default_value in options:
                    default_index = options.index(default_value)
                
                selected = st.selectbox(
                    f"Zuordnung für {import_col}",
                    options=options,
                    index=default_index,
                    format_func=lambda x: db_fields.get(x, x) if x != "(nicht importieren)" else x,
                    key=f"mapping_{import_col}",
                    label_visibility="collapsed"
                )
                
                if selected != "(nicht importieren)":
                    field_mapping[import_col] = selected
        
        # Prüfe Pflichtfelder
        mapped_db_fields = list(field_mapping.values())
        missing_required = [f for f in required_fields if f not in mapped_db_fields]
        
        if missing_required:
            st.warning(f"Pflichtfelder fehlen: {', '.join([db_fields[f] for f in missing_required])}")
    
    # Vorschau
    st.divider()
    st.subheader("4. Vorschau")
    
    preview_data = preview_import_data(rows, field_mapping, max_rows=5)
    
    if preview_data:
        st.dataframe(preview_data, use_container_width=True)
        st.caption(f"Zeige erste {len(preview_data)} von {len(rows)} Zeilen")
    else:
        st.warning("Keine Daten für Vorschau verfügbar")
    
    # Duplikat-Behandlung
    st.divider()
    st.subheader("5. Duplikat-Behandlung")
    
    duplicate_action = st.radio(
        "Was soll bei Duplikaten passieren?",
        ["skip", "update", "create"],
        format_func=lambda x: {
            "skip": "⊘ Überspringen (Duplikate werden nicht importiert)",
            "update": "↻ Aktualisieren (Existierende Kunden werden aktualisiert)",
            "create": " Neu erstellen (Duplikate werden trotzdem erstellt)"
        }[x],
        help="Duplikate werden erkannt über E-Mail, Telefon oder Name+PLZ"
    )
    
    # Import starten
    st.divider()
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        if missing_required:
            st.error("Import nicht möglich: Pflichtfelder fehlen")
        else:
            if st.button("Import starten", type="primary", use_container_width=True):
                with st.spinner("Importiere Daten..."):
                    stats = import_customers_batch(conn, rows, field_mapping, duplicate_action)
                
                # Ergebnis anzeigen
                if stats['errors'] == 0:
                    st.success("Import erfolgreich abgeschlossen!")
                elif stats['success'] > 0 or stats['updated'] > 0:
                    st.warning("Import mit Fehlern abgeschlossen")
                else:
                    st.error("Import fehlgeschlagen")
                
                # Statistiken
                st.code(format_import_statistics(stats))
                
                # Fehlerdetails
                if stats['error_details']:
                    with st.expander("Fehlerdetails anzeigen", expanded=False):
                        for error in stats['error_details']:
                            st.text(error)
    
    finally:
        conn.close()


# ============================================================================
# INTEGRATION IN ADMIN-PANEL
# ============================================================================

def add_import_export_to_admin_panel():
    """
    Fügt Import/Export-Seite zum Admin-Panel hinzu.
    
    Diese Funktion sollte in admin_panel.py aufgerufen werden.
    """
    render_import_export_ui()


if __name__ == "__main__":
    # Für Testing
    render_import_export_ui()
