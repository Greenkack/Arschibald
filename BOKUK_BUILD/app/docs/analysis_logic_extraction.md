# Analysis-Modul – Logik-Extraktion und Migrations-Mapping

Diese Datei extrahiert die vollständige Logik aus `analysis.py` und bereitet die Migration in eine Electron + PrimeReact App vor. Sie dient als Referenz für Datenflüsse, UI-Verhalten, Funktionsverträge, Export-Artefakte und TypeScript/Electron-Service-Schnittstellen.

## Überblick

Das Modul `analysis.py` ist das zentrale Analyse- und Dashboard-Modul der App und übernimmt:

- Rendering der Analyse-UI (Tabs für Übersicht, Wirtschaftlichkeit, Energie, Technik, Umwelt, Finanzierung und „Erweiterte Analysen“)
- Live-Pricing-Änderungen (Rabatte/Nachlässe, Aufpreise/Zuschläge, Sonderkosten) inkl. Einfluss auf den Endpreis und Re-Calculations
- Universal-Chart-Engine (Plotly) mit Theme/Color-Paletten, Chart-Typ-Switcher und Export zu Bildbytes für den PDF-Generator
- Integration erweiterter Berechnungen (LCOE, NPV/IRR, Energieflüsse, Temperatur/WR, Verschattung, Recycling, Optimierungen)
- Finanzierungsanalyse (Annuitätendarlehen, Leasing, Contracting) inklusive Tabellen, Sensitivitäten und ROI-Vergleichen
- Vorbereitung aller relevanten Chart-/Daten-Artefakte für den PDF-Export

## UI-Struktur und Hauptdatenflüsse

- Seitenleiste/Controls:

  - Simulationsdauer (Jahre), Strompreissteigerung (%/a), optionale Modern-Toggle
  - „Neu berechnen“-Trigger: ruft die Kernkalkulationen (perform_calculations) erneut auf
- Haupt-Tabs:

  - Übersicht/Ökonomie/Energie/Technik/Umwelt/Finanzierung/Erweiterte Analysen
  - Je Tab mehrere „render_*_switcher“-Sektionen, die einen Chart-Typ und Farbpalette wählen lassen und Plotly-Figuren generieren
- Pricing-Modifikationen-UI:

  - Rabatte/Nachlässe, Aufpreise/Zuschläge, Sonderkosten
  - Live-KPIs: base_cost, total_rabatte_nachlaesse, total_aufpreise_zuschlaege, final_price
  - Ergebnisse werden in `st.session_state["live_pricing_calculations"]` persistiert
- Rechenkerne/Abhängigkeiten:

  - `calculations.perform_calculations(project_data, ...)`
  - Admin-Settings via `database.load_admin_setting`
  - Finanzfunktionen aus `financial_tools.py`

### Wichtige Session-State-Keys

- `project_data`: Eingabedaten des Projekts (Adresse, Produkte, Parameter)
- `calculation_results`: Ergebnisse aus `perform_calculations`
- `live_pricing_calculations`: { base_cost, total_rabatte_nachlaesse, total_aufpreise_zuschlaege, final_price }
- `universal_charts`/`chart_bytes`: in der Analyse erzeugte Plotly-Charts als Bytes für PDFs
- `financing_schedules`: Tilgungs-/Leasingpläne und Visualisierungen
- `financing_scenarios`: Zinssensitivitäten inkl. Balkendiagramme/Tabelle
- `financing_roi_analysis`: ROI-/Cashflow-Vergleiche als Diagramme/Daten
- `advanced_calculation_results`: Ergebnisse der Advanced-Analysen und zusammengefasste KPIs

## Diagramm-Engine (Plotly)

Zentrale Bausteine:

- `create_universal_2d_chart(series, x, y, chart_type, palette, title, ...)`
- `create_multi_series_2d_chart(series_list, ...)`
- `_create_chart_by_type(type, data)`: Linien, Balken, gestapelte Flächen/Balken, Scatter
- `_apply_shadcn_like_theme(fig)`, `_apply_custom_style_to_fig(fig)`: Theme/Styles
- `_export_plotly_fig_to_bytes(fig, texts)`: Export als PNG-Bytes für PDF

