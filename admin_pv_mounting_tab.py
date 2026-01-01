"""
admin_pv_mounting_tab_v2.py

KOMPLETT ÜBERARBEITETES Admin-Dashboard für PV-Unterkonstruktion
================================================================

NEU in Version 2.0:
- Verbessertes Dashboard mit erweiterten Statistiken
- Marken-Dropdown zur Filterung
-  Vollständige CRUD-Funktionen (Create, Read, Update, Delete)
-  Erweiterte Such- und Filterfunktionen
- Visualisierungen mit Charts
- Moderne, übersichtliche UI

Integration:
  - Wird von admin_panel.py importiert
  - Nutzt pv_mounting_database.py
  - Deutsche Zahlenformatierung

Autor: Bokuk2 System
Version: 2.0.0 - MASSIV VERBESSERT
Datum: 2025-11-06
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import plotly.express as px
import plotly.graph_objects as go

# Import database functions
try:
    from pv_mounting_database import (
        initialize_database,
        read_components,
        create_component,
        update_component,
        delete_component,
        get_statistics,
        search_components)
    PV_MOUNTING_DB_AVAILABLE = True
except ImportError:
    PV_MOUNTING_DB_AVAILABLE = False


def format_german_number(value: float, decimals: int = 2) -> str:
    """Format number with German locale."""
    if value is None:
        return "0,00"
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted


def format_german_currency(value: float) -> str:
    """Format as German currency."""
    return f"{format_german_number(value, 2)} €"


def render_pv_mounting_admin_tab_v2() -> None:
    """NEUE Hauptfunktion für überarbeitetes PV-Unterkonstruktions-Dashboard."""
    
    if not PV_MOUNTING_DB_AVAILABLE:
        st.error("**PV-Montage-Datenbank nicht verfügbar**")
        return
    
    # Initialize database
    try:
        initialize_database()
    except Exception as e:
        st.error(f"Fehler beim Initialisieren der Datenbank: {e}")
        return
    
    # Header mit Styling
    st.markdown("""
        <style>
        .big-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-header">PV-Unterkonstruktions-Verwaltung 2.0</p>', unsafe_allow_html=True)
    
    # Navigation mit Icons
    sub_tabs = st.tabs([
        "Dashboard & Statistiken",
        " Komponenten verwalten",
        " Neue Komponente",
        " Erweiterte Suche",
        " Import/Export"
    ])
    
    with sub_tabs[0]:
        _render_enhanced_dashboard()
    
    with sub_tabs[1]:
        _render_enhanced_component_list()
    
    with sub_tabs[2]:
        _render_enhanced_create_component()
    
    with sub_tabs[3]:
        _render_advanced_search()
    
    with sub_tabs[4]:
        _render_import_export()


