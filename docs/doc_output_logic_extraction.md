# doc_output.py — vollständige Logik-Extraktion

Ziel: Alle UI- und Datenflüsse der Angebotsausgabe (PDF) dokumentieren. Dieses Modul bildet die Streamlit-UI für die PDF-Erstellung, Validierung, Inhalte/Abschnitte, Visualisierungen, Finanzanalyse-Optionen, Drag&Drop-Editor (Stub), sowie die Anbindung an den Generator (`pdf_generator.generate_offer_pdf*`) und moderne Patches.

## Überblick

- Rolle: UI-Orchestrator für PDF-Angebote mit reichhaltigen Optionen und Fallbacks.
- Hauptfunktionen:
  - `render_pdf_ui(texts, project_data, analysis_results, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, get_active_company_details_func, db_list_company_documents_func)`
  - `show_pdf_generation_ui_with_status(texts, project_data, analysis_results, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, get_active_company_details_func, db_list_company_documents_func)`
  - Hilfen: `_show_pdf_data_status`, `get_text_pdf_ui`, Dummy-Funktionen als Fallbacks.
- Externe Abhängigkeiten: `pdf_generator.generate_offer_pdf` bzw. `generate_offer_pdf_with_main_templates`, `_validate_pdf_data_availability`, `validate_pdf_data`, `create_fallback_pdf`; optional `doc_output_modern_patch`, `pdf_widgets.PDFSectionManager`, `pdf_debug_widget.integrate_pdf_debug`.
- State: Intensive Nutzung von `st.session_state` (u. a. Locks, Auswahl-Optionen, Custom-Content, Design-/Chart-/Finanz-Configs, Preview/Download-Puffer).

## Datenflüsse und Kontrakte

- Inputs in `render_pdf_ui`:
  - `texts: Dict[str,str]` (lokalisierte Strings)
  - `project_data: Dict` mit Bereichen: `customer_data`, `project_details`, `pv_details`.
  - `analysis_results: Dict` mit Kennzahlen & Chart-Bytefeldern (`*_chart_bytes`).
  - Admin-Funktionen: `load_admin_setting_func(key, default)`, `save_admin_setting_func(key, value)`.
  - Produktfunktionen: `list_products_func()`, `get_product_by_id_func(id)`.
  - Firmenfunktionen: `get_active_company_details_func() -> {id,name,logo_base64,...}`, `db_list_company_documents_func(company_id, doc_type?)`.
- Session Keys (Auszug):
  - Lock: `pdf_generating_lock_v1`.
  - Vorlagen: `selected_title_image_*`, `selected_offer_title_*`, `selected_cover_letter_*`.
  - Inclusion: `pdf_inclusion_options` mit Flags `include_company_logo|product_images|all_documents|append_additional_pages_after_main6`, `company_document_ids_to_include`, `selected_charts_for_pdf`.
  - Sections: `pdf_selected_main_sections` (Standard: 8 Hauptsektionen).
  - Design/Charts: `chart_config`, `pdf_design_config`, `pdf_modern_design_config`.
  - Custom Content: `custom_content_items`, `pdf_custom_texts`, `pdf_custom_images`.
  - Financing: `financing_config`, `pdf_include_*`, `pdf_financing_*`.
  - Output: `generated_pdf_bytes_for_download_v1`.
- Validierung:
  - Primär via `pdf_generator._validate_pdf_data_availability(project_data, analysis_results, texts)`.
  - Sekundär einfache Checks (Fallback) mit Anzeige von Warnings/Errors.
- Generator-Aufruf:
  - Bevorzugt modern Patch: `doc_output_modern_patch.enhance_pdf_generation_with_modern_design(offer_data, texts, ... )`.
  - Fallback: `_generate_offer_pdf_safe(...)` (bindet alle Inclusion/Design/Custom-Parameter ein).

## Funktionskatalog (Inputs/Outputs)

- `get_text_pdf_ui(texts, key, fallback=None) -> str`
  - Resiliente Textabfrage; ersetzt fehlende Keys mit Titel-kasierter Fallback-Form.
