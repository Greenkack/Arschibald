# Unit Tests für Calculation Bridge - Referenz

## Übersicht

Diese Datei dokumentiert die Unit Tests für das Calculation Bridge Modul, das Berechnungsergebnisse mit Kundenprojekten verknüpft.

**Testdatei:** `crm/integration/test_calculation_bridge.py`

## Ausführung

```bash
python crm/integration/test_calculation_bridge.py
```

## Getestete Funktionen

### 1. Speichern von Berechnungen

**Test:** `test_save_calculation_basic`

- Testet das grundlegende Speichern einer Berechnung
- Überprüft alle Felder (project_id, customer_id, version, calculation_type, etc.)
- Validiert JSON-Serialisierung der Berechnungsdaten

**Test:** `test_save_calculation_versioning`

- Testet automatische Versionierung bei mehreren Berechnungen
- Überprüft dass Versionen korrekt inkrementiert werden (v1, v2, v3)
- Validiert dass jede Berechnung eine eindeutige ID erhält

### 2. Abrufen von Berechnungen

**Test:** `test_get_calculations_for_project`

- Testet das Abrufen aller Berechnungen für ein Projekt
- Überprüft korrekte Sortierung (neueste zuerst)
- Validiert vollständige Datenstruktur

### 3. Hauptangebot-Verwaltung

**Test:** `test_set_main_offer`

- Testet das Markieren einer Berechnung als Hauptangebot
- Überprüft dass nur eine Berechnung als Hauptangebot markiert ist
- Validiert dass andere Berechnungen nicht markiert sind

### 4. Vergleichs-Funktion

**Test:** `test_compare_calculations`

- Testet den Vergleich zweier Berechnungen
- Überprüft Berechnung von absoluten und prozentualen Unterschieden
- Validiert Datenstruktur des Vergleichsergebnisses

### 5. Integration Test

**Test:** `test_integration_full_workflow`

- Testet den vollständigen Workflow:
  1. Erste Berechnung speichern
  2. Zweite Berechnung speichern (automatische Versionierung)
  3. Alle Berechnungen abrufen
  4. Hauptangebot markieren
  5. Hauptangebot abrufen
  6. Berechnungen vergleichen
  7. Berechnung löschen
  8. Verbleibende Berechnungen überprüfen

## Test-Infrastruktur

### NonClosingConnection Wrapper

Die Tests verwenden einen speziellen Wrapper, der verhindert dass die Datenbankverbindung geschlossen wird:

```python
class NonClosingConnection:
    """Wrapper für Datenbankverbindung die close() ignoriert"""
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        if name == 'close':
            return lambda: None
        return getattr(self._conn, name)
```

Dies ist notwendig, weil die calculation_bridge Funktionen die Verbindung nach jeder Operation schließen.

### Test-Datenbank Setup

Jeder Test verwendet eine In-Memory SQLite-Datenbank mit folgenden Tabellen:

- `customers` - Testkundendaten
- `projects` - Testprojektdaten  
- `project_calculations` - Berechnungsdaten

## Anforderungen

Die Tests decken folgende Anforderungen ab:

- **Requirement 2.1:** Berechnungen werden mit dynamischen Keys gespeichert
- **Requirement 2.2:** Automatische Versionierung funktioniert korrekt
- **Requirement 2.3:** Vergleichs-Funktion berechnet Unterschiede korrekt

## Testergebnisse

Alle 6 Tests bestehen erfolgreich:

```
======================================================================
  Unit Tests für Calculation Bridge (Task 2.1)
======================================================================

Test 1/6: Grundlegendes Speichern... ✓
Test 2/6: Automatische Versionierung... ✓
Test 3/6: Alle Berechnungen abrufen... ✓
Test 4/6: Hauptangebot setzen... ✓
Test 5/6: Berechnungen vergleichen... ✓
Test 6/6: Vollständiger Workflow... ✓

======================================================================
  Ergebnis: 6/6 Tests bestanden
  ✅ ALLE TESTS ERFOLGREICH!
======================================================================
```

## Nächste Schritte

Die Tests für Task 2.1 sind vollständig implementiert und bestehen alle. Die Berechnungsverknüpfung ist damit vollständig getestet und einsatzbereit.
