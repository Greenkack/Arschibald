"""
Solar Calculator Product Bridge - Verbindung zwischen React Frontend und Python Backend
Ersetzt Mock-Daten durch echte Produktdatenbank
"""
import json
import mimetypes
import os
import sqlite3
from typing import Any


class SolarCalculatorProductBridge:
    """Bridge zwischen React Frontend und Python Produktdatenbank"""

    def __init__(self, db_path: str = None):
        # Use the same database path as the React/Electron app
        if db_path is None:
            import os

            # Use the same path logic as React app connection.ts
            if os.name == 'nt':  # Windows
                user_data = os.environ.get('APPDATA', '')
            else:  # macOS/Linux
                user_data = os.environ.get('HOME', '')
                if user_data:
                    user_data = os.path.join(user_data, '.local', 'share')

            if user_data:
                db_dir = os.path.join(user_data, 'kakerlake', 'data')
                os.makedirs(db_dir, exist_ok=True)
                self.db_path = os.path.join(db_dir, 'app.sqlite')
            else:
                # Fallback to local data directory
                db_dir = 'data'
                os.makedirs(db_dir, exist_ok=True)
                self.db_path = os.path.join(db_dir, 'app.sqlite')
        else:
            self.db_path = db_path

        # Standardisierte Produkt-Key-Reihenfolge (deutsch) – muss app-weit
        # konsistent sein
        self._std_keys: tuple[str, ...] = (
            'id', 'kategorie', 'produkt_modell', 'hersteller', 'preis_stück',
            'pv_modul_leistung', 'kapazitaet_speicher_kwh', 'wr_leistung_kw', 'ladezyklen_speicher',
            'garantie_zeit', 'mass_laenge', 'mass_breite', 'mass_gewicht_kg', 'wirkungsgrad_prozent',
            'hersteller_land', 'beschreibung_info', 'eigenschaft_info', 'spezial_merkmal',
            'rating_null_zehn', 'image_base64', 'created_at', 'updated_at'
        )

    def get_connection(self):
        """Get connection to React database using dynamic path resolution"""
        import os
        import sqlite3

        # Use the same path logic as React app
        if os.name == 'nt':  # Windows
            user_data = os.environ.get('APPDATA', '')
        else:  # macOS/Linux
            user_data = os.environ.get('HOME', '')
            if user_data:
                user_data = os.path.join(user_data, '.local', 'share')

        if user_data:
            db_dir = os.path.join(user_data, 'kakerlake', 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'app.sqlite')
        else:
            # Fallback to local data directory
            db_path = os.path.join('data', 'app.sqlite')
            os.makedirs('data', exist_ok=True)

        return sqlite3.connect(db_path)

    def get_pv_manufacturers(self) -> list[str]:
        """Alle PV Modul Hersteller laden"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Use React schema: products table with 'brand' and 'category'
            # columns
            cursor.execute("""
                SELECT DISTINCT brand
                FROM products
                WHERE (category LIKE '%PV%' OR category LIKE '%modul%' OR category LIKE '%Modul%' OR category = 'PV Modul' OR category = 'pv_modul' OR category = 'PV_Modul' OR category = 'modul' OR category = 'Modul')
                AND brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """)
            return [row[0] for row in cursor.fetchall() if row[0]]
        except Exception:
            # Return empty list on error without printing to stdout
            return []
        finally:
            conn.close()

    # --- Import-Funktionen ---
    @staticmethod
    def _safe_ext(path: str) -> str:
        return (os.path.splitext(path)[1] or '').lower()

    @staticmethod
    def _validate_import_path(
            file_path: str, allowed_exts: tuple[str, ...]) -> tuple[bool, str]:
        try:
            if not file_path or not isinstance(file_path, str):
                return False, "Pfad fehlt"
            p = os.path.abspath(file_path)
            if not os.path.exists(p):
                return False, "Datei existiert nicht"
            ext = (os.path.splitext(p)[1] or '').lower()
            if ext not in allowed_exts:
                return False, f"Unzulässige Dateiendung: {ext}"
            try:
                size = os.path.getsize(p)
                if size > 10 * 1024 * 1024:
                    return False, "Datei zu groß (>10MB)"
            except Exception:
                pass
            return True, p
        except Exception as e:
            return False, f"Pfadprüfung fehlgeschlagen: {e}"

    def import_products_from_file(self,
                                  file_path: str,
                                  company_id: int | None = None,
                                  dry_run: bool = False) -> dict[str,
                                                                 Any]:
        """Importiert Produkte aus CSV/XLSX/JSON in die products-Tabelle mit Feldmapping und Validierung."""
        ok, result = self._validate_import_path(
            file_path, ('.csv', '.xlsx', '.xls', '.json'))
        if not ok:
            return {"success": False, "error": result}

        rows: list[dict[str, Any]] = []
        ext = self._safe_ext(result)
        try:
            if ext in ('.xlsx', '.xls'):
                try:
                    import pandas as pd  # type: ignore
                except Exception:
                    return {"success": False,
                            "error": "pandas nicht verfügbar für Excel-Import"}
                df = pd.read_excel(result)
                rows = df.fillna("")[:10000].to_dict(
                    orient='records')  # Begrenzung
            elif ext == '.csv':
                try:
                    import pandas as pd  # type: ignore
                    df = pd.read_csv(result)
                    rows = df.fillna("")[:20000].to_dict(orient='records')
                except Exception:
                    import csv
                    with open(result, newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for i, r in enumerate(reader):
                            if i >= 20000:
                                break
                            rows.append({k: (v or "") for k, v in r.items()})
            elif ext == '.json':
                with open(result, encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        rows = data[:20000]
                    elif isinstance(data, dict) and 'items' in data and isinstance(data['items'], list):
                        rows = data['items'][:20000]
                    else:
                        return {
                            "success": False,
                            "error": "JSON-Format nicht unterstützt (erwarte Liste)"}
        except Exception as e:
            return {"success": False, "error": f"Lesefehler: {e}"}

        # Feldmapping: flexible Keys aus deutscher/englischer Herkunft
        def map_row(raw: dict[str, Any]) -> dict[str, Any] | None:
            try:
                # Normalisierte Keys (lower, strip)
                norm = {str(k).strip().lower(): v for k, v in raw.items()}

                def pick(*names: str, default: Any = None):
                    for n in names:
                        if n in norm and norm[n] not in (None, ""):
                            return norm[n]
                    return default
                category = pick('category', 'kategorie')
                model_name = pick(
                    'model_name',
                    'produkt_modell',
                    'modell',
                    'model')
                brand = pick('brand', 'manufacturer', 'hersteller')
                if not category or not model_name:
                    return None
                price = pick(
                    'price_euro',
                    'preis',
                    'preis_stück',
                    'preis_stueck',
                    default=0.0)
                capacity_w = pick(
                    'capacity_w',
                    'pv_modul_leistung',
                    'leistung_w',
                    default=None)
                power_kw = pick('power_kw', 'wr_leistung_kw', default=None)
                storage_kwh = pick(
                    'storage_kwh',
                    'kapazitaet_speicher_kwh',
                    default=None)
                eff = pick(
                    'efficiency_percent',
                    'wirkungsgrad_prozent',
                    default=None)
                warranty = pick(
                    'warranty_years',
                    'garantie_zeit',
                    default=None)
                origin = pick(
                    'origin_country',
                    'hersteller_land',
                    default=None)
                length_m = pick('length_m', 'mass_laenge', default=None)
                width_m = pick('width_m', 'mass_breite', default=None)
                weight_kg = pick('weight_kg', 'mass_gewicht_kg', default=None)
                mapped: dict[str, Any] = {
                    'category': str(category).strip(),
                    'model_name': str(model_name).strip(),
                    'brand': (str(brand).strip() if brand else None),
                    'price_euro': float(price) if str(price).strip() != '' else 0.0,
                }
                if company_id is not None:
                    mapped['company_id'] = int(company_id)
                if capacity_w is not None and str(capacity_w).strip() != '':
                    mapped['capacity_w'] = float(capacity_w)
                if power_kw is not None and str(power_kw).strip() != '':
                    mapped['power_kw'] = float(power_kw)
                if storage_kwh is not None and str(storage_kwh).strip() != '':
                    # Map storage_kwh to storage_power_kw for React schema
                    # compatibility
                    # Keep as storage_kwh for now
                    mapped['storage_kwh'] = float(storage_kwh)
                if eff is not None and str(eff).strip() != '':
                    mapped['efficiency_percent'] = float(eff)
                if warranty is not None and str(warranty).strip() != '':
                    mapped['warranty_years'] = int(float(warranty))
                if origin:
                    mapped['origin_country'] = str(origin)
                if length_m is not None and str(length_m).strip() != '':
                    mapped['length_m'] = float(length_m)
                if width_m is not None and str(width_m).strip() != '':
                    mapped['width_m'] = float(width_m)
                if weight_kg is not None and str(weight_kg).strip() != '':
                    mapped['weight_kg'] = float(weight_kg)
                return mapped
            except Exception:
                return None

        mapped_rows: list[dict[str, Any]] = []
        for r in rows:
            m = map_row(r)
            if m:
                mapped_rows.append(m)

        if dry_run:
            return {"success": True, "dry_run": True, "rows": len(mapped_rows)}

        # Persistenz - Write directly to React database instead of using
        # product_db
        created = 0
        updated = 0
        skipped = 0
        errors: list[str] = []

        # Capture stdout to prevent print statements from corrupting JSON
        # output
        import sys
        from io import StringIO

        old_stdout = sys.stdout

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Ensure products table exists with React schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    model_name TEXT NOT NULL UNIQUE,
                    brand TEXT,
                    price_euro REAL DEFAULT 0,
                    capacity_w REAL,
                    storage_power_kw REAL,
                    power_kw REAL,
                    max_cycles INTEGER,
                    warranty_years INTEGER,
                    length_m REAL,
                    width_m REAL,
                    weight_kg REAL,
                    efficiency_percent REAL,
                    origin_country TEXT,
                    description TEXT DEFAULT '',
                    pros TEXT DEFAULT '',
                    cons TEXT DEFAULT '',
                    rating INTEGER,
                    image_base64 TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    datasheet_link_db_path TEXT,
                    additional_cost_netto REAL,
                    company_id INTEGER,
                    cell_technology TEXT,
                    module_structure TEXT,
                    cell_type TEXT,
                    version TEXT,
                    module_warranty_text TEXT,
                    labor_hours REAL
                )
            ''')

            for item in mapped_rows:
                # Capture stdout for each database operation
                sys.stdout = StringIO()
                try:
                    # Check if product exists by model_name
                    cursor.execute(
                        'SELECT id FROM products WHERE model_name = ?', (item['model_name'],))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing product
                        product_id = existing[0]
                        update_sql = '''
                            UPDATE products SET
                                category = ?, brand = ?, price_euro = ?, capacity_w = ?,
                                storage_power_kw = ?, power_kw = ?, max_cycles = ?, warranty_years = ?,
                                length_m = ?, width_m = ?, weight_kg = ?, efficiency_percent = ?,
                                origin_country = ?, description = ?, pros = ?, cons = ?,
                                rating = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        '''
                        cursor.execute(
                            update_sql,
                            (item.get(
                                'category',
                                ''),
                                item.get(
                                'brand',
                                ''),
                                item.get(
                                'price_euro',
                                0),
                                item.get('capacity_w'),
                                item.get('storage_power_kw'),
                                item.get('power_kw'),
                                item.get('max_cycles'),
                                item.get('warranty_years'),
                                item.get('length_m'),
                                item.get('width_m'),
                                item.get('weight_kg'),
                                item.get('efficiency_percent'),
                                item.get(
                                'origin_country',
                                ''),
                                item.get(
                                'description',
                                ''),
                                item.get(
                                'pros',
                                ''),
                                item.get(
                                'cons',
                                ''),
                                item.get('rating'),
                                product_id))
                        updated += 1
                    else:
                        # Insert new product
                        insert_sql = '''
                            INSERT INTO products (
                                category, model_name, brand, price_euro, capacity_w,
                                storage_power_kw, power_kw, max_cycles, warranty_years,
                                length_m, width_m, weight_kg, efficiency_percent,
                                origin_country, description, pros, cons, rating,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        '''
                        cursor.execute(
                            insert_sql,
                            (item.get(
                                'category',
                                ''),
                                item.get(
                                'model_name',
                                ''),
                                item.get(
                                'brand',
                                ''),
                                item.get(
                                'price_euro',
                                0),
                                item.get('capacity_w'),
                                item.get('storage_power_kw'),
                                item.get('power_kw'),
                                item.get('max_cycles'),
                                item.get('warranty_years'),
                                item.get('length_m'),
                                item.get('width_m'),
                                item.get('weight_kg'),
                                item.get('efficiency_percent'),
                                item.get(
                                'origin_country',
                                ''),
                                item.get(
                                'description',
                                ''),
                                item.get(
                                'pros',
                                ''),
                                item.get(
                                'cons',
                                ''),
                                item.get('rating')))
                        created += 1

                except Exception as e:
                    errors.append(
                        f"Error processing {
                            item.get(
                                'model_name',
                                'unknown')}: {
                            str(e)}")
                    skipped += 1
                finally:
                    sys.stdout = old_stdout  # Restore stdout after each operation

            conn.commit()
            conn.close()

        except Exception as e:
            sys.stdout = old_stdout  # Ensure stdout is always restored
            return {"success": False, "error": f"Database error: {e}"}

        return {"success": True,
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "errors": errors[:5]}

    # --- Einzelprodukt (manuell) anlegen/aktualisieren ---
    def _map_german_product_to_db(
            self, data: dict[str, Any]) -> dict[str, Any]:
        """Mappt deutsche UI-Felder auf die products-Tabellenspalten (englisch)."""
        def _is_blank(v: Any) -> bool:
            if v is None:
                return True
            if isinstance(v, str):
                s = v.strip()
                if s == "":
                    return True
                # '0' gilt als leer/ignorieren
                if s.replace(',', '.').lower() in {"0", "0.0", "0.00"}:
                    return True
                return False
            # Zahl 0 ebenfalls als leer werten
            try:
                if isinstance(v, (int, float)) and float(v) == 0.0:
                    return True
            except Exception:
                pass
            return False

        def g(name: str, *alts: str, default: Any = None):
            for k in (name, *alts):
                if k in data and data[k] not in (None, ""):
                    return data[k]
            return default
        mapped: dict[str, Any] = {
            'category': g('kategorie', 'category', default=''),
            'model_name': g('produkt_modell', 'model_name', 'model', default=''),
            'brand': g('hersteller', 'brand', 'manufacturer', default=None),
            'price_euro': g('preis_stück', 'preis_stueck', 'price_euro', 'price', default=None),
            'capacity_w': g('pv_modul_leistung', 'capacity_w', default=None),
            'power_kw': g('wr_leistung_kw', 'power_kw', default=None),
            'max_cycles': g('ladezyklen_speicher', 'max_cycles', default=None),
            'efficiency_percent': g('wirkungsgrad_prozent', 'efficiency_percent', default=None),
            'warranty_years': g('garantie_zeit', 'warranty_years', default=None),
            'length_m': g('mass_laenge', 'length_m', default=None),
            'width_m': g('mass_breite', 'width_m', default=None),
            'weight_kg': g('mass_gewicht_kg', 'weight_kg', default=None),
            'origin_country': g('hersteller_land', 'origin_country', default=None),
            'description': g('beschreibung_info', 'description', default=None),
            'pros': g('eigenschaft_info', default=None),
            'cons': g('spezial_merkmal', default=None),
            'rating': g('rating_null_zehn', 'rating', default=None),
            'image_base64': g('image_base64', default=None),
        }
        # Speichergröße: falls Kategorie Speicher und keine power_kw gesetzt,
        # aus kapazitaet_speicher_kwh übernehmen
        if (str(mapped.get('category') or '').lower().startswith('batterie')
                or 'speicher' in str(mapped.get('category') or '').lower()):
            kwh = g('kapazitaet_speicher_kwh', 'storage_kwh', default=None)
            if kwh is not None and str(kwh).strip(
            ) != '' and mapped.get('power_kw') in (None, ''):
                try:
                    # bevorzugt spezielles Feld der DB, wenn vorhanden
                    mapped['storage_power_kw'] = float(kwh)
                except Exception:
                    pass
        # Numerics casten, 0 als leer behandeln
        for k in [
            'price_euro',
            'capacity_w',
            'power_kw',
            'storage_power_kw',
            'efficiency_percent',
            'length_m',
            'width_m',
                'weight_kg']:
            v = mapped.get(k)
            if _is_blank(v):
                mapped[k] = None
            else:
                try:
                    mapped[k] = float(str(v).replace(',', '.'))
                except Exception:
                    mapped[k] = None
        for k in ['warranty_years', 'rating', 'max_cycles']:
            v = mapped.get(k)
            if _is_blank(v):
                mapped[k] = None
            else:
                try:
                    mapped[k] = int(float(str(v).replace(',', '.')))
                except Exception:
                    mapped[k] = None
        # Keys mit leerem Inhalt entfernen, außer Pflichtfelder
        for key in list(mapped.keys()):
            if key in ('category', 'model_name'):
                continue
            if mapped[key] in (None, ''):
                del mapped[key]
        return mapped

    def add_product_single(self, data: dict[str, Any]) -> dict[str, Any]:
        """Fügt ein einzelnes Produkt hinzu (deutsche Keys erlaubt)."""
        try:
            import product_db  # type: ignore
        except Exception as e:
            return {
                "success": False,
                "error": f"product_db nicht verfügbar: {e}"}
        mapped = self._map_german_product_to_db(data or {})
        # Pflichtfelder prüfen
        if not mapped.get('category') or not mapped.get('model_name'):
            return {
                "success": False,
                "error": "Pflichtfelder fehlen: kategorie & produkt_modell"}
        new_id = product_db.add_product(mapped)
        if not new_id:
            return {
                "success": False,
                "error": "Produkt konnte nicht angelegt werden (evtl. Duplikat?)"}
        return {"success": True, "id": int(new_id)}

    def update_product_single(self, product_id: int,
                              data: dict[str, Any]) -> dict[str, Any]:
        """Aktualisiert ein einzelnes Produkt per ID (deutsche Keys erlaubt)."""
        try:
            import product_db  # type: ignore
        except Exception as e:
            return {
                "success": False,
                "error": f"product_db nicht verfügbar: {e}"}
        mapped = self._map_german_product_to_db(data or {})
        ok = product_db.update_product(int(product_id), mapped)
        return {"success": bool(ok)}

    # --- Produkte auflisten/löschen ---
    def list_products(self, category: str | None = None,
                      company_id: int | None = None) -> dict[str, Any]:
        """Listet Produkte aus der DB und mappt sie auf standardisierte deutsche Keys.

        Parameter:
        - category: Optional. Wenn gesetzt, filtere nach exakter Kategorie (z.B. 'PV Modul', 'Wechselrichter').
        - company_id: Optional. Wenn gesetzt, filtere nach Firmen-ID (falls Feld in DB vorhanden ist).
        """
        try:
            import product_db  # type: ignore
        except Exception as e:
            return {
                "success": False,
                "error": f"product_db nicht verfügbar: {e}",
                "items": []}

        try:
            rows = product_db.list_products(
                category=category, company_id=company_id)
        except Exception as e:
            return {"success": False, "error": str(e), "items": []}

        std_items: list[dict[str, Any]] = []
        for r in rows:
            try:
                cat = r.get('category') or ''
                brand = r.get('brand') or r.get('manufacturer') or ''
                std_items.append(self._to_standard_product_dict(cat, brand, r))
            except Exception:
                # Fallback: rohen Datensatz durchreichen
                std_items.append(r)

        return {"success": True, "items": std_items}

    def delete_product_single(self, product_id: int) -> dict[str, Any]:
        """Löscht ein einzelnes Produkt per ID."""
        try:
            import product_db  # type: ignore
        except Exception as e:
            return {
                "success": False,
                "error": f"product_db nicht verfügbar: {e}"}
        try:
            pid = int(product_id)
            if pid <= 0:
                return {"success": False, "error": "Ungültige ID"}
        except Exception:
            return {"success": False, "error": "Ungültige ID"}
        ok = product_db.delete_product(pid)
        return {"success": bool(ok)}

    def import_customers_from_file(
            self, file_path: str, dry_run: bool = False) -> dict[str, Any]:
        """Importiert Kunden aus CSV/XLSX/JSON. Nutzt crm.py wenn möglich."""
        ok, result = self._validate_import_path(
            file_path, ('.csv', '.xlsx', '.xls', '.json'))
        if not ok:
            return {"success": False, "error": result}

        rows: list[dict[str, Any]] = []
        ext = self._safe_ext(result)
        try:
            if ext in ('.xlsx', '.xls'):
                try:
                    import pandas as pd  # type: ignore
                except Exception:
                    return {"success": False,
                            "error": "pandas nicht verfügbar für Excel-Import"}
                df = pd.read_excel(result)
                rows = df.fillna("")[:20000].to_dict(orient='records')
            elif ext == '.csv':
                try:
                    import pandas as pd  # type: ignore
                    df = pd.read_csv(result)
                    rows = df.fillna("")[:20000].to_dict(orient='records')
                except Exception:
                    import csv
                    with open(result, newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for i, r in enumerate(reader):
                            if i >= 20000:
                                break
                            rows.append({k: (v or "") for k, v in r.items()})
            elif ext == '.json':
                with open(result, encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        rows = data[:20000]
                    elif isinstance(data, dict) and 'items' in data and isinstance(data['items'], list):
                        rows = data['items'][:20000]
                    else:
                        return {
                            "success": False,
                            "error": "JSON-Format nicht unterstützt (erwarte Liste)"}
        except Exception as e:
            return {"success": False, "error": f"Lesefehler: {e}"}

        def map_customer(raw: dict[str, Any]) -> dict[str, Any] | None:
            try:
                n = {str(k).strip().lower(): v for k, v in raw.items()}

                def pick(*names: str, default: Any = None):
                    for nm in names:
                        if nm in n and n[nm] not in (None, ""):
                            return n[nm]
                    return default
                first = pick('first_name', 'vorname')
                last = pick('last_name', 'nachname', 'name')
                email = pick('email', 'e-mail')
                phone = pick('phone', 'telefon', 'tel')
                if not first or not last:
                    return None
                cust: dict[str, Any] = {
                    'first_name': str(first).strip(),
                    'last_name': str(last).strip(),
                }
                if email:
                    cust['email'] = str(email).strip()
                if phone:
                    cust['phone'] = str(phone).strip()
                for k_src, k_dst in [
                    ('salutation', 'salutation'), ('anrede', 'salutation'),
                    ('title', 'title'), ('titel', 'title'),
                    ('company', 'company_name'), ('firma', 'company_name'),
                    ('street', 'street'), ('straße', 'street'), ('strasse', 'street'),
                    ('zip', 'zip'), ('plz', 'zip'),
                    ('city', 'city'), ('ort', 'city'),
                ]:
                    v = n.get(k_src)
                    if v not in (None, ""):
                        cust[k_dst] = v
                return cust
            except Exception:
                return None

        mapped: list[dict[str, Any]] = []
        for r in rows:
            m = map_customer(r)
            if m:
                mapped.append(m)

        if dry_run:
            return {"success": True, "dry_run": True, "rows": len(mapped)}

        created = 0
        updated = 0
        skipped = 0
        errors: list[str] = []
        try:
            from crm import create_tables_crm
            from crm import save_customer as crm_save_customer  # type: ignore
            from database import get_db_connection  # type: ignore
            conn = get_db_connection()
            if conn is None:
                raise RuntimeError("DB Verbindung nicht verfügbar")
            create_tables_crm(conn)
            for c in mapped:
                try:
                    # Deduplizierung via (first_name, last_name, email) wenn
                    # möglich
                    cur = conn.cursor()
                    email_v = c.get('email')
                    if email_v:
                        cur.execute(
                            "SELECT id FROM customers WHERE first_name=? AND last_name=? AND email=?",
                            (c['first_name'],
                             c['last_name'],
                                email_v))
                    else:
                        cur.execute(
                            "SELECT id FROM customers WHERE first_name=? AND last_name=?",
                            (c['first_name'],
                             c['last_name']))
                    row = cur.fetchone()
                    if row:
                        c_update = c.copy()
                        c_update['id'] = int(row[0])
                        _id = crm_save_customer(conn, c_update)
                        updated += 1 if _id else 0
                    else:
                        _id = crm_save_customer(conn, c)
                        created += 1 if _id else 0
                except Exception as ie:
                    skipped += 1
                    errors.append(str(ie))
            conn.close()
        except Exception:
            # Fallback: Minimal-Insert in customers
            try:
                conn_fb = self.get_connection()
                cur = conn_fb.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, email TEXT, phone TEXT)")
                for c in mapped:
                    try:
                        if c.get('email'):
                            cur.execute(
                                "SELECT id FROM customers WHERE first_name=? AND last_name=? AND email=?",
                                (c['first_name'],
                                 c['last_name'],
                                    c['email']))
                        else:
                            cur.execute(
                                "SELECT id FROM customers WHERE first_name=? AND last_name=?",
                                (c['first_name'],
                                 c['last_name']))
                        row = cur.fetchone()
                        if row:
                            sets = ", ".join(
                                [f"{k}=?" for k in c.keys() if k != 'id'])
                            cur.execute(f"UPDATE customers SET {sets} WHERE id=?", [
                                        *([c[k] for k in c.keys() if k != 'id']), int(row[0])])
                            updated += 1
                        else:
                            cols = list(c.keys())
                            placeholders = ",".join(["?"] * len(cols))
                            cur.execute(
                                f"INSERT INTO customers ({
                                    ', '.join(cols)}) VALUES ({placeholders})", [
                                    c[k] for k in cols])
                            created += 1
                    except Exception as ie2:
                        skipped += 1
                        errors.append(str(ie2))
                conn_fb.commit()
                conn_fb.close()
            except Exception as e2:
                return {
                    "success": False,
                    "error": f"Import fehlgeschlagen: {e2}"}

        return {"success": True,
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "errors": errors[:5]}

    def add_customer_document_from_path(self,
                                        customer_id: int,
                                        project_id: int | None,
                                        file_path: str,
                                        display_name: str | None,
                                        doc_type: str = "other") -> dict[str,
                                                                         Any]:
        """Liest eine Datei von der Platte und speichert sie als Kundendokument über database.add_customer_document mit Whitelist/Limit."""
        allowed = ('.pdf', '.png', '.jpg', '.jpeg')
        ok, result = self._validate_import_path(file_path, allowed)
        if not ok:
            return {"success": False, "error": result}
        ext = self._safe_ext(result)
        mime, _ = mimetypes.guess_type(result)
        try:
            with open(result, 'rb') as f:
                data = f.read()
            from database import add_customer_document  # type: ignore
            doc_id = add_customer_document(
                int(customer_id),
                data,
                display_name or os.path.basename(result),
                doc_type=doc_type,
                project_id=int(project_id) if project_id is not None else None,
                suggested_filename=os.path.basename(result))
            if not doc_id:
                return {
                    "success": False,
                    "error": "Dokument konnte nicht gespeichert werden"}
            return {
                "success": True,
                "document_id": int(doc_id),
                "mime": mime or '',
                "ext": ext}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_pv_models_by_manufacturer(self, manufacturer: str) -> list[dict]:
        """PV Module nach Hersteller mit allen Eigenschaften"""
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Use React schema: products table with standardized columns
            cursor.execute(
                """
                SELECT id, category, model_name, brand, price_euro,
                       capacity_w, power_kw, efficiency_percent, length_m, width_m, weight_kg,
                       warranty_years, origin_country, description, created_at, updated_at
                FROM products
                WHERE brand = ? AND (category LIKE '%PV%' OR category LIKE '%modul%' OR category LIKE '%Modul%' OR category = 'pv_modul' OR category = 'PV_Modul' OR category = 'modul' OR category = 'Modul')
                ORDER BY model_name
                """,
                [manufacturer],
            )

            results: list[dict[str, Any]] = []
            for row in cursor.fetchall():
                d = dict(row)
                std = self._to_standard_product_dict(
                    'PV Modul', manufacturer, d)
                results.append(std)

            return results

        except Exception:
            # Return empty list on error without printing to stdout
            return []
        finally:
            conn.close()

    def get_inverter_manufacturers(self) -> list[str]:
        """Wechselrichter Hersteller"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT brand
                FROM products
                WHERE category LIKE '%Wechselrichter%' OR category LIKE '%Inverter%'
                AND brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """)
            return [row[0] for row in cursor.fetchall() if row[0]]
        except Exception:
            return []
        finally:
            conn.close()

    def get_inverter_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Wechselrichter nach Hersteller"""
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Use React schema: products table with standardized columns
            cursor.execute(
                """
                SELECT id, category, model_name, brand, price_euro,
                       capacity_w, power_kw, efficiency_percent, length_m, width_m, weight_kg,
                       warranty_years, origin_country, description, created_at, updated_at
                FROM products
                WHERE brand = ? AND (category LIKE '%Wechselrichter%' OR category LIKE '%Inverter%')
                ORDER BY model_name
                """,
                [manufacturer],
            )

            results: list[dict[str, Any]] = []
            for row in cursor.fetchall():
                d = dict(row)
                std = self._to_standard_product_dict(
                    'Wechselrichter', manufacturer, d)
                results.append(std)

            return results

        except Exception:
            # Return empty list on error without printing to stdout
            return []
        finally:
            conn.close()

    def get_storage_manufacturers(self) -> list[str]:
        """Batteriespeicher Hersteller"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT brand
                FROM products
                WHERE category LIKE '%Speicher%' OR category LIKE '%Batter%'
                AND brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """)
            return [row[0] for row in cursor.fetchall() if row[0]]
        except Exception:
            return []
        finally:
            conn.close()

    def get_storage_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Batteriespeicher nach Hersteller"""
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Use React schema: products table with standardized columns
            cursor.execute(
                """
                SELECT id, category, model_name, brand, price_euro,
                       capacity_w, power_kw, efficiency_percent, length_m, width_m, weight_kg,
                       warranty_years, origin_country, description, storage_power_kw,
                       created_at, updated_at
                FROM products
                WHERE brand = ? AND (category LIKE '%Speicher%' OR category LIKE '%Batter%')
                ORDER BY model_name
                """,
                [manufacturer],
            )

            results: list[dict[str, Any]] = []
            for row in cursor.fetchall():
                d = dict(row)
                # Map storage_power_kw to German schema fields
                if d.get('storage_power_kw') is not None:
                    d['kapazitaet_speicher_kwh'] = d['storage_power_kw']
                std = self._to_standard_product_dict(
                    'Batteriespeicher', manufacturer, d)
                # Fix storage_kwh from database storage_power_kw field
                if d.get('storage_power_kw') and d.get('storage_power_kw') > 0:
                    std['storage_kwh'] = d['storage_power_kw']
                    std['kapazitaet_speicher_kwh'] = d['storage_power_kw']
                results.append(std)

            return results

        except Exception:
            # Return empty list on error without printing to stdout
            return []
        finally:
            conn.close()

    def export_for_react(self) -> dict:
        """Export aller Produkte für React Frontend"""
        return {
            'pv_manufacturers': self.get_pv_manufacturers(),
            'inverter_manufacturers': self.get_inverter_manufacturers(),
            'storage_manufacturers': self.get_storage_manufacturers(),
        }

    def get_wallbox_manufacturers(self) -> list[str]:
        """Wallbox Hersteller"""
        return self._get_manufacturers_by_category('Wallbox')

    def get_wallbox_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Wallbox nach Hersteller"""
        return self._get_models_by_manufacturer('Wallbox', manufacturer)

    def get_ems_manufacturers(self) -> list[str]:
        """Energiemanagementsystem Hersteller"""
        return self._get_manufacturers_by_category('Energiemanagementsystem')

    def get_ems_models_by_manufacturer(self, manufacturer: str) -> list[dict]:
        """EMS nach Hersteller"""
        return self._get_models_by_manufacturer(
            'Energiemanagementsystem', manufacturer)

    def get_optimizer_manufacturers(self) -> list[str]:
        """Leistungsoptimierer Hersteller"""
        return self._get_manufacturers_by_category('Leistungsoptimierer')

    def get_optimizer_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Optimizer nach Hersteller"""
        return self._get_models_by_manufacturer(
            'Leistungsoptimierer', manufacturer)

    def get_carport_manufacturers(self) -> list[str]:
        """Carport Hersteller"""
        return self._get_manufacturers_by_category('Carport')

    def get_carport_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Carport nach Hersteller"""
        return self._get_models_by_manufacturer('Carport', manufacturer)

    def get_emergency_power_manufacturers(self) -> list[str]:
        """Notstromversorgung Hersteller"""
        return self._get_manufacturers_by_category('Notstromversorgung')

    def get_emergency_power_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Notstromversorgung nach Hersteller"""
        return self._get_models_by_manufacturer(
            'Notstromversorgung', manufacturer)

    def get_animal_protection_manufacturers(self) -> list[str]:
        """Tierabwehrschutz Hersteller"""
        return self._get_manufacturers_by_category('Tierabwehrschutz')

    def get_animal_protection_models_by_manufacturer(
            self, manufacturer: str) -> list[dict]:
        """Tierabwehrschutz nach Hersteller"""
        return self._get_models_by_manufacturer(
            'Tierabwehrschutz', manufacturer)

    def _get_manufacturers_by_category(self, category: str) -> list[str]:
        """Generische Funktion für Hersteller nach Kategorie"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # products_complete zuerst
            try:
                cursor.execute("""
                    SELECT DISTINCT hersteller
                    FROM products_complete
                    WHERE kategorie = ?
                    ORDER BY hersteller
                """, [category])
                manufacturers = [row[0] for row in cursor.fetchall()]
                if manufacturers:
                    return manufacturers
            except BaseException:
                pass

            # Fallback
            cursor.execute("""
                SELECT DISTINCT manufacturer
                FROM products
                WHERE category = ?
                ORDER BY manufacturer
            """, [category])
            return [row[0] for row in cursor.fetchall()]
        except BaseException:
            return []
        finally:
            conn.close()

    def _get_models_by_manufacturer(
            self,
            category: str,
            manufacturer: str) -> list[dict]:
        """Generische Funktion für Modelle nach Hersteller und Kategorie"""
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # products_complete
            try:
                cursor.execute(
                    """
                    SELECT
                        id, kategorie, produkt_modell, hersteller, preis_stück,
                        pv_modul_leistung, kapazitaet_speicher_kwh, wr_leistung_kw, ladezyklen_speicher,
                        garantie_zeit, mass_laenge, mass_breite, mass_gewicht_kg, wirkungsgrad_prozent,
                        hersteller_land, beschreibung_info, eigenschaft_info, spezial_merkmal,
                        rating_null_zehn, image_base64, created_at, updated_at
                    FROM products_complete
                    WHERE kategorie = ? AND hersteller = ?
                    ORDER BY produkt_modell
                    """,
                    [category, manufacturer],
                )

                results: list[dict[str, Any]] = []
                for row in cursor.fetchall():
                    d = dict(row)
                    std = self._to_standard_product_dict(
                        category, manufacturer, d)
                    results.append(std)

                if results:
                    return results
            except BaseException:
                pass

            # Fallback
            cursor.execute(
                """
                SELECT id, category, model_name, manufacturer, price_euro,
                       capacity_w, power_kw, efficiency_percent, length_m, width_m, weight_kg,
                       warranty_years, origin_country, description, created_at, updated_at
                FROM products
                WHERE manufacturer = ? AND category = ?
                ORDER BY model_name
                """,
                [manufacturer, category],
            )

            results: list[dict[str, Any]] = []
            for row in cursor.fetchall():
                d = dict(row)
                std = self._to_standard_product_dict(category, manufacturer, d)
                results.append(std)

            return results

        except Exception:
            # Return empty list on error without printing to stdout
            return []
        finally:
            conn.close()

    # --- Mapping-Helfer: Standardisierte Keys + Legacy-Aliase ---
    def _to_standard_product_dict(self,
                                  category: str,
                                  manufacturer: str,
                                  src: dict[str,
                                            Any]) -> dict[str,
                                                          Any]:
        """Erstellt einen dict mit den geforderten deutschen Keys in fester Reihenfolge und ergänzt Legacy-Felder.

        - src kann aus products_complete (deutsche Spalten) oder products (englische Spalten) stammen.
        - Fehlende Felder werden sinnvoll belegt (0/None/''), die Key-Reihenfolge bleibt erhalten.
        - Zusätzlich werden Legacy-Aliase ('model', 'brand', 'category', ...) ergänzt, um bestehende UI zu stützen.
        """
        # Quelle normalisieren
        def val(*names: str, default: Any = None) -> Any:
            for n in names:
                if n in src and src[n] not in (None, ''):
                    return src[n]
            return default

        # Deutsche Standard-Felder zusammenbauen (Insertion-Order == gewünschte
        # Reihenfolge)
        std: dict[str, Any] = {}
        std['id'] = val('id', default=None)
        std['kategorie'] = val('kategorie', 'category', default=category)
        std['produkt_modell'] = val(
            'produkt_modell',
            'model_name',
            'model',
            default='')
        std['hersteller'] = val(
            'hersteller',
            'manufacturer',
            'brand',
            default=manufacturer)
        std['preis_stück'] = val(
            'preis_stück',
            'price_euro',
            'price',
            default=0)
        std['pv_modul_leistung'] = val(
            'pv_modul_leistung', 'capacity_w', default=None)
        # Speicher kWh: products_complete hat kapazitaet_speicher_kwh; fallback
        # products nutzt häufig power_kw für Speichergröße
        std['kapazitaet_speicher_kwh'] = val(
            'kapazitaet_speicher_kwh',
            default=val(
                'storage_kwh',
                'storage_power_kw',
                'power_kw',
                default=None))
        std['wr_leistung_kw'] = val('wr_leistung_kw', 'power_kw', default=None)
        std['ladezyklen_speicher'] = val(
            'ladezyklen_speicher', 'max_cycles', default=None)
        std['garantie_zeit'] = val(
            'garantie_zeit',
            'warranty_years',
            default=None)
        std['mass_laenge'] = val('mass_laenge', 'length_m', default=None)
        std['mass_breite'] = val('mass_breite', 'width_m', default=None)
        std['mass_gewicht_kg'] = val(
            'mass_gewicht_kg', 'weight_kg', default=None)
        std['wirkungsgrad_prozent'] = val(
            'wirkungsgrad_prozent',
            'efficiency_percent',
            default=None)
        std['hersteller_land'] = val(
            'hersteller_land',
            'origin_country',
            default=None)
        std['beschreibung_info'] = val(
            'beschreibung_info', 'description', default='')
        std['eigenschaft_info'] = val('eigenschaft_info', default='')
        std['spezial_merkmal'] = val(
            'spezial_merkmal', 'special_features', default='')
        std['rating_null_zehn'] = val(
            'rating_null_zehn', 'rating', default=None)
        std['image_base64'] = val('image_base64', default=None)
        std['created_at'] = val('created_at', default=None)
        std['updated_at'] = val('updated_at', default=None)

        # Legacy-Aliase für bestehende UI (kann später entfernt werden, sobald
        # Frontend migriert ist)
        std.setdefault('category', std['kategorie'])
        std.setdefault('model', std['produkt_modell'])
        std.setdefault('brand', std['hersteller'])
        std.setdefault('price', std['preis_stück'])
        std.setdefault('capacity_w', std['pv_modul_leistung'])
        std.setdefault('storage_kwh', std['kapazitaet_speicher_kwh'])
        std.setdefault('power_kw', std['wr_leistung_kw'])
        std.setdefault('efficiency', std['wirkungsgrad_prozent'])
        std.setdefault('warranty_years', std['garantie_zeit'])
        std.setdefault('length_m', std['mass_laenge'])
        std.setdefault('width_m', std['mass_breite'])
        std.setdefault('weight_kg', std['mass_gewicht_kg'])
        std.setdefault('origin', std['hersteller_land'])
        std.setdefault('description', std['beschreibung_info'])
        std.setdefault('special_features', std['spezial_merkmal'])

        return std

    def save_solar_configuration(self, config_data: dict) -> bool:
        """Speichere Solar-Konfiguration für Berechnungen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Erstelle solar_configurations Tabelle falls nicht vorhanden
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solar_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    module_qty INTEGER,
                    module_brand TEXT,
                    module_model TEXT,
                    module_product_id INTEGER,
                    inverter_brand TEXT,
                    inverter_model TEXT,
                    inverter_product_id INTEGER,
                    inverter_qty INTEGER DEFAULT 1,
                    with_storage BOOLEAN DEFAULT 0,
                    storage_brand TEXT,
                    storage_model TEXT,
                    storage_product_id INTEGER,
                    wallbox_enabled BOOLEAN DEFAULT 0,
                    wallbox_brand TEXT,
                    wallbox_model TEXT,
                    wallbox_product_id INTEGER,
                    ems_enabled BOOLEAN DEFAULT 0,
                    ems_brand TEXT,
                    ems_model TEXT,
                    ems_product_id INTEGER,
                    optimizer_enabled BOOLEAN DEFAULT 0,
                    optimizer_brand TEXT,
                    optimizer_model TEXT,
                    optimizer_product_id INTEGER,
                    carport_enabled BOOLEAN DEFAULT 0,
                    carport_brand TEXT,
                    carport_model TEXT,
                    carport_product_id INTEGER,
                    emergency_power_enabled BOOLEAN DEFAULT 0,
                    emergency_power_brand TEXT,
                    emergency_power_model TEXT,
                    emergency_power_product_id INTEGER,
                    animal_protection_enabled BOOLEAN DEFAULT 0,
                    animal_protection_brand TEXT,
                    animal_protection_model TEXT,
                    animal_protection_product_id INTEGER,
                    total_kwp REAL,
                    estimated_annual_yield_kwh REAL,
                    calculation_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Konfiguration speichern
            cursor.execute("""
                INSERT INTO solar_configurations (
                    project_id, module_qty, module_brand, module_model, module_product_id,
                    inverter_brand, inverter_model, inverter_product_id, inverter_qty,
                    with_storage, storage_brand, storage_model, storage_product_id,
                    wallbox_enabled, wallbox_brand, wallbox_model, wallbox_product_id,
                    ems_enabled, ems_brand, ems_model, ems_product_id,
                    optimizer_enabled, optimizer_brand, optimizer_model, optimizer_product_id,
                    carport_enabled, carport_brand, carport_model, carport_product_id,
                    emergency_power_enabled, emergency_power_brand, emergency_power_model, emergency_power_product_id,
                    animal_protection_enabled, animal_protection_brand, animal_protection_model, animal_protection_product_id,
                    total_kwp, estimated_annual_yield_kwh
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config_data.get('project_id', 1),
                config_data.get('module_qty', 0),
                config_data.get('module_brand', ''),
                config_data.get('module_model', ''),
                config_data.get('module_product_id', 0),
                config_data.get('inverter_brand', ''),
                config_data.get('inverter_model', ''),
                config_data.get('inverter_product_id', 0),
                config_data.get('inverter_qty', 1),
                config_data.get('with_storage', False),
                config_data.get('storage_brand', ''),
                config_data.get('storage_model', ''),
                config_data.get('storage_product_id', 0),
                config_data.get('wallbox_enabled', False),
                config_data.get('wallbox_brand', ''),
                config_data.get('wallbox_model', ''),
                config_data.get('wallbox_product_id', 0),
                config_data.get('ems_enabled', False),
                config_data.get('ems_brand', ''),
                config_data.get('ems_model', ''),
                config_data.get('ems_product_id', 0),
                config_data.get('optimizer_enabled', False),
                config_data.get('optimizer_brand', ''),
                config_data.get('optimizer_model', ''),
                config_data.get('optimizer_product_id', 0),
                config_data.get('carport_enabled', False),
                config_data.get('carport_brand', ''),
                config_data.get('carport_model', ''),
                config_data.get('carport_product_id', 0),
                config_data.get('emergency_power_enabled', False),
                config_data.get('emergency_power_brand', ''),
                config_data.get('emergency_power_model', ''),
                config_data.get('emergency_power_product_id', 0),
                config_data.get('animal_protection_enabled', False),
                config_data.get('animal_protection_brand', ''),
                config_data.get('animal_protection_model', ''),
                config_data.get('animal_protection_product_id', 0),
                config_data.get('total_kwp', 0.0),
                config_data.get('estimated_annual_yield_kwh', 0.0)
            ))

            conn.commit()
            return True

        except Exception:
            # Error saving - return False without printing to stdout
            return False
        finally:
            conn.close()

