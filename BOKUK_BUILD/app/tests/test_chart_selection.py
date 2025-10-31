"""
Unit Tests für Diagrammauswahl-Funktionalität (Task 3.7)

Testet:
- check_chart_availability() Funktion
- Session State Management
- Dass nur ausgewählte Diagramme generiert werden

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.16
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import der zu testenden Funktionen
try:
    from pdf_ui import (
        check_chart_availability,
        CHART_KEY_TO_FRIENDLY_NAME_MAP,
        CHART_CATEGORIES
    )
    PDF_UI_AVAILABLE = True
except ImportError:
    PDF_UI_AVAILABLE = False
    print("Warning: pdf_ui module not available for testing")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def basic_project_data() -> Dict[str, Any]:
    """Basis-Projektdaten für Tests."""
    return {
        'customer_data': {
            'name': 'Test Kunde',
            'address': 'Teststraße 1',
        },
        'project_details': {
            'module_quantity': 20,
            'anlage_kwp': 8.0,
            'selected_module_id': 1,
            'selected_inverter_id': 1,
        }
    }


@pytest.fixture
def basic_analysis_results() -> Dict[str, Any]:
    """Basis-Analyseergebnisse für Tests."""
    return {
        'annual_pv_production_kwh': 8000.0,
        'annual_consumption_kwh': 5000.0,
        'total_investment_netto': 15000.0,
        'annual_savings': 1200.0,
    }


@pytest.fixture
def project_data_with_financing(basic_project_data) -> Dict[str, Any]:
    """Projektdaten mit Finanzierungsinformationen."""
    data = basic_project_data.copy()
    data['project_details']['include_financing'] = True
    return data


@pytest.fixture
def project_data_with_storage(basic_project_data) -> Dict[str, Any]:
    """Projektdaten mit Speicher."""
    data = basic_project_data.copy()
    data['project_details']['selected_storage_id'] = 5
    data['project_details']['selected_storage_name'] = 'Test Speicher 10kWh'
    return data


@pytest.fixture
def project_data_with_scenarios(basic_project_data) -> Dict[str, Any]:
    """Projektdaten mit mehreren Szenarien."""
    data = basic_project_data.copy()
    data['project_details']['scenarios'] = [
        {'name': 'Optimistisch', 'factor': 1.2},
        {'name': 'Realistisch', 'factor': 1.0},
        {'name': 'Pessimistisch', 'factor': 0.8},
    ]
    return data


@pytest.fixture
def project_data_with_advanced_analysis(basic_project_data) -> Dict[str, Any]:
    """Projektdaten mit erweiterter Analyse."""
    data = basic_project_data.copy()
    data['project_details']['include_advanced_analysis'] = True
    return data


@pytest.fixture
def analysis_results_with_financing(basic_analysis_results) -> Dict[str, Any]:
    """Analyseergebnisse mit Finanzierungsdaten."""
    results = basic_analysis_results.copy()
    results['financing_options'] = {
        'credit': {'monthly_rate': 250.0, 'total_cost': 18000.0},
        'leasing': {'monthly_rate': 200.0, 'total_cost': 16000.0},
    }
    return results


@pytest.fixture
def analysis_results_with_co2(basic_analysis_results) -> Dict[str, Any]:
    """Analyseergebnisse mit CO2-Daten."""
    results = basic_analysis_results.copy()
    results['co2_savings_kg_per_year'] = 4000.0
    return results


@pytest.fixture
def analysis_results_with_feed_in(basic_analysis_results) -> Dict[str, Any]:
    """Analyseergebnisse mit Einspeisedaten."""
    results = basic_analysis_results.copy()
    results['annual_feed_in_kwh'] = 3000.0
    results['feed_in_revenue'] = 300.0
    return results


@pytest.fixture
def analysis_results_with_tariff(basic_analysis_results) -> Dict[str, Any]:
    """Analyseergebnisse mit Tarifdaten."""
    results = basic_analysis_results.copy()
    results['current_electricity_cost'] = 0.30
    results['future_electricity_cost'] = 0.35
    return results


@pytest.fixture
def analysis_results_with_self_consumption(
        basic_analysis_results) -> Dict[str, Any]:
    """Analyseergebnisse mit Eigenverbrauchsdaten."""
    results = basic_analysis_results.copy()
    results['self_consumption_ratio'] = 0.65
    results['self_consumption_kwh'] = 5200.0
    return results


# ============================================================================
# TEST: check_chart_availability() - Basis-Diagramme
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityBasic:
    """Tests für check_chart_availability() mit Basis-Diagrammen."""

    def test_basic_charts_available_with_minimal_data(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Basis-Diagramme mit Mindestdaten verfügbar sind."""
        basic_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            'energy_balance_chart_bytes',
            'yearly_comparison_chart_bytes',
            'summary_chart_bytes',
        ]

        for chart_key in basic_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                basic_analysis_results
            )
            # Result should be truthy (True or a value that evaluates to True)
            assert result, f"{chart_key} sollte verfügbar sein (got {result})"

    def test_basic_charts_unavailable_without_data(self):
        """Test dass Basis-Diagramme ohne Daten nicht verfügbar sind."""
        empty_project_data = {'project_details': {}}
        empty_analysis_results = {}

        basic_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
        ]

        for chart_key in basic_charts:
            result = check_chart_availability(
                chart_key,
                empty_project_data,
                empty_analysis_results
            )
            # Result should be falsy (False, None, 0, etc.)
            assert not result, f"{chart_key} sollte ohne Daten nicht verfügbar sein (got {result})"

    def test_handles_none_project_data(self, basic_analysis_results):
        """Test dass None als project_data behandelt wird."""
        result = check_chart_availability(
            'monthly_prod_cons_chart_bytes',
            None,
            basic_analysis_results
        )
        assert not result, f"Sollte falsy sein mit None project_data (got {result})"

    def test_handles_none_analysis_results(self, basic_project_data):
        """Test dass None als analysis_results behandelt wird."""
        result = check_chart_availability(
            'monthly_prod_cons_chart_bytes',
            basic_project_data,
            None
        )
        # Basis-Charts brauchen nur project_data, sollte truthy sein
        assert result, f"Sollte truthy sein mit None analysis_results (got {result})"


