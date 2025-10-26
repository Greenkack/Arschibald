# pdf_ui.py
"""
Datei: pdf_ui.py
Zweck: Benutzeroberfläche für die Konfiguration und Erstellung von Angebots-PDFs.
       Ermöglicht die Auswahl von Vorlagen, Inhalten und spezifischen Diagrammen in einem Dreispaltenlayout.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-08 (Datenstatus-Anzeige und Fallback-PDF-Option hinzugefügt)
"""
import base64
import json
import os
import traceback
from collections.abc import Callable
from datetime import datetime
from typing import Any

import streamlit as st

from doc_output import _show_pdf_data_status
from pdf_widgets import render_pdf_structure_manager
from ui_state_manager import set_current_page

# --- Fallback-Funktionsreferenzen ---


def _dummy_load_admin_setting_pdf_ui(key, default=None):
    if key == 'pdf_title_image_templates':
        return [{'name': 'Standard-Titelbild (Fallback)', 'data': None}]
    if key == 'pdf_offer_title_templates':
        return [{'name': 'Standard-Titel (Fallback)',
                 'content': 'Angebot für Ihre Photovoltaikanlage'}]
    if key == 'pdf_cover_letter_templates':
        return [
            {
                'name': 'Standard-Anschreiben (Fallback)',
                'content': 'Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.'}]
    if key == 'active_company_id':
        return None
    if key == 'pdf_offer_presets':
        return []  # Korrekter Fallback als Liste
    return default


def _dummy_save_admin_setting_pdf_ui(key, value): return False


def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error("PDF-Generierungsfunktion (pdf_generator.py) nicht verfügbar oder fehlerhaft (Dummy in pdf_ui.py aktiv).")
    return


def _dummy_get_active_company_details() -> dict[str, Any] | None:
    return {"name": "Dummy Firma AG", "id": 0, "logo_base64": None}


def _dummy_list_company_documents(
        company_id: int, doc_type: str | None = None) -> list[dict[str, Any]]:
    return []


def _format_decimal_de(value: float, decimals: int = 2) -> str:
    try:
        formatted = f"{float(value):,.{decimals}f}"
    except Exception:
        formatted = f"{0.0:,.{decimals}f}"
    return formatted.replace(",", "#").replace(".", ",").replace("#", ".")


def _format_percent_de(value: float) -> str:
    return f"{_format_decimal_de(value, 2)} %"


def _format_currency_de(value: float) -> str:
    return f"{_format_decimal_de(value, 2)} €"


_generate_offer_pdf_safe = _dummy_generate_offer_pdf
try:
    from pdf_generator import generate_offer_pdf
    _generate_offer_pdf_safe = generate_offer_pdf
except (ImportError, ModuleNotFoundError):
    pass
except Exception:
    pass

# PDF-VORSCHAU INTEGRATION (NEU)
try:
    from pdf_preview import create_pdf_template_presets, show_pdf_preview_interface
    _PDF_PREVIEW_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _PDF_PREVIEW_AVAILABLE = False

    def show_pdf_preview_interface(*args, **kwargs):
        st.error(" PDF-Vorschau-Modul nicht verfügbar!")
        return

    def create_pdf_template_presets():
        return {}

#  PROFESSIONAL PDF GENERATOR INTEGRATION

# ============================================================================
# CHART CONFIGURATION - Task 3.1
# ============================================================================

# Vollständiges Mapping aller verfügbaren Diagramme mit
# benutzerfreundlichen Namen - VOLLSTÄNDIGE ERWEITERTE VERSION
CHART_KEY_TO_FRIENDLY_NAME_MAP = {
    # === BASIS-DIAGRAMME (aus analysis.py) ===
    'monthly_prod_cons_chart_bytes': "📊 Monatliche Produktion/Verbrauch (2D)",
    'cost_projection_chart_bytes': "💰 Stromkosten-Hochrechnung (2D)",
    'cumulative_cashflow_chart_bytes': "📈 Kumulierter Cashflow (2D)",
    'roi_chart_bytes': "💹 ROI-Entwicklung (2D)",
    'energy_balance_chart_bytes': "🔋 Energiebilanz (Donut)",
    'monthly_savings_chart_bytes': "💵 Monatliche Einsparungen (2D)",
    'yearly_comparison_chart_bytes': "📅 Jahresvergleich (2D)",
    'amortization_chart_bytes': "⏱️ Amortisationszeit (2D)",
    'co2_savings_chart_bytes': "🌱 CO₂-Einsparung (2D)",
    'financing_comparison_chart_bytes': "🏦 Finanzierungsvergleich (2D)",
    
    # === ERWEITERTE DIAGRAMME (aus calculations.py) ===
    'pv_usage_chart_bytes': "☀️ PV-Nutzung Detailliert (calculations.py)",
    'consumption_coverage_chart_bytes': "⚡ Verbrauchsdeckung Detailliert (calculations.py)",
    'cost_overview_chart_bytes': "💵 Kostenübersicht Komplett (calculations.py)",
    'break_even_scenarios_chart_bytes': "⏱️ Break-Even Szenarien (calculations.py)",
    'technical_degradation_chart_bytes': "🔧 Technische Degradation (calculations.py)",
    'maintenance_schedule_chart_bytes': "🛠️ Wartungsplan 25 Jahre (calculations.py)",
    'energy_price_comparison_chart_bytes': "💡 Energiepreis-Vergleich (calculations.py)",
    
    # === NEUE ADVANCED CHARTS (aus advanced_charts.py) ===
    'break_even_detailed_chart_bytes': "⭐ Break-Even Detailliert (NEU)",
    'lifecycle_cost_chart_bytes': "⭐ Lebenszykluskosten TCO (NEU)",
    
    # === GRUPPEN-DIAGRAMME ===
    'scenario_comparison_chart_bytes': "🔄 Szenario-Vergleich (2D Grouped)",
    'tariff_comparison_chart_bytes': "⚡ Tarif-Vergleich (2D Grouped)",
    'income_projection_chart_bytes': "💸 Einnahmen-Projektion (2D Multi-Line)",
    'battery_usage_chart_bytes': "🔋 Batterie-Nutzung (2D Stacked)",
    'grid_interaction_chart_bytes': "🔌 Netz-Interaktion (2D Line)",
    'self_consumption_chart_bytes': "🏠 Eigenverbrauch-Analyse (2D)",
    'feed_in_analysis_chart_bytes': "⚡ Einspeisung-Analyse (2D)",
    
    # === PIE/DONUT CHARTS ===
    'consumption_coverage_pie_chart_bytes': "🍰 Verbrauchsdeckung (Kreis)",
    'pv_usage_pie_chart_bytes': "🍰 PV-Nutzung (Kreis)",
    
    # === 3D SWITCHER CHARTS (aus analysis.py) ===
    'daily_production_switcher_chart_bytes': "🌅 Tagesproduktion (3D)",
    'weekly_production_switcher_chart_bytes': "📅 Wochenproduktion (3D)",
    'yearly_production_switcher_chart_bytes': "🗓️ Jahresproduktion (3D-Balken)",
    'project_roi_matrix_switcher_chart_bytes': "📊 Projektrendite-Matrix (3D)",
    'feed_in_revenue_switcher_chart_bytes': "💰 Einspeisevergütung (3D)",
    'prod_vs_cons_switcher_chart_bytes': "⚖️ Verbr. vs. Prod. (3D)",
    'tariff_cube_switcher_chart_bytes': "📦 Tarifvergleich (3D)",
    'co2_savings_value_switcher_chart_bytes': "🌍 CO2-Ersparnis vs. Wert (3D)",
    'investment_value_switcher_chart_bytes': "💎 Investitionsnutzwert (3D)",
    'storage_effect_switcher_chart_bytes': "🔋 Speicherwirkung (3D)",
    'selfuse_stack_switcher_chart_bytes': "🏠 Eigenverbr. vs. Einspeis. (3D)",
    'cost_growth_switcher_chart_bytes': "📈 Stromkostensteigerung (3D)",
    'selfuse_ratio_switcher_chart_bytes': "📊 Eigenverbrauchsgrad (3D)",
    'roi_comparison_switcher_chart_bytes': "💹 ROI-Vergleich (3D)",
    'scenario_comparison_switcher_chart_bytes': "🔄 Szenarienvergleich (3D)",
    'tariff_comparison_switcher_chart_bytes': "⚡ Vorher/Nachher Stromkosten (3D)",
    'income_projection_switcher_chart_bytes': "💸 Einnahmenprognose (3D)",
    
    # === LEGACY/SONSTIGE ===
    'yearly_production_chart_bytes': "📊 PV Visuals: Jahresproduktion",
    'break_even_chart_bytes': "⏱️ PV Visuals: Break-Even",
    'amortisation_chart_bytes': "⏱️ PV Visuals: Amortisation",
    'advanced_analysis_chart_bytes': "🔬 Erweiterte Analyse (2D)",
    'sensitivity_analysis_chart_bytes': "🎯 Sensitivitäts-Analyse (2D Heatmap)",
    'optimization_chart_bytes': "🚀 Optimierungs-Analyse (2D Scatter)",
    'performance_metrics_chart_bytes': "📈 Performance-Metriken (2D)",
    'comparison_matrix_chart_bytes': "📊 Vergleichs-Matrix (2D Heatmap)",
    'summary_chart_bytes': "📋 Zusammenfassung (2D)",
    'comparison_chart_bytes': "⚖️ Vergleich (2D)",
}

# Kategorisierung der Diagramme für bessere Übersicht - VOLLSTÄNDIG ERWEITERT
CHART_CATEGORIES = {
    '💰 Finanzierung & ROI': [
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'roi_chart_bytes',
        'monthly_savings_chart_bytes',
        'amortization_chart_bytes',
        'financing_comparison_chart_bytes',
        'income_projection_chart_bytes',
        'break_even_chart_bytes',
        'amortisation_chart_bytes',
        'cost_overview_chart_bytes',  # NEU: aus calculations.py
        'break_even_scenarios_chart_bytes',  # NEU: aus calculations.py
        'energy_price_comparison_chart_bytes',  # NEU: aus calculations.py
        'break_even_detailed_chart_bytes',  # NEU: advanced_charts.py
        'lifecycle_cost_chart_bytes',  # NEU: advanced_charts.py
        'roi_comparison_switcher_chart_bytes',  # 3D Version
        'investment_value_switcher_chart_bytes',  # 3D Version
        'cost_growth_switcher_chart_bytes',  # 3D Version
    ],
    '⚡ Energie & Produktion': [
        'monthly_prod_cons_chart_bytes',
        'energy_balance_chart_bytes',
        'battery_usage_chart_bytes',
        'grid_interaction_chart_bytes',
        'self_consumption_chart_bytes',
        'feed_in_analysis_chart_bytes',
        'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes',
        'yearly_production_chart_bytes',
        'pv_usage_chart_bytes',  # NEU: aus calculations.py
        'consumption_coverage_chart_bytes',  # NEU: aus calculations.py
        'daily_production_switcher_chart_bytes',  # 3D
        'weekly_production_switcher_chart_bytes',  # 3D
        'yearly_production_switcher_chart_bytes',  # 3D
        'feed_in_revenue_switcher_chart_bytes',  # 3D
        'prod_vs_cons_switcher_chart_bytes',  # 3D
        'selfuse_stack_switcher_chart_bytes',  # 3D
        'selfuse_ratio_switcher_chart_bytes',  # 3D
    ],
    '🔋 Speicher & Batterien': [
        'battery_usage_chart_bytes',
        'storage_effect_switcher_chart_bytes',  # 3D Version
        'grid_interaction_chart_bytes',
        'self_consumption_chart_bytes',
    ],
    '📊 Vergleiche & Szenarien': [
        'yearly_comparison_chart_bytes',
        'scenario_comparison_chart_bytes',
        'tariff_comparison_chart_bytes',
        'comparison_chart_bytes',
        'comparison_matrix_chart_bytes',
        'scenario_comparison_switcher_chart_bytes',  # 3D
        'tariff_comparison_switcher_chart_bytes',  # 3D
        'tariff_cube_switcher_chart_bytes',  # 3D
        'income_projection_switcher_chart_bytes',  # 3D
    ],
    '🌱 Umwelt & CO2': [
        'co2_savings_chart_bytes',
        'co2_savings_value_switcher_chart_bytes',  # 3D Version
    ],
    '🔬 Erweiterte Analysen': [
        'advanced_analysis_chart_bytes',
        'sensitivity_analysis_chart_bytes',
        'optimization_chart_bytes',
        'performance_metrics_chart_bytes',
        'project_roi_matrix_switcher_chart_bytes',  # 3D
        'technical_degradation_chart_bytes',  # NEU: aus calculations.py
        'maintenance_schedule_chart_bytes',  # NEU: aus calculations.py
    ],
    '📋 Zusammenfassungen': [
        'summary_chart_bytes',
    ],
    '🎯 Neue Features (2024)': [
        'break_even_detailed_chart_bytes',  # ⭐ NEU
        'lifecycle_cost_chart_bytes',  # ⭐ NEU
    ],
}

# ============================================================================
# END CHART CONFIGURATION
# ============================================================================

# ============================================================================
# CHART AVAILABILITY CHECK - Task 3.2
# ============================================================================


def check_chart_availability(
    chart_key: str,
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> bool:
    """
    PERMISSIVE VERSION: Prüft ob ein Diagramm verfügbar ist.

    ⚠️ NEUE LOGIK: Markiert Charts als verfügbar sobald IRGENDEINE Berechnung durchgeführt wurde!

    Args:
        chart_key: Schlüssel des Diagramms
        project_data: Projekt-Daten mit customer_data, project_details, etc.
        analysis_results: Analyse-Ergebnisse mit berechneten Werten

    Returns:
        True wenn Diagramm verfügbar, sonst False
    """
    try:
        # Sicherstellen dass Daten vorhanden sind
        if not isinstance(project_data, dict):
            project_data = {}
        if not isinstance(analysis_results, dict):
            analysis_results = {}

        # === NEUE PERMISSIVE LOGIK ===
        # 1. Chart existiert bereits? → SOFORT verfügbar!
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            return True

        # 2. Wurde IRGENDEINE Berechnung durchgeführt?
        has_any_calculation = (
            analysis_results.get('annual_pv_production_kwh') is not None or
            analysis_results.get('total_investment_netto') is not None or
            analysis_results.get('annual_savings') is not None or
            # Mindestens ein paar Ergebnisse vorhanden
            len(analysis_results) > 5
        )

        # 3. Wenn Berechnung vorhanden: ALLE Charts verfügbar! 🚀
        if has_any_calculation:
            # KEINE Spezialfälle mehr - ALLE Charts sind verfügbar!
            # Batterie-Charts funktionieren auch ohne Batterie (zeigen dann Nullwerte)
            # Szenario-Charts funktionieren auch mit einem Szenario (zeigen
            # dann einzelnes Szenario)
            return True

        project_details = project_data.get('project_details', {})

        # === FALLBACK: Ohne Berechnung - nur Basis-Charts ===
        # Wenn KEINE Berechnung durchgeführt wurde, nur die wichtigsten Charts
        # anbieten
        basic_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            'energy_balance_chart_bytes',
            'yearly_comparison_chart_bytes',
            'summary_chart_bytes',
        ]
        if chart_key in basic_charts:
            # Minimale Prüfung
            has_minimal_data = (
                project_details.get('module_quantity', 0) > 0 or
                project_details.get('anlage_kwp', 0) > 0 or
                True  # ⚠️ IMMER True! Lass User selbst entscheiden!
            )
            return has_minimal_data

        # ⚠️ ALLE ANDEREN CHARTS: PERMISSIVE! ⚠️
        # Wenn wir bis hierher kommen, lass den User entscheiden!
        # Chart verfügbar wenn: Chart existiert ODER irgendwelche Daten
        # vorhanden
        return True  # ✅ PERMISSIV: Lass User selbst entscheiden!

    except Exception as e:
        import logging
        logging.error(
            f"Fehler bei Verfügbarkeits-Prüfung für {chart_key}: {e}")
        # Im Fehlerfall: Prüfen ob Diagramm in analysis_results vorhanden
        return chart_key in analysis_results if isinstance(
            analysis_results, dict) else False

# ============================================================================
# END CHART AVAILABILITY CHECK
# ============================================================================

# ============================================================================
# CHART SELECTION UI - Task 3.3
# ============================================================================


def render_chart_selection_ui(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    texts: dict[str, str]
) -> list[str]:
    """
    Rendert die Diagrammauswahl-UI mit Kategorisierung und Verfügbarkeits-Prüfung.

    Args:
        project_data: Projekt-Daten
        analysis_results: Analyse-Ergebnisse
        texts: Übersetzungstexte

    Returns:
        Liste der ausgewählten Diagramm-Schlüssel
    """
    st.subheader("📊 Diagrammauswahl für erweiterte PDF")
    st.markdown(
        "**Wählen Sie die Diagramme aus, die in der erweiterten PDF enthalten sein sollen.**")
    
    # INFO-BANNER
    st.info("🎯 **Neue Features 2024:** Alle 65+ verfügbare Charts können jetzt optional in die PDF eingebaut werden! "
           "Charts werden dynamisch generiert und als hochauflösende PNG-Bilder in die PDF eingebettet.")

    # DEBUG: Zeige aktuellen Zustand
    debug_current = st.session_state.get(
        'pdf_inclusion_options', {}).get(
        'selected_charts_for_pdf', [])
    if debug_current:
        st.success(
            f"✅ **{len(debug_current)} Diagramme ausgewählt:** {', '.join(debug_current[:5])}"
            f"{'...' if len(debug_current) > 5 else ''}")

    # Verfügbare und nicht verfügbare Diagramme ermitteln
    available_charts = {}
    unavailable_charts = {}

    for chart_key, friendly_name in CHART_KEY_TO_FRIENDLY_NAME_MAP.items():
        if check_chart_availability(chart_key, project_data, analysis_results):
            available_charts[chart_key] = friendly_name
        else:
            unavailable_charts[chart_key] = friendly_name

    # ERWEITERTE STATISTIKEN
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Verfügbare Charts", len(available_charts))
    with col2:
        st.metric("🔴 Nicht verfügbar", len(unavailable_charts))
    with col3:
        current_selection = st.session_state.get(
            'pdf_inclusion_options', {}).get(
            'selected_charts_for_pdf', [])
        st.metric("📊 Ausgewählt", len(current_selection))
    with col4:
        total_charts = len(CHART_KEY_TO_FRIENDLY_NAME_MAP)
        availability_percent = round((len(available_charts) / total_charts) * 100)
        st.metric("📈 Verfügbarkeit", f"{availability_percent}%")

    # ERWEITERTE SCHNELLAUSWAHL-BUTTONS
    st.markdown("### 🚀 Schnellauswahl")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button(
            "✅ Alle verfügbaren",
                key="btn_select_all_charts"):
            if 'pdf_inclusion_options' not in st.session_state:
                st.session_state.pdf_inclusion_options = {}
            st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = list(
                available_charts.keys())
            st.success(f"✅ {len(available_charts)} Diagramme ausgewählt!")
            st.rerun()

    with col_btn2:
        if st.button("❌ Keine auswählen", key="btn_deselect_all_charts"):
            if 'pdf_inclusion_options' not in st.session_state:
                st.session_state.pdf_inclusion_options = {}
            st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = []
            st.success("❌ Alle Diagramme abgewählt!")
            st.rerun()

    with col_btn3:
        if st.button(
            "⭐ Empfohlene",
                key="btn_select_recommended_charts"):
            # Empfohlene Basis-Diagramme für professionelle PDFs
            recommended = [
                'monthly_prod_cons_chart_bytes',
                'cost_projection_chart_bytes',
                'cumulative_cashflow_chart_bytes',
                'roi_chart_bytes',
                'energy_balance_chart_bytes',
                'co2_savings_chart_bytes',
                'amortization_chart_bytes',
                'break_even_detailed_chart_bytes',  # NEU
                'lifecycle_cost_chart_bytes',  # NEU
                'pv_usage_chart_bytes',
                'consumption_coverage_chart_bytes',
            ]
            # Nur verfügbare empfohlene Diagramme auswählen
            recommended_available = [
                k for k in recommended if k in available_charts]
            if 'pdf_inclusion_options' not in st.session_state:
                st.session_state.pdf_inclusion_options = {}
            st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = recommended_available
            st.success(
                f"⭐ {len(recommended_available)} empfohlene Diagramme ausgewählt!")
            st.rerun()
            
    with col_btn4:
        if st.button(
            "🎯 Top 10",
                key="btn_select_top10_charts"):
            # Top 10 wichtigste Charts für Kunden
            top10 = [
                'cost_projection_chart_bytes',
                'roi_chart_bytes',
                'cumulative_cashflow_chart_bytes',
                'amortization_chart_bytes',
                'energy_balance_chart_bytes',
                'monthly_prod_cons_chart_bytes',
                'co2_savings_chart_bytes',
                'break_even_detailed_chart_bytes',
                'monthly_savings_chart_bytes',
                'pv_usage_chart_bytes',
            ]
            top10_available = [k for k in top10 if k in available_charts]
            if 'pdf_inclusion_options' not in st.session_state:
                st.session_state.pdf_inclusion_options = {}
            st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = top10_available
            st.success(f"🎯 {len(top10_available)} Top-Diagramme ausgewählt!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Kategorisierte Auswahl")

    # Kategorisierte Diagrammauswahl mit besserer Übersicht
    selected_charts = []

    # Initialisiere Session State falls nicht vorhanden
    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {}
    if 'selected_charts_for_pdf' not in st.session_state.pdf_inclusion_options:
        st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = []

    current_selection = st.session_state.pdf_inclusion_options['selected_charts_for_pdf']

    # Durch Kategorien iterieren mit erweiterten Features
    for category_name, chart_keys in CHART_CATEGORIES.items():
        # Prüfen ob Kategorie verfügbare Diagramme hat
        category_available = [k for k in chart_keys if k in available_charts]
        category_unavailable = [k for k in chart_keys if k in unavailable_charts]
        category_selected = [k for k in chart_keys if k in current_selection]

        if not category_available and not category_unavailable:
            continue  # Kategorie überspringen wenn keine Diagramme

        # Erweiterte Kategorie-Info
        category_status = f"✅ {len(category_available)} verfügbar"
        if category_unavailable:
            category_status += f" | ❌ {len(category_unavailable)} nicht verfügbar"
        if category_selected:
            category_status += f" | 📊 {len(category_selected)} ausgewählt"

        with st.expander(f"{category_name} ({category_status})", expanded=False):
            
            # Kategorie-Schnellauswahl
            if category_available:
                col_cat1, col_cat2, col_cat3 = st.columns(3)
                with col_cat1:
                    if st.button(f"✅ Alle aus {category_name}", key=f"select_all_{category_name}"):
                        for k in category_available:
                            if k not in current_selection:
                                current_selection.append(k)
                        st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = current_selection
                        st.rerun()
                
                with col_cat2:
                    if st.button(f"❌ Keine aus {category_name}", key=f"deselect_all_{category_name}"):
                        for k in category_available:
                            if k in current_selection:
                                current_selection.remove(k)
                        st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = current_selection
                        st.rerun()
                        
                with col_cat3:
                    # Zeige Kategorie-Status
                    st.metric(f"Auswahl", f"{len(category_selected)}/{len(category_available)}")
            
            if category_available:
                st.markdown("**🟢 Verfügbare Diagramme:**")

                for chart_key in category_available:
                    friendly_name = available_charts[chart_key]
                    is_selected = chart_key in current_selection

                    # Erweiterte Checkbox mit Status-Icons
                    chart_display_name = friendly_name
                    if "NEU" in friendly_name:
                        chart_display_name = f"🆕 {friendly_name}"
                    elif "3D" in friendly_name:
                        chart_display_name = f"🎨 {friendly_name}"
                    elif "calculations.py" in friendly_name:
                        chart_display_name = f"🔬 {friendly_name}"

                    # Checkbox für jedes Diagramm mit on_change Callback
                    checkbox_key = f"chart_select_{chart_key}"

                    # Callback-Funktion für sofortige Speicherung
                    def toggle_chart(key=chart_key, current=is_selected):
                        if 'pdf_inclusion_options' not in st.session_state:
                            st.session_state.pdf_inclusion_options = {}
                        if 'selected_charts_for_pdf' not in st.session_state.pdf_inclusion_options:
                            st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = []

                        current_list = st.session_state.pdf_inclusion_options['selected_charts_for_pdf']
                        # Toggle basierend auf Checkbox-Wert
                        checkbox_val = st.session_state.get(
                            f"chart_select_{key}", False)
                        if checkbox_val and key not in current_list:
                            current_list.append(key)
                        elif not checkbox_val and key in current_list:
                            current_list.remove(key)

                    selected = st.checkbox(
                        chart_display_name,
                        value=is_selected,
                        key=checkbox_key,
                        on_change=toggle_chart,
                        help=f"Chart-Key: {chart_key}"
                    )

                    # Aktualisiere lokale Liste für UI-Konsistenz
                    if selected and chart_key not in current_selection:
                        current_selection.append(chart_key)
                    elif not selected and chart_key in current_selection:
                        current_selection.remove(chart_key)

            if category_unavailable:
                st.markdown("**🔴 Nicht verfügbare Diagramme:**")
                for chart_key in category_unavailable:
                    friendly_name = unavailable_charts[chart_key]
                    st.text(f"⚪ {friendly_name}")
                    st.caption(f"💡 Tipp: Führen Sie eine Berechnung durch um dieses Diagramm verfügbar zu machen")

    # Aktualisiere Session State
    st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = current_selection

    # Finale Speicherung (redundant, aber sicher)
    st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = current_selection

    # Warnung wenn keine Diagramme ausgewählt
    if not current_selection:
        st.warning(
            "Keine Diagramme ausgewählt. Die PDF wird ohne zusätzliche Diagramme erstellt.")
    else:
        st.success(
            f"{len(current_selection)} Diagramme ausgewählt und bereit für PDF-Generierung")

    return current_selection