Chart-Switcher (Auszug):

- Produktion: täglich/wöchentlich/jährlich
- Produktion vs. Verbrauch (inkl. Pie-Hilfen: Deckung, PV-Nutzung)
- Speicher-Effekte, Autarkie-/Eigenverbrauchs-Stacks
- Kostenentwicklung, Tarifvergleiche, ROI-/Szenario-Vergleiche
- Einnahmeprojektion, kumulierte Cashflows, Stromkostenprojektion

Inputs/Outputs (Kontrakt, gekürzt):

- Input: `calculation_results` mit Keys wie
  - `annual_pv_production_kwh`, `annual_consumption_kwh`, `anlage_kwp`
  - `annual_total_savings_euro`, `annual_financial_benefit_year1`
  - `performance_ratio_percent`, `battery_capacity_kwh`, ...
- Output: Plotly-Figuren und PNG-Bytes; Speicherung unter Session-State für PDF

Fehlerinvarianten: Fehlende Keys werden robust behandelt (Fallbacks/0), UI zeigt Hinweise statt Exceptions.

### Vollständiger Funktionskatalog (Aus `analysis.py`)

- Entry-Points
  - `render_analysis` (klassisch) und „moderne“ Variante (zweite Definition)
  - `render_pricing_modifications_ui` (2 Varianten)
- Chart Core
  - `create_universal_2d_chart`, `create_multi_series_2d_chart`, `_create_chart_by_type`, `_apply_shadcn_like_theme`, `_apply_custom_style_to_fig`, `_export_plotly_fig_to_bytes`
- Chart Switcher (Renderer)
  - `render_daily_production_switcher`, `render_weekly_production_switcher`, `render_yearly_production_switcher`
  - `render_production_vs_consumption_switcher`, `render_selfuse_stack_switcher`, `render_selfuse_ratio_switcher`
  - `render_storage_effect_switcher`, `render_cost_growth_switcher`, `render_roi_comparison_switcher`
  - `render_scenario_comparison_switcher`, `render_tariff_comparison_switcher`, `render_tariff_cube_switcher`
  - `render_income_projection_switcher`, `render_co2_savings_value_switcher` (2 Varianten)
  - Pie-Helpers: `_create_coverage_pie_chart`, `_create_pv_usage_pie_chart`
- Advanced/Erweitert
  - `integrate_advanced_calculations`, `render_extended_calculations_dashboard`
  - `render_advanced_calculations_section`, `render_advanced_financial_analysis`, `render_advanced_energy_analysis`, `render_advanced_environmental_analysis`, `render_advanced_technical_analysis`, `render_advanced_comparison_analysis`
  - `prepare_advanced_calculations_for_pdf_export`
- Finanzierung
  - `render_financing_analysis` (inkl. Tilgungs-/Leasingplänen, Zinssensitivität, ROI, Steuer)
  - `prepare_financing_data_for_pdf_export`, `get_financing_data_summary`
- Utilities
  - `format_kpi_value`, `get_text`, `load_viz_settings`/`_get_visualization_settings`, `get_pricing_modifications_data`

Hinweis: Optional importierte Modern-/Enhancement-Module (z. B. `enhanced_analysis_charts`, `modern_dashboard_ui`) werden bei Abwesenheit über Fallback-Pfade abgefangen.

## Erweiterte Berechnungen und Abschnitte

AdvancedCalculationsIntegrator (verwendet über `st.session_state.calculations_integrator`):

- `calculate_lcoe_advanced(params)` → LCOE (diskontiert/undiskontiert)
- `calculate_npv_sensitivity(calc_results, rate)`
- `calculate_irr_advanced(calc_results)`
- `calculate_detailed_co2_analysis(calc_results)`
- `calculate_temperature_effects(calc_results, project_data)`
- `calculate_inverter_efficiency(calc_results, project_data)`
- `calculate_recycling_potential(calc_results, project_data)`
- `generate_optimization_suggestions(calc_results, project_data)`

