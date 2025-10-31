# pdf_integration_helper.py
"""
INTEGRATION HELPER für bestehende PDF-Generatoren
Erweitert bestehende PDFs um ALLE ausgewählten Charts und Financial Tools
"""

from __future__ import annotations

from typing import Any
import logging


def integrate_selected_charts_into_pdf(
    pdf_generator: Any,
    pdf_options: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Integriert ausgewählte Charts in einen bestehenden PDF-Generator
    
    Args:
        pdf_generator: Bestehender PDF-Generator (FPDF oder ähnlich)
        pdf_options: PDF-Optionen inkl. selected_charts_for_pdf
        analysis_results: Alle Analyse-Ergebnisse
        
    Returns:
        Dict mit Integrations-Statistiken
    """
    try:
        from pdf_chart_renderer import (
            render_all_selected_charts_to_pdf,
            render_financial_tools_to_pdf,
            create_chart_overview_page,
            get_chart_statistics
        )
        from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP
        
        stats = {
            'charts_added': 0,
            'financial_tools_added': 0,
            'overview_page_added': False,
            'errors': []
        }
        
        # 1. Hole ausgewählte Charts
        selected_charts = pdf_options.get('selected_charts_for_pdf', [])
        
        if not selected_charts:
            logging.warning("Keine Charts ausgewählt für PDF-Export")
            return stats
        
        # 2. Erstelle Übersichtsseite
        try:
            create_chart_overview_page(
                pdf=pdf_generator,
                selected_charts=selected_charts,
                chart_friendly_names=CHART_KEY_TO_FRIENDLY_NAME_MAP,
                analysis_results=analysis_results
            )
            stats['overview_page_added'] = True
        except Exception as e:
            logging.error(f"Fehler bei Chart-Übersichtsseite: {e}")
            stats['errors'].append(f"Übersichtsseite: {str(e)}")
        
        # 3. Rendere alle Charts
        try:
            charts_added = render_all_selected_charts_to_pdf(
                pdf=pdf_generator,
                selected_charts=selected_charts,
                analysis_results=analysis_results,
                chart_friendly_names=CHART_KEY_TO_FRIENDLY_NAME_MAP,
                max_charts_per_page=2
            )
            stats['charts_added'] = charts_added
        except Exception as e:
            logging.error(f"Fehler beim Chart-Rendering: {e}")
            stats['errors'].append(f"Charts: {str(e)}")
        
        # 4. Financial Tools
        financial_tools_results = pdf_options.get('financial_tools_results', {})
        if financial_tools_results:
            try:
                financial_pages = render_financial_tools_to_pdf(
                    pdf=pdf_generator,
                    financial_tools_results=financial_tools_results
                )
                stats['financial_tools_added'] = financial_pages
            except Exception as e:
                logging.error(f"Fehler bei Financial Tools: {e}")
                stats['errors'].append(f"Financial Tools: {str(e)}")
        
        return stats
        
    except ImportError as e:
        logging.error(f"Import-Fehler bei PDF-Integration: {e}")
        return {'error': f'Import-Fehler: {str(e)}'}
    except Exception as e:
        logging.error(f"Unerwarteter Fehler bei PDF-Integration: {e}")
        return {'error': f'Fehler: {str(e)}'}


def ensure_all_charts_in_analysis_results(
    analysis_results: dict[str, Any],
    calculation_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Stellt sicher, dass ALLE Charts in analysis_results verfügbar sind
    
    Kopiert fehlende Charts aus calculation_results nach analysis_results
    
    Args:
        analysis_results: Analyse-Ergebnisse
        calculation_results: Ergebnisse von perform_calculations()
        
    Returns:
        Erweiterte analysis_results
    """
    if not isinstance(analysis_results, dict):
        analysis_results = {}
    
    if not isinstance(calculation_results, dict):
        return analysis_results
    
    # Liste aller möglichen Chart-Keys
    chart_keys = [
        # Aus calculations.py
        'monthly_prod_cons_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'pv_usage_chart_bytes',
        'consumption_coverage_chart_bytes',
        'cost_overview_chart_bytes',
        'cost_projection_chart_bytes',
        'break_even_scenarios_chart_bytes',
        'technical_degradation_chart_bytes',
        'maintenance_schedule_chart_bytes',
        'energy_price_comparison_chart_bytes',
        
        # Aus analysis.py
        'roi_chart_bytes',
        'energy_balance_chart_bytes',
        'monthly_savings_chart_bytes',
        'yearly_comparison_chart_bytes',
        'amortization_chart_bytes',
        'co2_savings_chart_bytes',
        'financing_comparison_chart_bytes',
        
        # Erweiterte Charts
        'scenario_comparison_chart_bytes',
        'tariff_comparison_chart_bytes',
        'income_projection_chart_bytes',
        'battery_usage_chart_bytes',
        'grid_interaction_chart_bytes',
        'self_consumption_chart_bytes',
        'feed_in_analysis_chart_bytes',
        
        # Advanced Charts
        'break_even_detailed_chart_bytes',
        'lifecycle_cost_chart_bytes',
    ]
    
    # Kopiere fehlende Charts
    charts_added = 0
    for chart_key in chart_keys:
        if chart_key not in analysis_results or analysis_results[chart_key] is None:
            if chart_key in calculation_results and calculation_results[chart_key] is not None:
                analysis_results[chart_key] = calculation_results[chart_key]
                charts_added += 1
    
    if charts_added > 0:
        logging.info(f"✅ {charts_added} Charts von calculation_results nach analysis_results kopiert")
    
    return analysis_results


def create_charts_from_advanced_features(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Erstellt Charts aus Advanced Features falls noch nicht vorhanden
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyse-Ergebnisse
        
    Returns:
        Erweiterte analysis_results mit neuen Charts
    """
    try:
        from advanced_charts import create_all_advanced_charts
        
        # Prüfe ob Charts bereits existieren
        if 'break_even_detailed_chart_bytes' in analysis_results and 'lifecycle_cost_chart_bytes' in analysis_results:
            return analysis_results
        
        # Erstelle Charts
        advanced_charts = create_all_advanced_charts(project_data, analysis_results)
        
        # Füge hinzu
        if advanced_charts:
            analysis_results.update(advanced_charts)
            logging.info(f"✅ {len(advanced_charts)} Advanced Charts erstellt")
        
        return analysis_results
        
    except ImportError:
        logging.warning("advanced_charts Modul nicht verfügbar")
        return analysis_results
    except Exception as e:
        logging.error(f"Fehler beim Erstellen der Advanced Charts: {e}")
        return analysis_results


def prepare_complete_analysis_results(
    project_data: dict[str, Any],
    calculation_results: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    MASTER-FUNKTION: Bereitet vollständige analysis_results vor
    
    Sammelt ALLE Charts aus ALLEN Quellen:
    - calculation_results (perform_calculations)
    - analysis_results (Analyse-Modul)
    - advanced_charts (Neue Features)
    
    Args:
        project_data: Projektdaten
        calculation_results: Von perform_calculations()
        analysis_results: Von analysis.py
        
    Returns:
        Vollständige analysis_results mit ALLEN Charts
    """
    # 1. Kopiere Charts von calculation_results
    complete_results = ensure_all_charts_in_analysis_results(
        analysis_results,
        calculation_results
    )
    
    # 2. Erstelle Advanced Charts
    complete_results = create_charts_from_advanced_features(
        project_data,
        complete_results
    )
    
    # 3. Zähle verfügbare Charts
    chart_count = sum(
        1 for key, value in complete_results.items()
        if key.endswith('_chart_bytes') and value is not None
    )
    
    logging.info(f"✅ Vollständige analysis_results vorbereitet: {chart_count} Charts verfügbar")
    
    return complete_results
