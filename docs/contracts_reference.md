# Contracts-Referenz (PV-App)

Ziel: Eine zentrale, kurze und verlässliche Übersicht aller wichtigen Datenverträge (Inputs/Outputs), Session-State-Keys und PDF-Pipeline-Schnittstellen – als Nachschlagewerk für Entwicklung und Migration (Electron + PrimeReact + TypeScript).

## 1) Kern-Datenstrukturen

### project_data (Dict)

- customer_data
  - `customer_name: str`
  - `customer_address: str`
  - `customer_email: str | None`
  - `customer_phone: str | None`
- project_details
  - `module_quantity: int`
  - `selected_module_name: str | None`
  - `selected_module_id: int | None`
  - `selected_module_capacity_w: float` (Wp je Modul)
  - `anlage_kwp: float` (berechnet)
  - `selected_inverter_name: str | None`
  - `selected_inverter_id: int | None`
  - `selected_inverter_quantity: int` (>= 1)
  - `selected_inverter_power_kw_single: float`
  - `selected_inverter_power_kw: float` (gesamt)
  - Storage (optional)
    - `include_storage: bool`
    - `selected_storage_name: str | None`
    - `selected_storage_id: int | None`
    - `selected_storage_storage_power_kw: float` (kWh gesamt)
  - Additional (optional; je nach Auswahl)
    - `selected_wallbox_name/id`, `selected_ems_name/id`, `selected_optimizer_name/id`, `selected_carport_name/id`, `selected_notstrom_name/id`, `selected_tierabwehr_name/id`
- economic_data
  - ggf. Zinsen, Strompreise, Förderungen etc. (variiert je Setup)
- Top-Level Convenience
  - `inverter_power_kw: float` (Duplikat der Gesamtleistung für Analysen)

### analysis_results (Dict)

- Allgemein/Meta
  - `calculation_errors: List[str]` – Referenz auf die im Lauf gesammelten Fehlermeldungen/Warnungen
  - `simulation_period_years_effective: int` – effektive Laufzeit der Simulation (Jahre)
  - `electricity_price_increase_rate_effective_percent: float` – angenommene jährliche Strompreissteigerung

- Preis-Matrix & Quellen
  - `price_matrix_source_type: 'Excel' | 'CSV' | 'Keine'` – Quelle der Preis-Matrix
  - `price_matrix_loaded_successfully: bool` – ob Matrix geladen/parbar ist
  - `pvgis_data_used: bool` – ob PVGIS-Daten genutzt wurden (sonst manuelle Berechnung)
  - `pvgis_source: str` – z. B. "PVGIS-TMY", "Manuelle Berechnung" oder "Keine Anlage"
  - `specific_annual_yield_kwh_per_kwp: float` – spezifischer Jahresertrag (kWh/kWp·a)

- Verbrauch und Strompreis (Istwerte für Jahr 1)
  - `total_consumption_kwh_yr: float` – Haushalts- + Heizstrom Jahresverbrauch (kWh)
  - `jahresstromverbrauch_fuer_hochrechnung_kwh: float` – Basisverbrauch für Kostenhochrechnung
  - `aktueller_strompreis_fuer_hochrechnung_euro_kwh: float` – aktueller €/kWh

- Ertrag & Verteilung (Jahr 1)
  - `annual_pv_production_kwh: float` – Jahresproduktion PV (kWh)
  - `monthly_productions_sim: float[12]` – monatliche Produktion (Jahr 1)
  - `monthly_consumption_sim: float[12]` – monatlicher Verbrauch (Jahr 1)
  - `monthly_direct_self_consumption_kwh: float[12]` – monatlicher Direktverbrauch aus PV
  - `monthly_storage_charge_kwh: float[12]` – geladene Energiemenge in den Speicher (netto)
  - `monthly_storage_discharge_for_sc_kwh: float[12]` – aus Speicher entladene Energiemenge für Eigenverbrauch
  - `monthly_feed_in_kwh: float[12]` – monatliche Netzeinspeisung (kWh)
  - `monthly_grid_bezug_kwh: float[12]` – monatlicher Netzbezug (kWh)
  - `eigenverbrauch_pro_jahr_kwh: float` – Jahres-Eigenverbrauch gesamt (Direkt + Speicher)
  - `netzeinspeisung_kwh: float` – Jahres-Netzeinspeisung gesamt (kWh)
  - `grid_bezug_kwh: float` – Jahres-Netzbezug (kWh)

