# Design Document

## Overview

Das erweiterte PDF-Ausgabesystem muss so repariert werden, dass alle Produktdatenblätter (Hauptkomponenten und Zubehör), Firmendokumente, Diagramme und individuelle Seiten korrekt in die PDF eingebunden werden. Die funktionierende Logik aus dem `repair_pdf` Ordner dient als Referenz und wird in die aktuelle Implementierung übertragen.

### Hauptprobleme

1. **Produktdatenblätter fehlen**: Datenblätter für Zubehörkomponenten (Wallbox, EMS, Optimizer, Carport, Notstrom, Tierabwehr) werden nicht eingebunden
2. **Firmendokumente fehlen**: Ausgewählte Firmendokumente werden nicht angehängt
3. **Diagramme fehlen**: Ausgewählte Charts werden nicht in die PDF integriert
4. **Pfadkonstruktion fehlerhaft**: Basis-Verzeichnisse für Datenblätter und Dokumente werden nicht korrekt verwendet

## Architecture

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         pdf_ui.py                            │
│  - Benutzerauswahl (Charts, Dokumente, Optionen)            │
│  - Session State Management (_temp_ Keys)                   │
│  - Übergabe an PDF-Generator                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    pdf_generator.py                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  generate_offer_pdf()                                 │  │
│  │  - Hauptfunktion für PDF-Erstellung                   │  │
│  │  - Verarbeitet inclusion_options                      │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  _append_datasheets_and_documents()                   │  │
│  │  - Sammelt Produkt-IDs (Haupt + Zubehör)             │  │
│  │  - Lädt Datenblatt-Pfade aus DB                       │  │
│  │  - Konstruiert vollständige Pfade                     │  │
│  │  - Hängt PDFs mit PdfWriter an                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Visualizations Section                               │  │
│  │  - Iteriert über selected_charts_for_pdf              │  │
│  │  - Rendert Charts in Story                            │  │
│  │  - Verwendet charts_config_for_pdf_generator          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Datenfluss

```
1. Benutzer wählt Optionen in pdf_ui.py
   ├─ Charts: selected_charts_for_pdf
   ├─ Dokumente: company_document_ids_to_include
   └─ Zubehör: include_additional_components

2. Session State speichert Auswahl
   ├─ _temp_ Keys während Formular-Anzeige
   └─ Echte Keys nach Submit

3. generate_offer_pdf() erhält inclusion_options
   ├─ selected_charts_for_pdf: List[str]
   ├─ company_document_ids_to_include: List[int]
   └─ include_optional_component_details: bool

4. PDF-Generierung
   ├─ Haupt-PDF (6-8 Seiten) mit Charts in "Visualizations"
   └─ Anhänge via _append_datasheets_and_documents()

5. Rückgabe: Vollständige PDF mit allen Anhängen
```

## Components and Interfaces

### 1. Basis-Verzeichnisse (pdf_generator.py)

```python
# Konstanten für Dateipfade
_PDF_GENERATOR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(
    _PDF_GENERATOR_BASE_DIR, "data", "product_datasheets"
)
COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(
    _PDF_GENERATOR_BASE_DIR, "data", "company_docs"
)
```

**Zweck**: Definiert die Basis-Verzeichnisse für Datenblätter und Firmendokumente relativ zum pdf_generator.py

### 2. Produktdatenblatt-Sammlung

```python
def _collect_product_ids_for_datasheets(pv_details: Dict[str, Any]) -> List[int]:
    """
    Sammelt alle Produkt-IDs für Datenblätter (Haupt + Zubehör).
    
    Args:
        pv_details: PV-Details aus project_data
        
    Returns:
        Liste eindeutiger Produkt-IDs
    """
    product_ids = []
    
    # Hauptkomponenten
    if pv_details.get("selected_module_id"):
        product_ids.append(pv_details["selected_module_id"])
    if pv_details.get("selected_inverter_id"):
        product_ids.append(pv_details["selected_inverter_id"])
    if pv_details.get("include_storage") and pv_details.get("selected_storage_id"):
        product_ids.append(pv_details["selected_storage_id"])
    
    # Zubehörkomponenten (nur wenn aktiviert)
    if pv_details.get('include_additional_components', True):
        accessory_keys = [
            'selected_wallbox_id',
            'selected_ems_id',
            'selected_optimizer_id',
            'selected_carport_id',
            'selected_notstrom_id',
            'selected_tierabwehr_id'
        ]
        for key in accessory_keys:
            comp_id = pv_details.get(key)
            if comp_id:
                product_ids.append(comp_id)
    
    # Duplikate entfernen
    return list(set(filter(None, product_ids)))
```