# API Endpoints für React Integration


def create_product_api_file():
    """Erstellt API-File für React Bridge"""
    api_content = """
// Solar Calculator Product API Bridge
// Diese Datei wird von Python generiert und von React importiert

import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);
const pythonScript = path.join(process.cwd(), 'solar_calculator_bridge.py');

// Standardisiertes Produktmodell (deutsche Keys)
export interface ProductModel {
    id: number;
    kategorie: string;
    produkt_modell: string;
    hersteller: string;
    preis_stück?: number;
    pv_modul_leistung?: number;
    kapazitaet_speicher_kwh?: number;
    wr_leistung_kw?: number;
    ladezyklen_speicher?: number;
    garantie_zeit?: number;
    mass_laenge?: number;
    mass_breite?: number;
    mass_gewicht_kg?: number;
    wirkungsgrad_prozent?: number;
    hersteller_land?: string;
    beschreibung_info?: string;
    eigenschaft_info?: string;
    spezial_merkmal?: string;
    rating_null_zehn?: number;
    image_base64?: string | null;
    created_at?: string | null;
    updated_at?: string | null;
}

export class SolarProductAPI {
  static async getPVManufacturers(): Promise<string[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_pv_manufacturers`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading PV manufacturers:', error);
      return [];
    }
  }

  static async getPVModelsByManufacturer(manufacturer: string): Promise<ProductModel[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_pv_models "${manufacturer}"`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading PV models:', error);
      return [];
    }
  }

  static async getInverterManufacturers(): Promise<string[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_inverter_manufacturers`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading inverter manufacturers:', error);
      return [];
    }
  }

  static async getInverterModelsByManufacturer(manufacturer: string): Promise<ProductModel[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_inverter_models "${manufacturer}"`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading inverter models:', error);
      return [];
    }
  }

  static async getStorageManufacturers(): Promise<string[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_storage_manufacturers`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading storage manufacturers:', error);
      return [];
    }
  }

  static async getStorageModelsByManufacturer(manufacturer: string): Promise<ProductModel[]> {
    try {
      const { stdout } = await execAsync(`python "${pythonScript}" get_storage_models "${manufacturer}"`);
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('Error loading storage models:', error);
      return [];
    }
  }
}
"""

    with open("apps/renderer/src/lib/solarProductAPI.ts", "w", encoding="utf-8") as f:
        f.write(api_content)


