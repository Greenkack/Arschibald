# pdf_generator_patch.py
"""
PATCH für bestehende PDF-Generatoren
Erweitert automatisch PDFs um ALLE ausgewählten Charts und Financial Tools

VERWENDUNG:
    from pdf_generator_patch import patch_pdf_generator
    
    # Vor PDF-Erstellung:
    analysis_results = patch_pdf_generator(
        project_data=project_data,
        calculation_results=calculation_results,
        analysis_results=analysis_results
    )
    
    # Dann normal PDF erstellen mit erweiterten analysis_results
"""

from __future__ import annotations

from typing import Any
import logging


def patch_pdf_generator(
    project_data: dict[str, Any],
    calculation_results: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    MASTER-PATCH: Bereitet analysis_results für vollständigen PDF-Export vor
    
    Sammelt ALLE Charts aus:
    - calculation_results (perform_calculations)
    - analysis_results (Analyse-Modul) 
    - advanced_charts (Neue Features)
    
    Args:
        project_data: Projektdaten
        calculation_results: Von perform_calculations()
        analysis_results: Von analysis.py
        
    Returns:
        Vollständige analysis_results mit ALLEN verfügbaren Charts
    """
    try:
        from pdf_integration_helper import prepare_complete_analysis_results
        
        complete_results = prepare_complete_analysis_results(
            project_data=project_data,
            calculation_results=calculation_results,
            analysis_results=analysis_results
        )
        
        logging.info("[OK] PDF-Generator gepatcht - Alle Charts verfügbar")
        return complete_results
        
    except Exception as e:
        logging.error(f"[ERROR] Fehler beim Patchen des PDF-Generators: {e}")
        # Fallback: Gib zumindest analysis_results zurück
        return analysis_results


def add_charts_to_pdf_fpdf(
    pdf: Any,  # FPDF instance
    pdf_options: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Fügt Charts zu einem bestehenden FPDF-PDF hinzu
    
    Args:
        pdf: FPDF-Instance
        pdf_options: PDF-Optionen mit selected_charts_for_pdf
        analysis_results: Vollständige Analysis Results
        
    Returns:
        Statistiken über hinzugefügte Charts
    """
    try:
        from pdf_integration_helper import integrate_selected_charts_into_pdf
        
        stats = integrate_selected_charts_into_pdf(
            pdf_generator=pdf,
            pdf_options=pdf_options,
            analysis_results=analysis_results
        )
        
        logging.info(f"[OK] {stats.get('charts_added', 0)} Charts ins PDF eingefügt")
        return stats
        
    except Exception as e:
        logging.error(f"[ERROR] Fehler beim Hinzufügen der Charts: {e}")
        return {'error': str(e)}


def ensure_all_charts_available(
    analysis_results: dict[str, Any]
) -> tuple[int, int]:
    """
    Zählt verfügbare vs. fehlende Charts
    
    Returns:
        Tuple (verfügbar, fehlend)
    """
    from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP
    
    all_chart_keys = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())
    
    available = 0
    missing = 0
    
    for chart_key in all_chart_keys:
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            available += 1
        else:
            missing += 1
    
    return available, missing


# ============================================================================
# AUTO-PATCH SYSTEM
# ============================================================================

def auto_patch_session_state():
    """
    AUTO-PATCH: Patcht Session State automatisch wenn Berechnung durchgeführt wurde
    
    Verwendung in admin_panel.py oder gui.py:
        from pdf_generator_patch import auto_patch_session_state
        
        # Nach perform_calculations():
        auto_patch_session_state()
    """
    try:
        import streamlit as st
        
        # Prüfe ob Daten vorhanden
        if 'project_data' not in st.session_state:
            return
        
        if 'calculation_results' not in st.session_state and 'analysis_results' not in st.session_state:
            return
        
        calculation_results = st.session_state.get('calculation_results', {})
        analysis_results = st.session_state.get('analysis_results', {})
        project_data = st.session_state.get('project_data', {})
        
        # Patch durchführen
        patched_results = patch_pdf_generator(
            project_data=project_data,
            calculation_results=calculation_results,
            analysis_results=analysis_results
        )
        
        # Zurückschreiben
        st.session_state.analysis_results = patched_results
        
        # Statistik
        available, missing = ensure_all_charts_available(patched_results)
        
        logging.info(f"[TOOL] Auto-Patch: {available} Charts verfügbar, {missing} fehlen noch")
        
    except Exception as e:
        logging.error(f"[ERROR] Fehler beim Auto-Patch: {e}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_all_available_charts(analysis_results: dict[str, Any]) -> list[str]:
    """
    Gibt Liste aller verfügbaren Chart-Keys zurück
    
    Args:
        analysis_results: Analysis Results
        
    Returns:
        Liste der verfügbaren Chart-Keys
    """
    from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP
    
    available_charts = []
    
    for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            available_charts.append(chart_key)
    
    return available_charts


def recommend_charts_for_project(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> list[str]:
    """
    Empfiehlt Charts basierend auf Projektdaten
    
    Args:
        project_data: Projektdaten
        analysis_results: Analysis Results
        
    Returns:
        Liste empfohlener Chart-Keys
    """
    recommended = []
    
    # Basis-Charts (immer empfohlen)
    basis_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'roi_chart_bytes',
        'energy_balance_chart_bytes',
    ]
    
    for chart_key in basis_charts:
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            recommended.append(chart_key)
    
    # Finanzierung wenn vorhanden
    project_details = project_data.get('project_details', {})
    if project_details.get('include_financing', False):
        financing_charts = [
            'financing_comparison_chart_bytes',
            'break_even_detailed_chart_bytes',
            'lifecycle_cost_chart_bytes',
        ]
        for chart_key in financing_charts:
            if chart_key in analysis_results and analysis_results[chart_key] is not None:
                recommended.append(chart_key)
    
    # Batterie wenn vorhanden
    if project_details.get('selected_storage_id'):
        battery_charts = [
            'battery_usage_chart_bytes',
            'self_consumption_chart_bytes',
        ]
        for chart_key in battery_charts:
            if chart_key in analysis_results and analysis_results[chart_key] is not None:
                recommended.append(chart_key)
    
    # Umwelt
    if 'co2_savings_chart_bytes' in analysis_results and analysis_results['co2_savings_chart_bytes'] is not None:
        recommended.append('co2_savings_chart_bytes')
    
    return recommended


# ============================================================================
# LOGGING HELPER
# ============================================================================

def log_chart_availability():
    """
    Loggt Verfügbarkeit aller Charts (für Debugging)
    """
    try:
        import streamlit as st
        from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP
        
        analysis_results = st.session_state.get('analysis_results', {})
        
        print("\n" + "="*60)
        print("CHART AVAILABILITY REPORT")
        print("="*60)
        
        for chart_key, friendly_name in CHART_KEY_TO_FRIENDLY_NAME_MAP.items():
            is_available = chart_key in analysis_results and analysis_results[chart_key] is not None
            status = "[OK]" if is_available else "[ERROR]"
            print(f"{status} {friendly_name}")
        
        available, missing = ensure_all_charts_available(analysis_results)
        print("="*60)
        print(f"GESAMT: {available} verfügbar, {missing} fehlen")
        print("="*60 + "\n")
        
    except Exception as e:
        logging.error(f"Fehler beim Logging: {e}")