- `_show_pdf_data_status(project_data, analysis_results, texts) -> bool`
  - Zeigt 4 Status-Kacheln (Kunde, Module, WR, Berechnung); ruft `_validate_pdf_data_availability`; gibt `is_valid` zurück.
- `render_pdf_ui(...): None`
  - Orchestriert UI-Blöcke:
    - Datenkonsolidierung aus Session-State (Füll-Logik bei leeren Eingaben).
    - Visualisierungen & Diagramme: Chart-Typen, Styles, Preview (nur UI, kein Plotly-Render hier).
    - Finanzanalyse: umfangreiche Config inkl. Szenarien; speichert `financing_config` in Session.
    - PVGIS-Optionen (nur wenn Admin aktiviert).
    - Custom Texts/Images/Tables Manager.
    - Drag & Drop Editor (Stub) + erweiterte Styling/Design-Konfiguration.
    - Layout & Design, weitere Slider/Checkboxen.
    - Haupt-Form: Vorlagenauswahl (Titelbild/Titel/Anschreiben), Hauptsektionen, Diagramme, Inklusionsoptionen, Schnellauswahl.
    - PDF-Generierung: Validierung → Modern Patch versuchen → Fallback-Generator; Ergebnis in Session → Download Button außerhalb Form.
- `show_pdf_generation_ui_with_status(...)`
  - Header + `_show_pdf_data_status` + `_validate_pdf_data_availability`-Panel; dient als abgespeckte/diagnostische Variante der UI.

## Fehler- und Edge-Cases

- Fehlender `analysis_results`: UI blendet Info ein, PDF ggf. Fallback.
- Fehlende Firmeninfos: Fallback-Company, Logos optional.
- Fehlende Vorlagenlisten: Fallback-Optionen werden angezeigt.
- Nach `st.rerun()`: Lock/State-Variablen werden gesetzt, Download-Flow robust.
- Charts-Auswahl: filtert vorhandene `*_chart_bytes`; Quick-Select Handlings.

## Migration: Electron + PrimeReact + TypeScript

- UI-Übertragung:
  - Komponenten: PDFConfigurator, ChartOptionsPanel, FinancingPanel, CustomContentManager, SectionSelector, CompanyDocsPicker.
  - State: React Context/Redux statt Session; persistente Admin-Settings via better-sqlite3.
- Generator-Bridge:
  - Beibehalten der Python-PDF-Erzeugung über IPC/child_process; Übergabe von `offer_data` JSON (1:1 zu `final_inclusion_options_to_pass`, `sections_to_include`, `project_data`, `analysis_results`).
  - Alternativ reine TS-PDF-Pipeline mit pdf-lib + templating; Overlay-YAML aus `pdf_template_engine` parallelisieren.
- Charts:
  - Plotly-Kaleido serverseitig (Node: `plotly.js + node-kaleido` oder `puppeteer`) zur PNG-Erzeugung; Bytes in Payload einbetten.

## Mini-Contract (Erfolgskriterien)

- Eingaben vorhanden; `_validate_pdf_data_availability` → `is_valid=True`.
- `generate_offer_pdf` liefert `bytes` oder Modern-Patch liefert `bytes`.
- `st.download_button` erscheint mit Dateiname `Angebot_<Kunde>_<token>.pdf`.

## Tests (skizziert)

- Happy Path: valides `project_data` + `analysis_results` → PDF-Bytes ≠ None.
- Fehlende Analyse: Validierung zeigt Fehler; Fallback-PDF erzeugt.
- Charts-Auswahl: Auswahl persistiert, wird in Inclusion weitergereicht.
- Szenarien aktiv: `financing_config['scenarios']` vorhanden → im Generator konsumiert.

## Backlog

- Drag&Drop-Editor produktiv machen (Reihenfolge via `custom_section_order`).
- Deduplizierung/Reduktion UI-Schalter; Gruppierung in Tabs.
- Lokalisierung auditieren (Keys in `de.json`).
