# PV-Berechnungsalgorithmen Integration

## Überblick

Die umfassenden PV-Berechnungsalgorithmen aus `kalkulationen.py` wurden erfolgreich in die Anwendung integriert. Diese Implementierung bietet sowohl Python- als auch TypeScript-Unterstützung.

## Neue Module

### 1. `pv_calculations_core.py`

**Zweck**: Kernmodule der PV-Berechnungsalgorithmen für Python/Streamlit  
**Inhalt**:

- Grundberechnungen (Ertrag, Eigenverbrauch, Autarkie)
- Wirtschaftlichkeit (ROI, NPV, IRR, Amortisation)
- Speicherberechnungen und Optimierungen  
- Umwelt/CO2-Bilanz
- Finanzierung/Steuern
- Monte-Carlo-Simulation
- Erweiterte Analysen mit `PVCalculationsAdvanced` Klasse

### 2. `pvCalculationsAdvanced.ts`

**Zweck**: TypeScript-Äquivalente für React/Electron-App  
**Inhalt**:

- Alle Python-Funktionen portiert nach TypeScript
- React Hook `useAdvancedPvCalculations`
- Typdefinitionen für alle Berechnungsresultate
- Umfassende Eingabevalidierung und Fehlerbehandlung

## Integration in bestehende Module

### `calculations.py` - Erweitert

- Import der neuen Kernberechnungen
- Integration in `perform_calculations()` Funktion
- Erweiterte Ergebnisse werden zu bestehenden Resultaten hinzugefügt
- Fallback-Mechanismen bei Import-Fehlern

### `pvCalculations.ts` - Erweitert  

- Import der erweiterten TypeScript-Berechnungen
- Integration in `computePvResults()` Funktion
- Erweiterte Interface-Definitionen
- Rückwärtskompatibilität gewährleistet

## Verfügbare Berechnungsalgorithmen

### Grundberechnungen

```python
- calculate_annual_energy_yield()        # Jahresenergieertrag  
- calculate_self_consumption_quote()     # Eigenverbrauchsquote
- calculate_autarky_degree()             # Autarkiegrad
- calculate_specific_yield()             # Spezifischer Ertrag
- calculate_performance_ratio()          # Performance Ratio
```

### Wirtschaftlichkeit

```python
- calculate_payback_period()             # Amortisationszeit
- calculate_annual_cost_savings()        # Jährliche Einsparungen
- calculate_net_present_value()          # Kapitalwert (NPV)
- calculate_irr()                        # Interner Zinsfuß
- calculate_total_roi()                  # Gesamtrendite
```

### Speicherberechnungen

```python
- calculate_storage_coverage_degree()    # Speicherdeckungsgrad
- calculate_optimal_storage_size()       # Optimale Speichergröße
- calculate_emergency_power_capacity()   # Notstromkapazität
```

### Umwelt/Nachhaltigkeit

```python
- calculate_co2_savings()                # CO2-Einsparung
- calculate_co2_payback_time()           # CO2-Amortisationszeit
- calculate_detailed_co2_analysis()      # Detaillierte CO2-Bilanz
```

### Finanzierung

```python
- calculate_annuity()                    # Annuitätendarlehen
- calculate_leasing_costs()              # Leasingkosten
```

### Erweiterte Analysen

```python
- run_monte_carlo_simulation()           # Risikobewertung
- generate_optimization_suggestions()    # Optimierungsvorschläge
- calculate_comprehensive_pv_analysis()  # Vollständige Analyse
```

## Verwendung

### Python/Streamlit

```python
from pv_calculations_core import calculate_comprehensive_pv_analysis

# Projektdaten vorbereiten
project_data = {
    "anlage_kwp": 10,
    "annual_pv_production_kwh": 9500,
    "annual_consumption_kwh": 4000,
    "self_consumption_kwh": 2800,
    "total_investment_netto": 20000,
    "electricity_price_eur_kwh": 0.30,
    "feed_in_tariff_eur_kwh": 0.08
}

# Umfassende Analyse durchführen
results = calculate_comprehensive_pv_analysis(project_data)

# Ergebnisse verfügbar:
print(f"NPV: {results['npv_eur']} €")
print(f"IRR: {results['irr_percent']} %")
print(f"CO2-Einsparung: {results['annual_co2_savings_kg']} kg/Jahr")
```

### TypeScript/React

