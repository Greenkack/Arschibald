# Task 5: Produktdatenblätter in PDF einbinden - Visual Guide

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    generate_offer_pdf()                          │
│                                                                   │
│  1. Haupt-PDF generieren (8 Seiten)                             │
│  2. _append_datasheets_and_documents() aufrufen                 │
│  3. Finale PDF zurückgeben                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          _append_datasheets_and_documents()                      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Phase 1: Produktdatenblätter sammeln                      │  │
│  │  - PV-Module                                              │  │
│  │  - Wechselrichter                                         │  │
│  │  - Speicher                                               │  │
│  │  - Zubehör (wenn include_additional_components=True)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                         │
│                         ▼                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Phase 2: Firmendokumente sammeln                          │  │
│  │  - Nur wenn company_document_ids_to_include vorhanden     │  │
│  │  - Nur ausgewählte IDs                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         │                                         │
│                         ▼                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Phase 3: PDFs zusammenführen                              │  │
│  │  1. Haupt-PDF einlesen                                    │  │
│  │  2. Produktdatenblätter anhängen (in Reihenfolge)        │  │
│  │  3. Firmendokumente anhängen                              │  │
│  │  4. Finale PDF als Bytes zurückgeben                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Datenfluss

```
┌──────────────────┐
│  Projekt-Daten   │
│  - pv_details    │
│  - company_id    │
│  - document_ids  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  Produktdatenblätter laden                                │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PV-Module    │  │ Wechselrichter│  │ Speicher     │   │
│  │ ID: 123      │  │ ID: 456       │  │ ID: 789      │   │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘   │
│         │                 │                   │            │
│         ▼                 ▼                   ▼            │
│  get_product_by_id(123)  get_product_by_id(456) ...      │
│         │                 │                   │            │
│         ▼                 ▼                   ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Produkt-Info │  │ Produkt-Info │  │ Produkt-Info │   │
│  │ datasheet:   │  │ datasheet:   │  │ datasheet:   │   │
│  │ "module.pdf" │  │ "wr.pdf"     │  │ "bat.pdf"    │   │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘   │
│         │                 │                   │            │
│         ▼                 ▼                   ▼            │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Pfade kombinieren mit Basis-Pfad                 │    │
│  │ PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN + "module.pdf"│   │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Existenz prüfen: os.path.exists(full_path)       │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ paths_to_append = [                              │    │
│  │   "/data/product_datasheets/module.pdf",         │    │
│  │   "/data/product_datasheets/wr.pdf",             │    │
│  │   "/data/product_datasheets/bat.pdf"             │    │
│  │ ]                                                 │    │
│  └──────────────────────┬───────────────────────────┘    │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│  Firmendokumente laden (optional)                         │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │ db_list_company_documents(company_id)            │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Filtern nach company_document_ids_to_include     │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ paths_to_append += [                             │    │
│  │   "/data/company_docs/vollmacht.pdf",            │    │
│  │   "/data/company_docs/agb.pdf"                   │    │
│  │ ]                                                 │    │
│  └──────────────────────┬───────────────────────────┘    │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│  PDF zusammenführen                                       │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │ pdf_writer = PdfWriter()                         │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Haupt-PDF einlesen (8 Seiten)                    │    │
│  │ main_reader = PdfReader(BytesIO(main_pdf_bytes)) │    │
│  │ for page in main_reader.pages:                   │    │
│  │     pdf_writer.add_page(page)                    │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Datenblätter anhängen (in Reihenfolge)           │    │
│  │ for pdf_path in paths_to_append:                 │    │
│  │     reader = PdfReader(pdf_path)                 │    │
│  │     for page in reader.pages:                    │    │
│  │         pdf_writer.add_page(page)                │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │                                 │
│                         ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Finale PDF schreiben                             │    │
│  │ buffer = BytesIO()                               │    │
│  │ pdf_writer.write(buffer)                         │    │
│  │ return buffer.getvalue()                         │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## Komponenten-Hierarchie

```
Produktdatenblätter
├── Hauptkomponenten (immer)
│   ├── PV-Module (selected_module_id)
│   ├── Wechselrichter (selected_inverter_id)
│   └── Speicher (selected_storage_id) [wenn include_storage=True]
│
└── Zubehör (nur wenn include_additional_components=True)
    ├── Wallbox (selected_wallbox_id)
    ├── EMS (selected_ems_id)
    ├── Optimizer (selected_optimizer_id)
    ├── Carport (selected_carport_id)
    ├── Notstrom (selected_notstrom_id)
    └── Tierabwehr (selected_tierabwehr_id)

Firmendokumente (nur wenn company_document_ids_to_include vorhanden)
├── Dokument 1 (ID in Liste)
├── Dokument 2 (ID in Liste)
└── Dokument 3 (ID in Liste)
```

## Fehlerbehandlung-Fluss

```
┌─────────────────────────────────────────────────────────┐
│  Datenblatt laden                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Produkt in DB?        │
         └───────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
       Ja                Nein
        │                 │
        ▼                 ▼
┌───────────────┐  ┌──────────────────┐
│ Datenblatt-   │  │ Fehler loggen:   │
│ Pfad in DB?   │  │ "Produkt nicht   │
└───────┬───────┘  │  gefunden"       │
        │          └──────────────────┘
        │                 │
   ┌────┴────┐           │
   │         │           │
  Ja        Nein         │
   │         │           │
   ▼         ▼           │
┌──────┐ ┌──────────┐   │
│ Pfad │ │ Fehler   │   │
│ exist│ │ loggen:  │   │
│ iert?│ │ "Kein    │   │
└──┬───┘ │  Pfad"   │   │
   │     └──────────┘   │
   │         │           │
