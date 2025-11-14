# crm/features/template_manager.py
"""
Dokument-Vorlagen-Management System für CRM
Ermöglicht Verwaltung von Dokument-Vorlagen mit Platzhalter-System

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
import re
from datetime import datetime
from typing import Any


def create_template_tables(conn: sqlite3.Connection) -> None:
    """Erstellt die Tabellen für das Vorlagen-System.
    
    Args:
        conn: SQLite Datenbankverbindung
    """
    cursor = conn.cursor()
    
    try:
        # 1. Tabelle: document_templates (Vorlagen-Definitionen)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                placeholders TEXT,
                version INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        """)
        print("DB: Tabelle 'document_templates' erstellt/überprüft.")
        
        # 2. Tabelle: template_versions (Versionsverlauf)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                placeholders TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                change_note TEXT,
                FOREIGN KEY (template_id) REFERENCES document_templates(id) ON DELETE CASCADE,
                UNIQUE(template_id, version)
            )
        """)
        print("DB: Tabelle 'template_versions' erstellt/überprüft.")
        
        # 3. Indizes für Performance
        indices = [
            ("idx_document_templates_name", "document_templates", "name"),
            ("idx_document_templates_category", "document_templates", "category"),
            ("idx_document_templates_active", "document_templates", "is_active"),
            ("idx_template_versions_template_id", "template_versions", "template_id"),
        ]
        
        for index_name, table_name, column_name in indices:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
            except sqlite3.OperationalError:
                pass  # Index existiert bereits
        
        conn.commit()
        print("DB: Vorlagen-System-Tabellen erfolgreich erstellt/aktualisiert.")
        
    except Exception as e:
        print(f"DB FEHLER beim Erstellen der Vorlagen-Tabellen: {e}")
        conn.rollback()
        raise


# ============================================================================
# PLACEHOLDER UTILITIES
# ============================================================================

def extract_placeholders(content: str) -> list[str]:
    """Extrahiert alle Platzhalter aus einem Template-Inhalt.
    
    Platzhalter-Format: {{placeholder_name}}
    
    Args:
        content: Template-Inhalt
    
    Returns:
        Liste von Platzhalter-Namen (ohne {{}})
    """
    pattern = r'\{\{([a-zA-Z0-9_]+)\}\}'
    matches = re.findall(pattern, content)
    return list(set(matches))  # Duplikate entfernen


def replace_placeholders(content: str, data: dict[str, Any]) -> str:
    """Ersetzt Platzhalter im Template mit tatsächlichen Werten.
    
    Args:
        content: Template-Inhalt mit Platzhaltern
        data: Dictionary mit Werten für Platzhalter
    
    Returns:
        Inhalt mit ersetzten Platzhaltern
    """
    result = content
    
    for key, value in data.items():
        placeholder = f"{{{{{key}}}}}"
        # Konvertiere Wert zu String, behandle None
        str_value = "" if value is None else str(value)
        result = result.replace(placeholder, str_value)
    
    return result


def validate_placeholders(content: str, available_placeholders: list[str]) -> dict[str, list[str]]:
    """Validiert Platzhalter im Template.
    
    Args:
        content: Template-Inhalt
        available_placeholders: Liste verfügbarer Platzhalter
    
    Returns:
        Dictionary mit 'valid' und 'invalid' Listen
    """
    used_placeholders = extract_placeholders(content)
    available_set = set(available_placeholders)
    
    valid = [p for p in used_placeholders if p in available_set]
    invalid = [p for p in used_placeholders if p not in available_set]
    
    return {
        'valid': valid,
        'invalid': invalid,
        'unused': [p for p in available_placeholders if p not in used_placeholders]
    }


# ============================================================================
# TEMPLATE CRUD OPERATIONS
# ============================================================================

def create_template(
    conn: sqlite3.Connection,
    name: str,
    category: str,
    content: str,
    description: str | None = None,
    created_by: str | None = None
) -> int | None:
    """Erstellt eine neue Dokument-Vorlage.
    
    Args:
        conn: Datenbankverbindung
        name: Vorlagen-Name
        category: Kategorie (z.B. 'Angebot', 'Vertrag', 'Brief')
        content: Template-Inhalt mit Platzhaltern
        description: Beschreibung der Vorlage (optional)
        created_by: Ersteller (optional)
    
    Returns:
        Template-ID bei Erfolg, None bei Fehler
    """
    try:
        # Extrahiere Platzhalter
        placeholders = extract_placeholders(content)
        placeholders_str = ','.join(placeholders) if placeholders else None
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO document_templates 
            (name, category, content, placeholders, description, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), category, content, placeholders_str, description, created_by, created_by))
        
        template_id = cursor.lastrowid
        
        # Erstelle erste Version
        cursor.execute("""
            INSERT INTO template_versions 
            (template_id, version, content, placeholders, created_by, change_note)
            VALUES (?, 1, ?, ?, ?, 'Initiale Version')
        """, (template_id, content, placeholders_str, created_by))
        
        conn.commit()
        print(f"Template erstellt: {name} (ID: {template_id})")
        return template_id
    except Exception as e:
        print(f"Fehler beim Erstellen des Templates: {e}")
        conn.rollback()
        return None


def get_template_by_id(conn: sqlite3.Connection, template_id: int) -> dict[str, Any] | None:
    """Lädt eine Vorlage anhand der ID.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
    
    Returns:
        Template-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM document_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        
        if row:
            template = dict(row)
            # Parse Platzhalter-String zu Liste
            if template.get('placeholders'):
                template['placeholders'] = template['placeholders'].split(',')
            else:
                template['placeholders'] = []
            return template
        return None
    except Exception as e:
        print(f"Fehler beim Laden des Templates: {e}")
        return None