### 3. Datenblatt-Pfad-Konstruktion

```python
def _get_datasheet_path(product_id: int, get_product_by_id_func: Callable) -> Optional[str]:
    """
    Konstruiert den vollständigen Pfad zum Produktdatenblatt.
    
    Args:
        product_id: Produkt-ID
        get_product_by_id_func: Funktion zum Laden von Produktdetails
        
    Returns:
        Vollständiger Pfad oder None wenn nicht verfügbar
    """
    try:
        product_info = get_product_by_id_func(product_id)
        if not product_info:
            return None
            
        datasheet_path_from_db = product_info.get("datasheet_link_db_path")
        if not datasheet_path_from_db:
            return None
            
        full_path = os.path.join(
            PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN,
            datasheet_path_from_db
        )
        
        if os.path.exists(full_path):
            return full_path
        return None
        
    except Exception:
        return None
```

### 4. Firmendokument-Pfad-Konstruktion

```python
def _get_company_document_paths(
    company_id: int,
    document_ids: List[int],
    db_list_company_documents_func: Callable
) -> List[str]:
    """
    Konstruiert vollständige Pfade für Firmendokumente.
    
    Args:
        company_id: Firmen-ID
        document_ids: Liste der Dokument-IDs
        db_list_company_documents_func: Funktion zum Laden von Dokumenten
        
    Returns:
        Liste vollständiger Pfade
    """
    paths = []
    
    try:
        all_docs = db_list_company_documents_func(company_id, None)
        
        for doc_info in all_docs:
            if doc_info.get('id') in document_ids:
                relative_path = doc_info.get("relative_db_path")
                if relative_path:
                    full_path = os.path.join(
                        COMPANY_DOCS_BASE_DIR_PDF_GEN,
                        relative_path
                    )
                    if os.path.exists(full_path):
                        paths.append(full_path)
                        
    except Exception:
        pass
        
    return paths
```

### 5. PDF-Anhänge-Funktion

