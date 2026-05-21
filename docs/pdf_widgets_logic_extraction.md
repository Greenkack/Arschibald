# pdf_widgets.py — Logik-Extraktion

Kurzüberblick: Interaktiver Manager für PDF-Sektionen mit Drag & Drop, Fallback-Steuerung und Inhaltseditor. Export/Import von PDF-Strukturen als JSON.

## Kernkomponenten

- PDFSectionManager
  - available_sections: vordefinierte Kernsektionen mit Metadaten (name, icon, default_order, required, configurable, content_types).
  - content_templates: Vorlagen für Inhaltstypen (text, image, pdf, table, chart).
  - initialize_session_state(): legt folgende Keys in st.session_state an:
    - pdf_section_order: Reihenfolge der aktiven Sektionen (Liste von Keys)
    - pdf_custom_sections: benutzerdefinierte Sektionen (Map)
    - pdf_section_contents: Inhalte je Sektion (Map key -> List[Content])
  - render_drag_drop_interface(texts):
    - Checkbox „Drag & Drop aktivieren“; bei aktiv: Spalte mit verfügbaren Sektionen, Spalte mit aktueller PDF-Struktur.
    - Optionaler Bereich „Benutzerdefinierte Sektionen“.
  - _render_available_sections(): zeigt inaktive Sektionen mit Button „Hinzufügen“.
  - _render_pdf_structure(): nutzt sort_items (streamlit_sortables) bei Verfügbarkeit, sonst Fallback-Steuerung.
  - _render_pdf_structure_fallback(): Up/Down/Remove-Buttons je Sektion; Expander zur Sektionskonfiguration.
  - _render_section_editor(section_key, section_info): Listet Inhalte der Sektion, Edit/Remove je Element, Hinzufügen neuer Inhalte (Dropdown nach content_types).
  - _render_content_editor(section_key, idx, content): Editor je Content-Typ:
    - text: Textarea
    - image/pdf: file_uploader mit base64-Encodierung der Datei in content.data
    - table: Platzhalter
    - chart: Auswahl aus bekannten Diagramm-Keys (monthly_generation_chart, deckungsgrad_chart, cost_savings_chart, amortization_chart)
  - _render_custom_section_creator(): Anlage neuer Sektionen mit robustem slug-Key (bereinigt + fortlaufender Suffix bei Kollisionen).
  - export_configuration() -> Dict: {'section_order','custom_sections','section_contents','timestamp'}
  - import_configuration(config): Rekonstruiert State, registriert custom_sections in available_sections.

- render_pdf_structure_manager(texts)
  - UI mit Tabs: „Reihenfolge“, „Import/Export“, „Vorlagen“.
  - Import/Export: JSON-Download/Upload; Fehlertoleranz via try/except.
  - Vorlagen: standard/compact/technical mit vordefinierten Sektionslisten; Anwendung setzt pdf_section_order.

## Daten- und State-Verträge

- st.session_state:
  - pdf_section_order: List[str]
  - pdf_custom_sections: Dict[str, {name, icon, content_types, created}]
  - pdf_section_contents: Dict[str, List[{id, type, data}]]
  - pdf_section_manager: Instanz von PDFSectionManager

- available_sections (Defaults):
  - cover_page, project_overview, technical_components, cost_details, economics
  - Felder: name, icon, default_order, required, configurable, content_types

- content_templates:
  - text, image, pdf, table, chart (default_content je Typ)

## Fehler- und Edge-Handling

- Drag & Drop optional: Wenn streamlit_sortables nicht installiert (ImportError), Fallback-Steuerung aktiv.
- DnD-Fehler im Betrieb: try/except setzt auf Fallback und zeigt Warnung.
- Entfernen: required-Sektionen können nicht gelöscht werden (Button erscheint nicht).
- Uploads: Dateien werden als base64 in-memory gespeichert; Größen- und Sicherheitsaspekte beachten.

## Integration in die PDF-Pipeline

- Die Struktur (section_order + section_contents) kann als Vorgabe für die Seitenreihenfolge und Inhalte in pdf_generator.py dienen.
- Chart-Keys verbinden mit vorhandenen Chart-Funktionen (analysis.py/pv_visuals.py), die PNG-Bytes für den PDF-Einbau liefern.
- Custom-Sektionen: pdf_generator sollte generisch Inhalte anhand type interpretieren (text/image/pdf/table/chart).

## Migration zu Electron + PrimeReact + TypeScript

- State: in Redux/Zustand oder Context speichern; Serialisierung als JSON.
- Drag & Drop: react-beautiful-dnd oder dnd-kit für Reorder + Nested Content Listen.
- Uploads: FileReader -> base64 oder ArrayBuffer; persistieren im userData-Ordner.
- Content-Editoren: Rich-Text (TipTap/Slate), Tabellen (handsontable/ag-Grid), Diagramm-Auswahl via UI und serverseitige PNG-Erzeugung.
- Slug-Erzeugung: gleiche Bereinigung + laufender Index; Schema-Validierung.

## Tests

- Unit: import_configuration/export_configuration Roundtrip.
- UI: Fallback ohne streamlit_sortables; Up/Down/Remove korrekt; required-Sektion nicht entfernbar.
- Content-Editor: image/pdf erzeugen base64-Objekt, text persistiert.
