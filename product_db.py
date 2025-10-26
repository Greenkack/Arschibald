# product_db.py
# Modul zur Verwaltung der Produktdatenbank (SQLite)
import os
import sqlite3
import sys  # KORREKTUR: sys-Modul importieren
import traceback
from datetime import datetime
from typing import Any

# Datenbankverbindung und Verfügbarkeitsstatus
DB_AVAILABLE = False
get_db_connection_safe_pd = None
# ... (Rest des Moduls bis zum if __name__ == "__main__": Block bleibt unverändert) ...

# --- (Beginn des unveränderten Codes bis zum if __name__ Block) ---
try:
    from database import get_db_connection, init_db
    get_db_connection_safe_pd = get_db_connection
    DB_AVAILABLE = True
except ImportError as e:
    def _dummy_get_db_connection_ie():
        print(
            f"product_db.py: Importfehler für database.py: {e}. Dummy DB-Verbindung genutzt.")
        return
    get_db_connection_safe_pd = _dummy_get_db_connection_ie
    print(
        f"product_db.py: Importfehler für database.py: {e}. Dummy DB Funktionen werden genutzt.")
except Exception as e:
    def _dummy_get_db_connection_ex():
        print(
            f"product_db.py: Fehler beim Laden von database.py: {e}. Dummy DB-Verbindung genutzt.")
        return
    get_db_connection_safe_pd = _dummy_get_db_connection_ex
    print(
        f"product_db.py: Fehler beim Laden von database.py: {e}. Dummy DB Funktionen werden genutzt.")


def create_product_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            model_name TEXT NOT NULL UNIQUE,
            brand TEXT,
            price_euro REAL,
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
            description TEXT,
            pros TEXT,
            cons TEXT,
            rating REAL,
            image_base64 TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            datasheet_link_db_path TEXT,
            additional_cost_netto REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    _migrate_product_table_columns(conn)