Haupt-Renderer:

- `render_advanced_calculations_section(project_data, calc_results, texts)`
  - Tabs: Finanzanalyse, Energieoptimierung, Umwelt-Impact, Technische Details, Vergleichsanalysen
- `render_advanced_financial_analysis(results, texts)`
  - ROI (20J), NPV (20J, 4%), einfache IRR-Schätzung, Cashflow-/Kumulativ-Chart
- `render_advanced_energy_analysis(results, texts)`
  - Deckungsgrad, spez. Ertrag, PR, Kapazitätsfaktor; Monatsbilanz (Balken)
- `render_advanced_environmental_analysis(results, texts)`
  - CO2-Metriken (Jahr/20J, Bäume, Auto-km), CO2-Zeitreihe (Füllkurve)
- `render_advanced_technical_analysis(results, texts)`
  - System- und Energie-Parameter, vereinfachte Degradationsanalyse (Tabelle)
- `render_advanced_comparison_analysis(results, texts)`
  - Szenario-Vergleich (pess./real./opt.), Benchmark ggü. Regionen

PDF-Export-Vorbereitung:

- `prepare_advanced_calculations_for_pdf_export(calc_results, project_data, texts)`
  - LCOE, NPV@4%, IRR, CO2, Temperatur, WR-Wirkungsgrad, Recycling, Optimierungen
  - `extended_summary` mit konsolidierten KPIs
  - Speicherung unter `st.session_state["advanced_calculation_results"]`

### Detaillierte Kontrakte (Inputs/Outputs/Side-Effects)

- `render_pricing_modifications_ui(project_data, results, texts)`
  - Inputs: `results.total_investment_netto/brutto` (Basis), Texte, ggf. Session-State-Vorbelegung
  - Outputs: aktualisierte `st.session_state["live_pricing_calculations"]` mit `base_cost`, `total_rabatte_nachlaesse`, `total_aufpreise_zuschlaege`, `final_price`
  - Side-Effects: UI-Interaktionen (Slider/Inputs), Recalc-Trigger-Flag setzen
- `create_universal_2d_chart(series, ...)`
  - Inputs: `pandas.DataFrame`/Liste, X/Y-Spaltennamen, Typ, Palette, Titel
  - Outputs: Plotly-Figur; optional Speicherung als Bytes über `_export_plotly_fig_to_bytes`
  - Fehler: Leere Daten → Hinweis statt Exception; falsche Spaltennamen → defensive Checks
- `render_*_switcher(results, texts)`
  - Inputs: benötigte KPI-Keys je Switcher (siehe Matrix unten)
  - Outputs: Anzeige Plotly-Chart; optional Bytes im Session-State für PDF
  - Fehler: Fehlende Keys → Fallback 0/Warnungen; Charts werden übersprungen
- `prepare_advanced_calculations_for_pdf_export(calc_results, project_data, texts)`
  - Inputs: Ergebnisse/Projekt; Verfügbarkeit Integrator-Methoden
  - Outputs: `advanced_calculation_results` inkl. `extended_summary`
  - Fehler: Einzelmethoden im Try/Except; Warnungen statt Abbruch
- `render_financing_analysis(results, texts)`
  - Inputs: Finanzierungssumme, Zinssatz, Laufzeit, Leasingfaktor, PV-Erträge
  - Outputs: Tilgungs-/Leasingtabellen, Zinssensitivitäts-Charts, ROI-/Cashflow-Charts, Steuer-Metriken; Speicherung unter `financing_*`
  - Fehler: Negative/Nullwerte → Abfangen; Tabellen robust; Szenario-Listen nur bei gültigen Daten

### Switcher → Datenbedarf (Kurz-Matrix)

