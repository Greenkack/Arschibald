# product_db.py – Vollständige Logik-Extraktion und Migrationsleitfaden

Diese Dokumentation beschreibt die Produktdatenbank-Schicht (`product_db.py`) zu 100%: Schema, Migrationen, öffentliche APIs, Fehlerbehandlung, Integrationspunkte (z. B. PDF), sowie Vorschläge für TypeScript/Electron-Ports und Tests.

---

## Überblick und Rolle im System

- Zweck: CRUD- und Query-Schicht für Produkte (Module, Wechselrichter, Speicher, Zubehör …) in SQLite.
- Abhängigkeit: nutzt `database.get_db_connection` (Fallback bei Importproblemen). Führt eigenes Schema-/Migrationsmanagement für Tabelle `products`.
- Konsumenten:
  - UI/Admin: Produktpflege, Auswahl in Angeboten.
  - PDF-Generator: Detailblöcke für Komponenten via `get_product_by_id` (siehe `pdf_generator.py`).
  - Analysis/Preislogik: Preisaufschläge/Labels via Produktdaten (z. T. in `calculations.py` verknüpft).

---

## Datenbankzugriff und Verfügbarkeit

- `get_db_connection_safe_pd`: Wrapper, zeigt bei Importproblemen von `database.py` einen Dummy an (gibt `None` zurück und loggt).
- `DB_AVAILABLE`: Flag, das im Erfolgsfall auf True gesetzt wird (nicht strikt genutzt, da Wrapper maßgeblich ist).

---

## Tabellenschema: `products`

Spalten (aktuelle Zielstruktur nach Migration):

- id INTEGER PRIMARY KEY AUTOINCREMENT
- category TEXT NOT NULL
- model_name TEXT NOT NULL UNIQUE
- brand TEXT
- price_euro REAL
- capacity_w REAL              (Wp für Module)
- storage_power_kw REAL        (kWh für Speicher)
- power_kw REAL                (kW für WR, Wallbox etc.)
- max_cycles INTEGER           (Speicher-Zyklen)
- warranty_years INTEGER
- length_m REAL
- width_m REAL
- weight_kg REAL
- efficiency_percent REAL
- origin_country TEXT
- description TEXT
- pros TEXT
- cons TEXT
- rating REAL
- image_base64 TEXT            (Produktbild als Base64)
- created_at TEXT DEFAULT CURRENT_TIMESTAMP
- updated_at TEXT DEFAULT CURRENT_TIMESTAMP
- datasheet_link_db_path TEXT  (Pfad/Link zu Datenblatt im Filesystem/DB)
- additional_cost_netto REAL DEFAULT 0.0 (Aufpreisposition)

Bemerkungen:

- Pflichtfelder: `category`, `model_name` (NOT NULL + `model_name` UNIQUE).
- Timestamps: Defaults in der Tabelle; Insert/Update setzen zusätzlich ISO-Strings.
- Preis-/Leistungsfelder: MULTI-Kategorie-tauglich (Module/WR/Speicher/…)

---

## Migrationen und Schema-Selbstheilung

- `create_product_table(conn)`: legt Tabelle an (ohne alle potenziellen Spalten) und ruft direkt `_migrate_product_table_columns`.
- `_migrate_product_table_columns(conn)`:
  - PRAGMA table_info liest vorhandene Spalten.
  - Historische Umbenennungen:
    - `added_date` → `created_at`
    - `last_updated` → `updated_at`
  - Erwartete Spaltenliste wird durchiteriert und fehlende Spalten mit sinnvollen Defaults ergänzt:
    - TEXT → DEFAULT '' (falls nötig), REAL → DEFAULT 0.0, INTEGER → DEFAULT 0
    - `created_at`/`updated_at` → DEFAULT CURRENT_TIMESTAMP
    - NOT NULL für `category`, `model_name` (ggf. Default ergänzt)

Wichtig: Migration wird bei jeder Nutzung der CRUD-Layer aufgerufen, da `create_product_table` davor steht. Das sorgt für robuste Nachrüstungen.

---

## Öffentliche API-Funktionen

- create_product_table(conn)
  - Erstinitialisierung + Migration der Spalten.

