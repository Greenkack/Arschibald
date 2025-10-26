"""price_matrix_store.py

Persistenz- und Logikschicht für das NEUE dynamische Preismatrix-System.
Ziel: Excel-ähnliche, editierbare Matrix(en) mit Versionierung/Mehrfach-Sets.

Tabellen (normalisiert):
  price_matrix_sets (Matrix-Kopf / Metadaten)
  price_matrix_rows (Zeilen, definieren z.B. Modulanzahl oder frei wählbare Labels)
  price_matrix_columns (Spalten, definieren z.B. Speicher-Varianten)
  price_matrix_cells (Werte je Row/Column)

Design-Ziele:
  - Mehrere Matrizen verwaltbar (aktiv setzen)
  - CRUD für Zeilen/Spalten/Zellen
  - Export/Import (CSV)
  - Spätere Erweiterung: Formeln, Versionierung, Audit, Bulk Ops

API (erste Version):
  create_matrix(name, description="") -> matrix_id
  clone_matrix(matrix_id, new_name) -> new_matrix_id
  delete_matrix(matrix_id) -> bool
  list_matrices() -> List[dict]
  set_active_matrix(matrix_id) -> bool
  get_active_matrix_id() -> Optional[int]
  add_row(matrix_id, label, position=None) -> row_id
  add_column(matrix_id, label, position=None) -> column_id
  remove_row(row_id) -> bool
  remove_column(column_id) -> bool
  set_cell_value(matrix_id, row_id, column_id, value: float) -> bool
  get_matrix_full(matrix_id) -> dict { 'meta':..., 'rows': [...], 'columns': [...], 'cells': {(row_id,col_id): value}, 'wide': pandas.DataFrame }
  export_matrix_csv(matrix_id) -> str
  import_matrix_csv(name, csv_text) -> matrix_id

Fehler-behavior: Funktionen geben None/False zurück bei Problem, Details optional per Exception-Print.

"""
from __future__ import annotations

import csv
import io
import sqlite3
from datetime import datetime
from typing import Any

import pandas as pd

from database import get_db_connection

# Erweiterung: pricing_mode + include_accessories/include_misc + raw_input
# Vorbereitung
SCHEMA_VERSION_MATRIX = 2