```python
def _append_datasheets_and_documents(
    main_pdf_bytes: bytes,
    project_data: Dict[str, Any],
    inclusion_options: Dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int]
) -> bytes:
    """
    Hängt Produktdatenblätter und Firmendokumente an die Haupt-PDF an.
    
    Args:
        main_pdf_bytes: Haupt-PDF als Bytes
        project_data: Projektdaten
        inclusion_options: Auswahl-Optionen aus pdf_ui
        get_product_by_id_func: Funktion zum Laden von Produkten
        db_list_company_documents_func: Funktion zum Laden von Dokumenten
        active_company_id: ID der aktiven Firma
        
    Returns:
        Vollständige PDF mit Anhängen als Bytes
    """
    paths_to_append = []
    debug_info = {
        'product_datasheets_found': [],
        'product_datasheets_missing': [],
        'company_docs_found': [],
        'company_docs_missing': []
    }
    
    # 1. Produktdatenblätter sammeln
    pv_details = project_data.get('pv_details', {})
    product_ids = _collect_product_ids_for_datasheets(pv_details)
    
    for prod_id in product_ids:
        path = _get_datasheet_path(prod_id, get_product_by_id_func)
        if path:
            paths_to_append.append(path)
            debug_info['product_datasheets_found'].append(prod_id)
        else:
            debug_info['product_datasheets_missing'].append(prod_id)
    
    # 2. Firmendokumente sammeln
    doc_ids = inclusion_options.get("company_document_ids_to_include", [])
    if doc_ids and active_company_id:
        doc_paths = _get_company_document_paths(
            active_company_id,
            doc_ids,
            db_list_company_documents_func
        )
        paths_to_append.extend(doc_paths)
        debug_info['company_docs_found'].extend(doc_paths)
    
    # 3. Debug-Ausgabe
    print(f"\n{'='*80}")
    print(f"DEBUG: _append_datasheets_and_documents")
    print(f"{'='*80}")
    print(f"Produktdatenblätter gefunden: {len(debug_info['product_datasheets_found'])}")
    print(f"Produktdatenblätter fehlend: {len(debug_info['product_datasheets_missing'])}")
    print(f"Firmendokumente gefunden: {len(debug_info['company_docs_found'])}")
    print(f"Gesamt anzuhängen: {len(paths_to_append)}")
    print(f"{'='*80}\n")
    
    # 4. Keine Anhänge? Haupt-PDF zurückgeben
    if not paths_to_append:
        return main_pdf_bytes
    
    # 5. PDFs zusammenführen
    try:
        pdf_writer = PdfWriter()
        
        # Haupt-PDF hinzufügen
        main_reader = PdfReader(io.BytesIO(main_pdf_bytes))
        for page in main_reader.pages:
            pdf_writer.add_page(page)
        
        # Anhänge hinzufügen
        for pdf_path in paths_to_append:
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    pdf_writer.add_page(page)
            except Exception as e:
                print(f"Fehler beim Anhängen von {pdf_path}: {e}")
        
        # Finale PDF schreiben
        output = io.BytesIO()
        pdf_writer.write(output)
        return output.getvalue()
        
    except Exception as e:
        print(f"Fehler beim Zusammenführen der PDFs: {e}")
        return main_pdf_bytes
```

### 6. Charts in Visualizations Section

```python
# In generate_offer_pdf(), Section "Visualizations"

# Chart-Konfiguration (synchron mit pdf_ui.py)
charts_config_for_pdf_generator = {
    'monthly_prod_cons_chart_bytes': {
        "title_key": "pdf_chart_title_monthly_comp_pdf",
        "default_title": "Monatl. Produktion/Verbrauch (2D)"
    },
    'cost_projection_chart_bytes': {
        "title_key": "pdf_chart_label_cost_projection",
        "default_title": "Stromkosten-Hochrechnung (2D)"
    },
    # ... weitere Charts ...
}

# Charts aus inclusion_options laden
selected_charts = inclusion_options.get("selected_charts_for_pdf", [])

# Nur ausgewählte Charts rendern
for chart_key, config in charts_config_for_pdf_generator.items():
    if chart_key not in selected_charts:
        continue  # Überspringe nicht ausgewählte Charts
    
    chart_bytes = analysis_results.get(chart_key)
    if chart_bytes and isinstance(chart_bytes, bytes):
        # Chart in Story einfügen
        chart_title = get_text(texts, config["title_key"], config["default_title"])
        story.append(Paragraph(f"<b>{chart_title}</b>", STYLES['SubSectionTitle']))
        
        # Chart-Bild einfügen
        img_flowables = _get_image_flowable(
            chart_bytes,
            available_width * 0.6,
            texts,
            max_height=5*cm
        )
        story.extend(img_flowables)
```

## Data Models

### inclusion_options Dictionary

```python
{
    "include_company_logo": bool,
    "include_product_images": bool,
    "include_all_documents": bool,
    "company_document_ids_to_include": List[int],
    "selected_charts_for_pdf": List[str],  # Chart-Keys
    "include_optional_component_details": bool,
    "append_additional_pages_after_main6": bool
}
```

### Debug Info Dictionary

```python
{
    "product_datasheets_found": List[Dict[str, Any]],  # [{'id': int, 'model': str, 'path': str}]
    "product_datasheets_missing": List[Dict[str, Any]],  # [{'id': int, 'reason': str}]
    "company_docs_found": List[Dict[str, Any]],  # [{'id': int, 'name': str, 'path': str}]
    "company_docs_missing": List[Dict[str, Any]],  # [{'id': int, 'reason': str}]
    "total_paths_to_append": int
}
```

## Error Handling

### Fehlerbehandlungs-Strategie

