# CRM Integration Module

## Data Input Bridge

Das Data Input Bridge Modul ermöglicht die automatische Übernahme von Kunden- und Projektdaten aus der Bedarfsanalyse ins CRM-System.

### Funktionen

#### `extract_customer_data_from_session()`
Extrahiert alle Kundendaten aus `st.session_state`.

**Unterstützte Session-State-Keys:**
- `customer_first_name`, `first_name` → Vorname
- `customer_last_name`, `last_name` → Nachname
- `customer_email`, `email` → E-Mail
- `customer_phone`, `phone_landline` → Telefon (Festnetz)
- `customer_mobile`, `phone_mobile` → Telefon (Mobil)
- `customer_city`, `city` → Stadt
- `customer_zip`, `zip_code` → PLZ
- `customer_street`, `address` → Straße
- `income_tax_rate`, `income_tax_rate_percent` → Steuersatz

**Rückgabe:** Dictionary mit Kundendaten

#### `extract_project_data_from_session()`
Extrahiert alle Projektdaten aus `st.session_state`.

**Unterstützte Session-State-Keys:**
- `project_name` → Projektname
- `roof_type`, `dachform` → Dachtyp
- `module_quantity`, `anzahl_module` → Modulanzahl
- `annual_consumption`, `jahresverbrauch` → Jahresverbrauch
- `roof_area`, `freie_dachflaeche` → Dachfläche
- Und viele weitere...

**Rückgabe:** Dictionary mit Projektdaten

#### `check_duplicate_customer(conn, email)`
Prüft ob ein Kunde mit der E-Mail bereits existiert.

**Parameter:**
- `conn`: Datenbankverbindung
- `email`: E-Mail-Adresse

**Rückgabe:** Kundendaten (dict) wenn gefunden, sonst None

#### `validate_customer_data(customer_data)`
Validiert Kundendaten vor dem Speichern.

**Prüfungen:**
- Vorname und Nachname sind Pflichtfelder
- E-Mail-Format (muss @ enthalten)
- PLZ-Format (5 Ziffern)

**Rückgabe:** Tuple (is_valid, error_messages)

#### `validate_project_data(project_data)`
Validiert Projektdaten vor dem Speichern.

**Prüfungen:**
- Projektname ist Pflichtfeld
- Dachfläche, Verbrauch, Modulanzahl nicht negativ
- Dachneigung zwischen 0° und 90°

**Rückgabe:** Tuple (is_valid, error_messages)

### Verwendung

```python
import streamlit as st
from crm.integration import (
    extract_customer_data_from_session,
    extract_project_data_from_session,
    check_duplicate_customer,
    validate_customer_data,
)
from database import get_db_connection
from crm import save_customer, save_project

# 1. Daten aus Session State extrahieren
customer_data = extract_customer_data_from_session()
project_data = extract_project_data_from_session()

# 2. Validieren
is_valid, errors = validate_customer_data(customer_data)
if not is_valid:
    for error in errors:
        st.error(error)
    st.stop()

# 3. Duplikat prüfen
conn = get_db_connection()
existing = check_duplicate_customer(conn, customer_data['email'])

if existing:
    st.warning(f"Kunde existiert bereits: {existing['first_name']} {existing['last_name']}")
    action = st.radio("Was möchten Sie tun?", 
                      ["Aktualisieren", "Neu anlegen", "Abbrechen"])
    
    if action == "Aktualisieren":
        customer_data['id'] = existing['id']
    elif action == "Abbrechen":
        st.stop()

# 4. Speichern
customer_id = save_customer(conn, customer_data)
if customer_id:
    st.success(f"Kunde gespeichert! ID: {customer_id}")
    
    # Projekt mit Kunde verknüpfen
    project_data['customer_id'] = customer_id
    project_id = save_project(conn, project_data)
    
    if project_id:
        st.success(f"Projekt gespeichert! ID: {project_id}")
```

### Tests

Führe Tests aus mit:
```bash
python crm/integration/test_data_input_bridge.py
```

Oder mit pytest:
```bash
pytest crm/integration/test_data_input_bridge.py -v
```

### Nächste Schritte

Dieses Modul wird in Task 2.2 in die GUI integriert:
- Erweiterung des "Kunde in CRM speichern" Buttons in `gui.py`
- Vorschau-Dialog für zu übernehmende Daten
- Duplikat-Warnung mit Aktionsauswahl
- Erfolgsbestätigung mit Link zum Kundenprofil


