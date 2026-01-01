# crm/features/note_manager.py
"""
Notizen und Kommunikationshistorie Management für CRM-System.

Dieses Modul verwaltet alle Aktivitäten (Notizen, E-Mails, Anrufe, Termine)
mit Volltextsuche und Timeline-Funktionalität.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db_connection


# Aktivitätstypen
ACTIVITY_TYPES = {
    "note": "Notiz",
    "email": "E-Mail",
    "call": "Anruf",
    "appointment": "Termin",
    "meeting": "Besprechung",
    "task": "Aufgabe",
    "other": "Sonstiges"
}


def create_activity(
    customer_id: int,
    activity_type: str,
    title: str,
    content: str = "",
    created_by: str = "System",
    is_important: bool = False
) -> Optional[int]:
    """
    Erstellt eine neue Aktivität für einen Kunden.
    
    Args:
        customer_id: ID des Kunden
        activity_type: Typ der Aktivität (note, email, call, appointment, etc.)
        title: Titel der Aktivität
        content: Inhalt/Beschreibung der Aktivität
        created_by: Name des Erstellers
        is_important: Ob die Aktivität als wichtig markiert ist
        
    Returns:
        ID der erstellten Aktivität oder None bei Fehler
    """
    if activity_type not in ACTIVITY_TYPES:
        print(f"Ungültiger Aktivitätstyp: {activity_type}")
        return None
        
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO crm_activities 
            (customer_id, activity_type, title, content, created_by, is_important)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (customer_id, activity_type, title, content, created_by, int(is_important))
        )
        conn.commit()
        activity_id = cursor.lastrowid
        print(f"Aktivität erstellt: ID {activity_id}")
        return activity_id
    except Exception as e:
        print(f"Fehler beim Erstellen der Aktivität: {e}")
        return None
    finally:
        conn.close()


def get_activity(activity_id: int) -> Optional[Dict[str, Any]]:
    """
    Ruft eine einzelne Aktivität ab.
    
    Args:
        activity_id: ID der Aktivität
        
    Returns:
        Dictionary mit Aktivitätsdaten oder None
    """
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, customer_id, activity_type, title, content, 
                   created_by, created_at, is_important, archived
            FROM crm_activities
            WHERE id = ?
            """,
            (activity_id)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "customer_id": row[1],
                "activity_type": row[2],
                "activity_type_display": ACTIVITY_TYPES.get(row[2], row[2]),
                "title": row[3],
                "content": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "is_important": bool(row[7]),
                "archived": bool(row[8])
            }
        return None
    except Exception as e:
        print(f"Fehler beim Abrufen der Aktivität: {e}")
        return None
    finally:
        conn.close()


