# Task 6: Firmendokumente in PDF einbinden - Visual Guide

## Übersicht

Diese visuelle Anleitung zeigt, wie Firmendokumente in die PDF-Generierung integriert werden.

---

## Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                    generate_offer_pdf()                          │
│                                                                   │
│  1. Haupt-PDF generieren (8 Seiten)                             │
│  2. _append_datasheets_and_documents() aufrufen                 │
│                                                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         _append_datasheets_and_documents()                       │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: Produktdatenblätter laden                        │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │ • PV-Module                                               │  │
│  │ • Wechselrichter                                          │  │
│  │ • Speicher                                                │  │
│  │ • Zubehör (Wallbox, EMS, Optimizer, etc.)               │  │
│  │                                                           │  │
│  │ → paths_to_append = [datasheet1.pdf, datasheet2.pdf, ...]│  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PHASE 2: Firmendokumente laden                            │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │ IF active_company_id AND company_document_ids_to_include │  │
│  │ THEN:                                                     │  │
│  │   1. db_list_company_documents_func() aufrufen           │  │
│  │   2. Nach IDs filtern                                    │  │
│  │   3. Pfade konstruieren                                  │  │
│  │   4. Existenz prüfen                                     │  │
│  │                                                           │  │
│  │ → paths_to_append += [company_doc1.pdf, company_doc2.pdf]│  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PHASE 3: PDFs zusammenführen                              │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │ 1. Haupt-PDF einlesen                                    │  │
│  │ 2. Für jedes Dokument in paths_to_append:               │  │
│  │    • PDF einlesen                                        │  │
│  │    • Verschlüsselung prüfen                             │  │
│  │    • Alle Seiten anhängen                               │  │
│  │ 3. Finale PDF als Bytes zurückgeben                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Datenfluss

```
┌──────────────────┐
│  project_data    │
│  ├─ pv_details   │──────┐
│  └─ company_id   │      │
└──────────────────┘      │
                          │
┌──────────────────┐      │
│ inclusion_options│      │
│  └─ company_doc_ │      │
│     ids_to_      │──────┤
│     include      │      │
└──────────────────┘      │
                          ▼
                  ┌───────────────────┐
                  │ _append_datasheets│
                  │ _and_documents()  │
                  └───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  Produktdatenblätter laden      │
        │  ─────────────────────────────  │
        │  get_product_by_id_func()       │
        │  ↓                              │
        │  [module.pdf, inverter.pdf, ...]│
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  Firmendokumente laden          │
        │  ─────────────────────────────  │
        │  db_list_company_documents_func()│
        │  ↓                              │
        │  Filter nach IDs                │
        │  ↓                              │
        │  [agb.pdf, vollmacht.pdf, ...]  │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  PDF zusammenführen             │
        │  ─────────────────────────────  │
        │  PdfWriter + PdfReader          │
        │  ↓                              │
        │  Finale PDF (Bytes)             │
        └─────────────────────────────────┘
```

---

## Subtask 6.1: Firmendokumente laden

### Ablauf

```
START
  │
  ├─ Prüfe: company_document_ids_to_include vorhanden?
  │   ├─ NEIN → ENDE (keine Firmendokumente)
  │   └─ JA → weiter
  │
  ├─ Prüfe: active_company_id vorhanden?
  │   ├─ NEIN → ENDE (keine Firmendokumente)
  │   └─ JA → weiter
  │
  ├─ Prüfe: db_list_company_documents_func callable?
  │   ├─ NEIN → ENDE (keine Firmendokumente)
  │   └─ JA → weiter
  │
  ├─ Rufe db_list_company_documents_func(active_company_id, None) auf
  │   ↓
  │   Ergebnis: [
  │     {id: 1, display_name: 'AGB', relative_db_path: '1/agb.pdf'},
  │     {id: 2, display_name: 'Vollmacht', relative_db_path: '1/vollmacht.pdf'},
  │     {id: 3, display_name: 'Zertifikat', relative_db_path: '1/zertifikat.pdf'}
  │   ]
  │
  ├─ Für jedes Dokument:
  │   ├─ Prüfe: doc['id'] in company_document_ids_to_include?
  │   │   ├─ NEIN → Überspringen
  │   │   └─ JA → Weiter zu Subtask 6.2
  │   │
  │   └─ Prüfe: relative_db_path vorhanden?
  │       ├─ NEIN → Logge Warnung, überspringen
  │       └─ JA → Weiter zu Subtask 6.2
  │
ENDE
```

### Beispiel

```python
# Eingabe
active_company_id = 1
company_document_ids_to_include = [1, 3]  # Nur AGB und Zertifikat

# Datenbank-Abfrage
all_docs = db_list_company_documents_func(1, None)
# Ergebnis: [
#   {id: 1, display_name: 'AGB', relative_db_path: '1/agb.pdf'},
#   {id: 2, display_name: 'Vollmacht', relative_db_path: '1/vollmacht.pdf'},
#   {id: 3, display_name: 'Zertifikat', relative_db_path: '1/zertifikat.pdf'}
# ]

# Filterung
filtered_docs = [doc for doc in all_docs if doc['id'] in [1, 3]]
# Ergebnis: [
#   {id: 1, display_name: 'AGB', relative_db_path: '1/agb.pdf'},
#   {id: 3, display_name: 'Zertifikat', relative_db_path: '1/zertifikat.pdf'}
# ]
```

