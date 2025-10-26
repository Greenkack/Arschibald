# brand_logo_db.py
# Verwaltung der Marken-Logos für PDF-Seite 4

import base64
import os
import sqlite3
import traceback
from typing import Any

try:
    from database import get_db_connection, init_db
    DB_AVAILABLE = True
except ImportError as e:
    def get_db_connection():
        print(f"brand_logo_db.py: Importfehler für database.py: {e}")
        return
    DB_AVAILABLE = False
    print(f"brand_logo_db.py: Database nicht verfügbar: {e}")


def create_brand_logos_table(conn: sqlite3.Connection):
    """Erstellt die Tabelle für Marken-Logos"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brand_logos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL UNIQUE,
            logo_base64 TEXT,
            logo_format TEXT,
            file_size_bytes INTEGER DEFAULT 0,
            logo_position_x REAL DEFAULT 0,
            logo_position_y REAL DEFAULT 0,
            logo_width REAL DEFAULT 100,
            logo_height REAL DEFAULT 50,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("Tabelle 'brand_logos' erstellt oder bereits vorhanden.")


def add_brand_logo(
        brand_name: str,
        logo_base64: str,
        logo_format: str = "PNG",
        file_size_bytes: int = 0,
        position_x: float = 0,
        position_y: float = 0,
        width: float = 100,
        height: float = 50) -> bool:
    """Fügt ein neues Marken-Logo hinzu oder aktualisiert ein vorhandenes"""
    if not DB_AVAILABLE:
        print("Database nicht verfügbar - Logo kann nicht gespeichert werden")
        return False

    try:
        conn = get_db_connection()
        if not conn:
            print("Keine Datenbankverbindung möglich")
            return False

        # Tabelle erstellen falls sie nicht existiert
        create_brand_logos_table(conn)

        cursor = conn.cursor()

        # Prüfen ob Logo bereits existiert
        cursor.execute(
            "SELECT id FROM brand_logos WHERE brand_name = ?", (brand_name,))
        existing = cursor.fetchone()

        if existing:
            # Update existing logo
            cursor.execute("""
                UPDATE brand_logos
                SET logo_base64 = ?, logo_format = ?, file_size_bytes = ?,
                    logo_position_x = ?, logo_position_y = ?, logo_width = ?, logo_height = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE brand_name = ?
            """, (logo_base64, logo_format, file_size_bytes, position_x, position_y,
                  width, height, brand_name))
            print(f"Logo für Marke '{brand_name}' aktualisiert")
        else:
            # Insert new logo
            cursor.execute("""
                INSERT INTO brand_logos (brand_name, logo_base64, logo_format, file_size_bytes,
                                       logo_position_x, logo_position_y, logo_width, logo_height)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (brand_name, logo_base64, logo_format, file_size_bytes,
                  position_x, position_y, width, height))
            print(f"Neues Logo für Marke '{brand_name}' hinzugefügt")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Fehler beim Speichern des Logos für '{brand_name}': {e}")
        traceback.print_exc()
        return False