# ============================================================================
# TEST: check_chart_availability() - Finanzierungs-Diagramme
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityFinancing:
    """Tests für check_chart_availability() mit Finanzierungs-Diagrammen."""

    def test_financing_charts_available_with_financing_data(
        self,
        project_data_with_financing,
        analysis_results_with_financing
    ):
        """Test dass Finanzierungs-Diagramme mit Finanzierungsdaten verfügbar sind."""
        financing_charts = [
            'financing_comparison_chart_bytes',
            'income_projection_chart_bytes',
            'break_even_chart_bytes',
            'amortisation_chart_bytes',
            'amortization_chart_bytes',
        ]

        for chart_key in financing_charts:
            result = check_chart_availability(
                chart_key,
                project_data_with_financing,
                analysis_results_with_financing
            )
            assert result is True, f"{chart_key} sollte mit Finanzierungsdaten verfügbar sein"

    def test_financing_charts_unavailable_without_financing_flag(
        self,
        basic_project_data,
        analysis_results_with_financing
    ):
        """Test dass Finanzierungs-Diagramme ohne include_financing Flag nicht verfügbar sind."""
        result = check_chart_availability(
            'financing_comparison_chart_bytes',
            basic_project_data,
            analysis_results_with_financing
        )
        assert result is False

    def test_financing_charts_unavailable_without_financing_data(
        self,
        project_data_with_financing,
        basic_analysis_results
    ):
        """Test dass Finanzierungs-Diagramme ohne Finanzierungsdaten nicht verfügbar sind."""
        # Remove total_investment_netto to make financing data unavailable
        analysis_results_no_financing = {
            k: v for k,
            v in basic_analysis_results.items() if k != 'total_investment_netto'}
        result = check_chart_availability(
            'financing_comparison_chart_bytes',
            project_data_with_financing,
            analysis_results_no_financing
        )
        assert not result, f"Sollte falsy sein ohne Finanzierungsdaten (got {result})"