def get_template_by_name(conn: sqlite3.Connection, name: str) -> dict[str, Any] | None:
    """Lädt eine Vorlage anhand des Namens.
    
    Args:
        conn: Datenbankverbindung
        name: Template-Name
    
    Returns:
        Template-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM document_templates WHERE name = ?", (name.strip(),))
        row = cursor.fetchone()
        
        if row:
            template = dict(row)
            if template.get('placeholders'):
                template['placeholders'] = template['placeholders'].split(',')
            else:
                template['placeholders'] = []
            return template
        return None
    except Exception as e:
        print(f"Fehler beim Laden des Templates: {e}")
        return None


def get_all_templates(
    conn: sqlite3.Connection,
    category: str | None = None,
    active_only: bool = True
) -> list[dict[str, Any]]:
    """Lädt alle Vorlagen.
    
    Args:
        conn: Datenbankverbindung
        category: Nur Vorlagen dieser Kategorie laden (optional)
        active_only: Nur aktive Vorlagen laden (Standard: True)
    
    Returns:
        Liste von Template-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM document_templates WHERE 1=1"
        params = []
        
        if active_only:
            query += " AND is_active = 1"
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY category ASC, name ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            template = dict(row)
            if template.get('placeholders'):
                template['placeholders'] = template['placeholders'].split(',')
            else:
                template['placeholders'] = []
            templates.append(template)
        
        return templates
    except Exception as e:
        print(f"Fehler beim Laden der Templates: {e}")
        return []


