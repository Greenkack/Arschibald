# database.py (Schema Version 14 - Spaltennamen und last_modified korrigiert)
import json
import os
import sqlite3
import traceback
from datetime import datetime
from typing import Any

DB_SCHEMA_VERSION = 14
print(f"DATABASE.PY TOP LEVEL: DB_SCHEMA_VERSION ist auf "
      f"{DB_SCHEMA_VERSION} gesetzt.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_data.db')
CUSTOMER_DOCS_BASE_DIR = os.path.join(DATA_DIR, 'customer_docs')

if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        print(f"DB: Datenverzeichnis '{DATA_DIR}' erstellt.")
    except OSError as e:
        print(
            f"DB: FEHLER beim Erstellen des Datenverzeichnisses '{DATA_DIR}': {e}")
if not os.path.exists(CUSTOMER_DOCS_BASE_DIR):
    try:
        os.makedirs(CUSTOMER_DOCS_BASE_DIR)
        print(
            f"DB: Kunden-Dokumente Verzeichnis '{CUSTOMER_DOCS_BASE_DIR}' erstellt.")
    except OSError as e:
        print(
            f"DB: FEHLER beim Erstellen des Kunden-Dokumente Verzeichnisses '{CUSTOMER_DOCS_BASE_DIR}': {e}")

# --- Minimale DB-Helfer (Kompatibilität) ---


def get_db_connection() -> sqlite3.Connection | None:
    """Stellt eine SQLite-Verbindung zur Hauptdatenbank her (Row-Factory aktiviert).

    Diese Funktion wird von product_db.py und Brücken verwendet und kann in älteren
    Ständen fehlen. Hiermit wird die Produkt-CRUD wieder funktionsfähig.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.row_factory = sqlite3.Row  # komfortabler Zugriff per Spaltenname
        except Exception:
            pass
        return conn
    except Exception as e:
        print(f"DB: get_db_connection fehlgeschlagen: {e}")
        return None


def init_db(conn: sqlite3.Connection |
            None = None) -> sqlite3.Connection | None:
    """Optionale Initialisierung. Gibt eine Verbindung zurück.

    product_db.create_product_table() kümmert sich um die 'products'-Tabelle.
    Diese Funktion existiert primär als Kompatibilitäts-Stubs für Aufrufer,
    die init_db erwarten.
    """
    try:
        _conn = conn or get_db_connection()
        return _conn
    except Exception as e:
        print(f"DB: init_db Fehler: {e}")
        return None

# --- CRM Kunden-Dokumente (Kundenakte) Helper auf Modulebene ---


def _create_customer_documents_table(conn: sqlite3.Connection) -> None:
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                doc_type TEXT, -- e.g. 'offer_pdf', 'image', 'note', 'other'
                display_name TEXT,
                file_name TEXT,
                absolute_file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
            """
        )
        conn.commit()
    except Exception as e:
        print(f"DB Fehler _create_customer_documents_table: {e}")


def ensure_customer_documents_table() -> None:
    conn = get_db_connection()
    if not conn:
        return
    try:
        _create_customer_documents_table(conn)
    finally:
        conn.close()