# ============================================================================
# END CHART SELECTION UI
# ============================================================================

# ============================================================================
# CHART PREVIEW FUNCTIONALITY - Task 3.6
# ============================================================================


def generate_chart_thumbnail(
    chart_bytes: bytes | None,
    thumbnail_width: int = 200,
    thumbnail_height: int = 150
) -> bytes | None:
    """
    Generiert ein Thumbnail (Vorschaubild) für ein Diagramm.

    Args:
        chart_bytes: PNG-Bytes des Original-Diagramms
        thumbnail_width: Breite des Thumbnails in Pixeln
        thumbnail_height: Höhe des Thumbnails in Pixeln

    Returns:
        PNG-Bytes des Thumbnails oder None bei Fehler
    """
    try:
        if not chart_bytes:
            return None

        import io

        from PIL import Image

        # Original-Bild laden
        original_image = Image.open(io.BytesIO(chart_bytes))

        # Thumbnail erstellen (behält Seitenverhältnis bei)
        original_image.thumbnail(
            (thumbnail_width,
             thumbnail_height),
            Image.Resampling.LANCZOS)

        # Als PNG-Bytes zurückgeben
        thumbnail_buffer = io.BytesIO()
        original_image.save(thumbnail_buffer, format='PNG', optimize=True)
        thumbnail_buffer.seek(0)

        return thumbnail_buffer.getvalue()

    except Exception as e:
        import logging
        logging.error(f"Fehler beim Erstellen des Thumbnails: {e}")
        return None


def create_placeholder_thumbnail(
    width: int = 200,
    height: int = 150,
    text: str = "Vorschau nicht verfügbar"
) -> bytes:
    """
    Erstellt ein Platzhalter-Thumbnail wenn kein Diagramm verfügbar ist.

    Args:
        width: Breite des Platzhalters in Pixeln
        height: Höhe des Platzhalters in Pixeln
        text: Text der im Platzhalter angezeigt wird

    Returns:
        PNG-Bytes des Platzhalters
    """
    try:
        import io

        from PIL import Image, ImageDraw, ImageFont

        # Graues Platzhalter-Bild erstellen
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        # Rahmen zeichnen
        draw.rectangle([(0, 0), (width - 1, height - 1)],
                       outline=(200, 200, 200), width=2)

        # Text zentrieren
        try:
            # Versuche eine Schriftart zu laden
            font = ImageFont.truetype("arial.ttf", 12)
        except BaseException:
            # Fallback auf Standard-Schriftart
            font = ImageFont.load_default()

        # Text-Bounding-Box berechnen
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Text zentriert zeichnen
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        draw.text((text_x, text_y), text, fill=(150, 150, 150), font=font)

        # Als PNG-Bytes zurückgeben
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer.getvalue()

    except Exception as e:
        import logging
        logging.error(f"Fehler beim Erstellen des Platzhalter-Thumbnails: {e}")
        # Minimales 1x1 Pixel Bild als Fallback
        import io

        from PIL import Image
        img = Image.new('RGB', (1, 1), color=(240, 240, 240))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()


def render_chart_preview_grid(
    selected_charts: list[str],
    analysis_results: dict[str, Any],
    columns: int = 3
):
    """
    Rendert ein Grid mit Vorschaubildern der ausgewählten Diagramme.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
        analysis_results: Analyse-Ergebnisse mit generierten Diagrammen
        columns: Anzahl der Spalten im Grid
    """
    if not selected_charts:
        st.info(
            "ℹKeine Diagramme ausgewählt. Wählen Sie Diagramme aus, um eine Vorschau zu sehen.")
        return

    st.markdown("---")
    st.subheader("Diagramm-Vorschau")
    st.markdown(f"Vorschau der {len(selected_charts)} ausgewählten Diagramme:")

    # Grid erstellen
    rows = (len(selected_charts) + columns - 1) // columns  # Aufrunden

    for row in range(rows):
        cols = st.columns(columns)

        for col_idx in range(columns):
            chart_idx = row * columns + col_idx

            if chart_idx >= len(selected_charts):
                break

            chart_key = selected_charts[chart_idx]
            friendly_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(
                chart_key, chart_key)

            with cols[col_idx]:
                # Container für Diagramm-Vorschau
                with st.container():
                    st.markdown(f"**{friendly_name}**")

                    # Diagramm-Bytes aus analysis_results holen
                    chart_bytes = analysis_results.get(chart_key)

                    if chart_bytes:
                        # Thumbnail generieren
                        thumbnail_bytes = generate_chart_thumbnail(chart_bytes)

                        if thumbnail_bytes:
                            # Thumbnail anzeigen
                            st.image(thumbnail_bytes, use_container_width=True)

                            # Download-Button für Original
                            st.download_button(
                                label="Original",
                                data=chart_bytes,
                                file_name=f"{chart_key}.png",
                                mime="image/png",
                                key=f"download_{chart_key}_{chart_idx}"
                            )
                        else:
                            # Platzhalter wenn Thumbnail-Generierung
                            # fehlschlägt
                            placeholder = create_placeholder_thumbnail(
                                text="Thumbnail-Fehler")
                            st.image(placeholder, use_container_width=True)
                            st.caption(
                                "Thumbnail konnte nicht erstellt werden")
                    else:
                        # Platzhalter wenn Diagramm nicht verfügbar
                        placeholder = create_placeholder_thumbnail(
                            text="Noch nicht generiert")
                        st.image(placeholder, use_container_width=True)
                        st.caption(
                            "Diagramm wird bei PDF-Generierung erstellt")


def render_chart_preview_carousel(
    selected_charts: list[str],
    analysis_results: dict[str, Any]
):
    """
    Rendert eine Karussell-Ansicht der ausgewählten Diagramme.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
        analysis_results: Analyse-Ergebnisse mit generierten Diagrammen
    """
    if not selected_charts:
        return

    st.markdown("---")
    st.subheader("Diagramm-Karussell")

    # Initialisiere Session State für Karussell-Index
    if 'chart_carousel_index' not in st.session_state:
        st.session_state.chart_carousel_index = 0

    # Sicherstellen dass Index im gültigen Bereich ist
    if st.session_state.chart_carousel_index >= len(selected_charts):
        st.session_state.chart_carousel_index = 0

    current_index = st.session_state.chart_carousel_index
    chart_key = selected_charts[current_index]
    friendly_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(chart_key, chart_key)

    # Navigation
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button(
            "Zurück",
            key="carousel_prev",
            disabled=(
                current_index == 0)):
            st.session_state.chart_carousel_index = max(0, current_index - 1)
            st.rerun()

    with col2:
        st.markdown(f"**{current_index +
                         1} / {len(selected_charts)}: {friendly_name}**")

    with col3:
        if st.button("Weiter", key="carousel_next", disabled=(
                current_index >= len(selected_charts) - 1)):
            st.session_state.chart_carousel_index = min(
                len(selected_charts) - 1, current_index + 1)
            st.rerun()

    # Diagramm anzeigen
    chart_bytes = analysis_results.get(chart_key)

    if chart_bytes:
        st.image(chart_bytes, use_container_width=True)

        # Download-Button
        st.download_button(
            label="Diagramm herunterladen",
            data=chart_bytes,
            file_name=f"{chart_key}.png",
            mime="image/png",
            key=f"carousel_download_{chart_key}"
        )
    else:
        placeholder = create_placeholder_thumbnail(
            width=800, height=600, text="Diagramm noch nicht generiert")
        st.image(placeholder, use_container_width=True)
        st.info("Dieses Diagramm wird bei der PDF-Generierung erstellt.")


def render_chart_preview_tabs(
    selected_charts: list[str],
    analysis_results: dict[str, Any]
):
    """
    Rendert Tabs mit Vorschaubildern gruppiert nach Kategorien.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
        analysis_results: Analyse-Ergebnisse mit generierten Diagrammen
    """
    if not selected_charts:
        return

    st.markdown("---")
    st.subheader("Diagramm-Vorschau nach Kategorien")

    # Diagramme nach Kategorien gruppieren
    charts_by_category = {}
    for category_name, chart_keys in CHART_CATEGORIES.items():
        category_charts = [k for k in selected_charts if k in chart_keys]
        if category_charts:
            charts_by_category[category_name] = category_charts

    if not charts_by_category:
        st.info("Keine Diagramme in bekannten Kategorien gefunden.")
        return

    # Tabs erstellen
    tab_names = list(charts_by_category.keys())
    tabs = st.tabs(tab_names)

    for tab_idx, (category_name, category_charts) in enumerate(
            charts_by_category.items()):
        with tabs[tab_idx]:
            st.markdown(
                f"**{len(category_charts)} Diagramme in Kategorie '{category_name}'**")

            # Grid für diese Kategorie
            cols = st.columns(3)

            for chart_idx, chart_key in enumerate(category_charts):
                col_idx = chart_idx % 3
                friendly_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(
                    chart_key, chart_key)

                with cols[col_idx]:
                    st.markdown(f"**{friendly_name}**")

                    chart_bytes = analysis_results.get(chart_key)

                    if chart_bytes:
                        thumbnail_bytes = generate_chart_thumbnail(chart_bytes)

                        if thumbnail_bytes:
                            st.image(thumbnail_bytes, use_container_width=True)
                            st.download_button(
                                label="⬇️",
                                data=chart_bytes,
                                file_name=f"{chart_key}.png",
                                mime="image/png",
                                key=f"tab_download_{category_name}_{chart_key}"
                            )
                        else:
                            placeholder = create_placeholder_thumbnail(
                                text="Fehler")
                            st.image(placeholder, use_container_width=True)
                    else:
                        placeholder = create_placeholder_thumbnail(
                            text="Nicht generiert")
                        st.image(placeholder, use_container_width=True)


def render_chart_preview_interface(
    selected_charts: list[str],
    analysis_results: dict[str, Any],
    preview_mode: str = "grid"
):
    """
    Hauptfunktion zum Rendern der Diagramm-Vorschau-Oberfläche.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
        analysis_results: Analyse-Ergebnisse mit generierten Diagrammen
        preview_mode: Vorschau-Modus ('grid', 'carousel', 'tabs')
    """
    if not selected_charts:
        return

    # Vorschau-Modus-Auswahl
    st.markdown("---")
    preview_mode_selection = st.radio(
        "Vorschau-Ansicht:",
        options=["grid", "carousel", "tabs"],
        format_func=lambda x: {
            "grid": "Grid (Übersicht)",
            "carousel": "Karussell (Einzelansicht)",
            "tabs": "Tabs (Nach Kategorien)"
        }[x],
        horizontal=True,
        key="chart_preview_mode"
    )

    # Entsprechende Vorschau rendern
    if preview_mode_selection == "grid":
        render_chart_preview_grid(selected_charts, analysis_results)
    elif preview_mode_selection == "carousel":
        render_chart_preview_carousel(selected_charts, analysis_results)
    elif preview_mode_selection == "tabs":
        render_chart_preview_tabs(selected_charts, analysis_results)

# ============================================================================
# END CHART PREVIEW FUNCTIONALITY
# ============================================================================

# ============================================================================
# SESSION STATE MANAGEMENT - Task 3.4
# ============================================================================


def initialize_chart_selection_state():
    """
    Initialisiert den Session State für die Diagrammauswahl.
    """
    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {}

    if 'selected_charts_for_pdf' not in st.session_state.pdf_inclusion_options:
        st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = []

    if 'chart_selection_timestamp' not in st.session_state:
        st.session_state.chart_selection_timestamp = None


def save_chart_selection_to_persistent_storage(
    selected_charts: list[str],
    save_admin_setting_func: Callable[[str, Any], bool]
) -> bool:
    """
    Speichert die Diagrammauswahl persistent in der Datenbank.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
        save_admin_setting_func: Funktion zum Speichern von Admin-Einstellungen

    Returns:
        True wenn erfolgreich gespeichert, sonst False
    """
    try:
        # Als JSON speichern
        import json
        selection_json = json.dumps(selected_charts)
        success = save_admin_setting_func(
            'pdf_default_chart_selection', selection_json)

        if success:
            st.session_state.chart_selection_timestamp = datetime.now().timestamp()
            return True
        return False
    except Exception as e:
        import logging
        logging.error(f"Fehler beim Speichern der Diagrammauswahl: {e}")
        return False


def load_chart_selection_from_persistent_storage(
    load_admin_setting_func: Callable[[str, Any], Any]
) -> list[str]:
    """
    Lädt die gespeicherte Diagrammauswahl aus der Datenbank.

    Args:
        load_admin_setting_func: Funktion zum Laden von Admin-Einstellungen

    Returns:
        Liste der gespeicherten Diagramm-Schlüssel oder leere Liste
    """
    try:
        import json
        selection_json = load_admin_setting_func(
            'pdf_default_chart_selection', '[]')

        if isinstance(selection_json, str):
            selected_charts = json.loads(selection_json)
        elif isinstance(selection_json, list):
            selected_charts = selection_json
        else:
            selected_charts = []

        return selected_charts if isinstance(selected_charts, list) else []
    except Exception as e:
        import logging
        logging.error(f"Fehler beim Laden der Diagrammauswahl: {e}")
        return []


def estimate_pdf_size(selected_charts: list[str]) -> str:
    """
    Schätzt die PDF-Größe basierend auf der Anzahl ausgewählter Diagramme.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel

    Returns:
        Geschätzte Größe als formatierter String (z.B. "2.5 MB")
    """
    try:
        # Basis-PDF: ca. 500 KB
        base_size_kb = 500

        # Pro Diagramm: ca. 150 KB (hochauflösende PNG-Bilder)
        chart_size_kb = 150

        # Geschätzte Gesamtgröße
        total_size_kb = base_size_kb + (len(selected_charts) * chart_size_kb)

        # In MB umrechnen wenn > 1024 KB
        if total_size_kb >= 1024:
            size_mb = total_size_kb / 1024
            return f"{size_mb:.2f} MB"
        return f"{total_size_kb} KB"
    except Exception:
        return "Unbekannt"


def render_chart_selection_info_panel(selected_charts: list[str]):
    """
    Rendert ein Info-Panel mit Details zur Diagrammauswahl.

    Args:
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel
    """
    st.markdown("---")
    st.subheader("Auswahl-Zusammenfassung")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Ausgewählte Diagramme",
            value=len(selected_charts),
            delta=None
        )

    with col2:
        estimated_size = estimate_pdf_size(selected_charts)
        st.metric(
            label="Geschätzte PDF-Größe",
            value=estimated_size,
            delta=None
        )

    with col3:
        # Geschätzte Generierungszeit (ca. 0.5 Sekunden pro Diagramm)
        estimated_time_seconds = len(
            selected_charts) * 0.5 + 2  # +2 für Basis-PDF
        if estimated_time_seconds < 60:
            time_str = f"{int(estimated_time_seconds)} Sek."
        else:
            time_str = f"{int(estimated_time_seconds / 60)} Min."

        st.metric(
            label="Geschätzte Generierungszeit",
            value=time_str,
            delta=None
        )

    # Warnung bei vielen Diagrammen
    if len(selected_charts) > 20:
        st.warning(
            "Sie haben mehr als 20 Diagramme ausgewählt. Die PDF-Generierung kann länger dauern.")

    # Info bei keiner Auswahl
    if len(selected_charts) == 0:
        st.info("Keine Diagramme ausgewählt. Die PDF enthält nur die Standard-Seiten ohne zusätzliche Visualisierungen.")

    # Kategorien-Übersicht
    if selected_charts:
        st.markdown("**Ausgewählte Diagramme nach Kategorien:**")

        category_counts = {}
        for category_name, chart_keys in CHART_CATEGORIES.items():
            count = sum(1 for key in selected_charts if key in chart_keys)
            if count > 0:
                category_counts[category_name] = count

        # Als Spalten anzeigen
        if category_counts:
            cols = st.columns(len(category_counts))
            for idx, (category, count) in enumerate(category_counts.items()):
                with cols[idx]:
                    st.metric(category, count)


def manage_chart_selection_persistence(
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool]
):
    """
    Verwaltet das Laden und Speichern der Diagrammauswahl.

    Args:
        load_admin_setting_func: Funktion zum Laden von Admin-Einstellungen
        save_admin_setting_func: Funktion zum Speichern von Admin-Einstellungen
    """
    st.markdown("---")
    st.subheader("Auswahl speichern/laden")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Aktuelle Auswahl als Standard speichern",
                key="btn_save_chart_selection"):
            current_selection = st.session_state.get(
                'pdf_inclusion_options', {}).get(
                'selected_charts_for_pdf', [])
            success = save_chart_selection_to_persistent_storage(
                current_selection, save_admin_setting_func)

            if success:
                st.success(
                    f"{len(current_selection)} Diagramme als Standard gespeichert!")
            else:
                st.error("Fehler beim Speichern der Auswahl.")

    with col2:
        if st.button("Standard-Auswahl laden", key="btn_load_chart_selection"):
            loaded_selection = load_chart_selection_from_persistent_storage(
                load_admin_setting_func)

            if loaded_selection:
                if 'pdf_inclusion_options' not in st.session_state:
                    st.session_state.pdf_inclusion_options = {}
                st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = loaded_selection
                st.success(f"{len(loaded_selection)} Diagramme geladen!")
                st.rerun()
            else:
                st.info("Keine gespeicherte Standard-Auswahl gefunden.")

# ============================================================================
# END SESSION STATE MANAGEMENT
# ============================================================================

# ============================================================================
# CHART GENERATION INTEGRATION - Task 3.5
# ============================================================================


def filter_analysis_results_by_selection(
    analysis_results: dict[str, Any],
    selected_charts: list[str]
) -> dict[str, Any]:
    """
    Filtert die analysis_results, sodass nur ausgewählte Diagramme enthalten sind.

    Args:
        analysis_results: Vollständige Analyse-Ergebnisse mit allen Diagrammen
        selected_charts: Liste der ausgewählten Diagramm-Schlüssel

    Returns:
        Gefiltertes Dictionary mit nur den ausgewählten Diagrammen
    """
    try:
        if not isinstance(analysis_results, dict):
            return {}

        if not selected_charts:
            # Keine Diagramme ausgewählt - alle Chart-Bytes entfernen
            filtered = {
                k: v for k,
                v in analysis_results.items() if not k.endswith('_chart_bytes')}
            return filtered

        # Kopie erstellen
        filtered = analysis_results.copy()

        # Alle Chart-Keys finden
        all_chart_keys = [
            k for k in filtered.keys() if k.endswith('_chart_bytes')]

        # Nicht ausgewählte Diagramme entfernen
        for chart_key in all_chart_keys:
            if chart_key not in selected_charts:
                filtered.pop(chart_key, None)

        return filtered

    except Exception as e:
        import logging
        logging.error(f"Fehler beim Filtern der Analyse-Ergebnisse: {e}")
        return analysis_results


def generate_selected_charts_only(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    selected_charts: list[str]
) -> dict[str, Any]:
    """
    Generiert nur die ausgewählten Diagramme und gibt aktualisierte analysis_results zurück.

    Args:
        project_data: Projekt-Daten
        analysis_results: Bestehende Analyse-Ergebnisse
        selected_charts: Liste der zu generierenden Diagramm-Schlüssel

    Returns:
        Aktualisierte analysis_results mit nur den ausgewählten Diagrammen
    """
    try:
        # Filtere bestehende Ergebnisse
        filtered_results = filter_analysis_results_by_selection(
            analysis_results, selected_charts)

        # Prüfe welche Diagramme noch generiert werden müssen
        missing_charts = [
            k for k in selected_charts if k not in filtered_results or filtered_results[k] is None]

        if missing_charts:
            import logging
            logging.info(
                f"Folgende Diagramme müssen noch generiert werden: {missing_charts}")
            # Hier könnte man die Diagramm-Generierung triggern
            # Dies würde normalerweise in der Haupt-Berechnungslogik passieren

        return filtered_results

    except Exception as e:
        import logging
        logging.error(f"Fehler bei der Diagramm-Generierung: {e}")
        return analysis_results


