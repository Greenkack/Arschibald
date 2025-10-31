# pdf_ui.py – vollständige Logik-Extraktion (UI für Angebots-PDF)

Diese Datei stellt die Streamlit-Benutzeroberfläche zur Konfiguration und Erzeugung der Angebots-PDFs bereit. Sie orchestriert Vorlagen, Inhalte, optionale Zusatzseiten ab Seite 7, erweiterte Features (Finanzierung, Charts, Custom Content, Design), die eigentliche Generierung via `pdf_generator.generate_offer_pdf` sowie CRM-Ablage und Debug-Prüfungen.

Stand: 2025-06-08 (mit Datenstatus-Anzeige und Fallback-PDF-Option)

Quellen und Integrationen:

- Streamlit (UI, Session State, Form-Submit, Downloads)
- `doc_output._show_pdf_data_status` (Ampel/Status der Eingabedaten inkl. „fallback“-Zweig)
- `pdf_widgets.render_pdf_structure_manager` (Drag&Drop Reihenfolge-Manager)
- `pdf_generator.generate_offer_pdf` (Hauptgenerator; via Fallback sicher geladen)
- Optional: `pdf_preview.show_pdf_preview_interface` (Vorschau/Editor), `pypdf` oder `PyPDF2` (Debug-Check)
- CRM/DB: `database.get_db_connection`, `crm.save_customer/save_project/create_tables_crm`, `database.add_customer_document`

## Wichtigste Funktionen

### 1) render_pdf_ui(...)

Einstiegspunkt zur PDF-Erstellung via UI. Verantwortlichkeiten:

- Live-Kosten-Vorschau berechnen und in `st.session_state["live_pricing_calculations"]` persistieren.
- Minimalanforderungen prüfen (u. a. Modulanzahl und gewählte Hauptkomponenten). Bei ungenügenden Daten: Hinweise und vorzeitiger Abbruch.
- Datenstatus-Anzeige (`_show_pdf_data_status`):
  - Rückgabe `False`: UI-Abbruch (kritisch).
  - Rückgabe `"fallback"`: erzeugt ein vereinfachtes Informations-PDF via `_create_no_data_fallback_pdf` und bietet es zum Download an.
- Laden von Vorlagen/PDF-Presets aus Admin-Settings und robuste Typumgangslogik (Listen vs. JSON-String).
- Initialisierung und Pflege zentraler Session-State-Keys (siehe unten).
- „Vorlagen & Schnellauswahl“-Bereich: Presets laden/speichern, globale Auswahl/Abwahl.
- „Erweiterte PDF-Features“-Tabs: Finanzierung, Charts, Custom Content (Text/Bilder/Tabellen/Verwaltung), Design, Struktur (Drag&Drop).
- Hauptformular zur finalen Auswahl (Titelbild, Titeltext, Anschreiben, Inhalte, Zusatzseiten ab Seite 7, Firmendokumente, Charts, Hauptsektionen).
- Validierung und Übergabe aller Optionen an den Generator. Erzeugte Bytes stehen zum Download bereit und können im CRM abgelegt werden.

Signatur (vereinfacht):

- Inputs:
  - `texts: Dict[str,str]` – Übersetzungstexte
  - `project_data: Dict[str,Any]` – Kundendaten, Projektdetails, Verbräuche
  - `analysis_results: Dict[str,Any]` – Charts/Bytes, Kennzahlen, KPIs
  - `load_admin_setting_func(key, default)`/`save_admin_setting_func(key, value)` – Admin-Settings Zugriff
  - `list_products_func`, `get_product_by_id_func` – Produktdaten (Datenblätter/Anhänge)
  - Optional: `get_active_company_details_func`, `db_list_company_documents_func`

- Outputs/Side-Effects:
  - Streamlit-UI; setzt/liest diverse `st.session_state`-Keys
  - Ruft `_generate_offer_pdf_safe(...)` (Proxy auf `pdf_generator.generate_offer_pdf`)
  - Download-Button und CRM-Ablage (PDF + JSON-Snapshot)

Wichtig: `final_price`

- Live-Kosten werden hier berechnet und als `"final_price"` in `st.session_state["live_pricing_calculations"]` abgelegt. Der Generator darf dies als Netto-/Brutto-Anker verwenden (vgl. Projektkonventionen).

### 2) show_advanced_pdf_preview(...)

Optionales Vorschau-/Editor-Frontend, wenn `pdf_preview` verfügbar ist. Übergibt einen `generate_pdf_func`-Callback, der intern `_generate_offer_pdf_safe` mit Standardparametern (Admin-Settings, Produkte, Firmen-Dokumente) aufruft. Füllt bei fehlender Firma einen Standard-Fallback.