def _migrate_product_table_columns(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products)")
    existing_columns_info = {row[1]: row for row in cursor.fetchall()}
    existing_columns = list(existing_columns_info.keys())

    expected_columns_and_types = {
        "id": "INTEGER", "category": "TEXT", "model_name": "TEXT", "brand": "TEXT",
        "price_euro": "REAL", "capacity_w": "REAL", "storage_power_kw": "REAL",
        "power_kw": "REAL", "max_cycles": "INTEGER", "warranty_years": "INTEGER",
        "length_m": "REAL", "width_m": "REAL", "weight_kg": "REAL",
        "efficiency_percent": "REAL", "origin_country": "TEXT", "description": "TEXT",
        "pros": "TEXT", "cons": "TEXT", "rating": "REAL", "image_base64": "TEXT",
        "created_at": "TEXT", "updated_at": "TEXT",
        "datasheet_link_db_path": "TEXT",
        "additional_cost_netto": "REAL",
        # Optionaler Firmenbezug (wird u.a. in list_products als Filter
        # genutzt)
        "company_id": "INTEGER",
        # NEU: explizite Modul-Detailspalten, damit Seite 4 echte Werte hat
        # z.B. Monokristallin N-Type / TOPCon / HJT / PERC
        "cell_technology": "TEXT",
        "module_structure": "TEXT",         # z.B. Glas-Glas / Glas-Folie
        "cell_type": "TEXT",                # z.B. 108 Halbzellen
        "version": "TEXT",                  # z.B. All-Black / Black Frame
        # z.B. "25 Jahre Produktgarantie | 30 Jahre Leistungsgarantie"
        "module_warranty_text": "TEXT",
        # Wärmepumpen / Dienstleistungen Erweiterung
        # Arbeitsstunden (für Preislogik Wärmepumpe)
        "labor_hours": "REAL",
        # Enhanced Pricing System Fields
        # "Stück", "Meter", "pauschal", "kWp", etc.
        "calculate_per": "TEXT",
        "purchase_price_net": "REAL",       # Einkaufspreis netto
        "margin_type": "TEXT",              # "percentage" or "fixed"
        # Margin value (percentage or fixed amount)
        "margin_value": "REAL",
        "margin_priority": "INTEGER",       # Priority for margin application
        "pricing_category": "TEXT",         # Category for pricing rules
        "last_price_update": "TEXT",        # Last price update timestamp
        "technology": "TEXT",               # Technology field for pricing
        "feature": "TEXT",                  # Feature field for pricing
        "design": "TEXT",                   # Design field for pricing
        "upgrade": "TEXT",                  # Upgrade field for pricing
        "max_kwh_capacity": "REAL",         # Maximum kWh capacity
        # Outdoor optimization (0/1 boolean)
        "outdoor_opt": "INTEGER",
        "self_supply_feature": "INTEGER",   # Self supply feature (0/1 boolean)
        # Shadow fading feature (0/1 boolean)
        "shadow_fading": "INTEGER",
        # Smart home integration (0/1 boolean)
        "smart_home": "INTEGER"
    }

    if 'added_date' in existing_columns and 'created_at' not in existing_columns:
        try:
            print(
                "product_db.py: Alte Spalte 'added_date' gefunden, versuche Umbenennung zu 'created_at'.")
            cursor.execute(
                "ALTER TABLE products RENAME COLUMN added_date TO created_at;")
            conn.commit()
            existing_columns.remove('added_date')
            existing_columns.append('created_at')
            print("product_db.py: Spalte 'added_date' zu 'created_at' umbenannt.")
        except sqlite3.OperationalError as e_rename:
            print(
                f"product_db.py: Fehler beim Umbenennen von 'added_date' zu 'created_at': {e_rename}. Manuelle Migration könnte nötig sein.")

    if 'last_updated' in existing_columns and 'updated_at' not in existing_columns:
        try:
            print(
                "product_db.py: Alte Spalte 'last_updated' gefunden, versuche Umbenennung zu 'updated_at'.")
            cursor.execute(
                "ALTER TABLE products RENAME COLUMN last_updated TO updated_at;")
            conn.commit()
            existing_columns.remove('last_updated')
            existing_columns.append('updated_at')
            print("product_db.py: Spalte 'last_updated' zu 'updated_at' umbenannt.")
        except sqlite3.OperationalError as e_rename_lu:
            print(
                f"product_db.py: Fehler beim Umbenennen von 'last_updated' zu 'updated_at': {e_rename_lu}.")

    for col_name, col_type in expected_columns_and_types.items():
        if col_name not in existing_columns:
            try:
                default_suffix = ""
                if col_name == "created_at" or col_name == "updated_at":
                    default_suffix = " DEFAULT CURRENT_TIMESTAMP"
                elif col_type == "TEXT":
                    default_suffix = " DEFAULT ''"
                elif col_type == "REAL":
                    default_suffix = " DEFAULT 0.0"
                elif col_type == "INTEGER":
                    default_suffix = " DEFAULT 0"
                not_null_stmt = ""
                if col_name in ["category", "model_name"]:
                    not_null_stmt = " NOT NULL"
                alter_col_type = col_type
                if not_null_stmt and not default_suffix:
                    if col_type == "TEXT":
                        default_suffix = " DEFAULT ''"
                    elif col_type == "INTEGER":
                        default_suffix = " DEFAULT 0"
                    elif col_type == "REAL":
                        default_suffix = " DEFAULT 0.0"
                cursor.execute(
                    f"ALTER TABLE products ADD COLUMN {col_name} {alter_col_type}{not_null_stmt}{default_suffix}")
                conn.commit()
                print(
                    f"product_db.py: Spalte '{col_name}' ({alter_col_type}{not_null_stmt}{default_suffix}) zur Tabelle 'products' hinzugefügt.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    pass
                else:
                    print(
                        f"product_db.py: Fehler beim Hinzufügen von Spalte '{col_name}': {e}")
                    traceback.print_exc()
            except Exception as e_general_add:
                print(
                    f"product_db.py: Allgemeiner Fehler beim Hinzufügen der Spalte '{col_name}': {e_general_add}")
                traceback.print_exc()
    conn.commit()


def add_product(product_data: dict[str, Any]) -> int | None:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.add_product: DB nicht verfügbar.")
        return None
    create_product_table(conn)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    all_db_columns = {
        "id", "category", "model_name", "brand", "price_euro", "capacity_w", "storage_power_kw", "power_kw",
        "max_cycles", "warranty_years", "length_m", "width_m", "weight_kg", "efficiency_percent", "origin_country",
        "description", "pros", "cons", "rating", "image_base64", "created_at", "updated_at", "datasheet_link_db_path",
        "additional_cost_netto", "company_id",
        # NEU: Modul-Detailfelder
        "cell_technology", "module_structure", "cell_type", "version", "module_warranty_text", "labor_hours",
        # Enhanced Pricing System Fields
        "calculate_per", "purchase_price_net", "margin_type", "margin_value", "margin_priority",
        "pricing_category", "last_price_update", "technology", "feature", "design", "upgrade",
        "max_kwh_capacity", "outdoor_opt", "self_supply_feature", "shadow_fading", "smart_home"
    }
    insert_data: dict[str, Any] = {}
    if not product_data.get('category'):
        print(
            f"product_db.add_product: FEHLER - 'category' ist Pflicht. Produkt: {
                product_data.get(
                    'model_name',
                    'N/A')}")
        conn.close()
        return None
    if not product_data.get('model_name'):
        print(
            f"product_db.add_product: FEHLER - 'model_name' ist Pflicht. Daten: {product_data}")
        conn.close()
        return None
    for col_name in all_db_columns:
        if col_name == 'id':
            continue
        if col_name in product_data:
            insert_data[col_name] = product_data[col_name]
        else:
            # 0-Werte sollen als "ignoriert" gelten -> NULL speichern
            if col_name in ['category', 'model_name']:
                # Pflichtfelder werden vorausgesetzt, hier kein Ersatz
                insert_data[col_name] = product_data.get(col_name)
            elif col_name in ['created_at', 'updated_at']:
                insert_data[col_name] = now_iso
            else:
                insert_data[col_name] = None
    cursor.execute("SELECT id FROM products WHERE model_name = ?",
                   (insert_data['model_name'],))
    if cursor.fetchone():
        print(
            f"product_db.add_product: Fehler - Produkt mit Modellname '{
                insert_data['model_name']}' existiert bereits.")
        conn.close()
        return None
    fields = ', '.join(insert_data.keys())
    placeholders = ', '.join(['?'] * len(insert_data))
    try:
        cursor.execute(
            f"INSERT INTO products ({fields}) VALUES ({placeholders})", list(
                insert_data.values()))
        conn.commit()
        product_id = cursor.lastrowid
        print(
            f"product_db.add_product: Produkt '{
                insert_data['model_name']}' erfolgreich mit ID {product_id} hinzugefügt.")
        return product_id
    except sqlite3.Error as e:
        print(
            f"product_db.add_product: SQLite Fehler bei INSERT von '{
                insert_data.get(
                    'model_name',
                    'N/A')}': {e}")
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        conn.close()


def update_product(product_id: int | float,
                   product_data: dict[str, Any]) -> bool:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.update_product: DB nicht verfügbar.")
        return False
    create_product_table(conn)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    if 'last_updated' in product_data:
        product_data['updated_at'] = product_data.pop('last_updated')
    product_data['updated_at'] = now_iso
    cursor.execute("PRAGMA table_info(products)")
    db_columns = [col_info[1] for col_info in cursor.fetchall()]
    if 'category' in product_data and not product_data['category']:
        print(
            f"product_db.update_product: FEHLER - 'category' darf nicht leer sein für ID {product_id}.")
        conn.close()
        return False
    if 'model_name' in product_data and not product_data['model_name']:
        print(
            f"product_db.update_product: FEHLER - 'model_name' darf nicht leer sein für ID {product_id}.")
        conn.close()
        return False
    if 'model_name' in product_data:
        cursor.execute(
            "SELECT id FROM products WHERE model_name = ? AND id != ?",
            (product_data['model_name'],
             int(product_id)))
        if cursor.fetchone():
            print(
                f"product_db.update_product: Fehler - Modellname '{
                    product_data['model_name']}' existiert bereits für anderes Produkt.")
            conn.close()
            return False
    update_data = {k: v for k, v in product_data.items()
                   if k in db_columns and k != 'id'}
    if not update_data:
        print(
            f"product_db.update_product: Keine gültigen Felder zum Aktualisieren für ID {product_id}.")
        conn.close()
        return False
    fields_to_set = [f"{k}=?" for k in update_data]
    values = list(update_data.values())
    values.append(int(product_id))
    try:
        cursor.execute(
            f"UPDATE products SET {
                ', '.join(fields_to_set)} WHERE id=?",
            values)
        conn.commit()
        if cursor.rowcount > 0:
            print(
                f"product_db.update_product: Produkt ID {product_id} erfolgreich aktualisiert.")
            return True
        print(
            f"product_db.update_product: Produkt ID {product_id} nicht gefunden.")
        return False
    except sqlite3.Error as e:
        print(
            f"product_db.update_product: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_product(product_id: int | float) -> bool:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.delete_product: DB nicht verfügbar.")
        return False
    create_product_table(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id=?", (int(product_id),))
        conn.commit()
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(
                f"product_db.delete_product: Produkt ID {product_id} erfolgreich gelöscht.")
        else:
            print(
                f"product_db.delete_product: Produkt ID {product_id} nicht gefunden, nichts gelöscht.")
        return deleted_count > 0
    except sqlite3.Error as e:
        print(
            f"product_db.delete_product: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def list_products(category: str | None = None, company_id: int |
                  None = None) -> list[dict[str, Any]]:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.list_products: DB nicht verfügbar.")
        return []
    create_product_table(conn)
    cursor = conn.cursor()
    query = "SELECT * FROM products"
    params: list[Any] = []
    conditions = []

    if category:
        conditions.append("category = ?")
        params.append(category)

    if company_id is not None:
        conditions.append("company_id = ?")
        params.append(company_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY model_name COLLATE NOCASE"
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows] if rows else []
    except sqlite3.Error as e:
        print(f"product_db.list_products: SQLite Fehler: {e}")
        traceback.print_exc()
        return []
    finally:
        conn.close()


def get_product_by_id(product_id: int | float) -> dict[str, Any] | None:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.get_product_by_id: DB nicht verfügbar.")
        return None
    create_product_table(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products WHERE id=?", (int(product_id),))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(
            f"product_db.get_product_by_id: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        return None
    finally:
        conn.close()


def get_product_by_model_name(model_name: str) -> dict[str, Any] | None:
    if not model_name or not model_name.strip():
        print("product_db.get_product_by_model_name: Modellname darf nicht leer sein.")
        return None
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.get_product_by_model_name: DB nicht verfügbar.")
        return None
    create_product_table(conn)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM products WHERE model_name=? COLLATE NOCASE",
            (model_name.strip(),
             ))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(
            f"product_db.get_product_by_model_name: SQLite Fehler für Modell '{model_name}': {e}")
        traceback.print_exc()
        return None
    finally:
        conn.close()


def get_product_id_by_model_name(model_name: str) -> int | None:
    """Hilfsfunktion: liefert nur die ID für ein gegebenes Modell (oder None)."""
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.get_product_id_by_model_name: DB nicht verfügbar.")
        return None
    create_product_table(conn)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM products WHERE model_name=? COLLATE NOCASE",
            (model_name.strip(),
             ))
        row = cursor.fetchone()
        return int(row[0]) if row else None
    except sqlite3.Error as e:
        print(
            f"product_db.get_product_id_by_model_name: SQLite Fehler für Modell '{model_name}': {e}")
        traceback.print_exc()
        return None
    finally:
        conn.close()


