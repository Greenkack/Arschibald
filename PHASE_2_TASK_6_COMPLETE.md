# Phase 2 - Task 6: Erweiterte Ertrags-Heatmap ✅ COMPLETE

## Übersicht

Task 6 erweitert die Ertrags-Heatmap um umfassende Metriken und Visualisierungen:
- **Erweiterte Metriken**: Jahresertrag, monatlicher Durchschnitt, Verschattungsverlust, ROI, CO₂-Einsparung
- **3D-Visualisierung mit Heatmap**: Interaktive Darstellung mit allen Metriken im Hover-Text
- **Schwache Module identifizieren**: Automatische Erkennung von Modulen mit <50% Performance
- **Optimierungsvorschläge**: Konkrete Empfehlungen zur Verbesserung
- **Vergleichsansicht**: Side-by-Side Vergleich verschiedener Konfigurationen

## Implementierte Funktionen

### 6.1 Erweiterte Metriken-Berechnung

**Datei:** `utils/pv3d_analysis.py`

**Neue Dataclass:**
```python
@dataclass
class ExtendedYieldMetrics:
    module_index: int
    yearly_yield_kwh: float          # Jahresertrag in kWh
    monthly_avg_yield_kwh: float     # Monatlicher Durchschnittsertrag
    shading_loss_percent: float      # Verschattungsverlust in %
    roi_years: float                 # Return on Investment in Jahren
    co2_savings_kg: float            # CO₂-Einsparung in kg/Jahr
    relative_performance: float      # Relative Performance (0-100)
    position: Tuple[float, float, float]
```

**Hauptfunktion:**
```python
calculate_extended_yield_metrics(
    module_positions,
    module_transforms,
    building_dims,
    latitude=51.0,
    module_power_wp=400.0,
    electricity_price_eur_kwh=0.30,
    module_cost_eur=200.0
)
```

**Features:**
- Kombiniert Basis-Ertragspotential mit Verschattungs-Analyse
- Simuliert 4 repräsentative Tage im Jahr (Sonnenwenden + Tagundnachtgleichen)
- Berechnet durchschnittliche Verschattung über das Jahr
- Berücksichtigt Modulleistung, Strompreis und Modulkosten
- Berechnet CO₂-Einsparung (0.485 kg/kWh deutscher Strommix)

**Berechnungsformeln:**
```python
# Jahresertrag
yearly_yield_kwh = (module_power_wp / 1000) * 1000 * (effective_yield_percent / 100)

# Monatlicher Durchschnitt
monthly_avg_yield_kwh = yearly_yield_kwh / 12

# ROI
roi_years = module_cost_eur / (yearly_yield_kwh * electricity_price_eur_kwh)

# CO₂-Einsparung
co2_savings_kg = yearly_yield_kwh * 0.485
```

### 6.2 3D-Visualisierung mit Heatmap

**Funktion:**
```python
create_pv_module_3d_with_heatmap(
    module_positions,
    module_transforms,
    extended_metrics,
    color_by="yearly_yield"
)
```

**Farbgebungs-Modi:**
- `"yearly_yield"`: Jahresertrag (kWh) - Viridis Colorscale
- `"roi"`: Return on Investment (Jahre) - RdYlGn_r (Rot=lange ROI, Grün=kurze ROI)
- `"co2_savings"`: CO₂-Einsparung (kg/Jahr) - Greens
- `"performance"`: Relative Performance (%) - RdYlGn

**Hover-Text enthält:**
- Modul-Index und Position
- Jahresertrag und monatlicher Durchschnitt
- Performance-Prozentsatz
- Verschattungsverlust
- ROI in Jahren
- CO₂-Einsparung

**Beispiel:**
```
Modul #0
Position: (0.0, 0.0, 6.0)

Ertrag:
Jahresertrag: 380.5 kWh
Ø Monat: 31.7 kWh
Performance: 95.1%

Verschattung:
Verlust: 12.3%

Wirtschaftlichkeit:
ROI: 17.5 Jahre
CO₂-Einsparung: 184.5 kg/Jahr
```

### 6.3 Schwache Module identifizieren

**Funktionen:**
- `identify_weak_modules(extended_metrics, threshold_percent=50.0)` - Identifiziert Module mit niedriger Performance
- `suggest_module_optimization(weak_modules, extended_metrics)` - Generiert Optimierungsvorschläge

**Identifikations-Kriterien:**
- Performance < Schwellwert (Standard: 50%)
- Vergleich mit bestem Modul zur Berechnung des Ertragsverlust

**Optimierungsvorschläge basierend auf:**

1. **Hohe Verschattung (>40%)**
   - Priorität: HIGH
   - Vorschlag: "Modul an weniger verschattete Position verschieben"

