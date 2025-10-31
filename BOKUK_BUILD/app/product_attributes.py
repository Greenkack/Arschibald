# product_attributes.py
# Flexible Produkt-Attributdatenbank (Key/Value) mit CRUD
from __future__ import annotations

import sqlite3
import traceback
from datetime import datetime
from typing import Any

try:
    from database import get_db_connection
except Exception as e:
    get_db_connection = None  # type: ignore
    print(
        f"product_attributes.py: WARN - database.get_db_connection nicht verfügbar: {e}")


def _ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS product_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            attribute_key TEXT NOT NULL,
            attribute_value TEXT,
            unit TEXT,
            display_order INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id, attribute_key),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """
    )
    conn.commit()


def upsert_attribute(
        product_id: int,
        category: str,
        attribute_key: str,
        attribute_value: str | None,
        unit: str | None = None,
        display_order: int | None = None) -> int | None:
    if not get_db_connection:
        print("product_attributes.upsert_attribute: DB nicht verfügbar")
        return None
    conn = get_db_connection()
    if not conn:
        print("product_attributes.upsert_attribute: get_db_connection lieferte None")
        return None
    try:
        _ensure_tables(conn)
        cur = conn.cursor()
        now_iso = datetime.now().isoformat()
        # Versuche Update
        cur.execute(
            "SELECT id FROM product_attributes WHERE product_id = ? AND attribute_key = ?",
            (int(product_id), attribute_key),
        )
        row = cur.fetchone()
        if row:
            attr_id = int(row[0])
            cur.execute(
                "UPDATE product_attributes SET attribute_value = ?, unit = ?, display_order = COALESCE(?, display_order), updated_at = ? WHERE id = ?",
                (attribute_value,
                 unit,
                 display_order,
                 now_iso,
                 attr_id),
            )
            conn.commit()
            return attr_id
        cur.execute(
            "INSERT INTO product_attributes (product_id, category, attribute_key, attribute_value, unit, display_order, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (int(product_id),
             category,
             attribute_key,
             attribute_value,
             unit,
             display_order or 0,
             now_iso),
        )
        conn.commit()
        return int(cur.lastrowid)
    except Exception as e:
        print(f"product_attributes.upsert_attribute: Fehler: {e}")
        traceback.print_exc()
        try:
            conn.rollback()
        except Exception:
            pass
        return None
    finally:
        conn.close()


def get_attribute(
        product_id: int, attribute_key: str) -> dict[str, Any] | None:
    if not get_db_connection:
        return None
    conn = get_db_connection()
    if not conn:
        return None
    try:
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, product_id, category, attribute_key, attribute_value, unit, display_order, updated_at FROM product_attributes WHERE product_id = ? AND attribute_key = ?",
            (int(product_id), attribute_key),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "product_id": row[1],
            "category": row[2],
            "attribute_key": row[3],
            "attribute_value": row[4],
            "unit": row[5],
            "display_order": row[6],
            "updated_at": row[7],
        }
    except Exception:
        return None
    finally:
        conn.close()


def list_attributes(product_id: int) -> list[dict[str, Any]]:
    if not get_db_connection:
        return []
    conn = get_db_connection()
    if not conn:
        return []
    try:
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, product_id, category, attribute_key, attribute_value, unit, display_order, updated_at FROM product_attributes WHERE product_id = ? ORDER BY display_order, attribute_key",
            (int(product_id),),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "product_id": r[1],
                "category": r[2],
                "attribute_key": r[3],
                "attribute_value": r[4],
                "unit": r[5],
                "display_order": r[6],
                "updated_at": r[7],
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        conn.close()


def delete_attribute(attribute_id: int) -> bool:
    if not get_db_connection:
        return False
    conn = get_db_connection()
    if not conn:
        return False
    try:
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute("DELETE FROM product_attributes WHERE id = ?",
                    (int(attribute_id),))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"product_attributes.delete_attribute: Fehler: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        conn.close()


def get_attribute_value(product_id: int, key: str) -> str | None:
    rec = get_attribute(product_id, key)
    return None if not rec else rec.get("attribute_value")


def bulk_upsert(product_id: int,
                category: str,
                entries: list[tuple[str,
                                    str | None,
                                    str | None,
                                    int | None]]) -> int:
    """entries: Liste aus (key, value, unit, display_order). Rückgabe: Anzahl Upserts."""
    count = 0
    for k, v, u, d in entries:
        if upsert_attribute(product_id, category, k, v, u, d):
            count += 1
    return count


# --- Erweiterung: CSV Import/Export (nur neue Funktionen, bestehendes unberührt) ---
def export_attributes_to_csv(
        file_path: str,
        category: str | None = None) -> bool:
    """Exportiert Attribute aller Produkte (optional gefiltert nach Kategorie) in eine CSV-Datei."""
    try:
        import csv

        from product_db import list_products as _list_products

        products = _list_products(
            category=category) if category else _list_products()
        if not products:
            # leere CSV mit Header schreiben
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['product_id',
                                 'category',
                                 'model_name',
                                 'brand',
                                 'attribute_key',
                                 'attribute_value',
                                 'unit',
                                 'display_order'])
            return True

        rows_out = []
        for p in products:
            pid = int(p['id'])
            attrs = list_attributes(pid)
            if not attrs:
                rows_out.append([pid, p.get('category') or '', p.get(
                    'model_name') or '', p.get('brand') or '', '', '', '', ''])
            else:
                for a in attrs:
                    rows_out.append([
                        pid,
                        a.get('category') or p.get('category') or '',
                        p.get('model_name') or '',
                        p.get('brand') or '',
                        a.get('attribute_key') or '',
                        a.get('attribute_value') or '',
                        a.get('unit') or '',
                        a.get('display_order') or 0,
                    ])

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['product_id',
                             'category',
                             'model_name',
                             'brand',
                             'attribute_key',
                             'attribute_value',
                             'unit',
                             'display_order'])
            writer.writerows(rows_out)
        return True
    except Exception as e:
        print(f"product_attributes.export_attributes_to_csv Fehler: {e}")
        return False


def import_attributes_from_csv(
        file_path: str,
        *,
        category_col: str = 'category',
        model_col: str = 'model_name',
        brand_col: str = 'brand',
        ensure_products: bool = True) -> int:
    """Importiert/Upsertet Attribute aus CSV.
    Columns erwartet: category, model_name, brand, attribute_key, attribute_value, unit, display_order
    Wenn ensure_products=True, werden fehlende Produkte angelegt (nur wenn category+model_name vorhanden).
    Rückgabe: Anzahl upserteter Attribute.
    """
    try:
        import csv

        from product_db import add_product as _add_prod
        from product_db import get_product_by_model_name as _get_prod
        count = 0
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = (row.get(category_col) or '').strip()
                model = (row.get(model_col) or '').strip()
                brand = (row.get(brand_col) or '').strip()
                if not model:
                    continue
                prod = _get_prod(model)
                pid = int(prod['id']) if prod else None
                if not pid and ensure_products and category:
                    pid = _add_prod(
                        {'category': category, 'model_name': model, 'brand': brand})
                if not pid:
                    continue
                akey = (row.get('attribute_key') or '').strip()
                aval = (row.get('attribute_value') or '').strip()
                unit = (row.get('unit') or '').strip() or None
                try:
                    dord = int(row.get('display_order') or 0)
                except Exception:
                    dord = 0
                if akey:
                    if upsert_attribute(
                            pid,
                            category or (
                                prod.get('category') if prod else '') or '',
                            akey,
                            aval or None,
                            unit,
                            dord):
                        count += 1
        return count
    except Exception as e:
        print(f"product_attributes.import_attributes_from_csv Fehler: {e}")
        traceback.print_exc()
        return 0