---

## Subtask 6.2: Firmendokumente anhängen

### Ablauf

```
Für jedes gefilterte Dokument:
  │
  ├─ Extrahiere relative_db_path
  │   Beispiel: '1/agb.pdf'
  │
  ├─ Konstruiere vollständigen Pfad
  │   full_path = COMPANY_DOCS_BASE_DIR_PDF_GEN + relative_db_path
  │   Beispiel: 'C:/Users/.../data/company_docs/1/agb.pdf'
  │
  ├─ Prüfe: Datei existiert?
  │   ├─ NEIN → Logge Warnung, überspringen
  │   └─ JA → Zu paths_to_append hinzufügen
  │
  └─ Wiederhole für nächstes Dokument

Später beim Zusammenführen:
  │
  Für jeden Pfad in paths_to_append:
    │
    ├─ Öffne PDF mit PdfReader
    │
    ├─ Prüfe: PDF verschlüsselt?
    │   ├─ JA → Versuche zu entschlüsseln
    │   │   ├─ Erfolg → Weiter
    │   │   └─ Fehler → Logge Warnung, überspringen
    │   └─ NEIN → Weiter
    │
    ├─ Für jede Seite in PDF:
    │   └─ Füge Seite zu PdfWriter hinzu
    │
    └─ Wiederhole für nächsten Pfad
```

### Pfad-Konstruktion

```
COMPANY_DOCS_BASE_DIR_PDF_GEN
    = C:/Users/win10/Desktop/Bokuk2/data/company_docs

relative_db_path (aus Datenbank)
    = 1/agb.pdf

full_path = os.path.join(
    COMPANY_DOCS_BASE_DIR_PDF_GEN,
    relative_db_path
)
    = C:/Users/win10/Desktop/Bokuk2/data/company_docs/1/agb.pdf
```

### Verschlüsselung behandeln

```python
datasheet_reader = PdfReader(pdf_path)

if datasheet_reader.is_encrypted:
    try:
        # Versuche mit leerem Passwort
        datasheet_reader.decrypt('')
        logging.info(f"Verschlüsseltes Dokument entschlüsselt: {pdf_path}")
    except Exception as e:
        # Überspringen wenn Entschlüsselung fehlschlägt
        logging.warning(f"Konnte nicht entschlüsseln: {pdf_path}")
        continue  # Nächstes Dokument

# Alle Seiten anhängen
for page in datasheet_reader.pages:
    pdf_writer.add_page(page)
```

---

## Subtask 6.3: Reihenfolge und Integration

### Reihenfolge der Dokumente

```
paths_to_append = []

# PHASE 1: Produktdatenblätter (Zeilen 5100-5194)
paths_to_append.append('data/product_datasheets/modules/module1.pdf')
paths_to_append.append('data/product_datasheets/inverters/inverter1.pdf')
paths_to_append.append('data/product_datasheets/storage/battery1.pdf')

# PHASE 2: Firmendokumente (Zeilen 5195+)
paths_to_append.append('data/company_docs/1/agb.pdf')
paths_to_append.append('data/company_docs/1/zertifikat.pdf')

# Finale Reihenfolge:
# 1. Haupt-PDF (8 Seiten)
# 2. Modul-Datenblatt
# 3. Wechselrichter-Datenblatt
# 4. Speicher-Datenblatt
# 5. AGB
# 6. Zertifikat
```

### PDF-Zusammenführung

```
┌─────────────────┐
│   Haupt-PDF     │  8 Seiten
│   (Seiten 1-8)  │
└────────┬────────┘
         │
         ├─ Anhängen
         │
┌────────▼────────┐
│ Modul-Datenblatt│  2 Seiten
│ (Seiten 9-10)   │
└────────┬────────┘
         │
         ├─ Anhängen
         │
┌────────▼────────┐
│ Wechselrichter  │  3 Seiten
│ (Seiten 11-13)  │
└────────┬────────┘
         │
         ├─ Anhängen
         │
┌────────▼────────┐
│ Speicher        │  2 Seiten
│ (Seiten 14-15)  │
└────────┬────────┘
         │
         ├─ Anhängen
         │
┌────────▼────────┐
│ AGB             │  4 Seiten
│ (Seiten 16-19)  │
└────────┬────────┘
         │
         ├─ Anhängen
         │
┌────────▼────────┐
│ Zertifikat      │  1 Seite
│ (Seite 20)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Finale PDF     │  20 Seiten
│  (Bytes)        │
└─────────────────┘
```

---

## Fehlerbehandlung

