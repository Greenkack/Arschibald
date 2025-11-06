"""
admin_pv_mounting_tab.py

Render-Funktion für PV-Unterkonstruktions-Verwaltung im Admin Panel.
Kompakte Version des Admin-UIs - integriert als Tab, nicht standalone.

Integration:
  - Wird von admin_panel.py importiert und als Tab gerendert
  - Nutzt pv_mounting_database.py für alle CRUD-Operationen
  - Deutsche Zahlenformatierung mit Punkt-Tausender, Komma-Dezimal

Features:
  - Dashboard mit Statistiken
  - Komponenten-Tabelle mit Filtern
  - Neue Komponente erstellen
  - Komponenten bearbeiten/löschen
  - CSV/XLSX Import/Export
  - PDF-Datenblatt Upload/Download
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

# Import database functions
try:
    from pv_mounting_database import (
        initialize_database,
        read_components,
        create_component,
        update_component,
        delete_component,
        get_statistics,
        search_components,
        import_from_csv,
        import_from_excel,
        export_to_csv,
        export_to_excel,
    )
    PV_MOUNTING_DB_AVAILABLE = True
except ImportError:
    PV_MOUNTING_DB_AVAILABLE = False

# === CONSTANTS ===
MANUFACTURERS = ["K2 Systems", "Würth", "Prefa", "Schletter", "Renusol", "Sonstige"]
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


def _get_component_name(component: Dict[str, Any]) -> str:
    """Get component name from dict - handles both 'name' and 'product_name' fields."""
    return component.get('product_name') or component.get('name') or "Unbenannt"


def format_german_number(value: float, decimals: int = 2) -> str:
    """Format number with German locale (. as thousands, , as decimal)."""
    if value is None:
        return "0,00"
    
    # Format with comma decimal separator
    formatted = f"{value:,.{decimals}f}"
    
    # Replace comma with temp placeholder
    formatted = formatted.replace(',', 'TEMP')
    # Replace dot with comma (German decimal separator)
    formatted = formatted.replace('.', ',')
    # Replace temp with dot (German thousands separator)
    formatted = formatted.replace('TEMP', '.')
    
    return formatted


def render_pv_mounting_admin_tab() -> None:
    """Main render function for PV mounting component administration."""
    
    if not PV_MOUNTING_DB_AVAILABLE:
        st.error("❌ **PV-Montage-Datenbank nicht verfügbar**")
        st.info("Bitte stellen Sie sicher, dass `pv_mounting_database.py` im Projektverzeichnis vorhanden ist.")
        return
    
    # Initialize database
    try:
        initialize_database()
    except Exception as e:
        st.error(f"❌ Fehler beim Initialisieren der Datenbank: {e}")
        return
    
    st.markdown("## 🔧 PV-Unterkonstruktions-Verwaltung")
    st.markdown("---")
    
    # Sub-navigation
    sub_tabs = st.tabs([
        "📊 Dashboard",
        "📋 Komponenten verwalten",
        "➕ Neue Komponente",
        "📤 Import/Export"
    ])
    
    with sub_tabs[0]:
        _render_dashboard()
    
    with sub_tabs[1]:
        _render_components_list()
    
    with sub_tabs[2]:
        _render_create_component()
    
    with sub_tabs[3]:
        _render_import_export()


def _render_dashboard() -> None:
    """Render statistics dashboard."""
    
    st.markdown("### 📊 Statistik-Übersicht")
    
    try:
        stats = get_statistics()
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gesamt Komponenten",
                stats['total_components'],
                help="Anzahl aller aktiven Komponenten in der Datenbank"
            )
        
        with col2:
            st.metric(
                "Hersteller",
                len(stats['by_manufacturer']),
                help="Anzahl verschiedener Hersteller"
            )
        
        with col3:
            st.metric(
                "Kategorien",
                len(stats['by_category']),
                help="Anzahl verschiedener Produktkategorien"
            )
        
        with col4:
            st.metric(
                "Dachtypen",
                len(stats['by_roof_type']),
                help="Anzahl verschiedener Dachtypen"
            )
        
        st.markdown("---")
        
        # Detailed breakdown
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### Nach Hersteller")
            if stats['by_manufacturer']:
                df_manuf = pd.DataFrame(
                    list(stats['by_manufacturer'].items()),
                    columns=['Hersteller', 'Anzahl']
                ).sort_values('Anzahl', ascending=False)
                st.dataframe(df_manuf, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Daten verfügbar")
        
        with col_right:
            st.markdown("#### Nach Kategorie")
            if stats['by_category']:
                df_cat = pd.DataFrame(
                    list(stats['by_category'].items()),
                    columns=['Kategorie', 'Anzahl']
                ).sort_values('Anzahl', ascending=False)
                st.dataframe(df_cat, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Daten verfügbar")
        
        # Price statistics
        if stats['total_components'] > 0:
            st.markdown("---")
            st.markdown("#### Preisstatistiken")
            
            components = read_components()
            prices = [c['price_netto'] for c in components if c.get('price_netto') and c['price_netto'] > 0]
            
            if prices:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Durchschnittspreis",
                        f"{format_german_number(sum(prices) / len(prices))} €",
                        help="Durchschnittlicher Nettopreis aller Komponenten"
                    )
                
                with col2:
                    st.metric(
                        "Niedrigster Preis",
                        f"{format_german_number(min(prices))} €",
                        help="Günstigste Komponente"
                    )
                
                with col3:
                    st.metric(
                        "Höchster Preis",
                        f"{format_german_number(max(prices))} €",
                        help="Teuerste Komponente"
                    )
    
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Statistiken: {e}")


def _render_components_list() -> None:
    """Render components table with filters and actions."""
    
    st.markdown("### 📋 Komponenten-Übersicht")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_manufacturer = st.selectbox(
            "Hersteller",
            options=["Alle"] + MANUFACTURERS,
            key="pv_filter_manuf"
        )
    
    with col2:
        filter_category = st.selectbox(
            "Kategorie",
            options=["Alle"] + CATEGORIES,
            key="pv_filter_cat"
        )
    
    with col3:
        filter_roof_type = st.selectbox(
            "Dachtyp",
            options=["Alle"] + ROOF_TYPES,
            key="pv_filter_roof"
        )
    
    with col4:
        search_term = st.text_input(
            "🔍 Suche",
            placeholder="Name, Artikel-Nr...",
            key="pv_search"
        )
    
    st.markdown("---")
    
    # Build filters dict
    filters = {}
    if filter_manufacturer != "Alle":
        filters['manufacturer'] = filter_manufacturer
    if filter_category != "Alle":
        filters['category'] = filter_category
    if filter_roof_type != "Alle":
        filters['roof_type'] = filter_roof_type
    
    # Load components
    try:
        if search_term:
            components = search_components(
                search_term,
                fields=['name', 'article_number', 'description']
            )
            # Apply additional filters
            if filters:
                components = [
                    c for c in components
                    if all(
                        c.get(k) == v for k, v in filters.items()
                    )
                ]
        else:
            components = read_components(filters=filters)
        
        if not components:
            st.info("📭 Keine Komponenten gefunden.")
            return
        
        # Display count
        st.info(f"📦 **{len(components)}** Komponenten gefunden")
        
        # Render table
        for idx, comp in enumerate(components):
            with st.expander(
                f"**{_get_component_name(comp)}** ({comp['manufacturer']}) - {format_german_number(comp['price_netto'])} €",
                expanded=False
            ):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"**Artikel-Nr:** {comp.get('article_number', 'N/A')}")
                    st.markdown(f"**Kategorie:** {comp['category']}")
                    st.markdown(f"**Dachtyp:** {comp['roof_type']}")
                    st.markdown(f"**Material:** {comp.get('material', 'N/A')}")
                    st.markdown(f"**Einheit:** {comp.get('unit', 'Stk')}")
                    
                    if comp.get('description'):
                        st.markdown(f"**Beschreibung:** {comp['description']}")
                    
                    if comp.get('specifications'):
                        st.markdown("**Spezifikationen:**")
                        try:
                            specs = json.loads(comp['specifications']) if isinstance(comp['specifications'], str) else comp['specifications']
                            for key, value in specs.items():
                                st.markdown(f"- {key}: {value}")
                        except:
                            st.text(comp['specifications'])
                
                with col_actions:
                    st.markdown("**Aktionen:**")
                    
                    # Edit button
                    if st.button("✏️ Bearbeiten", key=f"edit_{comp['id']}", use_container_width=True):
                        st.session_state['pv_edit_component'] = comp
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Löschen", key=f"delete_{comp['id']}", type="secondary", use_container_width=True):
                        if delete_component(comp['id']):
                            st.success(f"✅ Komponente '{_get_component_name(comp)}' gelöscht")
                            st.rerun()
                        else:
                            st.error("❌ Fehler beim Löschen")
                    
                    # PDF download if available
                    if comp.get('pdf_bytes'):
                        st.download_button(
                            "📄 Datenblatt",
                            data=comp['pdf_bytes'],
                            file_name=f"{comp['article_number']}_Datenblatt.pdf",
                            mime="application/pdf",
                            key=f"pdf_{comp['id']}",
                            use_container_width=True
                        )
        
        # Handle edit mode
        if 'pv_edit_component' in st.session_state:
            st.markdown("---")
            _render_edit_component(st.session_state['pv_edit_component'])
    
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Komponenten: {e}")


def _render_edit_component(component: Dict[str, Any]) -> None:
    """Render edit form for existing component."""
    
    st.markdown(f"### ✏️ Komponente bearbeiten: **{_get_component_name(component)}**")
    
    with st.form(key="edit_component_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", value=_get_component_name(component))
            manufacturer = st.selectbox(
                "Hersteller *",
                options=MANUFACTURERS,
                index=MANUFACTURERS.index(component['manufacturer']) if component['manufacturer'] in MANUFACTURERS else 0
            )
            article_number = st.text_input("Artikel-Nr", value=component.get('article_number', ''))
            category = st.selectbox(
                "Kategorie *",
                options=CATEGORIES,
                index=CATEGORIES.index(component['category']) if component['category'] in CATEGORIES else 0
            )
            roof_type = st.selectbox(
                "Dachtyp *",
                options=ROOF_TYPES,
                index=ROOF_TYPES.index(component['roof_type']) if component['roof_type'] in ROOF_TYPES else 0
            )
        
        with col2:
            material = st.selectbox(
                "Material",
                options=MATERIALS,
                index=MATERIALS.index(component.get('material', 'Aluminium')) if component.get('material') in MATERIALS else 0
            )
            price = st.number_input(
                "Preis (€ netto) *",
                min_value=0.0,
                value=float(component['price_netto']),
                step=0.01,
                format="%.2f"
            )
            unit = st.selectbox(
                "Einheit",
                options=UNITS,
                index=UNITS.index(component.get('unit', 'Stk')) if component.get('unit') in UNITS else 0
            )
            weight_kg = st.number_input(
                "Gewicht (kg)",
                min_value=0.0,
                value=float(component.get('weight_kg', 0.0)),
                step=0.01
            )
        
        description = st.text_area(
            "Beschreibung",
            value=component.get('description', ''),
            height=100
        )
        
        # PDF upload
        pdf_file = st.file_uploader(
            "📄 Neues Datenblatt hochladen (PDF, optional)",
            type=['pdf'],
            key="edit_pdf_upload"
        )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submit = st.form_submit_button("💾 Speichern", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Abbrechen", use_container_width=True)
        
        if cancel:
            del st.session_state['pv_edit_component']
            st.rerun()
        
        if submit:
            if not name or not manufacturer or not category or not roof_type or price <= 0:
                st.error("❌ Bitte alle Pflichtfelder (*) ausfüllen und gültigen Preis eingeben")
            else:
                update_data = {
                    'product_name': name,  # Corrected field name
                    'manufacturer': manufacturer,
                    'article_number': article_number,
                    'category': category,
                    'roof_type': roof_type,
                    'material': material,
                    'price_netto': price,
                    'unit': unit,
                    'weight_kg': weight_kg,
                    'description': description,
                }
                
                # Handle PDF upload
                if pdf_file:
                    update_data['pdf_bytes'] = pdf_file.read()
                
                if update_component(component['id'], update_data):
                    st.success(f"✅ Komponente '{name}' erfolgreich aktualisiert!")
                    del st.session_state['pv_edit_component']
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Aktualisieren der Komponente")


def _render_create_component() -> None:
    """Render form to create new component."""
    
    st.markdown("### ➕ Neue Komponente erstellen")
    
    with st.form(key="create_component_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="z.B. K2 Systems SingleHook 4S")
            manufacturer = st.selectbox("Hersteller *", options=MANUFACTURERS)
            article_number = st.text_input("Artikel-Nr", placeholder="z.B. 2005024")
            category = st.selectbox("Kategorie *", options=CATEGORIES)
            roof_type = st.selectbox("Dachtyp *", options=ROOF_TYPES)
        
        with col2:
            material = st.selectbox("Material", options=MATERIALS)
            price = st.number_input(
                "Preis (€ netto) *",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Nettopreis ohne MwSt"
            )
            unit = st.selectbox("Einheit", options=UNITS, index=0)
            weight_kg = st.number_input(
                "Gewicht (kg)",
                min_value=0.0,
                step=0.01
            )
        
        description = st.text_area(
            "Beschreibung",
            placeholder="Optionale Beschreibung der Komponente...",
            height=100
        )
        
        # PDF upload
        pdf_file = st.file_uploader(
            "📄 Datenblatt hochladen (PDF, optional)",
            type=['pdf'],
            key="create_pdf_upload"
        )
        
        submit = st.form_submit_button("✅ Komponente erstellen", use_container_width=True, type="primary")
        
        if submit:
            if not name or not manufacturer or not category or not roof_type or price <= 0:
                st.error("❌ Bitte alle Pflichtfelder (*) ausfüllen und gültigen Preis eingeben")
            else:
                component_data = {
                    'product_name': name,  # Corrected field name
                    'manufacturer': manufacturer,
                    'article_number': article_number,
                    'category': category,
                    'roof_type': roof_type,
                    'material': material,
                    'price_netto': price,
                    'unit': unit,
                    'weight_kg': weight_kg,
                    'description': description,
                }
                
                # Handle PDF upload
                if pdf_file:
                    component_data['pdf_bytes'] = pdf_file.read()
                
                try:
                    component_id = create_component(component_data)
                    if component_id:
                        st.success(f"✅ Komponente '{name}' erfolgreich erstellt! (ID: {component_id})")
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Erstellen der Komponente")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")


def _render_import_export() -> None:
    """Render import/export functionality."""
    
    st.markdown("### 📤 Import/Export")
    
    tab_import, tab_export = st.tabs(["📥 Import", "📤 Export"])
    
    with tab_import:
        st.markdown("#### CSV/XLSX Datei importieren")
        st.info(
            "💡 **Erforderliche Spalten:** name, manufacturer, category, roof_type, price_netto\n\n"
            "**Optionale Spalten:** article_number, material, unit, weight_kg, description, specifications"
        )
        
        uploaded_file = st.file_uploader(
            "Datei auswählen",
            type=['csv', 'xlsx'],
            key="pv_import_file"
        )
        
        if uploaded_file:
            if st.button("🚀 Import starten", type="primary"):
                try:
                    # Save to temp file
                    temp_path = Path(f"temp_import_{uploaded_file.name}")
                    temp_path.write_bytes(uploaded_file.read())
                    
                    # Import based on file type
                    if uploaded_file.name.endswith('.csv'):
                        count, errors = import_from_csv(str(temp_path))
                    else:
                        count, errors = import_from_excel(str(temp_path))
                    
                    # Clean up
                    temp_path.unlink()
                    
                    # Show results
                    st.success(f"✅ **{count}** Komponenten erfolgreich importiert!")
                    
                    if errors:
                        with st.expander(f"⚠️ {len(errors)} Fehler aufgetreten", expanded=False):
                            for error in errors:
                                st.error(error)
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Import fehlgeschlagen: {e}")
    
    with tab_export:
        st.markdown("#### Komponenten exportieren")
        
        # Export filters
        exp_col1, exp_col2 = st.columns(2)
        
        with exp_col1:
            exp_manufacturer = st.selectbox(
                "Hersteller filtern",
                options=["Alle"] + MANUFACTURERS,
                key="exp_manuf"
            )
        
        with exp_col2:
            exp_category = st.selectbox(
                "Kategorie filtern",
                options=["Alle"] + CATEGORIES,
                key="exp_cat"
            )
        
        # Build filters
        exp_filters = {}
        if exp_manufacturer != "Alle":
            exp_filters['manufacturer'] = exp_manufacturer
        if exp_category != "Alle":
            exp_filters['category'] = exp_category
        
        # Export buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Als CSV exportieren", use_container_width=True):
                try:
                    export_path = Path("pv_components_export.csv")
                    export_to_csv(str(export_path), filters=exp_filters)
                    
                    with open(export_path, 'rb') as f:
                        st.download_button(
                            "⬇️ CSV herunterladen",
                            data=f.read(),
                            file_name="pv_komponenten.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    export_path.unlink()
                    st.success("✅ CSV-Export erfolgreich!")
                
                except Exception as e:
                    st.error(f"❌ Export fehlgeschlagen: {e}")
        
        with col2:
            if st.button("📊 Als XLSX exportieren", use_container_width=True):
                try:
                    export_path = Path("pv_components_export.xlsx")
                    export_to_excel(str(export_path), filters=exp_filters)
                    
                    with open(export_path, 'rb') as f:
                        st.download_button(
                            "⬇️ XLSX herunterladen",
                            data=f.read(),
                            file_name="pv_komponenten.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    export_path.unlink()
                    st.success("✅ XLSX-Export erfolgreich!")
                
                except Exception as e:
                    st.error(f"❌ Export fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test standalone
    st.set_page_config(page_title="PV Mounting Admin", page_icon="🔧", layout="wide")
    render_pv_mounting_admin_tab()
