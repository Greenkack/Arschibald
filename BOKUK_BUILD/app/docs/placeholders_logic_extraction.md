# pdf_template_engine/placeholders.py – vollständige Logik-Extraktion

Diese Datei definiert das Mapping von Beispiel- bzw. OCR-Texten aus den sechs Overlay-Templates (`coords/seite1.yml` … `seite6.yml`) zu logischen Platzhalter-Keys und baut mit `build_dynamic_data(...)` alle dynamischen Werte aus `project_data`, `analysis_results` und `company_info` zusammen. Die Ergebnisse werden vom PDF-Overlay-Renderer genutzt, um Texte, Zahlen und statische Marker korrekt in das 6-Seiten-Haupttemplate einzusetzen.

Stand: aktueller Codebestand aus `placeholders.py` (siehe Repo, Datum laut Datei).

## Kernartefakte

- PLACEHOLDER_MAPPING: Dict[str, str]
  - Mappt exakte Beispieltexte aus den YMLs auf semantische Keys (z. B. „8,4 kWp“ → `anlage_kwp`).
  - Mehrfach-Zuordnungen möglich (kollidierende Beispieltexte werden konsolidiert). Spätere `update`-Blöcke ergänzen Bereiche wie Footer, Seite 2, Seite 3, Seite 4.
- build_dynamic_data(project_data, analysis_results, company_info) → Dict[str, str]
  - Baut alle dynamischen Werte, wendet Formatierungen an, berechnet Quoten/Heuristiken und liefert alle Keys, die das Overlay erwartet (inkl. Platzhalter-Bilder als Base64).

## Platzhalter-Mapping – Überblick

Die Datei erweitert `PLACEHOLDER_MAPPING` schrittweise für:

- Seite 1: Kundendaten, KPIs, Speicherkennzahlen, Einspeisevergütung, MwSt.-Betrag, statische Texte „inklusive“, „DC Dachmontage“, „AC Installation | Inbetriebnahme“, Footer (`footer_company`, `footer_date`).
- Seite 2: Energieflüsse (kWh), Quoten und Anteile für Produktion/Verbrauch, optionaler Hinweistext zur Batterie-Heuristik und kWh-Anteile „Woher kommt mein Strom?“.
- Seite 3: Wirtschaftlichkeit (Ersparnisse, IRR, LCOE in Cent/kWh).
- Seite 4: Komponenten (Modul, WR, Speicher) – Hersteller, Modell, Leistung/Kapazität, Wirkungsgrad, Garantien, Zyklen; zusätzlich Base64-Bilder.

Wichtig: Die Beispieltexte müssen exakt den Einträgen in den jeweiligen `coords/seiteX.yml` entsprechen, damit die Zuordnung beim Overlay greift.

## build_dynamic_data – Contract und Verhalten

Signatur:

- Inputs:
  - `project_data: Dict[str, Any] | None` – enthält u. a. `customer_data`, `project_details`
  - `analysis_results: Dict[str, Any] | None` – KPIs, Energiesummen, Quoten, Preise
  - `company_info: Dict[str, Any] | None` – Firmeninfos inkl. `logo_base64`

- Return:
  - `Dict[str, str]`: Mapping „Platzhalter-Key → Stringwert“; fehlende Felder werden robust leer oder sinnvoll befüllt.

Hauptlogik:

- Hilfsfunktionen:
  - `as_str(v)`: robustes String-Casting mit leerem String als Fallback.
  - `fmt_number(val, decimals=1, unit="")`: bevorzugt `calculations.format_kpi_value`, sonst eigene „deutsche“ Formatierung (Komma als Dezimaltrenner, Punkt als Tausender).
  - `parse_float(val)`: tolerante Zahl-Extraktion (entfernt Einheiten, wandelt Komma/Punkt).

- Kunden/Firmendaten:
  - `customer_name` wird aus Anrede, Titel, Vor- und Nachname zusammengesetzt.
  - Adresse via `customer_street` (Straße + Hausnummer) und `customer_city_zip` (PLZ + Ort).
  - `company_*`-Felder aus `company_info` (Name, Straße, Stadt/PLZ, Phone, Mail, Website) plus `company_logo_b64`.
  - Footer: `footer_company` = Kundenname; `footer_date` = „Angebot, dd.mm.YYYY“.

