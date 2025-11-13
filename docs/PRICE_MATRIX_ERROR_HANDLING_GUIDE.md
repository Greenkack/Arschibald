# Preismatrix Error Handling Guide

## Übersicht

Das Preismatrix-System verfügt über eine robuste Fehlerbehandlung, die spezifische Fehlermeldungen, Fallback-Strategien und umfassendes Logging bietet.

## Features

### 1. Spezifische Fehlermeldungen

Jeder Fehlertyp hat eine eindeutige Fehlermeldung mit Kontext:

- **no_matrix**: Keine aktive Matrix gefunden
- **empty_matrix**: Matrix ist leer (keine Zeilen/Spalten)
- **no_row**: Modulanzahl nicht in Matrix gefunden
- **no_column**: Speichermodell nicht in Matrix gefunden
- **no_price**: Preis-Zelle ist leer
- **invalid_price**: Ungültiger Preiswert
- **invalid_input**: Ungültige Eingabeparameter

### 2. Benutzerfreundliche Fehlermeldungen

Alle Fehler werden in benutzerfreundliche Nachrichten umgewandelt:

```python
from price_matrix_lookup import calculate_price_from_matrix

result = calculate_price_from_matrix(10, "30kWh")

if not result['success']:
    print(result['user_message'])
    # Ausgabe:
    # ❌ Speichermodell '30kWh' nicht in Preismatrix gefunden.
    #
    # Verfügbare Speichermodelle:
    # • 10kWh
    # • 15kWh
    # • Kein Speicher
    #
    # Lösungsvorschläge:
    # • Wählen Sie ein verfügbares Speichermodell
    # • Wählen Sie 'Kein Speicher' wenn kein Speicher gewünscht
    # • Ergänzen Sie die Preismatrix im Admin-Bereich
```

### 3. Fallback-Strategien

Optional können Fallback-Strategien aktiviert werden:

```python
# Mit Fallback: Verwendet "Kein Speicher" wenn Modell nicht gefunden
result = calculate_price_from_matrix(
    10, "30kWh", 
    enable_fallback=True
)

if result['success'] and result['fallback_used']:
    print(f"Fallback verwendet: {result['fallback_info']['message']}")
    # Ausgabe:
    # Fallback verwendet: Hinweis: Speichermodell '30kWh' nicht verfügbar. 
    # Preis ohne Speicher wird verwendet.
```

**Verfügbare Fallback-Strategien:**

1. **Speichermodell-Fallback**: Verwendet "Kein Speicher" wenn Modell nicht gefunden
2. **Modulanzahl-Fallback**: Verwendet nächst-kleinere Modulanzahl (bereits in Floor-Logik integriert)

### 4. Umfassendes Logging

Alle Matrix-Lookups werden geloggt:

```python
# Erfolgreicher Lookup
2025-11-13 18:07:21,013 - price_matrix - INFO - Matrix-Lookup erfolgreich: 
base_price=15000.0, row=10, column=10kWh, matrix=Test Matrix, time=22.00ms

# Fehlgeschlagener Lookup
2025-11-13 18:07:20,342 - price_matrix - ERROR - Matrix-Lookup fehlgeschlagen: 
error_type=no_row, message=Modulanzahl 10 nicht in Preismatrix gefunden, 
module_count=10, storage_model=10kWh, matrix_id=95
```

### 5. Eingabe-Validierung

Alle Eingabeparameter werden vor dem Lookup validiert:

```python
from price_matrix_error_handler import validate_input_parameters

is_valid, error_msg = validate_input_parameters(module_count, storage_model)

if not is_valid:
    print(f"Ungültige Eingabe: {error_msg}")
```

**Validierungsregeln:**

- Modulanzahl muss eine Zahl > 0 sein
- Modulanzahl darf nicht unrealistisch hoch sein (> 10000)
- Speichermodell muss String oder None sein
- Speichermodell darf nicht leer sein

### 6. Edge Case Handling

Spezielle Behandlung für Edge Cases:

- Leere Matrix (keine Zeilen/Spalten)
- Matrix ohne Datenzeilen (nur Header)
- Matrix ohne Speicher-Spalten
- Ungültige Matrix-Struktur

## Verwendung

### Basis-Verwendung

```python
from price_matrix_lookup import calculate_price_from_matrix

result = calculate_price_from_matrix(
    module_count=20,
    storage_model="15kWh"
)

if result['success']:
    print(f"Preis: {result['base_price']} EUR")
    print(f"Matrix: {result['matrix_name']}")
    print(f"Zeile: {result['row_used']}")
    print(f"Spalte: {result['column_used']}")
else:
    print(f"Fehler: {result['user_message']}")
```

### Mit Fallback

```python
result = calculate_price_from_matrix(
    module_count=20,
    storage_model="30kWh",  # Nicht vorhanden
    enable_fallback=True     # Verwendet "Kein Speicher" als Fallback
)

if result['success']:
    if result['fallback_used']:
        print(f"Hinweis: {result['fallback_info']['message']}")
    print(f"Preis: {result['base_price']} EUR")
```