- Einspeisevergütung (Jahr 1)
  - `einspeiseverguetung_ct_per_kwh: float` – ct/kWh
  - `einspeiseverguetung_eur_per_kwh: float` – €/kWh
  - `annual_feed_in_revenue_year1: float` – Einspeiseerlös Jahr 1 (€)
  - `tax_benefit_feed_in_year1: float` – optional steuerlicher Vorteil (gewerblich)

- Kosten & Investitionen (Netto, sofern nicht anders angegeben)
  - `base_matrix_price_netto: float` – Grundpreis aus Preis-Matrix (Pauschale)
  - `cost_modules_aufpreis_netto: float` – Modulkosten (Aufpreis, falls nicht in Matrix-Pauschale)
  - `cost_inverter_aufpreis_netto: float` – Wechselrichter-Aufpreis
  - `cost_storage_aufpreis_product_db_netto: float` – Speicher-Aufpreis aus Produkt-DB (wenn Matrix "Ohne Speicher" oder kein Matrixpreis)
  - `cost_accessories_aufpreis_netto: float` – Zubehörpauschale
  - `cost_misc_netto: float` – sonstige Pauschalen
  - `cost_scaffolding_netto: float` – Gerüstkosten (abh. Fläche/Höhe)
  - `cost_custom_netto: float` – manuelle Zusatzkosten
  - `total_optional_components_cost_netto: float` – Summe optionale Komponenten
  - `total_additional_costs_netto: float` – Summe aller Zusatzkosten (nicht in Matrix-Pauschale)
  - `subtotal_netto: float` – Zwischensumme netto (Matrix + Zusatzkosten)
  - `total_investment_netto: float` – Endinvest netto (abzgl. Bonus)
  - `vat_rate_percent: float` – MwSt.-Satz (%)
  - `total_investment_brutto: float` – Endinvest brutto

- Wartungskosten
  - `annual_maintenance_costs_eur_year1: float` – Wartung Jahr 1 (€)

- Simulation über Laufzeit
  - `annual_productions_sim: float[N]` – Jahresproduktion pro Jahr (mit Degradation)
  - `annual_benefits_sim: float[N]` – jährlicher Nutzen (Ersparnis + EEG + Steuer)
  - `annual_maintenance_costs_sim: float[N]` – Wartung je Jahr
  - `annual_cash_flows_sim: float[N]` – Cashflow je Jahr (ohne Jahr 0)
  - `cumulative_cash_flows_sim: float[N+1]` – kumulierte Cashflows inkl. Jahr 0 (Invest)
  - `annual_elec_prices_sim: float[N]` – angenommener Strompreis €/kWh je Jahr
  - `annual_feed_in_tariffs_sim: float[N]` – Einspeisetarife €/kWh je Jahr (EEG → Marktwert)
  - `annual_revenue_from_feed_in_sim: float[N]` – jährliche Einspeiseerlöse (€)