- add_product(product_data: Dict[str, Any]) -> Optional[int]
  - Anforderungen: `category`, `model_name` müssen gesetzt sein.
  - Duplikat-Check: SELECT id WHERE model_name = ? (genau, case-insensitive nur wenn DB so konfiguriert ist; hier default case-sensitive).
  - Standardbefüllung fehlender Felder (Zahlen → 0/0.0, Timestamps → now_iso, andere → None).
  - Insert dynamisch via Spaltenliste/Placeholders; Commit/Rollback, Rückgabe der neuen ID oder None.

- update_product(product_id, product_data) -> bool
  - Setzt immer `updated_at = now_iso` (überschreibt ggf. übergebene Werte).
  - Validierungen: `category`/`model_name` falls im Update enthalten, dürfen nicht leer sein.
  - Einzigartigkeitsprüfung für `model_name` gegenüber anderen IDs.
  - Erlaubte Felder via PRAGMA-Resultat gefiltert; dynamisches UPDATE; Commit/Rollback; Rückgabe Erfolg/Fehlschlag.

- delete_product(product_id) -> bool
  - DELETE nach ID; Rückgabe, ob Zeile gelöscht wurde.

- list_products(category: Optional[str] = None, company_id: Optional[int] = None) -> List[Dict[str, Any]]
  - Baut WHERE-Bedingungen abhängig von optionalen Filtern und sortiert nach `model_name` (NOCASE Kollation).
  - Rückgabe: Liste mit dict(row), oder [].
  - Hinweis: Der Code enthält einen optionalen Filter `company_id`, die Spalte `company_id` existiert im aktuellen Schema nicht. Siehe „Auffälligkeiten & Backlog“.

- get_product_by_id(product_id) -> Optional[Dict[str, Any]]
  - Einfacher SELECT WHERE id = ?.

- get_product_by_model_name(model_name: str) -> Optional[Dict[str, Any]]
  - SELECT WHERE model_name = ? COLLATE NOCASE (case-insensitive Suche).

- update_product_image(product_id, image_base64) -> bool
  - Convenience-Wrapper um `update_product` mit `image_base64`.

- list_product_categories() -> List[str]
  - DISTINCT category, sortiert NOCASE.

---

## Fehlerbehandlung und Logging

- Try/Except um DB-Operationen; druckt sprechende Prefixe, stacktraces via `traceback.print_exc()`.
- Bei Schreibfehlern: `conn.rollback()`.
- Fallback für fehlendes `database.py`: Dummy-Verbindung, die `None` zurückgibt; alle CRUD-Methoden prüfen auf `None` und brechen sauber ab.

---

## Integrationspunkte

- PDF-Generator (`pdf_generator.py`): nutzt `get_product_by_id_func` als Callback, um technische Komponentenblöcke zu rendern (Module/WR/Speicher/Zubehör).
- Admin/Oberfläche: Produktpflege, Bild-Upload (`image_base64`), Datenblatt (`datasheet_link_db_path`), Aufpreise (`additional_cost_netto`).
- Preis-/Analysepfad: Produktdaten können für Preis-Matrix-Aufpreise oder technische Kennwerte genutzt werden.

---

## Auffälligkeiten, Konsistenz und Migrationshinweise

- company_id Filter in `list_products`:
  - Aktuelles Schema enthält KEINE Spalte `company_id`. Die Bedingung `company_id = ?` führt in SQLite zu „no such column: company_id“, sobald der Filter genutzt wird.
  - Empfohlene Optionen:
    1) Spalte ergänzen: `company_id INTEGER` (NULL erlaubt), Index: `CREATE INDEX IF NOT EXISTS idx_products_company ON products(company_id)` und in `_migrate_product_table_columns` aufnehmen.
    2) Alternativ den Filter aus `list_products` entfernen, falls Multi-Company nicht benötigt wird.
  - Da dies ein Schemaeingriff ist, sollte er versioniert erfolgen (z. B. PRAGMA user_version) – siehe `database.py` Migrationsmuster.

- Timestamps:
  - Tabelle hat DEFAULT CURRENT_TIMESTAMP, `add_product`/`update_product` überschreiben via ISO-String. Das ist funktional, kann aber zu unterschiedlichen Formatierungen führen. Optional vereinheitlichen.