def _render_enhanced_dashboard() -> None:
    """Verbessertes Dashboard mit Charts und erweiterten Statistiken."""
    
    st.markdown('<p class="section-header">Übersicht & Statistiken</p>', unsafe_allow_html=True)
    
    try:
        stats = get_statistics()
        all_components = read_components()
        
        # === TOP METRICS ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gesamt Komponenten",
                stats['total_components'],
                delta=f"+{len(all_components) - 25}" if len(all_components) > 25 else None,
                help="Anzahl aller aktiven Komponenten"
            )
        
        with col2:
            st.metric(
                " Hersteller",
                len(stats['by_manufacturer']),
                help="Verschiedene Hersteller"
            )
        
        with col3:
            st.metric(
                " Kategorien",
                len(stats['by_category']),
                help="Produktkategorien"
            )
        
        with col4:
            total_value = sum(c.get('price_netto', 0) for c in all_components)
            st.metric(
                "Gesamtwert",
                format_german_currency(total_value),
                help="Netto-Gesamtwert aller Komponenten"
            )
        
        st.markdown("---")
        
        # === CHARTS ===
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### Verteilung nach Hersteller")
            if stats['by_manufacturer']:
                df_manuf = pd.DataFrame(
                    list(stats['by_manufacturer'].items()),
                    columns=['Hersteller', 'Anzahl']
                ).sort_values('Anzahl', ascending=False)
                
                fig = px.bar(
                    df_manuf,
                    x='Anzahl',
                    y='Hersteller',
                    orientation='h',
                    title='',
                    color='Anzahl',
                    color_continuous_scale='blues'
                )
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.markdown("#### Top 10 Kategorien")
            if stats['by_category']:
                df_cat = pd.DataFrame(
                    list(stats['by_category'].items()),
                    columns=['Kategorie', 'Anzahl']
                ).sort_values('Anzahl', ascending=False).head(10)
                
                fig = px.pie(
                    df_cat,
                    values='Anzahl',
                    names='Kategorie',
                    title='',
                    hole=0.4
                )
                fig.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # === DETAILED BREAKDOWN ===
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("####  Nach Dachtyp")
            if stats['by_roof_type']:
                df_roof = pd.DataFrame(
                    list(stats['by_roof_type'].items()),
                    columns=['Dachtyp', 'Anzahl']
                ).sort_values('Anzahl', ascending=False)
                st.dataframe(df_roof, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("####  Preisstatistik")
            prices = [c.get('price_netto', 0) for c in all_components if c.get('price_netto', 0) > 0]
            if prices:
                price_stats = pd.DataFrame({
                    'Kennzahl': ['Durchschnitt', 'Median', 'Min', 'Max'],
                    'Preis': [
                        format_german_currency(sum(prices) / len(prices)),
                        format_german_currency(sorted(prices)[len(prices)//2]),
                        format_german_currency(min(prices)),
                        format_german_currency(max(prices))
                    ]
                })
                st.dataframe(price_stats, use_container_width=True, hide_index=True)
        
        with col3:
            st.markdown("#### Nach Einheit")
            units = {}
            for comp in all_components:
                unit = comp.get('unit', 'Stk')
                units[unit] = units.get(unit, 0) + 1
            
            df_units = pd.DataFrame(
                list(units.items()),
                columns=['Einheit', 'Anzahl']
            ).sort_values('Anzahl', ascending=False)
            st.dataframe(df_units, use_container_width=True, hide_index=True)
        
        # === RECENT ADDITIONS ===
        st.markdown("---")
        st.markdown("####  Neueste Komponenten")
        
        # Sort by ID (newest first)
        recent = sorted(all_components, key=lambda x: x.get('id', 0), reverse=True)[:5]
        if recent:
            recent_df = pd.DataFrame([{
                'Hersteller': c.get('manufacturer', ''),
                'Produkt': c.get('product_name', ''),
                'Kategorie': c.get('category', ''),
                'Preis': format_german_currency(c.get('price_netto', 0))
            } for c in recent])
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Fehler beim Laden der Statistiken: {e}")


def _render_enhanced_component_list() -> None:
    """Verbesserte Komponentenliste mit Marken-Dropdown und Filtern."""
    
    st.markdown('<p class="section-header"> Komponenten verwalten</p>', unsafe_allow_html=True)
    
    try:
        all_components = read_components()
        
        if not all_components:
            st.info("Keine Komponenten vorhanden. Erstellen Sie die erste Komponente im Tab 'Neue Komponente'.")
            return
        
        # === FILTER SECTION ===
        st.markdown("#### Filter & Suche")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Marken-Dropdown
            manufacturers = sorted(set(c.get('manufacturer', '') for c in all_components))
            selected_manufacturer = st.selectbox(
                " Hersteller",
                ['Alle'] + manufacturers,
                key='filter_manufacturer'
            )
        
        with col2:
            # Kategorie-Filter
            categories = sorted(set(c.get('category', '') for c in all_components))
            selected_category = st.selectbox(
                " Kategorie",
                ['Alle'] + categories,
                key='filter_category'
            )
        
        with col3:
            # Dachtyp-Filter
            roof_types = sorted(set(c.get('roof_type', '') for c in all_components))
            selected_roof = st.selectbox(
                " Dachtyp",
                ['Alle'] + roof_types,
                key='filter_roof'
            )
        
        with col4:
            # Suchfeld
            search_term = st.text_input(
                " Suche",
                placeholder="Produktname...",
                key='search_term'
            )
        
        # === FILTERING LOGIC ===
        filtered = all_components
        
        if selected_manufacturer != 'Alle':
            filtered = [c for c in filtered if c.get('manufacturer') == selected_manufacturer]
        
        if selected_category != 'Alle':
            filtered = [c for c in filtered if c.get('category') == selected_category]
        
        if selected_roof != 'Alle':
            filtered = [c for c in filtered if c.get('roof_type') == selected_roof]
        
        if search_term:
            search_lower = search_term.lower()
            filtered = [c for c in filtered if 
                       search_lower in c.get('product_name', '').lower() or
                       search_lower in c.get('manufacturer', '').lower() or
                       search_lower in c.get('article_number', '').lower()]
        
        st.info(f"**{len(filtered)}** von **{len(all_components)}** Komponenten angezeigt")
        
        # === TABLE WITH ACTIONS ===
        if filtered:
            st.markdown("---")
            
            # Create DataFrame
            df_display = pd.DataFrame([{
                'ID': c.get('id', ''),
                'Hersteller': c.get('manufacturer', ''),
                'Produkt': c.get('product_name', ''),
                'Art.-Nr.': c.get('article_number', ''),
                'Kategorie': c.get('category', ''),
                'Dachtyp': c.get('roof_type', ''),
                'Preis': format_german_currency(c.get('price_netto', 0)),
                'Einheit': c.get('unit', ''),
                'Gewicht': f"{c.get('weight_kg', 0):.2f} kg".replace('.', ','),
            } for c in filtered])
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # === ACTIONS ===
            st.markdown("---")
            st.markdown("####  Aktionen")
            
            col_action1, col_action2 = st.columns([1, 3])
            
            with col_action1:
                # Select component for editing/deleting
                component_ids = [c['id'] for c in filtered]
                selected_id = st.selectbox(
                    "Komponente auswählen",
                    component_ids,
                    format_func=lambda x: next((c['product_name'] for c in filtered if c['id'] == x), str(x))
                )
            
            with col_action2:
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(" Bearbeiten", use_container_width=True):
                        st.session_state['edit_component_id'] = selected_id
                        st.rerun()
                
                with col_btn2:
                    if st.button(" Duplizieren", use_container_width=True):
                        st.session_state['duplicate_component_id'] = selected_id
                        st.rerun()
                
                with col_btn3:
                    if st.button("Löschen", type="primary", use_container_width=True):
                        st.session_state['delete_component_id'] = selected_id
                        st.rerun()
            
            # === EDIT MODAL ===
            if 'edit_component_id' in st.session_state:
                _render_edit_component_modal(st.session_state['edit_component_id'])
            
            # === DELETE CONFIRMATION ===
            if 'delete_component_id' in st.session_state:
                _render_delete_confirmation(st.session_state['delete_component_id'])
        
    except Exception as e:
        st.error(f"Fehler beim Laden der Komponenten: {e}")
        st.exception(e)


def _render_edit_component_modal(component_id: int) -> None:
    """Modal zum Bearbeiten einer Komponente."""
    
    try:
        all_components = read_components()
        component = next((c for c in all_components if c['id'] == component_id), None)
        
        if not component:
            st.error(f"Komponente mit ID {component_id} nicht gefunden")
            del st.session_state['edit_component_id']
            return
        
        st.markdown("---")
        st.markdown(f"###  Komponente bearbeiten: {component.get('product_name', '')}")
        
        with st.form("edit_component_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                manufacturer = st.text_input("Hersteller *", value=component.get('manufacturer', ''))
                product_name = st.text_input("Produktname *", value=component.get('product_name', ''))
                article_number = st.text_input("Artikelnummer", value=component.get('article_number', ''))
                category = st.text_input("Kategorie *", value=component.get('category', ''))
                roof_type = st.text_input("Dachtyp *", value=component.get('roof_type', ''))
            
            with col2:
                material = st.text_input("Material", value=component.get('material', ''))
                dimensions = st.text_input("Abmessungen", value=component.get('dimensions', ''))
                weight_kg = st.number_input("Gewicht (kg)", value=component.get('weight_kg', 0.0), format="%.3f")
                price_netto = st.number_input("Preis netto (€)", value=component.get('price_netto', 0.0), format="%.2f")
                unit = st.selectbox("Einheit", ['Stk', 'm', 'kg', 'Set', 'Paar'], 
                                   index=['Stk', 'm', 'kg', 'Set', 'Paar'].index(component.get('unit', 'Stk')))
            
            quantity_per_module = st.number_input("Menge pro Modul", value=component.get('quantity_per_module', 0.0), format="%.2f")
            compatibility = st.text_area("Kompatibilität", value=component.get('compatibility', ''))
            warranty_years = st.number_input("Garantie (Jahre)", value=component.get('warranty_years', 10))
            notes = st.text_area("Notizen", value=component.get('notes', ''))
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button(" Speichern", use_container_width=True, type="primary")
            
            with col_cancel:
                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
            
            if submitted:
                updated_data = {
                    'id': component_id,
                    'manufacturer': manufacturer,
                    'product_name': product_name,
                    'article_number': article_number,
                    'category': category,
                    'roof_type': roof_type,
                    'material': material,
                    'dimensions': dimensions,
                    'weight_kg': weight_kg,
                    'price_netto': price_netto,
                    'unit': unit,
                    'quantity_per_module': quantity_per_module,
                    'compatibility': compatibility,
                    'warranty_years': warranty_years,
                    'notes': notes,
                    'specifications': component.get('specifications', {})
                }
                
                if update_component(updated_data):
                    st.success("Komponente erfolgreich aktualisiert!")
                    del st.session_state['edit_component_id']
                    st.rerun()
                else:
                    st.error("Fehler beim Aktualisieren der Komponente")
            
            if cancelled:
                del st.session_state['edit_component_id']
                st.rerun()
    
    except Exception as e:
        st.error(f"Fehler: {e}")
        del st.session_state['edit_component_id']


def _render_delete_confirmation(component_id: int) -> None:
    """Bestätigungsdialog zum Löschen."""
    
    try:
        all_components = read_components()
        component = next((c for c in all_components if c['id'] == component_id), None)
        
        if not component:
            del st.session_state['delete_component_id']
            return
        
        st.markdown("---")
        st.warning(f"**Wirklich löschen?** {component.get('manufacturer', '')} - {component.get('product_name', '')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Ja, löschen", type="primary", use_container_width=True):
                if delete_component(component_id):
                    st.success("Komponente gelöscht!")
                    del st.session_state['delete_component_id']
                    st.rerun()
                else:
                    st.error("Fehler beim Löschen")
        
        with col2:
            if st.button("Abbrechen", use_container_width=True):
                del st.session_state['delete_component_id']
                st.rerun()
    
    except Exception as e:
        st.error(f"Fehler: {e}")
        del st.session_state['delete_component_id']


def _render_enhanced_create_component() -> None:
    """Verbesserte Komponenten-Erstellung."""
    
    st.markdown('<p class="section-header"> Neue Komponente erstellen</p>', unsafe_allow_html=True)
    
    # Quick-Add-Vorlagen
    st.markdown("#### Schnell-Vorlagen")
    
    templates = {
        "Dachhaken": {
            'category': 'Dachhaken',
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'weight_kg': 0.45
        },
        "Montageschiene": {
            'category': 'Montageschiene',
            'unit': 'm',
            'quantity_per_module': 1.2,
            'weight_kg': 1.2
        },
        "Modulklemme": {
            'category': 'Modulklemme (End)',
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'weight_kg': 0.08
        }
    }
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (template_name, template_data) in enumerate(templates.items()):
        col = [col1, col2, col3][idx]
        with col:
            if st.button(f" {template_name}", use_container_width=True):
                st.session_state['component_template'] = template_data
                st.rerun()
    
    st.markdown("---")
    
    # Get template data if exists
    template = st.session_state.get('component_template', {})
    
    with st.form("create_component_form", clear_on_submit=True):
        st.markdown("#### Komponenten-Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            manufacturer = st.text_input(" Hersteller *", value=template.get('manufacturer', ''))
            product_name = st.text_input("Produktname *", value=template.get('product_name', ''))
            article_number = st.text_input(" Artikelnummer", value=template.get('article_number', ''))
            category = st.text_input(" Kategorie *", value=template.get('category', ''))
            roof_type = st.text_input(" Dachtyp *", value=template.get('roof_type', 'Universal'))
        
        with col2:
            material = st.text_input(" Material", value=template.get('material', ''))
            dimensions = st.text_input(" Abmessungen", value=template.get('dimensions', ''))
            weight_kg = st.number_input(" Gewicht (kg)", value=template.get('weight_kg', 0.0), format="%.3f")
            price_netto = st.number_input(" Preis netto (€)", value=template.get('price_netto', 0.0), format="%.2f")
            unit = st.selectbox("Einheit", ['Stk', 'm', 'kg', 'Set', 'Paar'], 
                               index=['Stk', 'm', 'kg', 'Set', 'Paar'].index(template.get('unit', 'Stk')))
        
        quantity_per_module = st.number_input(" Menge pro Modul", value=template.get('quantity_per_module', 0.0), format="%.2f")
        compatibility = st.text_area(" Kompatibilität", value=template.get('compatibility', ''))
        warranty_years = st.number_input(" Garantie (Jahre)", value=template.get('warranty_years', 10))
        notes = st.text_area("Notizen", value=template.get('notes', ''))
        
        submitted = st.form_submit_button("Komponente erstellen", use_container_width=True, type="primary")
        
        if submitted:
            if not all([manufacturer, product_name, category, roof_type]):
                st.error("Bitte füllen Sie alle Pflichtfelder aus!")
            else:
                new_component = {
                    'manufacturer': manufacturer,
                    'product_name': product_name,
                    'article_number': article_number,
                    'category': category,
                    'roof_type': roof_type,
                    'material': material,
                    'dimensions': dimensions,
                    'weight_kg': weight_kg,
                    'price_netto': price_netto,
                    'unit': unit,
                    'quantity_per_module': quantity_per_module,
                    'compatibility': compatibility,
                    'warranty_years': warranty_years,
                    'notes': notes,
                    'specifications': {}
                }
                
                try:
                    component_id = create_component(new_component)
                    st.success(f"Komponente erfolgreich erstellt! (ID: {component_id})")
                    
                    # Clear template
                    if 'component_template' in st.session_state:
                        del st.session_state['component_template']
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Erstellen: {e}")


def _render_advanced_search() -> None:
    """Erweiterte Suchfunktion."""
    
    st.markdown('<p class="section-header"> Erweiterte Suche</p>', unsafe_allow_html=True)
    
    st.info("Suchen Sie Komponenten mit erweiterten Filtern")
    
    # Search form
    with st.form("advanced_search"):
        col1, col2 = st.columns(2)
        
        with col1:
            search_manufacturer = st.text_input("Hersteller (enthält)")
            search_product = st.text_input("Produktname (enthält)")
            search_category = st.text_input("Kategorie (enthält)")
        
        with col2:
            price_min = st.number_input("Preis min (€)", value=0.0, format="%.2f")
            price_max = st.number_input("Preis max (€)", value=1000.0, format="%.2f")
            weight_max = st.number_input("Max Gewicht (kg)", value=100.0, format="%.2f")
        
        search_submitted = st.form_submit_button("Suchen", use_container_width=True, type="primary")
    
    if search_submitted:
        try:
            all_components = read_components()
            
            # Apply filters
            results = all_components
            
            if search_manufacturer:
                results = [c for c in results if search_manufacturer.lower() in c.get('manufacturer', '').lower()]
            
            if search_product:
                results = [c for c in results if search_product.lower() in c.get('product_name', '').lower()]
            
            if search_category:
                results = [c for c in results if search_category.lower() in c.get('category', '').lower()]
            
            results = [c for c in results if price_min <= c.get('price_netto', 0) <= price_max]
            results = [c for c in results if c.get('weight_kg', 0) <= weight_max]
            
            st.success(f"**{len(results)}** Komponenten gefunden")
            
            if results:
                df_results = pd.DataFrame([{
                    'Hersteller': c.get('manufacturer', ''),
                    'Produkt': c.get('product_name', ''),
                    'Kategorie': c.get('category', ''),
                    'Dachtyp': c.get('roof_type', ''),
                    'Preis': format_german_currency(c.get('price_netto', 0)),
                    'Gewicht': f"{c.get('weight_kg', 0):.2f} kg".replace('.', ','),
                } for c in results])
                
                st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        except Exception as e:
            st.error(f"Fehler bei der Suche: {e}")


def _render_import_export() -> None:
    """Import/Export-Funktionen."""
    
    st.markdown('<p class="section-header"> Daten Import/Export</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###  Export")
        
        try:
            all_components = read_components()
            
            if all_components:
                # Export as JSON
                json_data = json.dumps(all_components, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="Als JSON exportieren",
                    data=json_data,
                    file_name="pv_mounting_components.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # Export as CSV
                df_export = pd.DataFrame([{
                    'Hersteller': c.get('manufacturer', ''),
                    'Produktname': c.get('product_name', ''),
                    'Artikelnummer': c.get('article_number', ''),
                    'Kategorie': c.get('category', ''),
                    'Dachtyp': c.get('roof_type', ''),
                    'Material': c.get('material', ''),
                    'Abmessungen': c.get('dimensions', ''),
                    'Gewicht_kg': c.get('weight_kg', 0),
                    'Preis_netto': c.get('price_netto', 0),
                    'Einheit': c.get('unit', ''),
                    'Menge_pro_Modul': c.get('quantity_per_module', 0),
                } for c in all_components])
                
                csv_data = df_export.to_csv(index=False, encoding='utf-8-sig', sep=';')
                
                st.download_button(
                    label="Als CSV exportieren",
                    data=csv_data,
                    file_name="pv_mounting_components.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.success(f"{len(all_components)} Komponenten bereit zum Export")
            else:
                st.info("Keine Daten zum Exportieren vorhanden")
        
        except Exception as e:
            st.error(f"Export-Fehler: {e}")
    
    with col2:
        st.markdown("###  Import")
        st.info("Import-Funktion in Entwicklung")


# Alias für Kompatibilität
def render_pv_mounting_admin_tab():
    """Alias für alte Funktion - leitet zu v2 weiter."""
    render_pv_mounting_admin_tab_v2()


if __name__ == "__main__":
    st.set_page_config(page_title="PV-Unterkonstruktion Admin v2.0", layout="wide")
    render_pv_mounting_admin_tab_v2()