### 3) render_pdf_debug_section(...)

Ein Debug-Expander, der prüft:

- Verfügbarkeit von `pypdf` oder `PyPDF2`
- Aktive Firma und Anzahl hinterlegter Firmendokumente
- Projektauswahl für Module/WR/Speicher inkl. Prüfung auf vorhandene Datenblattdateien unter `data/product_datasheets`
- Aktuelle `pdf_inclusion_options` als JSON

## Fallbacks und Importschutz

Die Datei definiert Dummy-Fallbacks für nicht verfügbare Komponenten:

- `_dummy_load_admin_setting_pdf_ui`, `_dummy_save_admin_setting_pdf_ui`
- `_dummy_generate_offer_pdf` (zeigt UI-Fehler, liefert `None`)
- `_dummy_get_active_company_details` (Rumpf-Firmendaten)
- `_dummy_list_company_documents` (leere Liste)

`_generate_offer_pdf_safe` versucht, `pdf_generator.generate_offer_pdf` zu importieren; andernfalls wird der Dummy genutzt. Ähnlich für `pdf_preview`.

## Session State – zentrale Schlüssel und Struktur

Wird intensiv genutzt, sowohl zur UI-Steuerung als auch zur Übergabe an den Generator. Wichtigste Keys:

- `pdf_generating_lock_v1: bool` – Re-Entrancy-Guard während der Generierung
- `pdf_inclusion_options: dict` – Schalter und Listen für Inhalte:
  - `include_company_logo: bool`
  - `include_product_images: bool`
  - `include_all_documents: bool`
  - `company_document_ids_to_include: List[int]`
  - `selected_charts_for_pdf: List[str]`
  - `include_optional_component_details: bool`
  - `append_additional_pages_after_main6: bool` – Master-Schalter für Zusatzseiten ab Seite 7
  - temporäre Keys während der Formularauswahl: `_temp_company_document_ids_to_include`, `_temp_selected_charts_for_pdf`
- `pdf_selected_main_sections: List[str]` – Auswahl der Angebots-Sektionen (vom UI, nicht die fest definierten 6 Hauptseiten des Overlay-Templates)
- `pdf_preset_name_input: str` – Name beim Speichern einer Vorlage
- `live_pricing_calculations: dict` – Live-Kosten-Vorschau
  - `base_cost, discount_amount, surcharge_amount, price_after_discounts, total_rabatte_nachlaesse, total_aufpreise_zuschlaege, final_price`
- `financing_config: dict` – Feature-Flags und Default-Szenarien
- `chart_config: dict` – Chart-Typ, Auflösung, Effekte
- `custom_content_items: List[Text|Image|Table]` – Benutzerdefinierte Inhalte
- `temp_table_data: {headers, rows}` – Editor-Puffer für Tabellen
- `pdf_design_config: dict` – Theme, Farbschema, Typografie
- `pdf_section_order: List[str]` – Reihenfolge aus dem Struktur-Manager (Drag&Drop)
- `generated_pdf_bytes_for_download_v1: Optional[bytes]` – PDF Bytes
- `generated_pdf_meta: {timestamp, file_name}` – Stabiler Download-Dateiname
- CRM-bezogen: `_crm_feedback`, `_last_saved_crm_customer_id`, `_last_saved_crm_project_id`, `_crm_expanded`
- Navigation: `selected_page_key_sui` (z. B. auf `doc_output`/`crm` gesetzt)

## Minimalanforderungen & Datenstatus

Vor UI-Interaktion wird geprüft:

- `project_data` muss ein Dict sein.
- `project_details.module_quantity` und (Modul ODER Modulname) und (WR ODER WR-Name) müssen gesetzt sein.
- Bei Problemen: Info und Rückkehr (kein Formular).

`_show_pdf_data_status(project_data, analysis_results, texts)` liefert:

- `False` → UI-Abbruch ohne Formular
- `"fallback"` → Erzeugt (sofort) ein Info-/Fallback-PDF via `pdf_generator._create_no_data_fallback_pdf` und zeigt Download-Button
- sonst → normales Rendering/Generierung möglich

## Vorlagen, Presets und Labels

- Admin-Settings Keys: `pdf_title_image_templates`, `pdf_offer_title_templates`, `pdf_cover_letter_templates`, `pdf_offer_presets`.
- Robuste Typumgangslogik: bereits geladene Listen nicht erneut mit `json.loads` parsen; bei String (JSON) optional parsen; ansonsten Fallbacks setzen.
- Default-Sektionstitel-Mapping (`default_pdf_sections_map`) und Chart-Key-Mapping (`chart_key_to_friendly_name_map`) erzeugen UI-Beschriftungen dynamisch über `get_text_pdf_ui`.