def get_brand_logo(brand_name: str) -> dict[str, Any] | None:
    """Holt das Logo für eine bestimmte Marke"""
    if not DB_AVAILABLE:
        return None

    try:
        conn = get_db_connection()
        if not conn:
            return None

        # Tabelle erstellen falls sie nicht existiert
        create_brand_logos_table(conn)

        cursor = conn.cursor()
        cursor.execute("""
            SELECT brand_name, logo_base64, logo_format, file_size_bytes,
                   logo_position_x, logo_position_y, logo_width, logo_height,
                   is_active, created_at, updated_at
            FROM brand_logos
            WHERE brand_name = ?
        """, (brand_name,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'brand_name': result[0],
                'logo_base64': result[1],
                'logo_format': result[2],
                'file_size_bytes': result[3],
                'logo_position_x': result[4],
                'logo_position_y': result[5],
                'logo_width': result[6],
                'logo_height': result[7],
                'is_active': result[8],
                'created_at': result[9],
                'updated_at': result[10]
            }

        return None

    except Exception as e:
        print(f"Fehler beim Abrufen des Logos für '{brand_name}': {e}")
        return None


def list_all_brand_logos() -> list[dict[str, Any]]:
    """Listet alle verfügbaren Marken-Logos auf"""
    if not DB_AVAILABLE:
        return []

    try:
        conn = get_db_connection()
        if not conn:
            return []

        # Tabelle erstellen falls sie nicht existiert
        create_brand_logos_table(conn)

        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, brand_name, logo_format, file_size_bytes,
                   logo_position_x, logo_position_y, logo_width, logo_height,
                   is_active, created_at, updated_at
            FROM brand_logos
            WHERE is_active = 1
            ORDER BY brand_name
        """)

        results = cursor.fetchall()
        conn.close()

        logos = []
        for result in results:
            logos.append({
                'id': result[0],
                'brand_name': result[1],
                'logo_format': result[2],
                'file_size_bytes': result[3],
                'logo_position_x': result[4],
                'logo_position_y': result[5],
                'logo_width': result[6],
                'logo_height': result[7],
                'is_active': result[8],
                'created_at': result[9],
                'updated_at': result[10]
            })

        return logos

    except Exception as e:
        print(f"Fehler beim Abrufen der Logo-Liste: {e}")
        return []


def delete_brand_logo(brand_name: str) -> bool:
    """Löscht ein Marken-Logo"""
    if not DB_AVAILABLE:
        return False

    try:
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM brand_logos WHERE brand_name = ?", (brand_name,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_count > 0:
            print(f"Logo für Marke '{brand_name}' erfolgreich gelöscht")
            return True
        print(f"Kein Logo für Marke '{brand_name}' gefunden")
        return False

    except Exception as e:
        print(f"Fehler beim Löschen des Logos für '{brand_name}': {e}")
        return False


def upload_logo_from_file(brand_name: str, file_path: str) -> bool:
    """Lädt ein Logo aus einer Datei und speichert es in der Datenbank"""
    try:
        if not os.path.exists(file_path):
            print(f"Datei nicht gefunden: {file_path}")
            return False

        # Dateiformat bestimmen
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.png':
            logo_format = 'PNG'
        elif file_ext in ['.jpg', '.jpeg']:
            logo_format = 'JPEG'
        else:
            print(f"Nicht unterstütztes Dateiformat: {file_ext}")
            return False

        # Datei als Base64 einlesen
        with open(file_path, 'rb') as f:
            file_data = f.read()
            logo_base64 = base64.b64encode(file_data).decode('utf-8')

        # In Datenbank speichern
        return add_brand_logo(brand_name, logo_base64, logo_format)

    except Exception as e:
        print(f"Fehler beim Upload des Logos von '{file_path}': {e}")
        return False


def update_logo_position(brand_name: str, position_x: float, position_y: float,
                         width: float = None, height: float = None) -> bool:
    """Aktualisiert die Position und Größe eines Logos"""
    if not DB_AVAILABLE:
        return False

    try:
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()

        if width is not None and height is not None:
            cursor.execute("""
                UPDATE brand_logos
                SET logo_position_x = ?, logo_position_y = ?, logo_width = ?, logo_height = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE brand_name = ?
            """, (position_x, position_y, width, height, brand_name))
        else:
            cursor.execute("""
                UPDATE brand_logos
                SET logo_position_x = ?, logo_position_y = ?, updated_at = CURRENT_TIMESTAMP
                WHERE brand_name = ?
            """, (position_x, position_y, brand_name))

        updated_count = cursor.rowcount
        conn.commit()
        conn.close()

        if updated_count > 0:
            print(f"Position für Logo '{brand_name}' aktualisiert")
            return True
        print(f"Kein Logo für Marke '{brand_name}' gefunden")
        return False

    except Exception as e:
        print(
            f"Fehler beim Aktualisieren der Logo-Position für '{brand_name}': {e}")
        return False


def _normalize_brand_key(name: str) -> str:
    if not name:
        return ""
    return name.strip().lower().replace(" ", "")


def _base_brand_without_suffix(name: str) -> str:
    """Entfernt angehängte funktionale Suffixe wie PV / WR / SPEICHER / ESS / BATTERIE / AKKU / STROMSPEICHER"""
    if not name:
        return name
    import re
    base = name.strip()
    pattern = re.compile(
        r"^(.*?)(pv|wr|speicher|ess|batterie|akku|stromspeicher)$",
        re.IGNORECASE)
    prev = None
    while base and prev != base:
        prev = base
        m = pattern.match(base)
        if m and m.group(1).strip():
            base = m.group(1).strip()
    return base


def _fetch_all_brand_rows(conn) -> dict[str, dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT brand_name, logo_base64, logo_format, file_size_bytes,
               logo_position_x, logo_position_y, logo_width, logo_height,
               is_active, created_at, updated_at
        FROM brand_logos
        WHERE is_active = 1
    """)
    rows = cursor.fetchall()
    data: dict[str, dict[str, Any]] = {}
    for r in rows:
        data[r[0]] = {
            'brand_name': r[0],
            'logo_base64': r[1],
            'logo_format': r[2],
            'file_size_bytes': r[3],
            'logo_position_x': r[4],
            'logo_position_y': r[5],
            'logo_width': r[6],
            'logo_height': r[7],
            'is_active': r[8],
            'created_at': r[9],
            'updated_at': r[10]
        }
    return data


