# gui.py – Vollständige Logik-Extraktion und Migrationsleitfaden

Stand: 2025-09-13

Diese Datei extrahiert und dokumentiert 100% der Logik aus `gui.py` (kompakte, funktionsfähige Version Mai 2025) und bereitet die Migration auf eine Electron + PrimeReact + TypeScript Architektur vor. Sie dient als Referenz für UI-Flows, State/Events, Modul-Integrationen (Berechnung, PDF, Admin), Fehler-/Fallback-Strategien und konkrete IPC/Service-Schnittstellen.

## Überblick

- Rolle: Haupt-GUI der Streamlit-App. Definiert Navigation (Sidebar), orchestriert Modul-Renderings (Dateneingabe, Analyse, PDF, Admin, CRM, Optionen, Wärmepumpe, Solar Calculator etc.), verwaltet Übersetzungen/Text-Fallbacks, initialisiert DB einmalig, zeigt Live-Kosten-Vorschau, und kapselt Fehler.

- Wichtige Konzepte:
  - Navigation über Sidebar-Buttons (optional via `streamlit_shadcn_ui`), stabilisiert durch „nav-lock“ Heuristik gegen ungewolltes Zurückspringen.
  - Zentraler Session-State (Streamlit) als App-weite Datenablage und Ereignisbus.
  - Modul-Lade- und Fallback-Mechanik mit Fehlerliste.
  - Live-Kosten-Vorschau, die auf Berechnungsergebnissen und Pricing-Slidern basiert.
  - PDF-Pipeline Einstiegspunkte: „PDF-Ausgabe“, „PDF-Vorschau“, „Multi-Firmen-Angebote“.

## Module, Imports und Fallbacks

- Lärm-/Log-Reduktion: setzt `BROWSER=none`, reduziert Logger-Level für laute Pakete.
- Optionales UI-Framework: `streamlit_shadcn_ui` (SUI); Fallback auf Standard-Buttons, mit Nutzerhinweisen.
- Modul-Importe via `import_module_with_fallback(name, import_errors)` – sammelt Importfehler in `import_errors`.

Geladene Module (wenn vorhanden):

- `locales` (Übersetzungen), `database`, `product_db`, `data_input`, `calculations`, `analysis`, `crm`, `admin_panel`, `pdf_ui` (als `doc_output_module`), `quick_calc`, `info_platform`, `options`, `pv_visuals`, `ai_companion`, `multi_offer_generator`, `pdf_preview`, `crm_*` UIs, `heatpump_ui`, `solar_calculator`.

Spezielle Funktions-Referenzen aus `calculations` (falls vorhanden):

- `parse_module_price_matrix_csv` → `_parse_price_matrix_csv_from_calculations`
- `parse_module_price_matrix_excel` → `_parse_price_matrix_excel_from_calculations`

DB-Initialisierung: einmalig `database.init_db()` über `initialize_database_once()`, gesteuert durch `st.session_state['db_initialized']`.

## Übersetzungen und Text-Fallbacks

- Primär: `locales.load_translations('de')`.
- Sekundär: `de.json` im Projektverzeichnis.
- Tertiär: harte Fallbacks (Minimalwerte) im Code.
- Zugriff über `get_text_gui(key, default)` – nutzt `TEXTS` bzw. `_texts_initial`.

Wichtige Keys (Beispiele): `app_title`, `menu_item_*`, Fehlertexte (`db_init_error`, `gui_critical_error*`, `module_unavailable*`).

## Session-State Schema (Streamlit)

Initialisierung in `main()`:

- `project_data: { customer_data: {}, project_details: {}, economic_data: {} }`
- `calculation_results: {}`
- `calculation_results_timestamp: datetime | None`
- `calculation_results_backup: {}`
- Navigation:
  - `nav_lock_enabled: bool` (default True)
  - `nav_event: bool` (default False)
  - `selected_page_key_sui: string` (aktuelle Auswahl)
  - `selected_page_key_prev: string`
  - `last_rendered_page_key: string`
- Live-Pricing:
  - `live_pricing_calculations: { base_cost, total_rabatte_nachlaesse, total_aufpreise_zuschlaege, final_price, discount_amount, surcharge_amount, price_after_discounts }`
- Sonstige:
  - `db_initialized: bool`
  - Fallback-Flags für UI: `sui_button_fallback_warning`, `sui_unavailable_warning`
  - Debug-Flags im PDF-Preview-Tab: `preview_debug`, `preview_general_debug`

## Navigation und „nav-lock“

Seitenangebot (Labels → Keys):