Preset-Handling:

- Laden: Sucht per Name und schreibt Auswahl in `pdf_inclusion_options` und `pdf_selected_main_sections`.
- Speichern: Erzeugt neues Objekt `{name, selections}` und persistiert via `save_admin_setting_func('pdf_offer_presets', json.dumps(...))`.

## Erweiterte Features (Tabs)

1) Finanzierung

- Schaltet `financing_config.enabled` und legt Default-Szenarien an (`conservative/balanced/aggressive`, `bank_loan/kfw_loan`).

1) Charts

- `chart_config`: Chart-Typ, Auflösung, Effekte (`animation`, `3d_effects`, `gradient_effects`).

1) Custom Content

- Text: Titel, Inhalt, Stil, Position; erzeugt Items vom Typ `{"type":"text", ...}`.
- Bild: Upload, Titel, Beschreibung, Position; speichert Base64 (`image_data`) und `image_format`.
- Tabelle: Header-Liste, Zeilen-Editor, Position; speichert `headers` und `rows`.
- Verwaltung: Löschen einzelner/aller Items; einfache Vorschau-Hinweise.

1) Design

- `pdf_design_config`: `theme`, `color_scheme`, `typography`.

1) Struktur

- Ruft `render_pdf_structure_manager(texts)` auf. Dessen Ergebnis (z. B. Reihenfolge) wird in `pdf_section_order` erwartet und beim Generator übergeben.

## Hauptformular und Generierung

Formular-Inhalte:

- Auswahl: Titelbild (Name→Base64), Angebotstitel (Name→Text), Anschreiben (Name→Text)
- Master-Schalter: `append_additional_pages_after_main6`
- Bei aktivem Master-Schalter erscheinen:
  - Firmenlogo, Produktbilder, optionale Komponentendetails
  - „Alle Dokumente“ anhängen
  - Selektion spezifischer Firmendokumente (Checkboxen je Dokument der aktiven Firma)
  - Auswahl der Angebots-Sektionen (Zusatzseiten)
  - Auswahl der verfügbaren Charts (geordnet nach Mappings)

Submit-Flow:

- Temporäre Formular-Keys werden bei Submit in die persistierten Keys übernommen; bei deaktiviertem Zusatzseiten-Schalter werden die Selektionen zurückgesetzt.
- Lock `pdf_generating_lock_v1` verhindert Doppel-Submits.
- Optionale Validierung via `pdf_generator._validate_pdf_data_availability(...)`:
  - Bei kritischen Fehlern: Fallback-PDF über `create_fallback_pdf(...)` (Hinweis: in der Datei ist ein Wrapper-Call gezeigt; Implementierung muss im Generator vorhanden sein).
- Aufruf des Generators `_generate_offer_pdf_safe(...)` mit:
  - `project_data, analysis_results, company_info, company_logo_base64`
  - `selected_title_image_b64, selected_offer_title_text, selected_cover_letter_text`
  - `sections_to_include` (aus `pdf_selected_main_sections`)
  - `inclusion_options` (erweitert um `financing_config`, `chart_config`, `custom_content_items`, `pdf_editor_config`, `pdf_design_config`, `custom_section_order`)
  - `load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, db_list_company_documents_func, active_company_id, texts`

Download & CRM:

- Bei vorhandenen PDF-Bytes: stabiler Dateiname aus zufälligem Base32-Token; Download-Button.
- CRM-Expander:
  - Sucht/legt Kunden an (`save_customer`), legt Projekt an (`save_project`)
  - Ablage des PDFs via `add_customer_document(…, doc_type="offer_pdf")`
  - Ablage eines JSON-Snapshots (`doc_type="project_json"`)
  - Navigationswechsel in die CRM-Ansicht möglich

## Datenkontrakte – Übersicht

Inputs an den Generator (übergeben aus dem UI):

- `project_data: {customer_data?, project_details, consumption_data?, ...}`
- `analysis_results: {… Charts in *_chart_bytes, KPI-Werte …}`
- `company_info: {id, name, …, logo_base64?}`
- `sections_to_include: List[str]` – nur für Zusatzseiten (Seite 7+)
- `inclusion_options: {
    include_company_logo?, include_product_images?, include_all_documents?,
    company_document_ids_to_include?, selected_charts_for_pdf?, include_optional_component_details?,
    append_additional_pages_after_main6?, financing_config?, chart_config?, custom_content_items?,
    pdf_editor_config?, pdf_design_config?, custom_section_order?
  }`

Wichtige Session/State-Werte für Nebenfunktionen:

- `live_pricing_calculations.final_price` als Preisanker (siehe Projekt-Konventionen)
- `pdf_section_order` (Struktur-Manager)

## Edge-Cases und Fehlerbilder

- Admin-Settings liefern falschen Typ (z. B. String statt Liste): robust behandeln, ggf. resetten.
- Keine aktive Firma: Fallback-Firmendaten und Warnung; trotzdem Erstellung möglich.
- Keine PDF-Bibliothek installiert: Debug-Hinweis, Generierung ist davon unberührt (Generator nutzt ReportLab/PDF-Merge selbst).
- `analysis_results` ist leer: UI blendet Chart-Selektion aus; Generierung ggf. ohne Charts.
- Formular-Submit während Generierung: durch Lock verhindert.
- Validierung signalisiert `fallback`: Erzeugung eines einfachen Info-PDF statt Vollangebot.
- Fehlende Produkt-Datenblätter/Dateien: Debug-Bereich weist Dateipfade aus.
- Pfade: `data/company_docs` und `data/product_datasheets` werden relativ zu `cwd` zusammengesetzt.

## TypeScript/Electron-Mapping (Renderer ↔ Main)

Empfohlene Schnittstellen im Renderer (PrimeReact):

- State-Schema analog zu `st.session_state`:
  - `PdfInclusionOptions`, `FinancingConfig`, `ChartConfig`, `CustomContentItem` (Union aus `TextItem | ImageItem | TableItem`), `PdfDesignConfig`
- Services:
  - `pdfPresetsService.load/save`
  - `companyService.getActiveCompany()` / `companyDocs.list(companyId)`
  - `productsService.list/getById`
  - `pdfGenerator.generateOfferPdf(payload)` (IPC → Main)
  - `crmService.saveCustomerAndAttachDocs(payload)`

Beispieltypen (vereinfacht, TS):

- `type CustomContentItem =
  | { type: 'text'; id: string; title: string; content: string; style: 'normal'|'highlight'|'warning'|'info'|'success'; position: 'top'|'middle'|'bottom'|'after_analysis'; created: string }
  | { type: 'image'; id: string; title: string; description?: string; image_data: string; image_format: string; position: 'top'|'middle'|'bottom'|'gallery'; created: string }
  | { type: 'table'; id: string; title: string; headers: string[]; rows: string[][]; position: 'top'|'middle'|'bottom'|'pricing'; created: string }`

Payload an Main (vereinfacht):

- `{
     projectData,
     analysisResults,
     companyInfo,
     selectedTitleImageBase64?,
     selectedOfferTitleText?,
     selectedCoverLetterText?,
     sectionsToInclude: string[],
     inclusionOptions: PdfInclusionOptions & { financingConfig?; chartConfig?; customContentItems?; pdfDesignConfig?; customSectionOrder?: string[] }
   }`

## Tests und Backlog

Tests (empfohlen):

- Unit: `get_text_pdf_ui` (Fallback-Verhalten), `_get_all_available_chart_keys`, `_get_all_available_company_doc_ids`.
- UI/State: Formular-Submit über beide Pfade (mit/ohne Zusatzseiten); Preset-Laden/Speichern; Global Select/Deselect.
- Integration: Generator-Aufruf mit minimalen Daten; Fallback-PDF-Pfad; CRM-Ablage (Mock DB).
- Robustheit: Admin-Settings Typfehler, keine aktive Firma, fehlende Chart-Bytes.

Backlog/Verbesserungen:

- Fehlerfeedback beim Preset-Speichern/Laden internationalisieren.
- Einheitliche Validierungsrückgaben zwischen UI und `pdf_generator` (z. B. strukturierte Fehlercodes).
- Struktur-Manager: Validierung der übergebenen `custom_section_order` gegen `pdf_selected_main_sections`.
- Optional: Vorschau-Bilder der ersten PDF-Seiten einblenden (wenn `pdf_preview` aktiv).

## Kurz „How to“ für die Nutzung

- Rufe `render_pdf_ui(texts, project_data, analysis_results, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, get_active_company_details_func?, db_list_company_documents_func?)` aus der Streamlit-App auf (z. B. im Menüpunkt „Angebotsausgabe (PDF)“).
- Stelle sicher, dass:
  - `project_data.project_details` grundlegende Auswahl (Module/WR) enthält.
  - Charts/KPIs in `analysis_results` verfügbar sind, wenn Diagramme genutzt werden sollen.
  - Admin-Settings für Vorlagen/Preset sauber hinterlegt sind.
  - `pdf_generator.generate_offer_pdf` erreichbar ist – sonst werden Dummy/Fehlerpfade genutzt.
