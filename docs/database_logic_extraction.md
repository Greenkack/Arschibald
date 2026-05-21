# Datenbank-Logik – Extraktion aus `database.py`

Diese Datei fasst die komplette Datenbanklogik des Projekts zusammen (Stand: Schema-Version 14). Sie beschreibt Tabellen, Migrationspfad, Funktionen/Contracts, Seiteneffekte (Dateisystem) und bekannte Inkonsistenzen – als Grundlage für die Portierung nach Electron/PrimeReact.

## Übersicht

- DB-Engine: SQLite (Datei unter `data/app_data.db`)
- Schema-Version: `PRAGMA user_version = 14` (zusätzlich Spiegelung in `admin_settings.schema_version`)
- Datenverzeichnisse:
  - `data/` (DB, Preis-Matrizen, Artefakte)
  - `data/company_docs` (Firmendokumente, Firmen-Templates/Images)
  - `data/customer_docs` (Kundenbezogene Dokumente)
- JSON-Serialisierung: Komplexe Settings werden als JSON-String in `admin_settings.value` gespeichert
- Fehlerbehandlung: try/except mit Logging, teilweise defensive Fallbacks

## Tabellen und Schemas (mit Migrationen)

### admin_settings (v1)

- key TEXT PRIMARY KEY
- value TEXT (JSON-Strings oder einfache Werte; Booleans als 0/1)
- last_modified TEXT DEFAULT CURRENT_TIMESTAMP

### products (v2)

- Felder: `id`, `category`, `manufacturer`, `model_name` UNIQUE, `price_euro`, `datasheet_link`, `description`, `technical_data`, `image_base64`, `added_date`/`last_updated` TEXT, produktbezogene Specs (z. B. `capacity_w`, `power_kw`, `warranty_years`, `efficiency_percent`, etc.), `additional_cost_netto`, `max_cycles`
- Hinweis: Funktion `_add_company_id_to_products_table` fügt optional `company_id INTEGER REFERENCES companies(id)` hinzu, wird aber in `init_db` aktuell nicht aufgerufen

### companies (v12)

- Felder: `id`, `name` UNIQUE, `logo_base64`, Adresse/Kontakt, `tax_id`, `commercial_register`, `bank_details`, `pdf_footer_text`, `is_default` (0/1), `created_at`, `updated_at`
- Migration: ggf. Umbenennung `company_name` -> `name`, Sicherstellung fehlender Spalten

### company_documents (v12)

- Felder: `id`, `company_id` FK->companies(id) ON DELETE CASCADE, `document_type`, `display_name`, `file_name`, `absolute_file_path` UNIQUE (relativer Pfad), `uploaded_at`
- Hinweis: `absolute_file_path` ist relativ zu `data/company_docs`

### pdf_templates (v13)

- Felder: `id`, `template_type`, `name`, `content`, `image_data` BLOB, `created_at`, `updated_at`
- Index: `idx_pdf_templates_type` auf `template_type`

### Firmenspezifische Vorlagen (v14)

- company_text_templates: `id`, `company_id` FK, `name`, `content`, `template_type` (Default 'offer_text'), `created_at`, `updated_at`
- company_image_templates: `id`, `company_id` FK, `name`, `template_type` (Default 'title_image'), `file_path`, `created_at`, `updated_at`
- Indizes je Tabelle auf `(company_id)` und `(template_type)`

### customer_documents (ad-hoc)

- Felder: `id`, `customer_id` FK->customers(id), `project_id` (optional), `doc_type`, `display_name`, `file_name`, `absolute_file_path` (relativ zu `data/`!), `uploaded_at`

### crm_customers (ad-hoc)

- Felder: `id`, `first_name`, `last_name`, `email`, `phone`, `address`, `status` (Default 'active'), `created_at`, `updated_at`, `notes`, `project_data` (JSON)

### heat_pumps (Helper)

- Felder: `id`, `model_name` UNIQUE, `manufacturer`, `heating_output_kw`, `power_consumption_kw`, `scop`, `price`

Weitere implizite/erwartete Tabellen (nicht in dieser Datei definiert):

- customers (wird von `update_customer` und `customer_documents` referenziert)
- company_technique (wird von `add_default_technique_for_company` beschrieben)

## Migrations- und Initialisierungslogik

- DB_SCHEMA_VERSION = 14
- init_db():
  - Liest `PRAGMA user_version`
  - Führt schrittweise Migrationen aus: v1 (`admin_settings`) -> v2 (`products`) -> v12 (`companies`, `company_documents` + Spaltenprüfungen/Umbenennungen) -> v13 (`pdf_templates`) -> v14 (firmenspezifische Templates)
  - Setzt `PRAGMA user_version = DB_SCHEMA_VERSION`
  - Seedet `admin_settings` aus `INITIAL_ADMIN_SETTINGS` (JSON für Dict/List; Booleans als 0/1; spezielle Keys können NULL sein: `price_matrix_csv_data`, `active_company_id`)