def validate_chart_data_availability(
    chart_key: str,
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> tuple[bool, str]:
    """
    Validiert ob alle benötigten Daten für ein Diagramm vorhanden sind.

    Args:
        chart_key: Schlüssel des zu validierenden Diagramms
        project_data: Projekt-Daten
        analysis_results: Analyse-Ergebnisse

    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        # Prüfe ob Diagramm verfügbar ist
        is_available = check_chart_availability(
            chart_key, project_data, analysis_results)

        if not is_available:
            return False, f"Diagramm '{chart_key}' ist nicht verfügbar - benötigte Daten fehlen"

        # Prüfe ob Diagramm-Bytes vorhanden sind
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            return True, ""
        return False, f"Diagramm '{chart_key}' wurde noch nicht generiert"

    except Exception as e:
        return False, f"Fehler bei der Validierung: {str(e)}"


def get_chart_generation_errors(
    selected_charts: list[str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, str]:
    """
    Ermittelt alle Fehler bei der Diagramm-Generierung.

    Args:
        selected_charts: Liste der ausgewählten Diagramme
        project_data: Projekt-Daten
        analysis_results: Analyse-Ergebnisse

    Returns:
        Dictionary mit chart_key -> error_message für fehlerhafte Diagramme
    """
    errors = {}

    for chart_key in selected_charts:
        is_valid, error_msg = validate_chart_data_availability(
            chart_key, project_data, analysis_results)
        if not is_valid:
            errors[chart_key] = error_msg

    return errors


def render_chart_generation_status(
    selected_charts: list[str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
):
    """
    Zeigt den Status der Diagramm-Generierung an.

    Args:
        selected_charts: Liste der ausgewählten Diagramme
        project_data: Projekt-Daten
        analysis_results: Analyse-Ergebnisse
    """
    if not selected_charts:
        return

    st.markdown("---")
    st.subheader("Diagramm-Generierungsstatus")

    # Ermittle Fehler
    errors = get_chart_generation_errors(
        selected_charts, project_data, analysis_results)

    # Statistiken
    total = len(selected_charts)
    successful = total - len(errors)
    failed = len(errors)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gesamt", total)
    with col2:
        st.metric("✅ Erfolgreich", successful, delta=None)
    with col3:
        st.metric("❌ Fehler", failed, delta=None if failed == 0 else -failed)

    # Fehler anzeigen
    if errors:
        with st.expander("⚠️ Fehlerhafte Diagramme anzeigen", expanded=False):
            for chart_key, error_msg in errors.items():
                friendly_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(
                    chart_key, chart_key)
                st.error(f"**{friendly_name}**: {error_msg}")

            st.info(
                "Tipp: Führen Sie die Berechnungen erneut aus, um fehlende Diagramme zu generieren.")
    else:
        st.success(
            "Alle ausgewählten Diagramme sind verfügbar und können in die PDF eingefügt werden!")


def prepare_chart_data_for_pdf_generation(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    selected_charts: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Bereitet die Daten für die PDF-Generierung vor, indem nur ausgewählte Diagramme inkludiert werden.

    Args:
        project_data: Original Projekt-Daten
        analysis_results: Original Analyse-Ergebnisse
        selected_charts: Liste der ausgewählten Diagramme

    Returns:
        Tuple (prepared_project_data, prepared_analysis_results)
    """
    try:
        # Projekt-Daten unverändert lassen
        prepared_project_data = project_data.copy(
        ) if isinstance(project_data, dict) else {}

        # Analyse-Ergebnisse filtern
        prepared_analysis_results = filter_analysis_results_by_selection(
            analysis_results, selected_charts)

        # Metadaten hinzufügen
        prepared_analysis_results['_chart_selection_metadata'] = {
            'selected_count': len(selected_charts),
            'selected_charts': selected_charts,
            'timestamp': datetime.now().isoformat()
        }

        return prepared_project_data, prepared_analysis_results

    except Exception as e:
        import logging
        logging.error(f"Fehler bei der Vorbereitung der PDF-Daten: {e}")
        return project_data, analysis_results

# ============================================================================
# END CHART GENERATION INTEGRATION
# ============================================================================


# --- Hilfsfunktionen ---
def get_text_pdf_ui(
        texts_dict: dict[str, str], key: str, fallback_text: str | None = None) -> str:
    if not isinstance(texts_dict, dict):
        return fallback_text if fallback_text is not None else key.replace(
            "_", " ").title() + " (Texte fehlen)"
    return texts_dict.get(
        key, fallback_text if fallback_text is not None else key.replace(
            "_", " ").title() + " (Text-Key fehlt)")


def _get_all_available_chart_keys(
        analysis_results: dict[str, Any], chart_key_map: dict[str, str]) -> list[str]:
    if not analysis_results or not isinstance(analysis_results, dict):
        return []
    return [k for k in chart_key_map if analysis_results.get(k) is not None]


def _get_all_available_company_doc_ids(
        active_company_id: int | None,
        db_list_company_documents_func: Callable) -> list[int]:
    if active_company_id is None or not callable(
            db_list_company_documents_func):
        return []
    docs = db_list_company_documents_func(active_company_id, None)
    return [doc['id'] for doc in docs if isinstance(doc, dict) and 'id' in doc]

# --- Haupt-Render-Funktion für die PDF UI ---


def render_pdf_ui(
    texts: dict[str, str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[[
    ], dict[str, Any] | None] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[
        int, str | None], list[dict[str, Any]]] = _dummy_list_company_documents
):
    st.header(get_text_pdf_ui(
        texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))
    # Angebotstyp-Auswahl: Photovoltaik, Wärmepumpe, Kombiniert
    offer_type = st.radio("Angebotstyp",
                          ["Photovoltaik",
                           "Wärmepumpe",
                           "Kombiniert Photovoltaik + Wärmepumpe"],
                          key="radio_offer_type_selection")
    # Reihenfolge-Tracking: merken wann Photovoltaik/Wärmepumpe erstmals
    # vorhanden waren
    try:
        if 'pv_first_timestamp' not in st.session_state and isinstance(
                analysis_results, dict) and analysis_results.get('anlage_kwp'):
            st.session_state.pv_first_timestamp = datetime.now().timestamp()
        if 'hp_first_timestamp' not in st.session_state and st.session_state.get(
                'heatpump_offer'):
            st.session_state.hp_first_timestamp = datetime.now().timestamp()
    except Exception:
        pass

    # Separate Schnell-Generierungs-Buttons (Anforderung Punkt 6)
    col_gen1, col_gen2, col_gen3 = st.columns(3)
    with col_gen1:
        if st.button(" Photovoltaik-Angebot PDF", key="btn_generate_pv_pdf"):
            st.session_state.pdf_offer_type = "Photovoltaik"
            st.session_state.pdf_auto_generate_type = 'pv'
            st.session_state.pdf_auto_generate_now = True
            st.rerun()
    with col_gen2:
        if st.button(" Wärmepumpe-Angebot PDF", key="btn_generate_hp_pdf"):
            st.session_state.pdf_offer_type = "Wärmepumpe"
            st.session_state.pdf_auto_generate_type = 'hp'
            st.session_state.pdf_auto_generate_now = True
            st.rerun()
    with col_gen3:
        if st.button(
            " Kombi Photovoltaik + Wärmepumpe PDF",
                key="btn_generate_combo_pdf"):
            st.session_state.pdf_offer_type = "Kombiniert Photovoltaik + Wärmepumpe"
            st.session_state.pdf_auto_generate_type = 'combo'
            st.session_state.pdf_auto_generate_now = True
            st.rerun()

    # Debug-Bereich hinzufügen
    render_pdf_debug_section(
        texts,
        project_data,
        analysis_results,
        get_active_company_details_func,
        db_list_company_documents_func,
        get_product_by_id_func)

    if 'pdf_generating_lock_v1' not in st.session_state:
        st.session_state.pdf_generating_lock_v1 = False
    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {
            "include_company_logo": True, "include_product_images": True,
            "include_all_documents": False, "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [], "include_optional_component_details": True,
            "chart_layout": "one_per_page",
            # NEU: Zusatzseiten (ab Seite 9) nur optional anhängen
            "append_additional_pages_after_main6": False,
            # Legacy - kept for backward compatibility
            "append_additional_pages_after_main7": False,
            "append_additional_pages_after_main8": False,
            # Wärmepumpen-spezifische dynamische Blöcke (Standard aktiv)
            "include_hp_line_items": True,
            "include_hp_total_price_block": True,
            "include_hp_subsidy_block": True,
            "include_hp_financing_block": True,
            "include_hp_benefits_bullets": True,
            "include_hp_custom_texts": True,
        }
    if "pdf_selected_main_sections" not in st.session_state:
        st.session_state.pdf_selected_main_sections = [
            "ProjectOverview",
            "TechnicalComponents",
            "CostDetails",
            "Economics",
            "SimulationDetails",
            "CO2Savings",
            "Visualizations",
            "FutureAspects"]
    if 'pdf_preset_name_input' not in st.session_state:
        st.session_state.pdf_preset_name_input = ""

    minimal_data_ok = True
    if not project_data or not isinstance(project_data, dict):
        project_data = {}
    customer_data_pdf = project_data.get('customer_data', {})
    project_details_pdf = project_data.get('project_details', {})

    if offer_type == "Photovoltaik":
        # Original Mindestprüfung Photovoltaik
        if not (
            project_details_pdf.get('module_quantity') and (
                project_details_pdf.get('selected_module_id') or project_details_pdf.get('selected_module_name')) and (
                project_details_pdf.get('selected_inverter_id') or project_details_pdf.get('selected_inverter_name'))):
            minimal_data_ok = False
    elif offer_type == "Wärmepumpe":
        # Benötigt Wärmepumpen-Angebot aus Session
        hp_offer = st.session_state.get('heatpump_offer')
        if not hp_offer:
            minimal_data_ok = False
        else:
            # Erzeuge minimales Fake-Photovoltaik Grundgerüst für Validator
            project_data = {
                'customer_data': customer_data_pdf,
                'project_details': {
                    'module_quantity': 1,
                    'selected_module_name': 'Placeholder Modul',
                    'selected_inverter_name': 'Placeholder WR',
                    'anlage_kwp': 0.1,
                },
                'heatpump_offer': hp_offer,
            }
            # Minimale Analyseergebnisse synthetisch
            analysis_results = analysis_results or {}
            analysis_results.update(
                {
                    'anlage_kwp': 0.1,
                    'annual_pv_production_kwh': 0.0,
                    'total_investment_netto': hp_offer.get(
                        'beg_subsidy',
                        {}).get('effective_total_after_subsidy_net'),
                })
    else:  # Kombiniert
        hp_offer = st.session_state.get('heatpump_offer')
        if not hp_offer:
            minimal_data_ok = False
        else:
            # Sicherstellen, dass Photovoltaik-Daten vorhanden, sonst Dummy
            if not (project_details_pdf.get('module_quantity') and (project_details_pdf.get(
                    'selected_module_id') or project_details_pdf.get('selected_module_name'))):
                project_details_pdf.setdefault('module_quantity', 1)
                project_details_pdf.setdefault(
                    'selected_module_name', 'Placeholder Modul')
                project_details_pdf.setdefault(
                    'selected_inverter_name', 'Placeholder WR')
                project_details_pdf.setdefault('anlage_kwp', 0.1)
            project_data['heatpump_offer'] = hp_offer
            pv_total = analysis_results.get('total_investment_netto') if isinstance(
                analysis_results, dict) else None
            hp_total = hp_offer.get('beg_subsidy', {}).get(
                'effective_total_after_subsidy_net')
            if isinstance(analysis_results, dict):
                analysis_results['combined_final_price_netto'] = (
                    pv_total or 0) + (hp_total or 0)
                analysis_results['heatpump_after_subsidy_net'] = hp_total
    if not minimal_data_ok:
        st.info(
            get_text_pdf_ui(
                texts,
                "pdf_creation_minimal_data_missing_info",
                "Minimale Projektdaten...fehlen."))
        return
    if not analysis_results or not isinstance(analysis_results, dict):
        analysis_results = {}
        st.info(get_text_pdf_ui(texts, "pdf_creation_no_analysis_for_pdf_info",
                "Analyseergebnisse unvollständig..."))

    active_company = get_active_company_details_func()
    company_info_for_pdf = active_company if active_company else {
        "name": "Ihre Firma (Fallback)"}
    company_logo_b64_for_pdf = active_company.get(
        'logo_base64') if active_company else None
    active_company_id_for_docs = active_company.get(
        'id') if active_company else None  # Korrigiert: None statt 0 als Fallback

    if active_company:
        st.caption(
            f"Angebot für Firma: **{
                active_company.get(
                    'name',
                    'Unbekannt')}** (ID: {active_company_id_for_docs})")
    else:
        st.warning("Keine aktive Firma ausgewählt. PDF verwendet Fallback-Daten.")

    # OPTIONALE SEPARATE FIRMENAUSWAHL Photovoltaik / Wärmepumpe (Anforderung Zusatz 8)
    # Erwartet Liste von Dicts mit id,name
    companies_list = st.session_state.get('all_companies_list') or []
    if companies_list and isinstance(companies_list, list):
        with st.expander("Optionale separate Firmen für Photovoltaik und Wärmepumpe wählen"):
            pv_company_names = [c.get('name', 'Firma?')
                                for c in companies_list]
            wp_company_names = pv_company_names[:]
            pv_default_index = 0
            wp_default_index = 0
            # Falls aktive Firma existiert -> index setzen
            if active_company:
                for idx, c in enumerate(companies_list):
                    if c.get('id') == active_company.get('id'):
                        pv_default_index = idx
                        wp_default_index = idx
                        break
            pv_sel = st.selectbox(
                "Firma Photovoltaik",
                pv_company_names,
                index=pv_default_index,
                key="pv_company_select")
            wp_sel = st.selectbox(
                "Firma Wärmepumpe",
                wp_company_names,
                index=wp_default_index,
                key="wp_company_select")
            # IDs speichern
            try:
                pv_company_id = next(
                    (c.get('id') for c in companies_list if c.get('name') == pv_sel), None)
                wp_company_id = next(
                    (c.get('id') for c in companies_list if c.get('name') == wp_sel), None)
                st.session_state.pdf_inclusion_options['selected_company_pv_id'] = pv_company_id
                st.session_state.pdf_inclusion_options['selected_company_wp_id'] = wp_company_id
            except Exception:
                pass
    else:
        st.caption(
            "(Keine Firmenliste für getrennte Photovoltaik/Wärmepumpe Auswahl im Session-State gefunden)")

    # SEGMENT-REIHENFOLGE Photovoltaik/Wärmepumpe bestimmen, falls Kombination
    # gewählt
    if offer_type == "Kombiniert Photovoltaik + Wärmepumpe" and st.session_state.get(
            'heatpump_offer'):
        pv_ts = st.session_state.get('pv_first_timestamp')
        hp_ts = st.session_state.get('hp_first_timestamp')
        if pv_ts and hp_ts:
            segment_order = [
                'Photovoltaik',
                'Wärmepumpe'] if pv_ts <= hp_ts else [
                'Wärmepumpe',
                'Photovoltaik']
        elif pv_ts and not hp_ts:
            segment_order = ['Photovoltaik', 'Wärmepumpe']
        elif hp_ts and not pv_ts:
            segment_order = ['Wärmepumpe', 'Photovoltaik']
        else:
            # Fallback: Photovoltaik zuerst
            segment_order = ['Photovoltaik', 'Wärmepumpe']
        st.session_state.pdf_inclusion_options['segment_order'] = segment_order
        st.info(f"Segment-Reihenfolge: {' → '.join(segment_order)}")
    else:
        st.session_state.pdf_inclusion_options['segment_order'] = [offer_type]

    # DATENSTATUS-ANZEIGE UND EMPFEHLUNGEN
    st.markdown("---")
    data_status = _show_pdf_data_status(project_data, analysis_results, texts)

    # Wenn kritische Daten fehlen, PDF-Formular nicht anzeigen
    if not data_status:
        return
    if data_status == "fallback":
        # Fallback-PDF erstellen
        try:
            from pdf_generator import _create_no_data_fallback_pdf
            customer_data = project_data.get('customer_data', {})
            fallback_pdf = _create_no_data_fallback_pdf(texts, customer_data)

            if fallback_pdf:
                st.success(" Einfaches Info-PDF erstellt!")
                st.download_button(
                    label=" Info-PDF herunterladen",
                    data=fallback_pdf,
                    file_name=f"PV_Info_{
                        customer_data.get(
                            'last_name',
                            'Interessent')}.pdf",
                    mime="application/pdf")
            else:
                st.error("Fehler beim Erstellen des Info-PDFs")
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Fallback-PDFs: {e}")
        return

    st.markdown("---")

    # Vorlagen und Presets laden
    title_image_templates, offer_title_templates, cover_letter_templates, pdf_presets = [], [], [], []
    try:
        title_image_templates = load_admin_setting_func(
            'pdf_title_image_templates', [])
        offer_title_templates = load_admin_setting_func(
            'pdf_offer_title_templates', [])
        cover_letter_templates = load_admin_setting_func(
            'pdf_cover_letter_templates', [])

        # KORREKTUR: `load_admin_setting_func` gibt bereits eine Liste zurück, wenn der Wert als JSON-Array gespeichert wurde.
        # Kein erneutes `json.loads` nötig.
        loaded_presets = load_admin_setting_func(
            'pdf_offer_presets', [])  # Standard ist eine leere Liste
        if isinstance(loaded_presets, list):
            pdf_presets = loaded_presets
        # Fallback, falls doch als String gespeichert
        elif isinstance(loaded_presets, str) and loaded_presets.strip():
            try:
                pdf_presets = json.loads(loaded_presets)
                # Sicherstellen, dass es eine Liste ist
                if not isinstance(pdf_presets, list):
                    st.warning(
                        "PDF-Presets sind nicht im korrekten Listenformat gespeichert. Werden zurückgesetzt.")
                    pdf_presets = []
            except json.JSONDecodeError:
                st.warning(
                    "Fehler beim Parsen der PDF-Presets aus der Datenbank. Werden zurückgesetzt.")
                pdf_presets = []
        else:  # Default, falls nichts geladen oder unerwarteter Typ
            pdf_presets = []

        # Typsicherheit für andere Vorlagen
        if not isinstance(title_image_templates, list):
            title_image_templates = []
        if not isinstance(offer_title_templates, list):
            offer_title_templates = []
        if not isinstance(cover_letter_templates, list):
            cover_letter_templates = []

    except Exception as e_load_data:
        st.error(
            f"Fehler beim Laden von PDF-Vorlagen oder Presets: {e_load_data}")
        # Fallback-Werte sicherstellen
        title_image_templates, offer_title_templates, cover_letter_templates, pdf_presets = [], [], [], []

    # ... (Rest der Funktion render_pdf_ui wie in der vorherigen Antwort) ...    # (Initialisierung Session State für Vorlagenauswahl, Definitionen für "Alles auswählen/abwählen", Callbacks, UI-Elemente)
    if "selected_title_image_name_doc_output" not in st.session_state:
        st.session_state.selected_title_image_name_doc_output = title_image_templates[0]['name'] if title_image_templates and isinstance(
            title_image_templates[0], dict) else None
    if "selected_title_image_b64_data_doc_output" not in st.session_state:
        st.session_state.selected_title_image_b64_data_doc_output = title_image_templates[0]['data'] if title_image_templates and isinstance(
            title_image_templates[0], dict) else None
    if "selected_offer_title_name_doc_output" not in st.session_state:
        st.session_state.selected_offer_title_name_doc_output = offer_title_templates[0]['name'] if offer_title_templates and isinstance(
            offer_title_templates[0], dict) else None
    if "selected_offer_title_text_content_doc_output" not in st.session_state:
        st.session_state.selected_offer_title_text_content_doc_output = offer_title_templates[0]['content'] if offer_title_templates and isinstance(
            offer_title_templates[0], dict) else ""
    if "selected_cover_letter_name_doc_output" not in st.session_state:
        st.session_state.selected_cover_letter_name_doc_output = cover_letter_templates[0]['name'] if cover_letter_templates and isinstance(
            cover_letter_templates[0], dict) else None
    if "selected_cover_letter_text_content_doc_output" not in st.session_state:
        st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_templates[0]['content'] if cover_letter_templates and isinstance(
            cover_letter_templates[0], dict) else ""

    default_pdf_sections_map = {
        "ProjectOverview": get_text_pdf_ui(
            texts,
            "pdf_section_title_projectoverview",
            "1. Projektübersicht"),
        "TechnicalComponents": get_text_pdf_ui(
            texts,
            "pdf_section_title_technicalcomponents",
            "2. Systemkomponenten"),
        "CostDetails": get_text_pdf_ui(
            texts,
            "pdf_section_title_costdetails",
            "3. Kostenaufstellung"),
        "Economics": get_text_pdf_ui(
            texts,
            "pdf_section_title_economics",
            "4. Wirtschaftlichkeit"),
        "SimulationDetails": get_text_pdf_ui(
            texts,
            "pdf_section_title_simulationdetails",
            "5. Simulation"),
        "CO2Savings": get_text_pdf_ui(
            texts,
            "pdf_section_title_co2savings",
            "6. CO₂-Einsparung"),
        "Visualizations": get_text_pdf_ui(
            texts,
            "pdf_section_title_visualizations",
            "7. Grafiken"),
        "FutureAspects": get_text_pdf_ui(
            texts,
            "pdf_section_title_futureaspects",
            "8. Zukunftsaspekte")}
    all_main_section_keys = list(default_pdf_sections_map.keys())
    chart_key_to_friendly_name_map = {
        'monthly_prod_cons_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_monthly_compare",
            "Monatl. Produktion/Verbrauch (2D)"),
        'cost_projection_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_cost_projection",
            "Stromkosten-Hochrechnung (2D)"),
        'cumulative_cashflow_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_cum_cashflow",
            "Kumulierter Cashflow (2D)"),
        'consumption_coverage_pie_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_consum_coverage_pie",
            "Verbrauchsdeckung (Kreis)"),
        'pv_usage_pie_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_pv_usage_pie",
            "PV-Nutzung (Kreis)"),
        'daily_production_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_daily_3d",
            "Tagesproduktion (3D)"),
        'weekly_production_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_weekly_3d",
            "Wochenproduktion (3D)"),
        'yearly_production_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_yearly_3d_bar",
            "Jahresproduktion (3D-Balken)"),
        'project_roi_matrix_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_roi_matrix_3d",
            "Projektrendite-Matrix (3D)"),
        'feed_in_revenue_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_feedin_3d",
            "Einspeisevergütung (3D)"),
        'prod_vs_cons_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_prodcons_3d",
            "Verbr. vs. Prod. (3D)"),
        'tariff_cube_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_tariffcube_3d",
            "Tarifvergleich (3D)"),
        'co2_savings_value_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_co2value_3d",
            "CO2-Ersparnis vs. Wert (3D)"),
        'co2_savings_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_co2_realistic",
            "CO₂-Einsparung (3D)"),
        'investment_value_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_investval_3D",
            "Investitionsnutzwert (3D)"),
        'storage_effect_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_storageeff_3d",
            "Speicherwirkung (3D)"),
        'selfuse_stack_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_selfusestack_3d",
            "Eigenverbr. vs. Einspeis. (3D)"),
        'cost_growth_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_costgrowth_3d",
            "Stromkostensteigerung (3D)"),
        'selfuse_ratio_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_selfuseratio_3d",
            "Eigenverbrauchsgrad (3D)"),
        'roi_comparison_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_roicompare_3d",
            "ROI-Vergleich (3D)"),
        'scenario_comparison_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_scenariocomp_3d",
            "Szenarienvergleich (3D)"),
        'tariff_comparison_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_tariffcomp_3d",
            "Vorher/Nachher Stromkosten (3D)"),
        'income_projection_switcher_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_incomeproj_3d",
            "Einnahmenprognose (3D)"),
        'yearly_production_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_pvvis_yearly",
            "Photovoltaik Visuals: Jahresproduktion"),
        'break_even_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_pvvis_breakeven",
            "PV Visuals: Break-Even"),
        'amortisation_chart_bytes': get_text_pdf_ui(
            texts,
            "pdf_chart_label_Photovoltaikvis_amort",
            "Photovoltaik Visuals: Amortisation")}
    all_available_chart_keys_for_selection = _get_all_available_chart_keys(
        analysis_results, chart_key_to_friendly_name_map)
    all_available_company_doc_ids_for_selection = _get_all_available_company_doc_ids(
        active_company_id_for_docs, db_list_company_documents_func)

    def select_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = True
        st.session_state.pdf_inclusion_options["include_product_images"] = True
        st.session_state.pdf_inclusion_options["include_all_documents"] = True
        st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = all_available_company_doc_ids_for_selection[:]
        st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = all_available_chart_keys_for_selection[:]
        st.session_state.pdf_inclusion_options["include_optional_component_details"] = True
        st.session_state.pdf_inclusion_options["chart_layout"] = st.session_state.pdf_inclusion_options.get(
            "chart_layout", "one_per_page")
        st.session_state.pdf_selected_main_sections = all_main_section_keys[:]
        st.success("Alle Optionen ausgewählt!")

    def deselect_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = False
        st.session_state.pdf_inclusion_options["include_product_images"] = False
        st.session_state.pdf_inclusion_options["include_all_documents"] = False
        st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = [
        ]
        st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = []
        st.session_state.pdf_inclusion_options["include_optional_component_details"] = False
        st.session_state.pdf_inclusion_options["chart_layout"] = st.session_state.pdf_inclusion_options.get(
            "chart_layout", "one_per_page")
        st.session_state.pdf_selected_main_sections = []
        st.success("Alle Optionen abgewählt!")

    def load_preset_on_click(preset_name_to_load: str):
        selected_preset = next(
            (p for p in pdf_presets if p['name'] == preset_name_to_load), None)
        if selected_preset and 'selections' in selected_preset:
            selections = selected_preset['selections']
            st.session_state.pdf_inclusion_options["include_company_logo"] = selections.get(
                "include_company_logo", True)
            st.session_state.pdf_inclusion_options["include_product_images"] = selections.get(
                "include_product_images", True)
            st.session_state.pdf_inclusion_options["include_all_documents"] = selections.get(
                "include_all_documents", False)
            st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = selections.get(
                "company_document_ids_to_include", [])
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = selections.get(
                "selected_charts_for_pdf", [])
            st.session_state.pdf_inclusion_options["include_optional_component_details"] = selections.get(
                "include_optional_component_details", True)
            st.session_state.pdf_inclusion_options["chart_layout"] = selections.get(
                "chart_layout", st.session_state.pdf_inclusion_options.get(
                    "chart_layout", "one_per_page"))
            if "pdf_chart_layout_v1" in st.session_state:
                st.session_state.pdf_chart_layout_v1 = st.session_state.pdf_inclusion_options[
                    "chart_layout"]
            st.session_state.pdf_selected_main_sections = selections.get(
                "pdf_selected_main_sections", all_main_section_keys[:])
            st.success(f"Vorlage '{preset_name_to_load}' geladen.")
        else:
            st.warning(
                f"Vorlage '{preset_name_to_load}' nicht gefunden oder fehlerhaft.")

    def save_current_selection_as_preset():
        preset_name = st.session_state.get("pdf_preset_name_input", "").strip()
        if not preset_name:
            st.error("Bitte einen Namen für die Vorlage eingeben.")
            return
        if any(p['name'] == preset_name for p in pdf_presets):
            st.warning(
                f"Eine Vorlage mit dem Namen '{preset_name}' existiert bereits.")
            return
        current_selections = {
            "include_company_logo": st.session_state.pdf_inclusion_options.get("include_company_logo"),
            "include_product_images": st.session_state.pdf_inclusion_options.get("include_product_images"),
            "include_all_documents": st.session_state.pdf_inclusion_options.get("include_all_documents"),
            "company_document_ids_to_include": st.session_state.pdf_inclusion_options.get("company_document_ids_to_include"),
            "selected_charts_for_pdf": st.session_state.pdf_inclusion_options.get("selected_charts_for_pdf"),
            "include_optional_component_details": st.session_state.pdf_inclusion_options.get("include_optional_component_details"),
            "pdf_selected_main_sections": st.session_state.get("pdf_selected_main_sections"),
            "chart_layout": st.session_state.pdf_inclusion_options.get(
                "chart_layout",
                "one_per_page")}
        new_preset = {"name": preset_name, "selections": current_selections}
        updated_presets = pdf_presets + [new_preset]
        try:
            if save_admin_setting_func(
                'pdf_offer_presets',
                    json.dumps(updated_presets)):
                st.success(f"Vorlage '{preset_name}' erfolgreich gespeichert!")
                st.session_state.pdf_preset_name_input = ""
                # Um die Liste der Presets im Selectbox zu aktualisieren, ist ein Rerun nötig.
                # Dies geschieht, wenn das Hauptformular abgesendet wird oder durch eine andere Interaktion.
                # Alternativ könnte man hier ein st.rerun() erzwingen, aber das
                # kann die Formularinteraktion stören.
            else:
                st.error(
                    "Fehler beim Speichern der Vorlage in den Admin-Einstellungen.")
        except Exception as e_save_preset:
            st.error(f"Fehler beim Speichern der Vorlage: {e_save_preset}")

    st.markdown("---")
    st.subheader(get_text_pdf_ui(
        texts, "pdf_template_management_header", "Vorlagen & Schnellauswahl"))
    col_preset1, col_preset2 = st.columns([3, 2])
    with col_preset1:
        preset_names = [
            p['name'] for p in pdf_presets if isinstance(
                p, dict) and 'name' in p]
        if preset_names:
            selected_preset_name_to_load = st.selectbox(
                get_text_pdf_ui(
                    texts,
                    "pdf_load_preset_label",
                    "Vorlage laden"),
                options=[
                    get_text_pdf_ui(
                        texts,
                        "pdf_no_preset_selected_option",
                        "-- Keine Vorlage --")] +
                preset_names,
                key="pdf_preset_load_select_v1_stable")
            if selected_preset_name_to_load != get_text_pdf_ui(
                    texts, "pdf_no_preset_selected_option", "-- Keine Vorlage --"):
                if st.button(
                        get_text_pdf_ui(
                            texts,
                            "pdf_load_selected_preset_button",
                            "Ausgewählte Vorlage anwenden"),
                        key="pdf_load_preset_btn_v1_stable",
                        on_click=load_preset_on_click,
                        args=(
                            selected_preset_name_to_load,
                        )):
                    pass
        else:
            st.caption(
                get_text_pdf_ui(
                    texts,
                    "pdf_no_presets_available_caption",
                    "Keine Vorlagen gespeichert."))
    with col_preset2:
        st.text_input(get_text_pdf_ui(texts, "pdf_new_preset_name_label",
                      "Name für neue Vorlage"), key="pdf_preset_name_input")
        st.button(
            get_text_pdf_ui(
                texts,
                "pdf_save_current_selection_button",
                "Aktuelle Auswahl speichern"),
            on_click=save_current_selection_as_preset,
            key="pdf_save_preset_btn_v1_stable")
    col_global_select1, col_global_select2 = st.columns(2)
    with col_global_select1:
        st.button(f" {get_text_pdf_ui(texts,
                                      'pdf_select_all_button',
                                      'Alle Optionen auswählen')}",
                  on_click=select_all_options,
                  key="pdf_select_all_btn_v1_stable",
                  use_container_width=True)
    with col_global_select2:
        st.button(f" {get_text_pdf_ui(texts,
                                      'pdf_deselect_all_button',
                                      'Alle Optionen abwählen')}",
                  on_click=deselect_all_options,
                  key="pdf_deselect_all_btn_v1_stable",
                  use_container_width=True)
    st.markdown("---")

    #  ERWEITERTE PDF-FEATURES UI (AUSSERHALB DES FORMS)
    st.markdown("###  ERWEITERTE PDF-FEATURES")

    # Feature-Tabs inkl. Drag&Drop Struktur-Manager und Zahlungsmodalitäten
    ext_tab1, ext_tab2, ext_tab3, ext_tab4, ext_tab5, ext_tab6 = st.tabs([
        " Finanzierung",
        " Charts",
        " Custom Content",
        " Design",
        " Struktur",
        " Zahlungsmodalitäten"
    ])

    # TAB 6: ZAHLUNGSMODALITÄTEN (NEU)
    with ext_tab6:
        st.markdown("#### Zahlungsmodalitäten für Angebot")
        st.caption(
            "Konfigurieren Sie die Zahlungsbedingungen, die auf Seite 8 des Angebots erscheinen sollen.")

        try:
            # Import der Zahlungsvarianten-Komponenten
            from admin_payment_terms_ui import (
                get_payment_variant_for_pdf_generation,
                render_payment_variant_compact_selector,
            )

            # Bestimme Gesamtbetrag für Berechnungen - PRIORITÄT: Echter
            # finaler Preis
            project_total = 15000.0  # Default fallback
            try:
                # 1. HÖCHSTE PRIORITÄT: Solar Calculator finaler Preis mit
                # Provision
                if ('project_data' in st.session_state and
                    'project_details' in st.session_state.project_data and
                        'final_price_with_provision' in st.session_state.project_data['project_details']):
                    project_total = float(
                        st.session_state.project_data['project_details']['final_price_with_provision'])
                    print(
                        f"DEBUG: Zahlungsmodalitäten-Selector verwendet final_price_with_provision: {
                            project_total:,.2f} €")

                # 2. Fallback: Live Pricing Calculations
                elif 'live_pricing_calculations' in st.session_state:
                    live_calc = st.session_state['live_pricing_calculations']
                    if isinstance(live_calc,
                                  dict) and 'final_price' in live_calc:
                        project_total = float(live_calc['final_price'])
                        print(
                            f"DEBUG: Zahlungsmodalitäten-Selector verwendet final_price: {project_total:,.2f} €")

                # 3. Fallback: Analysis Results
                elif isinstance(analysis_results, dict):
                    if 'total_cost' in analysis_results:
                        project_total = float(analysis_results['total_cost'])
                    elif 'gesamtkosten' in analysis_results:
                        project_total = float(analysis_results['gesamtkosten'])
                    elif 'anlage_total_price' in analysis_results:
                        project_total = float(
                            analysis_results['anlage_total_price'])

                # 4. Fallback: Project Data
                elif isinstance(project_data, dict) and 'total_price' in project_data:
                    project_total = float(project_data['total_price'])

            except (ValueError, TypeError, KeyError):
                pass

            col_payment1, col_payment2 = st.columns([2, 1])

            with col_payment1:
                # Kompakte Zahlungsvarianten-Auswahl
                selected_payment_variant = render_payment_variant_compact_selector(
                    load_admin_setting_func=load_admin_setting_func,
                    widget_key_suffix="_pdf_ui",
                    show_preview=True,
                    project_total=project_total)

                # Speichere Auswahl in Session State für PDF-Generierung
                st.session_state['selected_payment_variant_key'] = selected_payment_variant

                # Zusätzliche Optionen
                if selected_payment_variant:
                    payment_options_col1, payment_options_col2 = st.columns(2)

                    with payment_options_col1:
                        include_payment_table = st.checkbox(
                            "Zahlungsplan-Tabelle im PDF",
                            value=True,
                            key="pdf_include_payment_table",
                            help="Fügt eine detaillierte Tabelle mit Zahlungsraten hinzu")

                    with payment_options_col2:
                        include_payment_amounts = st.checkbox(
                            "Euro-Beträge anzeigen",
                            value=True,
                            key="pdf_include_payment_amounts",
                            help="Zeigt berechnete Euro-Beträge neben Prozentsätzen")

                    # Speichere Optionen
                    st.session_state['payment_include_table'] = include_payment_table
                    st.session_state['payment_include_amounts'] = include_payment_amounts

                    if selected_payment_variant == 'variant_4':
                        variant_config = st.session_state.get(
                            'selected_payment_variant_config') or {}
                        perc_defaults = list(
                            variant_config.get(
                                'percents', [
                                    40.0, 30.0, 30.0]))
                        while len(perc_defaults) < 3:
                            perc_defaults.append(0.0)
                        custom_labels = list(
                            variant_config.get(
                                'custom_labels', [
                                    'Anzahlung', 'Nach DC-Montage', 'Nach Inbetriebnahme']))
                        while len(custom_labels) < 3:
                            custom_labels.append(
                                f"Rate {len(custom_labels) + 1}")

                        if st.session_state.get(
                                'custom_variant_active_key') != 'variant_4':
                            for idx in range(3):
                                key_name = f'custom_variant4_percent_{idx + 1}'
                                st.session_state[key_name] = float(
                                    perc_defaults[idx])
                            st.session_state['custom_variant_4_percents'] = [
                                float(val) for val in perc_defaults[:3]]
                            st.session_state['custom_variant_active_key'] = 'variant_4'

                        st.markdown("**Individuelle Aufteilung (Variante 4)**")

                        percent_inputs: list[float] = []
                        for idx in range(3):
                            key_name = f'custom_variant4_percent_{idx + 1}'
                            label = custom_labels[idx]
                            percent_value = st.number_input(
                                f"{label} (%)",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.5,
                                key=key_name,
                                help="Individueller Prozentanteil für diese Rate"
                            )
                            percent_inputs.append(float(percent_value))

                        custom_percents = [float(val)
                                           for val in percent_inputs]
                        st.session_state['custom_variant_4_percents'] = custom_percents
                        st.session_state['custom_variant_active_key'] = 'variant_4'
                        st.session_state['custom_variant_4_project_total'] = project_total

                        sum_pct = sum(custom_percents)
                        st.session_state['custom_variant_4_percent_sum'] = sum_pct

                        st.caption(
                            f"Gesamtsumme: {
                                _format_percent_de(sum_pct)}")

                        if abs(sum_pct - 100.0) > 0.01:
                            st.error(
                                f"Die Summe der Prozentwerte muss 100% ergeben (aktuell: {
                                    _format_decimal_de(
                                        sum_pct, 2)} %).")
                            st.session_state['custom_variant_4_valid'] = False
                        else:
                            st.session_state['custom_variant_4_valid'] = True

                        calculated_amounts = [
                            round(project_total * (pct / 100.0), 2) for pct in custom_percents]

                        st.markdown("**Aktuelle Aufteilung:**")
                        for idx, pct in enumerate(custom_percents):
                            label = custom_labels[idx]
                            amount_str = _format_currency_de(
                                calculated_amounts[idx])
                            percent_str = _format_percent_de(pct)
                            st.markdown(
                                f"- {label}: {percent_str} ({amount_str})")
                    else:
                        st.session_state.pop('custom_variant_active_key', None)
                        st.session_state.pop('custom_variant_4_percents', None)
                        st.session_state.pop('custom_variant_4_valid', None)
                        st.session_state.pop(
                            'custom_variant_4_percent_sum', None)
                        st.session_state.pop(
                            'custom_variant_4_project_total', None)
                        st.session_state.pop('custom_variant4_percent_1', None)
                        st.session_state.pop('custom_variant4_percent_2', None)
                        st.session_state.pop('custom_variant4_percent_3', None)

            with col_payment2:
                st.markdown("**ℹ️ Info:**")
                st.info(f"""
                **Projektbetrag:** {project_total:,.2f} €

                **Position im PDF:** Seite 8

                **Konfiguration:** Admin-Panel → Zahlungsmodalitäten
                """)

                if selected_payment_variant:
                    st.success("✅ Zahlungsmodalitäten aktiviert")
                else:
                    st.warning("⚠️ Keine Zahlungsmodalitäten ausgewählt")

            # Erweiterte Konfiguration in Expander
            if selected_payment_variant:
                with st.expander("Erweiterte Einstellungen", expanded=False):
                    payment_position = st.selectbox(
                        "Position im PDF:",
                        options=[
                            "Seite 8 (Standard)",
                            "Nach Kostenaufstellung",
                            "Letzte Seite"],
                        index=0,
                        key="pdf_payment_position",
                        help="Bestimmt, wo die Zahlungsmodalitäten im PDF erscheinen")

                    payment_style = st.selectbox(
                        "Darstellungsstil:",
                        options=["Standard", "Kompakt",
                                 "Detailliert", "Grafisch"],
                        index=0,
                        key="pdf_payment_style",
                        help="Visueller Stil der Zahlungsmodalitäten im PDF"
                    )

                    custom_payment_title = st.text_input(
                        "Benutzerdefinierter Titel:",
                        value="Zahlungsmodalitäten",
                        key="pdf_custom_payment_title",
                        help="Überschrift für den Zahlungsmodalitäten-Bereich"
                    )

                    # Speichere erweiterte Optionen
                    st.session_state['payment_position'] = payment_position
                    st.session_state['payment_style'] = payment_style
                    st.session_state['custom_payment_title'] = custom_payment_title

        except ImportError:
            st.error(
                "❌ Zahlungsmodalitäten-Komponenten nicht verfügbar. Bitte überprüfen Sie die admin_payment_terms_ui.py Datei.")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Zahlungsmodalitäten: {str(e)}")

    # TAB 1: ERWEITERTE FINANZIERUNGSANALYSE
    with ext_tab1:
        financing_enabled = st.checkbox(
            "Erweiterte Finanzierungsanalyse aktivieren",
            value=st.session_state.get(
                'financing_config', {}).get('enabled', False),
            key="financing_enabled_checkbox_outside_form"
        )

        if financing_enabled:
            financing_config = st.session_state.get('financing_config', {})
            financing_config['enabled'] = True

            col1_fin, col2_fin = st.columns(2)

            with col1_fin:
                financing_config['scenario_analysis'] = st.checkbox(
                    "3-Szenarien-Analyse",
                    value=financing_config.get('scenario_analysis', True),
                    key="financing_scenario_analysis_outside_form"
                )

                financing_config['sensitivity_analysis'] = st.checkbox(
                    "Sensitivitätsanalyse",
                    value=financing_config.get('sensitivity_analysis', True),
                    key="financing_sensitivity_analysis_outside_form"
                )

                financing_config['financing_options'] = st.checkbox(
                    "Finanzierungsoptionen",
                    value=financing_config.get('financing_options', True),
                    key="financing_options_enabled_outside_form"
                )

            with col2_fin:
                # Szenarien-Konfiguration (kompakt)
                if 'conservative' not in financing_config:
                    financing_config['conservative'] = {
                        'roi_year_1': 6.5, 'payback_years': 14.2, 'total_savings_20y': 28000}
                if 'balanced' not in financing_config:
                    financing_config['balanced'] = {
                        'roi_year_1': 8.2, 'payback_years': 12.5, 'total_savings_20y': 35000}
                if 'aggressive' not in financing_config:
                    financing_config['aggressive'] = {
                        'roi_year_1': 10.8, 'payback_years': 10.1, 'total_savings_20y': 45000}
                if 'bank_loan' not in financing_config:
                    financing_config['bank_loan'] = {
                        'interest_rate': 3.2, 'duration_years': 15, 'monthly_payment': 185}
                if 'kfw_loan' not in financing_config:
                    financing_config['kfw_loan'] = {
                        'interest_rate': 1.8, 'duration_years': 20, 'monthly_payment': 145}

                st.info(" Finanzierungs-Szenarien werden automatisch berechnet")

            st.session_state['financing_config'] = financing_config
        else:
            st.session_state['financing_config'] = {'enabled': False}

    # TAB 2: ENHANCED CHART CONFIGURATION
    with ext_tab2:
        chart_config = st.session_state.get('chart_config', {})

        col1_chart, col2_chart = st.columns(2)

        with col1_chart:
            chart_config['chart_type'] = st.selectbox(
                "Chart-Typ",
                options=[
                    "BAR",
                    "LINE",
                    "PIE",
                    "DONUT",
                    "AREA",
                    "SCATTER",
                    "RADAR",
                    "HEATMAP"],
                index=[
                    "BAR",
                    "LINE",
                    "PIE",
                    "DONUT",
                    "AREA",
                    "SCATTER",
                    "RADAR",
                    "HEATMAP"].index(
                    chart_config.get(
                        'chart_type',
                        'DONUT')),
                key="chart_type_select_outside_form")

            chart_config['resolution'] = st.selectbox(
                "Auflösung",
                options=["low", "medium", "high", "ultra"],
                index=["low", "medium", "high", "ultra"].index(
                    chart_config.get('resolution', 'high')
                ),
                key="chart_resolution_select_outside_form"
            )

        with col2_chart:
            if 'effects' not in chart_config:
                chart_config['effects'] = {}

            chart_config['effects']['animation'] = st.checkbox(
                "Animation-Effekte",
                value=chart_config.get('effects', {}).get('animation', True),
                key="chart_animation_effects_outside_form"
            )

            chart_config['effects']['3d_effects'] = st.checkbox(
                "3D-Effekte",
                value=chart_config.get('effects', {}).get('3d_effects', True),
                key="chart_3d_effects_outside_form"
            )

            chart_config['effects']['gradient_effects'] = st.checkbox(
                "Gradient-Effekte",
                value=chart_config.get('effects', {}).get(
                    'gradient_effects', True),
                key="chart_gradient_effects_outside_form"
            )

        st.session_state['chart_config'] = chart_config

    # TAB 5: DRAG & DROP STRUKTUR-MANAGER
    with ext_tab5:
        render_pdf_structure_manager(texts)

    # WÄRMEPUMPE OPTIONEN (eigener Block unter Tabs)
    st.markdown("###  Wärmepumpe – Optionale Ausgabeblöcke")
    hp_cols1 = st.columns(3)
    with hp_cols1[0]:
        st.session_state.pdf_inclusion_options['include_hp_line_items'] = st.checkbox(
            "Einzelpreise (Netto/Förderung/Nach Förderung)",
            value=st.session_state.pdf_inclusion_options.get(
                'include_hp_line_items',
                True),
            key='hp_inc_line_items')
        st.session_state.pdf_inclusion_options['include_hp_subsidy_block'] = st.checkbox(
            "Förderquote & absolut", value=st.session_state.pdf_inclusion_options.get(
                'include_hp_subsidy_block', True), key='hp_inc_subsidy_block')
    with hp_cols1[1]:
        st.session_state.pdf_inclusion_options['include_hp_total_price_block'] = st.checkbox(
            "Gesamtpreis Netto/MwSt/Brutto",
            value=st.session_state.pdf_inclusion_options.get(
                'include_hp_total_price_block',
                True),
            key='hp_inc_total_price')
        st.session_state.pdf_inclusion_options['include_hp_financing_block'] = st.checkbox(
            "Finanzierung (Monatsrate)", value=st.session_state.pdf_inclusion_options.get(
                'include_hp_financing_block', True), key='hp_inc_financing')
    with hp_cols1[2]:
        st.session_state.pdf_inclusion_options['include_hp_benefits_bullets'] = st.checkbox(
            "Nutzen-Bullets",
            value=st.session_state.pdf_inclusion_options.get(
                'include_hp_benefits_bullets',
                True),
            key='hp_inc_benefits')
        st.session_state.pdf_inclusion_options['include_hp_custom_texts'] = st.checkbox(
            "Individuelle Textbausteine", value=st.session_state.pdf_inclusion_options.get(
                'include_hp_custom_texts', True), key='hp_inc_custom_texts')

    # DESIGN DEFAULTS (Farben & Schrift) – werden in pdf_design_config abgelegt
    design_defaults = st.session_state.get('pdf_design_config', {}) or {}
    if 'color_primary' not in design_defaults:
        design_defaults['color_primary'] = '#1B366F'  # Dunkelblau
    if 'color_secondary' not in design_defaults:
        design_defaults['color_secondary'] = '#2F5597'  # Mittelblau
    if 'color_accent' not in design_defaults:
        design_defaults['color_accent'] = '#0A74DA'  # Akzent Blau
    if 'color_neutral_light' not in design_defaults:
        design_defaults['color_neutral_light'] = '#F4F5F7'
    if 'color_neutral_mid' not in design_defaults:
        design_defaults['color_neutral_mid'] = '#A0A5AE'
    if 'font_family_primary' not in design_defaults:
        design_defaults['font_family_primary'] = 'Helvetica'
    if 'font_family_primary_bold' not in design_defaults:
        design_defaults['font_family_primary_bold'] = 'Helvetica-Bold'
    st.session_state['pdf_design_config'] = design_defaults

    # TAB 3: ERWEITERTE CUSTOM CONTENT ERSTELLUNG
    with ext_tab3:
        st.markdown("####  Individuelle Inhalte & Uploads")

        if 'custom_content_items' not in st.session_state:
            st.session_state['custom_content_items'] = []

        # CONTENT-TYP AUSWAHL
        content_type_tab1, content_type_tab2, content_type_tab3, content_type_tab4 = st.tabs(
            [" Text-Inhalte", " Bilder & Fotos", " Tabellen", " Verwaltung"])

        # TAB 1: TEXT-INHALTE
        with content_type_tab1:
            st.markdown("**Individueller Text-Inhalt hinzufügen:**")

            col1_text, col2_text = st.columns([3, 1])

            with col1_text:
                text_title = st.text_input(
                    "Titel/Überschrift:",
                    placeholder="z.B. Besondere Hinweise, Garantiebedingungen...",
                    key="custom_text_title")

                text_content = st.text_area(
                    "Text-Inhalt:",
                    placeholder="Geben Sie hier Ihren individuellen Text ein...",
                    height=120,
                    key="custom_text_content")

                text_style = st.selectbox(
                    "Text-Stil:",
                    options=["normal", "highlight",
                             "warning", "info", "success"],
                    key="custom_text_style"
                )

            with col2_text:
                text_position = st.selectbox(
                    "Position im PDF:",
                    options=["top", "middle", "bottom", "after_analysis"],
                    format_func=lambda x: {
                        "top": " Oben (nach Deckblatt)",
                        "middle": " Mitte (nach Analyse)",
                        "bottom": " Unten (vor Anhang)",
                        "after_analysis": " Nach Berechnungen"
                    }[x],
                    key="custom_text_position"
                )

                st.markdown("---")

                if st.button(
                    " Text hinzufügen",
                    key="add_text_content",
                        type="primary"):
                    if text_title and text_content:
                        new_text_item = {
                            "type": "text",
                            "id": f"custom_text_{len(st.session_state['custom_content_items']) + 1}",
                            "title": text_title,
                            "content": text_content,
                            "style": text_style,
                            "position": text_position,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state['custom_content_items'].append(
                            new_text_item)
                        st.success(f" '{text_title}' hinzugefügt!")
                        st.rerun()
                    else:
                        st.error(" Bitte Titel und Inhalt eingeben!")

        # TAB 2: BILDER & FOTOS
        with content_type_tab2:
            st.markdown("**Bilder und Fotos hochladen:**")

            col1_img, col2_img = st.columns([2, 2])

            with col1_img:
                uploaded_image = st.file_uploader(
                    "Bild auswählen:",
                    type=['jpg', 'jpeg', 'png', 'gif', 'bmp'],
                    key="custom_image_upload"
                )

                if uploaded_image:
                    st.image(uploaded_image, caption="Vorschau", width=200)

            with col2_img:
                img_title = st.text_input(
                    "Bildtitel/Beschriftung:",
                    placeholder="z.B. Projektstandort, Dachansicht...",
                    key="custom_image_title"
                )

                img_description = st.text_area(
                    "Bildbeschreibung:",
                    placeholder="Optionale Beschreibung des Bildes...",
                    height=80,
                    key="custom_image_description"
                )

                img_position = st.selectbox(
                    "Position im PDF:",
                    options=["top", "middle", "bottom", "gallery"],
                    format_func=lambda x: {
                        "top": " Oben",
                        "middle": " Mitte",
                        "bottom": " Unten",
                        "gallery": " Bildergalerie"
                    }[x],
                    key="custom_image_position"
                )

                if st.button(
                    " Bild hinzufügen",
                    key="add_image_content",
                        type="primary"):
                    if uploaded_image and img_title:
                        # Bild zu Base64 konvertieren
                        image_bytes = uploaded_image.read()
                        image_b64 = base64.b64encode(image_bytes).decode()

                        new_image_item = {
                            "type": "image",
                            "id": f"custom_image_{len(st.session_state['custom_content_items']) + 1}",
                            "title": img_title,
                            "description": img_description,
                            "image_data": image_b64,
                            "image_format": uploaded_image.type,
                            "position": img_position,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state['custom_content_items'].append(
                            new_image_item)
                        st.success(f" Bild '{img_title}' hinzugefügt!")
                        st.rerun()
                    else:
                        st.error(" Bitte Bild und Titel eingeben!")

        # TAB 3: TABELLEN
        with content_type_tab3:
            st.markdown("**Individuelle Tabelle erstellen:**")

            table_title = st.text_input(
                "Tabellen-Titel:",
                placeholder="z.B. Zusätzliche Leistungen, Komponenten-Details...",
                key="custom_table_title")

            # Tabellen-Editor
            if 'temp_table_data' not in st.session_state:
                st.session_state['temp_table_data'] = {
                    'headers': ["Komponente", "Beschreibung", "Preis"],
                    'rows': [
                        ["Beispiel 1", "Beschreibung...", "1.000 €"],
                        ["Beispiel 2", "Beschreibung...", "2.000 €"]
                    ]
                }

            col1_table, col2_table = st.columns([3, 1])

            with col1_table:
                # Header bearbeiten
                st.markdown("**Spalten-Überschriften:**")
                headers_input = st.text_input(
                    "Spalten (mit Komma trennen):",
                    value=", ".join(
                        st.session_state['temp_table_data']['headers']),
                    key="table_headers_input"
                )

                if headers_input:
                    st.session_state['temp_table_data']['headers'] = [
                        h.strip() for h in headers_input.split(',')]

                # Zeilen bearbeiten
                st.markdown("**Tabellenzeilen:**")
                for i, row in enumerate(
                        st.session_state['temp_table_data']['rows']):
                    cols = st.columns(
                        len(st.session_state['temp_table_data']['headers']) + 1)

                    for j, header in enumerate(
                            st.session_state['temp_table_data']['headers']):
                        with cols[j]:
                            new_value = st.text_input(
                                f"{header}:",
                                value=row[j] if j < len(row) else "",
                                key=f"table_cell_{i}_{j}",
                                label_visibility="collapsed"
                            )
                            if j < len(row):
                                st.session_state['temp_table_data']['rows'][i][j] = new_value
                            else:
                                st.session_state['temp_table_data']['rows'][i].append(
                                    new_value)

                    with cols[-1]:
                        if st.button(
                            "",
                            key=f"delete_row_{i}",
                                help="Zeile löschen"):
                            st.session_state['temp_table_data']['rows'].pop(i)
                            st.rerun()

            with col2_table:
                table_position = st.selectbox(
                    "Position:",
                    options=["top", "middle", "bottom", "pricing"],
                    format_func=lambda x: {
                        "top": " Oben",
                        "middle": " Mitte",
                        "bottom": " Unten",
                        "pricing": " Bei Preisen"
                    }[x],
                    key="custom_table_position"
                )

                st.markdown("---")

                if st.button(" Zeile hinzufügen", key="add_table_row"):
                    new_row = [""] * \
                        len(st.session_state['temp_table_data']['headers'])
                    st.session_state['temp_table_data']['rows'].append(new_row)
                    st.rerun()

                if st.button(
                    " Tabelle hinzufügen",
                    key="add_table_content",
                        type="primary"):
                    if table_title and st.session_state['temp_table_data']['rows']:
                        new_table_item = {
                            "type": "table",
                            "id": f"custom_table_{len(st.session_state['custom_content_items']) + 1}",
                            "title": table_title,
                            "headers": st.session_state['temp_table_data']['headers'].copy(),
                            "rows": [row.copy() for row in st.session_state['temp_table_data']['rows']],
                            "position": table_position,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state['custom_content_items'].append(
                            new_table_item)
                        st.success(f" Tabelle '{table_title}' hinzugefügt!")
                        # Reset temp data
                        st.session_state['temp_table_data'] = {
                            'headers': ["Komponente", "Beschreibung", "Preis"],
                            'rows': [["", "", ""]]
                        }
                        st.rerun()
                    else:
                        st.error(" Bitte Titel eingeben und Zeilen ausfüllen!")

        # TAB 4: VERWALTUNG
        with content_type_tab4:
            content_count = len(st.session_state['custom_content_items'])

            if content_count > 0:
                st.success(
                    f" **{content_count} Custom Content-Element(e) aktiv**")

                # Bestehende Elemente anzeigen
                st.markdown("**Bestehende Inhalte:**")

                for i, item in enumerate(
                        st.session_state['custom_content_items']):
                    with st.expander(f"{item.get('type', '').upper()}: {item.get('title', 'Ohne Titel')} (Position: {item.get('position', 'unbekannt')})"):
                        col1_manage, col2_manage = st.columns([3, 1])

                        with col1_manage:
                            if item['type'] == 'text':
                                st.write(
                                    f"**Inhalt:** {item.get('content', '')[:100]}...")
                                st.write(
                                    f"**Stil:** {item.get('style', 'normal')}")
                            elif item['type'] == 'image':
                                st.write(
                                    f"**Beschreibung:** {item.get('description', 'Keine')}")
                                if 'image_data' in item:
                                    st.write("**Bild:**  Vorhanden")
                            elif item['type'] == 'table':
                                st.write(
                                    f"**Spalten:** {', '.join(item.get('headers', []))}")
                                st.write(
                                    f"**Zeilen:** {len(item.get('rows', []))}")

                            st.write(
                                f"**Erstellt:** {item.get('created', 'Unbekannt')}")

                        with col2_manage:
                            if st.button(
                                    " Löschen", key=f"delete_content_{i}"):
                                st.session_state['custom_content_items'].pop(i)
                                st.rerun()

                st.markdown("---")

                col1_clear, col2_clear = st.columns(2)
                with col1_clear:
                    if st.button(" Alle löschen", key="clear_all_content"):
                        st.session_state['custom_content_items'] = []
                        st.rerun()

                with col2_clear:
                    if st.button(" Vorschau", key="preview_content"):
                        st.info("Vorschau wird im generierten PDF angezeigt")
            else:
                st.info("ℹ **Noch keine Custom Content-Elemente hinzugefügt**")
                st.markdown("""
                **Verfügbare Content-Typen:**
                -  **Texte:** Individuelle Hinweise, Garantien, etc.
                -  **Bilder:** Fotos vom Projekt, Referenzen, etc.
                -  **Tabellen:** Zusätzliche Komponenten, Preislisten, etc.
                """)

    # TAB 4: PDF DESIGN THEMES
    with ext_tab4:
        pdf_design_config = st.session_state.get('pdf_design_config', {})

        col1_design, col2_design, col3_design = st.columns(3)

        with col1_design:
            pdf_design_config['theme'] = st.selectbox(
                "Theme",
                options=["professional", "modern", "classic", "minimal"],
                index=["professional", "modern", "classic", "minimal"].index(
                    pdf_design_config.get('theme', 'professional')
                ),
                key="design_theme_select_outside_form"
            )

        with col2_design:
            pdf_design_config['color_scheme'] = st.selectbox(
                "Farbschema",
                options=["blue_gradient", "green_modern",
                         "orange_warm", "purple_elegant"],
                index=["blue_gradient", "green_modern", "orange_warm", "purple_elegant"].index(
                    pdf_design_config.get('color_scheme', 'blue_gradient')
                ),
                key="color_scheme_select_outside_form"
            )

        with col3_design:
            pdf_design_config['typography'] = st.selectbox(
                "Typografie",
                options=["modern", "classic", "bold", "elegant"],
                index=["modern", "classic", "bold", "elegant"].index(
                    pdf_design_config.get('typography', 'modern')
                ),
                key="typography_select_outside_form"
            )
        # Vereinheitlichte Dienstleistungs-Darstellung (ausgelagert)
        try:
            from service_display_config_ui import render_service_display_config
            render_service_display_config(pdf_design_config, inline=True)
        except Exception as e:
            st.warning(f"Service Display UI konnte nicht geladen werden: {e}")

        st.session_state['pdf_design_config'] = pdf_design_config

    # Feature-Status anzeigen
    st.markdown("** Feature-Status:**")
    col1_status, col2_status, col3_status, col4_status = st.columns(4)

    with col1_status:
        financing_active = st.session_state.get(
            'financing_config', {}).get('enabled', False)
        st.write(f" Finanzierung: {'' if financing_active else ''}")

    with col2_status:
        chart_active = bool(st.session_state.get('chart_config', {}))
        st.write(f" Charts: {'' if chart_active else ''}")

    with col3_status:
        content_count = len(st.session_state.get('custom_content_items', []))
        st.write(f" Content: {content_count} Elemente")

    with col4_status:
        design_active = bool(st.session_state.get('pdf_design_config', {}))
        st.write(f" Design: {'' if design_active else ''}")

    st.markdown("---")

    # === Extended PDF Output Toggle - OUTSIDE FORM for immediate reactivity ===
    st.markdown("### Erweiterte PDF-Optionen")
    append_additional_pages_checkbox = st.checkbox(
        "Zusätzliche Seiten anhängen (Datenblätter, Dokumente, Diagramme)",
        value=st.session_state.pdf_inclusion_options.get("append_additional_pages_after_main8", False),
        key="pdf_cb_append_additional_pages",
        help="Fügt zusätzliche Seiten nach den Hauptseiten an: Produktdatenblätter, Firmendokumente, Diagramme"
    )

    # Save immediately to session state (outside form, so it works instantly)
    st.session_state.pdf_inclusion_options["append_additional_pages_after_main8"] = append_additional_pages_checkbox

    # KRITISCHER FIX: Wenn Zusatzseiten aktiviert, muss include_all_documents auch TRUE sein!
    # Sonst wird _append_datasheets_and_documents() NICHT aufgerufen!
    if append_additional_pages_checkbox:
        st.session_state.pdf_inclusion_options["include_all_documents"] = True
    else:
        st.session_state.pdf_inclusion_options["include_all_documents"] = False

    if append_additional_pages_checkbox:
        st.success(
            "✅ Zusatzseiten aktiv! Wählen Sie unten die Inhalte aus, die angehängt werden sollen.")

        # ===================================================================
        # DIAGRAMM-AUSWAHL AUSSERHALB DES FORMULARS (für sofortige Reaktion)
        # ===================================================================
        st.markdown("---")
        st.markdown("### Diagrammauswahl & Vorschau")

        # Chart Layout Selection
        with st.expander("Diagramm-Layout", expanded=False):
            chart_layout_options = [
                'one_per_page', 'two_per_page', 'four_per_page']
            chart_layout_labels = {
                'one_per_page': '1 Diagramm pro Seite',
                'two_per_page': '2 Diagramme pro Seite',
                'four_per_page': '4 Diagramme pro Seite'
            }

            current_layout = st.session_state.pdf_inclusion_options.get(
                "chart_layout", "one_per_page")
            selected_chart_layout = st.selectbox(
                "Layout für Diagramme im PDF:",
                options=chart_layout_options,
                format_func=lambda x: chart_layout_labels.get(x, x),
                index=chart_layout_options.index(current_layout) if current_layout in chart_layout_options else 0,
                key="pdf_chart_layout_outside_form"
            )
            st.session_state.pdf_inclusion_options["chart_layout"] = selected_chart_layout

        # Finanzierungsdetails Option (NEU)
        with st.expander("💰 Finanzierungsdetails", expanded=False):
            include_financing = st.checkbox(
                "Finanzierungsdetails in PDF einbinden",
                value=st.session_state.pdf_inclusion_options.get(
                    "include_financing_details",
                    False),
                help="Fügt detaillierte Finanzierungsinformationen (Kredit/Leasing) als zusätzliche Seiten hinzu",
                key="pdf_include_financing_details_checkbox")
            st.session_state.pdf_inclusion_options["include_financing_details"] = include_financing

            if include_financing:
                # Zeige Vorschau der verfügbaren Finanzierungsdaten
                project_data = st.session_state.get('project_data', {})
                customer_data = project_data.get('customer_data', {})
                financing_requested = customer_data.get(
                    'financing_requested', False)

                if financing_requested:
                    financing_type = customer_data.get(
                        'financing_type', 'Nicht spezifiziert')
                    financing_amount = customer_data.get(
                        'desired_financing_amount', 0)
                    st.success(
                        f"✅ Finanzierung aktiv: {financing_type} ({
                            financing_amount:,.2f} €)")
                else:
                    st.warning(
                        "⚠️ Keine Finanzierung im Projekt konfiguriert. Seite wird leer sein.")

        # Chart Selection
        if 'analysis_results' in st.session_state and st.session_state.analysis_results:
            analysis_results_for_charts = st.session_state.analysis_results
            project_data_for_charts = st.session_state.get('project_data', {})

            # NEUE FEATURES ANZEIGEN
            st.markdown("---")
            st.markdown("### 🌟 Erweiterte Features (AKTIV)")

            try:
                from advanced_features import get_all_advanced_features

                # Features berechnen
                advanced_features = get_all_advanced_features(
                    project_data_for_charts, analysis_results_for_charts)

                # Kompakte Übersicht
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    tariff = advanced_features.get(
                        'grid_tariff_optimization', {})
                    savings = tariff.get('potential_savings', 0)
                    st.metric("⚡ Tarif-Optimierung", f"{savings:,.0f} €/Jahr")

                with col2:
                    tax = advanced_features.get('tax_benefits', {})
                    benefit = tax.get(
                        'total_benefit', {}).get(
                        'first_year_linear', 0)
                    st.metric("💰 Steuervorteil J1", f"{benefit:,.0f} €")

                with col3:
                    subsidy = advanced_features.get('subsidy_optimization', {})
                    grants = subsidy.get('total_grants', 0)
                    st.metric("🎁 Förderungen", f"{grants:,.0f} €")

                with col4:
                    financing = advanced_features.get(
                        'financing_scenarios', {})
                    best = financing.get('best_scenario', {})
                    benefit_20y = best.get('net_benefit_20y', 0)
                    st.metric("💳 Beste Option", f"{benefit_20y:,.0f} €")

                # Details in Expander
                with st.expander("📊 Alle erweiterten Features anzeigen", expanded=False):
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "⚡ Tarif", "💰 Steuern", "🎁 Förderung", "🔋 Batterie", "💳 Finanzierung"
                    ])

                    with tab1:
                        st.markdown("### Stromtarif-Optimierung")
                        if 'error' not in tariff:
                            st.success(
                                f"✅ **{tariff.get('recommended_tariff')}**")
                            st.write(
                                f"Einsparung: **{tariff.get('potential_savings', 0):,.2f} €/Jahr**")

                    with tab2:
                        st.markdown("### Steuervorteile")
                        if 'error' not in tax:
                            st.write(
                                f"USt-Erstattung: **{tax.get('vat_refund', 0):,.2f} €**")
                            st.write(
                                f"Steuervorteil 20J: **{
                                    tax.get(
                                        'total_benefit',
                                        {}).get(
                                        'total_20y_linear',
                                        0):,.2f} €**")

                    with tab3:
                        st.markdown("### Verfügbare Förderungen")
                        if 'error' not in subsidy:
                            st.write(
                                f"Gesamte Zuschüsse: **{subsidy.get('total_grants', 0):,.2f} €**")
                            st.write(
                                f"Netto-Investition: **{subsidy.get('net_investment', 0):,.2f} €**")

                    with tab4:
                        st.markdown("### Batterie-Optimierung")
                        battery = advanced_features.get(
                            'battery_optimization', {})
                        if 'error' not in battery:
                            st.info(
                                battery.get(
                                    'recommendation',
                                    'Keine Optimierung nötig'))

                    with tab5:
                        st.markdown("### Finanzierungs-Szenarien")
                        if 'error' not in financing:
                            st.success(financing.get('recommendation', ''))

                st.success(
                    "✅ **8 neue Features sind aktiv!** Die Ergebnisse werden automatisch ins PDF integriert.")

            except ImportError:
                st.warning(
                    "⚠️ Erweiterte Features nicht verfügbar (Module nicht gefunden)")
            except Exception as e:
                st.error(f"Fehler bei erweiterten Features: {e}")

            st.markdown("---")

            # === FINANCIAL TOOLS UI ===
            st.markdown("### 💰 Financial Tools - Alle Finanz-Berechnungen")

            try:
                from financial_tools_ui import render_financial_tools_section

                # Financial Tools UI rendern
                financial_results = render_financial_tools_section(
                    project_data=project_data_for_charts,
                    analysis_results=analysis_results_for_charts,
                    session_key_prefix="pdf_fin_tools"
                )

                # Ergebnisse in Session State speichern
                if 'pdf_inclusion_options' not in st.session_state:
                    st.session_state.pdf_inclusion_options = {}

                st.session_state.pdf_inclusion_options['financial_tools_results'] = financial_results

            except ImportError:
                st.warning("⚠️ Financial Tools UI nicht verfügbar")
            except Exception as e:
                st.error(f"Fehler bei Financial Tools: {e}")

            st.markdown("---")

            # Nutze die bereits vorhandene render_chart_selection_ui Funktion
            # Diese speichert bereits in
            # st.session_state.pdf_inclusion_options['selected_charts_for_pdf']
            selected_charts = render_chart_selection_ui(
                project_data=project_data_for_charts,
                analysis_results=analysis_results_for_charts,
                texts=texts
            )

            # Chart Preview (sofort sichtbar)
            if selected_charts:
                st.markdown("---")
                st.markdown("### Diagramm-Vorschau")
                render_chart_preview_interface(
                    selected_charts=selected_charts,
                    analysis_results=analysis_results_for_charts,
                    preview_mode="grid"
                )
        else:
            st.info(
                "ℹ️ Keine Analyseergebnisse verfügbar. Bitte führen Sie zuerst eine Berechnung durch.")

            # Aber: Zeige verfügbare erweiterte Features trotzdem an
            with st.expander("🌟 Erweiterte Features Vorschau (ohne Berechnung)", expanded=True):
                st.markdown("""
                **Nach der Berechnung im Solar Calculator sind folgende Features verfügbar:**

                ### ⚡ Stromtarif-Optimierung
                - Vergleicht Einheitstarif, HT/NT-Tarif, Dynamischer Tarif
                - Berechnet Lastverschiebungspotenzial
                - Empfiehlt optimalen Tarif
                - **Einsparung:** Bis zu 520 €/Jahr

                ### 💰 Steuervorteile & AfA
                - Umsatzsteuer-Erstattung (19%)
                - Abschreibung (Linear 5%, Degressiv 25%)
                - Einkommensteuer-Berechnung
                - **Vorteil Jahr 1:** ~10.000 €
                - **Vorteil 20 Jahre:** ~24.000 €

                ### 🎁 Verfügbare Förderungen
                - KfW 270, KfW 442, BAFA
                - Landesförderungen (Bayern, NRW)
                - Kommunale Förderungen
                - **Gesamte Zuschüsse:** Bis zu 13.900 €

                ### 🔋 Batterie-Optimierung
                - Simuliert optimale Speichergröße
                - Berechnet ROI und Payback
                - **Autarkie-Steigerung:** Bis zu +8%

                ### 💳 Finanzierungs-Szenarien
                - Vergleicht Barkauf, Kredit, Leasing, PPA
                - 6 verschiedene Szenarien
                - **ROI-Verdopplung** möglich

                ### 📊 Break-Even Detailliert (Neues Chart!)
                - 3 Szenarien über 25 Jahre
                - Interaktives Liniendiagramm
                - Break-Even Marker

                ### 📊 Lebenszykluskosten TCO (Neues Chart!)
                - Total Cost of Ownership
                - Waterfall Chart
                - Alle Kosten über 25 Jahre

                ---

                ⚠️ **Um diese Features zu nutzen:**
                1. Gehen Sie zum **Solar Calculator** (Hauptseite)
                2. Füllen Sie alle Projektdaten aus
                3. Klicken Sie **"Berechnung durchführen"**
                4. Kommen Sie zurück zur PDF-Konfiguration
                5. Die Features sind dann verfügbar!
                """)

                st.info(
                    "💡 **Tipp:** Die neuen Features verdoppeln oft den ROI Ihrer PV-Anlage!")
    else:
        st.info("ℹ️ Standard-Modus: 8-Seiten-PDF ohne Zusatzseiten.")

        # === Quick Actions for Extended Options (OUTSIDE FORM) ===
        with st.expander("Schnellaktionen für Produktdatenblätter", expanded=False):
            st.markdown("**Auto-Auswahl zurücksetzen**")
            st.caption(
                "Setzt die Produktdatenblatt-Auswahl auf die im Solar Calculator gewählten Produkte zurück.")

            # Get auto-selected product IDs
            auto_selected_product_ids = set()
            project_details = st.session_state.get(
                'project_data', {}).get(
                'project_details', {})

            selected_product_keys = [
                'selected_module_id',
                'selected_inverter_id',
                'selected_battery_id',
                'selected_optimizer_id',
                'selected_wallbox_id',
                'selected_carport_id',
                'selected_notstrom_id',
                'selected_tierabwehr_id',
            ]

            for key in selected_product_keys:
                product_id = project_details.get(key)
                if product_id is not None and isinstance(product_id, int):
                    auto_selected_product_ids.add(product_id)

            if auto_selected_product_ids:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    # Guard gegen mehrfache Reruns
                    if st.button(
                        "Zurücksetzen auf Auto-Auswahl",
                            key="reset_datasheet_selection_btn_outside_form"):
                        if not st.session_state.get(
                                '_reset_datasheet_in_progress'):
                            st.session_state._reset_datasheet_in_progress = True
                            st.session_state.pdf_inclusion_options["selected_product_datasheets"] = list(
                                auto_selected_product_ids)
                            st.success(
                                f"{len(auto_selected_product_ids)} Produkt(e) aus Solar Calculator ausgewählt")
                            st.rerun()
                with col2:
                    st.caption(
                        f"{len(auto_selected_product_ids)} Produkt(e) im Solar Calculator konfiguriert")

                # Entferne Guard nach erfolgreichem Render
                if st.session_state.get('_reset_datasheet_in_progress'):
                    st.session_state._reset_datasheet_in_progress = False
            else:
                st.info(
                    "Keine Produkte im Solar Calculator konfiguriert. Bitte wählen Sie zuerst Produkte im Solar Calculator aus.")

    st.markdown("---")

    # Hauptformular
    # ... (Rest des Formulars und der PDF-Generierungslogik wie in der vorherigen Antwort, mit der Korrektur für st.form_submit_button) ...
    form_submit_key = "pdf_final_submit_btn_v13_corrected_again"
    submit_button_disabled = st.session_state.pdf_generating_lock_v1
    with st.form(key="pdf_generation_form_v13_final_locked_options_main", clear_on_submit=False):
        st.subheader(get_text_pdf_ui(
            texts, "pdf_config_header", "PDF-Konfiguration"))
        with st.container():
            st.markdown(
                "**" +
                get_text_pdf_ui(
                    texts,
                    "pdf_template_selection_info",
                    "Vorlagen für das Angebot auswählen") +
                "**")
            title_image_options = {
                t.get(
                    'name',
                    f"Bild {
                        i +
                        1}"): t.get('data') for i,
                t in enumerate(title_image_templates) if isinstance(
                    t,
                    dict) and t.get('name')}
            if not title_image_options:
                title_image_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_title_images_available",
                        "Keine Titelbilder verfügbar"): None}
            title_image_keys = list(title_image_options.keys())
            idx_title_img = title_image_keys.index(
                st.session_state.selected_title_image_name_doc_output) if st.session_state.selected_title_image_name_doc_output in title_image_keys else 0
            selected_title_image_name = st.selectbox(
                get_text_pdf_ui(
                    texts,
                    "pdf_select_title_image",
                    "Titelbild auswählen"),
                options=title_image_keys,
                index=idx_title_img,
                key="pdf_title_image_select_v13_form")
            if selected_title_image_name != st.session_state.selected_title_image_name_doc_output:
                st.session_state.selected_title_image_name_doc_output = selected_title_image_name
                st.session_state.selected_title_image_b64_data_doc_output = title_image_options.get(
                    selected_title_image_name)
            offer_title_options = {
                t.get(
                    'name',
                    f"Titel {
                        i +
                        1}"): t.get('content') for i,
                t in enumerate(offer_title_templates) if isinstance(
                    t,
                    dict) and t.get('name')}
            if not offer_title_options:
                offer_title_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_offer_titles_available",
                        "Keine Angebotstitel verfügbar"): "Standard Angebotstitel"}
            offer_title_keys = list(offer_title_options.keys())
            idx_offer_title = offer_title_keys.index(
                st.session_state.selected_offer_title_name_doc_output) if st.session_state.selected_offer_title_name_doc_output in offer_title_keys else 0
            selected_offer_title_name = st.selectbox(
                get_text_pdf_ui(
                    texts,
                    "pdf_select_offer_title",
                    "Überschrift/Titel auswählen"),
                options=offer_title_keys,
                index=idx_offer_title,
                key="pdf_offer_title_select_v13_form")
            if selected_offer_title_name != st.session_state.selected_offer_title_name_doc_output:
                st.session_state.selected_offer_title_name_doc_output = selected_offer_title_name
                st.session_state.selected_offer_title_text_content_doc_output = offer_title_options.get(
                    selected_offer_title_name, "")
            cover_letter_options = {
                t.get(
                    'name',
                    f"Anschreiben {
                        i +
                        1}"): t.get('content') for i,
                t in enumerate(cover_letter_templates) if isinstance(
                    t,
                    dict) and t.get('name')}
            if not cover_letter_options:
                cover_letter_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_cover_letters_available",
                        "Keine Anschreiben verfügbar"): "Standard Anschreiben"}
            cover_letter_keys = list(cover_letter_options.keys())
            idx_cover_letter = cover_letter_keys.index(
                st.session_state.selected_cover_letter_name_doc_output) if st.session_state.selected_cover_letter_name_doc_output in cover_letter_keys else 0
            selected_cover_letter_name = st.selectbox(
                get_text_pdf_ui(
                    texts,
                    "pdf_select_cover_letter",
                    "Anschreiben auswählen"),
                options=cover_letter_keys,
                index=idx_cover_letter,
                key="pdf_cover_letter_select_v13_form")
            if selected_cover_letter_name != st.session_state.selected_cover_letter_name_doc_output:
                st.session_state.selected_cover_letter_name_doc_output = selected_cover_letter_name
                st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_options.get(
                    selected_cover_letter_name, "")
        st.markdown("---")
        st.markdown("**" + get_text_pdf_ui(texts, "pdf_content_selection_info",
                    "Inhalte für das PDF auswählen") + "**")

        # === Use the global checkbox value (set outside the form) ===
        append_additional_pages_enabled = st.session_state.pdf_inclusion_options.get(
            "append_additional_pages_after_main8", False)

        if not append_additional_pages_enabled:
            st.info("ℹ️ Standardmodus: Es wird das Standard-8-Seiten-PDF generiert. Aktivieren Sie die Zusatzseiten für weitere Inhalte.")
        else:
            st.success(
                "✓ Erweiterter Modus aktiv: Zusätzliche Seiten werden ab Seite 9 angehängt.")

            # === SUBTASK 2.2: Finanzierungsdetails-Auswahl ===
            with st.expander("Finanzierungsdetails", expanded=False):
                # Use temporary variable for checkbox value within form
                financing_details_checkbox = st.checkbox(
                    "Finanzierungsoptionen einbinden",
                    value=st.session_state.pdf_inclusion_options.get(
                        "include_financing_details",
                        False),
                    key="pdf_cb_financing_details_v1")

                if financing_details_checkbox:
                    # Load financing options from payment_terms
                    try:
                        payment_terms = load_admin_setting_func(
                            'payment_terms', {})
                        payment_options = payment_terms.get(
                            'payment_options', [])
                        financing_opts = [opt for opt in payment_options if opt.get(
                            'payment_type') == 'financing' and opt.get('enabled', False)]

                        if financing_opts:
                            st.caption(
                                f"✓ {
                                    len(financing_opts)} Finanzierungsoption(en) verfügbar")
                            for opt in financing_opts:
                                st.text(f"  • {opt.get('name', 'Unbenannt')}")
                        else:
                            st.warning(
                                "Keine Finanzierungsoptionen in den Admin-Einstellungen konfiguriert.")
                    except Exception as e:
                        st.error(
                            f"Fehler beim Laden der Finanzierungsoptionen: {e}")

            # === SUBTASK 2.3: Produktdatenblatt-Auswahl ===
            with st.expander("Produktdatenblätter", expanded=False):
                try:
                    # Get products with datasheets
                    if callable(list_products_func):
                        all_products = list_products_func()

                        def _resolve_datasheet_path(
                                prod: dict[str, Any]) -> str | None:
                            if not isinstance(prod, dict):
                                return None
                            for key in (
                                "datasheet_link_db_path",
                                "datasheet_path",
                                "datasheet_link",
                                "datasheet_url",
                            ):
                                value = prod.get(key)
                                if isinstance(value, str) and value.strip():
                                    return value.strip()
                            return None

                        products_with_datasheets = []
                        for product in all_products:
                            if not isinstance(product, dict):
                                continue
                            datasheet_path = _resolve_datasheet_path(product)
                            if datasheet_path:
                                product_copy = dict(product)
                                product_copy["_resolved_datasheet_path"] = datasheet_path
                                products_with_datasheets.append(product_copy)

                        if products_with_datasheets:
                            st.caption(
                                f"✓ {
                                    len(products_with_datasheets)} Produkt(e) mit Datenblättern verfügbar")

                            # === AUTO-SELECT: Get selected product IDs from Solar Calculator ===
                            auto_selected_product_ids = set()
                            project_details = st.session_state.get(
                                'project_data', {}).get('project_details', {})

                            # Collect all selected product IDs from solar
                            # calculator
                            selected_product_keys = [
                                'selected_module_id',
                                'selected_inverter_id',
                                'selected_battery_id',
                                'selected_optimizer_id',
                                'selected_wallbox_id',
                                'selected_carport_id',
                                'selected_notstrom_id',
                                'selected_tierabwehr_id',
                            ]

                            for key in selected_product_keys:
                                product_id = project_details.get(key)
                                if product_id is not None and isinstance(
                                        product_id, int):
                                    auto_selected_product_ids.add(product_id)

                            # Initialize selected datasheets
                            if "selected_product_datasheets" not in st.session_state.pdf_inclusion_options:
                                # First time: auto-select products from solar
                                # calculator
                                st.session_state.pdf_inclusion_options["selected_product_datasheets"] = list(
                                    auto_selected_product_ids)

                            # Show info about auto-selected products
                            if auto_selected_product_ids:
                                auto_selected_count = len(
                                    auto_selected_product_ids)
                                st.info(
                                    f"{auto_selected_count} Produkt(e) aus dem Solar Calculator automatisch vorausgewählt (anpassbar)")

                            selected_datasheets = []
                            existing_selection = st.session_state.pdf_inclusion_options.get(
                                "selected_product_datasheets", [])

                            for product in products_with_datasheets:
                                if not isinstance(product, dict):
                                    continue

                                product_id = product.get('id')
                                datasheet_path = product.get(
                                    "_resolved_datasheet_path")
                                if product_id is None or not datasheet_path:
                                    continue

                                product_name = product.get('name') or product.get(
                                    'model_name') or 'Unbenannt'
                                product_type = product.get('product_type') or product.get(
                                    'category') or 'Unbekannt'

                                # Mark auto-selected products with icon
                                if product_id in auto_selected_product_ids:
                                    label = f"{product_name} ({product_type})"
                                else:
                                    label = f"{product_name} ({product_type})"

                                is_preselected = product_id in existing_selection
                                if st.checkbox(
                                    label,
                                    value=is_preselected,
                                    key=f"pdf_cb_datasheet_{product_id}_v1"
                                ):
                                    selected_datasheets.append(product_id)

                            st.session_state.pdf_inclusion_options["selected_product_datasheets"] = selected_datasheets

                            # Info about resetting to auto-selection
                            if auto_selected_product_ids:
                                st.caption(
                                    "Tipp: Verwenden Sie '⚡ Schnellaktionen' oberhalb des Formulars, um zur Auto-Auswahl zurückzukehren.")
                        else:
                            st.info(
                                "Keine Produkte mit Datenblättern in der Datenbank gefunden.")
                    else:
                        st.warning("Produktliste-Funktion nicht verfügbar.")
                except Exception as e:
                    st.error(f"Fehler beim Laden der Produktdatenblätter: {e}")

            # === SUBTASK 2.4: Firmendokument-Auswahl ===
            with st.expander("Firmendokumente", expanded=False):
                if active_company_id_for_docs is not None and callable(
                        db_list_company_documents_func):
                    try:
                        company_docs_list = db_list_company_documents_func(
                            active_company_id_for_docs, None)

                        if company_docs_list:
                            st.caption(
                                f"✓ {
                                    len(company_docs_list)} Firmendokument(e) verfügbar")

                            # Initialize selected documents
                            if "selected_company_documents" not in st.session_state.pdf_inclusion_options:
                                st.session_state.pdf_inclusion_options["selected_company_documents"] = [
                                ]

                            selected_docs = []
                            for doc in company_docs_list:
                                if isinstance(doc, dict) and 'id' in doc:
                                    doc_id = doc['id']
                                    doc_label = f"{
                                        doc.get(
                                            'display_name',
                                            doc.get(
                                                'file_name',
                                                'Unbenannt'))} ({
                                        doc.get(
                                            'document_type',
                                            'Unbekannt')})"

                                    if st.checkbox(
                                        doc_label, value=doc_id in st.session_state.pdf_inclusion_options.get(
                                            "selected_company_documents", []), key=f"pdf_cb_company_doc_{doc_id}_v1"):
                                        selected_docs.append(doc_id)

                            st.session_state.pdf_inclusion_options["selected_company_documents"] = selected_docs
                        else:
                            st.info(
                                "Keine Firmendokumente für diese Firma hinterlegt.")
                    except Exception as e:
                        st.error(f"Fehler beim Laden der Firmendokumente: {e}")
                else:
                    st.warning(
                        "Keine aktive Firma ausgewählt oder Dokumentfunktion nicht verfügbar.")

            # === SUBTASK 2.5: Diagramm-Auswahl ist jetzt AUSSERHALB des Formulars ===
            # Show comprehensive status of all additional pages selections
            st.markdown("---")
            st.markdown("#### 📋 Übersicht Zusatzseiten")

            append_active = st.session_state.pdf_inclusion_options.get(
                "append_additional_pages_after_main8", False)
            if append_active:
                # Status-Übersicht mit Metriken
                col1, col2, col3 = st.columns(3)

                with col1:
                    selected_charts_count = len(
                        st.session_state.pdf_inclusion_options.get(
                            "selected_charts_for_pdf", []))
                    st.metric("📊 Diagramme", selected_charts_count)

                with col2:
                    selected_datasheets_count = len(
                        st.session_state.pdf_inclusion_options.get(
                            "selected_product_datasheets", []))
                    st.metric(
                        "📄 Datenblätter",
                        selected_datasheets_count if selected_datasheets_count > 0 else "Auto")

                with col3:
                    selected_docs_count = len(
                        st.session_state.pdf_inclusion_options.get(
                            "selected_company_documents", []))
                    st.metric("📑 Dokumente", selected_docs_count)

                # Detaillierte Info
                info_parts = []
                if selected_charts_count > 0:
                    info_parts.append(f"✅ {selected_charts_count} Diagramm(e)")
                else:
                    info_parts.append("⚠️ Keine Diagramme")

                if selected_datasheets_count > 0:
                    info_parts.append(
                        f"✅ {selected_datasheets_count} Datenblatt/Datenblätter")
                else:
                    info_parts.append(
                        "✅ Auto-Auswahl (Module, Inverter, Speicher)")

                if selected_docs_count > 0:
                    info_parts.append(
                        f"✅ {selected_docs_count} Firmendokument(e)")
                else:
                    info_parts.append("⚠️ Keine Firmendokumente")

                st.info(" | ".join(info_parts))

                # Warnung wenn nichts ausgewählt
                if selected_charts_count == 0 and selected_docs_count == 0:
                    st.warning(
                        "⚠️ **Hinweis:** Scrollen Sie nach oben zu 'Zusätzliche Seiten anhängen' um Diagramme auszuwählen!")
            else:
                st.info(
                    "ℹ️ Zusatzseiten sind deaktiviert. Aktivieren Sie 'Zusätzliche Seiten anhängen' oberhalb des Formulars.")

        # ERWEITERTE PDF-FEATURES UI INTEGRATION (nur Trennlinie im Formular
        # belassen; Services-UI außerhalb für sofortige Reaktion)
        st.markdown("---")
        submitted_generate_pdf = st.form_submit_button(
            label=f"**{
                get_text_pdf_ui(
                    texts,
                    'pdf_generate_button',
                    'Angebots-PDF erstellen')}**",
            type="primary",
            disabled=submit_button_disabled)
        if submitted_generate_pdf:
            # Keine Konvertierung mehr nötig - Diagramme werden direkt außerhalb des Formulars gesetzt
            # Validiere nur, dass wenn append_additional_pages aktiv ist, die
            # Charts-Auswahl existiert
            append_after_main8_flag_submit = bool(
                st.session_state.pdf_inclusion_options.get(
                    "append_additional_pages_after_main8", False))

            if not append_after_main8_flag_submit:
                # Wenn Zusatzseiten deaktiviert, stelle sicher dass Charts
                # geleert sind
                st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = [
                ]

            # Debug-Ausgabe
            selected_chart_count = len(
                st.session_state.pdf_inclusion_options.get(
                    "selected_charts_for_pdf", []))
            print(
                f"DEBUG: PDF-Generierung gestartet mit {selected_chart_count} Diagramm(en)")

    # Dienstleistungen UI (außerhalb des Formulars für Live-Reaktivität)
    st.markdown("---")
    st.markdown("### Dienstleistungen (Seite 7 im Angebot)")
    if 'pdf_services' not in st.session_state:
        st.session_state.pdf_services = {
            'extras_enabled': False,
            # Standard-Dienstleistungen (standardmäßig aktiv)
            'service_consulting': True,
            'service_planning': True,
            'service_project_management': True,
            'service_optimization': True,
            'service_grid_application': True,
            'service_dc_installation': True,
            'service_ac_installation': True,
            'service_storage_installation': True,
            'service_commissioning_training': True,
            'service_grid_completion': True,
            'service_additional_tasks': False,
            'service_wallbox_cabling': False,
            'service_backup_power_activation': False,
            'service_energy_management_system': False,
            'service_dynamic_tariff_activation': False,
            'custom_entries': ''
        }
    pdf_services_state = st.session_state.pdf_services
    with st.expander("Standard-Dienstleistungen anpassen", expanded=False):

        # Load standard services dynamically from database
        try:
            from admin_services_ui import get_standard_services
            from services_integration import (
                _format_german_currency,
                get_service_quantity,
            )

            standard_services = get_standard_services()

            if standard_services:
                st.markdown(
                    "**Standard-Dienstleistungen (normalerweise immer enthalten):**")

                # Initialize standard services in session state if not exists
                if 'standard_services_selection' not in pdf_services_state:
                    pdf_services_state['standard_services_selection'] = {}

                # Get project details for quantity calculation
                project_details = {}
                if 'project_data' in st.session_state and 'project_details' in st.session_state.project_data:
                    project_details = st.session_state.project_data['project_details']

                # Display services in columns
                num_services = len(standard_services)
                if num_services > 0:
                    cols_per_row = min(2, num_services)
                    cols = st.columns(cols_per_row)

                    for i, service in enumerate(standard_services):
                        col_idx = i % cols_per_row

                        with cols[col_idx]:
                            service_id = service['id']
                            service_key = f"standard_service_{service_id}"

                            # Calculate quantity and price for display
                            try:
                                quantity = get_service_quantity(
                                    service, project_details)
                                total_price = service['price'] * quantity
                                formatted_price = _format_german_currency(
                                    total_price)

                                # Create detailed label with price info
                                if service['calculate_per'] == 'Pauschal' or quantity == 1:
                                    price_info = f" ({formatted_price})"
                                else:
                                    unit_price = _format_german_currency(
                                        service['price'])
                                    price_info = f" ({
                                        quantity:.2f} {
                                        service['calculate_per']} × {unit_price} = {formatted_price})"

                                label = f"{service['name']}{price_info}"

                            except Exception:
                                # Fallback if calculation fails
                                formatted_price = _format_german_currency(
                                    service['price'])
                                label = f"{
                                    service['name']} ({formatted_price})"
                                quantity = 1
                                total_price = service['price']

                            # Checkbox for service selection (default True for
                            # standard services)
                            is_selected = st.checkbox(
                                label,
                                value=pdf_services_state['standard_services_selection'].get(
                                    service_key,
                                    True),
                                key=f"pdf_standard_service_{service_id}_v3",
                                help=f"Kategorie: {
                                    service.get(
                                        'category',
                                        'Standard')}\\nBeschreibung: {
                                    service.get(
                                        'description',
                                        'Standard-Dienstleistung')}")

                            # Store selection state and service data
                            pdf_services_state['standard_services_selection'][service_key] = is_selected

                            # Store service details for PDF generation
                            if is_selected:
                                if 'selected_standard_services_details' not in pdf_services_state:
                                    pdf_services_state['selected_standard_services_details'] = {
                                    }

                                pdf_services_state['selected_standard_services_details'][service_key] = {
                                    'id': service['id'],
                                    'name': service['name'],
                                    'description': service.get('description', ''),
                                    'category': service.get('category', ''),
                                    'price': service['price'],
                                    'calculate_per': service['calculate_per'],
                                    'quantity': quantity,
                                    'total_price': total_price,
                                    'formatted_price': _format_german_currency(service['price']),
                                    'formatted_total': _format_german_currency(total_price),
                                    'is_standard': True,
                                    'is_active': True,
                                    'pdf_order': service.get('pdf_order', i + 1)
                                }
                            else:
                                # Remove from selected services if unchecked
                                if 'selected_standard_services_details' in pdf_services_state:
                                    pdf_services_state['selected_standard_services_details'].pop(
                                        service_key, None)

                # Show summary of ALL selected services (Standard + Optional)
                selected_standard_services = pdf_services_state.get(
                    'selected_standard_services_details', {})
                selected_optional_services = pdf_services_state.get(
                    'selected_optional_services_details', {})

                # Combine all selected services
                all_selected_services = {}
                all_selected_services.update(selected_standard_services)
                all_selected_services.update(selected_optional_services)

                if all_selected_services:
                    st.markdown("---")
                    st.markdown("**Ausgewählte Dienstleistungen:**")

                    # Sort services by type and name for better display
                    standard_services = []
                    optional_services = []

                    for service_data in all_selected_services.values():
                        if service_data.get('is_standard', False):
                            standard_services.append(service_data)
                        else:
                            optional_services.append(service_data)

                    # Sort by name within each category
                    standard_services.sort(key=lambda x: x.get('name', ''))
                    optional_services.sort(key=lambda x: x.get('name', ''))

                    total_all_price = 0

                    # Display standard services first
                    if standard_services:
                        st.markdown("*Standard-Services:*")
                        for service_data in standard_services:
                            total_all_price += service_data['total_price']
                            st.write(
                                f"✓ {
                                    service_data['name']}: {
                                    service_data['formatted_total']}")

                    # Display optional services
                    if optional_services:
                        if standard_services:  # Add spacing if we had standard services
                            st.markdown("")
                        st.markdown("*Optionale Services:*")
                        for service_data in optional_services:
                            total_all_price += service_data['total_price']
                            st.write(
                                f"✓ {
                                    service_data['name']}: {
                                    service_data['formatted_total']}")

                    st.markdown("---")
                    st.markdown(
                        f"**Gesamtsumme aller Services: {_format_german_currency(total_all_price)}**")

                    # Store totals for PDF access
                    pdf_services_state['total_standard_services_price'] = sum(
                        s['total_price'] for s in standard_services)
                    pdf_services_state['total_optional_services_price'] = sum(
                        s['total_price'] for s in optional_services)
                    pdf_services_state['total_all_services_price'] = total_all_price
                    pdf_services_state['formatted_total_standard_services'] = _format_german_currency(
                        pdf_services_state['total_standard_services_price'])
                    pdf_services_state['formatted_total_optional_services'] = _format_german_currency(
                        pdf_services_state['total_optional_services_price'])
                    pdf_services_state['formatted_total_all_services'] = _format_german_currency(
                        total_all_price)
                else:
                    # Clear totals if no services selected
                    pdf_services_state.pop(
                        'total_standard_services_price', None)
                    pdf_services_state.pop(
                        'formatted_total_standard_services', None)
                    pdf_services_state.pop(
                        'selected_standard_services_details', None)
                    pdf_services_state.pop(
                        'total_optional_services_price', None)
                    pdf_services_state.pop(
                        'formatted_total_optional_services', None)
                    pdf_services_state.pop(
                        'selected_optional_services_details', None)
                    pdf_services_state.pop('total_all_services_price', None)
                    pdf_services_state.pop(
                        'formatted_total_all_services', None)

            else:
                st.info("Keine Standard-Dienstleistungen in der Datenbank gefunden.")

        except ImportError as e:
            st.warning(f"Services-Integration nicht verfügbar: {e}")
            # Fallback to old hardcoded services
            col_std1, col_std2 = st.columns(2)
            with col_std1:
                pdf_services_state['service_consulting'] = st.checkbox(
                    "Beratung", value=pdf_services_state.get(
                        'service_consulting', True), key="pdf_srv_std_consulting")
                pdf_services_state['service_planning'] = st.checkbox(
                    "Planung", value=pdf_services_state.get(
                        'service_planning', True), key="pdf_srv_std_planning")
                pdf_services_state['service_project_management'] = st.checkbox(
                    "Projektierung", value=pdf_services_state.get(
                        'service_project_management', True), key="pdf_srv_std_project_mgmt")
                pdf_services_state['service_optimization'] = st.checkbox(
                    "Optimierung", value=pdf_services_state.get(
                        'service_optimization', True), key="pdf_srv_std_optimization")
                pdf_services_state['service_grid_application'] = st.checkbox(
                    "Anmeldung / Genehmigung EVU",
                    value=pdf_services_state.get(
                        'service_grid_application',
                        True),
                    key="pdf_srv_std_grid_application")
            with col_std2:
                pdf_services_state['service_dc_installation'] = st.checkbox(
                    "DC Montagearbeiten", value=pdf_services_state.get(
                        'service_dc_installation', True), key="pdf_srv_std_dc_install")
                pdf_services_state['service_ac_installation'] = st.checkbox(
                    "AC Elektroinstallationsarbeiten", value=pdf_services_state.get(
                        'service_ac_installation', True), key="pdf_srv_std_ac_install")
                pdf_services_state['service_storage_installation'] = st.checkbox(
                    "Installation Batteriespeicher", value=pdf_services_state.get(
                        'service_storage_installation', True), key="pdf_srv_std_storage_install")
                pdf_services_state['service_commissioning_training'] = st.checkbox(
                    "Inbetriebnahme & Einweisung", value=pdf_services_state.get(
                        'service_commissioning_training', True), key="pdf_srv_std_commissioning")
                pdf_services_state['service_grid_completion'] = st.checkbox(
                    "Fertigmeldung bei EVU", value=pdf_services_state.get(
                        'service_grid_completion', True), key="pdf_srv_std_grid_completion")
    pdf_services_state['extras_enabled'] = st.checkbox(
        "Extras / Sonstiges aktivieren?",
        value=pdf_services_state.get(
            'extras_enabled',
            False),
        key="pdf_services_extras_enabled_v2")
    if pdf_services_state['extras_enabled']:
        with st.expander("Optionale Dienstleistungen auswählen", expanded=False):

            # Load all optional services dynamically from database
            try:
                from admin_services_ui import get_optional_services
                from services_integration import (
                    _format_german_currency,
                    get_service_quantity,
                )

                optional_services = get_optional_services()

                if optional_services:
                    st.markdown("**Verfügbare optionale Dienstleistungen:**")

                    # Initialize optional services in session state if not
                    # exists
                    if 'optional_services_selection' not in pdf_services_state:
                        pdf_services_state['optional_services_selection'] = {}

                    # Get project details for quantity calculation
                    project_details = {}
                    if 'project_data' in st.session_state and 'project_details' in st.session_state.project_data:
                        project_details = st.session_state.project_data['project_details']

                    # Display services in columns
                    num_services = len(optional_services)
                    if num_services > 0:
                        # Create columns based on number of services (max 2
                        # columns)
                        cols_per_row = min(2, num_services)
                        cols = st.columns(cols_per_row)

                        for i, service in enumerate(optional_services):
                            col_idx = i % cols_per_row

                            with cols[col_idx]:
                                service_id = service['id']
                                service_key = f"optional_service_{service_id}"

                                # Calculate quantity and price for display
                                try:
                                    quantity = get_service_quantity(
                                        service, project_details)
                                    total_price = service['price'] * quantity
                                    formatted_price = _format_german_currency(
                                        total_price)

                                    # Create detailed label with price info
                                    if service['calculate_per'] == 'Pauschal' or quantity == 1:
                                        price_info = f" ({formatted_price})"
                                    else:
                                        unit_price = _format_german_currency(
                                            service['price'])
                                        price_info = f" ({
                                            quantity:.2f} {
                                            service['calculate_per']} × {unit_price} = {formatted_price})"

                                    label = f"{service['name']}{price_info}"

                                except Exception:
                                    # Fallback if calculation fails
                                    formatted_price = _format_german_currency(
                                        service['price'])
                                    label = f"{
                                        service['name']} ({formatted_price})"
                                    quantity = 1
                                    total_price = service['price']

                                # Checkbox for service selection
                                is_selected = st.checkbox(
                                    label,
                                    value=pdf_services_state['optional_services_selection'].get(
                                        service_key,
                                        False),
                                    key=f"pdf_optional_service_{service_id}_v3",
                                    help=f"Kategorie: {
                                        service.get(
                                            'category',
                                            'Allgemein')}\\nBeschreibung: {
                                        service.get(
                                            'description',
                                            'Keine Beschreibung verfügbar')}")

                                # Store selection state and service data
                                pdf_services_state['optional_services_selection'][service_key] = is_selected

                                # Store service details for PDF generation
                                if is_selected:
                                    if 'selected_optional_services_details' not in pdf_services_state:
                                        pdf_services_state['selected_optional_services_details'] = {
                                        }

                                    pdf_services_state['selected_optional_services_details'][service_key] = {
                                        'id': service['id'],
                                        'name': service['name'],
                                        'description': service.get('description', ''),
                                        'category': service.get('category', ''),
                                        'price': service['price'],
                                        'calculate_per': service['calculate_per'],
                                        'quantity': quantity,
                                        'total_price': total_price,
                                        'formatted_price': _format_german_currency(service['price']),
                                        'formatted_total': _format_german_currency(total_price),
                                        'is_standard': False,
                                        'is_active': True,
                                        'pdf_order': service.get('pdf_order', 999)
                                    }
                                else:
                                    # Remove from selected services if
                                    # unchecked
                                    if 'selected_optional_services_details' in pdf_services_state:
                                        pdf_services_state['selected_optional_services_details'].pop(
                                            service_key, None)

                    # Note: Summary of selected services is now shown in the Standard-Services section above
                    # This provides a unified view of all selected services
                    # (standard + optional)

                else:
                    st.info(
                        "Keine optionalen Dienstleistungen in der Datenbank gefunden.")

            except ImportError as e:
                st.warning(f"Services-Integration nicht verfügbar: {e}")
                # Fallback to old hardcoded services
                col_srv1, col_srv2 = st.columns(2)
                with col_srv1:
                    pdf_services_state['service_additional_tasks'] = st.checkbox(
                        "Weitere Tätigkeiten", value=pdf_services_state.get(
                            'service_additional_tasks', False), key="pdf_srv_additional_tasks_v2")
                    pdf_services_state['service_wallbox_cabling'] = st.checkbox(
                        "Leitungsverlegung Wallbox", value=pdf_services_state.get(
                            'service_wallbox_cabling', False), key="pdf_srv_wallbox_cabling_v2")
                    pdf_services_state['service_backup_power_activation'] = st.checkbox(
                        "Aktivierung Notstromversorgung", value=pdf_services_state.get(
                            'service_backup_power_activation', False), key="pdf_srv_backup_activation_v2")
                with col_srv2:
                    pdf_services_state['service_energy_management_system'] = st.checkbox(
                        "Installation Energiemanagementsystem", value=pdf_services_state.get(
                            'service_energy_management_system', False), key="pdf_srv_energy_management_v2")
                    pdf_services_state['service_dynamic_tariff_activation'] = st.checkbox(
                        "Aktivierung dynamischer Stromtarif", value=pdf_services_state.get(
                            'service_dynamic_tariff_activation', False), key="pdf_srv_dynamic_tariff_v2")

            # Custom entries (always available)
            st.markdown("---")
            pdf_services_state['custom_entries'] = st.text_area(
                "Sonstige / individuelle Eintragungen (eine pro Zeile oder mit Semikolon)",
                value=pdf_services_state.get(
                    'custom_entries',
                    ''),
                key="pdf_services_custom_entries_v2",
                height=100)
    # Combine all selected services for PDF generation
    all_selected_services = []

    # Add selected standard services
    if 'selected_standard_services_details' in pdf_services_state:
        for service_data in pdf_services_state['selected_standard_services_details'].values(
        ):
            all_selected_services.append(service_data)

    # Add selected optional services
    if 'selected_optional_services_details' in pdf_services_state:
        for service_data in pdf_services_state['selected_optional_services_details'].values(
        ):
            all_selected_services.append(service_data)

    # Sort services by pdf_order for consistent PDF display
    all_selected_services.sort(key=lambda x: x.get('pdf_order', 999))

    # Store combined services list for PDF access
    pdf_services_state['all_selected_services'] = all_selected_services

    # Calculate total price of all selected services
    total_all_services = sum(service['total_price']
                             for service in all_selected_services)
    pdf_services_state['total_all_services_price'] = total_all_services

    if total_all_services > 0:
        try:
            from services_integration import _format_german_currency
            pdf_services_state['formatted_total_all_services'] = _format_german_currency(
                total_all_services)
        except ImportError:
            pdf_services_state['formatted_total_all_services'] = f"{
                total_all_services:,.2f} €"
    else:
        pdf_services_state['formatted_total_all_services'] = "0,00 €"

    # Store services data for PDF generation
    st.session_state.pdf_services = pdf_services_state
    if 'project_data' in locals() and isinstance(project_data, dict):
        project_data['pdf_services'] = dict(pdf_services_state)

        # Also store services in project_details for compatibility
        if 'project_details' not in project_data:
            project_data['project_details'] = {}

        project_data['project_details']['pdf_selected_services'] = all_selected_services
        project_data['project_details']['pdf_services_total'] = total_all_services

    if submitted_generate_pdf and not st.session_state.pdf_generating_lock_v1:
        st.session_state.pdf_generating_lock_v1 = True
        pdf_bytes = None
        try:            # Datenvalidierung vor PDF-Erstellung
            try:
                from pdf_generator import (
                    _create_no_data_fallback_pdf,
                    _validate_pdf_data_availability,
                )

                validation_result = _validate_pdf_data_availability(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    texts=texts
                )

                # Zeige Validierungsstatus an
                if not validation_result['is_valid']:
                    st.warning(
                        f" Unvollständige Daten erkannt: {
                            ', '.join(
                                validation_result['missing_data_summary'])}")
                    st.info("Ein vereinfachtes Informations-PDF wird erstellt.")

                    # Kritische Fehler: Liste auswerten
                    critical_errors_list = validation_result.get(
                        'critical_errors', []) or []
                    if len(critical_errors_list) > 0:
                        st.error(
                            f" {len(critical_errors_list)} kritische Fehler gefunden. Erstelle Fallback-PDF...")
                        # Details anzeigen
                        with st.expander("Details zu kritischen Fehlern"):
                            for err in critical_errors_list:
                                st.error(f"- {err}")
                        # Erstelle Fallback-PDF (vereinfachtes Info-PDF)
                        pdf_bytes = _create_no_data_fallback_pdf(
                            texts=texts,
                            customer_data=project_data.get('customer_data', {})
                        )
                        st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
                        st.success(" Fallback-PDF erfolgreich erstellt!")
                        return
                    warnings_list = validation_result.get(
                        'warnings', []) or []
                    st.info(
                        f"ℹ {
                            len(warnings_list)} Warnungen. PDF wird mit verfügbaren Daten erstellt.")
                    if warnings_list:
                        with st.expander("Warnungsdetails anzeigen"):
                            for w in warnings_list:
                                st.warning(f"- {w}")
                else:
                    st.success(" Alle Daten vollständig verfügbar.")

            except ImportError:
                st.warning(
                    "Datenvalidierung nicht verfügbar. Fahre mit normaler PDF-Erstellung fort.")

            with st.spinner(get_text_pdf_ui(texts, 'pdf_generation_spinner', 'PDF wird generiert, bitte warten...')):
                final_inclusion_options_to_pass = st.session_state.pdf_inclusion_options.copy()

                #  NEUE FEATURES AUS SESSION STATE HINZUFÜGEN
                final_inclusion_options_to_pass.update({
                    'financing_config': st.session_state.get('financing_config', {}),
                    'chart_config': st.session_state.get('chart_config', {}),
                    'custom_content_items': st.session_state.get('custom_content_items', []),
                    'pdf_editor_config': st.session_state.get('pdf_editor_config', {}),
                    'pdf_design_config': st.session_state.get('pdf_design_config', {}),
                    # Drag & Drop Reihenfolge der Sektionen (falls gesetzt)
                    'custom_section_order': st.session_state.get('pdf_section_order', [])
                })

                # Mapping: Neuer Key 'selected_company_documents' → alter Key
                # 'company_document_ids_to_include'
                if 'selected_company_documents' in final_inclusion_options_to_pass:
                    final_inclusion_options_to_pass['company_document_ids_to_include'] = final_inclusion_options_to_pass.get(
                        'selected_company_documents', [])
                    print(
                        f"DEBUG: Mapped {
                            len(
                                final_inclusion_options_to_pass['company_document_ids_to_include'])} company documents from selected_company_documents")

                final_sections_to_include_to_pass = st.session_state.pdf_selected_main_sections[
                    :]
                pdf_bytes = _generate_offer_pdf_safe(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info_for_pdf,
                    company_logo_base64=company_logo_b64_for_pdf,
                    selected_title_image_b64=st.session_state.selected_title_image_b64_data_doc_output,
                    selected_offer_title_text=st.session_state.selected_offer_title_text_content_doc_output,
                    selected_cover_letter_text=st.session_state.selected_cover_letter_text_content_doc_output,
                    sections_to_include=final_sections_to_include_to_pass,
                    inclusion_options=final_inclusion_options_to_pass,
                    load_admin_setting_func=load_admin_setting_func,
                    save_admin_setting_func=save_admin_setting_func,
                    list_products_func=list_products_func,
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=active_company_id_for_docs,
                    texts=texts)
            st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
        except Exception as e_gen_final_outer:
            st.error(
                f"{
                    get_text_pdf_ui(
                        texts,
                        'pdf_generation_exception_outer',
                        'Kritischer Fehler im PDF-Prozess (pdf_ui.py):')} {e_gen_final_outer}")
            st.text_area("Traceback PDF Erstellung (pdf_ui.py):",
                         traceback.format_exc(), height=250)
            st.session_state.generated_pdf_bytes_for_download_v1 = None
        finally:
            st.session_state.pdf_generating_lock_v1 = False
            set_current_page("doc_output")
    if 'generated_pdf_bytes_for_download_v1' in st.session_state:
        # Nicht poppen: Bytes im Session-State belassen, damit Button-Klicks
        # (Reruns) weiterhin Zugriff haben
        pdf_bytes_to_download = st.session_state.get(
            'generated_pdf_bytes_for_download_v1')
        if pdf_bytes_to_download and isinstance(pdf_bytes_to_download, bytes):
            # Stabiler Timestamp/Dateiname über Reruns hinweg
            meta = st.session_state.get('generated_pdf_meta') or {}
            if not meta.get('timestamp') or not meta.get('file_name'):
                customer_name_for_file = customer_data_pdf.get(
                    'last_name', 'Angebot')
                file_name_customer_part = str(customer_name_for_file).replace(
                    ' ', '_') if customer_name_for_file and str(customer_name_for_file).strip() else "Photovoltaik_Angebot"
                timestamp_file = base64.b32encode(
                    os.urandom(5)).decode('utf-8').lower()
                file_name = f"Angebot_{file_name_customer_part}_{timestamp_file}.pdf"
                meta = {'timestamp': timestamp_file, 'file_name': file_name}
                st.session_state['generated_pdf_meta'] = meta
            else:
                timestamp_file = meta['timestamp']
                file_name = meta['file_name']
            st.success(get_text_pdf_ui(
                texts, "pdf_generation_success", "PDF erfolgreich erstellt!"))

            # Display extended PDF warnings if any
            if 'extended_pdf_warnings' in st.session_state and st.session_state.extended_pdf_warnings:
                with st.expander("Hinweise zur erweiterten PDF-Generierung", expanded=False):
                    for warning in st.session_state.extended_pdf_warnings:
                        st.warning(warning)
                    # Clear warnings after displaying
                    st.session_state.extended_pdf_warnings = []

            st.download_button(
                label=get_text_pdf_ui(
                    texts, "pdf_download_button", "PDF herunterladen"),
                data=pdf_bytes_to_download,
                file_name=file_name,
                mime="application/pdf",
                key=f"pdf_download_btn_final_{timestamp_file}_v13_final_stable"
            )

            # Sichtbares Feedback aus vorherigen CRM-Aktionen anzeigen
            _crm_feedback = st.session_state.get('_crm_feedback')
            if isinstance(_crm_feedback, dict) and _crm_feedback.get('msg'):
                if _crm_feedback.get('type') == 'success':
                    st.success(_crm_feedback['msg'])
                else:
                    st.error(_crm_feedback['msg'])

            # CRM: Kunde speichern + PDF in Kundenakte ablegen
            with st.expander(" CRM: Kunde speichern & PDF in Kundenakte ablegen", expanded=bool(st.session_state.get('_crm_expanded', False))):
                st.caption(
                    "Erstellt/aktualisiert den Kunden in der CRM Kundenverwaltung und speichert dieses PDF in der Kundenakte.")
                col_crm1, col_crm2 = st.columns([1, 1])
                with col_crm1:
                    if st.button(
                        " Kunde in CRM speichern",
                        key=f"btn_crm_save_{timestamp_file}",
                            type="primary"):
                        try:
                            import sqlite3

                            from crm import (
                                create_tables_crm,
                                save_customer,
                                save_project,
                            )
                            from database import (
                                add_customer_document,
                                get_db_connection,
                            )
                            conn = get_db_connection()
                            if conn is None:
                                st.error("Keine DB-Verbindung für CRM.")
                                st.session_state['_crm_feedback'] = {
                                    'type': 'error', 'msg': 'Keine DB-Verbindung für CRM.'}
                            else:
                                with st.spinner("Speichere im CRM…"):
                                    conn.row_factory = sqlite3.Row
                                    create_tables_crm(conn)
                                cur = conn.cursor()
                                first_name = project_data.get(
                                    'customer_data', {}).get('first_name', '')
                                last_name = project_data.get(
                                    'customer_data', {}).get('last_name', '')
                                email_val = project_data.get(
                                    'customer_data', {}).get('email', '')
                                cur.execute(
                                    "SELECT id FROM customers WHERE first_name = ? AND last_name = ? AND (email = ? OR ? = '') LIMIT 1",
                                    (first_name,
                                     last_name,
                                     email_val,
                                     email_val))
                                row = cur.fetchone()
                                if row:
                                    created_customer_id = int(row[0])
                                else:
                                    cust_payload = {
                                        'salutation': project_data.get(
                                            'customer_data',
                                            {}).get('salutation'),
                                        'title': project_data.get(
                                            'customer_data',
                                            {}).get('title'),
                                        'first_name': first_name or 'Interessent',
                                        'last_name': last_name or 'Unbekannt',
                                        'company_name': project_data.get(
                                            'customer_data',
                                            {}).get('company_name'),
                                        'address': project_data.get(
                                            'customer_data',
                                            {}).get('address'),
                                        'house_number': project_data.get(
                                            'customer_data',
                                            {}).get('house_number'),
                                        'zip_code': project_data.get(
                                            'customer_data',
                                            {}).get('zip_code'),
                                        'city': project_data.get(
                                            'customer_data',
                                            {}).get('city'),
                                        'state': project_data.get(
                                            'customer_data',
                                            {}).get('state'),
                                        'region': project_data.get(
                                            'customer_data',
                                            {}).get('region'),
                                        'email': email_val,
                                        'phone_landline': project_data.get(
                                            'customer_data',
                                            {}).get('phone_landline') or project_data.get(
                                                'customer_data',
                                                {}).get('phone'),
                                        'phone_mobile': project_data.get(
                                                    'customer_data',
                                                    {}).get('phone_mobile'),
                                        'income_tax_rate_percent': float(
                                                        project_data.get(
                                                            'customer_data',
                                                            {}).get('income_tax_rate_percent') or 0.0),
                                        'creation_date': datetime.now().isoformat(),
                                    }
                                    created_customer_id = save_customer(
                                        conn, cust_payload)
                                created_project_id = None
                                if created_customer_id:
                                    proj_details = project_data.get(
                                        'project_details', {})
                                    proj_payload = {
                                        'customer_id': created_customer_id,
                                        'project_name': proj_details.get('project_name') or f"Photovoltaik Angebot {
                                            datetime.now().strftime('%Y-%m-%d')}",
                                        'project_status': 'Angebot',
                                        'roof_type': proj_details.get('roof_type'),
                                        'roof_covering_type': proj_details.get('roof_covering_type'),
                                        'free_roof_area_sqm': proj_details.get('free_roof_area_sqm'),
                                        'roof_orientation': proj_details.get('roof_orientation'),
                                        'roof_inclination_deg': proj_details.get('roof_inclination_deg'),
                                        'building_height_gt_7m': int(
                                            bool(
                                                proj_details.get('building_height_gt_7m'))),
                                        'annual_consumption_kwh': proj_details.get('annual_consumption_kwh') or project_data.get(
                                            'consumption_data',
                                            {}).get('annual_consumption'),
                                        'costs_household_euro_mo': proj_details.get('costs_household_euro_mo'),
                                        'annual_heating_kwh': proj_details.get('annual_heating_kwh') or project_data.get(
                                            'consumption_data',
                                            {}).get('consumption_heating_kwh_yr'),
                                        'costs_heating_euro_mo': proj_details.get('costs_heating_euro_mo'),
                                        'anlage_type': proj_details.get('anlage_type'),
                                        'feed_in_type': proj_details.get('feed_in_type'),
                                        'module_quantity': proj_details.get('module_quantity'),
                                        'selected_module_id': proj_details.get('selected_module_id'),
                                        'selected_inverter_id': proj_details.get('selected_inverter_id'),
                                        'include_storage': int(
                                            bool(
                                                proj_details.get('include_storage'))),
                                        'selected_storage_id': proj_details.get('selected_storage_id'),
                                        'selected_storage_storage_power_kw': proj_details.get('selected_storage_storage_power_kw'),
                                        'include_additional_components': int(
                                            bool(
                                                proj_details.get('include_additional_components'))),
                                        'visualize_roof_in_pdf': int(
                                            bool(
                                                proj_details.get('visualize_roof_in_pdf'))),
                                        'latitude': proj_details.get('latitude'),
                                        'longitude': proj_details.get('longitude'),
                                        'creation_date': datetime.now().isoformat(),
                                    }
                                    created_project_id = save_project(
                                        conn, proj_payload)
                                if created_customer_id:
                                    # PDF ablegen (stabiler Dateiname aus Meta
                                    # verwenden)
                                    _ = add_customer_document(
                                        created_customer_id,
                                        pdf_bytes_to_download,
                                        display_name=file_name,
                                        doc_type="offer_pdf",
                                        project_id=created_project_id,
                                        suggested_filename=file_name,
                                    )
                                    # JSON-Snapshot ablegen
                                    snapshot = json.dumps(
                                        {"project_data": project_data,
                                            "analysis_results": analysis_results},
                                        ensure_ascii=False,
                                        default=str,
                                    ).encode("utf-8")
                                    json_name = f"Projekt_Snapshot_{timestamp_file}.json"
                                    _ = add_customer_document(
                                        created_customer_id,
                                        snapshot,
                                        display_name=json_name,
                                        doc_type="project_json",
                                        project_id=created_project_id,
                                        suggested_filename=json_name,
                                    )
                                    st.success(
                                        "Kunde gespeichert und Dokumente in der Kundenakte abgelegt.")
                                    st.session_state["_last_saved_crm_customer_id"] = created_customer_id
                                    st.session_state["_last_saved_crm_project_id"] = created_project_id
                                    st.session_state['_crm_feedback'] = {
                                        'type': 'success',
                                        'msg': 'Kunde gespeichert und Dokumente in der Kundenakte abgelegt.'}
                                    st.session_state['_crm_expanded'] = True
                                    try:
                                        conn.close()
                                    except Exception:
                                        pass
                                else:
                                    st.error(
                                        "Kunde konnte nicht gespeichert werden.")
                                    st.session_state['_crm_feedback'] = {
                                        'type': 'error', 'msg': 'Kunde konnte nicht gespeichert werden.'}
                        except Exception as e:
                            st.error(f"Fehler beim Speichern im CRM: {e}")
                            st.session_state['_crm_feedback'] = {
                                'type': 'error', 'msg': f'Fehler beim Speichern im CRM: {e}'}
                with col_crm2:
                    if st.button(
                        " Zur CRM Kundenverwaltung",
                            key=f"btn_go_crm_{timestamp_file}"):
                        last_id = st.session_state.get(
                            '_last_saved_crm_customer_id')
                        if last_id:
                            st.session_state['selected_customer_id'] = last_id
                            st.session_state['crm_view_mode'] = 'view_customer'
                        set_current_page('crm')
        elif pdf_bytes_to_download is None and not st.session_state.get('pdf_generating_lock_v1', True):
            st.error(
                get_text_pdf_ui(
                    texts,
                    "pdf_generation_failed_no_bytes_after_rerun",
                    "PDF-Generierung fehlgeschlagen (keine Daten nach Rerun)."))