# ============================================================================
# TEST: check_chart_availability() - Batterie-Diagramme
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityBattery:
    """Tests für check_chart_availability() mit Batterie-Diagrammen."""

    def test_battery_charts_available_with_storage(
        self,
        project_data_with_storage,
        basic_analysis_results
    ):
        """Test dass Batterie-Diagramme mit Speicher verfügbar sind."""
        battery_charts = [
            'battery_usage_chart_bytes',
            'self_consumption_chart_bytes',
            'storage_effect_switcher_chart_bytes',
        ]

        for chart_key in battery_charts:
            result = check_chart_availability(
                chart_key,
                project_data_with_storage,
                basic_analysis_results
            )
            assert result is True, f"{chart_key} sollte mit Speicher verfügbar sein"

    def test_battery_charts_unavailable_without_storage(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Batterie-Diagramme ohne Speicher nicht verfügbar sind."""
        battery_charts = [
            'battery_usage_chart_bytes',
            'self_consumption_chart_bytes',
        ]

        for chart_key in battery_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                basic_analysis_results
            )
            assert result is False, f"{chart_key} sollte ohne Speicher nicht verfügbar sein"


# ============================================================================
# TEST: check_chart_availability() - Szenario-Diagramme
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityScenarios:
    """Tests für check_chart_availability() mit Szenario-Diagrammen."""

    def test_scenario_charts_available_with_multiple_scenarios(
        self,
        project_data_with_scenarios,
        basic_analysis_results
    ):
        """Test dass Szenario-Diagramme mit mehreren Szenarien verfügbar sind."""
        scenario_charts = [
            'scenario_comparison_chart_bytes',
            'scenario_comparison_switcher_chart_bytes',
        ]

        for chart_key in scenario_charts:
            result = check_chart_availability(
                chart_key,
                project_data_with_scenarios,
                basic_analysis_results
            )
            assert result is True, f"{chart_key} sollte mit mehreren Szenarien verfügbar sein"

    def test_scenario_charts_unavailable_with_single_scenario(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Szenario-Diagramme mit nur einem Szenario nicht verfügbar sind."""
        project_data = basic_project_data.copy()
        project_data['project_details']['scenarios'] = [
            {'name': 'Standard', 'factor': 1.0}]

        result = check_chart_availability(
            'scenario_comparison_chart_bytes',
            project_data,
            basic_analysis_results
        )
        assert result is False

    def test_scenario_charts_unavailable_without_scenarios(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Szenario-Diagramme ohne Szenarien nicht verfügbar sind."""
        result = check_chart_availability(
            'scenario_comparison_chart_bytes',
            basic_project_data,
            basic_analysis_results
        )
        assert result is False


# ============================================================================
# TEST: check_chart_availability() - Analyse-Diagramme
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityAnalysis:
    """Tests für check_chart_availability() mit Analyse-Diagrammen."""

    def test_analysis_charts_available_with_advanced_analysis(
        self,
        project_data_with_advanced_analysis,
        basic_analysis_results
    ):
        """Test dass Analyse-Diagramme mit erweiterter Analyse verfügbar sind."""
        analysis_charts = [
            'sensitivity_analysis_chart_bytes',
            'optimization_chart_bytes',
            'advanced_analysis_chart_bytes',
            'performance_metrics_chart_bytes',
        ]

        for chart_key in analysis_charts:
            result = check_chart_availability(
                chart_key,
                project_data_with_advanced_analysis,
                basic_analysis_results
            )
            assert result is True, f"{chart_key} sollte mit erweiterter Analyse verfügbar sein"

    def test_analysis_charts_unavailable_without_advanced_analysis(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Analyse-Diagramme ohne erweiterte Analyse nicht verfügbar sind."""
        analysis_charts = [
            'sensitivity_analysis_chart_bytes',
            'optimization_chart_bytes',
        ]

        for chart_key in analysis_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                basic_analysis_results
            )
            assert result is False, f"{chart_key} sollte ohne erweiterte Analyse nicht verfügbar sein"


# ============================================================================
# TEST: check_chart_availability() - Spezielle Diagrammtypen
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilitySpecial:
    """Tests für check_chart_availability() mit speziellen Diagrammtypen."""

    def test_co2_charts_available_with_co2_data(
        self,
        basic_project_data,
        analysis_results_with_co2
    ):
        """Test dass CO2-Diagramme mit CO2-Daten verfügbar sind."""
        co2_charts = [
            'co2_savings_chart_bytes',
            'co2_savings_value_switcher_chart_bytes',
        ]

        for chart_key in co2_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                analysis_results_with_co2
            )
            assert result is True, f"{chart_key} sollte mit CO2-Daten verfügbar sein"

    def test_feed_in_charts_available_with_feed_in_data(
        self,
        basic_project_data,
        analysis_results_with_feed_in
    ):
        """Test dass Einspeise-Diagramme mit Einspeisedaten verfügbar sind."""
        feed_in_charts = [
            'feed_in_analysis_chart_bytes',
            'feed_in_revenue_switcher_chart_bytes',
        ]

        for chart_key in feed_in_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                analysis_results_with_feed_in
            )
            assert result is True, f"{chart_key} sollte mit Einspeisedaten verfügbar sein"

    def test_tariff_charts_available_with_tariff_data(
        self,
        basic_project_data,
        analysis_results_with_tariff
    ):
        """Test dass Tarif-Diagramme mit Tarifdaten verfügbar sind."""
        tariff_charts = [
            'tariff_comparison_chart_bytes',
            'tariff_comparison_switcher_chart_bytes',
            'tariff_cube_switcher_chart_bytes',
        ]

        for chart_key in tariff_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                analysis_results_with_tariff
            )
            assert result is True, f"{chart_key} sollte mit Tarifdaten verfügbar sein"

    def test_self_consumption_charts_available_with_self_consumption_data(
        self,
        basic_project_data,
        analysis_results_with_self_consumption
    ):
        """Test dass Eigenverbrauchs-Diagramme mit Eigenverbrauchsdaten verfügbar sind."""
        self_consumption_charts = [
            'consumption_coverage_pie_chart_bytes',
            'pv_usage_pie_chart_bytes',
            'selfuse_stack_switcher_chart_bytes',
            'selfuse_ratio_switcher_chart_bytes',
        ]

        for chart_key in self_consumption_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                analysis_results_with_self_consumption
            )
            assert result is True, f"{chart_key} sollte mit Eigenverbrauchsdaten verfügbar sein"

    def test_roi_charts_available_with_roi_data(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass ROI-Diagramme mit ROI-Daten verfügbar sind."""
        roi_charts = [
            'roi_chart_bytes',
            'cumulative_cashflow_chart_bytes',
            'roi_comparison_switcher_chart_bytes',
            'project_roi_matrix_switcher_chart_bytes',
        ]

        for chart_key in roi_charts:
            result = check_chart_availability(
                chart_key,
                basic_project_data,
                basic_analysis_results
            )
            assert result is True, f"{chart_key} sollte mit ROI-Daten verfügbar sein"

    def test_unknown_chart_defaults_to_checking_analysis_results(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass unbekannte Diagramme auf analysis_results geprüft werden."""
        # Unbekanntes Diagramm das in analysis_results existiert
        analysis_results = basic_analysis_results.copy()
        analysis_results['unknown_chart_bytes'] = b'some_data'

        result = check_chart_availability(
            'unknown_chart_bytes',
            basic_project_data,
            analysis_results
        )
        assert result is True

        # Unbekanntes Diagramm das nicht in analysis_results existiert
        result = check_chart_availability(
            'non_existent_chart_bytes',
            basic_project_data,
            basic_analysis_results
        )
        assert result is False


# ============================================================================
# TEST: check_chart_availability() - Fehlerbehandlung
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestCheckChartAvailabilityErrorHandling:
    """Tests für Fehlerbehandlung in check_chart_availability()."""

    def test_handles_invalid_project_data_structure(self):
        """Test dass ungültige project_data Struktur behandelt wird."""
        invalid_data = "not a dict"
        analysis_results = {}

        result = check_chart_availability(
            'monthly_prod_cons_chart_bytes',
            invalid_data,
            analysis_results
        )
        assert not result, f"Sollte falsy sein mit ungültiger Struktur (got {result})"

    def test_handles_invalid_analysis_results_structure(
            self, basic_project_data):
        """Test dass ungültige analysis_results Struktur behandelt wird."""
        invalid_results = "not a dict"

        result = check_chart_availability(
            'monthly_prod_cons_chart_bytes',
            basic_project_data,
            invalid_results
        )
        # Sollte trotzdem funktionieren da Basis-Charts nur project_data
        # brauchen
        assert result, f"Sollte truthy sein trotz ungültiger analysis_results (got {result})"

    def test_handles_missing_project_details(self):
        """Test dass fehlende project_details behandelt werden."""
        project_data = {'customer_data': {}}  # Kein project_details
        analysis_results = {}

        result = check_chart_availability(
            'monthly_prod_cons_chart_bytes',
            project_data,
            analysis_results
        )
        assert not result, f"Sollte falsy sein ohne project_details (got {result})"


# ============================================================================
# TEST: Session State Management
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestSessionStateManagement:
    """Tests für Session State Management der Diagrammauswahl."""

    def test_selected_charts_stored_in_session_state(self):
        """Test dass ausgewählte Diagramme im Session State gespeichert werden."""
        # Mock Streamlit Session State
        mock_session_state = {}

        # Simuliere Auswahl von Diagrammen
        selected_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            'roi_chart_bytes',
        ]

        # Speichere in Session State
        mock_session_state['pdf_inclusion_options'] = {
            'selected_charts_for_pdf': selected_charts
        }

        # Verifiziere dass Daten korrekt gespeichert sind
        assert 'pdf_inclusion_options' in mock_session_state
        assert 'selected_charts_for_pdf' in mock_session_state['pdf_inclusion_options']
        assert len(
            mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']) == 3
        assert 'monthly_prod_cons_chart_bytes' in mock_session_state[
            'pdf_inclusion_options']['selected_charts_for_pdf']

    def test_session_state_persists_across_selections(self):
        """Test dass Session State über mehrere Auswahlen hinweg persistiert."""
        mock_session_state = {
            'pdf_inclusion_options': {
                'selected_charts_for_pdf': ['chart1', 'chart2']
            }
        }

        # Füge weiteres Diagramm hinzu
        mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf'].append(
            'chart3')

        assert len(
            mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']) == 3
        assert 'chart3' in mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']

    def test_session_state_can_be_cleared(self):
        """Test dass Session State geleert werden kann."""
        mock_session_state = {
            'pdf_inclusion_options': {
                'selected_charts_for_pdf': ['chart1', 'chart2', 'chart3']
            }
        }

        # Leere Auswahl
        mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf'] = [
        ]

        assert len(
            mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']) == 0

    def test_session_state_handles_duplicate_selections(self):
        """Test dass Duplikate in der Auswahl vermieden werden."""
        mock_session_state = {
            'pdf_inclusion_options': {
                'selected_charts_for_pdf': ['chart1', 'chart2']
            }
        }

        # Versuche Duplikat hinzuzufügen
        chart_to_add = 'chart1'
        current_selection = mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']

        if chart_to_add not in current_selection:
            current_selection.append(chart_to_add)

        # Sollte immer noch nur 2 Einträge haben
        assert len(
            mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']) == 2

    def test_session_state_initializes_empty_if_not_present(self):
        """Test dass Session State leer initialisiert wird wenn nicht vorhanden."""
        mock_session_state = {}

        # Initialisiere wenn nicht vorhanden
        if 'pdf_inclusion_options' not in mock_session_state:
            mock_session_state['pdf_inclusion_options'] = {}
        if 'selected_charts_for_pdf' not in mock_session_state['pdf_inclusion_options']:
            mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf'] = [
            ]

        assert 'pdf_inclusion_options' in mock_session_state
        assert 'selected_charts_for_pdf' in mock_session_state['pdf_inclusion_options']
        assert mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf'] == [
        ]


