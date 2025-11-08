# Task 5: Preismatrix-Lookup-Logik - ABGESCHLOSSEN ✓

## Übersicht

Die Preismatrix-Lookup-Logik wurde vollständig implementiert und getestet. Das neue Modul `price_matrix_lookup.py` bietet eine robuste INDEX-basierte Preisabfrage aus der Preismatrix.

## Implementierte Funktionen

### 1. `find_module_count_row(matrix_data, module_count)`

**Zweck:** Findet die Zeile für eine gegebene Modulanzahl in Spalte A.

**Features:**
- ✓ Exakte Übereinstimmung wird bevorzugt
- ✓ Floor-Logik: Bei fehlender Zahl wird die nächst-kleinere verwendet
- ✓ Fehlerbehandlung: Gibt (None, None) zurück wenn keine passende Zeile gefunden

**Beispiel:**
```python
row_label, row_id = find_module_count_row(matrix_data, 18)
# Ergebnis: ('15', 2044) - Nächst-kleinere Zahl ist 15
```

### 2. `find_storage_column(matrix_data, storage_model)`

**Zweck:** Findet die Spalte für ein gegebenes Speichermodell in Zeile 1.

**Features:**
- ✓ Exakte Übereinstimmung mit Modellname (case-insensitive)
- ✓ Bei `storage_model = None`: Sucht "Kein Speicher" Spalte
- ✓ Unterstützt verschiedene Varianten: "Kein Speicher", "Ohne Speicher", "No Storage", etc.
- ✓ Fehlerbehandlung: Gibt (None, None) zurück wenn Modell nicht gefunden

**Beispiel:**
```python
col_label, col_id = find_storage_column(matrix_data, "15kWh")
# Ergebnis: ('15kWh', 429)

col_label, col_id = find_storage_column(matrix_data, None)
# Ergebnis: ('Kein Speicher', 431)
```

### 3. `lookup_price_by_intersection(matrix_data, row_id, column_id)`

**Zweck:** Holt den Preis an der Kreuzung von Zeile und Spalte.

**Features:**
- ✓ Validierung: Zelle muss existieren
- ✓ Validierung: Wert muss eine Zahl sein
- ✓ Unterstützt neues Datenformat mit `data_type` und `value`
- ✓ Fehlerbehandlung: Gibt None zurück bei leerer oder ungültiger Zelle

**Beispiel:**
```python
price = lookup_price_by_intersection(matrix_data, row_id=2045, column_id=429)
# Ergebnis: 23500.0
```

### 4. `calculate_price_from_matrix(module_count, storage_model, matrix_id=None)`

**Zweck:** Haupt-Lookup-Funktion die alle Schritte kombiniert.

**Features:**
- ✓ Lädt Matrix-Daten (aktive Matrix oder spezifische Matrix-ID)
- ✓ Kombiniert alle Lookup-Schritte
- ✓ Umfassende Fehlerbehandlung mit spezifischen Fehlertypen
- ✓ Gibt strukturiertes Ergebnis mit allen Details zurück

**Rückgabe-Struktur:**
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
    'error_type': str | None      # Fehlertyp für spezifische Behandlung
}
```

**Fehlertypen:**
- `no_matrix`: Keine aktive Matrix gefunden
- `no_row`: Modulanzahl nicht in Matrix gefunden
- `no_column`: Speichermodell nicht in Matrix gefunden
- `no_price`: Keine Preis-Zelle an Kreuzung
- `invalid_price`: Zelle enthält ungültigen Wert

**Beispiel:**
```python
result = calculate_price_from_matrix(20, "15kWh")
if result['success']:
    print(f"Preis: {result['base_price']} EUR")
    print(f"Zeile: {result['row_used']}, Spalte: {result['column_used']}")
else:
    print(f"Fehler: {result['error']}")