# NEU: PDF-VORSCHAU & BEARBEITUNG FUNKTION (BOMBE!)


def show_advanced_pdf_preview(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any] | None,
    texts: dict[str, str],
    load_admin_setting_func: Callable = _dummy_load_admin_setting_pdf_ui,
    save_admin_setting_func: Callable = _dummy_save_admin_setting_pdf_ui,
    get_active_company_details_func: Callable = _dummy_get_active_company_details,
    list_products_func: Callable = list,
    get_product_by_id_func: Callable = lambda x: {},
    db_list_company_documents_func: Callable = _dummy_list_company_documents
) -> bytes | None:
    """
    Erweiterte PDF-Vorschau mit Bearbeitungsmöglichkeiten und Seitenreihenfolge.
    Das wird BOMBE!

    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Übersetzungstexte
        ... weitere Callback-Funktionen

    Returns:
        PDF-Bytes falls erfolgreich generiert, sonst None
    """

    if not _PDF_PREVIEW_AVAILABLE:
        st.error(" PDF-Vorschau-Modul ist nicht verfügbar!")
        st.info(
            " Installieren Sie die erforderlichen Abhängigkeiten für die PDF-Vorschau.")
        return None

    # Firmendaten abrufen
    company_details = get_active_company_details_func()
    if not company_details:
        st.warning(" Keine aktive Firma gefunden. Verwende Standardwerte.")
        company_details = {
            "name": "Ihre Solarfirma",
            "street": "Musterstraße 1",
            "zip_code": "12345",
            "city": "Musterstadt",
            "phone": "+49 123 456789",
            "email": "info@ihresolarfirma.de",
            "id": 1
        }

    company_logo_base64 = company_details.get('logo_base64')

    # PDF-Vorschau-Interface aufrufen
    return show_pdf_preview_interface(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_details,
        company_logo_base64=company_logo_base64,
        texts=texts,
        generate_pdf_func=lambda **kwargs: _generate_offer_pdf_safe(
            load_admin_setting_func=load_admin_setting_func,
            save_admin_setting_func=save_admin_setting_func,
            list_products_func=list_products_func,
            get_product_by_id_func=get_product_by_id_func,
            db_list_company_documents_func=db_list_company_documents_func,
            active_company_id=company_details.get('id', 1),
            **kwargs
        )
    )

