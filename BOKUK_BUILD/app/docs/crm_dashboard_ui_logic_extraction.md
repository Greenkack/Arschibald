# CRM Dashboard UI – Logik-Extraktion (crm_dashboard_ui.py)

Stand: 2025-09-12

## Zweck und Überblick

`crm_dashboard_ui.py` bietet ein mehrteiliges Dashboard:

- Übersicht: KPIs, Aktivitäten-Timeline
- Kunden: Tabelle mit Suche/Filter und Detailansicht
- Projekte: Status-KPIs und Pipeline-Funnel (Plotly)
- Umsatz: Umsatz-KPIs und Liniendiagramm (Vergleich 2023/2024)
- Statistiken: Kundenverteilung (Pie), Anlagengrößen (Histogramm), Performance-Metriken

Abhängigkeiten (optional/hart): database.get_all_active_customers/get_customer_by_id/update_customer/get_db_connection; locales.get_text; plotly

## Hauptfunktion und Tabs

- render_crm_dashboard(texts, module_name=None)
  - prüft DB-Verfügbarkeit
  - rendert Header, Tabs und delegiert
- show_crm_dashboard(texts): öffentlicher Wrapper

Tabs → Unterfunktionen:

- render_overview_section(texts): KPIs und Aktivitätenliste (dummy)
- render_customers_section(texts): Kundenliste, Suche/Filter, Details
- render_projects_section(texts): Projekt-KPIs und Pipeline-Funnel (Dummy-Daten)
- render_revenue_section(texts): Umsätze und Monatschart (Dummy-Daten)
- render_statistics_section(texts): Verteilungen und Performance-Tabelle

## Datenflüsse und Annahmen

- get_all_active_customers() liefert Liste von Dicts mit u. a. name, email, phone, created_at, project_status, project_value, system_size
- Die KPIs in Overview nutzen einfache Aggregationen (teils Dummy)
- Kunden-Tabelle: Spalten-Mapping und Anzeige nur vorhandener Felder; Suche term-übergreifend per contains

## Contracts

- Inputs: texts: Dict[str,str] für UI-Texte
- Outputs: reine Streamlit-UI; keine Rückgabe
- Fehlerszenarien: DB-Import schlägt fehl → Hinweis und Abbruch

## Migration (Electron/TypeScript)

- Serviceschicht: CustomerService (list, get), ProjectService (stats), RevenueService (series), AnalyticsService (distributions)
- Charts via rechnerseitig erzeugte Daten; Plotly/Chart.js im Frontend
- Internationalisierung via locales/i18n Layer
