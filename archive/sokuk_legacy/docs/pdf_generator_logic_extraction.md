# pdf_generator.py – Vollständige Logik-Extraktion und Migrationsleitfaden

Diese Dokumentation extrahiert die komplette Logik aus `pdf_generator.py` (Stand: lokal), beschreibt Datenflüsse, öffentliche APIs, Validierung und Fallbacks, Styles/Design, die neue 6-Seiten-Template-Pipeline sowie den Legacy-ReportLab-Flow. Außerdem enthält sie klare TypeScript/Electron-Mappings und Tests/Backlog.

> Hinweis: Die App besitzt parallel eine „Overlay“-Engine (`pdf_template_engine/`) mit YML-Koordinaten (`coords/seite1.yml`…`seite6.yml`) und statischen Hintergrund-PDFs (`pdf_templates_static/notext/`). Diese wird hier detailliert eingeordnet.

---

## 1) Öffentliche APIs und Datenkontrakte

- generate_offer_pdf_with_main_templates(project_data, analysis_results, company_info, company_logo_base64, selected_title_image_b64, selected_offer_title_text, selected_cover_letter_text, sections_to_include, inclusion_options, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, db_list_company_documents_func, active_company_id, texts, use_modern_design=True, **kwargs) -> Optional[bytes]
  - Haupt-Einstieg: Erzeugt 6-Seiten-Hauptausgabe via Template-Engine und hängt optional die „Legacy“-Zusatzseiten an (ohne Deckblatt/Anschreiben). Enthält Seitenzähl-Overlay („Seite x von XX“) für Zusatzseiten.
  - Inputs: s. unten „Input-Keys“ und „Inklusions-Optionen“.
  - Output: Bytes des finalen PDFs.

- generate_main_template_pdf_bytes(project_data, analysis_results, company_info, additional_pdf=None) -> Optional[bytes]
  - Baut das 6-seitige Overlay-PDF: build_dynamic_data -> generate_overlay(total_pages) -> merge_with_background.
  - total_pages berücksichtigt Zusatzseiten (wenn vorhanden), damit „von XX“ korrekt ist.

- generate_offer_pdf(..., disable_main_template_combiner=False, ...) -> Optional[bytes]
  - Legacy-/Gesamter Generator. Ruft per Default den Template-Combiner auf; nur bei disable_main_template_combiner=True wird die klassische ReportLab-Erstellung ausgeführt (Deckblatt, Anschreiben, dynamische Sektionen, Custom Content, Anhänge).

- PDFGenerator Klasse (separater, einfacher Story/Platypus-Ansatz)
  - create_pdf(): iteriert über `module_order` und ruft `_draw_*`-Methoden. Eher Demo/Legacy; paralleler Ansatz zu den obigen Funktionen.

- merge_pdfs(pdf_files: List[str|bytes|BytesIO]) -> bytes
  - Robust zusammenführen via PyPDF/PyPDF2; Fallback gibt erste PDF zurück.

### Input-Datenkontrakte (Auszug)

- project_data
  - customer_data: { salutation, title, first_name, last_name, company_name, address, house_number, zip_code, city }
  - project_details: { module_quantity, include_storage, selected_module_id, selected_inverter_id, selected_inverter_quantity, selected_storage_id, selected_wallbox_id, selected_ems_id, selected_optimizer_id, selected_carport_id, selected_notstrom_id, selected_tierabwehr_id, satellite_image_base64_data, visualize_roof_in_pdf_satellite }
  - company_information: { name, street, zip_code, city, phone, email, website, tax_id, logo_base64 }
- analysis_results
  - Kern-KPIs: anlage_kwp, annual_pv_production_kwh, self_supply_rate_percent, self_consumption_percent
  - Kosten: base_matrix_price_netto, cost_*_netto, subtotal_netto, total_investment_netto, vat_rate_percent, total_investment_brutto
  - Wirtschaftlichkeit: annual_financial_benefit_year1, amortization_time_years, simple_roi_percent, lcoe_euro_per_kwh, npv_value, irr_percent
  - Simulation: annual_productions_sim, annual_benefits_sim, annual_maintenance_costs_sim, annual_cash_flows_sim, cumulative_cash_flows_sim
  - Visualisierungen (PNG-Bytes): diverse *_chart_bytes