## Datei-/Verzeichnis-Seiteneffekte

- `data/` und Unterordner werden bei Bedarf erstellt
- `company_docs` (Firmendokumente): Dateinamen werden sicherisiert, Pfad relativ gespeichert, Datei auf Disk geschrieben/gelöscht
- `customer_docs` (Kundendokumente): analog, aber `absolute_file_path` relativ zu `data/` (abweichende Praxis!)
- `cleanup_orphaned_files()`: löscht Dateien in `company_docs`, die nicht (mehr) in DB gelistet sind; entfernt leere Verzeichnisse
- `backup_database(path)`/`restore_database(path)`: Datei-Kopie der SQLite-DB
- `reset_database()`: löscht DB-Datei und `company_docs`-Verzeichnis, ruft `init_db()` (löscht NICHT `customer_docs`)

## Zentrale Funktionen/Contracts (Auswahl)

### Allgemein

- `get_db_connection() -> sqlite3.Connection|None`: Verbindung mit `row_factory = sqlite3.Row`
- `load_admin_setting(key, default=None) -> Any`: JSON-Decode, Bool-/NULL-Handling für spezielle Keys
- `save_admin_setting(key, value) -> bool`: JSON-Encode für Dict/List, Bool -> 0/1, NULL für `active_company_id`/`price_matrix_csv_data`
- `get_database_statistics() -> Dict`: Counts, Größe, `schema_version`
- `validate_database_integrity() -> Dict`: PRAGMA-Checks, Orphans in `company_documents`, doppelte `products.model_name`, Default-Company-Kohärenz

### PDF-Templates

- CRUD: `add_pdf_template`, `list_pdf_templates`, `get_pdf_template`, `update_pdf_template`, `delete_pdf_template`
- Helper: `get_pdf_template_by_name(template_type, name)`

### Companies

- CRUD: `add_company(company_data) -> id|None`, `list_companies()`, `get_company(id)`, `update_company(id, data)`, `delete_company(id)`
- Default/Active: `set_default_company(id)`, `get_active_company()` (nutzt `admin_settings.active_company_id` mit Fallback auf `is_default`)
- Defaulttechnik: `add_default_technique_for_company(company_id)` – insert in nicht definierte Tabelle `company_technique`

### Company Documents

- `add_company_document(company_id, display_name, document_type, original_filename, file_bytes) -> id|None`
- `list_company_documents(company_id, doc_type=None) -> List[Dict]` (liefert zusätzlich computed `absolute_file_path`)
- `delete_company_document(document_id) -> bool`

### Customer Documents (separate Ablage)

- `ensure_customer_documents_table()`, `_create_customer_documents_table(conn)`
- `add_customer_document(customer_id, file_bytes, display_name, doc_type='other', project_id=None, suggested_filename=None) -> id|None`
- `list_customer_documents(customer_id, project_id=None)`
- `get_customer_document_file_path(document_id) -> abs_path|None`
- `delete_customer_document(document_id) -> bool` (löscht auch Datei auf Disk)

### CRM (Kunden)

- `get_all_active_customers() -> List[Dict]`: erstellt `crm_customers` bei Bedarf, gibt aktive Kunden
- `create_customer(customer_data) -> bool`: Insert in `crm_customers`
- `get_customer_by_id(customer_id) -> Dict|None`
- Achtung: `update_customer` aktualisiert Tabelle `customers` (andere Struktur) – separate Domäne, nicht `crm_customers`

### Firmenspezifische Vorlagen

- Text: `add_company_text_template`, `list_company_text_templates(company_id, template_type=None)`, `update_company_text_template`, `delete_company_text_template`
- Bilder: `add_company_image_template` (legt Datei unter `company_docs/<id>/images` ab), `list_company_image_templates`, `get_company_image_template_data`, `update_company_image_template`, `delete_company_image_template`

### Wärmepumpen

- `create_heat_pumps_table(conn)`, `get_all_heat_pumps(conn)`, `add_heat_pump(conn, data)`, `update_heat_pump(conn, data)`, `delete_heat_pump(conn, id)` – Hinweis: nicht in `init_db()` integriert; eigener Lifecycle nötig

## Bekannte Inkonsistenzen/Beobachtungen

- Doppelte Konstanten/Initialisierungen in Datei (Variablen und `INITIAL_ADMIN_SETTINGS` kommen zweimal vor) – sollte dedupliziert werden
- Unterschiedliche Basis für `absolute_file_path`:
  - `customer_documents`: Pfad relativ zu `data/`
  - `company_documents`: Pfad relativ zu `data/company_docs`
- `update_customer` arbeitet auf Tabelle `customers`, während CRM-APIs `crm_customers` verwenden
- `company_technique` Tabelle wird verwendet, aber nicht angelegt
- `heat_pumps`-Tabellenanlage nicht in `init_db` integriert

