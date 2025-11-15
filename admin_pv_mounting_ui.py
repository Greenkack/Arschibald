"""
PV-Unterkonstruktions-Admin-UI
===============================

Streamlit Admin-Interface für PV-Montagekomponenten-Verwaltung
mit CRUD, CSV/XLSX Import/Export, PDF-Anhänge und Suchfunktion.

Autor: Bokuk2 System
Version: 1.0.0
Datum: 2025-11-06
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path

# Importiere Backend
from pv_mounting_database import (
    create_component,
    read_components,
    read_component_by_id,
    update_component,
    delete_component,
    import_from_csv,
    import_from_excel,
    export_to_csv,
    export_to_excel,
    get_statistics,
    search_components
)


# ==================== Konstanten ====================

MANUFACTURERS = [
    "K2 Systems",
    "Würth",
    "Prefa",
    "Schletter",
    "Renusol"
]

ROOF_TYPES = [
    "Ziegeldach",
    "Betondach",
    "Schieferdach",
    "Biberschwanzdach",
    "Blechdach (Trapezblech)",
    "Blechdach (Stehfalz)",
    "Sandwichplatten",
    "Flachdach"
]

CATEGORIES = [
    "Dachhaken",
    "Montageschiene",
    "Modulklemme (End)",
    "Modulklemme (Mittel)",
    "Schienenverbinder",
    "Stehfalzklemme",
    "Trapezblechschiene",
    "Aufständerung",
    "Schrauben",
    "Kabel",
    "Zubehör"
]

MATERIALS = [
    "Aluminium",
    "Edelstahl A2",
    "Edelstahl A4",
    "Stahl verzinkt",
    "Kunststoff",
    "Kupfer",
    "Gemischt"
]

UNITS = ["Stk", "m", "kg", "Set", "Paar"]


# ==================== Hilfsfunktionen ====================

def format_price(price: float) -> str:
    """Formatiert Preis im deutschen Format."""
    return f"{price:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def safe_json_loads(json_str: str) -> Any:
    """Sicher JSON parsen."""
    try:
        return json.loads(json_str) if json_str else {}
    except:
        return {}


def safe_json_dumps(data: Any) -> str:
    """Sicher JSON serialisieren."""
    try:
        return json.dumps(data, ensure_ascii=False, indent=2) if data else ""
    except:
        return ""


# ==================== Session State Initialisierung ====================

def init_session_state():
    """Initialisiert Session State Variablen."""
    if 'selected_component_id' not in st.session_state:
        st.session_state.selected_component_id = None
    if 'show_create_form' not in st.session_state:
        st.session_state.show_create_form = False
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'filter_manufacturer' not in st.session_state:
        st.session_state.filter_manufacturer = "Alle"
    if 'filter_roof_type' not in st.session_state:
        st.session_state.filter_roof_type = "Alle"
    if 'filter_category' not in st.session_state:
        st.session_state.filter_category = "Alle"


# ==================== UI-Komponenten ====================

def render_statistics_section():
    """Rendert Statistik-Übersicht."""
    st.header("Statistiken")
    
    stats = get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Gesamt Komponenten", stats['total_components'])
    
    with col2:
        manufacturers_count = len(stats['by_manufacturer'])
        st.metric("Hersteller", manufacturers_count)
    
    with col3:
        categories_count = len(stats['by_category'])
        st.metric("Kategorien", categories_count)
    
    # Detaillierte Statistiken in Expander
    with st.expander("Detaillierte Statistiken", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.subheader("Nach Hersteller")
            for item in stats['by_manufacturer']:
                st.write(f"**{item['manufacturer']}**: {item['count']}")
        
        with col_b:
            st.subheader("Nach Kategorie")
            for item in stats['by_category']:
                st.write(f"**{item['category']}**: {item['count']}")
        
        with col_c:
            st.subheader("Nach Dachtyp")
            for item in stats['by_roof_type']:
                st.write(f"**{item['roof_type']}**: {item['count']}")
        
        st.divider()
        
        # Preisstatistiken
        st.subheader("Preisstatistiken")
        price_stats = stats['price_statistics']
        
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("Min. Preis", format_price(price_stats['min_price']))
        with col_y:
            st.metric("Durchschnitt", format_price(price_stats['avg_price']))
        with col_z:
            st.metric("Max. Preis", format_price(price_stats['max_price']))


def render_search_and_filter():
    """Rendert Such- und Filterleiste."""
    st.subheader("🔎 Suche & Filter")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Suchbegriff",
            value=st.session_state.search_query,
            placeholder="Produktname, Hersteller, Artikelnummer...",
            key="search_input"
        )
        st.session_state.search_query = search_query
    
    with col2:
        if st.button("Suchen", use_container_width=True):
            st.rerun()
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        manufacturer = st.selectbox(
            "Hersteller",
            ["Alle"] + MANUFACTURERS,
            index=0 if st.session_state.filter_manufacturer == "Alle" else MANUFACTURERS.index(st.session_state.filter_manufacturer) + 1,
            key="filter_manufacturer_select"
        )
        st.session_state.filter_manufacturer = manufacturer
    
    with col_b:
        roof_type = st.selectbox(
            "Dachtyp",
            ["Alle"] + ROOF_TYPES,
            index=0 if st.session_state.filter_roof_type == "Alle" else ROOF_TYPES.index(st.session_state.filter_roof_type) + 1,
            key="filter_roof_type_select"
        )
        st.session_state.filter_roof_type = roof_type
    
    with col_c:
        category = st.selectbox(
            "Kategorie",
            ["Alle"] + CATEGORIES,
            index=0 if st.session_state.filter_category == "Alle" else CATEGORIES.index(st.session_state.filter_category) + 1,
            key="filter_category_select"
        )
        st.session_state.filter_category = category


def get_filtered_components() -> pd.DataFrame:
    """
    Gibt gefilterte Komponenten zurück.
    
    Returns:
        pd.DataFrame: DataFrame mit Komponenten
    """
    # Suchquery
    if st.session_state.search_query:
        components = search_components(st.session_state.search_query)
    else:
        # Filter aufbauen
        filters = {}
        
        if st.session_state.filter_manufacturer != "Alle":
            filters['manufacturer'] = st.session_state.filter_manufacturer
        
        if st.session_state.filter_roof_type != "Alle":
            filters['roof_type'] = st.session_state.filter_roof_type
        
        if st.session_state.filter_category != "Alle":
            filters['category'] = st.session_state.filter_category
        
        components = read_components(filters=filters if filters else None)
    
    # In DataFrame konvertieren
    if components:
        df = pd.DataFrame(components)
        # PDF-Bytes entfernen für Anzeige
        if 'pdf_bytes' in df.columns:
            df = df.drop(columns=['pdf_bytes'])
        return df
    else:
        return pd.DataFrame()


def render_components_table():
    """Rendert Komponenten-Tabelle."""
    st.subheader("📋 Komponenten-Liste")
    
    df = get_filtered_components()
    
    if df.empty:
        st.info("Keine Komponenten gefunden. Erstellen Sie eine neue Komponente oder passen Sie die Filter an.")
        return
    
    # Spalten für Anzeige auswählen
    display_columns = [
        'id', 'manufacturer', 'product_name', 'article_number', 
        'category', 'roof_type', 'price_netto', 'unit', 
        'quantity_per_module'
    ]
    
    # Nur vorhandene Spalten verwenden
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Tabelle anzeigen
    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "manufacturer": st.column_config.TextColumn("Hersteller", width="medium"),
            "product_name": st.column_config.TextColumn("Produktname", width="large"),
            "article_number": st.column_config.TextColumn("Art.-Nr.", width="small"),
            "category": st.column_config.TextColumn("Kategorie", width="medium"),
            "roof_type": st.column_config.TextColumn("Dachtyp", width="medium"),
            "price_netto": st.column_config.NumberColumn("Preis (€)", format="%.2f €", width="small"),
            "unit": st.column_config.TextColumn("Einheit", width="small"),
            "quantity_per_module": st.column_config.NumberColumn("Menge/Modul", format="%.2f", width="small")
        }
    )
    
    st.caption(f"**{len(df)}** Komponenten gefunden")
    
    # Aktionen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        component_id = st.number_input(
            "Komponente bearbeiten (ID)",
            min_value=1,
            step=1,
            key="edit_component_id"
        )
        
        if st.button("✏️ Bearbeiten", use_container_width=True):
            st.session_state.selected_component_id = component_id
            st.session_state.show_edit_form = True
            st.rerun()
    
    with col2:
        delete_id = st.number_input(
            "Komponente löschen (ID)",
            min_value=1,
            step=1,
            key="delete_component_id"
        )
        
        if st.button("Löschen", use_container_width=True, type="secondary"):
            if delete_component(delete_id, soft_delete=True):
                st.success(f"Komponente #{delete_id} wurde gelöscht.")
                st.rerun()
            else:
                st.error(f"Komponente #{delete_id} konnte nicht gelöscht werden.")
    
    with col3:
        if st.button("➕ Neue Komponente", use_container_width=True, type="primary"):
            st.session_state.show_create_form = True
            st.rerun()


def render_create_form():
    """Rendert Formular zum Erstellen einer neuen Komponente."""
    st.header("➕ Neue Komponente erstellen")
    
    with st.form("create_component_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            manufacturer = st.selectbox("Hersteller *", MANUFACTURERS, key="new_manufacturer")
            product_name = st.text_input("Produktname *", key="new_product_name")
            article_number = st.text_input("Artikelnummer", key="new_article_number")
            category = st.selectbox("Kategorie *", CATEGORIES, key="new_category")
            roof_type = st.selectbox("Dachtyp *", ROOF_TYPES, key="new_roof_type")
        
        with col2:
            material = st.selectbox("Material", MATERIALS, key="new_material")
            dimensions = st.text_input("Abmessungen", placeholder="z.B. 305×30 mm", key="new_dimensions")
            weight_kg = st.number_input("Gewicht (kg)", min_value=0.0, step=0.01, key="new_weight")
            warranty_years = st.number_input("Garantie (Jahre)", min_value=0, step=1, key="new_warranty")
            compatibility = st.text_area("Kompatibilität", placeholder="z.B. Für Tonziegel, Sparren ≥48mm", key="new_compatibility")
        
        st.divider()
        
        col3, col4 = st.columns(2)
        
        with col3:
            price_netto = st.number_input("Preis Netto (€) *", min_value=0.0, step=0.01, key="new_price")
            unit = st.selectbox("Einheit *", UNITS, key="new_unit")
            quantity_per_module = st.number_input(
                "Menge pro Modul *", 
                min_value=0.0, 
                value=1.0, 
                step=0.1,
                help="Durchschnittliche Anzahl dieser Komponente pro PV-Modul",
                key="new_quantity"
            )
        
        with col4:
            notes = st.text_area("Notizen", placeholder="Zusätzliche Informationen...", key="new_notes")
        
        # Spezifikationen als JSON
        st.subheader("Technische Spezifikationen (JSON)")
        specifications_json = st.text_area(
            "Spezifikationen",
            placeholder='{"max_load": "5kN", "temp_range": "-40 bis +85°C"}',
            help="Optionale technische Daten im JSON-Format",
            key="new_specifications"
        )
        
        # PDF-Upload
        st.subheader("📎 PDF-Anhang")
        pdf_file = st.file_uploader(
            "Datenblatt hochladen (optional)",
            type=['pdf'],
            key="new_pdf_upload"
        )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("💾 Speichern", use_container_width=True, type="primary")
        
        with col_cancel:
            cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if cancelled:
            st.session_state.show_create_form = False
            st.rerun()
        
        if submitted:
            # Validierung
            if not product_name or not manufacturer or not category or not roof_type or price_netto <= 0:
                st.error("Bitte füllen Sie alle Pflichtfelder (*) aus!")
            else:
                # Komponente erstellen
                component_data = {
                    'manufacturer': manufacturer,
                    'product_name': product_name,
                    'article_number': article_number if article_number else None,
                    'category': category,
                    'roof_type': roof_type,
                    'material': material if material else None,
                    'dimensions': dimensions if dimensions else None,
                    'weight_kg': weight_kg if weight_kg > 0 else None,
                    'price_netto': price_netto,
                    'unit': unit,
                    'quantity_per_module': quantity_per_module,
                    'compatibility': compatibility if compatibility else None,
                    'warranty_years': warranty_years if warranty_years > 0 else None,
                    'notes': notes if notes else None
                }
                
                # Spezifikationen parsen
                if specifications_json:
                    try:
                        specs = json.loads(specifications_json)
                        component_data['specifications'] = specs
                    except json.JSONDecodeError:
                        st.error("Ungültiges JSON-Format bei Spezifikationen!")
                        return
                
                # PDF-Datei
                if pdf_file:
                    component_data['pdf_bytes'] = pdf_file.read()
                    component_data['pdf_filename'] = pdf_file.name
                
                # In DB speichern
                try:
                    component_id = create_component(component_data)
                    st.success(f"Komponente #{component_id} wurde erfolgreich erstellt!")
                    st.session_state.show_create_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")


def render_edit_form():
    """Rendert Formular zum Bearbeiten einer Komponente."""
    component_id = st.session_state.selected_component_id
    
    if not component_id:
        st.warning("Keine Komponente ausgewählt.")
        return
    
    component = read_component_by_id(component_id, include_pdf=True)
    
    if not component:
        st.error(f"Komponente #{component_id} nicht gefunden.")
        st.session_state.show_edit_form = False
        return
    
    st.header(f"✏️ Komponente #{component_id} bearbeiten")
    
    with st.form("edit_component_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            manufacturer = st.selectbox("Hersteller *", MANUFACTURERS, index=MANUFACTURERS.index(component['manufacturer']) if component['manufacturer'] in MANUFACTURERS else 0)
            product_name = st.text_input("Produktname *", value=component['product_name'])
            article_number = st.text_input("Artikelnummer", value=component.get('article_number', '') or '')
            category = st.selectbox("Kategorie *", CATEGORIES, index=CATEGORIES.index(component['category']) if component['category'] in CATEGORIES else 0)
            roof_type = st.selectbox("Dachtyp *", ROOF_TYPES, index=ROOF_TYPES.index(component['roof_type']) if component['roof_type'] in ROOF_TYPES else 0)
        
        with col2:
            material = st.selectbox("Material", MATERIALS, index=MATERIALS.index(component.get('material', '')) if component.get('material') in MATERIALS else 0)
            dimensions = st.text_input("Abmessungen", value=component.get('dimensions', '') or '')
            weight_kg = st.number_input("Gewicht (kg)", min_value=0.0, value=float(component.get('weight_kg', 0.0) or 0.0), step=0.01)
            warranty_years = st.number_input("Garantie (Jahre)", min_value=0, value=int(component.get('warranty_years', 0) or 0), step=1)
            compatibility = st.text_area("Kompatibilität", value=component.get('compatibility', '') or '')
        
        st.divider()
        
        col3, col4 = st.columns(2)
        
        with col3:
            price_netto = st.number_input("Preis Netto (€) *", min_value=0.0, value=float(component['price_netto']), step=0.01)
            unit = st.selectbox("Einheit *", UNITS, index=UNITS.index(component.get('unit', 'Stk')) if component.get('unit') in UNITS else 0)
            quantity_per_module = st.number_input("Menge pro Modul *", min_value=0.0, value=float(component.get('quantity_per_module', 1.0)), step=0.1)
        
        with col4:
            notes = st.text_area("Notizen", value=component.get('notes', '') or '')
        
        # Spezifikationen
        st.subheader("Technische Spezifikationen (JSON)")
        current_specs = component.get('specifications', {})
        specifications_json = st.text_area(
            "Spezifikationen",
            value=safe_json_dumps(current_specs),
            help="Technische Daten im JSON-Format"
        )
        
        # PDF
        st.subheader("📎 PDF-Anhang")
        
        if component.get('pdf_filename'):
            st.info(f"Aktuelles PDF: **{component['pdf_filename']}**")
            
            col_dl, col_rm = st.columns(2)
            
            with col_dl:
                if component.get('pdf_bytes'):
                    st.download_button(
                        "📥 PDF herunterladen",
                        data=component['pdf_bytes'],
                        file_name=component['pdf_filename'],
                        mime='application/pdf',
                        use_container_width=True
                    )
            
            with col_rm:
                remove_pdf = st.checkbox("PDF entfernen")
        else:
            remove_pdf = False
        
        new_pdf_file = st.file_uploader("Neues PDF hochladen (ersetzt aktuelles)", type=['pdf'])
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("💾 Speichern", use_container_width=True, type="primary")
        
        with col_cancel:
            cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if cancelled:
            st.session_state.show_edit_form = False
            st.session_state.selected_component_id = None
            st.rerun()
        
        if submitted:
            # Update-Daten sammeln
            update_data = {
                'manufacturer': manufacturer,
                'product_name': product_name,
                'article_number': article_number if article_number else None,
                'category': category,
                'roof_type': roof_type,
                'material': material if material else None,
                'dimensions': dimensions if dimensions else None,
                'weight_kg': weight_kg if weight_kg > 0 else None,
                'price_netto': price_netto,
                'unit': unit,
                'quantity_per_module': quantity_per_module,
                'compatibility': compatibility if compatibility else None,
                'warranty_years': warranty_years if warranty_years > 0 else None,
                'notes': notes if notes else None
            }
            
            # Spezifikationen
            if specifications_json:
                try:
                    specs = json.loads(specifications_json)
                    update_data['specifications'] = specs
                except json.JSONDecodeError:
                    st.error("Ungültiges JSON-Format bei Spezifikationen!")
                    return
            
            # PDF-Handling
            if remove_pdf:
                update_data['pdf_bytes'] = None
                update_data['pdf_filename'] = None
            elif new_pdf_file:
                update_data['pdf_bytes'] = new_pdf_file.read()
                update_data['pdf_filename'] = new_pdf_file.name
            
            # Aktualisieren
            try:
                if update_component(component_id, update_data):
                    st.success(f"Komponente #{component_id} wurde erfolgreich aktualisiert!")
                    st.session_state.show_edit_form = False
                    st.session_state.selected_component_id = None
                    st.rerun()
                else:
                    st.error("Komponente konnte nicht aktualisiert werden.")
            except Exception as e:
                st.error(f"Fehler beim Aktualisieren: {e}")


def render_import_export_section():
    """Rendert Import/Export-Bereich."""
    st.header("📥 📤 Import / Export")
    
    tab1, tab2 = st.tabs(["📥 Import", "📤 Export"])
    
    with tab1:
        st.subheader("Daten importieren")
        
        import_format = st.radio("Format", ["CSV", "Excel"], horizontal=True)
        
        uploaded_file = st.file_uploader(
            f"Wählen Sie eine {import_format}-Datei",
            type=['csv'] if import_format == "CSV" else ['xlsx', 'xls']
        )
        
        if uploaded_file:
            st.info(f"Datei: **{uploaded_file.name}** ({uploaded_file.size:,} Bytes)")
            
            if st.button(f"{import_format} importieren", type="primary"):
                with st.spinner("Importiere Daten..."):
                    # Temporäre Datei speichern
                    temp_path = Path(f"temp_import.{import_format.lower()}")
                    
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        if import_format == "CSV":
                            count, errors = import_from_csv(str(temp_path))
                        else:
                            count, errors = import_from_excel(str(temp_path))
                        
                        if errors:
                            st.warning(f"Import abgeschlossen mit {len(errors)} Fehlern:")
                            for error in errors[:10]:  # Erste 10 Fehler
                                st.error(error)
                            if len(errors) > 10:
                                st.info(f"... und {len(errors) - 10} weitere Fehler")
                        
                        st.success(f"{count} Komponenten erfolgreich importiert!")
                        
                    except Exception as e:
                        st.error(f"Import-Fehler: {e}")
                    
                    finally:
                        # Temp-Datei löschen
                        if temp_path.exists():
                            temp_path.unlink()
        
        with st.expander("CSV/Excel Format-Anforderungen", expanded=False):
            st.markdown("""
            **Pflichtfelder:**
            - `manufacturer`: Hersteller
            - `product_name`: Produktname
            - `category`: Kategorie
            - `roof_type`: Dachtyp
            - `price_netto`: Preis (Netto)
            
            **Optionale Felder:**
            - `article_number`, `material`, `dimensions`, `weight_kg`
            - `unit`, `quantity_per_module`, `compatibility`
            - `warranty_years`, `specifications`, `notes`
            
            **Beispiel CSV:**
            ```
            manufacturer,product_name,category,roof_type,price_netto,unit
            K2 Systems,SingleHook 4S,Dachhaken,Ziegeldach,9.0,Stk
            Würth,Dachhaken PLUS Alu,Dachhaken,Ziegeldach,10.5,Stk
            ```
            """)
    
    with tab2:
        st.subheader("Daten exportieren")
        
        export_format = st.radio("Format", ["CSV", "Excel"], horizontal=True, key="export_format")
        
        # Filter für Export
        st.write("**Filter (optional)**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            exp_manufacturer = st.selectbox("Hersteller", ["Alle"] + MANUFACTURERS, key="export_manufacturer")
        with col2:
            exp_roof_type = st.selectbox("Dachtyp", ["Alle"] + ROOF_TYPES, key="export_roof_type")
        with col3:
            exp_category = st.selectbox("Kategorie", ["Alle"] + CATEGORIES, key="export_category")
        
        if st.button(f"📤 Als {export_format} exportieren", type="primary"):
            # Filter aufbauen
            export_filters = {}
            
            if exp_manufacturer != "Alle":
                export_filters['manufacturer'] = exp_manufacturer
            if exp_roof_type != "Alle":
                export_filters['roof_type'] = exp_roof_type
            if exp_category != "Alle":
                export_filters['category'] = exp_category
            
            # Exportieren
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pv_komponenten_{timestamp}.{export_format.lower()}"
            
            try:
                if export_format == "CSV":
                    success = export_to_csv(filename, filters=export_filters if export_filters else None)
                else:
                    success = export_to_excel(filename, filters=export_filters if export_filters else None)
                
                if success:
                    st.success(f"Export erfolgreich: **{filename}**")
                    
                    # Download-Button
                    with open(filename, 'rb') as f:
                        st.download_button(
                            f"📥 {filename} herunterladen",
                            data=f.read(),
                            file_name=filename,
                            mime='text/csv' if export_format == "CSV" else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                else:
                    st.error("Export fehlgeschlagen!")
            
            except Exception as e:
                st.error(f"Export-Fehler: {e}")


# ==================== Hauptanwendung ====================

def main():
    """Hauptfunktion der Streamlit-App."""
    st.set_page_config(
        page_title="PV-Unterkonstruktions-Verwaltung",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("PV-Unterkonstruktions-Verwaltung")
    st.caption("Admin-Panel für PV-Montagekomponenten-Datenbank")
    
    # Session State initialisieren
    init_session_state()
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("📋 Navigation")
        
        page = st.radio(
            "Bereich wählen",
            [
                "Dashboard",
                "📋 Komponenten verwalten",
                "➕ Neue Komponente",
                "📥 📤 Import/Export"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick Actions
        st.subheader("Quick Actions")
        
        if st.button("🔄 Daten aktualisieren", use_container_width=True):
            st.rerun()
        
        if st.button("Filter zurücksetzen", use_container_width=True):
            st.session_state.search_query = ""
            st.session_state.filter_manufacturer = "Alle"
            st.session_state.filter_roof_type = "Alle"
            st.session_state.filter_category = "Alle"
            st.rerun()
    
    # Hauptinhalt
    if page == "Dashboard":
        render_statistics_section()
        st.divider()
        st.subheader("📋 Alle Komponenten (Übersicht)")
        df = get_filtered_components()
        if not df.empty:
            st.dataframe(df[['id', 'manufacturer', 'product_name', 'category', 'roof_type', 'price_netto']].head(20), use_container_width=True)
            st.caption(f"Zeige erste 20 von {len(df)} Komponenten")
    
    elif page == "📋 Komponenten verwalten":
        # Edit-Form hat Priorität
        if st.session_state.show_edit_form:
            render_edit_form()
        else:
            render_search_and_filter()
            st.divider()
            render_components_table()
    
    elif page == "➕ Neue Komponente":
        render_create_form()
    
    elif page == "📥 📤 Import/Export":
        render_import_export_section()


if __name__ == "__main__":
    main()