def update_product_image(
        product_id: int | float,
        image_base64: str | None) -> bool:
    return update_product(int(product_id), {"image_base64": image_base64})


def list_product_categories() -> list[str]:
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.list_product_categories: DB nicht verfügbar.")
        return []
    create_product_table(conn)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category COLLATE NOCASE")
        rows = cursor.fetchall()
        return [row['category'] for row in rows]
    except sqlite3.Error as e:
        print(f"product_db.list_product_categories: SQLite Fehler: {e}")
        traceback.print_exc()
        return []
    finally:
        conn.close()

# --- Enhanced Pricing System Functions ---


def calculate_price_by_method(base_price: float,
                              quantity: float,
                              calculate_per: str,
                              product_specs: dict[str,
                                                  Any] | None = None) -> float:
    """
    Calculate total price based on calculate_per method.

    This function now uses the enhanced CalculatePerEngine for comprehensive
    calculation method support and feature integration.

    Args:
        base_price: Base unit price
        quantity: Quantity to calculate for
        calculate_per: Calculation method ("Stück", "Meter", "pauschal", "kWp", etc.)
        product_specs: Additional product specifications for calculations

    Returns:
        Total calculated price
    """
    try:
        # Import the enhanced engine
        from pricing.calculate_per_engine import CalculatePerEngine, CalculationContext

        # Create engine instance
        engine = CalculatePerEngine()

        # Create calculation context from product specs
        context = None
        if product_specs:
            context = CalculationContext(
                capacity_w=product_specs.get('capacity_w'),
                power_kw=product_specs.get('power_kw'),
                efficiency_percent=product_specs.get('efficiency_percent'),
                length_m=product_specs.get('length_m'),
                width_m=product_specs.get('width_m'),
                area_m2=product_specs.get('area_m2'),
                technology=product_specs.get('technology'),
                feature=product_specs.get('feature'),
                design=product_specs.get('design'),
                upgrade=product_specs.get('upgrade'),
                system_capacity_kwp=product_specs.get('system_capacity_kwp'),
                installation_area_m2=product_specs.get('installation_area_m2'),
                labor_hours=product_specs.get('labor_hours'),
                category=product_specs.get('category'),
                brand=product_specs.get('brand')
            )

        # Calculate using enhanced engine
        result = engine.calculate_price(
            base_price, quantity, calculate_per or "Stück", context)
        return result.total_price

    except ImportError:
        # Fallback to legacy implementation if enhanced engine not available
        print("product_db.calculate_price_by_method: Enhanced engine not available, using legacy calculation")
        return _legacy_calculate_price_by_method(
            base_price, quantity, calculate_per, product_specs)
    except Exception as e:
        # Fallback on any error
        print(
            f"product_db.calculate_price_by_method: Error using enhanced engine: {e}, using legacy calculation")
        return _legacy_calculate_price_by_method(
            base_price, quantity, calculate_per, product_specs)


def _legacy_calculate_price_by_method(base_price: float,
                                      quantity: float,
                                      calculate_per: str,
                                      product_specs: dict[str,
                                                          Any] | None = None) -> float:
    """
    Legacy calculate_price_by_method implementation for fallback.
    """
    if not calculate_per:
        calculate_per = "Stück"  # Default fallback

    calculate_per = calculate_per.lower().strip()

    if calculate_per in [
        "stück",
        "piece",
        "unit"] or calculate_per in [
        "meter",
            "m"]:
        return base_price * quantity
    if calculate_per in ["pauschal", "lump_sum", "flat"]:
        return base_price  # Ignore quantity for lump sum
    if calculate_per in ["kwp", "kw_peak"]:
        # For kWp calculation, we need the system capacity
        if product_specs and 'capacity_w' in product_specs:
            kwp = product_specs['capacity_w'] / 1000.0  # Convert W to kWp
            return base_price * kwp * quantity
        # Fallback to per piece if no capacity info
        return base_price * quantity
    # Unknown method, default to per piece
    print(
        f"product_db._legacy_calculate_price_by_method: Unknown calculate_per method '{calculate_per}', using per piece")
    return base_price * quantity