- input, solar_calculator, heatpump, analysis, crm_dashboard, crm, crm_calendar, crm_pipeline, options, admin, doc_output, quick_calc, info_platform

Verhalten:

- Buttons setzen bei Klick `nav_event=True`, aktualisieren `selected_page_key_sui` und triggern `st.rerun()`.
- „Nav-Lock“:
  - Hält die aktive Seite stabil, auch wenn Seiten-interne Interaktionen (die Reruns auslösen) passieren.
  - Wenn ein echtes Navigationsevent (`nav_event=True`) erkannt wird, wird `selected_page_key_prev` aktualisiert; sonst bleibt die Auswahl stabil.
  - `last_rendered_page_key` dient als Verlauf/Debug.

Ziel: verhindert unerwünschtes „Zurückspringen“ bei Streamlit-Reruns.

## Live-Kosten-Vorschau (Sidebar)

Funktion: `render_live_cost_preview()`

- Eingaben:
  - `calculation_results` aus Session (benutzt `base_matrix_price_netto` als Voraussetzung)
  - Fallback `base_matrix_price_netto` direkt aus Session-State
  - Pricing-Sliderwerte aus Session:
    - `pricing_modifications_discount_slider` (in %)
    - `pricing_modifications_rebates_slider` (EUR)
    - `pricing_modifications_surcharge_slider` (in %)
    - `pricing_modifications_special_costs_slider` (EUR)
    - `pricing_modifications_miscellaneous_slider` (EUR)

- Berechnung:
  - `discount_amount = base_cost * (discount_percent/100)`
  - `total_rabatte_nachlaesse = discount_amount + rebates_eur`
  - `price_after_discounts = base_cost - total_rabatte_nachlaesse`
  - `surcharge_amount = price_after_discounts * (surcharge_percent/100)`
  - `total_aufpreise_zuschlaege = surcharge_amount + special_costs_eur + miscellaneous_eur`
  - `final_price = price_after_discounts + total_aufpreise_zuschlaege`

- Ausgabe: formattierte Euro-Werte; Speichern in `st.session_state['live_pricing_calculations']` für globale Nutzung (z. B. PDF).

Edge Cases: Kein `calculation_results` oder `base_matrix_price_netto==0` → Vorschau wird nicht angezeigt.

## Seiten-Renderer und Modulverträge

Alle Seiten prüfen, ob das jeweilige Modul vorhanden ist und die erwartete Render-Funktion existiert. Fehler werden abgefangen und in der UI mit Traceback angezeigt.

- input → `data_input.render_data_input(TEXTS)`
- analysis → `analysis.render_analysis(TEXTS, calculation_results)`
- admin → `admin_panel.render_admin_panel(**kwargs)`
  - DB-Funktionen: `get_db_connection`, `save_admin_setting`, `load_admin_setting`, Firmen-CRUD/Dokumente
  - Product-DB: `list_products`, `add_product`, `update_product`, `delete_product`, `get_product_by_id`, `get_product_by_model_name`, `list_product_categories`
  - Parser: `_parse_price_matrix_csv_from_calculations`, `_parse_price_matrix_excel_from_calculations`
  - Validierung: kritische Funktions-Refs müssen callable sein, sonst Fehlermeldung
- doc_output (Tabs):
  - PDF-Ausgabe (Standard): `pdf_ui.render_pdf_ui(texts, project_data, analysis_results, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, get_active_company_details_func, db_list_company_documents_func)`
    - Vorab-Validierung: `project_data.project_details.module_quantity` vorhanden, `calculation_results` non-empty
    - Falls nicht valide: Schritt-für-Schritt-Hinweise
  - PDF-Vorschau: importiert `render_pdf_preview_interface`, `PDF_PREVIEW_AVAILABLE` aus `pdf_preview`
    - Wenn `PDF_PREVIEW_AVAILABLE=False`: Hinweise + Fallback „Basis-PDF-Generierung“ via `pdf_ui.generate_simple_pdf(project_data, calc_results)` und Download-Button
    - Wenn True: holt `active_company` via `database.get_active_company()` (Fallback: Warnung + Platzhalter), ruft `render_pdf_preview_interface(...)` mit Settings/Produkt-APIs
  - Multi-Firmen-Angebote: `multi_offer_generator.render_multi_offer_generator(TEXTS, project_data, calc_results)`; optional `render_product_selection()`