### Mit spezifischer Matrix

```python
result = calculate_price_from_matrix(
    module_count=20,
    storage_model="15kWh",
    matrix_id=5  # Spezifische Matrix-ID
)
```

## Error Response Format

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
    'error': str | None,          # Technische Fehlermeldung
    'error_type': str | None,     # Fehlertyp für Programmlogik
    'user_message': str | None,   # Benutzerfreundliche Fehlermeldung
    'fallback_used': bool,        # True wenn Fallback verwendet
    'fallback_info': dict | None, # Details zum Fallback
    'debug_info': dict | None     # Debug-Informationen bei Fehler
}
```

## Exception Classes

Für erweiterte Fehlerbehandlung stehen spezifische Exception-Klassen zur Verfügung:

```python
from price_matrix_error_handler import (
    PriceMatrixError,           # Basis-Exception
    MatrixNotFoundError,        # Matrix nicht gefunden
    ModuleCountNotFoundError,   # Modulanzahl nicht gefunden
    StorageModelNotFoundError,  # Speichermodell nicht gefunden
    PriceCellEmptyError,        # Preis-Zelle leer
    InvalidPriceError           # Ungültiger Preiswert
)

try:
    # ... Matrix-Operationen
    pass
except ModuleCountNotFoundError as e:
    print(f"Modulanzahl nicht gefunden: {e}")
    print(f"Verfügbare Modulanzahlen: {e.details['available_counts']}")
except StorageModelNotFoundError as e:
    print(f"Speichermodell nicht gefunden: {e}")
    print(f"Verfügbare Modelle: {e.details['available_models']}")
```

## Logging-Konfiguration

Das Logging kann angepasst werden:

```python
from price_matrix_error_handler import logger
import logging

# Log-Level ändern
logger.setLevel(logging.DEBUG)  # Zeigt alle Debug-Meldungen

# Zusätzlichen Handler hinzufügen (z.B. File-Handler)
file_handler = logging.FileHandler('price_matrix.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

## Best Practices

### 1. Immer Error Handling verwenden

```python
result = calculate_price_from_matrix(module_count, storage_model)

if not result['success']:
    # Zeige benutzerfreundliche Fehlermeldung
    st.error(result['user_message'])
    # Logge technische Details
    logger.error(f"Price lookup failed: {result['error']}")
    return None

return result['base_price']
```

### 2. Fallback nur wenn sinnvoll

```python
# Fallback für Benutzer-Eingaben (z.B. Konfigurator)
result = calculate_price_from_matrix(
    module_count, 
    storage_model, 
    enable_fallback=True  # Benutzerfreundlich
)

# Kein Fallback für Admin-Operationen
result = calculate_price_from_matrix(
    module_count, 
    storage_model, 
    enable_fallback=False  # Strikt, zeigt Fehler
)
```

### 3. Verfügbare Optionen anzeigen

```python
result = calculate_price_from_matrix(module_count, storage_model)

if not result['success'] and result['error_type'] == 'no_column':
    # Zeige verfügbare Speichermodelle
    matrix_data = price_matrix_store.get_matrix_full(result['matrix_id'])
    available_models = _extract_available_storage_models(matrix_data)
    
    st.selectbox(
        "Verfügbare Speichermodelle:",
        options=available_models
    )
```

## Testing

Umfassende Tests sind verfügbar:

```bash
python test_price_matrix_error_handling.py
```

**Getestete Szenarien:**

- Validierung ungültiger Eingaben
- Edge Case: Leere Matrix
- Edge Case: Keine aktive Matrix
- Modulanzahl nicht gefunden
- Speichermodell nicht gefunden
- Leere Preis-Zelle
- Fallback-Strategien
- Benutzerfreundliche Fehlermeldungen
- Logging-Funktionalität

## Troubleshooting

### Problem: Keine Logs sichtbar

**Lösung:** Log-Level erhöhen

```python
from price_matrix_error_handler import logger
import logging

logger.setLevel(logging.DEBUG)
```

### Problem: Fallback funktioniert nicht

**Lösung:** Prüfen ob `enable_fallback=True` gesetzt ist

```python
result = calculate_price_from_matrix(
    module_count, 
    storage_model, 
    enable_fallback=True  # Wichtig!
)
```

### Problem: Fehlermeldungen nicht benutzerfreundlich

**Lösung:** Verwenden Sie `user_message` statt `error`

```python
# Falsch
print(result['error'])  # Technische Meldung

# Richtig
print(result['user_message'])  # Benutzerfreundliche Meldung
```

## Requirements

Erfüllt folgende Requirements:

- **4.4**: Fehlermeldungen bei fehlenden Werten in Matrix
- **1.5**: Aussagekräftige Fehlermeldungen
- **3.4**: Fehlermeldung wenn Matrix-Datei nicht gefunden

## Siehe auch

- [Price Matrix Structure Guide](PRICE_MATRIX_STRUCTURE_GUIDE.md)
- [Price Matrix Lookup Reference](../price_matrix_lookup.py)
- [Error Handler Reference](../price_matrix_error_handler.py)
