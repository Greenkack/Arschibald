# Admin-Panel Logik-Extraktion (admin_panel.py)

Stand: basiert auf admin_panel.py (zuletzt geändert laut Kopf: 2025-06-21).

Zweck: Das Admin-Panel bündelt Konfigurationen und Stammdatenpflege für die gesamte App. Es ist UI-getrieben (Streamlit), arbeitet aber über klare Service-Funktionsverträge gegen die Datenbank- und Settings-Schicht. Dieses Dokument extrahiert alle relevanten Verträge, Datenflüsse, Validierungen, Nebenwirkungen sowie eine Abbildung auf eine künftige Electron + PrimeReact Architektur (TypeScript-Services + IPC).

## Bereiche/Module im Admin-Panel

- Firmenverwaltung (Mandanten) inkl. firmenspezifischer Dokumente und neuer firmenspezifischer Vorlagen (Text/Bild)
- Produktverwaltung (Import Excel/CSV, manuelle Pflege, Medienablage für Datenblätter)
- Allgemeine Berechnungsparameter (global_constants) inkl. Ertrags- und Simulationseinstellungen, „Cheat-Amortisationszeit“
- Preis-Matrix Upload/Verwaltung (Excel und CSV Varianten)
- Einspeisevergütungen (feed_in_tariffs: parts/full)
- PDF-Design (Farben), PDF-Branding durch aktive Firma (Logo/Info aus Firmenverwaltung)
- Visualisierungseinstellungen (viz settings innerhalb global_constants)
- Erweiterte Einstellungen: API-Keys, Lokalisierungstexte (JSON), Debug-Modus, Zurücksetzen von App-Daten

Globale Konventionen:

- get_text_local(key, fallback) liest Texte aus `st.session_state['_admin_panel_texts']` (vorher in `render_admin_panel` gesetzt).
- `WIDGET_KEY_SUFFIX = "_apv1"` wird für eindeutige Widget-Keys verwendet.
- Services/Funktionsreferenzen werden beim Eintritt in `render_admin_panel` als „safe“-Variablen gesetzt (z. B. `_load_admin_setting_safe`).

## Öffentlicher Einstiegspunkt

render_admin_panel(texts, get_db_connection_func, save_admin_setting_func, load_admin_setting_func, parse_price_matrix_csv_func, list_products_func, add_product_func, update_product_func, delete_product_func, get_product_by_id_func, get_product_by_model_name_func, list_product_categories_func, db_list_companies_func, db_add_company_func, db_get_company_by_id_func, db_update_company_func, db_delete_company_func, db_set_default_company_func, db_add_company_document_func, db_list_company_documents_func, db_delete_company_document_func, parse_price_matrix_excel_func?)

- Setzt Session-Texts, registriert alle Servicefunktionen in globalen _*_safe Variablen.
- Erzeugt Tabs gemäß ADMIN_TAB_KEYS_DEFINITION_GLOBAL und ruft pro Tab die passende Render-Funktion.
- parse_price_matrix_excel_func kann optional extern injiziert werden; sonst Fallback parse_module_price_matrix_excel.

## Firmenverwaltung (render_company_crud_tab)

Funktionen (von DB-Schicht bereitzustellen):

- list_companies() -> List[Company]
- add_company(data) -> int | None
- get_company_by_id(id) -> Company | None
- update_company(id, data) -> bool
- delete_company(id) -> bool
- set_default_company(id) -> bool  (setzt auch active_company_id Setting)
- add_company_document(company_id, display_name, document_type, original_filename, bytes) -> int | None
- list_company_documents(company_id, doc_type?) -> List[CompanyDocument]
- delete_company_document(document_id) -> bool
- Settings: load_admin_setting('active_company_id'), save_admin_setting('active_company_id', id)

Company Felder (aus UI sichtbar/erwartet):

- id, name (required), street, zip_code, city, phone, email, website, tax_id, commercial_register, bank_details, pdf_footer_text, logo_base64 (optional), is_default (0/1)

UI/Flow:

- Aktive Firma lesen (active_company_id) und Kurzinfo anzeigen.
- Expander „Neue Firma anlegen“ wird automatisch geöffnet, wenn Bearbeitung aktiv oder es noch keine Firmen gibt.
- Formular validiert Name != empty; Logo optional (max 2MB, base64 gespeicherter Inhalt), bei Update beibehaltbar.
- Beim Anlegen: Wenn es die erste Firma ist, wird automatisch set_default_company(new_id) versucht.
- Firmenliste Tabelle: Aktionen Bearbeiten, Löschen (mit 2-Klick-Bestätigung), Als Standard/Aktiv setzen (setzt DB-Default und active_company_id Setting)

Firmendokumente Tab (innerhalb Edit-Modus):