def add_customer_document(
        customer_id: int,
        file_bytes: bytes,
        display_name: str,
        doc_type: str = "other",
        project_id: int | None = None,
        suggested_filename: str | None = None) -> int | None:
    """Speichert eine Datei im Kundenakte-Ordner und erfasst sie in der DB. Gibt Dokument-ID zurück."""
    try:
        if not isinstance(file_bytes, (bytes, bytearray)
                          ) or len(file_bytes) == 0:
            return None
        conn = get_db_connection()
        if not conn:
            return None
        _create_customer_documents_table(conn)

        # Sichere Dateinamenserstellung
        safe_name = suggested_filename or f"{
            display_name or 'dokument'}_{
            datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
        safe_name = safe_name.replace("/", "_").replace("\\", "_")
        # Ordner für Kunden
        customer_dir = os.path.join(
            CUSTOMER_DOCS_BASE_DIR,
            f"customer_{customer_id}")
        os.makedirs(customer_dir, exist_ok=True)
        abs_path = os.path.join(customer_dir, safe_name)
        with open(abs_path, "wb") as f:
            f.write(file_bytes)

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO customer_documents (customer_id, project_id, doc_type, display_name, file_name, absolute_file_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (customer_id,
             project_id,
             doc_type,
             display_name or safe_name,
             safe_name,
             os.path.relpath(
                 abs_path,
                 DATA_DIR)))
        conn.commit()
        doc_id = cur.lastrowid
        conn.close()
        return doc_id
    except Exception as e:
        print(f"DB Fehler add_customer_document: {e}")
        return None


def list_customer_documents(
        customer_id: int, project_id: int | None = None) -> list[dict[str, Any]]:
    try:
        conn = get_db_connection()
        if not conn:
            return []
        _create_customer_documents_table(conn)
        cur = conn.cursor()
        if project_id is not None:
            cur.execute(
                "SELECT id, doc_type, display_name, file_name, absolute_file_path, uploaded_at FROM customer_documents WHERE customer_id = ? AND project_id = ? ORDER BY uploaded_at DESC",
                (customer_id, project_id),
            )
        else:
            cur.execute(
                "SELECT id, doc_type, display_name, file_name, absolute_file_path, uploaded_at FROM customer_documents WHERE customer_id = ? ORDER BY uploaded_at DESC",
                (customer_id,),
            )
        rows = cur.fetchall()
        conn.close()
        result: list[dict[str, Any]] = []
        for r in rows:
            result.append({
                "id": r[0],
                "doc_type": r[1],
                "display_name": r[2],
                "file_name": r[3],
                "relative_db_path": r[4],
                "uploaded_at": r[5],
            })
        return result
    except Exception as e:
        print(f"DB Fehler list_customer_documents: {e}")
        return []


def get_customer_document_file_path(document_id: int) -> str | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        cur.execute(
            "SELECT absolute_file_path FROM customer_documents WHERE id = ?",
            (document_id,
             ))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        rel = row[0]
        # absolute path relativ zum DATA_DIR
        return os.path.join(DATA_DIR, rel)
    except Exception as e:
        print(f"DB Fehler get_customer_document_file_path: {e}")
        return None


def delete_customer_document(document_id: int) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        # get path first
        cur = conn.cursor()
        cur.execute(
            "SELECT absolute_file_path FROM customer_documents WHERE id = ?",
            (document_id,
             ))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        rel_path = row[0]
        abs_path = os.path.join(DATA_DIR, rel_path)
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception as e_rm:
            print(
                f"DB Warnung: Datei konnte nicht gelöscht werden ({abs_path}): {e_rm}")
        cur.execute(
            "DELETE FROM customer_documents WHERE id = ?", (document_id,))
        conn.commit()
        success = cur.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"DB Fehler delete_customer_document: {e}")
        return False


