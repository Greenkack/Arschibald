# CRM Pipeline UI – Logik-Extraktion (crm_pipeline_ui.py)

Stand: 2025-09-12

## Zweck und Überblick

Das Modul `crm_pipeline_ui.py` bildet die Sales-Pipeline ab:

- Kanban-Übersicht mit Stufen (lead → qualified → proposal → negotiation → won; lost separat)
- Lead-Formular mit Kontaktdaten/Quelle/Wert/Wahrscheinlichkeit/Erwartetem Abschlussdatum
- Lead-Liste mit Filtern (Stufe, Quelle) und Sortierung
- Analytics: KPIs, Funnel, Trends, Quellen-Performance (Mock)

## Datenmodell: crm_leads

On-demand Anlage der Tabelle (falls nicht vorhanden):

- id INTEGER PRIMARY KEY AUTOINCREMENT
- company_name TEXT NOT NULL, contact_person TEXT NOT NULL
- email TEXT, phone TEXT, address TEXT, lead_source TEXT
- estimated_value REAL DEFAULT 0, probability INTEGER DEFAULT 50
- expected_close_date DATE, stage TEXT DEFAULT 'lead'
- stage_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Kernklassen/-Methoden

- Klasse CRMPipeline
  - pipeline_stages: Definition der Stufen (Name, Beschreibung, Farbe, Icon, Order)
  - lead_sources: Liste möglicher Quellen
  - render_pipeline_interface(texts): Tabs und Delegation
  - _render_pipeline_overview(): KPIs + Kanban pro aktiver Stufe; Liste gewonnener/verlorener Deals (30 Tage)
  - _render_pipeline_lead_card(lead, stage): kompakte Karte inkl. Buttons (Details/Stufe ändern)
  - _render_new_lead_form(): Formular; create via _create_lead
  - _render_lead_list(): Filter/Sorte; Anzeige via `_render_lead_detail_card`
  - _render_lead_detail_card(lead): Detailkarte inkl. Aktionen (Bearbeiten/Nächste Stufe/Verloren/Löschen)
  - _render_pipeline_analytics(): Zeitraumwahl; KPIs; Tabs (Funnel/Trend/Quelle)
  - _render_pipeline_funnel/_render_trend_analysis/_render_source_performance: textuelle Mock-Visualisierungen

## Datenbank-Helper

- _get_pipeline_statistics() → KPIs (SUM/AVG/COUNT) + Mock-Deltas
- _get_leads_by_stage(stage) → Liste der Leads einer Stufe (mit Table-Create)
- _get_recent_closed_leads(status) → gewonnene/verlorene der letzten 30 Tage
- _get_filtered_leads(stage_filter, source_filter, sort_by) → Filter/Sortierung
- _create_lead(lead_data) → INSERT
- _update_lead_stage(lead_id, new_stage) → UPDATE (Stufe + Timestamps)
- _delete_lead(lead_id) → DELETE
- _get_next_stage(current_stage) → folgender Schritt (oder None)
- _get_analytics_data(period) → Mock-Kennzahlen und -Verteilungen

## Contracts

- Lead-Objekt Felder: company_name, contact_person, email, phone, address, lead_source, estimated_value, probability, expected_close_date, stage, notes
- Datumsfelder: expected_close_date als date → Speicherung via ISO-String
- Stage-Änderungen setzen stage_changed_at/updated_at via CURRENT_TIMESTAMP

## Edge Cases

- DB nicht verfügbar: UI bricht mit Fehlermeldung ab
- Tabellen-Erstellung ist in den Query-Methoden abgesichert
- Anzeige limitiert in Kanban auf 5 Leads pro Spalte mit „+n weitere“

## Migration (Electron/TypeScript)

- LeadService: listByStage, listFiltered, create, updateStage, delete, analytics
- Kanban als Drag&Drop in Frontend (Stufe ändern → updateStage)
- Datumshandling über ISO-Strings und Date-Objekte