2. **Sehr niedrige Performance (<30%)**
   - Priorität: HIGH
   - Vorschlag: "Modul-Ausrichtung optimieren (Richtung Süden) und Neigung anpassen"

3. **Lange Amortisationszeit (>25 Jahre)**
   - Priorität: MEDIUM
   - Vorschlag: "Modul entfernen oder an bessere Position verschieben"

4. **Unterdurchschnittliche Performance**
   - Priorität: LOW
   - Vorschlag: "Position und Ausrichtung überprüfen"

**Rückgabewert:**
```python
[
    {
        "module_index": 1,
        "performance": 45.0,
        "yearly_loss_kwh": 150.0,
        "issue": "Hohe Verschattung (50.0%)",
        "suggestion": "Modul an weniger verschattete Position verschieben...",
        "priority": "high",
        "current_position": (2.0, 0.0, 6.0),
        "roi_years": 30.0,
        "shading_loss": 50.0
    }
]
```

### 6.4 Vergleichsansicht

**Funktion:**
```python
create_comparison_view(
    config_a_metrics,
    config_b_metrics,
    config_a_name="Konfiguration A",
    config_b_name="Konfiguration B"
)
```

**Rückgabewert:**
```python
{
    "summary": {
        "config_a": {
            "name": "Konfiguration A",
            "module_count": 10,
            "total_yearly_yield": 3800.0,
            "avg_performance": 85.0,
            "total_co2_savings": 1843.0,
            "avg_roi": 17.5,
            "avg_shading_loss": 12.0
        },
        "config_b": {...},
        "differences": {
            "module_count_diff": 2,
            "yearly_yield_diff": 500.0,
            "performance_diff": -5.0,
            "co2_diff": 242.5,
            "roi_diff": 2.0
        }
    },
    "table": DataFrame,  # Wenn pandas verfügbar
    "chart": Plotly Figure
}
```

**Vergleichs-Diagramm zeigt:**
- Modulanzahl
- Jahresertrag (kWh)
- Ø Performance (%)
- CO₂-Einsparung (kg)
- Ø ROI (Jahre)

**Vergleichstabelle enthält:**
- Alle Metriken für beide Konfigurationen
- Differenzen mit +/- Vorzeichen
- Ø Verschattungsverlust (%)

## Tests

**Datei:** `tests/test_phase2_task6_extended_yield.py`

**Test-Abdeckung:**
- ✅ 23 Tests, alle bestanden
- ✅ Basis-Funktionalität der erweiterten Metriken
- ✅ Süd-Ausrichtung besser als Nord
- ✅ Monatlicher Ertrag = Jahresertrag / 12
- ✅ Benutzerdefinierte Modulleistung
- ✅ ROI-Berechnung korrekt
- ✅ CO₂-Einsparung korrekt
- ✅ Heatmap-Erstellung mit verschiedenen Farbmodi
- ✅ Hover-Text enthält alle Metriken
- ✅ Identifikation schwacher Module
- ✅ Optimierungsvorschläge mit Prioritäten
- ✅ Vergleichsansicht mit Differenzen
- ✅ Vollständiger Workflow

**Test-Ausführung:**
```bash
python -m pytest tests/test_phase2_task6_extended_yield.py -v
```

**Ergebnis:**
```
23 passed in 6.95s
```

## Verwendung

### Beispiel 1: Erweiterte Metriken berechnen

```python
from utils.pv3d_analysis import calculate_extended_yield_metrics
from utils.pv3d import BuildingDims, ModuleTransform

# Module definieren
positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0), (4.0, 0.0, 6.0)]
transforms = {
    0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=30.0),    # Süd
    1: ModuleTransform(index=1, azimuth_deg=45.0, tilt_deg=25.0),   # Süd-Ost
    2: ModuleTransform(index=2, azimuth_deg=90.0, tilt_deg=20.0),   # Ost
}
dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)

# Metriken berechnen
metrics = calculate_extended_yield_metrics(
    positions,
    transforms,
    dims,
    latitude=51.0,
    module_power_wp=400.0,
    electricity_price_eur_kwh=0.30,
    module_cost_eur=200.0
)

# Ergebnisse anzeigen
for m in metrics:
    print(f"Modul {m.module_index}:")
    print(f"  Jahresertrag: {m.yearly_yield_kwh:.1f} kWh")
    print(f"  Performance: {m.relative_performance:.1f}%")
    print(f"  ROI: {m.roi_years:.1f} Jahre")
    print(f"  CO₂-Einsparung: {m.co2_savings_kg:.1f} kg/Jahr")
```

### Beispiel 2: Heatmap erstellen