def set_product_margin(
        product_id: int | float,
        margin_type: str,
        margin_value: float,
        priority: int = 0) -> bool:
    """
    Set profit margin for a specific product.

    Args:
        product_id: Product ID
        margin_type: "percentage" or "fixed"
        margin_value: Margin value (percentage as decimal or fixed amount)
        priority: Priority for margin application (higher = more priority)

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.set_product_margin: DB nicht verfügbar.")
        return False

    create_product_table(conn)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    try:
        # Validate margin_type
        if margin_type not in ["percentage", "fixed"]:
            print(
                f"product_db.set_product_margin: Invalid margin_type '{margin_type}'. Must be 'percentage' or 'fixed'.")
            return False

        # Update product margin settings
        cursor.execute("""
            UPDATE products
            SET margin_type = ?, margin_value = ?, margin_priority = ?, last_price_update = ?
            WHERE id = ?
        """, (margin_type, margin_value, priority, now_iso, int(product_id)))

        conn.commit()

        if cursor.rowcount > 0:
            print(
                f"product_db.set_product_margin: Margin set for product ID {product_id}: {margin_type} = {margin_value}")

            # Log the change in pricing history
            log_pricing_change(
                int(product_id),
                "margin_configuration",
                f"{margin_type}:{margin_value}:{priority}",
                f"Margin updated: {margin_type} = {margin_value}, priority = {priority}")
            return True
        print(
            f"product_db.set_product_margin: Product ID {product_id} not found.")
        return False

    except sqlite3.Error as e:
        print(
            f"product_db.set_product_margin: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def calculate_selling_price(product_id: int | float) -> dict[str, Any] | None:
    """
    Calculate selling price based on purchase price and margin configuration.

    Args:
        product_id: Product ID

    Returns:
        Dictionary with pricing breakdown or None if error
    """
    product = get_product_by_id(product_id)
    if not product:
        return None

    purchase_price = product.get('purchase_price_net', 0.0) or 0.0
    margin_type = product.get('margin_type', 'percentage') or 'percentage'
    margin_value = product.get('margin_value', 0.0) or 0.0

    if purchase_price <= 0:
        # If no purchase price set, use current price_euro as selling price
        return {
            'purchase_price_net': 0.0,
            'margin_type': margin_type,
            'margin_value': margin_value,
            'margin_amount': 0.0,
            'selling_price_net': product.get('price_euro', 0.0) or 0.0,
            'margin_percentage': 0.0,
            'source': 'direct_price'
        }

    if margin_type == 'percentage':
        margin_amount = purchase_price * (margin_value / 100.0)
        selling_price = purchase_price + margin_amount
        margin_percentage = margin_value
    elif margin_type == 'fixed':
        margin_amount = margin_value
        selling_price = purchase_price + margin_amount
        margin_percentage = (margin_amount / purchase_price *
                             100.0) if purchase_price > 0 else 0.0
    else:
        # Invalid margin type, return purchase price
        return {
            'purchase_price_net': purchase_price,
            'margin_type': margin_type,
            'margin_value': margin_value,
            'margin_amount': 0.0,
            'selling_price_net': purchase_price,
            'margin_percentage': 0.0,
            'source': 'error'
        }

    return {
        'purchase_price_net': purchase_price,
        'margin_type': margin_type,
        'margin_value': margin_value,
        'margin_amount': margin_amount,
        'selling_price_net': selling_price,
        'margin_percentage': margin_percentage,
        'source': 'calculated'
    }


def update_product_purchase_price(
        product_id: int | float,
        purchase_price_net: float,
        reason: str = "Manual update") -> bool:
    """
    Update the purchase price for a product and log the change.

    Args:
        product_id: Product ID
        purchase_price_net: New purchase price (net)
        reason: Reason for the change

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.update_product_purchase_price: DB nicht verfügbar.")
        return False

    create_product_table(conn)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    try:
        # Get current purchase price for logging
        cursor.execute(
            "SELECT purchase_price_net FROM products WHERE id = ?", (int(product_id),))
        row = cursor.fetchone()
        if not row:
            print(
                f"product_db.update_product_purchase_price: Product ID {product_id} not found.")
            return False

        old_price = row[0] or 0.0

        # Update purchase price
        cursor.execute("""
            UPDATE products
            SET purchase_price_net = ?, last_price_update = ?
            WHERE id = ?
        """, (purchase_price_net, now_iso, int(product_id)))

        conn.commit()

        if cursor.rowcount > 0:
            print(
                f"product_db.update_product_purchase_price: Purchase price updated for product ID {product_id}: {old_price} -> {purchase_price_net}")

            # Log the change
            log_pricing_change(
                int(product_id),
                "purchase_price_net",
                str(old_price),
                str(purchase_price_net),
                reason)
            return True
        return False

    except sqlite3.Error as e:
        print(
            f"product_db.update_product_purchase_price: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def log_pricing_change(
        product_id: int,
        field_name: str,
        old_value: str,
        new_value: str,
        reason: str = "",
        changed_by: str = "system") -> bool:
    """
    Log a pricing change to the pricing_history table.

    Args:
        product_id: Product ID
        field_name: Name of the field that changed
        old_value: Old value (as string)
        new_value: New value (as string)
        reason: Reason for the change
        changed_by: Who made the change

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        return False

    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    try:
        cursor.execute("""
            INSERT INTO pricing_history
            (product_id, field_name, old_value, new_value, change_reason, changed_by, changed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, field_name, old_value, new_value, reason, changed_by, now_iso))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"product_db.log_pricing_change: SQLite Fehler: {e}")
        return False
    finally:
        conn.close()