- company_info: vgl. company_information oben
- texts: Übersetzungen/Labels; get_text(key,fallback)
- sections_to_include: Liste von Abschnitts-Keys, z.B. ["ProjectOverview","TechnicalComponents",...]
- inclusion_options (Auszug)
  - append_additional_pages_after_main6: bool
  - skip_cover_and_letter: bool
  - include_company_logo, include_product_images, include_all_documents
  - company_document_ids_to_include: List[int]
  - include_optional_component_details: bool
  - financing_config, chart_config, custom_content_items, pdf_editor_config, pdf_design_config
  - selected_charts_for_pdf: List[str]
  - custom_section_order: List[str] mit Generator-Keys

---

## 2) 6-Seiten-Template-Pipeline (Overlay)

- Pfade: COORDS_DIR=coords/, BG_DIR=pdf_templates_static/notext/
- DYNAMIC_DATA_TEMPLATE definiert logische Platzhalter wie customer_name, pv_power_kWp, annual_yield_kwh, ...
- Ablauf
  1. build_dynamic_data(project_data, analysis_results, company_info)
  2. generate_overlay(coords_dir, dyn_data, total_pages)
  3. merge_with_background(overlay_bytes, bg_dir)
- Seitenzählung: total_pages = 6 + len(additional_pdf.pages), wenn Zusatz vorhanden, sonst 6.
- Integration: generate_offer_pdf_with_main_templates ruft zuerst optional den Legacy-PDF-Bytes-Generator (mit skip_cover_and_letter=True), setzt total_pages, erzeugt main6 und merged dann.

### Zusatzseiten-Footer und Seitennummern

- _overlay_footer_page_numbers(pdf_bytes, start_number=7, total_pages, logo_b64, footer_left_text)
  - Erzeugt pro Seite ein ReportLab-Overlay mit Datum, „Seite x von XX“, optional Firmenlogo oben links und linkem Footer-Text (z. B. Kundenname). Nutzt PRIMARY_COLOR_HEX leicht variiert als Footerbar.

---

## 3) Legacy-ReportLab-Flow (Story/Platypus)

- Header/Footer: PageNumCanvas + page_layout_handler(canvas, doc, ...)
  - Header ab Seite 2 („Angebot“ + Linie), Footer mit Datum + Seitennummer, dünne Deko-Linien oben/unten.
- Styles und Farben: STYLES, Farben (PRIMARY_COLOR_HEX etc.), Tabellenstyles (TABLE_STYLE_DEFAULT, DATA_TABLE_STYLE), Zebra-Funktion, Produkt-Tabellenstyles (MODERN_PRODUCT_TABLE_STYLE), u. a.
- Deckblatt: Titelbild (optional), Firmenlogo, Angebots-Titel (mit Platzhaltern), Firma-Block, Kundenadresse (4-Zeilen-Format), Angebotsnummer, Datum.
- Anschreiben: Absender, Empfängeradresse, Datum, Betreffzeile, Text (mit Platzhalterersetzung), Grußformel, Firmenname; KeepTogether.
- Dynamische Sektionen (per sections_to_include + custom order)
  - ProjectOverview: Satellitenbild (optional), KPIs (kWp, Module, Produktion, Autarkie), tabellarisch, KeepTogether.
  - TechnicalComponents: Modul/WR(+Menge)/Speicher; _add_product_details_to_story holt Produktdetails via get_product_by_id_func, baut Bild + Details-Tabelle + Beschreibung; optional weitere Komponenten (Wallbox, EMS, Optimierer, Carport, Notstrom, Tierabwehr) mit Titeltexten. Alles mit KeepTogether.
  - CostDetails: _prepare_cost_table_for_pdf sortiert Kostenpositionen, wendet formatierten Stil an, fügt Hinweise zu Speicherpreis-Logik hinzu; KeepTogether.
  - Economics: optional financing_config (Szenarien, Sensitivität, Optionen) + KPI-Tabelle (Bruttoinvestition, Vorteil J1, Amortisation, ROI, LCOE, NPV, IRR); KeepTogether.
  - SimulationDetails: _prepare_simulation_table_for_pdf (Header + Jahre, ggf. …-Zeile); KeepTogether.
  - CO2Savings: Einleitungs-/Haupt-Text, Vergleichstabelle (Bäume/Auto/Flug), optional Chart-Bytes, abschließender Text; KeepTogether.
  - Visualizations: Intro + ausgewählte Charts (max 3/Seite), je Chart Titel (bereinigt), Bild in kompakter Größe, KPI-Zeile (_build_chart_kpi_html), Beschreibung (_get_chart_description); KeepTogether und automatische Seitenumbrüche.
  - FutureAspects: E-Mobilität und Wärmepumpe Text-Module mit Werten aus analysis_results; KeepTogether.
  - Weitere optionale Firmen-Seiten: CompanyProfile, Certifications, References, Installation, Maintenance, Financing, Insurance, Warranty; alle KeepTogether.