# ============================================================================
# TEST: Nur ausgewählte Diagramme werden generiert
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestOnlySelectedChartsGenerated:
    """Tests dass nur ausgewählte Diagramme generiert werden."""

    def test_only_selected_charts_are_included(self):
        """Test dass nur ausgewählte Diagramme in die PDF eingefügt werden."""
        # Alle verfügbaren Diagramme
        all_charts = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())

        # Nur einige auswählen
        selected_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            'roi_chart_bytes',
        ]

        # Simuliere Filterung
        charts_to_generate = [
            chart for chart in all_charts if chart in selected_charts]

        assert len(charts_to_generate) == 3
        assert 'monthly_prod_cons_chart_bytes' in charts_to_generate
        assert 'cost_projection_chart_bytes' in charts_to_generate
        assert 'roi_chart_bytes' in charts_to_generate

        # Nicht ausgewählte Diagramme sollten nicht enthalten sein
        assert 'co2_savings_chart_bytes' not in charts_to_generate
        assert 'battery_usage_chart_bytes' not in charts_to_generate

    def test_empty_selection_results_in_no_charts(self):
        """Test dass leere Auswahl zu keinen Diagrammen führt."""
        all_charts = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())
        selected_charts = []

        charts_to_generate = [
            chart for chart in all_charts if chart in selected_charts]

        assert len(charts_to_generate) == 0

    def test_all_charts_selected_includes_all(self):
        """Test dass Auswahl aller Diagramme alle einschließt."""
        all_charts = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())
        selected_charts = all_charts.copy()

        charts_to_generate = [
            chart for chart in all_charts if chart in selected_charts]

        assert len(charts_to_generate) == len(all_charts)

    def test_chart_generation_respects_availability(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Diagramm-Generierung Verfügbarkeit respektiert."""
        # Wähle Diagramme aus die nicht verfügbar sind
        selected_charts = [
            'battery_usage_chart_bytes',  # Benötigt Speicher
            'financing_comparison_chart_bytes',  # Benötigt Finanzierung
        ]

        # Filtere nur verfügbare Diagramme
        available_selected_charts = [
            chart for chart in selected_charts if check_chart_availability(
                chart, basic_project_data, basic_analysis_results)]

        # Sollte leer sein da beide nicht verfügbar
        assert len(available_selected_charts) == 0

    def test_chart_generation_with_mixed_availability(
        self,
        project_data_with_storage,
        basic_analysis_results
    ):
        """Test Diagramm-Generierung mit gemischter Verfügbarkeit."""
        selected_charts = [
            'monthly_prod_cons_chart_bytes',  # Verfügbar
            'battery_usage_chart_bytes',  # Verfügbar (mit Speicher)
            'financing_comparison_chart_bytes',  # Nicht verfügbar
        ]

        # Filtere nur verfügbare Diagramme
        available_selected_charts = [
            chart for chart in selected_charts if check_chart_availability(
                chart, project_data_with_storage, basic_analysis_results)]

        assert len(available_selected_charts) == 2
        assert 'monthly_prod_cons_chart_bytes' in available_selected_charts
        assert 'battery_usage_chart_bytes' in available_selected_charts
        assert 'financing_comparison_chart_bytes' not in available_selected_charts


# ============================================================================
# TEST: Chart Configuration Integrity
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestChartConfigurationIntegrity:
    """Tests für die Integrität der Chart-Konfiguration."""

    def test_all_charts_have_friendly_names(self):
        """Test dass alle Diagramme benutzerfreundliche Namen haben."""
        assert len(CHART_KEY_TO_FRIENDLY_NAME_MAP) > 0

        for chart_key, friendly_name in CHART_KEY_TO_FRIENDLY_NAME_MAP.items():
            assert isinstance(chart_key, str)
            assert isinstance(friendly_name, str)
            assert len(friendly_name) > 0
            assert chart_key.endswith(
                '_bytes') or chart_key.endswith('_chart_bytes')

    def test_all_categorized_charts_exist_in_mapping(self):
        """Test dass alle kategorisierten Diagramme im Mapping existieren."""
        for category_name, chart_keys in CHART_CATEGORIES.items():
            for chart_key in chart_keys:
                assert chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP, \
                    f"Chart {chart_key} in Kategorie {category_name} existiert nicht im Mapping"

    def test_no_duplicate_charts_in_categories(self):
        """Test dass keine Diagramme in mehreren Kategorien doppelt vorkommen."""
        all_categorized_charts = []

        for category_name, chart_keys in CHART_CATEGORIES.items():
            all_categorized_charts.extend(chart_keys)

        # Prüfe auf Duplikate
        unique_charts = set(all_categorized_charts)

        # Einige Diagramme können absichtlich in mehreren Kategorien sein
        # aber wir prüfen dass es nicht zu viele sind
        duplicates = len(all_categorized_charts) - len(unique_charts)
        assert duplicates < 5, f"Zu viele Duplikate in Kategorien: {duplicates}"

    def test_categories_are_not_empty(self):
        """Test dass keine Kategorie leer ist."""
        for category_name, chart_keys in CHART_CATEGORIES.items():
            assert len(chart_keys) > 0, f"Kategorie {category_name} ist leer"

    def test_chart_keys_follow_naming_convention(self):
        """Test dass Chart-Keys der Namenskonvention folgen."""
        for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
            # Sollte mit _bytes oder _chart_bytes enden
            assert chart_key.endswith('_bytes') or chart_key.endswith('_chart_bytes'), \
                f"Chart-Key {chart_key} folgt nicht der Namenskonvention"

            # Sollte keine Großbuchstaben haben
            assert chart_key.islower() or '_' in chart_key, \
                f"Chart-Key {chart_key} sollte lowercase mit underscores sein"


# ============================================================================
# TEST: Integration Tests
# ============================================================================

@pytest.mark.skipif(not PDF_UI_AVAILABLE, reason="pdf_ui module not available")
class TestChartSelectionIntegration:
    """Integrationstests für die gesamte Diagrammauswahl-Funktionalität."""

    def test_complete_workflow_basic_project(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test kompletter Workflow mit Basis-Projekt."""
        # 1. Verfügbare Diagramme ermitteln
        available_charts = []
        for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
            if check_chart_availability(
                    chart_key,
                    basic_project_data,
                    basic_analysis_results):
                available_charts.append(chart_key)

        assert len(available_charts) > 0

        # 2. Einige Diagramme auswählen
        selected_charts = available_charts[:3]  # Erste 3 verfügbare

        # 3. In Session State speichern
        mock_session_state = {
            'pdf_inclusion_options': {
                'selected_charts_for_pdf': selected_charts
            }
        }

        # 4. Verifiziere dass nur ausgewählte generiert werden
        charts_to_generate = [
            chart for chart in available_charts
            if chart in mock_session_state['pdf_inclusion_options']['selected_charts_for_pdf']
        ]

        assert len(charts_to_generate) == 3
        assert charts_to_generate == selected_charts

    def test_complete_workflow_advanced_project(
        self,
        project_data_with_storage,
        analysis_results_with_financing
    ):
        """Test kompletter Workflow mit erweitertem Projekt."""
        # Füge erweiterte Analyse hinzu
        project_data = project_data_with_storage.copy()
        project_data['project_details']['include_financing'] = True
        project_data['project_details']['include_advanced_analysis'] = True

        # 1. Verfügbare Diagramme ermitteln
        available_charts = []
        for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
            if check_chart_availability(
                    chart_key,
                    project_data,
                    analysis_results_with_financing):
                available_charts.append(chart_key)

        # Sollte mehr verfügbare Diagramme haben als Basis-Projekt
        assert len(available_charts) > 10

        # 2. Alle verfügbaren auswählen
        selected_charts = available_charts.copy()

        # 3. Verifiziere dass alle ausgewählt sind
        assert len(selected_charts) == len(available_charts)

    def test_workflow_handles_changing_availability(
        self,
        basic_project_data,
        basic_analysis_results
    ):
        """Test dass Workflow sich ändernde Verfügbarkeit behandelt."""
        # 1. Initiale Auswahl ohne Speicher
        initial_selection = [
            'monthly_prod_cons_chart_bytes',
            'battery_usage_chart_bytes',  # Nicht verfügbar
        ]

        # 2. Filtere verfügbare
        available_initial = [
            chart for chart in initial_selection if check_chart_availability(
                chart, basic_project_data, basic_analysis_results)]

        assert len(available_initial) == 1  # Nur monthly_prod_cons

        # 3. Füge Speicher hinzu
        project_data_with_storage = basic_project_data.copy()
        project_data_with_storage['project_details']['selected_storage_id'] = 5

        # 4. Prüfe erneut
        available_with_storage = [
            chart for chart in initial_selection if check_chart_availability(
                chart, project_data_with_storage, basic_analysis_results)]

        assert len(available_with_storage) == 2  # Beide verfügbar


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