def generate_product_dynamic_keys(
        product: dict[str, Any], category_specific: bool = True) -> dict[str, Any]:
    """
    Generate dynamic keys for all product fields for PDF integration.

    Args:
        product: Product dictionary with all fields
        category_specific: Whether to generate category-specific keys only

    Returns:
        Dictionary with dynamic keys for PDF templates
    """
    if not product:
        return {}

    # Create safe key name from model name
    model_name = product.get('model_name', 'UNKNOWN')
    safe_name = ''.join(c.upper() if c.isalnum() else '_' for c in model_name)
    safe_name = safe_name.strip('_')

    category = product.get('category', '').lower()
    dynamic_keys = {}

    # Common fields for all products
    common_fields = {
        'id': product.get('id', ''),
        'category': product.get('category', ''),
        'model_name': product.get('model_name', ''),
        'brand': product.get('brand', ''),
        'price_euro': product.get('price_euro', 0.0),
        'calculate_per': product.get('calculate_per', 'Stück'),
        'warranty_years': product.get('warranty_years', 0),
        'weight_kg': product.get('weight_kg', 0.0),
        'origin_country': product.get('origin_country', ''),
        'description': product.get('description', '')
    }

    # Add common keys
    for field, value in common_fields.items():
        key_name = f"{safe_name}_{field.upper()}"
        dynamic_keys[key_name] = value

    if not category_specific:
        # Add all fields if not category-specific
        all_fields = [
            'capacity_w',
            'storage_power_kw',
            'power_kw',
            'max_cycles',
            'technology',
            'feature',
            'design',
            'upgrade',
            'max_kwh_capacity',
            'outdoor_opt',
            'self_supply_feature',
            'shadow_fading',
            'smart_home',
            'length_m',
            'width_m',
            'efficiency_percent']
        for field in all_fields:
            if field in product and product[field] is not None:
                key_name = f"{safe_name}_{field.upper()}"
                dynamic_keys[key_name] = product[field]
        return dynamic_keys

    # Category-specific fields
    if 'pv' in category or 'modul' in category or 'solar' in category:
        # PV Module specific fields
        pv_fields = {
            'capacity_w': product.get('capacity_w', 0.0),
            'technology': product.get('technology', ''),
            'feature': product.get('feature', ''),
            'design': product.get('design', ''),
            'shadow_fading': product.get('shadow_fading', 0),
            'length_m': product.get('length_m', 0.0),
            'width_m': product.get('width_m', 0.0),
            'efficiency_percent': product.get('efficiency_percent', 0.0)
        }

        for field, value in pv_fields.items():
            key_name = f"{safe_name}_{field.upper()}"
            dynamic_keys[key_name] = value

        # Special formatting for boolean fields
        dynamic_keys[f"{safe_name}_SHADOW_FADING_TEXT"] = "Ja" if product.get(
            'shadow_fading') else "Nein"

    elif 'wechselrichter' in category or 'inverter' in category:
        # Inverter specific fields
        inverter_fields = {
            'power_kw': product.get('power_kw', 0.0),
            'technology': product.get('technology', ''),
            'feature': product.get('feature', ''),
            'outdoor_opt': product.get('outdoor_opt', 0),
            'self_supply_feature': product.get('self_supply_feature', 0),
            'shadow_fading': product.get('shadow_fading', 0),
            'smart_home': product.get('smart_home', 0),
            'efficiency_percent': product.get('efficiency_percent', 0.0)
        }

        for field, value in inverter_fields.items():
            key_name = f"{safe_name}_{field.upper()}"
            dynamic_keys[key_name] = value

        # Special formatting for boolean fields
        dynamic_keys[f"{safe_name}_OUTDOOR_OPT_TEXT"] = "Ja" if product.get(
            'outdoor_opt') else "Nein"
        dynamic_keys[f"{safe_name}_SELF_SUPPLY_FEATURE_TEXT"] = "Ja" if product.get(
            'self_supply_feature') else "Nein"
        dynamic_keys[f"{safe_name}_SHADOW_FADING_TEXT"] = "Ja" if product.get(
            'shadow_fading') else "Nein"
        dynamic_keys[f"{safe_name}_SMART_HOME_TEXT"] = "Ja" if product.get(
            'smart_home') else "Nein"

    elif 'speicher' in category or 'battery' in category or 'akku' in category:
        # Battery storage specific fields
        battery_fields = {
            'storage_power_kw': product.get('storage_power_kw', 0.0),
            'max_cycles': product.get('max_cycles', 0),
            'technology': product.get('technology', ''),
            'feature': product.get('feature', ''),
            'upgrade': product.get('upgrade', ''),
            'max_kwh_capacity': product.get('max_kwh_capacity', 0.0)
        }

        for field, value in battery_fields.items():
            key_name = f"{safe_name}_{field.upper()}"
            dynamic_keys[key_name] = value

    return dynamic_keys


def get_product_with_dynamic_keys(
        product_id: int | float, category_specific: bool = True) -> dict[str, Any] | None:
    """
    Get product by ID with generated dynamic keys for PDF integration.

    Args:
        product_id: Product ID
        category_specific: Whether to generate only category-specific keys

    Returns:
        Product dictionary with dynamic_keys field added
    """
    product = get_product_by_id(product_id)
    if not product:
        return None

    # Generate dynamic keys
    dynamic_keys = generate_product_dynamic_keys(product, category_specific)
    product['dynamic_keys'] = dynamic_keys

    return product


def get_products_with_dynamic_keys(category: str | None = None,
                                   company_id: int | None = None,
                                   category_specific: bool = True) -> list[dict[str,
                                                                                Any]]:
    """
    Get all products with generated dynamic keys for PDF integration.

    Args:
        category: Filter by category
        company_id: Filter by company ID
        category_specific: Whether to generate only category-specific keys

    Returns:
        List of product dictionaries with dynamic_keys field added
    """
    products = list_products(category, company_id)

    for product in products:
        dynamic_keys = generate_product_dynamic_keys(
            product, category_specific)
        product['dynamic_keys'] = dynamic_keys

    return products


