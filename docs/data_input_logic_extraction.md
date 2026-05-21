# UI- und Eingabelogik – Extraktion aus `data_input.py`

Diese Dokumentation fasst die gesamte Eingabelogik (Streamlit-UI) zusammen, die Kundendaten, Projekt-/Gebäudedaten, Verbräuche, optionale Finanzierung sowie Geocoding/Maps behandelt. Ziel ist eine saubere Blaupause für die Portierung nach Electron + PrimeReact.

## Zweck und Kontext

- Rolle: Erfasst Projektstammdaten und Nutzerpräferenzen. Schreibt direkt in `st.session_state.project_data`.
- Keine Rückgabe: `render_data_input(texts)` modifiziert State in-place (kein return).
- Abhängigkeiten: `database` (Admin-Settings), `product_db` (Produkte), `requests` (HTTP), `pandas` (Kartenpunkt), `streamlit` (UI), optional `streamlit_shadcn_ui` (nicht zwingend genutzt), `base64` (Bilddaten), `os`/Env.
- i18n: `get_text_di(texts_dict, key, fallback)` liefert UI-Texte mit Fallbacks.

## Externe Services und Konfiguration

- Google Geocoding API: `get_coordinates_from_address_google` (HTTP GET an `https://maps.googleapis.com/maps/api/geocode/json`).
- Google Static Maps: `get_Maps_satellite_image_url` baut die URL für ein Satellitenbild.
- API-Key-Quelle: Zuerst aus Env `Maps_API_KEY`, sonst Admin-Setting `Maps_api_key`. Platzhalter-String wird als „nicht konfiguriert“ interpretiert.

## Session-State-Vertrag

- `st.session_state.project_data` ist die zentrale Datenstruktur. Unter-Objekte werden bei Bedarf angelegt:
  - `customer_data: {}`
  - `project_details: {}`
  - `economic_data: {}`
- Weitere State-Keys (UI-Flags/Daten):
  - `customer_data_expanded_di`, `consumption_data_expanded_di`, `building_data_expanded_di`, `economic_data_expanded_di` (Expander-Status)
  - `satellite_image_url_di` (String | None)

### Datenschema – customer_data (Auszug)

- Stammdaten: `type` ('Privat'|'Gewerblich'), `salutation`, `title`, `first_name`, `last_name`
- Adresse: `full_address`, `address` (Straße), `house_number`, `zip_code`, `city`, `state`
- Kontakt: `email`, `phone_landline`, `phone_mobile`
- Steuern: `income_tax_rate_percent` (float)
- Finanzierung (optional, wenn `financing_requested` true):
  - `financing_type` ('Bankkredit (Annuität)'|'Leasing'|'Contracting')
  - Persönlich: `birth_date`, `nationality`, `resident_since`, `marital_status`, `property_regime?`, `dependent_children`
  - Beruf & Einkommen: `professional_status`, `profession`, `employer_name`, `business_sector`, `employer_address`, `employed_since`, `employment_type`, `employment_end_date?`, `monthly_net_income`, `other_monthly_income`, `other_income_description?`
  - Ausgaben: `monthly_rent_costs`, `private_health_insurance`, `existing_loan_payments`, `existing_leasing_payments`, `alimony_payments`
  - Projektfinanzierung: `desired_financing_amount`, `equity_amount`, plus je nach Typ:
    - Bankkredit: `loan_term_years`, `interest_rate_percent`
    - Leasing: `leasing_term_months`, `leasing_factor_percent`
  - Zweiter Antragsteller (optional): `has_co_applicant`, `co_*`-Felder (analog ausgewählte Untermenge)

### Datenschema – project_details (Auszug)

- Projekt: `anlage_type` ('Neuanlage'|'Bestandsanlage'), `feed_in_type` ('Teileinspeisung'|'Volleinspeisung')
- Geometrie/Ort: `latitude`, `longitude`
- Visualisierung Satellit: `visualize_roof_in_pdf_satellite` (bool), `satellite_image_base64_data` (Base64|None), `satellite_image_for_pdf_url_source` (String|None)
- Verbrauch/Kosten: `annual_consumption_kwh_yr`, `consumption_heating_kwh_yr`, `calculate_electricity_price` (bool), `costs_household_euro_mo`, `costs_heating_euro_mo`, `electricity_price_kwh`
- Gebäude: `build_year`, `roof_type`, `roof_covering_type`, `free_roof_area_sqm`, `roof_orientation`, `roof_inclination_deg`, `building_height_gt_7m`
- Zukunft: `future_ev` (bool), `future_hp` (bool)

Hinweis: Der Block „Technik-Auswahl“ (Module/WR/Speicher) ist aktuell in dieser View entfernt/auskommentiert. Produklisten werden dennoch geladen; Nutzung optional optimierbar.

