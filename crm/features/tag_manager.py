# crm/features/tag_manager.py
"""
Tag Management System für CRM
Ermöglicht Kategorisierung und Segmentierung von Kunden

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
from datetime import datetime
from typing import Any


def create_tag_tables(conn: sqlite3.Connection) -> None:
    """Erstellt die Tabellen für das Tag-System.
    
    Args:
        conn: SQLite Datenbankverbindung
    """
    cursor = conn.cursor()
    
    try:
        # 1. Tabelle: crm_tags (Tag-Definitionen)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crm_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#808080',
                category TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        print("DB: Tabelle 'crm_tags' erstellt/überprüft.")
        
        # 2. Tabelle: customer_tags (Many-to-Many Beziehung)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_by TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES crm_tags(id) ON DELETE CASCADE,
                UNIQUE(customer_id, tag_id)
            )
        """)
        print("DB: Tabelle 'customer_tags' erstellt/überprüft.")
        
        # 3. Indizes für Performance
        indices = [
            ("idx_crm_tags_name", "crm_tags", "name"),
            ("idx_crm_tags_category", "crm_tags", "category"),
            ("idx_customer_tags_customer_id", "customer_tags", "customer_id"),
            ("idx_customer_tags_tag_id", "customer_tags", "tag_id"),
        ]
        
        for index_name, table_name, column_name in indices:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
            except sqlite3.OperationalError:
                pass  # Index existiert bereits
        
        conn.commit()
        print("DB: Tag-System-Tabellen erfolgreich erstellt/aktualisiert.")
        
    except Exception as e:
        print(f"DB FEHLER beim Erstellen der Tag-Tabellen: {e}")
        conn.rollback()
        raise


# ============================================================================
# TAG CRUD OPERATIONS
# ============================================================================

def create_tag(
    conn: sqlite3.Connection,
    name: str,
    color: str = '#808080',
    category: str | None = None,
    description: str | None = None,
    created_by: str | None = None
) -> int | None:
    """Erstellt einen neuen Tag.
    
    Args:
        conn: Datenbankverbindung
        name: Tag-Name (eindeutig)
        color: Hex-Farbe für Tag (Standard: grau)
        category: Kategorie des Tags (optional)
        description: Beschreibung des Tags (optional)
        created_by: Ersteller des Tags (optional)
    
    Returns:
        Tag-ID bei Erfolg, None bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crm_tags (name, color, category, description, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (name.strip(), color, category, description, created_by))
        conn.commit()
        tag_id = cursor.lastrowid
        print(f"Tag erstellt: {name} (ID: {tag_id})")
        return tag_id
    except sqlite3.IntegrityError:
        print(f"Tag '{name}' existiert bereits.")
        return None
    except Exception as e:
        print(f"Fehler beim Erstellen des Tags: {e}")
        conn.rollback()
        return None


def get_tag_by_id(conn: sqlite3.Connection, tag_id: int) -> dict[str, Any] | None:
    """Lädt einen Tag anhand der ID.
    
    Args:
        conn: Datenbankverbindung
        tag_id: Tag-ID
    
    Returns:
        Tag-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crm_tags WHERE id = ?", (tag_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Fehler beim Laden des Tags: {e}")
        return None


def get_tag_by_name(conn: sqlite3.Connection, name: str) -> dict[str, Any] | None:
    """Lädt einen Tag anhand des Namens.
    
    Args:
        conn: Datenbankverbindung
        name: Tag-Name
    
    Returns:
        Tag-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crm_tags WHERE name = ?", (name.strip()))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Fehler beim Laden des Tags: {e}")
        return None


def get_all_tags(
    conn: sqlite3.Connection,
    category: str | None = None,
    active_only: bool = True
) -> list[dict[str, Any]]:
    """Lädt alle Tags.
    
    Args:
        conn: Datenbankverbindung
        category: Nur Tags dieser Kategorie laden (optional)
        active_only: Nur aktive Tags laden (Standard: True)
    
    Returns:
        Liste von Tag-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM crm_tags WHERE 1=1"
        params = []
        
        if active_only:
            query += " AND is_active = 1"
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY name ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Tags: {e}")
        return []


