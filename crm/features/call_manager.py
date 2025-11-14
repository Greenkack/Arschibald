# crm/features/call_manager.py
"""
Anruf-Protokollierung für CRM-System.

Dieses Modul verwaltet Telefonanrufe mit Timer, Richtung (eingehend/ausgehend),
Telefonnummer-Auswahl und Integration in die Kommunikations-Timeline.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db_connection


# Anruf-Richtungen
CALL_DIRECTIONS = {
    "incoming": "Eingehend",
    "outgoing": "Ausgehend"
}


def ensure_call_fields() -> bool:
    """
    Stellt sicher, dass die crm_activities Tabelle alle benötigten Felder für Anrufe hat.
    Fügt fehlende Spalten hinzu, falls nötig.
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Prüfe, welche Spalten bereits existieren
        cursor.execute("PRAGMA table_info(crm_activities)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Füge fehlende Spalten hinzu
        columns_to_add = {
            "call_direction": "TEXT",  # 'incoming' oder 'outgoing'
            "call_phone_number": "TEXT",  # Telefonnummer
            "call_duration_seconds": "INTEGER DEFAULT 0",  # Dauer in Sekunden
            "call_notes": "TEXT"  # Zusätzliche Notizen zum Anruf
        }
        
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE crm_activities ADD COLUMN {column_name} {column_type}")
                    print(f"DB: Spalte '{column_name}' zu crm_activities hinzugefügt.")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"DB Warnung: Fehler beim Hinzufügen von '{column_name}': {e}")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Fehler beim Sicherstellen der Anruf-Felder: {e}")
        return False
    finally:
        conn.close()