INITIAL_ADMIN_SETTINGS: dict[str, Any] = {
    "price_matrix_csv_data": None,
    "feed_in_tariffs": {
        "parts": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 8.1},
            {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 7.0},
            {"kwp_min": 40.01, "kwp_max": 1000.0, "ct_per_kwh": 5.7}
        ],
        "full": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.9},
            {"kwp_min": 10.01, "kwp_max": 100.0, "ct_per_kwh": 10.8}
        ]
    },
    "global_constants": {
        'vat_rate_percent': 0.0, 'electricity_price_increase_annual_percent': 3.0,
        'simulation_period_years': 20, 'inflation_rate_percent': 2.0,
        'loan_interest_rate_percent': 4.0, 'capital_gains_tax_kest_percent': 26.375,
        'alternative_investment_interest_rate_percent': 5.0,
        'co2_emission_factor_kg_per_kwh': 0.474, 'maintenance_costs_base_percent': 1.5,
        'einspeiseverguetung_period_years': 20, 'marktwert_strom_eur_per_kwh_after_eeg': 0.03,
        'storage_cycles_per_year': 250, 'storage_efficiency': 0.90,
        'eauto_annual_km': 10000, 'eauto_consumption_kwh_per_100km': 18.0,
        'eauto_pv_share_percent': 30.0, 'heatpump_cop_factor': 3.5,
        'heatpump_pv_share_percent': 40.0, 'afa_period_years': 20,
        'pvgis_system_loss_default_percent': 14.0, 'annual_module_degradation_percent': 0.5,
        'maintenance_fixed_eur_pa': 50.0, 'maintenance_variable_eur_per_kwp_pa': 5.0,
        'maintenance_increase_percent_pa': 2.0, 'one_time_bonus_eur': 0.0,
        'global_yield_adjustment_percent': 0.0, 'default_specific_yield_kwh_kwp': 950.0,
        'reference_specific_yield_pr': 1100.0,
        'monthly_production_distribution': [0.03, 0.05, 0.08, 0.11, 0.13, 0.14, 0.13, 0.12, 0.09, 0.06, 0.04, 0.02],
        'monthly_consumption_distribution': [0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0837],
        'direct_self_consumption_factor_of_production': 0.25, 'app_debug_mode_enabled': False,
        "visualization_settings": {
            "cost_overview_chart": {  # Beispiel für das Kostenübersichtsdiagramm
                "chart_type": "bar",  # Mögliche Werte: "bar", "pie"
                # Später erweiterbar auf Palettennamen oder spezifische Farben
                "color_palette": "Plotly Standard",
                "primary_color_bar": "#1f77b4",  # Beispiel für Balkendiagramm
                "show_values_on_chart": True
            },
            "consumption_coverage_chart": {
                # Mögliche Werte: "pie", "bar" (ggf. donut)
                "chart_type": "pie",
                "color_palette": "Pastel",
                "show_percentage": True,
                "show_labels": True
            },
            "pv_usage_chart": {
                "chart_type": "pie",
                "color_palette": "Grün-Variationen",
                "show_percentage": True
            },
            "monthly_prod_cons_chart": {
                "chart_type": "line",  # Mögliche Werte: "line", "bar"
                "line_color_production": "#2ca02c",  # Grün
                "line_color_consumption": "#d62728",  # Rot
                "show_markers": True
            },
            "cumulative_cashflow_chart": {
                "chart_type": "line",
                "line_color": "#17becf",  # Cyan
                "show_zero_line": True
            },
            # Corporate CI Paletten (werden von analysis.py optional global
            # gezogen)
            "color_discrete_sequence": [
                "#0F172A",  # slate-900
                "#2563EB",  # blue-600
                "#22C55E",  # green-500
                "#F59E0B",  # amber-500
                "#EF4444",  # red-500
                "#06B6D4",  # cyan-500
                "#8B5CF6",  # violet-500
            ],
            "corporate_palettes": {
                "primary": ["#0F172A", "#334155", "#64748B"],
                "accent": ["#2563EB", "#22C55E", "#F59E0B"],
                "status": {"ok": "#22C55E", "warn": "#F59E0B", "err": "#EF4444"}
            }
            # Hier können später Einstellungen für weitere Diagramme
            # hinzugefügt werden
        },
        "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
        "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],

    },
    "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
    "title_options": ['Dr.', 'Prof.', 'Mag.', 'Ing.', ''],
    'active_company_id': None
}


def get_db_connection() -> sqlite3.Connection | None:
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"FATAL DB Error: {e}")
        traceback.print_exc()
        return None


def get_pdf_template_by_name(
        template_type: str, name: str) -> dict[str, Any] | None:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM pdf_templates WHERE template_type = ? AND name = ?",
            (template_type,
             name))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"DB Fehler get_pdf_template_by_name: {e}")
        return None
    finally:
        if conn:
            conn.close()


def backup_database(backup_path: str) -> bool:
    try:
        import shutil
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, backup_path)
            print(f"DB: Backup erfolgreich erstellt: {backup_path}")
            return True
        print(f"DB: Quelldatei {DB_PATH} existiert nicht für Backup.")
        return False
    except Exception as e:
        print(f"DB Fehler backup_database: {e}")
        return False


def restore_database(backup_path: str) -> bool:
    try:
        import shutil
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, DB_PATH)
            print(f"DB: Wiederherstellung erfolgreich von: {backup_path}")
            return True
        print(f"DB: Backup-Datei {backup_path} existiert nicht.")
        return False
    except Exception as e:
        print(f"DB Fehler restore_database: {e}")
        return False


