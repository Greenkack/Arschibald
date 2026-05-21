# === Lokale Datei mit dem Summary erzeugen (MD + TXT) ===

$base  = "C:\Users\win10\Desktop\Kakerlake 1"
$docs  = Join-Path $base "docs"
New-Item -ItemType Directory -Force -Path $docs | Out-Null
$md    = Join-Path $docs "kakerlake_archive_summary.md"
$txt   = Join-Path $docs "kakerlake_archive_summary.txt"

$CONTENT = @'

# Kakerlake – Code-Überblick & Extrakte

- Ziel: Migration der bestehenden **Python/Streamlit**-App (PV/Wärmepumpe) nach **React + Electron + Tailwind** – funktionsgleich, ohne KI.
- Herzstück: **Multi-PDF-Ausgabe** (PV, WP, kombiniert) aus statischen Templates + YAML-Koordinaten + dynamischen Platzhaltern.
- Deutsche Formatierung (Tausender-Punkt, Dezimal-Komma, €-Spacing) überall beibehalten.

## PDF-Template-System

- Engine (Erstellung/Merge/Overlay/Placeholder):
  - `pdf_template_engine/overlay.py`
  - `pdf_template_engine/dynamic_overlay.py`
  - `pdf_template_engine/merger.py`
  - `pdf_template_engine/placeholders.py`
  - `pdf_template_engine/prepare_backgrounds.py`
- Statische Templates:
  - Photovoltaik: `pdf_templates_static/notext/nt_nt_*.pdf`
    - gefunden: `nt_nt_01.pdf` … `nt_nt_07.pdf`
  - Wärmepumpe: `pdf_templates_static/notext/hp_nt_*.pdf`
- Layout/Koordinaten/Styles:
  - PV: `coords/*.yml`
  - WP: `coords_wp/*.yml`
  - (YAML enthält Positionen, Schriftgrößen/-arten, Farben, Layer; Engine setzt Platzhalter → Vektor/Text/Image-Overlay → Merge)

## Wichtige Module (Funktion/Verantwortung, Auszug)

- **Berechnung & Analyse**
  - `calculations.py` – PV-Kernrechnungen (Produktion, Eigenverbrauch, Speicherfluss, Einspeisung, Autarkie, Wirtschaftlichkeit)
  - `calculations_extended.py` – erweiterte KPIs/Simulationen (10/20 Jahre, Preissteigerungen, Degradation, Wartung)
  - `analysis.py`, `analysis_utils.py` – UI-gebundene Auswertung, Diagrammvorbereitung
  - `financial_tools.py` – Finanzierung (Zinsen, Ratenpläne, Laufzeiten, Effekte)
  - `calculations_heatpump.py` – WP-spezifische Last/Leistung/Kosten
  - `solar_calculator.py`, `heatpump_ui.py` – Streamlit-Oberflächen für PV/WP-Eingaben

- **PDF Orchestrierung**
  - `central_pdf_system.py` – zentraler PDF-Fluss, Template-Registrierung, Sicherheits-Sanitizer
  - `pdf_generator.py` – Standard/Erweitert PDF bauen, Seiten sequenzieren
  - `multi_offer_generator.py` – **Multi-PDF** (mehrere Firmen), Rotation/Preisstaffelung, ZIP-Export
  - `pdf_ui.py`, `pdf_widgets.py`, `pdf_preview.py`, `pdf_styles.py`, `pdf_helpers.py`, `pdf_migration.py` – UI-Schalter, Vorschau, Stil-Sets, Migrationshilfen

- **Daten/Optionen/Formatierung**
  - `database.py`, `product_db.py` – CRUD für Kunden/Produkte/Angebote/Logos
  - `options.py`, `init_database.py`, `update_tariffs.py` – globale App-Optionen, Tarife (Teileinspeisung/Volleinspeisung), PVGIS-Schalter
  - `product_attributes.py`, `brand_logo_db.py` – Produktattribute/Hersteller-Branding
  - `german_formatting.py` – **DE-Zahl/Währung/Einheiten** konsistent

- **UI (Streamlit)**
  - `gui.py`, `data_input.py` – Hauptnavigation, Eingabe-Flows (Bedarfsanalyse, Projektstammdaten)
  - CRM-Teile (Dashboard/Kundenverwaltung/Workflows) – CRUD, Aktivitätenzähler, Angebot→CRM-Übernahme