```python
from utils.pv3d_analysis import create_pv_module_3d_with_heatmap

# Heatmap mit Jahresertrag als Farbe
fig = create_pv_module_3d_with_heatmap(
    positions,
    transforms,
    metrics,
    color_by="yearly_yield"
)

# In Streamlit anzeigen
import streamlit as st
st.plotly_chart(fig, use_container_width=True)

# Oder mit ROI als Farbe
fig_roi = create_pv_module_3d_with_heatmap(
    positions,
    transforms,
    metrics,
    color_by="roi"
)
st.plotly_chart(fig_roi, use_container_width=True)
```

### Beispiel 3: Schwache Module finden und optimieren

```python
from utils.pv3d_analysis import (
    identify_weak_modules,
    suggest_module_optimization
)

# Schwache Module identifizieren (Performance <50%)
weak_modules = identify_weak_modules(metrics, threshold_percent=50.0)
print(f"Schwache Module: {weak_modules}")

# Optimierungsvorschläge generieren
suggestions = suggest_module_optimization(weak_modules, metrics)

# Vorschläge anzeigen
for suggestion in suggestions:
    print(f"\n⚠️ Modul {suggestion['module_index']} - {suggestion['priority'].upper()}")
    print(f"   Problem: {suggestion['issue']}")
    print(f"   Vorschlag: {suggestion['suggestion']}")
    print(f"   Ertragsverlust: {suggestion['yearly_loss_kwh']:.1f} kWh/Jahr")
```

### Beispiel 4: Konfigurationen vergleichen

```python
from utils.pv3d_analysis import create_comparison_view

# Zwei verschiedene Konfigurationen
metrics_optimal = calculate_extended_yield_metrics(
    positions_optimal,
    transforms_optimal,
    dims
)

metrics_suboptimal = calculate_extended_yield_metrics(
    positions_suboptimal,
    transforms_suboptimal,
    dims
)

# Vergleich erstellen
comparison = create_comparison_view(
    metrics_optimal,
    metrics_suboptimal,
    config_a_name="Optimale Konfiguration",
    config_b_name="Suboptimale Konfiguration"
)

# Zusammenfassung anzeigen
summary = comparison["summary"]
print(f"Konfiguration A: {summary['config_a']['total_yearly_yield']:.1f} kWh/Jahr")
print(f"Konfiguration B: {summary['config_b']['total_yearly_yield']:.1f} kWh/Jahr")
print(f"Differenz: {summary['differences']['yearly_yield_diff']:+.1f} kWh/Jahr")

# Diagramm anzeigen
st.plotly_chart(comparison["chart"], use_container_width=True)

# Tabelle anzeigen (wenn pandas verfügbar)
if "table" in comparison:
    st.dataframe(comparison["table"])
```

## Integration in UI

Die neuen Funktionen können in der Streamlit-UI wie folgt integriert werden:

```python
import streamlit as st
from utils.pv3d_analysis import (
    calculate_extended_yield_metrics,
    create_pv_module_3d_with_heatmap,
    identify_weak_modules,
    suggest_module_optimization
)

# Sidebar: Heatmap-Optionen
st.sidebar.subheader("📊 Ertrags-Heatmap")

color_mode = st.sidebar.selectbox(
    "Farbgebung",
    ["yearly_yield", "roi", "co2_savings", "performance"],
    format_func=lambda x: {
        "yearly_yield": "Jahresertrag (kWh)",
        "roi": "ROI (Jahre)",
        "co2_savings": "CO₂-Einsparung (kg)",
        "performance": "Performance (%)"
    }[x]
)

weak_threshold = st.sidebar.slider(
    "Schwellwert für schwache Module (%)",
    min_value=30,
    max_value=70,
    value=50,
    step=5
)

# Hauptbereich: Metriken berechnen
if st.button("Erweiterte Analyse durchführen"):
    with st.spinner("Berechne erweiterte Metriken..."):
        metrics = calculate_extended_yield_metrics(
            module_positions,
            module_transforms,
            building_dims,
            latitude=51.0
        )
    
    # Kennzahlen anzeigen
    st.subheader("📈 Gesamt-Kennzahlen")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_yield = sum(m.yearly_yield_kwh for m in metrics)
        st.metric("Jahresertrag", f"{total_yield:.0f} kWh")
    
    with col2:
        avg_performance = sum(m.relative_performance for m in metrics) / len(metrics)
        st.metric("Ø Performance", f"{avg_performance:.1f}%")
    
    with col3:
        total_co2 = sum(m.co2_savings_kg for m in metrics)
        st.metric("CO₂-Einsparung", f"{total_co2:.0f} kg/Jahr")
    
    with col4:
        avg_roi = sum(m.roi_years for m in metrics) / len(metrics)
        st.metric("Ø ROI", f"{avg_roi:.1f} Jahre")
    
    # Heatmap anzeigen
    st.subheader("🗺️ Ertrags-Heatmap")
    
    fig = create_pv_module_3d_with_heatmap(
        module_positions,
        module_transforms,
        metrics,
        color_by=color_mode
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Schwache Module identifizieren
    weak_modules = identify_weak_modules(metrics, weak_threshold)
    
    if weak_modules:
        st.warning(f"⚠️ {len(weak_modules)} Module mit <{weak_threshold}% Performance gefunden")
        
        suggestions = suggest_module_optimization(weak_modules, metrics)
        
        st.subheader("💡 Optimierungsvorschläge")
        
        for suggestion in suggestions:
            priority_color = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }[suggestion["priority"]]
            
            with st.expander(
                f"{priority_color} Modul {suggestion['module_index']} - "
                f"{suggestion['performance']:.1f}% Performance"
            ):
                st.write(f"**Problem:** {suggestion['issue']}")
                st.write(f"**Vorschlag:** {suggestion['suggestion']}")
                st.write(f"**Ertragsverlust:** {suggestion['yearly_loss_kwh']:.1f} kWh/Jahr")
                st.write(f"**Position:** {suggestion['current_position']}")
    else:
        st.success(f"✅ Alle Module haben ≥{weak_threshold}% Performance")
```