def export_admin_settings() -> dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM admin_settings")
        settings = {}
        for row in cursor.fetchall():
            key = row['key']
            value = row['value']
            if value and isinstance(value, str) and value.strip().startswith(
                    ('[', '{')) and value.strip().endswith((']', '}')):
                try:
                    settings[key] = json.loads(value)
                except json.JSONDecodeError:
                    settings[key] = value
            else:
                settings[key] = value
        return settings
    except Exception as e:
        print(f"DB Fehler export_admin_settings: {e}")
        return {}
    finally:
        if conn:
            conn.close()

# --- Hersteller-Logos: einfache Key-Value Verwaltung in admin_settings ---


def _ensure_admin_table(conn: sqlite3.Connection) -> None:
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.commit()
    except Exception:
        pass


def save_admin_setting(key: str, value: Any) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        _ensure_admin_table(conn)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO admin_settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key,
             json.dumps(value) if not isinstance(
                 value,
                 str) else value))
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Fehler save_admin_setting: {e}")
        return False
    finally:
        conn.close()


def load_admin_setting(key: str, default: Any = None) -> Any:
    conn = get_db_connection()
    if not conn:
        return default
    try:
        _ensure_admin_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
        row = cur.fetchone()
        if not row:
            return default
        val = row[0]
        try:
            return json.loads(val)
        except Exception:
            return val
    except Exception as e:
        print(f"DB Fehler load_admin_setting: {e}")
        return default
    finally:
        conn.close()


def get_brand_logo(brand_name: str) -> str | None:
    """Liefert Base64-Logo für Marke aus admin_settings (key: brand_logo_<name>) oder brand_logos Tabelle."""
    if not brand_name:
        return None

    # Normalisiere den Brand-Namen für konsistente Suche (entferne Leerzeichen
    # am Anfang/Ende)
    normalized_brand = brand_name.strip()

    # Erst in admin_settings suchen
    key = f"brand_logo_{normalized_brand}"
    val = load_admin_setting(key, None)
    if isinstance(val, str) and val.strip():
        return val

    # Fallback: zentrale Map 'brand_logos' {brand: base64}
    logos = load_admin_setting("brand_logos", {})
    if isinstance(logos, dict):
        # Exakte Suche zuerst
        v = logos.get(normalized_brand)
        if isinstance(v, str) and v.strip():
            return v

        # Falls nicht gefunden, versuche case-insensitive Suche ohne Datennamen
        # zu ändern
        for existing_brand, logo_data in logos.items():
            if existing_brand and normalized_brand.lower() == existing_brand.lower():
                if isinstance(logo_data, str) and logo_data.strip():
                    return logo_data

    # Neuer Fallback: brand_logos Tabelle
    try:
        from brand_logo_db import get_brand_logo as brand_db_get_logo
        logo_data = brand_db_get_logo(normalized_brand)
        if logo_data and logo_data.get('logo_base64'):
            return logo_data['logo_base64']

        # Falls exakte Suche in DB fehlschlägt, versuche case-insensitive ohne
        # Daten zu ändern
        from brand_logo_db import get_all_brand_logos
        all_logos = get_all_brand_logos()
        for logo in all_logos:
            if logo.get('brand_name', '').lower() == normalized_brand.lower():
                return logo.get('logo_base64')

    except Exception:
        pass

    return None


def import_admin_settings(settings: dict[str, Any]) -> bool:
    success_count = 0
    total_count = len(settings)

    for key, value in settings.items():
        if save_admin_setting(key, value):
            success_count += 1
        else:
            print(f"DB: Fehler beim Importieren der Einstellung '{key}'")

    print(
        f"DB: Import abgeschlossen. {success_count}/{total_count} Einstellungen erfolgreich importiert.")
    return success_count == total_count