- UNIQUE `model_name`:
  - Business-mäßig sinnvoll, aber bei Varianten kann ein zusammengesetzter Schlüssel (brand, model_name, category) sinnvoller sein.

- Defaults für TEXT-Spalten:
  - Migration fügt bei NOT NULL ggf. DEFAULT '' hinzu. Bei Insert werden fehlende Felder meist mit None gesetzt; SQLite akzeptiert das für NULL-fähige Spalten.

---

## TypeScript/Electron-Port – Vorschlag

Model (Type):

```ts
export interface Product {
  id?: number;
  category: string;
  model_name: string;
  brand?: string;
  price_euro?: number;
  capacity_w?: number;
  storage_power_kw?: number;
  power_kw?: number;
  max_cycles?: number;
  warranty_years?: number;
  length_m?: number;
  width_m?: number;
  weight_kg?: number;
  efficiency_percent?: number;
  origin_country?: string;
  description?: string;
  pros?: string;
  cons?: string;
  rating?: number;
  image_base64?: string;
  created_at?: string;
  updated_at?: string;
  datasheet_link_db_path?: string;
  additional_cost_netto?: number;
  // optional: company_id?: number;
}
```

DB-Layer (Main, better-sqlite3/knex):

- Migrations:
  - Tabelle `products` mit obigen Spalten.
  - Optional: `company_id INTEGER`, Indizes: `idx_products_model` (model_name), `idx_products_category`, optional `idx_products_company`.

- Service-Methoden:
  - addProduct(p: Product) -> id
  - updateProduct(id, patch: Partial\<Product\>) -> boolean
  - deleteProduct(id) -> boolean
  - listProducts(filters?: { category?: string; company_id?: number }) -> Product[]
  - getProductById(id) -> Product | undefined
  - getProductByModelName(name) -> Product | undefined
  - listProductCategories() -> string[]

Renderer/UI:

- Admin-Seiten für Erstellen/Bearbeiten/Löschen, Bild-Upload (Base64 oder Pfad), Datenblatt-Pfad-Picker.
- Auswahlkomponenten in Angebots-/Analyse-Flows.

---

## Edge-Cases

- Leere Pflichtfelder (`category`, `model_name`): Abbruch mit Log.
- Doppelte `model_name`: Insert/Update blockiert; Fall abfangen und Feedback geben.
- Bilder (`image_base64`): Große Strings → UI- und DB-Grenzen beachten; optional Dateiablage bevorzugen.
- Datenblatt-Pfad (`datasheet_link_db_path`): Existenz prüfen, falls für PDF-Anhänge verwendet.
- Typkonvertierungen: JSON/CSV-Importpfade sollten Strings/Numbers sauber parsen.

---

## Tests und Backlog

Unit-Tests (Python):

- Migration: Hinzufügen fehlender Spalten, Umbenennungen funktionieren idempotent.
- add_product: Pflichtfelder, Defaults, Duplikate.
- update_product: Feldfilterung, updated_at gesetzt, Duplicate-Name-Schutz.
- list_products: category-Filter korrekt; company_id-Filter nur nach Schemaergänzung.
- get_product_by_*: exakte/NOCASE-Suche.
- list_product_categories: DISTINCT + NOCASE-Order.

Backlog/Verbesserungen:

- Schema konsolidieren: `company_id` sauber integrieren (Migration + Index) ODER Filter entfernen.
- Indizes für Performance (model_name, category, optional company_id).
- Vereinheitlichte Zeitstempel (nur DB-Default nutzen oder nur ISO-String pflegen).
- Eindeutigkeit optional erweitern (brand/model/category).
- Optionale Validierung der Zahlenbereiche (z. B. efficiency_percent 0–100).

---

## „How-To“ kurz

- Produkte anlegen: `add_product({ category, model_name, ... })` – prüft Pflichtfelder und Duplikate.
- Änderungen speichern: `update_product(id, patch)` – setzt `updated_at` und schützt Pflichtfelder.
- Abfragen: `list_products({ category? })`, `get_product_by_id`, `get_product_by_model_name`.
- Kategorien auslesen: `list_product_categories()`.
- Integration im PDF: `get_product_by_id` als Callback an den Generator übergeben, um Details/Bilder einzubetten.