### Datenschema – economic_data (Auszug)

- `simulation_period_years`, `electricity_price_increase_annual_percent`, `custom_costs_netto`

## Kernfunktionen und Verhalten

### get_text_di(texts_dict, key, fallback)

- Zweck: Sicherer Zugriff auf Übersetzungen/Labels mit nachvollziehbarem Fallback (`key` → „Key Title (DI Text fehlt)“).
- Input: `texts_dict: Dict[str,str]`, `key: str`, `fallback_text_value?: str`
- Output: `str` (immer)

### parse_full_address_string(full_address, texts) -> Dict[str,str]

- Aufgabe: Extrahiert `street`, `house_number`, `zip_code`, `city` aus einem Freitext.
- Logik:
  - Regex für Postleitzahl/Stadt am Ende der Zeichenkette (auch „DE-12345 Stadt“ usw.).
  - Fallback: CSV-Splitting an Kommas und erneuter ZIP/City-Regex.
  - Straße/Hausnummer: Regex `^(.*?)\s+([\d\w][\d\w\s\-/.]*?)$` mit Plausibilitätscheck (Hausnummer enthält Ziffern).
- Rückgabe: Dict mit leeren Strings, falls nicht ermittelbar.
- Edge Cases: Mehrteilige Städtenamen, keine Hausnummer, Komma-Varianten, internationale Präfixe.

### get_coordinates_from_address_google(address, city, zip_code, api_key, texts) -> {latitude, longitude}|None

- Preconditions: API-Key vorhanden (nicht Platzhalter), `address` und `city` gesetzt.
- Ablauf: HTTP-GET gegen Geocoding API, prüft `status == OK` und extrahiert `geometry.location`.
- Fehler: Timeout/RequestException → None; unbekannte Strukturen → None. Keine UI-Meldungen (auskommentiert), „silent failure“ bevorzugt.

### get_Maps_satellite_image_url(lat, lon, api_key, texts, zoom=20, width=600, height=400) -> str|None

- Preconditions: API-Key vorhanden, keine Null-Koordinaten (es sei denn `allow_zero_coords_map_di` im State erlaubt).
- Ergebnis: Zusammengesetzte Static Maps URL.

### render_data_input(texts) -> None

- Struktur:
  - Kundendaten (Expander): Anlagentyp/Typ, Anrede/Titel/Name, Adresseingabe + Parser-Button, manuelle Felder, Bundesland, Koordinaten + Geocode-Button, Kartenpunkt, Satellitenbild-Section, Kontakte, Einkommensteuer.
  - Bedarfsanalyse (Expander): Verbräuche und Kosten, Berechnung Strompreis oder manuelle Eingabe.
  - Gebäudedaten (Expander): Baujahr, Dachart/-deckung, freie Dachfläche, Ausrichtung, Neigung, Gebäudehöhe.
  - Zukünftiger Mehrverbrauch: EV/HP Checkboxen.
  - Finanzierung (optional): Vollständige Erfassung je nach Typ inkl. zweitem Antragsteller; „Finanzierung berechnen“-Button (Platzhalter, Ergebnis im Analyse-Dashboard geplant).
  - Wirtschaftliche Parameter (Expander): Simulationsdauer, Strompreissteigerung, Zusatzkosten.
- Seiteneffekte:
  - Schreibt zahlreiche Felder in `st.session_state.project_data`.
  - Setzt/aktualisiert `st.session_state.satellite_image_url_di`.
  - Lädt optional Bilddaten (Base64) in `project_details.satellite_image_base64_data` via HTTP.
- Designentscheidungen:
  - Keine `st.rerun()` in Button-Callbacks (Streamlit rerunnt automatisch nach Interaktion).
  - Stabile Widget-Keys mit Suffix `_v6_exp_stable` zur Vermeidung von Key-Kollisionen.
  - UI-Meldungen (`st.warning/info`) weitgehend auskommentiert → sauberere Oberfläche im Normalbetrieb.

## Abhängigkeiten und Fallbacks

- `product_db`: `list_products`, `get_product_by_model_name`, `get_product_by_id` (Dummies aktiv, wenn Import fehlschlägt).
- `database`: `get_db_connection`, `load_admin_setting` (Dummies aktiv, wenn Import fehlschlägt).
- Optionales UI-Framework: `streamlit_shadcn_ui` – Import mit Fallback, im aktuellen Code jedoch nicht verwendet.

## Typische Fehler-/Randfälle

- Fehlende/Platzhalter-API-Keys → Geocoding/Static Maps deaktiviert.
- Unvollständige Adresse → Parser liefert nur Teilwerte; Geocoding-Button deaktiviert/warnt.
- Null-/Standardkoordinaten → Map/Satellitenbild werden nicht angezeigt.
- Netzwerkfehler beim Laden des Satellitenbildes → Base64-Felder werden zurückgesetzt.