### Fehler-Szenarien und Behandlung

| Szenario | Behandlung | Ergebnis |
|----------|-----------|----------|
| Keine active_company_id | Überspringen | Keine Firmendokumente |
| Leere company_document_ids_to_include | Überspringen | Keine Firmendokumente |
| Dokument nicht in DB | Logge Warnung | Fortfahren mit nächstem |
| Datei nicht gefunden | Logge Warnung | Fortfahren mit nächstem |
| Kein relativer Pfad | Logge Info | Fortfahren mit nächstem |
| PDF verschlüsselt | Versuche zu entschlüsseln | Bei Fehler: überspringen |
| Fehler beim Anhängen | Logge Error | Fortfahren mit nächstem |
| Fehler beim Schreiben | Logge Error | Haupt-PDF zurückgeben |

### Fehlerbehandlung-Fluss

```
TRY:
    Firmendokumente laden
    │
    ├─ Erfolg → Weiter
    └─ Fehler → Logge Error, fahre fort
    
    Für jedes Dokument:
        TRY:
            Pfad konstruieren
            Datei prüfen
            Zu Liste hinzufügen
            │
            ├─ Erfolg → Weiter
            └─ Fehler → Logge Warnung, nächstes Dokument
    
    PDFs zusammenführen:
        TRY:
            Haupt-PDF einlesen
            │
            ├─ Erfolg → Weiter
            └─ Fehler → Logge Error, Haupt-PDF zurückgeben
            
            Für jedes Dokument:
                TRY:
                    PDF einlesen
                    Verschlüsselung prüfen
                    Seiten anhängen
                    │
                    ├─ Erfolg → Weiter
                    └─ Fehler → Logge Error, nächstes Dokument
            
            Finale PDF schreiben
            │
            ├─ Erfolg → PDF zurückgeben
            └─ Fehler → Logge Error, Haupt-PDF zurückgeben

CATCH:
    Logge Error
    Gebe Haupt-PDF zurück (Graceful Degradation)
```

---

## Debug-Ausgabe

### Beispiel-Ausgabe

```
================================================================================
DEBUG: _append_datasheets_and_documents
================================================================================
Produktdatenblätter gefunden: 3
  - ID 1: Test Module -> C:/Users/.../data/product_datasheets/modules/test.pdf
  - ID 2: Test Inverter -> C:/Users/.../data/product_datasheets/inverters/test.pdf
  - ID 3: Test Battery -> C:/Users/.../data/product_datasheets/storage/test.pdf
Produktdatenblätter fehlend: 0
Firmendokumente gefunden: 2
  - ID 1: AGB -> C:/Users/.../data/company_docs/1/agb.pdf
  - ID 3: Zertifikat -> C:/Users/.../data/company_docs/1/zertifikat.pdf
Firmendokumente fehlend: 1
  - ID 2: Vollmacht -> Datei nicht gefunden
Gesamt anzuhängen: 5
================================================================================

Haupt-PDF eingelesen: 8 Seiten
Dokument angehängt: .../modules/test.pdf (2 Seiten)
Dokument angehängt: .../inverters/test.pdf (3 Seiten)
Dokument angehängt: .../storage/test.pdf (2 Seiten)
Dokument angehängt: .../company_docs/1/agb.pdf (4 Seiten)
Dokument angehängt: .../company_docs/1/zertifikat.pdf (1 Seite)
Erfolgreich angehängt: 5 von 5 Dokumenten
Finale PDF erstellt mit 20 Seiten
```

---

## Verwendung

### Beispiel-Aufruf

```python
# In generate_offer_pdf()
final_pdf_bytes = _append_datasheets_and_documents(
    main_pdf_bytes=main_pdf_bytes,  # 8-seitige Haupt-PDF
    pv_details={
        'selected_module_id': 1,
        'selected_inverter_id': 2,
        'selected_storage_id': 3,
        'include_storage': True
    },
    get_product_by_id_func=get_product_by_id,
    db_list_company_documents_func=list_company_documents,
    active_company_id=1,
    company_document_ids_to_include=[1, 3],  # AGB und Zertifikat
    include_additional_components=True
)

# Ergebnis: PDF mit 20 Seiten
# - Seiten 1-8: Haupt-PDF
# - Seiten 9-10: Modul-Datenblatt
# - Seiten 11-13: Wechselrichter-Datenblatt
# - Seiten 14-15: Speicher-Datenblatt
# - Seiten 16-19: AGB
# - Seite 20: Zertifikat
```

---

## Zusammenfassung

✅ **Subtask 6.1**: Firmendokumente werden aus der Datenbank geladen und nach IDs gefiltert  
✅ **Subtask 6.2**: Dokumente werden mit korrekten Pfaden angehängt, Fehler werden behandelt  
✅ **Subtask 6.3**: Produktdatenblätter kommen zuerst, dann Firmendokumente, finale PDF als Bytes

Die Implementierung ist **robust**, **getestet** und **produktionsreif**.