- Dokument-Typen: AGB, Datenschutz, Vollmacht, SEPA-Mandat, Freistellungsbescheinigung, Sonstiges
- Upload PDF max 5MB; Speicherung via add_company_document; Auflistung + Löschen mit 2-Klick-Bestätigung.

Neue firmenspezifische Vorlagen-Tabs:

- Textvorlagen: add_company_text_template, list_company_text_templates, update_company_text_template, delete_company_text_template
  - Felder: id, company_id, name, template_type in {offer_text, cover_letter, title_text, footer_text, custom}, content (Text)
- Bildvorlagen: add_company_image_template, list_company_image_templates, get_company_image_template_data, update_company_image_template, delete_company_image_template
  - Felder: id, company_id, name, template_type in {title_image, logo, reference, background, custom}, original_filename, image_data (Blob)

Nebenwirkungen/Validierungen:

- PNG/JPG Logo bis 2MB, Base64 im DB-Feld
- Dokumente PDF bis 5MB, Speicherung als BLOB in DB
- 2-Klick-Löschbestätigung über Session-State-Flag

## Produktverwaltung (render_product_management)

Funktionen (DB-Schicht):

- list_products(category?) -> List[Product]
- add_product(data) -> int | None
- update_product(id, data) -> bool
- delete_product(id) -> bool
- get_product_by_id(id) -> Product | None
- get_product_by_model_name(model_name) -> Product | None
- list_product_categories() -> List[str]

Produkt Felder (aus Import/Manuell ersichtlich):

- id, category, model_name, brand, price_euro, additional_cost_netto,
  capacity_w (Modul), efficiency_percent, length_m, width_m, weight_kg,
  power_kw (WR/Storage), storage_power_kw (kWh für Storage), max_cycles,
  warranty_years, description, pros, cons, rating,
  image_base64, datasheet_link_db_path, origin_country, created_at, updated_at

Medienablage für Datenblätter:

- Base-Pfad: `data/product_datasheets/<product_id>/<filename_with_timestamp>.pdf`
- Beim Update: altes Datenblatt löschen, leere Unterordner aufräumen; dann neues speichern und DB-Feld aktualisieren.
- Beim Anlegen: erst Produkt ohne Pfad anlegen, danach Datei speichern und DB-Update mit relativem Pfad.
- Lösch-Flow für existierendes Datenblatt: Datei entfernen, dann DB-Feld auf None setzen.

CSV/Excel Import:

- Excel: pd.read_excel(...)
- CSV: Auto-Erkennung (utf-8, iso-8859-1, latin1, cp1252; Trennzeichen autodetect oder „;“), Decimal/Thousands heuristisch; Spaltennamen normalisiert (lower + spaces→_)
- Pflichtspalten: model_name, category
- Zahlenfelder werden robust normalisiert (Punkte/Tausender entfernen, Komma→Punkt), int-Konvertierung für warranty_years, max_cycles, rating
- Vorhandene Produkte werden über model_name identifiziert und geupdatet, sonst add
- Ergebnisstatistik: imported, updated, skipped + Fehlerliste (erste 10 als JSON Anzeige)

Liste/Filter:

- Filter nach Kategorie; Anzeige Tabelle mit (ID, Modell, Bild, Datenblatt?, Kategorie, Preis) + Buttons Bearbeiten/Löschen

## Allgemeine Einstellungen (render_general_settings_extended)

Settings-Key: `global_constants` (dict). Defaults werden mit `_DEFAULT_GLOBAL_CONSTANTS_FALLBACK` gemerged.

Wichtige Keys (Auszug):

- MwSt., Inflation, Degradation, maintenance_fixed_eur_pa, maintenance_variable_eur_per_kwp_pa, maintenance_increase_percent_pa, alternative_investment_interest_rate_percent
- global_yield_adjustment_percent, reference_specific_yield_pr
- specific_yields_by_orientation_tilt: `Map[Orientation][Tilt]` → kWh/kWp/a
- simulation_period_years, electricity_price_increase_annual_percent
- visualization_settings (separat im Viz-Tab editierbar)

Speichern validiert keine komplexen Constraints; es werden fehlende Keys mit Defaults aufgefüllt.

Cheat-Amortisationszeit:

- Setting-Key: amortization_cheat_settings: {enabled: bool, mode: 'fixed'|'absolute_reduction'|'percentage_reduction', value_years?: number, percent?: number}

## Preis-Matrix (render_price_matrix)

Settings-Keys:

- price_matrix_excel_bytes: bytes (xls/xlsx-Datei; gelesen via parse_module_price_matrix_excel)
- price_matrix_csv_data: string (CSV-Inhalt; geparst via calculations.parse_price_matrix_csv)

Parsing:

- Excel: Bytes→DataFrame, Index: „Anzahl Module“, Normalisierung von Zahlenformaten („1.234,56“ → 1234.56), Drop leere Zeilen/Spalten.
- CSV: robust via injizierter Parser aus calculations.

Flows:

- Upload, Vorschau (DataFrame), Speichern in Settings; Anzeigen der gespeicherten Matrix + Löschen.

## Einspeisevergütungen (render_tariff_management)

Settings-Key: feed_in_tariffs: { parts: [{kwp_min, kwp_max, ct_per_kwh}], full: [...] }

- UI validiert: kwp_max > kwp_min; Zahleneingaben mit Schrittweiten; 2 getrennte Formulare für parts/full.

## Visualisierung (render_visualization_settings)

Teil von `global_constants.visualization_settings`

- Felder: default_color_palette, primary_chart_color, secondary_chart_color,
  chart_font_family, chart_font_size_title, chart_font_size_axis_label, chart_font_size_tick_label

## PDF Design (render_pdf_design_settings)

Settings-Key: `pdf_design_settings`: { primary_color, secondary_color }

- Anzeige des Logos/Infos der aktiven Firma (nur read-only Hinweise) – Pflege erfolgt in Firmenverwaltung.

## Erweiterte Einstellungen (render_advanced_settings)

API Keys:

- Keys: Maps_api_key, bing_maps_api_key, osm_nominatim_email
- Anzeige der aktuellen Werte nur als Platzhalter; Eingabe speichert neue Werte.

Lokalisierung:

- Settings-Key: `de_locale_data` (dict als JSON). Direkter Text-Editor (TextArea) → JSON parse → save_admin_setting.

Debug-Modus:

- Settings-Key: `app_debug_mode_enabled` (bool)

Reset App-Daten:

- Löscht `data/app_data.db` nach Sicherheitsphrase „ALLES ENDGÜLTIG LÖSCHEN“. Räumt Session-State weitgehend auf und fordert Neustart.

## Fehlerbehandlung und UX-Details

- Durchgehend st.rerun() nach erfolgreichen Änderungen, um UI-State zu konsolidieren.
- 2-Klick-Löschbestätigungen über Session-State Flags.
- Upload-Größenlimits: Logo 2MB, PDF 5MB, Bildvorlagen ähnlich (bei Bildvorlagen ohne explizites Limit außer Hinweis; technisch akzeptiert PNG/JPG/JPEG/SVG).
- Robuste CSV/Excel-Dekodierung: mehrfacher Encoding-Versuch, Separator-Heuristik.

## TypeScript/Electron Mapping (Zielarchitektur)

Empfohlene Services (Main-Prozess):

```ts
AdminSettingsService
  get(key): Promise<any>
  set(key, value): Promise<boolean>
  // keys: 'global_constants', 'price_matrix_excel_bytes'(Buffer), 'price_matrix_csv_data'(string),
  //       'feed_in_tariffs', 'de_locale_data', 'pdf_design_settings', 'Maps_api_key',
  //       'bing_maps_api_key', 'osm_nominatim_email', 'app_debug_mode_enabled', 'active_company_id'

CompanyService
  list(): Promise<Company[]>
  create(data: CompanyInput): Promise<number>
  getById(id: number): Promise<Company | null>
  update(id: number, patch: Partial<Company>): Promise<boolean>
  delete(id: number): Promise<boolean>
  setDefault(id: number): Promise<boolean>  // setzt DB-Flag und AdminSettings active_company_id

CompanyDocumentsService
  add(companyId: number, displayName: string, type: string, originalFilename: string, data: Buffer): Promise<number>
  list(companyId: number, type?: string): Promise<CompanyDocument[]>
  delete(documentId: number): Promise<boolean>

CompanyTextTemplatesService
  add(companyId: number, name: string, content: string, templateType: string): Promise<number>
  list(companyId: number): Promise<TextTemplate[]>
  update(id: number, name: string, content: string): Promise<boolean>
  delete(id: number): Promise<boolean>

CompanyImageTemplatesService
  add(companyId: number, name: string, type: string, originalFilename: string, data: Buffer): Promise<number>
  list(companyId: number): Promise<ImageTemplate[]>
  getData(id: number): Promise<Buffer>
  update(id: number, name: string): Promise<boolean>
  delete(id: number): Promise<boolean>

ProductService
  list(category?: string): Promise<Product[]>
  create(data: ProductInput): Promise<number>
  getById(id:number): Promise<Product|null>
  getByModelName(modelName: string): Promise<Product|null>
  update(id:number, patch: Partial<Product>): Promise<boolean>
  delete(id:number): Promise<boolean>
  listCategories(): Promise<string[]>
  saveDatasheetFile(productId:number, file: Buffer, originalName: string): Promise<string> // gibt relativen Pfad zurück
  deleteDatasheetFile(productId:number): Promise<boolean>

PriceMatrixService
  parseExcel(file: Buffer): Promise<PriceMatrixTable> // lokal in Renderer möglich, aber bevorzugt im Main
  parseCsv(csv: string): Promise<PriceMatrixTable>
  getExcel(): Promise<Buffer|null>
  setExcel(file: Buffer|null): Promise<boolean>
  getCsv(): Promise<string|null>
  setCsv(csv: string|null): Promise<boolean>

TariffService
  get(): Promise<FeedInTariffs>
  set(tariffs: FeedInTariffs): Promise<boolean>

LocalizationService
  get(): Promise<Record<string,string>>
  set(data: Record<string,string>): Promise<boolean>

DebugService
  getFlag(): Promise<boolean>
  setFlag(enabled: boolean): Promise<boolean>

MaintenanceService
  resetAppData(): Promise<boolean> // löscht DB-Datei sicher im userData/data Pfad; evtl. App-Neustart
```