## Mapping nach Electron + PrimeReact

### TypeScript-Datentypen (Vorschlag)

```ts
export interface CustomerData {
  type?: 'Privat' | 'Gewerblich';
  salutation?: string; title?: string; first_name?: string; last_name?: string;
  full_address?: string; address?: string; house_number?: string; zip_code?: string; city?: string; state?: string | null;
  email?: string; phone_landline?: string; phone_mobile?: string;
  income_tax_rate_percent?: number;
  financing_requested?: boolean;
  financing_type?: 'Bankkredit (Annuität)' | 'Leasing' | 'Contracting';
  birth_date?: string; nationality?: string; resident_since?: string; marital_status?: string; property_regime?: string; dependent_children?: number;
  professional_status?: string; profession?: string; employer_name?: string; business_sector?: string; employer_address?: string; employed_since?: string; employment_type?: string; employment_end_date?: string;
  monthly_net_income?: number; other_monthly_income?: number; other_income_description?: string;
  monthly_rent_costs?: number; private_health_insurance?: number; existing_loan_payments?: number; existing_leasing_payments?: number; alimony_payments?: number;
  desired_financing_amount?: number; equity_amount?: number; loan_term_years?: number; interest_rate_percent?: number; leasing_term_months?: number; leasing_factor_percent?: number;
  has_co_applicant?: boolean; co_birth_date?: string; co_nationality?: string; co_profession?: string; co_monthly_net_income?: number; co_professional_status?: string;
}

export interface ProjectDetails {
  anlage_type?: 'Neuanlage' | 'Bestandsanlage'; feed_in_type?: 'Teileinspeisung' | 'Volleinspeisung';
  latitude?: number; longitude?: number;
  visualize_roof_in_pdf_satellite?: boolean; satellite_image_base64_data?: string | null; satellite_image_for_pdf_url_source?: string | null;
  annual_consumption_kwh_yr?: number; consumption_heating_kwh_yr?: number; calculate_electricity_price?: boolean; costs_household_euro_mo?: number; costs_heating_euro_mo?: number; electricity_price_kwh?: number;
  build_year?: number; roof_type?: string | null; roof_covering_type?: string | null; free_roof_area_sqm?: number; roof_orientation?: string | null; roof_inclination_deg?: number; building_height_gt_7m?: boolean;
  future_ev?: boolean; future_hp?: boolean;
}

export interface EconomicData {
  simulation_period_years?: number; electricity_price_increase_annual_percent?: number; custom_costs_netto?: number;
}

export interface ProjectData { customer_data: CustomerData; project_details: ProjectDetails; economic_data: EconomicData; }
```

### Services/Hooks (Vorschlag)

- SettingsService: `loadSetting(key)` ↔ `load_admin_setting_safe` (Admin-Settings, inkl. `Maps_api_key` und Optionslisten wie Anrede/Titel/Bundesländer/Dacharten).
- ProductsService: `listProducts({category})` ↔ `list_products_safe` (nur laden, wenn „Technik-Auswahl“ wieder im UI benötigt wird).
- GeocodingService:
  - `parseFullAddress(full: string)` – die Regex-Logik als pure Funktion portieren.
  - `getCoordinates(addr, city, zip)` – Google Geocoding API via Node-Fetch; API-Key aus App-Settings.
  - `getStaticMapUrl(lat, lon, opts)` – Static Maps URL builder.
- State-Management:
  - In React via `useState`/`useReducer` oder Zustand/Redux. Struktur analog `ProjectData`.
  - „Expander“-Zustände als UI-Local-State (nicht persistieren), nur Formdaten persistieren.

### UI-Portierungsnotizen

- Streamlit `st.map` → in React z. B. leaflet oder Google Maps JavaScript API.
- Bilddownload/Base64 für PDF → im Main-Prozess ablegen (IPC), um CORS/Größe zu kontrollieren; Renderer hält nur Flag/Quelle.
- i18n → `get_text_di` entspricht `t('key', fallback)` in i18n-Bibliothek (react-i18next).

## Verbesserungsmöglichkeiten (vor Portierung)

- Produklisten nur laden, wenn benötigt (Technik-Auswahl wieder aktiv).
- Konsolidierung der UI-Meldungen und zentraler Error-Handler (statt auskommentierter `st.warning/info`).
- Validierungen ergänzen (Email/PLZ, Zahlenbereiche) und als Schema definieren (z. B. zod/yup in React).
- Einheitliche Benennung (`Maps_api_key` vs Env) und klarer Feature-Flag für „Satellitenbild in PDF“.