def get_database_statistics() -> dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {}

    stats = {}
    try:
        cursor = conn.cursor()

        # Admin Settings Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM admin_settings")
        stats['admin_settings_count'] = cursor.fetchone()['count']

        # Products Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['products_count'] = cursor.fetchone()['count']

        # Companies Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        stats['companies_count'] = cursor.fetchone()['count']

        # Company Documents Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM company_documents")
        stats['company_documents_count'] = cursor.fetchone()['count']

        # PDF Templates Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM pdf_templates")
        stats['pdf_templates_count'] = cursor.fetchone()['count']

        # Datenbankgröße
        if os.path.exists(DB_PATH):
            stats['database_size_mb'] = round(
                os.path.getsize(DB_PATH) / (1024 * 1024), 2)
        else:
            stats['database_size_mb'] = 0

        # Schema Version
        cursor.execute("PRAGMA user_version")
        stats['schema_version'] = cursor.fetchone()[0]

        return stats

    except Exception as e:
        print(f"DB Fehler get_database_statistics: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def validate_database_integrity() -> dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {
            "status": "error",
            "message": "Keine Datenbankverbindung möglich"}

    validation_results = {
        "status": "success",
        "errors": [],
        "warnings": [],
        "checks_performed": []
    }

    try:
        cursor = conn.cursor()

        # Check 1: PRAGMA integrity_check
        validation_results["checks_performed"].append(
            "SQLite Integritätsprüfung")
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        if integrity_result[0] != "ok":
            validation_results["errors"].append(
                f"SQLite Integritätsprüfung fehlgeschlagen: {
                    integrity_result[0]}")
            validation_results["status"] = "error"

        # Check 2: Überprüfung Foreign Key Constraints
        validation_results["checks_performed"].append(
            "Foreign Key Constraints")
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            for violation in fk_violations:
                validation_results["errors"].append(
                    f"Foreign Key Verletzung: {violation}")
            validation_results["status"] = "error"

        # Check 3: Verwaiste Company Documents
        validation_results["checks_performed"].append(
            "Verwaiste Company Documents")
        cursor.execute("""
            SELECT cd.id, cd.display_name
            FROM company_documents cd
            LEFT JOIN companies c ON cd.company_id = c.id
            WHERE c.id IS NULL
        """)
        orphaned_docs = cursor.fetchall()
        if orphaned_docs:
            for doc in orphaned_docs:
                validation_results["warnings"].append(
                    f"Verwaistes Dokument: ID {
                        doc['id']}, Name '{
                        doc['display_name']}'")

        # Check 4: Duplikate in Produktnamen
        validation_results["checks_performed"].append("Produkt-Duplikate")
        cursor.execute("""
            SELECT model_name, COUNT(*) as count
            FROM products
            GROUP BY model_name
            HAVING COUNT(*) > 1
        """)
        duplicate_products = cursor.fetchall()
        if duplicate_products:
            for dup in duplicate_products:
                validation_results["warnings"].append(
                    f"Doppelter Produktname: '{
                        dup['model_name']}' ({
                        dup['count']}x)")

        # Check 5: Fehlende Standardfirma
        validation_results["checks_performed"].append("Standard-Firma")
        cursor.execute(
            "SELECT COUNT(*) as count FROM companies WHERE is_default = 1")
        default_company_count = cursor.fetchone()['count']
        if default_company_count == 0:
            validation_results["warnings"].append(
                "Keine Standard-Firma definiert")
        elif default_company_count > 1:
            validation_results["warnings"].append(
                f"Mehrere Standard-Firmen ({default_company_count}) definiert")

        if validation_results["errors"]:
            validation_results["status"] = "error"
        elif validation_results["warnings"]:
            validation_results["status"] = "warning"

        return validation_results

    except Exception as e:
        print(f"DB Fehler validate_database_integrity: {e}")
        return {
            "status": "error",
            "message": f"Fehler bei der Validierung: {str(e)}",
            "errors": [str(e)],
            "warnings": [],
            "checks_performed": []
        }
    finally:
        if conn:
            conn.close()

# Hinzufügen zu database.py