- quick_calc → `quick_calc.render_quick_calc(TEXTS, module_name=...)`
- crm → `crm.render_crm(TEXTS, database.get_db_connection)`
- info_platform → `info_platform.render_info_platform(TEXTS, module_name=...)`
- options (Tabs):
  - Allgemein: `options.render_options(TEXTS, module_name=...)`
  - AI: `ai_companion.render_ai_companion()` (DeepSeek Hinweis)
- heatpump → `heatpump_ui.render_heatpump(TEXTS, module_name=...)`
- solar_calculator → `solar_calculator.render_solar_calculator(TEXTS, module_name=...)`
- crm_dashboard → `crm_dashboard_ui.render_crm_dashboard(TEXTS, module_name=...)`
- crm_pipeline → `crm_pipeline_ui.render_crm_pipeline(TEXTS, module_name=...)`
- crm_calendar → `crm_calendar_ui.render_crm_calendar(TEXTS, module_name=...)`

## Fehlerbehandlung und Fallbacks

- Importfehler werden gesammelt und in der Sidebar angezeigt.
- DB-Init-Fehler landen ebenfalls in `import_errors`.
- Kritische Fehler in `main` werden mit globalem Catch abgefangen und mit Traceback (sofern möglich) angezeigt.
- PDF-Vorschau importiert optional und zeigt Installationshinweise für `PyMuPDF`, `Pillow`, `ReportLab`.
- `streamlit_shadcn_ui` optional: Infos/Warnings bei Fallback auf Standard-Buttons.

## Externe Abhängigkeiten

- Pflicht: Streamlit, pandas, json, datetime, logging, os, sys
- Optional: `streamlit_shadcn_ui`, `PyMuPDF` (für Vorschau), `Pillow`, `ReportLab`

## Daten- und API-Verträge (wichtige Strukturen)

- `project_data` (vereinfacht):
  - `customer_data: { ... }`
  - `project_details: { module_quantity: number, ... }`
  - `economic_data: { ... }`

- `calculation_results`: dict mit Schlüsseln aus `calculations.perform_calculations` (z. B. `base_matrix_price_netto`, `total_investment_netto`, KPIs etc.).

- `live_pricing_calculations` (siehe Live-Kosten-Vorschau).

- Admin-Funktions-Refs siehe oben.

## Migration zu Electron + PrimeReact + TypeScript

Zielbild:

- Renderer (PrimeReact + React Router) ersetzt Streamlit UI. Sidebar-Navigation als feste Komponente, Routen pro Seite.
- Main-Prozess: Services/IPC für DB, Produkte, PDF, Preis-Matrix-Parser.
- Globaler State (z. B. Zustand/Redux) ersetzt `st.session_state`.

### Komponenten und Routen (Renderer)

- `AppSidebar` (PrimeReact PanelMenu/Buttons) → setzt Route (`/input`, `/analysis`, `/pdf`, `/admin`, usw.).
- Routen-Komponenten:
  - `/input` → DataInputPage
  - `/analysis` → AnalysisPage
  - `/pdf` → PdfOutputPage (mit Tabs: Output, Preview, MultiOffers)
  - `/admin` → AdminPanelPage
  - `/quick-calc`, `/crm`, `/crm/dashboard`, `/crm/calendar`, `/crm/pipeline`, `/options`, `/info`, `/heatpump`, `/solar-calculator`

„Nav-Lock“ Übertragung:

- In React normalerweise nicht nötig, da Reruns nicht passieren; falls interne State-Updates ungewollte Re-Renders mit Seiteneffekten verursachen, kann eine „debounced route change“ oder Compare-Guard genutzt werden. Empfehlung: Kein besonderer Lock – stattdessen Route-Quelle (Button/Link) ist alleinige Navigation.

### Globaler State (Store)

- `projectData`: wie oben strukturiert
- `calculationResults`: vollständiges Ergebnisobjekt
- `livePricing`: derived selector aus `calculationResults.base_matrix_price_netto` und Pricing-Slidern
- `pricingControls`: { discountPct, rebatesEur, surchargePct, specialCostsEur, miscEur }
- `texts`: geladen via i18n/JSON
- `activeCompany`: aus DB

### Services und IPC-Verträge (Main)

- DatabaseService
  - `initDb(): Promise<void>`
  - `getDbConnection()` – intern; über IPC exponierte Methoden: `loadAdminSetting(key)`, `saveAdminSetting(key, value)`
  - Firmenverwaltung: `listCompanies()`, `addCompany(company)`, `getCompany(id)`, `updateCompany(company)`, `deleteCompany(id)`, `setDefaultCompany(id)`, `addCompanyDocument(doc)`, `listCompanyDocuments(companyId)`, `deleteCompanyDocument(docId)`