- Custom Content: position-basiert (top, middle, bottom). Typen: text, image, table; jeweils KeepTogether.
- Anhänge: include_all_documents + _PYPDF_AVAILABLE: Dateien aus data/company_docs und data/product_datasheets (Details siehe TODO-Hinweis unten im Code – Funktion endet im Ausschnitt kurz vor dem Zusammenstellen der Wege).

---

## 4) Validierung, Fallbacks und Platzhalter

- Vor-Validierung in generate_offer_pdf: Ergänzt fehlende company_information im project_data und versucht final_price zu setzen (SessionState live_pricing_calculations.final_price > Analyse-Totals > None).
- _validate_pdf_data_availability(project_data, analysis_results, texts) wird aufgerufen; bei Fehlern wird _create_no_data_fallback_pdf(texts, customer_data) genutzt. Bei fehlendem ReportLab gibt es _create_plaintext_pdf_fallback(...).
- Platzhalterersetzung: _replace_placeholders(text_template, customer_data, company_info, offer_number, texts, analysis_results)
  - Unterstützt [VollständigeAnrede], [Angebotsnummer], [Datum], Kundenfelder, sowie Analyse-Platzhalter wie [AnlagenleistungkWp], [GesamtinvestitionBrutto], [FinanziellerVorteilJahr1].
  - Anrede-Logik via _generate_complete_salutation_line(customer_data,texts) (Herr/Frau/Familie/Firma/generic).

Fehlende Implementierungen im File (vermutlich existieren in demselben Modul oder in Nachbar-Dateien; hier referenziert):

- _validate_pdf_data_availability
- _create_no_data_fallback_pdf
- _create_plaintext_pdf_fallback

Diese sollten laut Projekt-Anweisung in pdf_generator.py vorhanden sein oder aus Hilfsmodulen stammen. Im vorliegenden Ausschnitt sind sie nicht enthalten – bitte prüfen und nachziehen.

---

## 5) Wichtige Hilfsfunktionen

- format_kpi_value(value, unit, na_text_key, precision, texts_dict)
  - Deutsche Formatierung, Prozent/Jahre-Sonderfälle, NaN/Inf/Strings robust.
- _get_image_flowable(image_data_input, desired_width, texts, caption_key?, max_height?, align)
  - Decodiert Base64 oder Bytes, skaliert proportional, baut optional Bildunterschrift.
- _sanitize_chart_title(raw_title)
  - Entfernt Klammerzusätze „(Jahr 1)“, „(3D)“ für kompaktere Titel im PDF.
- _build_chart_kpi_html(chart_key, analysis, texts)
  - Liefert passende KPI-Zeile je Chart-Typ.
- `_prepare_cost_table_for_pdf(...)` und `_prepare_simulation_table_for_pdf(...)`
  - Erzeugen saubere Tabellen-Daten inkl. Style-Auswahl.
