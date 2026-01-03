"""
Tests für Phase 2 - Task 6: Erweiterte Ertrags-Heatmap

Testet alle Funktionen für erweiterte Ertrags-Metriken:
- Berechnung erweiterter Metriken (Jahresertrag, ROI, CO₂-Einsparung)
- 3D-Visualisierung mit Heatmap
- Identifikation schwacher Module
- Optimierungsvorschläge
- Vergleichsansicht
"""

import pytest
import math
from typing import List, Dict, Tuple

# Import der zu testenden Funktionen
from utils.pv3d_analysis import (
    calculate_extended_yield_metrics,
    ExtendedYieldMetrics,
    create_pv_module_3d_with_heatmap,
    identify_weak_modules,
    suggest_module_optimization,
    create_comparison_view
)

from utils.pv3d import (
    BuildingDims,
    ModuleTransform
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_building():
    """Erstellt ein Beispiel-Gebäude."""
    return BuildingDims(
        length_m=10.0,
        width_m=6.0,
        wall_height_m=6.0
    )


@pytest.fixture
def sample_modules():
    """Erstellt Beispiel-Module mit verschiedenen Ausrichtungen."""
    positions = [
        (0.0, 0.0, 6.0),   # Modul 0: Optimal (Süd, 30°)
        (2.0, 0.0, 6.0),   # Modul 1: Gut (Süd-Ost, 25°)
        (4.0, 0.0, 6.0),   # Modul 2: Mittel (Ost, 20°)
        (6.0, 0.0, 6.0),   # Modul 3: Schlecht (Nord, 15°)
    ]
    
    transforms = {
        0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=30.0),    # Süd
        1: ModuleTransform(index=1, azimuth_deg=45.0, tilt_deg=25.0),   # Süd-Ost
        2: ModuleTransform(index=2, azimuth_deg=90.0, tilt_deg=20.0),   # Ost
        3: ModuleTransform(index=3, azimuth_deg=180.0, tilt_deg=15.0),  # Nord
    }
    
    return positions, transforms


# ============================================================================
# TESTS: ERWEITERTE METRIKEN BERECHNUNG
# ============================================================================

def test_calculate_extended_yield_metrics_basic(sample_building, sample_modules):
    """Test: Basis-Funktionalität der erweiterten Metriken-Berechnung."""
    positions, transforms = sample_modules
    
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building,
        latitude=51.0
    )
    
    # Prüfe dass für jedes Modul Metriken berechnet wurden
    assert len(metrics) == len(positions)
    
    # Prüfe dass alle Metriken vorhanden sind
    for metric in metrics:
        assert isinstance(metric, ExtendedYieldMetrics)
        assert metric.yearly_yield_kwh >= 0
        assert metric.monthly_avg_yield_kwh >= 0
        assert 0 <= metric.shading_loss_percent <= 100
        assert metric.roi_years > 0
        assert metric.co2_savings_kg >= 0
        assert 0 <= metric.relative_performance <= 100


def test_extended_metrics_south_better_than_north(sample_building, sample_modules):
    """Test: Süd-Ausrichtung hat besseren Ertrag als Nord-Ausrichtung."""
    positions, transforms = sample_modules
    
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building
    )
    
    # Modul 0 (Süd) sollte besser sein als Modul 3 (Nord)
    south_metric = metrics[0]
    north_metric = metrics[3]
    
    assert south_metric.yearly_yield_kwh > north_metric.yearly_yield_kwh
    assert south_metric.relative_performance > north_metric.relative_performance
    assert south_metric.roi_years < north_metric.roi_years


def test_extended_metrics_monthly_is_yearly_divided_by_12(sample_building, sample_modules):
    """Test: Monatlicher Ertrag ist Jahresertrag / 12."""
    positions, transforms = sample_modules
    
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building
    )
    
    for metric in metrics:
        expected_monthly = metric.yearly_yield_kwh / 12.0
        assert abs(metric.monthly_avg_yield_kwh - expected_monthly) < 0.01


def test_extended_metrics_custom_module_power(sample_building, sample_modules):
    """Test: Benutzerdefinierte Modulleistung wird berücksichtigt."""
    positions, transforms = sample_modules
    
    # Test mit 400W Modul
    metrics_400w = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building,
        module_power_wp=400.0
    )
    
    # Test mit 500W Modul
    metrics_500w = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building,
        module_power_wp=500.0
    )
    
    # 500W Modul sollte mehr Ertrag haben
    assert metrics_500w[0].yearly_yield_kwh > metrics_400w[0].yearly_yield_kwh


