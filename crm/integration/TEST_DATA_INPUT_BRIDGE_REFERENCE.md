# Data Input Bridge - Test Reference

## Übersicht

Vollständige Unit Tests für das Data Input Bridge Modul (Task 1.1).

**Test-Datei:** `crm/integration/test_data_input_bridge.py`

## Test-Ausführung

```bash
# Mit pytest (empfohlen)
python -m pytest crm/integration/test_data_input_bridge.py -v

# Direkt ausführen
python crm/integration/test_data_input_bridge.py
```

## Test-Kategorien

### 1. Kundenextraktion Tests (5 Tests)

#### ✅ test_extract_customer_data_complete
- Testet vollständige Extraktion aller Kundenfelder
- Prüft alle 20+ Felder (Name, Adresse, Kontakt, etc.)
- Verifiziert Metadaten (creation_date, last_updated)

#### ✅ test_extract_customer_data_minimal
- Testet Extraktion mit minimalen Daten (nur Pflichtfelder)
- Prüft Default-Werte (num_persons=1, type='Privat')

#### ✅ test_extract_customer_data_whitespace_trimming
- Testet automatisches Entfernen von Whitespace
- Prüft trim() für alle String-Felder

#### ✅ test_extract_customer_data_missing_names_fallback
- Testet Fallback-Logik bei fehlenden Namen
- Firmenname wird als Vor-/Nachname verwendet

#### ✅ test_extract_customer_data_empty_session
- Testet Verhalten bei leerem Session State
- Prüft Default-Werte ('Interessent', 'Unbekannt')

### 2. Projektextraktion Tests (4 Tests)

#### ✅ test_extract_project_data_complete
- Testet vollständige Extraktion aller Projektfelder
- Prüft 30+ Felder (Dach, Verbrauch, Komponenten, etc.)
- Verifiziert Boolean-zu-Integer-Konvertierung

#### ✅ test_extract_project_data_consumption_fallback
- Testet Fallback für Verbrauchsdaten
- Prüft consumption_data als Alternative zu project_details

#### ✅ test_extract_project_data_auto_name_generation
- Testet automatische Projektname-Generierung
- Format: "Projekt YYYY-MM-DD HH:MM"

#### ✅ test_extract_project_data_empty_session
- Testet Verhalten bei leerem Session State
- Prüft Default-Werte für alle Felder

### 3. Validierung Tests (6 Tests)

#### ✅ test_validate_required_fields_valid
- Testet erfolgreiche Validierung mit allen Pflichtfeldern
- Erwartet: is_valid=True, missing=[]

#### ✅ test_validate_required_fields_missing_first_name
- Testet fehlenden Vornamen
- Erwartet: is_valid=False, missing=['Vorname']

#### ✅ test_validate_required_fields_missing_last_name
- Testet fehlenden Nachnamen
- Erwartet: is_valid=False, missing=['Nachname']

#### ✅ test_validate_required_fields_missing_both
- Testet beide fehlende Pflichtfelder
- Erwartet: is_valid=False, missing=['Vorname', 'Nachname']

#### ✅ test_validate_required_fields_whitespace_only
- Testet Felder mit nur Whitespace
- Whitespace wird als fehlend behandelt

#### ✅ test_validate_required_fields_none_values
- Testet None-Werte in Pflichtfeldern
- None wird als fehlend behandelt

### 4. Duplikatsprüfung Tests (6 Tests)

#### ✅ test_check_duplicate_customer_exists
- Testet Erkennung existierender Kunden
- Prüft vollständige Rückgabe der Kundendaten

#### ✅ test_check_duplicate_customer_not_exists
- Testet Verhalten bei nicht existierendem Kunden
- Erwartet: None

#### ✅ test_check_duplicate_customer_case_insensitive
- Testet case-insensitive E-Mail-Suche
- 'max@example.com' = 'MAX@EXAMPLE.COM'

#### ✅ test_check_duplicate_customer_empty_email
- Testet Verhalten bei leerer/None E-Mail
- Erwartet: None (keine Suche)

#### ✅ test_check_duplicate_customer_whitespace_trimming
- Testet automatisches Trimming bei Suche
- '  max@example.com  ' findet 'max@example.com'

#### ✅ test_check_duplicate_customer_error_handling
- Testet Fehlerbehandlung bei DB-Fehlern
- Erwartet: None statt Exception

### 5. Vorschau Tests (2 Tests)