```typescript
import { useAdvancedPvCalculations } from '../utils/pvCalculationsAdvanced';

function PvAnalysisComponent() {
  const input = {
    pv_power_kwp: 10,
    annual_production_kwh: 9500,
    annual_consumption_kwh: 4000,
    self_consumption_kwh: 2800,
    investment_costs_eur: 20000,
    electricity_price_eur_kwh: 0.30,
    feed_in_tariff_eur_kwh: 0.08
  };

  const results = useAdvancedPvCalculations(input);

  return (
    <div>
      <h3>Erweiterte PV-Analyse</h3>
      <p>NPV: {results?.npv_eur}€</p>
      <p>IRR: {results?.irr_percent}%</p>
      <p>CO2-Einsparung: {results?.annual_co2_savings_kg} kg/Jahr</p>
      
      {results?.monte_carlo_analysis && (
        <div>
          <h4>Risikobewertung</h4>
          <p>Erfolgswahrscheinlichkeit: {results.monte_carlo_analysis.success_probability}%</p>
        </div>
      )}
    </div>
  );
}
```

## Neue Ergebnisfelder

Die Integration fügt folgende neue Felder zu den Berechnungsergebnissen hinzu:

### Python (`calculations.py`)

```python
results.update({
    "pv_calculations_core_results": ...,           # Vollständige erweiterte Ergebnisse
    "extended_npv_eur": ...,                       # Erweiterter NPV
    "extended_irr_percent": ...,                   # Erweiterter IRR
    "extended_payback_years": ...,                 # Erweiterte Amortisation
    "monte_carlo_success_probability": ...,        # MC-Erfolgswahrscheinlichkeit
    "co2_total_savings_lifetime_tons": ...,        # CO2-Einsparung Lebensdauer
    "co2_tree_equivalent": ...,                    # CO2-Baumäquivalent
    "optimization_suggestions_available": ...,     # Optimierungsvorschläge verfügbar
})
```

### TypeScript (`pvCalculations.ts`)

```typescript
interface PvCalcResult {
  // ... bestehende Felder
  
  // Neue erweiterte Felder:
  extended_analysis?: any;                         // Vollständige erweiterte Analyse
  monte_carlo_success_probability?: number;       // MC-Erfolgswahrscheinlichkeit
  co2_total_savings_lifetime_tons?: number;       // CO2-Lebensdauer-Einsparung
  optimization_suggestions_count?: number;        // Anzahl Optimierungsvorschläge
}
```

## Sicherheit und Robustheit

### Eingabevalidierung

- Alle numerischen Eingaben werden mit `safe_float()` validiert
- Plausibilitätsprüfungen für kritische Parameter
- Division durch Null wird abgefangen mit `safe_divide()`
- Wertebereich-Validierung (z.B. Prozente 0-100%)

### Fehlerbehandlung

- Try-catch um alle erweiterten Berechnungen
- Graceful Fallbacks bei Importfehlern
- Detaillierte Fehlermeldungen für Debugging
- Keine Unterbrechung der Hauptberechnungen bei Fehlern

### Performance

- Berechnungen nur bei plausiblen Eingabedaten
- Caching von aufwendigen Operationen
- Optimierte Algorithmen für Monte-Carlo-Simulation
- Lazy Loading der erweiterten Module

## Testing

### Testbare Komponenten

- Alle Berechnungsfunktionen sind Unit-testbar
- Deterministische Monte-Carlo-Simulation mit Seed
- Mock-Daten für Entwicklung verfügbar
- Benchmark-Tests für Performance

### Validierung

- Vergleich mit bekannten Referenzwerten
- Cross-Validation zwischen Python und TypeScript
- End-to-End Tests für Berechnungsketten
- Edge-Case Tests (Nullwerte, Extremwerte)

## Migration und Kompatibilität

### Rückwärtskompatibilität

- Alle bestehenden Funktionen bleiben unverändert
- Bestehende APIs werden nicht gebrochen
- Schrittweise Migration möglich
- Fallback auf bestehende Berechnungen

### Erweiterbarkeit  

- Modulare Architektur für neue Algorithmen
- Plugin-System für spezielle Berechnungen
- Konfigurierbare Parameter über Admin-Panel
- Internationalisierung vorbereitet

## Nächste Schritte

1. **UI-Integration**: Erweiterte Ergebnisse in BuildingData und Analysis anzeigen
2. **Dashboard**: CO2-Bilanz und Monte-Carlo-Ergebnisse visualisieren  
3. **PDF-Reports**: Optimierungsvorschläge in PDF-Generierung integrieren
4. **Admin-Panel**: Konfiguration der Berechnungsparameter
5. **Performance**: Caching und Optimierung bei großen Datenmengen

## Dokumentation

- Alle Funktionen sind vollständig dokumentiert
- Beispiele für häufige Anwendungsfälle
- API-Referenz für Entwickler
- Benutzerhandbuch für Endanwender

Die Integration ist vollständig rückwärtskompatibel und erweitert die bestehenden Berechnungen um über 25 neue Algorithmen, ohne die bestehende Funktionalität zu beeinträchtigen.