def test_extended_metrics_roi_calculation(sample_building, sample_modules):
    """Test: ROI-Berechnung ist korrekt."""
    positions, transforms = sample_modules
    
    module_cost = 200.0
    electricity_price = 0.30
    
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building,
        module_cost_eur=module_cost,
        electricity_price_eur_kwh=electricity_price
    )
    
    for metric in metrics:
        # ROI = Kosten / (Jahresertrag * Strompreis)
        expected_roi = module_cost / (metric.yearly_yield_kwh * electricity_price)
        assert abs(metric.roi_years - expected_roi) < 0.1


def test_extended_metrics_co2_savings(sample_building, sample_modules):
    """Test: CO₂-Einsparung wird berechnet."""
    positions, transforms = sample_modules
    
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building
    )
    
    for metric in metrics:
        # CO₂-Einsparung = Jahresertrag * 0.485 kg/kWh
        expected_co2 = metric.yearly_yield_kwh * 0.485
        assert abs(metric.co2_savings_kg - expected_co2) < 0.1


# ============================================================================
# TESTS: 3D-VISUALISIERUNG MIT HEATMAP
# ============================================================================

def test_create_heatmap_basic(sample_modules):
    """Test: Basis-Funktionalität der Heatmap-Erstellung."""
    positions, transforms = sample_modules
    
    # Erstelle Beispiel-Metriken
    metrics = [
        ExtendedYieldMetrics(
            module_index=i,
            yearly_yield_kwh=400.0 - i * 50,
            monthly_avg_yield_kwh=33.3 - i * 4.2,
            shading_loss_percent=10.0 + i * 10,
            roi_years=15.0 + i * 5,
            co2_savings_kg=194.0 - i * 24,
            relative_performance=90.0 - i * 15,
            position=positions[i]
        )
        for i in range(len(positions))
    ]
    
    fig = create_pv_module_3d_with_heatmap(
        positions,
        transforms,
        metrics,
        color_by="yearly_yield"
    )
    
    # Prüfe dass Figure erstellt wurde
    assert fig is not None
    assert len(fig.data) > 0


def test_create_heatmap_different_color_modes(sample_modules):
    """Test: Verschiedene Farbgebungs-Modi funktionieren."""
    positions, transforms = sample_modules
    
    metrics = [
        ExtendedYieldMetrics(
            module_index=i,
            yearly_yield_kwh=400.0,
            monthly_avg_yield_kwh=33.3,
            shading_loss_percent=10.0,
            roi_years=15.0,
            co2_savings_kg=194.0,
            relative_performance=90.0,
            position=positions[i]
        )
        for i in range(len(positions))
    ]
    
    color_modes = ["yearly_yield", "roi", "co2_savings", "performance"]
    
    for mode in color_modes:
        fig = create_pv_module_3d_with_heatmap(
            positions,
            transforms,
            metrics,
            color_by=mode
        )
        assert fig is not None
        assert len(fig.data) > 0


def test_create_heatmap_hover_text_contains_all_metrics(sample_modules):
    """Test: Hover-Text enthält alle Metriken."""
    positions, transforms = sample_modules
    
    metrics = [
        ExtendedYieldMetrics(
            module_index=0,
            yearly_yield_kwh=400.0,
            monthly_avg_yield_kwh=33.3,
            shading_loss_percent=10.0,
            roi_years=15.0,
            co2_savings_kg=194.0,
            relative_performance=90.0,
            position=positions[0]
        )
    ]
    
    fig = create_pv_module_3d_with_heatmap(
        positions[:1],
        {0: transforms[0]},
        metrics
    )
    
    # Prüfe dass Hover-Text alle wichtigen Informationen enthält
    hover_text = fig.data[0].text[0]
    assert "Modul #0" in hover_text
    assert "Jahresertrag" in hover_text
    assert "400.0 kWh" in hover_text
    assert "ROI" in hover_text
    assert "CO₂-Einsparung" in hover_text