- KPIs/Wirtschaftlichkeit
  - `annual_electricity_cost_savings_self_consumption_year1: float` – Ersparnis Jahr 1 aus Eigenverbrauch (€)
  - `annual_financial_benefit_year1: float` – Gesamtnutzen Jahr 1 (€)
  - `amortization_time_years: float` – Amortisationszeit (Jahre); ggf. Cheat angewendet
  - `amortization_time_years_original: float` – optional, Originalwert vor Cheat
  - `npv_value: float` – Nettobarwert (bei Diskontsatz = loan_interest_rate)
  - `npv_per_kwp: float` – NPV pro kWp
  - `irr_percent: float` – interner Zinsfuß (%)
  - `lcoe_euro_per_kwh: float` – Stromgestehungskosten €/kWh (diskontiert)
  - `effektiver_pv_strompreis_ct_kwh: float` – LCOE in ct/kWh
  - `simple_roi_percent: float` – einfacher ROI Jahr 1 (%)
  - `performance_ratio_percent: float` – PR (%)
  - `afa_linear_pa_eur: float` – lineare AfA (€/Jahr)
  - `restwert_anlage_eur_nach_laufzeit: float` – Restwert nach Simulationsdauer (€)
  - `eigenkapitalrendite_roe_pct: float` – Eigenkapitalrendite (hier ~ IRR)
  - `alternativanlage_kapitalwert_eur: float` – Vergleichswert Alternativanlage

- CO2/Umwelt
  - `annual_co2_savings_kg: float` – CO2-Einsparung Jahr 1 (kg)
  - `co2_equivalent_trees_per_year: float` – Bäume/Jahr (Äquivalent)
  - `co2_equivalent_car_km_per_year: float` – Pkw-km/Jahr (Äquivalent)
  - `co2_equivalent_flights_muc_pmi_per_year: float` – Flüge MUC–PMI/Jahr (Äquivalent)
  - `co2_avoidance_cost_euro_per_tonne: float` – Vermeidungskosten €/t CO2

- Zukunftsgeräte (optional)
  - `eauto_ladung_durch_pv_kwh: float` – PV-Anteil am EV-Laden (kWh/Jahr)
  - `pv_deckungsgrad_wp_pct: float` – PV-Deckungsgrad für Wärmepumpe (%)

- Chart-Bytes (für PDF-Einbau; PNG)
  - `yearly_production_chart_bytes: bytes | None`
  - `break_even_chart_bytes: bytes | None`
  - `amortisation_chart_bytes: bytes | None`
  - `co2_savings_chart_bytes: bytes | None`

- Fallback-Preise
  - `final_price: float | None` – UI-Livepreis oder aus `total_investment_*` abgeleitet

### company_info (Dict)

- `id: int | str`
- `name: str`
- `address: str | None`
- `logo_base64: str | None`
- Weitere Felder je nach DB (Telefon, E-Mail, Bankverbindung etc.)

### product_db (Minimalfelder je Kategorie)

- Modul: `id, model_name, capacity_w`
- Wechselrichter: `id, model_name, power_kw`
- Speicher: `id, model_name, storage_power_kw`
- Weitere: `model_name` + sinnvolle Basisattribute für Darstellung/Preislogik

## 2) Wichtige Session-State-Keys

- Live-Pricing
  - `live_pricing_calculations = { base_cost: float, total_rabatte_nachlaesse: float, total_aufpreise_zuschlaege: float, final_price: float }`
- PDF-Konfiguration (doc_output/pdf_ui)
  - `pdf_selected_main_sections: List[str]` (Reihenfolge der Hauptkapitel)
  - `pdf_inclusion_options: Dict`
    - Flags: `include_company_logo`, `include_product_images`, `all_documents`, `append_additional_pages_after_main6`
    - Listen: `company_document_ids_to_include: List[int]`, `selected_charts_for_pdf: List[str]`
  - `pdf_design_config: Dict` (Design-/Layout-Optionen klassisch)
  - `chart_config: Dict` (Diagramm-Auswahl/Parameter UI-seitig)
  - `financing_config: Dict` (Szenarien/Parameter für Finanzvergleiche)
  - `generated_pdf_bytes_for_download_v1: bytes | None`
- PDF Themes/Visuals (pdf_styles)
  - `pdf_theme_settings = { selected_theme: str, chart_customizations: Dict, layout_customizations: Dict, effects: Dict }`
  - `custom_themes: Dict[str, ThemeDef]`
