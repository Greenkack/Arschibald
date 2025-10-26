# BOK Applikation – Gesamtindex

Dieser Index bietet einen schnellen Überblick über die Struktur und die wichtigsten Komponenten der Anwendung.

## Projektüberblick

Die Anwendung umfasst:

- Umfangreiche Python-Skripte für Berechnungen (PV, Wärmepumpe, Finanz, PDFs)
- UI-Module (Streamlit / interne Dashboards / CRM / Admin)
- PDF-Generierungssystem mit modularen Styles & Widgets
- Datenbank- und Migrations-Skripte
- Mehrsprachigkeit / Lokalisierung (`de.json`)
- Node.js / Frontend-Bestandteile (PrimeReact-Integration, theming, Komponenten)

## Hauptbereiche (Top-Level Verzeichnisse)

- `apps/` – App-Module und ggf. Microfrontends
- `assets/` – Logos, Bilder, statische Ressourcen
- `components/` – Wiederverwendbare UI-Komponenten
- `coords/`, `coords_wp/` – Koordinatendaten / Wärmepumpen relevanter Datenraum
- `data/` – Laufzeitdaten, erzeugte Artefakte, ggf. Cache
- `docs/` – Dokumentation & technische Reports
- `kakerlake-react-electron/` – Experimenteller/ separater Frontend- oder Electron-Client
- `packages/` – (Falls Monorepo-Aspekt) Node/Python Pakete
- `pdf_template_engine/`, `pdf_templates_static/` – PDF Baukastensystem
- `tests/` – Testscripte & Konfigurationen
- `theming/` – Styles, Themes, visuelle Konfiguration
- `tools/` – Hilfsskripte & Wartung
- `utils/` – Utility-Funktionen

## Wichtige Einzeldateien (Auswahl)

- `calculations.py`, `calculations_extended.py`, `pv_calculations_core.py` – Zentrale Berechnungslogik
- `pdf_generator.py`, `pdf_styles.py`, `pdf_widgets.py` – PDF System
- `crm.py`, `crm_dashboard_ui.py`, `crm_pipeline_ui.py` – CRM Module
- `admin_panel.py` – Administrationsoberfläche
- `multi_offer_generator.py` – Angebots-/Multi-PDF-Erstellung
- `database.py`, `database_bridge.py` – DB Anbindung
- `locales.py`, `de.json` – Internationalisierung / Lokalisierung
- `README.md` – Hauptbeschreibung
- `requirements.txt` – Python Abhängigkeiten
- `package.json` / `pnpm-workspace.yaml` – Node & Workspaces

## Hinweise

Diese Datei dient als schneller Einstiegspunkt. Ergänzungen oder Querverlinkungen zu tieferen Architekturdetails können in `README.md` oder den Dokumentationsdateien unter `docs/` erfolgen.

Stand: Automatisch erzeugt am 2025-09-19.