def update_template(
    conn: sqlite3.Connection,
    template_id: int,
    name: str | None = None,
    category: str | None = None,
    content: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
    updated_by: str | None = None,
    change_note: str | None = None
) -> bool:
    """Aktualisiert eine Vorlage und erstellt neue Version bei Inhaltsänderung.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
        name: Neuer Name (optional)
        category: Neue Kategorie (optional)
        content: Neuer Inhalt (optional, erstellt neue Version)
        description: Neue Beschreibung (optional)
        is_active: Aktiv-Status (optional)
        updated_by: Bearbeiter (optional)
        change_note: Änderungsnotiz für Versionierung (optional)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        
        # Lade aktuelle Version
        cursor.execute("SELECT version, content FROM document_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        current_version = row[0]
        current_content = row[1]
        
        # Baue UPDATE-Statement dynamisch
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name.strip())
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        # Bei Inhaltsänderung: neue Version erstellen
        if content is not None and content != current_content:
            new_version = current_version + 1
            placeholders = extract_placeholders(content)
            placeholders_str = ','.join(placeholders) if placeholders else None
            
            updates.append("content = ?")
            params.append(content)
            updates.append("placeholders = ?")
            params.append(placeholders_str)
            updates.append("version = ?")
            params.append(new_version)
            
            # Speichere neue Version
            cursor.execute("""
                INSERT INTO template_versions 
                (template_id, version, content, placeholders, created_by, change_note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (template_id, new_version, content, placeholders_str, updated_by, change_note or 'Aktualisierung'))
        
        if updated_by is not None:
            updates.append("updated_by = ?")
            params.append(updated_by)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        if not updates:
            return True  # Nichts zu aktualisieren
        
        params.append(template_id)
        query = f"UPDATE document_templates SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Templates: {e}")
        conn.rollback()
        return False


def delete_template(conn: sqlite3.Connection, template_id: int) -> bool:
    """Löscht eine Vorlage (und alle Versionen).
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM document_templates WHERE id = ?", (template_id,))
        conn.commit()
        print(f"Template gelöscht (ID: {template_id})")
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen des Templates: {e}")
        conn.rollback()
        return False


# ============================================================================
# VERSION MANAGEMENT
# ============================================================================

def get_template_versions(conn: sqlite3.Connection, template_id: int) -> list[dict[str, Any]]:
    """Lädt alle Versionen einer Vorlage.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
    
    Returns:
        Liste von Versions-Dictionaries (neueste zuerst)
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM template_versions 
            WHERE template_id = ?
            ORDER BY version DESC
        """, (template_id,))
        rows = cursor.fetchall()
        
        versions = []
        for row in rows:
            version = dict(row)
            if version.get('placeholders'):
                version['placeholders'] = version['placeholders'].split(',')
            else:
                version['placeholders'] = []
            versions.append(version)
        
        return versions
    except Exception as e:
        print(f"Fehler beim Laden der Template-Versionen: {e}")
        return []


def get_template_version(
    conn: sqlite3.Connection,
    template_id: int,
    version: int
) -> dict[str, Any] | None:
    """Lädt eine spezifische Version einer Vorlage.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
        version: Versionsnummer
    
    Returns:
        Versions-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM template_versions 
            WHERE template_id = ? AND version = ?
        """, (template_id, version))
        row = cursor.fetchone()
        
        if row:
            version_data = dict(row)
            if version_data.get('placeholders'):
                version_data['placeholders'] = version_data['placeholders'].split(',')
            else:
                version_data['placeholders'] = []
            return version_data
        return None
    except Exception as e:
        print(f"Fehler beim Laden der Template-Version: {e}")
        return None


def restore_template_version(
    conn: sqlite3.Connection,
    template_id: int,
    version: int,
    restored_by: str | None = None
) -> bool:
    """Stellt eine frühere Version einer Vorlage wieder her.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
        version: Versionsnummer zum Wiederherstellen
        restored_by: Benutzer der wiederherstellt (optional)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Lade die gewünschte Version
        version_data = get_template_version(conn, template_id, version)
        if not version_data:
            return False
        
        # Aktualisiere Template mit Inhalt der alten Version
        return update_template(
            conn,
            template_id,
            content=version_data['content'],
            updated_by=restored_by,
            change_note=f"Wiederherstellung von Version {version}"
        )
    except Exception as e:
        print(f"Fehler beim Wiederherstellen der Template-Version: {e}")
        return False


