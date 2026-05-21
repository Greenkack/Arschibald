# Preismatrix-System API Dokumentation

## Übersicht

Das Preismatrix-System bietet eine robuste, Excel-ähnliche INDEX/MATCH Logik für die Preisberechnung von PV-Anlagen. Diese Dokumentation beschreibt alle verfügbaren APIs und deren Verwendung.

## Inhaltsverzeichnis

1. [Schnellstart](#schnellstart)
2. [Matrix-Verwaltung](#matrix-verwaltung)
3. [Preis-Lookup](#preis-lookup)
4. [Fehlerbehandlung](#fehlerbehandlung)
5. [Performance-Monitoring](#performance-monitoring)
6. [Best Practices](#best-practices)

---

## Schnellstart

### Einfacher Preis-Lookup

```python
from price_matrix_lookup import calculate_price_from_matrix

# Berechne Preis für 20 Module mit 15kWh Speicher
result = calculate_price_from_matrix(
    module_count=20,
    storage_model="15kWh"
)

if result['success']:
    print(f"Preis: {result['base_price']} EUR")
    print(f"Zeile: {result['row_used']}, Spalte: {result['column_used']}")
else:
    print(f"Fehler: {result['user_message']}")
```

### Matrix hochladen

```python
from admin_price_matrix_upload import upload_price_matrix

# CSV-Datei hochladen
with open('price_matrix.csv', 'r') as f:
    csv_data = f.read()

success, message = upload_price_matrix(
    csv_data=csv_data,
    matrix_name="Preisliste 2024"
)

if success:
    print("Matrix erfolgreich hochgeladen!")
else:
    print(f"Fehler: {message}")
```

---

## Matrix-Verwaltung

### `price_matrix_store` Modul

#### Matrix erstellen

```python
from price_matrix_store import create_matrix

matrix_id = create_matrix(
    name="Preisliste Q1 2024",
    description="Aktuelle Preise für Q1",
    pricing_mode='pauschal',  # oder 'additiv'
    include_accessories=True,
    include_misc=True
)
```

**Parameter:**
- `name` (str): Eindeutiger Name der Matrix
- `description` (str, optional): Beschreibung
- `pricing_mode` (str): 'pauschal' oder 'additiv'
- `include_accessories` (bool): Zubehör einbeziehen
- `include_misc` (bool): Sonstiges einbeziehen

**Returns:** `int` - Matrix-ID oder `None` bei Fehler

#### Matrizen auflisten

```python
from price_matrix_store import list_matrices

matrices = list_matrices()

for matrix in matrices:
    print(f"ID: {matrix['id']}")
    print(f"Name: {matrix['name']}")
    print(f"Aktiv: {matrix['is_active']}")
    print(f"Modus: {matrix['pricing_mode']}")
```

**Returns:** `List[dict]` - Liste aller Matrizen mit Metadaten

#### Aktive Matrix setzen

```python
from price_matrix_store import set_active_matrix

success = set_active_matrix(matrix_id=5)
```

**Parameter:**
- `matrix_id` (int): ID der zu aktivierenden Matrix

**Returns:** `bool` - True bei Erfolg

#### Matrix-Daten abrufen

```python
from price_matrix_store import get_matrix_full

matrix_data = get_matrix_full(matrix_id=5)

if matrix_data:
    print(f"Name: {matrix_data['meta']['name']}")
    print(f"Zeilen: {len(matrix_data['rows'])}")
    print(f"Spalten: {len(matrix_data['columns'])}")
    
    # Als DataFrame
    df = matrix_data['wide']
    print(df)
```

**Returns:** `dict` mit folgenden Feldern:
- `meta`: Metadaten (Name, Beschreibung, etc.)
- `rows`: Liste der Zeilen
- `columns`: Liste der Spalten
- `cells`: Dictionary der Zellwerte
- `wide`: pandas DataFrame

#### Matrix klonen

```python
from price_matrix_store import clone_matrix

new_matrix_id = clone_matrix(
    matrix_id=5,
    new_name="Preisliste Q2 2024"
)
```

#### Matrix löschen

```python
from price_matrix_store import delete_matrix

success = delete_matrix(matrix_id=5)
```

#### Zeilen und Spalten hinzufügen

```python
from price_matrix_store import add_row, add_column

# Zeile hinzufügen (z.B. für 25 Module)
row_id = add_row(
    matrix_id=5,
    label="25",
    position=None  # Am Ende einfügen
)

# Spalte hinzufügen (z.B. für neues Speichermodell)
column_id = add_column(
    matrix_id=5,
    label="20kWh Speicher",
    position=None
)
```

#### Zellwert setzen

```python
from price_matrix_store import set_cell_value

success = set_cell_value(
    matrix_id=5,
    row_id=10,
    column_id=3,
    value=18500.00,
    raw_input="18500",
    data_type='number'
)
```

**Parameter:**
- `matrix_id` (int): Matrix-ID
- `row_id` (int): Zeilen-ID
- `column_id` (int): Spalten-ID
- `value` (float): Numerischer Wert
- `raw_input` (str, optional): Original-Eingabe
- `data_type` (str): 'text', 'number', 'formula', 'date'

---

## Preis-Lookup

### `price_matrix_lookup` Modul

#### Hauptfunktion: `calculate_price_from_matrix`

```python
from price_matrix_lookup import calculate_price_from_matrix

result = calculate_price_from_matrix(
    module_count=20,
    storage_model="15kWh",
    matrix_id=None,  # None = aktive Matrix
    enable_fallback=True
)
```

**Parameter:**
- `module_count` (int): Anzahl der PV-Module
- `storage_model` (str | None): Speichermodell-Name oder None für "Kein Speicher"
- `matrix_id` (int | None): Spezifische Matrix-ID oder None für aktive Matrix
- `enable_fallback` (bool): Fallback-Strategien aktivieren

**Returns:** `dict` mit folgenden Feldern:

```python
{
    'success': bool,              # True wenn Preis gefunden
    'base_price': float | None,   # Gefundener Preis
    'row_used': str | None,       # Verwendetes Zeilen-Label
    'row_id': int | None,         # Verwendete Zeilen-ID
    'column_used': str | None,    # Verwendetes Spalten-Label
    'column_id': int | None,      # Verwendete Spalten-ID
    'matrix_id': int | None,      # Verwendete Matrix-ID
    'matrix_name': str | None,    # Name der Matrix
    'error': str | None,          # Fehlermeldung bei Fehler
    'error_type': str | None,     # Fehlertyp
    'user_message': str | None,   # Benutzerfreundliche Fehlermeldung
    'fallback_used': bool,        # True wenn Fallback verwendet
    'fallback_info': dict | None, # Details zum Fallback
    'debug_info': dict | None     # Debug-Informationen
}
```

#### Fehlertypen

- `invalid_input`: Ungültige Eingabeparameter
- `no_matrix`: Keine aktive Matrix gefunden
- `empty_matrix`: Matrix ist leer
- `no_row`: Modulanzahl nicht in Matrix gefunden
- `no_column`: Speichermodell nicht in Matrix gefunden
- `no_price`: Keine Preis-Zelle an Kreuzung
- `invalid_price`: Zelle enthält ungültigen Wert

#### Beispiele

**Erfolgreicher Lookup:**

```python
result = calculate_price_from_matrix(20, "15kWh")

if result['success']:
    print(f"✅ Preis gefunden: {result['base_price']} EUR")
    print(f"   Zeile: {result['row_used']} (ID: {result['row_id']})")
    print(f"   Spalte: {result['column_used']} (ID: {result['column_id']})")
    print(f"   Matrix: {result['matrix_name']}")
```

**Ohne Speicher:**

```python
result = calculate_price_from_matrix(20, None)  # None = "Kein Speicher"
```

**Mit Fallback:**

```python
result = calculate_price_from_matrix(
    module_count=23,  # Nicht in Matrix
    storage_model="15kWh",
    enable_fallback=True
)

if result['fallback_used']:
    print(f"⚠️ Fallback verwendet: {result['fallback_info']['message']}")
    print(f"   Original: {result['fallback_info']['original_module_count']}")
    print(f"   Verwendet: {result['fallback_info']['fallback_module_count']}")
```

**Fehlerbehandlung:**

```python
result = calculate_price_from_matrix(999, "UnbekannterSpeicher")

if not result['success']:
    print(f"❌ Fehler: {result['user_message']}")
    print(f"   Typ: {result['error_type']}")
    
    # Detaillierte Fehlerinfo
    if result['debug_info']:
        print(f"   Debug: {result['debug_info']}")
```

---

## Fehlerbehandlung

### `price_matrix_error_handler` Modul

#### Benutzerdefinierte Exceptions

```python
from price_matrix_error_handler import (
    MatrixNotFoundError,
    ModuleCountNotFoundError,
    StorageModelNotFoundError,
    PriceCellEmptyError,
    InvalidPriceError
)

try:
    result = calculate_price_from_matrix(20, "15kWh")
    if not result['success']:
        # Fehler basierend auf Typ behandeln
        if result['error_type'] == 'no_matrix':
            print("Keine Matrix aktiv!")
        elif result['error_type'] == 'no_row':
            print("Modulanzahl nicht gefunden!")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
```

#### Benutzerfreundliche Fehlermeldungen

```python
from price_matrix_error_handler import create_user_friendly_error_message

error = ModuleCountNotFoundError(23, [10, 15, 20, 25, 30])
message = create_user_friendly_error_message(error)

print(message)
# Ausgabe:
# ❌ Modulanzahl nicht gefunden
# 
# Die gewählte Modulanzahl (23) ist nicht in der Preismatrix vorhanden.
# 
# Verfügbare Modulanzahlen:
# • 10 Module
# • 15 Module
# • 20 Module
# • 25 Module
# • 30 Module
# 
# 💡 Tipp: Wählen Sie eine der verfügbaren Modulanzahlen.
```

#### Logging

```python
from price_matrix_error_handler import logger

# Logging ist automatisch aktiviert
# Logs werden in logs/price_matrix.log geschrieben

# Manuelles Logging
logger.info("Matrix-Lookup gestartet")
logger.warning("Fallback verwendet")
logger.error("Lookup fehlgeschlagen")
```

---

## Performance-Monitoring

### `price_matrix_performance` Modul

#### Performance-Monitor verwenden

```python
from price_matrix_performance import PerformanceMonitor

# Monitor erstellen
monitor = PerformanceMonitor()

# Operation tracken
with monitor.track_operation('matrix_lookup'):
    result = calculate_price_from_matrix(20, "15kWh")

# Bericht generieren
report = monitor.generate_report()
print(report)
```

**Ausgabe:**

```
======================================================================
PREISMATRIX PERFORMANCE BERICHT
======================================================================

Monitoring-Laufzeit: 0:05:23.456789

OPERATIONS-METRIKEN
----------------------------------------------------------------------

matrix_lookup:
  Ausführungen: 150
  Gesamt-Zeit: 1234.56 ms
  Durchschnitt: 8.23 ms
  Min: 2.45 ms
  Max: 45.67 ms

CACHE-METRIKEN
----------------------------------------------------------------------

matrix_cache:
  Anfragen: 150
  Hits: 145
  Misses: 5
  Hit-Rate: 96.7%
  Einträge: 3
  Speicher: 0.25 MB
  Ø Lookup-Zeit: 0.12 ms

======================================================================
```

#### Decorator für automatisches Tracking

```python
from price_matrix_performance import performance_tracked

@performance_tracked('custom_operation')
def my_function():
    # Ihre Logik hier
    pass

# Funktion wird automatisch getrackt
my_function()
```

#### Benchmark durchführen

```python
from price_matrix_performance import benchmark_matrix_lookup

results = benchmark_matrix_lookup(
    module_counts=[10, 15, 20, 25, 30],
    storage_models=["10kWh", "15kWh", "20kWh", None],
    iterations=100
)

print(f"Gesamt-Lookups: {results['total_lookups']}")
print(f"Erfolgreich: {results['successful_lookups']}")
print(f"Durchschnitt: {results['avg_time_ms']:.2f} ms")
print(f"Lookups/Sekunde: {results['lookups_per_second']:.0f}")
```

#### Cache-Performance analysieren

```python
from price_matrix_performance import analyze_cache_performance

analysis = analyze_cache_performance()

print(f"Gesamt Hit-Rate: {analysis['overall_hit_rate']:.1f}%")
print(f"Gesamt Speicher: {analysis['total_memory_mb']:.2f} MB")

for cache_name, info in analysis['caches'].items():
    print(f"\n{cache_name}:")
    print(f"  Hit-Rate: {info['hit_rate']:.1f}%")
    print(f"  Einträge: {info['entry_count']}")
    print(f"  Speicher: {info['memory_mb']:.2f} MB")

# Empfehlungen
for recommendation in analysis['recommendations']:
    print(recommendation)
```

#### Speicherverbrauch prüfen

```python
from price_matrix_performance import get_memory_usage

memory = get_memory_usage()

print(f"Prozess-Speicher: {memory['process_memory_mb']:.2f} MB")
print(f"Matrix-Cache: {memory['matrix_cache_mb']:.2f} MB")
print(f"Objekte: {memory['total_objects']}")
```

---

## Best Practices

### 1. Fehlerbehandlung

Immer das `success` Feld prüfen:

```python
result = calculate_price_from_matrix(20, "15kWh")

if result['success']:
    # Erfolg - Preis verwenden
    price = result['base_price']
else:
    # Fehler - Benutzer informieren
    print(result['user_message'])
```

### 2. Fallback-Strategien

Fallback nur wenn sinnvoll aktivieren:

```python
# Für Benutzer-Eingaben: Fallback aktivieren
result = calculate_price_from_matrix(
    module_count=user_input,
    storage_model=selected_storage,
    enable_fallback=True
)

# Für exakte Berechnungen: Fallback deaktivieren
result = calculate_price_from_matrix(
    module_count=exact_count,
    storage_model=exact_model,
    enable_fallback=False
)
```

### 3. Performance-Optimierung

Cache nutzen durch wiederholte Lookups:

```python
# Erste Anfrage lädt Matrix
result1 = calculate_price_from_matrix(20, "15kWh")

# Weitere Anfragen nutzen Cache (schneller)
result2 = calculate_price_from_matrix(25, "15kWh")
result3 = calculate_price_from_matrix(30, "20kWh")
```

### 4. Matrix-Validierung

Matrix vor Aktivierung validieren:

```python
from price_matrix_validation import validate_matrix_structure

# Matrix hochladen
matrix_id = import_matrix_csv("Neue Matrix", csv_data)

# Validieren
is_valid, errors = validate_matrix_structure(matrix_id)

if is_valid:
    # Aktivieren
    set_active_matrix(matrix_id)
else:
    # Fehler anzeigen
    for error in errors:
        print(f"❌ {error}")
```

### 5. Logging aktivieren

Für Debugging und Monitoring:

```python
import logging

# Logging-Level setzen
logging.basicConfig(level=logging.INFO)

# Jetzt werden alle Matrix-Operationen geloggt
result = calculate_price_from_matrix(20, "15kWh")
```

### 6. Performance-Monitoring

In Produktion aktivieren:

```python
from price_matrix_performance import get_global_monitor

# Monitor holen
monitor = get_global_monitor()

# Regelmäßig Bericht generieren
report = monitor.generate_report()
print(report)

# Optimierungen prüfen
recommendations = monitor.get_optimization_recommendations()
for rec in recommendations:
    print(rec)
```

---

## Erweiterte Verwendung

### Matrix-Export und -Import

```python
from price_matrix_store import export_matrix_csv, import_matrix_csv

# Export
csv_data = export_matrix_csv(matrix_id=5, delimiter=';')

# In Datei speichern
with open('export.csv', 'w') as f:
    f.write(csv_data)

# Import
with open('import.csv', 'r') as f:
    csv_data = f.read()

new_matrix_id = import_matrix_csv(
    name="Importierte Matrix",
    csv_text=csv_data,
    delimiter=';'
)
```

### Batch-Lookups

```python
from price_matrix_lookup import calculate_price_from_matrix

# Mehrere Preise auf einmal berechnen
configurations = [
    (10, "10kWh"),
    (15, "15kWh"),
    (20, "20kWh"),
    (25, None),  # Ohne Speicher
]

results = []
for module_count, storage_model in configurations:
    result = calculate_price_from_matrix(module_count, storage_model)
    results.append(result)

# Erfolgreiche Lookups filtern
successful = [r for r in results if r['success']]
print(f"{len(successful)} von {len(results)} erfolgreich")
```

### Custom Error Handling

```python
from price_matrix_error_handler import (
    MatrixLookupError,
    create_detailed_error_report
)

try:
    result = calculate_price_from_matrix(20, "15kWh")
    
    if not result['success']:
        # Detaillierten Fehlerbericht erstellen
        error_report = create_detailed_error_report(
            Exception(result['error']),
            module_count=20,
            storage_model="15kWh",
            matrix_id=None,
            matrix_data=None
        )
        
        # An Monitoring-System senden
        send_to_monitoring(error_report)
        
except Exception as e:
    print(f"Kritischer Fehler: {e}")
```

---

## API-Referenz

### Vollständige Funktionsliste

#### `price_matrix_store`

- `create_matrix(name, description, pricing_mode, include_accessories, include_misc)` → `int | None`
- `clone_matrix(matrix_id, new_name)` → `int | None`
- `delete_matrix(matrix_id)` → `bool`
- `list_matrices()` → `List[dict]`
- `set_active_matrix(matrix_id)` → `bool`
- `get_active_matrix_id()` → `int | None`
- `add_row(matrix_id, label, position)` → `int | None`
- `add_column(matrix_id, label, position)` → `int | None`
- `remove_row(row_id)` → `bool`
- `remove_column(column_id)` → `bool`
- `set_cell_value(matrix_id, row_id, column_id, value, raw_input, data_type)` → `bool`
- `get_matrix_full(matrix_id)` → `dict | None`
- `export_matrix_csv(matrix_id, delimiter)` → `str | None`
- `import_matrix_csv(name, csv_text, delimiter)` → `int | None`
- `lookup_price(matrix_id, row_label, column_label)` → `float | None`
- `lookup_price_with_meta(matrix_id, row_label, column_label)` → `dict`
- `update_matrix_pricing_mode(matrix_id, pricing_mode, include_accessories, include_misc)` → `bool`

#### `price_matrix_lookup`

- `calculate_price_from_matrix(module_count, storage_model, matrix_id, enable_fallback)` → `dict`
- `find_module_count_row(matrix_data, module_count)` → `Tuple[str | None, int | None]`
- `find_storage_column(matrix_data, storage_model)` → `Tuple[str | None, int | None]`
- `lookup_price_by_intersection(matrix_data, row_id, column_id)` → `float | None`

#### `price_matrix_error_handler`

- `create_user_friendly_error_message(error)` → `str`
- `get_fallback_price(module_count, storage_model, error, matrix_data)` → `dict | None`
- `validate_input_parameters(module_count, storage_model)` → `Tuple[bool, str | None]`
- `handle_edge_cases(module_count, storage_model, matrix_data)` → `dict | None`
- `create_detailed_error_report(exception, module_count, storage_model, matrix_id, matrix_data)` → `dict`

#### `price_matrix_performance`

- `PerformanceMonitor()` - Klasse für Performance-Monitoring
- `performance_tracked(operation_name)` - Decorator für automatisches Tracking
- `get_global_monitor()` → `PerformanceMonitor`
- `reset_global_monitor()` → `None`
- `benchmark_matrix_lookup(module_counts, storage_models, iterations)` → `dict`
- `analyze_cache_performance()` → `dict`
- `get_memory_usage()` → `dict`

---

## Support und Feedback

Bei Fragen oder Problemen:

1. Prüfen Sie die Logs in `logs/price_matrix.log`
2. Verwenden Sie Performance-Monitoring für Diagnose
3. Konsultieren Sie die Fehlerbehandlungs-Dokumentation
4. Kontaktieren Sie das Entwicklungsteam

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024  
**Autor:** Preismatrix-System Team