if __name__ == "__main__":
    import sys

    bridge = SolarCalculatorProductBridge()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "get_pv_manufacturers":
            print(json.dumps(bridge.get_pv_manufacturers()))
        elif command == "get_pv_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_pv_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_inverter_manufacturers":
            print(json.dumps(bridge.get_inverter_manufacturers()))
        elif command == "get_inverter_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_inverter_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_storage_manufacturers":
            print(json.dumps(bridge.get_storage_manufacturers()))
        elif command == "get_storage_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_storage_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_wallbox_manufacturers":
            print(json.dumps(bridge.get_wallbox_manufacturers()))
        elif command == "get_wallbox_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_wallbox_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_ems_manufacturers":
            print(json.dumps(bridge.get_ems_manufacturers()))
        elif command == "get_ems_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_ems_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_optimizer_manufacturers":
            print(json.dumps(bridge.get_optimizer_manufacturers()))
        elif command == "get_optimizer_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_optimizer_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_carport_manufacturers":
            print(json.dumps(bridge.get_carport_manufacturers()))
        elif command == "get_carport_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_carport_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_emergency_power_manufacturers":
            print(json.dumps(bridge.get_emergency_power_manufacturers()))
        elif command == "get_emergency_power_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_emergency_power_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "get_animal_protection_manufacturers":
            print(json.dumps(bridge.get_animal_protection_manufacturers()))
        elif command == "get_animal_protection_models" and len(sys.argv) > 2:
            print(
                json.dumps(
                    bridge.get_animal_protection_models_by_manufacturer(
                        sys.argv[2])))
        elif command == "save_config" and len(sys.argv) > 2:
            config_json = sys.argv[2]
            config_data = json.loads(config_json)
            success = bridge.save_solar_configuration(config_data)
            print(json.dumps({"success": success}))
        # --- Imports ---
        elif command == "import_products_from_file" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])

                # Handle bytes data (from file upload)
                if 'data' in payload and 'filename' in payload:
                    import os
                    import tempfile

                    # Create temporary file with the uploaded data
                    file_extension = payload.get('file_extension', 'xlsx')
                    temp_filename = f"temp_upload.{file_extension}"
                    temp_path = os.path.join(
                        tempfile.gettempdir(), temp_filename)

                    # Convert data array back to bytes and write to temp file
                    data_bytes = bytes(payload['data'])
                    with open(temp_path, 'wb') as temp_file:
                        temp_file.write(data_bytes)

                    try:
                        res = bridge.import_products_from_file(
                            temp_path,
                            company_id=payload.get('company_id'),
                            dry_run=bool(payload.get('dry_run', False))
                        )
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    # Handle file path (existing functionality)
                    res = bridge.import_products_from_file(
                        payload.get('file_path', ''),
                        company_id=payload.get('company_id'),
                        dry_run=bool(payload.get('dry_run', False))
                    )

                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        elif command == "import_customers_from_file" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
                res = bridge.import_customers_from_file(
                    payload.get(
                        'file_path', ''), dry_run=bool(
                        payload.get(
                            'dry_run', False)))
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        elif command == "add_customer_document_from_path" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
                res = bridge.add_customer_document_from_path(
                    int(
                        payload.get('customer_id')), payload.get('project_id'), payload.get(
                        'file_path', ''), payload.get('display_name'), payload.get(
                        'doc_type', 'other'))
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        elif command == "add_product_single" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
                res = bridge.add_product_single(payload)
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        elif command == "update_product_single" and len(sys.argv) > 3:
            try:
                pid = int(sys.argv[2])
                payload = json.loads(sys.argv[3])
                res = bridge.update_product_single(pid, payload)
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        elif command == "products_list":
            try:
                payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
                category = payload.get('category')
                company_id = payload.get('company_id')
                res = bridge.list_products(
                    category=category, company_id=company_id)
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps(
                    {"success": False, "error": str(e), "items": []}))
        elif command == "delete_product_single" and len(sys.argv) > 2:
            try:
                pid = int(sys.argv[2])
                res = bridge.delete_product_single(pid)
                print(json.dumps(res, default=str))
            except Exception as e:
                print(json.dumps({"success": False, "error": str(e)}))
        # --- CRM/Projects bridges ---
        elif command == "crm_list_customers":
            try:
                # Use database.get_db_connection if available for consistent
                # config
                try:
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                except Exception:
                    conn = bridge.get_connection()
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM customers ORDER BY id DESC").fetchall()
                print(json.dumps([dict(r) for r in rows], default=str))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_get_customer" and len(sys.argv) > 2:
            try:
                cid = int(sys.argv[2])
                try:
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                except Exception:
                    conn = bridge.get_connection()
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT * FROM customers WHERE id = ?", (cid,))
                row = cur.fetchone()
                print(json.dumps(dict(row) if row else None, default=str))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_save_customer" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
                # Basic input sanitation
                if not isinstance(payload, dict):
                    raise ValueError("Invalid payload")
                for k in ["first_name", "last_name"]:
                    if k in payload and isinstance(payload[k], str):
                        payload[k] = payload[k].strip()
                try:
                    from crm import create_tables_crm
                    from crm import save_customer as crm_save_customer  # type: ignore
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    create_tables_crm(conn)
                    new_id = crm_save_customer(conn, payload)
                    print(json.dumps({"id": new_id}))
                except Exception:
                    # Fallback minimal insert/update
                    conn = bridge.get_connection()
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cols = []
                    vals: list[Any] = []
                    now = None
                    try:
                        from datetime import datetime as _dt
                        now = _dt.now().isoformat()
                    except Exception:
                        now = None
                    payload = payload.copy()
                    if now:
                        payload.setdefault('last_updated', now)
                        payload.setdefault('creation_date', now)
                    if payload.get('id'):
                        cid = int(payload['id'])
                        data = {k: v for k, v in payload.items() if k != 'id'}
                        sets = ", ".join([f"{k}=?" for k in data])
                        cur.execute(
                            f"UPDATE customers SET {sets} WHERE id=?", [
                                *data.values(), cid])
                        conn.commit()
                        print(json.dumps({"id": cid}))
                    else:
                        cols = list(payload.keys())
                        vals = [payload[k] for k in cols]
                        placeholders = ",".join(["?"] * len(cols))
                        cur.execute(
                            f"INSERT INTO customers ({
                                ', '.join(cols)}) VALUES ({placeholders})", vals)
                        conn.commit()
                        print(json.dumps({"id": cur.lastrowid}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_delete_customer" and len(sys.argv) > 2:
            try:
                cid = int(sys.argv[2])
                try:
                    from crm import (
                        delete_customer as crm_delete_customer,  # type: ignore
                    )
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    ok = crm_delete_customer(conn, cid)
                    print(json.dumps({"success": bool(ok)}))
                except Exception:
                    conn = bridge.get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "DELETE FROM projects WHERE customer_id=?", (cid,))
                    cur.execute("DELETE FROM customers WHERE id=?", (cid,))
                    conn.commit()
                    print(json.dumps({"success": cur.rowcount > 0}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_list_projects_for_customer" and len(sys.argv) > 2:
            try:
                cid = int(sys.argv[2])
                try:
                    from crm import load_projects_for_customer  # type: ignore
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    rows = load_projects_for_customer(conn, cid)
                    print(json.dumps(rows, default=str))
                except Exception:
                    conn = bridge.get_connection()
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT * FROM projects WHERE customer_id=? ORDER BY id DESC", (cid,)).fetchall()
                    print(json.dumps([dict(r) for r in rows], default=str))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_get_project" and len(sys.argv) > 2:
            try:
                pid = int(sys.argv[2])
                try:
                    from crm import load_project  # type: ignore
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    row = load_project(conn, pid)
                    print(json.dumps(row, default=str))
                except Exception:
                    conn = bridge.get_connection()
                    conn.row_factory = sqlite3.Row
                    row = conn.execute(
                        "SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
                    print(json.dumps(dict(row) if row else None, default=str))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_save_project" and len(sys.argv) > 2:
            try:
                payload = json.loads(sys.argv[2])
                if not isinstance(payload, dict):
                    raise ValueError("Invalid payload")
                try:
                    from crm import create_tables_crm
                    from crm import save_project as crm_save_project  # type: ignore
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    create_tables_crm(conn)
                    new_id = crm_save_project(conn, payload)
                    print(json.dumps({"id": new_id}))
                except Exception:
                    conn = bridge.get_connection()
                    cur = conn.cursor()
                    if payload.get('id'):
                        pid = int(payload['id'])
                        data = {k: v for k, v in payload.items() if k != 'id'}
                        sets = ", ".join([f"{k}=?" for k in data.keys()])
                        cur.execute(
                            f"UPDATE projects SET {sets} WHERE id=?", [
                                *data.values(), pid])
                        conn.commit()
                        print(json.dumps({"id": pid}))
                    else:
                        cols = list(payload.keys())
                        vals = [payload[k] for k in cols]
                        placeholders = ",".join(["?"] * len(cols))
                        cur.execute(
                            f"INSERT INTO projects ({
                                ', '.join(cols)}) VALUES ({placeholders})", vals)
                        conn.commit()
                        print(json.dumps({"id": cur.lastrowid}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        elif command == "crm_delete_project" and len(sys.argv) > 2:
            try:
                pid = int(sys.argv[2])
                try:
                    from crm import delete_project as crm_delete_project  # type: ignore
                    from database import get_db_connection  # type: ignore
                    conn = get_db_connection()
                    if conn is None:
                        raise RuntimeError("DB connection unavailable")
                    ok = crm_delete_project(conn, pid)
                    print(json.dumps({"success": bool(ok)}))
                except Exception:
                    conn = bridge.get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM projects WHERE id=?", (pid,))
                    conn.commit()
                    print(json.dumps({"success": cur.rowcount > 0}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            finally:
                try:
                    conn.close()  # type: ignore
                except Exception:
                    pass
        else:
            print(json.dumps({"error": "Unknown command"}))
    else:
        # Test aller Funktionen
        print("=== PV Manufacturers ===")
        print(bridge.get_pv_manufacturers())
        print("\n=== Inverter Manufacturers ===")
        print(bridge.get_inverter_manufacturers())
        print("\n=== Storage Manufacturers ===")
        print(bridge.get_storage_manufacturers())
        print("\n=== Additional Components ===")
        print(f"Wallbox: {bridge.get_wallbox_manufacturers()}")
        print(f"EMS: {bridge.get_ems_manufacturers()}")
        print(f"Optimizer: {bridge.get_optimizer_manufacturers()}")
        print(f"Carport: {bridge.get_carport_manufacturers()}")
        print(f"Emergency Power: {bridge.get_emergency_power_manufacturers()}")
        print(
            f"Animal Protection: {
                bridge.get_animal_protection_manufacturers()}")

        # Beispiel: Erste PV Hersteller Modelle
        pv_manufacturers = bridge.get_pv_manufacturers()
        if pv_manufacturers:
            print(f"\n=== Models for {pv_manufacturers[0]} ===")
            models = bridge.get_pv_models_by_manufacturer(pv_manufacturers[0])
            for model in models[:3]:  # Erste 3
                name = model.get('produkt_modell') or model.get('model')
                wp = model.get('pv_modul_leistung') or model.get('capacity_w')
                preis = model.get('preis_stück') or model.get('price')
                print(f"- {name}: {wp}W, {preis}€")
