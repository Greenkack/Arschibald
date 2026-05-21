# CRM – Logik-Extraktion (crm.py)

Stand: 2025-09-12

## Zweck und Überblick

Das Modul `crm.py` implementiert die Kernfunktionen des Customer Relationship Management (CRM) innerhalb der Streamlit-App:

- Datenmodell und Migrationen für Kunden (`customers`) und Projekte (`projects`)
- CRUD-Operationen für Kunden und Projekte
- Streamlit-UI-Flows (Listen, Detail, Anlegen/Bearbeiten, Löschen) mit Sitzungszustand (`st.session_state`)
- Kundenakte (Dateiablage) via optionale DB-Helfer aus `database.py`

Das Modul ist eigenständig nutzbar und migriert bestehende Tabellen sicher mit `PRAGMA table_info` und `ALTER TABLE`.

## Datenmodell und Migrationen

### Tabelle: customers

Spalten (mit Default-Anlage in CREATE TABLE; zusätzliche Spalten werden migrationssicher per `ALTER TABLE` ergänzt):

- id INTEGER PRIMARY KEY AUTOINCREMENT
- salutation TEXT
- title TEXT
- first_name TEXT NOT NULL
- last_name TEXT NOT NULL
- company_name TEXT
- address TEXT
- house_number TEXT
- zip_code TEXT
- city TEXT
- state TEXT
- region TEXT
- email TEXT
- phone_landline TEXT
- phone_mobile TEXT
- income_tax_rate_percent REAL DEFAULT 0.0
- creation_date TEXT
- last_updated TEXT

Migration: Nach dem initialen `CREATE TABLE IF NOT EXISTS` werden die tatsächlich vorhandenen Spalten via `PRAGMA table_info(customers)` ermittelt. Fehlende Spalten aus
`{"state","region","email","phone_landline","phone_mobile","income_tax_rate_percent","creation_date","last_updated"}` werden mittels `ALTER TABLE customers ADD COLUMN ...` ergänzt. Fehler (z. B. duplicate column) werden protokolliert, aber nicht fatal behandelt.

### Tabelle: projects

Spalten (Auszug; alle werden in einer CREATE TABLE IF NOT EXISTS-Anweisung angelegt):

- id INTEGER PRIMARY KEY AUTOINCREMENT
- customer_id INTEGER NOT NULL (FK auf customers.id)
- project_name TEXT NOT NULL
- project_status TEXT
- roof_type TEXT, roof_covering_type TEXT, roof_orientation TEXT
- free_roof_area_sqm REAL, roof_inclination_deg INTEGER, building_height_gt_7m INTEGER
- annual_consumption_kwh REAL, costs_household_euro_mo REAL
- annual_heating_kwh REAL, costs_heating_euro_mo REAL
- anlage_type TEXT, feed_in_type TEXT
- module_quantity INTEGER
- selected_module_id INTEGER, selected_inverter_id INTEGER
- include_storage INTEGER, selected_storage_id INTEGER, selected_storage_storage_power_kw REAL
- include_additional_components INTEGER
- selected_wallbox_id INTEGER, selected_ems_id INTEGER, selected_optimizer_id INTEGER
- selected_carport_id INTEGER, selected_notstrom_id INTEGER, selected_tierabwehr_id INTEGER
- visualize_roof_in_pdf INTEGER
- latitude REAL, longitude REAL
- creation_date TEXT, last_updated TEXT

Hinweise:

- Zeitstempel werden als ISO-8601-Strings abgelegt (`datetime.now().isoformat()`).
- Boolean-Flags sind als INTEGER (0/1) modelliert.

## CRUD-APIs (Funktionen)

Alle Funktionen nutzen eine gegebene `sqlite3.Connection` und arbeiten mit `sqlite3.Row` oder `dict`-Äquivalenten.

- create_tables_crm(conn):
  - Legt `customers` und `projects` an (falls nicht vorhanden) und führt Spalten-Migrationen auf `customers` durch.

- save_customer(conn, customer_data) -> Optional[int]:
  - Upsert-Logik: Wenn `id` vorhanden → UPDATE, sonst INSERT.
  - Erzwingt Pflichtfelder: `first_name`, `last_name`; leere Werte werden auf `Interessent` bzw. `Unbekannt` gesetzt.
  - Normalisiert optionale Strings (trim) und setzt `last_updated` immer auf now().
  - Verwendet Spalten-Whitelist: nur Keys, die in `PRAGMA table_info(customers)` existieren, werden gespeichert.
  - Rückgabe: Kunden-ID oder None.

- load_customer(conn, customer_id) -> Optional[Dict]:
  - Lädt einen Kunden als dict; None, wenn nicht gefunden.

- delete_customer(conn, customer_id) -> bool:
  - Löscht erst alle Projekte des Kunden, dann den Kunden. Rückgabe, ob Zeilen gelöscht wurden.

- load_all_customers(conn) -> List[Dict]:
  - Lädt alle Kunden als Liste von dicts.

- save_project(conn, project_data) -> Optional[int]:
  - Upsert-Logik analog `save_customer`. Setzt `last_updated` und ggf. `creation_date`.
  - Spalten-Whitelist via `PRAGMA table_info(projects)`.

- load_project(conn, project_id) -> Optional[Dict]
- delete_project(conn, project_id) -> bool
- load_projects_for_customer(conn, customer_id) -> List[Dict]

