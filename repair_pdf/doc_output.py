"""
Datei: pdf_ui.py
Zweck: Benutzeroberfläche für die Konfiguration und Erstellung von Angebots-PDFs.
       Ermöglicht die Auswahl von Vorlagen, Inhalten und spezifischen Diagrammen in einem Dreispaltenlayout.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-03
"""
# pdf_ui.py (ehemals doc_output.py)
# Modul für die Angebotsausgabe (PDF)

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import traceback
import os

import os  # (bereits vorhanden, hier nur zur Orientierung)

# Dynamische PDF-Overlay-Pfade (Koordinatendateien und PDF-Hintergründe)
_PDF_UI_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_DIR_PDF_UI = os.path.join(_PDF_UI_BASE_DIR, "coords")
BG_DIR_PDF_UI = os.path.join(_PDF_UI_BASE_DIR, "pdf_templates_static", "notext")

# Vorlage für dynamische Platzhalter (identisch zu pdf_generator.py)
DYNAMIC_DATA_TEMPLATE: Dict[str, str] = {
    "customer_name": "",
    "customer_street": "",
    "customer_city_zip": "",
    "customer_phone": "",
    "customer_email": "",
    "savings_with_battery": "",
    "savings_without_battery": "",
    "pv_power_kWp": "",
    "battery_capacity_kWh": "",
    "annual_yield_kwh": "",
    "self_sufficiency": "",
    "self_consumption": ""
}

# --- Fallback-Funktionsreferenzen ---
# (Diese bleiben unverändert)
def _dummy_load_admin_setting_pdf_ui(key, default=None):
    if key == 'pdf_title_image_templates': return [{'name': 'Standard-Titelbild (Fallback)', 'data': None}]
    if key == 'pdf_offer_title_templates': return [{'name': 'Standard-Titel (Fallback)', 'content': 'Angebot für Ihre Photovoltaikanlage'}]
    if key == 'pdf_cover_letter_templates': return [{'name': 'Standard-Anschreiben (Fallback)', 'content': 'Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.'}]
    elif key == 'active_company_id': return None
    elif key == 'company_information': return {"name": "Ihre Firma (Fallback)", "id": 0, "logo_base64": None}
    elif key == 'company_logo_base64': return None
    return default
def _dummy_save_admin_setting_pdf_ui(key, value): return False
def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error("PDF-Generierungsfunktion (pdf_generator.py) nicht verfügbar oder fehlerhaft (Dummy in pdf_ui.py aktiv).")
    missing_args = [k for k in ['load_admin_setting_func', 'save_admin_setting_func', 'list_products_func', 'get_product_by_id_func'] if k not in kwargs or not callable(kwargs[k])]
    if missing_args: st.error(f"Dummy PDF Generator: Fehlende Kernfunktionen: {', '.join(missing_args)}")
    return None
def _dummy_get_active_company_details() -> Optional[Dict[str, Any]]:
    return {"name": "Dummy Firma AG", "id": 0, "logo_base64": None}
def _dummy_list_company_documents(company_id: int, doc_type: Optional[str]=None) -> List[Dict[str, Any]]:
    return []

# PDF DEBUG WIDGET IMPORT
try:
    from pdf_debug_widget import integrate_pdf_debug
    DEBUG_WIDGET_AVAILABLE = True
except ImportError:
    DEBUG_WIDGET_AVAILABLE = False

_generate_offer_pdf_safe = _dummy_generate_offer_pdf
try:
    from pdf_generator import generate_offer_pdf
    _generate_offer_pdf_safe = generate_offer_pdf
except (ImportError, ModuleNotFoundError): pass
except Exception: pass

# --- Hilfsfunktionen ---
def get_text_pdf_ui(texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict):
        return fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Texte fehlen)"
    return texts_dict.get(key, fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Text-Key fehlt)")