- PDF Struktur/Content (pdf_widgets)
  - `pdf_section_order: List[str]`
  - `pdf_section_contents: Dict[str, List[{ id: str, type: 'text'|'image'|'pdf'|'table'|'chart', data: Any }]>`
  - `pdf_custom_sections: Dict[str, { name: str, icon: str, content_types: List[str], created: ISODate }]>`
- Erweiterte Analysen
  - `advanced_calculation_results: Dict` – konsolidierte KPIs und Detailfelder für Advanced-Abschnitte (siehe unten)
- Wärmepumpe (heatpump_ui)
  - `building_data: Dict` – Ergebnisse der Gebäudeanalyse/Heizlast
  - `heatpump_data: Dict` – ausgewählte Wärmepumpe + Optionen
  - `economics_data: Dict` – Wirtschaftlichkeit (WP vs. Altanlage)
  - `integration_data: Dict` – PV-Integration (Deckung/Optimierung)

## 3) PDF-Pipeline – Generator-Vertrag

Eingabe an `pdf_generator.generate_offer_pdf_with_main_templates` (vereinheitlicht):

- `project_data: Dict` (siehe oben)
- `analysis_results: Dict` (inkl. `*_chart_bytes`)
- `company_info: Dict`
- `sections_to_include: List[str]` (z. B. Deckblatt, Projektübersicht, Komponenten, Kosten, Wirtschaftlichkeit …)
- `inclusion_options: Dict` (Logos, Produktbilder, Firmendokumente, Charts, Append-Optionen)
- `texts: Dict[str, str]` (Lokalisierung)
- optional: Theme/Stylesheet (aus `pdf_styles` abgeleitet) bzw. `pdf_theme_settings`

Ausgabe:

- `bytes` (PDF)

Fehler-/Fallback-Politik:

- Validierung (`_validate_pdf_data_availability`) füllt fehlende `final_price`/Firmendaten, warnt bei fehlenden KPIs, nutzt Defaults.
- Falls Charts fehlen (`*_chart_bytes = None`), sollte der Generator Platzhalter/Überspringen unterstützen.

## 4) Visuals/Charts – Contracts

- Renderer: `pv_visuals.py` erzeugt Plotly 3D-Figuren und speichert PNG-Bytes in `analysis_results`:
  - `yearly_production_chart_bytes`, `break_even_chart_bytes`, `amortisation_chart_bytes`, `co2_savings_chart_bytes`
- Export benötigt `kaleido`; bei Fehler → `None` (Generator muss robust sein).

## 5) Themes/Styles – Contracts

- Farbpalette `get_color_palette()` liefert `Dict[str, Color]` mit Keys:
  - `primary, secondary, text, separator, white, black, grey, darkgrey`
- ParagraphStyles (ReportLab) – Beispiele (Name → Zweck):
  - `OfferMainTitle`, `SectionTitle`, `SubSectionTitle`, `TableText/Number/Header`, `ImageCaption` …
- TableStyles: `get_base_table_style`, `get_data_table_style`, `get_product_table_style`, `get_main_product_table_style`
- Theme-Manager (UI):
  - `pdf_theme_settings.selected_theme`
  - `chart_customizations`: `grid, grid_alpha, line_width, marker_size, shadow, gradient`
  - `layout_customizations`: `margin_*`, `header_height`, `footer_height`, `section_spacing`, `element_spacing`
  - `effects`: `watermark, page_numbers, header_line, footer_line, section_borders, highlight_important, use_icons, rounded_corners` (+ ggf. `watermark_settings`)

## 6) Finanz-APIs (financial_tools)

