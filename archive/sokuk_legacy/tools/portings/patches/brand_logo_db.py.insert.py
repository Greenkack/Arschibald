# === AUTO-GENERATED INSERT PATCH ===
# target_module: brand_logo_db.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import base64
import os
import sqlite3
import traceback
from typing import Any


# --- DEF BLOCK START: func create_brand_logos_table ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func add_brand_logo ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func get_brand_logo ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func list_all_brand_logos ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func delete_brand_logo ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func upload_logo_from_file ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func update_logo_position ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func get_logos_for_brands ---
def get_logos_for_brands(brand_names: list[str]) -> dict[str, dict[str, Any]]:
    """Holt Logos für eine Liste von Herstellern"""
    if not DB_AVAILABLE:
        return {}

    try:
        conn = get_db_connection()
        if not conn:
            return {}

        # Tabelle erstellen falls sie nicht existiert
        create_brand_logos_table(conn)

        cursor = conn.cursor()

        # Placeholder für IN-Klausel erstellen
        placeholders = ','.join('?' * len(brand_names))

        cursor.execute(f"""
            SELECT brand_name, logo_base64, logo_format, file_size_bytes,
                   logo_position_x, logo_position_y, logo_width, logo_height,
                   is_active, created_at, updated_at
            FROM brand_logos
            WHERE brand_name IN ({placeholders}) AND is_active = 1
        """, brand_names)

        results = cursor.fetchall()
        conn.close()

        logos_dict = {}
        for result in results:
            logos_dict[result[0]] = {
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

        return logos_dict

    except Exception as e:
        print(f"Fehler beim Abrufen der Logos für Herstellerliste: {e}")
        return {}
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func deactivate_brand_logo ---
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
# --- DEF BLOCK END ---