- _add_product_details_to_story(...)
  - Holt Produktdaten via Callback, baut kombinierte Text/Bild-Tabellen und hält die Einheit zusammen.

---

## 6) Electron/TypeScript-Mapping

- Services
  - PdfTemplateService: buildDynamicData(project, analysis, company) -> OverlayBytes; mergeWithBackground(overlay, bgDir) -> Bytes
  - PdfComposeService: combineMain6WithAdditional(main6, additional, opts) -> Bytes; overlayFooterNumbers(pdf, start, total, logo?, leftText?) -> Bytes
  - PdfLegacyService: renderOfferPdf(project, analysis, company, opts) -> Bytes (Deckblatt, Anschreiben, Sektionen, Charts, Custom, Attachments)
- Models
  - ProjectData, AnalysisResults, CompanyInfo, InclusionOptions, Texts
- Renderer
  - UI wählt sections_to_include, selected_charts_for_pdf, custom_section_order, uploads Images (b64), editiert Texte; sendet an Main via IPC; erhält PDF-Bytes und speichert.
- Assets
  - coords/*, pdf_templates_static/notext/* im app userData oder read-only in asar; Pfad-Resolver im Main.

---

## 7) Edge-Cases und Fehlerbilder

- Fehlendes ReportLab/PyPDF: Fallbacks aktiv (Plaintext oder Rückgabe erste PDF beim Merge).
- Leere/fehlerhafte Bilddaten: Bildplatzhalter mit Hinweistext; keine Eskalation.
- Unvollständige analysis_results: Validierung greift; KPIs nutzen na_text_key.
- Diagramm-Bytes fehlen/korrupt: Chart wird übersprungen bzw. mit Fehler-Placeholder gelistet.
- Sehr lange Texte/Anschreiben: KeepTogether verhindert harte Brüche; kann zu mehr Seiten führen.
- custom_section_order unvollständig: Rest wird in Standard-Reihenfolge ergänzt.
- Doppeltes MODULE_MAP im File: Prefer letztere Definition (enthält „wirtschaftlichkeitsanalyse“); an anderer Stelle aufräumen.

---

## 8) Tests und Backlog

- Unit-Tests (Python)
  - format_kpi_value: Zahlen, Strings (mit Komma/Punkt), NaN/Inf, Einheiten (%, Jahre)
  - _replace_placeholders: alle Platzhalter, Familen-/Firma-Fälle
  - `_prepare_cost_table_for_pdf`, `_prepare_simulation_table_for_pdf`: korrekte Reihenfolge/Formatierung, na_text
  - _overlay_footer_page_numbers: Seitennummern korrekt, keine Exceptions bei fehlenden Libs
- Integrationstests
  - generate_main_template_pdf_bytes mit/ohne additional_pdf
  - generate_offer_pdf_with_main_templates: skip_cover_and_letter, append_additional_pages_after_main6, Seitenzählung
  - generate_offer_pdf Legacy: jede Sektion, Charts-Auswahl (max 3/Seite), Custom Content, Attachments (wenn implementiert)
- Backlog/Verbesserungen
  - Fehlende Validierungs-/Fallback-Funktionen im File ergänzen oder auslagern und importieren
  - Doppeltes MODULE_MAP entfernen
  - page_layout_handler: Debug-Prints entfernen und Farben konsistent mit Theme nutzen
  - Konsolidierung: PDFGenerator Klasse vs. Legacy-Funktionen
  - Attachment-Logik fertig implementieren (am Dateiende abgeschnitten)

---

## 9) Kurze „How-To“

- Main-Flow empfehlen: generate_offer_pdf_with_main_templates(...)
- Für reine Legacy-Erstellung: generate_offer_pdf(..., disable_main_template_combiner=True)
- Für Modul-orientierte, einfache PDFs: PDFGenerator(create) mit module_order
- Stellen Sie sicher, dass coords/ und pdf_templates_static/notext/ vorhanden sind und Platzhalter per pdf_template_engine/placeholders.py gemappt werden.
