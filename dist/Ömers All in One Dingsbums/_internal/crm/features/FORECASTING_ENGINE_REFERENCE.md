# CRM Forecasting Engine - Technical Reference

## Module: forecasting_engine.py

Vollständige technische Dokumentation des Forecasting-Systems.

## Funktionen

### Tabellen-Management

#### `create_forecasting_tables(conn=None)`

Erstellt die Datenbanktabellen für Verkaufsziele und Forecasts.

**Parameter:**
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `bool`: True bei Erfolg, False bei Fehler

**Beispiel:**
```python
from crm.features.forecasting_engine import create_forecasting_tables

success = create_forecasting_tables()
if success:
    print("Tabellen erfolgreich erstellt")
```

#### `ensure_forecasting_tables()`

Stellt sicher, dass die Forecasting-Tabellen existieren.

**Returns:**
- `bool`: True bei Erfolg

---

### Verkaufsziele (Sales Targets)

#### `create_sales_target(...)`

Erstellt ein neues Verkaufsziel.

**Parameter:**
- `target_name` (str): Name des Ziels
- `target_type` (str): 'individual', 'team', 'company'
- `period_type` (str): 'monthly', 'quarterly', 'yearly'
- `period_start` (str): Start-Datum (YYYY-MM-DD)
- `period_end` (str): End-Datum (YYYY-MM-DD)
- `target_value` (float): Zielwert
- `assigned_to` (str, optional): Mitarbeiter-Name (nur bei 'individual')
- `target_unit` (str, optional): Einheit ('EUR', 'deals', 'leads'), default: 'EUR'
- `description` (str, optional): Beschreibung
- `created_by` (str, optional): Ersteller
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `int`: ID des erstellten Ziels oder None bei Fehler

**Beispiel:**
```python
target_id = create_sales_target(
    target_name="Q1 2025 Umsatzziel",
    target_type="company",
    period_type="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31",
    target_value=100000.0,
    description="Quartalsziel"
)
```

#### `get_sales_targets(...)`

Lädt Verkaufsziele mit optionalen Filtern.

**Parameter:**
- `target_type` (str, optional): Filter nach Typ
- `assigned_to` (str, optional): Filter nach Mitarbeiter
- `status` (str, optional): Filter nach Status
- `period_start` (str, optional): Filter nach Start-Datum
- `period_end` (str, optional): Filter nach End-Datum
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `list[dict]`: Liste von Verkaufszielen

**Beispiel:**
```python
# Alle aktiven Company-Ziele
targets = get_sales_targets(target_type="company", status="active")

for target in targets:
    print(f"{target['target_name']}: {target['current_value']}/{target['target_value']}")
```

#### `update_target_progress(target_id, current_value, conn=None)`

Aktualisiert den Fortschritt eines Verkaufsziels.

**Parameter:**
- `target_id` (int): ID des Ziels
- `current_value` (float): Aktueller Wert
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `bool`: True bei Erfolg

**Beispiel:**
```python
success = update_target_progress(target_id=1, current_value=50000.0)
```

#### `update_target_status(target_id, status, conn=None)`

Aktualisiert den Status eines Verkaufsziels.

**Parameter:**
- `target_id` (int): ID des Ziels
- `status` (str): Neuer Status ('active', 'completed', 'failed', 'cancelled')
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `bool`: True bei Erfolg

**Beispiel:**
```python
success = update_target_status(target_id=1, status="completed")
```

---

### Forecasting

#### `calculate_pipeline_forecast(period_start, period_end, conn=None)`

Berechnet einen Forecast basierend auf Pipeline-Daten mit Wahrscheinlichkeits-Gewichtung.

**Wahrscheinlichkeiten nach Stage:**
- lead: 10%
- qualified: 25%
- proposal: 50%
- negotiation: 75%
- won: 100%
- lost: 0%

**Parameter:**
- `period_start` (str): Start-Datum (YYYY-MM-DD)
- `period_end` (str): End-Datum (YYYY-MM-DD)
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `dict`: Forecast-Daten mit folgender Struktur:
  ```python
  {
      'forecast_value': float,  # Prognostizierter Wert
      'confidence_level': float,  # 0.0 - 1.0
      'details': {
          'total_leads': int,
          'stage_breakdown': {
              'stage_name': {
                  'count': int,
                  'total_value': float,
                  'weighted_value': float
              }
          },
          'period_start': str,
          'period_end': str
      }
  }
  ```