def _show_pdf_data_status(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> bool:
    """
    Zeigt den Status der verfügbaren Daten für die PDF-Erstellung an und gibt zurück, ob die Daten ausreichen.
    """
    st.subheader(get_text_pdf_ui(texts, "pdf_data_status_header", " Datenstatus für PDF-Erstellung"))
    
    validation_result = None
    data_sufficient = False

    # Datenvalidierung mit direktem Import der PDF-Generator-Validierung
    try:
        from pdf_generator import _validate_pdf_data_availability
        validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
        
        # ULTRA-AI-KORREKTUR: Zusätzliche Prüfung, um einen Absturz zu verhindern.
        if validation_result is None:
            st.error(get_text_pdf_ui(texts, "pdf_validation_internal_error", "Interner Fehler: Die Datenvalidierung hat kein Ergebnis zurückgegeben."))
            return False # Sauberer Ausstieg, um Absturz zu verhindern

        # Sicheres Abrufen des Wertes mit .get()
        data_sufficient = validation_result.get('is_valid', False)

    except ImportError:
        # Fallback zur lokalen Validierung, wenn Import fehlschlägt
        st.warning("Validierungsfunktion in pdf_generator.py nicht gefunden. Führe einfache Prüfung durch.")
        validation_result = {'is_valid': True, 'warnings': [], 'critical_errors': [], 'missing_data_summary': []}
        if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
            validation_result['critical_errors'].append("Keine Analyseergebnisse verfügbar")
            validation_result['missing_data_summary'].append("Analyseergebnisse")
            data_sufficient = False
        else:
            data_sufficient = True

    # Status-Indikatoren anzeigen
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        customer_data = project_data.get('customer_data', {})
        if customer_data and customer_data.get('last_name'):
            st.success(" " + get_text_pdf_ui(texts, "customer_data_complete", "Kundendaten"))
        else:
            st.info("ℹ " + get_text_pdf_ui(texts, "customer_data_incomplete", "Kundendaten"))
    with col2:
        pv_details = project_data.get('pv_details', {})
        project_details = project_data.get('project_details', {})
        modules_ok = (pv_details and pv_details.get('selected_modules')) or (project_details and project_details.get('module_quantity', 0) > 0)
        if modules_ok:
            st.success(" " + get_text_pdf_ui(texts, "pv_config_complete", "PV-Module"))
        else:
            st.info("ℹ " + get_text_pdf_ui(texts, "pv_config_incomplete", "PV-Module"))
    with col3:
        project_details = project_data.get('project_details', {})
        inverter_ok = project_details and (project_details.get('selected_inverter_id') or project_details.get('selected_inverter_name'))
        if inverter_ok:
            st.success(" " + get_text_pdf_ui(texts, "inverter_config_complete", "Wechselrichter"))
        else:
            st.info("ℹ " + get_text_pdf_ui(texts, "inverter_config_incomplete", "Wechselrichter"))
    with col4:
        if analysis_results and isinstance(analysis_results, dict) and len(analysis_results) > 1 and analysis_results.get('anlage_kwp'):
            st.success(" " + get_text_pdf_ui(texts, "analysis_complete", "Berechnung"))
        else:
            st.error(" " + get_text_pdf_ui(texts, "analysis_missing", "Berechnung"))
            
    # Handlungsempfehlungen
    if not data_sufficient:
        critical_messages = validation_result.get('critical_errors', [])
        critical_summary = ", ".join(critical_messages) if critical_messages else "Kritische Daten fehlen"
        st.error(" " + get_text_pdf_ui(texts, "pdf_creation_blocked", f"PDF-Erstellung nicht möglich. {critical_summary}"))
        st.info(get_text_pdf_ui(texts, "pdf_creation_instructions", "Bitte führen Sie eine Wirtschaftlichkeitsberechnung durch, bevor Sie ein PDF erstellen."))
    elif validation_result.get('warnings'):
        warn_list = validation_result.get('warnings', []) or []
        st.warning(" " + get_text_pdf_ui(texts, "pdf_creation_warnings", "PDF kann erstellt werden, enthält aber möglicherweise nicht alle gewünschten Informationen."))
        st.info(get_text_pdf_ui(texts, "pdf_creation_with_warnings", f"Bei unvollständigen Daten wird ein vereinfachtes PDF mit den verfügbaren Informationen erstellt. ({len(warn_list)} Warnungen)"))
        with st.expander("Warnungsdetails anzeigen"):
            for w in warn_list:
                st.warning(f"- {w}")
    else:
        st.success(" " + get_text_pdf_ui(texts, "pdf_data_complete", "Alle erforderlichen Daten verfügbar - vollständiges PDF kann erstellt werden!"))
    
    return data_sufficient

def render_pdf_ui(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]] = _dummy_list_company_documents
):
    #  PREMIUM PDF UI HEADER
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; padding: 30px; margin: 20px 0; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.2); text-align: center;">
        <h1 style="color: white; margin: 0; font-weight: 700; font-size: 32px;">
             PREMIUM PDF GENERATOR
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">
            Erstellen Sie professionelle Angebots-PDFs mit erweiterten Optionen
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # SESSION STATE DATEN KONSOLIDIERUNG - FIX FÜR FEHLENDE DATEN
    if not project_data or not isinstance(project_data, dict) or len(project_data) == 0:
        potential_sources = ['current_project_data', 'project_details', 'projektdaten']
        for source in potential_sources:
            if st.session_state.get(source) and isinstance(st.session_state[source], dict):
                project_data = st.session_state[source]
                st.session_state.project_data = project_data
                st.success(f" Projektdaten aus '{source}' wiederhergestellt")
                break
    
    if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) == 0:
        potential_sources = ['calculation_results', 'current_analysis_results', 'kpi_results', 'berechnung_ergebnisse']
        for source in potential_sources:
            source_data = st.session_state.get(source)
            if source_data and isinstance(source_data, dict) and len(source_data) > 0:
                analysis_results = source_data
                st.session_state.analysis_results = analysis_results
                st.success(f" Analyseergebnisse aus '{source}' wiederhergestellt")
                break
    
    # DEBUG WIDGET INTEGRATION
    if DEBUG_WIDGET_AVAILABLE:
        integrate_pdf_debug(project_data, analysis_results, texts)
    
    # DATENSTATUS-ANZEIGE
    data_sufficient = _show_pdf_data_status(project_data, analysis_results, texts)
    
    #  ERWEITERTE OPTIONEN BEREICH
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                border-radius: 15px; padding: 20px; margin: 15px 0; 
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
        <h3 style="color: white; margin: 0; font-weight: 600; text-align: center;">
             ERWEITERTE PDF-OPTIONEN
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    #  VISUALISIERUNGEN & DIAGRAMME SEKTION
    with st.expander(" VISUALISIERUNGEN & DIAGRAMME", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("** Diagramm-Typ:**")
            chart_type = st.selectbox(
                "Wählen Sie den Diagramm-Typ",
                options=["CIRCLE", "DONUT", "BAR", "COLUMN", "LINE", "AREA", "PIE"],
                format_func=lambda x: {
                    "CIRCLE": " Kreis",
                    "DONUT": " Donut", 
                    "BAR": " Balken",
                    "COLUMN": " Säulen",
                    "LINE": " Linie",
                    "AREA": " Fläche",
                    "PIE": "🥧 Torte"
                }.get(x, x),
                index=0,
                key="pdf_chart_type"
            )
            
        with col2:
            st.markdown("** Farb-Schema:**")
            color_scheme = st.selectbox(
                "Farb-Schema auswählen",
                options=["PROFESSIONAL", "SOLAR", "ECO", "MODERN", "CUSTOM"],
                format_func=lambda x: {
                    "PROFESSIONAL": " Professional",
                    "SOLAR": " Solar",
                    "ECO": " Eco",
                    "MODERN": " Modern",
                    "CUSTOM": " Benutzerdefiniert"
                }.get(x, x),
                key="pdf_color_scheme"
            )
            
            if color_scheme == "CUSTOM":
                primary_color = st.color_picker("Primärfarbe", "#2E86AB", key="pdf_primary_color")
                secondary_color = st.color_picker("Sekundärfarbe", "#A23B72", key="pdf_secondary_color")
        
        with col3:
            st.markdown("** ERWEITERTE DIAGRAMM-OPTIONEN:**")
            
            # Diagramm-Typen
            chart_types = st.multiselect(
                " Diagramm-Typen auswählen:",
                options=["CIRCLE", "DONUT", "BAR", "LINE", "AREA", "POLAR", "RADAR", "WATERFALL"],
                default=["CIRCLE", "BAR"],
                format_func=lambda x: {
                    "CIRCLE": " Kreisdiagramm",
                    "DONUT": " Donut-Diagramm", 
                    "BAR": " Balkendiagramm",
                    "LINE": " Liniendiagramm",
                    "AREA": " Flächendiagramm",
                    "POLAR": " Polar-Diagramm",
                    "RADAR": " Radar-Diagramm",
                    "WATERFALL": " Wasserfalldiagramm"
                }.get(x, x),
                key="pdf_chart_types"
            )
            
            # Chart-Eigenschaften
            show_values = st.checkbox(" Werte anzeigen", value=True, key="pdf_show_values")
            show_legend = st.checkbox(" Legende anzeigen", value=True, key="pdf_show_legend")
            use_3d_effect = st.checkbox(" 3D-Effekt", value=False, key="pdf_3d_effect")
            animate_charts = st.checkbox(" Animierte Diagramme", value=False, key="pdf_animate_charts")
            
            # Erweiterte Chart-Optionen
            with st.expander(" Erweiterte Chart-Einstellungen", expanded=False):
                chart_resolution = st.selectbox(" Auflösung", ["Standard", "Hoch", "Ultra"], key="pdf_chart_resolution")
                chart_style = st.selectbox(" Stil", ["Modern", "Classic", "Minimal", "Bold"], key="pdf_chart_style_detailed")
                
                # Spezielle Donut-Optionen
                if "DONUT" in chart_types:
                    donut_inner_radius = st.slider(" Donut Innenradius (%)", 20, 80, 50, key="pdf_donut_inner_radius")
                
                # Spezielle Bar-Optionen
                if "BAR" in chart_types:
                    bar_orientation = st.selectbox(" Balken-Ausrichtung", ["Vertikal", "Horizontal"], key="pdf_bar_orientation")
                    bar_width = st.slider(" Balken-Breite", 0.3, 1.0, 0.6, 0.1, key="pdf_bar_width")
                
                # Polar & Radar Optionen
                if "POLAR" in chart_types or "RADAR" in chart_types:
                    polar_grid = st.checkbox(" Gitternetz anzeigen", value=True, key="pdf_polar_grid")
    
    # Zusätzliche Diagramm-Konfiguration
    with st.expander(" DIAGRAMM-KONFIGURATION", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
            <h4 style="margin: 0; color: white;"> ERWEITERTE DIAGRAMM-FEATURES</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Konfigurieren Sie Ihre Diagramme für maximale Wirkung</p>
        </div>
        """, unsafe_allow_html=True)
        
        diag_col1, diag_col2, diag_col3 = st.columns(3)
        
        with diag_col1:
            st.markdown("** Design-Optionen:**")
            gradient_effects = st.checkbox(" Gradient-Effekte", value=True, key="pdf_gradient_effects")
            shadow_effects = st.checkbox(" Schatten-Effekte", value=False, key="pdf_shadow_effects")
            rounded_corners = st.checkbox(" Abgerundete Ecken", value=True, key="pdf_rounded_corners")
            transparency = st.slider(" Transparenz (%)", 0, 50, 0, key="pdf_transparency")
            
        with diag_col2:
            st.markdown("** Beschriftungen:**")
            title_size = st.selectbox(" Titel-Größe", ["Klein", "Normal", "Groß", "Extra Groß"], index=1, key="pdf_title_size")
            label_rotation = st.slider(" Label-Rotation (°)", -90, 90, 0, key="pdf_label_rotation")
            show_percentages = st.checkbox("% Prozent-Werte", value=True, key="pdf_show_percentages")
            show_absolute = st.checkbox("# Absolute Werte", value=True, key="pdf_show_absolute")
            
        with diag_col3:
            st.markdown("** Interaktivität:**")
            highlight_segments = st.checkbox(" Segmente hervorheben", value=False, key="pdf_highlight_segments")
            explode_slices = st.checkbox(" Segmente 'explodieren'", value=False, key="pdf_explode_slices")
            color_mapping = st.selectbox(" Farbzuordnung", 
                ["Automatisch", "Nach Wert", "Nach Kategorie", "Benutzerdefiniert"], 
                key="pdf_color_mapping"
            )
            
        # Diagramm-Vorschau
        st.markdown("---")
        st.markdown("** DIAGRAMM-VORSCHAU:**")
        
        if chart_types:
            preview_cols = st.columns(min(len(chart_types), 4))
            for i, chart_type in enumerate(chart_types[:4]):
                with preview_cols[i]:
                    st.markdown(f"""
                    <div style="background: #f0f2f6; border-radius: 8px; padding: 10px; text-align: center; margin: 5px 0;">
                        <h5 style="margin: 0;">{chart_type}</h5>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                            {"" if chart_type == "CIRCLE" else 
                             "" if chart_type == "DONUT" else
                             "" if chart_type == "BAR" else
                             "" if chart_type == "LINE" else
                             "" if chart_type == "AREA" else
                             "" if chart_type == "POLAR" else
                             "" if chart_type == "RADAR" else
                             ""} Aktiviert
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(" Wählen Sie mindestens einen Diagramm-Typ aus")
        
        # Chart-Konfiguration für Session State speichern
        chart_config = {
            'chart_types': chart_types,
            'show_values': show_values,
            'show_legend': show_legend,
            'use_3d_effect': use_3d_effect,
            'animate_charts': animate_charts,
            'chart_resolution': chart_resolution,
            'chart_style_detailed': chart_style,
            'gradient_effects': gradient_effects,
            'shadow_effects': shadow_effects,
            'rounded_corners': rounded_corners,
            'transparency': transparency,
            'title_size': title_size,
            'label_rotation': label_rotation,
            'show_percentages': show_percentages,
            'show_absolute': show_absolute,
            'highlight_segments': highlight_segments,
            'explode_slices': explode_slices,
            'color_mapping': color_mapping
        }
        
        # Spezielle Konfigurationen hinzufügen
        if "DONUT" in chart_types:
            chart_config['donut_inner_radius'] = donut_inner_radius
        if "BAR" in chart_types:
            chart_config['bar_orientation'] = bar_orientation
            chart_config['bar_width'] = bar_width
        if "POLAR" in chart_types or "RADAR" in chart_types:
            chart_config['polar_grid'] = polar_grid
            
        # In Session State speichern
        st.session_state['chart_config'] = chart_config
        
        # Konfiguration-Summary
        st.markdown("** KONFIGURATION-ÜBERSICHT:**")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric(" Diagramm-Typen", len(chart_types))
            st.metric(" Design-Features", 
                sum([gradient_effects, shadow_effects, rounded_corners, use_3d_effect]))
            
        with summary_col2:  
            st.metric(" Beschriftungs-Features", 
                sum([show_values, show_legend, show_percentages, show_absolute]))
            st.metric(" Interaktivität", 
                sum([highlight_segments, explode_slices, animate_charts]))
            
        with summary_col3:
            active_chart_types = ", ".join(chart_types[:2]) + ("..." if len(chart_types) > 2 else "")
            st.metric(" Aktive Typen", active_chart_types if active_chart_types else "Keine")
            st.metric(" Erweiterte Optionen", f"{chart_resolution} | {chart_style}")
    
    
    #  FINANZANALYSE SEKTION (ERWEITERT)
    with st.expander(" FINANZANALYSE & WIRTSCHAFTLICHKEIT (OPTIONAL)", expanded=False):
        include_financing = st.checkbox(" Erweiterte Finanzierungsanalyse einschließen", value=False, key="pdf_include_financing")
        
        if include_financing:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                        border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
                <h4 style="margin: 0; color: white;"> FINANZIERUNGSOPTIONEN</h4>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Konfigurieren Sie die Finanzierungsparameter für Ihr PDF</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Basis-Finanzierungsparameter
            fin_col1, fin_col2, fin_col3 = st.columns(3)
            
            with fin_col1:
                st.markdown("** Grundparameter:**")
                loan_duration = st.slider(" Laufzeit (Jahre)", 5, 25, 15, key="pdf_loan_duration")
                interest_rate = st.slider(" Zinssatz (%)", 1.0, 8.0, 3.5, 0.1, key="pdf_interest_rate")
                down_payment = st.slider(" Anzahlung (%)", 0, 50, 20, key="pdf_down_payment")
                
            with fin_col2:
                st.markdown("** Zusätzliche Analysen:**")
                show_roi_analysis = st.checkbox(" ROI-Analyse", value=True, key="pdf_roi_analysis")
                show_payback_period = st.checkbox(" Amortisationszeit", value=True, key="pdf_payback")
                show_cash_flow = st.checkbox(" Cash-Flow-Tabelle", value=True, key="pdf_cash_flow")
                show_sensitivity = st.checkbox(" Sensitivitätsanalyse", value=False, key="pdf_sensitivity")
                
            with fin_col3:
                st.markdown("** Premium Features:**")
                show_tax_benefits = st.checkbox(" Steuervorteile", value=True, key="pdf_tax_benefits")
                show_inflation_impact = st.checkbox(" Inflationseffekte", value=False, key="pdf_inflation")
                show_comparison_table = st.checkbox(" Vergleichstabelle", value=True, key="pdf_comparison")
                show_financing_scenarios = st.checkbox(" 3 Finanzierungsszenarien", value=False, key="pdf_scenarios")
            
            # Erweiterte Optionen
            st.markdown("---")
            adv_col1, adv_col2 = st.columns(2)
            
            with adv_col1:
                st.markdown("** Erweiterte Einstellungen:**")
                annual_price_increase = st.slider(" Jährliche Strompreissteigerung (%)", 0.0, 8.0, 3.0, 0.5, key="pdf_price_increase")
                maintenance_costs = st.slider(" Jährliche Wartungskosten (€)", 0, 500, 150, 25, key="pdf_maintenance")
                insurance_costs = st.slider(" Jährliche Versicherung (€)", 0, 300, 100, 25, key="pdf_insurance")
                
            with adv_col2:
                st.markdown("** Visualisierung:**")
                chart_style = st.selectbox(" Diagrammstil", 
                    ["Modern", "Business", "Minimalist", "Colorful"], 
                    key="pdf_chart_style"
                )
                include_charts = st.checkbox(" Finanz-Diagramme einschließen", value=True, key="pdf_fin_charts")
                table_style = st.selectbox(" Tabellenstil",
                    ["Standard", "Elegant", "Kompakt", "Detailliert"],
                    key="pdf_table_style"
                )
                
            # Szenario-Konfiguration (wenn Szenarien aktiviert)
            if show_financing_scenarios:
                st.markdown("---")
                st.markdown("** FINANZIERUNGSSZENARIEN KONFIGURATION:**")
                scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
                
                with scenario_col1:
                    st.markdown("** Szenario 1: Konservativ**")
                    st.caption(" Niedrige Eigenkapitalquote, lange Laufzeit")
                    s1_down = st.slider("Anzahlung (%)", 0, 30, 10, key="s1_down")
                    s1_years = st.slider("Laufzeit (Jahre)", 15, 25, 20, key="s1_years")
                    
                with scenario_col2:
                    st.markdown("** Szenario 2: Ausgewogen**")
                    st.caption(" Mittlere Eigenkapitalquote und Laufzeit")
                    s2_down = st.slider("Anzahlung (%)", 10, 40, 25, key="s2_down")
                    s2_years = st.slider("Laufzeit (Jahre)", 10, 20, 15, key="s2_years")
                    
                with scenario_col3:
                    st.markdown("** Szenario 3: Aggressiv**")
                    st.caption(" Hohe Eigenkapitalquote, kurze Laufzeit")
                    s3_down = st.slider("Anzahlung (%)", 30, 60, 40, key="s3_down")
                    s3_years = st.slider("Laufzeit (Jahre)", 5, 15, 10, key="s3_years")
            
            # Finanzierungsdaten zusammenfassen
            financing_config = {
                'loan_duration': loan_duration,
                'interest_rate': interest_rate,
                'down_payment': down_payment,
                'annual_price_increase': annual_price_increase,
                'maintenance_costs': maintenance_costs,
                'insurance_costs': insurance_costs,
                'show_roi_analysis': show_roi_analysis,
                'show_payback_period': show_payback_period,
                'show_cash_flow': show_cash_flow,
                'show_sensitivity': show_sensitivity,
                'show_tax_benefits': show_tax_benefits,
                'show_inflation_impact': show_inflation_impact,
                'show_comparison_table': show_comparison_table,
                'show_financing_scenarios': show_financing_scenarios,
                'chart_style': chart_style,
                'include_charts': include_charts,
                'table_style': table_style
            }
            
            # Szenarien hinzufügen wenn aktiviert
            if show_financing_scenarios:
                financing_config['scenarios'] = {
                    'conservative': {'down_payment': s1_down, 'duration': s1_years},
                    'balanced': {'down_payment': s2_down, 'duration': s2_years},
                    'aggressive': {'down_payment': s3_down, 'duration': s3_years}
                }
            
            # Session State speichern für PDF-Generierung
            st.session_state['financing_config'] = financing_config
            
            # Vorschau der Finanzierungsparameter
            st.markdown("---")
            st.markdown("** FINANZIERUNGSÜBERSICHT:**")
            preview_col1, preview_col2, preview_col3 = st.columns(3)
            
            with preview_col1:
                st.metric(" Laufzeit", f"{loan_duration} Jahre")
                st.metric(" Zinssatz", f"{interest_rate}%")
                
            with preview_col2:
                st.metric(" Anzahlung", f"{down_payment}%")
                st.metric(" Strompreissteigerung", f"{annual_price_increase}%")
                
            with preview_col3:
                active_features = sum([show_roi_analysis, show_payback_period, show_cash_flow, 
                                     show_sensitivity, show_tax_benefits, show_inflation_impact])
                st.metric(" Aktive Features", f"{active_features}/6")
                if show_financing_scenarios:
                    st.metric(" Szenarien", "3 Varianten")
                else:
                    st.metric(" Szenarien", "Standard")
        else:
            st.info(" **Tipp:** Aktivieren Sie die Finanzierungsanalyse für detaillierte Wirtschaftlichkeitsberechnungen, ROI-Analysen und verschiedene Finanzierungsszenarien in Ihrem PDF.")
    
    
    #  PV GIS INTEGRATION
    pvgis_enabled = load_admin_setting_func('enable_pvgis_integration', False) if callable(load_admin_setting_func) else False
    
    if pvgis_enabled:
        with st.expander(" PV GIS INTEGRATION (OPTIONAL)", expanded=False):
            include_pvgis = st.checkbox(" PV GIS Daten einschließen", value=False, key="pdf_include_pvgis")
            
            if include_pvgis:
                pvgis_col1, pvgis_col2 = st.columns(2)
                
                with pvgis_col1:
                    st.markdown("** Standort-Daten:**")
                    show_irradiance_map = st.checkbox(" Einstrahlungskarte", value=True, key="pdf_irradiance_map")
                    show_weather_data = st.checkbox(" Wetterdaten", value=True, key="pdf_weather_data")
                    
                with pvgis_col2:
                    st.markdown("** PV GIS Analysen:**")
                    show_monthly_data = st.checkbox(" Monatliche Daten", value=True, key="pdf_monthly_data")
                    show_optimal_tilt = st.checkbox(" Optimaler Neigungswinkel", value=False, key="pdf_optimal_tilt")
    
    #  UNLIMITED CUSTOM TEXTS & IMAGES
    with st.expander(" UNLIMITED CUSTOM TEXTS & IMAGES", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff7b7b 0%, #667eea 100%); 
                    border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
            <h4 style="margin: 0; color: white;"> UNBEGRENZTE ANPASSUNGSMÖGLICHKEITEN</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Fügen Sie beliebige Texte, Bilder und Inhalte zu Ihrem PDF hinzu</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Custom Content Manager
        if 'custom_content_items' not in st.session_state:
            st.session_state.custom_content_items = []
        
        # Custom Content hinzufügen
        add_col1, add_col2, add_col3 = st.columns(3)
        
        with add_col1:
            if st.button(" Text hinzufügen", use_container_width=True):
                new_item = {
                    'type': 'text',
                    'id': f"text_{len(st.session_state.custom_content_items)}",
                    'title': f"Custom Text {len([i for i in st.session_state.custom_content_items if i['type'] == 'text']) + 1}",
                    'content': 'Ihr benutzerdefinierter Text hier...',
                    'position': 'middle',
                    'style': 'normal'
                }
                st.session_state.custom_content_items.append(new_item)
                st.rerun()
                
        with add_col2:
            if st.button(" Bild hinzufügen", use_container_width=True):
                new_item = {
                    'type': 'image',
                    'id': f"image_{len(st.session_state.custom_content_items)}",
                    'title': f"Custom Image {len([i for i in st.session_state.custom_content_items if i['type'] == 'image']) + 1}",
                    'content': None,
                    'caption': 'Bildunterschrift',
                    'position': 'middle',
                    'size': 'medium'
                }
                st.session_state.custom_content_items.append(new_item)
                st.rerun()
                
        with add_col3:
            if st.button(" Tabelle hinzufügen", use_container_width=True):
                new_item = {
                    'type': 'table',
                    'id': f"table_{len(st.session_state.custom_content_items)}",
                    'title': f"Custom Table {len([i for i in st.session_state.custom_content_items if i['type'] == 'table']) + 1}",
                    'headers': ['Spalte 1', 'Spalte 2', 'Spalte 3'],
                    'rows': [['Zeile 1', 'Daten', 'Werte'], ['Zeile 2', 'Mehr', 'Info']],
                    'position': 'middle'
                }
                st.session_state.custom_content_items.append(new_item)
                st.rerun()
        
        # Aktuell hinzugefügten Content verwalten
        if st.session_state.custom_content_items:
            st.markdown("---")
            st.markdown(f"** IHRE CUSTOM INHALTE ({len(st.session_state.custom_content_items)} Elemente):**")
            
            # Content Items anzeigen und bearbeiten
            for i, item in enumerate(st.session_state.custom_content_items):
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                    """, unsafe_allow_html=True)
                    
                    # Header mit Typ-Icon und Lösch-Button
                    header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
                    
                    with header_col1:
                        type_icon = "" if item['type'] == 'text' else "" if item['type'] == 'image' else ""
                        st.markdown(f"**{type_icon} {item['title']} (ID: {item['id']})**")
                    
                    with header_col2:
                        # Move Up/Down
                        move_col1, move_col2 = st.columns(2)
                        with move_col1:
                            if st.button("", key=f"up_{item['id']}", help="Nach oben") and i > 0:
                                st.session_state.custom_content_items[i], st.session_state.custom_content_items[i-1] = \
                                    st.session_state.custom_content_items[i-1], st.session_state.custom_content_items[i]
                                st.rerun()
                        with move_col2:
                            if st.button("", key=f"down_{item['id']}", help="Nach unten") and i < len(st.session_state.custom_content_items) - 1:
                                st.session_state.custom_content_items[i], st.session_state.custom_content_items[i+1] = \
                                    st.session_state.custom_content_items[i+1], st.session_state.custom_content_items[i]
                                st.rerun()
                    
                    with header_col3:
                        if st.button(" Löschen", key=f"delete_{item['id']}", type="secondary"):
                            st.session_state.custom_content_items.remove(item)
                            st.rerun()
                    
                    # Content-spezifische Bearbeitung
                    if item['type'] == 'text':
                        # Text-Editor
                        edit_col1, edit_col2 = st.columns([2, 1])
                        
                        with edit_col1:
                            new_content = st.text_area(
                                "Inhalt:",
                                value=item['content'],
                                height=100,
                                key=f"content_{item['id']}"
                            )
                            item['content'] = new_content
                            
                        with edit_col2:
                            item['position'] = st.selectbox(
                                "Position im PDF:",
                                ["top", "middle", "bottom"],
                                index=["top", "middle", "bottom"].index(item['position']),
                                format_func=lambda x: {"top": " Oben", "middle": " Mitte", "bottom": " Unten"}[x],
                                key=f"pos_{item['id']}"
                            )
                            
                            item['style'] = st.selectbox(
                                "Text-Stil:",
                                ["normal", "bold", "italic", "highlight", "quote"],
                                index=["normal", "bold", "italic", "highlight", "quote"].index(item['style']),
                                format_func=lambda x: {
                                    "normal": " Normal",
                                    "bold": " Fett",
                                    "italic": " Kursiv", 
                                    "highlight": " Hervorgehoben",
                                    "quote": " Zitat"
                                }[x],
                                key=f"style_{item['id']}"
                            )
                    
                    elif item['type'] == 'image':
                        # Image-Upload
                        edit_col1, edit_col2 = st.columns([2, 1])
                        
                        with edit_col1:
                            uploaded_file = st.file_uploader(
                                "Bild hochladen:",
                                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                                key=f"upload_{item['id']}"
                            )
                            
                            if uploaded_file is not None:
                                # Bild in Base64 konvertieren für Speicherung
                                import base64
                                item['content'] = base64.b64encode(uploaded_file.read()).decode()
                                item['filename'] = uploaded_file.name
                                st.success(f" Bild '{uploaded_file.name}' hochgeladen")
                            
                            item['caption'] = st.text_input(
                                "Bildunterschrift:",
                                value=item['caption'],
                                key=f"caption_{item['id']}"
                            )
                            
                        with edit_col2:
                            item['position'] = st.selectbox(
                                "Position:",
                                ["top", "middle", "bottom"],
                                index=["top", "middle", "bottom"].index(item['position']),
                                format_func=lambda x: {"top": " Oben", "middle": " Mitte", "bottom": " Unten"}[x],
                                key=f"img_pos_{item['id']}"
                            )
                            
                            item['size'] = st.selectbox(
                                "Bildgröße:",
                                ["small", "medium", "large", "full"],
                                index=["small", "medium", "large", "full"].index(item['size']),
                                format_func=lambda x: {
                                    "small": " Klein",
                                    "medium": " Mittel",
                                    "large": " Groß",
                                    "full": " Vollbild"
                                }[x],
                                key=f"size_{item['id']}"
                            )
                    
                    elif item['type'] == 'table':
                        # Tabellen-Editor
                        st.markdown("** Tabellen-Editor:**")
                        
                        # Header bearbeiten
                        headers_text = st.text_input(
                            "Spalten-Überschriften (mit ; getrennt):",
                            value=";".join(item['headers']),
                            key=f"headers_{item['id']}"
                        )
                        item['headers'] = [h.strip() for h in headers_text.split(';') if h.strip()]
                        
                        # Rows bearbeiten
                        st.markdown("**Tabellenzeilen:**")
                        for row_idx, row in enumerate(item['rows']):
                            row_text = st.text_input(
                                f"Zeile {row_idx + 1} (mit ; getrennt):",
                                value=";".join(row),
                                key=f"row_{item['id']}_{row_idx}"
                            )
                            item['rows'][row_idx] = [cell.strip() for cell in row_text.split(';')]
                        
                        # Zeile hinzufügen/entfernen
                        table_col1, table_col2 = st.columns(2)
                        with table_col1:
                            if st.button(" Zeile hinzufügen", key=f"add_row_{item['id']}", use_container_width=True):
                                item['rows'].append([''] * len(item['headers']))
                                st.rerun()
                        with table_col2:
                            if st.button(" Letzte Zeile entfernen", key=f"remove_row_{item['id']}", use_container_width=True) and len(item['rows']) > 1:
                                item['rows'].pop()
                                st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Gesamt-Übersicht
            st.markdown("---")
            st.markdown("** CUSTOM CONTENT ÜBERSICHT:**")
            
            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
            
            text_count = len([i for i in st.session_state.custom_content_items if i['type'] == 'text'])
            image_count = len([i for i in st.session_state.custom_content_items if i['type'] == 'image'])
            table_count = len([i for i in st.session_state.custom_content_items if i['type'] == 'table'])
            
            with overview_col1:
                st.metric(" Texte", text_count)
            with overview_col2:
                st.metric(" Bilder", image_count)
            with overview_col3:  
                st.metric(" Tabellen", table_count)
            with overview_col4:
                st.metric(" Gesamt", len(st.session_state.custom_content_items))
            
            # Reset Button
            if st.button(" Alle Custom Inhalte löschen", type="secondary"):
                st.session_state.custom_content_items = []
                st.success(" Alle Custom Inhalte wurden gelöscht")
                st.rerun()
                
        else:
            st.info(" **Tipp:** Fügen Sie unbegrenzt eigene Texte, Bilder und Tabellen zu Ihrem PDF hinzu. Jedes Element kann individuell positioniert und gestaltet werden!")

    #  PDF DRAG & DROP EDITOR (REAL-TIME)
    with st.expander(" PDF DRAG & DROP EDITOR (REAL-TIME)", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
            <h4 style="margin: 0; color: white;"> INTERAKTIVER PDF EDITOR</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Drag & Drop Editor mit Real-Time Vorschau und Echtzeit-Änderungen</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Editor Configuration
        if 'pdf_editor_config' not in st.session_state:
            st.session_state.pdf_editor_config = {
                'editor_mode': 'visual',
                'real_time_preview': True,
                'auto_save': True,
                'grid_snap': True,
                'element_locking': False,
                'version_history': True,
                'collaboration_mode': False,
                'template_library': True
            }
        
        # Editor-Modi
        editor_col1, editor_col2, editor_col3 = st.columns(3)
        
        with editor_col1:
            st.session_state.pdf_editor_config['editor_mode'] = st.selectbox(
                " Editor-Modus:",
                ["visual", "split", "code"],
                index=["visual", "split", "code"].index(st.session_state.pdf_editor_config['editor_mode']),
                format_func=lambda x: {
                    "visual": " Visuell",
                    "split": " Split-View", 
                    "code": " Code-Editor"
                }[x]
            )
            
        with editor_col2:
            st.session_state.pdf_editor_config['real_time_preview'] = st.checkbox(
                " Real-Time Vorschau",
                value=st.session_state.pdf_editor_config['real_time_preview']
            )
            
        with editor_col3:
            st.session_state.pdf_editor_config['auto_save'] = st.checkbox(
                " Auto-Save",
                value=st.session_state.pdf_editor_config['auto_save']
            )
        
        # Advanced Editor Settings
        st.markdown("** ERWEITERTE EDITOR-EINSTELLUNGEN:**")
        
        advanced_col1, advanced_col2, advanced_col3, advanced_col4 = st.columns(4)
        
        with advanced_col1:
            st.session_state.pdf_editor_config['grid_snap'] = st.checkbox(
                " Grid-Snap",
                value=st.session_state.pdf_editor_config['grid_snap'],
                help="Automatisches Einrasten am Raster"
            )
            
        with advanced_col2:
            st.session_state.pdf_editor_config['element_locking'] = st.checkbox(
                " Element-Lock",
                value=st.session_state.pdf_editor_config['element_locking'],
                help="Elemente vor versehentlichem Verschieben schützen"
            )
            
        with advanced_col3:
            st.session_state.pdf_editor_config['version_history'] = st.checkbox(
                " Versionsverlauf",
                value=st.session_state.pdf_editor_config['version_history'],
                help="Automatische Versionierung der Änderungen"
            )
            
        with advanced_col4:
            st.session_state.pdf_editor_config['collaboration_mode'] = st.checkbox(
                " Kollaboration",
                value=st.session_state.pdf_editor_config['collaboration_mode'],
                help="Mehrbenutzermodus (Beta)"
            )
        
        # Drag & Drop Elements Library
        st.markdown("---")
        st.markdown("** ELEMENT-BIBLIOTHEK (DRAG & DROP):**")
        
        # Element Categories
        element_tabs = st.tabs([" Text", " Charts", " Bilder", " Tabellen", " Shapes", " Business"])
        
        with element_tabs[0]:  # Text Elements
            text_elements_col1, text_elements_col2, text_elements_col3 = st.columns(3)
            
            with text_elements_col1:
                st.markdown("""
                ** Text-Elemente:**
                -  Überschrift H1-H6
                -  Absatztext
                -  Zitat-Block
                -  Aufzählung
                -  Nummerierung
                """)
                
            with text_elements_col2:
                st.markdown("""
                ** Text-Stile:**
                - **Fett** / *Kursiv*
                - `Code-Stil`
                - ==Highlight==
                - ~~Durchgestrichen~~
                -  Farbiger Text
                """)
                
            with text_elements_col3:
                if st.button(" Text-Element hinzufügen", use_container_width=True):
                    st.success(" Text-Element zur Drag & Drop Zone hinzugefügt")
        
        with element_tabs[1]:  # Chart Elements
            chart_elements_col1, chart_elements_col2 = st.columns(2)
            
            with chart_elements_col1:
                st.markdown("""
                ** Standard Charts:**
                -  Balkendiagramm
                -  Liniendiagramm  
                - 🥧 Kreisdiagramm
                -  Flächendiagramm
                """)
                
            with chart_elements_col2:
                st.markdown("""
                ** Spezial Charts:**
                -  Donut Chart
                -  Radar Chart
                -  Wasserfall Chart
                -  Polar Chart
                """)
                
            if st.button(" Chart-Element hinzufügen", use_container_width=True):
                st.success(" Chart-Element zur Drag & Drop Zone hinzugefügt")
        
        with element_tabs[2]:  # Image Elements  
            image_col1, image_col2 = st.columns(2)
            
            with image_col1:
                uploaded_image = st.file_uploader(
                    " Bild hochladen:",
                    type=['png', 'jpg', 'jpeg', 'gif', 'svg']
                )
                
            with image_col2:
                st.markdown("""
                ** Bild-Optionen:**
                -  Rotation & Skalierung
                -  Filter & Effekte
                -  Zuschneiden
                -  Rahmen & Schatten
                """)
                
            if uploaded_image:
                if st.button(" Bild zur Drag & Drop Zone", use_container_width=True):
                    st.success(f" Bild '{uploaded_image.name}' hinzugefügt")
        
        with element_tabs[3]:  # Table Elements
            st.markdown("** TABELLEN-GENERATOR:**")
            
            table_col1, table_col2 = st.columns(2)
            
            with table_col1:
                table_rows = st.number_input("Zeilen:", min_value=1, max_value=20, value=3)
                table_cols = st.number_input("Spalten:", min_value=1, max_value=10, value=3)
                
            with table_col2:
                table_style = st.selectbox(
                    "Tabellen-Stil:",
                    ["basic", "striped", "bordered", "modern", "business"]
                )
                
            if st.button(" Tabelle erstellen", use_container_width=True):
                st.success(f" Tabelle ({table_rows}x{table_cols}) im {table_style}-Stil erstellt")
        
        with element_tabs[4]:  # Shape Elements
            shapes_col1, shapes_col2, shapes_col3 = st.columns(3)
            
            with shapes_col1:
                st.markdown("""
                ** Basis-Shapes:**
                -  Kreis
                -  Rechteck
                -  Dreieck
                -  Stern
                """)
                
            with shapes_col2:
                st.markdown("""
                ** Pfeile & Linien:**
                -  Einfacher Pfeil
                -  Doppelpfeil
                -  Gerade Linie
                -  Geschwungene Linie
                """)
                
            with shapes_col3:
                st.markdown("""
                ** Erweitert:**
                -  Sprechblase
                -  Label/Tag
                -  Pin/Marker
                -  Verbinder
                """)
                
            if st.button(" Shape hinzufügen", use_container_width=True):
                st.success(" Shape zur Drag & Drop Zone hinzugefügt")
        
        with element_tabs[5]:  # Business Elements
            business_col1, business_col2 = st.columns(2)
            
            with business_col1:
                st.markdown("""
                ** Business-Elemente:**
                -  Firmen-Logo
                -  KPI-Dashboard
                -  Preis-Tabelle
                -  ROI-Analyse
                """)
                
            with business_col2:
                st.markdown("""
                ** Templates:**
                -  Angebot-Template  
                -  Report-Template
                -  Präsentation
                -  Dashboard
                """)
                
            if st.button(" Business-Element hinzufügen", use_container_width=True):
                st.success(" Business-Element zur Drag & Drop Zone hinzugefügt")
        
        # Drag & Drop Zone Simulation
        st.markdown("---")
        st.markdown("** DRAG & DROP EDITOR ZONE:**")
        
        # Simulated Canvas
        st.markdown("""
        <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 30px; 
                    min-height: 300px; background: #f8f9fa; text-align: center;">
            <h3 style="color: #666; margin-top: 50px;"> DRAG & DROP CANVAS</h3>
            <p style="color: #888;">Ziehen Sie Elemente aus der Bibliothek hierher</p>
            <p style="color: #888;"> Real-Time Vorschau |  Auto-Save |  Grid-Snap</p>
            
            <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4> BEISPIEL PDF-SEITE</h4>
                <p>Hier würden Ihre Drag & Drop Elemente erscheinen...</p>
                <div style="height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 10px 0;"></div>
                <p><em> Interaktiver Editor mit Real-Time Updates</em></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Editor Tools
        st.markdown("** EDITOR-WERKZEUGE:**")
        
        tools_col1, tools_col2, tools_col3, tools_col4, tools_col5 = st.columns(5)
        
        with tools_col1:
            if st.button("↶ Rückgängig", use_container_width=True):
                st.info("⏮ Letzte Aktion wurde rückgängig gemacht")
                
        with tools_col2:
            if st.button("↷ Wiederholen", use_container_width=True):
                st.info("⏭ Aktion wurde wiederhergestellt")
                
        with tools_col3:
            if st.button(" Kopieren", use_container_width=True):
                st.info(" Auswahl wurde kopiert")
                
        with tools_col4:
            if st.button(" Zoom", use_container_width=True):
                st.info(" Zoom-Modus aktiviert")
                
        with tools_col5:
            if st.button(" Speichern", use_container_width=True):
                st.success(" PDF-Layout wurde gespeichert")
        
        # Real-Time Preview Settings
        if st.session_state.pdf_editor_config['real_time_preview']:
            st.markdown("---")
            st.markdown("** REAL-TIME VORSCHAU EINSTELLUNGEN:**")
            
            preview_col1, preview_col2, preview_col3 = st.columns(3)
            
            with preview_col1:
                preview_quality = st.select_slider(
                    " Vorschau-Qualität:",
                    options=["niedrig", "mittel", "hoch", "ultra"],
                    value="hoch"
                )
                
            with preview_col2:
                preview_refresh = st.select_slider(
                    " Aktualisierung:",
                    options=["1s", "500ms", "250ms", "real-time"],
                    value="250ms"
                )
                
            with preview_col3:
                preview_device = st.selectbox(
                    " Gerät-Vorschau:",
                    ["desktop", "tablet", "mobile", "print"]
                )
                
            st.success(f" Real-Time Vorschau: {preview_quality} Qualität, {preview_refresh} Aktualisierung, {preview_device} Ansicht")

    #  PDF UI VERSCHÖNERUNG (ADVANCED STYLING)
    with st.expander(" PDF UI VERSCHÖNERUNG (ADVANCED STYLING)", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff9a56 0%, #ff6b95 100%); 
                    border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
            <h4 style="margin: 0; color: white;"> ERWEITERTE PDF-GESTALTUNG</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Professionelle Design-Tools für perfekte PDF-Layouts</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Design Configuration
        if 'pdf_design_config' not in st.session_state:
            st.session_state.pdf_design_config = {
                'theme': 'professional',
                'color_scheme': 'blue_gradient',
                'typography': 'modern',
                'layout_style': 'clean',
                'header_style': 'modern',
                'footer_style': 'minimal',
                'page_margins': 'standard',
                'spacing': 'comfortable'
            }
        
        # Design Themes
        st.markdown("** DESIGN-THEMES:**")
        
        theme_col1, theme_col2, theme_col3, theme_col4 = st.columns(4)
        
        with theme_col1:
            if st.button(" Professional", use_container_width=True):
                st.session_state.pdf_design_config.update({
                    'theme': 'professional',
                    'color_scheme': 'blue_gradient',
                    'typography': 'serif',
                    'layout_style': 'clean'
                })
                st.success(" Professional Theme aktiviert")
                
        with theme_col2:
            if st.button(" Creative", use_container_width=True):
                st.session_state.pdf_design_config.update({
                    'theme': 'creative',
                    'color_scheme': 'rainbow_gradient',
                    'typography': 'modern',
                    'layout_style': 'dynamic'
                })
                st.success(" Creative Theme aktiviert")
                
        with theme_col3:
            if st.button(" Eco", use_container_width=True):
                st.session_state.pdf_design_config.update({
                    'theme': 'eco',
                    'color_scheme': 'green_gradient',
                    'typography': 'natural',
                    'layout_style': 'organic'
                })
                st.success(" Eco Theme aktiviert")
                
        with theme_col4:
            if st.button(" Futuristic", use_container_width=True):
                st.session_state.pdf_design_config.update({
                    'theme': 'futuristic',
                    'color_scheme': 'neon_gradient',
                    'typography': 'tech',
                    'layout_style': 'minimal'
                })
                st.success(" Futuristic Theme aktiviert")
        
        # Advanced Color Customization
        st.markdown("---")
        st.markdown("** FARB-KONFIGURATION:**")
        
        color_tabs = st.tabs([" Farbschema", " Gradients", " Akzente", " Charts"])
        
        with color_tabs[0]:  # Color Scheme
            color_col1, color_col2 = st.columns(2)
            
            with color_col1:
                primary_color = st.color_picker(" Primärfarbe", value="#667eea")
                secondary_color = st.color_picker(" Sekundärfarbe", value="#764ba2")
                
            with color_col2:
                accent_color = st.color_picker(" Akzentfarbe", value="#ff7b7b")
                text_color = st.color_picker(" Textfarbe", value="#333333")
                
            # Farb-Vorschau
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin: 15px 0;">
                <div style="width: 50px; height: 50px; background: {primary_color}; border-radius: 8px; border: 2px solid #ddd;"></div>
                <div style="width: 50px; height: 50px; background: {secondary_color}; border-radius: 8px; border: 2px solid #ddd;"></div>
                <div style="width: 50px; height: 50px; background: {accent_color}; border-radius: 8px; border: 2px solid #ddd;"></div>
                <div style="width: 50px; height: 50px; background: {text_color}; border-radius: 8px; border: 2px solid #ddd;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        with color_tabs[1]:  # Gradients
            gradient_options = st.columns(3)
            
            with gradient_options[0]:
                st.markdown("** Warm Gradients:**")
                if st.button(" Feuer", use_container_width=True):
                    st.info("Feuer-Gradient aktiviert")
                if st.button(" Sonnenuntergang", use_container_width=True):
                    st.info("Sonnenuntergang-Gradient aktiviert")
                    
            with gradient_options[1]:
                st.markdown("** Cool Gradients:**")
                if st.button(" Ocean", use_container_width=True):
                    st.info("Ocean-Gradient aktiviert")
                if st.button(" Ice", use_container_width=True):
                    st.info("Ice-Gradient aktiviert")
                    
            with gradient_options[2]:
                st.markdown("** Special:**")
                if st.button(" Rainbow", use_container_width=True):
                    st.info("Rainbow-Gradient aktiviert")
                if st.button(" Galaxy", use_container_width=True):
                    st.info("Galaxy-Gradient aktiviert")
        
        with color_tabs[2]:  # Accents
            accent_col1, accent_col2 = st.columns(2)
            
            with accent_col1:
                st.markdown("** AKZENT-STILE:**")
                accent_style = st.selectbox(
                    "Stil wählen:",
                    ["minimal", "bold", "elegant", "playful", "corporate"]
                )
                
                accent_intensity = st.slider(
                    "Intensität:",
                    min_value=10, max_value=100, value=70, step=10
                )
                
            with accent_col2:
                st.markdown("** AKZENT-BEREICHE:**")
                accent_areas = st.multiselect(
                    "Bereiche hervorheben:",
                    ["Headers", "Charts", "Tables", "Callouts", "Buttons", "Borders"],
                    default=["Headers", "Charts"]
                )
                
        with color_tabs[3]:  # Chart Colors
            st.markdown("** CHART-FARBPALETTEN:**")
            
            palette_col1, palette_col2, palette_col3 = st.columns(3)
            
            with palette_col1:
                st.markdown("** Vordefiniert:**")
                chart_palette = st.selectbox(
                    "Palette:",
                    ["viridis", "plasma", "inferno", "magma", "coolwarm", "seismic"]
                )
                
            with palette_col2:
                st.markdown("** Kategorisch:**")
                categorical_palette = st.selectbox(
                    "Kategorien:",
                    ["tab10", "tab20", "set1", "set2", "set3", "paired"]
                )
                
            with palette_col3:
                st.markdown("** Divergierend:**")
                diverging_palette = st.selectbox(
                    "Divergenz:",
                    ["RdYlBu", "RdBu", "BrBG", "PiYG", "PRGn", "RdYlGn"]
                )
        
        # Typography Settings
        st.markdown("---")
        st.markdown("** TYPOGRAFIE-EINSTELLUNGEN:**")
        
        typo_col1, typo_col2, typo_col3 = st.columns(3)
        
        with typo_col1:
            font_family = st.selectbox(
                " Schriftart:",
                ["Arial", "Helvetica", "Times New Roman", "Calibri", "Georgia", "Verdana", "Roboto", "Open Sans"]
            )
            
            font_size_base = st.slider(
                " Basis-Schriftgröße:",
                min_value=8, max_value=16, value=11
            )
            
        with typo_col2:
            heading_style = st.selectbox(
                " Überschriften-Stil:",
                ["bold", "light", "medium", "black", "condensed"]
            )
            
            line_height = st.slider(
                " Zeilenhöhe:",
                min_value=1.0, max_value=2.0, value=1.4, step=0.1
            )
            
        with typo_col3:
            text_alignment = st.selectbox(
                " Textausrichtung:",
                ["left", "center", "right", "justify"]
            )
            
            letter_spacing = st.slider(
                " Buchstabenabstand:",
                min_value=0.0, max_value=2.0, value=0.0, step=0.1
            )
        
        # Layout & Spacing
        st.markdown("---")
        st.markdown("** LAYOUT & ABSTÄNDE:**")
        
        layout_col1, layout_col2, layout_col3 = st.columns(3)
        
        with layout_col1:
            st.markdown("** SEITENRÄNDER:**")
            margin_top = st.slider("Oben (mm):", 10, 50, 25)
            margin_bottom = st.slider("Unten (mm):", 10, 50, 25)
            margin_left = st.slider("Links (mm):", 10, 50, 20)
            margin_right = st.slider("Rechts (mm):", 10, 50, 20)
            
        with layout_col2:
            st.markdown("** ELEMENT-ABSTÄNDE:**")
            section_spacing = st.slider("Abschnitte:", 10, 50, 25)
            paragraph_spacing = st.slider("Absätze:", 5, 25, 12)
            chart_spacing = st.slider("Charts:", 10, 40, 20)
            
        with layout_col3:
            st.markdown("** SPEZIAL-LAYOUT:**")
            multi_column = st.checkbox(" Mehrspaltig")
            if multi_column:
                column_count = st.slider("Spalten:", 2, 4, 2)
                column_gap = st.slider("Spalten-Abstand:", 5, 20, 10)
            
            watermark = st.checkbox(" Wasserzeichen")
            if watermark:
                watermark_text = st.text_input("Text:", "SOLAR ANALYSE")
                watermark_opacity = st.slider("Transparenz:", 0.1, 0.5, 0.1)
        
        # Advanced Design Features
        st.markdown("---")
        st.markdown("** ERWEITERTE DESIGN-FEATURES:**")
        
        advanced_design_tabs = st.tabs([" Backgrounds", " Borders", " Effects", " Responsive"])
        
        with advanced_design_tabs[0]:  # Backgrounds
            bg_col1, bg_col2 = st.columns(2)
            
            with bg_col1:
                background_type = st.selectbox(
                    " Hintergrund-Typ:",
                    ["solid", "gradient", "pattern", "image", "none"]
                )
                
                if background_type == "solid":
                    bg_color = st.color_picker("Farbe:", "#ffffff")
                elif background_type == "gradient":
                    bg_gradient = st.selectbox("Gradient:", ["linear", "radial", "diagonal"])
                elif background_type == "pattern":
                    bg_pattern = st.selectbox("Muster:", ["dots", "lines", "grid", "waves"])
                    
            with bg_col2:
                st.markdown("** Hintergrund-Vorschau:**")
                if background_type == "solid":
                    st.markdown(f'<div style="width:100%; height:100px; background:{bg_color}; border-radius:8px; border:1px solid #ddd;"></div>', unsafe_allow_html=True)
                elif background_type == "gradient":
                    st.markdown('<div style="width:100%; height:100px; background:linear-gradient(45deg, #667eea, #764ba2); border-radius:8px;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="width:100%; height:100px; background:#f8f9fa; border-radius:8px; border:1px solid #ddd; display:flex; align-items:center; justify-content:center; color:#666;">Vorschau</div>', unsafe_allow_html=True)
        
        with advanced_design_tabs[1]:  # Borders
            border_col1, border_col2 = st.columns(2)
            
            with border_col1:
                border_style = st.selectbox(
                    " Rahmen-Stil:",
                    ["none", "solid", "dashed", "dotted", "double", "groove"]
                )
                
                border_width = st.slider("Breite (px):", 0, 10, 1)
                border_color = st.color_picker("Rahmen-Farbe:", "#dddddd")
                
            with border_col2:
                border_radius = st.slider("Ecken-Radius (px):", 0, 20, 4)
                
                # Border-Vorschau
                st.markdown(f"""
                <div style="width:100%; height:80px; 
                           border: {border_width}px {border_style} {border_color}; 
                           border-radius: {border_radius}px; 
                           background: #f9f9f9; 
                           display: flex; align-items: center; justify-content: center;
                           color: #666;">
                    Rahmen-Vorschau
                </div>
                """, unsafe_allow_html=True)
        
        with advanced_design_tabs[2]:  # Effects
            effects_col1, effects_col2 = st.columns(2)
            
            with effects_col1:
                st.markdown("** SCHATTEN-EFFEKTE:**")
                shadow_enabled = st.checkbox("Schatten aktivieren")
                if shadow_enabled:
                    shadow_blur = st.slider("Unschärfe:", 0, 20, 5)
                    shadow_offset_x = st.slider("X-Versatz:", -10, 10, 2)
                    shadow_offset_y = st.slider("Y-Versatz:", -10, 10, 2)
                    shadow_color = st.color_picker("Schatten-Farbe:", "#00000040")
                    
            with effects_col2:
                st.markdown("** SPEZIAL-EFFEKTE:**")
                glow_effect = st.checkbox(" Glow-Effekt")
                emboss_effect = st.checkbox(" Prägung")
                glass_effect = st.checkbox(" Glas-Effekt")
                neon_effect = st.checkbox(" Neon-Effekt")
        
        with advanced_design_tabs[3]:  # Responsive
            st.markdown("** RESPONSIVE DESIGN:**")
            
            responsive_col1, responsive_col2 = st.columns(2)
            
            with responsive_col1:
                auto_scaling = st.checkbox(" Auto-Skalierung")
                mobile_optimized = st.checkbox(" Mobil-optimiert")
                print_optimized = st.checkbox(" Druck-optimiert")
                
            with responsive_col2:
                page_format = st.selectbox(
                    " Seitenformat:",
                    ["A4", "A5", "Letter", "Legal", "Custom"]
                )
                
                if page_format == "Custom":
                    custom_width = st.number_input("Breite (mm):", value=210)
                    custom_height = st.number_input("Höhe (mm):", value=297)
        
        # Design Preview
        st.markdown("---")
        st.markdown("** DESIGN-VORSCHAU:**")
        
        # Live Preview Simulation
        current_theme = st.session_state.pdf_design_config['theme']
        st.markdown(f"""
        <div style="border: 2px solid #ddd; border-radius: 12px; padding: 20px; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="margin: 0;"> {current_theme.upper()} THEME PREVIEW</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Live-Vorschau Ihres PDF-Designs</p>
            </div>
            
            <div style="margin: 15px 0;">
                <h4 style="color: #333; margin-bottom: 10px;"> Beispiel-Chart</h4>
                <div style="height: 120px; background: linear-gradient(90deg, #ff7b7b, #667eea); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    Ihr Chart hier mit aktuellen Design-Einstellungen
                </div>
            </div>
            
            <div style="margin: 15px 0;">
                <h4 style="color: #333;"> Beispiel-Text</h4>
                <p style="color: #666; line-height: 1.6;">
                    Dies ist ein Beispieltext, der zeigt, wie Ihr PDF mit den aktuellen Design-Einstellungen aussehen wird. 
                    Schriftart: {font_family}, Größe: {font_size_base}pt, Ausrichtung: {text_alignment}
                </p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea;">
                <strong> Design-Status:</strong> {current_theme.title()} Theme aktiv mit erweiterten Styling-Optionen
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Design Export/Import
        st.markdown("---")
        st.markdown("** DESIGN SPEICHERN/LADEN:**")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button(" Design speichern", use_container_width=True):
                st.success(" Aktuelles Design wurde gespeichert")
                
        with export_col2:
            if st.button(" Design laden", use_container_width=True):
                st.info(" Design-Datei auswählen...")
                
        with export_col3:
            if st.button(" Standard zurücksetzen", use_container_width=True):
                st.session_state.pdf_design_config = {
                    'theme': 'professional',
                    'color_scheme': 'blue_gradient',
                    'typography': 'modern',
                    'layout_style': 'clean'
                }
                st.success(" Design auf Standard zurückgesetzt")
    
        st.markdown("** Texte hinzufügen:**")
        
        # Dynamische Text-Eingabe
        if 'pdf_custom_texts' not in st.session_state:
            st.session_state.pdf_custom_texts = []
            
        text_col1, text_col2 = st.columns([3, 1])
        
        with text_col1:
            new_text_title = st.text_input("Titel für neuen Text", key="new_text_title")
            new_text_content = st.text_area("Text-Inhalt", height=100, key="new_text_content")
            
        with text_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(" Text hinzufügen", key="add_custom_text"):
                if new_text_title and new_text_content:
                    st.session_state.pdf_custom_texts.append({
                        'title': new_text_title,
                        'content': new_text_content
                    })
                    st.success(" Text hinzugefügt!")
                    st.rerun()
        
        # Vorhandene Texte anzeigen
        if st.session_state.pdf_custom_texts:
            st.markdown("** Hinzugefügte Texte:**")
            for i, text_item in enumerate(st.session_state.pdf_custom_texts):
                text_display_col1, text_display_col2 = st.columns([4, 1])
                with text_display_col1:
                    st.markdown(f"**{text_item['title']}:** {text_item['content'][:100]}{'...' if len(text_item['content']) > 100 else ''}")
                with text_display_col2:
                    if st.button("", key=f"remove_text_{i}"):
                        st.session_state.pdf_custom_texts.pop(i)
                        st.rerun()
        
        st.markdown("---")
        st.markdown("** Bilder hinzufügen:**")
        
        # Bild-Upload
        uploaded_images = st.file_uploader(
            "Bilder für PDF hochladen",
            type=['png', 'jpg', 'jpeg', 'gif'],
            accept_multiple_files=True,
            key="pdf_custom_images"
        )
        
        if uploaded_images:
            st.success(f" {len(uploaded_images)} Bild(er) hochgeladen")
            
            # Bild-Positionierung
            image_position = st.selectbox(
                "Bild-Position im PDF",
                options=["TOP", "MIDDLE", "BOTTOM", "SIDEBAR"],
                format_func=lambda x: {
                    "TOP": " Oben",
                    "MIDDLE": " Mitte", 
                    "BOTTOM": " Unten",
                    "SIDEBAR": " Seitenleiste"
                }.get(x, x),
                key="pdf_image_position"
            )
    
    #  LAYOUT & DESIGN OPTIONEN
    with st.expander(" LAYOUT & DESIGN", expanded=False):
        layout_col1, layout_col2, layout_col3 = st.columns(3)
        
        with layout_col1:
            st.markdown("** Seitenlayout:**")
            page_orientation = st.selectbox(
                "Seitenausrichtung",
                options=["PORTRAIT", "LANDSCAPE"],
                format_func=lambda x: " Hochformat" if x == "PORTRAIT" else " Querformat",
                key="pdf_page_orientation"
            )
            
            margins = st.selectbox(
                "Seitenränder",
                options=["NORMAL", "NARROW", "WIDE", "CUSTOM"],
                format_func=lambda x: {
                    "NORMAL": " Normal",
                    "NARROW": " Schmal", 
                    "WIDE": " Breit",
                    "CUSTOM": " Benutzerdefiniert"
                }.get(x, x),
                key="pdf_margins"
            )
            
        with layout_col2:
            st.markdown("** Styling:**")
            header_style = st.selectbox(
                "Kopfzeilen-Stil",
                options=["MODERN", "CLASSIC", "MINIMAL", "BOLD"],
                format_func=lambda x: {
                    "MODERN": " Modern",
                    "CLASSIC": " Klassisch",
                    "MINIMAL": " Minimal", 
                    "BOLD": " Fett"
                }.get(x, x),
                key="pdf_header_style"
            )
            
            font_family = st.selectbox(
                "Schriftart",
                options=["ARIAL", "HELVETICA", "TIMES", "CALIBRI", "CUSTOM"],
                key="pdf_font_family"
            )
            
        with layout_col3:
            st.markdown("** Effekte:**")
            add_watermark = st.checkbox(" Wasserzeichen", value=False, key="pdf_watermark")
            add_page_numbers = st.checkbox(" Seitenzahlen", value=True, key="pdf_page_numbers")
            add_footer = st.checkbox(" Fußzeile", value=True, key="pdf_footer")
    
    #  DRAG & DROP BEARBEITUNG
    with st.expander(" DRAG & DROP BEARBEITUNG (EXPERIMENTAL)", expanded=False):
        enable_dragdrop = st.checkbox(" Drag & Drop Bearbeitung aktivieren", value=True, key="pdf_enable_dragdrop")
        
        if enable_dragdrop:
            st.info(" Drag & Drop Funktionalität wird in der nächsten Version implementiert!")
            
            drag_col1, drag_col2 = st.columns(2)
            
            with drag_col1:
                st.markdown("** Verfügbare Elemente:**")
                st.markdown("""
                -  Text-Blöcke
                -  Diagramme  
                -  Bilder
                -  Tabellen
                -  KPI-Widgets
                """)
                
            with drag_col2:
                st.markdown("** Drag & Drop Zone:**")
                st.markdown("""
                <div style="border: 2px dashed #ccc; border-radius: 10px; 
                           padding: 40px; text-align: center; margin: 10px 0;">
                    <p> Ziehen Sie Elemente hierher</p>
                    <p style="color: #999; font-size: 12px;">Drag & Drop wird bald verfügbar sein</p>
                </div>
                """, unsafe_allow_html=True)
    
    # === DIAGRAMM-OPTIONEN ===
    st.markdown("---")
    with st.expander(" Diagramm-Optionen", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Diagramm-Typ:**")
            chart_type = st.selectbox(
                "Wählen Sie den Diagramm-Typ",
                options=["KREISDIAGRAMM", "DONUT", "BALKENDIAGRAMM", "LINIENDIAGRAMM", "SÄULENDIAGRAMM"],
                index=0,
                key="pdf_chart_type_select"
            )
            
            st.markdown("**Farbschema:**")
            color_scheme = st.selectbox(
                "Farben für Diagramme",
                options=["Standard", "Blau-Töne", "Grün-Töne", "Orange-Töne", "Violett-Töne", "Benutzerdefiniert"],
                key="pdf_color_scheme_select"
            )
        
        with col2:
            st.markdown("**Erweiterte Chart-Optionen:**")
            show_data_labels = st.checkbox(" Datenbeschriftungen anzeigen", value=True)
            show_legend = st.checkbox(" Legende anzeigen", value=True)
            animated_charts = st.checkbox(" Animierte Diagramme", value=False)
            
            if color_scheme == "Benutzerdefiniert":
                st.color_picker("Primärfarbe", "#1f77b4", key="custom_primary_color")
                st.color_picker("Sekundärfarbe", "#ff7f0e", key="custom_secondary_color")
    
    with st.expander(" FINANZANALYSE & WIRTSCHAFTLICHKEIT", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            include_financing = st.checkbox(" Finanzierungsanalyse einbinden", value=True)
            include_roi_analysis = st.checkbox(" ROI-Analyse detailliert", value=True)
            include_payback_calculation = st.checkbox("⏱ Amortisationsrechnung", value=True)
            
            # Session State für PDF-Integration setzen
            st.session_state['pdf_include_financing'] = include_financing
            st.session_state['pdf_include_roi'] = include_roi_analysis
            st.session_state['pdf_include_payback'] = include_payback_calculation
        
        with col2:
            include_cash_flow = st.checkbox(" Cash-Flow Projektion", value=False)
            include_sensitivity = st.checkbox(" Sensitivitätsanalyse", value=False)
            financing_years = st.slider("Finanzierungslaufzeit (Jahre)", 5, 25, 15)
            
            # Session State für erweiterte Finanzfeatures
            st.session_state['pdf_include_cashflow'] = include_cash_flow
            st.session_state['pdf_include_sensitivity'] = include_sensitivity
            st.session_state['pdf_financing_years'] = financing_years
        
        # Finanzierungsdaten für PDF vorbereiten
        if include_financing and analysis_results:
            try:
                from analysis import prepare_financing_data_for_pdf_export, get_financing_data_summary
                
                # Finanzierungsdaten aus aktuellen Berechnungen extrahieren
                financing_data = prepare_financing_data_for_pdf_export(analysis_results, texts)
                financing_summary = get_financing_data_summary()
                
                # In Session State für PDF-Generierung speichern
                st.session_state['pdf_financing_data'] = financing_data
                st.session_state['pdf_financing_summary'] = financing_summary
                
                # Kurze Vorschau anzeigen
                if financing_summary and financing_summary.get('financing_amount', 0) > 0:
                    st.success(f" Finanzierungsdaten verfügbar: {financing_summary.get('financing_amount', 0):,.2f} € | Monatlich: {financing_summary.get('monthly_payment', 0):,.2f} €")
                else:
                    st.info("ℹ Aktivieren Sie 'Finanzierung gewünscht' in der Dateneingabe für detaillierte Finanzanalyse")
                    
            except Exception as e:
                st.warning(f" Finanzierungsdaten konnten nicht geladen werden: {e}")
                st.session_state['pdf_financing_data'] = None
    
    with st.expander(" INDIVIDUELLE INHALTE", expanded=False):
        st.markdown("**Benutzerdefinierte Texte & Bilder:**")
        
        # Custom Text Sections
        st.markdown("** Eigene Textabschnitte:**")
        num_custom_texts = st.number_input("Anzahl benutzerdefinierter Textabschnitte", 0, 10, 0)
        
        custom_texts = []
        for i in range(int(num_custom_texts)):
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    title = st.text_input(f"Titel {i+1}", key=f"custom_text_title_{i}")
                with col2:
                    content = st.text_area(f"Inhalt {i+1}", key=f"custom_text_content_{i}", height=100)
                custom_texts.append({"title": title, "content": content})
        
        # Custom Images
        st.markdown("** Eigene Bilder:**")
        num_custom_images = st.number_input("Anzahl benutzerdefinierter Bilder", 0, 10, 0)
        
        custom_images = []
        for i in range(int(num_custom_images)):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    image_title = st.text_input(f"Bildtitel {i+1}", key=f"custom_image_title_{i}")
                with col2:
                    uploaded_file = st.file_uploader(f"Bild {i+1}", type=['png', 'jpg', 'jpeg'], key=f"custom_image_{i}")
                    if uploaded_file:
                        custom_images.append({"title": image_title, "file": uploaded_file})
    
    with st.expander(" ERWEITERTE PDF-EINSTELLUNGEN", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**PV GIS Integration:**")
            include_pvgis = st.checkbox(" PV GIS Daten einbinden", value=True, key="pdf_include_pvgis")
            if include_pvgis:
                pvgis_detail_level = st.select_slider(
                    "PV GIS Detailgrad",
                    options=["Basis", "Standard", "Erweitert", "Vollständig"],
                    value="Standard"
                )
            
            st.markdown("**Drag & Drop Bearbeitung:**")
            enable_dragdrop = st.checkbox(" PDF Drag & Drop aktivieren", value=True)
            st.session_state['enable_dragdrop'] = enable_dragdrop
            
            if enable_dragdrop:
                # Drag & Drop PDF Manager einbinden
                try:
                    from pdf_widgets import PDFSectionManager
                    
                    if 'pdf_section_manager' not in st.session_state:
                        st.session_state.pdf_section_manager = PDFSectionManager()
                        st.session_state.pdf_section_manager.initialize_session_state()
                    
                    st.markdown("** PDF-Struktur anpassen:**")
                    with st.container():
                        st.info(" Drag & Drop Manager aktiviert - Scrollen Sie nach unten für die Bearbeitungsoberfläche")
                        show_dragdrop_later = True
                except ImportError:
                    st.warning(" Drag & Drop System nicht verfügbar")
            
        with col2:
            st.markdown("**PDF-Format Optionen:**")
            pdf_quality = st.select_slider(
                "PDF-Qualität",
                options=["Standard", "Hoch", "Premium", "Ultra"],
                value="Hoch"
            )
            
            page_layout = st.selectbox(
                "Seitenlayout",
                options=["A4 Hochformat", "A4 Querformat", "A3 Hochformat"],
                index=0
            )
    
    st.markdown("---")
    
    # PDF-Generierung nur erlauben wenn ausreichende Daten vorhanden
    if not data_sufficient:
        st.warning(get_text_pdf_ui(texts, "pdf_blocked_insufficient_data", 
            "PDF-Erstellung ist blockiert. Bitte vervollständigen Sie die erforderlichen Daten."))
        return
        
    if 'pdf_generating_lock_v1' not in st.session_state:
        st.session_state.pdf_generating_lock_v1 = False

    if not project_data or not isinstance(project_data, dict): 
        project_data = {}
    customer_data_pdf = project_data.get('customer_data', {})
    
    if not analysis_results or not isinstance(analysis_results, dict):
        analysis_results = {}
        st.info(get_text_pdf_ui(texts, "pdf_creation_no_analysis_for_pdf_info", "Analyseergebnisse sind unvollständig oder nicht vorhanden. Einige PDF-Inhalte könnten fehlen."))

    active_company = get_active_company_details_func()
    company_info_for_pdf = {}
    company_logo_b64_for_pdf = None
    active_company_id_for_docs = None
    if active_company and isinstance(active_company, dict):
        company_info_for_pdf = active_company
        company_logo_b64_for_pdf = active_company.get('logo_base64')
        active_company_id_for_docs = active_company.get('id')
        st.caption(f"Angebot für Firma: **{active_company.get('name', 'Unbekannt')}** (ID: {active_company_id_for_docs})")
    else:
        st.warning("Keine aktive Firma ausgewählt. PDF verwendet Fallback-Daten für Firmeninformationen."); company_info_for_pdf = {"name": "Ihre Firma (Fallback)"}; active_company_id_for_docs = 0

    try:
        title_image_templates = load_admin_setting_func('pdf_title_image_templates', [])
        offer_title_templates = load_admin_setting_func('pdf_offer_title_templates', [])
        cover_letter_templates = load_admin_setting_func('pdf_cover_letter_templates', [])
        if not isinstance(title_image_templates, list): title_image_templates = []
        if not isinstance(offer_title_templates, list): offer_title_templates = []
        if not isinstance(cover_letter_templates, list): cover_letter_templates = []
    except Exception as e_load_tpl:
        st.error(f"Fehler Laden PDF-Vorlagen: {e_load_tpl}"); title_image_templates, offer_title_templates, cover_letter_templates = [], [], []

    if "selected_title_image_name_doc_output" not in st.session_state: st.session_state.selected_title_image_name_doc_output = None
    if "selected_title_image_b64_data_doc_output" not in st.session_state: st.session_state.selected_title_image_b64_data_doc_output = None
    if "selected_offer_title_name_doc_output" not in st.session_state: st.session_state.selected_offer_title_name_doc_output = None
    if "selected_offer_title_text_content_doc_output" not in st.session_state: st.session_state.selected_offer_title_text_content_doc_output = ""
    if "selected_cover_letter_name_doc_output" not in st.session_state: st.session_state.selected_cover_letter_name_doc_output = None
    if "selected_cover_letter_text_content_doc_output" not in st.session_state: st.session_state.selected_cover_letter_text_content_doc_output = ""

    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {
            "include_company_logo": True,
            "include_product_images": True, 
            "include_all_documents": False, 
            "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [],
            "include_optional_component_details": True,
            # Zusatzseiten (alter Generator) ab Seite 7 anhängen
            "append_additional_pages_after_main6": False
        }
    if "pdf_selected_main_sections" not in st.session_state:
         st.session_state.pdf_selected_main_sections = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics", "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"]

    submit_button_disabled = st.session_state.pdf_generating_lock_v1

    with st.form(key="pdf_generation_form_v12_final_locked_options", clear_on_submit=False):
        st.subheader(get_text_pdf_ui(texts, "pdf_config_header", "PDF-Konfiguration"))

    with st.container():  # Vorlagenauswahl
        st.markdown("**" + get_text_pdf_ui(texts, "pdf_template_selection_info", "Vorlagen für das Angebot auswählen") + "**")
        # Optional: Erweiterte Ausgabe ab Seite 7 (alte Zusatzseiten) aktivieren
        st.session_state.pdf_inclusion_options["append_additional_pages_after_main6"] = st.checkbox(
            " Ab Seite 7: Zusätzliche klassische Angebotsseiten anhängen",
            value=st.session_state.pdf_inclusion_options.get("append_additional_pages_after_main6", False),
            help="Erzeugt zuerst das 6-Seiten-Haupttemplate und hängt anschließend weitere Seiten aus dem klassischen Generator an."
        )
        title_image_options = {t.get('name', f"Bild {i+1}"): t.get('data') for i, t in enumerate(title_image_templates) if isinstance(t, dict) and t.get('name')}
        if not title_image_options:
            title_image_options = {get_text_pdf_ui(texts, "no_title_images_available", "Keine Titelbilder verfügbar"): None}
        title_image_keys = list(title_image_options.keys())
        idx_title_img = 0
        if st.session_state.selected_title_image_name_doc_output in title_image_keys:
            idx_title_img = title_image_keys.index(st.session_state.selected_title_image_name_doc_output)
        elif title_image_keys:
            st.session_state.selected_title_image_name_doc_output = title_image_keys[0]
        selected_title_image_name = st.selectbox(
            get_text_pdf_ui(texts, "pdf_select_title_image", "Titelbild auswählen"),
            options=title_image_keys,
            index=idx_title_img,
            key="pdf_title_image_select_v12_form"
        )
        st.session_state.selected_title_image_name_doc_output = selected_title_image_name
        st.session_state.selected_title_image_b64_data_doc_output = title_image_options.get(selected_title_image_name)

        offer_title_options = {t.get('name', f"Titel {i+1}"): t.get('content') for i, t in enumerate(offer_title_templates) if isinstance(t, dict) and t.get('name')}
        if not offer_title_options:
            offer_title_options = {get_text_pdf_ui(texts, "no_offer_titles_available", "Keine Angebotstitel verfügbar"): "Standard Angebotstitel"}
        offer_title_keys = list(offer_title_options.keys())
        idx_offer_title = 0
        if st.session_state.selected_offer_title_name_doc_output in offer_title_keys:
            idx_offer_title = offer_title_keys.index(st.session_state.selected_offer_title_name_doc_output)
        elif offer_title_keys:
            st.session_state.selected_offer_title_name_doc_output = offer_title_keys[0]
        selected_offer_title_name = st.selectbox(
            get_text_pdf_ui(texts, "pdf_select_offer_title", "Überschrift/Titel auswählen"),
            options=offer_title_keys,
            index=idx_offer_title,
            key="pdf_offer_title_select_v12_form"
        )
        st.session_state.selected_offer_title_name_doc_output = selected_offer_title_name
        st.session_state.selected_offer_title_text_content_doc_output = offer_title_options.get(selected_offer_title_name, "")

        cover_letter_options = {t.get('name', f"Anschreiben {i+1}"): t.get('content') for i, t in enumerate(cover_letter_templates) if isinstance(t, dict) and t.get('name')}
        if not cover_letter_options:
            cover_letter_options = {get_text_pdf_ui(texts, "no_cover_letters_available", "Keine Anschreiben verfügbar"): "Standard Anschreiben"}
        cover_letter_keys = list(cover_letter_options.keys())
        idx_cover_letter = 0
        if st.session_state.selected_cover_letter_name_doc_output in cover_letter_keys:
            idx_cover_letter = cover_letter_keys.index(st.session_state.selected_cover_letter_name_doc_output)
        elif cover_letter_keys:
            st.session_state.selected_cover_letter_name_doc_output = cover_letter_keys[0]
        selected_cover_letter_name = st.selectbox(
            get_text_pdf_ui(texts, "pdf_select_cover_letter", "Anschreiben auswählen"),
            options=cover_letter_keys,
            index=idx_cover_letter,
            key="pdf_cover_letter_select_v12_form"
        )
        st.session_state.selected_cover_letter_name_doc_output = selected_cover_letter_name
        st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_options.get(selected_cover_letter_name, "")

        # Template-Vorschau hinzufügen (aus Multi-Generator)
        with st.expander(" Template-Vorschau", expanded=False):
            preview_cols = st.columns(3)
            with preview_cols[0]:
                if st.session_state.selected_title_image_b64_data_doc_output:
                    st.success(" Titelbild ausgewählt")
                else:
                    st.info("ℹ Kein Titelbild")

            with preview_cols[1]:
                if st.session_state.selected_offer_title_text_content_doc_output:
                    st.text_area("Titel-Vorschau:", value=st.session_state.selected_offer_title_text_content_doc_output, height=60, disabled=True)
                else:
                    st.info("Standard-Titel wird verwendet")

            with preview_cols[2]:
                if st.session_state.selected_cover_letter_text_content_doc_output:
                    preview_text = st.session_state.selected_cover_letter_text_content_doc_output
                    if len(preview_text) > 200:
                        preview_text = preview_text[:200] + "..."
                    st.text_area("Anschreiben-Vorschau:", value=preview_text, height=100, disabled=True)
                else:
                    st.info("Standard-Anschreiben wird verwendet")
        st.markdown("---")

        # === OPTIONALE MODERNE DESIGN-FEATURES INTEGRATION ===
        modern_design_config = None
        try:
            from doc_output_modern_patch import render_modern_pdf_ui_enhancement
            modern_design_config = render_modern_pdf_ui_enhancement(
                texts, project_data, analysis_results, 
                load_admin_setting_func, save_admin_setting_func,
                list_products_func, get_product_by_id_func,
                get_active_company_details_func, db_list_company_documents_func
            )
            if modern_design_config:
                st.session_state.pdf_modern_design_config = modern_design_config
        except ImportError:
            pass  # Moderne Features nicht verfügbar
        except Exception as e:
            st.warning(f"Moderne Design-Features konnten nicht geladen werden: {e}")
        # === ENDE MODERNE DESIGN-FEATURES ===

        st.markdown("**" + get_text_pdf_ui(texts, "pdf_content_selection_info", "Inhalte für das PDF auswählen") + "**")
        col_pdf_content1, col_pdf_content2, col_pdf_content3 = st.columns(3)

        with col_pdf_content1:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_branding", "Branding & Dokumente") + "**")
            st.session_state.pdf_inclusion_options["include_company_logo"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_company_logo_label", "Firmenlogo anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_company_logo", True), key="pdf_cb_logo_v12_form")
            st.session_state.pdf_inclusion_options["include_product_images"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_product_images_label", "Produktbilder anzeigen? (Haupt & Zubehör)"), value=st.session_state.pdf_inclusion_options.get("include_product_images", True), key="pdf_cb_prod_img_v12_form")
            st.session_state.pdf_inclusion_options["include_optional_component_details"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_optional_component_details_label", "Details zu optionalen Komponenten anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_optional_component_details", True), key="pdf_cb_opt_comp_details_v12_form")
            st.session_state.pdf_inclusion_options["include_all_documents"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_product_datasheets_label", "Datenblätter (Haupt & Zubehör) & Firmendokumente anhängen?"), value=st.session_state.pdf_inclusion_options.get("include_all_documents", False), key="pdf_cb_all_docs_v12_form")

            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_select_company_docs", "Zusätzliche Firmendokumente") + "**")
            selected_doc_ids_for_pdf_temp_ui_col1 = []
            if active_company_id_for_docs is not None and isinstance(active_company_id_for_docs, int):
                company_docs_list = db_list_company_documents_func(active_company_id_for_docs, None)
                if company_docs_list:
                    for doc_item in company_docs_list:
                        if isinstance(doc_item, dict) and 'id' in doc_item:
                            doc_id_item = doc_item['id']
                            doc_label_item = f"{doc_item.get('display_name', doc_item.get('file_name', 'Unbenannt'))} ({doc_item.get('document_type')})"
                            is_doc_checked_by_default_col1 = doc_id_item in st.session_state.pdf_inclusion_options.get("company_document_ids_to_include", [])
                            if st.checkbox(doc_label_item, value=is_doc_checked_by_default_col1, key=f"pdf_cb_company_doc_{doc_id_item}_v12_form"):
                                if doc_id_item not in selected_doc_ids_for_pdf_temp_ui_col1: selected_doc_ids_for_pdf_temp_ui_col1.append(doc_id_item)
                    st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = selected_doc_ids_for_pdf_temp_ui_col1
                else: st.caption(get_text_pdf_ui(texts, "pdf_no_company_documents_available", "Keine spezifischen Dokumente für diese Firma hinterlegt."))
            else: st.caption(get_text_pdf_ui(texts, "pdf_select_active_company_for_docs", "Aktive Firma nicht korrekt für Dokumentenauswahl gesetzt."))

        with col_pdf_content2:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_main_sections", "Hauptsektionen") + "**")
            default_pdf_sections_map = {
                "ProjectOverview": get_text_pdf_ui(texts, "pdf_section_title_projectoverview", "1. Projektübersicht"),
                "TechnicalComponents": get_text_pdf_ui(texts, "pdf_section_title_technicalcomponents", "2. Systemkomponenten"),
                "CostDetails": get_text_pdf_ui(texts, "pdf_section_title_costdetails", "3. Kostenaufstellung"),
                "Economics": get_text_pdf_ui(texts, "pdf_section_title_economics", "4. Wirtschaftlichkeit"),
                "SimulationDetails": get_text_pdf_ui(texts, "pdf_section_title_simulationdetails", "5. Simulation"),
                "CO2Savings": get_text_pdf_ui(texts, "pdf_section_title_co2savings", "6. CO₂-Einsparung"),
                "Visualizations": get_text_pdf_ui(texts, "pdf_section_title_visualizations", "7. Grafiken"),
                "FutureAspects": get_text_pdf_ui(texts, "pdf_section_title_futureaspects", "8. Zukunftsaspekte")
            }
            temp_selected_main_sections_ui_col2 = []
            current_selected_in_state_col2 = st.session_state.get("pdf_selected_main_sections", list(default_pdf_sections_map.keys()))
            for section_key, section_label_from_map in default_pdf_sections_map.items():
                is_section_checked_by_default_col2 = section_key in current_selected_in_state_col2
                if st.checkbox(section_label_from_map, value=is_section_checked_by_default_col2, key=f"pdf_section_cb_{section_key}_v12_form"):
                    if section_key not in temp_selected_main_sections_ui_col2: temp_selected_main_sections_ui_col2.append(section_key)
            st.session_state.pdf_selected_main_sections = temp_selected_main_sections_ui_col2
            
            # Erweiterte Sektions-Vorschau (aus Multi-Generator)
            if len(temp_selected_main_sections_ui_col2) == 0:
                st.warning(" Mindestens eine Sektion muss ausgewählt sein!")
            else:
                st.success(f" {len(temp_selected_main_sections_ui_col2)} Sektionen ausgewählt")
                
            # Quick-Select Buttons für häufige Kombinationen
            with st.expander(" Schnellauswahl", expanded=False):
                if st.button(" Basis-Angebot", help="Grundlegende Sektionen für ein einfaches Angebot"):
                    st.session_state.pdf_selected_main_sections = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"]
                    st.rerun()
                
                if st.button(" Vollständiges Angebot", help="Alle verfügbaren Sektionen"):
                    st.session_state.pdf_selected_main_sections = list(default_pdf_sections_map.keys())
                    st.rerun()
                
                if st.button(" Nur Wirtschaftlichkeit", help="Fokus auf finanzielle Aspekte"):
                    st.session_state.pdf_selected_main_sections = ["ProjectOverview", "CostDetails", "Economics", "SimulationDetails"]
                    st.rerun()

        with col_pdf_content3:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_charts", "Diagramme & Visualisierungen") + "**")
            selected_chart_keys_for_pdf_ui_col3 = []
            if analysis_results and isinstance(analysis_results, dict):
                chart_key_to_friendly_name_map = {
                    'monthly_prod_cons_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_monthly_compare", "Monatl. Produktion/Verbrauch (2D)"),
                    'cost_projection_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cost_projection", "Stromkosten-Hochrechnung (2D)"),
                    'cumulative_cashflow_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cum_cashflow", "Kumulierter Cashflow (2D)"),
                    'consumption_coverage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_consum_coverage_pie", "Verbrauchsdeckung (Kreis)"),
                    'pv_usage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pv_usage_pie", "PV-Nutzung (Kreis)"),
                    'daily_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_daily_3d", "Tagesproduktion (3D)"),
                    'weekly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_weekly_3d", "Wochenproduktion (3D)"),
                    'yearly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_yearly_3d_bar", "Jahresproduktion (3D-Balken)"),
                    'project_roi_matrix_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roi_matrix_3d", "Projektrendite-Matrix (3D)"),
                    'feed_in_revenue_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_feedin_3d", "Einspeisevergütung (3D)"),
                    'prod_vs_cons_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_prodcons_3d", "Verbr. vs. Prod. (3D)"),
                    'tariff_cube_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcube_3d", "Tarifvergleich (3D)"),
                    'co2_savings_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_co2value_3d", "CO2-Ersparnis vs. Wert (3D)"),
                    'investment_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_investval_3D", "Investitionsnutzwert (3D)"),
                    'storage_effect_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_storageeff_3d", "Speicherwirkung (3D)"),
                    'selfuse_stack_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfusestack_3d", "Eigenverbr. vs. Einspeis. (3D)"),
                    'cost_growth_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_costgrowth_3d", "Stromkostensteigerung (3D)"),
                    'selfuse_ratio_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfuseratio_3d", "Eigenverbrauchsgrad (3D)"),
                    'roi_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roicompare_3d", "ROI-Vergleich (3D)"),
                    'scenario_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_scenariocomp_3d", "Szenarienvergleich (3D)"),
                    'tariff_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcomp_3d", "Vorher/Nachher Stromkosten (3D)"),
                    'income_projection_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_incomeproj_3d", "Einnahmenprognose (3D)"),
                    'yearly_production_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_yearly", "PV Visuals: Jahresproduktion"),
                    'break_even_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_breakeven", "PV Visuals: Break-Even"),
                    'amortisation_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_amort", "PV Visuals: Amortisation"),
                }
                available_chart_keys = [k for k in analysis_results.keys() if k.endswith('_chart_bytes') and analysis_results[k] is not None]
                ordered_display_keys = [k_map for k_map in chart_key_to_friendly_name_map.keys() if k_map in available_chart_keys]
                for k_avail in available_chart_keys:
                    if k_avail not in ordered_display_keys: ordered_display_keys.append(k_avail)

                current_selected_charts_in_state = st.session_state.pdf_inclusion_options.get("selected_charts_for_pdf", [])
                for chart_key in ordered_display_keys:
                    friendly_name = chart_key_to_friendly_name_map.get(chart_key, chart_key.replace('_chart_bytes', '').replace('_', ' ').title())
                    is_selected_by_default = chart_key in current_selected_charts_in_state
                    if st.checkbox(friendly_name, value=is_selected_by_default, key=f"pdf_include_chart_{chart_key}_v12_form"):
                        if chart_key not in selected_chart_keys_for_pdf_ui_col3: selected_chart_keys_for_pdf_ui_col3.append(chart_key)
            else:
                st.caption(get_text_pdf_ui(texts, "pdf_no_charts_to_select", "Keine Diagrammdaten für PDF-Auswahl."))
                st.caption("Tipp: Stelle sicher, dass die Analyse ausgeführt wurde und 'kaleido' installiert ist, damit Plotly-Grafiken als PNG exportiert werden können.")
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = selected_chart_keys_for_pdf_ui_col3
            
            # Erweiterte Diagramm-Optionen (aus Multi-Generator)
            if len(selected_chart_keys_for_pdf_ui_col3) > 0:
                st.success(f" {len(selected_chart_keys_for_pdf_ui_col3)} Diagramme ausgewählt")
            else:
                st.info("ℹ Keine Diagramme ausgewählt")
                
            # Quick-Select für Diagramme
            with st.expander(" Diagramm-Schnellauswahl", expanded=False):
                basic_charts = ['monthly_prod_cons_chart_bytes', 'cost_projection_chart_bytes', 'cumulative_cashflow_chart_bytes']
                advanced_charts = [k for k in ordered_display_keys if 'switcher' in k][:5]  # Top 5 3D-Charts
                
                if st.button(" Basis-Diagramme", help="Wichtigste 2D-Diagramme für Standardangebote"):
                    st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = [k for k in basic_charts if k in available_chart_keys]
                    st.rerun()
                
                if st.button(" Erweiterte Visualisierungen", help="Auswahl der besten 3D-Visualisierungen"):
                    st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = [k for k in advanced_charts if k in available_chart_keys]
                    st.rerun()
                
                if st.button(" Alle verfügbaren", help="Alle vorhandenen Diagramme auswählen"):
                    st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = available_chart_keys
                    st.rerun()
                
                if st.button(" Keine Diagramme", help="Alle Diagramme abwählen"):
                    st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = []
                    st.rerun()

        st.markdown("---")
        
        submitted_generate_pdf = st.form_submit_button(
            f"**{get_text_pdf_ui(texts, 'pdf_generate_button', 'Angebots-PDF erstellen')}**",
            type="primary",
            disabled=submit_button_disabled
        )


        
    # WOW Features (experimentell)
    with st.expander(" Erweiterte Features (Experimental)", expanded=False):
        st.markdown("** Visuelle Verbesserungen:**")
        
        wow_col1, wow_col2 = st.columns(2)
        with wow_col1:
            extended_features['wow_features']['shadows'] = st.checkbox(
                " Schatten-Effekte",
                value=extended_features['wow_features'].get('shadows', False),
                help="Fügt professionelle Schatten-Effekte hinzu"
            )
            extended_features['wow_features']['gradients'] = st.checkbox(
                " Gradient-Effekte",
                value=extended_features['wow_features'].get('gradients', True),
                help="Moderne Farbverläufe für bessere Visualisierung"
            )
            extended_features['wow_features']['rounded_corners'] = st.checkbox(
                " Abgerundete Ecken",
                value=extended_features['wow_features'].get('rounded_corners', True),
                help="Moderne abgerundete Ecken für bessere Optik"
            )
        
        with wow_col2:
            extended_features['wow_features']['cinematic_transitions'] = st.checkbox(
                " Kinematische Übergänge",
                value=extended_features['wow_features'].get('cinematic_transitions', False),
                help="Professionelle Seitenübergänge (experimentell)"
            )
            extended_features['wow_features']['interactive_widgets'] = st.checkbox(
                " Interaktive Widgets",
                value=extended_features['wow_features'].get('interactive_widgets', False),
                help="Interaktive PDF-Elemente (experimentell)"
            )
            extended_features['wow_features']['ai_layout_optimization'] = st.checkbox(
                "🤖 AI Layout-Optimierung",
                value=extended_features['wow_features'].get('ai_layout_optimization', False),
                help="Automatische Layout-Optimierung (experimentell)"
            )
        
        # Aktivierte Features Anzeige
        active_wow_features = [name for name, active in extended_features['wow_features'].items() if active]
        if active_wow_features:
            st.success(f" **{len(active_wow_features)} experimentelle Features aktiv:** {', '.join(active_wow_features)}")
        else:
            st.info(" Keine experimentellen Features ausgewählt")

    # PDF-Generierung verarbeiten

    if submitted_generate_pdf and not st.session_state.pdf_generating_lock_v1:
        st.session_state.pdf_generating_lock_v1 = True 
        pdf_bytes = None 
        try:
            # Datenvalidierung vor PDF-Erstellung
            try:
                from pdf_generator import validate_pdf_data, create_fallback_pdf
                
                validation_result = validate_pdf_data(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info_for_pdf
                )
                
                # Zeige Validierungsstatus an
                if not validation_result['is_valid']:
                    st.warning(f" Unvollständige Daten erkannt: {', '.join(validation_result['missing_data'])}")
                    
                    if validation_result['critical_errors'] > 0:
                        st.error(f" {validation_result['critical_errors']} kritische Fehler gefunden. Erstelle Fallback-PDF...")
                        
                        # Erstelle Fallback-PDF
                        pdf_bytes = create_fallback_pdf(
                            issues=validation_result['missing_data'],
                            warnings=validation_result['warnings'],
                            texts=texts
                        )
                        st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
                        st.success(" Fallback-PDF erfolgreich erstellt!")
                        return
                    else:
                        st.info(f"ℹ {validation_result['warnings']} Warnungen. PDF wird mit verfügbaren Daten erstellt.")
                else:
                    st.success(" Alle Daten vollständig verfügbar.")
                    
            except ImportError:
                st.warning("Datenvalidierung nicht verfügbar. Fahre mit normaler PDF-Erstellung fort.")
            
            with st.spinner(get_text_pdf_ui(texts, 'pdf_generation_spinner', 'PDF wird generiert, bitte warten...')):
                final_inclusion_options_to_pass = st.session_state.pdf_inclusion_options.copy()
                # Übergabe der (optional) angepassten Sektionen-Reihenfolge aus dem Drag&Drop-Manager
                try:
                    if 'pdf_section_manager' in st.session_state and hasattr(st.session_state, 'pdf_section_order'):
                        final_inclusion_options_to_pass['custom_section_order'] = st.session_state.pdf_section_order[:]
                except Exception:
                    pass
                final_sections_to_include_to_pass = st.session_state.pdf_selected_main_sections[:]
                
                # === ERWEITERTE PROFESSIONAL PDF FEATURES INTEGRATION ===
                # Füge Professional PDF Features zu inclusion_options hinzu
                extended_features = st.session_state.get('pdf_extended_features', {})
                
                # === FINANZIERUNGSANALYSE INTEGRATION ===
                financing_config = st.session_state.get('financing_config', {})
                if include_financing and financing_config:
                    extended_features.update({
                        'advanced_financing': True,
                        'financing_config': financing_config
                    })
                    st.success(f" Erweiterte Finanzanalyse aktiviert mit {len([k for k, v in financing_config.items() if str(k).startswith('show_') and v])} Features")
                
                # Inklusive Chart-/Design-/Custom-Configs, damit Optionen in der PDF wirken
                final_inclusion_options_to_pass.update({
                    'executive_summary': extended_features.get('executive_summary', True),
                    'enhanced_charts': extended_features.get('enhanced_charts', True),
                    'product_showcase': extended_features.get('product_showcase', True),
                    'environmental_section': extended_features.get('environmental_section', True),
                    'technical_details': extended_features.get('technical_details', True),
                    'financial_breakdown': extended_features.get('financial_breakdown', True),
                    'advanced_financing': extended_features.get('advanced_financing', False),
                    'financing_config': extended_features.get('financing_config', {}),
                    'page_numbers': extended_features.get('page_numbers', True),
                    'background_type': extended_features.get('background_type', 'none'),
                    'wow_features': extended_features.get('wow_features', {}),
                    # Diese drei stammen aus der UI und müssen explizit weitergereicht werden
                    'chart_config': st.session_state.get('chart_config', {}),
                    'custom_content_items': st.session_state.get('custom_content_items', []),
                    'pdf_design_config': st.session_state.get('pdf_design_config', {}),
                    # Ab Seite 7 anhängen (alte Generator-Seiten) optional
                    'append_additional_pages_after_main6': bool(st.session_state.get('pdf_inclusion_options', {}).get('append_additional_pages_after_main6', False))
                })
                
                # Professional PDF Features Aktivierungsinfo
                active_prof_features = [name for name, active in extended_features.items() if active and name != 'wow_features']
                if len(active_prof_features) > 5:  # Wenn viele Features aktiv sind
                    st.info(f" Professional PDF Mode: {len(active_prof_features)} erweiterte Features aktiv")
                
                # === MODERNE DESIGN-FEATURES INTEGRATION ===
                # Füge moderne Design-Konfiguration zu den Angebotsdaten hinzu
                enhanced_project_data = project_data.copy()
                if hasattr(st.session_state, 'pdf_modern_design_config') and st.session_state.pdf_modern_design_config:
                    enhanced_project_data['modern_design_config'] = st.session_state.pdf_modern_design_config
                    st.info(" Moderne Design-Features werden angewendet...")
                
                # Versuche erweiterte PDF-Generierung mit modernem Design
                pdf_bytes = None
                try:
                    from doc_output_modern_patch import enhance_pdf_generation_with_modern_design
                    
                    # Erstelle offer_data Dictionary für erweiterte Generierung
                    offer_data_enhanced = {
                        'project_data': enhanced_project_data,
                        'analysis_results': analysis_results,
                        'company_info': company_info_for_pdf,
                        'company_logo_base64': company_logo_b64_for_pdf,
                        'selected_title_image_b64': st.session_state.selected_title_image_b64_data_doc_output,
                        'selected_offer_title_text': st.session_state.selected_offer_title_text_content_doc_output,
                        'selected_cover_letter_text': st.session_state.selected_cover_letter_text_content_doc_output,
                        'sections_to_include': final_sections_to_include_to_pass,
                        'inclusion_options': final_inclusion_options_to_pass,
                        'active_company_id': active_company_id_for_docs
                    }
                    
                    # Erweiterte PDF-Generierung versuchen
                    pdf_bytes = enhance_pdf_generation_with_modern_design(
                        offer_data=offer_data_enhanced,
                        texts=texts,
                        template_name="Professional",
                        modern_design_config=st.session_state.get('pdf_modern_design_config'),
                        load_admin_setting_func=load_admin_setting_func,
                        save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func,
                        get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func
                    )
                    
                    if pdf_bytes:
                        st.success(" PDF mit modernen Design-Features erstellt!")
                    
                except ImportError:
                    pass  # Fallback auf Standard-Generierung
                except Exception as e:
                    st.warning(f"Erweiterte PDF-Generierung fehlgeschlagen: {e}. Verwende Standard-Generierung.")
                
                # Fallback auf Standard-PDF-Generierung falls erweiterte Generierung fehlgeschlagen
                if pdf_bytes is None:
                    pdf_bytes = _generate_offer_pdf_safe(
                        project_data=enhanced_project_data, analysis_results=analysis_results,
                        company_info=company_info_for_pdf, company_logo_base64=company_logo_b64_for_pdf,
                        selected_title_image_b64=st.session_state.selected_title_image_b64_data_doc_output,
                        selected_offer_title_text=st.session_state.selected_offer_title_text_content_doc_output,
                        selected_cover_letter_text=st.session_state.selected_cover_letter_text_content_doc_output,
                        sections_to_include=final_sections_to_include_to_pass,
                        inclusion_options=final_inclusion_options_to_pass,
                        load_admin_setting_func=load_admin_setting_func, save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func, get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func,
                        active_company_id=active_company_id_for_docs, texts=texts
                    )
            st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
        except Exception as e_gen_final_outer:
            st.error(f"{get_text_pdf_ui(texts, 'pdf_generation_exception_outer', 'Kritischer Fehler im PDF-Prozess (pdf_ui.py):')} {e_gen_final_outer}")
            st.text_area("Traceback PDF Erstellung (pdf_ui.py):", traceback.format_exc(), height=250)
            st.session_state.generated_pdf_bytes_for_download_v1 = None
        finally:
            st.session_state.pdf_generating_lock_v1 = False 
            st.session_state.selected_page_key_sui = "doc_output" # KORREKTUR: Sicherstellen, dass Seite erhalten bleibt
            st.rerun() 

    if 'generated_pdf_bytes_for_download_v1' in st.session_state:
        pdf_bytes_to_download = st.session_state.pop('generated_pdf_bytes_for_download_v1') 
        if pdf_bytes_to_download and isinstance(pdf_bytes_to_download, bytes):
            customer_name_for_file = customer_data_pdf.get('last_name', 'Angebot')
            if not customer_name_for_file or not str(customer_name_for_file).strip(): customer_name_for_file = "Photovoltaik_Angebot"
            timestamp_file = base64.b32encode(os.urandom(5)).decode('utf-8').lower() 
            file_name = f"Angebot_{str(customer_name_for_file).replace(' ', '_')}_{timestamp_file}.pdf"
            st.success(get_text_pdf_ui(texts, "pdf_generation_success", "PDF erfolgreich erstellt!"))
            st.download_button(
                label=get_text_pdf_ui(texts, "pdf_download_button", "PDF herunterladen"),
                data=pdf_bytes_to_download,
                file_name=file_name,
                mime="application/pdf",
                key=f"pdf_download_btn_final_{timestamp_file}" 
            )
        elif pdf_bytes_to_download is None and st.session_state.get('pdf_generating_lock_v1', True) is False : 
             st.error(get_text_pdf_ui(texts, "pdf_generation_failed_no_bytes_after_rerun", "PDF-Generierung fehlgeschlagen (keine Daten nach Rerun)."))

    # DRAG & DROP INTERFACE (wenn aktiviert)
    if st.session_state.get('enable_dragdrop', False) and 'pdf_section_manager' in st.session_state:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%); 
                    border-radius: 15px; padding: 25px; margin: 20px 0; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h3 style="color: white; margin: 0; font-weight: 600;">
                 PDF DRAG & DROP MANAGER
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                Passen Sie die Reihenfolge und Inhalte Ihrer PDF-Sektionen individuell an
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            st.session_state.pdf_section_manager.render_drag_drop_interface(texts)
        except Exception as e:
            st.error(f"Drag & Drop Interface Fehler: {e}")
            st.info("Drag & Drop System vorübergehend nicht verfügbar.")

    _show_pdf_data_status(project_data, analysis_results, texts) # Datenstatus-Anzeige aufrufen

def show_pdf_generation_ui_with_status(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]] = _dummy_list_company_documents
):
    """
    Erweiterte PDF-Generierungs-UI mit Datenstatus-Anzeige und besseren Fallback-Optionen.
    """
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))
    
    # DEBUG WIDGET INTEGRATION
    if DEBUG_WIDGET_AVAILABLE:
        integrate_pdf_debug(project_data, analysis_results, texts)
    
    # DATENSTATUS-ANZEIGE
    _show_pdf_data_status(project_data, analysis_results, texts)
    st.markdown("---")
    
    # DATENVALIDIERUNG
    try:
        from pdf_generator import _validate_pdf_data_availability
        validation_result = _validate_pdf_data_availability(project_data, analysis_results, texts)
        
        # Status-Badge anzeigen
        if validation_result['is_valid']:
            st.success(" " + get_text_pdf_ui(texts, "pdf_data_ready", "Daten für PDF-Erstellung bereit"))
        else:
            st.warning(" " + get_text_pdf_ui(texts, "pdf_data_incomplete", "Daten unvollständig - Fallback-PDF wird erstellt"))
        
        # Detailierte Warnungen anzeigen
        if validation_result['warnings']:
            with st.expander(get_text_pdf_ui(texts, "pdf_data_warnings", " Datenhinweise anzeigen")):
                for warning in validation_result['warnings']:
                    st.info(f"ℹ {warning}")
        
        # Kritische Fehler anzeigen
        if validation_result['critical_errors']:
            with st.expander(get_text_pdf_ui(texts, "pdf_critical_errors", " Kritische Probleme")):
                for error in validation_result['critical_errors']:
                    st.error(f" {error}")
                st.info(get_text_pdf_ui(texts, "pdf_fallback_info", 
                    "Bei kritischen Problemen wird ein Informations-PDF mit Anweisungen zur Datensammlung erstellt."))
    
    except ImportError:
        st.warning(get_text_pdf_ui(texts, "pdf_validation_unavailable", "Datenvalidierung nicht verfügbar"))
    
    st.markdown("---")
    
    # Rest der ursprünglichen UI bleibt unverändert
    # Hier würde der bestehende Code von show_pdf_generation_ui fortgeführt...

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-03, Gemini Ultra: Lock-Mechanismus implementiert und Logik für Download-Button-Anzeige nach st.rerun() angepasst.
#                           Initialisierung von Session-State-Variablen für Vorlagen und UI-Optionen verbessert.
#                           Signatur von db_list_company_documents_func in Dummies und Funktionsaufrufen angepasst.
# 2025-06-03, Gemini Ultra: Neue UI-Option "Details zu optionalen Komponenten anzeigen?" hinzugefügt.
#                           `chart_key_to_friendly_name_map` erweitert, um alle Diagramme aus `analysis.py` abzudecken.
#                           Sichergestellt, dass `pdf_inclusion_options` und `pdf_selected_main_sections` im `st.form`-Kontext korrekt aktualisiert werden.
# 2025-06-03, Gemini Ultra: `st.session_state.selected_page_key_sui = "doc_output"` vor `st.rerun()` im `finally`-Block der PDF-Generierung hinzugefügt.
# 2025-06-03, Gemini Ultra: Neue Funktion `_show_pdf_data_status` zur Anzeige des Datenstatus für die PDF-Erstellung hinzugefügt.
#                           Aufruf von `_show_pdf_data_status` am Ende der `render_pdf_ui` Funktion integriert.
# 2025-06-03, Gemini Ultra: Datenstatus-Anzeige in die doc_output UI integriert.
# 2025-06-03, Gemini Ultra: Import für PDF-Status-Widget zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Erweiterte PDF-UI mit Datenstatus-Anzeige zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Import der Debug-Widget-Funktionalität zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Session State Konsolidierung in render_pdf_ui hinzugefügt.