## Preis-Matrix (INDEX/MATCH-Semantik)

- Admin lädt Excel/CSV: **Zeilen = Modulanzahl**, **Spalten = Speichermodelle** (Schreibweise identisch zu Produkt-DB).  
  Fallback-Spalte **„kein Speicher“** vorhanden.
- Lookup: (Anzahl Module, Speichermodell) → **schlüsselfertiger Endpreis** (inkl. Installation/Genehmigungen).
- Typische Parser/Cacher im Code (Heuristik): `parse_module_price_matrix_excel`, `load_price_matrix_df_with_cache`.

## PV-Fluss (Energie & Geld) – Zielverhalten (für TS-Port)

Gegeben (je Kunde dynamisch):  

- Jahresproduktion kWh (aus kWp × Standort/Neigungs-/Ausrichtungsfaktoren bzw. PVGIS oder statisch)  
- Direktverbrauch kWh  
- Speicher: Jahresladevolumen = (Kapazität_kWh × **300** Tage) [deine Vorgabe]  
- Entnahme aus Speicher kWh (limitiert durch Bedarf)  
- Überschuss: Produktion – Direktverbrauch – Speicherladung → Einspeisung  
- Tarife: strompreis €/kWh (aus Jahreskosten/Jahresverbrauch) + Einspeisevergütung €/kWh

Berechne:  

- `savingsDirectEuro = directUseKWh * strompreis`  
- `savingsFromBatteryEuro = fromBatteryKWh * strompreis`  
- `revenueFeedInEuro = feedInFromProductionKWh * feedInTariff`  
- `revenueBatteryExportEuro = batterySurplusKWh * feedInTariff`  
- `totalAnnualBenefitEuro = sum(obiger vier)`  
- Kennzahlen: Autarkie, Eigenverbrauchsquote, Amortisation, 10/20-Jahre-Hochrechnungen (mit Preissteigerungen/Inflation/Wartung/Degradation)

## Multi-PDF-Ausgabe

- Auswahl **mehrerer Firmen** → Rotation (linear/zufällig/kategoriespezifisch), Preisstaffelungen je Firma (%), Startpunkt (PV/WR/Speicher).  
- Jede Firma erhält: Standard-PDF (7 Seiten) + optional erweiterte Module (Datenblätter, Diagramme, Firmendokumente, AGB/Datenschutz, Custom Content).  
- Ergebnis: 2..N Angebote → ZIP.  
- Alle Schalter/Optionen werden in `pdf_ui.py`/Engine-Modulen verarbeitet; Platzhalter + Koordinate bestimmen Einbettung.

## Migrationsempfehlung (Technikplan)

1. **Core (TypeScript) kapseln:** Ein sauberes Input/Output-Schema (z. B. `CustomerBasics`, `PVSetup`, `Tariffs`, `PVResult*`).  
2. **Preis-Matrix-Adapter (TS):** 1:1 INDEX/MATCH-Lookup inkl. Fallback „kein Speicher“.  
3. **PDF-Renderer in Electron:**  
   - Weiterverwendung der **YAML-Koordinaten** & der **Platzhalter-Namen**; Mapping-Layer in TS (z. B. pdf-lib oder node-canvas + Hummus/PDFKit).  
   - Template-Hintergründe (`*_nt_*.pdf`) als Background-Pages, dann Overlay-Draws gemäß YAML.  
4. **DE-Formatierung:** Zentrales Intl/Formatter-Modul (€, kWh, Prozent, Datumsangaben) → UI + PDF identisch.  
5. **UI (React + Tailwind):** Menüs/Untermenüs wie beschrieben, aber mit neuem Flow (Bedarfsanalyse → PV/WP → Ergebnisse → PDF).  
6. **CRM/DB:** CRUD-Endpoints/Storage (lokal: SQLite/Better-SQLite3 oder Server-API).  
7. **Tests:** Golden-Master Samples (Energie/Geld-Flüsse), Snapshot-PDF-Tests (Bounding-Box-Toleranzen).

---
'@

# Dateien schreiben (UTF-8)

Set-Content -Path $md  -Value $CONTENT -Encoding UTF8
Set-Content -Path $txt -Value $CONTENT -Encoding UTF8

Write-Host "Erstellt:" $md
Write-Host "Erstellt:" $txt
