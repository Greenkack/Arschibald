# CRM PDF Bridge - Test Reference

## Task 3.1: Tests für PDF-Archivierung

**Status:** ✅ ABGESCHLOSSEN

### Übersicht

Umfassende Test-Suite für die automatische PDF-Archivierung in der Kundenakte mit Metadaten-Extraktion und Versionierung.

### Test-Kategorien

#### 1. Metadaten-Extraktion Tests

**test_extract_pdf_metadata()**
- Testet Extraktion von Metadaten aus PDF-Dateien
- Prüft Angebotsdaten-Integration
- Validiert Dateigröße, Typ, Datum

**test_extract_pdf_metadata_various_types()**
- Testet verschiedene PDF-Typen (Angebot, Rechnung, Vertrag, Bericht)
- Prüft korrekte Typ-Erkennung aus Dateinamen
- Validiert alle 5 Dokumenttypen

**test_extract_pdf_metadata_without_offer_data()**
- Testet Metadaten-Extraktion ohne Angebotsdaten
- Prüft Fallback-Werte
- Validiert Basis-Metadaten

#### 2. Versionierung Tests

**test_get_next_version_number()**
- Testet Versionsnummern-Ermittlung
- Prüft erste Version für neuen Kunden
- Validiert Versionszähler

**test_create_versioned_filename()**
- Testet Erstellung versionierter Dateinamen
- Prüft verschiedene Dateinamen-Formate
- Validiert Datums-Integration

**test_versioning_with_multiple_pdfs()**
- Testet Versionierung mit mehreren PDFs
- Speichert 3 PDFs nacheinander
- Prüft korrekte Versionsnummern (v1, v2, v3)
- Validiert nächste Version (v4)

#### 3. Automatisches Speichern Tests

**test_auto_save_pdf_to_customer_documents()**
- Testet vollständigen Auto-Save-Workflow
- Erstellt Test-Kunde und Test-PDF
- Prüft Speicherung in Datenbank
- Validiert Dokument-ID und Metadaten

**test_auto_save_with_project_id()**
- Testet Speicherung mit Projekt-ID
- Prüft projektspezifische Filterung
- Validiert Projekt-Zuordnung

**test_auto_save_nonexistent_file()**
- Testet Fehlerbehandlung für nicht existierende Dateien
- Prüft None-Rückgabe
- Validiert Fehler-Logging

#### 4. Helper-Funktionen Tests

**test_pdf_type_helpers()**
- Testet Badge-Farben für PDF-Typen
- Testet deutsche Labels
- Validiert alle 5 Dokumenttypen

**test_format_document_list()**
- Testet Dokumentenlisten-Formatierung
- Prüft Versions-Extraktion
- Validiert Datums-Formatierung

#### 5. Integration Tests

**test_integration_workflow()**
- Testet kompletten End-to-End-Workflow
- Durchläuft alle 4 Schritte:
  1. Metadaten extrahieren
  2. Versionsnummer ermitteln
  3. Dateinamen erstellen
  4. PDF speichern
- Validiert vollständige Integration

### Test-Ergebnisse

```
✅ 12 Tests bestanden
❌ 0 Tests fehlgeschlagen

Erfolgsrate: 100%
```

### Getestete Funktionen

1. **Automatisches Speichern**
   - ✅ PDF in Kundenakte speichern
   - ✅ Dokument-ID zurückgeben
   - ✅ Dateisystem-Integration
   - ✅ Datenbank-Integration

2. **Metadaten-Extraktion**
   - ✅ PDF-Typ aus Dateinamen
   - ✅ Dateigröße ermitteln
   - ✅ Angebotsdaten integrieren
   - ✅ Datum formatieren

3. **Versionierung**
   - ✅ Erste Version (v1)
   - ✅ Folgeversionen (v2, v3, ...)
   - ✅ Nächste Version ermitteln
   - ✅ Versionierte Dateinamen

### Test-Ausführung

```bash
# Alle Tests ausführen
python crm/integration/test_pdf_bridge.py

# Einzelne Tests (in Python)
from crm.integration.test_pdf_bridge import test_auto_save_pdf_to_customer_documents
test_auto_save_pdf_to_customer_documents()
```

### Test-Datenbank

Die Tests verwenden:
- **Test-Kunde-ID:** 99999
- **Test-Kunde-Name:** Test Kunde PDF
- **Test-E-Mail:** test.pdf@example.com

Alle Test-Daten werden nach jedem Test automatisch bereinigt.

### Abhängigkeiten

- `database.py` - Datenbankfunktionen
- `crm/integration/pdf_bridge.py` - PDF-Bridge-Modul
- `tempfile` - Temporäre Dateien
- `sqlite3` - Datenbank-Tests

### Anforderungen (Requirements)

Erfüllt Requirements:
- **3.1:** Automatische PDF-Archivierung
- **3.2:** Metadaten-Extraktion
- **3.3:** Versionierung
- **3.4:** Chronologische Sortierung

### Nächste Schritte

Task 3.1 ist abgeschlossen. Die Tests validieren:
- ✅ Automatisches Speichern funktioniert
- ✅ Metadaten werden korrekt extrahiert
- ✅ Versionierung funktioniert einwandfrei

Die PDF-Archivierung ist vollständig getestet und einsatzbereit.

---

**Erstellt:** 2025-11-13  
**Task:** 3.1 - Tests für PDF-Archivierung  
**Status:** ✅ Abgeschlossen
