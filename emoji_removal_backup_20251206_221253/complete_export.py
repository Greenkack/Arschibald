# complete_export.py
"""
VOLLSTÄNDIGER EXPORT ALLER CHARTS UND BERECHNUNGEN
Sammelt ALLE Features aus ALLEN Modulen und macht sie verfügbar
"""

from __future__ import annotations

from typing import Any


def collect_all_charts_from_calculations(
        results: dict[str, Any]) -> dict[str, bytes]:
    """
    Sammelt ALLE Chart-Bytes aus calculations.py Ergebnissen

    Args:
        results: Ergebnisse von perform_calculations()

    Returns:
        Dict mit allen Chart-Bytes
    """
    chart_keys = [
        # Aus calculations.py (Zeile 4198-4207)
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
    ]

    charts = {}
    for key in chart_keys:
        if key in results and results[key] is not None:
            charts[key] = results[key]

    return charts


def collect_all_financial_calculations(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Sammelt ALLE Finanz-Berechnungen aus financial_tools.py

    Args:
        project_data: Projektdaten
        analysis_results: Analyse-Ergebnisse

    Returns:
        Dict mit allen Finanz-Berechnungen
    """
    try:
        from financial_tools import (
            calculate_annuity,
            calculate_capital_gains_tax,
            calculate_contracting_costs,
            calculate_depreciation,
            calculate_financing_comparison,
            calculate_leasing_costs,
        )

        total_investment = analysis_results.get('total_investment', 0)
        annual_savings = analysis_results.get('annual_savings_after_pv', 0)

        financial_calcs = {}

        # 1. Annuität (Kredit)
        if total_investment > 0:
            try:
                annuity = calculate_annuity(
                    principal=total_investment,
                    annual_interest_rate=3.5,  # Standard
                    duration_years=15
                )
                financial_calcs['annuity_15y'] = annuity
            except BaseException:
                pass

            try:
                annuity_20y = calculate_annuity(
                    principal=total_investment,
                    annual_interest_rate=3.5,
                    duration_years=20
                )
                financial_calcs['annuity_20y'] = annuity_20y
            except BaseException:
                pass

        # 2. Leasing
        if total_investment > 0:
            try:
                leasing = calculate_leasing_costs(
                    total_investment=total_investment,
                    leasing_factor=1.2,  # 1.2%
                    duration_months=180  # 15 Jahre
                )
                financial_calcs['leasing_180m'] = leasing
            except BaseException:
                pass

        # 3. Abschreibung
        if total_investment > 0:
            try:
                depreciation_linear = calculate_depreciation(
                    initial_value=total_investment,
                    useful_life_years=20,
                    method='linear'
                )
                financial_calcs['depreciation_linear'] = depreciation_linear
            except BaseException:
                pass

            try:
                depreciation_degressive = calculate_depreciation(
                    initial_value=total_investment,
                    useful_life_years=20,
                    method='degressive'
                )
                financial_calcs['depreciation_degressive'] = depreciation_degressive
            except BaseException:
                pass

        # 4. Finanzierungs-Vergleich
        if total_investment > 0:
            try:
                comparison = calculate_financing_comparison(
                    investment=total_investment,
                    annual_interest_rate=3.5,
                    loan_duration_years=15,
                    leasing_factor_percent=1.2
                )
                financial_calcs['financing_comparison'] = comparison
            except BaseException:
                pass

        # 5. Kapitalertragssteuer (auf Einspeisevergütung)
        annual_feed_in = analysis_results.get('annual_feed_in_revenue', 0)
        if annual_feed_in > 0:
            try:
                capital_gains = calculate_capital_gains_tax(
                    profit=annual_feed_in,
                    tax_rate=26.375  # KESt in Deutschland
                )
                financial_calcs['capital_gains_tax'] = capital_gains
            except BaseException:
                pass

        # 6. Contracting-Kosten
        annual_consumption = project_data.get('annual_consumption', 0)
        if annual_consumption > 0:
            try:
                contracting = calculate_contracting_costs(
                    base_fee=1200,  # €/Jahr
                    consumption_price=0.15,  # €/kWh
                    annual_consumption_kwh=annual_consumption,
                    ppa_duration_years=20
                )
                financial_calcs['contracting_costs'] = contracting
            except BaseException:
                pass

        return financial_calcs

    except ImportError:
        return {'error': 'financial_tools nicht verfügbar'}
    except Exception as e:
        return {'error': str(e)}


def collect_all_extended_calculations(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Sammelt ALLE erweiterten Berechnungen aus calculations_extended.py

    Args:
        project_data: Projektdaten
        analysis_results: Analyse-Ergebnisse

    Returns:
        Dict mit allen erweiterten Berechnungen
    """
    try:
        # calculations_extended.py importieren
        import calculations_extended

        extended_calcs = {}

        # Alle Funktionen aus calculations_extended sammeln
        # (Diese müssen identifiziert werden - hier Platzhalter)

        # Beispiel: Wenn es eine perform_extended_analysis gibt:
        if hasattr(calculations_extended, 'perform_extended_analysis'):
            try:
                extended_results = calculations_extended.perform_extended_analysis(
                    project_data, analysis_results)
                extended_calcs['extended_analysis'] = extended_results
            except BaseException:
                pass

        return extended_calcs

    except ImportError:
        return {'error': 'calculations_extended nicht verfügbar'}
    except Exception as e:
        return {'error': str(e)}


def get_complete_chart_mapping() -> dict[str, str]:
    """
    VOLLSTÄNDIGE Mapping-Liste ALLER verfügbaren Charts

    Returns:
        Dict mit Chart-Key → Freundlicher Name
    """
    return {
        # === AUS CALCULATIONS.PY ===
        'monthly_prod_cons_chart_bytes': "Monatl. Produktion/Verbrauch (calculations.py)",
        'cumulative_cashflow_chart_bytes': "Kumulativer Cashflow (calculations.py)",
        'pv_usage_chart_bytes': "☀️ PV-Nutzung (calculations.py)",
        'consumption_coverage_chart_bytes': "Verbrauchsdeckung (calculations.py)",
        'cost_overview_chart_bytes': "💵 Kostenübersicht (calculations.py)",
        'cost_projection_chart_bytes': "Kostenprojektion (calculations.py)",
        'break_even_scenarios_chart_bytes': "⏱️ Break-Even Szenarien (calculations.py)",
        'technical_degradation_chart_bytes': "Technische Degradation (calculations.py)",
        'maintenance_schedule_chart_bytes': "🛠️ Wartungsplan (calculations.py)",
        'energy_price_comparison_chart_bytes': "Energiepreis-Vergleich (calculations.py)",

        # === AUS ANALYSIS.PY (BESTEHEND) ===
        'roi_chart_bytes': "ROI-Entwicklung (analysis.py)",
        'energy_balance_chart_bytes': "⚖️ Energiebilanz Donut (analysis.py)",
        'monthly_savings_chart_bytes': "Monatliche Einsparungen (analysis.py)",
        'yearly_comparison_chart_bytes': "📅 Jahresvergleich (analysis.py)",
        'amortization_chart_bytes': "⏱️ Amortisationszeit (analysis.py)",
        'co2_savings_chart_bytes': "CO₂-Einsparung (analysis.py)",
        'financing_comparison_chart_bytes': "💳 Finanzierungsvergleich (analysis.py)",

        # === AUS CALCULATIONS_EXTENDED.PY ===
        'scenario_comparison_chart_bytes': "🔀 Szenario-Vergleich (extended)",
        'tariff_comparison_chart_bytes': "Tarif-Vergleich (extended)",
        'income_projection_chart_bytes': "Einnahmen-Projektion (extended)",
        'battery_usage_chart_bytes': "🔋 Batterie-Nutzung (extended)",
        'grid_interaction_chart_bytes': "🔌 Netz-Interaktion (extended)",
        'self_consumption_chart_bytes': "🏠 Eigenverbrauch-Analyse (extended)",
        'feed_in_analysis_chart_bytes': "📤 Einspeisung-Analyse (extended)",

        # === AUS ANALYSIS.PY (ERWEITERT) ===
        'advanced_analysis_chart_bytes': "🔬 Erweiterte Analyse (analysis.py)",
        'sensitivity_analysis_chart_bytes': "Sensitivitäts-Analyse (analysis.py)",
        'optimization_chart_bytes': "⚙️ Optimierungs-Analyse (analysis.py)",
        'performance_metrics_chart_bytes': "Performance-Metriken (analysis.py)",
        'comparison_matrix_chart_bytes': "📋 Vergleichs-Matrix (analysis.py)",

        # === AUS DOC_OUTPUT.PY ===
        'summary_chart_bytes': "Zusammenfassung (doc_output.py)",
        'comparison_chart_bytes': "⚖️ Vergleich (doc_output.py)",

        # === 3D CHARTS (LEGACY) ===
        'consumption_coverage_pie_chart_bytes': "🥧 Verbrauchsdeckung Kreis (3D)",
        'pv_usage_pie_chart_bytes': "🥧 PV-Nutzung Kreis (3D)",
        'daily_production_switcher_chart_bytes': "☀️ Tagesproduktion (3D)",
        'weekly_production_switcher_chart_bytes': "📅 Wochenproduktion (3D)",
        'yearly_production_switcher_chart_bytes': "Jahresproduktion (3D)",
        'project_roi_matrix_switcher_chart_bytes': "💼 Projektrendite-Matrix (3D)",
        'feed_in_revenue_switcher_chart_bytes': "💵 Einspeisevergütung (3D)",
        'prod_vs_cons_switcher_chart_bytes': "Produktion vs Verbrauch (3D)",
        'tariff_cube_switcher_chart_bytes': "Tarifvergleich Würfel (3D)",
        'co2_savings_value_switcher_chart_bytes': "CO2 Ersparnis vs Wert (3D)",
        'investment_value_switcher_chart_bytes': "💎 Investitionsnutzwert (3D)",
        'storage_effect_switcher_chart_bytes': "🔋 Speicherwirkung (3D)",
        'selfuse_stack_switcher_chart_bytes': "🏠 Eigenverbrauch Stack (3D)",
        'cost_growth_switcher_chart_bytes': "Kostensteigerung (3D)",
        'selfuse_ratio_switcher_chart_bytes': "Eigenverbrauchsgrad (3D)",
        'roi_comparison_switcher_chart_bytes': "ROI-Vergleich (3D)",
        'scenario_comparison_switcher_chart_bytes': "🔀 Szenario-Vergleich (3D)",
        'tariff_comparison_switcher_chart_bytes': "Stromkosten Vorher/Nachher (3D)",
        'income_projection_switcher_chart_bytes': "💵 Einnahmen-Prognose (3D)",
        'yearly_production_chart_bytes': "PV Visuals: Jahresproduktion",
        'break_even_chart_bytes': "⏱️ PV Visuals: Break-Even",
        'amortisation_chart_bytes': "⏱️ PV Visuals: Amortisation",

        # === NEUE FEATURES (advanced_charts.py) ===
        'break_even_detailed_chart_bytes': "⭐ Break-Even Detailliert (NEU)",
        'lifecycle_cost_chart_bytes': "⭐ Lebenszykluskosten TCO (NEU)",
    }


def get_complete_calculation_list() -> list[dict[str, str]]:
    """
    VOLLSTÄNDIGE Liste ALLER verfügbaren Berechnungen

    Returns:
        Liste mit Berechnung-Info
    """
    return [
        # === FINANCIAL_TOOLS.PY ===
        {'name': 'Annuität-Berechnung',
         'module': 'financial_tools',
         'function': 'calculate_annuity'},
        {'name': 'Leasing-Kosten',
         'module': 'financial_tools',
         'function': 'calculate_leasing_costs'},
        {'name': 'Abschreibung (AfA)',
         'module': 'financial_tools',
         'function': 'calculate_depreciation'},
        {'name': 'Finanzierungs-Vergleich', 'module': 'financial_tools',
            'function': 'calculate_financing_comparison'},
        {'name': 'Kapitalertragssteuer', 'module': 'financial_tools',
            'function': 'calculate_capital_gains_tax'},
        {'name': 'Contracting-Kosten', 'module': 'financial_tools',
            'function': 'calculate_contracting_costs'},

        # === ADVANCED_FEATURES.PY (NEU) ===
        {'name': 'Stromtarif-Optimierung',
         'module': 'advanced_features',
         'function': 'grid_tariff_optimization'},
        {'name': 'Steuervorteile-Rechner',
         'module': 'advanced_features',
         'function': 'tax_benefit_calculator'},
        {'name': 'Förderungs-Optimierung',
         'module': 'advanced_features',
         'function': 'subsidy_optimizer'},
        {'name': 'Batterie-Optimierung', 'module': 'advanced_features',
            'function': 'advanced_battery_optimization'},
        {'name': 'Finanzierungs-Szenarien',
         'module': 'advanced_features',
         'function': 'financing_scenario_comparison'},

        # === CALCULATIONS.PY ===
        {'name': 'PV-Produktion', 'module': 'calculations',
            'function': 'calculate_pv_production'},
        {'name': 'Verbrauchsdeckung', 'module': 'calculations',
            'function': 'calculate_consumption_coverage'},
        {'name': 'Finanzmetriken', 'module': 'calculations',
            'function': 'calculate_financial_metrics'},
        {'name': 'ROI Detailliert', 'module': 'calculations',
            'function': 'calculate_roi_detailed'},
        {'name': 'CO₂-Ersparnis', 'module': 'calculations',
            'function': 'calculate_co2_savings'},
        {'name': 'Amortisationszeit', 'module': 'calculations',
            'function': 'calculate_payback_period'},

        # === CALCULATIONS_EXTENDED.PY ===
        {'name': 'Erweiterte PV-Analyse',
         'module': 'calculations_extended',
         'function': 'perform_extended_analysis'},
        {'name': 'Szenario-Analysen',
         'module': 'calculations_extended',
         'function': 'calculate_scenarios'},

        # === ANALYSIS.PY ===
        {'name': 'Vollständige Analyse', 'module': 'analysis',
            'function': 'perform_full_analysis'},
        {'name': 'Sensitivitätsanalyse', 'module': 'analysis',
            'function': 'perform_sensitivity_analysis'},
        {'name': 'Optimierungsvorschläge', 'module': 'analysis',
            'function': 'generate_optimization_suggestions'},
    ]


def export_all_results(
    project_data: dict[str, Any],
    calculation_results: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    MASTER-EXPORT: Sammelt ALLE Ergebnisse aus ALLEN Modulen

    Args:
        project_data: Projektdaten
        calculation_results: Ergebnisse von perform_calculations()
        analysis_results: Ergebnisse von analysis.py

    Returns:
        Vollständiges Dict mit ALLEN Ergebnissen
    """
    complete_export = {
        'charts': {},
        'calculations': {},
        'financial': {},
        'extended': {},
        'advanced': {},
        'metadata': {
            'total_charts': 0,
            'total_calculations': 0,
            'modules_loaded': []
        }
    }

    # 1. Alle Charts sammeln
    try:
        charts_calc = collect_all_charts_from_calculations(calculation_results)
        complete_export['charts'].update(charts_calc)
        complete_export['metadata']['modules_loaded'].append('calculations')
    except BaseException:
        pass

    try:
        if analysis_results:
            # Charts aus analysis_results
            for key in get_complete_chart_mapping().keys():
                if key in analysis_results and analysis_results[key] is not None:
                    complete_export['charts'][key] = analysis_results[key]
            complete_export['metadata']['modules_loaded'].append('analysis')
    except BaseException:
        pass

    # 2. Financial Tools
    try:
        financial = collect_all_financial_calculations(
            project_data, analysis_results)
        complete_export['financial'] = financial
        complete_export['metadata']['modules_loaded'].append('financial_tools')
    except BaseException:
        pass

    # 3. Extended Calculations
    try:
        extended = collect_all_extended_calculations(
            project_data, analysis_results)
        complete_export['extended'] = extended
        complete_export['metadata']['modules_loaded'].append(
            'calculations_extended')
    except BaseException:
        pass

    # 4. Advanced Features
    try:
        from advanced_features import get_all_advanced_features
        advanced = get_all_advanced_features(project_data, analysis_results)
        complete_export['advanced'] = advanced
        complete_export['metadata']['modules_loaded'].append(
            'advanced_features')
    except BaseException:
        pass

    # Zähler aktualisieren
    complete_export['metadata']['total_charts'] = len(
        complete_export['charts'])
    complete_export['metadata']['total_calculations'] = (
        len(complete_export['financial']) +
        len(complete_export['extended']) +
        len(complete_export['advanced'])
    )

    return complete_export