def get_customer_activities(
    customer_id: int,
    activity_type: Optional[str] = None,
    include_archived: bool = False,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Ruft alle Aktivitäten eines Kunden ab.
    
    Args:
        customer_id: ID des Kunden
        activity_type: Optional - Filter nach Aktivitätstyp
        include_archived: Ob archivierte Aktivitäten eingeschlossen werden sollen
        limit: Maximale Anzahl der Ergebnisse
        
    Returns:
        Liste von Aktivitäts-Dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        
        # Basis-Query
        query = """
            SELECT id, customer_id, activity_type, title, content, 
                   created_by, created_at, is_important, archived
            FROM crm_activities
            WHERE customer_id = ?
        """
        params = [customer_id]
        
        # Filter nach Typ
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
            
        # Filter archivierte
        if not include_archived:
            query += " AND archived = 0"
            
        # Sortierung und Limit
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        activities = []
        for row in rows:
            activities.append({
                "id": row[0],
                "customer_id": row[1],
                "activity_type": row[2],
                "activity_type_display": ACTIVITY_TYPES.get(row[2], row[2]),
                "title": row[3],
                "content": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "is_important": bool(row[7]),
                "archived": bool(row[8]),
                "is_old": _is_activity_old(row[6])
            })
            
        return activities
    except Exception as e:
        print(f"Fehler beim Abrufen der Aktivitäten: {e}")
        return []
    finally:
        conn.close()


def update_activity(
    activity_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    is_important: Optional[bool] = None,
    archived: Optional[bool] = None
) -> bool:
    """
    Aktualisiert eine Aktivität.
    
    Args:
        activity_id: ID der Aktivität
        title: Neuer Titel (optional)
        content: Neuer Inhalt (optional)
        is_important: Neuer wichtig-Status (optional)
        archived: Neuer archiviert-Status (optional)
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Baue Update-Query dynamisch
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
            
        if content is not None:
            updates.append("content = ?")
            params.append(content)
            
        if is_important is not None:
            updates.append("is_important = ?")
            params.append(int(is_important))
            
        if archived is not None:
            updates.append("archived = ?")
            params.append(int(archived))
            
        if not updates:
            return True  # Nichts zu aktualisieren
            
        params.append(activity_id)
        query = f"UPDATE crm_activities SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Aktivität: {e}")
        return False
    finally:
        conn.close()


def delete_activity(activity_id: int) -> bool:
    """
    Löscht eine Aktivität.
    
    Args:
        activity_id: ID der Aktivität
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crm_activities WHERE id = ?", (activity_id))
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen der Aktivität: {e}")
        return False
    finally:
        conn.close()


def toggle_important(activity_id: int) -> bool:
    """
    Schaltet den wichtig-Status einer Aktivität um.
    
    Args:
        activity_id: ID der Aktivität
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE crm_activities 
            SET is_important = NOT is_important 
            WHERE id = ?
            """,
            (activity_id)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Umschalten des wichtig-Status: {e}")
        return False
    finally:
        conn.close()


def search_activities(
    search_term: str,
    customer_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Volltextsuche in Aktivitäten.
    
    Args:
        search_term: Suchbegriff
        customer_id: Optional - Filter nach Kunden-ID
        activity_type: Optional - Filter nach Aktivitätstyp
        limit: Maximale Anzahl der Ergebnisse
        
    Returns:
        Liste von Aktivitäts-Dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        
        # Einfache LIKE-Suche (SQLite FTS5 kann später hinzugefügt werden)
        query = """
            SELECT id, customer_id, activity_type, title, content, 
                   created_by, created_at, is_important, archived
            FROM crm_activities
            WHERE (title LIKE ? OR content LIKE ?)
        """
        search_pattern = f"%{search_term}%"
        params = [search_pattern, search_pattern]
        
        if customer_id:
            query += " AND customer_id = ?"
            params.append(customer_id)
            
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
            
        query += " AND archived = 0 ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        activities = []
        for row in rows:
            activities.append({
                "id": row[0],
                "customer_id": row[1],
                "activity_type": row[2],
                "activity_type_display": ACTIVITY_TYPES.get(row[2], row[2]),
                "title": row[3],
                "content": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "is_important": bool(row[7]),
                "archived": bool(row[8])
            })
            
        return activities
    except Exception as e:
        print(f"Fehler bei der Suche: {e}")
        return []
    finally:
        conn.close()


def auto_archive_old_activities(days_threshold: int = 30) -> int:
    """
    Archiviert automatisch Aktivitäten, die älter als X Tage sind.
    
    Args:
        days_threshold: Anzahl der Tage, nach denen archiviert wird
        
    Returns:
        Anzahl der archivierten Aktivitäten
    """
    conn = get_db_connection()
    if not conn:
        return 0
        
    try:
        cursor = conn.cursor()
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        cursor.execute(
            """
            UPDATE crm_activities 
            SET archived = 1 
            WHERE created_at < ? AND archived = 0 AND is_important = 0
            """,
            (threshold_date.strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        
        count = cursor.rowcount
        if count > 0:
            print(f"{count} Aktivitäten automatisch archiviert")
        return count
    except Exception as e:
        print(f"Fehler beim Auto-Archivieren: {e}")
        return 0
    finally:
        conn.close()


def get_activity_statistics(customer_id: int) -> Dict[str, Any]:
    """
    Ruft Statistiken über Aktivitäten eines Kunden ab.
    
    Args:
        customer_id: ID des Kunden
        
    Returns:
        Dictionary mit Statistiken
    """
    conn = get_db_connection()
    if not conn:
        return {}
        
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl
        cursor.execute(
            "SELECT COUNT(*) FROM crm_activities WHERE customer_id = ? AND archived = 0",
            (customer_id)
        )
        total = cursor.fetchone()[0]
        
        # Nach Typ
        cursor.execute(
            """
            SELECT activity_type, COUNT(*) 
            FROM crm_activities 
            WHERE customer_id = ? AND archived = 0
            GROUP BY activity_type
            """,
            (customer_id)
        )
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Wichtige
        cursor.execute(
            "SELECT COUNT(*) FROM crm_activities WHERE customer_id = ? AND is_important = 1 AND archived = 0",
            (customer_id)
        )
        important = cursor.fetchone()[0]
        
        # Letzte Aktivität
        cursor.execute(
            "SELECT created_at FROM crm_activities WHERE customer_id = ? ORDER BY created_at DESC LIMIT 1",
            (customer_id)
        )
        last_activity_row = cursor.fetchone()
        last_activity = last_activity_row[0] if last_activity_row else None
        
        return {
            "total": total,
            "by_type": by_type,
            "important": important,
            "last_activity": last_activity
        }
    except Exception as e:
        print(f"Fehler beim Abrufen der Statistiken: {e}")
        return {}
    finally:
        conn.close()


def _is_activity_old(created_at: str, days_threshold: int = 30) -> bool:
    """
    Prüft, ob eine Aktivität als "alt" gilt.
    
    Args:
        created_at: Erstellungsdatum als String
        days_threshold: Anzahl der Tage für "alt"
        
    Returns:
        True wenn alt, False sonst
    """
    try:
        created_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        return created_date < threshold_date
    except Exception:
        return False


# Hilfsfunktionen für spezifische Aktivitätstypen

def add_note(customer_id: int, title: str, content: str, created_by: str = "System", is_important: bool = False) -> Optional[int]:
    """Fügt eine Notiz hinzu."""
    return create_activity(customer_id, "note", title, content, created_by, is_important)


def add_email_activity(customer_id: int, subject: str, body: str, created_by: str = "System") -> Optional[int]:
    """Fügt eine E-Mail-Aktivität hinzu."""
    return create_activity(customer_id, "email", subject, body, created_by, False)


def add_call_activity(customer_id: int, title: str, notes: str, created_by: str = "System") -> Optional[int]:
    """Fügt eine Anruf-Aktivität hinzu."""
    return create_activity(customer_id, "call", title, notes, created_by, False)


def add_appointment_activity(customer_id: int, title: str, details: str, created_by: str = "System") -> Optional[int]:
    """Fügt eine Termin-Aktivität hinzu."""
    return create_activity(customer_id, "appointment", title, details, created_by, False)