def create_heat_pumps_table(conn):
    """Erstellt die Tabelle für Wärmepumpen, falls sie nicht existiert."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS heat_pumps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL UNIQUE,
                manufacturer TEXT,
                heating_output_kw REAL,
                power_consumption_kw REAL,
                scop REAL, -- Seasonal Coefficient of Performance
                price REAL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Fehler beim Erstellen der heat_pumps-Tabelle: {e}")


def get_all_heat_pumps(conn):
    """Holt alle Wärmepumpen aus der Datenbank."""
    c = conn.cursor()
    c.execute("SELECT * FROM heat_pumps ORDER BY heating_output_kw")
    return c.fetchall()


def add_heat_pump(conn, data):
    """Fügt eine neue Wärmepumpe hinzu."""
    sql = ''' INSERT INTO heat_pumps(model_name, manufacturer, heating_output_kw, power_consumption_kw, scop, price)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid


def update_heat_pump(conn, data):
    """Aktualisiert eine Wärmepumpe."""
    sql = ''' UPDATE heat_pumps
              SET model_name = ?, manufacturer = ?, heating_output_kw = ?, power_consumption_kw = ?, scop = ?, price = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


def delete_heat_pump(conn, id):
    """Löscht eine Wärmepumpe."""
    sql = 'DELETE FROM heat_pumps WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

# Stellen Sie sicher, dass create_heat_pumps_table() beim Initialisieren der DB aufgerufen wird.
# Beispiel im Haupt-DB-Initialisierungsblock:
# conn = create_connection(database_file)
# if conn is not None:
#     create_products_table(conn)
#     create_heat_pumps_table(conn) # HIER HINZUFÜGEN
#     ...


def cleanup_orphaned_files() -> dict[str, Any]:
    cleanup_results = {
        "files_checked": 0,
        "files_removed": 0,
        "errors": [],
        "removed_files": []
    }

    try:
        # Company Documents Verzeichnis prüfen
        if not os.path.exists(COMPANY_DOCS_BASE_DIR):
            return cleanup_results

        # Alle Dateien in DB abrufen
        conn = get_db_connection()
        if not conn:
            cleanup_results["errors"].append("Keine Datenbankverbindung")
            return cleanup_results

        cursor = conn.cursor()
        cursor.execute("SELECT absolute_file_path FROM company_documents")
        db_files = set(row['absolute_file_path'] for row in cursor.fetchall())
        conn.close()

        # Alle physischen Dateien durchgehen
        for root, dirs, files in os.walk(COMPANY_DOCS_BASE_DIR):
            for file in files:
                cleanup_results["files_checked"] += 1
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(
                    full_path, COMPANY_DOCS_BASE_DIR)

                if relative_path not in db_files:
                    try:
                        os.remove(full_path)
                        cleanup_results["files_removed"] += 1
                        cleanup_results["removed_files"].append(relative_path)
                        print(
                            f"DB Cleanup: Verwaiste Datei entfernt: {relative_path}")
                    except Exception as e:
                        cleanup_results["errors"].append(
                            f"Fehler beim Löschen von {relative_path}: {str(e)}")

        # Leere Verzeichnisse entfernen
        for root, dirs, files in os.walk(COMPANY_DOCS_BASE_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(
                            f"DB Cleanup: Leeres Verzeichnis entfernt: {dir_path}")
                except Exception as e:
                    cleanup_results["errors"].append(
                        f"Fehler beim Entfernen des Verzeichnisses {dir_path}: {str(e)}")

        return cleanup_results

    except Exception as e:
        cleanup_results["errors"].append(
            f"Allgemeiner Fehler beim Cleanup: {str(e)}")
        return cleanup_results


def reset_database() -> bool:
    try:
        # Datenbankdatei löschen
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"DB: Datenbankdatei {DB_PATH} gelöscht")

        # Company Documents Verzeichnis löschen
        if os.path.exists(COMPANY_DOCS_BASE_DIR):
            import shutil
            shutil.rmtree(COMPANY_DOCS_BASE_DIR)
            print(
                f"DB: Company Documents Verzeichnis {COMPANY_DOCS_BASE_DIR} gelöscht")

        # Datenbank neu initialisieren
        init_db()
        print("DB: Datenbank erfolgreich zurückgesetzt und neu initialisiert")
        return True

    except Exception as e:
        print(f"DB Fehler reset_database: {e}")
    return False