- Daily/Weekly/Yearly Production: `annual_pv_production_kwh`, ggf. synthetische Profile oder vorhandene Zeitreihen
- Production vs Consumption: `annual_pv_production_kwh`, `annual_consumption_kwh`
- Selfuse Stack/Ratio: `eigenverbrauch_pro_jahr_kwh`, `self_supply_rate_percent`
- Storage Effect: `battery_capacity_kwh`, `netzbezug_kwh`/`grid_bezug_kwh`
- Cost Growth: `strompreis_aktuell_eur_kwh`, `preisanstieg_prozent` oder UI-Einstellung
- ROI Comparison/Scenario: `annual_total_savings_euro`, `total_investment_netto`
- Tariff Comparison/Cube: Tarifparameter aus Admin-Settings, `annual_consumption_kwh`
- Income Projection: `annual_financial_benefit_year1`, Eskalationsannahmen
- CO2 Savings: `co2_savings_kg_per_year` oder Proxy über Produktion

### State- und Event-Flows

- Recalc-Trigger: Sidebar-Button setzt Flag → `perform_calculations` wird neu aufgerufen → `calculation_results` aktualisiert → Chart-Sektionen rerendern
- Pricing-Änderungen: Änderungen in Pricing-UI → `live_pricing_calculations` neu berechnet → `final_price` in PDF-Pipeline verwendet (Fallbacks, siehe Copilot-Anweisungen)
- PDF-Export: Beim Rendern Charts als Bytes exportieren und in `session_state` sammeln; `pdf_generator` konsumiert diese Artefakte

### Edge-Cases & Fehlerbilder

- Fehlende Admin-Settings/Preis-Matrix → Preisberechnung fallbackt; UI meldet Hinweis
- Doppelzählungen Speicher-Aufpreis: Gegenprüfen zu Produkt-DB (siehe Projektbesonderheiten)
- Projekte ohne Speicher: Switcher „Speicher-Effekt“ blendet sich aus/zeigt Nullreihen
- Sehr kleine Anlagengröße (`anlage_kwp` ≈ 0): Spezifischer Ertrag/Kapazitätsfaktor → 0 statt Division durch 0
- Negative/Null Finanzierungseingaben: Tabellen nicht rendern; Info-Hinweis
- PNG-Export in headless-Umgebungen: Fallbacks oder Renderer-seitige Exporte vorsehen

### Performance-Hinweise

- Plotly: Figure-Objekte wiederverwenden, Daten ggf. aggregieren; PNG-Export asynchron machen
- Große Tabellen (Tilgungspläne > 30 Jahre): Pagination/Virtualisierung in UI
- Advanced-Berechnungen: Feature-Flags, Lazy-Ausführung; Ergebnisse cachen (`session_state`)

### Testing-/Verifikationshinweise

- Vertrags-Tests für `CalculationResults`-Schlüssel (Smoke-Tests)
- Snapshot-Tests für Chart-Spezifikationen (Determinismus sichern)
- Finanzierungsfunktionen: Unit-Tests für Annuität/Leasing/AfA mit Randfällen
- PDF-Export: Tests gegen leere/inkonsistente `session_state`-Artefakte

### Migrations-Backlog (gezielte Aufgaben)

- [ ] Dedupliziere `render_analysis` und `render_pricing_modifications_ui`
- [ ] Extrahiere Universal-Chart-API (TS) und vereinheitliche Paletten/Theme
- [ ] Implementiere `FinancingService` inkl. Schedules und Sensitivitäten
- [ ] Mappe `AdvancedAnalyticsService`-Methoden (Stub → Implementierung)
- [ ] Verdrahte PDF-Export-Artefakte (Bytes + `extended_summary`) in neue Pipeline

### IPC-Beispielverträge (TypeScript)

- `calc/run` (Renderer → Main)
  - Input: `{ project: ProjectData, opts?: CalcOptions }`
  - Output: `CalculationResults`
- `pricing/apply`
  - Input: `{ base: number, mods: PricingMods }`
  - Output: `LivePricing`