def update_tag(
    conn: sqlite3.Connection,
    tag_id: int,
    name: str | None = None,
    color: str | None = None,
    category: str | None = None,
    description: str | None = None,
    is_active: bool | None = None
) -> bool:
    """Aktualisiert einen Tag.
    
    Args:
        conn: Datenbankverbindung
        tag_id: Tag-ID
        name: Neuer Name (optional)
        color: Neue Farbe (optional)
        category: Neue Kategorie (optional)
        description: Neue Beschreibung (optional)
        is_active: Aktiv-Status (optional)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        
        # Baue UPDATE-Statement dynamisch
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name.strip())
        if color is not None:
            updates.append("color = ?")
            params.append(color)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if not updates:
            return True  # Nichts zu aktualisieren
        
        params.append(tag_id)
        query = f"UPDATE crm_tags SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        print(f"Tag-Name bereits vergeben.")
        return False
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Tags: {e}")
        conn.rollback()
        return False


def delete_tag(conn: sqlite3.Connection, tag_id: int) -> bool:
    """Löscht einen Tag (und alle Zuordnungen).
    
    Args:
        conn: Datenbankverbindung
        tag_id: Tag-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crm_tags WHERE id = ?", (tag_id,))
        conn.commit()
        print(f"Tag gelöscht (ID: {tag_id})")
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen des Tags: {e}")
        conn.rollback()
        return False


# ============================================================================
# CUSTOMER-TAG ASSIGNMENT OPERATIONS
# ============================================================================

def assign_tag_to_customer(
    conn: sqlite3.Connection,
    customer_id: int,
    tag_id: int,
    assigned_by: str | None = None
) -> bool:
    """Weist einem Kunden einen Tag zu.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
        tag_id: Tag-ID
        assigned_by: Zuweiser (optional)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer_tags (customer_id, tag_id, assigned_by)
            VALUES (?, ?, ?)
        """, (customer_id, tag_id, assigned_by))
        conn.commit()
        print(f"Tag {tag_id} zu Kunde {customer_id} zugewiesen")
        return True
    except sqlite3.IntegrityError:
        print(f"Tag bereits zugewiesen.")
        return False
    except Exception as e:
        print(f"Fehler beim Zuweisen des Tags: {e}")
        conn.rollback()
        return False