Renderer (PrimeReact) kommuniziert via IPC (preload bridge) mit obigen Services.

### TypeScript Typen (Kurzformen)

type Company = { id: number; name: string; street?: string; zip_code?: string; city?: string; phone?: string; email?: string; website?: string; tax_id?: string; commercial_register?: string; bank_details?: string; pdf_footer_text?: string; logo_base64?: string; is_default?: 0|1 };

type CompanyDocument = { id: number; company_id: number; display_name: string; document_type: string; file_name: string; created_at: string };

type TextTemplate = { id: number; company_id: number; name: string; template_type: string; content: string };

type ImageTemplate = { id: number; company_id: number; name: string; template_type: string; original_filename: string };

type Product = { id: number; category: string; model_name: string; brand?: string; price_euro?: number; additional_cost_netto?: number; capacity_w?: number; storage_power_kw?: number; power_kw?: number; max_cycles?: number; warranty_years?: number; length_m?: number; width_m?: number; weight_kg?: number; efficiency_percent?: number; origin_country?: string; description?: string; pros?: string; cons?: string; rating?: number; image_base64?: string; datasheet_link_db_path?: string; created_at?: string; updated_at?: string };

type PriceMatrixTable = { indexLabel: string; rows: Array<{ modulesCount: number; [col: string]: number }>; columns: string[] };

type FeedInTariffs = { parts: Array<{ kwp_min: number; kwp_max: number; ct_per_kwh: number }>; full: Array<{ kwp_min: number; kwp_max: number; ct_per_kwh: number }> };

## Edge Cases und Annahmen

- active_company_id kann in Settings als String gespeichert sein; bei Nutzung in UI wird auf int gecastet; ungültige Werte → Warnung.
- Preis-Matrix Excel: Index-Spalte muss „Anzahl Module“ heißen; ansonsten Fehlermeldung. Nach Reinigung darf DataFrame nicht leer sein.
- CSV Import Produkte: Manche Dateien haben gemischte Tausender-/Dezimaltrenner; es gibt eine Heuristik zur Korrektur.
- Dateien löschen: Beim Entfernen alter Datenblätter wird versucht, leere Ordner zu löschen.
- Bildvorlagen: get_company_image_template_data liefert Binärdaten; Anzeige erfolgt direkt aus Bytes.
- Lokalisierung: Der Editor setzt keine Schemavalidierung voraus, nur JSON-Validität und Top-Level Objekt.

## Validierungs-/Erfolgsmeldungs-Kontrakt (UI → Services)

- Bei erfolgreichen Mutationen sollte der Service deterministisch true/ID liefern. UI führt daraufhin st.rerun() aus.
- Bei Fehlern liefert Service false/null und UI zeigt eine generische/konkrete Fehlermeldung.

## Migrationstipps PrimeReact

- Tabs: PrimeReact TabView; Formulare: Controlled Components; Dateiupload: FileUpload mit custom upload handler → IPC.
- 2-Klick-Löschen: ConfirmDialog oder Toast + zweiten Klick.
- Tabellen: DataTable mit Paginator/Filter; Bild-Preview via base64-URL oder Blob-URL aus getData().
- Form State: Zentrale Formik/React-Hook-Form; Fehlertoleranzen wie im Streamlit-Original beibehalten.

## Verweise/Abhängigkeiten

- calculations.py: parse_price_matrix_csv wird hier erwartet und im Admin-Panel injiziert.
- database.py: Firmen/Produkte/Docs/Templates-CRUD, inkl. neue Endpunkte für firmenspezifische Text-/Bildvorlagen (siehe oben genannte Funktionsnamen).
- PDF-Pipeline: PDF-Design/Firmenlogo wird von pdf_generator/pdf_template_engine konsumiert; active_company_id wichtig für konsistente Angebote.

— Ende —
