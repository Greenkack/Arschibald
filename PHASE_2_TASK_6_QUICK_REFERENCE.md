# Phase 2 - Task 6: Quick Reference

## Status: ✅ COMPLETE

## Was wurde implementiert?

### 1. Erweiterte Metriken (6.1)
```python
from utils.pv3d_analysis import calculate_extended_yield_metrics

metrics = calculate_extended_yield_metrics(
    module_positions,
    module_transforms,
    building_dims,
    latitude=51.0,
    module_power_wp=400.0,
    electricity_price_eur_kwh=0.30,
    module_cost_eur=200.0
)

# Jedes Modul hat:
# - yearly_yield_kwh: Jahresertrag
# - monthly_avg_yield_kwh: Monatlicher Durchschnitt
# - shading_loss_percent: Verschattungsverlust
# - roi_years: Return on Investment
# - co2_savings_kg: CO₂-Einsparung
# - relative_performance: Performance 0-100%
```

### 2. Heatmap-Visualisierung (6.2)
```python
from utils.pv3d_analysis import create_pv_module_3d_with_heatmap

fig = create_pv_module_3d_with_heatmap(
    module_positions,
    module_transforms,
    metrics,
    color_by="yearly_yield"  # oder "roi", "co2_savings", "performance"
)

# Hover-Text zeigt alle Metriken
```

### 3. Schwache Module (6.3)
```python
from utils.pv3d_analysis import (
    identify_weak_modules,
    suggest_module_optimization
)

# Finde Module mit <50% Performance
weak = identify_weak_modules(metrics, threshold_percent=50.0)

# Generiere Optimierungsvorschläge
suggestions = suggest_module_optimization(weak, metrics)

# Jeder Vorschlag hat:
# - issue: Problem-Beschreibung
# - suggestion: Optimierungsvorschlag
# - priority: "high", "medium", "low"
# - yearly_loss_kwh: Ertragsverlust
```

### 4. Vergleichsansicht (6.4)
```python
from utils.pv3d_analysis import create_comparison_view

comparison = create_comparison_view(
    config_a_metrics,
    config_b_metrics,
    config_a_name="Optimal",
    config_b_name="Suboptimal"
)

# Enthält:
# - summary: Zusammenfassung mit Differenzen
# - chart: Plotly Vergleichs-Diagramm
# - table: DataFrame (wenn pandas verfügbar)
```

## Tests

```bash
python -m pytest tests/test_phase2_task6_extended_yield.py -v
```

**Ergebnis:** 23/23 Tests bestanden ✅

## Dateien

- **Implementation:** `utils/pv3d_analysis.py` (erweitert)
- **Tests:** `tests/test_phase2_task6_extended_yield.py` (neu)
- **Dokumentation:** `PHASE_2_TASK_6_COMPLETE.md` (neu)

## Nächster Task

**Task 7:** Verbessere manuelle Modulplatzierung
- Modul-Hervorhebung
- Magnet-Funktion (Snap-to-Grid)
- Kopieren & Einfügen
- Vorschau bei Verschieben
- Tastatur-Shortcuts