---

## PDF Bridge

Das PDF Bridge Modul ermöglicht die automatische Archivierung von generierten PDFs in der Kundenakte mit Metadaten-Extraktion und Versionierung.

### Funktionen

#### `auto_save_pdf_to_customer_documents()`
Speichert ein PDF automatisch in der Kundenakte mit Metadaten und Versionierung.

**Parameter:**
- `pdf_path`: Pfad zur PDF-Datei
- `customer_id`: Kunden-ID
- `project_id`: Optional - Projekt-ID
- `offer_data`: Optional - Angebotsdaten für Metadaten
- `display_name`: Optional - Anzeigename (wird automatisch generiert wenn nicht angegeben)

**Rückgabe:** Dokument-ID bei Erfolg, None bei Fehler

#### `extract_pdf_metadata()`
Extrahiert Metadaten aus PDF-Datei und Angebotsdaten.

**Parameter:**
- `pdf_path`: Pfad zur PDF-Datei
- `offer_data`: Optional - Angebotsdaten für zusätzliche Metadaten

**Rückgabe:** Dictionary mit Metadaten (doc_type, version, date, file_size, etc.)

#### `get_next_version_number()`
Ermittelt die nächste Versionsnummer für einen Dokumenttyp.

**Parameter:**
- `customer_id`: Kunden-ID
- `doc_type`: Dokumenttyp (z.B. 'offer_pdf')
- `project_id`: Optional - Projekt-ID für projektspezifische Versionierung

**Rückgabe:** Nächste Versionsnummer (1, 2, 3, ...)

#### `create_versioned_filename()`
Erstellt einen versionierten Dateinamen.

**Parameter:**
- `original_filename`: Original-Dateiname
- `version`: Versionsnummer
- `metadata`: Metadaten für zusätzliche Informationen

**Rückgabe:** Versionierter Dateiname (z.B. "angebot_v1_2025-01-13.pdf")

#### `get_pdf_type_badge_color()`
Gibt die Badge-Farbe für einen PDF-Typ zurück.

**Parameter:**
- `doc_type`: Dokumenttyp

**Rückgabe:** Farbe als Hex-Code