## Python → TypeScript Mapping (Vorschlag)

Zur späteren Implementierung der Electron/PrimeReact-Services eine grobe Abbildung:

- AdminSettingsService
  - load/save/exportAll/importAll ↔ load_admin_setting/save_admin_setting/export_admin_settings/import_admin_settings
- PdfTemplatesService
  - add/list/get/update/remove/getByName ↔ add_pdf_template/list_pdf_templates/get_pdf_template/update_pdf_template/delete_pdf_template/get_pdf_template_by_name
- CompaniesService
  - add/list/get/update/remove/setDefault/getActive ↔ add_company/list_companies/get_company/update_company/delete_company/set_default_company/get_active_company
- DocumentsService
  - addCompanyDoc/listCompanyDocs/deleteCompanyDoc ↔ add_company_document/list_company_documents/delete_company_document
  - addCustomerDoc/listCustomerDocs/deleteCustomerDoc ↔ add_customer_document/list_customer_documents/delete_customer_document
- CompanyTemplatesService
  - addText/addImage/listText/listImage/getImageData/updateText/updateImage/deleteText/deleteImage ↔ entsprechende company_*_templates-Funktionen
- CRMService
  - listActiveCustomers/createCustomer/getCustomerById ↔ get_all_active_customers/create_customer/get_customer_by_id

## Ports/Abbildung für Electron + PrimeReact (Vorschlag)

- DB-Zugriff in Electron Main: `better-sqlite3` (synchron, robust) oder `sqlite3`/`knex` (async)
- IPC-API (Main <-> Renderer): Service-Methoden spiegeln obige Contracts
- Datei-Handling: Pfade relativ zu `app.getPath('userData')/data` und strikte Sanitization
- Settings: JSON in Key/Value-Store beibehalten; Booleans als echte Booleans in TS, im DB-Adapter konvertieren
- Migrations: user_version-basierte Migrationskette wie oben; initiale Seeds aus `INITIAL_ADMIN_SETTINGS`

## Minimale TS-Schnittstellen (Skizze)

```ts
// Services im Main-Prozess
interface AdminSettingsService {
  load<T=any>(key: string, defaultValue?: T): Promise<T>;
  save(key: string, value: any): Promise<boolean>;
  exportAll(): Promise<Record<string, any>>;
  importAll(s: Record<string, any>): Promise<boolean>;
}

interface CompaniesService {
  add(data: CompanyInput): Promise<number|null>;
  list(): Promise<Company[]>;
  get(id: number): Promise<Company|null>;
  update(id: number, data: Partial<CompanyInput>): Promise<boolean>;
  remove(id: number): Promise<boolean>;
  setDefault(id: number): Promise<boolean>;
  getActive(): Promise<Company|null>;
}

interface DocumentsService {
  addCompanyDoc(companyId: number, file: Buffer, displayName: string, docType: string, originalName: string): Promise<number|null>;
  listCompanyDocs(companyId: number, docType?: string): Promise<CompanyDocument[]>;
  deleteCompanyDoc(docId: number): Promise<boolean>;

  addCustomerDoc(customerId: number, file: Buffer, displayName: string, docType?: string, projectId?: number): Promise<number|null>;
  listCustomerDocs(customerId: number, projectId?: number): Promise<CustomerDocument[]>;
  deleteCustomerDoc(docId: number): Promise<boolean>;
}

interface PdfTemplatesService {
  add(t: { type: string; name: string; content?: string; imageData?: Buffer }): Promise<number|null>;
  list(type?: string): Promise<PdfTemplate[]>;
  get(id: number): Promise<PdfTemplate|null>;
  update(id: number, data: { name: string; content?: string; imageData?: Buffer|null }): Promise<boolean>;
  remove(id: number): Promise<boolean>;
  getByName(type: string, name: string): Promise<PdfTemplate|null>;
}

interface CompanyTemplatesService {
  addText(companyId: number, name: string, content: string, type?: string): Promise<number|null>;
  addImage(companyId: number, name: string, image: Buffer, type?: string, originalName?: string): Promise<number|null>;
  listText(companyId: number, type?: string): Promise<CompanyTextTemplate[]>;
  listImage(companyId: number, type?: string): Promise<CompanyImageTemplate[]>;
  getImageData(templateId: number): Promise<Buffer|null>;
  updateText(id: number, name: string, content: string): Promise<boolean>;
  updateImage(id: number, name: string): Promise<boolean>;
  deleteText(id: number): Promise<boolean>;
  deleteImage(id: number): Promise<boolean>;
}

interface CRMService {
  listActiveCustomers(): Promise<CrmCustomer[]>;
  createCustomer(data: CrmCustomerInput): Promise<boolean>;
  getCustomerById(id: number): Promise<CrmCustomer|null>;
}
```

Diese Extraktion dient als Blaupause für die anschließende TS-Implementierung (Services, Migrations, IPC-Routen, React-Hooks).