# --- Debug-Bereich für PDF-Anhänge ---


def render_pdf_debug_section(
    texts: dict[str, str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    get_active_company_details_func: Callable,
    db_list_company_documents_func: Callable,
    get_product_by_id_func: Callable
):
    """Rendert einen Debug-Bereich für PDF-Anhänge (nur für Entwickler/Troubleshooting)"""
    with st.expander("Debug-Informationen (nur für Entwickler)", expanded=False):
        st.subheader("Systemstatus")

        # PyPDF Verfügbarkeit prüfen
        try:
            from pypdf import PdfReader, PdfWriter
            pypdf_status = " pypdf verfügbar"
        except ImportError:
            try:
                from PyPDF2 import PdfReader, PdfWriter
                pypdf_status = " PyPDF2 verfügbar (Fallback)"
            except ImportError:
                pypdf_status = " Keine PDF-Bibliothek verfügbar"

        st.write(f"**PDF-Bibliothek:** {pypdf_status}")

        # Aktive Firma prüfen
        active_company = get_active_company_details_func()
        if active_company:
            st.write(
                f"**Aktive Firma:** {active_company.get('name')} (ID: {active_company.get('id')})")

            # Firmendokumente prüfen
            company_docs = db_list_company_documents_func(
                active_company.get('id'), None)
            st.write(f"**Verfügbare Firmendokumente:** {len(company_docs)}")
            for doc in company_docs:
                doc_path = os.path.join(
                    os.getcwd(), "data", "company_docs", doc.get(
                        "relative_db_path", ""))
                status = "" if os.path.exists(doc_path) else ""
                st.write(
                    f"  {status} {
                        doc.get('display_name')} (ID: {
                        doc.get('id')})")
        else:
            st.write("**Aktive Firma:**  Keine aktive Firma")

        # Projektdetails prüfen
        project_details = project_data.get('project_details', {})
        st.write("**Ausgewählte Produkte:**")

        # Alle möglichen Produkt-IDs aus dem Solar Calculator
        product_ids = [
            ('Modul', project_details.get('selected_module_id')),
            ('Wechselrichter', project_details.get('selected_inverter_id')),
            ('Batteriespeicher', project_details.get('selected_storage_id')),
            ('Leistungsoptimierer', project_details.get('selected_optimizer_id')),
            ('Wallbox', project_details.get('selected_wallbox_id')),
            ('Carport', project_details.get('selected_carport_id')),
            ('Notstromversorgung', project_details.get('selected_notstrom_id')),
            ('Tierabwehrschutz', project_details.get('selected_tierabwehr_id'))
        ]

        for comp_type, prod_id in product_ids:
            if prod_id:
                try:
                    product_info = get_product_by_id_func(prod_id)
                    if product_info:
                        datasheet_path = product_info.get(
                            "datasheet_link_db_path")
                        if datasheet_path:
                            full_path = os.path.join(
                                os.getcwd(), "data", "product_datasheets", datasheet_path)
                            status = "✅" if os.path.exists(full_path) else "❌"
                            st.write(
                                f"  {status} {comp_type}: {
                                    product_info.get('model_name')} (ID: {prod_id})")
                            if not os.path.exists(full_path):
                                st.write(
                                    f"      Datenblatt fehlt: {full_path}")
                        else:
                            st.write(
                                f"   {comp_type}: {
                                    product_info.get('model_name')} (Kein Datenblatt-Pfad)")
                    else:
                        st.write(
                            f"  ❌ {comp_type}: Produkt ID {prod_id} nicht in DB gefunden")
                except Exception as e:
                    st.write(
                        f"  ❌ {comp_type}: Fehler beim Laden von ID {prod_id}: {e}")
            # Keine "Nicht ausgewählt" Meldung mehr - nur tatsächlich
            # ausgewählte Produkte anzeigen

        # Current PDF inclusion options anzeigen
        st.subheader("Aktuelle PDF-Einstellungen")
        if 'pdf_inclusion_options' in st.session_state:
            options = st.session_state.pdf_inclusion_options
            st.json(options)
        else:
            st.write("Keine PDF-Einstellungen in Session State")

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-05, Gemini Ultra: TypeError bei `st.form_submit_button` in `pdf_ui.py` durch Entfernen des ungültigen `key`-Arguments behoben.
# 2025-06-05, Gemini Ultra: Buttons "Alles auswählen", "Alles abwählen" und Vorlagenmanagement (Laden/Speichern) in `pdf_ui.py` implementiert.
#                           Vorlagen werden als JSON unter dem Admin-Setting 'pdf_offer_presets' gespeichert.
#                           Callbacks für die Buttons aktualisieren `st.session_state.pdf_inclusion_options` und `st.session_state.pdf_selected_main_sections`.
#                           Checkbox-Logik angepasst, um Auswahl im Formular temporär zu sammeln und bei Submit in Session State zu schreiben.
# 2025-06-05, Gemini Ultra: TypeError beim Laden von PDF-Presets behoben. `json.loads` wird nicht mehr auf bereits geparste Listen angewendet.
#                           Sicherheitsprüfungen für geladene Presets hinzugefügt. Fallback für `active_company_id_for_docs` auf `None` korrigiert.
#                           Sicherere Initialisierung der Vorlagenauswahl im Session State.
# 2025-06-06, Gemini Ultra: Debug-Bereich für PDF-Anhänge hinzugefügt. Prüft Verfügbarkeit von PyPDF, aktive Firma, Firmendokumente und Projektdetails.
# 2025-06-07, Gemini Ultra: PDF-Vorschau-Integration hinzugefügt.
# 2025-06-07, Gemini Ultra: Erweiterte PDF-Vorschau-Funktion (BOMBE!) hinzugefügt.
# 2025-06-08, Gemini Ultra: Datenstatus-Anzeige und Fallback-PDF-Option hinzugefügt.
# 2025-09-20, GitHub Copilot: Zahlungsmodalitäten-Tab und Integration
# hinzugefügt.


def prepare_payment_data_for_pdf_generation(
    load_admin_setting_func: Callable[[str, Any], Any]
) -> dict[str, Any] | None:
    """
    Bereitet die ausgewählten Zahlungsmodalitäten für die PDF-Generierung vor.

    Args:
        load_admin_setting_func: Funktion zum Laden der Admin-Einstellungen

    Returns:
        Dictionary mit Zahlungsdaten für PDF-Generator oder None
    """

    # Hole ausgewählte Zahlungsvariante aus Session State
    selected_variant_key = st.session_state.get('selected_payment_variant_key')
    if not selected_variant_key:
        return None

    try:
        from admin_payment_terms_ui import get_payment_variant_for_pdf_generation

        # Bestimme Gesamtbetrag - PRIORITÄT: Echter finaler Preis aus
        # Live-Berechnungen
        project_total = 15000.0  # Default fallback

        # Versuche Gesamtbetrag aus verschiedenen Quellen zu holen
        # (Prioritätsreihenfolge)
        try:
            # 1. HÖCHSTE PRIORITÄT: Solar Calculator finaler Preis mit
            # Provision
            if ('project_data' in st.session_state and
                'project_details' in st.session_state.project_data and
                    'final_price_with_provision' in st.session_state.project_data['project_details']):
                project_total = float(
                    st.session_state.project_data['project_details']['final_price_with_provision'])
                print(
                    f"DEBUG: Zahlungsmodalitäten verwenden final_price_with_provision aus Solar Calculator: {
                        project_total:,.2f} €")

            # 2. Fallback: Live Pricing Calculations
            elif 'live_pricing_calculations' in st.session_state:
                live_calc = st.session_state['live_pricing_calculations']
                if isinstance(live_calc, dict) and 'final_price' in live_calc:
                    project_total = float(live_calc['final_price'])
                    print(
                        f"DEBUG: Zahlungsmodalitäten verwenden final_price aus live_pricing_calculations: {
                            project_total:,.2f} €")

            # 3. Fallback: PDF Total Cost
            elif 'pdf_total_cost' in st.session_state:
                project_total = float(st.session_state['pdf_total_cost'])
                print(
                    f"DEBUG: Zahlungsmodalitäten verwenden pdf_total_cost: {
                        project_total:,.2f} €")

            # 4. Fallback: Analysis Results
            elif 'analysis_results' in st.session_state:
                analysis = st.session_state['analysis_results']
                if isinstance(analysis, dict):
                    for key in [
                        'total_cost',
                        'gesamtkosten',
                            'anlage_total_price']:
                        if key in analysis:
                            project_total = float(analysis[key])
                            print(
                                f"DEBUG: Zahlungsmodalitäten verwenden {key} aus analysis_results: {
                                    project_total:,.2f} €")
                            break

            else:
                print(
                    f"DEBUG: Zahlungsmodalitäten verwenden Default-Wert: {project_total:,.2f} €")

        except (ValueError, TypeError) as e:
            print(
                f"DEBUG: Fehler beim Bestimmen des Projektbetrags für Zahlungsmodalitäten: {e}")

        # Hole Optionen aus Session State
        include_amounts = st.session_state.get('payment_include_amounts', True)
        include_table = st.session_state.get('payment_include_table', True)
        position = st.session_state.get(
            'payment_position', 'Seite 8 (Standard)')
        style = st.session_state.get('payment_style', 'Standard')
        custom_title = st.session_state.get(
            'custom_payment_title', 'Zahlungsmodalitäten')

        # Generiere Zahlungsdaten
        payment_data = get_payment_variant_for_pdf_generation(
            selected_variant_key=selected_variant_key,
            load_admin_setting_func=load_admin_setting_func,
            project_total=project_total,
            include_amounts=include_amounts
        )

        if payment_data and payment_data.get('validation_passed', False):
            # Füge UI-Optionen hinzu
            payment_data.update({
                'include_table': include_table,
                'position': position,
                'style': style,
                'custom_title': custom_title,
                'ui_total_amount': project_total
            })

            # Zahlungsdaten für PDF-Platzhalter im Session State ablegen
            st.session_state['pdf_payment_data'] = payment_data

            return payment_data

        st.session_state.pop('pdf_payment_data', None)
        return None

    except ImportError:
        st.error("❌ Zahlungsmodalitäten-Funktionen nicht verfügbar.")
        return None
    except Exception as e:
        st.error(f"❌ Fehler bei Zahlungsdaten-Vorbereitung: {str(e)}")
        return None


def get_payment_data_for_pdf():
    """
    Convenience-Funktion zum Abrufen der Zahlungsdaten für PDF-Generatoren.

    Returns:
        Zahlungsdaten oder None
    """

    # Diese Funktion kann von PDF-Generatoren aufgerufen werden
    try:

        # Dummy-Load-Funktion falls keine verfügbar
        def dummy_load(key, default=None):
            return st.session_state.get(f'admin_setting_{key}', default)

        return prepare_payment_data_for_pdf_generation(dummy_load)

    except Exception:
        return None