- Seite 1:
  - `anlage_kwp`: aus `analysis_results.anlage_kwp` oder berechnet aus `module_quantity * module_capacity_w / 1000` (2 Nachkommastellen, „kWp“). Zusätzlich `pv_power_kWp` kompatibel gefüllt.
  - `pv_modules_count_number` und `pv_modules_count_with_unit` (…„Stück“).
  - `inverter_total_power_kw`: Gesamtleistung (kW) ohne Dezimalstellen (berechnet aus Single×Menge möglich).
  - `storage_capacity_kwh` und `battery_capacity_kwh`: Kapazität aus DB (bevorzugt `storage_power_kw` als kWh, dann echte Kapazitätsfelder), sonst UI oder Analysis-Fallbacks; Darstellung mit 2 Nachkommastellen.
  - `annual_pv_production_kwh`: Jahresproduktion mit 2 Nachkommastellen („kWh/Jahr“), plus Kurzform `pv_prod_kwh_short`.
  - `annual_feed_in_revenue_eur`: Einspeisevergütung Jahr 1 (oder generalisiert) in Euro.
  - `vat_amount_eur`: MwSt.-Betrag (19% Netto) oder brutto-netto-Differenz.
  - Statisch: `static_inklusive`, `static_dc_dachmontage`, `static_ac_installation`.

- Seite 2 – Energieflüsse und Quoten:
  - Summen aus Ergebnislisten (`monthly_direct_self_consumption_kwh`, `monthly_storage_charge_kwh`, `monthly_storage_discharge_for_sc_kwh`), konsistent korrigiert (Deckelung vs. Produktion/Verbrauch) und heuristische Überschreibungen (Batterie: Kapazität × 300 Tage).
  - Abgeleitete Größen: `grid_feed_in_kwh`, `grid_bezug_kwh`, `annual_consumption_kwh` aus vielen Quellen (inkl. Haushalts+Heizung-Fallback).
  - KWh-Anteile: `consumption_direct_kwh`, `consumption_battery_kwh`, `consumption_grid_kwh`.
  - Prozent-Verteilung Produktion: Direkt/Batterie/Einspeisung normalisieren auf 100% mit integer-Rundung; Template-Token werden gezielt vertauscht, um Layout-Anforderungen zu erfüllen:
    - `direct_consumption_quote_prod_percent` zeigt Einspeisung in %
    - `battery_use_quote_prod_percent` zeigt Batterieanteil in %
    - `feed_in_quote_prod_percent_number` ist der Direktverbrauch (Zahl ohne „%“)
  - Verbrauchsverteilung unten: `battery_cover_consumption_percent`, `grid_consumption_rate_percent`, `direct_cover_consumption_percent_number`.
  - Optionaler Hinweis: `battery_note_text` (Batterie × 300-Tage Heuristik).

- Seite 3 – Wirtschaftlichkeit:
  - `savings_with_battery`, `savings_with_battery_number`, `savings_without_battery`, `savings_without_battery_number`.
  - `irr_percent` (1 Nachkommastelle) und `lcoe_cent_per_kwh` (Cent/kWh aus Euro/kWh).

- Seite 4 – Komponenten:
  - Modul, WR, Speicher: Hersteller, Modell, Leistung/Kapazität, Effizienz, Garantien (inkl. Leistungsgarantie „\<Jahre\> / \<Prozent\>“), Entladetiefe, Zyklen.
  - Bilder: `module_image_b64`, `inverter_image_b64`, `storage_image_b64`.
  - Quellen: `project_details.selected_*_name` → Lookup via `product_db.get_product_by_model_name` (robust mit Try/Except).

## Datenquellen und Fallback-Reihenfolgen (wichtig)