def get_logos_for_brands(brand_names: list[str]) -> dict[str, dict[str, Any]]:
    """Holt Logos für eine Liste von Herstellern.
    Erweitert: Versucht auch Varianten ohne funktionale Suffixe zu matchen.
    Reihenfolge je Marke:
      1. Exakter Name
      2. Name ohne Leerzeichen (Fallback bereits durch Aufrufer evtl.)
      3. Basis ohne Suffix (PV/WR/SPEICHER/ESS/BATTERIE/AKKU/STROMSPEICHER)
      4. Groß/Klein ignorieren
    Liefert dict mit Key des tatsächlich gefundenen DB-Namens.
    """
    if not DB_AVAILABLE:
        return {}
    try:
        conn = get_db_connection()
        if not conn:
            return {}
        create_brand_logos_table(conn)
        # Alle aktiven Logos einmal holen
        all_rows = _fetch_all_brand_rows(conn)
        conn.close()

        # Indexe bauen
        index_exact = {k: v for k, v in all_rows.items()}
        index_norm = {_normalize_brand_key(k): v for k, v in all_rows.items()}
        index_base = {
            _normalize_brand_key(
                _base_brand_without_suffix(k)): v for k,
            v in all_rows.items()}

        result: dict[str, dict[str, Any]] = {}
        for wanted in brand_names:
            if not wanted:
                continue
            # 1. Exakt
            if wanted in index_exact:
                result[wanted] = index_exact[wanted]
                continue
            norm = _normalize_brand_key(wanted)
            base = _normalize_brand_key(_base_brand_without_suffix(wanted))
            # 2. Normalisiert (Spaces entfernt, lower)
            if norm in index_norm:
                result[wanted] = index_norm[norm]
                continue
            # 3. Basis ohne Suffix
            if base in index_base:
                result[wanted] = index_base[base]
                continue
            # 4. Versuche zusätzlich Groß/Klein Variation des Basis-Originals
            # (bereits durch lower abgedeckt – hier keine Extra-Logik nötig)
            # Wenn kein Treffer: Debug-Hinweis (einmal pro Marke)
            print(f"Kein Logo-Match für {wanted} inkl. Varianten")
        return result
    except Exception as e:
        print(f"Fehler beim erweiterten Logo-Matching: {e}")
        return {}


def deactivate_brand_logo(brand_name: str) -> bool:
    """Deaktiviert ein Logo (soft delete)"""
    if not DB_AVAILABLE:
        return False

    try:
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE brand_logos
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE brand_name = ?
        """, (brand_name,))

        updated_count = cursor.rowcount
        conn.commit()
        conn.close()

        if updated_count > 0:
            print(f"Logo für Marke '{brand_name}' deaktiviert")
            return True
        print(f"Kein Logo für Marke '{brand_name}' gefunden")
        return False

    except Exception as e:
        print(f"Fehler beim Deaktivieren des Logos für '{brand_name}': {e}")
        return False


if __name__ == "__main__":
    # Test der Funktionen
    print("Testing brand logo database functions...")

    # Test: Tabelle erstellen
    if DB_AVAILABLE:
        conn = get_db_connection()
        if conn:
            create_brand_logos_table(conn)
            conn.close()
            print("✓ Tabelle erstellt")

        # Test: Alle Logos auflisten
        logos = list_all_brand_logos()
        print(f"✓ Anzahl verfügbare Logos: {len(logos)}")
        for logo in logos:
            print(f"  - {logo['brand_name']} ({logo['logo_format']})")
    else:
        print("✗ Database nicht verfügbar für Tests")