**Unterstützte Typen:**
- `offer_pdf` → Blau (#2563EB)
- `invoice_pdf` → Grün (#22C55E)
- `contract_pdf` → Orange (#F59E0B)
- `report_pdf` → Violett (#8B5CF6)
- `other_pdf` → Grau (#64748B)

#### `get_pdf_type_label()`
Gibt das deutsche Label für einen PDF-Typ zurück.

**Parameter:**
- `doc_type`: Dokumenttyp

**Rückgabe:** Deutsches Label (z.B. "Angebot", "Rechnung", etc.)

#### `format_document_list_for_display()`
Formatiert eine Dokumentenliste für die Anzeige mit zusätzlichen Informationen.

**Parameter:**
- `docs`: Liste von Dokumenten aus der Datenbank

**Rückgabe:** Formatierte Dokumentenliste mit zusätzlichen Display-Feldern:
- `type_label`: Deutsches Label für Dokumenttyp
- `badge_color`: Farbe für Badge
- `version`: Extrahierte Versionsnummer
- `formatted_date`: Formatiertes Datum (DD.MM.YYYY HH:MM)

### Verwendung

#### Automatische Archivierung (in pdf_generator.py)
```python
from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents

# Nach PDF-Generierung
doc_id = auto_save_pdf_to_customer_documents(
    pdf_path="path/to/generated.pdf",
    customer_id=123,
    project_id=456,  # Optional
    offer_data=offer_data,  # Optional, für Metadaten
    display_name="Benutzerdefinierter Name"  # Optional
)

if doc_id:
    print(f"PDF erfolgreich archiviert! Dokument-ID: {doc_id}")
```

#### Manuelle Metadaten-Extraktion
```python
from crm.integration.pdf_bridge import extract_pdf_metadata

metadata = extract_pdf_metadata(
    pdf_path="path/to/file.pdf",
    offer_data=offer_data  # Optional
)

print(f"Typ: {metadata['doc_type']}")
print(f"Version: {metadata['version']}")
print(f"Größe: {metadata['file_size']} bytes")
```

#### Versionsverwaltung
```python
from crm.integration.pdf_bridge import get_next_version_number

version = get_next_version_number(
    customer_id=123,
    doc_type='offer_pdf',
    project_id=456  # Optional
)

print(f"Nächste Version: v{version}")
```

#### UI-Helfer
```python
from crm.integration.pdf_bridge import (
    get_pdf_type_badge_color,
    get_pdf_type_label,
    format_document_list_for_display
)

# Badge-Farbe für Dokumenttyp
color = get_pdf_type_badge_color('offer_pdf')  # '#2563EB'

# Deutsches Label für Dokumenttyp
label = get_pdf_type_label('offer_pdf')  # 'Angebot'

# Dokumentenliste formatieren
formatted_docs = format_document_list_for_display(docs)
for doc in formatted_docs:
    print(f"{doc['type_label']} v{doc['version']}: {doc['display_name']}")
```

### Integration

#### 1. PDF Generator Integration
Das PDF Bridge wird automatisch nach erfolgreicher PDF-Erstellung in `pdf_generator.py` aufgerufen:
- Prüft auf Kundenzuordnung im Session State
- Archiviert PDF automatisch wenn Kunde gefunden
- Loggt Erfolg/Fehler-Meldungen

#### 2. CRM UI Integration
Erweiterte Kundenakte-Anzeige in `crm.py`:
- Farbcodierte Badges für PDF-Typen
- Versionsnummern in Dateinamen
- Chronologische Sortierung (neueste zuerst)
- Dateigrößen-Anzeige
- Verbesserte Download/Löschen-Buttons

#### 3. Session State Integration
Automatische Kunden-/Projekt-Erkennung aus Streamlit Session State:
- `current_customer_id` oder `selected_customer_id`
- `current_project_id` oder `selected_project_id`
- `current_customer` Dictionary mit 'id' Feld

### Tests

Führe Tests aus mit:
```bash
python crm/integration/test_pdf_bridge.py
```

**Test-Abdeckung:**
- Metadaten-Extraktion
- Versionsnummerierung
- Dateinamen-Generierung
- PDF-Typ-Helfer
- Dokumentenlisten-Formatierung
- Kompletter Integrations-Workflow

### Features

#### 1. Automatische PDF-Archivierung
- PDFs werden automatisch nach Generierung in Kundenakte gespeichert
- Kein manueller Upload erforderlich
- Nahtlose Integration mit pdf_generator.py

#### 2. Metadaten-Extraktion
- Automatische Erkennung des PDF-Typs (Angebot, Rechnung, Vertrag, Bericht)
- Dateigröße-Tracking
- Datum und Zeitstempel
- Extraktion von Angebotsdaten (Angebots-ID, Kundenname, Projekttyp)

#### 3. Automatische Versionierung
- Intelligente Versionsnummerierung (v1, v2, v3, ...)
- Versionsnummern werden automatisch für gleichen Dokumenttyp erhöht
- Versionierte Dateinamen enthalten Datumsstempel

#### 4. Erweiterte UI-Anzeige
- Farbcodierte Badges für verschiedene PDF-Typen
- Versionsnummern in Dokumentenliste
- Chronologische Sortierung (neueste zuerst)
- Dateigrößen-Anzeige
- Formatierte Datumsangaben

#### 5. PDF-Typ-Klassifizierung
Unterstützte PDF-Typen mit Farbcodierung:
- **Angebot** (Offer) - Blau (#2563EB)
- **Rechnung** (Invoice) - Grün (#22C55E)
- **Vertrag** (Contract) - Orange (#F59E0B)
- **Bericht** (Report) - Violett (#8B5CF6)
- **Sonstiges** (Other) - Grau (#64748B)

### Fehlerbehandlung

Das PDF Bridge enthält umfassende Fehlerbehandlung:
- Graceful Fallback wenn Kunde nicht zugeordnet
- Datenbankverbindungs-Fehlerbehandlung
- Dateisystem-Fehlerbehandlung
- Detailliertes Logging für Debugging

Alle Fehler werden geloggt, unterbrechen aber nicht den PDF-Generierungsprozess.

### Anforderungen

- Python 3.10+
- Streamlit (für UI-Integration)
- database.py (für Kundendokument-Speicherung)
- pdf_generator.py (für automatische Archivierung)