- `calculate_annuity(principal, apr, years)` → `{ monatliche_rate, gesamtzinsen, gesamtkosten, effective_rate, tilgungsplan[], laufzeit_monate }`
- `calculate_leasing_costs(total_investment, leasing_factor, duration_months, residual_value_percent)` → Kosten/Restwert/Effektivkosten
- `calculate_depreciation(initial_value, useful_life_years, method='linear')` → lineare Abschreibung + Plan
- `calculate_financing_comparison(investment, apr, years, leasing_factor)` → `{ kredit, leasing, cash_kauf, empfehlung }`
- `calculate_capital_gains_tax(profit, tax_rate)` → Steuer/Netto
- `calculate_contracting_costs(base_fee, consumption_price, consumed_kwh, period_years)` → Periodenkosten/Effektivpreis

## 7) Edge/Fallback-Checkliste

- `final_price` nicht gesetzt → aus `live_pricing_calculations` oder `total_investment_*` ableiten.
- Firmendaten fehlen → `company_info` in `project_data.company_information` injizieren.
- Charts `None` → Generator überspringt/platzhaltert.
- Plotly/Kaleido/Fonts/Headless → Laufzeitumgebung prüfen.
- DnD-Paket fehlt → `pdf_widgets` nutzt Button-Fallback.

## 8) Pipeline-Diagramm

```mermaid
flowchart LR
  A[UI: analysis/pdf_ui/doc_output] --> B[Consolidation: project_data + analysis_results + company_info + sections + inclusion_options + theme]
  B --> C[Validation: _validate_pdf_data_availability + Fallback-Fills]
  C --> D[PDF Generator: generate_offer_pdf_with_main_templates]
  D --> E[PDF Bytes]
  E --> F[Preview: pdf_preview (PyMuPDF → PNG)]
  E --> G[Download Button]
```

## 9) Beispiel – Generator-Call (Pseudo)

```json
{
  "project_data": { "customer_data": {"customer_name": "Max Mustermann"}, "project_details": {"anlage_kwp": 9.86, "module_quantity": 22} },
  "analysis_results": { "total_investment_netto": 18750.0, "annual_pv_production_kwh": 9800, "yearly_production_chart_bytes": "<base64>" },
  "company_info": { "name": "Solar GmbH", "logo_base64": "<base64>" },
  "sections_to_include": ["cover_page", "project_overview", "technical_components", "cost_details", "economics"],
  "inclusion_options": { "include_company_logo": true, "selected_charts_for_pdf": ["yearly_production_chart_bytes", "break_even_chart_bytes"] },
  "texts": { "offer_title": "Ihr PV-Angebot" },
  "theme": { "selected_theme": "modern_blue" }
}
```

## 10) Migrationstipps (TS)

- Contracts als TS-Interfaces pflegen (zod-Validation), JSON-Persistence im `userData`.
- Chart-Bytes serverseitig generieren (node-kaleido) → als `ArrayBuffer` einbetten.
- PDF-Stack (pdf-lib/pdfmake) mit zweiphasigem Seitenzähler (optional).
- Preview mit `pdf.js`; DnD via `dnd-kit`.

## 11) Erweiterte Berechnungen – Contracts (calculations_extended)

Quelle: `calculations_extended.py` und Advanced-Bereiche in `analysis.py`.

- Sammler-Funktion: `run_all_extended_analyses(offer_data) -> Dict[str, Any]`
  - Erwartete Inputs (offer_data):
    - `total_investment: float`, `annual_savings: float`, `annual_production_kwh: float`, `pv_size_kwp: float`, optional `total_embodied_energy_kwh: float`
  - Ergebnisse (Keys, Einheiten):
    - `dynamic_payback_3_percent: float (Jahre)`
    - `dynamic_payback_5_percent: float (Jahre)`
    - `net_present_value: float (€)`
    - `internal_rate_of_return: float (%)`
    - `profitability_index: float (ratio)`
    - `lcoe: float` – in ct/kWh gemäß Implementierung; Mapping zum PDF: `lcoe_euro_per_kwh = lcoe/100`
    - `co2_avoidance_per_year_tons: float (t/a)`
    - `energy_payback_time: float (Jahre)`
    - `co2_payback_time: float (Jahre)`
    - `total_roi_percent: float (%)`
    - `annual_equity_return_percent: float (%)`
    - `profit_after_10_years: float (€)`
    - `profit_after_20_years: float (€)`