```

## Test-Ergebnisse

Alle Tests wurden erfolgreich durchgeführt:

### ✓ Test 1: Modulanzahl-Suche
- Exakte Übereinstimmung: ✓
- Floor-Logik (18 -> 15): ✓
- Floor-Logik (23 -> 20): ✓
- Keine passende Zeile (zu klein): ✓
- Größte Zahl (30 -> 25): ✓

### ✓ Test 2: Speichermodell-Suche
- Exakte Übereinstimmung: ✓
- Case-insensitive Suche: ✓
- None -> "Kein Speicher": ✓
- Nicht gefundenes Modell: ✓

### ✓ Test 3: Preis-Lookup
- Gültiger Preis: ✓
- Anderer gültiger Preis: ✓
- Leere Zelle: ✓
- Ungültige IDs: ✓

### ✓ Test 4: Haupt-Lookup-Funktion
- Exakte Übereinstimmung (20 Module, 15kWh): ✓
- Floor-Logik (18 Module -> 15, 10kWh): ✓
- Kein Speicher (10 Module, None): ✓
- Modulanzahl zu klein (5 Module): ✓
- Speichermodell nicht gefunden (30kWh): ✓
- Matrix-ID explizit angeben: ✓

## Verwendung

### Einfaches Beispiel

```python
import price_matrix_lookup

# Preis für 20 Module mit 15kWh Speicher abrufen
result = price_matrix_lookup.calculate_price_from_matrix(20, "15kWh")

if result['success']:
    print(f"Basispreis: {result['base_price']} EUR")
    print(f"Verwendet: Zeile {result['row_used']}, Spalte {result['column_used']}")
else:
    print(f"Fehler: {result['error']}")
```

### Erweiterte Fehlerbehandlung

```python
result = price_matrix_lookup.calculate_price_from_matrix(module_count, storage_model)

if result['success']:
    # Erfolg: Preis verwenden
    base_price = result['base_price']
    
elif result['error_type'] == 'no_matrix':
    # Keine aktive Matrix: Admin benachrichtigen
    show_admin_warning("Bitte aktivieren Sie eine Preismatrix")
    
elif result['error_type'] == 'no_row':
    # Modulanzahl nicht gefunden: Benutzer informieren
    show_user_error(f"Modulanzahl {module_count} nicht verfügbar")
    
elif result['error_type'] == 'no_column':
    # Speichermodell nicht gefunden: Alternative vorschlagen
    show_user_error(f"Speichermodell nicht verfügbar")
    
elif result['error_type'] == 'no_price':
    # Preis nicht definiert: Admin benachrichtigen
    show_admin_warning("Preismatrix unvollständig")
    
else:
    # Allgemeiner Fehler
    show_error(result['error'])
```

## Integration mit bestehenden Systemen

Das Modul ist vollständig kompatibel mit:
- ✓ `price_matrix_store.py` - Verwendet dessen Datenstrukturen
- ✓ `database.py` - Nutzt `get_pricing_calculation_mode()`
- ✓ `excel/excel_models.py` - Kompatibel mit Cell-Datentypen

## Nächste Schritte

Die Lookup-Logik ist nun bereit für die Integration in den Solarcalculator (Task 6):
1. Modus-Prüfung implementieren
2. Matrix-Preisberechnung in Solarcalculator integrieren
3. UI-Anpassungen für Matrix-Modus
4. Standard-Berechnung deaktivieren bei aktivem Matrix-Modus

## Dateien

- **Implementierung:** `price_matrix_lookup.py`
- **Tests:** `test_price_matrix_lookup.py`
- **Dokumentation:** Dieses Dokument

## Anforderungen erfüllt

- ✓ Requirement 4.1: Modulanzahl-Suche mit Floor-Logik
- ✓ Requirement 4.2: Speichermodell-Suche
- ✓ Requirement 4.3: "Kein Speicher" Fallback
- ✓ Requirement 4.4: Preis-Lookup an Kreuzung
- ✓ Requirement 4.5: Strukturiertes Ergebnis
- ✓ Requirement 4.6: Validierung und Fehlerbehandlung
- ✓ Requirement 7.2: Fehler bei fehlender Modulanzahl
- ✓ Requirement 7.3: Fehler bei fehlendem Speichermodell
- ✓ Requirement 7.4: Fehler bei leerer Zelle
- ✓ Requirement 7.5: Fehler bei ungültigem Wert

---

**Status:** ✓ ABGESCHLOSSEN
**Datum:** 2025-11-08
**Getestet:** Ja, alle Tests bestanden
