# CRM Forecasting System - Quick Reference

## Übersicht

Das Forecasting-System ermöglicht die Definition von Verkaufszielen und die automatische Berechnung von Sales Forecasts basierend auf Pipeline-Daten.

## Hauptfunktionen

### 1. Verkaufsziele (Sales Targets)

**Ziel-Typen:**
- `company` - Unternehmensziel
- `team` - Team-Ziel
- `individual` - Individuelles Ziel (Mitarbeiter)

**Zeiträume:**
- `monthly` - Monatlich
- `quarterly` - Quartalsweise
- `yearly` - Jährlich

**Status:**
- `active` - Aktiv
- `completed` - Abgeschlossen
- `failed` - Nicht erreicht
- `cancelled` - Abgebrochen

### 2. Forecasts

**Forecast-Methoden:**
- `pipeline_based` - Basierend auf Pipeline-Daten mit Wahrscheinlichkeits-Gewichtung
- `historical` - Basierend auf historischen Daten
- `manual` - Manuell eingegeben

**Wahrscheinlichkeits-Gewichtung nach Stage:**
- Lead: 10%
- Qualified: 25%
- Proposal: 50%
- Negotiation: 75%
- Won: 100%
- Lost: 0%

### 3. Zielerreichungs-Status

**Health-Status:**
- `excellent` - 🟢 Ziel erreicht (≥100%)
- `good` - 🔵 Auf Kurs (Fortschritt ≥ Zeitfortschritt)
- `warning` - 🟠 Gefährdet (Fortschritt ≥ 80% des Zeitfortschritts)
- `critical` - 🔴 Kritisch (Fortschritt < 80% des Zeitfortschritts)

## Verwendung

### Verkaufsziel erstellen

```python
from crm.features.forecasting_engine import create_sales_target

target_id = create_sales_target(
    target_name="Q1 2025 Umsatzziel",
    target_type="company",
    period_type="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31",
    target_value=100000.0,
    target_unit="EUR",
    description="Quartalsziel für das gesamte Unternehmen",
    created_by="Admin"
)
```

### Forecast berechnen

```python
from crm.features.forecasting_engine import calculate_pipeline_forecast

forecast = calculate_pipeline_forecast(
    period_start="2025-01-01",
    period_end="2025-03-31"
)

print(f"Prognostizierter Wert: {forecast['forecast_value']:.2f} €")
print(f"Konfidenz: {forecast['confidence_level']:.2%}")
```

### Zielerreichung prüfen

```python
from crm.features.forecasting_engine import get_target_achievement_status

status = get_target_achievement_status(target_id)

print(f"Zielerreichung: {status['achievement_percentage']:.1f}%")
print(f"Health: {status['health']}")
```

### Gefährdete Ziele finden

```python
from crm.features.forecasting_engine import check_at_risk_targets

at_risk = check_at_risk_targets()

for target_status in at_risk:
    print(f"Ziel {target_status['target_id']}: {target_status['health']}")
```

## UI-Integration

### Dashboard anzeigen

```python
import streamlit as st
from crm.features.forecasting_ui import render_forecasting_dashboard

render_forecasting_dashboard()
```

## Datenbank-Schema

### sales_targets

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | INTEGER | Primärschlüssel |
| target_name | TEXT | Name des Ziels |
| target_type | TEXT | 'individual', 'team', 'company' |
| assigned_to | TEXT | Mitarbeiter (bei individual) |
| period_type | TEXT | 'monthly', 'quarterly', 'yearly' |
| period_start | DATE | Start-Datum |
| period_end | DATE | End-Datum |
| target_value | REAL | Zielwert |
| target_unit | TEXT | Einheit ('EUR', 'deals', 'leads') |
| current_value | REAL | Aktueller Wert |
| status | TEXT | Status des Ziels |
| description | TEXT | Beschreibung |
| created_at | TIMESTAMP | Erstellungsdatum |
| updated_at | TIMESTAMP | Aktualisierungsdatum |
| created_by | TEXT | Ersteller |

### sales_forecasts

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | INTEGER | Primärschlüssel |
| target_id | INTEGER | Verknüpftes Ziel (optional) |
| forecast_period | TEXT | Zeitraum-Typ |
| period_start | DATE | Start-Datum |
| period_end | DATE | End-Datum |
| forecast_value | REAL | Prognostizierter Wert |
| confidence_level | REAL | Konfidenz (0.0 - 1.0) |
| forecast_method | TEXT | Methode |
| pipeline_data | TEXT | JSON mit Pipeline-Daten |
| calculation_details | TEXT | JSON mit Berechnungsdetails |
| notes | TEXT | Notizen |
| created_at | TIMESTAMP | Erstellungsdatum |
| created_by | TEXT | Ersteller |

## Best Practices

1. **Realistische Ziele setzen**: Basieren Sie Ziele auf historischen Daten und aktueller Pipeline
2. **Regelmäßig aktualisieren**: Nutzen Sie `auto_update_target_progress_from_pipeline()` für automatische Updates
3. **Warnungen beachten**: Prüfen Sie regelmäßig gefährdete Ziele mit `check_at_risk_targets()`
4. **Forecasts dokumentieren**: Speichern Sie Forecasts mit Notizen für spätere Analysen
5. **Zeiträume anpassen**: Wählen Sie Zeiträume passend zur Verkaufszykluslänge

## Troubleshooting

**Problem**: Forecast-Wert ist 0
- **Lösung**: Prüfen Sie, ob Leads in der Pipeline vorhanden sind und `estimated_value` gesetzt ist

**Problem**: Konfidenz ist niedrig
- **Lösung**: Mehr Leads in die Pipeline aufnehmen (Konfidenz steigt mit Anzahl der Leads)

**Problem**: Ziel wird nicht als gefährdet erkannt
- **Lösung**: Prüfen Sie, ob der Zeitraum korrekt ist und ob `current_value` aktualisiert wurde

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Logs in der Konsole
2. Führen Sie die Tests aus: `python crm/features/test_forecasting.py`
3. Kontaktieren Sie den Support mit Fehlermeldungen