- Anlage kWp: `analysis_results.anlage_kwp` → berechnet aus `project_details` → `project_details.anlage_kwp`
- Batterie kWh: Produkt-DB (`storage_power_kw`→kWh; dann `capacity_kwh`/`usable_capacity_kwh`/`nominal_capacity_kwh`) → UI `selected_storage_storage_power_kw` → weitere Felder (Analysis/Projekt)
- Jahresproduktion: `analysis_results.annual_pv_production_kwh` → `annual_yield_kwh` → `sim_annual_yield_kwh`
- Jahresverbrauch: Viele Felder (Analysis/Projekt/Gesamt) plus Haushalts+Heizung-Additionsfallback
- Einspeisung/Netzbezug: aus Produktion/Verbrauch und Direkt/Speicher abgeleitet (immer >= 0)

## Formatierung und Lokalisierung

- Primär-Formatter: `calculations.format_kpi_value` (wenn verfügbar), sonst lokaler Fallback (deutsche Formatierung).
- Immer konkrete Einheiten in der Ausgabe: „kWh/Jahr“, „kWh“, „kW“, „Jahre“, „€“, „Cent“, „%“.
- Anzahl Nachkommastellen pro Feld festgelegt (z. B. Seite 1: kWp mit 2 Nachkommastellen; Summen in kWh meist 0 Nachkommastellen).

## Integration mit Template-Engine und Generator

- `PLACEHOLDER_MAPPING` liefert das Bindeglied: Beispieltext (aus `coords/*.yml`) → logischer Key (z. B. `anlage_kwp`).
- Der Overlay-Renderer ersetzt anschließend die Beispieltexte im PDF-Hintergrund mit den in `build_dynamic_data` gelieferten Werten.
- Firmendaten (inkl. Logo) werden übergeben, damit Header/Footer korrekt sind; `company_logo_b64` wird gesondert als Bild verwendet.

## Edge-Cases und Robustheit

- Fehlende Module/WR/Speicher: entsprechende Felder bleiben leer, Bilder werden nicht gesetzt.
- Ungültige Zahlenformate: `parse_float` entfernt Einheiten und wandelt sicher; bei Fehlern wird Fallback-String genutzt.
- „storage_power_kw“ als kWh: Projektkonvention wird explizit unterstützt, aber Begrenzung (0 < kWh <= 200) verhindert grobe Ausreißer.
- Prozentverteilungen Seite 2: Integer-Normalisierung garantiert Summe 100%; Korrektur-Logik verteilt Überhänge.
- Batterie-300-Tage-Heuristik: Überschreibt Summen nur, wenn Kapazität bekannt; erzeugt Info-Hinweis.

## TypeScript/Electron-Mapping

- Interface `PlaceholdersData` (Renderer/Main): Map<string, string>
- Service in Main (PDF-Engine):
  - `buildPlaceholders(projectData, analysisResults, companyInfo) → PlaceholdersData`
  - nutzt identische Fallbackreihenfolgen; Formatter analog (`Intl.NumberFormat('de-DE')` + Einheitssuffixe)
- Renderer nutzt die gelieferten Keys im Overlay-Prozess (z. B. beim Zeichnen in PDF-Kontext oder beim Ersetzen auf Canvas vor dem Rendern).

## Tests (empfohlen) und Backlog

- Unit-Tests Formatter/Floats: `fmt_number`, `parse_float` mit lokalen Testwerten (de/EN-Varianten, mit Einheiten).
- build_dynamic_data:
  - Mindestdatensatz ohne Produkte → keine Exceptions, leere Strings an den erwarteten Keys.
  - Batteriepfad: Priorität DB → UI → Analysis/Projekt.
  - Seite-2-Quoten: Summe 100% (Int), keine negativen kWh, Vertauschung der Pfeil-Labels wie gefordert.
  - Seite-4-Details: wenn `product_db` nicht verfügbar → kein Crash, nur leere Felder.
- Backlog:
  - Mapping-Drift verhindern: Script, das `coords/*.yml` tokenisiert und gegen `PLACEHOLDER_MAPPING` diffed.
  - Erweiterung: Zusätzliche Platzhalter für weitere Seiten/Abschnitte (z. B. Garantie-Details, Hersteller-Links) sauber aufnehmen.