#### ✅ test_get_data_preview_summary
- Testet Erstellung der Vorschau-Zusammenfassung
- Prüft customer, project und counts Strukturen

#### ✅ test_get_data_preview_summary_minimal
- Testet Vorschau mit minimalen Daten
- Prüft korrekte Formatierung

### 6. Integration Test (1 Test)

#### ✅ test_integration_full_workflow
- Testet vollständigen Workflow:
  1. Daten extrahieren
  2. Pflichtfelder validieren
  3. Duplikat prüfen
  4. Vorschau erstellen
- End-to-End Test aller Funktionen

## Test-Ergebnisse

```
======================================================================
  Unit Tests für Data Input Bridge (Task 1.1)
======================================================================

✅ 24/24 Tests bestanden (100%)

Kategorien:
- Kundenextraktion: 5/5 ✅
- Projektextraktion: 4/4 ✅
- Validierung: 6/6 ✅
- Duplikatsprüfung: 6/6 ✅
- Vorschau: 2/2 ✅
- Integration: 1/1 ✅
```

## Abgedeckte Requirements

### ✅ Requirement 1.1: Vollständige Datenextraktion
- Alle Kundenfelder werden korrekt extrahiert
- Alle Projektfelder werden korrekt extrahiert
- Whitespace wird automatisch entfernt
- Fallback-Logik funktioniert

### ✅ Requirement 1.2: Duplikatserkennung
- E-Mail-basierte Duplikatserkennung
- Case-insensitive Suche
- Fehlerbehandlung bei DB-Problemen

### ✅ Requirement 1.3: Fehlerbehandlung bei fehlenden Pflichtfeldern
- Validierung von Vorname und Nachname
- Klare Fehlermeldungen
- Whitespace und None werden erkannt

## Code Coverage

Die Tests decken alle Funktionen im `data_input_bridge.py` Modul ab:

- ✅ `extract_customer_data_from_session()` - 100%
- ✅ `extract_project_data_from_session()` - 100%
- ✅ `check_duplicate_customer()` - 100%
- ✅ `validate_required_fields()` - 100%
- ✅ `get_data_preview_summary()` - 100%

## Verwendung in der Entwicklung

### Test während der Entwicklung ausführen
```bash
# Alle Tests
python -m pytest crm/integration/test_data_input_bridge.py -v

# Einzelner Test
python -m pytest crm/integration/test_data_input_bridge.py::test_extract_customer_data_complete -v

# Mit Coverage
python -m pytest crm/integration/test_data_input_bridge.py --cov=crm.integration.data_input_bridge
```

### Test-Driven Development
1. Test schreiben (rot)
2. Implementierung anpassen (grün)
3. Refactoring (grün bleiben)

## Wartung

### Neue Tests hinzufügen
Wenn neue Funktionen zum `data_input_bridge.py` hinzugefügt werden:

1. Test-Funktion mit `test_` Präfix erstellen
2. Setup, Execute, Assert Pattern verwenden
3. Zur Test-Liste im `__main__` Block hinzufügen
4. Ausführen und verifizieren

### Test-Struktur
```python
def test_neue_funktion():
    """Test: Beschreibung was getestet wird"""
    # Setup - Testdaten vorbereiten
    test_data = {...}
    
    # Execute - Funktion ausführen
    result = neue_funktion(test_data)
    
    # Assert - Ergebnis prüfen
    assert result == expected
    print("✓ Test test_neue_funktion bestanden")
```

## Bekannte Einschränkungen

1. **Streamlit Mock**: Tests verwenden Mock für `streamlit` - keine echte Streamlit-Umgebung
2. **In-Memory DB**: Duplikatsprüfung nutzt SQLite In-Memory - keine persistente DB
3. **Keine UI-Tests**: Nur Backend-Logik wird getestet

## Nächste Schritte

Nach erfolgreicher Implementierung von Task 1.1:

- ✅ Task 1: Automatische Datenübernahme (abgeschlossen)
- ✅ Task 1.1: Unit Tests (abgeschlossen)
- ⏭️ Task 2: Berechnungsergebnisse verknüpfen
- ⏭️ Task 2.1: Unit Tests für Berechnungsverknüpfung

## Support

Bei Fragen oder Problemen:
1. Test-Ausgabe prüfen (detaillierte Fehlermeldungen)
2. Einzelne Tests isoliert ausführen
3. Debug-Prints in Tests hinzufügen
4. Implementierung gegen Test-Erwartungen prüfen