def test_create_heatmap_empty_metrics_raises_error(sample_modules):
    """Test: Leere Metriken-Liste wirft Fehler."""
    positions, transforms = sample_modules
    
    with pytest.raises(ValueError):
        create_pv_module_3d_with_heatmap(
            positions,
            transforms,
            [],  # Leere Liste
            color_by="yearly_yield"
        )


# ============================================================================
# TESTS: SCHWACHE MODULE IDENTIFIZIEREN
# ============================================================================

def test_identify_weak_modules_basic():
    """Test: Basis-Funktionalität der Identifikation schwacher Module."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 200.0, 16.7, 50.0, 30.0, 97.0, 45.0, (2, 0, 6)),
        ExtendedYieldMetrics(2, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (4, 0, 6)),
        ExtendedYieldMetrics(3, 150.0, 12.5, 60.0, 40.0, 73.0, 35.0, (6, 0, 6)),
    ]
    
    weak = identify_weak_modules(metrics, threshold_percent=50.0)
    
    # Module 1 und 3 haben <50% Performance
    assert 1 in weak
    assert 3 in weak
    assert 0 not in weak
    assert 2 not in weak


def test_identify_weak_modules_custom_threshold():
    """Test: Benutzerdefinierter Schwellwert funktioniert."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (2, 0, 6)),
        ExtendedYieldMetrics(2, 300.0, 25.0, 30.0, 20.0, 146.0, 70.0, (4, 0, 6)),
    ]
    
    # Mit 75% Schwellwert
    weak = identify_weak_modules(metrics, threshold_percent=75.0)
    
    # Nur Modul 2 hat <75% Performance
    assert 2 in weak
    assert 0 not in weak
    assert 1 not in weak


def test_identify_weak_modules_all_good():
    """Test: Keine schwachen Module wenn alle gut sind."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 380.0, 31.7, 15.0, 16.0, 184.0, 85.0, (2, 0, 6)),
    ]
    
    weak = identify_weak_modules(metrics, threshold_percent=50.0)
    
    assert len(weak) == 0


# ============================================================================
# TESTS: OPTIMIERUNGSVORSCHLÄGE
# ============================================================================

def test_suggest_module_optimization_basic():
    """Test: Basis-Funktionalität der Optimierungsvorschläge."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 200.0, 16.7, 50.0, 30.0, 97.0, 45.0, (2, 0, 6)),
    ]
    
    weak = [1]
    suggestions = suggest_module_optimization(weak, metrics)
    
    assert len(suggestions) == 1
    assert suggestions[0]["module_index"] == 1
    assert "issue" in suggestions[0]
    assert "suggestion" in suggestions[0]
    assert "priority" in suggestions[0]


def test_suggest_optimization_high_shading():
    """Test: Hohe Verschattung führt zu high priority."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 200.0, 16.7, 50.0, 30.0, 97.0, 45.0, (2, 0, 6)),
    ]
    
    suggestions = suggest_module_optimization([1], metrics)
    
    # Modul 1 hat 50% Verschattung -> high priority
    assert suggestions[0]["priority"] == "high"
    assert "Verschattung" in suggestions[0]["issue"]


def test_suggest_optimization_low_performance():
    """Test: Sehr niedrige Performance führt zu high priority."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 100.0, 8.3, 10.0, 50.0, 49.0, 25.0, (2, 0, 6)),
    ]
    
    suggestions = suggest_module_optimization([1], metrics)
    
    # Modul 1 hat 25% Performance -> high priority
    assert suggestions[0]["priority"] == "high"
    assert "Performance" in suggestions[0]["issue"]