def create_call(
    customer_id: int,
    phone_number: str,
    direction: str,
    duration_seconds: int = 0,
    notes: str = "",
    created_by: str = "System"
) -> Optional[int]:
    """
    Erstellt einen neuen Anruf-Eintrag.
    
    Args:
        customer_id: ID des Kunden
        phone_number: Telefonnummer
        direction: Richtung ('incoming' oder 'outgoing')
        duration_seconds: Dauer des Anrufs in Sekunden
        notes: Notizen zum Anruf
        created_by: Name des Erstellers
        
    Returns:
        ID des erstellten Anrufs oder None bei Fehler
    """
    if direction not in CALL_DIRECTIONS:
        print(f"Ungültige Anruf-Richtung: {direction}")
        return None
    
    # Stelle sicher, dass die Felder existieren
    ensure_call_fields()
    
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        
        # Erstelle Titel basierend auf Richtung
        direction_text = CALL_DIRECTIONS[direction]
        title = f"{direction_text}er Anruf - {phone_number}"
        
        # Formatiere Dauer für Content
        duration_text = format_duration(duration_seconds)
        content = f"Dauer: {duration_text}"
        if notes:
            content += f"\n\nNotizen:\n{notes}"
        
        cursor.execute(
            """
            INSERT INTO crm_activities 
            (customer_id, activity_type, title, content, created_by, 
             call_direction, call_phone_number, call_duration_seconds, call_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (customer_id, "call", title, content, created_by, 
             direction, phone_number, duration_seconds, notes)
        )
        conn.commit()
        call_id = cursor.lastrowid
        print(f"Anruf erstellt: ID {call_id}")
        return call_id
    except Exception as e:
        print(f"Fehler beim Erstellen des Anrufs: {e}")
        return None
    finally:
        conn.close()


def get_call(call_id: int) -> Optional[Dict[str, Any]]:
    """
    Ruft einen einzelnen Anruf ab.
    
    Args:
        call_id: ID des Anrufs
        
    Returns:
        Dictionary mit Anrufdaten oder None
    """
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, customer_id, activity_type, title, content, 
                   created_by, created_at, is_important, archived,
                   call_direction, call_phone_number, call_duration_seconds, call_notes
            FROM crm_activities
            WHERE id = ? AND activity_type = 'call'
            """,
            (call_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "customer_id": row[1],
                "activity_type": row[2],
                "title": row[3],
                "content": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "is_important": bool(row[7]),
                "archived": bool(row[8]),
                "call_direction": row[9],
                "call_direction_display": CALL_DIRECTIONS.get(row[9], row[9]) if row[9] else None,
                "call_phone_number": row[10],
                "call_duration_seconds": row[11] or 0,
                "call_duration_formatted": format_duration(row[11] or 0),
                "call_notes": row[12]
            }
        return None
    except Exception as e:
        print(f"Fehler beim Abrufen des Anrufs: {e}")
        return None
    finally:
        conn.close()


def get_customer_calls(
    customer_id: int,
    direction: Optional[str] = None,
    include_archived: bool = False,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Ruft alle Anrufe eines Kunden ab.
    
    Args:
        customer_id: ID des Kunden
        direction: Optional - Filter nach Richtung ('incoming' oder 'outgoing')
        include_archived: Ob archivierte Anrufe eingeschlossen werden sollen
        limit: Maximale Anzahl der Ergebnisse
        
    Returns:
        Liste von Anruf-Dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        
        # Basis-Query
        query = """
            SELECT id, customer_id, activity_type, title, content, 
                   created_by, created_at, is_important, archived,
                   call_direction, call_phone_number, call_duration_seconds, call_notes
            FROM crm_activities
            WHERE customer_id = ? AND activity_type = 'call'
        """
        params = [customer_id]
        
        # Filter nach Richtung
        if direction:
            query += " AND call_direction = ?"
            params.append(direction)
            
        # Filter archivierte
        if not include_archived:
            query += " AND archived = 0"
            
        # Sortierung und Limit
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        calls = []
        for row in rows:
            calls.append({
                "id": row[0],
                "customer_id": row[1],
                "activity_type": row[2],
                "title": row[3],
                "content": row[4],
                "created_by": row[5],
                "created_at": row[6],
                "is_important": bool(row[7]),
                "archived": bool(row[8]),
                "call_direction": row[9],
                "call_direction_display": CALL_DIRECTIONS.get(row[9], row[9]) if row[9] else None,
                "call_phone_number": row[10],
                "call_duration_seconds": row[11] or 0,
                "call_duration_formatted": format_duration(row[11] or 0),
                "call_notes": row[12]
            })
            
        return calls
    except Exception as e:
        print(f"Fehler beim Abrufen der Anrufe: {e}")
        return []
    finally:
        conn.close()


def update_call(
    call_id: int,
    phone_number: Optional[str] = None,
    direction: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Aktualisiert einen Anruf.
    
    Args:
        call_id: ID des Anrufs
        phone_number: Neue Telefonnummer (optional)
        direction: Neue Richtung (optional)
        duration_seconds: Neue Dauer (optional)
        notes: Neue Notizen (optional)
        
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
        
        if phone_number is not None:
            updates.append("call_phone_number = ?")
            params.append(phone_number)
            
        if direction is not None:
            if direction not in CALL_DIRECTIONS:
                print(f"Ungültige Anruf-Richtung: {direction}")
                return False
            updates.append("call_direction = ?")
            params.append(direction)
            
        if duration_seconds is not None:
            updates.append("call_duration_seconds = ?")
            params.append(duration_seconds)
            
        if notes is not None:
            updates.append("call_notes = ?")
            params.append(notes)
            
        if not updates:
            return True  # Nichts zu aktualisieren
        
        # Aktualisiere auch title und content
        if phone_number or direction or duration_seconds or notes:
            # Hole aktuelle Daten
            cursor.execute(
                """
                SELECT call_direction, call_phone_number, call_duration_seconds, call_notes
                FROM crm_activities WHERE id = ?
                """,
                (call_id,)
            )
            row = cursor.fetchone()
            if row:
                current_direction = direction if direction else row[0]
                current_phone = phone_number if phone_number is not None else row[1]
                current_duration = duration_seconds if duration_seconds is not None else row[2]
                current_notes = notes if notes is not None else row[3]
                
                # Aktualisiere title und content
                direction_text = CALL_DIRECTIONS.get(current_direction, current_direction)
                new_title = f"{direction_text}er Anruf - {current_phone}"
                duration_text = format_duration(current_duration or 0)
                new_content = f"Dauer: {duration_text}"
                if current_notes:
                    new_content += f"\n\nNotizen:\n{current_notes}"
                
                updates.append("title = ?")
                params.append(new_title)
                updates.append("content = ?")
                params.append(new_content)
            
        params.append(call_id)
        query = f"UPDATE crm_activities SET {', '.join(updates)} WHERE id = ? AND activity_type = 'call'"
        
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Anrufs: {e}")
        return False
    finally:
        conn.close()


def delete_call(call_id: int) -> bool:
    """
    Löscht einen Anruf.
    
    Args:
        call_id: ID des Anrufs
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM crm_activities WHERE id = ? AND activity_type = 'call'",
            (call_id,)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen des Anrufs: {e}")
        return False
    finally:
        conn.close()


def get_call_statistics(customer_id: int) -> Dict[str, Any]:
    """
    Ruft Statistiken über Anrufe eines Kunden ab.
    
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
            """
            SELECT COUNT(*) FROM crm_activities 
            WHERE customer_id = ? AND activity_type = 'call' AND archived = 0
            """,
            (customer_id,)
        )
        total = cursor.fetchone()[0]
        
        # Nach Richtung
        cursor.execute(
            """
            SELECT call_direction, COUNT(*) 
            FROM crm_activities 
            WHERE customer_id = ? AND activity_type = 'call' AND archived = 0
            GROUP BY call_direction
            """,
            (customer_id,)
        )
        by_direction = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Gesamtdauer
        cursor.execute(
            """
            SELECT SUM(call_duration_seconds) 
            FROM crm_activities 
            WHERE customer_id = ? AND activity_type = 'call' AND archived = 0
            """,
            (customer_id,)
        )
        total_duration = cursor.fetchone()[0] or 0
        
        # Durchschnittliche Dauer
        avg_duration = total_duration / total if total > 0 else 0
        
        # Letzter Anruf
        cursor.execute(
            """
            SELECT created_at, call_direction, call_phone_number 
            FROM crm_activities 
            WHERE customer_id = ? AND activity_type = 'call' 
            ORDER BY created_at DESC LIMIT 1
            """,
            (customer_id,)
        )
        last_call_row = cursor.fetchone()
        last_call = None
        if last_call_row:
            last_call = {
                "date": last_call_row[0],
                "direction": last_call_row[1],
                "phone_number": last_call_row[2]
            }
        
        return {
            "total": total,
            "by_direction": by_direction,
            "incoming": by_direction.get("incoming", 0),
            "outgoing": by_direction.get("outgoing", 0),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": format_duration(total_duration),
            "average_duration_seconds": int(avg_duration),
            "average_duration_formatted": format_duration(int(avg_duration)),
            "last_call": last_call
        }
    except Exception as e:
        print(f"Fehler beim Abrufen der Anruf-Statistiken: {e}")
        return {}
    finally:
        conn.close()


def format_duration(seconds: int) -> str:
    """
    Formatiert eine Dauer in Sekunden zu einem lesbaren String.
    
    Args:
        seconds: Dauer in Sekunden
        
    Returns:
        Formatierter String (z.B. "5:23" oder "1:02:15")
    """
    if seconds < 0:
        seconds = 0
        
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def parse_duration(duration_str: str) -> int:
    """
    Parst einen Dauer-String zu Sekunden.
    
    Args:
        duration_str: String im Format "MM:SS" oder "HH:MM:SS"
        
    Returns:
        Dauer in Sekunden
    """
    try:
        parts = duration_str.split(":")
        if len(parts) == 2:
            # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            return 0
    except Exception:
        return 0


# Hilfsfunktion für schnellen Zugriff
def add_call(
    customer_id: int,
    phone_number: str,
    direction: str,
    duration_seconds: int = 0,
    notes: str = "",
    created_by: str = "System"
) -> Optional[int]:
    """Fügt einen Anruf hinzu (Alias für create_call)."""
    return create_call(customer_id, phone_number, direction, duration_seconds, notes, created_by)