- ProductService
  - `listProducts(filter?)`, `addProduct(p)`, `updateProduct(p)`, `deleteProduct(id)`, `getProductById(id)`, `getProductByModelName(name)`, `listProductCategories()`
- PriceMatrixService
  - `parseCsv(csvText, columnNames: string[]): Promise<DataFrameLike>`
  - `parseExcel(fileBytes, columnNames: string[]): Promise<DataFrameLike>`
- PdfService
  - `renderPdfUi(input): Promise<PdfBytes | DownloadHandle>` – in Electron eher als „PDF erzeugen“ statt UI; die Renderer-UI konfiguriert und ruft `generateOfferPdf()`
  - `generateSimplePdf(projectData, calcResults): Promise<PdfBytes>`
  - `renderPreview(projectData, calcResults, companyInfo, options): Promise<PreviewHandle>`
- CalculationsService
  - `performCalculations(projectData): Promise<CalculationResults>`
- CompanyService
  - `getActiveCompany(): Promise<Company>`

Hinweis: In Electron werden PDF-Vorschau, -Erzeugung und Template-Overlays entweder im Main (Node) oder in einem Worker ausgeführt, nicht im Renderer. Charts kommen als PNG-Bytes aus dem Renderer (oder Headless-Renderer) und werden vom Main zusammengeführt.

### Typen (Auszug)

- `AppTexts: Record<string, string>`
- `ProjectData = { customerData: object; projectDetails: { moduleQuantity: number; /* ... */ }; economicData: object }`
- `CalculationResults = { base_matrix_price_netto?: number; total_investment_netto?: number; /* + KPIs & Listen */ }`
- `LivePricing = { baseCost: number; totalRabatteNachlaesse: number; totalAufpreiseZuschlaege: number; finalPrice: number; discountAmount: number; surchargeAmount: number; priceAfterDiscounts: number }`

### Event-Flows

- Renderer lädt `texts` (i18n) und initialisiert Store.
- Beim Start: `DatabaseService.initDb()`; `CompanyService.getActiveCompany()`.
- Dateneingabe speichert `projectData` → `CalculationsService.performCalculations` → Store `calculationResults`.
- Live-Kosten-Vorschau ist derived: `selectLivePricing(calculationResults, pricingControls)`.
- PDF-Seite nutzt `projectData`, `calculationResults`, `activeCompany` → `PdfService.*`.

## Edge-Cases und Robustheit

- Fehlende Module → klare UI-Warnungen, Tracebacks bei Renderfehlern.
- Fehlende `project_data`/`calculation_results` in PDF → Schritt-für-Schritt-Hinweise.
- Keine aktive Firma → Warnung, Fallback-Company.
- SUI fehlt → Info + Standard-Buttons.
- DB-Init-Fehler → in Sidebar gelistet.

## Tests (empfohlen)

Unit:

- Live-Pricing Formeln (Randfälle: 0-Basispreis, nur Prozente, nur EUR-Auf-/Abschläge, Negativ-Slider verhindern).
- Übersetzungs-Fallback: locales → de.json → harte Defaults.

Integration:

- Navigation: Klick-Wechsel der Seiten bleibt stabil auch bei stärkeren Re-Renders innerhalb einer Seite.
- PDF-Vorschau: Fallback greift, wenn PyMuPDF fehlt; Standard-PDF wird erzeugt.
- Admin-Panel: Parser- und DB-Funktions-Refs vorhanden, Fehleranzeige wenn fehlend.

E2E:

- Voller Angebotsfluss: Eingabe → Analyse → PDF → Download.
- Multi-Firmen-Angebote mit Produktwahl.

## Migration Backlog

- Routen-Skelett in React anlegen; Seitenkomponenten je Tab.
- Globaler Store (Zustand oder Redux Toolkit) mit `projectData`, `calculationResults`, `pricingControls`, `texts`.
- IPC-Handler im Main-Prozess implementieren (DB, Produkte, PDF, Preis-Matrix, Calculations).
- PDF-Preview im Renderer als Canvas/Image-Viewer; Anbindung an Main-Generierung.
- Charts als PNG-Bytes an Main übergeben (für PDF-Zusammenführung).
- Settings/Companies CRUD UI (Admin) mit Validierung.
- Lint/Format Pipelines und grundlegende Tests aufsetzen.

---

Diese Dokumentation spiegelt die exakte Logik von `gui.py` wider und bildet die verbindliche Grundlage für die Migration. Änderungen an Verträgen (Keys/Funktionen) sollten hier aktualisiert werden.