def test_suggest_optimization_long_roi():
    """Test: Lange ROI führt zu medium priority."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 250.0, 20.8, 15.0, 30.0, 121.0, 60.0, (2, 0, 6)),
    ]
    
    suggestions = suggest_module_optimization([1], metrics)
    
    # Modul 1 hat 30 Jahre ROI -> medium priority
    assert suggestions[0]["priority"] == "medium"
    assert "Amortisationszeit" in suggestions[0]["issue"]


def test_suggest_optimization_sorted_by_priority():
    """Test: Vorschläge sind nach Priorität sortiert."""
    metrics = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 250.0, 20.8, 15.0, 30.0, 121.0, 60.0, (2, 0, 6)),  # medium
        ExtendedYieldMetrics(2, 100.0, 8.3, 50.0, 50.0, 49.0, 25.0, (4, 0, 6)),    # high
        ExtendedYieldMetrics(3, 300.0, 25.0, 10.0, 20.0, 146.0, 70.0, (6, 0, 6)),  # low
    ]
    
    weak = [1, 2, 3]
    suggestions = suggest_module_optimization(weak, metrics)
    
    # Erste Vorschlag sollte high priority sein
    assert suggestions[0]["priority"] == "high"
    assert suggestions[0]["module_index"] == 2


# ============================================================================
# TESTS: VERGLEICHSANSICHT
# ============================================================================

def test_create_comparison_view_basic():
    """Test: Basis-Funktionalität der Vergleichsansicht."""
    metrics_a = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 380.0, 31.7, 15.0, 16.0, 184.0, 85.0, (2, 0, 6)),
    ]
    
    metrics_b = [
        ExtendedYieldMetrics(0, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 330.0, 27.5, 25.0, 18.0, 160.0, 75.0, (2, 0, 6)),
    ]
    
    result = create_comparison_view(metrics_a, metrics_b)
    
    assert "summary" in result
    assert "chart" in result
    assert result["summary"]["config_a"]["module_count"] == 2
    assert result["summary"]["config_b"]["module_count"] == 2


def test_comparison_view_calculates_differences():
    """Test: Differenzen werden korrekt berechnet."""
    metrics_a = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
    ]
    
    metrics_b = [
        ExtendedYieldMetrics(0, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (0, 0, 6)),
    ]
    
    result = create_comparison_view(metrics_a, metrics_b)
    
    diffs = result["summary"]["differences"]
    
    # B hat 50 kWh weniger Jahresertrag als A
    assert abs(diffs["yearly_yield_diff"] - (-50.0)) < 0.1
    
    # B hat 10% weniger Performance als A
    assert abs(diffs["performance_diff"] - (-10.0)) < 0.1


def test_comparison_view_chart_has_both_configs():
    """Test: Diagramm enthält beide Konfigurationen."""
    metrics_a = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
    ]
    
    metrics_b = [
        ExtendedYieldMetrics(0, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (0, 0, 6)),
    ]
    
    result = create_comparison_view(
        metrics_a,
        metrics_b,
        config_a_name="Optimal",
        config_b_name="Suboptimal"
    )
    
    fig = result["chart"]
    
    # Prüfe dass beide Konfigurationen im Diagramm sind
    assert len(fig.data) == 2
    assert fig.data[0].name == "Optimal"
    assert fig.data[1].name == "Suboptimal"


def test_comparison_view_with_different_module_counts():
    """Test: Vergleich mit unterschiedlicher Modulanzahl."""
    metrics_a = [
        ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 380.0, 31.7, 15.0, 16.0, 184.0, 85.0, (2, 0, 6)),
    ]
    
    metrics_b = [
        ExtendedYieldMetrics(0, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (0, 0, 6)),
        ExtendedYieldMetrics(1, 330.0, 27.5, 25.0, 18.0, 160.0, 75.0, (2, 0, 6)),
        ExtendedYieldMetrics(2, 300.0, 25.0, 30.0, 20.0, 146.0, 70.0, (4, 0, 6)),
    ]
    
    result = create_comparison_view(metrics_a, metrics_b)
    
    # B hat 1 Modul mehr als A
    assert result["summary"]["differences"]["module_count_diff"] == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_workflow_extended_yield(sample_building, sample_modules):
    """Test: Vollständiger Workflow von Berechnung bis Visualisierung."""
    positions, transforms = sample_modules
    
    # 1. Berechne erweiterte Metriken
    metrics = calculate_extended_yield_metrics(
        positions,
        transforms,
        sample_building
    )
    
    assert len(metrics) == len(positions)
    
    # 2. Identifiziere schwache Module
    weak = identify_weak_modules(metrics, threshold_percent=60.0)
    
    # Modul 3 (Nord) sollte schwach sein
    assert 3 in weak
    
    # 3. Generiere Optimierungsvorschläge
    suggestions = suggest_module_optimization(weak, metrics)
    
    assert len(suggestions) > 0
    
    # 4. Erstelle Visualisierung
    fig = create_pv_module_3d_with_heatmap(
        positions,
        transforms,
        metrics,
        color_by="yearly_yield"
    )
    
    assert fig is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