- `chart/export`
  - Input: `{ fig: PlotlySpec, theme?: ChartTheme, width?: number, height?: number }`
  - Output: `{ bytes: Uint8Array, contentType: 'image/png' }`
- `financing/annuity`
  - Input: `{ principal: number, rate: number, years: number }`
  - Output: `{ monatliche_rate: number, gesamtkosten: number, gesamtzinsen: number, plan: FinancingScheduleRow[] }`

## Financing/Finanzierung

Verwendete Funktionen aus `financial_tools.py`:

- `calculate_annuity(principal, rate, years)` → monatliche Rate, Gesamtkosten/-zinsen, Tilgungsplan
- `calculate_leasing_costs(amount, factor, years)` → monatliche Rate, effektive Kosten
- `calculate_depreciation(amount, years, method)` → jährliche Abschreibung, Steuerersparnis (30%)
- `calculate_financing_comparison(amount, credit_rate, years, leasing_factor)` → Gegenüberstellung + Empfehlung
- `calculate_capital_gains_tax(amount, tax_rate)`; `calculate_contracting_costs(...)` (falls verwendet)

Sichtbare Abschnitte:

- Tilgungs-/Leasingpläne mit Tabellen und Plotly-Visualisierung
- Zinssensitivität: Basiszins ± Variation, Balken für Rate/Gesamtkosten, Tabelle
- ROI-Vergleich: Barkauf vs. Kredit vs. Leasing (ROI%, Nettonutzen, kumulierter Cashflow)
- Steuerliche Aspekte: AfA linear (20J), KESt auf Erträge
- Rentabilitätsvergleich mit/ohne Finanzierung auf 20 Jahre (vereinfachte Darstellung)

Session-State für PDF:

- `financing_schedules` → Tabellen/Bytes
- `financing_scenarios` → Rates-/Costs-Chart-Bytes, Szenario-Tabelle
- `financing_roi_analysis` → ROI- und Cashflow-Chart-Bytes, ROI-Tabelle

## Doppelte Definitionen / Konsolidierung (für Migration)

In `analysis.py` existieren teils doppelte Varianten:

- `render_analysis` (klassisch vs. „modern“)
- `render_pricing_modifications_ui` (zwei Implementierungen, ähnliche Felder)
- `render_co2_savings_value_switcher` (zwei Varianten)

Migrationsvorschlag:

- Einen einzigen, modularen `renderAnalysis`-Container in React mit Feature-Flags für „modern“
- Eine konsolidierte Pricing-UI-Komponente mit einheitlichem State und Rechenlogik
- CO2-Switcher vereinheitlichen, Charts über generische Chart-Komponente steuern

## TypeScript/Electron: Services, IPC und Datamodelle

Ziel ist die Trennung in Services (Electron Main) und UI (PrimeReact im Renderer) mit klaren IPC-Verträgen.

Empfohlene Services (Electron Main):

- CalculationsService
  - Methoden: `performCalculations(project: ProjectData, opts?: CalcOptions): CalculationResults`
  - Optional: `prepareAdvancedForPdf(calc: CalculationResults, project: ProjectData): AdvancedExport`
- PricingService
  - Methoden: `applyPricingModifiers(base: number, mods: PricingMods): LivePricing`
  - Persistiert Benutzeranpassungen (pro Projekt) in DB/JSON
- ChartService
  - Methoden: `exportPlotlyToPng(figSpec: PlotlySpec, theme?: ChartTheme): Uint8Array`
  - Alternativ: Renderer-seitig exportieren und Bytes an Main senden
- FinancingService
  - Methoden: `calculateAnnuity(...)`, `calculateLeasing(...)`, `calculateDepreciation(...)`, `compareFinancing(...)`, `calculateTax(...)`
- AdvancedAnalyticsService
  - Methoden: `calculateLcoeAdvanced(...)`, `npvSensitivity(...)`, `irrAdvanced(...)`, `co2Detailed(...)`, `tempEffects(...)`, `inverterEfficiency(...)`, `recyclingPotential(...)`, `optimizationSuggestions(...)`