def remove_tag_from_customer(
    conn: sqlite3.Connection,
    customer_id: int,
    tag_id: int
) -> bool:
    """Entfernt einen Tag von einem Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
        tag_id: Tag-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM customer_tags 
            WHERE customer_id = ? AND tag_id = ?
        """, (customer_id, tag_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Entfernen des Tags: {e}")
        conn.rollback()
        return False


def get_customer_tags(conn: sqlite3.Connection, customer_id: int) -> list[dict[str, Any]]:
    """Lädt alle Tags eines Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
    
    Returns:
        Liste von Tag-Dictionaries
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, ct.assigned_at, ct.assigned_by
            FROM crm_tags t
            JOIN customer_tags ct ON t.id = ct.tag_id
            WHERE ct.customer_id = ?
            ORDER BY t.name ASC
        """, (customer_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kunden-Tags: {e}")
        return []


def get_customers_by_tag(conn: sqlite3.Connection, tag_id: int) -> list[int]:
    """Lädt alle Kunden-IDs mit einem bestimmten Tag.
    
    Args:
        conn: Datenbankverbindung
        tag_id: Tag-ID
    
    Returns:
        Liste von Kunden-IDs
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT customer_id 
            FROM customer_tags 
            WHERE tag_id = ?
            ORDER BY assigned_at DESC
        """, (tag_id))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kunden nach Tag: {e}")
        return []


def get_customers_by_tags(
    conn: sqlite3.Connection,
    tag_ids: list[int],
    match_all: bool = False
) -> list[int]:
    """Lädt alle Kunden-IDs mit bestimmten Tags.
    
    Args:
        conn: Datenbankverbindung
        tag_ids: Liste von Tag-IDs
        match_all: True = Kunde muss alle Tags haben, False = mindestens einen Tag
    
    Returns:
        Liste von Kunden-IDs
    """
    try:
        if not tag_ids:
            return []
        
        cursor = conn.cursor()
        
        if match_all:
            # Kunde muss ALLE Tags haben
            placeholders = ','.join('?' * len(tag_ids))
            cursor.execute(f"""
                SELECT customer_id
                FROM customer_tags
                WHERE tag_id IN ({placeholders})
                GROUP BY customer_id
                HAVING COUNT(DISTINCT tag_id) = ?
            """, (*tag_ids, len(tag_ids)))
        else:
            # Kunde muss MINDESTENS EINEN Tag haben
            placeholders = ','.join('?' * len(tag_ids))
            cursor.execute(f"""
                SELECT DISTINCT customer_id
                FROM customer_tags
                WHERE tag_id IN ({placeholders})
            """, tag_ids)
        
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kunden nach Tags: {e}")
        return []


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def assign_tags_to_customers(
    conn: sqlite3.Connection,
    customer_ids: list[int],
    tag_ids: list[int],
    assigned_by: str | None = None
) -> dict[str, int]:
    """Weist mehreren Kunden mehrere Tags zu (Massen-Tagging).
    
    Args:
        conn: Datenbankverbindung
        customer_ids: Liste von Kunden-IDs
        tag_ids: Liste von Tag-IDs
        assigned_by: Zuweiser (optional)
    
    Returns:
        Dictionary mit Statistiken (success, skipped, errors)
    """
    stats = {'success': 0, 'skipped': 0, 'errors': 0}
    
    try:
        cursor = conn.cursor()
        
        for customer_id in customer_ids:
            for tag_id in tag_ids:
                try:
                    cursor.execute("""
                        INSERT INTO customer_tags (customer_id, tag_id, assigned_by)
                        VALUES (?, ?, ?)
                    """, (customer_id, tag_id, assigned_by))
                    stats['success'] += 1
                except sqlite3.IntegrityError:
                    stats['skipped'] += 1  # Bereits zugewiesen
                except Exception:
                    stats['errors'] += 1
        
        conn.commit()
        print(f"Massen-Tagging: {stats['success']} zugewiesen, {stats['skipped']} übersprungen, {stats['errors']} Fehler")
        return stats
    except Exception as e:
        print(f"Fehler beim Massen-Tagging: {e}")
        conn.rollback()
        stats['errors'] += len(customer_ids) * len(tag_ids)
        return stats


def remove_tags_from_customers(
    conn: sqlite3.Connection,
    customer_ids: list[int],
    tag_ids: list[int]
) -> int:
    """Entfernt mehrere Tags von mehreren Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_ids: Liste von Kunden-IDs
        tag_ids: Liste von Tag-IDs
    
    Returns:
        Anzahl entfernter Zuordnungen
    """
    try:
        cursor = conn.cursor()
        
        customer_placeholders = ','.join('?' * len(customer_ids))
        tag_placeholders = ','.join('?' * len(tag_ids))
        
        cursor.execute(f"""
            DELETE FROM customer_tags 
            WHERE customer_id IN ({customer_placeholders})
            AND tag_id IN ({tag_placeholders})
        """, (*customer_ids, *tag_ids))
        
        conn.commit()
        removed_count = cursor.rowcount
        print(f"Massen-Entfernung: {removed_count} Tag-Zuordnungen entfernt")
        return removed_count
    except Exception as e:
        print(f"Fehler beim Massen-Entfernen: {e}")
        conn.rollback()
        return 0


# ============================================================================
# STATISTICS
# ============================================================================

def get_tag_statistics(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Lädt Statistiken für alle Tags.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Dictionaries mit Tag-Statistiken
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.id,
                t.name,
                t.color,
                t.category,
                COUNT(ct.customer_id) as customer_count
            FROM crm_tags t
            LEFT JOIN customer_tags ct ON t.id = ct.tag_id
            WHERE t.is_active = 1
            GROUP BY t.id, t.name, t.color, t.category
            ORDER BY customer_count DESC, t.name ASC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Tag-Statistiken: {e}")
        return []


def get_tag_categories(conn: sqlite3.Connection) -> list[str]:
    """Lädt alle verwendeten Tag-Kategorien.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Kategorien
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category 
            FROM crm_tags 
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category ASC
        """)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kategorien: {e}")
        return []


# ============================================================================
# INITIALIZATION
# ============================================================================

def ensure_tag_tables() -> None:
    """Stellt sicher, dass die Tag-Tabellen existieren."""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            create_tag_tables(conn)
            conn.close()
    except Exception as e:
        print(f"Fehler beim Initialisieren der Tag-Tabellen: {e}")


# Initialisiere Tabellen beim Import
try:
    ensure_tag_tables()
except Exception:
    pass  # Fehler beim Import ignorieren