┌──┴──┐     │           │
│     │     │           │
Ja   Nein   │           │
│     │     │           │
▼     ▼     ▼           ▼
┌─────────────────────────┐
│ Anhängen oder           │
│ Fehler loggen           │
│ (Verarbeitung läuft     │
│  weiter)                │
└─────────────────────────┘
```

## Reihenfolge der Anhänge

```
Finale PDF-Struktur:

┌─────────────────────────────────────┐
│ Seite 1-8: Haupt-PDF                │  ← Immer vorhanden
│  - Deckblatt                         │
│  - Anschreiben                       │
│  - Angebotspositionen                │
│  - Produktdetails                    │
│  - Wirtschaftlichkeit                │
│  - Diagramme                         │
│  - Zusammenfassung                   │
│  - Kontakt                           │
├─────────────────────────────────────┤
│ Produktdatenblätter (in Reihenfolge)│  ← Wenn vorhanden
│  1. PV-Module                        │
│  2. Wechselrichter                   │
│  3. Speicher                         │
│  4. Wallbox                          │
│  5. EMS                              │
│  6. Optimizer                        │
│  7. Carport                          │
│  8. Notstrom                         │
│  9. Tierabwehr                       │
├─────────────────────────────────────┤
│ Firmendokumente                      │  ← Wenn ausgewählt
│  1. Vollmacht                        │
│  2. AGBs                             │
│  3. Zertifikate                      │
│  4. ...                              │
└─────────────────────────────────────┘
```

## Debug-Informationen

Die Funktion sammelt detaillierte Debug-Informationen:

```python
debug_info = {
    'product_datasheets_found': [
        {'id': 123, 'model': 'Trina Solar 400W', 'path': '/data/.../module.pdf'},
        {'id': 456, 'model': 'Fronius Symo', 'path': '/data/.../wr.pdf'}
    ],
    'product_datasheets_missing': [
        {'id': 789, 'model': 'BYD Battery', 'reason': 'Datei nicht gefunden'}
    ],
    'company_docs_found': [
        {'id': 1, 'name': 'Vollmacht', 'path': '/data/.../vollmacht.pdf'}
    ],
    'company_docs_missing': [
        {'id': 2, 'name': 'AGBs', 'reason': 'Kein relativer Pfad in DB'}
    ],
    'total_paths_to_append': 3
}
```

Diese Informationen werden im Log ausgegeben:

```
================================================================================
DEBUG: _append_datasheets_and_documents
================================================================================
Produktdatenblätter gefunden: 2
  - ID 123: Trina Solar 400W -> /data/.../module.pdf
  - ID 456: Fronius Symo -> /data/.../wr.pdf
Produktdatenblätter fehlend: 1
  - ID 789: BYD Battery -> Datei nicht gefunden
Firmendokumente gefunden: 1
  - ID 1: Vollmacht -> /data/.../vollmacht.pdf
Firmendokumente fehlend: 1
  - ID 2: AGBs -> Kein relativer Pfad in DB
Gesamt anzuhängen: 3
================================================================================
```

## Beispiel-Aufruf

```python
# In generate_offer_pdf()
if include_all_documents_opt and _PYPDF_AVAILABLE:
    logging.info("Anhängen von Produktdatenblättern und Firmendokumenten...")
    main_pdf_bytes = _append_datasheets_and_documents(
        main_pdf_bytes=main_pdf_bytes,                    # Haupt-PDF (8 Seiten)
        pv_details=pv_details_pdf,                        # Alle Produkt-IDs
        get_product_by_id_func=get_product_by_id_func,    # DB-Funktion
        db_list_company_documents_func=db_list_company_documents_func,  # DB-Funktion
        active_company_id=active_company_id,              # Firma-ID
        company_document_ids_to_include=company_document_ids_to_include_opt,  # Dokument-IDs
        include_additional_components=pv_details_pdf.get('include_additional_components', True)  # Zubehör?
    )
```

## Verschlüsselte PDFs

```
┌─────────────────────────────────────┐
│ PDF einlesen                         │
└────────────┬────────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Verschlüsselt?│
     └───────┬───────┘
             │
      ┌──────┴──────┐
      │             │
     Ja            Nein
      │             │
      ▼             ▼
┌─────────────┐ ┌──────────┐
│ Entschlüs-  │ │ Direkt   │
│ seln mit    │ │ anhängen │
│ leerem PW   │ └──────────┘
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
Erfolg  Fehler
   │       │
   ▼       ▼
┌──────┐ ┌──────────┐
│Anhän-│ │Übersprin-│
│gen   │ │gen +     │
└──────┘ │Fehler log│
         └──────────┘
```

## Performance-Überlegungen

```
Optimierungen:
├── Duplikate entfernen (set())
├── Nur existierende Pfade anhängen
├── Fehler nicht propagieren (try-except)
├── BytesIO für Speicher-Effizienz
└── Logging nur bei Bedarf

Potenzielle Bottlenecks:
├── Große Datenblätter (mehrere MB)
├── Viele Komponenten (>10)
├── Verschlüsselte PDFs
└── Netzwerk-Zugriff (falls Pfade remote)
```

## Zusammenfassung

Die Implementierung folgt einem klaren, dreiphasigen Ansatz:

1. **Sammeln** - Alle Pfade zu Datenblättern und Dokumenten sammeln
2. **Validieren** - Existenz prüfen, Fehler loggen
3. **Zusammenführen** - Alle PDFs in der richtigen Reihenfolge anhängen

Dabei wird besonderer Wert auf:

- **Robustheit** - Fehler werden behandelt, nicht propagiert
- **Transparenz** - Detailliertes Logging für Debugging
- **Flexibilität** - Konfigurierbar über Parameter
- **Performance** - Effiziente Pfad-Operationen und Speicher-Management

gelegt.