## Streamlit-UI: State Machine und Flows

Die zentrale UI-Funktion ist `render_crm(texts, get_db_connection_func)` und steuert via `st.session_state` mehrere Ansichten:

- Steuer-Keys:
  - crm_view_mode: 'customer_list' | 'add_customer' | 'edit_customer' | 'view_customer' | 'add_project' | 'edit_project' | 'view_project'
  - selected_customer_id: Optional[int]
  - selected_project_id: Optional[int]

- customer_list:
  - Button: "Neuen Kunden anlegen" → view_mode='add_customer'.
  - Lädt Kunden (DataFrame `hide_index=True`), zeigt je Kunde: ID, Name (Vor-/Nachname, Ort) und Aktionen: Ansehen, Bearbeiten, Löschen.
  - Löschen ist zweistufig (Bestätigung über `session_state[confirm_delete_customer_{id}]`).

- add_customer/edit_customer:
  - Formular für alle Kundenfelder (Strings/Nummern) mit Validierung (Vor-/Nachname Pflicht).
  - Submit → `save_customer`, Erfolg → zurück zur Liste, Auswahl des gespeicherten Kunden.
  - Cancel → zurück zur Liste.

- view_customer (inkl. Projektliste und Kundenakte):
  - Zeigt Kundendetails (Name, E-Mail, Adresse, Steuersatz).
  - Projekte des Kunden als Tabelle und als Kartenliste mit Aktionen: Ansehen, Bearbeiten, Löschen (erneut zweistufige Bestätigung).
  - Button: "Neues Projekt anlegen" → view_mode='add_project'.
  - Kundenakte (Dateiablage) in Expander:
    - Nutzt optionale DB-Helfer aus `database` (falls vorhanden):
      - _ensure_customer_documents_table(), _add_customer_document_db, _list_customer_documents_db, _delete_customer_document_db, _get_customer_document_file_path
    - Upload: Mehrfach-Dateiuploader akzeptiert gängige Typen (pdf/jpg/png/gif/bmp/doc/xls/txt); ggf. doc_type=offer_pdf.
    - Liste: Name, Typ, Zeit; Download via Dateipfad; Lösch-Button.

- add_project/edit_project:
  - Hinweis: Projektdaten können aus `st.session_state['project_data']` (Eingabe-Tab) geladen werden.
  - Formular für Projektdaten: Dachdaten, Verbrauch, Anlagen-/Einspeisetyp, Komponenten, Speicher, Geo, Visualisierung.
  - Produkt-DB-Integration (optional, via `st.session_state.product_db_module`): Module/WR/Speicher-Auswahl per `list_products`.
  - Submit → `save_project` (Pflicht: Projektname), Erfolg → zurück zu view_customer.
  - Cancel → zurück zu view_customer.

- view_project:
  - Zeigt Projektdetails (Status, Komponenten, Speicher etc.).
  - Aktionen: Bearbeiten, Löschen (zweistufig), Zurück zur Kundenprojekten/Listenansicht.

## Verträge (Contracts)

- Eingaben (Formulare) sind Strings, Zahlen oder Booleans; Persistenz erfolgt als TEXT/REAL/INTEGER.
- Zeitangaben: ISO-Strings in TEXT-Spalten.
- Rückgaben der CRUD-Funktionen sind dicts mit Keys gemäß Tabellenspalten.
- Session-State-Keys werden konsistent gesetzt und vor Navigation via `st.rerun()` erzwungen.

## Fehlerbehandlung und Edge Cases

- Datenbankmodul nicht verfügbar: In `render_crm` wird ein Fehler angezeigt und die Funktion beendet.
- Migration: `ALTER TABLE`-Fehler werden geloggt; bereits vorhandene Spalten sind unkritisch.
- Pflichtfelder: Bei Kunden werden leere Namen mit Defaults gefüllt; bei Projekten ist `project_name` Pflicht.
- Dokumentenablage: Alle Operationen sind optional und werden nur ausgeführt, wenn die entsprechenden Funktionen importiert werden konnten.

## Hinweise für Migration (Electron/TypeScript)

- Serviceschicht vorschlagen:
  - CustomerService: create/update/delete/get/list
  - ProjectService: create/update/delete/get/list, listByCustomer
  - FileVaultService: add/list/delete/getFilePath
- UI-Routing: `crm_view_mode` als Router-State; Navigation über Actions.
- Persistenz: SQLite via better-sqlite3/knex; Migrations über knex-migrate.
- Datums-/Zeitfelder: als ISO-Strings oder native Date-Objekte behalten; beim Rendern formatieren.

## Test-Harness (__main__)

- Enthält einen vollständigen In-Memory-Test mit `sqlite3.connect(':memory:')`, der Tabellen erzeugt, Kunden/Projekte anlegt, lädt und wieder löscht.
- Simuliert Produkt-DB via Mock-Klasse.

## Bekannte Punkte und ToDos

- Internationalisierung: Texte kommen über `texts`/get_text_crm; bei TS-Migration entsprechend i18n-Layer nutzen.
- Validierung erweitern (E-Mail/Telefon-Formate; harte Constraints in DB).
- Indexe für häufige Suchen (z. B. projects.customer_id, customers.last_name, customers.city).