Hinweise/Konventionen:

- In derselben Datei existieren doppelte `calculate_lcoe`-Definitionen (€/kWh vs. ct/kWh). Für Konsistenz in den Verträgen bevorzugen wir: `lcoe_euro_per_kwh` in `analysis_results` und konvertieren ggf. aus ct/kWh.
- Advanced-UI nutzt zusätzlich Integrator-Funktionen (in `calculations.py: AdvancedCalculationsIntegrator`) mit Ergebnisfeldern:
  - `calculate_lcoe_advanced` → `{ lcoe_simple: €/kWh, lcoe_discounted: €/kWh, yearly_lcoe: number[], grid_comparison: ratio, savings_potential: €/kWh }`
  - `calculate_npv_sensitivity(calc_results, rate:number)` → `npv:number`
  - `calculate_irr_advanced(calc_results)` → `{ irr: %, mirr: %, profitability_index: number }`
  - Weitere (CO2/Temperatur/WR/Recycling/Optimierung) liefern strukturierte Dicts; Ergebnisse werden UI-seitig dargestellt und optional in `advanced_calculation_results` persistiert.

Empfohlene TS-Interfaces (Auszug):

- `ExtendedAnalysesResult` mit obigen Keys; `LcoeAdvancedResult` wie Integrator; ggf. kombinierter Typ für `advanced_calculation_results`.

## 12) Wärmepumpen-Analyse – Contracts (heatpump_ui/calculations_heatpump)

Quelle: `heatpump_ui.py`, `calculations_heatpump.py`.

- building_data (Session):
  - Grunddaten: `area:number`, `type:string`, `year:string`, `insulation:string`, `heating_system:string`, `hot_water:string`
  - Verbrauch: `consumption_inputs = { oil_l:number, gas_kwh:number, wood_ster:number, heating_hours:number, system_efficiency_pct:number }`
  - Parameter: `desired_temp:number`, `heating_days:number`, `outside_temp:number`, `system_temp:string`
  - Ergebnisse: `heat_load_kw:number`, `heat_load_source:'verbrauchsbasiert'|'gebäudedaten'`, `calculated_at: datetime`

- heatpump_data (Session):
  - `selected_heatpump: { manufacturer, model, type, heating_power:number, cop:number, scop:number, price:number, ... }`
  - `alternatives: List<...>` (weitere Geräte)
  - Optionen: `sizing_factor:number`, `hot_water_storage:number`, `backup_heating:boolean`, `smart_control:boolean`
  - `building_data: building_data`

- economics_data (Session, UI-Version):
  - `total_investment:number`, `annual_savings:number`, `payback_time:number|inf`,
  - `hp_electricity_consumption:number`, `annual_hp_cost:number`, `annual_old_cost:number`,
  - `heat_demand_kwh:number`, `electricity_price:number`, `subsidy_amount:number`

- integration_data (Session):
  - `pv_coverage_hp:number` (0..1), `annual_pv_savings_hp:number`, `total_annual_savings:number`,
  - `smart_control_enabled:boolean`, `thermal_storage_size:number`

- calculations_heatpump.calculate_heatpump_economics(...) (Service-Rückgabe):
  - `{ heating_demand_kwh, electricity_consumption_kwh, annual_electricity_cost, annual_alternative_cost, annual_savings, payback_period_years|null, total_savings_20y, investment_cost, cop, recommendation }`

TS-Mapping-Hinweise:

- UI-eigene `economics_data` unterscheidet sich leicht von der Service-Funktion; bei einer TS-Portierung entweder eine vereinheitlichte Struktur definieren oder beide Varianten unterstützen und beim Speichern konvertieren.
- Für PV-Integration werden PV-KPIs aus `analysis_results` benötigt: `annual_pv_production_kwh`, `anlage_kwp`.