IPC-Kanäle (Vorschlag):

- `calc/run`, `calc/prepareAdvanced`
- `pricing/apply`
- `chart/export`
- `financing/annuity`, `financing/leasing`, `financing/depreciation`, `financing/compare`, `financing/tax`
- `advanced/lcoe`, `advanced/npv`, `advanced/irr`, `advanced/co2`, `advanced/temp`, `advanced/inverter`, `advanced/recycling`, `advanced/optimize`

TypeScript-Interfaces (Auszug):

- `ProjectData`: Adresse, Produkte, Anlagendaten, Tarife, Kundentyp, MwSt-Satz, etc.
- `CalculationResults`:
  - Preise/Kosten: `base_matrix_price_netto`, `total_additional_costs_netto`, `total_investment_netto/brutto`
  - Energie/KPIs: `anlage_kwp`, `annual_pv_production_kwh`, `annual_consumption_kwh`, `performance_ratio_percent`, ...
  - Wirtschaftlichkeit: Cashflows/NPV/IRR (falls verfügbar)
- `PricingMods`: `{ rabatte: Mod[], aufpreise: Mod[], sonderkosten: Mod[] }`
- `LivePricing`: `{ base_cost: number; total_rabatte_nachlaesse: number; total_aufpreise_zuschlaege: number; final_price: number }`
- `FinancingScheduleRow`: `{ jahr: number; rate: number; zins: number; tilgung: number; restschuld: number }`
- `AdvancedExport`: `{ lcoe_analysis?: LcoeResult; irr_analysis?: IrrResult; co2_analysis?: Co2Result; temperature_effects?: any; inverter_efficiency?: any; recycling_analysis?: any; optimization_suggestions?: any; extended_summary: ExtendedSummary }`

Fehler-/Edge-Handling:

- Null-/Fehlende Werte defensiv behandeln; Fallbacks verwenden (z. B. 0 oder konservative Defaults)
- Große Datenmengen: Chart-Downsampling optional, Export asynchron
- Rechte/Assets: PDF-/Bildpfade prüfen, fehlende Assets überspringen

## PDF-Export-Artefakte aus der Analyse

- Allgemein: Alle relevanten Diagramme werden zusätzlich als PNG-Bytes exportiert und im Session-State gesammelt (z. B. `chart_bytes`, `financing_*`, `advanced_calculation_results`).
- Der PDF-Generator konsumiert daraus Deckblatt-/KPI-Zahlen, Charts (Produktion, Cashflow, ROI, CO2), Tabellen (Tilgungspläne, Szenarien) und Extended KPIs (`extended_summary`).

## Migration: Hinweise und Schritte

1) Konsolidierung in Python (optional): Dubletten markieren und eine Referenzvariante wählen
2) TypeScript-Service-Skelette erzeugen; IPC-Kanäle definieren
3) PrimeReact-Komponenten aufsetzen: Tabs, Pricing-UI, Chart-Switcher, Financing-Panels, Advanced-Panels
4) Chart-Engine abstrahieren: einheitlicher ChartSpec → Plotly/ECharts Renderer, Export via Service
5) PDF-Pipeline anpassen: Chart-Bytes/Extended-KPIs aus Services einsammeln und an Template-Engine übergeben

## Anhänge: Funktionskontrakte (Kurzform)

- prepare_advanced_calculations_for_pdf_export(calc_results, project_data, texts)
  - Input: Berechnungsergebnisse/Projekt; Output: `AdvancedExport` + Session-State
  - Fehler: fehlende Integrator-Funktion → Warnung, Teilresultate leer
- render_advanced_* (5 Sektionen)
  - Input: `results`, `texts`; Output: UI + evtl. Chart-Bytes; robust gegen fehlende Keys
- Zinssensitivität/ROI in Finanzierung
  - Input: `financing_amount`, `interest_rate`, `term`, `leasing_factor`
  - Output: Charts (Rates/Costs, Cashflow), Tabellen; Speicherung in Session-State

— Ende —