def _ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    # Sets
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_matrix_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 0,
            pricing_mode TEXT DEFAULT 'pauschal', -- 'pauschal' | 'additiv'
            include_accessories INTEGER DEFAULT 1,
            include_misc INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Rows
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_matrix_rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matrix_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            label TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE
        )
        """
    )
    # Columns
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_matrix_columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matrix_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            label TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE
        )
        """
    )
    # Cells
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_matrix_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matrix_id INTEGER NOT NULL,
            row_id INTEGER NOT NULL,
            column_id INTEGER NOT NULL,
            value REAL,
            raw_input TEXT, -- Falls künftig Formeln oder Strings gespeichert werden
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(matrix_id, row_id, column_id),
            FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE,
            FOREIGN KEY(row_id) REFERENCES price_matrix_rows(id) ON DELETE CASCADE,
            FOREIGN KEY(column_id) REFERENCES price_matrix_columns(id) ON DELETE CASCADE
        )
        """
    )
    # Dynamische Migrationen für bestehende Installationen
    # price_matrix_sets: prüfen auf neue Spalten
    cur.execute("PRAGMA table_info(price_matrix_sets)")
    existing_cols = {r[1] for r in cur.fetchall()}
    alter_cmds = []
    if 'pricing_mode' not in existing_cols:
        alter_cmds.append(
            "ALTER TABLE price_matrix_sets ADD COLUMN pricing_mode TEXT DEFAULT 'pauschal'")
    if 'include_accessories' not in existing_cols:
        alter_cmds.append(
            "ALTER TABLE price_matrix_sets ADD COLUMN include_accessories INTEGER DEFAULT 1")
    if 'include_misc' not in existing_cols:
        alter_cmds.append(
            "ALTER TABLE price_matrix_sets ADD COLUMN include_misc INTEGER DEFAULT 1")
    for cmd in alter_cmds:
        try:
            cur.execute(cmd)
        except Exception:
            pass
    # price_matrix_cells: raw_input
    cur.execute("PRAGMA table_info(price_matrix_cells)")
    cell_cols = {r[1] for r in cur.fetchall()}
    if 'raw_input' not in cell_cols:
        try:
            cur.execute(
                "ALTER TABLE price_matrix_cells ADD COLUMN raw_input TEXT")
        except Exception:
            pass
    conn.commit()


def _recalc_positions(cur: sqlite3.Cursor, table: str, matrix_id: int) -> None:
    cur.execute(
        f"SELECT id FROM {table} WHERE matrix_id = ? ORDER BY position ASC, id ASC",
        (matrix_id,
         ))
    rows = cur.fetchall()
    for idx, r in enumerate(rows):
        cur.execute(f"UPDATE {table} SET position=? WHERE id=?", (idx, r[0]))


def create_matrix(
        name: str,
        description: str = "",
        pricing_mode: str = 'pauschal',
        include_accessories: bool = True,
        include_misc: bool = True) -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO price_matrix_sets (name, description, pricing_mode, include_accessories, include_misc) VALUES (?, ?, ?, ?, ?)",
            (name,
             description,
             pricing_mode,
             1 if include_accessories else 0,
             1 if include_misc else 0))
        matrix_id = cur.lastrowid
        conn.commit()
        conn.close()
        return matrix_id
    except Exception as e:
        print(f"price_matrix_store.create_matrix Fehler: {e}")
        return None


def list_matrices() -> list[dict[str, Any]]:
    try:
        conn = get_db_connection()
        if not conn:
            return []
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, is_active, pricing_mode, include_accessories, include_misc, created_at, updated_at FROM price_matrix_sets ORDER BY created_at DESC")
        data = []
        for row in cur.fetchall():
            data.append({"id": row[0],
                         "name": row[1],
                         "description": row[2],
                         "is_active": bool(row[3]),
                         "pricing_mode": row[4] or 'pauschal',
                         "include_accessories": bool(row[5]),
                         "include_misc": bool(row[6]),
                         "created_at": row[7],
                         "updated_at": row[8]})
        conn.close()
        return data
    except Exception as e:
        print(f"price_matrix_store.list_matrices Fehler: {e}")
        return []


def set_active_matrix(matrix_id: int) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "UPDATE price_matrix_sets SET is_active=0 WHERE is_active=1")
        cur.execute(
            "UPDATE price_matrix_sets SET is_active=1, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (matrix_id,
             ))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok
    except Exception as e:
        print(f"price_matrix_store.set_active_matrix Fehler: {e}")
        return False


def get_active_matrix_id() -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM price_matrix_sets WHERE is_active=1 LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"price_matrix_store.get_active_matrix_id Fehler: {e}")
        return None


def delete_matrix(matrix_id: int) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute("DELETE FROM price_matrix_sets WHERE id=?", (matrix_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok
    except Exception as e:
        print(f"price_matrix_store.delete_matrix Fehler: {e}")
        return False


def clone_matrix(matrix_id: int, new_name: str) -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, description, pricing_mode, include_accessories, include_misc FROM price_matrix_sets WHERE id=?",
            (matrix_id,
             ))
        base = cur.fetchone()
        if not base:
            conn.close()
            return None
        cur.execute(
            "INSERT INTO price_matrix_sets (name, description, pricing_mode, include_accessories, include_misc) VALUES (?, ?, ?, ?, ?)",
            (new_name,
             base[1],
                base[2],
                base[3],
                base[4]))
        new_id = cur.lastrowid
        # Rows
        cur.execute(
            "SELECT id, position, label FROM price_matrix_rows WHERE matrix_id=?",
            (matrix_id,
             ))
        rows_map = {}
        for r in cur.fetchall():
            cur.execute(
                "INSERT INTO price_matrix_rows (matrix_id, position, label) VALUES (?, ?, ?)",
                (new_id,
                 r[1],
                    r[2]))
            rows_map[r[0]] = cur.lastrowid
        # Columns
        cur.execute(
            "SELECT id, position, label FROM price_matrix_columns WHERE matrix_id=?",
            (matrix_id,
             ))
        cols_map = {}
        for c in cur.fetchall():
            cur.execute(
                "INSERT INTO price_matrix_columns (matrix_id, position, label) VALUES (?, ?, ?)",
                (new_id,
                 c[1],
                    c[2]))
            cols_map[c[0]] = cur.lastrowid
        # Cells
        cur.execute(
            "SELECT row_id, column_id, value FROM price_matrix_cells WHERE matrix_id=?",
            (matrix_id,
             ))
        for cell in cur.fetchall():
            old_r, old_c, val = cell
            nr = rows_map.get(old_r)
            nc = cols_map.get(old_c)
            if nr and nc:
                cur.execute(
                    "INSERT INTO price_matrix_cells (matrix_id, row_id, column_id, value) VALUES (?, ?, ?, ?)",
                    (new_id,
                     nr,
                     nc,
                     val))
        conn.commit()
        conn.close()
        return new_id
    except Exception as e:
        print(f"price_matrix_store.clone_matrix Fehler: {e}")
        return None


def add_row(
        matrix_id: int,
        label: str,
        position: int | None = None) -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM price_matrix_rows WHERE matrix_id=?", (matrix_id,))
        count = cur.fetchone()[0]
        pos = position if position is not None and 0 <= position <= count else count
        # Verschiebe nachfolgende
        if pos < count:
            cur.execute(
                "UPDATE price_matrix_rows SET position=position+1 WHERE matrix_id=? AND position>=?",
                (matrix_id,
                 pos))
        cur.execute(
            "INSERT INTO price_matrix_rows (matrix_id, position, label) VALUES (?, ?, ?)",
            (matrix_id,
             pos,
             label))
        row_id = cur.lastrowid
        conn.commit()
        conn.close()
        return row_id
    except Exception as e:
        print(f"price_matrix_store.add_row Fehler: {e}")
        return None


def add_column(
        matrix_id: int,
        label: str,
        position: int | None = None) -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM price_matrix_columns WHERE matrix_id=?", (matrix_id,))
        count = cur.fetchone()[0]
        pos = position if position is not None and 0 <= position <= count else count
        if pos < count:
            cur.execute(
                "UPDATE price_matrix_columns SET position=position+1 WHERE matrix_id=? AND position>=?",
                (matrix_id,
                 pos))
        cur.execute(
            "INSERT INTO price_matrix_columns (matrix_id, position, label) VALUES (?, ?, ?)",
            (matrix_id,
             pos,
             label))
        col_id = cur.lastrowid
        conn.commit()
        conn.close()
        return col_id
    except Exception as e:
        print(f"price_matrix_store.add_column Fehler: {e}")
        return None


def remove_row(row_id: int) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        # Matrix ID für Recalc ermitteln
        cur.execute(
            "SELECT matrix_id, position FROM price_matrix_rows WHERE id=?", (row_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        matrix_id, pos = row[0], row[1]
        cur.execute("DELETE FROM price_matrix_rows WHERE id=?", (row_id,))
        # Positionen anpassen
        cur.execute(
            "UPDATE price_matrix_rows SET position=position-1 WHERE matrix_id=? AND position> ?",
            (matrix_id,
             pos))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"price_matrix_store.remove_row Fehler: {e}")
        return False


def remove_column(column_id: int) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT matrix_id, position FROM price_matrix_columns WHERE id=?", (column_id,))
        col = cur.fetchone()
        if not col:
            conn.close()
            return False
        matrix_id, pos = col[0], col[1]
        cur.execute(
            "DELETE FROM price_matrix_columns WHERE id=?", (column_id,))
        cur.execute(
            "UPDATE price_matrix_columns SET position=position-1 WHERE matrix_id=? AND position> ?",
            (matrix_id,
             pos))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"price_matrix_store.remove_column Fehler: {e}")
        return False


def set_cell_value(
        matrix_id: int,
        row_id: int,
        column_id: int,
        value: float | None,
        raw_input: str | None = None) -> bool:
    try:
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM price_matrix_rows WHERE id=? AND matrix_id=?",
            (row_id,
             matrix_id))
        if not cur.fetchone():
            conn.close()
            return False
        cur.execute(
            "SELECT 1 FROM price_matrix_columns WHERE id=? AND matrix_id=?",
            (column_id,
             matrix_id))
        if not cur.fetchone():
            conn.close()
            return False
        cur.execute(
            "SELECT id FROM price_matrix_cells WHERE matrix_id=? AND row_id=? AND column_id=?",
            (matrix_id,
             row_id,
             column_id))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE price_matrix_cells SET value=?, raw_input=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (value,
                 raw_input,
                 existing[0]))
        else:
            cur.execute(
                "INSERT INTO price_matrix_cells (matrix_id, row_id, column_id, value, raw_input) VALUES (?, ?, ?, ?, ?)",
                (matrix_id,
                 row_id,
                 column_id,
                 value,
                 raw_input))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"price_matrix_store.set_cell_value Fehler: {e}")
        return False


def get_matrix_full(matrix_id: int) -> dict[str, Any] | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, description, is_active, pricing_mode, include_accessories, include_misc, created_at, updated_at FROM price_matrix_sets WHERE id=?",
            (matrix_id,
             ))
        meta_row = cur.fetchone()
        if not meta_row:
            conn.close()
            return None
        meta = {
            "id": meta_row[0],
            "name": meta_row[1],
            "description": meta_row[2],
            "is_active": bool(
                meta_row[3]),
            "pricing_mode": meta_row[4] or 'pauschal',
            "include_accessories": bool(
                meta_row[5]),
            "include_misc": bool(
                meta_row[6]),
            "created_at": meta_row[7],
            "updated_at": meta_row[8]}
        cur.execute(
            "SELECT id, position, label FROM price_matrix_rows WHERE matrix_id=? ORDER BY position ASC",
            (matrix_id,
             ))
        rows = [{"id": r[0], "position": r[1], "label": r[2]}
                for r in cur.fetchall()]
        cur.execute(
            "SELECT id, position, label FROM price_matrix_columns WHERE matrix_id=? ORDER BY position ASC",
            (matrix_id,
             ))
        cols = [{"id": c[0], "position": c[1], "label": c[2]}
                for c in cur.fetchall()]
        cur.execute(
            "SELECT row_id, column_id, value, raw_input FROM price_matrix_cells WHERE matrix_id=?",
            (matrix_id,
             ))
        cells_raw = cur.fetchall()
        cells_map: dict[tuple[int, int], float] = {}
        for rr, cc, val, raw_input in cells_raw:
            cells_map[(rr, cc)] = {"value": val, "raw_input": raw_input}
        # Wide DataFrame aufbauen
        if rows and cols:
            data = []
            row_labels = []
            for r in rows:
                row_labels.append(r["label"])
                row_values = []
                for c in cols:
                    cell_obj = cells_map.get((r["id"], c["id"]))
                    if cell_obj is None:
                        row_values.append(None)
                    else:
                        if cell_obj.get("value") is not None:
                            row_values.append(cell_obj.get("value"))
                        elif cell_obj.get("raw_input"):
                            row_values.append(cell_obj.get("raw_input"))
                        else:
                            row_values.append(None)
                data.append(row_values)
            wide = pd.DataFrame(
                data,
                columns=[
                    c["label"] for c in cols],
                index=row_labels)
        else:
            wide = pd.DataFrame()
        conn.close()
        return {
            "meta": meta,
            "rows": rows,
            "columns": cols,
            "cells": cells_map,
            "wide": wide}
    except Exception as e:
        print(f"price_matrix_store.get_matrix_full Fehler: {e}")
        return None


def export_matrix_csv(matrix_id: int, delimiter: str = ';') -> str | None:
    full = get_matrix_full(matrix_id)
    if not full:
        return None
    df = full['wide']
    if df.empty:
        return ""
    # Erste Spalte als Row-Label
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter)
    header = ["ROW_LABEL"] + list(df.columns)
    writer.writerow(header)
    for idx, row in df.iterrows():
        out_row = []
        for v in row.tolist():
            if pd.isna(v):
                out_row.append("")
            else:
                out_row.append(f"{v}")
        writer.writerow([idx] + out_row)
    return output.getvalue()


def import_matrix_csv(
        name: str,
        csv_text: str,
        delimiter: str = ';') -> int | None:
    try:
        conn = get_db_connection()
        if not conn:
            return None
        _ensure_tables(conn)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO price_matrix_sets (name, description) VALUES (?, ?)",
            (name,
             f"Imported {
                 datetime.utcnow().isoformat()}"))
        matrix_id = cur.lastrowid
        reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            conn.commit()
            conn.close()
            return matrix_id
        header = rows[0]
        col_labels = header[1:]
        col_ids = []
        for pos, cl in enumerate(col_labels):
            cur.execute(
                "INSERT INTO price_matrix_columns (matrix_id, position, label) VALUES (?, ?, ?)",
                (matrix_id,
                 pos,
                 cl.strip()))
            col_ids.append(cur.lastrowid)
        for rline in rows[1:]:
            if not rline:
                continue
            label = rline[0].strip()
            if not label:
                continue
            cur.execute(
                "INSERT INTO price_matrix_rows (matrix_id, position, label) VALUES (?, ?, ?)",
                (matrix_id,
                 10**6,
                 label))
            rid = cur.lastrowid
            for ci, val_txt in enumerate(rline[1:]):
                v_clean = val_txt.strip()
                if v_clean == "":
                    continue
                # Formeln oder Texte beginnen mit '=' oder enthalten
                # nicht-numerische Zeichen
                try:
                    val_f = float(v_clean.replace(',', '.'))
                    cur.execute(
                        "INSERT INTO price_matrix_cells (matrix_id, row_id, column_id, value, raw_input) VALUES (?, ?, ?, ?, ?)",
                        (matrix_id,
                         rid,
                         col_ids[ci],
                            val_f,
                            None))
                except ValueError:
                    cur.execute(
                        "INSERT INTO price_matrix_cells (matrix_id, row_id, column_id, value, raw_input) VALUES (?, ?, ?, ?, ?)",
                        (matrix_id,
                         rid,
                         col_ids[ci],
                            None,
                            v_clean))
        # Positionen neu sortieren
        _recalc_positions(cur, 'price_matrix_rows', matrix_id)
        conn.commit()
        conn.close()
        return matrix_id
    except Exception as e:
        print(f"price_matrix_store.import_matrix_csv Fehler: {e}")
        return None

# Hilfsfunktion für Preisermittlung (einfacher Prototyp)


def lookup_price(
        matrix_id: int,
        row_label: str,
        column_label: str) -> float | None:
    full = get_matrix_full(matrix_id)
    if not full:
        return None
    df = full['wide']
    if df.empty:
        return None
    # Zeilen-Label exakte Suche, sonst nächst kleinere Zahl falls numerisch
    chosen_row_label = None
    floor_source_label = None
    if row_label in df.index:
        row_series = df.loc[row_label]
        chosen_row_label = row_label
    else:
        # Falls numerisch: floor matching
        try:
            target = float(str(row_label).replace(',', '.'))
            numeric_index = []
            for idx in df.index:
                try:
                    numeric_index.append(
                        (float(str(idx).replace(',', '.')), idx))
                except ValueError:
                    pass
            candidates = [idx for val, idx in numeric_index if val <= target]
            if candidates:
                chosen_label = candidates[-1]
                floor_source_label = chosen_label if str(
                    chosen_label) != str(row_label) else None
                row_series = df.loc[chosen_label]
                chosen_row_label = chosen_label
            else:
                return None
        except ValueError:
            return None
    # Spalten Lookup direkt
    if column_label in df.columns:
        v = row_series.get(column_label)
        if pd.isna(v):
            return None
        try:
            return float(v)
        except Exception:
            return None
    return None


def lookup_price_with_meta(
        matrix_id: int, row_label: str, column_label: str) -> dict[str, Any]:
    """Erweitertes Lookup mit Metadaten für Debug / Analyse.

    Returns dict:
        {
          'value': Optional[float],
          'row_used': Optional[str],
          'row_floor_source': Optional[str],
          'column_used': Optional[str]
        }
    """
    value = lookup_price(matrix_id, row_label, column_label)
    full = get_matrix_full(matrix_id)
    row_used = None
    row_floor_source = None
    if full and full['wide'] is not None and not full['wide'].empty:
        df = full['wide']
        # Wiederhole Row-Logik für Metainfo (leicht redundant, aber klar)
        if row_label in df.index:
            row_used = row_label
        else:
            try:
                target = float(str(row_label).replace(',', '.'))
                numeric_index = []
                for idx in df.index:
                    try:
                        numeric_index.append(
                            (float(str(idx).replace(',', '.')), idx))
                    except ValueError:
                        pass
                candidates = [idx for val,
                              idx in numeric_index if val <= target]
                if candidates:
                    row_used = candidates[-1]
                    if str(row_used) != str(row_label):
                        row_floor_source = row_used
            except ValueError:
                pass
    return {
        'value': value,
        'row_used': row_used,
        'row_floor_source': row_floor_source,
        'column_used': column_label if value is not None else None
    }


def update_matrix_pricing_mode(
        matrix_id: int,
        pricing_mode: str,
        include_accessories: bool | None = None,
        include_misc: bool | None = None) -> bool:
    try:
        if pricing_mode not in ('pauschal', 'additiv'):
            return False
        conn = get_db_connection()
        if not conn:
            return False
        _ensure_tables(conn)
        cur = conn.cursor()
        fields = ["pricing_mode = ?",]
        params: list[Any] = [pricing_mode]
        if include_accessories is not None:
            fields.append("include_accessories = ?")
            params.append(1 if include_accessories else 0)
        if include_misc is not None:
            fields.append("include_misc = ?")
            params.append(1 if include_misc else 0)
        params.append(matrix_id)
        cur.execute(
            f"UPDATE price_matrix_sets SET {
                ', '.join(fields)}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            params)
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok
    except Exception as e:
        print(f"price_matrix_store.update_matrix_pricing_mode Fehler: {e}")
        return False


__all__ = [
    'create_matrix',
    'clone_matrix',
    'delete_matrix',
    'list_matrices',
    'set_active_matrix',
    'get_active_matrix_id',
    'add_row',
    'add_column',
    'remove_row',
    'remove_column',
    'set_cell_value',
    'get_matrix_full',
    'export_matrix_csv',
    'import_matrix_csv',
    'lookup_price',
    'lookup_price_with_meta',
    'update_matrix_pricing_mode']