1. **Graceful Degradation**: Wenn einzelne Anhänge fehlen, wird die PDF trotzdem erstellt
2. **Silent Failures**: Fehler beim Laden einzelner Dateien werden geloggt, aber nicht propagiert
3. **Fallback**: Bei kritischen Fehlern wird die Haupt-PDF ohne Anhänge zurückgegeben
4. **Debug-Logging**: Detaillierte Informationen über gefundene/fehlende Dateien

### Fehlerszenarien

| Szenario | Behandlung |
|----------|------------|
| Datenblatt-Pfad in DB fehlt | Loggen, fortfahren |
| Datenblatt-Datei existiert nicht | Loggen, fortfahren |
| Firmendokument nicht gefunden | Loggen, fortfahren |
| Produkt-ID nicht in DB | Loggen, fortfahren |
| PDF-Merge fehlschlägt | Haupt-PDF zurückgeben |
| Chart-Bytes ungültig | Platzhalter anzeigen |

## Testing Strategy

### Unit Tests

1. **_collect_product_ids_for_datasheets()**
   - Test mit nur Hauptkomponenten
   - Test mit Hauptkomponenten + Zubehör
   - Test mit include_additional_components=False
   - Test mit Duplikaten

2. **_get_datasheet_path()**
   - Test mit existierendem Datenblatt
   - Test mit fehlendem Datenblatt
   - Test mit fehlendem Pfad in DB
   - Test mit ungültiger Produkt-ID

3. **_get_company_document_paths()**
   - Test mit existierenden Dokumenten
   - Test mit fehlenden Dokumenten
   - Test mit leerer Dokument-Liste

### Integration Tests

1. **Vollständige PDF-Generierung**
   - Test mit allen Komponenten (Haupt + Zubehör)
   - Test mit ausgewählten Charts
   - Test mit Firmendokumenten
   - Verifizierung der Seitenanzahl

2. **Fehlerszenarien**
   - Test mit fehlenden Datenblättern
   - Test mit ungültigen Pfaden
   - Test ohne Anhänge

### Manuelle Tests

1. **PDF-Erstellung in GUI**
   - Alle Zubehörkomponenten auswählen
   - Mehrere Charts auswählen
   - Firmendokumente auswählen
   - PDF öffnen und Seitenanzahl prüfen

2. **Debug-Ausgabe prüfen**
   - Terminal-Ausgabe auf gefundene/fehlende Dateien prüfen
   - Pfadkonstruktion verifizieren

## Implementation Notes

### Kritische Änderungen

1. **Basis-Verzeichnisse definieren** (pdf_generator.py, Zeile ~573)

   ```python
   PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "product_datasheets")
   COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "company_docs")
   ```

2. **Zubehör-IDs sammeln** (pdf_generator.py, ~Zeile 2690)

   ```python
   if pv_details.get('include_additional_components', True):
       for opt_id_key in ['selected_wallbox_id', 'selected_ems_id', ...]:
           comp_id = pv_details.get(opt_id_key)
           if comp_id:
               product_ids.append(comp_id)
   ```

3. **Pfadkonstruktion mit Basis-Verzeichnis** (pdf_generator.py, ~Zeile 2704)

   ```python
   full_datasheet_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, datasheet_path_from_db)
   ```

4. **Charts nur wenn ausgewählt** (pdf_generator.py, ~Zeile 2296)

   ```python
   selected_charts = inclusion_options.get("selected_charts_for_pdf", [])
   for chart_key, config in charts_config.items():
       if chart_key not in selected_charts:
           continue
   ```

### Synchronisation mit repair_pdf

Die Implementierung muss exakt der Logik aus `repair_pdf/pdf_generator.py` folgen:

- Zeilen 573-575: Basis-Verzeichnisse
- Zeilen 2680-2770: _append_datasheets_and_documents()
- Zeilen 2287-2353: Charts in Visualizations Section

### Rückwärtskompatibilität

- Bestehende PDFs ohne Anhänge funktionieren weiterhin
- Neue Optionen sind optional (Standardwerte)
- Fehlerhafte Konfigurationen führen zu Fallback-Verhalten