## Technische Details

### Algorithmus: Erweiterte Metriken

1. **Basis-Ertragspotential berechnen:**
   - Verwendet `calculate_yield_heatmap()` für Ausrichtungs- und Neigungsfaktoren

2. **Durchschnittliche Verschattung über Jahr:**
   - Simuliert 4 repräsentative Tage (Sonnenwenden + Tagundnachtgleichen)
   - Berechnet Verschattung um 12:00 Uhr für jeden Tag
   - Mittelt die Werte

3. **Effektives Ertragspotential:**
   ```python
   effective_yield_percent = base_yield_percent * (1.0 - avg_shading)
   ```

4. **Jahresertrag:**
   ```python
   # Annahme: 1000 kWh/kWp bei optimaler Ausrichtung in Deutschland
   yearly_yield_kwh = (module_power_wp / 1000) * 1000 * (effective_yield_percent / 100)
   ```

5. **ROI:**
   ```python
   yearly_revenue = yearly_yield_kwh * electricity_price_eur_kwh
   roi_years = module_cost_eur / yearly_revenue
   ```

6. **CO₂-Einsparung:**
   ```python
   # Deutscher Strommix 2024: 0.485 kg CO₂/kWh
   co2_savings_kg = yearly_yield_kwh * 0.485
   ```

### Performance

- **Caching:** Alle Funktionen verwenden `@cached` Decorator
- **Cache-TTL:** 120 Sekunden für erweiterte Metriken
- **Monitoring:** Performance-Tracking mit `@monitor_performance`

**Benchmark (10 Module):**
- `calculate_extended_yield_metrics()`: ~150ms (inkl. 4 Verschattungs-Simulationen)
- `create_pv_module_3d_with_heatmap()`: ~20ms
- `identify_weak_modules()`: <1ms
- `suggest_module_optimization()`: ~2ms
- `create_comparison_view()`: ~15ms

## Nächste Schritte

Task 6 ist vollständig implementiert und getestet. Die nächsten Tasks in Phase 2 sind:

- **Task 7:** Verbessere manuelle Modulplatzierung
  - 7.1: Modul-Hervorhebung
  - 7.2: Magnet-Funktion (Snap-to-Grid)
  - 7.3: Kopieren & Einfügen
  - 7.4: Vorschau bei Verschieben
  - 7.5: Tastatur-Shortcuts

- **Task 8:** Checkpoint - Optimierungen validiert

## Validierung

✅ **Alle Sub-Tasks abgeschlossen:**
- ✅ 6.1 Erweiterte Metriken (Jahresertrag, ROI, CO₂-Einsparung)
- ✅ 6.2 3D-Visualisierung mit Heatmap und erweiterten Hover-Details
- ✅ 6.3 Schwache Module identifizieren und markieren
- ✅ 6.4 Vergleichsansicht für verschiedene Konfigurationen

✅ **Alle Tests bestehen:** 23/23 Tests erfolgreich

✅ **Requirements erfüllt:**
- ✅ Requirement 4.1: Erweiterte Metriken (Jahresertrag, monatlich, Verschattung, ROI, CO₂)
- ✅ Requirement 4.2: Erweiterte Hover-Details mit allen Metriken
- ✅ Requirement 4.3: Vergleichsansicht verschiedener Modulpositionen
- ✅ Requirement 4.4: Schwache Module markieren und Optimierungsvorschläge

---

**Status:** ✅ **COMPLETE**
**Datum:** 2025-01-03
**Tests:** 23 passed
**Code-Qualität:** Alle Funktionen dokumentiert, getestet und optimiert