**Konfidenz-Berechnung:**
- 0 Leads: 0.0
- < 5 Leads: 0.3
- < 10 Leads: 0.5
- < 20 Leads: 0.7
- ≥ 20 Leads: 0.85

**Beispiel:**
```python
forecast = calculate_pipeline_forecast(
    period_start="2025-01-01",
    period_end="2025-03-31"
)

print(f"Forecast: {forecast['forecast_value']:,.2f} €")
print(f"Konfidenz: {forecast['confidence_level']:.2%}")
print(f"Basierend auf {forecast['details']['total_leads']} Leads")
```

#### `create_forecast(...)`

Erstellt einen neuen Forecast.

**Parameter:**
- `forecast_period` (str): 'monthly', 'quarterly', 'yearly'
- `period_start` (str): Start-Datum (YYYY-MM-DD)
- `period_end` (str): End-Datum (YYYY-MM-DD)
- `forecast_value` (float): Prognostizierter Wert
- `confidence_level` (float): Konfidenz (0.0 - 1.0)
- `forecast_method` (str, optional): Methode, default: 'pipeline_based'
- `target_id` (int, optional): Verknüpftes Ziel
- `pipeline_data` (dict, optional): Pipeline-Daten
- `calculation_details` (dict, optional): Berechnungsdetails
- `notes` (str, optional): Notizen
- `created_by` (str, optional): Ersteller
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `int`: ID des erstellten Forecasts oder None bei Fehler

**Beispiel:**
```python
forecast_id = create_forecast(
    forecast_period="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31",
    forecast_value=150000.0,
    confidence_level=0.75,
    forecast_method="pipeline_based",
    notes="Basierend auf aktueller Pipeline"
)
```

#### `get_forecasts(...)`

Lädt Forecasts mit optionalen Filtern.

**Parameter:**
- `target_id` (int, optional): Filter nach Ziel-ID
- `period_start` (str, optional): Filter nach Start-Datum
- `period_end` (str, optional): Filter nach End-Datum
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `list[dict]`: Liste von Forecasts

**Beispiel:**
```python
# Alle Forecasts für ein bestimmtes Ziel
forecasts = get_forecasts(target_id=1)

for forecast in forecasts:
    print(f"Forecast: {forecast['forecast_value']:,.2f} € ({forecast['confidence_level']:.2%})")
```

---

### Analyse & Tracking

#### `get_target_achievement_status(target_id, conn=None)`

Berechnet den detaillierten Zielerreichungsstatus.

**Parameter:**
- `target_id` (int): ID des Ziels
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `dict`: Status-Informationen mit folgender Struktur:
  ```python
  {
      'target_id': int,
      'target_value': float,
      'current_value': float,
      'achievement_percentage': float,  # Zielerreichung in %
      'remaining_value': float,  # Verbleibender Wert
      'time_percentage': float,  # Zeitfortschritt in %
      'status': str,  # 'achieved', 'on_track', 'at_risk', 'off_track'
      'health': str,  # 'excellent', 'good', 'warning', 'critical'
      'period_start': str,
      'period_end': str
  }
  ```

**Status-Logik:**
- `achieved` (excellent): Zielerreichung ≥ 100%
- `on_track` (good): Zielerreichung ≥ Zeitfortschritt
- `at_risk` (warning): Zielerreichung ≥ 80% des Zeitfortschritts
- `off_track` (critical): Zielerreichung < 80% des Zeitfortschritts

**Beispiel:**
```python
status = get_target_achievement_status(target_id=1)

print(f"Zielerreichung: {status['achievement_percentage']:.1f}%")
print(f"Zeitfortschritt: {status['time_percentage']:.1f}%")
print(f"Health: {status['health']}")

if status['health'] == 'critical':
    print("⚠️ WARNUNG: Ziel gefährdet!")
```

#### `check_at_risk_targets(conn=None)`

Findet alle gefährdeten Ziele (at_risk oder off_track).

**Parameter:**
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `list[dict]`: Liste gefährdeter Ziele mit Status-Informationen

**Beispiel:**
```python
at_risk = check_at_risk_targets()

if at_risk:
    print(f"⚠️ {len(at_risk)} gefährdete Ziele gefunden:")
    for target_status in at_risk:
        print(f"  - Ziel {target_status['target_id']}: {target_status['health']}")
else:
    print("✅ Alle Ziele auf Kurs!")
```