def clear_all_products() -> bool:
    """
    Clear all products from the database.
    WARNING: This will delete ALL products permanently!

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        print("product_db.clear_all_products: DB nicht verfügbar.")
        return False

    create_product_table(conn)
    cursor = conn.cursor()

    try:
        # Get count before deletion for logging
        cursor.execute("SELECT COUNT(*) FROM products")
        count_before = cursor.fetchone()[0]

        # Delete all products
        cursor.execute("DELETE FROM products")

        # Reset auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")

        conn.commit()

        print(
            f"product_db.clear_all_products: {count_before} Produkte erfolgreich gelöscht.")
        return True

    except sqlite3.Error as e:
        print(f"product_db.clear_all_products: SQLite Fehler: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()


def get_pricing_history(product_id: int | float,
                        limit: int = 50) -> list[dict[str, Any]]:
    """
    Get pricing history for a product.

    Args:
        product_id: Product ID
        limit: Maximum number of records to return

    Returns:
        List of pricing history records
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        return []

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT field_name, old_value, new_value, change_reason, changed_by, changed_at
            FROM pricing_history
            WHERE product_id = ?
            ORDER BY changed_at DESC
            LIMIT ?
        """, (int(product_id), limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

    except sqlite3.Error as e:
        print(
            f"product_db.get_pricing_history: SQLite Fehler für ID {product_id}: {e}")
        return []
    finally:
        conn.close()


def get_products_by_calculate_per(calculate_per: str) -> list[dict[str, Any]]:
    """
    Get all products that use a specific calculation method.

    Args:
        calculate_per: Calculation method to filter by

    Returns:
        List of products using the specified calculation method
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        return []

    create_product_table(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM products
            WHERE calculate_per = ?
            ORDER BY category, model_name COLLATE NOCASE
        """, (calculate_per,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

    except sqlite3.Error as e:
        print(f"product_db.get_products_by_calculate_per: SQLite Fehler: {e}")
        return []
    finally:
        conn.close()


def update_product_pricing_fields(
        product_id: int | float, pricing_data: dict[str, Any]) -> bool:
    """
    Update multiple pricing-related fields for a product.

    Args:
        product_id: Product ID
        pricing_data: Dictionary with pricing field updates

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection_safe_pd()
    if conn is None:
        return False

    create_product_table(conn)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    # Define allowed pricing fields
    pricing_fields = {
        'calculate_per', 'purchase_price_net', 'margin_type', 'margin_value',
        'margin_priority', 'pricing_category', 'technology', 'feature',
        'design', 'upgrade', 'max_kwh_capacity', 'outdoor_opt',
        'self_supply_feature', 'shadow_fading', 'smart_home'
    }

    # Filter to only allowed pricing fields
    update_data = {k: v for k, v in pricing_data.items()
                   if k in pricing_fields}

    if not update_data:
        print(
            "product_db.update_product_pricing_fields: No valid pricing fields to update.")
        return False

    # Add timestamp
    update_data['last_price_update'] = now_iso

    try:
        # Get current values for logging
        cursor.execute("SELECT * FROM products WHERE id = ?",
                       (int(product_id),))
        current_product = cursor.fetchone()
        if not current_product:
            print(
                f"product_db.update_product_pricing_fields: Product ID {product_id} not found.")
            return False

        current_dict = dict(current_product)

        # Build update query
        fields_to_set = [f"{k}=?" for k in update_data]
        values = list(update_data.values())
        values.append(int(product_id))

        cursor.execute(
            f"UPDATE products SET {
                ', '.join(fields_to_set)} WHERE id=?",
            values)
        conn.commit()

        if cursor.rowcount > 0:
            # Log changes
            for field, new_value in update_data.items():
                if field != 'last_price_update':  # Don't log timestamp updates
                    old_value = current_dict.get(field)
                    if str(old_value) != str(new_value):
                        log_pricing_change(
                            int(product_id),
                            field,
                            str(old_value),
                            str(new_value),
                            "Bulk pricing update")

            print(
                f"product_db.update_product_pricing_fields: Updated {
                    len(update_data)} pricing fields for product ID {product_id}")
            return True
        return False

    except sqlite3.Error as e:
        print(
            f"product_db.update_product_pricing_fields: SQLite Fehler für ID {product_id}: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

# --- (Ende des unveränderten Codes) ---


if __name__ == "__main__":
    print("--- Testlauf für product_db.py ---")
    _original_db_path_pdb = None

    try:
        import importlib

        import database
        import product_db

        _original_db_path_pdb = database.DB_PATH
        test_db_file = "test_product_db_run.db"

        if os.path.exists(test_db_file):
            try:
                os.remove(test_db_file)
                print(
                    f"INFO: Vorhandene Test-DB '{test_db_file}' für sauberen Test gelöscht.")
            except Exception as e_del_test_db:
                print(
                    f"WARNUNG: Konnte existierende Test-DB '{test_db_file}' nicht löschen: {e_del_test_db}")

        database.DB_PATH = test_db_file

        importlib.reload(database)
        importlib.reload(product_db)

        conn_test_pdb = product_db.get_db_connection_safe_pd()

        if conn_test_pdb:
            product_db.create_product_table(conn_test_pdb)
            conn_test_pdb.close()
            print(
                f"INFO: Temporäre DB für Test '{test_db_file}' initialisiert.")
        else:
            print(
                "FEHLER: Konnte keine Test-DB-Verbindung für product_db Test herstellen.")
            if _original_db_path_pdb:
                database.DB_PATH = _original_db_path_pdb
            exit()

        print("Test-Produktdatenbank initialisiert.")

        products_to_add = [{"category": "Modul",
                            "model_name": "AlphaSolar 450W",
                            "brand": "AlphaSolar",
                            "price_euro": 180.0,
                            "capacity_w": 450},
                           {"category": "Modul",
                            "model_name": "BetaSun 400W",
                            "brand": "BetaSun",
                            "price_euro": 160.0,
                            "capacity_w": 400},
                           {"category": "Wechselrichter",
                            "model_name": "PowerMax 5K",
                            "brand": "InvertCorp",
                            "price_euro": 800.0,
                            "power_kw": 5.0},
                           {"category": "Batteriespeicher",
                            "model_name": "EnergyCell 10kWh",
                            "brand": "StoreIt",
                            "price_euro": 3500.0,
                            "storage_power_kw": 10.0,
                            "max_cycles": 6000},
                           {"category": "Modul",
                            "model_name": "AlphaSolar 450W",
                            "brand": "AlphaSolar",
                            "price_euro": 185.0}]
        added_ids = []
        for i, p_data in enumerate(products_to_add):
            print(
                f"\nVersuche Produkt hinzuzufügen: {p_data.get('model_name')}")
            p_id = product_db.add_product(p_data.copy())
            if p_id:
                added_ids.append(p_id)
                print(f"  -> ERFOLG: ID {p_id}")
            else:
                print("  -> FEHLER (oder Duplikat, erwartet für letztes Element)")

        print("\n--- Alle Produkte auflisten ---")
        all_prods = product_db.list_products()
        for p in all_prods:
            print(
                f"  ID: {
                    p['id']}, Kat: {
                    p['category']}, Modell: {
                    p['model_name']}, Preis: {
                    p.get('price_euro')}")

        print("\n--- Kategorien auflisten ---")
        categories = product_db.list_product_categories()
        print(f"  Gefundene Kategorien: {categories}")

        if added_ids:
            first_id = added_ids[0]
            print(f"\n--- Produkt mit ID {first_id} abrufen ---")
            prod_by_id = product_db.get_product_by_id(first_id)
            if prod_by_id:
                print(f"  Gefunden: {prod_by_id['model_name']}")
            else:
                print("  -> NICHT GEFUNDEN")

            print("\n--- Produkt 'AlphaSolar 450W' nach Modellname abrufen ---")
            prod_by_name = product_db.get_product_by_model_name(
                "AlphaSolar 450W")
            if prod_by_name:
                print(
                    f"  Gefunden: ID {
                        prod_by_name['id']}, Marke: {
                        prod_by_name['brand']}")
            else:
                print("  -> NICHT GEFUNDEN")

            print(
                f"\n--- Produkt ID {first_id} aktualisieren (Preis und Marke) ---")
            update_data = {"price_euro": 182.50, "brand": "AlphaSolar Inc."}
            success_update = product_db.update_product(first_id, update_data)
            print(f"  Update erfolgreich: {success_update}")
            updated_p = product_db.get_product_by_id(first_id)
            if updated_p:
                print(
                    f"  Neuer Preis: {
                        updated_p.get('price_euro')}, Neue Marke: {
                        updated_p.get('brand')}")

            print(f"\n--- Produkt ID {first_id} löschen ---")
            success_delete = product_db.delete_product(first_id)
            print(f"  Löschen erfolgreich: {success_delete}")
            deleted_p = product_db.get_product_by_id(first_id)
            if not deleted_p:
                print(
                    f"  Produkt ID {first_id} nach Löschen nicht mehr gefunden (korrekt).")
            else:
                print(f"  FEHLER: Produkt ID {first_id} immer noch gefunden!")
    except Exception as e_test_main:
        print(f"Hauptfehler im product_db Testlauf: {e_test_main}")
        traceback.print_exc()
    finally:
        # KORREKTUR: sys.modules verwenden, um auf das geladene database-Modul
        # zuzugreifen
        if _original_db_path_pdb and 'database' in sys.modules:
            sys.modules['database'].DB_PATH = _original_db_path_pdb
            print(
                f"INFO: DB_PATH im Modul 'database' zurückgesetzt auf: {
                    sys.modules['database'].DB_PATH}")

        # test_db_file wird innerhalb des try-Blocks definiert.
        # Sicherstellen, dass es nur verwendet wird, wenn es existiert.
        # `locals()` kann verwendet werden, um zu prüfen, ob die Variable im lokalen Scope definiert ist.
        test_db_file_local_check = locals().get('test_db_file')
        if test_db_file_local_check and os.path.exists(
                test_db_file_local_check):
            try:
                os.remove(test_db_file_local_check)
                print(
                    f"INFO: Temporäre Test-DB '{test_db_file_local_check}' gelöscht.")
            except Exception as e_del_final:
                print(
                    f"WARNUNG: Konnte temporäre Test-DB '{test_db_file_local_check}' nicht löschen: {e_del_final}")

    print("\n--- Testlauf product_db.py beendet ---")

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-04, Gemini Ultra: Korrektur im `if __name__ == "__main__":` Block. `product_db` wird nun importiert, bevor `importlib.reload(product_db)` aufgerufen wird, um den `NameError` zu beheben. `importlib` wird ebenfalls importiert. Sichergestellt, dass die Test-DB vor dem Testlauf gelöscht und danach aufgeräumt wird. DB_PATH wird im `finally`-Block für das `database`-Modul korrekt zurückgesetzt.
# 2025-06-04, Gemini Ultra: `sys`-Modul am Anfang von `product_db.py` importiert, um `NameError: name 'sys' is not defined` im `finally`-Block des Testskripts zu beheben. Die Variable `test_db_file` wird nun sicher über `locals().get('test_db_file')` geprüft, bevor auf sie zugegriffen wird.
# 2025-06-05, Gemini Ultra: Funktion `list_products` aktualisiert, um
# `company_id` als optionalen Filter zu berücksichtigen. Dadurch können
# Produkte für eine bestimmte Firma geladen werden.


def calculate_enhanced_product_pricing(product: dict[str, Any], quantity: float = 1.0,
                                       system_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Calculate enhanced pricing for a product using all available features and calculate_per method.

    Args:
        product: Product dictionary with all fields
        quantity: Quantity to calculate for
        system_context: Additional system context (system capacity, installation area, etc.)

    Returns:
        Dictionary with detailed pricing calculation results
    """
    try:
        from pricing.calculate_per_engine import CalculatePerEngine, CalculationContext

        # Extract base pricing information
        base_price = float(product.get('price_euro', 0.0))
        calculate_per = product.get('calculate_per', 'Stück')

        if base_price <= 0:
            return {
                'success': False,
                'error': 'Invalid base price',
                'base_price': base_price,
                'total_price': 0.0
            }

        # Create comprehensive calculation context
        context = CalculationContext(
            # Technical specifications
            capacity_w=product.get('capacity_w'),
            power_kw=product.get('power_kw'),
            efficiency_percent=product.get('efficiency_percent'),
            length_m=product.get('length_m'),
            width_m=product.get('width_m'),

            # Enhanced product attributes
            technology=product.get('technology'),
            feature=product.get('feature'),
            design=product.get('design'),
            upgrade=product.get('upgrade'),

            # Storage and capacity information
            system_capacity_kwp=product.get('max_kwh_capacity'),
            labor_hours=product.get('labor_hours'),

            # Product classification
            category=product.get('category'),
            brand=product.get('brand')
        )

        # Add system context if provided
        if system_context:
            if 'system_capacity_kwp' in system_context:
                context.system_capacity_kwp = system_context['system_capacity_kwp']
            if 'installation_area_m2' in system_context:
                context.installation_area_m2 = system_context['installation_area_m2']
            if 'labor_hours' in system_context:
                context.labor_hours = system_context['labor_hours']

        # Calculate using enhanced engine
        engine = CalculatePerEngine()
        result = engine.calculate_price(
            base_price, quantity, calculate_per, context)

        # Return comprehensive result
        return {
            'success': True,
            'product_id': product.get('id'),
            'model_name': product.get('model_name'),
            'category': product.get('category'),
            'base_price': result.base_price,
            'unit_price': result.unit_price,
            'quantity': result.quantity,
            'calculation_method': result.calculation_method.value,
            'calculation_factor': result.calculation_factor,
            'total_price': result.total_price,
            'price_adjustments': result.price_adjustments,
            'calculation_notes': result.calculation_notes,
            'validation_warnings': result.validation_warnings,
            'context_used': {
                'technology': context.technology,
                'feature': context.feature,
                'design': context.design,
                'upgrade': context.upgrade,
                'efficiency_percent': context.efficiency_percent,
                'capacity_w': context.capacity_w,
                'power_kw': context.power_kw,
                'category': context.category
            }
        }

    except ImportError as e:
        return {
            'success': False,
            'error': f'Enhanced pricing engine not available: {e}',
            'base_price': product.get('price_euro', 0.0),
            'total_price': product.get('price_euro', 0.0) * quantity
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Calculation error: {e}',
            'base_price': product.get('price_euro', 0.0),
            'total_price': product.get('price_euro', 0.0) * quantity
        }


def get_product_pricing_breakdown(product_id: int | float,
                                  quantity: float = 1.0,
                                  system_context: dict[str,
                                                       Any] | None = None) -> dict[str,
                                                                                   Any] | None:
    """
    Get detailed pricing breakdown for a product by ID.

    Args:
        product_id: Product ID
        quantity: Quantity to calculate for
        system_context: Additional system context

    Returns:
        Detailed pricing breakdown or None if product not found
    """
    product = get_product_by_id(product_id)
    if not product:
        return None

    return calculate_enhanced_product_pricing(
        product, quantity, system_context)


def calculate_system_pricing(components: list[dict[str, Any]],
                             system_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Calculate pricing for a complete system with multiple components.

    Args:
        components: List of component dictionaries with product_id/model_name and quantity
        system_context: System-level context (total capacity, installation area, etc.)

    Returns:
        Complete system pricing breakdown
    """
    try:
        component_results = []
        total_base_price = 0.0
        total_final_price = 0.0
        total_adjustments = 0.0
        all_warnings = []

        for comp in components:
            # Get product information
            if 'product_id' in comp:
                product = get_product_by_id(comp['product_id'])
            elif 'model_name' in comp:
                product = get_product_by_model_name(comp['model_name'])
            else:
                continue

            if not product:
                continue

            quantity = comp.get('quantity', 1.0)

            # Calculate component pricing
            comp_result = calculate_enhanced_product_pricing(
                product, quantity, system_context)

            if comp_result['success']:
                component_results.append(comp_result)
                total_base_price += comp_result['base_price'] * quantity
                total_final_price += comp_result['total_price']

                # Sum adjustments
                if comp_result['price_adjustments']:
                    comp_adjustments = sum(
                        comp_result['price_adjustments'].values())
                    if comp_result['calculation_method'] == 'Stück':
                        comp_adjustments *= quantity
                    total_adjustments += comp_adjustments

                # Collect warnings
                all_warnings.extend(comp_result['validation_warnings'])

        return {
            'success': True,
            'component_count': len(component_results),
            'components': component_results,
            'total_base_price': total_base_price,
            'total_adjustments': total_adjustments,
            'total_final_price': total_final_price,
            'system_context': system_context,
            'validation_warnings': all_warnings
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'System pricing calculation error: {e}',
            'components': [],
            'total_final_price': 0.0
        }


def validate_calculate_per_integration() -> dict[str, Any]:
    """
    Validate that calculate_per integration is working correctly.

    Returns:
        Validation results with test cases
    """
    try:
        from pricing.calculate_per_engine import (
            get_supported_calculation_methods,
            validate_calculation_method,
        )

        # Test basic functionality
        test_results = []

        # Test 1: Basic per piece calculation
        try:
            result = calculate_price_by_method(100.0, 5, "Stück")
            test_results.append({
                'test': 'Basic per piece',
                'expected': 500.0,
                'actual': result,
                'passed': abs(result - 500.0) < 0.01
            })
        except Exception as e:
            test_results.append({
                'test': 'Basic per piece',
                'error': str(e),
                'passed': False
            })

        # Test 2: Per meter calculation
        try:
            result = calculate_price_by_method(8.50, 25.0, "Meter")
            test_results.append({
                'test': 'Per meter',
                'expected': 212.5,
                'actual': result,
                'passed': abs(result - 212.5) < 0.01
            })
        except Exception as e:
            test_results.append({
                'test': 'Per meter',
                'error': str(e),
                'passed': False
            })

        # Test 3: Lump sum calculation
        try:
            result = calculate_price_by_method(2500.0, 3, "pauschal")
            test_results.append({
                'test': 'Lump sum',
                'expected': 2500.0,
                'actual': result,
                'passed': abs(result - 2500.0) < 0.01
            })
        except Exception as e:
            test_results.append({
                'test': 'Lump sum',
                'error': str(e),
                'passed': False
            })

        # Test 4: Per kWp with product specs
        try:
            product_specs = {'capacity_w': 400.0, 'category': 'Modul'}
            result = calculate_price_by_method(150.0, 25, "kWp", product_specs)
            expected = 1500.0  # 25 * 400W = 10kWp, 10kWp * 150 = 1500
            test_results.append({
                'test': 'Per kWp with specs',
                'expected': expected,
                'actual': result,
                'passed': abs(result - expected) < 0.01
            })
        except Exception as e:
            test_results.append({
                'test': 'Per kWp with specs',
                'error': str(e),
                'passed': False
            })

        # Test 5: Feature integration
        try:
            product_specs = {
                'capacity_w': 400.0,
                'technology': 'HJT',
                'feature': 'Bifazial',
                'category': 'Modul'
            }
            result = calculate_price_by_method(
                180.0, 1, "Stück", product_specs)
            # Base 180 + HJT (50) + Bifazial (50) = 280
            test_results.append({
                'test': 'Feature integration',
                'expected': 280.0,
                'actual': result,
                'passed': abs(result - 280.0) < 0.01
            })
        except Exception as e:
            test_results.append({
                'test': 'Feature integration',
                'error': str(e),
                'passed': False
            })

        # Summary
        passed_tests = sum(
            1 for test in test_results if test.get(
                'passed', False))
        total_tests = len(test_results)

        return {
            'success': True,
            'supported_methods': get_supported_calculation_methods(),
            'test_results': test_results,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (
                    passed_tests / total_tests * 100) if total_tests > 0 else 0}}

    except ImportError as e:
        return {
            'success': False,
            'error': f'Enhanced pricing engine not available: {e}',
            'fallback_available': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Validation error: {e}'
        }