# ============================================================================
# TEMPLATE RENDERING
# ============================================================================

def render_template(
    conn: sqlite3.Connection,
    template_id: int,
    data: dict[str, Any]
) -> str | None:
    """Rendert eine Vorlage mit den gegebenen Daten.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
        data: Dictionary mit Werten für Platzhalter
    
    Returns:
        Gerenderter Inhalt oder None bei Fehler
    """
    try:
        template = get_template_by_id(conn, template_id)
        if not template:
            return None
        
        return replace_placeholders(template['content'], data)
    except Exception as e:
        print(f"Fehler beim Rendern des Templates: {e}")
        return None


def preview_template(
    conn: sqlite3.Connection,
    template_id: int,
    sample_data: dict[str, Any] | None = None
) -> str | None:
    """Erstellt eine Vorschau einer Vorlage mit Beispieldaten.
    
    Args:
        conn: Datenbankverbindung
        template_id: Template-ID
        sample_data: Beispieldaten (optional, sonst Platzhalter-Namen)
    
    Returns:
        Vorschau-Inhalt oder None bei Fehler
    """
    try:
        template = get_template_by_id(conn, template_id)
        if not template:
            return None
        
        # Wenn keine Beispieldaten gegeben, nutze Platzhalter-Namen
        if sample_data is None:
            sample_data = {p: f"[{p}]" for p in template['placeholders']}
        
        return replace_placeholders(template['content'], sample_data)
    except Exception as e:
        print(f"Fehler beim Erstellen der Template-Vorschau: {e}")
        return None


# ============================================================================
# STATISTICS & UTILITIES
# ============================================================================

def get_template_categories(conn: sqlite3.Connection) -> list[str]:
    """Lädt alle verwendeten Template-Kategorien.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Kategorien
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category 
            FROM document_templates 
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category ASC
        """)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kategorien: {e}")
        return []


def get_template_statistics(conn: sqlite3.Connection) -> dict[str, Any]:
    """Lädt Statistiken über Vorlagen.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl
        cursor.execute("SELECT COUNT(*) FROM document_templates")
        total = cursor.fetchone()[0]
        
        # Aktive Vorlagen
        cursor.execute("SELECT COUNT(*) FROM document_templates WHERE is_active = 1")
        active = cursor.fetchone()[0]
        
        # Nach Kategorie
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM document_templates
            WHERE is_active = 1
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_category': by_category
        }
    except Exception as e:
        print(f"Fehler beim Laden der Template-Statistiken: {e}")
        return {'total': 0, 'active': 0, 'inactive': 0, 'by_category': {}}


def duplicate_template(
    conn: sqlite3.Connection,
    template_id: int,
    new_name: str,
    created_by: str | None = None
) -> int | None:
    """Dupliziert eine Vorlage.
    
    Args:
        conn: Datenbankverbindung
        template_id: ID der zu duplizierenden Vorlage
        new_name: Name für die neue Vorlage
        created_by: Ersteller (optional)
    
    Returns:
        ID der neuen Vorlage oder None bei Fehler
    """
    try:
        template = get_template_by_id(conn, template_id)
        if not template:
            return None
        
        return create_template(
            conn,
            name=new_name,
            category=template['category'],
            content=template['content'],
            description=f"Kopie von: {template['name']}",
            created_by=created_by
        )
    except Exception as e:
        print(f"Fehler beim Duplizieren des Templates: {e}")
        return None


# ============================================================================
# INITIALIZATION
# ============================================================================

def ensure_template_tables() -> None:
    """Stellt sicher, dass die Template-Tabellen existieren."""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            create_template_tables(conn)
            conn.close()
    except Exception as e:
        print(f"Fehler beim Initialisieren der Template-Tabellen: {e}")


# Initialisiere Tabellen beim Import
try:
    ensure_template_tables()
except Exception:
    pass  # Fehler beim Import ignorieren