#### `auto_update_target_progress_from_pipeline(target_id, conn=None)`

Aktualisiert den Zielfortschritt automatisch basierend auf gewonnenen Leads in der Pipeline.

**Parameter:**
- `target_id` (int): ID des Ziels
- `conn` (sqlite3.Connection, optional): Datenbankverbindung

**Returns:**
- `bool`: True bei Erfolg

**Logik:**
- Summiert `estimated_value` aller Leads mit `stage='won'`
- Berücksichtigt nur Leads im Zeitraum des Ziels
- Aktualisiert `current_value` des Ziels

**Beispiel:**
```python
# Automatisches Update für alle aktiven Ziele
targets = get_sales_targets(status='active')

for target in targets:
    success = auto_update_target_progress_from_pipeline(target['id'])
    if success:
        print(f"✅ Ziel {target['target_name']} aktualisiert")
```

---

## Workflow-Beispiele

### Kompletter Workflow: Ziel erstellen und überwachen

```python
from crm.features.forecasting_engine import (
    create_sales_target,
    calculate_pipeline_forecast,
    create_forecast,
    get_target_achievement_status,
    auto_update_target_progress_from_pipeline
)

# 1. Ziel erstellen
target_id = create_sales_target(
    target_name="Q1 2025 Umsatzziel",
    target_type="company",
    period_type="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31",
    target_value=100000.0
)

# 2. Forecast berechnen
forecast_data = calculate_pipeline_forecast(
    period_start="2025-01-01",
    period_end="2025-03-31"
)

# 3. Forecast speichern
forecast_id = create_forecast(
    forecast_period="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31",
    forecast_value=forecast_data['forecast_value'],
    confidence_level=forecast_data['confidence_level'],
    target_id=target_id,
    pipeline_data=forecast_data['details']
)

# 4. Fortschritt automatisch aktualisieren
auto_update_target_progress_from_pipeline(target_id)

# 5. Status prüfen
status = get_target_achievement_status(target_id)

print(f"Ziel: {status['achievement_percentage']:.1f}% erreicht")
print(f"Health: {status['health']}")
```

### Tägliche Überwachung

```python
from crm.features.forecasting_engine import (
    get_sales_targets,
    auto_update_target_progress_from_pipeline,
    check_at_risk_targets
)

# Alle aktiven Ziele aktualisieren
active_targets = get_sales_targets(status='active')

for target in active_targets:
    auto_update_target_progress_from_pipeline(target['id'])

# Gefährdete Ziele prüfen
at_risk = check_at_risk_targets()

if at_risk:
    # Benachrichtigungen versenden
    for target_status in at_risk:
        print(f"⚠️ Ziel {target_status['target_id']} benötigt Aufmerksamkeit!")
```

---

## Performance-Hinweise

1. **Batch-Updates**: Verwenden Sie eine gemeinsame Datenbankverbindung für mehrere Operationen
2. **Indizes**: Die Tabellen haben Indizes auf häufig verwendeten Feldern
3. **Caching**: Forecast-Berechnungen können gecacht werden für wiederholte Abfragen

## Fehlerbehandlung

Alle Funktionen geben `None`, `False` oder leere Listen bei Fehlern zurück und loggen Fehler in die Konsole.

**Beispiel:**
```python
target_id = create_sales_target(...)

if target_id is None:
    print("Fehler beim Erstellen des Ziels - siehe Konsole für Details")
```

## Integration mit anderen Modulen

### CRM Pipeline
```python
# Automatisches Update bei Lead-Status-Änderung
def on_lead_won(lead_id, estimated_value):
    # Aktualisiere alle relevanten Ziele
    targets = get_sales_targets(status='active')
    for target in targets:
        auto_update_target_progress_from_pipeline(target['id'])
```

### Benachrichtigungssystem
```python
from crm.utils.notification_manager import create_reminder

# Erstelle Erinnerung für gefährdete Ziele
at_risk = check_at_risk_targets()
for target_status in at_risk:
    create_reminder(
        reminder_type='target_at_risk',
        related_id=target_status['target_id'],
        message=f"Ziel gefährdet: {target_status['achievement_percentage']:.1f}% erreicht"
    )
```

---

## Version History

- **v1.0** (2025-01-14): Initiale Implementierung
  - Verkaufsziele (CRUD)
  - Pipeline-basierte Forecasts
  - Zielerreichungs-Tracking
  - Warnungen für gefährdete Ziele
